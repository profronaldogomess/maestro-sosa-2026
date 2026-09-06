import os
import re
import io
import time
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
import ai_engine as ai

# ==============================================================================
# 1. CONEXÃO E CREDENCIAIS (BLINDAGEM ANTI-503 / RETRY AUTOMÁTICO)
# ==============================================================================

def conectar(max_tentativas=4):
    """
    SOSA V2026: Conecta ao Google Sheets com retentativa automática (Exponential Backoff)
    blindando o sistema contra erros 503 (Service Unavailable) e 429 (Rate Limit).
    """
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    
    for tentativa in range(1, max_tentativas + 1):
        try:
            if os.path.exists("credentials.json"):
                creds = service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
            else:
                creds = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
            
            gc = gspread.authorize(creds)
            return gc.open("SOSA_DB_2026")
            
        except Exception as e:
            erro_str = str(e)
            
            if any(cod in erro_str for cod in ["503", "500", "502", "429", "UNAVAILABLE", "unavailable", "ResourceExhausted"]):
                if tentativa < max_tentativas:
                    time.sleep(tentativa * 1.2)
                    continue
            
            if tentativa == max_tentativas:
                if "429" in erro_str:
                    st.warning("⚠️ Limite de tráfego do Google Sheets (429). Aguarde alguns segundos...")
                elif any(c in erro_str for c in ["503", "UNAVAILABLE", "unavailable"]):
                    st.warning("⚠️ Servidores do Google Sheets momentaneamente instáveis (503). Recarregue a página.")
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
# 2. CARREGAMENTO DE DADOS (CACHE RESILIENTE ANTI-FALHA)
# ==============================================================================

@st.cache_data(ttl=300)
def carregar_tudo():
    wb_internal = conectar()
    if not wb_internal: 
        return None, [pd.DataFrame()] * 12

    def safe_get(conn, nome, colunas_padrao=[], max_retries=3):
        if not conn: return pd.DataFrame(columns=colunas_padrao)
        
        for t in range(max_retries):
            try:
                ws = conn.worksheet(nome)
                dados = ws.get_all_values() 
                if not dados or len(dados) < 1:
                    return pd.DataFrame(columns=colunas_padrao)
                
                linhas_validas = [r for r in dados[1:] if any(str(c).strip() for c in r)]
                if not linhas_validas:
                    return pd.DataFrame(columns=colunas_padrao)
                    
                df = pd.DataFrame(linhas_validas, columns=dados[0])
                df.columns = [str(c).strip().upper() for c in df.columns]
                
                for col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    if any(x in col for x in ["NOTA", "MEDIA", "VALOR", "SOMA"]):
                        df[col] = df[col].apply(util.sosa_to_float)
                    if col == "DATA" or "DATA" in col:
                        df[col] = df[col].apply(util.formatar_data_br)
                    if col == "ID_AVALIACAO":
                        df[col] = df[col].apply(util.sanitizar_nome_variante_soberana)

                return df
                
            except Exception as e: 
                if t < max_retries - 1 and any(c in str(e) for c in ["503", "500", "429", "UNAVAILABLE", "unavailable"]):
                    time.sleep(1.0)
                    continue
                print(f"Aviso ao carregar {nome}: {e}")
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
# 3. FUNÇÕES DE ESCRITA E ATUALIZAÇÃO (UPSERT & BATCH ATÔMICO)
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
    """MOTOR DE PROPAGAÇÃO EM CASCATA EM LOTE"""
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
        
        def update_tab_batch(aba, col_id, col_nome, col_turma=None):
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

        update_tab_batch("DB_DIARIO_BORDO", 1, 2, 3)
        update_tab_batch("DB_NOTAS", 0, 1, 2)
        update_tab_batch("DB_RELATORIOS", 1, 2, None)
        update_tab_batch("DB_GABARITOS_ALUNOS", 1, 2, 3)
        
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

