import gspread
import pandas as pd
from google.oauth2 import service_account
import streamlit as st
import os
import requests
import base64
from datetime import datetime
from googleapiclient.discovery import build
import utils as util  # <--- ADICIONE ESTA LINHA AQUI


def conectar():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        if os.path.exists("credentials.json"):
            creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
        else:
            creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
        return gspread.authorize(creds).open("SOSA_DB_2026")
    except Exception as e:
        if "429" in str(e):
            st.warning("⚠️ Limite de tráfego do Google. Aguarde alguns segundos.")
        else:
            st.error(f"Erro de Conexão: {e}")
        return None

def obter_creds_drive():
    """Retorna as credenciais para uso direto com a API do Google Drive."""
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if os.path.exists("credentials.json"):
        return service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
    else:
        return service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)

def limpar_id(valor):
    if pd.isna(valor) or valor == "": return ""
    s_val = str(valor).strip()
    if s_val.endswith(".0"): return s_val[:-2]
    return s_val

@st.cache_data(ttl=300)
def carregar_tudo():
    # 1. Conecta ao Workbook (wb)
    wb_internal = conectar()
    if not wb_internal: 
        return None, [pd.DataFrame()] * 12

    # 2. Função interna com o wb passado explicitamente para evitar erro de escopo
    def safe_get(conn, nome, colunas_padrao=[]):
        try:
            ws = conn.worksheet(nome) # Agora usa 'conn' que foi passado
            dados = ws.get_all_values() 
            if not dados or len(dados) < 1:
                return pd.DataFrame(columns=colunas_padrao)
            
            df = pd.DataFrame(dados[1:], columns=dados[0])
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # --- BLINDAGEM DECIMAL SOSA ---
            for col in df.columns:
                if any(x in col for x in ["NOTA", "MEDIA", "VALOR", "SOMA"]):
                    df[col] = df[col].apply(util.sosa_to_float)

            # --- LÓGICA ESPECÍFICA POR TABELA (PRESERVADA) ---
            if nome == "DB_AULAS_PRONTAS":
                if "LINK_DRIVE" not in df.columns: df["LINK_DRIVE"] = ""
            
            elif nome == "DB_PLANOS":
                if "ANO" in df.columns:
                    df['ANO'] = df['ANO'].astype(str).apply(lambda x: f"{x}º" if x.isdigit() and "º" not in x else x)
                if "LINK_DRIVE" not in df.columns: df["LINK_DRIVE"] = ""

            elif nome == "DB_CURRICULO":
                # VACINA SOSA: Garante que o ANO do currículo seja numérico para os filtros
                if "ANO" in df.columns:
                    df['ANO'] = pd.to_numeric(df['ANO'], errors='coerce')

            return df
        except Exception as e: 
            print(f"Erro ao carregar {nome}: {e}")
            return pd.DataFrame(columns=colunas_padrao)

    # Definição das colunas para as tabelas
    cols_planos = ["DATA", "SEMANA", "ANO", "TRIMESTRE", "TURMA", "PLANO_TEXTO", "LINK_DRIVE"]
    cols_aulas = ["DATA", "SEMANA_REF", "TIPO_MATERIAL", "CONTEUDO", "ANO", "LINK_DRIVE"]
    cols_alunos = ["ID", "NOME_ALUNO", "TURMA", "STATUS", "NECESSIDADES", "ORIGEM"]
    cols_relatorios = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TIPO", "CONTEUDO"]
    cols_diario = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "VISTO_ATIVIDADE", "TAGS", "OBSERVACOES"]
    cols_registro = ["DATA", "SEMANA", "TURMA", "CONTEUDO_MINISTRADO", "ADAPTACAO_PEI", "STATUS_CURRICULO"]
    cols_notas = ["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]
    cols_diagnosticos = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "ID_AVALIACAO", "RESPOSTAS_ALUNO", "NOTA_CALCULADA", "LINK_FOTO_DRIVE"]

    # 3. Retorno com a chamada passando o wb_internal
    return wb_internal, (
        safe_get(wb_internal, "DB_ALUNOS", cols_alunos), 
        safe_get(wb_internal, "DB_CURRICULO"), 
        safe_get(wb_internal, "DB_MATERIAIS"),
        safe_get(wb_internal, "DB_PLANOS", cols_planos), 
        safe_get(wb_internal, "DB_AULAS_PRONTAS", cols_aulas), 
        safe_get(wb_internal, "DB_NOTAS", cols_notas), 
        safe_get(wb_internal, "DB_DIARIO_BORDO", cols_diario), 
        safe_get(wb_internal, "DB_TURMAS"), 
        safe_get(wb_internal, "DB_RELATORIOS", cols_relatorios), 
        safe_get(wb_internal, "DB_HORARIOS"), 
        safe_get(wb_internal, "DB_REGISTRO_AULAS", cols_registro),
        safe_get(wb_internal, "DB_GABARITOS_ALUNOS", cols_diagnosticos)
    )

