import os
import re
import io
import base64
import requests
import gspread
import pandas as pd
import streamlit as st
from datetime import datetime, date, timedelta
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import utils as util

# ==============================================================================
# 1. CONEXÃO E CREDENCIAIS
# ==============================================================================

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

# ==============================================================================
# 2. CARREGAMENTO DE DADOS (CACHE OTIMIZADO)
# ==============================================================================

@st.cache_data(ttl=300)
def carregar_tudo():
    wb_internal = conectar()
    if not wb_internal: 
        return None, [pd.DataFrame()] * 12

    def safe_get(conn, nome, colunas_padrao=[]):
        try:
            ws = conn.worksheet(nome)
            dados = ws.get_all_values() 
            if not dados or len(dados) < 1:
                return pd.DataFrame(columns=colunas_padrao)
            
            df = pd.DataFrame(dados[1:], columns=dados[0])
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # VACINA DE NORMALIZAÇÃO SOSA (ANTI-ESPAÇO INVISÍVEL)
            for col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                if any(x in col for x in ["NOTA", "MEDIA", "VALOR", "SOMA"]):
                    df[col] = df[col].apply(util.sosa_to_float)
                if col == "DATA":
                    df[col] = df[col].apply(util.formatar_data_br)

            return df
        except Exception as e: 
            print(f"Erro ao carregar {nome}: {e}")
            return pd.DataFrame(columns=colunas_padrao)

    cols_planos = ["DATA", "SEMANA", "ANO", "TURMA", "EIXO", "PLANO_TEXTO", "LINK_DRIVE"]
    cols_aulas = ["DATA", "SEMANA_REF", "TIPO_MATERIAL", "CONTEUDO", "ANO", "LINK_DRIVE"]
    cols_alunos = ["ID", "NOME_ALUNO", "TURMA", "STATUS", "NECESSIDADES", "ORIGEM"]
    cols_relatorios = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TIPO", "CONTEUDO"]
    cols_diario = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "VISTO_ATIVIDADE", "TAGS", "OBSERVACOES", "BONUS"]
    cols_registro = ["DATA", "SEMANA", "TURMA", "CONTEUDO_MINISTRADO", "ADAPTACAO_PEI", "STATUS_CURRICULO"]
    cols_notas = ["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]
    cols_diagnosticos = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "ID_AVALIACAO", "RESPOSTAS_ALUNO", "NOTA_CALCULADA", "LINK_FOTO_DRIVE"]

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

# ==============================================================================
# 3. FUNÇÕES DE ESCRITA E ATUALIZAÇÃO (UPSERT)
# ==============================================================================

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