def limpar_notas_turma_trimestre(turma, trimestre, forcar=False):
    """
    SOSA V2026.PRO - VACINA ANTI-DELEÇÃO ACIDENTAL:
    Apenas apaga registros do DB_NOTAS se forcar=True (durante consolidação explícita no Painel).
    Chamadas automáticas vindas do Scanner CIR apenas limpam o cache em memória,
    preservando 100% dos bônus manuais e notas lançadas pelo professor no banco.
    """
    st.cache_data.clear()
    if not forcar:
        return True
    try:
        wb = conectar()
        if not wb: return False
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
        service = build('drive', 'v3', credentials=creds) if creds else None
        
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]+)"

        for i, row in enumerate(dados):
            if i == 0: continue 
            linha_completa_txt = " ".join(map(str, row))
            
            if valor_conteudo in linha_completa_txt:
                if service:
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
        service = build('drive', 'v3', credentials=creds) if creds else None
        
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})"
        linha_para_deletar = -1
        
        for i, row in enumerate(dados):
            if i == 0: continue 
            if len(row) > 2 and row[1].strip() == semana.strip() and row[2].strip() == ano.strip():
                if service:
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
        service = build('drive', 'v3', credentials=creds) if creds else None
        
        ws_gaveta = wb.worksheet("DB_AULAS_PRONTAS")
        dados_gaveta = ws_gaveta.get_all_values()
        for i, row in enumerate(dados_gaveta):
            if i > 0 and row[2] == identificador:
                if service:
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
# MOTOR DE RELOCAÇÃO TEMPORAL EM CASCATA (SOSA V2026 - PRESERVAÇÃO DE DOCS)
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
    SOSA V2026: Muda a semana de um plano e de TODAS as suas aulas vinculadas em CASCATA,
    renomeando os títulos no Google Drive e PRESERVANDO 100% os arquivos Google Docs originais.
    Operações em lote para evitar erro 429.
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
        
        # 2. MIGRAÇÃO EM CASCATA EM LOTE: Atualiza a referência de TODAS as Aulas em DB_AULAS_PRONTAS
        try:
            ws_aulas = wb.worksheet("DB_AULAS_PRONTAS")
            dados_a = ws_aulas.get_all_values()
            ano_num = "".join(filter(str.isdigit, str(ano)))
            updates_aulas = []
            for j, row_a in enumerate(dados_a):
                if j > 0 and len(row_a) > 4 and row_a[1].strip() == semana_antiga.strip() and ano_num in row_a[4]:
                    updates_aulas.append(gspread.Cell(row=j+1, col=2, value=nova_semana.strip()))
            if updates_aulas:
                ws_aulas.update_cells(updates_aulas)
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
# 7. CONCILIADOR CRONOLÓGICO SOBERANO POR JANELA SEMANAL (SOSA V2026)
# ==============================================================================
def conciliar_calendario_e_planos_cronologicos(ano_alvo="6º"):
    """
    SOSA V2026: CONCILIADOR CRONOLÓGICO POR JANELA DE 7 DIAS.
    Re-indexa as semanas de DB_PLANOS em ordem cronológica e vincula
    automaticamente as aulas 'AVULSA / Registro via Diário' do DB_REGISTRO_AULAS em lote.
    """
    try:
        wb = conectar()
        if not wb: return False
        
        ano_num = "".join(filter(str.isdigit, str(ano_alvo)))
        
        ws_planos = wb.worksheet("DB_PLANOS")
        dados_p = ws_planos.get_all_values()
        if len(dados_p) <= 1: return False
        
        rows_p = dados_p[1:]
        
        planos_ano = []
        for idx_r, r in enumerate(rows_p):
            if len(r) > 2 and ano_num in str(r[2]):
                try:
                    dt_obj = datetime.strptime(r[0].strip(), "%d/%m/%Y")
                    planos_ano.append((dt_obj, idx_r + 2, r))
                except: pass
        
        planos_ano.sort(key=lambda x: x[0])
        
        intervalos_semanas = []
        updates_planos = []
        
        for seq_idx, (dt_obj, row_num, row_data) in enumerate(planos_ano, start=1):
            nova_sem_label = f"Semana {seq_idx:02d}"
            updates_planos.append(gspread.Cell(row=row_num, col=2, value=nova_sem_label))
            
            dt_inicio = dt_obj.date() if isinstance(dt_obj, datetime) else dt_obj
            dt_fim = dt_inicio + timedelta(days=6)
            
            plano_txt = row_data[5] if len(row_data) > 5 else ""
            obj_c = ai.extrair_tag(plano_txt, "OBJETO_CONHECIMENTO") or ai.extrair_tag(plano_txt, "CONTEUDOS_ESPECIFICOS") or "Conteúdo Programático"
            
            intervalos_semanas.append({
                "semana": nova_sem_label,
                "inicio": dt_inicio,
                "fim": dt_fim,
                "conteudo": obj_c
            })

        if updates_planos:
            ws_planos.update_cells(updates_planos)

        # RECONCILIAR E VINCULAR DB_REGISTRO_AULAS EM LOTE
        ws_reg = wb.worksheet("DB_REGISTRO_AULAS")
        dados_r = ws_reg.get_all_values()
        if len(dados_r) > 1:
            updates_reg = []
            for idx_r, r in enumerate(dados_r[1:], start=2):
                if len(r) >= 4 and ano_num in str(r[2]):
                    try:
                        dt_aula = datetime.strptime(r[0].strip(), "%d/%m/%Y").date()
                        sem_r = r[1].strip()
                        cont_r = r[3].strip()
                        
                        semana_encontrada = None
                        for window in intervalos_semanas:
                            if window["inicio"] <= dt_aula <= window["fim"]:
                                semana_encontrada = window["semana"]
                                break
                        
                        if semana_encontrada:
                            updates_reg.append(gspread.Cell(row=idx_r, col=2, value=semana_encontrada))
                            if sem_r == "AVULSA" or "Registro via Diário" in cont_r or cont_r == "":
                                novo_titulo = f"{ano_alvo} Ano - Aula - {semana_encontrada}"
                                updates_reg.append(gspread.Cell(row=idx_r, col=4, value=novo_titulo))
                    except Exception as e_row:
                        print(f"Erro linha {idx_r}: {e_row}")

            if updates_reg:
                ws_reg.update_cells(updates_reg)

        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro no conciliador: {e}")
        return False

