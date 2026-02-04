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
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR) - ARQUITETURA V30.6 (FIX NAMEERROR)
# ==============================================================================
if menu == "🧪 Criador de Aulas":
    st.title("🧪 Laboratório de Produção Semiótica")
    st.markdown("---")
    
    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "refino_lab_ativo", "refino_lab_tipo", "comp_temp", "comp_pei"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_lab = int(time.time())
        st.rerun()

    if "v_lab" not in st.session_state: st.session_state.v_lab = 1
    v = st.session_state.v_lab

    tab_producao, tab_complementar, tab_acervo = st.tabs([
        "🚀 Laboratório de Produção", 
        "📚 Atividades Complementares",
        "📂 Acervo de Materiais"
    ])

    # --- ABA 1: LABORATÓRIO DE PRODUÇÃO (AULA 1 E 2) ---
    with tab_producao:
        is_refinando_aula = "refino_lab_ativo" in st.session_state and st.session_state.get("refino_lab_tipo") == "AULA"
        
        if is_refinando_aula:
            meta = st.session_state.refino_lab_ativo
            st.warning(f"🛠️ **MODO REFINO ATIVO:** Editando **{meta['aula']}** | **{meta['semana']}**")
            if st.button("❌ CANCELAR REFINO", key="canc_ref_aula"): reset_laboratorio()

        with st.container(border=True):
            st.markdown("### ⚙️ 1. Parâmetros de Regência")
            c1, c2, c3 = st.columns([1, 2, 1.5])
            lista_anos = [6, 7, 8, 9]
            idx_ano = lista_anos.index(int(st.session_state.refino_lab_ativo['ano'].replace('º',''))) if is_refinando_aula else 0
            ano_lab = c1.selectbox("Série/Ano:", lista_anos, index=idx_ano, disabled=is_refinando_aula, key=f"lab_ano_{v}")
            planos_ano = df_planos[df_planos['ANO'] == f"{ano_lab}º"]
            
            if planos_ano.empty:
                st.error(f"❌ Nenhum plano encontrado para o {ano_lab}º Ano.")
                aula_alvo = None
            else:
                todas_semanas = planos_ano['SEMANA'].tolist()
                idx_sem = todas_semanas.index(st.session_state.refino_lab_ativo['semana']) if is_refinando_aula else 0
                sem_lab = c2.selectbox("Semana de Referência (PIP):", todas_semanas, index=idx_sem, disabled=is_refinando_aula, key=f"lab_sem_{v}")
                aula_alvo = c3.radio("🎯 Alvo da Produção:", ["Aula 1", "Aula 2"], index=0, horizontal=True, disabled=is_refinando_aula)

        if aula_alvo and not is_refinando_aula:
            plano_row = planos_ano[planos_ano['SEMANA'] == sem_lab].iloc[0]
            plano_raw = plano_row['PLANO_TEXTO']
            with st.container(border=True):
                st.markdown(f"### 🔗 Sincronia PIP: {aula_alvo}")
                col_p1, col_p2, col_p3 = st.columns([1, 1, 1.5])
                qtd_q = col_p1.slider("Nº de Questões:", 1, 15, 5, key=f"q_sld_{v}")
                nivel = col_p2.select_slider("Rigor Técnico:", options=["Básico", "Médio", "Desafio"], key=f"rig_sld_{v}")
                instr_extra = col_p3.text_input("Instruções Adicionais:", placeholder="Ex: Use exemplos de Itabuna...", key=f"inst_in_{v}")
                if st.button("💎 COMPILAR MATERIAL DE ELITE", use_container_width=True, type="primary"):
                    st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR AULA. PLANO: {plano_raw}. FOCO: {aula_alvo}. QTD: {qtd_q}. NÍVEL: {nivel}. EXTRA: {instr_extra}")
                    st.session_state.refino_lab_tipo = "AULA"
                    st.rerun()

        if "lab_temp" in st.session_state and st.session_state.get("refino_lab_tipo") == "AULA":
            st.markdown("---")
            cmd_refine = st.chat_input("Deseja ajustar algo na aula?")
            if cmd_refine:
                st.session_state.lab_temp = ai.gerar_ia("REFINADOR_MATERIAIS", f"ORDEM: {cmd_refine}\n\nATUAL:\n{st.session_state.lab_temp}")
                st.session_state.v_lab += 1
                st.rerun()
            
            t_prof, t_alu, t_gab, t_pei, t_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "✅ Gabarito", "♿ PEI", "☁️ SINCRONIA"])
            with t_prof: ed_prof = st.text_area("Lousa:", ai.extrair_tag(st.session_state.lab_temp, "PROFESSOR"), height=400, key=f"ed_prof_{v}")
            with t_alu: ed_alu = st.text_area("Folha:", ai.extrair_tag(st.session_state.lab_temp, "ALUNO"), height=400, key=f"ed_alu_{v}")
            with t_gab: ed_gab = st.text_area("Gabarito:", ai.extrair_tag(st.session_state.lab_temp, "GABARITO"), height=200, key=f"ed_gab_{v}")
            with t_pei:
                txt_pei_aula = st.session_state.get("lab_pei") or ai.extrair_tag(st.session_state.lab_temp, "PEI")
                if not txt_pei_aula:
                    if st.button("✨ GERAR PEI", key="btn_gen_pei_aula"):
                        st.session_state.lab_pei = ai.gerar_ia("ARQUITETO_PEI_V24", f"ADAPTE: {ed_alu}")
                        st.rerun()
                else: st.session_state.lab_pei = st.text_area("Material PEI:", txt_pei_aula, height=400, key=f"ed_pei_aula_{v}")
            
            with t_sync:
                if st.button("💾 FINALIZAR E SINCRONIZAR (TRIPLE SYNC)", use_container_width=True, type="primary"):
                    with st.status("🚀 Sincronizando Aula...", expanded=True) as status:
                        f_aula = st.session_state.refino_lab_ativo['aula'].split(" - ")[0] if is_refinando_aula else aula_alvo
                        f_sem = st.session_state.refino_lab_ativo['semana'] if is_refinando_aula else sem_lab
                        f_ano = st.session_state.refino_lab_ativo['ano'] if is_refinando_aula else f"{ano_lab}º"
                        nome_base = f"AULA_{f_aula.replace(' ','')}_{f_ano.replace('º','')}ANO_{f_sem.replace(' ','')}"
                        
                        status.write("🧹 Limpando versões obsoletas...")
                        db.excluir_registro_com_drive("DB_AULAS_PRONTAS", f"{f_aula} - {f_sem}")
                        
                        status.write("📄 Enviando Material do Aluno...")
                        doc_alu = exporter.gerar_docx_aluno_v24(nome_base, ed_alu, {"ano": f_ano, "trimestre": "I Trimestre"})
                        link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_base}_ALUNO", trimestre="I Trimestre", categoria=f_ano, semana=f_sem, modo="AULA")
                        
                        status.write("👨‍🏫 Enviando Guia do Professor...")
                        doc_prof = exporter.gerar_docx_professor_v25(nome_base, ed_prof, {"ano": f_ano, "semana": f_sem, "trimestre": "I Trimestre"})
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_base}_PROF", trimestre="I Trimestre", categoria=f_ano, semana=f_sem, modo="AULA")
                        
                        link_pei = "N/A"
                        if st.session_state.get("lab_pei"):
                            status.write("♿ Enviando Material PEI...")
                            doc_pei = exporter.gerar_docx_pei_v25(f"{nome_base}_PEI", st.session_state.lab_pei, {"ano": f_ano, "trimestre": "I Trimestre"})
                            link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_base}_PEI", trimestre="I Trimestre", categoria=f_ano, semana=f_sem, modo="AULA")
                        
                        conteudo_banco = f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n[PEI]\n{st.session_state.get('lab_pei', 'N/A')}\n\n--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI({link_pei})"
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), f_sem, f"{f_aula} - {f_sem}", conteudo_banco, f_ano, link_alu])
                        status.update(label="✅ Aula Sincronizada!", state="complete"); st.balloons(); time.sleep(1.5); reset_laboratorio()

    # --- ABA 2: ATIVIDADES COMPLEMENTARES ---
    with tab_complementar:
        is_refinando_comp = "refino_lab_ativo" in st.session_state and st.session_state.get("refino_lab_tipo") == "COMPLEMENTAR"
        
        if is_refinando_comp:
            meta = st.session_state.refino_lab_ativo
            st.warning(f"🛠️ **MODO REFINO ATIVO:** Editando **{meta['aula']}** | **{meta['semana']}**")
            if st.button("❌ CANCELAR REFINO", key="canc_ref_comp"): reset_laboratorio()

        if not is_refinando_comp:
            st.subheader("📚 Laboratório de Reforço e Aprofundamento")
            with st.container(border=True):
                c_c1, c_c2, c_c3 = st.columns([1, 2, 1.5])
                ano_comp = c_c1.selectbox("Série:", [6, 7, 8, 9], key=f"comp_ano_{v}")
                planos_comp = df_planos[df_planos['ANO'] == f"{ano_comp}º"]
                if planos_comp.empty: st.warning("⚠️ Selecione uma série com planos cadastrados.")
                else:
                    sem_comp = c_c2.selectbox("Semana Base (PIP):", planos_comp['SEMANA'].tolist(), key=f"comp_sem_{v}")
                    foco_comp = c_c3.selectbox("Foco Pedagógico:", ["Fixação (Mecânico)", "Desafio (Contextualizado)", "Recomposição (Básico)"])
                    plano_ref = planos_comp[planos_comp['SEMANA'] == sem_comp].iloc[0]['PLANO_TEXTO']
                    st.info(f"🔗 **PIP Ativo:** Gerando exercícios sobre '{ai.extrair_tag(plano_ref, 'CONTEUDOS_ESPECIFICOS')}'")
                    col_cp1, col_cp2 = st.columns(2)
                    qtd_comp = col_cp1.slider("Quantidade de Questões:", 5, 20, 10, key=f"comp_q_{v}")
                    nivel_comp = col_cp2.select_slider("Nível de Dificuldade:", options=["Fácil", "Médio", "Difícil"], value="Médio")
                    if st.button("💎 GERAR LISTA DE ELITE", use_container_width=True, type="primary"):
                        st.session_state.comp_temp = ai.gerar_ia("MESTRE_V24", f"GERAR LISTA COMPLEMENTAR. BASE: {plano_ref}. QTD: {qtd_comp}. NÍVEL: {nivel_comp}. FOCO: {foco_comp}.")
                        st.session_state.refino_lab_tipo = "COMPLEMENTAR"
                        st.rerun()

        if ("comp_temp" in st.session_state) or (is_refinando_comp and "lab_temp" in st.session_state):
            st.markdown("---")
            txt_base = st.session_state.get("comp_temp") or st.session_state.get("lab_temp")
            
            cmd_ref_comp = st.chat_input("Refinar lista complementar...")
            if cmd_ref_comp:
                novo_txt = ai.gerar_ia("REFINADOR_MATERIAIS", f"ORDEM: {cmd_ref_comp}\n\nATUAL:\n{txt_base}")
                if is_refinando_comp: st.session_state.lab_temp = novo_txt
                else: st.session_state.comp_temp = novo_txt
                st.session_state.v_lab += 1
                st.rerun()
            
            t_c_alu, t_c_gab, t_c_pei, t_c_sync = st.tabs(["📝 Lista Regular", "✅ Gabarito", "♿ PEI", "☁️ Sincronia"])
            with t_c_alu: ed_comp_alu = st.text_area("Conteúdo:", ai.extrair_tag(txt_base, "ALUNO"), height=400, key=f"ed_comp_alu_{v}")
            with t_c_gab: ed_comp_gab = st.text_area("Gabarito:", ai.extrair_tag(txt_base, "GABARITO"), height=300, key=f"ed_comp_gab_{v}")
            with t_c_pei:
                txt_pei_comp = st.session_state.get("comp_pei") or ai.extrair_tag(txt_base, "PEI")
                if not txt_pei_comp:
                    if st.button("✨ GERAR PEI", key="btn_gen_pei_comp"):
                        st.session_state.comp_pei = ai.gerar_ia("ARQUITETO_PEI_V24", f"ADAPTE: {ed_comp_alu}")
                        st.rerun()
                else: st.session_state.comp_pei = st.text_area("Lista PEI:", txt_pei_comp, height=400, key=f"ed_comp_pei_{v}")

            with t_c_sync:
                if st.button("💾 SALVAR TUDO NO DRIVE", use_container_width=True, type="primary"):
                    with st.status("🚀 Enviando Lista Complementar...", expanded=True) as status:
                        f_sem = st.session_state.refino_lab_ativo['semana'] if is_refinando_comp else sem_comp
                        f_ano = st.session_state.refino_lab_ativo['ano'] if is_refinando_comp else f"{ano_comp}º"
                        f_tipo = st.session_state.refino_lab_ativo['aula'] if is_refinando_comp else f"LISTA COMPLEMENTAR - {foco_comp}"
                        nome_comp = f"LISTA_{f_ano.replace('º','')}ANO_{f_sem.replace(' ','')}"
                        
                        status.write("🧹 Limpando versões obsoletas...")
                        db.excluir_registro_com_drive("DB_AULAS_PRONTAS", f_tipo)
                        
                        status.write("📤 Enviando Lista Regular...")
                        doc_comp = exporter.gerar_docx_aluno_v24(nome_comp, ed_comp_alu, {"ano": f_ano, "trimestre": "I Trimestre"})
                        link_comp = db.subir_e_converter_para_google_docs(doc_comp, nome_comp, trimestre="I Trimestre", categoria=f_ano, semana=f_sem, modo="AULA")
                        
                        link_comp_pei = "N/A"
                        if st.session_state.get("comp_pei"):
                            status.write("📤 Enviando Lista PEI...")
                            doc_comp_pei = exporter.gerar_docx_pei_v25(f"{nome_comp}_PEI", st.session_state.comp_pei, {"ano": f_ano, "trimestre": "I Trimestre"})
                            link_comp_pei = db.subir_e_converter_para_google_docs(doc_comp_pei, f"{nome_comp}_PEI", trimestre="I Trimestre", categoria=f_ano, semana=f_sem, modo="AULA")
                        
                        status.write("💾 Registrando no Acervo...")
                        conteudo_banco = f"[ALUNO]\n{ed_comp_alu}\n\n[GABARITO]\n{ed_comp_gab}\n\n[PEI]\n{st.session_state.get('comp_pei', 'N/A')}\n\n--- LINKS ---\nRegular({link_comp}) PEI({link_comp_pei})"
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), f_sem, f_tipo, conteudo_banco, f_ano, link_comp])
                        status.update(label="✅ Lista Sincronizada!", state="complete"); st.balloons(); time.sleep(1.5); reset_laboratorio()

    # --- ABA 3: ACERVO DE MATERIAIS ---
    with tab_acervo:
        st.subheader("📂 Acervo de Materiais Produzidos")
        if not df_aulas.empty:
            df_g = df_aulas[df_aulas['SEMANA_REF'] != "AVALIAÇÃO"].copy()
            f_ano_g = st.selectbox("Filtrar por Série:", ["Todos", "6º", "7º", "8º", "9º"], key="gav_ano_v26")
            if f_ano_g != "Todos": df_g = df_g[df_g['ANO'] == f_ano_g]
            
            for _, row in df_g.iloc[::-1].iterrows():
                with st.container(border=True):
                    c_t1, c_t2, c_t3, c_t4, c_t5, c_t6 = st.columns([1.5, 1, 1, 1, 1, 1])
                    c_t1.markdown(f"**{row['TIPO_MATERIAL']}**\n({row['SEMANA_REF']})")
                    
                    txt_full = str(row['CONTEUDO'])
                    l_reg = re.search(r"Regular\((.*?)\)|Aluno\((.*?)\)|LINK: (https://.*)", txt_full)
                    link_reg = l_reg.group(1) or l_reg.group(2) or l_reg.group(3) if l_reg else None
                    l_prof = re.search(r"Prof\((.*?)\)", txt_full).group(1) if "Prof(" in txt_full else None
                    l_pei = re.search(r"PEI\((.*?)\)", txt_full).group(1) if "PEI(" in txt_full and "PEI(N/A)" not in txt_full else None
                    
                    if link_reg: c_t2.link_button("📝 ALUNO", link_reg, use_container_width=True)
                    if l_prof: c_t3.link_button("👨‍🏫 PROF", l_prof, use_container_width=True)
                    if l_pei: c_t4.link_button("♿ PEI", l_pei, use_container_width=True)
                    else: c_t4.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                    
                    if c_t5.button("🔄 REFINAR", key=f"ref_{row.name}", use_container_width=True):
                        st.session_state.refino_lab_ativo = {"ano": row['ANO'], "semana": row['SEMANA_REF'], "aula": row['TIPO_MATERIAL']}
                        st.session_state.lab_temp = row['CONTEUDO']
                        if "LISTA COMPLEMENTAR" in str(row['TIPO_MATERIAL']).upper():
                            st.session_state.refino_lab_tipo = "COMPLEMENTAR"
                        else:
                            st.session_state.refino_lab_tipo = "AULA"
                        st.rerun()

                    if c_t6.button("🗑️ APAGAR", key=f"del_lab_{row.name}", use_container_width=True):
                        if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", row['TIPO_MATERIAL']): st.rerun()
                    
                    with st.expander("📄 Ver Detalhes"):
                        st.text(txt_full)
        else: st.info("📭 Acervo vazio.")
                            
