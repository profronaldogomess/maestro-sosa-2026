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
import ai_engine as ai
from datetime import date, datetime, timedelta



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
    "👤 Biografia do Estudante",
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
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR V42.1 - INTEGRADO & BLINDADO)
# ==============================================================================
if menu == "🧪 Criador de Aulas":
    st.title("🧪 Laboratório de Produção Semiótica (V42.1)")
    st.markdown("---")
    
    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "sosa_id_atual", "lab_meta", "hub_origem"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.cache_data.clear() 
        st.session_state.v_lab = int(time.time())
        st.rerun()

    if "v_lab" not in st.session_state: 
        st.session_state.v_lab = int(time.time())
    v = st.session_state.v_lab

    # 1. INICIALIZAÇÃO DE SEGURANÇA
    meta = st.session_state.get("lab_meta", {})
    is_hub = meta.get("tipo") == "PRODUÇÃO_HUB"
    ed_prof, ed_alu, ed_res, ed_dua = "", "", "", ""
    s_id = st.session_state.get("sosa_id_atual", "SEM-ID")

# --- ÁREA DE EXIBIÇÃO E REFINO (VERSÃO V42.2 - FIX DUPLICIDADE & NOMENCLATURA) ---
    if "lab_temp" in st.session_state:
        txt_base = st.session_state.lab_temp
        
        # 1. EXTRAÇÃO DE SEGURANÇA E IDENTIFICAÇÃO
        s_id_extraido = ai.extrair_tag(txt_base, "SOSA_ID")
        # Se a IA gerou um ID feio, mantemos o que o sistema criou originalmente
        s_id = st.session_state.get("sosa_id_atual", "SEM-ID")
        
        is_recomp = "RECOMP" in s_id.upper()
        is_projeto = "PROJETO" in s_id.upper() or "[JUSTIFICATIVA_PHC]" in txt_base

        # 2. MOTOR DE DISTRIBUIÇÃO DE VARIÁVEIS (PREVENTIVO)
        ed_prof = ai.extrair_tag(txt_base, "PROFESSOR")
        ed_alu = ai.extrair_tag(txt_base, "ALUNO")
        ed_res = ai.extrair_tag(txt_base, "RESPOSTAS_PEDAGOGICAS") or ai.extrair_tag(txt_base, "GABARITO")
        ed_dua = ai.extrair_tag(txt_base, "PEI")
        ed_grade = ai.extrair_tag(txt_base, "GRADE_DE_CORRECAO")

        st.success(f"💎 Material em Edição: **{s_id}**")

        # --- 🤖 REFINADOR MAESTRO ---
        with st.container(border=True):
            st.subheader("🤖 Refinador Maestro (Perícia V31)")
            cmd_refine_lab = st.chat_input("Solicite ajustes...", key=f"chat_lab_ref_{v}")
            if cmd_refine_lab:
                with st.spinner("Reengenharia..."):
                    persona_refino = "REFINADOR_PROJETOS_V31" if is_projeto else "REFINADOR_MATERIAIS"
                    st.session_state.lab_temp = ai.gerar_ia(persona_refino, f"ORDEM: {cmd_refine_lab}\n\nATUAL:\n{txt_base}")
                    st.session_state.v_lab = int(time.time()); st.rerun()
            if st.button("🗑️ DESCARTAR EDIÇÃO"): reset_laboratorio()
        
        # --- 🗂️ TABS DINÂMICAS (BLOCO ÚNICO E PROTEGIDO) --
        if is_recomp:
            t_prof, t_alu, t_gab, t_pei, t_sync = st.tabs(["👨‍🏫 Tratado do Professor", "📝 Folha do Aluno", "✅ Respostas Pedagógicas", "♿ Material PEI", "☁️ SINCRONIA"])
            with t_prof: 
                st.info("🔬 Gênese Científica e Perícia de Mediação (BNCC/PHC)")
                st.text_area("Mapa de Regência:", ed_prof, height=450, key=f"p_recomp_area_{v}")
            with t_alu: 
                st.warning("📸 SOBERANIA VISUAL: Verifique os [ PROMPT IMAGEM ]")
                st.text_area("Questões Regulares:", ed_alu, height=450, key=f"a_recomp_area_{v}")
            with t_gab: 
                st.subheader("✅ Expectativa de Aprendizagem")
                st.text_area("Respostas Detalhadas:", ed_res, height=300, key=f"g_recomp_area_{v}")
                st.divider()
                st.subheader("🔍 Grade de Perícia (Descritores)")
                # Extrai a grade que agora virá em formato de lista
                val_grade = ai.extrair_tag(txt_base, "GRADE_DE_CORRECAO")
                st.text_area("Análise por Item:", val_grade, height=300, key=f"grade_recomp_area_{v}")
            with t_pei: 
                st.info("♿ Simetria 50%: Andaime Cognitivo por Questão.")
                st.text_area("Atividade Adaptada:", ed_dua, height=450, key=f"pei_recomp_area_{v}")

# ... (No Triple-Sync, o código permanece o mesmo da V42.1, pois ele já é robusto)
        
        elif is_projeto:
            t_prof, t_alu, t_dua, t_sync = st.tabs(["👨‍🏫 Mapa do Professor", "📝 Roteiro do Aluno", "♿ DUA/PEI", "☁️ SINCRONIA"])
            with t_prof:
                st.text_area("Justificativa e Rubrica:", ed_prof, height=450, key=f"p_proj_area_{v}")
            with t_alu:
                st.text_area("Roteiro Investigativo:", ed_alu, height=450, key=f"a_proj_area_{v}")
            with t_dua:
                st.text_area("Estratégia DUA:", ed_dua, height=450, key=f"dua_proj_area_{v}")
        
        else:
            t_prof, t_alu, t_gab, t_pei, t_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "✅ Gabarito", "♿ PEI", "☁️ SINCRONIA"])
            with t_prof: st.text_area("Lousa:", ed_prof, height=450, key=f"ed_prof_reg_{v}")
            with t_alu: st.text_area("Folha:", ed_alu, height=450, key=f"ed_alu_reg_{v}")
            with t_gab: st.text_area("Gabarito:", ed_res, height=200, key=f"ed_res_reg_{v}")
            with t_pei: st.text_area("PEI:", ed_dua, height=400, key=f"ed_pei_reg_{v}")

        # --- ☁️ ABA DE SINCRONIA (TRIPLE-SYNC V45) ---
        with t_sync:
            st.subheader("🚀 Protocolo de Custódia Digital V45")
            if st.button("💾 EXECUTAR TRIPLE-SYNC (SUBSTITUIR)", use_container_width=True, type="primary", key=f"btn_triple_{v}"):
                with st.status("Sincronizando Ativos de Elite...") as status:
                    db.excluir_registro_com_drive("DB_AULAS_PRONTAS", s_id)
                    ano_str = f"{meta.get('ano', '6')}º"
                    sem_ref = meta.get('semana_ref', 'RECOMPOSIÇÃO')
                    info_doc = {"ano": ano_str, "trimestre": meta.get('trimestre', 'I Trimestre'), "valor": "0,00", "valor_questao": "0,00", "qtd_questoes": 10}

                    doc_alu = exporter.gerar_docx_aluno_v24(s_id, ed_alu, info_doc)
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{s_id}_ALUNO", modo="AULA")
                    
                    doc_pei = exporter.gerar_docx_pei_v25(f"{s_id}_PEI", ed_dua, info_doc)
                    link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{s_id}_PEI", modo="AULA")
                    
                    txt_prof_final = f"{ed_prof}\n\n[RESPOSTAS_PEDAGOGICAS]\n{ed_res}\n\n[GRADE_DE_CORRECAO]\n{ed_grade}"
                    doc_prof = exporter.gerar_docx_professor_v25(s_id, txt_prof_final, {"ano": ano_str, "semana": sem_ref, "trimestre": info_doc['trimestre']})
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{s_id}_PROF", modo="AULA")
                    
                    links_f = f"--- LINKS ---\nRegular({link_alu}) PEI({link_pei}) Prof({link_prof})"
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), sem_ref, s_id, txt_base + f"\n\n{links_f}", ano_str, link_alu])
                    status.update(label="✅ Sincronizado!", state="complete")
                    st.balloons(); time.sleep(1); reset_laboratorio()

    # --- SEÇÃO DE ENTRADA (CONFIGURAÇÃO INICIAL) ---
    else:
        tab_producao, tab_diagnostico, tab_trabalhos, tab_complementar, tab_acervo_lab = st.tabs([
            "🚀 Produção (Aula 1/2)", "🔍 Sonda de Proficiência", "📋 Engenharia de Trabalhos", "📚 Atividades Complementares", "📂 Acervo de Materiais"
        ])

        with tab_producao:
            if is_hub:
                st.info("📬 **PLANO IMPORTADO DO DASHBOARD**")
                with st.container(border=True):
                    c1, c2 = st.columns([2, 1])
                    plano_txt = st.session_state.lab_temp
                    eixo_p = ai.extrair_tag(plano_txt, "CONTEUDO_GERAL")
                    sem_ref = st.session_state.lab_meta.get('semana_ref')
                    ano_ref_hub = st.session_state.lab_meta.get('ano')
                    
                    c1.markdown(f"### 🎯 {eixo_p}")
                    c1.caption(f"Semana: {sem_ref} | Série: {ano_ref_hub}º")
                    st.warning(f"📖 **Herança Detectada:** {sem_ref}")
                    
                    aulas_no_banco = df_aulas[(df_aulas['SEMANA_REF'] == sem_ref) & (df_aulas['ANO'].str.contains(str(ano_ref_hub)))]
                    opcoes_aula = []
                    if not any("Aula 1" in str(x) for x in aulas_no_banco['TIPO_MATERIAL']): opcoes_aula.append("Aula 1")
                    if not any("Aula 2" in str(x) for x in aulas_no_banco['TIPO_MATERIAL']): opcoes_aula.append("Aula 2")
                    if not any("Sábado" in str(x) for x in aulas_no_banco['TIPO_MATERIAL']): opcoes_aula.append("Sábado Letivo")
                    
                    if not opcoes_aula:
                        st.success(f"✅ **Safra Concluída!**")
                        if st.button("🔄 REPRODUZIR (SOBREPOR)"): reset_laboratorio()
                    else:
                        aula_alvo_hub = c2.radio("Selecione a Aula:", opcoes_aula, key=f"hub_aula_{v}")
                        instr_extra = st.text_area("📝 Informações Extras:", key=f"hub_extra_{v}")
                        qtd_q_hub = st.slider("Quantidade de Questões:", 3, 15, 10, key=f"hub_q_{v}")
                        if st.button("💎 MATERIALIZAR AULA DE ELITE", use_container_width=True, type="primary"):
                            with st.spinner(f"Expandindo {aula_alvo_hub}..."):
                                nome_elite = util.gerar_nome_material_elite(ano_ref_hub, aula_alvo_hub, sem_ref)
                                st.session_state.sosa_id_atual = nome_elite
                                st.session_state.lab_meta['aula_alvo'] = aula_alvo_hub
                                tag_aula = "AULA_1" if "Aula 1" in aula_alvo_hub else "AULA_2" if "Aula 2" in aula_alvo_hub else "SABADO_LETIVO"
                                prompt_expansao = f"PERSONA: MAESTRO_SOSA_V28_ELITE. ID: {nome_elite}.\nSÉRIE: {ano_ref_hub}º. ALVO: {aula_alvo_hub}. QTD: {qtd_q_hub}.\n--- HERANÇA TÉCNICA ---\nROTEIRO DO PLANO: {ai.extrair_tag(plano_txt, tag_aula)}.\nESTRATÉGIA PEI: {ai.extrair_tag(plano_txt, 'ADAPTACAO_PEI')}.\nEXTRAS: {instr_extra}.\n\nMISSÃO: Gere o material completo com as TAGS [PROFESSOR], [ALUNO], [GABARITO], [PEI], [GABARITO_PEI]."
                                st.session_state.lab_temp = ai.gerar_ia("MAESTRO_SOSA_V28_ELITE", prompt_expansao, usar_busca=True)
                                st.rerun()
            else:
                st.markdown("### ⚙️ Configurar Produção de Aula (Herança Didática)")
                with st.container(border=True):
                    c1, c2, c3 = st.columns([1, 2, 1])
                    ano_lab = c1.selectbox("Série/Ano:", [6, 7, 8, 9], key=f"prod_ano_{v}")
                    ano_ref_prod = f"{ano_lab}º"
                    
                    planos_ano = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_lab))]
                    
                    if planos_ano.empty: 
                        st.error("❌ Nenhum planejamento encontrado para esta série.")
                    else:
                        sem_lab = c2.selectbox("Semana Base (Ponto ID):", planos_ano["SEMANA"].tolist(), key=f"prod_sem_{v}")
                        plano_row = planos_ano[planos_ano["SEMANA"] == sem_lab].iloc[0]
                        plano_txt = str(plano_row['PLANO_TEXTO'])
                        
                        # --- MOTOR DE FILTRAGEM DE SAFRA (A MÁGICA ESTÁ AQUI) ---
                        # Busca o que já foi produzido para esta semana e ano
                        aulas_existentes = df_aulas[(df_aulas['SEMANA_REF'] == sem_lab) & (df_aulas['ANO'] == ano_ref_prod)]
                        lista_prontas = aulas_existentes['TIPO_MATERIAL'].astype(str).tolist()
                        
                        opcoes_pendentes = []
                        if not any("Aula 1" in t for t in lista_prontas): opcoes_pendentes.append("Aula 1")
                        if not any("Aula 2" in t for t in lista_prontas): opcoes_pendentes.append("Aula 2")
                        
                        if not opcoes_pendentes:
                            c3.success("✅ Safra Completa!")
                            st.info(f"As Aulas 1 e 2 da '{sem_lab}' já estão no seu Acervo.")
                        else:
                            aula_alvo_prod = c3.radio("🎯 Aula Pendente:", opcoes_pendentes, horizontal=True, key=f"prod_alvo_{v}")
                            
                            instr_extra_prod = st.text_area("📝 Contexto Adicional:", key=f"prod_extra_{v}")
                            qtd_q_prod = st.slider("Quantidade de Questões:", 3, 15, 10, key=f"prod_q_{v}")
                            
                            if st.button("💎 COMPILAR MATERIAL DE ELITE", use_container_width=True, type="primary"):
                                with st.spinner("Arquitetando Tratado Didático..."):
                                    nome_elite = util.gerar_nome_material_elite(ano_lab, aula_alvo_prod, sem_lab)
                                    st.session_state.sosa_id_atual = nome_elite
                                    st.session_state.lab_meta = {
                                        "ano": ano_lab, 
                                        "trimestre": plano_row.get('TURMA', 'I Trimestre'), 
                                        "tipo": aula_alvo_prod, 
                                        "semana_ref": sem_lab, 
                                        "aula_alvo": aula_alvo_prod
                                    }
                                    
                                    # Seleciona a tag correta do plano (AULA_1 ou AULA_2)
                                    tag_alvo = "AULA_1" if "1" in aula_alvo_prod else "AULA_2"
                                    roteiro_plano = ai.extrair_tag(plano_txt, tag_alvo)
                                    
                                    prompt_manual = (
                                        f"PERSONA: MAESTRO_SOSA_V28_ELITE. ID: {nome_elite}.\n"
                                        f"SÉRIE: {ano_ref_prod}. ALVO: {aula_alvo_prod}. QTD: {qtd_q_prod}.\n"
                                        f"--- HERANÇA DO PLANO ---\n{roteiro_plano}\n"
                                        f"--- EXTRAS ---\n{instr_extra_prod}"
                                    )
                                    st.session_state.lab_temp = ai.gerar_ia("MAESTRO_SOSA_V28_ELITE", prompt_manual, usar_busca=True)
                                    st.rerun()

        with tab_diagnostico:
            st.markdown("### 🔍 Configurar Sonda de Proficiência")
            with st.container(border=True):
                c1, c2 = st.columns([1, 1])
                ano_sonda = c1.selectbox("Série Atual:", [6, 7, 8, 9], key=f"s_ano_{v}")
                trim_sonda = c2.selectbox("Trimestre da Sonda:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"s_trim_{v}")
                
                # Lógica de retrocesso curricular
                if trim_sonda == "I Trimestre":
                    ano_busca = int(ano_sonda) - 1
                    trim_busca = "Todos"
                    st.warning(f"💡 **Diagnóstico Inicial:** Buscando conteúdos do {ano_busca}º Ano para nivelamento.")
                elif trim_sonda == "II Trimestre":
                    ano_busca = int(ano_sonda)
                    trim_busca = "I"
                    st.info(f"🎯 **Sonda de Ciclo:** Avaliando conteúdos do I Trimestre.")
                else:
                    ano_busca = int(ano_sonda)
                    trim_busca = "II"
                    st.info(f"🎯 **Sonda de Ciclo:** Avaliando conteúdos do II Trimestre.")
                
                # FILTRAGEM DA MATRIZ
                df_cur_sonda = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_busca))]
                if trim_busca != "Todos":
                    df_cur_sonda = df_cur_sonda[df_cur_sonda["TRIMESTRE"] == trim_busca]
                
                if not df_cur_sonda.empty:
                    lista_eixos_sonda = sorted(df_cur_sonda["EIXO"].unique().tolist())
                    sel_eixos_s = st.multiselect("1. Selecione o(s) Eixo(s):", lista_eixos_sonda, key=f"s_eixos_{v}")
                    
                    if sel_eixos_s:
                        df_cont_s = df_cur_sonda[df_cur_sonda["EIXO"].isin(sel_eixos_s)]
                        lista_conts_s = sorted(df_cont_s["CONTEUDO_ESPECIFICO"].unique().tolist())
                        sel_conts_s = st.multiselect("2. Selecione os Conteúdos:", lista_conts_s, key=f"s_conts_{v}")
                        
                        if sel_conts_s:
                            st.divider()
                            c_q1, c_q2 = st.columns([1, 2])
                            qtd_q_sonda = c_q1.slider("Nº de Questões:", 3, 15, 10, key=f"s_qtd_in_{v}")
                            instr_extra_s = c_q2.text_area("📝 Contexto Adicional:", key=f"s_instr_{v}")
                            
                            if st.button("🚀 GERAR SONDA DE PROFICIÊNCIA", use_container_width=True, type="primary"):
                                with st.spinner("Maestro Sosa arquitetando Tratado Diagnóstico..."):
                                    nome_elite_sonda = util.gerar_nome_material_elite(ano_sonda, "Sonda Diagnóstica", trim_sonda)
                                    st.session_state.sosa_id_atual = nome_elite_sonda
                                    st.session_state.lab_meta = {
                                        "ano": ano_sonda, "trimestre": trim_sonda, 
                                        "tipo": "SONDA", "aula_alvo": "Sonda Diagnóstica", "semana_ref": "AVALIAÇÃO"
                                    }
                                    
                                    peso_q = 10.0 / qtd_q_sonda
                                    peso_q_str = util.sosa_to_str(peso_q)

                                    # PROMPT IMPERATIVO V68
                                    prompt_sonda = (
                                        f"ORDEM DE PERÍCIA V68 - RIGOR NUMÉRICO E DENSIDADE\n"
                                        f"SÉRIE: {ano_sonda}º Ano | VALOR: 10.0 | QTD: {qtd_q_sonda}\n"
                                        f"CONTEÚDOS: {' / '.join(sel_conts_s)}.\n\n"
                                        f"🚨 DIRETRIZES DE EXECUÇÃO:\n"
                                        f"1. [VALOR: 10.0] na linha 1.\n"
                                        f"2. [PROFESSOR]: Escreva no mínimo 3 parágrafos técnicos de fundamentação e mediação.\n"
                                        f"3. [ALUNO]: Gere EXATAMENTE {qtd_q_sonda} questões no formato inline: **QUESTÃO XX ({peso_q_str} ponto) -**.\n"
                                        f"4. [GRADE_DE_CORRECAO]: Tabela ou lista técnica de descritores e análise de distratores.\n"
                                        f"5. [PEI]: Gere {int(qtd_q_sonda/2 if qtd_q_sonda%2==0 else (qtd_q_sonda+1)/2)} questões com andaime cognitivo.\n\n"
                                        f"CHECKLIST: Proibido introduções ou conversas. Vá direto às tags."
                                    )
                                    st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_SONDA_DIAGNOSTICA", prompt_sonda, usar_busca=True)
                                    st.rerun()