# ==============================================================================
# MOTOR CANÔNICO DE ANTI-DUPLICIDADE E BAIXAS LIMPAS (SOSA V2026.MASTER)
# ==============================================================================

def normalizar_semana_chave(semana):
    """Extrai com segurança o rótulo da semana (ex: 'Semana 20') sem quebrar a tela."""
    if not semana or pd.isna(semana): return ""
    s_str = str(semana).strip()
    if " (" in s_str: return s_str.split(" (")[0].strip()
    if " - " in s_str: return s_str.split(" - ")[0].strip()
    return s_str

def excluir_plano_completo_canonico(semana, ano):
    """
    SOSA V2026: Apaga qualquer plano existente para a mesma SEMANA e ANO com correspondência canônica exata.
    """
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet("DB_PLANOS")
        dados = ws.get_all_values()
        if len(dados) <= 1: return True

        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds) if creds else None
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})"

        sem_alvo = normalizar_semana_chave(semana).upper()
        ano_alvo = "".join(filter(str.isdigit, str(ano)))

        linhas_para_deletar = []
        for i, row in enumerate(dados[1:], start=2):
            if len(row) > 2:
                sem_row = normalizar_semana_chave(row[1]).upper()
                ano_row = "".join(filter(str.isdigit, str(row[2])))
                
                if sem_row == sem_alvo and ano_row == ano_alvo:
                    if service:
                        linha_txt = " ".join(map(str, row))
                        ids_encontrados = re.findall(padrao_id, linha_txt)
                        for file_id in ids_encontrados:
                            try: service.files().delete(fileId=file_id).execute()
                            except: pass
                    linhas_para_deletar.append(i)

        for idx in reversed(linhas_para_deletar):
            ws.delete_rows(idx)

        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro na exclusão canônica de plano: {e}")
        return False

def excluir_aula_pronta_canonica(semana_ref, tipo_material, ano):
    """
    SOSA V2026: Remove registros e arquivos duplicados de aulas e materiais em DB_AULAS_PRONTAS.
    """
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet("DB_AULAS_PRONTAS")
        dados = ws.get_all_values()
        if len(dados) <= 1: return True

        creds = obter_creds_drive()
        service = build('drive', 'v3', credentials=creds) if creds else None
        padrao_id = r"(?:/d/|id=)([a-zA-Z0-9-_]{25,})"

        sem_alvo = normalizar_semana_chave(semana_ref).upper()
        tipo_alvo = str(tipo_material).strip().upper()
        ano_alvo = "".join(filter(str.isdigit, str(ano)))

        linhas_para_deletar = []
        for i, row in enumerate(dados[1:], start=2):
            if len(row) > 4:
                sem_row = normalizar_semana_chave(row[1]).upper()
                tipo_row = str(row[2]).strip().upper()
                ano_row = "".join(filter(str.isdigit, str(row[4])))

                if (sem_row == sem_alvo or sem_alvo in sem_row) and (tipo_row == tipo_alvo or tipo_alvo in tipo_row) and ano_row == ano_alvo:
                    if service:
                        linha_txt = " ".join(map(str, row))
                        ids_encontrados = re.findall(padrao_id, linha_txt)
                        for file_id in ids_encontrados:
                            try: service.files().delete(fileId=file_id).execute()
                            except: pass
                    linhas_para_deletar.append(i)

        for idx in reversed(linhas_para_deletar):
            ws.delete_rows(idx)

        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro na exclusão canônica de aula: {e}")
        return False