def salvar_no_banco(aba_nome, linha):
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet(aba_nome)
        linha_str = [str(x).strip() for x in linha]
        ws.append_row(linha_str, value_input_option="USER_ENTERED", insert_data_option="INSERT_ROWS")
        st.cache_data.clear() 
        return True
    except Exception as e:
        st.error(f"Erro ao salvar no banco: {e}")
        return False

def excluir_registro(aba_nome, valor_conteudo):
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if len(row) > 3 and row[3] == valor_conteudo:
                ws.delete_rows(i + 1)
                st.cache_data.clear()
                return True
        return False
    except: return False

def gerar_proximo_id(df_alunos):
    if df_alunos.empty or 'ID' not in df_alunos.columns: return 2601001
    try:
        ids_num = pd.to_numeric(df_alunos['ID'], errors='coerce').dropna()
        return int(ids_num.max() + 1) if not ids_num.empty else 2601001
    except: return 2601001

def limpar_diario_data_turma(data, turma):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_DIARIO_BORDO")
        dados = ws.get_all_values()
        indices = [i + 1 for i, row in enumerate(dados) if i > 0 and len(row) > 3 and row[0] == data and row[3] == turma]
        for idx in reversed(indices): ws.delete_rows(idx)
        return True
    except: return False

def limpar_notas_turma_trimestre(turma, trimestre):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_NOTAS")
        dados = ws.get_all_values()
        indices = [i + 1 for i, row in enumerate(dados) if i > 0 and len(row) > 3 and row[2] == turma and row[3] == trimestre]
        for idx in reversed(indices): ws.delete_rows(idx)
        return True
    except: return False