# --- ABA 3: ENGENHARIA DE TRABALHOS (VERSÃO V31.7 - BLINDAGEM DE TABELAS) ---
        with tab_trabalhos:
            st.subheader("📋 Engenharia de Projetos e Semanários (BNCC Elite)")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([1.5, 1, 1])
                natureza_p = c1.selectbox("Natureza do Ativo:", 
                    ["Semanário Temático", "Projeto de Identidade (Itabuna)", "Investigação Científica", "Projeto BNCC Livre"], 
                    key=f"t_nat_{v}")
                ano_t = c2.selectbox("Série Alvo:", [6, 7, 8, 9], key=f"t_ano_{v}")
                modo_t = c3.selectbox("Modo de Execução:", ["Individual", "Em Grupo (Equipes)", "Interdisciplinar"], key=f"t_modo_{v}")

            with st.container(border=True):
                st.markdown("#### 🌟 Alinhamento de Competências Gerais (BNCC)")
                comps_proj = st.multiselect("Selecione as Competências Âncora do Projeto:", [
                    "1. Conhecimento", "2. Pensamento Crítico e Criativo", "3. Repertório Cultural",
                    "4. Comunicação", "5. Cultura Digital", "6. Trabalho e Projeto de Vida",
                    "7. Argumentação", "8. Autoconhecimento", "9. Empatia e Cooperação", "10. Responsabilidade e Cidadania"
                ], key=f"t_comp_bncc_{v}")

            with st.container(border=True):
                c_t1, c_t2, c_t3 = st.columns([2, 1, 1])
                tema_t = c_t1.text_input("Título do Projeto/Tema:", placeholder="Ex: A Matemática do Cacau...", key=f"t_tema_{v}")
                valor_t = c_t2.number_input("Valor (0-10):", 0.0, 10.0, 2.0, step=0.5, key=f"t_val_{v}")
                qtd_aulas_t = c_t3.slider("Duração (Aulas):", 1, 10, 2, key=f"t_q_aulas_{v}")
                
            df_cur_t = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_t))]
            if not df_cur_t.empty:
                lista_eixos_t = sorted(df_cur_t["EIXO"].unique().tolist())
                eixos_sel_t = st.multiselect("Eixos da Matriz para Integrar:", lista_eixos_t, key=f"t_eixos_multi_{v}")
                
                if eixos_sel_t:
                    df_hab_t = df_cur_t[df_cur_t["EIXO"].isin(eixos_sel_t)]
                    conts_t = st.multiselect("Conteúdos Específicos (Itabuna):", 
                                           sorted(df_hab_t["CONTEUDO_ESPECIFICO"].unique().tolist()), 
                                           key=f"t_cont_multi_{v}")
                    
                    instr_extra_p = st.text_area("📝 Instruções de Pesquisa / Contexto Adicional:", key=f"t_extra_proj_{v}")

                    if st.button("🚀 MATERIALIZAR PROJETO DE ELITE", use_container_width=True, type="primary"):
                        if not tema_t or not conts_t:
                            st.error("Defina o Título e selecione ao menos um Conteúdo da Matriz.")
                        else:
                            with st.spinner("Maestro Sosa arquitetando roteiro investigativo..."):
                                nome_legivel = util.gerar_nome_material_elite(ano_t, "Projeto", tema_t)
                                
                                st.session_state.sosa_id_atual = nome_legivel
                                st.session_state.lab_meta = {
                                    "ano": ano_t, "trimestre": "I Trimestre", 
                                    "tipo": "PROJETO", "aula_alvo": tema_t, "semana_ref": "PROJETO"
                                }
                                
                                prompt_t = (
                                    f"ID_FORNECIDO: {nome_legivel}.\n"
                                    f"TEMA: {tema_t}. NATUREZA: {natureza_p}.\n"
                                    f"SÉRIE: {ano_t}º Ano. MODO: {modo_t}.\n"
                                    f"COMPETÊNCIAS BNCC: {', '.join(comps_proj)}.\n"
                                    f"CONTEÚDOS ITABUNA: {', '.join(conts_t)}.\n"
                                    f"VALOR: {util.sosa_to_str(valor_t)} | DURAÇÃO: {qtd_aulas_t} aulas.\n"
                                    f"EXTRAS: {instr_extra_p}.\n\n"
                                    f"🚨 AVISO CRÍTICO DE FORMATAÇÃO:\n"
                                    f"NÃO USE TABELAS DE CARACTERES (BORDAS). O Word quebra a formatação.\n"
                                    f"Entregue a [RUBRICA_DE_MERITO] em formato de lista de tópicos clara.\n\n"
                                    f"MISSÃO: Use o ID_FORNECIDO na tag [SOSA_ID]. Gere o material completo com as TAGS [SOSA_ID], [COMPETENCIAS_BNCC], [HABILIDADES_BNCC], [OBJETO_CONHECIMENTO], [CONTEXTO_GLOCAL], [PROFESSOR], [ALUNO], [ESTRATEGIA_DUA_PEI], [RUBRICA_DE_MERITO]."
                                )
                                st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_PROJETOS_V31_ELITE", prompt_t, usar_busca=True)
                                st.session_state.v_lab = int(time.time())
                                st.rerun()