def dar_baixa_plano_evento(semana, ano, motivo_ou_status="RECESSO", data_str="N/A", turma="GLOBAL"):
    """
    SOSA V2026: Dá baixa limpa em uma semana de recesso, feriado ou evento,
    marcando o status em DB_PLANOS como CONCLUIDO_RECESSO/EVENTO sem gerar arquivos.
    """
    try:
        wb = conectar()
        if not wb: return False
        
        sem_limpa = normalizar_semana_chave(semana)
        ano_num = "".join(filter(str.isdigit, str(ano)))
        ano_fmt = f"{ano_num}º" if ano_num else str(ano)
        status_chave = f"CONCLUIDO_{str(motivo_ou_status).upper().replace(' ', '_')}"

        ws_planos = wb.worksheet("DB_PLANOS")
        dados_p = ws_planos.get_all_values()
        
        encontrado = False
        for i, row in enumerate(dados_p[1:], start=2):
            if len(row) > 2:
                if normalizar_semana_chave(row[1]).upper() == sem_limpa.upper() and "".join(filter(str.isdigit, str(row[2]))) == ano_num:
                    ws_planos.update_cell(i, 5, status_chave)
                    encontrado = True
                    break
        
        if not encontrado:
            txt_plano_evento = f"[OBJETO_CONHECIMENTO] {str(motivo_ou_status).upper()} \n[CONTEUDOS_ESPECIFICOS] {motivo_ou_status} \n[AULA_1] N/A (Recesso / Evento / Feriado) \n[AULA_2] N/A \n--- LINK DRIVE --- N/A"
            ws_planos.append_row([
                data_str if data_str != "N/A" else datetime.now().strftime("%d/%m/%Y"), 
                sem_limpa, 
                ano_fmt, 
                "II Trimestre" if "20" in sem_limpa or "21" in sem_limpa else "I Trimestre", 
                status_chave, 
                txt_plano_evento, 
                "N/A"
            ], value_input_option="USER_ENTERED")

        if turma != "GLOBAL" and data_str != "N/A":
            limpar_diario_data_turma(data_str, turma)
            salvar_no_banco("DB_DIARIO_BORDO", [data_str, "GLOBAL", "TODOS OS ALUNOS", turma, "ISENTO", "DIA NÃO LETIVO", str(motivo_ou_status), "0,00"])
            salvar_no_banco("DB_REGISTRO_AULAS", [data_str, sem_limpa, turma, f"EVENTO/RECESSO: {motivo_ou_status}", "N/A", "N/A", "NÃO LETIVO", "", ""])

        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro ao dar baixa em evento/recesso: {e}")
        return False

def dar_baixa_aula_livro_offline(semana, ano, turma="GLOBAL", data_str="N/A", detalhes_livro="Conteúdo aplicado via Livro/Lousa"):
    """
    SOSA V2026: Registra a aula ministrada via Livro/Lousa no Diário de Bordo (DB_REGISTRO_AULAS)
    e arquiva o plano em DB_PLANOS como CONCLUIDO_LIVRO, fazendo a semana sumir do Criador de Aulas.
    """
    try:
        wb = conectar()
        if not wb: return False
        
        sem_limpa = normalizar_semana_chave(semana)
        ano_num = "".join(filter(str.isdigit, str(ano)))
        ano_fmt = f"{ano_num}º" if ano_num else str(ano)

        ws_planos = wb.worksheet("DB_PLANOS")
        dados_p = ws_planos.get_all_values()
        
        encontrado = False
        for i, row in enumerate(dados_p[1:], start=2):
            if len(row) > 2:
                if normalizar_semana_chave(row[1]).upper() == sem_limpa.upper() and "".join(filter(str.isdigit, str(row[2]))) == ano_num:
                    ws_planos.update_cell(i, 5, "CONCLUIDO_LIVRO")
                    encontrado = True
                    break

        if not encontrado:
            txt_plano_offline = f"[OBJETO_CONHECIMENTO] AULA CUMPRIDA VIA LIVRO DIDÁTICO \n[CONTEUDOS_ESPECIFICOS] {detalhes_livro} \n[AULA_1] Ministrada via Livro Didático / Lousa \n[AULA_2] Exercícios do Livro \n--- LINK DRIVE --- N/A"
            ws_planos.append_row([
                data_str if data_str != "N/A" else datetime.now().strftime("%d/%m/%Y"), 
                sem_limpa, 
                ano_fmt, 
                "I Trimestre", 
                "CONCLUIDO_LIVRO", 
                txt_plano_offline, 
                "N/A"
            ], value_input_option="USER_ENTERED")

        ws_reg = wb.worksheet("DB_REGISTRO_AULAS")
        conteudo_reg = f"Livro Didático / Lousa ({detalhes_livro})"
        ws_reg.append_row([
            data_str if data_str != "N/A" else datetime.now().strftime("%d/%m/%Y"),
            sem_limpa,
            turma if turma and turma != "GLOBAL" else f"{ano_num}º Ano",
            conteudo_reg,
            "Acompanhamento em Sala",
            "N/A",
            "🟢 Concluído (Livro)",
            "CONCLUIDO_OFFLINE",
            "Normal"
        ], value_input_option="USER_ENTERED")

        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro ao dar baixa burocrática em aula de livro: {e}")
        return False