def salvar_lote(aba_nome, lista_de_linhas):
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        ws.append_rows(lista_de_linhas, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except: return False

def atualizar_necessidade_aluno(id_aluno, nova_necessidade):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_ALUNOS")
        cell = ws.find(str(id_aluno))
        if cell:
            ws.update_cell(cell.row, 5, nova_necessidade.upper())
            st.cache_data.clear()
            return True
        return False
    except: return False

def salvar_rec_final(id_aluno, nome_aluno, turma, nota_rec_final):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_NOTAS")
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if len(row) > 3 and row[0] == str(id_aluno) and row[3] == "REC_FINAL":
                ws.delete_rows(i + 1)
                break
        ws.append_row([id_aluno, nome_aluno, turma, "REC_FINAL", 0, 0, 0, 0, str(nota_rec_final).replace('.', ',')])
        st.cache_data.clear()
        return True
    except: return False

def salvar_ata_conselho(data, turma, tipo, conteudo):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_RELATORIOS")
        dados = ws.get_all_values()
        for i in range(len(dados) - 1, 0, -1):
            row = dados[i]
            if len(row) > 3 and row[1] == "TURMA" and row[2] == turma and row[3] == tipo:
                ws.delete_rows(i + 1)
        ws.append_row([data, "TURMA", turma, tipo, conteudo])
        st.cache_data.clear()
        return True
    except: return False

def subir_e_converter_para_google_docs(file_stream, nome_arquivo, trimestre="I Trimestre", categoria="Material de Sala", semana="Semana Geral", aula="Aula Geral", modo="AULA"):
    try:
        URL_DA_PONTE = "https://script.google.com/macros/s/AKfycby6JpIPHk6vlCfQSms-wxLcRmUNNw6yVOf6qkBnEuTrco2bVFw8Apl9m0wqTIlOcw01_w/exec" 
        
        file_stream.seek(0)
        file_b64 = base64.b64encode(file_stream.read()).decode('utf-8')
        
        payload = {
            "fileName": nome_arquivo, "trimestre": trimestre, "categoria": categoria, 
            "semanaRef": semana, "aulaRef": aula, "modo": modo, "fileB64": file_b64
        }
        
        response = requests.post(URL_DA_PONTE, json=payload, timeout=60)
        resposta_texto = response.text.strip()
        
        # AJUSTE SOSA: Aceita qualquer link válido do Google (Docs ou Drive)
        if "google.com" in resposta_texto and "https" in resposta_texto:
            return resposta_texto
        else:
            return f"ERRO_NO_UPLOAD: {resposta_texto[:50]}"
    except Exception as e: 
        return f"Erro de Conexão: {e}"

def limpar_todo_drive_da_conta_servico():
    try:
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(q="'me' in owners", fields="files(id, name)").execute()
        items = results.get('files', [])
        if not items: return "A conta de serviço já está vazia."
        for item in items: service.files().delete(fileId=item['id']).execute()
        service.files().emptyTrash().execute()
        return f"Sucesso! {len(items)} arquivos apagados."
    except Exception as e: return f"Erro na limpeza: {e}"

def salvar_link_na_planilha(aba_nome, coluna_busca, valor_busca, link_drive):
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        dados = ws.get_all_values()
        cabecalho = dados[0]
        col_link_idx = cabecalho.index("LINK_DRIVE") + 1
        col_busca_idx = cabecalho.index(coluna_busca)
        for i, row in enumerate(dados):
            if i > 0 and row[col_busca_idx] == valor_busca:
                ws.update_cell(i + 1, col_link_idx, link_drive)
                st.cache_data.clear() 
                return True
        return False
    except: return False

def atualizar_plano_existente(semana, ano, novo_texto_formatado):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if i > 0 and row[1] == semana and row[2] == ano:
                ws.update_cell(i + 1, 6, novo_texto_formatado) 
                st.cache_data.clear()
                return True
        return False
    except: return False

def excluir_plano_total(semana, ano):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if i > 0 and row[1] == semana and row[2] == ano:
                ws.delete_rows(i + 1)
                st.cache_data.clear()
                return True
        return False
    except: return False

def extrair_id_da_url(url):
    import re
    match = re.search(r"/d/(.*?)/", url)
    return match.group(1) if match else None

def excluir_registro_com_drive(aba_nome, valor_conteudo):
    """
    VERSÃO UNIVERSAL V26 - MAESTRO SOSA
    Localiza o registro em QUALQUER coluna, deleta arquivos no Drive e remove a linha.
    """
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        dados = ws.get_all_values()
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        import re
        # Padrao para pegar IDs de documentos ou arquivos (id= ou /d/)
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]+)"

        for i, row in enumerate(dados):
            if i == 0: continue # Pula cabeçalho
            
            # Transforma a linha inteira em um texto único para busca
            linha_completa_txt = " ".join(map(str, row))
            
            # Se o conteúdo que queremos apagar está em algum lugar dessa linha
            if valor_conteudo in linha_completa_txt:
                # 1. Busca todos os IDs do Google Drive presentes na linha inteira
                ids_encontrados = re.findall(padrao_id, linha_completa_txt)
                
                # 2. Deleta cada arquivo encontrado no Drive
                for file_id in ids_encontrados:
                    try:
                        # Verifica se o ID tem tamanho de um ID real do Google (geralmente > 20 caracteres)
                        if len(file_id) > 20:
                            service.files().delete(fileId=file_id).execute()
                    except:
                        pass # Arquivo já deletado ou sem permissão
                
                # 3. Remove a linha da planilha
                ws.delete_rows(i + 1)
                st.cache_data.clear()
                return True
                
        return False
    except Exception as e:
        st.error(f"Erro na limpeza universal: {e}")
        return False