# --- ABA 4: ATIVIDADES COMPLEMENTARES (VERSÃO V32.0 - CLÍNICA PEDAGÓGICA) ---
        with tab_complementar:
            st.subheader("📚 Atividades Complementares e Recomposição (Ponte Curricular)")
            
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                ano_alvo = c1.selectbox("Série Alvo (Sua Turma):", [6, 7, 8, 9], key=f"comp_ano_alvo_{v}")
                
                origem_tipo = c2.radio("Origem do Conteúdo (DNA Curricular):", 
                    ["Série Atual (Safra/Consolidação)", "Ano Anterior (Intervenção/Recomposição)"], 
                    horizontal=True, key=f"comp_origem_tipo_{v}")
            
            # --- LÓGICA DE INTERVENÇÃO CLÍNICA (SCANNER LOOKUP) ---
            contexto_scanner = ""
            if "Ano Anterior" in origem_tipo:
                with st.container(border=True):
                    st.markdown("#### 🔍 1. Análise de Evidências (Scanner)")
                    c_t1, c_t2 = st.columns([1, 1])
                    turma_interv = c_t1.selectbox("Selecione a Turma para Diagnóstico:", sorted(df_alunos['TURMA'].unique()), key=f"comp_turma_{v}")
                    ano_origem = c_t2.selectbox("Buscar base em qual série?", [1, 2, 3, 4, 5, 6, 7, 8], index=ano_alvo-2, key=f"comp_ano_orig_{v}")
                    
                    # Busca erros reais no Scanner para esta turma
                    if not df_diagnosticos.empty:
                        erros_turma = df_diagnosticos[df_diagnosticos['TURMA'] == turma_interv]
                        if not erros_turma.empty:
                            media_baixa = erros_turma[erros_turma['NOTA_CALCULADA'].apply(util.sosa_to_float) < 6.0]
                            if not media_baixa.empty:
                                lista_avs = media_baixa['ID_AVALIACAO'].unique()
                                st.error(f"🚨 **Lacunas Detectadas:** A turma teve baixo desempenho em: {', '.join(lista_avs[:2])}")
                                contexto_scanner = f"A Turma {turma_interv} apresentou dificuldades reais nas avaliações: {lista_avs}. Foque em resgatar a base do {ano_origem}º ano."
                            else:
                                st.success("✅ Turma com bom desempenho médio no Scanner.")
            else:
                ano_origem = ano_alvo
                st.info(f"📖 **Modo Safra:** Consolidando o conteúdo planejado para o {ano_alvo}º Ano.")

            # --- FILTRAGEM DA MATRIZ ---
            df_cur_comp = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_origem))]
            
            if not df_cur_comp.empty:
                with st.container(border=True):
                    c_f1, c_f2 = st.columns(2)
                    sel_eixo_c = c_f1.multiselect("2. Eixo da Matriz:", sorted(df_cur_comp["EIXO"].unique().tolist()), key=f"comp_eixo_{v}")
                    if sel_eixo_c:
                        sel_cont_c = c_f2.multiselect("3. Conteúdo Base:", sorted(df_cur_comp[df_cur_comp["EIXO"].isin(sel_eixo_c)]["CONTEUDO_ESPECIFICO"].unique().tolist()), key=f"comp_cont_{v}")
                        if sel_cont_c:
                            sel_obj_c = st.multiselect("4. Objetivos Oficiais:", sorted(df_cur_comp[df_cur_comp["CONTEUDO_ESPECIFICO"].isin(sel_cont_c)]["OBJETIVOS"].unique().tolist()), key=f"comp_obj_{v}")
                            
                            st.divider()
                            c_q1, c_q2, c_q3 = st.columns([1, 1, 2])
                            tipo_comp = c_q1.selectbox("Objetivo:", ["Fixação", "Reforço", "Aprofundamento", "Recomposição"], key=f"comp_tipo_{v}")
                            qtd_q_comp = c_q2.slider("Nº Questões:", 3, 15, 10, key=f"comp_q_{v}")
                            instr_extra_c = c_q3.text_area("📝 Contexto Adicional:", key=f"comp_instr_{v}")

                            if st.button("🚀 GERAR MATERIAL DE ELITE", use_container_width=True, type="primary"):
                                with st.spinner("Maestro Sosa arquitetando material com DNA único..."):
                                    
                                    # 1. GERAÇÃO DO DNA ÚNICO (SOSA-ID)
                                    # O util.gerar_sosa_id já traz o fuso de Itabuna e um hash aleatório
                                    sosa_id_hash = util.gerar_sosa_id(tipo_comp, ano_alvo, "I") 
                                    
                                    # 2. DEFINIÇÃO DA NOMENCLATURA DE SOBERANIA
                                    if "Ano Anterior" in origem_tipo:
                                        # PADRÃO: RECOMP - {TURMA} - ID
                                        nome_elite_c = f"RECOMP - {turma_interv} - {sosa_id_hash}"
                                        persona_alvo = "ARQUITETO_RECOMPOSICAO_V68_ELITE"
                                    else:
                                        # PADRÃO: {ANO}º Ano - {TIPO} - ID
                                        nome_elite_c = f"{ano_alvo}º Ano - {tipo_comp} - {sosa_id_hash}"
                                        persona_alvo = "MAESTRO_SOSA_V28_ELITE"

                                    # 3. CARREGAMENTO NO ESTADO DO SISTEMA
                                    st.session_state.sosa_id_atual = nome_elite_c
                                    st.session_state.lab_meta = {
                                        "ano": ano_alvo, 
                                        "trimestre": "I Trimestre", 
                                        "tipo": tipo_comp.upper(), 
                                        "semana_ref": "RECOMPOSIÇÃO" if "Ano Anterior" in origem_tipo else "SAFRA"
                                    }
                                    
                                    # 4. DISPARO DA IA COM O ID FORNECIDO
                                    prompt_c = (
                                        f"ID_FORNECIDO: {nome_elite_c}.\n"
                                        f"SÉRIE ALVO: {ano_alvo}º Ano | SÉRIE ORIGEM: {ano_origem}º Ano.\n"
                                        f"OBJETIVO: {tipo_comp}. CONTEXTO SCANNER: {contexto_scanner}.\n"
                                        f"CONTEÚDOS: {', '.join(sel_cont_c)}.\n"
                                        f"OBJETIVOS: {', '.join(sel_obj_c)}.\n"
                                        f"QUANTIDADE: {qtd_q_comp} questões. EXTRAS: {instr_extra_c}.\n\n"
                                        f"MISSÃO: Use o ID_FORNECIDO na tag [SOSA_ID]. Gere com as TAGS [VALOR: 0.0], [SOSA_ID], [MAPA_DE_RECOMPOSICAO], [PROFESSOR], [ALUNO], [RESPOSTAS_PEDAGOGICAS], [GRADE_DE_CORRECAO], [PEI]."
                                    )
                                    
                                    st.session_state.lab_temp = ai.gerar_ia(persona_alvo, prompt_c, usar_busca=True)
                                    st.session_state.v_lab = int(time.time())
                                    st.rerun()

        # --- ABA 5: ACERVO DE MATERIAIS (VERSÃO V43 - COMPATÍVEL COM PROJETOS BNCC ELITE) ---
        with tab_acervo_lab:
            st.subheader("📂 Gestão de Acervo de Materiais (PIP - Aulas, Projetos e Revisões)")
            
            # 1. FILTROS DE BUSCA DE ELITE
            c_m1, c_m2, c_m3 = st.columns([1, 1, 1])
            f_trim_m = c_m1.selectbox("📅 Filtrar Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="m_trim_filter")
            f_ano_m = c_m2.selectbox("🎓 Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key="m_ano_filter")
            f_tipo_m = c_m3.selectbox("🧪 Tipo de Ativo:", ["Todos", "Aula", "PROJETO", "Fixação", "REVISÃO"], key="m_tipo_filter")

            # 2. PROCESSAMENTO DA BASE
            df_m = df_aulas.copy()
            if f_trim_m != "Todos":
                df_m = df_m[df_m['CONTEUDO'].str.contains(f_trim_m, na=False)]
            if f_ano_m != "Todos":
                df_m = df_m[df_m['ANO'] == f_ano_m]
            if f_tipo_m != "Todos":
                df_m = df_m[df_m['TIPO_MATERIAL'].str.upper().str.contains(f_tipo_m.upper())]

            df_m = df_m.iloc[::-1] # Mais recentes no topo

            if not df_m.empty:
                for _, row in df_m.iterrows():
                    with st.container(border=True):
                        txt_f = str(row['CONTEUDO'])
                        identificador = row['TIPO_MATERIAL']
                        
                        # DETECÇÃO DE TIPO (AULA VS PROJETO)
                        is_projeto_h = "[JUSTIFICATIVA_PHC]" in txt_f or "PROJETO" in identificador.upper()
                        
                        st.markdown(f"### 📘 {identificador}")
                        
                        # EXTRAÇÃO DE METADADOS BNCC (Se for projeto)
                        if is_projeto_h:
                            val_hab = ai.extrair_tag(txt_f, "HABILIDADES_BNCC") or ai.extrair_tag(txt_f, "HABILIDADE_BNCC")
                            val_comp = ai.extrair_tag(txt_f, "COMPETENCIAS_BNCC")
                            if val_hab: st.caption(f"🆔 **Habilidades:** {val_hab}")
                            if val_comp: st.caption(f"🌟 **Competências:** {val_comp}")

                        # 3. EXTRAÇÃO DE LINKS
                        l_alu = re.search(r"(?:Aluno|Regular)\((.*?)\)", txt_f).group(1) if re.search(r"(?:Aluno|Regular)\((.*?)\)", txt_f) else row.get('LINK_DRIVE')
                        l_pei = re.search(r"PEI\((.*?)\)", txt_f).group(1) if "PEI(" in txt_f and "PEI(N/A)" not in txt_f else None
                        l_prof = re.search(r"Prof\((.*?)\)", txt_f).group(1) if "Prof(" in txt_f and "Prof(N/A)" not in txt_f else None

                        c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
                        if l_alu: c_b1.link_button("📝 ALUNO", str(l_alu), use_container_width=True, type="primary")
                        if l_pei: c_b2.link_button("♿ PEI", str(l_pei), use_container_width=True)
                        else: c_b2.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                        if l_prof: c_b3.link_button("👨‍🏫 PROF", str(l_prof), use_container_width=True)
                        else: c_b3.button("⚪ SEM GUIA", disabled=True, use_container_width=True)
                        
                        if c_b4.button("🔄 REFINAR", key=f"ref_mat_h_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = txt_f
                            st.session_state.sosa_id_atual = identificador
                            st.session_state.lab_meta = {"ano": str(row["ANO"]).replace("º",""), "tipo": "REFINO", "aula_alvo": row['TIPO_MATERIAL'], "semana_ref": row['SEMANA_REF']}
                            st.success("Material carregado!"); time.sleep(0.5); st.rerun()
                            
                        if c_b5.button("🗑️ APAGAR", key=f"del_mat_h_{row.name}", use_container_width=True):
                            if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", identificador):
                                st.rerun()

                        # 4. EXPANDER DE CONTEÚDO (VISÃO HÍBRIDA)
                        with st.expander("👁️ VER DETALHES DO MATERIAL"):
                            col_v1, col_v2 = st.columns(2)
                            
                            if is_projeto_h:
                                # VISÃO DE PROJETO
                                with col_v1:
                                    st.markdown("**👨‍🏫 Seção do Professor (PHC)**")
                                    st.info(f"**Justificativa:**\n{ai.extrair_tag(txt_f, 'JUSTIFICATIVA_PHC')}")
                                    st.warning(f"**Rubrica de Mérito:**\n{ai.extrair_tag(txt_f, 'RUBRICA_DE_MERITO')}")
                                with col_v2:
                                    st.markdown("**📝 Roteiro do Aluno (Investigação)**")
                                    st.success(f"**Contexto:**\n{ai.extrair_tag(txt_f, 'CONTEXTO_INVESTIGATIVO')}")
                                    st.write(f"**Missão:**\n{ai.extrair_tag(txt_f, 'MISSÃO_DE_PESQUISA')}")
                                    st.write(f"**Passo a Passo:**\n{ai.extrair_tag(txt_f, 'PASSO_A_PASSO')}")
                                    st.caption(f"**Produto:** {ai.extrair_tag(txt_f, 'PRODUTO_ESPERADO')}")
                            else:
                                # VISÃO DE AULA REGULAR
                                with col_v1:
                                    st.markdown("#### 👨‍🏫 Seção do Professor")
                                    st.write(ai.extrair_tag(txt_f, "PROFESSOR") or "Conteúdo não formatado.")
                                with col_v2:
                                    st.markdown("#### 📝 Seção do Aluno")
                                    st.write(ai.extrair_tag(txt_f, "ALUNO") or "Conteúdo não formatado.")
                            
                            # Rodapé de Acessibilidade
                            dua_txt = ai.extrair_tag(txt_f, "ESTRATEGIA_DUA_PEI") or ai.extrair_tag(txt_f, "PEI")
                            if dua_txt:
                                st.divider()
                                st.markdown("♿ **Estratégia de Acessibilidade (DUA/PEI):**")
                                st.caption(dua_txt)
            else:
                st.info("📭 Nenhum material encontrado com os filtros selecionados.")
                
# ==============================================================================
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - VERSÃO V31.9 (FULL INTEGRATION)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("📅 Engenharia de Planejamento (Ponto ID)")
    st.markdown("---")

    # 1. DEFINIÇÃO DA FUNÇÃO DE RESET (Resolve o erro reportUndefinedVariable)
    def reset_planejamento():
        keys_to_clear = ["p_temp", "refino_ativo"]
        for k in keys_to_clear:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_plano = int(time.time())
        st.rerun()

    if "v_plano" not in st.session_state: 
        st.session_state.v_plano = int(time.time())
    
    v = st.session_state.v_plano 

    tab_gerar, tab_producao, tab_acervo, tab_matriz, tab_auditoria = st.tabs([
        "🚀 Engenharia de Planejamento", "🏗️ Dashboard de Produção", "📂 Gestão de Acervo (PIP)", "📖 Matriz Curricular Ativa", "📈 Auditoria de Cobertura"
    ])
    
    with tab_gerar:
        # --- 🛡️ STATUS E NATUREZA ---
        with st.container(border=True):
            st.markdown("### 🛡️ 1. Status e Natureza da Semana")
            cg1, cg2, cg3 = st.columns([1.5, 1, 1])
            tipo_semana = cg1.selectbox("Natureza:", ["Aula Regular", "Avaliação / Trabalho", "Evento Extraordinário"], key=f"gate_tipo_{v}")
            tem_sabado = cg2.toggle("Sábado Letivo?", key=f"gate_sab_{v}")
            carga_horaria = cg3.select_slider("Aulas Úteis:", options=["1 Aula", "2 Aulas", "3 Aulas"], value="2 Aulas", key=f"gate_carga_{v}")

        # --- ⚙️ PARÂMETROS DE REGÊNCIA ---
        with st.container(border=True):
            st.markdown("### ⚙️ 2. Parâmetros de Regência")
            c1, c2, c3 = st.columns([1, 2, 1.5])
            ano_p = c1.selectbox("Série/Ano:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key=f"ano_sel_{v}")
            todas_semanas = util.gerar_semanas()
            sem_p = c2.selectbox("Semana de Referência:", todas_semanas, key=f"sem_sel_{v}")
            sem_limpa = sem_p.split(" (")[0]
            trim_atual = sem_p.split(" - ")[1] if " - " in sem_p else "I Trimestre"
            
            ctx_ia = ""
            if tipo_semana == "Avaliação / Trabalho":
                st.markdown("#### 📦 Vincular Ativo de Safra (Lookup)")
                mats_ano = df_aulas[df_aulas['ANO'].str.contains(str(ano_p))]
                if not mats_ano.empty:
                    ativo_sel = st.selectbox("Selecione o Material Pronto:", mats_ano['TIPO_MATERIAL'].tolist(), key=f"ativo_lookup_{v}")
                    dados_ativo = mats_ano[mats_ano['TIPO_MATERIAL'] == ativo_sel].iloc[0]
                    ctx_ia = f"MODO AVALIAÇÃO. ATIVO VINCULADO: {ativo_sel}. CONTEÚDO DO ATIVO: {dados_ativo['CONTEUDO']}"
                else:
                    st.warning("Nenhum material (Prova/Trabalho) encontrado para este ano.")
            
            elif tipo_semana == "Evento Extraordinário":
                st.markdown("#### 🌟 Foco em Competências Gerais (BNCC)")
                comps_bncc = st.multiselect("Selecione as Competências do Evento:", [
                    "1. Conhecimento", "2. Pensamento Crítico", "3. Repertório Cultural", "4. Comunicação", 
                    "5. Cultura Digital", "6. Projeto de Vida", "7. Argumentação", "8. Autoconhecimento", 
                    "9. Empatia", "10. Responsabilidade"
                ], key=f"comp_geral_{v}")
                ctx_ia = f"MODO EVENTO. COMPETÊNCIAS: {', '.join(comps_bncc)}"
            
            else:
                modo_p = c3.radio("Método:", ["📖 Livro Didático", "🎛️ Manual (Banco)"], horizontal=True, key=f"modo_p_{v}")
                if modo_p == "🎛️ Manual (Banco)":
                    st.markdown("#### 🎯 Seleção Manual da Matriz (Itabuna)")
                    df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == str(ano_p)]
                    sel_eixo = st.multiselect("1. Eixo:", sorted(df_matriz_ano['EIXO'].unique().tolist()), key=f"p_eixo_{v}")
                    sel_cont = st.multiselect("2. Conteúdo:", sorted(df_matriz_ano[df_matriz_ano['EIXO'].isin(sel_eixo)]['CONTEUDO_ESPECIFICO'].unique().tolist()) if sel_eixo else [], key=f"p_cont_{v}")
                    sel_obj = st.multiselect("3. Objetivos:", sorted(df_matriz_ano[df_matriz_ano['CONTEUDO_ESPECIFICO'].isin(sel_cont)]['OBJETIVOS'].unique().tolist()) if sel_cont else [], key=f"p_obj_{v}")
                    ctx_ia = f"MODO REGULAR. EIXO: {sel_eixo}, CONTEÚDO: {sel_cont}, OBJETIVOS: {sel_obj}."
                else:
                    cx1, cx2 = st.columns([2, 1])
                    sel_mat = cx1.multiselect("Livro:", df_materiais["NOME_ARQUIVO"].tolist() if not df_materiais.empty else [], key=f"p_livro_{v}")
                    pags = cx2.text_input("Páginas:", key=f"p_pags_{v}")
                    ctx_ia = f"MODO LIVRO: {sel_mat} PÁGINAS: {pags}."

            strat = st.text_area("Estratégia / Descrição do Evento:", key=f"p_strat_{v}")

        if st.button("🚀 COMPILAR PLANEJAMENTO INTEGRADO", use_container_width=True, type="primary", key=f"btn_compilar_{v}"):
            with st.spinner("Maestro SOSA realizando Integração de Safra..."):
                df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == str(ano_p)]
                status_sabado = "ATIVADO" if tem_sabado else "DESATIVADO"
                prompt = (
                    f"TIPO SEMANA: {tipo_semana}. ANO: {ano_p}º. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}. SÁBADO: {status_sabado}.\n"
                    f"CONTEXTO TÉCNICO: {ctx_ia}. ESTRATÉGIA: {strat}.\n\n"
                    f"--- MATRIZ ITABUNA ---\n{df_matriz_ano.to_string(index=False)}"
                )
                st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt)
                st.session_state.v_plano = int(time.time())
                st.rerun()

        # --- ✏️ EDITOR E VISUALIZAÇÃO ---
        if "p_temp" in st.session_state:
            txt_bruto = st.session_state.p_temp
            t_ed, t_vis = st.tabs(["✏️ Editor de Texto", "👁️ Estrutura BNCC Elite"])
            
            with t_ed:
                with st.container(border=True):
                    st.subheader("🤖 Refinador Maestro")
                    cmd_refine = st.chat_input("Solicite ajustes...", key=f"chat_refine_{v}")
                    if cmd_refine:
                        with st.spinner("Reengenharia em curso..."):
                            st.session_state.p_temp = ai.gerar_ia("REFINADOR_PEDAGOGICO", f"ORDEM: {cmd_refine}\n\nATUAL:\n{st.session_state.p_temp}")
                            st.session_state.v_plano = int(time.time())
                            st.rerun()
                    if st.button("🗑️ LIMPAR GERADO", use_container_width=True, key=f"btn_clear_{v}"): reset_planejamento()

                c_ed1, c_ed2 = st.columns([1, 2])
                ed_hab = c_ed1.text_input("Habilidade/Competência:", ai.extrair_tag(txt_bruto, "HABILIDADE_BNCC") or ai.extrair_tag(txt_bruto, "COMPETENCIA_GERAL"), key=f"ed_h_{v}")
                ed_comp = c_ed2.text_input("Competências Foco:", ai.extrair_tag(txt_bruto, "COMPETENCIAS_FOCO"), key=f"ed_c_{v}")
                ed_geral = st.text_input("Objeto de Conhecimento:", ai.extrair_tag(txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL"), key=f"ed_g_{v}")
                ed_espec = st.text_area("Conteúdos Específicos:", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS"), key=f"ed_e_{v}")
                ed_objs = st.text_area("Objetivos de Aprendizagem:", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO"), key=f"ed_o_{v}")
                ed_a1 = st.text_area("AULA 1:", ai.extrair_tag(txt_bruto, "AULA_1"), height=200, key=f"a1_{v}")
                ed_a2 = st.text_area("AULA 2:", ai.extrair_tag(txt_bruto, "AULA_2"), height=200, key=f"a2_{v}")
                
                # INICIALIZAÇÃO DE ed_a3 (Resolve o erro "ed_a3" não está definido)
                val_a3 = ai.extrair_tag(txt_bruto, "SABADO_LETIVO")
                ed_a3 = st.text_area("SÁBADO LETIVO:", val_a3 if val_a3 else "N/A", key=f"ed_a3_{v}")
                
                ed_ava = st.text_area("Avaliação/Logística:", ai.extrair_tag(txt_bruto, "AVALIACAO_DE_MERITO") or ai.extrair_tag(txt_bruto, "AVALIACAO"), key=f"ed_ava_{v}")
                ed_dua = st.text_area("Estratégia DUA/PEI:", ai.extrair_tag(txt_bruto, "ESTRATEGIA_DUA_PEI") or ai.extrair_tag(txt_bruto, "ADAPTACAO_PEI"), key=f"ed_dua_{v}")

                if st.button("💾 FINALIZAR E DISPARAR PRODUÇÃO", use_container_width=True, type="primary", key=f"btn_save_{v}"):
                    with st.status("Sincronizando Hub Acadêmico...") as status:
                        final_ano_str = f"{ano_p}º"
                        nome_arquivo = f"PLANO_{ano_p}ANO_{sem_limpa.replace(' ', '')}"
                        db.excluir_plano_completo(sem_limpa, final_ano_str)
                        
                        # Consolidação para o DOCX
                        dados_docx = {
                            "geral": f"[{ed_hab}] {ed_geral}", 
                            "especificos": ed_espec, "objetivos": ed_objs, 
                            "recursos": "Livro Didático e Materiais de Safra",
                            "metodologia": f"COMPETÊNCIAS: {ed_comp}\n\nAULA 01:\n{ed_a1}\n\nAULA 02:\n{ed_a2}",
                            "avaliacao": ed_ava, "pei": ed_dua
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": final_ano_str, "semana": sem_limpa, "trimestre": trim_atual})
                        link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=trim_atual, categoria=final_ano_str, semana=sem_limpa, modo="PLANEJAMENTO")
                        
                        if "https" in str(link_drive):
                            final_txt = (
                                f"[HABILIDADE_BNCC] {ed_hab} \n[COMPETENCIAS_FOCO] {ed_comp} \n"
                                f"[OBJETO_CONHECIMENTO] {ed_geral} \n[CONTEUDOS_ESPECIFICOS] {ed_espec} \n"
                                f"[OBJETIVOS_ENSINO] {ed_objs} \n[AULA_1] {ed_a1} \n[AULA_2] {ed_a2} \n"
                                f"[SABADO_LETIVO] {ed_a3} \n[AVALIACAO_DE_MERITO] {ed_ava} \n"
                                f"[ESTRATEGIA_DUA_PEI] {ed_dua} \n--- LINK DRIVE --- {link_drive}"
                            )
                            db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_limpa, final_ano_str, trim_atual, "HUB_ATIVO", final_txt, link_drive])
                            status.update(label="✅ Plano Sincronizado!", state="complete")
                            st.balloons()
                            reset_planejamento()

            with t_vis:
                st.subheader("👁️ Estrutura BNCC Elite (Visão de Regência)")
                c_v1, c_v2 = st.columns(2)
                with c_v1:
                    st.info(f"**🎯 Objeto:** {ed_geral}")
                    st.markdown(f"**🆔 Habilidade:** {ed_hab}")
                    st.markdown(f"**🌟 Competências:** {ed_comp}")
                with c_v2:
                    st.success(f"**👨‍🏫 Aula 1:**\n{ed_a1}")
                    st.success(f"**👨‍🏫 Aula 2:**\n{ed_a2}")
                st.divider()
                c_v3, c_v4 = st.columns(2)
                with c_v3: st.warning(f"**♿ DUA/PEI:**\n{ed_dua}")
                with c_v4: st.error(f"**📝 Avaliação:**\n{ed_ava}")
                if ed_a3 != "N/A": st.info(f"**🗓️ Sábado Letivo:**\n{ed_a3}")
                
# --- ABA 2: DASHBOARD DE PRODUÇÃO (VERSÃO V31.9 - FIX LOGIC) ---
    with tab_producao:
        st.subheader("🏗️ Linha de Montagem de Materiais")
        if not df_planos.empty:
            planos_ativos = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]
            
            if not planos_ativos.empty:
                for _, row in planos_ativos.iterrows():
                    with st.container(border=True):
                        c_p1, c_p2, c_p3, c_p4 = st.columns([1.5, 1.5, 1, 1])
                        
                        sem_ref = row['SEMANA']
                        ano_ref = row['ANO']
                        
                        c_p1.markdown(f"**{sem_ref}**\n`Série: {ano_ref}`")
                        
                        # --- VERIFICAÇÃO DE PROGRESSO REAL (CORRIGIDA) ---
                        # Agora olhamos para a coluna TIPO_MATERIAL, que é onde o nome da aula reside
                        aulas_no_banco = df_aulas[(df_aulas['SEMANA_REF'] == sem_ref) & (df_aulas['ANO'] == ano_ref)]
                        lista_tipos = aulas_no_banco['TIPO_MATERIAL'].astype(str).tolist()
                        
                        # Verifica se "Aula 1" ou "Aula 2" constam na lista de materiais prontos
                        a1_status = "✅" if any("Aula 1" in t for t in lista_tipos) else "⏳"
                        a2_status = "✅" if any("Aula 2" in t for t in lista_tipos) else "⏳"
                        
                        c_p2.markdown(f"**Progresso:**\n{a1_status} Aula 1 | {a2_status} Aula 2")
                        
                        # Botão para ir ao Criador
                        if c_p3.button("🧪 PRODUZIR", key=f"gen_hub_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = row["PLANO_TEXTO"]
                            st.session_state.sosa_id_atual = util.gerar_sosa_id("AULA", row["ANO"], row["TURMA"])
                            st.session_state.lab_meta = {
                                "ano": str(row["ANO"]).replace("º",""), 
                                "trimestre": row["TURMA"], 
                                "tipo": "PRODUÇÃO_HUB",
                                "semana_ref": sem_ref
                            }
                            st.success("Conteúdo enviado! Vá ao Criador de Aulas.")

                        if c_p4.button("✅ CONCLUIR", key=f"fin_hub_{row.name}", use_container_width=True):
                            if db.arquivar_plano_produzido(sem_ref, ano_ref):
                                st.success("Safra Concluída!"); time.sleep(1); st.rerun()
            else:
                st.info("📭 Nenhum plano pendente no Dashboard.")

# --- ABA 3: GESTÃO DE ACERVO (VERSÃO V31.5 - FULL BNCC ELITE) ---
    with tab_acervo:
        st.subheader("📂 Repositório de Planos Estratégicos (Visão 360°)")
        if not df_planos.empty:
            c_h1, c_h2 = st.columns([1, 2])
            f_ano_h = c_h1.selectbox("Filtrar por Série:", ["Todos", "1º", "2º", "3º", "4º", "5º", "6º", "7º", "8º", "9º"], key="hist_ano_v31")
            
            df_h = df_planos.copy()
            if f_ano_h != "Todos": 
                df_h = df_h[df_h["ANO"] == f"{f_ano_h}º"]
            
            if not df_h.empty:
                # Inverte para mostrar os mais recentes primeiro
                lista_semanas = df_h["SEMANA"].tolist()[::-1]
                sel_h = st.selectbox("Selecionar Plano para Visualização:", lista_semanas, key="hist_sem_v31")
                
                dados_h = df_h[df_h["SEMANA"] == sel_h].iloc[0]
                raw_h = str(dados_h["PLANO_TEXTO"])
                
                # --- BOTÕES DE AÇÃO ---
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("🔄 REABRIR PARA REFINO", use_container_width=True, key=f"btn_reopen_{sel_h}"):
                        st.session_state.refino_ativo = {"ano": dados_h["ANO"], "semana": sel_h}
                        st.session_state.p_temp = raw_h
                        st.session_state.v_plano = int(time.time())
                        st.success("✅ Plano carregado no Editor!")
                        st.rerun()
                with col_btn2:
                    if st.button("🚀 MANDAR PARA PRODUÇÃO", use_container_width=True, type="primary", key=f"btn_hub_act_{sel_h}"):
                        if db.ativar_plano_no_hub(sel_h, dados_h["ANO"]):
                            st.success("✅ Plano enviado ao Dashboard!"); time.sleep(1); st.rerun()
                with col_btn3:
                    if "https" in str(dados_h["LINK_DRIVE"]): 
                        st.link_button("📂 ABRIR NO DRIVE", str(dados_h["LINK_DRIVE"]), use_container_width=True)

                # --- VISUALIZAÇÃO DE ELITE (MAPA DO PLANO) ---
                with st.container(border=True):
                    # 1. CABEÇALHO TÉCNICO
                    val_objeto = ai.extrair_tag(raw_h, "OBJETO_CONHECIMENTO") or ai.extrair_tag(raw_h, "CONTEUDO_GERAL")
                    val_hab = ai.extrair_tag(raw_h, "HABILIDADE_BNCC") or ai.extrair_tag(raw_h, "BNCC_CODE")
                    val_comp = ai.extrair_tag(raw_h, "COMPETENCIAS_FOCO") or ai.extrair_tag(raw_h, "COMPETENCIAS_BNCC")
                    
                    st.markdown(f"### 🎯 {val_objeto}")
                    st.markdown(f"**🆔 Habilidade:** `{val_hab}`")
                    st.info(f"**🌟 Competências Foco:** {val_comp}")
                    
                    # 2. CONTEÚDOS E OBJETIVOS (LITERAL ITABUNA)
                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown("<div style='background-color:rgba(41, 98, 255, 0.1); padding:10px; border-radius:5px;'><b>📖 Conteúdos:</b><br>"+ai.extrair_tag(raw_h, 'CONTEUDOS_ESPECIFICOS')+"</div>", unsafe_allow_html=True)
                    with c_info2:
                        st.markdown("<div style='background-color:rgba(46, 204, 113, 0.1); padding:10px; border-radius:5px;'><b>✅ Objetivos:</b><br>"+ai.extrair_tag(raw_h, 'OBJETIVOS_ENSINO')+"</div>", unsafe_allow_html=True)
                    
                    st.divider()
                    
                    # 3. ROTEIRO DE AULAS
                    c_v1, c_v2 = st.columns(2)
                    with c_v1: 
                        st.markdown("##### 📘 Aula 1 (Fundamentação)")
                        st.write(ai.extrair_tag(raw_h, "AULA_1"))
                    with c_v2: 
                        st.markdown("##### 📗 Aula 2 (Aplicação)")
                        st.write(ai.extrair_tag(raw_h, "AULA_2"))
                    
                    # 4. SÁBADO, AVALIAÇÃO E DUA
                    st.divider()
                    c_v3, c_v4 = st.columns(2)
                    with c_v3:
                        val_dua = ai.extrair_tag(raw_h, "ESTRATEGIA_DUA_PEI") or ai.extrair_tag(raw_h, "ADAPTACAO_PEI")
                        st.warning(f"**♿ Estratégia DUA/PEI:**\n{val_dua}")
                    with c_v4:
                        val_ava = ai.extrair_tag(raw_h, "AVALIACAO_DE_MERITO") or ai.extrair_tag(raw_h, "AVALIACAO")
                        st.error(f"**📝 Avaliação de Mérito:**\n{val_ava}")
                    
                    sab_txt = ai.extrair_tag(raw_h, "SABADO_LETIVO")
                    if sab_txt and "N/A" not in sab_txt.upper():
                        st.success(f"**🗓️ Sábado Letivo:**\n{sab_txt}")
                
                if st.button("🗑️ EXCLUIR PLANO DO ACERVO", use_container_width=True, key=f"btn_del_plan_{sel_h}"):
                    if db.excluir_plano_completo(sel_h, dados_h["ANO"]): 
                        st.rerun()
            else: 
                st.info("📭 Nenhum plano encontrado para esta série.")
        else: 
            st.info("📭 Acervo vazio.")

    # --- ABA 4: MATRIZ CURRICULAR ATIVA ---
    with tab_matriz:
        st.subheader("📖 Matriz de Competências e Status de Execução")
        if not df_curriculo.empty:
            ano_c = st.selectbox("Série para Consulta:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key="matriz_ano_v35")
            df_c = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_c))].copy()
            planos_feitos = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_c))]
            lista_conteudos_oficiais = [ai.extrair_tag(p, "CONTEUDOS_ESPECIFICOS").upper() for p in planos_feitos["PLANO_TEXTO"]]
            texto_soberano_planos = " | ".join(lista_conteudos_oficiais)

            def checar_conclusao_cirurgica(conteudo_db):
                if not texto_soberano_planos: return "⏳ PENDENTE"
                def limpar(t): return re.sub(r'[^A-Z0-9]', '', str(t).upper())
                target_limpo = limpar(conteudo_db)
                soberano_limpo = limpar(texto_soberano_planos)
                if target_limpo in soberano_limpo: return "✅ CONCLUÍDO"
                palavras = [p for p in str(conteudo_db).upper().replace(";", "").replace(",", "").split() if len(p) > 4]
                if not palavras: return "⏳ PENDENTE"
                matches = sum(1 for p in palavras if limpar(p) in soberano_limpo)
                return "✅ CONCLUÍDO" if matches >= 2 else "⏳ PENDENTE"

            df_c["STATUS"] = df_c["CONTEUDO_ESPECIFICO"].apply(checar_conclusao_cirurgica)
            st.dataframe(df_c[["TRIMESTRE", "EIXO", "CONTEUDO_ESPECIFICO", "STATUS"]], use_container_width=True, hide_index=True)

    # --- ABA 5: ANALYTICS DE COBERTURA (CORREÇÃO TYPEERROR) ---
    with tab_auditoria:
        st.subheader("📈 Analytics de Cobertura Curricular")
        if not df_curriculo.empty:
            ano_m = st.selectbox("Analisar Série:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key="auditoria_ano_v35")
            df_m = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_m))].copy()
            planos_m = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_m))]
            lista_cont_m = [ai.extrair_tag(t, "CONTEUDOS_ESPECIFICOS").upper() for t in planos_m["PLANO_TEXTO"]]
            texto_m_soberano = " | ".join(lista_cont_m)
            
            def concluido_num_cirurgico(x):
                def limpar(t): return re.sub(r'[^A-Z0-9]', '', str(t).upper())
                txt = limpar(x)
                if txt in limpar(texto_m_soberano): return 1
                palavras = [p for p in str(x).upper().split() if len(p) > 4]
                return 1 if (palavras and sum(1 for p in palavras if limpar(p) in limpar(texto_m_soberano)) >= 2) else 0

            df_m["CONCLUIDO"] = df_m["CONTEUDO_ESPECIFICO"].apply(concluido_num_cirurgico)
            progresso_trim = df_m.groupby("TRIMESTRE")["CONCLUIDO"].agg(["sum", "count"]).reset_index()
            
            if not progresso_trim.empty:
                # VACINA CONTRA TYPEERROR: Força conversão para numérico antes do cálculo
                progresso_trim["sum"] = pd.to_numeric(progresso_trim["sum"], errors='coerce').fillna(0)
                progresso_trim["count"] = pd.to_numeric(progresso_trim["count"], errors='coerce').fillna(1)
                
                progresso_trim["%"] = (progresso_trim["sum"] / progresso_trim["count"] * 100)
                # Converte o resultado final para float antes de arredondar
                progresso_trim["%"] = pd.to_numeric(progresso_trim["%"]).round(1)
                
                c1, c2, c3 = st.columns(3)
                total_geral = (progresso_trim["sum"].sum() / progresso_trim["count"].sum() * 100) if progresso_trim["count"].sum() > 0 else 0
                c1.metric("Cobertura Anual", f"{total_geral:.1f}%")
                p_i = progresso_trim[progresso_trim["TRIMESTRE"] == "I"]["%"].values[0] if "I" in progresso_trim["TRIMESTRE"].values else 0
                c2.metric("Progresso I Trimestre", f"{p_i}%")
                p_ii = progresso_trim[progresso_trim["TRIMESTRE"] == "II"]["%"].values[0] if "II" in progresso_trim["TRIMESTRE"].values else 0
                c3.metric("Progresso II Trimestre", f"{p_ii}%")

                st.plotly_chart(px.bar(progresso_trim, x="TRIMESTRE", y="%", text="%", title=f"Evolução da Cobertura Real - {ano_m}º Ano", color="%", color_continuous_scale="RdYlGn", range_y=[0, 110]), use_container_width=True)
            
# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO (V28.0) - INTERFACE MOBILE FAST
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("📝 Diário de Bordo: Execução Rápida")
    
    if "v_diario" not in st.session_state: st.session_state.v_diario = 1
    v = st.session_state.v_diario

    # 1. FILTROS RÁPIDOS
    with st.container(border=True):
        c1, c2 = st.columns(2)
        turma_sel = c1.selectbox("👥 Turma:", sorted(df_alunos['TURMA'].unique()), key=f"db_t_{v}")
        data_sel = c2.date_input("📅 Data:", date.today(), key=f"db_d_{v}")
        data_str = data_sel.strftime("%d/%m/%Y")

    # 2. DETECÇÃO AUTOMÁTICA DO COCKPIT (O HANDSHAKE)
    aula_ativa = df_registro_aulas[(df_registro_aulas['TURMA'] == turma_sel) & (df_registro_aulas['DATA'] == data_str)]
    
    if not aula_ativa.empty:
        material_hoje = aula_ativa.iloc[0]['CONTEUDO_MINISTRADO']
        st.info(f"🚀 **Aula Ativa:** {material_hoje}")
    else:
        st.warning("⚠️ Nenhuma aula aberta no Cockpit para hoje. Registre primeiro na 'Gestão da Turma'.")
        material_hoje = "Aula Avulsa"

    # 3. MESA DE LANÇAMENTO MOBILE
    st.markdown("---")
    alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
    
    # Botão de Visto em Lote (Economia de Cliques)
    if st.button("✅ DAR VISTO EM TODOS OS ALUNOS", use_container_width=True):
        st.session_state[f"visto_lote_{turma_sel}"] = True
        st.rerun()

    dados_diario = []
    for _, alu in alunos_turma.iterrows():
        id_a = db.limpar_id(alu['ID'])
        is_pei = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
        
        # Valor padrão do visto (checa se o botão de lote foi clicado)
        visto_padrao = st.session_state.get(f"visto_lote_{turma_sel}", True)

        dados_diario.append({
            "ID": id_a,
            "ESTUDANTE": f"♿ {alu['NOME_ALUNO']}" if is_pei else alu['NOME_ALUNO'],
            "FALTOU": False,
            "VISTO": visto_padrao,
            "⭐ BÔNUS": 0.0,
            "TAG": "",
            "OBS": ""
        })

    # Editor Vertical (Otimizado para Celular)
    df_editado = st.data_editor(
        pd.DataFrame(dados_diario),
        column_config={
            "ID": None,
            "ESTUDANTE": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
            "FALTOU": st.column_config.CheckboxColumn("F", help="Faltou"),
            "VISTO": st.column_config.CheckboxColumn("V", help="Visto"),
            "⭐ BÔNUS": st.column_config.SelectboxColumn("Bônus", options=[0.0, 0.1, 0.2, 0.3, 0.5, 1.0]),
            "TAG": st.column_config.SelectboxColumn("Tag", options=["", "Dormiu", "Conversa", "Destaque", "Sem Material", "PEI Concluído"]),
            "OBS": st.column_config.TextColumn("Obs")
        },
        hide_index=True, use_container_width=True, key=f"editor_diario_{v}"
    )

    # 4. SALVAMENTO E SINCRONIA
    if st.button("💾 SALVAR REGISTROS E CONSOLIDAR", type="primary", use_container_width=True):
        with st.status("Sincronizando Práxis...") as status:
            db.limpar_diario_data_turma(data_str, turma_sel)
            linhas_diario = []
            for _, r in df_editado.iterrows():
                tag_f = "AUSÊNCIA" if r['FALTOU'] else r['TAG']
                visto_f = False if r['FALTOU'] else r['VISTO']
                
                linhas_diario.append([
                    data_str, r['ID'], r['ESTUDANTE'].replace("♿ ", ""), turma_sel,
                    str(visto_f), tag_f, f"[{material_hoje}] {r['OBS']}", util.sosa_to_str(r['⭐ BÔNUS'])
                ])
            
            if db.salvar_lote("DB_DIARIO_BORDO", linhas_diario):
                status.update(label="✅ Diário Sincronizado!", state="complete")
                st.balloons()
                # Limpa o estado do visto em lote
                if f"visto_lote_{turma_sel}" in st.session_state: del st.session_state[f"visto_lote_{turma_sel}"]
                time.sleep(1); st.rerun()