# ==============================================================================
# 8. MOTOR DE SOBERANIA REGIMENTAL (VISTOS, CADEADO & CONTROLE ATITUDINAL)
# ==============================================================================

def isentar_vistos_data_turma(data_str, turma):
    """Transforma todas as chamadas de visto de uma data em 'ISENTO' em lote."""
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet("DB_DIARIO_BORDO")
        dados = ws.get_all_values()
        updates = []
        for i, row in enumerate(dados):
            if i > 0 and len(row) > 4:
                if row[0].strip() == data_str.strip() and row[3].strip() == turma.strip():
                    updates.append(gspread.Cell(row=i + 1, col=5, value="ISENTO"))
        if updates:
            ws.update_cells(updates)
            st.cache_data.clear()
            return True
        return False
    except Exception as e:
        print(f"Erro ao isentar visto: {e}")
        return False

def ajustar_bonus_punicao_diario(data_str, id_aluno, turma, novo_bonus_str, nova_obs_sufixo=""):
    """Permite perdoar punições ou revogar bônus com registro no Diário."""
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet("DB_DIARIO_BORDO")
        dados = ws.get_all_values()
        id_busca = str(limpar_id(id_aluno))
        for i, row in enumerate(dados):
            if i > 0 and len(row) > 7:
                if row[0].strip() == data_str.strip() and limpar_id(row[1]) == id_busca and row[3].strip() == turma.strip():
                    obs_antiga = row[6]
                    obs_final = f"{obs_antiga} | {nova_obs_sufixo}".strip(" | ") if nova_obs_sufixo else obs_antiga
                    ws.update_cell(i + 1, 7, obs_final)
                    ws.update_cell(i + 1, 8, novo_bonus_str)
                    st.cache_data.clear()
                    return True
        return False
    except Exception as e:
        print(f"Erro ao ajustar bônus: {e}")
        return False

def salvar_refaccao_soberana(data_str, id_aluno, nome_aluno, turma, pts_refaccao, alvo_refaccao):
    """
    SOSA V2026 - GRAVAÇÃO DE REFACÇÃO COM UPSERT BLINDADO (ANTI-DUPLICIDADE):
    Apaga qualquer registro anterior de refacção do aluno antes de gravar o novo bônus,
    impedindo que múltiplos cliques acumulem pontos indevidos.
    """
    try:
        wb = conectar()
        if not wb: return False
        ws = wb.worksheet("DB_DIARIO_BORDO")
        dados = ws.get_all_values()
        id_clean = str(limpar_id(id_aluno))
        
        linhas_para_deletar = []
        for i in range(1, len(dados)):
            row = dados[i]
            if len(row) > 6 and str(limpar_id(row[1])) == id_clean and row[3].strip() == turma.strip():
                if "Refacção" in str(row[6]) or "Refaccao" in str(row[6]) or "REFACÇÃO" in str(row[6]) or "SISTEMA_NOTA" in str(row[5]):
                    linhas_para_deletar.append(i + 1)
                    
        for idx_del in reversed(linhas_para_deletar):
            ws.delete_rows(idx_del)
            
        if pts_refaccao > 0:
            nome_limpo = str(nome_aluno).replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
            ws.append_row([
                data_str, id_clean, nome_limpo, turma, "TRUE", "SISTEMA_NOTA",
                f"Refacção de Avaliação ({alvo_refaccao})", util.sosa_to_str(pts_refaccao)
            ], value_input_option="USER_ENTERED")
            
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro no salvamento de refacção: {e}")
        return False

def salvar_config_corte_trimestre(turma, trimestre, data_corte_str):
    tipo_chave = f"CORTE_TRIMESTRE_{turma}_{trimestre.replace(' ', '_').upper()}"
    return salvar_ata_conselho(datetime.now().strftime("%d/%m/%Y"), turma, tipo_chave, data_corte_str)

def obter_config_corte_trimestre(turma, trimestre):
    try:
        wb = conectar()
        if not wb: return None
        ws = wb.worksheet("DB_RELATORIOS")
        dados = ws.get_all_values()
        tipo_chave = f"CORTE_TRIMESTRE_{turma}_{trimestre.replace(' ', '_').upper()}"
        for i in range(len(dados) - 1, 0, -1):
            row = dados[i]
            if len(row) > 4 and row[2] == turma and row[3] == tipo_chave:
                return row[4].strip()
        return None
    except:
        return None