def salvar_lote(aba_nome, lista_de_linhas):
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet(aba_nome)
        linhas_str = [[str(x).strip() for x in linha] for linha in lista_de_linhas]
        ws.append_rows(linhas_str, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro ao salvar lote em {aba_nome}: {e}")
        return False

def gerar_proximo_id(df_alunos):
    if df_alunos.empty or 'ID' not in df_alunos.columns: return 2601001
    try:
        ids_num = pd.to_numeric(df_alunos['ID'], errors='coerce').dropna()
        return int(ids_num.max() + 1) if not ids_num.empty else 2601001
    except: return 2601001

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

def atualizar_aluno_cascata(id_aluno, novo_nome, nova_turma, nova_nec):
    """MOTOR DE PROPAGAÇÃO EM CASCATA V48"""
    try:
        wb = conectar()
        id_str = str(limpar_id(id_aluno))
        
        ws_alunos = wb.worksheet("DB_ALUNOS")
        dados_alunos = ws_alunos.get_all_values()
        for i, row in enumerate(dados_alunos):
            if i > 0 and limpar_id(row[0]) == id_str:
                ws_alunos.update_cell(i + 1, 2, novo_nome)
                ws_alunos.update_cell(i + 1, 3, nova_turma)
                ws_alunos.update_cell(i + 1, 5, nova_nec)
                break
        
        def update_tab(aba, col_id, col_nome, col_turma=None):
            try:
                ws = wb.worksheet(aba)
                dados = ws.get_all_values()
                updates = []
                for i, row in enumerate(dados):
                    if i > 0 and len(row) > col_id and limpar_id(row[col_id]) == id_str:
                        updates.append(gspread.Cell(row=i+1, col=col_nome+1, value=novo_nome))
                        if col_turma is not None:
                            updates.append(gspread.Cell(row=i+1, col=col_turma+1, value=nova_turma))
                if updates:
                    ws.update_cells(updates)
            except Exception as e:
                print(f"Erro ao atualizar {aba}: {e}")

        update_tab("DB_DIARIO_BORDO", 1, 2, 3)
        update_tab("DB_NOTAS", 0, 1, 2)
        update_tab("DB_RELATORIOS", 1, 2, None)
        update_tab("DB_GABARITOS_ALUNOS", 1, 2, 3)
        
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro na cascata: {e}")
        return False

def atualizar_fechamento_aula(data, turma, status, ponte, clima):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_REGISTRO_AULAS")
        dados = ws.get_all_values()
        
        for i, row in enumerate(dados):
            if i > 0 and len(row) >= 3 and row[0] == data and row[2] == turma:
                ws.update_cell(i + 1, 7, status)
                ws.update_cell(i + 1, 8, ponte)
                ws.update_cell(i + 1, 9, clima)
                st.cache_data.clear()
                return True
        
        nova_linha = [data, "AVULSA", turma, "Registro via Diário", "N/A", "N/A", status, ponte, clima]
        ws.append_row(nova_linha, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro no fechamento: {e}")
        return False

def ativar_plano_no_hub(semana, ano):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if i == 0: continue
            if row[1].strip() == semana.strip() and row[2].strip() == ano.strip():
                ws.update_cell(i + 1, 5, "HUB_ATIVO")
                st.cache_data.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Erro na ativação: {e}")
        return False

def arquivar_plano_produzido(semana, ano):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if i == 0: continue
            if row[1].strip() == semana.strip() and row[2].strip() == ano.strip():
                ws.update_cell(i + 1, 5, "PRODUZIDO")
                st.cache_data.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Erro ao arquivar: {e}")
        return False

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

def salvar_cronograma_av(lista_dados):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_REGISTRO_AULAS") 
        dados_atuais = ws.get_all_values()
        for i, row in enumerate(dados_atuais):
            if len(row) > 3 and row[2] == lista_dados[1] and row[3] == lista_dados[2]:
                ws.delete_rows(i + 1)
                break
        ws.append_row(lista_dados, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except: return False

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

def salvar_gabarito_escaneado(dados_lista):
    return salvar_no_banco("DB_GABARITOS_ALUNOS", dados_lista)

# ==============================================================================
# 4. FUNÇÕES DE EXCLUSÃO (DELEÇÃO REVERSA E CASCATA)
# ==============================================================================

def excluir_registro(aba_nome, valor_conteudo):
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if len(row) > 3 and valor_conteudo in " ".join(row):
                ws.delete_rows(i + 1)
                st.cache_data.clear()
                return True
        return False
    except: return False

def limpar_diario_data_turma(data, turma):
    """Limpa apenas os registros comuns do diário, protegendo Arguições e Notas"""
    try:
        wb = conectar()
        ws = wb.worksheet("DB_DIARIO_BORDO")
        dados = ws.get_all_values()
        
        tags_protegidas = ["SISTEMA_NOTA", "ARGUIÇÃO", "NOTA_EXTERNA"]
        
        indices = []
        for i, row in enumerate(dados):
            if i > 0 and len(row) > 5:
                if row[0] == data and row[3] == turma and row[5] not in tags_protegidas:
                    indices.append(i + 1)
                    
        for idx in reversed(indices): 
            ws.delete_rows(idx)
            
        return True
    except: 
        return False

def limpar_notas_turma_trimestre(turma, trimestre):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_NOTAS")
        dados = ws.get_all_values()
        indices = [i + 1 for i, row in enumerate(dados) if i > 0 and len(row) > 3 and row[2] == turma and row[3] == trimestre]
        for idx in reversed(indices): ws.delete_rows(idx)
        return True
    except: return False

def excluir_aluno_por_id(id_aluno):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_ALUNOS")
        id_busca = str(limpar_id(id_aluno))
        celula = ws.find(id_busca)
        if celula:
            ws.delete_rows(celula.row)
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        print(f"Erro na exclusão por ID: {e}")
        return False

def excluir_aula_aberta(data_str, turma):
    """BORRACHA TEMPORAL V49"""
    try:
        wb = conectar()
        ws_reg = wb.worksheet("DB_REGISTRO_AULAS")
        dados_reg = ws_reg.get_all_values()
        for i in range(len(dados_reg) - 1, 0, -1):
            row = dados_reg[i]
            if len(row) >= 3 and row[0] == data_str and row[2] == turma:
                ws_reg.delete_rows(i + 1)
        
        ws_diario = wb.worksheet("DB_DIARIO_BORDO")
        dados_diario = ws_diario.get_all_values()
        for i in range(len(dados_diario) - 1, 0, -1):
            row = dados_diario[i]
            if len(row) >= 4 and row[0] == data_str and row[3] == turma:
                ws_diario.delete_rows(i + 1)
                
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro na Borracha Temporal: {e}")
        return False

def excluir_registro_com_drive(aba_nome, valor_conteudo):
    """VERSÃO UNIVERSAL V26 - MAESTRO SOSA"""
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        dados = ws.get_all_values()
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]+)"

        for i, row in enumerate(dados):
            if i == 0: continue 
            linha_completa_txt = " ".join(map(str, row))
            
            if valor_conteudo in linha_completa_txt:
                ids_encontrados = re.findall(padrao_id, linha_completa_txt)
                for file_id in ids_encontrados:
                    try:
                        if len(file_id) > 20:
                            service.files().delete(fileId=file_id).execute()
                    except: pass 
                
                ws.delete_rows(i + 1)
                st.cache_data.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Erro na limpeza universal: {e}")
        return False

def excluir_plano_completo(semana, ano):
    """ENGENHARIA DE LIMPEZA V26 - MAESTRO SOSA"""
    try:
        wb = conectar()
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})"
        linha_para_deletar = -1
        
        for i, row in enumerate(dados):
            if i == 0: continue 
            if len(row) > 2 and row[1].strip() == semana.strip() and row[2].strip() == ano.strip():
                linha_txt = " ".join(map(str, row))
                ids_encontrados = re.findall(padrao_id, linha_txt)
                for file_id in ids_encontrados:
                    try: service.files().delete(fileId=file_id).execute()
                    except: pass
                linha_para_deletar = i + 1
                break 
        
        if linha_para_deletar != -1:
            ws.delete_rows(linha_para_deletar)
            st.cache_data.clear() 
            return True
        return False
    except Exception as e:
        st.error(f"Erro na exclusão cirúrgica: {e}")
        return False

