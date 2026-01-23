import gspread
import pandas as pd
from google.oauth2 import service_account
import streamlit as st
import os

def conectar():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        
        # TENTATIVA 1: Conexão Local (Seu computador)
        if os.path.exists("credentials.json"):
            creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
        
        # TENTATIVA 2: Conexão Nuvem (Streamlit Cloud)
        else:
            # Na nuvem, ele busca nos "Segredos" do sistema
            creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
            
        return gspread.authorize(creds).open("SOSA_DB_2026")
    except Exception as e:
        # Evita mostrar erro na tela se for apenas timeout
        if "429" in str(e):
            st.warning("⚠️ Limite de tráfego do Google. Aguarde alguns segundos.")
        else:
            st.error(f"Erro de Conexão: {e}")
        return None

def limpar_id(valor):
    """Remove decimais (.0) e converte para string limpa."""
    if pd.isna(valor) or valor == "":
        return ""
    s_val = str(valor).strip()
    if s_val.endswith(".0"):
        return s_val[:-2]
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
            
            # Se o DF estiver vazio mas tivermos colunas padrão, cria o DF com elas
            if df.empty and colunas_padrao:
                df = pd.DataFrame(columns=colunas_padrao)
            
            if not df.empty:
                df.columns = [str(c).strip().upper() for c in df.columns]
                
                # --- CORREÇÕES ESPECÍFICAS DE SCHEMA ---
                if nome == "DB_AULAS_PRONTAS":
                    mapeamento = {
                        'ORIGEM': 'DATA', 'LOUSA': 'SEMANA_REF', 
                        'ATIVIDADE': 'TIPO_MATERIAL', 'GABARITO': 'CONTEUDO', 'IMAGENS': 'ANO'
                    }
                    df = df.rename(columns=mapeamento)
                
                elif nome == "DB_PLANOS":
                    mapeamento_planos = {
                        'SERIE': 'ANO', 'SÉRIE': 'ANO', 
                        'TRIM': 'TRIMESTRE', 'ETAPA': 'TRIMESTRE'
                    }
                    df = df.rename(columns=mapeamento_planos)
                    if "ANO" in df.columns:
                        df['ANO'] = df['ANO'].astype(str).apply(lambda x: f"{x}º" if x.isdigit() else x)

                elif nome == "DB_RELATORIOS":
                    if "TURMA" in df.columns and "TIPO" not in df.columns:
                        df = df.rename(columns={"TURMA": "TIPO"})
                    if "ID_ALUNO" in df.columns:
                        df['ID_ALUNO'] = df['ID_ALUNO'].apply(limpar_id)

                elif nome == "DB_ALUNOS":
                     if "ID" in df.columns:
                        df['ID'] = df['ID'].apply(limpar_id)

                elif nome == "DB_DIARIO_BORDO":
                    if "ID_ALUNO" in df.columns:
                        df['ID_ALUNO'] = df['ID_ALUNO'].apply(limpar_id)
                
                # --- CORREÇÃO CRÍTICA: DB_NOTAS ---
                elif nome == "DB_NOTAS":
                    if "ID_ALUNO" in df.columns:
                        df['ID_ALUNO'] = df['ID_ALUNO'].apply(limpar_id)
                    
                    # Garante que as colunas de notas existam (Auto-Reparo)
                    cols_essenciais = ["NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]
                    for col in cols_essenciais:
                        if col not in df.columns:
                            df[col] = 0.0 # Cria a coluna com zero se não existir

            return df
        except: return pd.DataFrame(columns=colunas_padrao)

    cols_planos = ["DATA", "SEMANA", "ANO", "TRIMESTRE", "TURMA", "PLANO_TEXTO"]
    cols_aulas = ["DATA", "SEMANA_REF", "TIPO_MATERIAL", "CONTEUDO", "ANO"]
    cols_alunos = ["ID", "NOME_ALUNO", "TURMA", "STATUS", "NECESSIDADES", "ORIGEM"]
    cols_relatorios = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TIPO", "CONTEUDO"]
    cols_diario = ["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "VISTO_ATIVIDADE", "TAGS", "OBSERVACOES"]
    cols_registro = ["DATA", "SEMANA", "TURMA", "CONTEUDO_MINISTRADO", "ADAPTACAO_PEI", "STATUS_CURRICULO"]
    cols_notas = ["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]

    return wb, (
        safe_get("DB_ALUNOS", cols_alunos), 
        safe_get("DB_CURRICULO"), 
        safe_get("DB_MATERIAIS"),
        safe_get("DB_PLANOS", cols_planos), 
        safe_get("DB_AULAS_PRONTAS", cols_aulas), 
        safe_get("DB_NOTAS", cols_notas), 
        safe_get("DB_DIARIO_BORDO", cols_diario), 
        safe_get("DB_TURMAS"), 
        safe_get("DB_RELATORIOS", cols_relatorios), 
        safe_get("DB_HORARIOS"),
        safe_get("DB_REGISTRO_AULAS", cols_registro)
    )

def salvar_no_banco(aba_nome, linha):
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet(aba_nome)
        
        # Se a aba estiver vazia, cria o cabeçalho correto
        if not ws.get_all_values():
            if aba_nome == "DB_AULAS_PRONTAS":
                ws.append_row(["DATA", "SEMANA_REF", "TIPO_MATERIAL", "CONTEUDO", "ANO"])
            elif aba_nome == "DB_PLANOS":
                ws.append_row(["DATA", "SEMANA", "ANO", "TRIMESTRE", "TURMA", "PLANO_TEXTO"])
            elif aba_nome == "DB_RELATORIOS":
                ws.append_row(["DATA", "ID_ALUNO", "NOME_ALUNO", "TIPO", "CONTEUDO"])
            elif aba_nome == "DB_DIARIO_BORDO":
                ws.append_row(["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "VISTO_ATIVIDADE", "TAGS", "OBSERVACOES"])
            elif aba_nome == "DB_REGISTRO_AULAS":
                ws.append_row(["DATA", "SEMANA", "TURMA", "CONTEUDO_MINISTRADO", "ADAPTACAO_PEI", "STATUS_CURRICULO"])
            elif aba_nome == "DB_NOTAS":
                ws.append_row(["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"])
        
        linha_str = [str(x) for x in linha]
        ws.append_row(linha_str)
        st.cache_data.clear() 
        return True
    except Exception as e:
        st.error(f"Erro ao salvar: {e}")
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

# --- FUNÇÕES DE ALTA PERFORMANCE (LOTE) ---
def limpar_diario_data_turma(data, turma):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_DIARIO_BORDO")
        dados = ws.get_all_values()
        indices_para_deletar = []
        for i, row in enumerate(dados):
            if i == 0: continue 
            if len(row) > 3 and row[0] == data and row[3] == turma:
                indices_para_deletar.append(i + 1)
        for idx in reversed(indices_para_deletar):
            ws.delete_rows(idx)
        return True
    except Exception as e:
        st.error(f"Erro ao limpar dados antigos: {e}")
        return False

def limpar_notas_turma_trimestre(turma, trimestre):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_NOTAS")
        dados = ws.get_all_values()
        indices_para_deletar = []
        for i, row in enumerate(dados):
            if i == 0: continue 
            if len(row) > 3 and row[2] == turma and row[3] == trimestre:
                indices_para_deletar.append(i + 1)
        for idx in reversed(indices_para_deletar):
            ws.delete_rows(idx)
        return True
    except Exception as e:
        st.error(f"Erro ao limpar notas antigas: {e}")
        return False

def salvar_lote(aba_nome, lista_de_linhas):
    try:
        wb = conectar()
        ws = wb.worksheet(aba_nome)
        ws.append_rows(lista_de_linhas)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar lote: {e}")
        return False

# --- NOVA FUNÇÃO: EDITAR ALUNO (ADICIONADA PARA O SISTEMA V14) ---
def atualizar_necessidade_aluno(id_aluno, nova_necessidade):
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet("DB_ALUNOS")
        
        # 1. Procura a célula que contém o ID exato do aluno
        cell = ws.find(str(id_aluno))
        
        if cell:
            # 2. A coluna NECESSIDADES é a 5ª coluna (A=1, B=2, C=3, D=4, E=5)
            ws.update_cell(cell.row, 5, nova_necessidade.upper())
            st.cache_data.clear()
            return True
        else:
            st.error("ID do aluno não encontrado na planilha.")
            return False
    except Exception as e:
        st.error(f"Erro ao atualizar aluno: {e}")
        return False

# --- FUNÇÃO PARA O BOLETIM ANUAL (RECUPERAÇÃO FINAL) ---
def salvar_rec_final(id_aluno, nome_aluno, turma, nota_rec_final):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_NOTAS")
        
        # 1. Remove nota anterior de Rec Final se houver
        dados = ws.get_all_values()
        for i, row in enumerate(dados):
            if len(row) > 3 and row[0] == str(id_aluno) and row[3] == "REC_FINAL":
                ws.delete_rows(i + 1)
                break
        
        # 2. Salva a nova
        ws.append_row([id_aluno, nome_aluno, turma, "REC_FINAL", 0, 0, 0, 0, str(nota_rec_final).replace('.', ',')])
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar Rec Final: {e}")
        return False

# --- FUNÇÃO ESPECIAL: SALVAR ATA (SUBSTITUI ANTERIOR) ---
def salvar_ata_conselho(data, turma, tipo, conteudo):
    try:
        wb = conectar()
        ws = wb.worksheet("DB_RELATORIOS")
        dados = ws.get_all_values()
        
        # Varre de trás para frente para encontrar e apagar duplicatas
        for i in range(len(dados) - 1, 0, -1):
            row = dados[i]
            if len(row) > 3:
                if row[1] == "TURMA" and row[2] == turma and row[3] == tipo:
                    ws.delete_rows(i + 1)
        
        # Salva a nova versão
        ws.append_row([data, "TURMA", turma, tipo, conteudo])
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro ao salvar Ata: {e}")
        return False

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# --- FUNÇÃO AUXILIAR PARA PEGAR CREDENCIAIS (CORREÇÃO DE ERRO) ---
def obter_creds_drive():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    if os.path.exists("credentials.json"):
        return service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
    else:
        return service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)

# --- FUNÇÃO DE UPLOAD ATUALIZADA ---
def subir_e_converter_para_google_docs(file_stream, nome_arquivo):
    try:
        from googleapiclient.discovery import build
        from googleapiclient.http import MediaIoBaseUpload
        
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)

        # --- CONFIGURAÇÃO ---
        ID_DA_SUA_PASTA = "1W8U5R-J36X_vHXeGyDH2TqWc96rEY7Rr" 
        SEU_EMAIL_PESSOAL = "prof.ronaldogomess@gmail.com" 

        file_metadata = {
            'name': nome_arquivo,
            'parents': [ID_DA_SUA_PASTA]
        }
        
        # TENTATIVA 1: Subir como DOCX puro (Gasta menos cota e é mais seguro)
        media = MediaIoBaseUpload(
            file_stream, 
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            resumable=True
        )
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id, webViewLink'
        ).execute()
        
        file_id = file.get('id')

        # TENTATIVA DE TRANSFERIR PROPRIEDADE
        try:
            service.permissions().create(
                fileId=file_id,
                transferOwnership=True,
                body={'type': 'user', 'role': 'owner', 'emailAddress': SEU_EMAIL_PESSOAL}
            ).execute()
        except:
            # Se falhar a transferência, apenas dá permissão de escrita
            service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'writer'}
            ).execute()

        return file.get('webViewLink')

    except Exception as e:
        if "quota" in str(e).lower():
            return "⚠️ O Google ainda diz que está cheio. Clique no botão 'Resetar Espaço' na lateral e tente de novo."
        return f"Erro: {e}"
        
        # 1. Cria o arquivo
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        file_id = file.get('id')

        # 2. TRANSFERÊNCIA DE PROPRIEDADE (O "Pulo do Gato")
        # Isso faz com que VOCÊ seja o dono e o arquivo use o SEU espaço
        service.permissions().create(
            fileId=file_id,
            transferOwnership=True, # Transfere a conta do espaço para você
            body={
                'type': 'user',
                'role': 'owner',
                'emailAddress': SEU_EMAIL_PESSOAL
            }
        ).execute()
        
        # 3. Limpa a lixeira da conta de serviço para evitar que ela lote de novo
        service.files().emptyTrash().execute()

        return file.get('webViewLink')

    except Exception as e:
        error_msg = str(e)
        if "quota" in error_msg.lower():
            return "Erro: A conta de serviço ainda está acusando cota cheia. Tente excluir arquivos antigos da pasta ou verifique se o e-mail pessoal está correto."
        return f"Erro no Drive: {error_msg}"
    
def limpar_todo_drive_da_conta_servico():
    try:
        from googleapiclient.discovery import build
        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds)
        
        # Lista todos os arquivos que a conta de serviço é dona
        results = service.files().list(
            q="'me' in owners", 
            fields="files(id, name)"
        ).execute()
        items = results.get('files', [])
        
        if not items:
            return "A conta de serviço já está vazia."
        
        for item in items:
            service.files().delete(fileId=item['id']).execute()
            
        # Limpa a lixeira permanentemente
        service.files().emptyTrash().execute()
        
        return f"Sucesso! {len(items)} arquivos inúteis foram apagados e o espaço foi liberado."
    except Exception as e:
        return f"Erro na limpeza: {e}"