def transferir_titularidade_gabarito(id_origem, nome_origem, id_destino, nome_destino, turma, trimestre, id_avaliacao, status_origem_apos="PENDENTE"):
    """
    SOSA V2026.MASTER - TROCA DE TITULARIDADE SOBERANA:
    Transfere o gabarito, nota e evidência da prova de um aluno para o verdadeiro dono.
    """
    try:
        wb = conectar()
        if not wb: return False
        
        id_origem_clean = str(limpar_id(id_origem))
        id_destino_clean = str(limpar_id(id_destino))
        nome_curto_av = id_avaliacao.split("-")[0].strip()
        
        ws_gab = wb.worksheet("DB_GABARITOS_ALUNOS")
        dados_gab = ws_gab.get_all_values()
        
        registro_origem = None
        for i in range(1, len(dados_gab)):
            row = dados_gab[i]
            if len(row) > 4 and row[3] == turma and nome_curto_av in row[4]:
                if str(limpar_id(row[1])) == id_origem_clean:
                    registro_origem = row
                    break
                    
        if not registro_origem:
            return False
            
        data_prova = registro_origem[0]
        id_av_real = registro_origem[4]
        respostas_aluno = registro_origem[5]
        nota_calc = registro_origem[6]
        link_foto = registro_origem[7] if len(registro_origem) > 7 else "N/A"
        
        for i in range(len(dados_gab) - 1, 0, -1):
            row = dados_gab[i]
            if len(row) > 4 and row[3] == turma and nome_curto_av in row[4]:
                if str(limpar_id(row[1])) == id_destino_clean:
                    ws_gab.delete_rows(i + 1)
        
        salvar_no_banco("DB_GABARITOS_ALUNOS", [
            data_prova, id_destino_clean, nome_destino, turma, id_av_real, respostas_aluno, nota_calc, link_foto
        ])
        
        dados_gab_atual = ws_gab.get_all_values()
        for i in range(len(dados_gab_atual) - 1, 0, -1):
            row = dados_gab_atual[i]
            if len(row) > 4 and row[3] == turma and nome_curto_av in row[4]:
                if str(limpar_id(row[1])) == id_origem_clean:
                    if "PENDENTE" in status_origem_apos.upper():
                        ws_gab.delete_rows(i + 1)
                    elif "FALTOU" in status_origem_apos.upper() or "JUSTIFICADO" in status_origem_apos.upper():
                        ws_gab.update_cell(i + 1, 6, status_origem_apos)
                        ws_gab.update_cell(i + 1, 7, "0,00")
                        ws_gab.update_cell(i + 1, 8, "N/A")
                        
        st.cache_data.clear()
        return True
    except Exception as e:
        print(f"Erro ao transferir titularidade: {e}")
        return False