def excluir_avaliacao_completa(identificador, tipo_prova_nome):
    """LIMPEZA EM CASCATA V31.8"""
    try:
        wb = conectar()
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        ws_gaveta = wb.worksheet("DB_AULAS_PRONTAS")
        dados_gaveta = ws_gaveta.get_all_values()
        for i, row in enumerate(dados_gaveta):
            if i > 0 and row[2] == identificador:
                ids = re.findall(r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})", " ".join(row))
                for f_id in ids:
                    try: service.files().delete(fileId=f_id).execute()
                    except: pass
                ws_gaveta.delete_rows(i + 1)
                break
        
        ws_cron = wb.worksheet("DB_REGISTRO_AULAS")
        dados_cron = ws_cron.get_all_values()
        indices_para_deletar = [i + 1 for i, row in enumerate(dados_cron) if i > 0 and tipo_prova_nome in row[3]]
        
        for idx in reversed(indices_para_deletar):
            ws_cron.delete_rows(idx)
            
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro na exclusão em cascata: {e}")
        return False

# ==============================================================================
# 5. INTEGRAÇÃO COM GOOGLE DRIVE (SOSA BRIDGE V45.9 - VACINA ANTI-QUOTA)
# ==============================================================================
def salvar_foto_gabarito_drive(imagem_bytes, nome_aluno, turma, avaliacao_nome):
    """
    SOSA V2026.MASTER: Envia a foto do gabarito como IMAGEM JPG PURA (.jpg) para o Google Drive
    prioritariamente via Apps Script Bridge que possui cota de usuário, evitando o erro 403.
    """
    try:
        # Tenta envio prioritário via Ponte Apps Script para utilizar a cota do usuário
        link_ponte = subir_e_converter_para_google_docs(
            imagem_bytes, 
            f"GABARITO_{turma}_{nome_aluno.replace(' ', '_')}", 
            trimestre="I Trimestre", 
            categoria=turma, 
            semana=avaliacao_nome, 
            modo="SCANNER"
        )
        if "http" in str(link_ponte):
            return link_ponte

        # Fallback via Drive API Nativa com verificação de pasta
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        nome_limpo = re.sub(r'[^a-zA-Z0-9_]', '_', str(nome_aluno))
        data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_arquivo = f"GABARITO_{turma}_{nome_limpo}_{data_str}.jpg"
        
        folder_id = None
        try:
            q_folder = f"mimeType='application/vnd.google-apps.folder' and name contains '{turma}' and trashed=false"
            res_f = service.files().list(q=q_folder, fields="files(id, name)").execute()
            folders = res_f.get('files', [])
            if folders:
                folder_id = folders[0]['id']
        except Exception as e_f:
            print(f"Busca de pasta: {e_f}")

        file_metadata = {'name': nome_arquivo, 'mimeType': 'image/jpeg'}
        if folder_id:
            file_metadata['parents'] = [folder_id]

        media = MediaIoBaseUpload(io.BytesIO(imagem_bytes), mimetype='image/jpeg', resumable=True)
        file_drive = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        file_id = file_drive.get('id')
        try:
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'reader'}
            ).execute()
        except: pass
        
        return file_drive.get('webViewLink', f"https://drive.google.com/file/d/{file_id}/view")
    except Exception as e:
        print(f"Aviso no salvamento da foto JPG: {e}")
        return "N/A"