# ==============================================================================
# MÓDULO: PAINEL DE NOTAS V32 - CÁLCULO AUTOMÁTICO E TRANSBORDAMENTO DE BÔNUS
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.title("📊 Torre de Comando: Gestão de Notas e Performance")
    st.markdown("---")

    if "v_notas" not in st.session_state: st.session_state.v_notas = 1
    v = st.session_state.v_notas

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro na aba 'Gestão da Turma'.")
    else:
        # 1. CONFIGURADOR DE PESOS (CRITÉRIOS DO TRIMESTRE)
        with st.container(border=True):
            st.markdown("### ⚙️ Configuração de Critérios do Trimestre")
            c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1.5, 1, 0.8, 0.8, 0.8])
            turma_sel = c_f1.selectbox("👥 Selecione a Turma:", sorted(df_alunos['TURMA'].unique()), key="n_turma")
            trimestre_sel = c_f2.selectbox("📅 Trimestre Atual:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="n_trim")
            
            # Pesos que definem o teto de cada nota no sistema da prefeitura
            p_visto = c_f3.number_input("Peso Vistos:", 0.0, 10.0, 3.0, step=0.5, key=f"p_v_{trimestre_sel}")
            p_teste = c_f4.number_input("Peso Teste:", 0.0, 10.0, 3.0, step=0.5, key=f"p_t_{trimestre_sel}")
            p_prova = c_f5.number_input("Peso Prova:", 0.0, 10.0, 4.0, step=0.5, key=f"p_p_{trimestre_sel}")
            
            if (p_visto + p_teste + p_prova) != 10.0:
                st.warning(f"⚠️ A soma dos pesos ({p_visto + p_teste + p_prova}) é diferente de 10.0.")

        # 2. MOTOR DE CÁLCULO AUTOMÁTICO (DIÁRIO DE BORDO)
        # Este bloco garante que a nota de visto seja zerada e recalculada por trimestre
        vistos_auto_map = {}
        bonus_total_map = {}
        
        # Datas oficiais de Itabuna (conforme utils.py)
        calendario = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
            "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
        }
        dt_ini, dt_fim = calendario.get(trimestre_sel)

        if not df_diario.empty:
            df_d_t = df_diario[df_diario['TURMA'] == turma_sel].copy()
            # Converte datas para comparação real
            df_d_t['DATA_DT'] = pd.to_datetime(df_d_t['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
            # Filtra apenas o que aconteceu NESTE trimestre
            df_d_trim = df_d_t[(df_d_t['DATA_DT'] >= dt_ini) & (df_d_t['DATA_DT'] <= dt_fim)]
            
            for id_aluno in df_alunos[df_alunos['TURMA'] == turma_sel]['ID']:
                id_l = db.limpar_id(id_aluno)
                d_alu = df_d_trim[df_d_trim['ID_ALUNO'].apply(db.limpar_id) == id_l]
                
                if not d_alu.empty:
                    # Cálculo de Vistos (Proporcional ao peso do trimestre)
                    aulas_com_visto = len(d_alu[d_alu['VISTO_ATIVIDADE'].astype(str).upper() == "TRUE"])
                    total_aulas_periodo = len(d_alu)
                    vistos_auto_map[id_l] = round((aulas_com_visto / total_aulas_periodo * p_visto), 2)
                    
                    # Soma de Bônus (Diário + Projetos salvos no diário)
                    bonus_total_map[id_l] = d_alu['BONUS'].apply(util.sosa_to_float).sum() if 'BONUS' in d_alu.columns else 0.0
                else:
                    vistos_auto_map[id_l], bonus_total_map[id_l] = 0.0, 0.0

        # 3. CONSOLIDAÇÃO DA MESA DE LANÇAMENTO
        notas_banco = df_notas[(df_notas['TURMA'] == turma_sel) & (df_notas['TRIMESTRE'] == trimestre_sel)]
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        dados_editor = []
        for _, alu in alunos_turma.iterrows():
            id_a = db.limpar_id(alu['ID'])
            reg_b = notas_banco[notas_banco['ID_ALUNO'].apply(db.limpar_id) == id_a]
            
            # Carrega notas salvas ou inicia zerado
            n_teste = util.sosa_to_float(reg_b.iloc[0]['NOTA_TESTE']) if not reg_b.empty else 0.0
            n_prova = util.sosa_to_float(reg_b.iloc[0]['NOTA_PROVA']) if not reg_b.empty else 0.0
            n_rec = util.sosa_to_float(reg_b.iloc[0]['NOTA_REC']) if not reg_b.empty else 0.0
            
            is_pei = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"]

            dados_editor.append({
                "ID": id_a,
                "ESTUDANTE": f"♿ {alu['NOME_ALUNO']}" if is_pei else alu['NOME_ALUNO'],
                "VISTOS (AUTO)": vistos_auto_map.get(id_a, 0.0),
                "BÔNUS (TOTAL)": bonus_total_map.get(id_a, 0.0),
                "TESTE (LANÇAR)": n_teste,
                "PROVA (LANÇAR)": n_prova,
                "REC. PARALELA": n_rec
            })

        # 4. TABELA 1: AJUSTE DE SOBERANIA (ENTRADA)
        st.subheader("📝 1. Consolidação de Dados")
        st.caption(f"Nota de Vistos calculada automaticamente para o {trimestre_sel}. Bônus integrado do Diário e Projetos.")
        
        df_input = st.data_editor(
            pd.DataFrame(dados_editor),
            column_config={
                "ID": None,
                "ESTUDANTE": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                "VISTOS (AUTO)": st.column_config.NumberColumn("Vistos (Sistema)", format="%.1f", disabled=True, help="Calculado pelo Diário de Bordo"),
                "BÔNUS (TOTAL)": st.column_config.NumberColumn("⭐ Bônus", format="%.1f", disabled=True, help="Soma de méritos e projetos"),
                "TESTE (LANÇAR)": st.column_config.NumberColumn("Nota Teste", min_value=0.0, max_value=p_teste, format="%.1f"),
                "PROVA (LANÇAR)": st.column_config.NumberColumn("Nota Prova", min_value=0.0, max_value=p_prova, format="%.1f"),
                "REC. PARALELA": st.column_config.NumberColumn("🔄 Rec.", min_value=0.0, max_value=10.0, format="%.1f"),
            },
            hide_index=True, use_container_width=True, key=f"editor_v32_{v}"
        )

        # 5. ALGORITMO DE TRANSBORDAMENTO (COMPATIBILIDADE PREFEITURA)
        def aplicar_transbordamento(row):
            bonus_restante = row['BÔNUS (TOTAL)']
            v_base = row['VISTOS (AUTO)']
            t_base = row['TESTE (LANÇAR)']
            p_base = row['PROVA (LANÇAR)']
            
            # Passo 1: Completar Vistos
            v_final = min(p_visto, v_base + bonus_restante)
            bonus_restante -= (v_final - v_base)
            
            # Passo 2: Completar Teste (se sobrar bônus)
            t_final = min(p_teste, t_base + max(0, bonus_restante))
            bonus_restante -= (t_final - t_base)
            
            # Passo 3: Completar Prova (se sobrar bônus)
            p_final = min(p_prova, p_base + max(0, bonus_restante))
            
            # Média Final e Recuperação
            soma_notas = v_final + t_final + p_final
            media_final = min(10.0, max(soma_notas, row['REC. PARALELA']))
            
            return pd.Series([v_final, t_final, p_final, media_final])

        df_input[['V_PREF', 'T_PREF', 'P_PREF', 'MEDIA_FINAL']] = df_input.apply(aplicar_transbordamento, axis=1)

        # 6. TABELA 2: EXPORTAÇÃO PREFEITURA (SAÍDA AUTOMÁTICA)
        st.markdown("---")
        st.subheader("🏛️ 2. Gabarito de Lançamento (Sistema Prefeitura)")
        st.info("As notas abaixo são calculadas em tempo real. Copie os valores para o sistema oficial.")
        
        def style_situacao(v):
            color = '#2ECC71' if v >= 6.0 else '#FF4B4B'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_input[['ESTUDANTE', 'V_PREF', 'T_PREF', 'P_PREF', 'MEDIA_FINAL']].style.applymap(
                style_situacao, subset=['MEDIA_FINAL']
            ).format({
                "V_PREF": "{:.1f}", "T_PREF": "{:.1f}", "P_PREF": "{:.1f}", "MEDIA_FINAL": "{:.2f}"
            }),
            use_container_width=True,
            hide_index=True,
            column_config={
                "V_PREF": st.column_config.NumberColumn("Atividades", help="Lançar no campo 'Atividades' da prefeitura"),
                "T_PREF": st.column_config.NumberColumn("Teste", help="Lançar no campo 'Teste' da prefeitura"),
                "P_PREF": st.column_config.NumberColumn("Prova", help="Lançar no campo 'Prova' da prefeitura"),
                "MEDIA_FINAL": st.column_config.NumberColumn("Média Final", format="%.2f")
            }
        )

        # 7. SALVAMENTO
        if st.button("💾 SALVAR E SINCRONIZAR BOLETIM", type="primary", use_container_width=True):
            with st.status("Sincronizando registros...") as status:
                db.limpar_notas_turma_trimestre(turma_sel, trimestre_sel)
                linhas_save = []
                for _, r in df_input.iterrows():
                    linhas_save.append([
                        r['ID'], r['ESTUDANTE'].replace("♿ ", ""), turma_sel, trimestre_sel,
                        util.sosa_to_str(r["V_PREF"]), util.sosa_to_str(r["T_PREF"]),
                        util.sosa_to_str(r["P_PREF"]), util.sosa_to_str(r["REC. PARALELA"]),
                        util.sosa_to_str(r['MEDIA_FINAL'])
                    ])
                if db.salvar_lote("DB_NOTAS", linhas_save):
                    status.update(label="✅ Boletim Sincronizado!", state="complete")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

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
# MÓDULO: GESTÃO DA TURMA (V32.0) - COCKPIT DE INTELIGÊNCIA ESTRATÉGICA
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Cockpit de Regência: Gestão 360°")
    st.markdown("---")

    if "v_gestao" not in st.session_state: st.session_state.v_gestao = 1
    v = st.session_state.v_gestao

    tab_cockpit, tab_criar, tab_povoar, tab_editar = st.tabs([
        "📊 Cockpit da Turma", "🏗️ Arquitetura de Turmas", "➕ Povoar Alunos", "✏️ Edição & Transferência"
    ])

# --- ABA 1: COCKPIT DA TURMA (VERSÃO V33.0 - RADAR DE ALERTAS INTEGRADO) ---
    with tab_cockpit:
        if df_turmas.empty:
            st.info("📭 Nenhuma turma cadastrada.")
        else:
            c_f1, c_f2 = st.columns([1, 1])
            turma_foco = c_f1.selectbox("🎯 Selecione a Turma:", sorted(df_turmas['ID_TURMA'].unique()), key=f"foco_t_{v}")
            trim_foco = c_f2.selectbox("📅 Trimestre de Safra:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"foco_trim_{v}")
            
            alunos_t = df_alunos[df_alunos['TURMA'] == turma_foco].sort_values(by="NOME_ALUNO")
            ano_num = "".join(filter(str.isdigit, turma_foco)) 

            # --- 1. DASHBOARD DE STATUS (KPIs) ---
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Alunos", len(alunos_t))
            
            mask_pei = ~alunos_t['NECESSIDADES'].astype(str).str.upper().str.strip().isin(["NENHUMA", "PENDENTE", "", "NAN"])
            c2.metric("Estudantes PEI", len(alunos_t[mask_pei]))
            
            engaj_medio = 0
            if not df_diario.empty:
                vistos_t = df_diario[df_diario['TURMA'] == turma_foco]
                if not vistos_t.empty:
                    vistos_validos = vistos_t[vistos_t['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]
                    engaj_medio = (len(vistos_validos) / len(vistos_t)) * 100
            c3.metric("Engajamento Médio", f"{engaj_medio:.0f}%")
            c4.metric("Série", f"{ano_num}º Ano")

            # ==============================================================================
            # 🚨 NOVO BLOCO: RADAR DE ALERTA PEDAGÓGICO (INTEGRAÇÃO COM SCANNER)
            # ==============================================================================
            st.markdown("---")
            with st.container(border=True):
                st.subheader("📡 Radar de Alerta Pedagógico (Baseado no Scanner)")
                
                if df_diagnosticos.empty:
                    st.info("💡 Aguardando dados de gabaritos para gerar alertas de lacunas.")
                else:
                    # Filtra diagnósticos da turma atual
                    diag_turma = df_diagnosticos[df_diagnosticos['TURMA'] == turma_foco]
                    
                    if diag_turma.empty:
                        st.success("✅ Nenhuma lacuna crítica detectada para esta turma até o momento.")
                    else:
                        col_r1, col_r2 = st.columns([1.2, 1.8])
                        
                        with col_r1:
                            # Média da última avaliação
                            ultima_av_nome = diag_turma['ID_AVALIACAO'].iloc[-1]
                            media_av = diag_turma[diag_turma['ID_AVALIACAO'] == ultima_av_nome]['NOTA_CALCULADA'].apply(util.sosa_to_float).mean()
                            st.metric(f"Última Avaliação: {ultima_av_nome[:20]}...", f"{media_av:.2f}")
                            
                            if media_av < 6.0:
                                st.error("🚨 DESEMPENHO EM ALERTA")
                            else:
                                st.success("🟢 DESEMPENHO DENTRO DA META")

                        with col_r2:
                            # Identifica alunos em risco (notas baixas recorrentes)
                            alunos_risco = diag_turma[diag_turma['NOTA_CALCULADA'].apply(util.sosa_to_float) < 5.0]['NOME_ALUNO'].unique()
                            if len(alunos_risco) > 0:
                                st.warning(f"⚠️ **Atenção Prioritária:** {len(alunos_risco)} alunos com dificuldades críticas.")
                                with st.expander("Ver lista de alunos em risco"):
                                    for a in alunos_risco: st.caption(f"• {a}")
                            
                            # Sugestão de Ação
                            if media_av < 6.0:
                                st.markdown("💡 **Sugestão do Maestro:** Gere um material de **Recomposição** focado nos erros desta avaliação antes de avançar o conteúdo.")
                            else:
                                st.markdown("💡 **Sugestão do Maestro:** Prossiga com a **Safra Atual** planejada.")

            st.markdown("---")
            col_esq, col_dir = st.columns([1.8, 1.2])

            with col_esq:
                st.subheader("🕒 Abertura de Aula (Handshake Diário)")
                with st.container(border=True):
                    st.markdown("#### 🚀 Registrar Ativo para Hoje")
                    planos_ano = df_planos[df_planos['ANO'].str.contains(ano_num)]
                    materiais_ano = df_aulas[df_aulas['ANO'].str.contains(ano_num)]

                    c_r1, c_r2 = st.columns(2)
                    data_aula = c_r1.date_input("Data da Aula:", date.today(), key=f"dt_reg_{v}")
                    plano_sel = c_r2.selectbox("Vincular Plano Base:", ["Nenhum"] + planos_ano['SEMANA'].tolist(), key=f"plano_reg_{v}")
                    
                    # Filtro inteligente de materiais (Prioriza Recomposição se a média for baixa)
                    mats_sel = st.multiselect("📦 Selecione o Material (Aula/Sonda/Projeto):", options=materiais_ano['TIPO_MATERIAL'].tolist(), key=f"mats_reg_{v}")

                    if st.button("💾 ABRIR AULA NO DIÁRIO", use_container_width=True, type="primary"):
                        with st.spinner("Sincronizando com o Diário Mobile..."):
                            conteudo_final = " + ".join(mats_sel) if mats_sel else "Aula Baseada no Plano"
                            db.salvar_no_banco("DB_REGISTRO_AULAS", [
                                data_aula.strftime("%d/%m/%Y"), plano_sel, turma_foco, 
                                conteudo_final, "PENDENTE", "ABERTA"
                            ])
                            st.success(f"✅ Aula aberta! Agora você pode preencher o Diário de Bordo.")
                            time.sleep(1); st.rerun()

                st.subheader("📜 Histórico de Ativos Aplicados")
                aulas_reg = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco].iloc[::-1]
                if not aulas_reg.empty:
                    for _, reg in aulas_reg.head(5).iterrows():
                        with st.expander(f"📅 {reg['DATA']} - {reg['CONTEUDO_MINISTRADO'][:40]}..."):
                            st.write(f"**Material:** {reg['CONTEUDO_MINISTRADO']}")
                            st.write(f"**Plano Vinculado:** {reg['SEMANA']}")

            with col_dir:
                st.subheader("📂 Inventário e Alunos")
                with st.container(border=True):
                    st.markdown(f"**📦 Ativos Disponíveis ({ano_num}º Ano)**")
                    # Mostra os últimos 5 materiais criados para esta série
                    for m in materiais_ano['TIPO_MATERIAL'].tail(5):
                        st.caption(f"• {m}")
                
                with st.container(border=True):
                    st.markdown("**👥 Foco PEI**")
                    for _, alu in alunos_t.iterrows():
                        if str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]:
                            st.warning(f"♿ {alu['NOME_ALUNO']}")

# --- ABA 2: ARQUITETURA DE TURMAS (VERSÃO V32.1 - COM ESCUDO ANTI-DUPLICIDADE) ---
    with tab_criar:
        st.subheader("🏗️ Configurar Nova Turma")
        v_t = f"t_{v}"
        
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            ano_t = c1.selectbox("Série/Ano:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key=f"ano_{v_t}")
            letra_t = c2.selectbox("Letra:", ["A", "B", "C", "D", "E", "F", "G"], key=f"letra_{v_t}")
            turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"], key=f"turno_{v_t}")

        dias_aula = st.multiselect(
            "📅 Selecione os Dias de Aula (Máx 2):", 
            ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"], 
            max_selections=2, 
            key=f"dias_{v_t}"
        )

        horarios_escolhidos = {}
        if dias_aula:
            st.markdown("#### ⏰ Defina o Tempo de Aula por dia")
            # Define opções de horário baseadas no turno
            if turno_t == "Matutino":
                opcoes_h = {"1º Tempo": "07:10h – 09:10h", "2º Tempo": "09:30h – 11:30h"}
            elif turno_t == "Vespertino":
                opcoes_h = {"1º Tempo": "13:10h – 15:10h", "2º Tempo": "15:30h – 17:30h"}
            else:
                opcoes_h = {"1º Tempo": "18:30h – 20:30h", "2º Tempo": "20:40h – 22:40h"}

            cols_h = st.columns(len(dias_aula))
            for i, dia in enumerate(dias_aula):
                with cols_h[i]:
                    st.info(f"**{dia}**")
                    t_sel = st.radio(f"Horário para {dia}:", options=list(opcoes_h.keys()), key=f"radio_{dia}_{v_t}")
                    horarios_escolhidos[dia] = t_sel
            
            st.divider()
            
            if st.button("🚀 CADASTRAR TURMA AGORA", use_container_width=True, type="primary", key=f"btn_cad_{v_t}"):
                # 1. GERAÇÃO DA SIGLA ÚNICA (DNA DA TURMA)
                prefixo_turno = turno_t[0].upper() # M, V ou N
                sigla = f"{ano_t}ª {prefixo_turno}{letra_t}" # Ex: 6ª MA
                
                # 2. ESCUDO DE INTEGRIDADE: VERIFICAÇÃO DE DUPLICIDADE
                turmas_existentes = []
                if not df_turmas.empty:
                    turmas_existentes = df_turmas['ID_TURMA'].astype(str).str.strip().tolist()

                if sigla in turmas_existentes:
                    st.error(f"🚨 **ERRO DE SOBERANIA:** A turma **{sigla}** já está cadastrada no sistema. Verifique o Cockpit ou a aba de Edição.")
                else:
                    with st.status("Sincronizando Nova Arquitetura...") as status:
                        str_dias = " / ".join(dias_aula)
                        str_horarios = " / ".join([f"{d[:3]}: {horarios_escolhidos[d]}" for d in dias_aula])
                        
                        # Salva no banco: [ID_TURMA, NOME_TURMA, TURNO, DIAS_SEMANA, HORARIO_TEMPO, STATUS]
                        sucesso = db.salvar_no_banco("DB_TURMAS", [
                            sigla, 
                            f"{ano_t}º Ano {letra_t}", 
                            turno_t, 
                            str_dias, 
                            str_horarios, 
                            "ATIVO"
                        ])
                        
                        if sucesso:
                            status.update(label=f"✅ Turma {sigla} cadastrada com sucesso!", state="complete")
                            st.balloons()
                            time.sleep(1.5)
                            st.cache_data.clear() # Limpa o cache para a nova turma aparecer nos filtros
                            st.rerun()
                        else:
                            status.update(label="❌ Erro ao acessar o Google Sheets.", state="error")

    # --- ABA 3: POVOAR ALUNOS ---
    with tab_povoar:
        st.subheader("➕ Inclusão de Estudantes")
        t_dest = st.selectbox("Turma de Destino:", df_turmas['ID_TURMA'].tolist() if not df_turmas.empty else [], key=f"dest_{v}")
        metodo = st.radio("Método:", ["Manual", "CSV"], horizontal=True, key=f"met_{v}")
        if metodo == "Manual":
            with st.form("f_manual", clear_on_submit=True):
                nome_a = st.text_input("Nome Completo:").upper()
                nec_a = st.text_input("Necessidades/CID:", value="NENHUMA").upper()
                if st.form_submit_button("💾 Salvar"):
                    id_n = db.gerar_proximo_id(df_alunos)
                    db.salvar_no_banco("DB_ALUNOS", [id_n, nome_a, t_dest, "ATIVO", nec_a, "MANUAL"])
                    st.success("Cadastrado!"); st.rerun()
        else:
            f_csv = st.file_uploader("Arquivo CSV", type=["csv"], key=f"csv_{v}")
            if f_csv and st.button("🚀 Importar Lista", key=f"btn_csv_{v}"):
                df_up = pd.read_csv(f_csv)
                id_b = db.gerar_proximo_id(df_alunos)
                for idx, r in df_up.iterrows():
                    db.salvar_no_banco("DB_ALUNOS", [id_b+idx, str(r['NOME']).upper(), t_dest, "ATIVO", "NENHUMA", "CSV"])
                st.success("Importado!"); st.rerun()

    # --- ABA 4: EDIÇÃO & TRANSFERÊNCIA ---
    with tab_editar:
        st.subheader("✏️ Alterar Cadastro ou Transferir Aluno")
        turmas_com_alunos = sorted(df_alunos['TURMA'].unique().tolist())
        t_origem = st.selectbox("Selecione a Turma Atual:", [""] + turmas_com_alunos, key=f"orig_{v}")
        
        if t_origem:
            alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO")
            aluno_sel_nome = st.selectbox("Selecione o Aluno:", alunos_opcoes['NOME_ALUNO'].tolist(), key=f"alu_ed_{v}")
            
            dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
            id_fixo = dados_atuais['ID']

            with st.form("form_edicao_aluno_v33"):
                st.info(f"🆔 Editando Registro ID: {id_fixo}")
                c_e1, c_e2 = st.columns(2)
                novo_nome = c_e1.text_input("Nome Completo:", value=dados_atuais['NOME_ALUNO'])
                nova_nec = c_e2.text_input("Necessidades/CID:", value=dados_atuais['NECESSIDADES'])
                
                c_e3, c_e4 = st.columns(2)
                novo_status = c_e3.selectbox("Status:", ["ATIVO", "DESISTENTE", "TRANSFERIDO"], index=0)
                
                lista_turmas_total = df_turmas['ID_TURMA'].tolist()
                idx_turma_atual = lista_turmas_total.index(t_origem) if t_origem in lista_turmas_total else 0
                nova_turma = c_e4.selectbox("Transferir para:", lista_turmas_total, index=idx_turma_atual)
                
                if st.form_submit_button("💾 CONFIRMAR ALTERAÇÕES E LIMPAR DUPLICIDADE"):
                    with st.status("Executando Protocolo de Limpeza e Atualização...") as status:
                        if db.excluir_aluno_por_id(id_fixo):
                            sucesso = db.salvar_no_banco("DB_ALUNOS", [
                                id_fixo, novo_nome.upper().strip(), nova_turma, 
                                novo_status, nova_nec.upper().strip(), "EDITADO"
                            ])
                            if sucesso:
                                status.update(label="✅ Cadastro Atualizado!", state="complete")
                                st.balloons(); time.sleep(1); st.rerun()

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
# MÓDULO: CENTRAL DE AVALIAÇÕES (V64.0 - ACERVO PIP E SINCRONIA TOTAL)
# ==============================================================================
elif menu == "📝 Central de Avaliações":
    st.title("📝 Arquiteto de Exames e Gestão de Safra")
    st.markdown("---")
    
    is_refinando_av = "refino_av_ativo" in st.session_state

    def reset_avaliacoes():
        keys_to_del = ["temp_prova", "temp_revisao", "av_pei", "refino_av_ativo", "av_valor_total", "av_gab_pei", "av_res_pei_ia", "av_nome_fixo"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.cache_data.clear()
        st.session_state.v_av = int(time.time())
        st.rerun()

    if "v_av" not in st.session_state: st.session_state.v_av = 1
    v = st.session_state.v_av

    tab_arquiteto, tab_refino, tab_vis, tab_recomposicao, tab_finalizar, tab_acervo_av = st.tabs([
        "🚀 Arquiteto de Exames", "🤖 Refinador Maestro", "👁️ Visualização 360°", "🔥 Recomposição/Revisão", "💾 Finalizar Ativo", "🗂️ Acervo de Safra"
    ])

# --- ABA 1: ARQUITETO (VERSÃO V65.2 - COM DIAGNÓSTICO ATIVO) ---
    with tab_arquiteto:
        if is_refinando_av:
            st.warning(f"🛠️ **MODO REFINO:** Editando {st.session_state.refino_av_ativo.get('tipo')}")
            if st.button("❌ CANCELAR E VOLTAR AO NOVO"): reset_avaliacoes()

        with st.container(border=True):
            st.markdown("### ⚙️ 1. Configuração do Exame")
            c1, c2, c3, c4 = st.columns([1.5, 1, 1, 1])
            tipo_av = c1.selectbox("Tipo:", ["Teste", "Prova", "Recuperação", "2ª Chamada"], key=f"av_t_{v}")
            v_total = c2.number_input("Valor Total:", 0.0, 10.0, 3.0 if "Teste" in tipo_av else 4.0, step=0.5, key=f"av_v_{v}")
            ano_av = c3.selectbox("Série:", [6, 7, 8, 9], index=0, key=f"av_a_{v}")
            qtd_q = c4.number_input("Nº Total de Questões:", 2, 20, 10, key=f"av_q_{v}")

        with st.container(border=True):
            st.markdown("### 📊 2. Distribuição de Dificuldade (Taxonomia)")
            cd1, cd2, cd3 = st.columns(3)
            q_facil = cd1.number_input("Fáceis:", 0, qtd_q, int(qtd_q*0.3), key=f"q_f_{v}")
            q_medio = cd2.number_input("Médias:", 0, qtd_q, int(qtd_q*0.5), key=f"q_m_{v}")
            q_dificil = cd3.number_input("Difíceis:", 0, qtd_q, qtd_q - (q_facil + q_medio), key=f"q_d_{v}")
            soma_q = q_facil + q_medio + q_dificil

        with st.container(border=True):
            st.markdown("### 🎯 3. Matriz de Mérito e Filtro Curricular")
            c_trim1, c_trim2 = st.columns([1, 2])
            trim_filtro = c_trim1.selectbox("Filtrar por Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"av_trim_filter_{v}")
            
            df_planos_trim = df_planos[(df_planos["ANO"].astype(str).str.contains(str(ano_av))) & (df_planos["TURMA"].astype(str).str.contains(trim_filtro))]
            semanas_do_trimestre = df_planos_trim["SEMANA"].unique().tolist()
            df_materiais_trim = df_aulas[(df_aulas["ANO"].astype(str).str.contains(str(ano_av))) & (df_aulas["SEMANA_REF"].isin(semanas_do_trimestre))]
            
            mats_selecionados = c_trim2.multiselect(f"Ativos de Safra Detectados ({len(df_materiais_trim)}):", options=df_materiais_trim["TIPO_MATERIAL"].tolist(), key=f"av_ref_{v}")

        # ==============================================================================
        # 🔍 NOVO BLOCO: DIAGNÓSTICO DE SOBERANIA (INTELIGÊNCIA EM TEMPO REAL)
        # ==============================================================================
        with st.container(border=True):
            st.markdown("#### 🔍 Diagnóstico de Configuração")
            col_diag1, col_diag2 = st.columns(2)
            
            with col_diag1:
                # Validação de Soma de Questões
                if soma_q == qtd_q:
                    st.success(f"✅ Taxonomia: {soma_q}/{qtd_q} questões distribuídas.")
                elif soma_q < qtd_q:
                    st.warning(f"⚠️ Taxonomia: Faltam {qtd_q - soma_q} questões para o total.")
                else:
                    st.error(f"🚨 Taxonomia: Você excedeu o total em {soma_q - qtd_q} questões.")
                
                # Validação de Peso Municipal (Itabuna)
                if tipo_av == "Teste" and v_total != 3.0:
                    st.info("💡 Nota: O padrão para Testes em Itabuna costuma ser 3,0.")
                elif tipo_av == "Prova" and v_total != 4.0:
                    st.info("💡 Nota: O padrão para Provas em Itabuna costuma ser 4,0.")

            with col_diag2:
                # Cálculo de Peso por Questão
                peso_q_live = v_total / qtd_q if qtd_q > 0 else 0
                st.metric("Peso por Questão", f"{peso_q_live:.2f} pts")
                
                # Validação de Materiais
                if not mats_selecionados:
                    st.error("❌ Nenhum material de safra selecionado.")
                else:
                    st.success(f"📚 Cobertura: {len(mats_selecionados)} aula(s) vinculada(s).")

        # --- BOTÃO DE COMPILAÇÃO ---
        if st.button("💎 COMPILAR EXAME COM GRADE DE PERÍCIA", use_container_width=True, type="primary"):
            if soma_q != qtd_q: 
                st.error(f"Erro: A soma das dificuldades ({soma_q}) deve ser igual ao total de questões ({qtd_q}).")
            elif not mats_selecionados: 
                st.error("Selecione os Ativos de Safra.")
            else:
                with st.spinner(f"Arquitetando {qtd_q} questões com pesos iguais e gabarito blindado..."):
                    peso_por_questao = v_total / qtd_q
                    peso_str = util.sosa_to_str(peso_por_questao)

                    contexto_aulas = ""
                    for m_nome in mats_selecionados:
                        m_row = df_materiais_trim[df_materiais_trim["TIPO_MATERIAL"] == m_nome].iloc[0]
                        contexto_aulas += f"MATERIAL_ID: {m_nome}\nCONTEÚDO: {m_row['CONTEUDO']}\n"

                    prompt = (
                        f"ORDEM DE PRODUÇÃO V65 - RIGOR TOTAL E ANTI-CHUTE\n"
                        f"TIPO: {tipo_av} | SÉRIE: {ano_av}º Ano | VALOR TOTAL: {v_total}\n"
                        f"QUANTIDADE OBRIGATÓRIA: {qtd_q} questões.\n"
                        f"VALOR POR QUESTÃO: {peso_str} (Todas com o mesmo peso).\n"
                        f"DISTRIBUIÇÃO: {q_facil} Fáceis, {q_medio} Médias, {q_dificil} Difíceis.\n\n"
                        f"🚨 DIRETRIZES DE ELITE:\n"
                        f"1. Inicie com [VALOR: {v_total}].\n"
                        f"2. Use o formato: **QUESTÃO XX ({peso_str} ponto) -** para todas.\n"
                        f"3. Aplique a Engenharia Anti-Chute no gabarito (distribuição equilibrada).\n"
                        f"4. Inclua [ PROMPT IMAGEM: ... ] para questões que necessitem de suporte visual.\n"
                        f"5. Organize a [GRADE_DE_CORRECAO] de forma ultra-detalhada (Habilidade + Justificativa + Perícia de Distratores).\n\n"
                        f"CONTEÚDO BASE:\n{contexto_aulas}"
                    )
                    
                    st.session_state.temp_prova = ai.gerar_ia("ARQUITETO_EXAMES_V30_ELITE", prompt, usar_busca=True)
                    st.session_state.av_valor_total = v_total
                    st.session_state.av_nome_fixo = f"{tipo_av.upper()}_{ano_av}ANO_{trim_filtro.replace(' ', '')}"
                    st.rerun()

    # --- ABA 2: REFINADOR ---
    with tab_refino:
        if "temp_prova" in st.session_state:
            st.subheader("🤖 Refinamento de Precisão")
            cmd = st.chat_input("Solicitar ajuste no exame ou na grade...", key=f"chat_av_{v}")
            if cmd:
                with st.spinner("Reescrevendo..."):
                    st.session_state.temp_prova = ai.gerar_ia("REFINADOR_EXAMES", f"ORDEM: {cmd}\n\nATUAL:\n{st.session_state.temp_prova}")
                    st.session_state.v_av += 1; st.rerun()
            st.text_area("Editor de Exame:", st.session_state.temp_prova, height=500, key=f"ed_av_raw_{v}")
        else: st.info("Gere um exame para refinar.")

    # --- ABA 3: VISUALIZAÇÃO ---
    with tab_vis:
        if "temp_prova" in st.session_state:
            txt_f = st.session_state.temp_prova
            t1, t2, t3, t4 = st.tabs(["📝 Prova Regular", "🔍 Grade de Perícia (AAP/DF)", "♿ Prova PEI", "✅ Gabaritos"])
            with t1: st.text_area("Questões:", ai.extrair_tag(txt_f, "QUESTOES"), height=500, key=f"vis_reg_{v}")
            with t2: st.text_area("Habilidades e Distratores:", ai.extrair_tag(txt_f, "GRADE_DE_CORRECAO"), height=500, key=f"vis_grade_{v}")
            with t3: st.text_area("PEI:", ai.extrair_tag(txt_f, "PEI"), height=500, key=f"vis_pei_{v}")
            with t4: 
                c_g1, c_g2 = st.columns(2)
                c_g1.markdown("### Regular"); c_g1.code(ai.extrair_tag(txt_f, "GABARITO_TEXTO"))
                c_g2.markdown("### PEI"); c_g2.code(ai.extrair_tag(txt_f, "GABARITO_PEI"))
        else: st.info("Aguardando geração...")

    # --- ABA 4: RECOMPOSIÇÃO ---
    with tab_recomposicao:
        if "temp_prova" in st.session_state:
            st.subheader("🚀 Gerador de Revisão Sincronizada")
            if st.button("💎 MATERIALIZAR REVISÃO DE ELITE", use_container_width=True, type="primary"):
                with st.spinner("Convertendo prova em roteiro de recomposição..."):
                    prompt_rev = f"PROVA BASE:\n{st.session_state.temp_prova}\n\nID_EXAME: {st.session_state.av_nome_fixo}"
                    st.session_state.temp_revisao = ai.gerar_ia("ARQUITETO_REVISAO_V29", prompt_rev)
                    st.rerun()
            
            if "temp_revisao" in st.session_state:
                txt_rev = st.session_state.temp_revisao
                tr1, tr2, tr3, tr_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "♿ PEI", "☁️ SINCRONIA"])
                with tr1: st.text_area("Guia:", ai.extrair_tag(txt_rev, "PROFESSOR"), height=400, key=f"rev_prof_{v}")
                with tr2: st.text_area("Folha:", ai.extrair_tag(txt_rev, "ALUNO"), height=400, key=f"rev_alu_{v}")
                with tr3: st.text_area("PEI:", ai.extrair_tag(txt_rev, "PEI"), height=400, key=f"rev_pei_{v}")
                
                with tr_sync:
                    if st.button("💾 EXECUTAR TRIPLE-SYNC DA REVISÃO", use_container_width=True, type="primary"):
                        with st.status("Sincronizando...") as status:
                            nome_rev = f"REVISAO_{st.session_state.av_nome_fixo}"
                            db.excluir_registro_com_drive("DB_AULAS_PRONTAS", nome_rev)
                            
                            doc_alu = exporter.gerar_docx_aluno_v24(nome_rev, ai.extrair_tag(txt_rev, "ALUNO"), {"ano": f"{ano_av}º", "trimestre": trim_filtro})
                            link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_rev}_ALUNO", modo="AULA")
                            
                            doc_pei = exporter.gerar_docx_pei_v25(f"{nome_rev}_PEI", ai.extrair_tag(txt_rev, "PEI"), {"ano": f"{ano_av}º", "trimestre": trim_filtro})
                            link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_rev}_PEI", modo="AULA")
                            
                            doc_prof = exporter.gerar_docx_professor_v25(nome_rev, ai.extrair_tag(txt_rev, "PROFESSOR"), {"ano": f"{ano_av}º", "semana": "REVISÃO", "trimestre": trim_filtro})
                            link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_rev}_PROF", modo="AULA")
                            
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_rev, 
                                txt_rev + f"\n--- LINKS ---\nRegular({link_alu}) PEI({link_pei}) Prof({link_prof})", f"{ano_av}º", link_alu
                            ])
                            status.update(label="✅ Revisão Sincronizada!", state="complete"); st.balloons()
        else: st.warning("⚠️ Gere a prova primeiro.")

    # --- ABA 5: FINALIZAR ATIVO (CORREÇÃO DE SINCRONIA PEI) ---
    with tab_finalizar:
        if "temp_prova" in st.session_state:
            st.subheader("💾 Consolidação do Ativo de Safra")
            v_tipo = st.session_state.get(f"av_t_{v}", "Prova")
            v_ano = st.session_state.get(f"av_a_{v}", 6)
            v_qtd = st.session_state.get(f"av_q_{v}", 10)
            c_s1, c_s2 = st.columns(2)
            trim_av = c_s1.selectbox("Trimestre Alvo:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"trim_fin_{v}")
            nome_arq = c_s2.text_input("Nome do Arquivo:", st.session_state.get('av_nome_fixo', 'AVALIACAO'), key=f"name_av_in_{v}")

            if st.button("💾 SALVAR COMO PRONTO PARA APLICAÇÃO", use_container_width=True, type="primary"):
                with st.status("Sincronizando Ativos e Gerando DOCX...") as status:
                    v_total_num = st.session_state.get('av_valor_total', 10.0)
                    identificador = f"{v_tipo} - {v_ano}º Ano ({trim_av})"
                    db.excluir_avaliacao_completa(identificador, v_tipo)
                    
                    # 1. Geração Regular
                    info_reg = {"ano": f"{v_ano}º", "tipo_prova": v_tipo, "valor": util.sosa_to_str(v_total_num), "valor_questao": util.sosa_to_str(v_total_num/v_qtd), "qtd_questoes": v_qtd, "trimestre": trim_av}
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, st.session_state.temp_prova, info_reg)
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, modo="AVALIACAO")
                    
                    # 2. Geração PEI
                    txt_pei = ai.extrair_tag(st.session_state.temp_prova, "PEI")
                    link_pei = "N/A"
                    if txt_pei:
                        qtd_q_pei = len(re.findall(r'QUESTÃO', txt_pei.upper()))
                        info_pei = {"ano": f"{v_ano}º", "tipo_prova": v_tipo, "valor": util.sosa_to_str(v_total_num), "valor_questao": util.sosa_to_str(v_total_num/qtd_q_pei), "qtd_questoes": qtd_q_pei, "trimestre": trim_av}
                        doc_pei = exporter.gerar_docx_prova_v25(f"{nome_arq}_PEI", txt_pei, info_pei)
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_arq}_PEI", modo="AVALIACAO")

                    # 3. Geração Guia Professor (Grade de Perícia)
                    txt_prof = ai.extrair_tag(st.session_state.temp_prova, "GRADE_DE_CORRECAO")
                    link_prof = "N/A"
                    if txt_prof:
                        doc_prof = exporter.gerar_docx_professor_v25(f"{nome_arq}_GRADE", txt_prof, {"ano": f"{v_ano}º", "semana": "AVALIAÇÃO", "trimestre": trim_av})
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_arq}_GRADE", modo="AVALIACAO")

                    # CONSOLIDAÇÃO FINAL NO BANCO (COM TODOS OS LINKS)
                    conteudo_final_banco = f"[VALOR: {v_total_num}]\n" + st.session_state.temp_prova + f"\n--- LINKS ---\nRegular({link_reg}) PEI({link_pei}) Prof({link_prof})"
                    
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [
                        datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", identificador, 
                        conteudo_final_banco, f"{v_ano}º", link_reg
                    ])
                    status.update(label="✅ Ativo Salvo com Sucesso!", state="complete"); st.balloons(); time.sleep(1.5); reset_avaliacoes()