def salvar_cronograma_av(lista_dados):
    """
    Salva ou atualiza o cronograma de provas.
    Estrutura: [DATA, TURMA, TIPO, ASSUNTO, LINK]
    """
    try:
        wb = conectar()
        # Usaremos a aba DB_REGISTRO_AULAS ou criaremos uma nova DB_CRONOGRAMA
        ws = wb.worksheet("DB_REGISTRO_AULAS") 
        # Lógica: Se já existe a mesma TURMA e TIPO, removemos a antiga (Upsert)
        dados_atuais = ws.get_all_values()
        for i, row in enumerate(dados_atuais):
            if len(row) > 3 and row[2] == lista_dados[1] and row[3] == lista_dados[2]:
                ws.delete_rows(i + 1)
                break
        
        ws.append_row(lista_dados, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except:
        return False

def excluir_plano_completo(semana, ano):
    """
    ENGENHARIA DE LIMPEZA V26 - MAESTRO SOSA
    Localiza o plano por Semana e Ano, deleta no Drive e remove a linha da planilha.
    """
    try:
        wb = conectar()
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        import re
        # Regex para capturar IDs de documentos Google (/d/ID/ ou id=ID)
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})"

        linha_para_deletar = -1
        
        for i, row in enumerate(dados):
            if i == 0: continue # Pula o cabeçalho
            
            # row[1] é SEMANA, row[2] é ANO (Ex: "6º")
            if len(row) > 2 and row[1].strip() == semana.strip() and row[2].strip() == ano.strip():
                # 1. Varredura de IDs do Drive na linha inteira
                linha_txt = " ".join(map(str, row))
                ids_encontrados = re.findall(padrao_id, linha_txt)
                
                # 2. Execução do Delete na Nuvem
                for file_id in ids_encontrados:
                    try:
                        service.files().delete(fileId=file_id).execute()
                    except:
                        pass # Arquivo pode já ter sido removido
                
                linha_para_deletar = i + 1
                break # Alvo encontrado e processado
        
        # 3. Remoção da linha na Planilha
        if linha_para_deletar != -1:
            ws.delete_rows(linha_para_deletar)
            st.cache_data.clear() # Limpa o cache para refletir a mudança
            return True
            
        return False
    except Exception as e:
        st.error(f"Erro na exclusão cirúrgica: {e}")
        return False

def excluir_avaliacao_completa(identificador, tipo_prova_nome):
    """
    LIMPEZA EM CASCATA V31.8
    1. Deleta arquivos no Drive.
    2. Remove da gaveta (DB_AULAS_PRONTAS).
    3. Remove todos os agendamentos no cronograma (DB_REGISTRO_AULAS).
    """
    try:
        wb = conectar()
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        import re
        
        # 1. LIMPEZA NA GAVETA E DRIVE
        ws_gaveta = wb.worksheet("DB_AULAS_PRONTAS")
        dados_gaveta = ws_gaveta.get_all_values()
        for i, row in enumerate(dados_gaveta):
            if i > 0 and row[2] == identificador:
                # Busca IDs do Drive para deletar
                ids = re.findall(r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})", " ".join(row))
                for f_id in ids:
                    try: service.files().delete(fileId=f_id).execute()
                    except: pass
                ws_gaveta.delete_rows(i + 1)
                break
        
        # 2. LIMPEZA NO CRONOGRAMA (DB_REGISTRO_AULAS)
        ws_cron = wb.worksheet("DB_REGISTRO_AULAS")
        dados_cron = ws_cron.get_all_values()
        # Filtra linhas onde o conteúdo contém o nome da prova (ex: "Aplicação: Teste")
        indices_para_deletar = [i + 1 for i, row in enumerate(dados_cron) if i > 0 and tipo_prova_nome in row[3]]
        
        # Deleta de baixo para cima para não errar o índice
        for idx in reversed(indices_para_deletar):
            ws_cron.delete_rows(idx)
            
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro na exclusão em cascata: {e}")
        return False
    
def salvar_gabarito_escaneado(dados_lista):
    """
    Salva na aba DB_GABARITOS_ALUNOS.
    Estrutura: [DATA, ID_ALUNO, NOME_ALUNO, TURMA, ID_AVALIACAO, RESPOSTAS, NOTA, LINK_FOTO]
    """
    return salvar_no_banco("DB_GABARITOS_ALUNOS", dados_lista)