def subir_e_converter_para_google_docs(file_stream, nome_arquivo, trimestre="I Trimestre", categoria="6º Ano", semana="Semana Geral", modo="AULA"):
    """
    SOSA BRIDGE V45.9: Envia arquivos para o Apps Script com rota de imagem JPG para o Scanner.
    """
    try:
        URL_DA_PONTE = "https://script.google.com/macros/s/AKfycbzbvOfX3KCgVg7yIrVxqLvsbSRa6TFHv564bdzgVsQt2tE8DiM_XcW-IM2ehNMoonWpmQ/exec" 
        
        if isinstance(file_stream, bytes):
            file_b64 = base64.b64encode(file_stream).decode('utf-8')
        else:
            file_stream.seek(0)
            file_b64 = base64.b64encode(file_stream.read()).decode('utf-8')
        
        nome_limpo_arq = re.sub(r'[^a-zA-Z0-9_\-]', '_', str(nome_arquivo))
        
        if modo == "SCANNER":
            nome_envio = f"GABARITO_{nome_limpo_arq}.jpg"
        else:
            nome_envio = f"{nome_limpo_arq}.docx" if not nome_limpo_arq.endswith((".docx", ".pdf")) else nome_limpo_arq

        payload = {
            "fileName": nome_envio, 
            "trimestre": trimestre, 
            "categoria": categoria, 
            "semanaRef": semana, 
            "modo": modo, 
            "fileB64": file_b64
        }
        
        response = requests.post(URL_DA_PONTE, json=payload, timeout=60)
        resposta_texto = response.text.strip()
        
        if response.status_code == 200 and "google.com" in resposta_texto and "https://" in resposta_texto and len(resposta_texto) < 250:
            return resposta_texto
            
        if modo == "SCANNER":
            return f"data:image/jpeg;base64,{file_b64}"
            
        return "N/A"
    except Exception as e:
        print(f"Aviso no envio do arquivo: {e}")
        if modo == "SCANNER" and 'file_b64' in locals():
            return f"data:image/jpeg;base64,{file_b64}"
        return "N/A"

