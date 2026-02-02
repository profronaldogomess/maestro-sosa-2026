import gspread
import pandas as pd
from google.oauth2 import service_account
import streamlit as st
import os
import requests
import base64
from datetime import datetime
from googleapiclient.discovery import build

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
    wb = conectar()
    if not wb: return None, [pd.DataFrame()]*11 
    
    def safe_get(nome, colunas_padrao=[]):
        try:
            ws = wb.worksheet(nome)
            dados = ws.get_all_records()
            df = pd.DataFrame(dados)
            
            if df.empty: return pd.DataFrame(columns=colunas_padrao)
            
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            if nome == "DB_AULAS_PRONTAS":
                df = df.dropna(subset=["DATA", "SEMANA_REF"], how="all")
                if "LINK_DRIVE" not in df.columns: df["LINK_DRIVE"] = ""

            elif nome == "DB_PLANOS":
                if "ANO" in df.columns:
                    df['ANO'] = df['ANO'].astype(str).apply(lambda x: f"{x}º" if x.isdigit() and "º" not in x else x)
                if "LINK_DRIVE" not in df.columns: df["LINK_DRIVE"] = ""

            return df
        except: return pd.DataFrame(columns=colunas_padrao)

    cols_planos = ["DATA", "SEMANA", "ANO", "TRIMESTRE", "TURMA", "PLANO_TEXTO", "LINK_DRIVE"]
    cols_aulas = ["DATA", "SEMANA_REF", "TIPO_MATERIAL", "CONTEUDO", "ANO", "LINK_DRIVE"]
    cols_alunos = ["ID", "NOME_ALUNO", "TURMA", "STATUS", "NECESSIDADES", "ORIGEM"]
    cols_relatorios = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TIPO", "CONTEUDO"]
    cols_diario = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "VISTO_ATIVIDADE", "TAGS", "OBSERVACOES"]
    cols_registro = ["DATA", "SEMANA", "TURMA", "CONTEUDO_MINISTRADO", "ADAPTACAO_PEI", "STATUS_CURRICULO"]
    cols_notas = ["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]

    return wb, (
        safe_get("DB_ALUNOS", cols_alunos), safe_get("DB_CURRICULO"), safe_get("DB_MATERIAIS"),
        safe_get("DB_PLANOS", cols_planos), safe_get("DB_AULAS_PRONTAS", cols_aulas), 
        safe_get("DB_NOTAS", cols_notas), safe_get("DB_DIARIO_BORDO", cols_diario), 
        safe_get("DB_TURMAS"), safe_get("DB_RELATORIOS", cols_relatorios), 
        safe_get("DB_HORARIOS"), safe_get("DB_REGISTRO_AULAS", cols_registro)
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
        # 1. Certifique-se de usar a URL da ÚLTIMA IMPLANTAÇÃO do seu Script
        URL_DA_PONTE = "https://script.google.com/macros/s/AKfycby6JpIPHk6vlCfQSms-wxLcRmUNNw6yVOf6qkBnEuTrco2bVFw8Apl9m0wqTIlOcw01_w/exec" 
        
        file_stream.seek(0)
        file_b64 = base64.b64encode(file_stream.read()).decode('utf-8')
        
        payload = {
            "fileName": nome_arquivo, 
            "trimestre": trimestre, 
            "categoria": categoria, 
            "semanaRef": semana, 
            "aulaRef": aula, 
            "modo": modo, 
            "fileB64": file_b64
        }
        
        # 2. Timeout de 60s para conversões pesadas
        response = requests.post(URL_DA_PONTE, json=payload, timeout=60)
        resposta_texto = response.text.strip()
        
        # 🚨 BLINDAGEM SOSA: Verifica se o retorno é um link válido do Google
        if "https://docs.google.com" in resposta_texto:
            return resposta_texto
        else:
            # Se o Google retornar um erro (HTML ou texto de erro), o Python avisa aqui
            st.error(f"⚠️ Falha na Ponte Google: {resposta_texto[:100]}...")
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
    """Localiza o registro, deleta os arquivos no Drive e remove a linha da planilha."""
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        dados = ws.get_all_values()
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        for i, row in enumerate(dados):
            # Procura o conteúdo na coluna 3 (índice 3)
            if len(row) > 3 and valor_conteudo in row[3]:
                import re
                # Extrai todos os IDs de arquivos Google Docs do texto
                links = re.findall(r"https://docs\.google\.com/document/d/([a-zA-Z0-9-_]+)", row[3])
                for file_id in links:
                    try: 
                        service.files().delete(fileId=file_id).execute()
                    except: 
                        pass # Arquivo pode já ter sido deletado manualmente
                
                ws.delete_rows(i + 1)
                st.cache_data.clear()
                return True
        return False
    except Exception as e:
        st.error(f"Erro na limpeza: {e}")
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
