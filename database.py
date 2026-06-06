import os
import re
import base64
import requests
import gspread
import pandas as pd
import streamlit as st
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
import utils as util

# ==============================================================================
# 1. CONEXÃO E CREDENCIAIS
# ==============================================================================

def conectar():
    try:
        scope =["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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
    scope =["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
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
            df.columns =[str(c).strip().upper() for c in df.columns]
            
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

    cols_planos =["DATA", "SEMANA", "ANO", "TURMA", "EIXO", "PLANO_TEXTO", "LINK_DRIVE"]
    cols_aulas =["DATA", "SEMANA_REF", "TIPO_MATERIAL", "CONTEUDO", "ANO", "LINK_DRIVE"]
    cols_alunos =["ID", "NOME_ALUNO", "TURMA", "STATUS", "NECESSIDADES", "ORIGEM"]
    cols_relatorios =["DATA", "ID_ALUNO", "NOME_ALUNO", "TIPO", "CONTEUDO"]
    cols_diario =["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "VISTO_ATIVIDADE", "TAGS", "OBSERVACOES", "BONUS"]
    cols_registro =["DATA", "SEMANA", "TURMA", "CONTEUDO_MINISTRADO", "ADAPTACAO_PEI", "STATUS_CURRICULO"]
    cols_notas =["ID_ALUNO", "NOME_ALUNO", "TURMA", "TRIMESTRE", "NOTA_VISTOS", "NOTA_TESTE", "NOTA_PROVA", "NOTA_REC", "MEDIA_FINAL"]
    cols_diagnosticos =["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "ID_AVALIACAO", "RESPOSTAS_ALUNO", "NOTA_CALCULADA", "LINK_FOTO_DRIVE"]

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
        ws = wb.worksheet(aba_nome)
        ws.append_rows(lista_de_linhas, value_input_option="USER_ENTERED")
        st.cache_data.clear()
        return True
    except: return False

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
                updates =[]
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
        
        nova_linha =[data, "AVULSA", turma, "Registro via Diário", "N/A", "N/A", status, ponte, clima]
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
            if len(row) > 3 and row[3] == valor_conteudo:
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
        
        # 🚨 LEI DAS TAGS PROTEGIDAS: Estes registros NUNCA serão apagados pelo Diário Rápido
        tags_protegidas =["SISTEMA_NOTA", "ARGUIÇÃO", "NOTA_EXTERNA"]
        
        indices =[]
        for i, row in enumerate(dados):
            if i > 0 and len(row) > 5:
                # Se for a mesma data, mesma turma, e NÃO for uma tag protegida, marca para deletar
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
        indices =[i + 1 for i, row in enumerate(dados) if i > 0 and len(row) > 3 and row[2] == turma and row[3] == trimestre]
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
        indices_para_deletar =[i + 1 for i, row in enumerate(dados_cron) if i > 0 and tipo_prova_nome in row[3]]
        
        for idx in reversed(indices_para_deletar):
            ws_cron.delete_rows(idx)
            
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Erro na exclusão em cascata: {e}")
        return False

# ==============================================================================
# 5. INTEGRAÇÃO COM GOOGLE DRIVE (SOSA BRIDGE V45.4 - PERSONAL DRIVE)
# ==============================================================================
def subir_e_converter_para_google_docs(file_stream, nome_arquivo, trimestre="I Trimestre", categoria="6º Ano", semana="Semana Geral", modo="AULA"):
    """
    SOSA BRIDGE V45.4 (RESTORED): Retorna ao método original do Google Apps Script
    para gravar os arquivos diretamente no seu Drive Pessoal, usando a sua cota de espaço enorme.
    """
    try:
        # 🚨 ATENÇÃO: Se o senhor gerou um novo link de script, substitua nesta linha abaixo:
        URL_DA_PONTE = "https://script.google.com/macros/s/AKfycbzO1V0EyL8jp571wM_ulvK0RDiha6FFXTmCT67cqihyMXveoHcxQ7w5PP-MA3HU7Z_1MA/exec" 
        
        if isinstance(file_stream, bytes):
            file_b64 = base64.b64encode(file_stream).decode('utf-8')
        else:
            file_stream.seek(0)
            file_b64 = base64.b64encode(file_stream.read()).decode('utf-8')
        
        payload = {
            "fileName": nome_arquivo, 
            "trimestre": trimestre, 
            "categoria": categoria, 
            "semanaRef": semana, 
            "modo": modo, 
            "fileB64": file_b64
        }
        
        response = requests.post(URL_DA_PONTE, json=payload, timeout=60)
        resposta_texto = response.text.strip()
        
        # Se o Google Apps Script responder com a URL oficial do Docs, salva com sucesso
        if "google.com" in resposta_texto and "https://" in resposta_texto and len(resposta_texto) < 250:
            return resposta_texto
        else:
            # Se o script falhar ou retornar uma página de erro, repassa o erro para o main.py exibir
            return f"ERRO_PONTE_GOOGLE: {resposta_texto[:250]}"
            
    except Exception as e:
        return f"ERRO_CONEXAO_PONTE: {str(e)}"
