import streamlit as st
import pandas as pd
from datetime import date, datetime
import database as db
import ai_engine as ai
import utils as util
from google.genai import types
import time
import os
import plotly.express as px
import exporter
import re
import ai_engine as ai  # <--- ADICIONE ESTA LINHA AQUI


st.set_page_config(page_title="SOSA 2026 | Master Intelligence", layout="wide", page_icon="🏫")

# --- CONTROLE DE TEMA (DESIGN PREMIUM CORRIGIDO) ---
with st.sidebar:
    tema_selecionado = st.radio("Visual do Sistema:", ["🌙 Dark Mode", "🌞 Light Mode"], horizontal=True)

# --- DEFINIÇÃO DA PALETA DE CORES ---
BRAND_BLUE = "#2962FF" 
BRAND_NAVY = "#000B1A" 

if tema_selecionado == "🌙 Dark Mode":
    cor_fundo = BRAND_NAVY
    cor_texto = "#FFFFFF"
    cor_sidebar = "#001226"
    cor_card_bg = "#001E3C"
    cor_card_borda = "#003366"
    cor_titulo_card = "#A0AEC0"
else:
    cor_fundo = "#F8FAFC"
    cor_texto = "#1A202C"  # Texto bem escuro para o Light Mode
    cor_sidebar = "#FFFFFF"
    cor_card_bg = "#FFFFFF"
    cor_card_borda = "#E2E8F0"
    cor_titulo_card = "#4A5568"

# --- INJEÇÃO DE CSS DINÂMICO (CORREÇÃO DE CONTRASTE) ---
st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
        * {{ font-family: 'Inter', sans-serif; }}

        .stApp {{
            background-color: {cor_fundo} !important;
            color: {cor_texto} !important;
        }}

        /* FORÇAR COR DO TEXTO EM TODO O SISTEMA */
        p, span, label, h1, h2, h3, .stMarkdown {{
            color: {cor_texto} !important;
        }}
        
        /* SIDEBAR */
        [data-testid="stSidebar"] {{
            background-color: {cor_sidebar} !important;
            border-right: 1px solid {cor_card_borda};
        }}
        
        /* CORRIGIR TEXTO DOS BOTÕES DE RÁDIO (NAVEGAÇÃO) */
        div[role="radiogroup"] label p {{
            color: {cor_texto} !important;
            font-weight: 500;
        }}

        /* BOTÃO SELECIONADO (AZUL DA LOGO) */
        div[role="radiogroup"] label[aria-checked="true"] {{
            background-color: {BRAND_BLUE}22 !important;
            border: 1px solid {BRAND_BLUE} !important;
        }}
        
        div[role="radiogroup"] label[aria-checked="true"] p {{
            color: {BRAND_BLUE} !important;
            font-weight: 700;
        }}

        /* CARDS DE MÉTRICAS */
        div[data-testid="stMetric"] {{
            background-color: {cor_card_bg} !important;
            border: 1px solid {cor_card_borda} !important;
            border-radius: 16px;
        }}
        
        div[data-testid="stMetricLabel"] p {{
            color: {cor_titulo_card} !important;
        }}
        
        div[data-testid="stMetricValue"] div {{
            color: {BRAND_BLUE} !important;
        }}

        /* INPUTS E SELECTBOXES */
        .stSelectbox div[data-baseweb="select"] {{
            background-color: {cor_card_bg} !important;
            color: {cor_texto} !important;
        }}
        
        /* CORRIGIR TEXTO DENTRO DO SELECTBOX */
        div[data-testid="stSelectbox"] p {{
            color: {cor_texto} !important;
        }}

        /* BOTÕES DE AÇÃO */
        .stButton button {{
            background-color: {BRAND_BLUE} !important;
            color: white !important;
            border-radius: 10px !important;
            font-weight: 700 !important;
        }}
    </style>