# ==============================================================================
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - ARQUITETURA V26.5 (SINCRO TOTAL)
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

    tab_gerar, tab_hist, tab_matriz, tab_auditoria = st.tabs([
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
        
        with st.container(border=True):
            st.markdown("### ⚙️ 1. Parâmetros de Regência")
            c1, c2, c3 = st.columns([1, 2, 1.5])
            
            lista_anos = [6, 7, 8, 9]
            idx_ano = lista_anos.index(int(st.session_state.refino_ativo['ano'].replace('º',''))) if is_refinando else 0
            ano_p = c1.selectbox("Série/Ano:", lista_anos, index=idx_ano, disabled=is_refinando, key="ano_sel_v26")
            
            todas_semanas = util.gerar_semanas()
            idx_sem = 0
            if is_refinando:
                try: idx_sem = [s.split(" (")[0] for s in todas_semanas].index(st.session_state.refino_ativo['semana'])
                except: idx_sem = 0

            sem_p = c2.selectbox("Semana de Referência:", todas_semanas, index=idx_sem, disabled=is_refinando, key="sem_sel_v26")
            sem_limpa = sem_p.split(" (")[0]
            modo_p = c3.radio("Método de Elaboração:", ["📖 Livro Didático", "🎛️ Manual (Banco)"], horizontal=True, disabled=is_refinando)

            if not is_refinando:
                plano_existente = df_planos[(df_planos['ANO'] == f"{ano_p}º") & (df_planos['SEMANA'] == sem_limpa)]
                if not plano_existente.empty:
                    st.warning(f"⚠️ **STATUS: PLANO DETECTADO.** Já existe planejamento para o {ano_p}º Ano na {sem_limpa}.")
                else:
                    st.success(f"✅ **STATUS: DISPONÍVEL.** {ano_p}º Ano livre para planejamento na {sem_limpa}.")

        df_f = df_curriculo[df_curriculo['ANO'] == ano_p]
        cont_pre, obj_pre, eixo_pre = [], [], ""
        sel_mat, pags = [], "" 

        with st.container(border=True):
            if modo_p == "🎛️ Manual (Banco)":
                st.markdown("#### 🎯 Matriz Curricular (Fiel ao Banco)")
                cx1, cx2 = st.columns(2)
                
                # 1. Seleção de Eixo (Uso estrito de strings para evitar erro Pylance)
                # Garantimos que 'EIXO' seja lido como texto
                col_eixo = 'EIXO'
                lista_eixos = df_f[col_eixo].unique() if not df_f.empty else []
                eixo_pre = cx1.selectbox("Eixo Temático:", lista_eixos, key=f"eixo_v26_{v}")
                
                # 2. Seleção de Conteúdos (Filtro por string literal)
                col_cont = 'CONTEUDO_ESPECIFICO'
                df_filtrado_cont = df_f[df_f[col_eixo] == eixo_pre] if not df_f.empty else pd.DataFrame()
                opcoes_cont = df_filtrado_cont[col_cont].unique() if not df_filtrado_cont.empty else []
                cont_pre = st.multiselect("Conteúdos Específicos:", options=opcoes_cont, key=f"cont_v26_{v}")
                
                # 3. Seleção de Objetivos
                col_obj = 'OBJETIVOS'
                df_filtrado_obj = df_f[df_f[col_cont].isin(cont_pre)] if not df_f.empty else pd.DataFrame()
                opcoes_obj = df_filtrado_obj[col_obj].unique() if not df_filtrado_obj.empty else []
                obj_pre = st.multiselect("Objetivos de Ensino:", options=opcoes_obj, key=f"obj_v26_{v}")
                
                ctx_ia = f"MÉTODO MANUAL. EIXO: {eixo_pre}. CONTEÚDOS: {cont_pre}. OBJETIVOS: {obj_pre}."
            
            else:
                st.markdown("#### 📖 Referência Bibliográfica")
                cx1, cx2 = st.columns([2, 1])
                
                # Lista de materiais da base de conhecimento
                lista_materiais = df_materiais['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
                sel_mat = cx1.multiselect("Livro Didático:", lista_materiais, key=f"livro_v26_{v}")
                pags = cx2.text_input("Páginas:", placeholder="Ex: 10-15", key=f"pags_v26_{v}")
                ctx_ia = f"MÉTODO LIVRO: {sel_mat} PÁGINAS: {pags}."

            # Campo de Estratégia (Comum a ambos os métodos)
            strat = st.text_area("Estratégia Pedagógica / Observações:", placeholder="Ex: Focar na Catarse e Instrumentalização...", key=f"strat_v26_{v}")

        cb1, cb2 = st.columns([2, 1])
        pronto = (cont_pre and obj_pre) if modo_p == "🎛️ Manual (Banco)" else (sel_mat and pags)
        
        with cb1:
            label_btn = "🚀 RECOMPOR PLANEJAMENTO (REFINO)" if is_refinando else "🚀 COMPILAR PLANEJAMENTO DE ELITE"
            if st.button(label_btn, use_container_width=True, type="primary", disabled=not pronto and not is_refinando):
                with st.spinner("Maestro SOSA processando PHC..."):
                    prompt = f"ANO: {ano_p}º, SEMANA: {sem_p}. {ctx_ia}. ESTRATÉGIA: {strat}."
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

            t_ed, t_vis = st.tabs(["✏️ Editor de Texto", "👁️ Estrutura PIP"])
            with t_ed:
                col_ed1, col_ed2 = st.columns(2)
                ed_geral = col_ed1.text_input("Eixo:", limpar_v26(ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL"), "CONTEÚDO GERAL"), key=f"ed_g_{v}")
                ed_espec = col_ed2.text_area("Conteúdos:", limpar_v26(ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS"), "CONTEÚDOS ESPECÍFICOS"), key=f"ed_e_{v}")
                ed_objs = st.text_area("Objetivos:", limpar_v26(ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO"), "OBJETIVOS DE ENSINO"), key=f"ed_o_{v}")
                ed_met = st.text_area("Metodologia (PHC):", limpar_v26(ai.extrair_tag(txt_bruto, "METODOLOGIA"), "METODOLOGIA"), height=300, key=f"ed_m_{v}")
                ed_ava = st.text_area("Avaliação:", limpar_v26(ai.extrair_tag(txt_bruto, "AVALIACAO"), "AVALIAÇÃO"), key=f"ed_a_{v}")
                ed_pei = st.text_area("Adaptação PEI:", limpar_v26(ai.extrair_tag(txt_bruto, "ADAPTACAO_PEI"), "ADAPTAÇÃO PEI"), key=f"ed_p_{v}")

            with t_vis:
                st.markdown(f"**EIXO:** {ed_geral}")
                st.markdown(f"**CONTEÚDOS:** {ed_espec}")
                st.markdown(f"**OBJETIVOS:** {ed_objs}")
                st.markdown("---")
                st.markdown(f"**METODOLOGIA:**\n{ed_met}")

            # --- BOTÃO DE SALVAMENTO BLINDADO (CORREÇÃO DE VARIÁVEIS) ---
            if st.button("💾 FINALIZAR E SINCRONIZAR (DRIVE + BANCO)", use_container_width=True, type="primary"):
                with st.status("Iniciando Protocolo de Sincronia...", expanded=True) as status:
                    
                    # 1. DEFINIÇÃO DE METADADOS (RESOLVE O ERRO DE NOME_ARQUIVO)
                    final_ano = st.session_state.refino_ativo['ano'] if is_refinando else f"{ano_p}º"
                    final_semana = st.session_state.refino_ativo['semana'] if is_refinando else sem_limpa
                    nome_arquivo = f"PLANO_{final_ano.replace('º','')}ANO_{final_semana.replace(' ', '')}"
                    
                    # 2. LÓGICA UPSERT (LIMPEZA POR COORDENADAS)
                    status.write(f"🧹 Removendo versões obsoletas de {final_semana} ({final_ano})...")
                    db.excluir_plano_completo(final_semana, final_ano) 
                    
                    # 3. GERAÇÃO DO DOCX ELITE
                    status.write("📄 Gerando Documento Word de Elite...")
                    dados_docx = {"geral": ed_geral, "especificos": ed_espec, "objetivos": ed_objs, "metodologia": ed_met, "avaliacao": ed_ava, "pei": ed_pei}
                    doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": final_ano, "semana": final_semana, "trimestre": "I Trimestre"})
                    
                    # 4. UPLOAD PARA O DRIVE
                    status.write("📤 Enviando para o Google Drive...")
                    link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre="I Trimestre", categoria=final_ano, semana=final_semana, modo="PLANEJAMENTO")
                    
                    if "https" in str(link_drive):
                        # 5. SALVAMENTO NO BANCO
                        status.write("💾 Registrando no Banco de Dados...")
                        final_txt = f"MARKER_CONTEUDO_GERAL {ed_geral} \nMARKER_CONTEUDOS_ESPECIFICOS {ed_espec} \nMARKER_OBJETIVOS_ENSINO {ed_objs} \nMARKER_METODOLOGIA {ed_met} \nMARKER_AVALIACAO {ed_ava} \nMARKER_ADAPTACAO_PEI {ed_pei} \nMARKER_MODALIDADE {modo_p.upper()} \n--- LINK DRIVE --- {link_drive}"
                        
                        sucesso = db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), final_semana, final_ano, "I Trimestre", "PADRÃO", final_txt, link_drive])
                        
                        if sucesso:
                            status.update(label="✅ Sincronia Concluída!", state="complete")
                            st.balloons()
                            reset_planejamento()
                    else:
                        status.update(label="❌ Erro no Upload.", state="error")
                        st.error(link_drive)

    # --- ABA 2: GESTÃO DE ACERVO (EDIÇÃO VIVA) ---
    with tab_hist:
        st.subheader("📂 Gestão de Acervo Pedagógico")
        if not df_planos.empty:
            f_ano_h = st.selectbox("Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key="hist_ano_v26")
            df_h = df_planos.copy()
            if f_ano_h != "Todos": df_h = df_h[df_h['ANO'] == f_ano_h]
            
            if not df_h.empty:
                sel_h = st.selectbox("Selecionar Plano:", df_h['SEMANA'].tolist(), key="hist_sem_v26")
                dados_h = df_h[df_h['SEMANA'] == sel_h].iloc[0]
                raw_h = dados_h['PLANO_TEXTO']
                
                link_h = "Não encontrado"
                if "--- LINK DRIVE ---" in str(raw_h):
                    link_h = str(raw_h).split("--- LINK DRIVE ---")[-1].strip()

                st.markdown(f"### 📝 Plano: {sel_h} ({dados_h['ANO']})")
                
                c_h1, c_h2 = st.columns(2)
                with c_h1:
                    if st.button("🔄 REABRIR PARA REFINO IA", use_container_width=True):
                        st.session_state.refino_ativo = {"ano": dados_h['ANO'], "semana": sel_h}
                        st.session_state.p_temp = raw_h
                        st.info("Modo Refino Ativado. Vá para a aba 'Engenharia de Planejamento'.")
                with c_h2:
                    if "https" in link_h:
                        st.link_button("🚀 ABRIR NO GOOGLE DRIVE", link_h, use_container_width=True)

                with st.expander("👁️ Pré-visualização Rápida"):
                    st.text(raw_h)

                st.markdown("---")
                if st.button("🗑️ EXCLUIR PLANO DEFINITIVAMENTE", use_container_width=True):
                    if db.excluir_plano_completo(sel_h, dados_h['ANO']):
                        st.success(f"Plano removido com sucesso!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Erro ao tentar excluir o plano.")
            else: st.info("Nenhum plano encontrado.")
        else: st.info("📭 Acervo vazio.")

    # --- ABA 3 E 4 (MANTIDAS) ---
    with tab_matriz:
        st.subheader("📖 Matriz Curricular Ativa")
        if not df_curriculo.empty:
            ano_c = st.selectbox("Série:", [6, 7, 8, 9], key="matriz_ano_v26")
            df_c = df_curriculo[df_curriculo['ANO'] == ano_c].copy()
            concluidos = " ".join(df_planos[df_planos['ANO'] == f"{ano_c}º"]['PLANO_TEXTO'].astype(str).tolist()).upper() if not df_planos.empty else ""
            df_c['STATUS'] = df_c['CONTEUDO_ESPECIFICO'].apply(lambda x: "✅ CONCLUÍDO" if str(x).upper() in concluidos else "⏳ PENDENTE")
            st.dataframe(df_c[['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO', 'STATUS']], use_container_width=True, hide_index=True)

    with tab_auditoria:
        st.subheader("📈 Auditoria de Cobertura Curricular")
        if not df_curriculo.empty:
            ano_m = st.selectbox("Analisar Série:", [6, 7, 8, 9], key="auditoria_ano_v26")
            df_m = df_curriculo[df_curriculo['ANO'] == ano_m].copy()
            
            if not df_m.empty:
                planejados = " ".join(df_planos[df_planos['ANO'] == f"{ano_m}º"]['PLANO_TEXTO'].astype(str).tolist()).upper() if not df_planos.empty else ""
                
                # Forçamos o STATUS_NUM a ser inteiro (0 ou 1)
                df_m['STATUS_NUM'] = df_m['CONTEUDO_ESPECIFICO'].apply(lambda x: 1 if str(x).upper() in planejados else 0)
                
                # Realizamos o agrupamento
                progresso = df_m.groupby('EIXO')['STATUS_NUM'].agg(['sum', 'count']).reset_index()
                
                # --- CORREÇÃO CIRÚRGICA SOSA V26 ---
                # Forçamos a conversão para numérico (float) para garantir que o cálculo funcione
                progresso['sum'] = pd.to_numeric(progresso['sum'], errors='coerce').fillna(0)
                progresso['count'] = pd.to_numeric(progresso['count'], errors='coerce').fillna(1) # Evita divisão por zero
                
                # Cálculo da porcentagem com conversão explícita para float antes do round
                progresso['%'] = (progresso['sum'] / progresso['count'] * 100).astype(float).round(1)
                
                # Gráfico de Cobertura
                st.plotly_chart(px.bar(
                    progresso, x='EIXO', y='%', text='%', color='%', 
                    color_continuous_scale='RdYlGn', range_y=[0, 105],
                    title=f"Cobertura Curricular - {ano_m}º Ano"
                ), use_container_width=True)
            else:
                st.info("📭 Nenhum conteúdo encontrado na matriz para este ano.")

# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO RÁPIDO V26 - INTEGRAÇÃO PONTO ID & PEI
# ==============================================================================
if menu == "📝 Diário de Bordo Rápido":
    st.title("📝 Diário de Bordo: Engajamento e Ponto ID")
    st.markdown("---")

    if "v_diario" not in st.session_state: st.session_state.v_diario = 1
    v = st.session_state.v_diario
    # ---------------------------------------------------------

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro.")
    else:
        # --- 1. CONTEXTO DE EXECUÇÃO (MOBILE-FIRST) ---
        with st.container(border=True):
            c1, c2 = st.columns([1, 1])
            turma_sel = c1.selectbox("👥 Turma:", sorted(df_alunos['TURMA'].unique()), key="db_turma")
            data_sel = c2.date_input("📅 Data:", date.today(), key="db_data")
            data_str = data_sel.strftime("%d/%m/%Y")

            # Integração Ponto ID (Busca o Planejamento)
            planos_turma = df_planos[df_planos['ANO'] == f"{turma_sel[0]}º"] # Pega o ano pela sigla da turma
            
            if not planos_turma.empty:
                c3, c4 = st.columns([2, 1])
                semana_sel = c3.selectbox("🔗 Vincular à Semana:", planos_turma['SEMANA'].tolist(), key="db_sem")
                aula_alvo = c4.radio("🎯 Aula:", ["Aula 1", "Aula 2"], horizontal=True)
                
                # Recupera o conteúdo planejado para exibir como lembrete
                plano_ref = planos_turma[planos_turma['SEMANA'] == semana_sel].iloc[0]['PLANO_TEXTO']
                conteudo_previsto = ai.extrair_tag(plano_ref, "CONTEUDOS_ESPECIFICOS")
                st.caption(f"📖 **Conteúdo Previsto:** {conteudo_previsto}")
            else:
                st.error("❌ Nenhum planejamento encontrado para este ano. Vincule no Ponto ID primeiro.")
                semana_sel, aula_alvo = "N/A", "N/A"

        # --- 2. PREPARAÇÃO DA GRADE DE ENGAJAMENTO ---
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        # Busca registros existentes para evitar duplicidade (UPSERT)
        df_existente = pd.DataFrame()
        if not df_diario.empty:
            # Filtramos por data, turma e agora também pela aula (1 ou 2) para permitir dois registros no mesmo dia se necessário
            df_existente = df_diario[
                (df_diario['DATA'] == data_str) & 
                (df_diario['TURMA'] == turma_sel) &
                (df_diario['OBSERVACOES'].str.contains(aula_alvo))
            ]

        dados_editor = []
        for _, aluno in alunos_turma.iterrows():
            id_a = db.limpar_id(aluno['ID'])
            is_pei = str(aluno['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
            nome_display = f"♿ {aluno['NOME_ALUNO']}" if is_pei else aluno['NOME_ALUNO']
            
            # Valores padrão
            visto_val = True
            faltou_val = False
            tag_val = ""
            obs_val = ""

            # Se já existir registro, carrega os dados
            if not df_existente.empty:
                reg = df_existente[df_existente['ID_ALUNO'].apply(db.limpar_id) == id_a]
                if not reg.empty:
                    visto_val = str(reg.iloc[0]['VISTO_ATIVIDADE']).upper() == "TRUE"
                    tag_val = str(reg.iloc[0]['TAGS'])
                    obs_val = str(reg.iloc[0]['OBSERVACOES']).replace(f"[{aula_alvo}]", "").strip()
                    if "AUSÊNCIA" in tag_val: faltou_val = True

            dados_editor.append({
                "ID": id_a,
                "ALUNO": nome_display,
                "FALTOU": faltou_val,
                "VISTO": visto_val,
                "PEI": "✅" if is_pei else "---",
                "OCORRÊNCIA": tag_val if tag_val != "nan" else "",
                "OBS": obs_val if obs_val != "nan" else ""
            })

        # --- 3. GRADE INTERATIVA (OTIMIZADA PARA CELULAR) ---
        st.markdown(f"### 📝 Registro de Engajamento: {aula_alvo}")
        
        df_editado = st.data_editor(
            pd.DataFrame(dados_editor),
            column_config={
                "ID": None, # Esconde o ID para ganhar espaço no celular
                "ALUNO": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                "FALTOU": st.column_config.CheckboxColumn("Faltou?", help="Marca ausência justificada"),
                "VISTO": st.column_config.CheckboxColumn("Visto", help="Atividade concluída"),
                "PEI": st.column_config.TextColumn("PEI", width="small", disabled=True),
                "OCORRÊNCIA": st.column_config.SelectboxColumn(
                    "Tags", 
                    options=["", "Dormiu", "Conversa", "Se destacou", "Sem material", "Vetor Disciplinar", "PEI Concluído", "PEI Incompleto"],
                    width="small"
                ),
                "OBS": st.column_config.TextColumn("Obs", width="medium")
            },
            hide_index=True,
            use_container_width=True,
            key=f"editor_diario_{v}"
        )

        # --- 4. LÓGICA DE SALVAMENTO INTELIGENTE ---
        if st.button("💾 SALVAR DIÁRIO DE ENGAJAMENTO", type="primary", use_container_width=True):
            with st.status("Sincronizando registros...", expanded=True) as status:
                # Limpeza de duplicatas para a mesma aula/dia/turma
                db.limpar_diario_data_turma(data_str, turma_sel) # Nota: Ajustar db.py para considerar aula_alvo se desejar rigor total
                
                linhas_para_salvar = []
                for _, row in df_editado.iterrows():
                    # Lógica de Ausência: Se faltou, o visto é anulado e a tag é forçada
                    tag_final = row['OCORRÊNCIA']
                    visto_final = row['VISTO']
                    if row['FALTOU']:
                        tag_final = "AUSÊNCIA JUSTIFICADA"
                        visto_final = False
                    
                    # Adiciona o marcador de Aula no início da observação para o Ponto ID
                    obs_final = f"[{aula_alvo}] {row['OBS']}".strip()
                    
                    linhas_para_salvar.append([
                        data_str,
                        row['ID'],
                        row['ALUNO'].replace("♿ ", ""),
                        turma_sel,
                        str(visto_final),
                        tag_final,
                        obs_final
                    ])
                
                if db.salvar_lote("DB_DIARIO_BORDO", linhas_para_salvar):
                    status.update(label="✅ Diário Sincronizado com Sucesso!", state="complete")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

# ==============================================================================
# MÓDULO: PAINEL DE NOTAS & VISTOS V26.4 - FILTRO SELETIVO E ALTO CONTRASTE
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.title("📊 Painel de Notas: Sincronia e Pesos Dinâmicos")
    st.markdown("---")

    if "v_notas" not in st.session_state: st.session_state.v_notas = 1
    v = st.session_state.v_notas

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro.")
    else:
        # --- 1. CONFIGURADOR DE PESOS ---
        with st.container(border=True):
            st.markdown("### ⚙️ Configuração do Trimestre")
            c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1.5, 1, 0.8, 0.8, 0.8])
            turma_sel = c_f1.selectbox("👥 Turma:", sorted(df_alunos['TURMA'].unique()), key="n_turma")
            trimestre_sel = c_f2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="n_trim")
            p_visto = c_f3.number_input("Peso Vistos:", 0.0, 10.0, 3.0, step=0.5)
            p_teste = c_f4.number_input("Peso Teste:", 0.0, 10.0, 3.0, step=0.5)
            p_prova = c_f5.number_input("Peso Prova:", 0.0, 10.0, 4.0, step=0.5)

        # --- 2. SINCRONIZADOR COM SCANNER (FILTRO SELETIVO) ---
        with st.expander("📸 Sincronizar com Scanner de Gabaritos", expanded=True):
            c_s1, c_s2 = st.columns(2)
            
            provas_escaneadas = []
            if not df_diagnosticos.empty:
                provas_escaneadas = df_diagnosticos[df_diagnosticos['TURMA'] == turma_sel]['ID_AVALIACAO'].unique().tolist()
            
            # --- LÓGICA DE FILTRO SELETIVO SOSA ---
            # Só mostra "Teste" no campo de Teste e "Prova" no campo de Prova
            opcoes_teste = [p for p in provas_escaneadas if "TESTE" in p.upper()]
            opcoes_prova = [p for p in provas_escaneadas if "PROVA" in p.upper()]
            
            av_teste_id = c_s1.selectbox("Vincular Teste (3.0):", ["Nenhum"] + opcoes_teste)
            av_prova_id = c_s2.selectbox("Vincular Prova (4.0):", ["Nenhum"] + opcoes_prova)
            
            if st.button("🔄 CARREGAR NOTAS DO SCANNER", type="primary", use_container_width=True):
                st.toast("Notas filtradas e importadas!", icon="✅")
                st.rerun()

# --- 3. CÁLCULO AUTOMÁTICO DE VISTOS (FILTRADO POR TRIMESTRE) ---
        vistos_calculados = {}
        
        # Definição das datas oficiais de 2026 (Sincronizado com utils.py)
        calendario = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
            "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
        }
        dt_ini, dt_fim = calendario.get(trimestre_sel)

        if not df_diario.empty:
            # 1. Filtramos o diário pela turma
            df_d_t = df_diario[df_diario['TURMA'] == turma_sel].copy()
            
            # 2. Convertemos a coluna DATA para formato de data real para comparação
            df_d_t['DATA_DT'] = pd.to_datetime(df_d_t['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
            
            # 3. FILTRO TEMPORAL: Só pegamos registros dentro do trimestre selecionado
            df_d_trimestre = df_d_t[(df_d_t['DATA_DT'] >= dt_ini) & (df_d_t['DATA_DT'] <= dt_fim)]
            
            for id_aluno in df_alunos[df_alunos['TURMA'] == turma_sel]['ID']:
                id_limpo = db.limpar_id(id_aluno)
                d_aluno = df_d_trimestre[df_d_trimestre['ID_ALUNO'].apply(db.limpar_id) == id_limpo]
                
                if not d_aluno.empty:
                    # Aulas válidas (presença ou falta justificada não penaliza)
                    aulas_validas = d_aluno[~d_aluno['TAGS'].astype(str).str.upper().str.contains("AUSÊNCIA JUSTIFICADA", na=False)]
                    total_aulas = len(aulas_validas)
                    
                    # Conta apenas vistos "TRUE" dentro deste trimestre
                    vistos_recebidos = len(aulas_validas[aulas_validas['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    
                    nota_visto = (vistos_recebidos / total_aulas * p_visto) if total_aulas > 0 else 0.0
                    vistos_calculados[id_limpo] = round(nota_visto, 2)
                else:
                    # Se não há nenhuma aula registrada para o aluno NESTE trimestre, a nota de visto começa em 0.0
                    vistos_calculados[id_limpo] = 0.0
        else:
            # Se o diário está vazio, todos começam com 0.0
            vistos_calculados = {db.limpar_id(id_a): 0.0 for id_a in df_alunos[df_alunos['TURMA'] == turma_sel]['ID']}

        # --- 4. MONTAGEM DA GRADE (PRESERVAÇÃO DE DADOS) ---
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        notas_no_banco = df_notas[(df_notas['TURMA'] == turma_sel) & (df_notas['TRIMESTRE'] == trimestre_sel)]
        
        dados_grade = []
        for _, aluno in alunos_turma.iterrows():
            id_a = db.limpar_id(aluno['ID'])
            reg_banco = notas_no_banco[notas_no_banco['ID_ALUNO'].apply(db.limpar_id) == id_a]
            
            # Valores que já estão na planilha
            n_visto_base = util.sosa_to_float(reg_banco.iloc[0].get('NOTA_VISTOS', 0)) if not reg_banco.empty else vistos_calculados.get(id_a, p_visto)
            n_teste_base = util.sosa_to_float(reg_banco.iloc[0].get('NOTA_TESTE', 0)) if not reg_banco.empty else 0.0
            n_prova_base = util.sosa_to_float(reg_banco.iloc[0].get('NOTA_PROVA', 0)) if not reg_banco.empty else 0.0
            n_bonus_base = util.sosa_to_float(reg_banco.iloc[0].get('NOTA_REC', 0)) if not reg_banco.empty else 0.0

            # SOBREPOSIÇÃO: Só altera se o seletor NÃO for "Nenhum"
            if av_teste_id != "Nenhum":
                reg_s = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diagnosticos['ID_AVALIACAO'] == av_teste_id)]
                if not reg_s.empty: n_teste_base = util.sosa_to_float(reg_s.iloc[0]['NOTA_CALCULADA'])

            if av_prova_id != "Nenhum":
                reg_p = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diagnosticos['ID_AVALIACAO'] == av_prova_id)]
                if not reg_p.empty: n_prova_base = util.sosa_to_float(reg_p.iloc[0]['NOTA_CALCULADA'])

            dados_grade.append({
                "ID": id_a, "NOME": aluno['NOME_ALUNO'],
                "VISTOS": n_visto_base, "TESTE": n_teste_base, 
                "PROVA": n_prova_base, "BÔNUS": n_bonus_base, "RECUPERAÇÃO": 0.0
            })

        st.markdown("### 📝 Consolidação de Notas")
        df_edit = st.data_editor(
            pd.DataFrame(dados_grade),
            column_config={
                "ID": None, "NOME": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                "VISTOS": st.column_config.NumberColumn(f"Vistos ({p_visto})", format="%.2f"),
                "TESTE": st.column_config.NumberColumn(f"Teste ({p_teste})", format="%.2f"),
                "PROVA": st.column_config.NumberColumn(f"Prova ({p_prova})", format="%.2f"),
                "BÔNUS": st.column_config.NumberColumn("Bônus", format="%.2f", help="Atividades Complementares"),
                "RECUPERAÇÃO": st.column_config.NumberColumn("Recuperação", format="%.2f")
            },
            hide_index=True, use_container_width=True, key=f"editor_notas_v26_{v}"
        )

        # --- 5. CÁLCULOS E EXIBIÇÃO (ALTO CONTRASTE CORRIGIDO) ---
        df_edit['SOMA'] = df_edit["VISTOS"] + df_edit["TESTE"] + df_edit["PROVA"] + df_edit["BÔNUS"]
        df_edit['MÉDIA FINAL'] = df_edit.apply(lambda r: min(10.0, max(r['SOMA'], r['RECUPERAÇÃO'])), axis=1)

        st.markdown("### 📊 Pré-visualização do Desempenho")
        df_view = df_edit[['NOME', 'SOMA', 'MÉDIA FINAL']].copy()
        
        # ESTILO DE ALTA VISIBILIDADE (TEXTO PRETO EM FUNDO VIBRANTE)
        def style_performance(v):
            if v < 6.0:
                return 'background-color: #FF0000; color: #000000; font-weight: 900; border: 1px solid black;'
            return 'background-color: #00FF00; color: #000000; font-weight: 700;'

        st.dataframe(
            df_view.style.applymap(style_performance, subset=['SOMA', 'MÉDIA FINAL'])
            .format("{:.2f}", subset=['SOMA', 'MÉDIA FINAL']),
            use_container_width=True, hide_index=True
        )

        if st.button("💾 SALVAR E SINCRONIZAR BOLETIM", type="primary", use_container_width=True):
            with st.status("Sincronizando...", expanded=False) as status:
                db.limpar_notas_turma_trimestre(turma_sel, trimestre_sel)
                linhas = []
                for _, r in df_edit.iterrows():
                    linhas.append([
                        r['ID'], r['NOME'], turma_sel, trimestre_sel,
                        util.sosa_to_str(r["VISTOS"]), util.sosa_to_str(r["TESTE"]),
                        util.sosa_to_str(r["PROVA"]), util.sosa_to_str(r["BÔNUS"]),
                        util.sosa_to_str(r['MÉDIA FINAL'])
                    ])
                db.salvar_lote("DB_NOTAS", linhas)
                status.update(label="✅ Notas Salvas!", state="complete")
                st.balloons()

# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO V26 - ANÁLISE DE TENDÊNCIA
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Boletim Estratégico e Tendência Acadêmica")
    st.markdown("---")

    if df_notas.empty:
        st.warning("⚠️ Sem notas lançadas.")
    else:
        turma_sel = st.selectbox("Selecione a Turma:", sorted(df_alunos['TURMA'].unique()))
        
        # Pivotagem para visão anual
        df_t = df_notas[df_notas['TURMA'] == turma_sel]
        pivot = df_t.pivot_table(index=["ID_ALUNO", "NOME_ALUNO"], columns="TRIMESTRE", values="MEDIA_FINAL", aggfunc='first').reset_index()
        
        # Garantir colunas
        for c in ["I Trimestre", "II Trimestre", "III Trimestre"]:
            if c not in pivot.columns: pivot[c] = 0.0

        # --- LÓGICA DE TENDÊNCIA E ALERTAS ---
        def analisar_aluno(row):
            t1, t2, t3 = row.get("I Trimestre", 0), row.get("II Trimestre", 0), row.get("III Trimestre", 0)
            
            # Seta de Evolução
            seta = "➖"
            if t2 > t1 and t2 > 0: seta = "⬆️"
            elif t2 < t1 and t2 > 0: seta = "⬇️"
            
            # Alerta PEI
            aluno_info = df_alunos[df_alunos['ID'].apply(db.limpar_id) == db.limpar_id(row['ID_ALUNO'])].iloc[0]
            is_pei = str(aluno_info['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
            tag_pei = "♿" if is_pei else ""
            
            soma = t1 + t2 + t3
            status = "✅ APROVADO" if soma >= 18 else "⚠️ RECUPERAÇÃO" if soma > 0 else "⏳ EM CURSO"
            
            return pd.Series([tag_pei, seta, soma, status])

        pivot[['PEI', 'EVOLUÇÃO', 'SOMA', 'STATUS']] = pivot.apply(analisar_aluno, axis=1)

        st.dataframe(
            pivot[['PEI', 'NOME_ALUNO', 'I Trimestre', 'EVOLUÇÃO', 'II Trimestre', 'III Trimestre', 'SOMA', 'STATUS']],
            column_config={
                "SOMA": st.column_config.NumberColumn("Total (Meta 18)", format="%.1f"),
                "STATUS": st.column_config.TextColumn("Situação Final")
            },
            use_container_width=True, hide_index=True
        )

        # --- CONSELHO DE CLASSE IA (INTEGRADO) ---
        if st.button("🧠 GERAR PAUTA DE CONSELHO 360°", type="primary", use_container_width=True):
            with st.spinner("Analisando tendências de aprendizado..."):
                contexto = pivot[['NOME_ALUNO', 'SOMA', 'STATUS', 'EVOLUÇÃO']].to_string()
                prompt = f"Analise o desempenho da turma {turma_sel}. Dados:\n{contexto}\nIdentifique quem está em queda (⬇️) e sugira intervenções PHC."
                st.info(ai.gerar_ia("PLANE_PEDAGOGICO", prompt))

# ==============================================================================
# MÓDULO: GESTÃO DA TURMA - CENTRO DE COMANDO ESTRATÉGICO V26
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Centro de Comando: Gestão 360° da Turma")
    st.markdown("---")

    # --- 1. SELETOR DE TURMA (O GATILHO DO SISTEMA) ---
    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Povoar a turma primeiro.")
    else:
        turmas_disponiveis = sorted(df_alunos['TURMA'].unique())
        c_top1, c_top2 = st.columns([1, 2])
        turma_sel = c_top1.selectbox("🎯 Selecione a Turma para Comando:", turmas_disponiveis, key="cmd_turma")
        
        # Filtragem de dados da turma em todas as frentes
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        notas_turma = df_notas[df_notas['TURMA'] == turma_sel] if not df_notas.empty else pd.DataFrame()
        diario_turma = df_diario[df_diario['TURMA'] == turma_sel] if not df_diario.empty else pd.DataFrame()
        diagnosticos_turma = df_diagnosticos[df_diagnosticos['TURMA'] == turma_sel] if not df_diagnosticos.empty else pd.DataFrame()

        tab_heatmap, tab_individual, tab_conselho, tab_cadastro = st.tabs([
            "📊 Mapa de Calor (Heatmap)", 
            "👤 Prontuário 360° (Individual)", 
            "🗣️ Simulador de Conselho", 
            "🏗️ Gestão de Cadastro"
        ])

        # --- ABA 1: MAPA DE CALOR (VISÃO ESTRATÉGICA) ---
        with tab_heatmap:
            st.subheader(f"📈 Mapa de Desempenho e Engajamento - {turma_sel}")
            
# --- CÁLCULO DE MÉTRICAS PARA O HEATMAP (VERSÃO BLINDADA) ---
            heatmap_data = []
            for _, aluno in alunos_turma.iterrows():
                id_a = db.limpar_id(aluno['ID'])
                
                # 1. Desempenho (Notas) - Proteção contra ausência de notas
                n_aluno = notas_turma[notas_turma['ID_ALUNO'].apply(db.limpar_id) == id_a] if not notas_turma.empty else pd.DataFrame()
                media = n_aluno['MEDIA_FINAL'].mean() if not n_aluno.empty and 'MEDIA_FINAL' in n_aluno.columns else 0.0
                
                # 2. Engajamento (Vistos) - Proteção contra Diário vazio
                v_aluno = diario_turma[diario_turma['ID_ALUNO'].apply(db.limpar_id) == id_a] if not diario_turma.empty else pd.DataFrame()
                
                vistos = 0
                if not v_aluno.empty and 'VISTO_ATIVIDADE' in v_aluno.columns:
                    # Correção: Adicionado .str antes do .upper() para funcionar em colunas Pandas
                    vistos = len(v_aluno[v_aluno['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                
                # 3. Comportamento (Ocorrências)
                tags_negativas = ["Dormiu", "Conversa", "Agitado", "Sem material", "Vetor Disciplinar"]
                ocorrencias = 0
                if not v_aluno.empty and 'TAGS' in v_aluno.columns:
                    ocorrencias = len(v_aluno[v_aluno['TAGS'].isin(tags_negativas)])
                
                heatmap_data.append({
                    "Nome": aluno['NOME_ALUNO'],
                    "Média": round(media, 1),
                    "Vistos": vistos,
                    "Ocorrências": ocorrencias,
                    "Perfil": "♿ PEI" if str(aluno['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""] else "📝 REGULAR"
                })
            
            df_heat = pd.DataFrame(heatmap_data)
            
            # Visualização Gráfica
            fig_heat = px.scatter(
                df_heat, x="Vistos", y="Média", 
                size="Média", color="Ocorrências",
                hover_name="Nome", text="Nome",
                color_continuous_scale="RdYlGn_r", # Vermelho para muitas ocorrências
                title="Relação: Esforço (Vistos) vs Resultado (Média)",
                labels={"Vistos": "Quantidade de Vistos", "Média": "Média Acadêmica"}
            )
            fig_heat.update_traces(textposition='top center')
            st.plotly_chart(fig_heat, use_container_width=True)

            st.markdown("#### 📋 Lista de Prioridade Pedagógica")
            st.dataframe(df_heat.sort_values(by="Média"), use_container_width=True, hide_index=True)

        # --- ABA 2: PRONTUÁRIO 360° (INDIVIDUAL) ---
        with tab_individual:
            aluno_360 = st.selectbox("🔍 Selecione o Aluno para Raio-X:", alunos_turma['NOME_ALUNO'].tolist())
            id_360 = db.limpar_id(alunos_turma[alunos_turma['NOME_ALUNO'] == aluno_360].iloc[0]['ID'])
            info_a = alunos_turma[alunos_turma['NOME_ALUNO'] == aluno_360].iloc[0]

            c_360_1, c_360_2 = st.columns([1, 2])
            
            with c_360_1:
                st.markdown(f"### {aluno_360}")
                st.info(f"♿ **Necessidades:** {info_a['NECESSIDADES']}")
                st.metric("Média Atual", f"{df_heat[df_heat['Nome']==aluno_360]['Média'].values[0]:.1f}")
                st.metric("Total de Vistos", f"{df_heat[df_heat['Nome']==aluno_360]['Vistos'].values[0]}")

            with c_360_2:
                st.markdown("#### 📜 Histórico Recente")
                t_hist1, t_hist2, t_hist3 = st.tabs(["📝 Diário", "📸 Scanner", "📊 Notas"])
                
                with t_hist1:
                    st.dataframe(diario_turma[diario_turma['ID_ALUNO'].apply(db.limpar_id) == id_360][['DATA', 'TAGS', 'OBSERVACOES']], use_container_width=True)
                
                with t_hist2:
                    if not diagnosticos_turma.empty:
                        st.dataframe(diagnosticos_turma[diagnosticos_turma['ID_ALUNO'].apply(db.limpar_id) == id_360][['DATA', 'ID_AVALIACAO', 'NOTA_CALCULADA']], use_container_width=True)
                    else: st.info("Sem diagnósticos de scanner.")
                
                with t_hist3:
                    st.dataframe(notas_turma[notas_turma['ID_ALUNO'].apply(db.limpar_id) == id_360][['TRIMESTRE', 'MEDIA_FINAL']], use_container_width=True)

        # --- ABA 3: SIMULADOR DE CONSELHO (IA) ---
        with tab_conselho:
            st.subheader("🗣️ Síntese para Conselho de Classe")
            st.info("A IA vai cruzar Notas, Scanner e Diário para gerar a pauta da reunião.")
            
            if st.button("🚀 GERAR PAUTA ESTRATÉGICA", type="primary", use_container_width=True):
                with st.spinner("Maestro Sosa processando dados da turma..."):
                    # Preparação do Contexto para a IA
                    resumo_notas = df_heat[['Nome', 'Média', 'Perfil']].to_string()
                    resumo_comportamento = diario_turma['TAGS'].value_counts().to_string()
                    
                    prompt_conselho = (
                        f"VOCÊ É O COORDENADOR PEDAGÓGICO DO SISTEMA SOSA.\n"
                        f"TURMA: {turma_sel}. DADOS ACADÊMICOS:\n{resumo_notas}\n\n"
                        f"DADOS COMPORTAMENTAIS (TAGS):\n{resumo_comportamento}\n\n"
                        f"MISSÃO: Gere uma síntese para o Conselho de Classe baseada na Pedagogia Histórico-Crítica (PHC).\n"
                        f"1. Identifique o 'Grupo de Risco' (Baixa nota + Baixo esforço).\n"
                        f"2. Identifique o 'Grupo de Apoio' (Alunos PEI e progresso).\n"
                        f"3. Sugira uma estratégia de Recomposição Curricular para a turma.\n"
                        f"4. Use tom profissional e técnico. SEM MARKDOWN (** ou #)."
                    )
                    
                    st.session_state.pauta_conselho = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_conselho)
            
            if "pauta_conselho" in st.session_state:
                st.text_area("📄 Pauta Gerada:", st.session_state.pauta_conselho, height=400)
                if st.button("💾 Arquivar Pauta em DB_RELATORIOS"):
                    db.salvar_ata_conselho(datetime.now().strftime("%d/%m/%Y"), turma_sel, "PAUTA_CONSELHO", st.session_state.pauta_conselho)
                    st.success("Pauta arquivada!")

        # --- ABA 4: GESTÃO DE CADASTRO (MANTIDA E MELHORADA) ---
        with tab_cadastro:
            st.subheader("🏗️ Manutenção de Alunos e Turmas")
            # (Aqui você mantém o seu código original de Povoar Alunos, CSV e Editar CID)
            # ... (Código original de cadastro aqui) ...
            st.info("Use esta aba para inclusão de novos alunos ou correção de CID.")

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
# MÓDULO: RELATÓRIOS PEI
# ==============================================================================
elif menu == "♿ Relatórios PEI / Perfil IA":
    st.header("♿ Analista Clínico-Pedagógico (PEI)")
    
    if df_alunos.empty:
        st.warning("Cadastre alunos primeiro.")
    else:
        filtro_nome = st.text_input("🔍 Buscar Aluno por Nome:", placeholder="Digite para filtrar...")
        
        c_t, c_a = st.columns(2)
        turma_pei = c_t.selectbox("Selecione a Turma:", sorted(df_alunos['TURMA'].unique()), key="pei_turma")
        
        df_a_pei = df_alunos[df_alunos['TURMA'] == turma_pei]
        if filtro_nome:
            df_a_pei = df_a_pei[df_a_pei['NOME_ALUNO'].str.contains(filtro_nome, case=False)]
        
        if not df_a_pei.empty:
            aluno_id_nome = c_a.selectbox("Selecione o Aluno:", df_a_pei['NOME_ALUNO'].tolist(), key="pei_aluno")
            dados_aluno = df_a_pei[df_a_pei['NOME_ALUNO'] == aluno_id_nome].iloc[0]
            id_aluno = db.limpar_id(dados_aluno['ID']) 
            cid_aluno = dados_aluno.get('NECESSIDADES', 'NENHUMA')
            
            st.info(f"👤 **Aluno:** {aluno_id_nome} | 🆔 **ID:** {id_aluno} | 🏥 **Necessidades/CID:** {cid_aluno}")
            
            tab_tec, tab_zap, tab_doc_oficial, tab_plano_trimestral, tab_hist_pei = st.tabs(["📈 Evolução Técnica", "📱 WhatsApp/Pais", "📄 Documento Oficial (Capa)", "📅 Plano Trimestral (Currículo Adaptado)", "🗂️ Histórico Salvo"])
            
            evidencias_txt = "Sem registros recentes no diário."
            if not df_diario.empty and 'ID_ALUNO' in df_diario.columns:
                d_aluno = df_diario[df_diario['NOME_ALUNO'] == aluno_id_nome]
                if not d_aluno.empty:
                    ultimos = d_aluno.tail(5)
                    evidencias_txt = "\n".join([f"- {row['DATA']}: {row.get('TAGS', '')} ({row.get('OBSERVACOES', '')})" for _, row in ultimos.iterrows()])

            ultimo_relatorio = "Primeiro relatório do ano."
            historico_existente = False
            if not df_relatorios.empty:
                r_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == str(id_aluno)]
                if not r_aluno.empty:
                    ultimo_relatorio = r_aluno.iloc[-1]['CONTEUDO']
                    historico_existente = True

            with tab_tec:
                st.markdown("### 🧠 Gerador de Relatório Técnico (Ponto ID)")
                percepcao = st.text_area("Sua percepção atual (O que você viu essa semana?):", placeholder="Ex: Melhorou na cópia, mas agrediu o colega...")
                
                hoje_str = datetime.now().strftime("%d/%m/%Y")
                ja_salvou_hoje = False
                if not df_relatorios.empty:
                    check_hoje = df_relatorios[(df_relatorios['ID_ALUNO'].apply(db.limpar_id) == str(id_aluno)) & (df_relatorios['DATA'] == hoje_str)]
                    if not check_hoje.empty:
                        st.warning(f"⚠️ Já existe um relatório salvo hoje ({hoje_str}). Se salvar novamente, será criado um novo registro.")
                        ja_salvou_hoje = True

                if st.button("🧠 Gerar Análise Evolutiva"):
                    with st.spinner("O Especialista está analisando a evolução..."):
                        instrucao_extra = ""
                        if historico_existente:
                            instrucao_extra = "IMPORTANTE: Este é um relatório de ACOMPANHAMENTO. Compare com o 'Histórico Anterior'. O aluno evoluiu? Regrediu? Manteve-se estável? Cite as mudanças."
                        
                        prompt_pei = (
                            f"ALUNO: {aluno_id_nome}. CID/NECESSIDADES: {cid_aluno}.\n"
                            f"HISTÓRICO ANTERIOR: {ultimo_relatorio}\n"
                            f"EVIDÊNCIAS DO DIÁRIO (Últimos dias): {evidencias_txt}\n"
                            f"PERCEPÇÃO ATUAL DO PROFESSOR: {percepcao}\n\n"
                            f"AÇÃO: Escreva um RELATÓRIO DE EVOLUÇÃO para o sistema escolar.\n"
                            f"{instrucao_extra}\n"
                            f"REGRAS: Texto corrido, SEM MARKDOWN, SEM NEGRITO. Linguagem técnica mas acessível. "
                            f"Se tiver CID, correlacione. Se não, aponte barreiras. Cite evidências."
                        )
                        st.session_state.res_pei_tec = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_pei)
                
                if "res_pei_tec" in st.session_state:
                    st.info("🤖 **Refinamento:** O Especialista está ouvindo. Peça ajustes abaixo se necessário.")
                    ajuste_pei = st.chat_input("Ex: 'Seja mais breve', 'Cite que ele melhorou na leitura'...")
                    
                    if ajuste_pei:
                        with st.spinner("Reescrevendo..."):
                            prompt_refino = f"TEXTO ATUAL: {st.session_state.res_pei_tec}. AJUSTE SOLICITADO: {ajuste_pei}. Mantenha o tom técnico."
                            st.session_state.res_pei_tec = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_refino)
                            st.rerun()

                    txt_editavel = st.text_area("Texto Gerado (Editável):", st.session_state.res_pei_tec, height=300)
                    if st.button("💾 Salvar Evolução no Banco"):
                        db.salvar_no_banco("DB_RELATORIOS", [
                            hoje_str, 
                            id_aluno, 
                            aluno_id_nome, 
                            "EVOLUCAO_TECNICA", 
                            txt_editavel
                        ])
                        st.success("Relatório salvo com sucesso!"); del st.session_state.res_pei_tec; time.sleep(1); st.rerun()

            with tab_zap:
                st.markdown("### 📱 Comunicado para Família/Coordenação")
                solicitacao = st.text_input("Motivo do contato:", placeholder="Ex: Reunião de pais, Elogio, Alerta de comportamento")
                
                if st.button("🚀 Gerar Mensagem Curta"):
                    base_texto = st.session_state.get("res_pei_tec", ultimo_relatorio)
                    prompt_zap = (
                        f"Baseado neste relatório técnico: '{base_texto}'.\n"
                        f"Crie uma mensagem de WhatsApp para os pais. MOTIVO: {solicitacao}.\n"
                        f"Tom: Empático, parceiro, direto. Use emojis moderados. Resuma os pontos chaves."
                    )
                    st.session_state.res_pei_zap = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_zap)
                
                if "res_pei_zap" in st.session_state:
                    st.text_area("Copie para o WhatsApp:", st.session_state.res_pei_zap, height=200)

            with tab_doc_oficial:
                st.markdown("### 📄 Capa do PEI (Plano de Acessibilidade Curricular)")
                st.info("Preencha os dados complementares para gerar o documento oficial.")
                
                c1, c2 = st.columns(2)
                data_nasc = c1.date_input("Data de Nascimento:", value=date(2013, 1, 1))
                nome_mae = c2.text_input("Nome da Mãe/Responsável:")
                
                if st.button("📄 Gerar Plano de Acessibilidade (Capa)"):
                    with st.spinner("Consultando Diário de Bordo e gerando perfil técnico..."):
                        prompt_capa = (
                            f"ALUNO: {aluno_id_nome}. IDADE: {date.today().year - data_nasc.year} anos.\n"
                            f"DIAGNÓSTICO/CID: {cid_aluno}.\n"
                            f"EVIDÊNCIAS COMPORTAMENTAIS (DIÁRIO): {evidencias_txt}\n"
                            f"OBJETIVO: Redigir a 'Seção 1 - Plano de Acessibilidade Curricular' do PEI.\n"
                            f"Gere o texto técnico dividido EXATAMENTE nos 4 tópicos: Habilidades Sociais, Comunicativas, Emocionais e Funcionais."
                        )
                        st.session_state.res_capa_pei = ai.gerar_ia("ESPECIALISTA_PEI", prompt_capa)
                
                if "res_capa_pei" in st.session_state:
                    st.text_area("Texto do Documento Oficial:", st.session_state.res_capa_pei, height=400)
                    if st.button("💾 Salvar Capa do PEI"):
                        db.salvar_no_banco("DB_RELATORIOS", [
                            datetime.now().strftime("%d/%m/%Y"), 
                            id_aluno, 
                            aluno_id_nome, 
                            "PEI_CAPA_OFICIAL", 
                            st.session_state.res_capa_pei
                        ])
                        st.success("Documento salvo!"); del st.session_state.res_capa_pei; time.sleep(1); st.rerun()

            with tab_plano_trimestral:
                st.markdown("### 📅 Plano Trimestral (Currículo Adaptado)")
                
                trimestre_sel = st.selectbox("Selecione o Trimestre:", ["I", "II", "III"], key="pei_trimestre")
                
                perfil_aluno = "Perfil não encontrado. Usando apenas CID."
                if not df_relatorios.empty:
                    r_capa = df_relatorios[
                        (df_relatorios['ID_ALUNO'].apply(db.limpar_id) == str(id_aluno)) & 
                        (df_relatorios['TIPO'] == "PEI_CAPA_OFICIAL")
                    ]
                    if not r_capa.empty:
                        perfil_aluno = r_capa.iloc[-1]['CONTEUDO']
                        st.success("✅ Perfil do Aluno (Capa) carregado com sucesso.")
                    else:
                        st.warning("⚠️ Capa do PEI não encontrada. Gere-a na aba anterior para um resultado melhor.")

                curriculo_texto = "Currículo não encontrado."
                if not df_curriculo.empty:
                    ano_aluno = "".join(filter(str.isdigit, turma_pei))
                    if ano_aluno:
                        df_curr_trim = df_curriculo[
                            (df_curriculo['ANO'] == int(ano_aluno)) & 
                            (df_curriculo['TRIMESTRE'] == trimestre_sel)
                        ]
                        if not df_curr_trim.empty:
                            curriculo_texto = "\n".join(df_curr_trim['CONTEUDO_ESPECIFICO'].tolist())
                            st.info(f"📚 Currículo do {ano_aluno}º Ano ({trimestre_sel} Trimestre) carregado.")
                        else:
                            st.error("Currículo vazio para este ano/trimestre.")
                    else:
                        st.error("Não foi possível identificar o ano da turma.")

                if st.button("🚀 Gerar Plano Adaptado"):
                    with st.spinner("O Especialista está adaptando o currículo..."):
                        prompt_adaptacao = (
                            f"ALUNO: {aluno_id_nome}. CID: {cid_aluno}.\n"
                            f"PERFIL DE APRENDIZAGEM (CAPA): {perfil_aluno}\n"
                            f"CURRÍCULO REGULAR DO TRIMESTRE: {curriculo_texto}\n"
                            f"OBJETIVO: Criar a tabela de 'Currículo Adaptado' para o PEI.\n"
                            f"Gere o texto estruturado com: CONTEÚDO, OBJETIVO ADAPTADO, FUNÇÕES PSÍQUICAS e MATERIAIS."
                        )
                        st.session_state.res_plano_trim = ai.gerar_ia("ESPECIALISTA_ADAPTACAO", prompt_adaptacao)

                if "res_plano_trim" in st.session_state:
                    st.text_area("Plano Trimestral Adaptado:", st.session_state.res_plano_trim, height=500)
                    if st.button("💾 Salvar Plano Trimestral"):
                        db.salvar_no_banco("DB_RELATORIOS", [
                            datetime.now().strftime("%d/%m/%Y"), 
                            id_aluno, 
                            aluno_id_nome, 
                            f"PEI_PLANO_TRIMESTRAL_{trimestre_sel}", 
                            st.session_state.res_plano_trim
                        ])
                        st.success("Plano Trimestral salvo!"); del st.session_state.res_plano_trim; time.sleep(1); st.rerun()

            with tab_hist_pei:
                st.markdown("### 🗂️ Arquivo Morto (Mais recente primeiro)")
                if not df_relatorios.empty:
                    hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == str(id_aluno)]
                    if not hist_aluno.empty:
                        hist_aluno = hist_aluno.iloc[::-1]
                        for _, row in hist_aluno.iterrows():
                            tipo_exibicao = row.get('TIPO', row.get('TURMA', 'REGISTRO'))
                            with st.expander(f"{row['DATA']} - {tipo_exibicao}"):
                                st.write(row['CONTEUDO'])
                    else:
                        st.info("Nenhum histórico para este aluno.")
                else:
                    st.info("Banco de relatórios vazio.")

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