# --- ABA 6: ACERVO DE SAFRA (VERSÃO V65 - DESIGN PIP & INTELIGÊNCIA DE GABARITO) ---
    with tab_acervo_av:
        st.subheader("🗂️ Gestão de Acervo de Safra (PIP - Provas e Revisões)")
        
        # 1. FILTROS DE BUSCA DE ELITE
        c_h1, c_h2, c_h3 = st.columns([1, 1, 1])
        f_trim_h = c_h1.selectbox("📅 Filtrar Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="h_trim_av")
        f_ano_h = c_h2.selectbox("🎓 Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key="h_ano_av")
        f_tipo_h = c_h3.selectbox("📝 Tipo de Ativo:", ["Todos", "AVALIAÇÃO", "REVISÃO"], key="h_tipo_av")

        # 2. FILTRAGEM DA BASE
        df_exames = df_aulas[df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy()
        if f_trim_h != "Todos": df_exames = df_exames[df_exames['CONTEUDO'].str.contains(f_trim_h, na=False)]
        if f_ano_h != "Todos": df_exames = df_exames[df_exames['ANO'] == f_ano_h]
        if f_tipo_h != "Todos": df_exames = df_exames[df_exames['SEMANA_REF'] == f_tipo_h]

        df_exames = df_exames.iloc[::-1] # Mais recentes no topo

        if not df_exames.empty:
            for _, row in df_exames.iterrows():
                with st.container(border=True):
                    txt_f = str(row['CONTEUDO'])
                    identificador = row['TIPO_MATERIAL']
                    valor_ex = ai.extrair_tag(txt_f, "VALOR")
                    
                    # --- CABEÇALHO DO CARD ---
                    c_tit, c_val = st.columns([3, 1])
                    c_tit.markdown(f"### 📄 {identificador}")
                    if valor_ex: c_val.info(f"💰 Valor: {valor_ex}")

                    # --- EXTRAÇÃO DE GABARITO EXPRESSO (PARA VISÃO RÁPIDA) ---
                    gab_simples = ai.extrair_tag(txt_f, "GABARITO_TEXTO") or ai.extrair_tag(txt_f, "RESPOSTAS_IA")
                    if gab_simples:
                        st.markdown(f"**✅ Gabarito Expresso:** `{gab_simples}`")

                    # --- EXTRAÇÃO ROBUSTA DE LINKS ---
                    l_reg = re.search(r"Regular\((.*?)\)", txt_f).group(1) if "Regular(" in txt_f else (re.search(r"Aluno\((.*?)\)", txt_f).group(1) if "Aluno(" in txt_f else row.get('LINK_DRIVE'))
                    l_pei = re.search(r"PEI\((.*?)\)", txt_f).group(1) if "PEI(" in txt_f and "PEI(N/A)" not in txt_f else None
                    l_prof = re.search(r"Prof\((.*?)\)", txt_f).group(1) if "Prof(" in txt_f and "Prof(N/A)" not in txt_f else None

                    # --- BOTÕES DE AÇÃO ---
                    c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
                    if l_reg: c_b1.link_button("📝 REGULAR", str(l_reg), use_container_width=True, type="primary")
                    if l_pei: c_b2.link_button("♿ PEI", str(l_pei), use_container_width=True)
                    else: c_b2.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                    if l_prof: c_b3.link_button("🔍 PERÍCIA", str(l_prof), use_container_width=True)
                    else: c_b3.button("⚪ SEM GRADE", disabled=True, use_container_width=True)
                    
                    if c_b4.button("🔄 REFINAR", key=f"ref_av_h_{row.name}", use_container_width=True):
                        st.session_state.temp_prova = txt_f
                        st.session_state.av_nome_fixo = identificador
                        st.rerun()
                        
                    if c_b5.button("🗑️ APAGAR", key=f"del_av_h_{row.name}", use_container_width=True):
                        if db.excluir_avaliacao_completa(identificador, row['SEMANA_REF']): st.rerun()

                    # --- EXPANDER COM ABAS INTERNAS (O GRANDE MELHORAMENTO) ---
                    with st.expander("👁️ RAIO-X DO ATIVO (GABARITO, PERÍCIA E QUESTÕES)"):
                        t_gab, t_ques, t_pei_v = st.tabs(["🎯 Gabarito & Perícia", "📝 Questões Regulares", "♿ Versão PEI"])
                        
                        with t_gab:
                            st.markdown("#### 🔍 Análise de Habilidades e Distratores")
                            grade = ai.extrair_tag(txt_f, "GRADE_DE_CORRECAO")
                            if grade:
                                st.info(grade)
                            else:
                                st.warning("Grade de perícia não localizada neste ativo.")
                            
                            st.markdown("#### ✅ Respostas Detalhadas")
                            respostas = ai.extrair_tag(txt_f, "RESPOSTAS_IA") or ai.extrair_tag(txt_f, "GABARITO_TEXTO")
                            st.code(respostas if respostas else "Gabarito não processado.")

                        with t_ques:
                            st.markdown("#### 📝 Visualização das Questões (Regular)")
                            questoes = ai.extrair_tag(txt_f, "QUESTOES")
                            st.write(questoes if questoes else "Texto das questões não localizado.")

                        with t_pei_v:
                            st.markdown("#### ♿ Visualização da Versão Adaptada (PEI)")
                            pei_txt = ai.extrair_tag(txt_f, "PEI")
                            if pei_txt:
                                st.write(pei_txt)
                                st.divider()
                                st.markdown("**✅ Gabarito PEI:**")
                                st.code(ai.extrair_tag(txt_f, "GABARITO_PEI") or "Gabarito PEI não localizado.")
                            else:
                                st.info("Este ativo não possui versão PEI gerada.")
        else:
            st.info("📭 Nenhum ativo de safra encontrado com os filtros selecionados.")

# ==============================================================================
# MÓDULO: CENTRAL DE INTELIGÊNCIA DE RESULTADOS (V64.2 - CORREÇÃO DE FILTROS)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("📸 Central de Inteligência de Resultados (CIR)")
    st.markdown("---")

    if "v_scan" not in st.session_state: st.session_state.v_scan = 1
    v = st.session_state.v_scan

    # --- FUNÇÃO AUXILIAR: FILTRO HIERÁRQUICO BLINDADO V64.2 ---
    def filtrar_ativos_cir_v64(turma, trimestre_nome, apenas_provas=True):
        """
        Motor de busca inteligente que cruza Série, Trimestre e Tipo de Material.
        """
        if not turma or not trimestre_nome: return []
        try:
            serie_num = str(turma)[0] # Pega o "6" de "6º Ano"
            df_f = df_aulas[df_aulas['ANO'].astype(str).str.contains(serie_num)].copy()
            
            # Normalização de Data para detecção de Trimestre
            def detectar_trimestre(x):
                try:
                    # Se for serial do Sheets (ex: 46063)
                    if str(x).replace('.','',1).isdigit():
                        dt = date(1899, 12, 30) + timedelta(days=int(float(x)))
                        return util.obter_info_trimestre(dt)[0]
                    # Se for string de data (DD/MM/YYYY)
                    if "/" in str(x):
                        partes = str(x).split("/")
                        dt = date(int(partes[2]), int(partes[1]), int(partes[0]))
                        return util.obter_info_trimestre(dt)[0]
                except: pass
                return "Outros"

            df_f['TRIM_DETECTADO'] = df_f['DATA'].apply(detectar_trimestre)
            
            # Filtro por Trimestre (na data ou no texto do conteúdo)
            mask_trim = (df_f['TRIM_DETECTADO'] == trimestre_nome) | \
                        (df_f['CONTEUDO'].str.contains(trimestre_nome, na=False))
            df_f = df_f[mask_trim]

            if apenas_provas:
                permitidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "DIAGNOSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]
                df_f = df_f[df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos))]
            else:
                # Filtro para Aba 2: Trabalhos, Projetos e Fixação
                permitidos = ["PROJETO", "FIXAÇÃO", "REFORÇO", "ATIVIDADE", "TRABALHO", "AULA"]
                proibidos = ["TESTE", "PROVA", "RECUPERAÇÃO", "SONDA"]
                df_f = df_f[df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos))]
                df_f = df_f[~df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(proibidos))]
            
            return sorted(df_f['TIPO_MATERIAL'].unique().tolist())
        except Exception as e: 
            return []

    # --- ABAS PERSISTENTES ---
    tab_pericia, tab_atividades, tab_soberania, tab_raiox, tab_acervo_cir, tab_dash_cir = st.tabs([
        "📸 1. Perícia de Gabaritos", "✍️ 2. Atividades & Projetos", "🏛️ 3. Hub de Soberania", 
        "📊 4. Raio-X Pedagógico", "📂 5. Acervo de Evidências", "📈 6. Dashboard"
    ])

# --- ABA 1: PERÍCIA DE GABARITOS (VERSÃO V46.0 - TURBO + REGISTRO DE FALTA) ---
    with tab_pericia:
        c1, c2, c3 = st.columns([1, 1, 1.5])
        t_sel = c1.selectbox("👥 Turma:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"t_p_{v}")
        tr_sel = c2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_p_{v}")
        opcoes_p = filtrar_ativos_cir_v64(t_sel, tr_sel, apenas_provas=True)
        at_sel = c3.selectbox("📋 Selecione a Avaliação:", [""] + opcoes_p, key=f"at_p_{v}")

        if not t_sel or not at_sel:
            st.info("💡 Selecione a Turma e a Avaliação para iniciar o fluxo de correção em massa.")
        else:
            # 1. CARREGAMENTO DE GABARITO MESTRE
            dados_at = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel].iloc[0]
            txt_at = str(dados_at['CONTEUDO'])
            val_tag = ai.extrair_tag(txt_at, "VALOR")
            v_total_at = util.sosa_to_float(val_tag) if val_tag else 10.0

            def extrair_gab_v64(texto, is_pei=False):
                tag = "GABARITO_PEI" if is_pei else "GABARITO_TEXTO"
                raw = ai.extrair_tag(texto, tag) or ai.extrair_tag(texto, "GABARITO")
                if not raw: return []
                matches = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", raw.upper())
                mapa = {int(num): letra for num, letra in matches}
                return [mapa[n] for n in sorted(mapa.keys())]

            gab_reg = extrair_gab_v64(txt_at, False)
            gab_pei = extrair_gab_v64(txt_at, True) or gab_reg

            # 2. FILTRAGEM DE PENDENTES (AUTO-AVANÇO)
            escaneados = df_diagnosticos[df_diagnosticos['ID_AVALIACAO'] == at_sel]['ID_ALUNO'].astype(str).tolist()
            pendentes = df_alunos[(df_alunos['TURMA'] == t_sel) & (~df_alunos['ID'].astype(str).isin(escaneados))].sort_values(by="NOME_ALUNO")

            if pendentes.empty:
                st.success("🏆 SOBERANIA ALCANÇADA: Todos os alunos desta turma foram corrigidos!")
                if st.button("🔄 REVISAR HUB DE AUDITORIA"): st.rerun()
            else:
                # SELECIONA O PRIMEIRO DA FILA
                al_info = pendentes.iloc[0]
                al_sel = al_info['NOME_ALUNO']
                id_aluno_atual = al_info['ID']
                is_pei_aluno = str(al_info['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"]
                
                st.markdown(f"### 📸 Corrigindo agora: **{al_sel}**")
                c_p1, c_p2 = st.columns([2, 1])
                with c_p1: st.caption(f"Fila de Espera: {len(pendentes)} alunos restantes.")
                with c_p2: st.info("♿ PEI" if is_pei_aluno else "📝 REGULAR")

                # --- ÁREA DE CAPTURA E BOTÃO DE FALTA ---
                col_cam, col_falta = st.columns([2, 1])
                img = col_cam.camera_input(f"Gabarito de {al_sel}", key=f"cam_{id_aluno_atual}")
                
                with col_falta:
                    st.write("---")
                    st.markdown("**O aluno faltou?**")
                    if st.button("❌ REGISTRAR FALTA", use_container_width=True, help="Remove o aluno da fila e marca nota 0,00"):
                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                            datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, at_sel, 
                            "FALTOU", "0,00", "N/A"
                        ])
                        st.warning(f"Falta de {al_sel} registrada."); time.sleep(0.5); st.rerun()

                if img and "current_scan_res" not in st.session_state:
                    with st.spinner("Perito Sosa analisando marcações..."):
                        res_json = ai.analisar_gabarito_vision(img.getvalue())
                        gab_alvo = gab_pei if is_pei_aluno else gab_reg
                        qtd_q = len(gab_alvo)
                        # Normaliza a resposta da IA garantindo o tamanho correto do gabarito
                        st.session_state.current_scan_res = [res_json.get(f"{i+1:02d}", res_json.get(str(i+1), "?")) for i in range(qtd_q)]
                        st.session_state.current_scan_img = img.getvalue()
                        st.rerun()

                # 4. MESA DE PERÍCIA IMEDIATA
                if "current_scan_res" in st.session_state:
                    gab_alvo = gab_pei if is_pei_aluno else gab_reg
                    res_lidas = st.session_state.current_scan_res
                    
                    st.markdown("---")
                    col_res1, col_res2 = st.columns([1.5, 1])
                    
                    with col_res1:
                        st.subheader("⚖️ Mesa de Perícia")
                        dados_pericia = []
                        for i, lido in enumerate(res_lidas):
                            if i < len(gab_alvo): # Trava de segurança
                                certo = gab_alvo[i]
                                if lido == certo: status = "✅ ACERTO"
                                elif lido == "X": status = "🚫 DUPLA"
                                elif lido == "?": status = "⚪ VAZIA"
                                else: status = f"❌ (Era {certo})"
                                dados_pericia.append({"Q": f"{i+1:02d}", "Lido": lido, "Status": status})
                        
                        df_mesa = st.data_editor(pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                            column_config={"Lido": st.column_config.SelectboxColumn("Ajustar", options=["A", "B", "C", "D", "E", "X", "?"], required=True)},
                            key=f"ed_turbo_{id_aluno_atual}")
                    
                    with col_res2:
                        st.subheader("📊 Resultado")
                        novas_res = df_mesa["Lido"].tolist()
                        acertos = sum(1 for i, r in enumerate(novas_res) if i < len(gab_alvo) and r == gab_alvo[i])
                        nota_f = (acertos / len(gab_alvo)) * v_total_at if len(gab_alvo) > 0 else 0
                        
                        st.metric("Nota Final", f"{nota_f:.2f}", delta=f"{acertos}/{len(gab_alvo)} acertos")
                        
                        if st.button("💾 SALVAR E PRÓXIMO ALUNO ➔", type="primary", use_container_width=True):
                            with st.spinner("Arquivando evidência..."):
                                link_pasta = db.subir_e_converter_para_google_docs(st.session_state.current_scan_img, al_sel.replace(" ","_"), trimestre=tr_sel, categoria=t_sel, semana=at_sel, modo="SCANNER")
                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                    datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, at_sel, 
                                    ";".join(novas_res), util.sosa_to_str(nota_f), link_pasta
                                ])
                                del st.session_state.current_scan_res
                                del st.session_state.current_scan_img
                                st.success(f"✅ {al_sel} salvo!"); time.sleep(0.5); st.rerun()

                    if st.button("🗑️ DESCARTAR E REPETIR FOTO"):
                        del st.session_state.current_scan_res
                        del st.session_state.current_scan_img
                        st.rerun()