def executar_saneamento_banco_soberano():
    """
    SOSA V2026 - MOTOR DE SANEAMENTO ATÔMICO UNIVERSAL BLINDADO:
    1. Higieniza datas seriais (46259, 46270 -> DD/MM/YYYY).
    2. Dedupica refacções acumuladas por múltiplos cliques.
    3. PRESERVA bônus manuais já existentes em DB_NOTAS (regra do maior valor: max(banco, live)).
    4. Estende a janela do II Trimestre até 11/09/2026 para acolher a recuperação.
    """
    wb = conectar()
    if not wb:
        return False, "Falha de conexão com o Google Sheets."

    relatorio_execucao = []

    try:
        # 1. SANEAMENTO DE DATAS SERIAIS EM TODAS AS ABAS
        for aba_nome in ["DB_RELATORIOS", "DB_AULAS_PRONTAS", "DB_GABARITOS_ALUNOS"]:
            try:
                ws_temp = wb.worksheet(aba_nome)
                dados_temp = ws_temp.get_all_values()
                if len(dados_temp) > 1:
                    mod_d = False
                    for idx in range(1, len(dados_temp)):
                        dt_val = str(dados_temp[idx][0]).strip()
                        if dt_val.isdigit() and len(dt_val) == 5:
                            dados_temp[idx][0] = util.formatar_data_br(dt_val)
                            mod_d = True
                    if mod_d:
                        ws_temp.clear()
                        ws_temp.update(values=dados_temp, range_name='A1')
            except Exception as e_dt:
                print(f"Aviso serial {aba_nome}: {e_dt}")

        # 2. DEDUPLICAÇÃO BLINDADA DO DIÁRIO (LIMITA A 1 REFACÇÃO POR ALUNO NO TRIMESTRE)
        ws_diario = wb.worksheet("DB_DIARIO_BORDO")
        dados_diario = ws_diario.get_all_values()
        
        if len(dados_diario) > 1:
            header_d = dados_diario[0]
            rows_d = dados_diario[1:]

            diario_dedup = {}
            refaccao_rastreada = set()

            for r in rows_d:
                dt_k = util.formatar_data_br(r[0])
                id_k = limpar_id(r[1])
                turma_k = str(r[3]).strip()
                visto_k = str(r[4]).strip().upper()
                tag_k = str(r[5]).strip()
                obs_k = str(r[6]).strip()
                bonus_k = util.sosa_to_float(r[7])

                is_refaccao_entry = ("Refacção" in obs_k or "Refaccao" in obs_k or "REFACÇÃO" in obs_k or tag_k == "SISTEMA_NOTA")
                if is_refaccao_entry:
                    chave_ref = (id_k, turma_k)
                    if chave_ref in refaccao_rastreada:
                        continue
                    refaccao_rastreada.add(chave_ref)
                    bonus_k = 0.50

                chave = (dt_k, id_k, turma_k, tag_k if is_refaccao_entry else "")

                if chave not in diario_dedup:
                    diario_dedup[chave] = {
                        "data": dt_k, "id": id_k, "nome": r[2], "turma": turma_k,
                        "visto": visto_k, "tag": tag_k, "obs": obs_k, "bonus": bonus_k
                    }
                else:
                    if visto_k == "TRUE": diario_dedup[chave]["visto"] = "TRUE"
                    if tag_k and tag_k != "AUSÊNCIA": diario_dedup[chave]["tag"] = tag_k
                    if obs_k and obs_k not in diario_dedup[chave]["obs"]:
                        diario_dedup[chave]["obs"] = f"{diario_dedup[chave]['obs']} | {obs_k}".strip(" | ")
                    if not is_refaccao_entry and bonus_k != 0:
                        diario_dedup[chave]["bonus"] = round(diario_dedup[chave]["bonus"] + bonus_k, 2)

            linhas_diario_finais = [header_d]
            for reg in diario_dedup.values():
                b_str = f"{reg['bonus']:.2f}".replace(".", ",") if reg['bonus'] != 0 else "0,00"
                linhas_diario_finais.append([
                    reg["data"], reg["id"], reg["nome"], reg["turma"],
                    reg["visto"], reg["tag"], reg["obs"], b_str
                ])

            ws_diario.clear()
            ws_diario.update(values=linhas_diario_finais, range_name='A1')
            relatorio_execucao.append("✅ DB_DIARIO_BORDO: Deduplicado com preservação atitudinal.")

        # 3. RECONSOLIDAÇÃO SOBERANA COM PRESERVAÇÃO DE BÔNUS MANUAIS DO BANCO
        ws_alunos = wb.worksheet("DB_ALUNOS")
        dados_alunos = ws_alunos.get_all_values()
        alunos_dict = {limpar_id(r[0]): {"id": limpar_id(r[0]), "nome": r[1], "turma": r[2]} for r in dados_alunos[1:]}

        ws_notas = wb.worksheet("DB_NOTAS")
        dados_notas_atuais = ws_notas.get_all_values()
        
        # Mapeia notas que o professor já havia alterado/bonificado manualmente no DB_NOTAS
        mapa_banco_existente = {}
        for r_n in dados_notas_atuais[1:]:
            if len(r_n) > 8:
                chave_n = (limpar_id(r_n[0]), str(r_n[2]).strip(), str(r_n[3]).strip())
                mapa_banco_existente[chave_n] = {
                    "c1": util.sosa_to_float(r_n[4]),
                    "c2": util.sosa_to_float(r_n[5]),
                    "c3": util.sosa_to_float(r_n[6]),
                    "rec": util.sosa_to_float(r_n[7]),
                    "media": util.sosa_to_float(r_n[8])
                }

        ws_gab = wb.worksheet("DB_GABARITOS_ALUNOS")
        dados_gab = ws_gab.get_all_values()

        df_d_clean = pd.DataFrame(linhas_diario_finais[1:], columns=[c.upper() for c in header_d])
        df_g_clean = pd.DataFrame(dados_gab[1:], columns=[c.upper() for c in dados_gab[0]])

        # Janela do II Trimestre estendida para 11/09/2026 para acolher a recuperação de 05/09!
        trims_config = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 11)),
            "III Trimestre": (date(2026, 9, 12), date(2026, 12, 17))
        }

        novas_linhas_notas = [["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]]

        for trim_nome, (dt_inicio, dt_fim) in trims_config.items():
            padrao_t_reg = util.obter_regex_trimestre(trim_nome)

            for id_aluno, al_info in alunos_dict.items():
                turma_al = al_info["turma"]
                nome_al = al_info["nome"]

                vistos_live = 0.0
                bonus_live = 0.0

                if not df_d_clean.empty:
                    df_d_sub = df_d_clean[(df_d_clean['ID_ALUNO'].apply(limpar_id) == id_aluno) & (df_d_clean['TURMA'] == turma_al)].copy()
                    if not df_d_sub.empty:
                        df_d_sub['DT_OBJ'] = pd.to_datetime(df_d_sub['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                        df_d_trim = df_d_sub[(df_d_sub['DT_OBJ'] >= dt_inicio) & (df_d_sub['DT_OBJ'] <= dt_fim)]
                        
                        if not df_d_trim.empty:
                            validas = df_d_trim[df_d_trim['VISTO_ATIVIDADE'].str.upper() != "ISENTO"]
                            tot_v = len(validas['DATA'].unique()) if not validas.empty else 1
                            if tot_v == 0: tot_v = 1
                            v_ok = len(validas[validas['VISTO_ATIVIDADE'].str.upper() == "TRUE"])
                            vistos_live = round((v_ok / tot_v * 3.0), 2)
                            bonus_live = df_d_trim['BONUS'].apply(util.sosa_to_float).sum()

                teste_live = 0.0
                prova_live = 0.0
                rec_live = -1.0

                if not df_g_clean.empty:
                    df_g_sub = df_g_clean[(df_g_clean['ID_ALUNO'].apply(limpar_id) == id_aluno) & (df_g_clean['TURMA'] == turma_al)]
                    if not df_g_sub.empty:
                        for _, r_g in df_g_sub.iterrows():
                            av_id_txt = str(r_g['ID_AVALIACAO']).upper()
                            resp_g_txt = str(r_g['RESPOSTAS_ALUNO']).upper()
                            
                            if re.search(padrao_t_reg, av_id_txt):
                                if resp_g_txt.startswith("FALTOU_INJUSTIFICADO") or resp_g_txt == "FALTOU":
                                    n_g = 0.0
                                else:
                                    n_g = util.sosa_to_float(r_g['NOTA_CALCULADA'])

                                if any(x in av_id_txt for x in ["RECUPERAÇÃO", "RECUPERACAO", "REC_"]):
                                    rec_live = n_g
                                elif any(x in av_id_txt for x in ["TESTE", "SIMULADO", "TRABALHO"]) and "SONDA" not in av_id_txt:
                                    teste_live = max(teste_live, n_g)
                                elif any(x in av_id_txt for x in ["PROVA", "AVALIAÇÃO", "AVALIACAO", "EXAME", "2ª"]):
                                    prova_live = max(prova_live, n_g)

                # BLINDAGEM SOBERANA: Se o professor já tinha dado nota maior no banco com bônus, preserva a maior!
                dados_antigos = mapa_banco_existente.get((id_aluno, turma_al, trim_nome), {})
                c1_final_base = max(dados_antigos.get("c1", 0.0), vistos_live)
                teste_final = max(dados_antigos.get("c2", 0.0), teste_live)
                prova_final = max(dados_antigos.get("c3", 0.0), prova_live)
                rec_final = max(dados_antigos.get("rec", -1.0), rec_live)

                c1_final = min(3.0, c1_final_base + max(0.0, bonus_live))
                rem_b = max(0.0, bonus_live) - (c1_final - c1_final_base)
                c2_final = min(3.0, teste_final + max(0.0, rem_b))
                rem_b -= (c2_final - teste_final)
                c3_final = min(4.0, prova_final + max(0.0, rem_b))

                soma_bruta = c1_final + c2_final + c3_final
                media_calculada = min(10.0, round(soma_bruta * 2) / 2)

                if rec_final > 0 and media_calculada < 6.0:
                    media_com_rec = (media_calculada + rec_final) / 2.0
                    media_final = min(10.0, max(media_calculada, round(media_com_rec * 2) / 2))
                else:
                    media_final = media_calculada

                # Preserva média manual lançada no conselho se for superior
                media_salvar = max(media_final, dados_antigos.get("media", 0.0))

                novas_linhas_notas.append([
                    id_aluno, nome_al, turma_al, trim_nome,
                    f"{c1_final_base:.2f}".replace(".", ","),
                    f"{teste_final:.2f}".replace(".", ","),
                    f"{prova_final:.2f}".replace(".", ","),
                    f"{rec_final:.2f}".replace(".", ",") if rec_final >= 0 else "-1",
                    f"{media_salvar:.1f}".replace(".", ",")
                ])

        ws_notas.clear()
        ws_notas.update(values=novas_linhas_notas, range_name='A1')
        relatorio_execucao.append("✅ DB_NOTAS: Consolidação concluída com proteção não-regressiva de bônus!")

        st.cache_data.clear()
        return True, "\n".join(relatorio_execucao)

    except Exception as e:
        return False, f"Erro durante o saneamento: {str(e)}"