""", unsafe_allow_html=True)

# --- CARREGAMENTO ---
wb, (df_alunos, df_curriculo, df_materiais, df_planos, df_aulas, df_notas, df_diario, df_turmas, df_relatorios, df_horarios, df_registro_aulas, df_diagnosticos) = db.carregar_tudo()
# --- SIDEBAR COM LOGOTIPO ---
with st.sidebar:
    try:
        col_esq, col_meio, col_dir = st.columns([1, 2, 1])
        with col_meio:
            st.image("logo.png", width=100) 
    except:
        st.markdown("### 🏫 **SOSA**")
    
    st.markdown("<h3 style='text-align: center; margin-top: -15px; font-size: 14px;'>Maestro V14</h3>", unsafe_allow_html=True)
    st.markdown("---")

    if st.sidebar.button("🚨 Resetar Espaço do Drive"):
        msg = db.limpar_todo_drive_da_conta_servico()
        st.sidebar.success(msg)
    
    if st.button("🔄 Sincronizar Dados"):
        st.cache_data.clear()
        st.rerun()
    
def prensa_hidraulica_texto(texto, label):
    # Remove o rótulo se a IA insistir em escrever, independente de maiúscula/minúscula ou acento
    limpo = texto.replace(label, "").replace(label.upper(), "").replace(label.lower(), "")
    # Remove os dois pontos iniciais que costumam sobrar
    if limpo.startswith(":") or limpo.startswith(" :"):
        limpo = limpo.split(":", 1)[-1]
    return limpo.strip()

# MENU DE NAVEGAÇÃO
menu = st.sidebar.radio("Navegação:", [
    "📅 Planejamento (Ponto ID)",
    "🧪 Criador de Aulas",
    "📝 Central de Avaliações",
    "📸 Scanner de Gabaritos",
    "📝 Diário de Bordo Rápido",
    "📊 Painel de Notas & Vistos",
    "📈 Boletim Anual & Conselho",
    "👥 Gestão da Turma",
    "📚 Base de Conhecimento",
    "♿ Relatórios PEI / Perfil IA"
])


# ==============================================================================
# FUNÇÃO AUXILIAR DE VISUALIZAÇÃO HÍBRIDA (VERSÃO V25.11 - CONTEXTUAL)
# ==============================================================================
# --- FUNÇÃO DE VISUALIZAÇÃO V25.85 ---
def exibir_material_estruturado(texto_raw, key_prefix, dados_plano=None, info_aula=None):
    """
    Versão V25.90: Híbrida e Blindada. 
    Detecta automaticamente se é PLANEJAMENTO ou AULA.
    """
    if info_aula is None: info_aula = {}
    
    # Extração de Metadados
    f_aula = info_aula.get("aula", "Aula Geral")
    f_ano = info_aula.get("ano", "6")
    f_semana = info_aula.get("semana", "Semana Geral")
    f_trimestre = info_aula.get("trimestre", "I Trimestre")
    f_categoria = f"{f_ano}ano" # Formato esperado pelo Apps Script

    # --- LÓGICA DE DETECÇÃO DE CONTEÚDO ---
    if dados_plano:
        # MODO PLANEJAMENTO: Usa as tags MARKER_
        ed_met = ai.extrair_tag(texto_raw, "METODOLOGIA")
        ed_obj = ai.extrair_tag(texto_raw, "OBJETIVOS_ENSINO")
        ed_ava = ai.extrair_tag(texto_raw, "AVALIACAO")
        ed_pei_plan = ai.extrair_tag(texto_raw, "ADAPTACAO_PEI")
        
        t1, t2, t3, t4, t_exp = st.tabs(["🏫 Metodologia", "🎯 Objetivos", "📝 Avaliação", "♿ PEI", "📥 EXPORTAR/SYNC"])
        
        with t1: st.text_area("Roteiro das Aulas:", ed_met, height=400, key=f"{key_prefix}_met")
        with t2: st.text_area("Objetivos Curriculares:", ed_obj, height=400, key=f"{key_prefix}_obj")
        with t3: st.text_area("Critérios de Avaliação:", ed_ava, height=200, key=f"{key_prefix}_ava")
        with t4: st.text_area("Adaptação PEI (Plano):", ed_pei_plan, height=300, key=f"{key_prefix}_pei_plan")
        
        modo_sync = "PLANEJAMENTO"
        nome_base = f"PLANO_{f_ano}ANO_{f_semana.replace(' ', '')}"
        # No planejamento, o 'ed_prof' para o banco será o próprio texto do plano
        ed_prof_para_banco = texto_raw 

    else:
        # MODO CRIADOR DE AULAS: Usa as tags [PROFESSOR] e [ALUNO]
        ed_prof = ai.extrair_tag(texto_raw, "PROFESSOR")
        ed_alu = ai.extrair_tag(texto_raw, "ALUNO")
        
        t1, t2, t3, t4, t5, t_exp = st.tabs(["✍️ Lousa", "📄 Folha", "✅ Gabarito", "🎨 Imagens", "♿ PEI", "📥 EXPORTAR/SYNC"])
        
        with t1: st.text_area("Esquema de Lousa:", ed_prof, height=400, key=f"{key_prefix}_lousa")
        with t2: st.text_area("Folha do Aluno:", ed_alu, height=400, key=f"{key_prefix}_folha")
        with t3: st.text_area("Gabarito:", ai.extrair_tag(texto_raw, "GABARITO"), height=200, key=f"{key_prefix}_gab")
        with t4: st.text_area("Prompts de Imagem:", ai.extrair_tag(texto_raw, "IMAGENS"), height=150, key=f"{key_prefix}_img")
        
        with t5:
            st.subheader("♿ Adaptação PEI (Material)")
            if "lab_pei" not in st.session_state:
                if st.button("♿ GERAR ADAPTAÇÃO PEI", use_container_width=True, key=f"{key_prefix}_gen_pei"):
                    st.session_state.lab_pei = ai.gerar_ia("ARQUITETO_PEI_V24", f"ADAPTE: {ed_alu}")
                    st.rerun()
            else:
                st.session_state.lab_pei = st.text_area("PEI:", st.session_state.lab_pei, height=400, key=f"{key_prefix}_pei_area")
        
        modo_sync = "AULA"
        nome_base = f"AULA_{f_aula.replace(' ','')}_{f_ano}ANO_{datetime.now().strftime('%d%m')}"
        ed_prof_para_banco = ed_prof

# --- ABA DE EXPORTAÇÃO E SINCRONIA (UNIFICADA V25.96) ---
    with t_exp:
        st.subheader("🚀 Sincronia de Elite SOSA")
        
        # Definição do nome base para os arquivos
        if modo_sync == "PLANEJAMENTO":
            nome_base = f"PLANO_{f_ano}ANO_{f_semana.replace(' ', '')}"
        else:
            nome_base = f"AULA_{f_aula.replace(' ','')}_{f_ano}ANO_{datetime.now().strftime('%d%m')}"

        if st.button("☁️ SINCRONIZAR TUDO NO DRIVE E BANCO", use_container_width=True, type="primary", key=f"{key_prefix}_btn_sync"):
            with st.status("Iniciando Protocolo de Sincronia e Limpeza...", expanded=True) as status:
                
                # 1. LÓGICA ANTI-DUPLICIDADE (UPSERT)
                status.write("🧹 Verificando e removendo versões obsoletas...")
                if modo_sync == "PLANEJAMENTO":
                    filtro = df_planos[(df_planos['SEMANA'] == f_semana) & (df_planos['ANO'] == f"{f_ano}º")]
                    for _, row_antiga in filtro.iterrows():
                        db.excluir_registro_com_drive("DB_PLANOS", row_antiga['PLANO_TEXTO'])
                else:
                    filtro = df_aulas[(df_aulas['SEMANA_REF'] == f_semana) & (df_aulas['TIPO_MATERIAL'].str.contains(f_aula))]
                    for _, row_antiga in filtro.iterrows():
                        db.excluir_registro_com_drive("DB_AULAS_PRONTAS", row_antiga['CONTEUDO'])

                # 2. PROCESSAMENTO POR MODO
                if modo_sync == "PLANEJAMENTO":
                    # Geração do DOCX do Plano
                    doc_plano = exporter.gerar_docx_plano_pedagogico_ELITE(nome_base, dados_plano, {"ano": f"{f_ano}º", "semana": f_semana, "trimestre": f_trimestre})
                    
                    status.write("📤 Enviando Novo Plano para a Hierarquia Oficial...")
                    link = db.subir_e_converter_para_google_docs(doc_plano, nome_base, trimestre=f_trimestre, categoria=f"{f_ano}º Ano", semana=f_semana, modo="PLANEJAMENTO")
                    
                    if "https" in str(link):
                        final_txt = (
                            f"MARKER_CONTEUDO_GERAL {dados_plano['geral']} \n"
                            f"MARKER_CONTEUDOS_ESPECIFICOS {dados_plano['especificos']} \n"
                            f"MARKER_OBJETIVOS_ENSINO {dados_plano['objetivos']} \n"
                            f"MARKER_METODOLOGIA {dados_plano['metodologia']} \n"
                            f"MARKER_AVALIACAO {dados_plano['avaliacao']} \n"
                            f"MARKER_ADAPTACAO_PEI {dados_plano['pei']} \n"
                            f"MARKER_MODALIDADE {info_aula.get('modalidade', 'MANUAL')} \n"
                            f"--- LINK DRIVE --- {link}"
                        )
                        
                        sucesso = db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), f_semana, f"{f_ano}º", f_trimestre, "PADRÃO", final_txt, link])
                        if sucesso:
                            status.update(label="✅ Plano Sincronizado!", state="complete")
                            st.balloons()
                    else:
                        status.update(label="❌ Falha na Ponte Google.", state="error")
                        st.error(link)

                else:
                    # MODO AULA (CRIADOR DE AULAS)
                    status.write("📄 Gerando Materiais (Fluxo Nativo)...")
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_base, ed_alu, {"ano": f"{f_ano}º", "trimestre": f_trimestre})
                    doc_prof = exporter.gerar_docx_professor_v25(nome_base, ed_prof, {"ano": f"{f_ano}º", "semana": f_semana, "trimestre": f_trimestre})
                    
                    status.write("📤 Enviando Material do Aluno...")
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_base}_ALUNO", trimestre=f_trimestre, categoria=f_categoria, semana=f_semana, modo="AULA")
                    
                    status.write("📤 Enviando Guia do Professor...")
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_base}_PROF", trimestre=f_trimestre, categoria=f_categoria, semana=f_semana, modo="AULA")
                    
                    link_pei = "N/A"
                    if "lab_pei" in st.session_state:
                        status.write("♿ Enviando Material PEI Adaptado...")
                        doc_pei = exporter.gerar_docx_pei_v25(f"{nome_base}_PEI", st.session_state.lab_pei, {"ano": f"{f_ano}º", "trimestre": f_trimestre})
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_base}_PEI", trimestre=f_trimestre, categoria=f_categoria, semana=f_semana, modo="AULA")

                    if "https" in str(link_alu) and "https" in str(link_prof):
                        # CONTEÚDO ESTRUTURADO PARA AULAS (Sem variáveis de prova)
                        conteudo_banco = f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI({link_pei})"
                        
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), f_semana, f"{f_aula}", conteudo_banco, f"{f_ano}º", link_alu
                        ])
                        status.update(label="✅ Aula Sincronizada!", state="complete")
                        st.balloons()
                    else:
                        status.update(label="❌ Erro no Upload da Aula.", state="error")
                        st.error(f"Falha no envio dos arquivos.")
                       

# ==============================================================================
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR V32.4) - ORGANIZAÇÃO TOTAL
# ==============================================================================
if menu == "🧪 Criador de Aulas":
    st.title("🧪 Laboratório de Produção Semiótica (V32)")
    st.markdown("---")
    
    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "refino_lab_tipo", "comp_temp", "comp_pei", "sosa_id_atual", "lab_meta"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_lab = int(time.time())
        st.rerun()

    v = st.session_state.get("v_lab", 1)

    # DEFINIÇÃO DAS ABAS MESTRAS
    tab_producao, tab_diagnostico, tab_trabalhos, tab_complementar, tab_acervo = st.tabs([
        "🚀 Produção (Aula 1/2)", 
        "🔍 Diagnóstico Reverso", 
        "📋 Engenharia de Trabalhos",
        "📚 Atividades Complementares",
        "📂 Acervo de Materiais"
    ])

    # --- FUNÇÃO INTERNA PARA EXIBIR O EDITOR (EVITA REPETIÇÃO E ERROS) ---
    def exibir_editor_material(txt_base, s_id, meta_dados):
        st.markdown("---")
        st.success(f"💎 Material Gerado: **{s_id}**")
        
        # Botão para descartar e voltar ao formulário
        if st.button("🆕 GERAR NOVO (LIMPAR ATUAL)", use_container_width=True):
            reset_laboratorio()

        t_prof, t_alu, t_gab, t_pei, t_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "✅ Gabarito/Rubrica", "♿ PEI", "☁️ SINCRONIA"])
        
        with t_prof: 
            ed_prof = st.text_area("Lousa (2 Colunas):", ai.extrair_tag(txt_base, "PROFESSOR"), height=400, key=f"ed_prof_{v}")
        with t_alu: 
            ed_alu = st.text_area("Folha do Aluno:", ai.extrair_tag(txt_base, "ALUNO"), height=400, key=f"ed_alu_{v}")
        with t_gab: 
            res_txt = ai.extrair_tag(txt_base, "GABARITO") or ai.extrair_tag(txt_base, "RUBRICA")
            ed_res = st.text_area("Respostas/Critérios:", res_txt, height=300, key=f"ed_res_{v}")
        
        with t_pei:
            st.subheader("♿ Adaptação Curricular PEI (Elite)")
            if st.button("✨ GERAR/ATUALIZAR MATERIAL PEI", use_container_width=True, key=f"btn_pei_{v}"):
                with st.spinner("Realizando reengenharia de acessibilidade..."):
                    res_pei_ia = ai.gerar_ia("ARQUITETO_PEI_V24", f"ADAPTE PARA PEI: {ed_alu}")
                    st.session_state.lab_pei = ai.extrair_tag(res_pei_ia, "PEI")
                    st.session_state.lab_gab_pei = ai.extrair_tag(res_pei_ia, "GABARITO_PEI")
                    st.rerun()
            
            if "lab_pei" in st.session_state:
                c_p1, c_p2 = st.columns(2)
                with c_p1: st.text_area("📄 Material PEI:", st.session_state.lab_pei, height=400, key=f"ed_pei_mat_{v}")
                with c_p2: st.text_area("✅ Gabarito PEI:", st.session_state.get("lab_gab_pei", ""), height=400, key=f"ed_pei_gab_{v}")

        with t_sync:
            if st.button("💾 FINALIZAR E SINCRONIZAR", use_container_width=True, type="primary", key=f"btn_sync_{v}"):
                with st.status("Sincronizando...") as status:
                    nome_final = f"{s_id} - {meta_dados['tipo']}"
                    ano_str = f"{meta_dados['ano']}º"
                    
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_final, ed_alu, {"ano": ano_str, "trimestre": meta_dados['trimestre']})
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, nome_final, modo="AULA")
                    
                    if "https" in str(link_alu):
                        conteudo_banco = (
                            f"[SOSA_ID: {s_id}]\n"
                            f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n"
                            f"[GABARITO]\n{ed_res}\n\n"
                            f"[PEI]\n{st.session_state.get('lab_pei', 'N/A')}\n\n"
                            f"[GABARITO_PEI]\n{st.session_state.get('lab_gab_pei', 'N/A')}\n\n"
                            f"--- LINKS ---\nAluno({link_alu})"
                        )
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "PRODUÇÃO", nome_final, conteudo_banco, ano_str, link_alu])
                        status.update(label="✅ Sincronizado com Sucesso!", state="complete")
                        st.balloons(); time.sleep(1); reset_laboratorio()

    # --- ABA 1: PRODUÇÃO ---
    with tab_producao:
        if "lab_temp" not in st.session_state:
            with st.container(border=True):
                st.markdown("### ⚙️ 1. Parâmetros de Regência")
                c1, c2, c3 = st.columns([1, 2, 1.5])
                ano_lab = c1.selectbox("Série/Ano:", [6, 7, 8, 9], key=f"lab_ano_{v}")
                planos_ano = df_planos[df_planos['ANO'].astype(str).str.contains(str(ano_lab))]
                
                if planos_ano.empty: st.error("❌ Nenhum plano encontrado.")
                else:
                    sem_lab = c2.selectbox("Semana Base (PIP):", planos_ano['SEMANA'].tolist(), key=f"lab_sem_{v}")
                    aula_alvo = c3.radio("🎯 Alvo:", ["Aula 1", "Aula 2", "Ambas"], horizontal=True)
                    plano_ref = planos_ano[planos_ano['SEMANA'] == sem_lab].iloc[0]['PLANO_TEXTO']
                    
                    col_p1, col_p2 = st.columns(2)
                    qtd_q = col_p1.slider("Nº de Questões:", 1, 15, 5)
                    instr_extra = col_p2.text_input("Instruções Adicionais:")
                    
                    if st.button("💎 COMPILAR MATERIAL", use_container_width=True, type="primary"):
                        s_id = util.gerar_sosa_id("AULA", ano_lab, "I")
                        st.session_state.sosa_id_atual = s_id
                        st.session_state.lab_meta = {"ano": ano_lab, "trimestre": "I Trimestre", "tipo": "AULA"}
                        st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR AULA. ID: {s_id}. PLANO: {plano_ref}. FOCO: {aula_alvo}. QTD: {qtd_q}. EXTRA: {instr_extra}")
                        st.rerun()
        else:
            exibir_editor_material(st.session_state.lab_temp, st.session_state.sosa_id_atual, st.session_state.lab_meta)

    # --- ABA 2: DIAGNÓSTICO ---
    with tab_diagnostico:
        if "lab_temp" not in st.session_state:
            st.subheader("🔍 Inteligência de Nivelamento")
            with st.container(border=True):
                cd1, cd2 = st.columns(2)
                ano_diag = cd1.selectbox("Série Atual:", [6, 7, 8, 9], key=f"diag_ano_{v}")
                trim_diag = cd2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
                
                if trim_diag == "I Trimestre":
                    ano_busca = ano_diag - 1
                    df_retro = df_curriculo[df_curriculo['ANO'] == ano_busca]
                else:
                    df_retro = df_curriculo[(df_curriculo['ANO'] == ano_diag) & (df_curriculo['TRIMESTRE'] != trim_diag)]

                if not df_retro.empty:
                    sel_retro = st.multiselect("Pré-requisitos:", df_retro['CONTEUDO_ESPECIFICO'].tolist())
                    if st.button("🧠 GERAR DIAGNÓSTICO"):
                        s_id = util.gerar_sosa_id("DIAG", ano_diag, trim_diag)
                        st.session_state.sosa_id_atual = s_id
                        st.session_state.lab_meta = {"ano": ano_diag, "trimestre": trim_diag, "tipo": "DIAGNOSTICO"}
                        st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR DIAGNÓSTICO. ID: {s_id}. CONTEÚDOS: {sel_retro}.")
                        st.rerun()
        else:
            st.info("Material em edição na aba 'Produção'.")

    # --- ABA 3: TRABALHOS ---
    with tab_trabalhos:
        if "lab_temp" not in st.session_state:
            st.subheader("📋 Engenharia de Trabalhos")
            with st.container(border=True):
                ct1, ct2, ct3 = st.columns([1, 1, 1])
                ano_trab = ct1.selectbox("Série:", [6, 7, 8, 9], key=f"trab_ano_{v}")
                tipo_trab = ct2.selectbox("Formato:", ["Pesquisa", "Projeto", "Seminário"])
                valor_trab = ct3.number_input("Valor:", 0.0, 10.0, 2.0)
                tema_trab = st.text_input("Tema:")
                if st.button("🚀 CRIAR TRABALHO"):
                    s_id = util.gerar_sosa_id("TRAB", ano_trab, "I")
                    st.session_state.sosa_id_atual = s_id
                    st.session_state.lab_meta = {"ano": ano_trab, "trimestre": "I Trimestre", "tipo": "TRABALHO"}
                    st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR TRABALHO. ID: {s_id}. TEMA: {tema_trab}. VALOR: {valor_trab}.")
                    st.rerun()
        else:
            st.info("Material em edição na aba 'Produção'.")

    # --- ABA 4: COMPLEMENTAR ---
    with tab_complementar:
        st.subheader("📚 Reforço e Aprofundamento")
        # (Lógica simplificada para manter o foco na correção do erro principal)
        st.info("Use esta aba para gerar listas extras baseadas no PIP.")

    # --- ABA 5: ACERVO (DASHBOARD VISUAL V27) ---
    with tab_acervo:
        st.subheader("📂 Acervo de Materiais Produzidos")
        if not df_aulas.empty:
            f_ano_g = st.selectbox("Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key="gav_ano_v32")
            df_g = df_aulas.copy()
            if f_ano_g != "Todos": df_g = df_g[df_g['ANO'] == f_ano_g]
            
            for _, row in df_g.iloc[::-1].iterrows():
                raw_c = str(row['CONTEUDO'])
                s_id_h = ai.extrair_tag(raw_c, "SOSA_ID")
                
                with st.container(border=True):
                    c_t1, c_t2, c_t3, c_t4, c_t5 = st.columns([2, 1, 1, 1, 1])
                    c_t1.markdown(f"**{row['TIPO_MATERIAL']}**\n`ID: {s_id_h}`")
                    
                    l_reg = re.search(r"Aluno\((.*?)\)|LINK: (https://.*)", raw_c)
                    link_reg = l_reg.group(1) or l_reg.group(2) if l_reg else row.get('LINK_DRIVE')
                    
                    if link_reg: c_t2.link_button("📝 VER", str(link_reg), use_container_width=True)
                    
                    if c_t3.button("🔄 REFINAR", key=f"ref_{row.name}", use_container_width=True):
                        st.session_state.refino_lab_ativo = {"ano": row['ANO'], "aula": row['TIPO_MATERIAL']}
                        st.session_state.lab_temp = raw_c
                        st.session_state.sosa_id_atual = s_id_h
                        st.session_state.lab_meta = {"ano": row['ANO'].replace('º',''), "trimestre": "I Trimestre", "tipo": "REFINO"}
                        st.rerun()

                    if c_t4.button("🗑️ APAGAR", key=f"del_{row.name}", use_container_width=True):
                        if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", row['TIPO_MATERIAL']): st.rerun()
                    
                    with st.expander(f"👁️ Visualizar Estrutura: {s_id_h}"):
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            st.info("**👨‍🏫 Guia do Professor**")
                            st.write(ai.extrair_tag(raw_c, "PROFESSOR"))
                        with col_v2:
                            st.success("**📝 Folha do Aluno**")
                            st.write(ai.extrair_tag(raw_c, "ALUNO"))
                        st.divider()
                        col_v3, col_v4 = st.columns(2)
                        with col_v3:
                            st.warning("**✅ Gabarito / Rubrica**")
                            st.write(ai.extrair_tag(raw_c, "GABARITO") or ai.extrair_tag(raw_c, "RUBRICA"))
                        with col_v4:
                            st.error("**♿ Adaptação PEI**")
                            st.write(ai.extrair_tag(raw_c, "PEI"))
        else:
            st.info("📭 Acervo vazio.")
                            
# ==============================================================================
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - ARQUITETURA V27 (SINCRO TOTAL)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("📅 Engenharia de Planejamento (Ponto ID)")
    st.markdown("---")

    # 1. FUNÇÕES DE SUPORTE TÉCNICO
    def limpar_v26(texto, label):
        if not texto: return ""
        t = texto.replace(label, "").replace(label.upper(), "").replace(label.lower(), "").strip()
        if t.startswith(":") or t.startswith(" :"): t = t[1:].strip()
        return t

    def reset_planejamento():
        if "p_temp" in st.session_state: del st.session_state.p_temp
        if "refino_ativo" in st.session_state: del st.session_state.refino_ativo
        st.session_state.v_plano = int(time.time())
        st.rerun()

    if "v_plano" not in st.session_state:
        st.session_state.v_plano = int(time.time())
    
    v = st.session_state.v_plano 

    # CORREÇÃO AQUI: Nomeamos as variáveis exatamente como serão usadas nos 'with'
    tab_gerar, tab_acervo, tab_matriz, tab_auditoria = st.tabs([
        "🚀 Engenharia de Planejamento", 
        "📂 Gestão de Acervo (PIP)", 
        "📖 Matriz Curricular Ativa", 
        "📈 Auditoria de Cobertura"
    ])
    
    # --- ABA 1: ENGENHARIA DE PLANEJAMENTO ---
    with tab_gerar:
        is_refinando = "refino_ativo" in st.session_state
        
        if is_refinando:
            meta = st.session_state.refino_ativo
            st.warning(f"🛠️ **MODO REFINO ATIVO:** Editando **{meta['ano']}** | **{meta['semana']}**.")
            if st.button("❌ CANCELAR REFINO E VOLTAR AO NOVO", use_container_width=True):
                reset_planejamento()
        
        # --- GATEKEEPER DE STATUS DA SEMANA ---
        with st.container(border=True):
            st.markdown("### 🛡️ 1. Status da Jornada e Calendário")
            cg1, cg2, cg3 = st.columns([1.5, 1, 1])
            tipo_semana = cg1.selectbox("Natureza da Semana:", ["Aula Regular", "Avaliação Diagnóstica", "Avaliação Trimestral", "Recuperação Paralela", "Evento Escolar/Feriado"], key=f"gate_tipo_{v}")
            tem_sabado = cg2.toggle("Sábado Letivo?", key=f"gate_sab_{v}")
            carga_horaria = cg3.select_slider("Carga Horária Útil:", options=["1 Aula", "2 Aulas", "4 Aulas"], value="4 Aulas", key=f"gate_carga_{v}")

        with st.container(border=True):
            st.markdown("### ⚙️ 2. Parâmetros de Regência")
            c1, c2, c3 = st.columns([1, 2, 1.5])
            
            lista_anos = [6, 7, 8, 9]
            idx_ano = lista_anos.index(int(st.session_state.refino_ativo['ano'].replace('º',''))) if is_refinando else 0
            ano_p = c1.selectbox("Série/Ano:", lista_anos, index=idx_ano, disabled=is_refinando, key=f"ano_sel_v26_{v}")
            
            todas_semanas = util.gerar_semanas()
            idx_sem = 0
            if is_refinando:
                try: idx_sem = [s.split(" (")[0] for s in todas_semanas].index(st.session_state.refino_ativo['semana'])
                except: idx_sem = 0

            sem_p = c2.selectbox("Semana de Referência:", todas_semanas, index=idx_sem, disabled=is_refinando, key=f"sem_sel_v26_{v}")
            sem_limpa = sem_p.split(" (")[0]
            modo_p = c3.radio("Método de Elaboração:", ["📖 Livro Didático", "🎛️ Manual (Banco)"], horizontal=True, disabled=is_refinando)

            try:
                data_ref = datetime.strptime(sem_p.split("(")[1].split(" ")[0], "%d/%m").replace(year=2026).date()
                feriado = util.verificar_feriado_itabuna(data_ref)
                if feriado: st.warning(f"📅 **Alerta de Calendário:** {feriado} detectado nesta semana.")
            except: pass

        df_f = df_curriculo[df_curriculo['ANO'] == ano_p]
        cont_pre, obj_pre, eixo_pre = [], [], ""
        sel_mat, pags = [], "" 

        with st.container(border=True):
            if modo_p == "🎛️ Manual (Banco)":
                st.markdown("#### 🎯 Matriz Curricular (Fiel ao Banco)")
                cx1, cx2 = st.columns(2)
                col_eixo = 'EIXO'
                lista_eixos = df_f[col_eixo].unique() if not df_f.empty else []
                eixo_pre = cx1.selectbox("Eixo Temático:", lista_eixos, key=f"eixo_v26_{v}")
                col_cont = 'CONTEUDO_ESPECIFICO'
                df_filtrado_cont = df_f[df_f[col_eixo] == eixo_pre] if not df_f.empty else pd.DataFrame()
                opcoes_cont = df_filtrado_cont[col_cont].unique() if not df_filtrado_cont.empty else []
                cont_pre = st.multiselect("Conteúdos Específicos:", options=opcoes_cont, key=f"cont_v26_{v}")
                col_obj = 'OBJETIVOS'
                df_filtrado_obj = df_f[df_f[col_cont].isin(cont_pre)] if not df_f.empty else pd.DataFrame()
                opcoes_obj = df_filtrado_obj[col_obj].unique() if not df_filtrado_obj.empty else []
                obj_pre = st.multiselect("Objetivos de Ensino:", options=opcoes_obj, key=f"obj_v26_{v}")
                ctx_ia = f"MÉTODO MANUAL. EIXO: {eixo_pre}. CONTEÚDOS: {cont_pre}. OBJETIVOS: {obj_pre}."
            else:
                st.markdown("#### 📖 Referência Bibliográfica")
                cx1, cx2 = st.columns([2, 1])
                lista_materiais = df_materiais['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
                sel_mat = cx1.multiselect("Livro Didático:", lista_materiais, key=f"livro_v26_{v}")
                pags = cx2.text_input("Páginas:", placeholder="Ex: 10-15", key=f"pags_v26_{v}")
                ctx_ia = f"MÉTODO LIVRO: {sel_mat} PÁGINAS: {pags}."

            strat = st.text_area("Estratégia Pedagógica / Observações:", placeholder="Ex: Focar na resolução de problemas...", key=f"strat_v26_{v}")

        cb1, cb2 = st.columns([2, 1])
        pronto = (cont_pre and obj_pre) if modo_p == "🎛️ Manual (Banco)" else (sel_mat and pags)
        
        with cb1:
            label_btn = "🚀 RECOMPOR PLANEJAMENTO (REFINO)" if is_refinando else "🚀 COMPILAR PLANEJAMENTO BNCC"
            if st.button(label_btn, use_container_width=True, type="primary", disabled=not pronto and not is_refinando):
                with st.spinner("Maestro SOSA processando Didática BNCC..."):
                    info_gate = f"TIPO_SEMANA: {tipo_semana}. CARGA: {carga_horaria}. SABADO: {tem_sabado}."
                    prompt = f"ANO: {ano_p}º, SEMANA: {sem_p}. {info_gate}. {ctx_ia}. ESTRATÉGIA: {strat}."
                    st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt)
                    st.rerun()
        with cb2:
            if "p_temp" in st.session_state:
                if st.button("🗑️ DESCARTAR RASCUNHO", use_container_width=True): reset_planejamento()

        if "p_temp" in st.session_state:
            st.markdown("---")
            txt_bruto = st.session_state.p_temp
            cmd_refine = st.chat_input("Solicitar alteração técnica no plano...")
            if cmd_refine:
                with st.spinner("Reescrevendo lógica pedagógica..."):
                    prompt_refino = f"ORDEM: {cmd_refine}\n\nTEXTO ATUAL:\n{txt_bruto}"
                    st.session_state.p_temp = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino)
                    st.session_state.v_plano = int(time.time())
                    st.rerun()

            t_ed, t_vis = st.tabs(["✏️ Editor de Texto", "👁️ Estrutura de Regência"])
            with t_ed:
                col_ed1, col_ed2 = st.columns([1, 2])
                ed_bncc = col_ed1.text_input("Código BNCC:", ai.extrair_tag(txt_bruto, "BNCC_CODE"), key=f"ed_b_{v}")
                ed_geral = col_ed2.text_input("Eixo:", ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL"), key=f"ed_g_{v}")
                ed_espec = st.text_area("Conteúdos (Literais):", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS"), key=f"ed_e_{v}")
                ed_objs = st.text_area("Objetivos (Literais):", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO"), key=f"ed_o_{v}")
                col_a1, col_a2 = st.columns(2)
                ed_a1 = col_a1.text_area("AULA 1 (BNCC):", ai.extrair_tag(txt_bruto, "AULA_1"), height=300, key=f"a1_{v}")
                ed_a2 = col_a2.text_area("AULA 2 (BNCC):", ai.extrair_tag(txt_bruto, "AULA_2"), height=300, key=f"a2_{v}")
                ed_ava = st.text_area("Avaliação:", ai.extrair_tag(txt_bruto, "AVALIACAO"), key=f"ed_a_{v}")
                ed_pei = st.text_area("Adaptação PEI:", ai.extrair_tag(txt_bruto, "ADAPTACAO_PEI"), key=f"ed_p_{v}")
                if tem_sabado:
                    ed_sab = st.text_area("Sábado Letivo:", ai.extrair_tag(txt_bruto, "SABADO_LETIVO"), key=f"ed_s_{v}")
                else: ed_sab = "N/A"

            with t_vis:
                st.markdown(f"### 🎯 Planejamento: {ed_geral}")
                st.caption(f"**Competência BNCC:** {ed_bncc}")
                st.divider()
                st.markdown(f"**CONTEÚDOS:** {ed_espec}")
                st.markdown(f"**OBJETIVOS:** {ed_objs}")
                st.divider()
                col_v1, col_v2 = st.columns(2)
                with col_v1:
                    st.markdown("#### 📘 Aula 1")
                    st.write(ed_a1)
                with col_v2:
                    st.markdown("#### 📗 Aula 2")
                    st.write(ed_a2)
                if tem_sabado:
                    st.warning(f"🗓️ **Sábado Letivo:** {ed_sab}")
                st.divider()
                st.markdown(f"**📝 AVALIAÇÃO:**\n{ed_ava}")
                st.markdown(f"**♿ ESTRATÉGIA PEI:**\n{ed_pei}")

            if st.button("💾 FINALIZAR E SINCRONIZAR (DRIVE + BANCO)", use_container_width=True, type="primary"):
                with st.status("Iniciando Protocolo de Sincronia...", expanded=True) as status:
                    final_ano = st.session_state.refino_ativo['ano'] if is_refinando else f"{ano_p}º"
                    final_semana = st.session_state.refino_ativo['semana'] if is_refinando else sem_limpa
                    nome_arquivo = f"PLANO_{final_ano.replace('º','')}ANO_{final_semana.replace(' ', '')}"
                    db.excluir_plano_completo(final_semana, final_ano) 
                    metodologia_unificada = f"AULA 1:\n{ed_a1}\n\nAULA 2:\n{ed_a2}"
                    if tem_sabado: metodologia_unificada += f"\n\nSÁBADO LETIVO:\n{ed_sab}"
                    dados_docx = {"geral": f"[{ed_bncc}] {ed_geral}", "especificos": ed_espec, "objetivos": ed_objs, "metodologia": metodologia_unificada, "avaliacao": ed_ava, "pei": ed_pei}
                    doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": final_ano, "semana": final_semana, "trimestre": "I Trimestre"})
                    link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre="I Trimestre", categoria=final_ano, semana=final_semana, modo="PLANEJAMENTO")
                    if "https" in str(link_drive):
                        final_txt = f"MARKER_BNCC_CODE {ed_bncc} \nMARKER_CONTEUDO_GERAL {ed_geral} \nMARKER_CONTEUDOS_ESPECIFICOS {ed_espec} \nMARKER_OBJETIVOS_ENSINO {ed_objs} \nMARKER_AULA_1 {ed_a1} \nMARKER_AULA_2 {ed_a2} \nMARKER_SABADO_LETIVO {ed_sab} \nMARKER_AVALIACAO {ed_ava} \nMARKER_ADAPTACAO_PEI {ed_pei} \n--- LINK DRIVE --- {link_drive}"
                        db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), final_semana, final_ano, "I Trimestre", "PADRÃO", final_txt, link_drive])
                        status.update(label="✅ Sincronia Concluída!", state="complete")
                        st.balloons(); reset_planejamento()

    # --- ABA 2: GESTÃO DE ACERVO (PIP) ---
    with tab_acervo:
        st.subheader("📂 Repositório de Planos Estratégicos")
        if not df_planos.empty:
            c_h1, c_h2 = st.columns(2)
            f_ano_h = c_h1.selectbox("Filtrar por Série:", ["Todos", "6º", "7º", "8º", "9º"], key="hist_ano_v27")
            df_h = df_planos.copy()
            if f_ano_h != "Todos": df_h = df_h[df_h['ANO'] == f_ano_h]
            if not df_h.empty:
                sel_h = st.selectbox("Selecionar Plano para Visualização:", df_h['SEMANA'].tolist(), key="hist_sem_v27")
                dados_h = df_h[df_h['SEMANA'] == sel_h].iloc[0]
                raw_h = str(dados_h['PLANO_TEXTO'])
                
                bncc_h = ai.extrair_tag(raw_h, "BNCC_CODE")
                eixo_h = ai.extrair_tag(raw_h, "CONTEUDO_GERAL")
                espec_h = ai.extrair_tag(raw_h, "CONTEUDOS_ESPECIFICOS")
                obj_h = ai.extrair_tag(raw_h, "OBJETIVOS_ENSINO")
                a1_h = ai.extrair_tag(raw_h, "AULA_1")
                a2_h = ai.extrair_tag(raw_h, "AULA_2")
                ava_h = ai.extrair_tag(raw_h, "AVALIACAO")
                pei_h = ai.extrair_tag(raw_h, "ADAPTACAO_PEI")
                link_h = dados_h.get('LINK_DRIVE', "Não encontrado")

                st.markdown(f"### 📝 Plano: {sel_h} ({dados_h['ANO']})")
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("🔄 REABRIR PARA REFINO IA", use_container_width=True, key=f"reopen_{v}"):
                        st.session_state.refino_ativo = {"ano": dados_h['ANO'], "semana": sel_h}
                        st.session_state.p_temp = raw_h
                        st.rerun()
                with col_btn2:
                    if "https" in str(link_h): st.link_button("🚀 ABRIR NO GOOGLE DRIVE", str(link_h), use_container_width=True)

                with st.container(border=True):
                    st.markdown(f"#### 🎯 {eixo_h if eixo_h else 'Conteúdo Geral'}")
                    st.caption(f"🆔 **BNCC:** {bncc_h}")
                    col_info1, col_info2 = st.columns(2)
                    with col_info1: st.info(f"**Conteúdos:**\n{espec_h}")
                    with col_info2: st.success(f"**Objetivos:**\n{obj_h}")
                    st.divider()
                    col_v1, col_v2 = st.columns(2)
                    with col_v1:
                        st.markdown("##### 📘 Aula 1")
                        st.write(a1_h if a1_h else ai.extrair_tag(raw_h, "METODOLOGIA"))
                    with col_v2:
                        st.markdown("##### 📗 Aula 2")
                        st.write(a2_h if a2_h else "N/A")
                    st.divider()
                    col_v3, col_v4 = st.columns(2)
                    with col_v3: st.markdown("##### 📝 Avaliação"); st.write(ava_h)
                    with col_v4: st.markdown("##### ♿ Estratégia PEI"); st.write(pei_h)

                with st.expander("🛠️ Ver Código-Fonte"): st.text(raw_h)
                if st.button("🗑️ EXCLUIR PLANO DEFINITIVAMENTE", use_container_width=True, key=f"del_plano_{v}"):
                    if db.excluir_plano_completo(sel_h, dados_h['ANO']): st.rerun()
            else: st.info("Nenhum plano encontrado.")
        else: st.info("📭 Acervo vazio.")

    # --- ABA 3: MATRIZ CURRICULAR ATIVA (V27.2 - BUSCA ROBUSTA) ---
    with tab_matriz:
        st.subheader("📖 Matriz de Competências e Status de Execução")
        if not df_curriculo.empty:
            ano_c = st.selectbox("Série para Consulta:", [6, 7, 8, 9], key="matriz_ano_v27")
            
            # 1. Filtrar currículo do ano selecionado
            df_c = df_curriculo[df_curriculo['ANO'] == ano_c].copy()
            
            # 2. Capturar planos e normalizar texto para busca
            # Filtra planos que contenham o número do ano (ex: "6" em "6º")
            planos_feitos = df_planos[df_planos['ANO'].astype(str).str.contains(str(ano_c))]
            texto_todos_planos = " ".join(planos_feitos['PLANO_TEXTO'].astype(str)).upper()

            # 3. Função de Verificação Inteligente (Busca por palavras-chave)
            def checar_conclusao_robusta(conteudo_db):
                if not texto_todos_planos: return "⏳ PENDENTE"
                
                conteudo_limpo = str(conteudo_db).upper()
                # Teste 1: Busca exata (Literal)
                if conteudo_limpo in texto_todos_planos:
                    return "✅ CONCLUÍDO"
                
                # Teste 2: Busca por palavras-chave (Garante que termos técnicos batam)
                # Removemos palavras curtas (e, de, o, os) e focamos nos termos principais
                palavras = [p for p in conteudo_limpo.replace(";", "").replace(",", "").split() if len(p) > 3]
                if not palavras: return "⏳ PENDENTE"
                
                # Se pelo menos 2 palavras-chave importantes existirem no plano, consideramos concluído
                matches = sum(1 for p in palavras if p in texto_todos_planos)
                if matches >= 2:
                    return "✅ CONCLUÍDO"
                
                return "⏳ PENDENTE"

            df_c['STATUS'] = df_c['CONTEUDO_ESPECIFICO'].apply(checar_conclusao_robusta)

            # 4. Exibição da Tabela
            st.dataframe(
                df_c[['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO', 'STATUS']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "STATUS": st.column_config.TextColumn("Situação", width="small"),
                    "CONTEUDO_ESPECIFICO": st.column_config.TextColumn("Conteúdo do Currículo", width="large")
                }
            )
        else:
            st.info("📭 Base de currículo não localizada.")

    # --- ABA 4: ANALYTICS DE COBERTURA (V27.2 - KPI TRIMESTRAL) ---
    with tab_auditoria:
        st.subheader("📈 Analytics de Cobertura Curricular")
        if not df_curriculo.empty:
            ano_m = st.selectbox("Analisar Série:", [6, 7, 8, 9], key="auditoria_ano_v27")
            
            # Processamento para o Gráfico
            df_m = df_curriculo[df_curriculo['ANO'] == ano_m].copy()
            planos_m = df_planos[df_planos['ANO'].astype(str).str.contains(str(ano_m))]
            texto_m = " ".join(planos_m['PLANO_TEXTO'].astype(str)).upper()
            
            # Aplicando a mesma lógica robusta para o gráfico
            def concluido_num(x):
                txt = str(x).upper()
                if txt in texto_m: return 1
                palavras = [p for p in txt.replace(";", "").replace(",", "").split() if len(p) > 3]
                if palavras and sum(1 for p in palavras if p in texto_m) >= 2: return 1
                return 0

            df_m['CONCLUIDO'] = df_m['CONTEUDO_ESPECIFICO'].apply(concluido_num)
            
            # Agrupamento por Trimestre
            progresso_trim = df_m.groupby('TRIMESTRE')['CONCLUIDO'].agg(['sum', 'count']).reset_index()
            progresso_trim['%'] = (progresso_trim['sum'] / progresso_trim['count'] * 100).round(1)
            
            # KPIs de Topo (Cartões Modernos)
            c1, c2, c3 = st.columns(3)
            total_geral = (df_m['CONCLUIDO'].sum() / len(df_m) * 100)
            c1.metric("Cobertura Anual", f"{total_geral:.1f}%")
            
            # Progresso por Trimestre (I e II)
            p_i = progresso_trim[progresso_trim['TRIMESTRE'] == 'I']['%'].values[0] if 'I' in progresso_trim['TRIMESTRE'].values else 0
            c2.metric("Progresso I Trimestre", f"{p_i}%")
            
            p_ii = progresso_trim[progresso_trim['TRIMESTRE'] == 'II']['%'].values[0] if 'II' in progresso_trim['TRIMESTRE'].values else 0
            c3.metric("Progresso II Trimestre", f"{p_ii}%")

            # Gráfico de Barras
            fig_cob = px.bar(
                progresso_trim, 
                x='TRIMESTRE', 
                y='%', 
                text='%',
                title=f"Evolução da Cobertura - {ano_m}º Ano",
                color='%',
                color_continuous_scale='RdYlGn',
                range_y=[0, 110]
            )
            st.plotly_chart(fig_cob, use_container_width=True)

            # Lista de Pendências
            with st.expander("🔍 Ver Conteúdos Pendentes (Próximos Passos)"):
                pendentes = df_m[df_m['CONCLUIDO'] == 0][['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO']]
                if not pendentes.empty:
                    st.table(pendentes)
                else:
                    st.success("🎉 Excelente! Todo o currículo planejado.")
        else:
            st.info("Aguardando dados para gerar analytics.")


# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO RÁPIDO V26.6 - COM REGISTRO DE BÔNUS ⭐
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("📝 Diário de Bordo: Engajamento e Bônus")
    st.markdown("---")

    if "v_diario" not in st.session_state: st.session_state.v_diario = 1
    v = st.session_state.v_diario

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro.")
    else:
        with st.container(border=True):
            c1, c2 = st.columns([1, 1])
            turma_sel = c1.selectbox("👥 Turma:", sorted(df_alunos['TURMA'].unique()), key="db_turma")
            data_sel = c2.date_input("📅 Data:", date.today(), key="db_data")
            data_str = data_sel.strftime("%d/%m/%Y")

            planos_turma = df_planos[df_planos['ANO'] == f"{turma_sel[0]}º"]
            
            if not planos_turma.empty:
                c3, c4 = st.columns([2, 1])
                semana_sel = c3.selectbox("🔗 Vincular à Semana:", planos_turma['SEMANA'].tolist(), key="db_sem")
                aula_alvo = c4.radio("🎯 Aula:", ["Aula 1", "Aula 2"], horizontal=True)
                plano_ref = planos_turma[planos_turma['SEMANA'] == semana_sel].iloc[0]['PLANO_TEXTO']
                st.caption(f"📖 **Conteúdo Previsto:** {ai.extrair_tag(plano_ref, 'CONTEUDOS_ESPECIFICOS')}")
            else:
                st.error("❌ Planejamento não encontrado.")
                semana_sel, aula_alvo = "N/A", "N/A"

        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        df_existente = pd.DataFrame()
        if not df_diario.empty:
            df_existente = df_diario[
                (df_diario['DATA'] == data_str) & 
                (df_diario['TURMA'] == turma_sel) &
                (df_diario['OBSERVACOES'].str.contains(aula_alvo, na=False))
            ]

        dados_editor = []
        for _, aluno in alunos_turma.iterrows():
            id_a = db.limpar_id(aluno['ID'])
            is_pei = str(aluno['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
            
            visto_val, faltou_val, tag_val, obs_val, bonus_val = True, False, "", "", 0.0

            if not df_existente.empty:
                reg = df_existente[df_existente['ID_ALUNO'].apply(db.limpar_id) == id_a]
                if not reg.empty:
                    visto_val = str(reg.iloc[0]['VISTO_ATIVIDADE']).upper() == "TRUE"
                    tag_val = str(reg.iloc[0]['TAGS'])
                    obs_val = str(reg.iloc[0]['OBSERVACOES']).replace(f"[{aula_alvo}]", "").strip()
                    # Puxa o bônus se a coluna existir no dataframe
                    if 'BONUS' in reg.columns: bonus_val = util.sosa_to_float(reg.iloc[0]['BONUS'])
                    if "AUSÊNCIA" in tag_val: faltou_val = True

            dados_editor.append({
                "ID": id_a,
                "ALUNO": f"♿ {aluno['NOME_ALUNO']}" if is_pei else aluno['NOME_ALUNO'],
                "FALTOU": faltou_val,
                "VISTO": visto_val,
                "⭐ BÔNUS": bonus_val, # NOVA COLUNA
                "OCORRÊNCIA": tag_val if tag_val != "nan" else "",
                "OBS": obs_val if obs_val != "nan" else ""
            })

        st.markdown(f"### 📝 Registro de Engajamento: {aula_alvo}")
        df_editado = st.data_editor(
            pd.DataFrame(dados_editor),
            column_config={
                "ID": None,
                "ALUNO": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                "FALTOU": st.column_config.CheckboxColumn("Faltou?", width="small"),
                "VISTO": st.column_config.CheckboxColumn("Visto", width="small"),
                "⭐ BÔNUS": st.column_config.NumberColumn("Bônus", min_value=0.0, max_value=2.0, step=0.1, format="%.1f"),
                "OCORRÊNCIA": st.column_config.SelectboxColumn("Tags", options=["", "Dormiu", "Conversa", "Se destacou", "Sem material", "Vetor Disciplinar", "PEI Concluído"]),
                "OBS": st.column_config.TextColumn("Obs", width="medium")
            },
            hide_index=True, use_container_width=True, key=f"editor_diario_{v}"
        )

        if st.button("💾 SALVAR DIÁRIO E BÔNUS", type="primary", use_container_width=True):
            with st.status("Sincronizando...", expanded=False) as status:
                db.limpar_diario_data_turma(data_str, turma_sel)
                linhas = []
                for _, row in df_editado.iterrows():
                    tag_f, visto_f = row['OCORRÊNCIA'], row['VISTO']
                    if row['FALTOU']:
                        tag_f, visto_f = "AUSÊNCIA JUSTIFICADA", False
                    
                    linhas.append([
                        data_str, row['ID'], row['ALUNO'].replace("♿ ", ""), turma_sel,
                        str(visto_f), tag_f, f"[{aula_alvo}] {row['OBS']}".strip(),
                        util.sosa_to_str(row['⭐ BÔNUS']) # SALVA O BÔNUS NA COLUNA H
                    ])
                
                if db.salvar_lote("DB_DIARIO_BORDO", linhas):
                    status.update(label="✅ Salvo com Sucesso!", state="complete")
                    st.balloons(); time.sleep(1); st.rerun()

# ==============================================================================
# MÓDULO: PAINEL DE NOTAS & VISTOS V26.7 - PESOS PERSISTENTES E AUTO-AJUSTE
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.title("📊 Painel de Notas: Sincronia e Padrão Prefeitura")
    st.markdown("---")

    # --- 1. INICIALIZAÇÃO DE ESTADO (PERSISTÊNCIA DE PESOS) ---
    if "p_visto" not in st.session_state: st.session_state.p_visto = 3.0
    if "p_teste" not in st.session_state: st.session_state.p_teste = 3.0
    if "p_prova" not in st.session_state: st.session_state.p_prova = 4.0
    if "v_notas" not in st.session_state: st.session_state.v_notas = 1
    v = st.session_state.v_notas

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro.")
    else:
        # --- 2. CONFIGURADOR DE PESOS (COM MEMÓRIA) ---
        with st.container(border=True):
            st.markdown("### ⚙️ Configuração de Pesos (Padrão Prefeitura)")
            c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1.5, 1, 0.8, 0.8, 0.8])
            
            turma_sel = c_f1.selectbox("👥 Turma:", sorted(df_alunos['TURMA'].unique()), key="n_turma")
            trimestre_sel = c_f2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="n_trim")
            
            # Os inputs agora são vinculados ao session_state para não resetarem
            p_visto = c_f3.number_input("Peso Vistos:", 0.0, 10.0, value=st.session_state.p_visto, step=0.5, key="input_visto")
            p_teste = c_f4.number_input("Peso Teste:", 0.0, 10.0, value=st.session_state.p_teste, step=0.5, key="input_teste")
            p_prova = c_f5.number_input("Peso Prova:", 0.0, 10.0, value=st.session_state.p_prova, step=0.5, key="input_prova")
            
            # Atualiza o estado global com o que o professor digitou
            st.session_state.p_visto = p_visto
            st.session_state.p_teste = p_teste
            st.session_state.p_prova = p_prova

        # --- 3. CENTRAL DE SINCRONIA (COM AUTO-DETECÇÃO DE PESO) ---
        with st.expander("🔄 Central de Sincronização Ativa", expanded=True):
            c_s1, c_s2 = st.columns(2)
            provas_escaneadas = []
            if not df_diagnosticos.empty:
                provas_escaneadas = df_diagnosticos[df_diagnosticos['TURMA'] == turma_sel]['ID_AVALIACAO'].unique().tolist()
            
            opcoes_teste = [p for p in provas_escaneadas if "TESTE" in p.upper()]
            opcoes_prova = [p for p in provas_escaneadas if "PROVA" in p.upper()]
            
            av_teste_id = c_s1.selectbox("Vincular Teste:", ["Nenhum"] + opcoes_teste)
            av_prova_id = c_s2.selectbox("Vincular Prova:", ["Nenhum"] + opcoes_prova)
            
            col_btn1, col_btn2 = st.columns(2)
            
            if col_btn1.button("📸 IMPORTAR NOTAS E AJUSTAR PESOS", use_container_width=True, type="primary"):
                # Lógica de Auto-Ajuste de Peso baseada no DNA da Prova
                if av_teste_id != "Nenhum":
                    prova_ref_t = df_aulas[df_aulas['TIPO_MATERIAL'] == av_teste_id]
                    if not prova_ref_t.empty:
                        txt_t = str(prova_ref_t.iloc[0]['CONTEUDO'])
                        m_v = re.search(r"\[VALOR:\s*(\d+[\.,]\d+|\d+)\]", txt_t.upper())
                        if m_v: st.session_state.p_teste = util.sosa_to_float(m_v.group(1))
                
                if av_prova_id != "Nenhum":
                    prova_ref_p = df_aulas[df_aulas['TIPO_MATERIAL'] == av_prova_id]
                    if not prova_ref_p.empty:
                        txt_p = str(prova_ref_p.iloc[0]['CONTEUDO'])
                        m_v = re.search(r"\[VALOR:\s*(\d+[\.,]\d+|\d+)\]", txt_p.upper())
                        if m_v: st.session_state.p_prova = util.sosa_to_float(m_v.group(1))
                
                st.rerun()
            
            if col_btn2.button("⭐ ATUALIZAR BÔNUS DO DIÁRIO", use_container_width=True):
                st.cache_data.clear()
                st.rerun()

        # --- 4. CÁLCULO DE VISTOS E BÔNUS ---
        vistos_calculados = {}
        bonus_calculados = {}
        calendario = {"I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)), "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)), "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))}
        dt_ini, dt_fim = calendario.get(trimestre_sel)

        if not df_diario.empty:
            df_d_t = df_diario[df_diario['TURMA'] == turma_sel].copy()
            df_d_t['DATA_DT'] = pd.to_datetime(df_d_t['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
            df_d_trim = df_d_t[(df_d_t['DATA_DT'] >= dt_ini) & (df_d_t['DATA_DT'] <= dt_fim)]
            
            for id_aluno in df_alunos[df_alunos['TURMA'] == turma_sel]['ID']:
                id_limpo = db.limpar_id(id_aluno)
                d_aluno = df_d_trim[df_d_trim['ID_ALUNO'].apply(db.limpar_id) == id_limpo]
                if not d_aluno.empty:
                    aulas_validas = d_aluno[~d_aluno['TAGS'].astype(str).str.upper().str.contains("AUSÊNCIA JUSTIFICADA", na=False)]
                    vistos_recebidos = len(aulas_validas[aulas_validas['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    vistos_calculados[id_limpo] = round((vistos_recebidos / len(aulas_validas) * st.session_state.p_visto), 2) if len(aulas_validas) > 0 else 0.0
                    bonus_calculados[id_limpo] = d_aluno['BONUS'].apply(util.sosa_to_float).sum() if 'BONUS' in d_aluno.columns else 0.0
                else:
                    vistos_calculados[id_limpo] = 0.0
                    bonus_calculados[id_limpo] = 0.0

        # --- 5. EDITOR DE CONSOLIDAÇÃO ---
        st.subheader("📝 1. Consolidação de Dados (Professor)")
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        notas_no_banco = df_notas[(df_notas['TURMA'] == turma_sel) & (df_notas['TRIMESTRE'] == trimestre_sel)]
        
        dados_grade = []
        for _, aluno in alunos_turma.iterrows():
            id_a = db.limpar_id(aluno['ID'])
            reg_banco = notas_no_banco[notas_no_banco['ID_ALUNO'].apply(db.limpar_id) == id_a]
            
            n_visto_base = vistos_calculados.get(id_a, 0.0)
            n_bonus_base = bonus_calculados.get(id_a, 0.0)
            n_teste_base = util.sosa_to_float(reg_banco.iloc[0].get('NOTA_TESTE', 0)) if not reg_banco.empty else 0.0
            n_prova_base = util.sosa_to_float(reg_banco.iloc[0].get('NOTA_PROVA', 0)) if not reg_banco.empty else 0.0

            if av_teste_id != "Nenhum":
                reg_s = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diagnosticos['ID_AVALIACAO'] == av_teste_id)]
                if not reg_s.empty: n_teste_base = util.sosa_to_float(reg_s.iloc[0]['NOTA_CALCULADA'])
            if av_prova_id != "Nenhum":
                reg_p = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diagnosticos['ID_AVALIACAO'] == av_prova_id)]
                if not reg_p.empty: n_prova_base = util.sosa_to_float(reg_p.iloc[0]['NOTA_CALCULADA'])

            dados_grade.append({"ID": id_a, "NOME": aluno['NOME_ALUNO'], "VISTOS": n_visto_base, "TESTE": n_teste_base, "PROVA": n_prova_base, "BÔNUS": n_bonus_base, "REC_PARALELA": 0.0})

        df_edit = st.data_editor(pd.DataFrame(dados_grade), hide_index=True, use_container_width=True, key=f"ed_notas_v26_{v}")

        # --- 6. LÓGICA DE DISTRIBUIÇÃO DE BÔNUS ---
        def distribuir_bonus(row):
            bonus = row['BÔNUS']
            v, t, p = row['VISTOS'], row['TESTE'], row['PROVA']
            espaco_v = max(0, st.session_state.p_visto - v); v_f = v + min(bonus, espaco_v); bonus -= min(bonus, espaco_v)
            espaco_t = max(0, st.session_state.p_teste - t); t_f = t + min(bonus, espaco_t); bonus -= min(bonus, espaco_t)
            espaco_p = max(0, st.session_state.p_prova - p); p_f = p + min(bonus, espaco_p)
            soma = v_f + t_f + p_f
            return pd.Series([v_f, t_f, p_f, min(10.0, max(soma, row['REC_PARALELA']))])

        df_edit[['V_F', 'T_F', 'P_F', 'MEDIA']] = df_edit.apply(distribuir_bonus, axis=1)

        # --- 7. TABELA FINAL (ALTO CONTRASTE - TEXTO PRETO) ---
        st.markdown("### 📊 2. Nota Final (Padrão Prefeitura - Com Bônus)")
        
        def style_pref(v):
            if v < 6.0: return 'background-color: #FF0000; color: #000000; font-weight: 900;' # Vermelho com Texto Preto
            return 'background-color: #00FF00; color: #000000; font-weight: 700;' # Verde com Texto Preto

        st.dataframe(
            df_edit[['NOME', 'V_F', 'T_F', 'P_F', 'REC_PARALELA', 'MEDIA']].style.applymap(style_pref, subset=['MEDIA'])
            .format("{:.2f}", subset=['V_F', 'T_F', 'P_F', 'REC_PARALELA', 'MEDIA']),
            use_container_width=True, hide_index=True
        )

        if st.button("💾 SALVAR E SINCRONIZAR TUDO", type="primary", use_container_width=True):
            with st.status("Sincronizando...", expanded=False) as status:
                db.limpar_notas_turma_trimestre(turma_sel, trimestre_sel)
                linhas = []
                for _, r in df_edit.iterrows():
                    linhas.append([
                        r['ID'], r['NOME'], turma_sel, trimestre_sel,
                        util.sosa_to_str(r["V_F"]), util.sosa_to_str(r["T_F"]),
                        util.sosa_to_str(r["P_F"]), util.sosa_to_str(r["BÔNUS"]),
                        util.sosa_to_str(r['MEDIA'])
                    ])
                db.salvar_lote("DB_NOTAS", linhas)
                status.update(label="✅ Notas Salvas!", state="complete")
                st.balloons()

# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO V26 - INTELIGÊNCIA PREDITIVA E 360°
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Boletim Estratégico e Inteligência de Conselho")
    st.markdown("---")

    if df_notas.empty:
        st.warning("⚠️ Sem notas lançadas no sistema.")
    else:
        # --- 1. FILTRO DE TURMA ---
        turma_sel = st.selectbox("🎯 Selecione a Turma para Análise:", sorted(df_alunos['TURMA'].unique()), key="bol_turma_v26")
        
        # --- 2. PROCESSAMENTO DE DADOS (DATA FUSION) ---
        df_t = df_notas[df_notas['TURMA'] == turma_sel].copy()
        
        # Pivotagem para visão anual
        pivot = df_t.pivot_table(index=["ID_ALUNO", "NOME_ALUNO"], columns="TRIMESTRE", values="MEDIA_FINAL", aggfunc='first').reset_index()
        
        # Garantir que as colunas dos 3 trimestres existam
        for c in ["I Trimestre", "II Trimestre", "III Trimestre"]:
            if c not in pivot.columns: pivot[c] = 0.0
        pivot = pivot.fillna(0.0)

        # --- 3. CÁLCULO DE ÍNDICE DE ESFORÇO (DIÁRIO) ---
        esforco_map = {}
        if not df_diario.empty:
            df_d_t = df_diario[df_diario['TURMA'] == turma_sel]
            for id_a in pivot['ID_ALUNO']:
                id_limpo = db.limpar_id(id_a)
                d_aluno = df_d_t[df_d_t['ID_ALUNO'].apply(db.limpar_id) == id_limpo]
                if not d_aluno.empty:
                    vistos = len(d_aluno[d_aluno['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    total_aulas = len(d_aluno)
                    esforco_map[id_limpo] = (vistos / total_aulas * 100) if total_aulas > 0 else 0.0
                else: esforco_map[id_limpo] = 0.0

        # --- 4. LÓGICA PREDITIVA E TENDÊNCIA ---
        def calcular_predicao(row):
            t1, t2, t3 = row["I Trimestre"], row["II Trimestre"], row["III Trimestre"]
            soma = t1 + t2 + t3
            falta = max(0.0, 18.0 - soma)
            
            # Tendência
            seta = "➖"
            if t2 > t1 and t1 > 0: seta = "⬆️"
            elif t2 < t1 and t2 > 0: seta = "⬇️"
            
            # Status e Risco
            if soma >= 18.0: status = "✅ APROVADO"
            elif falta > 10.0: status = "🚨 RISCO CRÍTICO"
            elif soma > 0: status = "⚠️ EM RECUPERAÇÃO"
            else: status = "⏳ AGUARDANDO"
            
            # PEI Tag
            aluno_info = df_alunos[df_alunos['ID'].apply(db.limpar_id) == db.limpar_id(row['ID_ALUNO'])].iloc[0]
            pei = "♿" if str(aluno_info['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""] else "📝"
            
            esforco = esforco_map.get(db.limpar_id(row['ID_ALUNO']), 0.0)
            
            return pd.Series([pei, seta, esforco, soma, falta, status])

        pivot[['PERFIL', 'EVOLUÇÃO', 'ESFORÇO %', 'TOTAL', 'PRECISA DE', 'SITUAÇÃO']] = pivot.apply(calcular_predicao, axis=1)

        # --- 5. DASHBOARD DE TOPO (KPIs) ---
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média da Turma", f"{pivot['TOTAL'].mean()/3:.1f}")
        c2.metric("Aprovação Atual", f"{(len(pivot[pivot['TOTAL']>=18])/len(pivot)*100):.0f}%")
        c3.metric("Esforço Médio", f"{pivot['ESFORÇO %'].mean():.0f}%")
        c4.metric("Risco Crítico", len(pivot[pivot['SITUAÇÃO'] == "🚨 RISCO CRÍTICO"]), delta_color="inverse")

        # --- 6. TABELA DE ELITE (VISUALIZAÇÃO) ---
        st.markdown("### 📊 Mapa de Desempenho Anual")
        
        def style_boletim(v):
            if v == "✅ APROVADO": return 'background-color: #006400; color: white;'
            if v == "🚨 RISCO CRÍTICO": return 'background-color: #8B0000; color: white; font-weight: bold;'
            if v == "⚠️ EM RECUPERAÇÃO": return 'background-color: #FFD700; color: black;'
            return ''

        st.dataframe(
            pivot[['PERFIL', 'NOME_ALUNO', 'I Trimestre', 'EVOLUÇÃO', 'II Trimestre', 'III Trimestre', 'ESFORÇO %', 'TOTAL', 'PRECISA DE', 'SITUAÇÃO']]
            .style.applymap(style_boletim, subset=['SITUAÇÃO'])
            .format("{:.1f}", subset=['I Trimestre', 'II Trimestre', 'III Trimestre', 'TOTAL', 'PRECISA DE'])
            .format("{:.0f}%", subset=['ESFORÇO %']),
            use_container_width=True, hide_index=True
        )

        # --- 7. FLASHCARD DE CONSELHO (INDIVIDUAL) ---
        st.markdown("---")
        st.subheader("👤 Perícia Individual para Conselho")
        aluno_c = st.selectbox("Selecione o aluno para ver o diagnóstico 360°:", pivot['NOME_ALUNO'].tolist())
        
        if aluno_c:
            dados_a = pivot[pivot['NOME_ALUNO'] == aluno_c].iloc[0]
            id_a = db.limpar_id(dados_a['ID_ALUNO'])
            
            col_f1, col_f2 = st.columns([1, 2])
            with col_f1:
                st.markdown(f"**Status:** {dados_a['SITUAÇÃO']}")
                st.metric("Esforço (Vistos)", f"{dados_a['ESFORÇO %']:.0f}%")
                st.metric("Pontos Restantes", f"{dados_a['PRECISA DE']:.1f}")
            
            with col_f2:
                # Busca lacunas no Scanner
                if not df_diagnosticos.empty:
                    erros = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diagnosticos['NOTA_CALCULADA'] < 0.5)]
                    if not erros.empty:
                        st.error(f"🚨 **Lacunas Cognitivas:** Errou {len(erros)} questões críticas nas últimas avaliações.")
                    else:
                        st.success("✅ **Domínio Técnico:** Bom desempenho nas questões do Scanner.")
                
                if st.button(f"🧠 Gerar Argumento de Conselho para {aluno_c}"):
                    with st.spinner("Maestro analisando biografia escolar..."):
                        prompt = (
                            f"Gere um argumento técnico para conselho de classe.\n"
                            f"ALUNO: {aluno_c}. NOTAS: I({dados_a['I Trimestre']}), II({dados_a['II Trimestre']}).\n"
                            f"ESFORÇO (VISTOS): {dados_a['ESFORÇO %']:.0f}%.\n"
                            f"TENDÊNCIA: {dados_a['EVOLUÇÃO']}.\n"
                            f"SITUAÇÃO: {dados_a['SITUAÇÃO']}.\n"
                            f"Use a Pedagogia Histórico-Crítica. Foque se o problema é falta de base ou falta de engajamento."
                        )
                        st.info(ai.gerar_ia("PLANE_PEDAGOGICO", prompt))

        # --- 8. ATA AUTOMÁTICA ---
        if st.button("📝 GERAR ATA SINTÉTICA DA TURMA", use_container_width=True):
            with st.spinner("Compilando dados da turma..."):
                resumo = pivot[['NOME_ALUNO', 'TOTAL', 'ESFORÇO %', 'SITUAÇÃO']].to_string()
                prompt_ata = f"Escreva uma ata de conselho de classe para a turma {turma_sel}. Resumo dos dados:\n{resumo}\nSeja formal e sugira ações de recomposição."
                st.text_area("Copia e cole na Ata Oficial:", ai.gerar_ia("PLANE_PEDAGOGICO", prompt_ata), height=300)

# ==============================================================================
# MÓDULO: GESTÃO DA TURMA V26.8 - ARQUITETURA, EDIÇÃO E DASHBOARD
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Centro de Comando: Gestão de Turmas e Alunos")
    st.markdown("---")

    tab_dash, tab_criar, tab_povoar, tab_editar = st.tabs([
        "📊 Dashboard de Regência",
        "🏗️ Arquitetura de Turmas", 
        "➕ Povoar Alunos", 
        "✏️ Edição & Transferência"
    ])

    # --- ABA 1: DASHBOARD DE REGÊNCIA (VISÃO ANALÍTICA) ---
    with tab_dash:
        if not df_turmas.empty:
            st.subheader("📊 Raio-X da Carga Horária")
            
            # KPIs Globais
            c1, c2, c3, c4 = st.columns(4)
            total_alunos = len(df_alunos)
            ativos = len(df_alunos[df_alunos['STATUS'] == "ATIVO"])
            peis = len(df_alunos[~df_alunos['NECESSIDADES'].astype(str).str.upper().isin(["NENHUMA", "PENDENTE", "", "NAN"])])
            
            c1.metric("Total de Alunos", total_alunos)
            c2.metric("Alunos Ativos", ativos)
            c3.metric("Estudantes PEI", peis)
            c4.metric("Turmas", len(df_turmas))

            # Gráfico de Distribuição por Turma
            df_contagem = df_alunos.groupby(['TURMA', 'STATUS']).size().reset_index(name='Qtd')
            fig_dist = px.bar(df_contagem, x='TURMA', y='Qtd', color='STATUS', 
                             title="Distribuição de Alunos por Turma e Status",
                             color_discrete_map={"ATIVO": "#00FF00", "DESISTENTE": "#FF3333", "TRANSFERIDO": "#FFA500"})
            st.plotly_chart(fig_dist, use_container_width=True)

            # Cards das Turmas
            for _, row in df_turmas.iterrows():
                with st.container(border=True):
                    col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
                    col_m1.markdown(f"### {row['ID_TURMA']}")
                    col_m1.caption(f"🕒 {row['HORARIO_TEMPO']}")
                    col_m2.markdown(f"📅 **Dias:** {row['DIAS_SEMANA']}")
                    
                    q_t = len(df_alunos[df_alunos['TURMA'] == row['ID_TURMA']])
                    q_p = len(df_alunos[(df_alunos['TURMA'] == row['ID_TURMA']) & 
                                       (~df_alunos['NECESSIDADES'].astype(str).str.upper().isin(["NENHUMA", "PENDENTE", ""]))])
                    
                    col_m3.metric("Alunos", q_t)
                    col_m3.button(f"Ver Lista: {row['ID_TURMA']}", key=f"ver_{row['ID_TURMA']}")
        else:
            st.info("📭 Nenhuma turma cadastrada.")

    # --- ABA 2: CRIAR TURMA (DNA CRONOLÓGICO) ---
    with tab_criar:
        st.subheader("🏗️ Configurar Nova Turma")
        with st.form("form_nova_turma", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            ano_t = c1.selectbox("Série/Ano:", [6, 7, 8, 9])
            letra_t = c2.selectbox("Letra:", ["A", "B", "C", "D", "E", "F"])
            turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino"])
            
            dias_aula = st.multiselect("📅 Dias de Aula:", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"], max_selections=2)
            
            if turno_t == "Matutino":
                opcoes_h = {"1º Tempo": "07:10h – 09:10h", "2º Tempo": "09:30h – 11:30h"}
            else:
                opcoes_h = {"1º Tempo": "13:10h – 15:10h", "2º Tempo": "15:30h – 17:30h"}
            
            tempo_sel = st.radio("⏰ Tempo de Aula:", list(opcoes_h.keys()), horizontal=True)
            
            if st.form_submit_button("🚀 CADASTRAR TURMA"):
                sigla = f"{ano_t}ª {'M' if turno_t == 'Matutino' else 'V'}{letra_t}"
                db.salvar_no_banco("DB_TURMAS", [sigla, f"{ano_t}º Ano {letra_t}", turno_t, " / ".join(dias_aula), f"{tempo_sel} ({opcoes_h[tempo_sel]})", "ATIVO"])
                st.success(f"✅ Turma {sigla} criada!"); st.rerun()

    # --- ABA 3: POVOAR ALUNOS ---
    with tab_povoar:
        st.subheader("➕ Inclusão de Estudantes")
        t_dest = st.selectbox("Turma de Destino:", df_turmas['ID_TURMA'].tolist() if not df_turmas.empty else [])
        metodo = st.radio("Método:", ["Manual", "CSV"], horizontal=True)
        
        if metodo == "Manual":
            with st.form("f_manual", clear_on_submit=True):
                nome_a = st.text_input("Nome Completo:").upper()
                nec_a = st.text_input("Necessidades/CID:", value="NENHUMA").upper()
                if st.form_submit_button("💾 Salvar"):
                    id_n = db.gerar_proximo_id(df_alunos)
                    db.salvar_no_banco("DB_ALUNOS", [id_n, nome_a, t_dest, "ATIVO", nec_a, "MANUAL"])
                    st.success("Cadastrado!"); st.rerun()
        else:
            f_csv = st.file_uploader("Arquivo CSV", type=["csv"])
            if f_csv and st.button("🚀 Importar Lista"):
                df_up = pd.read_csv(f_csv)
                id_b = db.gerar_proximo_id(df_alunos)
                for idx, r in df_up.iterrows():
                    db.salvar_no_banco("DB_ALUNOS", [id_b+idx, str(r['NOME']).upper(), t_dest, "ATIVO", "NENHUMA", "CSV"])
                st.success("Importado!"); st.rerun()

# --- ABA 4: EDIÇÃO & TRANSFERÊNCIA (VERSÃO BLINDADA V26.9) ---
    with tab_editar:
        st.subheader("✏️ Alterar Cadastro ou Transferir Aluno")
        
        c_ed1, c_ed2 = st.columns(2)
        # Lista de turmas que realmente possuem alunos cadastrados
        turmas_com_alunos = sorted(df_alunos['TURMA'].unique().tolist())
        t_origem = c_ed1.selectbox("Selecione a Turma Atual:", [""] + turmas_com_alunos, key="ed_t_orig")
        
        if t_origem:
            alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO")
            aluno_sel_nome = c_ed2.selectbox("Selecione o Aluno:", alunos_opcoes['NOME_ALUNO'].tolist())
            
            dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
            
            # INÍCIO DO FORMULÁRIO
            with st.form("form_edicao_aluno_v26"):
                st.markdown(f"### Editando: {aluno_sel_nome}")
                col_e1, col_e2 = st.columns(2)
                
                novo_nome = col_e1.text_input("Nome Completo:", value=dados_atuais['NOME_ALUNO'])
                nova_nec = col_e2.text_input("Necessidades/CID:", value=dados_atuais['NECESSIDADES'])
                
                col_e3, col_e4 = st.columns(2)
                
                # Lógica de Index Seguro para Status
                lista_status = ["ATIVO", "DESISTENTE", "TRANSFERIDO", "AFASTADO"]
                status_atual = str(dados_atuais['STATUS']).upper()
                idx_s = lista_status.index(status_atual) if status_atual in lista_status else 0
                novo_status = col_e3.selectbox("Status do Aluno:", lista_status, index=idx_s)
                
                # --- CORREÇÃO DO VALUEERROR (INDEX SEGURO PARA TURMA) ---
                lista_id_turmas = df_turmas['ID_TURMA'].tolist() if not df_turmas.empty else [t_origem]
                turma_atual_aluno = dados_atuais['TURMA']
                
                # Se a turma do aluno não estiver na lista de turmas, usamos o index 0 para não travar
                if turma_atual_aluno in lista_id_turmas:
                    idx_t = lista_id_turmas.index(turma_atual_aluno)
                else:
                    idx_t = 0
                
                nova_turma = col_e4.selectbox("Transferir para Turma:", lista_id_turmas, index=idx_t)
                
                # BOTÃO DE SUBMIT (OBRIGATÓRIO DENTRO DO FORM)
                btn_confirmar = st.form_submit_button("💾 CONFIRMAR ALTERAÇÕES E TRANSFERÊNCIA", use_container_width=True)
                
                if btn_confirmar:
                    # Lógica de salvamento (Upsert)
                    with st.spinner("Atualizando registro..."):
                        # Remove o antigo e salva o novo com o mesmo ID
                        db.excluir_registro("DB_ALUNOS", dados_atuais['NOME_ALUNO'])
                        sucesso = db.salvar_no_banco("DB_ALUNOS", [
                            dados_atuais['ID'], novo_nome.upper(), nova_turma, novo_status, nova_nec.upper(), "EDITADO"
                        ])
                        if sucesso:
                            st.success(f"✅ Dados de {novo_nome} atualizados!")
                            st.cache_data.clear()
                            time.sleep(1)
                            st.rerun()

        st.markdown("---")
        st.subheader("🗑️ Gestão de Turmas")
        t_para_deletar = st.selectbox("Excluir Turma (Cuidado):", [""] + df_turmas['ID_TURMA'].tolist())
        if t_para_deletar and st.button("🚨 APAGAR TURMA DEFINITIVAMENTE"):
            if len(df_alunos[df_alunos['TURMA'] == t_para_deletar]) > 0:
                st.error("❌ Não é possível apagar uma turma que ainda possui alunos.")
            else:
                db.excluir_registro("DB_TURMAS", t_para_deletar)
                st.success(f"Turma {t_para_deletar} removida."); st.rerun()

# ==============================================================================
# MÓDULO: BASE DE CONHECIMENTO
# ==============================================================================
elif menu == "📚 Base de Conhecimento":
    st.header("📚 Central de Inteligência SOSA")
    tab_upload, tab_biblioteca = st.tabs(["📤 Upload", "📖 Biblioteca"])
    with tab_upload:
        with st.form("form_upload"):
            tipo_doc = st.selectbox("Categoria:", ["Livro Didático - 6º Ano", "Livro Didático - 7º Ano", "Livro Didático - 8º Ano", "Livro Didático - 9º Ano", "Referencial Pedagógico (Prefeitura)", "Documento PEI / AEE", "Outros"])
            nome_arq = st.text_input("Nome do Arquivo")
            uploaded_file = st.file_uploader("Selecione o PDF", type=["pdf"])
            if st.form_submit_button("🚀 Salvar"):
                if uploaded_file and nome_arq:
                    temp_path = f"temp_{uploaded_file.name}"
                    with open(temp_path, "wb") as f: f.write(uploaded_file.getbuffer())
                    uri = ai.subir_para_google(temp_path, nome_arq)
                    db.salvar_no_banco("DB_MATERIAIS", [datetime.now().strftime("%d/%m/%Y"), nome_arq, uri, tipo_doc])
                    st.success("Catalogado!"); os.remove(temp_path); st.rerun()
    with tab_biblioteca:
        st.dataframe(df_materiais, use_container_width=True, hide_index=True)

# ==============================================================================
# MÓDULO: RELATÓRIOS PEI V26 - DOSSIÊ DE EVIDÊNCIAS INTEGRADO (CORRIGIDO)
# ==============================================================================
elif menu == "♿ Relatórios PEI / Perfil IA":
    st.title("♿ Analista de Inclusão: Dossiê de Evidências")
    st.markdown("---")

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia.")
    else:
        # --- 1. FILTRAGEM INTELIGENTE (CORREÇÃO DO ERRO .STR.STRIP) ---
        # Criamos uma máscara booleana blindada contra valores nulos (NaN)
        mask_pei = ~df_alunos['NECESSIDADES'].astype(str).str.upper().str.strip().isin(["NENHUMA", "PENDENTE", "", "NAN"])
        df_somente_pei = df_alunos[mask_pei]
        
        if df_somente_pei.empty:
            st.info("💡 Nenhum aluno com CID/Necessidades detectado. Mostrando lista geral para teste.")
            df_somente_pei = df_alunos

        c_t, c_a = st.columns([1, 2])
        turma_pei = c_t.selectbox("Filtrar Turma:", sorted(df_somente_pei['TURMA'].unique()), key="pei_t")
        
        lista_alunos_turma = df_somente_pei[df_somente_pei['TURMA'] == turma_pei]['NOME_ALUNO'].tolist()
        aluno_pei_nome = c_a.selectbox("Selecionar Estudante PEI:", lista_alunos_turma, key="pei_a")
        
        # Dados do Aluno Selecionado
        dados_a = df_somente_pei[df_somente_pei['NOME_ALUNO'] == aluno_pei_nome].iloc[0]
        id_a = db.limpar_id(dados_a['ID'])
        cid = dados_a['NECESSIDADES']

        # --- 2. MOTOR DE BUSCA DE EVIDÊNCIAS (DATA FUSION) ---
        with st.status("🔍 Maestro Sosa compilando evidências de todos os painéis...", expanded=False) as status:
            # A. Evidências do Diário (Engajamento e Bônus)
            d_aluno = df_diario[df_diario['ID_ALUNO'].apply(db.limpar_id) == id_a] if not df_diario.empty else pd.DataFrame()
            
            vistos_concluidos = 0
            bonus_total = 0.0
            if not d_aluno.empty:
                # Conta tags de conclusão PEI
                vistos_concluidos = len(d_aluno[d_aluno['TAGS'].astype(str).str.upper().str.contains("PEI CONCLUÍDO", na=False)])
                # Soma bônus ⭐
                if 'BONUS' in d_aluno.columns:
                    bonus_total = d_aluno['BONUS'].apply(util.sosa_to_float).sum()
            
            # B. Evidências do Scanner (Desempenho em Provas Adaptadas)
            s_aluno = df_diagnosticos[df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a] if not df_diagnosticos.empty else pd.DataFrame()
            media_scanner = s_aluno['NOTA_CALCULADA'].mean() if not s_aluno.empty else 0.0
            
            # C. Evidências do Planejamento (Estratégias Ponto ID)
            estrategias = []
            if not df_planos.empty:
                # Filtra planos do ano correspondente (ex: 6º ano)
                p_ano = df_planos[df_planos['ANO'].str.contains(str(turma_pei[0]), na=False)]
                for p_txt in p_ano['PLANO_TEXTO']:
                    est = ai.extrair_tag(p_txt, "ADAPTACAO_PEI")
                    if est and len(est) > 5: estrategias.append(est)
            estrategias_unicas = list(set(estrategias))[-3:] # Pega as 3 últimas

            status.update(label="✅ Dossiê de Evidências Compilado!", state="complete")

        # --- 3. DASHBOARD DE MONITORAMENTO PEI ---
        c_m1, c_m2, c_m3, c_m4 = st.columns(4)
        c_m1.metric("Engajamento PEI", f"{vistos_concluidos} Vistos")
        c_m2.metric("Bônus Acumulado ⭐", f"{bonus_total:.1f}")
        c_m3.metric("Média Scanner", f"{media_scanner:.2f}")
        c_m4.metric("Perfil", "Em Evolução" if bonus_total > 0 else "Monitoramento")

        tab_rel, tab_doc, tab_zap, tab_hist = st.tabs([
            "🧠 Relatório de Evidências (IA)", 
            "📄 Capa do PEI Oficial", 
            "📱 Comunicado Pais", 
            "🗂️ Histórico Salvo"
        ])

        # --- ABA 1: RELATÓRIO DE EVIDÊNCIAS (INTEGRAÇÃO TOTAL) ---
        with tab_rel:
            st.subheader("📝 Relatório Técnico de Acompanhamento")
            percepcao = st.text_area("Sua percepção analítica (O que a IA não viu?):", placeholder="Ex: Demonstrou maior autonomia na resolução de problemas...")
            
            if st.button("🚀 GERAR RELATÓRIO BASEADO EM EVIDÊNCIAS", type="primary", use_container_width=True):
                with st.spinner("Maestro Sosa cruzando dados e redigindo..."):
                    prompt_pei = (
                        f"VOCÊ É UM ESPECIALISTA EM EDUCAÇÃO INCLUSIVA (PADRÃO SOSA).\n"
                        f"ESTUDANTE: {aluno_pei_nome}. CID: {cid}.\n\n"
                        f"DADOS REAIS COLETADOS NO SISTEMA:\n"
                        f"- ENGAJAMENTO: {vistos_concluidos} atividades adaptadas concluídas.\n"
                        f"- MÉRITO: {bonus_total} pontos de bônus por desafios superados.\n"
                        f"- DESEMPENHO: Média de {media_scanner:.2f} no Scanner de Gabaritos.\n"
                        f"- ESTRATÉGIAS DO PONTO ID: {'; '.join(estrategias_unicas)}.\n"
                        f"- PERCEPÇÃO DO PROFESSOR: {percepcao}\n\n"
                        f"MISSÃO: Escreva um relatório técnico de evolução trimestral.\n"
                        f"REGRAS: Use linguagem clínica-pedagógica. Cite os números acima para validar o progresso. SEM MARKDOWN."
                    )
                    st.session_state.res_pei_v26 = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_pei)
            
            if "res_pei_v26" in st.session_state:
                txt_final = st.text_area("Relatório Gerado (Editável):", st.session_state.res_pei_v26, height=400)
                if st.button("💾 ARQUIVAR RELATÓRIO NO BANCO"):
                    db.salvar_no_banco("DB_RELATORIOS", [datetime.now().strftime("%d/%m/%Y"), id_a, aluno_pei_nome, "ACOMPANHAMENTO_PEI", txt_final])
                    st.success("Relatório arquivado com sucesso!")

        # --- ABA 2: CAPA DO PEI (INTEGRADO AO PONTO ID) ---
        with tab_doc:
            st.subheader("📄 Seção 1: Plano de Acessibilidade")
            if st.button("📄 Gerar Capa do PEI (Sincronizada com Planejamento)"):
                with st.spinner("Correlacionando barreiras e estratégias..."):
                    prompt_capa = (
                        f"ALUNO: {aluno_pei_nome}. CID: {cid}.\n"
                        f"ESTRATÉGIAS PLANEJADAS NO PONTO ID: {estrategias_unicas}.\n"
                        f"Gere a Seção 1 do PEI (Habilidades Sociais, Comunicativas, Emocionais e Funcionais) "
                        f"garantindo que as estratégias citadas coincidam com o que o professor já planejou."
                    )
                    st.session_state.res_capa_v26 = ai.gerar_ia("ESPECIALISTA_PEI", prompt_capa)
            
            if "res_capa_v26" in st.session_state:
                st.text_area("Texto da Capa:", st.session_state.res_capa_v26, height=400)

        # --- ABA 3: COMUNICADO PAIS (ZAP) ---
        with tab_zap:
            st.subheader("📱 Mensagem para Família")
            motivo = st.text_input("Motivo do contato:", "Progresso nas atividades adaptadas")
            if st.button("🚀 Gerar Mensagem Acolhedora"):
                base = st.session_state.get("res_pei_v26", "O aluno está evoluindo conforme o plano.")
                prompt_zap = f"Com base neste relatório: '{base}', gere uma mensagem de WhatsApp para os pais. Motivo: {motivo}. Tom: Empático e profissional."
                st.info(ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_zap))

# --- ABA 4: HISTÓRICO (VERSÃO BLINDADA CONTRA KEYERROR) ---
        with tab_hist:
            st.subheader("🗂️ Histórico de Documentos Salvos")
            if not df_relatorios.empty:
                # Filtra os relatórios do aluno
                hist = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_a].iloc[::-1]
                
                if not hist.empty:
                    for _, row in hist.iterrows():
                        # --- LÓGICA DE ACESSO SEGURO SOSA ---
                        # Tenta pegar a data, se não existir usa "Sem Data"
                        data_rel = row.get('DATA', 'Sem Data')
                        
                        # Tenta pegar 'TIPO', se não existir tenta 'TURMA', se não 'Registro'
                        # Isso evita o KeyError se a coluna mudar de nome na planilha
                        tipo_rel = row.get('TIPO', row.get('TURMA', 'REGISTRO'))
                        
                        conteudo_rel = row.get('CONTEUDO', 'Conteúdo não localizado.')

                        with st.expander(f"📅 {data_rel} - {tipo_rel}"):
                            st.write(conteudo_rel)
                else: 
                    st.info("📭 Nenhum documento encontrado para este aluno.")
            else: 
                st.info("📭 Banco de relatórios vazio.")

# ==============================================================================
# MÓDULO: ARQUITETO DE EXAMES - ARQUITETURA V33.0 (SESSÃO TRAVADA + DUAL SYNC)
# ==============================================================================
elif menu == "📝 Central de Avaliações":
    st.title("📝 Arquiteto de Exames e Gestão de Cronograma")
    st.markdown("---")
    
    def reset_avaliacoes():
        keys_to_del = ["temp_prova", "av_pei", "refino_av_ativo", "av_valor_total", "av_gab_pei", "av_res_pei_ia", "av_nome_fixo"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_av = int(time.time())
        st.rerun()

    if "v_av" not in st.session_state: st.session_state.v_av = 1
    v = st.session_state.v_av

    tab_arquiteto, tab_refino, tab_vis, tab_agenda, tab_acervo = st.tabs([
        "🚀 Arquiteto de Exames", "🤖 Refinador Maestro", "👁️ Visualização", "📅 Sincronia & Agenda", "🗂️ Acervo & Cronograma"
    ])

    # --- ABA 1: ARQUITETO (GERAÇÃO) ---
    with tab_arquiteto:
        is_refinando_av = "refino_av_ativo" in st.session_state
        if is_refinando_av:
            meta = st.session_state.refino_av_ativo
            st.warning(f"🛠️ **MODO REFINO ATIVO:** Editando {meta.get('tipo')} ({meta.get('ano')})")
            if st.button("❌ CANCELAR REFINO E VOLTAR AO NOVO"): reset_avaliacoes()

        with st.container(border=True):
            st.markdown("### ⚙️ 1. Configuração do Exame")
            c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
            opcoes_tipo = ["Teste", "Prova", "Recuperação Paralela", "Recuperação Final", "2ª Chamada"]
            
            idx_t = 0
            if is_refinando_av:
                tipo_orig = st.session_state.refino_av_ativo.get('tipo', '').split(" - ")[0]
                if tipo_orig in opcoes_tipo: idx_t = opcoes_tipo.index(tipo_orig)
            
            tipo_av = c1.selectbox("Tipo:", opcoes_tipo, index=idx_t, disabled=is_refinando_av, key=f"av_t_{v}")
            v_total = c2.number_input("Valor Total:", 0.0, 10.0, 3.0 if "Teste" in tipo_av else 4.0, step=0.5, key=f"av_v_{v}")
            
            lista_anos = [6, 7, 8, 9]
            idx_a = 0
            if is_refinando_av:
                ano_orig = str(st.session_state.refino_av_ativo.get('ano', '6')).replace('º','')
                if ano_orig.isdigit() and int(ano_orig) in lista_anos: idx_a = lista_anos.index(int(ano_orig))
            
            ano_av = c3.selectbox("Série:", lista_anos, index=idx_a, disabled=is_refinando_av, key=f"av_a_{v}")
            qtd_q = c4.number_input("Nº Questões:", 5, 20, 10, key=f"av_q_{v}")

        if not is_refinando_av:
            with st.container(border=True):
                st.markdown("### 🎯 2. Matriz PIP e Contexto")
                df_p_ano = df_planos[df_planos['ANO'] == f"{ano_av}º"]
                if not df_p_ano.empty:
                    semanas_av = st.multiselect("Semanas Base:", df_p_ano['SEMANA'].tolist(), key=f"av_s_{v}")
                    if st.button("💎 COMPILAR EXAME DE ELITE", use_container_width=True, type="primary"):
                        with st.spinner("Maestro Arquiteto processando..."):
                            planos_filtrados = df_p_ano[df_p_ano['SEMANA'].isin(semanas_av)]
                            ctx_p = "\n".join(planos_filtrados['PLANO_TEXTO'].tolist())
                            prompt = f"TIPO: {tipo_av} | VALOR: {v_total} | QTD: {qtd_q}\nPLANOS: {ctx_p}\nORDEM: Gere com [ORIENTACOES], [QUESTOES], [GABARITO_TEXTO] e [RESPOSTAS_IA]."
                            st.session_state.temp_prova = ai.gerar_ia("ARQUITETO_EXAMES_V25", prompt)
                            st.session_state.av_valor_total = v_total
                            # TRAVA O NOME DO ARQUIVO PARA A SESSÃO
                            st.session_state.av_nome_fixo = f"{tipo_av.upper()}_{ano_av}ANO_{datetime.now().strftime('%d%m_%H%M')}"
                            st.rerun()

    # --- ABA 2: REFINADOR MAESTRO ---
    with tab_refino:
        if "temp_prova" in st.session_state:
            st.subheader("🤖 Refinamento de Precisão")
            cmd = st.chat_input("Solicitar ajuste no exame...")
            if cmd:
                with st.spinner("Reescrevendo exame..."):
                    st.session_state.temp_prova = ai.gerar_ia("REFINADOR_EXAMES", f"ORDEM: {cmd}\n\nATUAL:\n{st.session_state.temp_prova}")
                    # IMPORTANTE: Se refinou a prova regular, o PEI antigo não vale mais
                    if "av_pei" in st.session_state: 
                        del st.session_state.av_pei
                        st.toast("⚠️ Prova alterada. Lembre-se de atualizar a versão PEI!", icon="♿")
                    st.session_state.v_av += 1
                    st.rerun()
            st.session_state.temp_prova = st.text_area("Editor de Exame:", st.session_state.temp_prova, height=500, key=f"ed_av_raw_{v}")
        else: st.info("Gere ou selecione uma prova para refinar.")

    # --- ABA 3: VISUALIZAÇÃO ---
    with tab_vis:
        if "temp_prova" in st.session_state:
            t_v_alu, t_v_gab, t_v_pei_prova, t_v_pei_gab = st.tabs([
                "📝 Aluno (Regular)", "✅ Gabarito (Regular)", "♿ Prova PEI", "📊 Gabarito PEI"
            ])
            with t_v_alu: st.text(ai.extrair_tag(st.session_state.temp_prova, "QUESTOES"))
            with t_v_gab: 
                st.code(ai.extrair_tag(st.session_state.temp_prova, "GABARITO_TEXTO"))
                st.write(ai.extrair_tag(st.session_state.temp_prova, "RESPOSTAS_IA"))
            
            with t_v_pei_prova:
                if st.button("✨ GERAR/ATUALIZAR PROVA PEI", use_container_width=True):
                    with st.spinner("Realizando Reengenharia PEI..."):
                        prompt_pei = f"ADAPTE PARA PEI: {ai.extrair_tag(st.session_state.temp_prova, 'QUESTOES')}. Use [PEI], [GABARITO_PEI] e [RESPOSTAS_PEI_IA]."
                        res_pei = ai.gerar_ia("ARQUITETO_PEI_V24", prompt_pei)
                        st.session_state.av_pei = ai.extrair_tag(res_pei, "PEI")
                        st.session_state.av_gab_pei = ai.extrair_tag(res_pei, "GABARITO_PEI")
                        st.session_state.av_res_pei_ia = ai.extrair_tag(res_pei, "RESPOSTAS_PEI_IA")
                        st.rerun()
                if "av_pei" in st.session_state:
                    st.text_area("Conteúdo PEI:", st.session_state.av_pei, height=400, key=f"area_pei_vis_{v}")
            with t_v_pei_gab:
                if "av_gab_pei" in st.session_state:
                    st.code(st.session_state.av_gab_pei)
                    st.write(st.session_state.get("av_res_pei_ia", ""))
        else: st.info("Aguardando geração...")

    # --- ABA 4: SINCRONIA & AGENDA (O BLOQUEIO DE SEGURANÇA) ---
    with tab_agenda:
        if "temp_prova" in st.session_state:
            st.subheader("📅 Finalização e Agendamento")
            c_s1, c_s2 = st.columns(2)
            trim_av = c_s1.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
            
            # NOME TRAVADO: Garante que o refino não crie um novo arquivo
            nome_sugerido = st.session_state.refino_av_ativo.get('nome_arquivo') if is_refinando_av else st.session_state.get('av_nome_fixo', 'AVALIACAO')
            nome_arq = c_s2.text_input("Nome do Arquivo (Drive):", nome_sugerido, key=f"name_av_input_{v}")
            
            sel_turmas = st.multiselect("Turmas:", sorted([t for t in df_alunos['TURMA'].unique() if str(ano_av) in str(t)]))
            data_app = st.date_input("Data:", date.today())

            # AVISO DE PEI PENDENTE
            if "av_pei" not in st.session_state:
                st.warning("⚠️ **Atenção:** A versão PEI ainda não foi gerada para este material.")

            if st.button("💾 FINALIZAR, SALVAR E AGENDAR", use_container_width=True, type="primary"):
                with st.status("🚀 Sincronizando...", expanded=True) as status:
                    # 1. DEFINIÇÃO DE VALORES E IDENTIFICADORES
                    v_total_num = st.session_state.get('av_valor_total', 10.0)
                    v_t_str = f"{v_total_num}".replace('.', ',')
                    
                    # Criamos um identificador único que inclui o Trimestre para facilitar a busca
                    identificador = f"{tipo_av} - {ano_av}º Ano ({trim_av})"
                    
                    info_doc = {"ano": f"{ano_av}º", "tipo_prova": tipo_av, "valor": v_t_str, "qtd_questoes": qtd_q, "trimestre": trim_av}
                    
                    # 2. LIMPEZA (UPSERT) - Remove versões antigas da mesma prova/ano/trimestre
                    db.excluir_avaliacao_completa(identificador, tipo_av)

                    # 3. UPLOAD DOS DOCUMENTOS
                    status.write("📄 Enviando Prova Regular...")
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, st.session_state.temp_prova, info_doc)
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, trimestre=trim_av, categoria=f"{ano_av}º Ano", semana="AVALIAÇÃO", modo="AVALIACAO")
                    
                    link_pei = "N/A"
                    if "av_pei" in st.session_state:
                        status.write("♿ Enviando Prova PEI...")
                        doc_pei = exporter.gerar_docx_prova_v25(f"{nome_arq}_PEI", st.session_state.av_pei, info_doc)
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_arq}_PEI", trimestre=trim_av, categoria=f"{ano_av}º Ano", semana="AVALIAÇÃO", modo="AVALIACAO")
                    
                    if "https" in str(link_reg):
                        # 4. INJEÇÃO DE DNA (METADADOS PARA O SCANNER E NOTAS)
                        # Aqui inserimos as tags que o Scanner vai ler para saber o valor real
                        dna_sosa = f"\n\n[METADADOS_AVALIAÇÃO]\n[VALOR: {v_total_num}]\n[TRIMESTRE: {trim_av}]\n"
                        
                        conteudo_banco = (
                            f"{dna_sosa}" # DNA no topo para leitura rápida
                            f"{st.session_state.temp_prova}\n\n"
                            f"[PEI]\n{st.session_state.get('av_pei','')}\n\n"
                            f"[GABARITO_PEI]\n{st.session_state.get('av_gab_pei','')}\n\n"
                            f"[RESPOSTAS_PEI_IA]\n{st.session_state.get('av_res_pei_ia','')}\n\n"
                            f"--- LINKS ---\nRegular({link_reg}) PEI({link_pei})"
                        )
                        
                        # 5. SALVAMENTO NO ACERVO (DB_AULAS_PRONTAS)
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), 
                            "AVALIAÇÃO", 
                            identificador, 
                            conteudo_banco, 
                            f"{ano_av}º", 
                            link_reg
                        ])
                        
                        # 6. REGISTRO NO CRONOGRAMA (DB_REGISTRO_AULAS)
                        for t in sel_turmas:
                            db.salvar_no_banco("DB_REGISTRO_AULAS", [
                                data_app.strftime("%d/%m/%Y"), 
                                "AVALIAÇÃO", 
                                t, 
                                f"Aplicação: {tipo_av} (Valor: {v_t_str})", 
                                "SIM", 
                                "AGENDADA"
                            ])
                        
                        status.update(label="✅ Sincronia Concluída!", state="complete")
                        st.balloons(); time.sleep(1.5); reset_avaliacoes()
        else: st.info("Gere a prova primeiro.")

    # --- ABA 5: ACERVO & CRONOGRAMA ---
    with tab_acervo:
        c_h1, c_h2 = st.columns([1.6, 1])
        with c_h1:
            st.markdown("#### 📄 Exames Gerados")
            df_exames = df_aulas[df_aulas['SEMANA_REF'] == "AVALIAÇÃO"].iloc[::-1]
            for _, row in df_exames.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['TIPO_MATERIAL']}**")
                    txt_f = str(row['CONTEUDO'])
                    l_reg = re.search(r"Regular\((.*?)\)", txt_f).group(1) if "Regular(" in txt_f else row.get('LINK_DRIVE')
                    l_pei = re.search(r"PEI\((.*?)\)", txt_f).group(1) if "PEI(" in txt_f and "PEI(N/A)" not in txt_f else None

                    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
                    if l_reg: c_b1.link_button("📝 REGULAR", str(l_reg), use_container_width=True)
                    if l_pei: c_b2.link_button("♿ PEI", str(l_pei), use_container_width=True)
                    else: c_b2.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                    
                    if c_b3.button("🔄 REFINAR", key=f"ref_av_{row.name}", use_container_width=True):
                        st.session_state.temp_prova = ai.extrair_tag(txt_f, "QUESTOES") or txt_f.split("[PEI]")[0]
                        st.session_state.av_pei = ai.extrair_tag(txt_f, "PEI")
                        st.session_state.av_gab_pei = ai.extrair_tag(txt_f, "GABARITO_PEI")
                        st.session_state.av_res_pei_ia = ai.extrair_tag(txt_f, "RESPOSTAS_PEI_IA")
                        st.session_state.refino_av_ativo = {
                            "tipo": str(row['TIPO_MATERIAL']), 
                            "ano": str(row['ANO']),
                            "nome_arquivo": str(row['TIPO_MATERIAL']).replace(" - ", "_")
                        }
                        st.rerun()
                        
                    if c_b4.button("🗑️ Apagar", key=f"del_av_{row.name}", use_container_width=True):
                        db.excluir_avaliacao_completa(row['TIPO_MATERIAL'], str(row['TIPO_MATERIAL']).split(" - ")[0])
                        st.rerun()
        with c_h2:
            st.markdown("#### 🗓️ Próximas Aplicações")
            if not df_registro_aulas.empty:
                # --- FILTRO ROBUSTO SOSA V26 ---
                # Remove espaços e garante que compare sempre em maiúsculas
                df_cron = df_registro_aulas[
                    df_registro_aulas['SEMANA'].astype(str).str.strip().str.upper() == "AVALIAÇÃO"
                ].copy()
                
                if not df_cron.empty:
                    # Ordena pela data mais próxima
                    st.dataframe(
                        df_cron[['DATA', 'TURMA', 'CONTEUDO_MINISTRADO', 'STATUS_CURRICULO']], 
                        use_container_width=True, 
                        hide_index=True
                    )
                else:
                    st.info("📅 Nenhuma prova agendada no cronograma para exibir.")
            else:
                st.info("📭 O Diário de Classe (Registro) está vazio.")

# ==============================================================================
# MÓDULO: SCANNER & PERÍCIA - ARQUITETURA V26 (INTEGRAL CORRIGIDA)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("📸 Inteligência Diagnóstica e Perícia")
    st.markdown("---")

    def reset_scanner():
        if "scan_res" in st.session_state: del st.session_state.scan_res
        if "scan_img" in st.session_state: del st.session_state.scan_img
        st.session_state.v_scan = int(time.time())
        st.rerun()

    if "v_scan" not in st.session_state: st.session_state.v_scan = 1
    v = st.session_state.v_scan

    # --- 1. FILTROS ESTRATÉGICOS ---
    with st.container(border=True):
        st.markdown("### 🔍 Filtros de Perícia")
        c1, c2, c3 = st.columns(3)
        lista_anos = ["Todos", "6º", "7º", "8º", "9º"]
        f_ano = c1.selectbox("Série/Ano:", lista_anos, key=f"f_ano_scan_{v}")
        lista_trim = ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"]
        f_trim = c2.selectbox("Trimestre:", lista_trim, key=f"f_trim_scan_{v}")
        turmas_disponiveis = sorted(df_alunos['TURMA'].unique())
        if f_ano != "Todos":
            turmas_disponiveis = [t for t in turmas_disponiveis if f_ano[0] in t]
        f_turma = c3.selectbox("Turma:", ["Todas"] + turmas_disponiveis, key=f"f_turma_scan_{v}")

    # --- 2. FILTRAGEM DO BANCO DE DADOS ---
    df_p = df_diagnosticos.copy()
    if f_ano != "Todos": df_p = df_p[df_p['TURMA'].str.contains(f_ano[0])]
    if f_turma != "Todas": df_p = df_p[df_p['TURMA'] == f_turma]

    tab_scan, tab_acervo, tab_dash = st.tabs([
        "📸 Capturar Gabarito", 
        "📂 Acervo de Evidências", 
        "📊 Dashboard de Perícia (Raio-X)"
    ])

    # --- ABA 1: CAPTURAR GABARITO (DENTRO DO ELIF) ---
    with tab_scan:
        if f_turma == "Todas":
            st.warning("⚠️ Selecione uma **Turma** nos filtros acima.")
        else:
            serie_num = "".join(filter(str.isdigit, f_ano)) if f_ano != "Todos" else ""
            provas_filtro = df_aulas[(df_aulas['SEMANA_REF'] == "AVALIAÇÃO") & (df_aulas['ANO'].str.contains(serie_num))]
            
            if provas_filtro.empty:
                st.error(f"❌ Nenhuma avaliação encontrada para o {f_ano}.")
            else:
                c_av1, c_av2 = st.columns([2, 1])
                prova_sel = c_av1.selectbox("📋 Avaliação:", provas_filtro['TIPO_MATERIAL'].tolist(), key=f"p_scan_act_{v}")
                
                prova_data = provas_filtro[provas_filtro['TIPO_MATERIAL'] == prova_sel].iloc[0]
                txt_conteudo = str(prova_data['CONTEUDO'])
                
                # DNA SOSA: Detecção de Valor
                match_v = re.search(r"\[VALOR:\s*(\d+[\.,]\d+|\d+)\]", txt_conteudo.upper())
                if match_v: v_prova_base = util.sosa_to_float(match_v.group(1))
                else:
                    if "TESTE" in prova_sel.upper(): v_prova_base = 3.0
                    else: v_prova_base = 4.0

                ids_corrigidos = df_p[df_p['ID_AVALIACAO'] == prova_sel]['ID_ALUNO'].astype(str).tolist() if not df_p.empty else []
                alunos_pendentes = df_alunos[(df_alunos['TURMA'] == f_turma) & (~df_alunos['ID'].astype(str).isin(ids_corrigidos))]

                if alunos_pendentes.empty:
                    st.success(f"✅ Todos os alunos da turma {f_turma} já foram escaneados!")
                else:
                    aluno_scan = st.selectbox("👤 Aluno Pendente:", alunos_pendentes['NOME_ALUNO'].tolist(), key=f"a_scan_act_{v}")
                    aluno_info = df_alunos[df_alunos['NOME_ALUNO'] == aluno_scan].iloc[0]
                    is_pei_aluno = str(aluno_info['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
                    
                    if is_pei_aluno:
                        st.warning(f"♿ **MODO PEI ATIVADO:** {aluno_scan} ({aluno_info['NECESSIDADES']})")
                        gab_raw = ai.extrair_tag(txt_conteudo, "GABARITO_PEI")
                        if not gab_raw: gab_raw = ai.extrair_tag(txt_conteudo, "GABARITO_REGULAR") or ai.extrair_tag(txt_conteudo, "GABARITO_TEXTO")
                    else:
                        st.success(f"📝 **MODO REGULAR:** {aluno_scan}")
                        gab_raw = ai.extrair_tag(txt_conteudo, "GABARITO_REGULAR") or ai.extrair_tag(txt_conteudo, "GABARITO_TEXTO")

                    gab_oficial = re.findall(r"\d+[\s\.\:\-]*([A-E])", gab_raw.upper())
                    qtd_q = len(gab_oficial)
                    
                    st.info(f"📊 **Configuração:** {qtd_q} questões | Valor: {v_prova_base:.1f} pts.")
                    img_file = st.camera_input("📸 Capture o Gabarito", key=f"cam_input_{v}")

                    if img_file:
                        if st.button("🧠 ANALISAR MARCAÇÕES", type="primary", use_container_width=True):
                            with st.spinner("Analisando..."):
                                st.session_state.scan_res = ai.analisar_gabarito_vision(img_file.getvalue())
                                st.session_state.scan_img = img_file.getvalue()
                                st.rerun()

                    if "scan_res" in st.session_state:
                        st.subheader("📝 Conferência de Perícia")
                        dados_pericia = []
                        for i in range(1, qtd_q + 1):
                            q_key = f"{i:02d}"
                            resp_aluno = st.session_state.scan_res.get(q_key) or st.session_state.scan_res.get(str(i)) or "?"
                            resp_certa = gab_oficial[i-1] if i <= len(gab_oficial) else "?"
                            dados_pericia.append({"Q": q_key, "Marcação": resp_aluno, "Gabarito": resp_certa})
                        
                        df_base = pd.DataFrame(dados_pericia)

                        def calcular_status(row):
                            m, g = str(row['Marcação']).upper(), str(row['Gabarito']).upper()
                            if m == g: return "✅ CORRETA"
                            if m == "X": return "🚫 ANULADA"
                            if m == "?" or m == "": return "⚪ VAZIA"
                            return "❌ INCORRETA"

                        df_base['Status'] = df_base.apply(calcular_status, axis=1)

                        df_edit = st.data_editor(
                            df_base,
                            use_container_width=True,
                            hide_index=True,
                            column_config={
                                "Q": st.column_config.TextColumn("Q", disabled=True),
                                "Marcação": st.column_config.SelectboxColumn("Marcação", options=["A", "B", "C", "D", "E", "X", "?"], required=True),
                                "Gabarito": st.column_config.TextColumn("Gabarito", disabled=True),
                                "Status": st.column_config.TextColumn("Status", disabled=True)
                            },
                            key=f"editor_pericia_{v}"
                        )

                        df_edit['Status'] = df_edit.apply(calcular_status, axis=1)
                        acertos = len(df_edit[df_edit['Marcação'] == df_edit['Gabarito']])
                        nota_final = (acertos / qtd_q) * v_prova_base
                        st.metric("Nota Final (Precisão SOSA)", f"{nota_final:.2f}", delta=f"{acertos}/{qtd_q} acertos")

                        c_btn1, c_btn2 = st.columns(2)
                        if c_btn1.button("💾 SALVAR E PRÓXIMO", type="primary", use_container_width=True):
                            with st.status("Sincronizando...", expanded=False) as status:
                                import io
                                img_io = io.BytesIO(st.session_state.scan_img)
                                link_foto = db.subir_e_converter_para_google_docs(img_io, f"SCAN_{aluno_scan}", trimestre=f_trim, categoria=f_turma, modo="SCANNER")
                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                    datetime.now().strftime("%d/%m/%Y"), aluno_info['ID'], aluno_scan, f_turma, prova_sel,
                                    ";".join(df_edit['Marcação'].tolist()), util.sosa_to_str(nota_final), link_foto
                                ])
                                status.update(label="✅ Salvo!", state="complete")
                                st.balloons(); time.sleep(1); reset_scanner()
                        
                        if c_btn2.button("🗑️ DESCARTAR", use_container_width=True):
                            reset_scanner()
                            
    # --- ABA 2: ACERVO DE EVIDÊNCIAS (DENTRO DO ELIF) ---
    with tab_acervo:
        st.subheader(f"📂 Histórico de Correções - {f_turma if f_turma != 'Todas' else 'Geral'}")
        if not df_p.empty:
            st.dataframe(df_p, column_config={"NOTA_CALCULADA": st.column_config.NumberColumn("Nota", format="%.2f"), "LINK_FOTO_DRIVE": st.column_config.LinkColumn("📸 Ver Gabarito")}, use_container_width=True, hide_index=True)
        else: st.info("📭 Nenhum registro encontrado.")

    # --- ABA 3: DASHBOARD DE PERÍCIA (DENTRO DO ELIF) ---
    with tab_dash:
        if not df_p.empty:
            provas_no_filtro = df_p['ID_AVALIACAO'].unique()
            prova_alvo = st.selectbox("🎯 Selecione a Avaliação para Análise:", provas_no_filtro, key="sb_dash_av")
            
            df_pericia = pd.merge(df_p[df_p['ID_AVALIACAO'] == prova_alvo], df_alunos[['ID', 'NECESSIDADES']], left_on='ID_ALUNO', right_on='ID', how='left')
            df_pericia['PERFIL'] = df_pericia['NECESSIDADES'].apply(lambda x: "♿ PEI" if str(x).upper() not in ["NENHUMA", "PENDENTE", ""] else "📝 REGULAR")
            
            prova_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == prova_alvo]
            if not prova_ref.empty:
                txt_full = str(prova_ref.iloc[0]['CONTEUDO'])
                v_base_dash = 10.0
                match_v_d = re.search(r"VALOR:?\s*(\d+[\.,]\d+|\d+)", txt_full.upper())
                if match_v_d: v_base_dash = util.sosa_to_float(match_v_d.group(1))
                elif "TESTE" in prova_alvo.upper(): v_base_dash = 3.0
                elif "PROVA" in prova_alvo.upper(): v_base_dash = 4.0

                t_reg, t_pei = st.tabs(["📝 Visão Regular", "♿ Visão PEI (Adaptada)"])

                def gerar_raio_x(perfil_tipo, tag_gabarito, v_ref):
                    df_f = df_pericia[df_pericia['PERFIL'] == perfil_tipo]
                    if df_f.empty:
                        st.info(f"Nenhum aluno do perfil {perfil_tipo} escaneado.")
                        return
                    gab_raw = ai.extrair_tag(txt_full, tag_gabarito) or ai.extrair_tag(txt_full, "GABARITO_REGULAR")
                    gab_oficial = re.findall(r"\d+[\s\.\:\-]*([A-E])", gab_raw.upper())
                    questoes_brutas = ai.extrair_tag(txt_full, "QUESTOES")
                    lista_enunciados = re.split(r'\d+[\s\.\ª\º]*Questão[\s\.\:]*', questoes_brutas)
                    lista_enunciados = [q.strip() for q in lista_enunciados if q.strip()]
                    stats = []
                    for i, certa in enumerate(gab_oficial):
                        respostas = [r.split(";")[i] if len(r.split(";")) > i else "?" for r in df_f['RESPOSTAS_ALUNO']]
                        acertos = respostas.count(certa)
                        stats.append({"Questão": f"{i+1:02d}", "Acerto %": (acertos/len(df_f)*100), "Gabarito": certa, "Texto": lista_enunciados[i] if i < len(lista_enunciados) else ""})
                    
                    df_stats = pd.DataFrame(stats)
                    c1, c2, c3 = st.columns(3)
                    media_p = df_f['NOTA_CALCULADA'].mean()
                    c1.metric(f"Média {perfil_tipo}", f"{media_p:.2f}")
                    c2.metric("Aproveitamento", f"{(media_p/v_ref*100):.1f}%")
                    c3.metric("Total Alunos", len(df_f))
                    st.plotly_chart(px.bar(df_stats, x="Questão", y="Acerto %", text="Acerto %", color="Acerto %", color_continuous_scale="RdYlGn", range_y=[0, 110]), use_container_width=True)
                    for _, row in df_stats.iterrows():
                        cor = "🔴" if row['Acerto %'] < 50 else "🟡" if row['Acerto %'] < 75 else "🟢"
                        with st.expander(f"{cor} Questão {row['Questão']} - Domínio: {row['Acerto %']:.1f}%"):
                            st.write(f"**Enunciado:** {row['Texto']}")

                with t_reg: gerar_raio_x("📝 REGULAR", "GABARITO_REGULAR", v_base_dash)
                with t_pei: gerar_raio_x("♿ PEI", "GABARITO_PEI", v_base_dash)
            else: st.error("❌ Conteúdo da prova não localizado.")
        else: st.info("📭 Selecione os filtros para visualizar o Dashboard de Perícia.")