# --- ABA 2: ATIVIDADES & PROJETOS (V66.0 - SOBERANIA DE NOTAS E MÉRITO) ---
    with tab_atividades:
        st.subheader("✍️ Gestão de Notas de Projetos e Atividades")
        
        c_f1, c_f2 = st.columns(2)
        t_sel_a = c_f1.selectbox("👥 Selecione a Turma:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"t_a_v66_{v}")
        tr_sel_a = c_f2.selectbox("📅 Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_a_v66_{v}")

        # Busca ativos que não são provas (Projetos, Fixação, etc)
        opcoes_a = filtrar_ativos_cir_v64(t_sel_a, tr_sel_a, apenas_provas=False)
        at_sel_a = st.selectbox("📋 Selecione o Trabalho ou Atividade:", [""] + opcoes_a, key=f"at_a_sel_v66_{v}")

        if not t_sel_a or not at_sel_a:
            st.info("💡 Selecione a Turma e o Material para abrir a Mesa de Lançamento de Notas.")
        else:
            # 1. LEITURA E DNA DO MATERIAL
            dados_at = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_a].iloc[0]
            txt_at = str(dados_at['CONTEUDO'])
            
            # Tenta extrair o valor sugerido no material, senão assume 2.0 como padrão
            val_sugerido = ai.extrair_tag(txt_at, "VALOR")
            v_max_padrao = util.sosa_to_float(val_sugerido) if val_sugerido else 2.0

            with st.container(border=True):
                c_m1, c_m2 = st.columns([2, 1])
                c_m1.warning(f"📝 **ATIVIDADE EM FOCO:** {at_sel_a}")
                v_max_ativ = c_m2.number_input("💎 Valor Máximo desta Atividade:", 0.0, 10.0, v_max_padrao, step=0.5, key=f"v_max_{v}")

            with st.expander("👁️ REVISAR ROTEIRO E CRITÉRIOS (RUBRICA)"):
                c_v1, c_v2 = st.columns(2)
                with c_v1:
                    st.markdown("**👨‍🏫 Guia do Professor:**")
                    st.write(ai.extrair_tag(txt_at, "PROFESSOR"))
                with c_v2:
                    st.markdown("**📝 Roteiro do Aluno:**")
                    st.write(ai.extrair_tag(txt_at, "ALUNO"))

            # 2. MESA DE LANÇAMENTO DE NOTAS (AUTONOMIA TOTAL)
            st.divider()
            st.subheader(f"⭐ Mesa de Notas: {at_sel_a}")
            st.caption(f"As notas lançadas abaixo (até {v_max_ativ}) serão integradas ao bônus do aluno no boletim.")
            
            alunos_a = df_alunos[df_alunos['TURMA'] == t_sel_a].sort_values(by="NOME_ALUNO")
            
            # Busca se já existem notas lançadas para este material no Diário de Bordo
            notas_existentes = {}
            if not df_diario.empty:
                # Filtra registros que contenham o nome deste material nas observações
                df_filtro_mat = df_diario[df_diario['OBSERVACOES'].str.contains(at_sel_a, na=False)]
                for _, row_d in df_filtro_mat.iterrows():
                    notas_existentes[db.limpar_id(row_d['ID_ALUNO'])] = util.sosa_to_float(row_d.get('BONUS', 0))

            dados_notas_projeto = []
            for _, alu in alunos_a.iterrows():
                id_a = db.limpar_id(alu['ID'])
                nota_atual = notas_existentes.get(id_a, 0.0)
                
                dados_notas_projeto.append({
                    "ID": id_a, 
                    "Estudante": alu['NOME_ALUNO'], 
                    "Nota Alcançada": nota_atual,
                    "Status": "✅ Lançado" if nota_atual > 0 else "⏳ Pendente"
                })
            
            df_notas_ed = st.data_editor(
                pd.DataFrame(dados_notas_projeto),
                hide_index=True, use_container_width=True,
                column_config={
                    "ID": None,
                    "Estudante": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                    "Nota Alcançada": st.column_config.NumberColumn(f"Nota (0 a {v_max_ativ})", min_value=0.0, max_value=v_max_ativ, step=0.1, format="%.1f"),
                    "Status": st.column_config.TextColumn("Status", width="small", disabled=True)
                },
                key=f"ed_notas_proj_{at_sel_a.replace(' ','_')}"
            )

            # 3. SALVAMENTO NO DIÁRIO DE BORDO (INTEGRAÇÃO COM PAINEL DE NOTAS)
            if st.button("💾 CONSOLIDAR NOTAS NO BOLETIM ANUAL", type="primary", use_container_width=True):
                with st.status("Sincronizando Notas de Mérito com o Ecossistema...") as status:
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    lista_lote_diario = []
                    
                    for _, r in df_notas_ed.iterrows():
                        # Salvamos no Diário de Bordo para que o Painel de Notas some como Bônus
                        # A tag 'PROJETO' ajuda a identificar a origem da nota
                        lista_lote_diario.append([
                            data_hoje, 
                            r['ID'], 
                            r['Estudante'], 
                            t_sel_a, 
                            "TRUE", # Visto como True pois houve entrega
                            "PROJETO/ATIVIDADE", 
                            f"[{at_sel_a}] Nota atribuída na CIR.", 
                            util.sosa_to_str(r['Nota Alcançada'])
                        ])
                    
                    if lista_lote_diario:
                        # Limpa registros antigos deste material para esta turma para evitar duplicidade de bônus
                        db.limpar_diario_data_turma(data_hoje, t_sel_a) # Opcional: pode-se criar uma função específica para limpar por material
                        
                        db.salvar_lote("DB_DIARIO_BORDO", lista_lote_diario)
                        status.update(label=f"✅ Notas de {at_sel_a} integradas com sucesso!", state="complete")
                        st.balloons()
                        time.sleep(1)
                        st.rerun()