# ==============================================================================
# MOTOR DE RELOCAÇÃO TEMPORAL EM CASCATA (SOSA V202.6 - PRESERVAÇÃO DE DOCS)
# ==============================================================================
def renomear_arquivo_drive(link_drive, novo_nome):
    """Renomeia um arquivo no Google Drive preservando seu ID e link original."""
    try:
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})"
        match = re.search(padrao_id, str(link_drive))
        if match:
            file_id = match.group(1)
            file_metadata = {'name': novo_nome}
            service.files().update(fileId=file_id, body=file_metadata).execute()
            return True
        return False
    except Exception as e:
        print(f"Erro ao renomear arquivo no Drive: {e}")
        return False

def relocador_plano_semana(semana_antiga, ano, nova_semana, link_drive):
    """
    SOSA V202.6: Muda a semana de um plano e de TODAS as suas aulas vinculadas em CASCATA,
    renomeando os títulos no Google Drive e PRESERVANDO 100% os arquivos Google Docs originais.
    """
    try:
        wb = conectar()
        
        # 1. Atualiza a semana do Plano de Ensino em DB_PLANOS
        ws_planos = wb.worksheet("DB_PLANOS")
        dados_p = ws_planos.get_all_values()
        for i, row in enumerate(dados_p):
            if i > 0 and len(row) > 2 and row[1].strip() == semana_antiga.strip() and row[2].strip() == ano.strip():
                ws_planos.update_cell(i + 1, 2, nova_semana.strip())
                break
        
        # 2. MIGRAÇÃO EM CASCATA: Atualiza a referência de TODAS as Aulas em DB_AULAS_PRONTAS
        try:
            ws_aulas = wb.worksheet("DB_AULAS_PRONTAS")
            dados_a = ws_aulas.get_all_values()
            ano_num = "".join(filter(str.isdigit, str(ano)))
            for j, row_a in enumerate(dados_a):
                if j > 0 and len(row_a) > 4 and row_a[1].strip() == semana_antiga.strip() and ano_num in row_a[4]:
                    ws_aulas.update_cell(j + 1, 2, nova_semana.strip())
        except Exception as e_a:
            print(f"Aviso na cascata de aulas: {e_a}")
                
        # 3. Renomeia o título do arquivo no Google Drive sem alterar seu ID
        novo_nome_docs = f"PLANO_{ano.replace('º','')}_{nova_semana.split(' (')[0].replace(' ', '')}"
        renomear_arquivo_drive(link_drive, novo_nome_docs)
        
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro no Relocador em Cascata: {e}")
        return False

# ==============================================================================
# 6. DOWNLOAD DE BYTES PARA RECORTE DE PDF (SOSA BRIDGE V45.9)
# ==============================================================================

def baixar_bytes_arquivo_drive(url_ou_id):
    """Baixa os bytes brutos de um arquivo PDF no Google Drive para fatiamento em memória."""
    if not url_ou_id: return None
    try:
        match = re.search(r"(?:id=|[dD]/)([\w-]+)", str(url_ou_id))
        file_id = match.group(1) if match else str(url_ou_id).strip()
        
        creds = obter_creds_drive()
        if creds:
            service = build('drive', 'v3', credentials=creds)
            request_media = service.files().get_media(fileId=file_id)
            return request_media.execute()
        else:
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            res = requests.get(download_url, timeout=30)
            if res.status_code == 200:
                return res.content
    except Exception as e:
        print(f"Erro ao baixar PDF do Drive: {e}")
    return None