# --- ABA 3: HUB DE SOBERANIA (V67.0 - AUDITORIA E NOTAS EXTERNAS) ---
    with tab_soberania:
        st.subheader("🏛️ Hub de Soberania: Autoridade do Professor")
        st.markdown("---")

        c_h1, c_h2 = st.columns([1, 1])
        t_sel_h = c_h1.selectbox("👥 Selecione a Turma:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"t_h_v67_{v}")
        tr_sel_h = c_h2.selectbox("📅 Trimestre de Referência:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_h_v67_{v}")

        if not t_sel_h:
            st.info("💡 Selecione uma turma para exercer a soberania sobre os resultados.")
        else:
            sub_auditoria, sub_externas = st.tabs(["⚖️ Auditoria de Gabaritos", "🌍 Notas Externas (SAEB/Governo)"])

            # --- SUB-ABA 1: AUDITORIA DE GABARITOS ---
            with sub_auditoria:
                st.markdown("#### 🔍 Revisão de Leituras do Scanner")
                # Busca todos os gabaritos escaneados desta turma
                gabaritos_turma = df_diagnosticos[df_diagnosticos['TURMA'] == t_sel_h]
                
                if gabaritos_turma.empty:
                    st.warning("📭 Nenhum gabarito escaneado encontrado para esta turma.")
                else:
                    # Filtra por avaliação específica para não misturar
                    av_alvo_h = st.selectbox("Selecione a Avaliação para Auditoria:", gabaritos_turma['ID_AVALIACAO'].unique())
                    dados_av_h = gabaritos_turma[gabaritos_turma['ID_AVALIACAO'] == av_alvo_h]

                    st.caption("Ajuste as notas abaixo se houver erro de leitura ou necessidade pedagógica.")
                    
                    df_auditoria_ed = st.data_editor(
                        dados_av_h[['ID_ALUNO', 'NOME_ALUNO', 'RESPOSTAS_ALUNO', 'NOTA_CALCULADA', 'LINK_FOTO_DRIVE']],
                        column_config={
                            "ID_ALUNO": None,
                            "NOME_ALUNO": st.column_config.TextColumn("Estudante", disabled=True),
                            "RESPOSTAS_ALUNO": st.column_config.TextColumn("Leitura Scanner", disabled=True),
                            "NOTA_CALCULADA": st.column_config.NumberColumn("Nota Final (Soberana)", min_value=0.0, max_value=10.0, step=0.1, format="%.1f"),
                            "LINK_FOTO_DRIVE": st.column_config.LinkColumn("🔗 Ver Prova")
                        },
                        hide_index=True, use_container_width=True, key=f"ed_soberania_{v}"
                    )

                    if st.button("⚖️ HOMOLOGAR NOTAS AUDITADAS", use_container_width=True, type="primary"):
                        with st.spinner("Atualizando registros oficiais..."):
                            # Aqui o sistema pega a nota editada e envia para o DB_NOTAS
                            lista_homologacao = []
                            for _, r in df_auditoria_ed.iterrows():
                                lista_homologacao.append([
                                    r['ID_ALUNO'], r['NOME_ALUNO'], t_sel_h, tr_sel_h, 
                                    "0,0", "0,0", util.sosa_to_str(r['NOTA_CALCULADA']), "0,0", util.sosa_to_str(r['NOTA_CALCULADA'])
                                ])
                            
                            if db.salvar_lote("DB_NOTAS", lista_homologacao):
                                st.success("✅ Notas auditadas e enviadas ao Boletim!")
                                st.balloons()

            # --- SUB-ABA 2: NOTAS EXTERNAS ---
            with sub_externas:
                st.markdown("#### 🌍 Lançamento de Indicadores Externos (SAEB / Município)")
                st.caption("Use este espaço para integrar resultados de provas do Governo ou da Prefeitura.")
                
                alunos_h = df_alunos[df_alunos['TURMA'] == t_sel_h].sort_values(by="NOME_ALUNO")
                
                dados_externos = []
                for _, alu in alunos_h.iterrows():
                    dados_externos.append({
                        "ID": alu['ID'],
                        "Estudante": alu['NOME_ALUNO'],
                        "Nota SAEB/Externa": 0.0,
                        "Observação": ""
                    })
                
                df_ext_ed = st.data_editor(
                    pd.DataFrame(dados_externos),
                    column_config={
                        "ID": None,
                        "Nota SAEB/Externa": st.column_config.NumberColumn("Nota (0-10)", min_value=0.0, max_value=10.0, step=0.1),
                        "Observação": st.column_config.TextColumn("Origem (Ex: SAEB 2026)")
                    },
                    hide_index=True, use_container_width=True, key=f"ed_externas_{v}"
                )

                if st.button("💾 INTEGRAR NOTAS EXTERNAS AO PERFIL", use_container_width=True):
                    with st.spinner("Arquivando indicadores externos..."):
                        # Salva na aba de Relatórios para consulta no Raio-X e Conselho
                        for _, r in df_ext_ed.iterrows():
                            if r['Nota SAEB/Externa'] > 0:
                                db.salvar_no_banco("DB_RELATORIOS", [
                                    datetime.now().strftime("%d/%m/%Y"), 
                                    r['ID'], r['Estudante'], 
                                    "NOTA_EXTERNA", 
                                    f"Nota: {r['Nota SAEB/Externa']} | Origem: {r['Observação']}"
                                ])
                        st.success("✅ Indicadores externos integrados ao histórico dos alunos!")

    # --- ABA 4: RAIO-X PEDAGÓGICO (V72.1 - FIX UNDEFINED VARIABLE & ROBUSTEZ) ---
    with tab_raiox:
        st.subheader("📊 Raio-X Pedagógico: Diagnóstico Individual de Lacunas")
        st.markdown("---")

        c1, c2, c3 = st.columns([1, 1, 1.5])
        t_sel_r = c1.selectbox("👥 Selecione a Turma:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"t_r_v72_{v}")
        tr_sel_r = c2.selectbox("📅 Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_r_v72_{v}")
        
        opcoes_r = filtrar_ativos_cir_v64(t_sel_r, tr_sel_r, apenas_provas=True)
        at_sel_r = c3.selectbox("📋 Selecione a Avaliação para Raio-X:", [""] + opcoes_r, key=f"at_r_v72_{v}")

        if not t_sel_r or not at_sel_r:
            st.info("💡 Selecione a Turma e a Avaliação para carregar a Perícia Pedagógica.")
        else:
            # 1. RECUPERAÇÃO DE METADADOS E GABARITOS
            prova_query = df_aulas[df_aulas['TIPO_MATERIAL'].str.strip() == at_sel_r.strip()]
            
            if not prova_query.empty:
                dados_prova = prova_query.iloc[0]
                txt_prova = str(dados_prova['CONTEUDO'])
                grade_pericia = ai.extrair_tag(txt_prova, "GRADE_DE_CORRECAO")
                
                def extrair_gab_v72(texto, tag_alvo="GABARITO_TEXTO"):
                    raw = ai.extrair_tag(texto, tag_alvo) or ai.extrair_tag(texto, "GABARITO")
                    matches = re.findall(r"(\d+)\s*[\-\.\:]\s*([A-E])", raw.upper())
                    if matches: return {int(num): letra for num, letra in matches}
                    letras = re.findall(r"\b[A-E]\b", raw.upper())
                    return {i+1: letra for i, letra in enumerate(letras)}

                gab_reg_map = extrair_gab_v72(txt_prova, "GABARITO_TEXTO")
                gab_pei_map = extrair_gab_v72(txt_prova, "GABARITO_PEI")

                # 2. CRUZAMENTO DE DADOS (RESPOSTAS + PERFIL DO ALUNO)
                respostas_brutas = df_diagnosticos[
                    (df_diagnosticos['TURMA'].str.strip() == t_sel_r.strip()) & 
                    (df_diagnosticos['ID_AVALIACAO'].str.strip() == at_sel_r.strip())
                ].copy()

                if respostas_brutas.empty:
                    st.warning("⚠️ Nenhuma resposta de aluno encontrada para esta avaliação.")
                else:
                    # Normalização de IDs para o merge
                    df_alunos_min = df_alunos[['ID', 'NECESSIDADES']].copy()
                    df_alunos_min['ID'] = df_alunos_min['ID'].apply(db.limpar_id)
                    respostas_brutas['ID_ALUNO_L'] = respostas_brutas['ID_ALUNO'].apply(db.limpar_id)
                    
                    df_analise = pd.merge(respostas_brutas, df_alunos_min, left_on='ID_ALUNO_L', right_on='ID', how='left')
                    df_analise['IS_PEI'] = df_analise['NECESSIDADES'].apply(lambda x: str(x).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"])

                    # --- SELETOR DE LENTE PEDAGÓGICA ---
                    st.markdown("### 🎯 1. Análise de Performance por Item")
                    perfil_visao = st.radio("Filtrar Visão Macro:", ["📝 Alunos Regulares", "♿ Alunos PEI"], horizontal=True, key=f"perfil_v_{v}")
                    
                    is_pei_view = "PEI" in perfil_visao
                    df_filtrado = df_analise[df_analise['IS_PEI'] == is_pei_view]
                    gab_ativo = gab_pei_map if is_pei_view else gab_reg_map

                    if df_filtrado.empty:
                        st.info(f"📭 Não há dados de {perfil_visao} para esta avaliação.")
                    else:
                        # --- CÁLCULO DE ESTATÍSTICAS POR ITEM (FIX UNDEFINED VARIABLE) ---
                        num_q_total = len(gab_ativo)
                        stats_list = []
                        
                        # Vacina Anti-Erro: Garante que a coluna seja tratada como string e lida corretamente
                        matriz_respostas = [str(r).split(';') for r in df_filtrado['RESPOSTAS_ALUNO']]

                        for i in range(1, num_q_total + 1):
                            correta = gab_ativo.get(i, "?")
                            votos = [res[i-1] if len(res) >= i else "?" for res in matriz_respostas]
                            acertos = votos.count(correta)
                            perc = (acertos / len(votos)) * 100 if len(votos) > 0 else 0
                            erradas = [v for v in votos if v != correta and v in ["A", "B", "C", "D", "E"]]
                            distrator = max(set(erradas), key=erradas.count) if erradas else "Nenhum"
                            stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": correta, "Distrator Crítico": distrator})

                        df_stats = pd.DataFrame(stats_list)
                        col_graf, col_item = st.columns([1.2, 1])
                        
                        with col_graf:
                            fig = px.bar(df_stats, x="Questão", y="Acerto %", text_auto='.0f', 
                                    color="Acerto %", color_continuous_scale="RdYlGn",
                                    title=f"Desempenho: {perfil_visao}")
                            fig.update_layout(yaxis_range=[0, 110], height=350)
                            st.plotly_chart(fig, use_container_width=True)

                        with col_item:
                            with st.container(border=True):
                                st.markdown("**🔬 Perícia do Item**")
                                q_sel = st.selectbox("Analisar questão:", df_stats["Questão"].tolist(), key=f"q_sel_v72_{is_pei_view}")
                                info_q = df_stats[df_stats["Questão"] == q_sel].iloc[0]
                                idx_num = int(q_sel[1:])
                                st.write(f"**Gabarito:** :green[{info_q['Gabarito']}] | **Média:** {info_q['Acerto %']:.1f}%")
                                if info_q['Distrator Crítico'] != "Nenhum": st.error(f"**Distrator Crítico:** {info_q['Distrator Crítico']}")
                                
                                try:
                                    padrao = rf"(?si)QUESTÃO\s*0?{idx_num}\b.*?(?=QUESTÃO\s*0?{idx_num+1}\b|$)"
                                    match = re.search(padrao, grade_pericia)
                                    if match: st.info(match.group(0).strip())
                                except: st.caption("Detalhes da grade não localizados.")

                    # --- PARTE B: DIAGNÓSTICO INDIVIDUAL (MICRO) ---
                    st.markdown("---")
                    st.markdown("#### 👤 2. Perícia Individual: Lacunas por Estudante")
                    
                    alunos_turma = df_alunos[df_alunos['TURMA'] == t_sel_r].sort_values(by="NOME_ALUNO")
                    dados_indiv = []

                    for _, alu in alunos_turma.iterrows():
                        id_a = db.limpar_id(alu['ID'])
                        is_pei_alu = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"]
                        reg_aluno = df_analise[df_analise['ID_ALUNO_L'] == id_a]
                        
                        if reg_aluno.empty:
                            dados_indiv.append({"Estudante": alu['NOME_ALUNO'], "Perfil": "🔴 Ausente", "Nota": 0.0, "Lacunas Cognitivas": "N/A"})
                        else:
                            nota_alu = util.sosa_to_float(reg_aluno.iloc[0]['NOTA_CALCULADA'])
                            resp_lista = str(reg_aluno.iloc[0]['RESPOSTAS_ALUNO']).split(';')
                            gab_alvo_alu = gab_pei_map if is_pei_alu else gab_reg_map
                            
                            erros_hab = []
                            for i, r in enumerate(resp_lista):
                                q_n = i + 1
                                if r != gab_alvo_alu.get(q_n):
                                    match_h = re.search(rf"QUESTÃO\s*0?{q_n}\b.*?:(.*?)(?=\n|JUSTIFICATIVA|PERÍCIA|$)", grade_pericia, re.IGNORECASE)
                                    erros_hab.append(match_h.group(1).strip().replace("[","").replace("]","") if match_h else f"Q{q_n}")
                            
                            dados_indiv.append({
                                "Estudante": alu['NOME_ALUNO'],
                                "Perfil": "♿ PEI" if is_pei_alu else "📝 Regular",
                                "Nota": nota_alu,
                                "Lacunas Cognitivas": " | ".join(list(set(erros_hab))) if erros_hab else "✅ Domínio Total"
                            })

                    df_indiv = pd.DataFrame(dados_indiv)
                    st.dataframe(
                        df_indiv.style.format({"Nota": "{:.1f}"}).applymap(lambda v: 'color: #FF4B4B; font-weight: bold' if isinstance(v, float) and v < 6.0 else '', subset=['Nota']),
                        use_container_width=True, hide_index=True,
                        column_config={"Lacunas Cognitivas": st.column_config.TextColumn("Lacunas Cognitivas (Habilidades a Reforçar)", width="large")}
                    )

# --- ABA 5: ACERVO DE EVIDÊNCIAS (V71.0 - CUSTÓDIA COM FILTROS INTELIGENTES) ---
    with tab_acervo_cir:
        st.subheader("📂 Cofre Digital de Evidências: Localização Rápida")
        st.markdown("---")

        if df_diagnosticos.empty:
            st.info("📭 Nenhuma evidência arquivada ainda.")
        else:
            # 1. BARRA DE FILTROS DE ELITE
            with st.container(border=True):
                c_f1, c_f2, c_f3 = st.columns([1, 1, 1.5])
                
                # Filtro 1: Turma
                lista_turmas_ev = ["Todas"] + sorted(df_diagnosticos['TURMA'].unique().tolist())
                f_turma = c_f1.selectbox("👥 Filtrar por Turma:", lista_turmas_ev, key=f"f_t_ev_{v}")
                
                # Filtro 2: Trimestre (Busca por texto no ID da Avaliação)
                f_trim = c_f2.selectbox("📅 Filtrar por Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key=f"f_tr_ev_{v}")
                
                # Preparação da base filtrada para o Filtro 3
                df_ev_filtrado = df_diagnosticos.copy()
                if f_turma != "Todas":
                    df_ev_filtrado = df_ev_filtrado[df_ev_filtrado['TURMA'] == f_turma]
                if f_trim != "Todos":
                    df_ev_filtrado = df_ev_filtrado[df_ev_filtrado['ID_AVALIACAO'].str.contains(f_trim, na=False)]
                
                # Filtro 3: Material (Dinâmico com base nos filtros anteriores)
                lista_mats_ev = ["Todos"] + sorted(df_ev_filtrado['ID_AVALIACAO'].unique().tolist())
                f_mat = c_f3.selectbox("📋 Selecionar Material Específico:", lista_mats_ev, key=f"f_m_ev_{v}")
                
                if f_mat != "Todos":
                    df_ev_filtrado = df_ev_filtrado[df_ev_filtrado['ID_AVALIACAO'] == f_mat]

            # 2. EXIBIÇÃO DOS RESULTADOS
            st.markdown(f"**🔍 Registros Localizados:** {len(df_ev_filtrado)}")
            
            if df_ev_filtrado.empty:
                st.warning("⚠️ Nenhum registro encontrado com os filtros selecionados.")
            else:
                # Ordena pelos mais recentes
                df_ev_exibicao = df_ev_filtrado.iloc[::-1]
                
                # Tabela de Custódia com Link Direto
                st.dataframe(
                    df_ev_exibicao[['DATA', 'NOME_ALUNO', 'TURMA', 'ID_AVALIACAO', 'NOTA_CALCULADA', 'LINK_FOTO_DRIVE']],
                    column_config={
                        "DATA": st.column_config.TextColumn("Data", width="small"),
                        "NOME_ALUNO": st.column_config.TextColumn("Estudante", width="medium"),
                        "TURMA": st.column_config.TextColumn("Turma", width="small"),
                        "ID_AVALIACAO": st.column_config.TextColumn("Avaliação", width="medium"),
                        "NOTA_CALCULADA": st.column_config.NumberColumn("Nota", format="%.1f", width="small"),
                        "LINK_FOTO_DRIVE": st.column_config.LinkColumn("🔗 Ver Evidência (Drive)", width="medium")
                    },
                    use_container_width=True,
                    hide_index=True
                )

                # 3. RESUMO DE PERFORMANCE DO FILTRO
                with st.expander("📊 Resumo Rápido desta Seleção"):
                    c_r1, c_r2, c_r3 = st.columns(3)
                    media_sel = df_ev_filtrado['NOTA_CALCULADA'].apply(util.sosa_to_float).mean()
                    c_r1.metric("Média do Grupo", f"{media_sel:.2f}")
                    
                    acima_media = len(df_ev_filtrado[df_ev_filtrado['NOTA_CALCULADA'].apply(util.sosa_to_float) >= 6.0])
                    c_r2.metric("Alunos com Sucesso", acima_media)
                    
                    abaixo_media = len(df_ev_filtrado) - acima_media
                    c_r3.metric("Alunos em Alerta", abaixo_media, delta_color="inverse")

    # --- ABA 6: DASHBOARD (V73.0 - TORRE DE COMANDO COM FILTRO DE TURMA) ---
    with tab_dash_cir:
        st.subheader("📈 Torre de Comando: Inteligência de Resultados 360°")
        st.markdown("---")

        if df_diagnosticos.empty:
            st.info("📭 Aguardando dados de gabaritos para gerar a inteligência analítica.")
        else:
            # 1. PREPARAÇÃO E FUSÃO DE DADOS (DATA FUSION)
            df_dash = df_diagnosticos.copy()
            df_dash['NOTA_NUM'] = df_dash['NOTA_CALCULADA'].apply(util.sosa_to_float)
            
            # Cruzamento com a base de alunos para identificar Perfil (Regular/PEI)
            df_alunos_min = df_alunos[['ID', 'NECESSIDADES']].copy()
            df_alunos_min['ID'] = df_alunos_min['ID'].apply(db.limpar_id)
            df_dash['ID_ALUNO_L'] = df_dash['ID_ALUNO'].apply(db.limpar_id)
            
            df_final_base = pd.merge(df_dash, df_alunos_min, left_on='ID_ALUNO_L', right_on='ID', how='left')
            df_final_base['PERFIL'] = df_final_base['NECESSIDADES'].apply(
                lambda x: "♿ PEI" if str(x).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"] else "📝 REGULAR"
            )

            # --- SELETOR DE SOBERANIA (FILTRO DE TURMA) ---
            with st.container(border=True):
                lista_turmas_dash = ["Todas as Turmas"] + sorted(df_final_base['TURMA'].unique().tolist())
                turma_sel_dash = st.selectbox("🎯 Selecione a Turma para Análise de Performance:", lista_turmas_dash, key=f"dash_t_filter_{v}")

            # Aplicação do Filtro
            if turma_sel_dash != "Todas as Turmas":
                df_final = df_final_base[df_final_base['TURMA'] == turma_sel_dash].copy()
            else:
                df_final = df_final_base.copy()

            if df_final.empty:
                st.warning(f"⚠️ Não há dados processados para a turma {turma_sel_dash}.")
            else:
                # 2. KPIs DE TOPO (MÉTRICAS AJUSTADAS AO FILTRO)
                c1, c2, c3, c4 = st.columns(4)
                
                media_geral = df_final['NOTA_NUM'].mean()
                c1.metric("Média do Grupo", f"{media_geral:.2f}", 
                        delta=f"{media_geral - 6.0:.1f}", 
                        delta_color="normal" if media_geral >= 6 else "inverse")
                
                total_correcoes = len(df_final)
                c2.metric("Total de Correções", total_correcoes)
                
                taxa_sucesso = (len(df_final[df_final['NOTA_NUM'] >= 6.0]) / total_correcoes) * 100 if total_correcoes > 0 else 0
                c3.metric("Taxa de Sucesso", f"{taxa_sucesso:.1f}%")
                
                media_pei = df_final[df_final['PERFIL'] == "♿ PEI"]['NOTA_NUM'].mean()
                c4.metric("Média PEI", f"{media_pei:.2f}" if not pd.isna(media_pei) else "0.00")

                st.markdown("---")

                # 3. ANÁLISE GRÁFICA (VISÃO SEGREGADA)
                col_esq, col_dir = st.columns(2)

                with col_esq:
                    st.markdown(f"**⚖️ Índice de Equidade: {turma_sel_dash}**")
                    # Gráfico de Box Plot para ver a dispersão das notas por perfil
                    fig_perfil = px.box(df_final, x="PERFIL", y="NOTA_NUM", color="PERFIL",
                                    points="all", title="Distribuição de Notas: Regular vs PEI",
                                    color_discrete_map={"📝 REGULAR": BRAND_BLUE, "♿ PEI": "#FF4B4B"})
                    fig_perfil.update_layout(showlegend=False, yaxis_range=[0, 11], height=400)
                    st.plotly_chart(fig_perfil, use_container_width=True)

                with col_dir:
                    st.markdown(f"**📊 Performance por Ativo: {turma_sel_dash}**")
                    # Média de cada prova aplicada para o grupo selecionado
                    df_ativos = df_final.groupby('ID_AVALIACAO')['NOTA_NUM'].mean().reset_index().sort_values(by='NOTA_NUM')
                    fig_ativos = px.bar(df_ativos, x="NOTA_NUM", y="ID_AVALIACAO", orientation='h',
                                    title="Média de Acertos por Avaliação",
                                    text_auto='.1f', color="NOTA_NUM", color_continuous_scale="RdYlGn")
                    fig_ativos.update_layout(xaxis_range=[0, 11], height=400)
                    st.plotly_chart(fig_ativos, use_container_width=True)

                # 4. MAPA DE CALOR DE HABILIDADES (LACUNAS BNCC ESPECÍFICAS)
                st.markdown("---")
                st.markdown(f"**🔥 Mapa de Calor: Domínio de Habilidades BNCC ({turma_sel_dash})**")
                
                df_habilidades = []
                # Itera apenas sobre as avaliações que aparecem no filtro atual
                for avaliacao in df_final['ID_AVALIACAO'].unique():
                    # Busca o conteúdo da prova no banco de materiais
                    prova_query = df_aulas[df_aulas['TIPO_MATERIAL'] == avaliacao]
                    if not prova_query.empty:
                        prova_txt = prova_query['CONTEUDO'].iloc[0]
                        grade = ai.extrair_tag(prova_txt, "GRADE_DE_CORRECAO")
                        
                        # Busca códigos BNCC (Ex: EF06MA01)
                        codigos = re.findall(r"EF\d{2}MA\d{2}", grade)
                        for cod in set(codigos):
                            # Calcula a média de acerto do grupo filtrado para esta prova
                            media_hab = df_final[df_final['ID_AVALIACAO'] == avaliacao]['NOTA_NUM'].mean()
                            df_habilidades.append({"Habilidade": cod, "Domínio %": media_hab * 10, "Ativo": avaliacao})

                if df_habilidades:
                    df_hab_plot = pd.DataFrame(df_habilidades)
                    fig_hab = px.scatter(df_hab_plot, x="Habilidade", y="Domínio %", size="Domínio %", color="Domínio %",
                                        hover_name="Ativo", title="Nível de Domínio por Descritor",
                                        color_continuous_scale="RdYlGn", range_y=[0, 105])
                    st.plotly_chart(fig_hab, use_container_width=True)
                else:
                    st.info("Habilidades BNCC serão mapeadas conforme o senhor realizar as perícias no Raio-X.")

                # 5. ALERTAS DE INTERVENÇÃO (FOCO NA TURMA)
                st.markdown("---")
                st.markdown(f"#### 🚨 Alertas de Risco Pedagógico: {turma_sel_dash}")
                
                # Filtra alunos do grupo atual com média abaixo de 5.0
                df_alerta = df_final[df_final['NOTA_NUM'] < 5.0].groupby(['NOME_ALUNO', 'TURMA', 'PERFIL'])['NOTA_NUM'].count().reset_index()
                df_alerta.columns = ['Estudante', 'Turma', 'Perfil', 'Qtd. Avaliações Críticas']
                
                if not df_alerta.empty:
                    st.warning(f"Identificamos {len(df_alerta)} alunos em {turma_sel_dash} que necessitam de recomposição urgente.")
                    st.dataframe(df_alerta.sort_values(by='Qtd. Avaliações Críticas', ascending=False), 
                                use_container_width=True, hide_index=True)
                else:
                    st.success(f"Nenhum aluno da turma {turma_sel_dash} em zona de risco crítico no momento.")

# ==============================================================================
# MÓDULO: BIOGRAFIA DO ESTUDANTE (V35.0 - DOSSIÊ 360° PARA PAIS)
# ==============================================================================
elif menu == "👤 Biografia do Estudante":
    st.title("👤 Dossiê de Soberania do Estudante")
    st.markdown("---")

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia.")
    else:
        # 1. FILTROS DE ACESSO RÁPIDO
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1.5, 1])
            turma_b = c1.selectbox("Turma:", sorted(df_alunos['TURMA'].unique()), key="bio_t")
            lista_alunos = df_alunos[df_alunos['TURMA'] == turma_b].sort_values(by="NOME_ALUNO")
            aluno_b = c2.selectbox("Estudante:", lista_alunos['NOME_ALUNO'].tolist(), key="bio_a")
            trim_b = c3.selectbox("Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="bio_trim")

        # Captura dados básicos
        info_alu = lista_alunos[lista_alunos['NOME_ALUNO'] == aluno_b].iloc[0]
        id_alu = db.limpar_id(info_alu['ID'])
        is_pei = str(info_alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"]

        # --- CABEÇALHO DE STATUS ---
        c_h1, c_h2, c_h3 = st.columns([2, 1, 1])
        with c_h1:
            st.subheader(f"🎓 {aluno_b}")
            if is_pei: st.warning(f"♿ Perfil Inclusivo: {info_alu['NECESSIDADES']}")
        with c_h2:
            # Calculadora de Aprovação (Meta 18.0)
            if not df_notas.empty:
                n_alu = df_notas[df_notas['ID_ALUNO'].apply(db.limpar_id) == id_alu]
                soma_atual = n_alu['MEDIA_FINAL'].apply(util.sosa_to_float).sum()
                st.metric("Soma Anual", f"{soma_atual:.1f}", delta=f"{soma_atual - 18.0:.1f}", help="Meta para aprovação: 18.0 pontos")

        st.markdown("---")

        # --- SEÇÃO 1: VIDA ESCOLAR (VISTOS E ATITUDE) ---
        st.markdown("### 📊 1. Engajamento e Atitude (Diário de Bordo)")
        col_v1, col_v2 = st.columns([1.2, 1.8])

        with col_v1:
            if not df_diario.empty:
                d_alu = df_diario[df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu].copy()
                if not d_alu.empty:
                    total_aulas = len(d_alu)
                    vistos = len(d_alu[d_alu['VISTO_ATIVIDADE'].astype(str).upper() == "TRUE"])
                    perc_visto = (vistos / total_aulas) * 100
                    st.metric("Entrega de Atividades", f"{perc_visto:.0f}%", f"{vistos} vistos de {total_aulas} aulas")
                    st.progress(perc_visto / 100)
                else: st.info("Sem registros de vistos.")

        with col_v2:
            st.markdown("**🚩 Ocorrências e Observações:**")
            if not d_alu.empty:
                # Filtra tags importantes como "Dormiu", "Conversa", "Sem Material"
                tags_importantes = d_alu[d_alu['TAGS'] != ""]
                if not tags_importantes.empty:
                    for _, row in tags_importantes.tail(5).iterrows():
                        cor_tag = "🔴" if any(x in row['TAGS'].upper() for x in ["DORMIU", "CONVERSA", "MATERIAL"]) else "🟢"
                        st.caption(f"{cor_tag} **{row['DATA']}**: {row['TAGS']} - *{row['OBSERVACOES']}*")
                else: st.success("✅ Nenhuma ocorrência negativa registrada.")

        # --- SEÇÃO 2: DESEMPENHO E PROVAS (SCANNER) ---
        st.markdown("---")
        st.markdown("### 📝 2. Desempenho em Avaliações (Scanner)")
        
        if not df_diagnosticos.empty:
            diag_alu = df_diagnosticos[df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu].copy()
            if not diag_alu.empty:
                # Tabela simplificada para o pai ver
                st.dataframe(
                    diag_alu[['DATA', 'ID_AVALIACAO', 'NOTA_CALCULADA']].rename(columns={'ID_AVALIACAO': 'Prova', 'NOTA_CALCULADA': 'Nota'}),
                    use_container_width=True, hide_index=True
                )
            else: st.info("O aluno ainda não realizou provas escaneadas.")

        # --- SEÇÃO 3: RAIO-X DE DIFICULDADES (O QUE ESTUDAR?) ---
        st.markdown("---")
        with st.container(border=True):
            st.markdown("### 🔍 3. Raio-X de Dificuldades (O que estudar?)")
            st.caption("Este campo mostra as habilidades que o aluno errou no Scanner e precisa reforçar em casa.")
            
            if not diag_alu.empty:
                ultima_av = diag_alu.iloc[-1]
                prova_ref = df_aulas[df_aulas['TIPO_MATERIAL'].str.strip() == ultima_av['ID_AVALIACAO'].strip()]
                
                if not prova_ref.empty:
                    txt_p = str(prova_ref.iloc[0]['CONTEUDO'])
                    grade = ai.extrair_tag(txt_p, "GRADE_DE_CORRECAO")
                    tag_g = "GABARITO_PEI" if is_pei else "GABARITO_TEXTO"
                    gab_oficial = re.findall(r"\b[A-E]\b", (ai.extrair_tag(txt_p, tag_g) or ai.extrair_tag(txt_p, "GABARITO")).upper())
                    respostas = str(ultima_av['RESPOSTAS_ALUNO']).split(';')
                    
                    lacunas = []
                    for i, r in enumerate(respostas):
                        if i < len(gab_oficial) and r != gab_oficial[i] and r not in ["FALTOU", "X", "?"]:
                            q_n = i + 1
                            m_h = re.search(rf"QUESTÃO\s*0?{q_n}\b.*?:(.*?)(?=\n|JUSTIFICATIVA|PERÍCIA|$)", grade, re.IGNORECASE)
                            lacunas.append(m_h.group(1).strip().replace("[","").replace("]","") if m_h else f"Questão {q_n}")
                    
                    if lacunas:
                        for l in list(set(lacunas)):
                            st.error(f"❌ **Reforçar:** {l}")
                    else: st.success("✅ O aluno demonstrou domínio total na última avaliação.")
                else: st.caption("Grade de habilidades não localizada.")
            else: st.info("Aguardando primeira avaliação para gerar o Raio-X.")

        st.caption(f"Dossiê atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