# ==============================================================================
# 6. CONCILIADOR CRONOLÓGICO SOBERANO POR JANELA SEMANAL (SOSA V2026)
# ==============================================================================
def conciliar_calendario_e_planos_cronologicos(ano_alvo="6º"):
    """
    SOSA V2026: CONCILIADOR CRONOLÓGICO POR JANELA DE 7 DIAS.
    Re-indexa as semanas de DB_PLANOS em ordem cronológica e vincula
    automaticamente as aulas 'AVULSA / Registro via Diário' do DB_REGISTRO_AULAS.
    """
    try:
        wb = conectar()
        if not wb: return False
        
        ano_num = "".join(filter(str.isdigit, str(ano_alvo)))
        
        # 1. ORDENAR E RE-INDEXAR DB_PLANOS POR DATA CRONOLÓGICA
        ws_planos = wb.worksheet("DB_PLANOS")
        dados_p = ws_planos.get_all_values()
        if len(dados_p) <= 1: return False
        
        rows_p = dados_p[1:]
        
        # Filtra e ordena planos do ano alvo por data real
        planos_ano = []
        for idx_r, r in enumerate(rows_p):
            if len(r) > 2 and ano_num in str(r[2]):
                try:
                    dt_obj = datetime.strptime(r[0].strip(), "%d/%m/%Y")
                    planos_ano.append((dt_obj, idx_r + 2, r))
                except: pass
        
        # Ordena por data cronológica crescente
        planos_ano.sort(key=lambda x: x[0])
        
        # Cria janelas de 7 dias para cada semana
        intervalos_semanas = []
        
        for seq_idx, (dt_obj, row_num, row_data) in enumerate(planos_ano, start=1):
            nova_sem_label = f"Semana {seq_idx:02d}"
            ws_planos.update_cell(row_num, 2, nova_sem_label) # Atualiza Coluna SEMANA em DB_PLANOS
            
            dt_inicio = dt_obj.date() if isinstance(dt_obj, datetime) else dt_obj
            dt_fim = dt_inicio + timedelta(days=6) # Janela de 7 dias (Segunda a Domingo)
            
            plano_txt = row_data[5] if len(row_data) > 5 else ""
            obj_c = util.extrair_tag(plano_txt, "OBJETO_CONHECIMENTO") or util.extrair_tag(plano_txt, "CONTEUDOS_ESPECIFICOS") or "Conteúdo Programático"
            
            intervalos_semanas.append({
                "semana": nova_sem_label,
                "inicio": dt_inicio,
                "fim": dt_fim,
                "conteudo": obj_c
            })

        # 2. RECONCILIAR E VINCULAR DB_REGISTRO_AULAS PELA JANELA DE 7 DIAS
        ws_reg = wb.worksheet("DB_REGISTRO_AULAS")
        dados_r = ws_reg.get_all_values()
        if len(dados_r) > 1:
            for idx_r, r in enumerate(dados_r[1:], start=2):
                if len(r) >= 4 and ano_num in str(r[2]):
                    try:
                        dt_aula = datetime.strptime(r[0].strip(), "%d/%m/%Y").date()
                        sem_r = r[1].strip()
                        cont_r = r[3].strip()
                        
                        # Procura qual janela semanal de 7 dias engloba a data desta aula
                        semana_encontrada = None
                        for window in intervalos_semanas:
                            if window["inicio"] <= dt_aula <= window["fim"]:
                                semana_encontrada = window["semana"]
                                break
                        
                        if semana_encontrada:
                            ws_reg.update_cell(idx_r, 2, semana_encontrada) # Atualiza coluna SEMANA
                            if sem_r == "AVULSA" or "Registro via Diário" in cont_r or cont_r == "":
                                novo_titulo = f"{ano_alvo} Ano - Aula - {semana_encontrada}"
                                ws_reg.update_cell(idx_r, 4, novo_titulo) # Atualiza CONTEUDO
                    except Exception as e_row:
                        print(f"Erro linha {idx_r}: {e_row}")

        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro no conciliador: {e}")
        return False
