import io
import streamlit as st
import pandas as pd
import gspread
from datetime import date, datetime, timedelta, timezone
import random  # 🚨 VACINA DE IMPORTAÇÃO: Habilita geradores e embaralhadores psicométricos
import database as db
import ai_engine as ai
import utils as util
import time
import os
import plotly.express as px
import exporter
import re

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE (BRANDING EXCLUSIVO) ---
st.set_page_config(
    page_title="Ronaldo Gomes", 
    layout="wide", 
    page_icon="💻", # Ícone da aba atualizado para 💻
    initial_sidebar_state="expanded"
)

# --- SISTEMA DE BLINDAGEM E PERSISTÊNCIA (6 HORAS) ---
def check_password():
    """Gerencia o acesso com card Glassmorphism executivo e persistência de 6h."""
    
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "login_timestamp" not in st.session_state:
        st.session_state["login_timestamp"] = None

    # Verifica se a sessão de 6h ainda é válida
    if st.session_state["password_correct"]:
        tempo_decorrido = time.time() - st.session_state["login_timestamp"]
        if tempo_decorrido < 21600: # 6 horas
            return True
        else:
            st.session_state["password_correct"] = False
            st.warning("Sessão expirada. Por favor, entre novamente.")

    # INTERFACE DE LOGIN EXECUTIVA (Glassmorphism Bento Card)
    _, col_login, _ = st.columns([1, 2, 1]) 
    
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
            with col_l2:
                try: st.image("logo.png", width=140) 
                except: st.markdown("<h2 style='text-align: center;'>Ronaldo Gomes</h2>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align: center; margin-top: 5px; margin-bottom: 0px;'>🔐 Portal de Soberania</h3>", unsafe_allow_html=True)
            st.caption("Sistema de Alta Performance Pedagógica & Gestão 360°")
            st.markdown("---")
            
            st.pills("Perfil de Acesso:", ["👑 Prof. Ronaldo Gomes (Proprietário)"], default="👑 Prof. Ronaldo Gomes (Proprietário)", key="pills_login_profile")
            
            # FORMULÁRIO DE LOGIN
            with st.form("login_portal_form"):
                input_password = st.text_input("Chave de Acesso de Elite:", type="password", placeholder="Digite sua chave de segurança...")
                st.checkbox("Manter conectado por 6 horas", value=True, disabled=True)
                
                btn_entrar = st.form_submit_button("🚀 ENTRAR NO PAINEL", use_container_width=True, type="primary")
                
                if btn_entrar:
                    if input_password == "2496":
                        st.session_state["password_correct"] = True
                        st.session_state["login_timestamp"] = time.time()
                        st.toast("Acesso Autorizado! Carregando Soberania...", icon="✅")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("❌ Chave incorreta. Acesso negado.")
            
            st.caption("🛡️ SOSA Bridge V45.9 • Servidor Online • Criptografia Ativa • Itabuna/BA")
    
    return False

if not check_password():
    st.stop()



# --- MOTOR DE NAVEGAÇÃO ONE-CLICK (GLOBAL) ---
if "menu_atual" not in st.session_state:
    st.session_state.menu_atual = "📅 Planejamento (Ponto ID)"

def navegar_para(destino):
    st.session_state.menu_atual = destino
    st.rerun()

def atualizar_menu():
    st.session_state.menu_atual = st.session_state._menu_radio

# 🔬 FILTRO DE LEITURA GLOBAL (LATEX, TABELAS NATIVAS E IMAGENS V2026.MASTER)
def preparar_para_leitura(texto):
    if not texto or not isinstance(texto, str): return ""
    
    # Vacina de escape do Form Feed
    texto = texto.replace('\x0c', '\\f')
    
    # 🚨 AUTO-ENCAPSULADOR LATEX: Transforma \frac{a}{b} solto em $$ \frac{a}{b} $$
    texto = re.sub(r'(?<!\$)\\\bfrac\{([^}]+)\}\{([^}]+)\}(?!\$)', r'$$ \\frac{\1}{\2} $$', texto)
    texto = re.sub(r'(?<!\$)\\\b(times|div|sqrt|circ|degree)\b(?!\$)', r'$$ \\\1 $$', texto)
    
    # Corrige cifrões duplos repetidos
    texto = re.sub(r'\$\$\s*\$\$', '$$', texto)
    
    # Limpa tags obsoletas do GeoGebra se houver
    texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', '', texto, flags=re.IGNORECASE | re.DOTALL)
    
    # Prompts de Imagem transformados em caixas elegantes e compactas
    texto = re.sub(
        r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', 
        r'\n\n🖼️ **[ILUSTRAÇÃO TÉCNICA SUGERIDA]**\n```english\n\1\n```\n\n', 
        texto, 
        flags=re.IGNORECASE | re.DOTALL
    )
    
    return texto

# --- ESTILIZAÇÃO DE LUXO E DEFINIÇÃO DE TEMAS (GLOBAL SOBERANO) ---
BRAND_BLUE = "#2962FF"
BRAND_NAVY = "#000B1A"

if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "🌙 Dark"

if st.session_state.tema_sistema == "🌙 Dark":
    cor_fundo, cor_texto, cor_sidebar, cor_card = BRAND_NAVY, "#FFFFFF", "#001226", "#001E3C"
    cor_borda = "#003366"
else:
    cor_fundo, cor_texto, cor_sidebar, cor_card = "#F8FAFC", "#1A202C", "#FFFFFF", "#FFFFFF"
    cor_borda = "#E2E8F0"

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
        * {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .stApp {{ background-color: {cor_fundo} !important; color: {cor_texto} !important; }}
        [data-testid="stSidebar"] {{ background-color: {cor_sidebar} !important; border-right: 1px solid {cor_borda}; }}
        div[data-testid="stMetric"] {{ background: {cor_card} !important; border: 1px solid {cor_borda} !important; border-radius: 16px !important; padding: 15px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; }}
        .stButton button {{ background: linear-gradient(135deg, {BRAND_BLUE}, #0039CB) !important; color: white !important; border-radius: 12px !important; font-weight: 700 !important; width: 100%; transition: all 0.3s ease; }}
        .stButton button:hover {{ transform: translateY(-2px); box-shadow: 0 8px 15px rgba(41, 98, 255, 0.3) !important; }}
        .clock-container {{ background: {BRAND_BLUE}15; color: {BRAND_BLUE}; padding: 8px 15px; border-radius: 30px; font-weight: 800; font-size: 14px; text-align: center; margin: 10px 0; border: 1px solid {BRAND_BLUE}33; }}
        /* BENTO GRID EFFECT PARA CONTAINERS */
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{ border-radius: 16px !important; box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important; transition: all 0.3s ease; background: {cor_card}; border-color: {cor_borda} !important; }}
        div[data-testid="stVerticalBlock"] > div[style*="border"]:hover {{ box-shadow: 0 8px 20px rgba(0,0,0,0.08) !important; }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: IDENTIDADE, RELÓGIO E NAVEGAÇÃO ESTRATÉGICA AGRUPADA ---
with st.sidebar:
    try: st.logo("logo.png", icon_image="logo.png")
    except: pass
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try: st.image("logo.png", width=110)
        except: pass
    
    st.markdown("<h2 style='text-align: center; font-size: 20px; margin-top: 5px; margin-bottom: 0px;'>Ronaldo Gomes</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 11px; color: {BRAND_BLUE}; font-weight: 800; letter-spacing: 1px;'>SOBERANIA PEDAGÓGICA</p>", unsafe_allow_html=True)

    # 🚨 SELETOR DE TEMA COM PERSISTÊNCIA SOBERANA
    tema_sel_pills = st.segmented_control("Visual do Sistema:", ["🌙 Dark", "🌞 Light"], default=st.session_state.tema_sistema, key="seg_tema_sidebar")
    if tema_sel_pills and tema_sel_pills != st.session_state.tema_sistema:
        st.session_state.tema_sistema = tema_sel_pills
        st.rerun()

    # RELÓGIO DIGITAL & DIA LETIVO
    fuso_br = timezone(timedelta(hours=-3))
    agora_br = datetime.now(fuso_br)
    hora_atual = agora_br.strftime("%H:%M:%S")
    data_atual = agora_br.strftime("%d/%m/%Y")
    data_atual_dt = agora_br.date() 
    
    with st.container(border=True):
        st.markdown(f"<div style='text-align: center; font-weight: 800; font-size: 13px; color: {BRAND_BLUE};'>🕒 {hora_atual} | 📅 {data_atual}</div>", unsafe_allow_html=True)
        
        feriado_hoje = util.verificar_feriado_itabuna(data_atual_dt)
        if feriado_hoje:
            st.caption(f"🎉 FERIADO: {feriado_hoje.upper()}")
        else:
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            nome_dia = dias_semana[data_atual_dt.weekday()]
            st.caption(f"🟢 {nome_dia}-feira • Dia Letivo")

    # RADAR DE SOBERANIA
    with st.expander("🔔 Radar de Notificações", expanded=False):
        try:
            planos_pendentes = len(df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)]) if not df_planos.empty else 0
            if planos_pendentes > 0:
                st.warning(f"⏳ {planos_pendentes} Plano(s) no Hub de Produção")
            else: st.success("✅ Nenhum plano pendente")
        except: pass

        try:
            if not df_notas.empty:
                uti_count = len(df_notas[df_notas['MEDIA_FINAL'].apply(util.sosa_to_float) < 6.0])
                if uti_count > 0:
                    st.error(f"🚑 {uti_count} Aluno(s) na UTI Pedagógica")
                else: st.success("✅ Nenhum aluno na UTI")
        except: pass

    st.markdown("---")

    # NAVEGAÇÃO ESTRATÉGICA AGRUPADA EM 3 MÓDULOS PRINCIPAIS
    st.markdown("<p style='font-size: 11px; color: gray; font-weight: bold; letter-spacing: 1px;'>ÁREA DE ATUAÇÃO:</p>", unsafe_allow_html=True)
    
    modulos_map = {
        "📅 Planejamento (Ponto ID)": "📚 Aulas",
        "🧪 Criador de Aulas": "📚 Aulas",
        "📚 Base de Conhecimento": "📚 Aulas",
        
        "📝 Central de Avaliações": "📝 Provas",
        "📸 Scanner de Gabaritos": "📝 Provas",
        "📊 Painel de Notas & Vistos": "📝 Provas",
        "📈 Boletim Anual & Conselho": "📝 Provas",
        
        "📝 Diário de Bordo Rápido": "👥 Regência",
        "👤 Biografia do Estudante": "👥 Regência",
        "👥 Gestão da Turma": "👥 Regência",
        "♿ Relatórios PEI / Perfil IA": "👥 Regência"
    }
    
    modulo_default = modulos_map.get(st.session_state.menu_atual, "📚 Aulas")
    
    modulo_ativo = st.segmented_control(
        "Módulo:", 
        ["📚 Aulas", "📝 Provas", "👥 Regência"], 
        default=modulo_default,
        key="seg_modulo_sidebar"
    )

    paginas_por_modulo = {
        "📚 Aulas": [
            "📅 Planejamento (Ponto ID)",
            "🧪 Criador de Aulas",
            "📚 Base de Conhecimento"
        ],
        "📝 Provas": [
            "📝 Central de Avaliações",
            "📸 Scanner de Gabaritos",
            "📊 Painel de Notas & Vistos",
            "📈 Boletim Anual & Conselho"
        ],
        "👥 Regência": [
            "📝 Diário de Bordo Rápido",
            "👤 Biografia do Estudante",
            "👥 Gestão da Turma",
            "♿ Relatórios PEI / Perfil IA"
        ]
    }

    paginas_disponiveis = paginas_por_modulo.get(modulo_ativo, paginas_por_modulo["📚 Aulas"])
    
    idx_pag = paginas_disponiveis.index(st.session_state.menu_atual) if st.session_state.menu_atual in paginas_disponiveis else 0
    
    pagina_selecionada = st.pills(
        "Selecione o Painel:", 
        paginas_disponiveis, 
        default=paginas_disponiveis[idx_pag],
        key="pills_pagina_sidebar"
    )

    if pagina_selecionada and pagina_selecionada != st.session_state.menu_atual:
        st.session_state.menu_atual = pagina_selecionada
        st.rerun()

    menu = st.session_state.menu_atual

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    
    with st.popover("⚙️ Conta & Sessão", use_container_width=True):
        st.caption("👑 **Prof. Ronaldo Gomes**")
        st.caption("Licença Ativa • SOSA 2026")
        st.markdown("---")
        
        c_pop1, c_pop2 = st.columns(2)
        if c_pop1.button("🔄 Sync", use_container_width=True, key="btn_pop_sync"):
            st.cache_data.clear()
            st.rerun()
            
        if c_pop2.button("🚪 Sair", use_container_width=True, key="btn_pop_sair"):
            st.session_state["password_correct"] = False
            st.session_state["login_timestamp"] = None
            st.rerun()

    st.caption("Itabuna/BA • © 2026")

# --- CARREGAMENTO DE DADOS ---
wb, (df_alunos, df_curriculo, df_materiais, df_planos, df_aulas, df_notas, df_diario, df_turmas, df_relatorios, df_horarios, df_registro_aulas, df_diagnosticos) = db.carregar_tudo()



# --- FUNÇÕES AUXILIARES ---
def prensa_hidraulica_texto(texto, label):
    limpo = texto.replace(label, "").replace(label.upper(), "").replace(label.lower(), "")
    if limpo.startswith(":") or limpo.startswith(" :"):
        limpo = limpo.split(":", 1)[-1]
    return limpo.strip()

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
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - V2026.ULTIMATE
# (AULAS EXPOSITIVAS OBJETIVAS, GATILHOS NEWS/TECH, UNIDADES TEMÁTICAS BNCC E CONCILIADOR)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("Engenharia de Planejamento (Ponto ID)")
    st.caption("Arquitetura estratégica da semana: Aulas expositivas objetivas, sensibilização com Notícias/Tech, alinhamento BNCC de Matemática e Conciliador Cronológico.")
    st.markdown("---")

    def reset_planejamento():
        keys_to_clear = ["p_temp", "refino_ativo", "p_meta"]
        for k in keys_to_clear:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_plano = int(time.time())
        st.rerun()

    if "v_plano" not in st.session_state: 
        st.session_state.v_plano = int(time.time())
    v = st.session_state.v_plano 

    tab_gerar, tab_producao, tab_acervo, tab_inteligencia = st.tabs([
        "Novo Plano", "Hub de Produção", "Acervo de Planos", "Inteligência Curricular & Conciliação"
    ])
    
    # ==============================================================================
    # ABA 1: NOVO PLANO
    # ==============================================================================
    with tab_gerar:
        with st.container(border=True):
            st.markdown("#### 📦 1. Parâmetros da Semana & Carga Horária")
            
            c1, c2, c3 = st.columns([1, 2, 2])
            ano_p = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_sel_{v}")
            ano_str_busca = f"{ano_p}º"

            todas_semanas = util.gerar_semanas()
            sobrescrever_planos = st.toggle("Mostrar semanas já planejadas (Permitir Sobrescrita)", value=False, key=f"tog_sobrescrever_{v}")
            
            if not df_planos.empty and 'ANO' in df_planos.columns and 'SEMANA' in df_planos.columns:
                semanas_planejadas = df_planos[df_planos['ANO'] == ano_str_busca]['SEMANA'].tolist()
            else:
                semanas_planejadas = []
                
            if sobrescrever_planos:
                semanas_disponiveis = [s for s in todas_semanas if "Jornada" not in s]
            else:
                semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_planejadas and "Jornada" not in s]

            if not semanas_disponiveis:
                st.success(f"🏆 Todas as semanas do {ano_p}º Ano já foram planejadas!")
                st.info("💡 Ative a opção 'Permitir Sobrescrita' acima caso deseje re-planejar alguma semana.")
                st.stop()

            sem_p = c2.selectbox("Semana de Referência:", semanas_disponiveis, key=f"sem_sel_{v}")
            sem_limpa = db.normalizar_semana_chave(sem_p) if hasattr(db, 'normalizar_semana_chave') else sem_p.split(" (")[0].strip()
            
            trim_atual = "I Trimestre"
            if " - " in str(sem_p):
                partes_sem = str(sem_p).split(" - ")
                if len(partes_sem) > 1:
                    trim_atual = partes_sem[1].strip()

            status_especial_sem = ""
            motivo_especial_sem = ""
            if not df_relatorios.empty:
                config_sem_rec = df_relatorios[df_relatorios['TIPO'] == f"CONFIG_SEMANA_{sem_limpa}"]
                if not config_sem_rec.empty:
                    partes_c = str(config_sem_rec.iloc[-1]['CONTEUDO']).split('|')
                    status_especial_sem = partes_c[0]
                    motivo_especial_sem = partes_c[1] if len(partes_c) > 1 else ""

            if status_especial_sem and "Normal" not in status_especial_sem:
                st.warning(f"📌 **Status Especial Detectado no Calendário:** {status_especial_sem} " + (f"(*{motivo_especial_sem}*)" if motivo_especial_sem else ""))

            tipo_semana = c3.selectbox("DNA da Abordagem:", [
                "Aula de Safra (Regular)", 
                "🏖️ Recesso / Férias / Feriado",
                "Aplicação de Exame", 
                "Revisão & Recomposição", 
                "Semana de Provas Oficiais (Global)",
                "Devolutiva de Resultados & Recuperação",
                "Trabalho Investigativo", 
                "Sonda de Proficiência",
                "Aula Aberta (Dinâmicas e Eventos)"
            ], key=f"gate_tipo_{v}")
            
            st.markdown("---")
            
            carga_horaria = st.pills(
                "⏱️ Carga Horária da Semana:", 
                ["1 Aula (Feriado/Evento)", "2 Aulas (Semana Normal)", "3 Aulas (+ Sábado Letivo)"], 
                default="2 Aulas (Semana Normal)",
                key=f"carga_pills_{v}"
            )

        # BAIXA LIMPA EM RECESSO / FÉRIAS / FERIADO (SEM GERAR ARQUIVOS)
        if "Recesso" in tipo_semana or "Férias" in tipo_semana or "Feriado" in tipo_semana:
            with st.container(border=True):
                st.markdown("#### 🏖️ Conclusão Burocrática de Recesso / Férias")
                st.info(f"A semana **{sem_limpa}** será registrada como Recesso/Feriado. Nenhum arquivo será gerado e ela não aparecerá como pendente no Criador de Aulas.")
                
                motivo_recesso_txt = st.text_input("Observação (Opcional):", value="Recesso Escolar / Feriado", key=f"obs_rec_ponto_{v}")
                
                if st.button("🏖️ DAR BAIXA EM RECESSO (SEM GERAR NADA)", type="primary", use_container_width=True, key=f"btn_baixa_rec_{v}"):
                    with st.spinner("Registrando baixa por Recesso/Férias..."):
                        db.dar_baixa_plano_evento(
                            semana=sem_limpa, 
                            ano=ano_str_busca, 
                            motivo_ou_status=motivo_recesso_txt
                        )
                        st.success(f"✅ Semana {sem_limpa} registrada como Recesso/Feriado com sucesso!")
                        st.balloons(); time.sleep(1); st.rerun()

        elif tipo_semana in ["Aplicação de Exame", "Semana de Provas Oficiais (Global)", "Sonda de Proficiência", "Devolutiva de Resultados & Recuperação"]:
            with st.container(border=True):
                st.markdown("#### 📋 2. Vínculo de Prova do Acervo & Extração de Habilidades")
                st.caption("Selecione o exame já forjado no acervo para que o sistema extraia automaticamente os conteúdos, descritores SAEB e habilidades BNCC para o Plano Padronizado SOSA.")

                df_ativos_ano = df_aulas[df_aulas['ANO'].astype(str).str.contains(str(ano_p))] if not df_aulas.empty else pd.DataFrame()
                
                opcoes_ativos = []
                if not df_ativos_ano.empty:
                    mask_ex = (df_ativos_ano['SEMANA_REF'] == "AVALIAÇÃO") | (df_ativos_ano['TIPO_MATERIAL'].str.contains("PROVA|TESTE|SONDA|AVALIAÇÃO|AVALIACAO|EXAME", case=False, na=False))
                    opcoes_ativos = sorted(df_ativos_ano[mask_ex]['TIPO_MATERIAL'].unique().tolist())
                
                c_ex1, c_ex2 = st.columns([2, 1])
                exame_selecionado = c_ex1.selectbox("📋 Selecione a Prova/Exame do Acervo (Opcional):", [""] + opcoes_ativos, key=f"sel_mat_vinculo_{v}")
                pincamento_exame_manual = c_ex2.text_input("ou Digite o Nome/Assunto da Prova:", placeholder="Ex: Prova Trimestral de Operações com Decimais", key=f"inp_exame_manual_{v}")

                habilidades_extraidas = ""
                conteudos_extraidos = ""
                texto_prova_completo = ""

                if exame_selecionado and not df_ativos_ano.empty:
                    match_ex = df_ativos_ano[df_ativos_ano['TIPO_MATERIAL'] == exame_selecionado]
                    if not match_ex.empty:
                        texto_prova_completo = str(match_ex.iloc[0]['CONTEUDO'])
                        grade = ai.extrair_tag(texto_prova_completo, "GRADE_DE_CORRECAO") or ai.extrair_tag(texto_prova_completo, "GRADE_DE_CORRECAO_PEI")
                        if grade:
                            descritores = re.findall(r'(?i)(?:DESCRITOR_SAEB|HABILIDADE|BNCC|DESCRITOR)\s*:\s*([^|\]\n]+)', grade)
                            if descritores:
                                habilidades_extraidas = ", ".join(list(dict.fromkeys([d.strip() for d in descritores])))
                        
                        if not habilidades_extraidas:
                            codes = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', texto_prova_completo, re.IGNORECASE)
                            if codes:
                                habilidades_extraidas = ", ".join(list(set([c.upper() for c in codes])))
                        
                        conteudos_extraidos = ai.extrair_tag(texto_prova_completo, "CONTEUDOS_ESPECIFICOS") or ai.extrair_tag(texto_prova_completo, "OBJETO_CONHECIMENTO") or exame_selecionado

                if not conteudos_extraidos:
                    conteudos_extraidos = pincamento_exame_manual if pincamento_exame_manual.strip() else (exame_selecionado if exame_selecionado else f"Aplicação da Avaliação de Matemática - {sem_limpa}")

                if not habilidades_extraidas:
                    habilidades_extraidas = f"EF0{ano_p}MA01 - Habilidades do {ano_p}º Ano avaliadas no exame regimental."

                diretriz_logistica = st.text_area(
                    "📋 Orientações Logísticas e Roteiro da Aplicação (Editável):",
                    value=(
                        f"INÍCIO (10 min): Acolhimento dos estudantes, organização do ambiente da sala de aula e leitura orientada das instruções e critérios de pontuação da prova.\n"
                        f"MEIO (35 min): Aplicação supervisionada do exame ({exame_selecionado if exame_selecionado else conteudos_extraidos}). Acompanhamento e suporte mediado aos estudantes do Grupo 1 (PEI Nível 1, 2 e 3).\n"
                        f"FIM (5 min): Recolhimento organizado dos cadernos de questões e cartões de resposta OMR para posterior escaneamento no Scanner CIR."
                    ),
                    height=140,
                    key=f"txt_rot_exec_{v}_{hash(exame_selecionado or pincamento_exame_manual)}"
                )

                st.info("💡 **Geração Automática do Plano Padronizado:** Ao clicar em 'Gerar Plano Padronizado', o texto completo será montado com todas as tags SOSA pronto para você **Copiar e Colar**. A semana será gravada como **PRODUZIDA/ISENTA**, dispensando a geração no Criador de Aulas.")

                c_save_ex1, c_save_ex2 = st.columns(2)

                if c_save_ex1.button("🧠 Gerar Plano Padronizado SOSA (Para Copiar / Lapidar)", type="primary", use_container_width=True, key=f"btn_gen_exame_plan_{v}"):
                    nome_exame_tit = exame_selecionado if exame_selecionado else conteudos_extraidos
                    
                    if "1 Aula" in carga_horaria:
                        roteiro_a1 = diretriz_logistica
                        roteiro_a2 = "N/A (Carga horária de 1 Aula)"
                        roteiro_sab = "N/A"
                    elif "2 Aulas" in carga_horaria:
                        roteiro_a1 = f"AULA 01 - APLICAÇÃO DO EXAME:\n{diretriz_logistica}"
                        roteiro_a2 = f"AULA 02 - SEGUNDA CHAMADA / DEVOLUTIVA:\nINÍCIO: Acolhimento e atendimento aos estudantes ausentes.\nMEIO: Aplicação de 2ª chamada regimental / Correção comentada dos itens mais errados e vistos nos cadernos.\nFIM: Síntese dos resultados."
                        roteiro_sab = "N/A"
                    else:
                        roteiro_a1 = f"AULA 01 - APLICAÇÃO DO EXAME:\n{diretriz_logistica}"
                        roteiro_a2 = "AULA 02 - CONTINUIDADE / SEGUNDA CHAMADA REGIMENTAL"
                        roteiro_sab = "SÁBADO LETIVO - OFICINA / RECOMPOSIÇÃO"

                    plano_formatado_exame = (
                        f"[HABILIDADE_BNCC] {habilidades_extraidas}\n"
                        f"[COMPETENCIAS_FOCO] Competência Específica 2 (Raciocínio Lógico) e 6 (Enfrentar Situações-Problema)\n"
                        f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} - {nome_exame_tit}\n"
                        f"[CONTEUDOS_ESPECIFICOS] {conteudos_extraidos}\n"
                        f"[OBJETIVOS_ENSINO] Mensurar a proficiência e o nível de consolidação dos objetos de conhecimento do {ano_p}º Ano.\n"
                        f"[JUSTIFICATIVA_PEDAGOGICA] Verificação de aprendizagem regimental do {trim_atual} conforme calendário escolar.\n"
                        f"[AULA_1] {roteiro_a1}\n"
                        f"[AULA_2] {roteiro_a2}\n"
                        f"[SABADO_LETIVO] {roteiro_sab}\n"
                        f"[AVALIACAO_DE_MERITO] Correção automatizada via Scanner de Gabaritos (CIR) com análise TRI de distratores.\n"
                        f"[ESTRATEGIA_DUA_PEI] Garantia de provas adaptadas (PEI N1, N2 e N3) para os estudantes do Grupo 1 com tempo adicional conforme legislação."
                    )

                    st.session_state.p_temp = plano_formatado_exame
                    st.session_state.p_meta = {
                        "semana": sem_limpa, 
                        "trimestre": trim_atual, 
                        "ano": ano_str_busca, 
                        "base": f"Exame: {nome_exame_tit}",
                        "status_final": "PRODUZIDO"
                    }
                    st.toast("✅ Plano de Exame gerado no formato padronizado!", icon="🎯")
                    st.rerun()

                if c_save_ex2.button("💾 Salvar Diretamente e Arquivar no Hub", use_container_width=True, key=f"btn_direct_save_ex_{v}"):
                    with st.spinner("Salvando e sincronizando Plano de Exame no Drive..."):
                        nome_exame_tit = exame_selecionado if exame_selecionado else conteudos_extraidos
                        nome_arquivo = f"PLANO_{ano_str_busca.replace('º','')}_{sem_limpa.replace(' ', '')}"
                        
                        db.excluir_plano_completo(sem_limpa, ano_str_busca)
                        
                        dados_docx = {
                            "geral": f"{tipo_semana.upper()} - {nome_exame_tit}",
                            "especificos": conteudos_extraidos,
                            "objetivos": "Mensurar proficiência e consolidação de habilidades.",
                            "recursos": f"Material Impresso / Exame: {nome_exame_tit}",
                            "metodologia": diretriz_logistica,
                            "avaliacao": "Scanner CIR (TRI) e observação da aplicação.",
                            "pei": "Provas adaptadas (PEI N1, N2 e N3) conforme perfil dos estudantes."
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(
                            nome_arquivo, dados_docx, {"ano": ano_str_busca, "semana": sem_limpa, "trimestre": trim_atual}
                        )
                        link_drive = db.subir_e_converter_para_google_docs(
                            doc_io, nome_arquivo, trimestre=trim_atual, categoria=ano_str_busca, semana=sem_limpa, modo="PLANEJAMENTO"
                        )
                        
                        final_txt = (
                            f"[HABILIDADE_BNCC] {habilidades_extraidas} \n"
                            f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} - {nome_exame_tit} \n"
                            f"[CONTEUDOS_ESPECIFICOS] {conteudos_extraidos} \n"
                            f"[AULA_1] {diretriz_logistica} \n"
                            f"[AULA_2] N/A (Aplicação de Exame) \n"
                            f"[SABADO_LETIVO] N/A \n"
                            f"--- LINK DRIVE --- {link_drive}"
                        )
                        
                        db.salvar_no_banco("DB_PLANOS", [
                            datetime.now().strftime("%d/%m/%Y"), sem_limpa, ano_str_busca, trim_atual, "PRODUZIDO", final_txt, link_drive
                        ])
                        
                        st.success(f"✅ Plano para {sem_limpa} salvo como PRODUZIDO com sucesso!")
                        st.balloons(); time.sleep(1); st.rerun()

        else:
            with st.container(border=True):
                st.markdown("#### 📖 2. Base Curricular, Fatiamento do Livro & Sensibilização News/Tech")
                st.caption(f"ℹ️ **Carga Horária Selecionada:** {carga_horaria}. A IA distribuirá o conteúdo nas aulas conforme o número real de aulas.")
                
                modo_p = st.pills(
                    "Selecione a Fonte de Dados:", 
                    ["Livro Didático (Cofre Digital)", "Manual (Matriz)", "Links da Web"], 
                    default="Livro Didático (Cofre Digital)",
                    key=f"pills_fonte_{v}"
                )
                
                ctx_ia, uri_livro_drive, links_web_texto, base_didatica_info = "", None, "", "Matriz Curricular"
                texto_teoria_extraido, texto_exercicios_extraido = "", ""
                
                if modo_p == "Manual (Matriz)":
                    df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str).str.contains(str(ano_p))].copy() if not df_curriculo.empty else pd.DataFrame()
                    col_eixo_real = next((c for c in df_matriz_ano.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None) if not df_matriz_ano.empty else None
                    col_trim_real = next((c for c in df_matriz_ano.columns if trim_atual.upper() in c.upper()), None) if not df_matriz_ano.empty else None

                    sel_eixo, sel_cont = [], []
                    if col_eixo_real and not df_matriz_ano.empty:
                        eixos_disponiveis = sorted(df_matriz_ano[col_eixo_real].dropna().unique().tolist())
                        sel_eixo = st.multiselect("Unidade Temática BNCC (Eixo):", eixos_disponiveis, key=f"ms_eixo_matriz_{v}")
                        
                        if col_trim_real and sel_eixo:
                            df_eixos_sel = df_matriz_ano[df_matriz_ano[col_eixo_real].isin(sel_eixo)]
                            topicos_fatiados = set()
                            for _, r_eixo in df_eixos_sel.iterrows():
                                texto_trim = str(r_eixo.get(col_trim_real, ''))
                                texto_limpo = re.sub(r'\[cite:.*?\]', '', texto_trim).strip()
                                for t_item in texto_limpo.split(';'):
                                    t_clean = t_item.strip()
                                    if t_clean and len(t_clean) > 3:
                                        topicos_fatiados.add(t_clean)
                                        
                            sel_cont = st.multiselect("Objetos de Conhecimento Específicos:", sorted(list(topicos_fatiados)), key=f"ms_cont_matriz_{v}")
                            
                        ctx_ia = f"UNIDADE TEMÁTICA BNCC: {sel_eixo}, OBJETOS DE CONHECIMENTO: {sel_cont}."
                    else: st.warning("⚠️ Não foi possível ler as colunas da matriz carregada.")
                
                elif modo_p == "Links da Web":
                    links_web_texto = st.text_area("Cole os Links da Web ou Notícias (um por linha):", placeholder="https://...", key=f"ta_links_web_{v}")
                    base_didatica_info = "Artigos / Notícias da Web"
                
                else: # Livro Didático
                    cx1, cx2, cx3 = st.columns([2, 1.5, 1.5])
                    livros_disponiveis = df_materiais[df_materiais['TIPO'].str.contains(str(ano_p), na=False)]['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
                    sel_mat = cx1.selectbox("Livro do Cofre Digital:", [""] + livros_disponiveis, key=f"sel_livro_ponto_{v}")
                    
                    pags_teoria_input = cx2.text_input("📘 Páginas de Teoria / Leitura:", placeholder="Ex: 184-186, 189", key=f"pags_teo_ponto_{v}")
                    pags_ex_input = cx3.text_input("📝 Páginas de Exercícios / Fixação:", placeholder="Ex: 187-188, 190-192", key=f"pags_ex_ponto_{v}")

                    if sel_mat:
                        uri_livro_drive = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_mat].iloc[0]['URI_ARQUIVO']
                        base_didatica_info = f"Livro: {sel_mat} | Teoria: {pags_teoria_input if pags_teoria_input else 'Geral'} | Exercícios: {pags_ex_input if pags_ex_input else 'Geral'}"

                        list_pags_teo = util.processar_intervalos_paginas(pags_teoria_input)
                        list_pags_ex = util.processar_intervalos_paginas(pags_ex_input)

                        if list_pags_teo or list_pags_ex:
                            with st.spinner("🔍 Fatiando páginas selecionadas do Drive..."):
                                bytes_pdf = db.baixar_bytes_arquivo_drive(uri_livro_drive)
                                if bytes_pdf:
                                    if list_pags_teo: texto_teoria_extraido = util.extrair_texto_pdf_por_paginas(bytes_pdf, list_pags_teo)
                                    if list_pags_ex: texto_exercicios_extraido = util.extrair_texto_pdf_por_paginas(bytes_pdf, list_pags_ex)

                    st.markdown("##### ✍️ Injeção Auxiliar / Autonomia Docente (Opcional)")
                    recorte_livro_texto = st.text_area(
                        "Cole anotações extras, exercícios autorais ou notícias do dia:",
                        placeholder="Cole aqui textos extras do seu caderno ou notícias recentes...",
                        height=90,
                        key=f"recorte_ponto_id_{v}"
                    )

                    if texto_teoria_extraido or texto_exercicios_extraido or recorte_livro_texto.strip():
                        with st.expander("👁️ MESA DE INSPEÇÃO DA IA (PRÉVIA DO CONTEÚDO LIDO DO LIVRO)", expanded=True):
                            t_insp1, t_insp2, t_insp3 = st.tabs(["📘 Teoria (Livro)", "📝 Exercícios (Livro)", "✍️ Texto Auxiliar"])
                            with t_insp1:
                                if texto_teoria_extraido: st.text_area("Teoria Lida:", texto_teoria_extraido, height=150, disabled=True, key=f"ta_insp_teo_{v}")
                                else: st.info("Nenhuma página de teoria fatiada.")
                            with t_insp2:
                                if texto_exercicios_extraido: st.text_area("Exercícios Lidos:", texto_exercicios_extraido, height=150, disabled=True, key=f"ta_insp_ex_{v}")
                                else: st.info("Nenhuma página de exercício fatiada.")
                            with t_insp3:
                                if recorte_livro_texto.strip(): st.text_area("Texto Auxiliar Autorizado:", recorte_livro_texto, height=150, disabled=True, key=f"ta_insp_aux_{v}")
                                else: st.info("Nenhum texto auxiliar digitado.")

            foco_a1, foco_a2, foco_sab = "N/A", "N/A", "N/A"
            with st.popover("⚙️ Ajustes Finos & Foco Específico das Aulas (Opcional)", use_container_width=True):
                st.caption("Especifique o tema ou gancho de notícia/tecnologia para cada aula.")
                if "1 Aula" in carga_horaria:
                    foco_a1 = st.text_area("Foco da Única Aula:", placeholder="Ex: Pergunta sobre inflação e exercícios de soma de decimais...", height=80, key=f"foco_a1_p1_{v}")
                elif "2 Aulas" in carga_horaria:
                    foco_a1 = st.text_area("Foco da Aula 1 (Conceito/Sensibilização):", placeholder="Ex: Explicar algoritmo e conectar com notícias de tecnologia...", height=80, key=f"foco_a1_p2_{v}")
                    foco_a2 = st.text_area("Foco da Aula 2 (Fixação):", placeholder="Ex: Resolver exercícios da pág. 185...", height=80, key=f"foco_a2_p2_{v}")
                else:
                    foco_a1 = st.text_area("Foco da Aula 1:", placeholder="Ex: Explicar conceito...", height=80, key=f"foco_a1_p3_{v}")
                    foco_a2 = st.text_area("Foco da Aula 2:", placeholder="Ex: Resolver exercícios...", height=80, key=f"foco_a2_p3_{v}")
                    foco_sab = st.text_area("Foco do Sábado Letivo:", placeholder="Ex: Oficina prática...", height=80, key=f"foco_sab_p3_{v}")

            c_g1, c_g2 = st.columns(2)

            if c_g1.button("🧠 Iniciar Motor de IA: Gerar Planejamento Ancorado (Custo Zero)", use_container_width=True, type="primary", key=f"btn_gen_ia_ponto_{v}"):
                with st.status("🚀 Iniciando Protocolo de Planejamento Expositivo...", expanded=True) as status:
                    status.write("📚 Consolidando recortes do livro, diretrizes e ganchos News/Tech...")
                    
                    precisa_de_internet = False
                    if modo_p == "Manual (Matriz)": diretriz_base = "MÉTODO MANUAL: Baseie-se na Matriz Curricular."
                    elif modo_p == "Links da Web": diretriz_base = f"MÉTODO WEB: Use estes links:\n{links_web_texto}"; precisa_de_internet = True
                    else: diretriz_base = f"MÉTODO LIVRO DIDÁTICO: O professor utilizará o livro '{base_didatica_info}'."

                    if "1 Aula" in carga_horaria:
                        diretriz_carga_promp = (
                            "🚨 ATENÇÃO: CARGA HORÁRIA DE APENAS 1 AULA NA SEMANA.\n"
                            "- Concentre TODA a explicação teórica e os exercícios na AULA 1 no formato INÍCIO ➔ MEIO ➔ FIM.\n"
                            "- As tags [AULA_2] e [SABADO_LETIVO] DEVEM conter 'N/A (Carga horária de 1 Aula)'."
                        )
                    elif "2 Aulas" in carga_horaria:
                        diretriz_carga_promp = (
                            "CARGA HORÁRIA: 2 AULAS NA SEMANA.\n"
                            "- Distribua a teoria na AULA 1 e a fixação na AULA 2, ambas no formato INÍCIO ➔ MEIO ➔ FIM.\n"
                            "- Tag [SABADO_LETIVO] deve conter 'N/A'."
                        )
                    else:
                        diretriz_carga_promp = "CARGA HORÁRIA: 3 AULAS NA SEMANA. Distribua o conteúdo na AULA 1, AULA 2 e SÁBADO LETIVO no formato INÍCIO ➔ MEIO ➔ FIM."

                    template_forcado = (
                        "[HABILIDADE_BNCC] (Código BNCC alfanumérico ex: EF06MA01)\n"
                        "[COMPETENCIAS_FOCO] (Competências Específicas de Matemática 1 a 8 da Pág. 267 da BNCC)\n"
                        "[OBJETO_CONHECIMENTO] (Tema principal e Unidade Temática BNCC)\n"
                        "[CONTEUDOS_ESPECIFICOS] (Tópicos matemáticos)\n"
                        "[OBJETIVOS_ENSINO] (Objetivos pedagógicos)\n"
                        "[JUSTIFICATIVA_PEDAGOGICA] (Justificativa)\n"
                        "[AULA_1] INÍCIO (Sensibilização/News/Tech - 10 min): ...\nMEIO (Fundamentação/Quadro - 25 min): ...\nFIM (Fixação/Exercícios - 15 min): ...\n"
                        "[AULA_2] (AULA 2 no mesmo formato ou N/A se for 1 aula)\n"
                        "[SABADO_LETIVO] (SÁBADO no mesmo formato ou N/A)\n"
                        "[AVALIACAO_DE_MERITO] (Como avaliar)\n"
                        "[ESTRATEGIA_DUA_PEI] (Adaptação PEI)\n"
                    )

                    pacote_recorte_completo = ""
                    if texto_teoria_extraido: pacote_recorte_completo += f"--- PÁGINAS DE TEORIA ---\n{texto_teoria_extraido}\n\n"
                    if texto_exercicios_extraido: pacote_recorte_completo += f"--- PÁGINAS DE EXERCÍCIOS ---\n{texto_exercicios_extraido}\n\n"
                    if recorte_livro_texto.strip(): pacote_recorte_completo += f"--- TEXTO AUXILIAR DO PROFESSOR ---\n{recorte_livro_texto.strip()}\n\n"

                    prompt = (
                        f"TIPO: {tipo_semana}\n{diretriz_base}\n"
                        f"SÉRIE: {ano_p}º Ano. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}.\n"
                        f"{diretriz_carga_promp}\n"
                        f"BASE DIDÁTICA: {base_didatica_info}\n"
                        f"DIRETRIZ AULA 1: {foco_a1}\nDIRETRIZ AULA 2: {foco_a2}\nDIRETRIZ SÁBADO: {foco_sab}\n"
                        f"MATRIZ OFICIAL:\n{ctx_ia if ctx_ia else 'Baseada na leitura direta das páginas do Livro Didático.'}\n\n"
                        f"🚨 PREENCHA OBRIGATORIAMENTE ESTE TEMPLATE EXATO:\n{template_forcado}"
                    )
                    
                    status.write("⚡ Maestro Sosa (Gemini 3.6 Flash) está arquitetando o plano expositivo alinhado...")
                    resultado_ia = ai.gerar_ia("PLANE_PEDAGOGICO", prompt, url_drive=uri_livro_drive, usar_busca=precisa_de_internet, recorte_livro=pacote_recorte_completo)
                    
                    if "ERRO" in resultado_ia.upper() or "⚠️" in resultado_ia:
                        status.update(label="❌ Falha na comunicação com a IA.", state="error")
                        st.error(resultado_ia)
                    else:
                        status.write("✅ Plano arquitetado com sucesso!")
                        st.session_state.p_temp = resultado_ia
                        st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info}
                        
                        status.update(label="🎉 Planejamento Concluído!", state="complete")
                        time.sleep(0.8)
                        st.rerun()

            if c_g2.button("✍️ Elaborar Manualmente (Sem IA)", use_container_width=True, key=f"btn_manual_ponto_{v}"):
                espec_pre = ", ".join(sel_cont) if 'sel_cont' in locals() and sel_cont else ""
                
                texto_manual_template = (
                    f"[HABILIDADE_BNCC] EF0{ano_p}MA01\n"
                    f"[COMPETENCIAS_FOCO] Competência Específica 2 (Raciocínio Lógico e Argumentação)\n"
                    f"[OBJETO_CONHECIMENTO] Unidade Temática: Números / Álgebra\n"
                    f"[CONTEUDOS_ESPECIFICOS] {espec_pre}\n"
                    f"[OBJETIVOS_ENSINO]\n"
                    f"[AULA_1] INÍCIO (Sensibilização - 10 min):\nMEIO (Fundamentação/Quadro - 25 min):\nFIM (Fixação/Exercícios - 15 min):\n"
                    f"[AULA_2] INÍCIO:\nMEIO:\nFIM:\n"
                    f"[SABADO_LETIVO] N/A\n"
                    f"[AVALIACAO_DE_MERITO]\n"
                    f"[ESTRATEGIA_DUA_PEI]"
                )
                
                st.session_state.p_temp = texto_manual_template
                st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info}
                st.rerun()

    # MESA DE LAPIDAÇÃO (VERSÃO BENTO GRID + SELO VISUAL BNCC MATEMÁTICA)
    @st.fragment
    def renderizar_mesa_lapidacao_plano():
        if "p_temp" in st.session_state:
            txt_bruto = st.session_state.p_temp
            meta = st.session_state.get("p_meta", {})
            semana_nome = meta.get('semana', 'Atual')
            
            # DETECÇÃO VISUAL DA UNIDADE TEMÁTICA BNCC
            unidade_bncc = "🔢 NÚMEROS"
            if any(x in txt_bruto.upper() for x in ["ÁLGEBRA", "ALGEBRA", "EQUAÇÃO", "VARIÁVEL", "FUNÇÃO"]):
                unidade_bncc = "🧮 ÁLGEBRA"
            elif any(x in txt_bruto.upper() for x in ["GEOMETRIA", "ÂNGULO", "TRIÂNGULO", "POLÍGONO", "PLANO CARTESIANO"]):
                unidade_bncc = "📐 GEOMETRIA"
            elif any(x in txt_bruto.upper() for x in ["GRANDEZAS", "MEDIDAS", "PERÍMETRO", "ÁREA", "VOLUME", "CAPACIDADE"]):
                unidade_bncc = "📏 GRANDEZAS E MEDIDAS"
            elif any(x in txt_bruto.upper() for x in ["PROBABILIDADE", "ESTATÍSTICA", "GRÁFICO", "TABELA", "AMOSTRA"]):
                unidade_bncc = "📊 PROBABILIDADE E ESTATÍSTICA"

            st.markdown("---")
            
            with st.container(border=True):
                st.markdown(f"### 🛠️ Mesa de Lapidação do Plano: **{semana_nome}**")
                
                # BADGES VISUAIS BNCC
                c_bad1, c_bad2 = st.columns([1.5, 2.5])
                c_bad1.markdown(f"**Unidade Temática BNCC:** `{unidade_bncc}`")
                comp_foco_txt = ai.extrair_tag(txt_bruto, "COMPETENCIAS_FOCO") or "Competência Específica 2 (Raciocínio Lógico)"
                c_bad2.markdown(f"**Competência Específica:** `{comp_foco_txt[:55]}...`")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 1. BOTÃO DE HARMONIZAÇÃO RÁPIDA COM IA
                if st.button("🧠 Harmonizar e Enriquecer Plano com IA (Linguagem Oficial BNCC)", use_container_width=True, key=f"btn_harm_plan_{v}"):
                    with st.spinner("Analisando o plano e refinando os tópicos brutos para linguagem pedagógica oficial..."):
                        prompt_harm = (
                            f"REESCREVA O PLANO ABAIXO EM LINGUAGEM PEDAGÓGICA OFICIAL DA BNCC/SAEB.\n"
                            f"Se houver nomes de arquivos brutos (ex: 'REVISAO_AVALIAÇÃO_6ANO...'), substitua por tópicos matemáticos reais e formais (ex: 'Recomposição de Frações, Divisibilidade, Operações e Perímetro').\n"
                            f"Mantenha todas as tags [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS], [OBJETIVOS_ENSINO], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO] e [ESTRATEGIA_DUA_PEI].\n\n"
                            f"PLANO ATUAL:\n{txt_bruto}"
                        )
                        st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_harm, usar_busca=False)
                        st.toast("✅ Plano harmonizado com sucesso!", icon="✨")
                        st.rerun()

                # 2. BLOCO DE CÓPIA DIRETA PARA O PROFESSOR
                with st.expander("📋 COPIAR TEXTO FORMATADO DO PLANO (ÁREA DE TRANSFERÊNCIA)", expanded=False):
                    st.caption("Clique no ícone de cópia no canto superior direito do bloco abaixo para copiar o texto formatado:")
                    st.code(st.session_state.p_temp, language=None)

                # 3. REFINADOR DE COAUTORIA
                cmd_refine = st.chat_input("Refinador IA (Ex: 'Detalhe melhor a explicação da Aula 1')", key=f"chat_refine_ponto_{v}")
                if cmd_refine:
                    with st.spinner("Reescrevendo plano com suas instruções..."):
                        prompt_refino = f"ORDEM DE AJUSTE: {cmd_refine}\n\nPLANO ATUAL:\n{st.session_state.p_temp}"
                        st.session_state.p_temp = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino, usar_busca=False)
                        st.rerun()

            # 4. ABAS DE EDIÇÃO DOS CAMPOS PADRONIZADOS
            tab_curriculo, tab_roteiro, tab_inclusao = st.tabs([
                "📚 1. Base Curricular & BNCC", 
                "📝 2. Roteiro das Aulas", 
                "♿ 3. Avaliação & PEI"
            ])
            
            with tab_curriculo:
                ed_hab = st.text_input("Habilidade BNCC / Descritores:", ai.extrair_tag(txt_bruto, "HABILIDADE_BNCC") or "EF06MA01", key=f"frag_hab_{v}")
                ed_comp = st.text_input("Competências Específicas BNCC (Pág. 267):", ai.extrair_tag(txt_bruto, "COMPETENCIAS_FOCO") or "Competência Específica 2 (Raciocínio Lógico) e 6 (Enfrentar Situações-Problema)", key=f"frag_comp_{v}")
                ed_geral = st.text_input("Objeto de Conhecimento / Unidade Temática:", ai.extrair_tag(txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL") or "RECOMPOSIÇÃO DE APRENDIZAGEM & REVISÃO", key=f"frag_geral_{v}")
                ed_espec = st.text_area("Conteúdos Específicos:", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS") or txt_bruto, height=130, key=f"frag_espec_{v}")
                ed_objs = st.text_area("Objetivos de Aprendizagem:", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO") or "Consolidar os objetos de conhecimento e superar as lacunas observadas nas avaliações.", height=130, key=f"frag_objs_{v}")
            
            with tab_roteiro:
                c_a1, c_a2, c_a3 = st.columns(3)
                ed_a1 = c_a1.text_area("AULA 1 (Início ➔ Meio ➔ Fim):", ai.extrair_tag(txt_bruto, "AULA_1"), height=380, key=f"frag_a1_{v}")
                ed_a2 = c_a2.text_area("AULA 2 (Início ➔ Meio ➔ Fim):", ai.extrair_tag(txt_bruto, "AULA_2"), height=380, key=f"frag_a2_{v}")
                ed_sab = c_a3.text_area("SÁBADO LETIVO:", ai.extrair_tag(txt_bruto, "SABADO_LETIVO") or "N/A", height=380, key=f"frag_sab_{v}")
                
            with tab_inclusao:
                ed_ava = st.text_area("Avaliação de Mérito:", ai.extrair_tag(txt_bruto, "AVALIACAO_DE_MERITO") or "Observação direta do engajamento e correção das atividades do caderno.", height=150, key=f"frag_ava_{v}")
                ed_pei = st.text_area("Estratégia DUA/PEI:", ai.extrair_tag(txt_bruto, "ESTRATEGIA_DUA_PEI") or "Utilização de cadernos adaptados (PEI N1, N2 e N3) com suporte visual e mediação individualizada.", height=150, key=f"frag_pei_{v}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # 5. BOTÃO DE SALVAMENTO FINAL NO BANCO DE DADOS E DRIVE
            if st.button("💾 SALVAR PLANO NO BANCO DE DADOS E NO DRIVE", use_container_width=True, type="primary", key=f"frag_btn_save_{v}"):
                with st.status("Gerando DOCX e Sincronizando com o Google Drive...", expanded=True) as status:
                    ano_fmt_s = meta.get('ano', '6º')
                    sem_fmt_s = meta.get('semana', 'Semana Geral')
                    trim_fmt_s = meta.get('trimestre', 'I Trimestre')
                    
                    nome_arquivo = f"PLANO_{str(ano_fmt_s).replace('º','')}_{str(sem_fmt_s).replace(' ', '')}"
                    db.excluir_plano_completo(sem_fmt_s, ano_fmt_s)
                    
                    metodologia_docx = f"AULA 01:\n{ed_a1}"
                    if "N/A" not in ed_a2.upper() and len(ed_a2) > 5: 
                        metodologia_docx += f"\n\nAULA 02:\n{ed_a2}"
                    if "N/A" not in ed_sab.upper() and len(ed_sab) > 5: 
                        metodologia_docx += f"\n\nSÁBADO LETIVO:\n{ed_sab}"
                    
                    dados_docx = {
                        "geral": ed_geral, 
                        "especificos": ed_espec, 
                        "objetivos": ed_objs, 
                        "recursos": meta.get('base', 'Acervo Didático SOSA'), 
                        "metodologia": metodologia_docx,
                        "avaliacao": ed_ava, 
                        "pei": ed_pei
                    }
                    
                    status.write("📄 Gerando arquivo Word DOCX Oficial...")
                    doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(
                        nome_arquivo, dados_docx, {"ano": ano_fmt_s, "semana": sem_fmt_s, "trimestre": trim_fmt_s}
                    )
                    
                    status.write("📤 Enviando para a Pasta de Planos no Google Drive...")
                    link_drive = db.subir_e_converter_para_google_docs(
                        doc_io, nome_arquivo, trimestre=trim_fmt_s, categoria=ano_fmt_s, semana=sem_fmt_s, modo="PLANEJAMENTO"
                    )
                    
                    status_banco = meta.get("status_final", "PRODUZIDO")

                    final_txt = (
                        f"[HABILIDADE_BNCC] {ed_hab} \n"
                        f"[COMPETENCIAS_FOCO] {ed_comp} \n"
                        f"[OBJETO_CONHECIMENTO] {ed_geral} \n"
                        f"[CONTEUDOS_ESPECIFICOS] {ed_espec} \n"
                        f"[OBJETIVOS_ENSINO] {ed_objs} \n"
                        f"[AULA_1] {ed_a1} \n"
                        f"[AULA_2] {ed_a2} \n"
                        f"[SABADO_LETIVO] {ed_sab} \n"
                        f"[AVALIACAO_DE_MERITO] {ed_ava} \n"
                        f"[ESTRATEGIA_DUA_PEI] {ed_pei} \n"
                        f"--- LINK DRIVE --- {link_drive}"
                    )
                    
                    db.salvar_no_banco("DB_PLANOS", [
                        datetime.now().strftime("%d/%m/%Y"), sem_fmt_s, ano_fmt_s, trim_fmt_s, status_banco, final_txt, link_drive
                    ])
                    
                    status.update(label="✅ Plano Sincronizado no Banco de Dados e Google Drive!", state="complete")
                    st.balloons()
                    time.sleep(1.2)
                    reset_planejamento()

    renderizar_mesa_lapidacao_plano()

    # ==============================================================================
    # ABA 2: HUB DE PRODUÇÃO & BAIXA LIMPA OFFLINE
    # ==============================================================================
    with tab_producao:
        st.markdown("#### Hub de Produção de Materiais & Baixa Limpa")
        st.caption("Planos aprovados aguardando a geração dos materiais com IA ou a baixa por aula com Livro Didático / Evento.")
        
        if not df_planos.empty:
            planos_ativos = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]
            if not planos_ativos.empty:
                for _, row in planos_ativos.iterrows():
                    with st.container(border=True):
                        c_p1, c_p2, c_p3, c_p4 = st.columns([2, 1, 1.2, 1])
                        c_p1.markdown(f"**{row['SEMANA']}** | Série: {row['ANO']} ({row['TURMA']})")
                        c_p1.caption("Status: ⏳ HUB ATIVO (Aguardando Produção / Execução)")
                        
                        if c_p2.button("🚀 Gerar Material IA", key=f"gen_hub_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = str(row["PLANO_TEXTO"])
                            st.session_state.sosa_id_atual = util.gerar_sosa_id("AULA", row['ANO'], row["TURMA"])
                            st.session_state.lab_meta = {
                                "ano": str(row['ANO']).replace("º",""), 
                                "trimestre": row["TURMA"], 
                                "tipo": "PRODUÇÃO_HUB", 
                                "semana_ref": row['SEMANA']
                            }
                            navegar_para("🧪 Criador de Aulas")

                        with c_p3.popover("📖 Baixa: Livro Didático"):
                            st.info("💡 **Baixa Limpa sem IA:** Registre os detalhes da aula ministrada pelo livro sem poluir o banco de arquivos.")
                            txt_obs_manual = st.text_input("Detalhes (Ex: Livro A Conquista - Págs. 184 a 187):", key=f"txt_man_obs_hub_{row.name}")
                            data_exec_livro = st.date_input("Data da Execução:", date.today(), format="DD/MM/YYYY", key=f"dt_livro_hub_{row.name}")
                            
                            if st.button("💾 CONFIRMAR BAIXA POR LIVRO", type="primary", key=f"btn_conf_man_hub_{row.name}"):
                                dt_str_livro = data_exec_livro.strftime("%d/%m/%Y")
                                db.dar_baixa_aula_livro_offline(
                                    semana=row['SEMANA'], 
                                    ano=row['ANO'], 
                                    turma=row['TURMA'], 
                                    data_str=dt_str_livro, 
                                    detalhes_livro=txt_obs_manual
                                )
                                st.success("✅ Plano concluído por Livro Didático e registrado no Diário com sucesso!")
                                st.balloons(); time.sleep(1); st.rerun()

                        with c_p4.popover("🛑 Baixa: Evento/Feriado"):
                            st.info("💡 **Conclusão por Calendário:** Arquive esta semana devido a feriado, evento ou aplicação de exames.")
                            motivo_evento = st.selectbox("Motivo:", ["Feriado / Recesso", "Semana de Provas Globais", "Conselho de Classe / Evento"], key=f"mot_ev_hub_{row.name}")
                            
                            if st.button("🛑 ARQUIVAR SEMANA", key=f"fin_hub_ev_{row.name}", use_container_width=True):
                                db.dar_baixa_plano_evento(
                                    semana=row['SEMANA'], 
                                    ano=row['ANO'], 
                                    motivo_ou_status=motivo_evento
                                )
                                st.success("✅ Semana arquivada no planejamento!")
                                time.sleep(1); st.rerun()
            else: st.success("🎉 Nenhum plano pendente de produção no Hub.")

    # ==============================================================================
    # ABA 3: ACERVO DE PLANOS & RELOCADOR DE SEMANAS EM CASCATA
    # ==============================================================================
    with tab_acervo:
        st.markdown("#### Acervo de Planos Estratégicos")
        if not df_planos.empty:
            f_ano_h = st.selectbox("Filtrar por Série:", ["Todos", "6º", "7º", "8º", "9º"], key="hist_ano")
            df_h = df_planos[df_planos["ANO"] == f_ano_h] if f_ano_h != "Todos" else df_planos.copy()
            
            if not df_h.empty:
                sel_h = st.selectbox("Selecionar Plano:", df_h["SEMANA"].tolist()[::-1], key="hist_sem")
                dados_h = df_h[df_h["SEMANA"] == sel_h].iloc[0]
                
                link_atual = str(dados_h.get("LINK_DRIVE", ""))
                is_corrupted = "html" in link_atual.lower() or "Page Not Found" in link_atual or not link_atual.startswith("http")
                
                if is_corrupted:
                    st.error("⚠️ **Detector de Falhas:** O link deste arquivo precisa de recuperação.")
                    if st.button("🔄 RECONSTRUIR DOCUMENTO E RECUPERAR LINK NO DRIVE", type="primary", use_container_width=True, key=f"heal_btn_{sel_h.replace(' ','')}"):
                        with st.status("Reconstruindo...", expanded=True) as status:
                            plano_txt_bruto = str(dados_h['PLANO_TEXTO'])
                            
                            ed_geral = ai.extrair_tag(plano_txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(plano_txt_bruto, "CONTEUDO_GERAL") or "Planejamento Semanal"
                            ed_espec = ai.extrair_tag(plano_txt_bruto, "CONTEUDOS_ESPECIFICOS")
                            ed_objs = ai.extrair_tag(plano_txt_bruto, "OBJETIVOS_ENSINO")
                            ed_a1 = ai.extrair_tag(plano_txt_bruto, "AULA_1")
                            ed_a2 = ai.extrair_tag(plano_txt_bruto, "AULA_2")
                            ed_sab = ai.extrair_tag(plano_txt_bruto, "SABADO_LETIVO")
                            
                            metodologia_docx = f"AULA 01:\n{ed_a1}"
                            if "N/A" not in ed_a2.upper() and len(ed_a2) > 5: metodologia_docx += f"\n\nAULA 02:\n{ed_a2}"
                            if "N/A" not in ed_sab.upper() and len(ed_sab) > 5: metodologia_docx += f"\n\nSÁBADO LETIVO:\n{ed_sab}"
                            
                            dados_docx = {
                                "geral": ed_geral, "especificos": ed_espec, "objetivos": ed_objs, 
                                "recursos": "Livro Didático", 
                                "metodologia": metodologia_docx,
                                "avaliacao": ai.extrair_tag(plano_txt_bruto, "AVALIACAO_DE_MERITO"), 
                                "pei": ai.extrair_tag(plano_txt_bruto, "ESTRATEGIA_DUA_PEI")
                            }
                            
                            nome_arquivo = f"PLANO_{dados_h['ANO'].replace('º','')}_{sel_h.replace(' ', '')}"
                            doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": dados_h['ANO'], "semana": sel_h, "trimestre": dados_h['TURMA']})
                            
                            link_novo = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=dados_h['TURMA'], categoria=dados_h['ANO'], semana=sel_h, modo="PLANEJAMENTO")
                            
                            if "https" in link_novo and len(link_novo) < 250:
                                try:
                                    wb = db.conectar()
                                    ws = wb.worksheet("DB_PLANOS")
                                    dados_sheet = ws.get_all_values()
                                    
                                    for row_idx, row in enumerate(dados_sheet):
                                        if row_idx > 0 and row[1] == sel_h and row[2] == dados_h['ANO']:
                                            ws.update_cell(row_idx+1, 7, link_novo)
                                            novo_plano_texto = plano_txt_bruto.split("--- LINK DRIVE ---")[0] + f"--- LINK DRIVE --- {link_novo}"
                                            ws.update_cell(row_idx+1, 6, novo_plano_texto)
                                            break
                                    
                                    status.update(label="✅ Documento Recuperado!", state="complete")
                                    st.balloons(); st.cache_data.clear(); time.sleep(1.2); st.rerun()
                                except Exception as e: st.error(f"Erro ao salvar no banco: {e}")
                            else:
                                status.update(label="❌ Falha na recuperação.", state="error")
                                st.error(link_novo)
                else:
                    c_btn1, c_btn2 = st.columns(2)
                    c_btn1.link_button("📂 Abrir DOCX no Drive", link_atual, use_container_width=True)
                    if c_btn2.button("🗑️ Apagar Plano", use_container_width=True, key=f"del_plan_h_{sel_h.replace(' ', '')}"):
                        if db.excluir_plano_completo(sel_h, dados_h["ANO"]): st.rerun()

                    @st.fragment
                    def renderizar_relocador_fragmento():
                        with st.expander("🔄 Mover este Plano e Aulas para Outra Semana", expanded=False):
                            st.info("💡 Altera a semana do plano e de todas as suas aulas no banco sem apagar os arquivos no Drive.")
                            
                            todas_semanas_reloc = util.gerar_semanas()
                            semanas_ocupadas_ano = df_planos[df_planos['ANO'] == dados_h['ANO']]['SEMANA'].tolist()
                            semanas_livres_reloc = [s.split(" (")[0] for s in todas_semanas_reloc if s.split(" (")[0] not in semanas_ocupadas_ano and "Jornada" not in s]
                            
                            if not semanas_livres_reloc:
                                st.warning("Todas as semanas deste ano letivo já possuem planos cadastrados.")
                            else:
                                nova_semana_dest = st.selectbox("Selecione a Semana de Destino:", semanas_livres_reloc, key=f"reloc_sem_{sel_h.replace(' ','')}")
                                
                                if st.button("🚀 CONFIRMAR MUDANÇA DE SEMANA EM CASCATA", type="primary", use_container_width=True, key=f"btn_reloc_exe_{sel_h.replace(' ','')}"):
                                    with st.spinner("Transferindo plano e aulas em cascata..."):
                                        sucesso_reloc = db.relocador_plano_semana(
                                            semana_antiga=sel_h, 
                                            ano=dados_h['ANO'], 
                                            nova_semana=nova_semana_dest, 
                                            link_drive=link_atual
                                        )
                                        if sucesso_reloc:
                                            st.success(f"✅ Plano transferido para {nova_semana_dest}!")
                                            st.balloons(); time.sleep(1.2); st.rerun()
                                        else: st.error("Erro ao transferir a semana.")

                    renderizar_relocador_fragmento()
            else: st.info("Nenhum plano encontrado.")

    # ==============================================================================
    # ABA 4: INTELIGÊNCIA CURRICULAR & ASSISTENTE DE CONCILIAÇÃO CRONOLÓGICA
    # ==============================================================================
    with tab_inteligencia:
        st.markdown("### 🧠 Inteligência Curricular e Planejamento Trimestral")
        
        modo_inteligencia = st.segmented_control(
            "Selecione a Visão:", 
            ["📊 Status de Execução (Checklist)", "🖨️ Gerador de Plano Trimestral", "⚡ Conciliador Cronológico"], 
            default="📊 Status de Execução (Checklist)",
            key=f"seg_intel_{v}"
        )
        st.markdown("---")

        def limpar_tags_cite(texto):
            if not isinstance(texto, str): return ""
            return re.sub(r'\[cite:.*?\]', '', texto).strip()

        if modo_inteligencia == "📊 Status de Execução (Checklist)":
            st.caption("O sistema cruza os conteúdos do CSV com os planos gerados no Ponto ID.")
            c1, c2 = st.columns(2)
            ano_c = c1.selectbox("Série:", [6, 7, 8, 9], key="matriz_ano")
            trim_c = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="matriz_trim")
            
            col_ano = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None) if not df_curriculo.empty else None
            col_eixo = next((c for c in df_curriculo.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None) if not df_curriculo.empty else None
            col_trim = next((c for c in df_curriculo.columns if trim_c.upper() in c.upper()), None) if not df_curriculo.empty else None

            if col_ano and col_eixo and col_trim:
                df_c = df_curriculo[df_curriculo[col_ano].astype(str).str.contains(str(ano_c))].copy()
                
                if not df_c.empty:
                    dados_checklist = []
                    planos_feitos = df_planos[(df_planos["ANO"].astype(str).str.contains(str(ano_c))) & (df_planos["TURMA"] == trim_c)] if not df_planos.empty else pd.DataFrame()
                    texto_soberano = " | ".join([ai.extrair_tag(p, "CONTEUDOS_ESPECIFICOS").upper() for p in planos_feitos["PLANO_TEXTO"]]) if not planos_feitos.empty else ""
                    texto_soberano_limpo = re.sub(r'[^A-Z0-9]', '', texto_soberano)

                    for _, row in df_c.iterrows():
                        eixo = row[col_eixo]
                        conteudos_brutos = limpar_tags_cite(row[col_trim])
                        topicos = [t.strip() for t in conteudos_brutos.split(';') if t.strip()]
                        
                        for topico in topicos:
                            target = re.sub(r'[^A-Z0-9]', '', topico.upper())
                            status = "✅ CONCLUÍDO" if target in texto_soberano_limpo and len(target) > 5 else "⏳ PENDENTE"
                            dados_checklist.append({"Unidade Temática (Eixo)": eixo, "Conteúdo Específico": topico, "Status": status})
                    
                    if dados_checklist:
                        df_check = pd.DataFrame(dados_checklist)
                        concluidos = len(df_check[df_check['Status'] == "✅ CONCLUÍDO"])
                        total = len(df_check)
                        progresso = (concluidos / total) * 100 if total > 0 else 0
                        
                        st.progress(progresso / 100)
                        st.caption(f"**Progresso do Trimestre:** {concluidos} de {total} tópicos concluídos ({progresso:.1f}%)")
                        
                        def colorir_status(val):
                            if "CONCLUÍDO" in str(val): return 'color: #2ECC71; font-weight: bold;'
                            return 'color: #F1C40F; font-weight: bold;'
                            
                        st.dataframe(df_check.style.map(colorir_status, subset=['Status']), use_container_width=True, hide_index=True)
                    else: st.info("Nenhum conteúdo cadastrado para este trimestre no CSV.")
            else: st.error("As colunas do currículo não correspondem ao formato esperado.")

        elif modo_inteligencia == "🖨️ Gerador de Plano Trimestral":
            st.markdown("#### Gerador Automático de Plano Trimestral (DOCX)")
            c_t1, c_t2 = st.columns(2)
            ano_trim = c_t1.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"])
            trim_alvo = c_t2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
            ano_num_trim = "".join(filter(str.isdigit, ano_trim))
            
            if st.button("🖨️ Extrair Dados e Gerar Documento Oficial", type="primary", use_container_width=True):
                with st.spinner("Minerando planos e compilando documento..."):
                    col_ano = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None) if not df_curriculo.empty else None
                    col_eixo = next((c for c in df_curriculo.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None) if not df_curriculo.empty else None
                    col_trim = next((c for c in df_curriculo.columns if trim_alvo.upper() in c.upper()), None) if not df_curriculo.empty else None
                    
                    if not col_ano or not col_eixo or not col_trim:
                        st.error("Erro na leitura das colunas do CSV.")
                        st.stop()
                        
                    df_matriz_trim = df_curriculo[df_curriculo[col_ano].astype(str).str.contains(ano_num_trim)].copy()
                    
                    if df_matriz_trim.empty:
                        st.error("Nenhum dado encontrado na matriz para esta série.")
                    else:
                        planos_trim = df_planos[(df_planos['ANO'].str.contains(ano_num_trim)) & (df_planos['TURMA'] == trim_alvo)] if not df_planos.empty else pd.DataFrame()
                        
                        bncc_codes = set()
                        metodologias = set()
                        
                        if not planos_trim.empty:
                            for txt in planos_trim['PLANO_TEXTO'].dropna():
                                hab = ai.extrair_tag(str(txt), "HABILIDADE_BNCC")
                                codes = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', hab, re.IGNORECASE)
                                bncc_codes.update([c.upper() for c in codes])
                                
                                aula1 = ai.extrair_tag(str(txt), "AULA_1").lower()
                                if "prática" in aula1 or "quadro" in aula1: metodologias.add("Exposição dialogada e resolução no quadro")
                                if "livro" in aula1 or "página" in aula1: metodologias.add("Leitura e fixação no livro didático")
                                if "tecnologia" in aula1 or "news" in aula1: metodologias.add("Sensibilização com notícias e tecnologia")
                                if "jogo" in aula1 or "lúdico" in aula1: metodologias.add("Atividades lúdicas e desafios")
                                if "revisão" in aula1 or "correção" in aula1: metodologias.add("Revisão e recomposição de aprendizagem")
                        
                        if not metodologias:
                            metodologias = {"Aulas expositivas e dialogadas", "Resolução de exercícios de fixação", "Uso do livro didático"}
                            
                        hab_str = ", ".join(sorted(list(bncc_codes))) if bncc_codes else "Habilidades trabalhadas conforme planos semanais."
                        met_str = "• " + "\n• ".join(sorted(list(metodologias)))
                        
                        dados_tabela = []
                        for _, row in df_matriz_trim.iterrows():
                            eixo = str(row[col_eixo]).strip()
                            conteudos = limpar_tags_cite(row[col_trim]).replace(";", ";\n")
                            
                            if conteudos and conteudos.upper() != "NAN":
                                dados_tabela.append({
                                    "eixo": eixo, "conteudos": conteudos,
                                    "habilidades": hab_str, "metodologia": met_str
                                })
                        
                        info_trim = {"trimestre": trim_alvo, "ano": ano_trim}
                        nome_arq = f"PLANEJAMENTO_TRIMESTRAL_{trim_alvo.replace(' ', '')}_{ano_trim.replace('º ', '')}"
                        
                        doc_stream = exporter.gerar_docx_planejamento_trimestral(nome_arq, info_trim, dados_tabela)
                        link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq, trimestre=trim_alvo, categoria=ano_trim, modo="PLANEJAMENTO")
                        
                        if "https" in link_doc:
                            st.success("✅ Plano Trimestral gerado com sucesso!")
                            st.link_button("📂 ABRIR DOCUMENTO OFICIAL", link_doc, type="primary", use_container_width=True)
                            st.balloons()
                        else: st.error(f"Erro ao salvar no Drive: {link_doc}")

        elif modo_inteligencia == "⚡ Conciliador Cronológico":
            with st.container(border=True):
                st.markdown("#### ⚡ Assistente de Conciliação e Re-indexação de Semanas")
                st.caption("Reorganiza cronologicamente as semanas invertidas ou saltadas do DB_PLANOS e vincula automaticamente as aulas avulsas do diário.")
                
                c_conc1, c_conc2 = st.columns([1, 1])
                ano_conc_sel = c_conc1.selectbox("Série para Conciliar:", ["6º", "7º", "8º", "9º"], key=f"sel_ano_conc_{v}")
                
                if c_conc2.button("🚀 EXECUTAR CONCILIAÇÃO E RE-INDEXAÇÃO CRONOLÓGICA", type="primary", use_container_width=True, key=f"btn_run_conc_{v}"):
                    with st.status(f"Reconciliando semanas do {ano_conc_sel} Ano no banco de dados...", expanded=True) as status_conc:
                        status_conc.write("🔍 Analisando datas de criação e ordenando cronologicamente...")
                        sucesso_c = db.conciliar_calendario_e_planos_cronologicos(ano_conc_sel)
                        
                        if sucesso_c:
                            status_conc.update(label="✅ Semanas re-indexadas e aulas avulsas vinculadas com sucesso!", state="complete")
                            st.balloons(); time.sleep(1.2); st.rerun()
                        else:
                            status_conc.update(label="⚠️ Erro ao conciliar dados ou nenhum registro encontrado.", state="error")








# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO RÁPIDO - V2026.MOBILE_TOUCH (SOSA MASTER)
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("📝 Diário de Bordo Rápido")
    st.caption("Lançamento em tempo real adaptado para Smartphone (Touch) e Desktop com Auto-Isenção de Vistos.")
    st.markdown("---")

    if "v_diario_rapido" not in st.session_state:
        st.session_state.v_diario_rapido = int(time.time())
    v_dr = st.session_state.v_diario_rapido

    lista_turmas_diario = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_diario = sorted(turmas_reais['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_diario = sorted(df_alunos['TURMA'].unique())

    if not lista_turmas_diario:
        st.warning("⚠️ Nenhuma turma cadastrada no sistema. Cadastre as turmas no cockpit de Gestão da Turma.")
    else:
        with st.container(border=True):
            c_d1, c_d2 = st.columns([1.5, 1])
            turma_dr = c_d1.selectbox("👥 Selecione a Turma:", lista_turmas_diario, key=f"dr_turma_{v_dr}")
            data_dr = c_d2.date_input("📅 Data da Aula:", date.today(), format="DD/MM/YYYY", key=f"dr_data_{v_dr}")
            data_dr_str = data_dr.strftime("%d/%m/%Y")

        alunos_dr = df_alunos[df_alunos['TURMA'] == turma_dr].sort_values(by="NOME_ALUNO") if not df_alunos.empty else pd.DataFrame()

        if alunos_dr.empty:
            st.warning(f"⚠️ Nenhum aluno encontrado na turma {turma_dr}.")
        else:
            aula_registro = df_registro_aulas[(df_registro_aulas['DATA'] == data_dr_str) & (df_registro_aulas['TURMA'] == turma_dr)] if not df_registro_aulas.empty else pd.DataFrame()
            conteudo_aula_hoje = aula_registro.iloc[0]['CONTEUDO_MINISTRADO'] if not aula_registro.empty else "Registro Rápido de Sala"

            st.info(f"📌 **Aula Registrada ({data_dr_str}):** {conteudo_aula_hoje}")
            diario_dia_atual = df_diario[(df_diario['DATA'] == data_dr_str) & (df_diario['TURMA'] == turma_dr)] if not df_diario.empty else pd.DataFrame()

            @st.fragment
            def renderizar_diario_rapido_fragmento():
                key_presenca = f"dr_presencas_{turma_dr}_{data_dr_str}"
                key_vistos = f"dr_vistos_{turma_dr}_{data_dr_str}"
                key_tags = f"dr_tags_{turma_dr}_{data_dr_str}"
                key_obs = f"dr_obs_{turma_dr}_{data_dr_str}"

                if key_presenca not in st.session_state:
                    st.session_state[key_presenca] = {}
                    st.session_state[key_vistos] = {}
                    st.session_state[key_tags] = {}
                    st.session_state[key_obs] = {}

                    for _, alu in alunos_dr.iterrows():
                        id_l = db.limpar_id(alu['ID'])
                        reg_existente = diario_dia_atual[diario_dia_atual['ID_ALUNO'].apply(db.limpar_id) == id_l] if not diario_dia_atual.empty else pd.DataFrame()
                        
                        if not reg_existente.empty:
                            tag_exist = str(reg_existente.iloc[-1].get('TAGS', ''))
                            visto_exist = str(reg_existente.iloc[-1].get('VISTO_ATIVIDADE', '')).upper()
                            obs_exist = str(reg_existente.iloc[-1].get('OBSERVACOES', ''))

                            st.session_state[key_presenca][id_l] = False if tag_exist == "AUSÊNCIA" else True
                            st.session_state[key_vistos][id_l] = True if visto_exist == "TRUE" else False
                            st.session_state[key_tags][id_l] = tag_exist if tag_exist != "AUSÊNCIA" else ""
                            st.session_state[key_obs][id_l] = obs_exist
                        else:
                            st.session_state[key_presenca][id_l] = True
                            st.session_state[key_vistos][id_l] = False
                            st.session_state[key_tags][id_l] = ""
                            st.session_state[key_obs][id_l] = ""

                modo_view_dr = st.segmented_control(
                    "Visualização da Classe:",
                    ["📱 Smartphone (Cards Touch)", "💻 Desktop (Tabela Tátil)"],
                    default="📱 Smartphone (Cards Touch)",
                    key=f"dr_view_mode_{v_dr}"
                )

                c_m1, c_m2, c_m3 = st.columns(3)
                if c_m1.button("🟢 Todos Presentes", use_container_width=True, key=f"btn_all_p_{v_dr}"):
                    for al_id in st.session_state[key_presenca]: st.session_state[key_presenca][al_id] = True
                    st.rerun()

                if c_m2.button("📘 Todos com Visto", use_container_width=True, key=f"btn_all_v_{v_dr}"):
                    for al_id in st.session_state[key_vistos]: st.session_state[key_vistos][al_id] = True
                    st.rerun()

                if c_m3.button("🔄 Resetar Formulário", use_container_width=True, key=f"btn_res_dr_{v_dr}"):
                    del st.session_state[key_presenca]; del st.session_state[key_vistos]
                    del st.session_state[key_tags]; del st.session_state[key_obs]
                    st.rerun()

                st.markdown("---")

                if "Smartphone" in modo_view_dr:
                    filtro_mob = st.pills(
                        "Filtro de Exibição:", 
                        ["Todos", "🔴 Faltosos", "📘 Com Visto", "⚪ Sem Visto"], 
                        default="Todos",
                        key=f"flt_mob_pills_{v_dr}"
                    )

                    def icone_perfil(nec):
                        n = str(nec).upper().strip()
                        if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                        if "DEFASAGEM LEITURA" in n: return "🧱"
                        if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
                        if "ALTA PERFORMANCE" in n: return "🚀"
                        if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                        return "♿"

                    options_tags_mob = ["⭐ +0.5", "💬 Conversa", "📱 Celular", "🧱 Def. Leitura", "🧮 Def. Mat.", "📉 -0.5"]

                    for _, alu in alunos_dr.iterrows():
                        id_l = db.limpar_id(alu['ID'])
                        nome_a = alu['NOME_ALUNO']
                        is_pres = st.session_state[key_presenca].get(id_l, True)
                        is_visto = st.session_state[key_vistos].get(id_l, False)

                        if filtro_mob == "🔴 Faltosos" and is_pres: continue
                        if filtro_mob == "📘 Com Visto" and not is_visto: continue
                        if filtro_mob == "⚪ Sem Visto" and is_visto: continue

                        with st.container(border=True):
                            c_card1, c_card2, c_card3 = st.columns([2, 1, 1])
                            c_card1.markdown(f"**{icone_perfil(alu['NECESSIDADES'])} {nome_a}**")
                            
                            lbl_pres = "🟢 PRESENTE" if is_pres else "🔴 FALTOU"
                            if c_card2.button(lbl_pres, key=f"btn_p_mob_{id_l}_{v_dr}", use_container_width=True):
                                st.session_state[key_presenca][id_l] = not is_pres
                                st.rerun()

                            lbl_visto = "📘 VISTO OK" if is_visto else "⚪ SEM VISTO"
                            if c_card3.button(lbl_visto, key=f"btn_v_mob_{id_l}_{v_dr}", use_container_width=True):
                                st.session_state[key_vistos][id_l] = not is_visto
                                st.rerun()

                            if is_pres:
                                val_tag_atual = st.session_state[key_tags].get(id_l, None)
                                default_tag_mob = val_tag_atual if val_tag_atual in options_tags_mob else None

                                tag_sel_mob = st.segmented_control(
                                    "Ocorrência / Bônus:",
                                    options_tags_mob,
                                    default=default_tag_mob,
                                    key=f"seg_tag_mob_{id_l}_{v_dr}"
                                )
                                st.session_state[key_tags][id_l] = tag_sel_mob if tag_sel_mob else ""

                            obs_mob = st.text_input(
                                "Observação (Use o Ditado por Voz do celular):",
                                value=st.session_state[key_obs].get(id_l, ""),
                                key=f"inp_obs_mob_{id_l}_{v_dr}",
                                placeholder="Digite ou dite uma anotação..."
                            )
                            st.session_state[key_obs][id_l] = obs_mob

                else:
                    dados_grid = []
                    for _, alu in alunos_dr.iterrows():
                        id_l = db.limpar_id(alu['ID'])
                        def icone_perfil(nec):
                            n = str(nec).upper().strip()
                            if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                            if "DEFASAGEM LEITURA" in n: return "🧱"
                            if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
                            if "ALTA PERFORMANCE" in n: return "🚀"
                            if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                            return "♿"

                        dados_grid.append({
                            "ID": id_l,
                            "Estudante": f"{icone_perfil(alu['NECESSIDADES'])} {alu['NOME_ALUNO']}",
                            "Presente?": st.session_state[key_presenca].get(id_l, True),
                            "Visto OK?": st.session_state[key_vistos].get(id_l, False),
                            "Ocorrência / Tag": st.session_state[key_tags].get(id_l, ""),
                            "Observação Individual": st.session_state[key_obs].get(id_l, "")
                        })

                    df_grid_ed = st.data_editor(
                        pd.DataFrame(dados_grid),
                        hide_index=True, use_container_width=True, height=450,
                        column_config={
                            "ID": None,
                            "Estudante": st.column_config.TextColumn("Estudante", disabled=True, width="medium"),
                            "Presente?": st.column_config.CheckboxColumn("Presente?", default=True, width="small"),
                            "Visto OK?": st.column_config.CheckboxColumn("Visto OK?", default=False, width="small"),
                            "Ocorrência / Tag": st.column_config.SelectboxColumn("Ocorrência / Bônus", options=["", "⭐ DESTAQUE (+0.5)", "💬 CONVERSA/DESATENTO", "📱 USO DE CELULAR", "🧱 DEFASAGEM LEITURA", "🧮 DEFASAGEM MATEMÁTICA", "📉 INDISCIPLINA (-0.5)", "🕒 ATRASO"], width="medium"),
                            "Observação Individual": st.column_config.TextColumn("Observação Rápida", width="large")
                        },
                        key=f"ed_grid_dr_{v_dr}"
                    )

                    for _, r_ed in df_grid_ed.iterrows():
                        al_id = r_ed['ID']
                        st.session_state[key_presenca][al_id] = r_ed['Presente?']
                        st.session_state[key_vistos][al_id] = r_ed['Visto OK?']
                        st.session_state[key_tags][al_id] = str(r_ed['Ocorrência / Tag'])
                        st.session_state[key_obs][al_id] = str(r_ed['Observação Individual'])

                # BOTÃO FLUTUANTE DE SALVAMENTO COM CÁLCULO SEGURO (.iterrows)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 CONSOLIDAR E SALVAR DIÁRIO DO DIA", type="primary", use_container_width=True, key=f"btn_save_dr_{v_dr}"):
                    with st.spinner("Gravando presença, vistos e ocorrências em lote..."):
                        linhas_salvar = []
                        data_hoje_save = data_dr_str

                        # 🚨 CONTAGEM DE VISTOS CORRIGIDA E SEGURA COM .iterrows()
                        total_vistos_dados_hoje = 0
                        for _, alu_c in alunos_dr.iterrows():
                            al_id_c = db.limpar_id(alu_c['ID'])
                            if st.session_state[key_vistos].get(al_id_c, False) and st.session_state[key_presenca].get(al_id_c, True):
                                total_vistos_dados_hoje += 1

                        for _, alu in alunos_dr.iterrows():
                            al_id = db.limpar_id(alu['ID'])
                            nome_limpo = alu['NOME_ALUNO'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                            
                            is_presente = st.session_state[key_presenca].get(al_id, True)
                            is_visto_check = st.session_state[key_vistos].get(al_id, False)
                            tag_sel = str(st.session_state[key_tags].get(al_id, "")).strip()
                            obs_text = str(st.session_state[key_obs].get(al_id, "")).strip()

                            bônus_val = "0,00"
                            if "DESTAQUE" in tag_sel or "+0.5" in tag_sel: bônus_val = "0,50"
                            elif "INDISCIPLINA" in tag_sel or "-0.5" in tag_sel: bônus_val = "-0,50"

                            if not is_presente:
                                tag_final = "AUSÊNCIA"
                                visto_final = "FALSE"
                            else:
                                tag_final = tag_sel
                                # Se ninguém na turma ganhou visto hoje, marca ISENTO para proteger a média C1!
                                if total_vistos_dados_hoje == 0:
                                    visto_final = "ISENTO"
                                else:
                                    visto_final = "TRUE" if is_visto_check else "FALSE"

                            linhas_salvar.append([
                                data_hoje_save, al_id, nome_limpo, turma_dr,
                                visto_final, tag_final, obs_text, bônus_val
                            ])

                        if linhas_salvar:
                            db.limpar_diario_data_turma(data_hoje_save, turma_dr)
                            db.salvar_lote("DB_DIARIO_BORDO", linhas_salvar)
                            
                            if total_vistos_dados_hoje == 0:
                                st.toast("✅ Aula sem vistos registrada! Vistos marcados como ISENTO para não diminuir notas.", icon="🛡️")
                            else:
                                st.toast("✅ Diário de Bordo Consolidado com Sucesso!", icon="✅")
                                
                            st.balloons()
                            time.sleep(1)
                            st.rerun()

            renderizar_diario_rapido_fragmento()






# ==============================================================================
# MÓDULO: LABORATÓRIO DE PRODUÇÃO DIDÁTICA (CRIADOR DE AULAS) - V2026.ULTIMATE
# (INÍCIO/MEIO/FIM, LETRAMENTO BNCC, PEI ON-DEMAND COM PEI 3 ANCORADO E MODO TURBO 1-CLIQUE)
# ==============================================================================
elif menu == "🧪 Criador de Aulas":
    st.title("Laboratório de Produção Didática")
    st.caption("Desenvolva aulas de safra (Início ➔ Meio ➔ Fim), projetos interdisciplinares, listas de exercícios ancoradas no Livro Didático e adaptações PEI On-Demand.")
    st.markdown("---")
    
    if "v_lab" not in st.session_state: 
        st.session_state.v_lab = int(time.time())
    v = st.session_state.v_lab

    if "forja_aula" not in st.session_state:
        st.session_state.forja_aula = {
            'fase': 1, 'info': {}, 'links_web': '', 'qtd_q': 5, 'tipo_material': 'AULA',
            'teoria': '', 'reg_q': '', 'reg_gab': '', 'pei_1': '', 'pei_2': '', 'pei_3': '', 'pei_gab': '', 'nome_base': ''
        }
    
    fa = st.session_state.forja_aula

    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "sosa_id_atual", "lab_meta", "hub_origem", "chat_history_lab"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.session_state.forja_aula = {
            'fase': 1, 'info': {}, 'links_web': '', 'qtd_q': 5, 'tipo_material': 'AULA',
            'teoria': '', 'reg_q': '', 'reg_gab': '', 'pei_1': '', 'pei_2': '', 'pei_3': '', 'pei_gab': '', 'nome_base': ''
        }
        st.cache_data.clear() 
        st.session_state.v_lab = int(time.time())
        st.rerun()

    def extrair_memoria_aulas_trimestre(turma_ou_ano, trimestre):
        if df_registro_aulas.empty: return "", []
        ano_num = "".join(filter(str.isdigit, str(turma_ou_ano)))
        if not ano_num: return "", []
        
        df_reg_ano = df_registro_aulas[df_registro_aulas['TURMA'].astype(str).str.contains(ano_num)].copy()
        if df_reg_ano.empty: return "", []
        
        padrao_trim = trimestre
        df_reg_trim = df_reg_ano[
            df_reg_ano['CONTEUDO_MINISTRADO'].astype(str).str.contains(padrao_trim, regex=False, case=False, na=False) | 
            (df_reg_ano['SEMANA'].astype(str).str.contains(padrao_trim, regex=False, case=False, na=False))
        ]
        
        if df_reg_trim.empty: df_reg_trim = df_reg_ano.copy()
            
        conteudos_usados = df_reg_trim['CONTEUDO_MINISTRADO'].dropna().unique().tolist()
        semanas_usadas = df_reg_trim['SEMANA'].dropna().unique().tolist()
        
        paginas_livro = set()
        if not df_planos.empty:
            planos_rel = df_planos[(df_planos['ANO'].astype(str).str.contains(ano_num)) & (df_planos['SEMANA'].isin(semanas_usadas))]
            for _, r_p in planos_rel.iterrows():
                base_txt = ai.extrair_tag(str(r_p['PLANO_TEXTO']), "BASE_DIDATICA")
                if base_txt and "Livro" in base_txt:
                    paginas_livro.add(base_txt)
                    
        memoria_txt = f"--- MEMÓRIA DAS AULAS MINISTRADAS NO DIÁRIO ({turma_ou_ano} / {trimestre}) ---\n"
        memoria_txt += f"• Total de Aulas Efetivamente Concluídas: {len(df_reg_trim)}\n"
        if paginas_livro:
            memoria_txt += f"• Páginas do Livro Didático Trabalhadas: {', '.join(sorted(list(paginas_livro)))}\n"
        memoria_txt += "• Conteúdos e Tópicos Ministrados:\n  - " + "\n  - ".join(conteudos_usados) + "\n\n"
        
        return memoria_txt, conteudos_usados

    tab_forja, tab_acervo_lab = st.tabs(["Forja de Materiais", "Acervo Digital & Hub de Produção"])

    # ==============================================================================
    # ABA 1: FORJA DE MATERIAIS
    # ==============================================================================
    with tab_forja:
        if "lab_temp" in st.session_state:
            @st.fragment
            def renderizar_mesa_lapidacao_lab():
                txt_base = st.session_state.lab_temp
                s_id = st.session_state.get("sosa_id_atual", "SEM-ID")
                meta = st.session_state.get("lab_meta", {})
                st.success(f"Material em Edição: {s_id}")

                with st.container(border=True):
                    st.markdown("#### Ajuste de Coautoria (Maestro Copilot - Gemini 3.6 Flash)")
                    if "chat_history_lab" not in st.session_state:
                        st.session_state.chat_history_lab = [{"role": "assistant", "avatar": "🤖", "content": "Saudações, Mestre. O material base está na mesa. Como deseja refinar?"}]
                    
                    chat_container_lab = st.container(height=200)
                    with chat_container_lab:
                        for msg in st.session_state.chat_history_lab:
                            with st.chat_message(msg["role"], avatar=msg["avatar"]):
                                st.markdown(msg["content"])
                    
                    if cmd_refine_lab := st.chat_input("Instruções de alteração para a IA...", key=f"chat_lab_ref_{v}"):
                        st.session_state.chat_history_lab.append({"role": "user", "avatar": "💻", "content": cmd_refine_lab})
                        with chat_container_lab:
                            with st.chat_message("user", avatar="💻"): st.markdown(cmd_refine_lab)
                            with st.chat_message("assistant", avatar="🤖"):
                                with st.spinner("Ajustando material..."):
                                    hist_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history_lab[-5:]])
                                    prompt_refino = f"HISTÓRICO:\n{hist_text}\n\nORDEM: {cmd_refine_lab}\n\nCONTEÚDO:\n{txt_base}"
                                    resultado_refino = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino)
                                    msg_chat = ai.extrair_tag(resultado_refino, "MENSAGEM_CHAT") or "Ajustado com sucesso!"
                                    novo_conteudo = ai.extrair_tag(resultado_refino, "CONTEUDO_ATUALIZADO") or resultado_refino
                                    
                                    st.markdown(msg_chat)
                                    st.session_state.chat_history_lab.append({"role": "assistant", "avatar": "🤖", "content": msg_chat})
                                    st.session_state.lab_temp = novo_conteudo
                                    st.rerun()

                    if st.button("Descartar Edição e Voltar ao Início", use_container_width=True, key=f"btn_disc_lab_{v}"): 
                        reset_laboratorio()
                
                st.markdown("---")
                modo_leitura = st.toggle("👁️ Modo Leitura (Renderizar Matemática LaTeX)", value=False, key=f"read_mode_lab_{v}")
                
                val_prof = ai.extrair_tag(txt_base, "PROFESSOR") or ai.extrair_tag(txt_base, "JUSTIFICATIVA_PHC")
                val_alu = ai.extrair_tag(txt_base, "ALUNO") or ai.extrair_tag(txt_base, "PASSO_A_PASSO")
                val_gab = ai.extrair_tag(txt_base, "GABARITO") or ai.extrair_tag(txt_base, "RUBRICA_DE_MERITO")
                val_pei1 = ai.extrair_tag(txt_base, "PEI_NIVEL_1") or ai.extrair_tag(txt_base, "NIVEL_1") or ai.extrair_tag(txt_base, "PEI")
                val_pei3 = ai.extrair_tag(txt_base, "PEI_NIVEL_3") or ai.extrair_tag(txt_base, "NIVEL_3")
                val_img = ai.extrair_tag(txt_base, "IMAGENS")

                t_prof, t_alu, t_gab, t_pei_tab, t_img_tab, t_sync = st.tabs(["Guia Professor", "Folha Aluno", "Gabarito", "Adaptação PEI", "Imagens", "Sincronia"])
                
                with t_prof: 
                    if modo_leitura: st.markdown(preparar_para_leitura(val_prof))
                    else: ed_prof = st.text_area("Lousa/Mediação:", val_prof, height=350, key=f"ed_prof_reg_{v}")
                
                with t_alu: 
                    if modo_leitura: st.markdown(preparar_para_leitura(val_alu))
                    else: ed_alu = st.text_area("Folha/Roteiro:", val_alu, height=350, key=f"ed_alu_reg_{v}")
                
                with t_gab: 
                    if modo_leitura: st.markdown(preparar_para_leitura(val_gab))
                    else: ed_gab = st.text_area("Gabarito:", val_gab, height=200, key=f"ed_res_reg_{v}")
                
                with t_pei_tab: 
                    st.markdown("**🔵 PEI Nível 1 / Nível 2:**")
                    ed_pei1 = st.text_area("Nível 1/2:", val_pei1, height=200, key=f"ed_pei1_reg_{v}")
                    st.markdown("**🔴 PEI Nível 3 (Bento Cards + Rubrica):**")
                    ed_pei3 = st.text_area("Nível 3:", val_pei3, height=200, key=f"ed_pei3_reg_{v}")
                
                with t_img_tab: 
                    ed_img = st.text_area("Prompts de Imagem:", val_img, height=150, key=f"ed_img_reg_{v}")

                with t_sync:
                    st.markdown("#### 🚀 Sincronia e Custódia Digital Canônica")
                    if st.button("Sincronizar Ativos e Enviar para o Drive", use_container_width=True, type="primary", key=f"btn_triple_{v}"):
                        with st.status("Sincronizando Ativos Canônicos...") as status:
                            ano_str = f"{meta.get('ano', '6')}º" if "º" not in str(meta.get('ano', '6')) else str(meta.get('ano', '6'))
                            sem_ref = meta.get('semana_ref', 'Geral')
                            trim_ref = meta.get('trimestre', 'I Trimestre')
                            info_doc = {"ano": ano_str, "trimestre": trim_ref, "semana": sem_ref}

                            db.excluir_aula_pronta_canonica(semana_ref=sem_ref, tipo_material=s_id, ano=ano_str)

                            status.write("📄 Gerando Material do Aluno Word...")
                            doc_alu = exporter.gerar_docx_aluno_v24(s_id, ed_alu, info_doc)
                            link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{s_id}_ALUNO", modo="AULA")
                            
                            link_pei1 = "N/A"
                            if ed_pei1:
                                status.write("🔵 Gerando Material PEI N1 Word...")
                                doc_pei1 = exporter.gerar_docx_pei_v25(f"{s_id}_PEI_N1", ed_pei1, info_doc)
                                link_pei1 = db.subir_e_converter_para_google_docs(doc_pei1, f"{s_id}_PEI_N1", modo="AULA")
                            
                            link_pei3 = "N/A"
                            if ed_pei3:
                                status.write("🔴 Gerando Material PEI N3 (Bento Cards) Word...")
                                doc_pei3 = exporter.gerar_docx_pei_qualitativa(f"{s_id}_PEI_N3", ed_pei3, info_doc)
                                link_pei3 = db.subir_e_converter_para_google_docs(doc_pei3, f"{s_id}_PEI_N3", modo="AULA")

                            status.write("👨‍🏫 Gerando Guia do Professor Word...")
                            doc_prof = exporter.gerar_docx_professor_v25(s_id, ed_prof, info_doc)
                            link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{s_id}_PROF", modo="AULA")
                            
                            links_f = f"--- LINKS ---\nRegular({link_alu})\nPEI_N1({link_pei1})\nPEI_N3({link_pei3})\nProf({link_prof})"
                            conteudo_final = f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n[GABARITO]\n{ed_gab}\n\n[PEI_NIVEL_1]\n{ed_pei1}\n\n[PEI_NIVEL_3]\n{ed_pei3}\n\n[IMAGENS]\n{ed_img}\n\n{links_f}"
                            
                            db.salvar_no_banco("DB_AULAS_PRONTAS",[
                                datetime.now().strftime("%d/%m/%Y"), sem_ref, s_id, conteudo_final, ano_str, link_alu
                            ])
                            
                            db.dar_baixa_aula_livro_offline(semana=sem_ref, ano=ano_str, turma=trim_ref, data_str=datetime.now().strftime("%d/%m/%Y"), detalhes_livro=s_id)

                            status.update(label="✅ Sincronizado com Sucesso!", state="complete")
                            st.balloons(); time.sleep(1); reset_laboratorio()

            renderizar_mesa_lapidacao_lab()

        else:
            if fa['fase'] == 1:
                st.markdown("### 🎯 Painel de Configuração")
                
                tipo_criacao = st.pills(
                    "Tipo de Material a Desenvolver:", 
                    ["Aula de Safra (Teoria e Prática)", "Projeto ou Trabalho Interdisciplinar", "Lista Híbrida ou Recomposição de Elite"], 
                    default="Aula de Safra (Teoria e Prática)",
                    key=f"lab_pills_tipo_{v}"
                )
                
                if "Aula de Safra" in tipo_criacao:
                    fa['tipo_material'] = 'AULA'
                    with st.container(border=True):
                        st.markdown("#### 📦 1. Herança de Roteiro do Ponto ID & Ancoragem no Livro")
                        sobrescrever_lab_flag = st.toggle("Mostrar semanas já concluídas (Permitir Sobrescrita)", value=False, key=f"tog_sobrescrever_lab_{v}")
                        
                        c1, c2 = st.columns([1, 2])
                        ano_lab = c1.selectbox("Série:", [6, 7, 8, 9], key=f"prod_ano_{v}")
                        
                        if not df_planos.empty:
                            if sobrescrever_lab_flag:
                                planos_ano = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_lab))].copy()
                            else:
                                planos_ano = df_planos[
                                    (df_planos["ANO"].astype(str).str.contains(str(ano_lab))) & 
                                    (df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False))
                                ].copy()
                        else:
                            planos_ano = pd.DataFrame()
                        
                        if planos_ano.empty:
                            st.success(f"🏆 **Soberania Total!** Nenhuma semana pendente de material no Criador de Aulas para o {ano_lab}º Ano.")
                            st.info("💡 As semanas que foram marcadas como Recesso, Feriado ou ministradas pelo Livro já foram arquivadas.")
                        else:
                            semanas_opcoes = planos_ano["SEMANA"].unique().tolist()
                            
                            sem_lab = c2.selectbox("Semana Pendente no Hub:", semanas_opcoes, key=f"prod_sem_{v}")
                            plano_row = planos_ano[planos_ano["SEMANA"] == sem_lab].iloc[0]
                            plano_txt = str(plano_row['PLANO_TEXTO'])
                            trim_real = str(plano_row['TURMA'])

                            base_herdada = ai.extrair_tag(plano_txt, "BASE_DIDATICA")
                            obj_geral = ai.extrair_tag(plano_txt, "OBJETO_CONHECIMENTO") or ai.extrair_tag(plano_txt, "CONTEUDO_GERAL")

                            a_geradas_sem = df_aulas[(df_aulas['ANO'].astype(str).str.contains(str(ano_lab))) & (df_aulas['SEMANA_REF'] == sem_lab)]['TIPO_MATERIAL'].astype(str).tolist() if not df_aulas.empty else []
                            tem_aula1 = any("Aula 1" in mat for mat in a_geradas_sem)
                            tem_aula2 = any("Aula 2" in mat for mat in a_geradas_sem)
                            tem_sabado = any("Sábado" in mat or "Sabado" in mat for mat in a_geradas_sem)

                            plano_pede_a2 = len(ai.extrair_tag(plano_txt, "AULA_2")) > 30 and "N/A" not in ai.extrair_tag(plano_txt, "AULA_2").upper()
                            txt_sabado = ai.extrair_tag(plano_txt, "SABADO_LETIVO")
                            plano_pede_sab = len(txt_sabado) > 10 and "N/A" not in txt_sabado.upper() and "NÃO PROGRAMADA" not in txt_sabado.upper()

                            opcoes_disponiveis = []
                            if not tem_aula1: opcoes_disponiveis.append("Aula 1")
                            if plano_pede_a2 and not tem_aula2: opcoes_disponiveis.append("Aula 2")
                            if plano_pede_sab and not tem_sabado: opcoes_disponiveis.append("Sábado Letivo")

                            if not opcoes_disponiveis:
                                opcoes_disponiveis = ["Aula 1"]
                                if plano_pede_a2: opcoes_disponiveis.append("Aula 2")

                            c_c1, c_c2 = st.columns([1, 1])
                            aula_alvo_prod = c_c1.pills("Material Alvo:", opcoes_disponiveis, default=opcoes_disponiveis[0], key=f"pills_aula_alvo_{v}")
                            qtd_q_prod = c_c2.slider("Nº de Exercícios na Folha:", 1, 15, 5, key=f"sld_qtd_q_{v}")

                            if "1" in str(aula_alvo_prod): tag_roteiro = "AULA_1"
                            elif "2" in str(aula_alvo_prod): tag_roteiro = "AULA_2"
                            else: tag_roteiro = "SABADO_LETIVO"
                            
                            roteiro_especifico = ai.extrair_tag(plano_txt, tag_roteiro)
                            st.info(f"📌 **Roteiro Ativo do Plano:** {roteiro_especifico}")

                            st.markdown("##### 📖 Ancoragem no Livro Didático & Autonomia Docente")
                            
                            col_p1, col_p2 = st.columns(2)
                            pags_teo_lab = col_p1.text_input("📘 Páginas de Teoria (Aula 1):", placeholder="Ex: 184-186, 189", key=f"pags_teo_lab_{v}")
                            pags_ex_lab = col_p2.text_input("📝 Páginas de Exercícios (Aula 2):", placeholder="Ex: 187-188, 190-192", key=f"pags_ex_lab_{v}")

                            txt_lab_teo_ext, txt_lab_ex_ext = "", ""
                            
                            if "https" in base_herdada or "drive.google.com" in base_herdada:
                                list_p_teo = util.processar_intervalos_paginas(pags_teo_lab)
                                list_p_ex = util.processar_intervalos_paginas(pags_ex_lab)
                                
                                if list_p_teo or list_p_ex:
                                    with st.spinner("🔍 Fatiando páginas do livro no Drive..."):
                                        bytes_pdf_lab = db.baixar_bytes_arquivo_drive(base_herdada)
                                        if bytes_pdf_lab:
                                            if list_p_teo: txt_lab_teo_ext = util.extrair_texto_pdf_por_paginas(bytes_pdf_lab, list_p_teo)
                                            if list_p_ex: txt_lab_ex_ext = util.extrair_texto_pdf_por_paginas(bytes_pdf_lab, list_p_ex)

                            recorte_exercicios_livro = st.text_area(
                                "✍️ Injeção Auxiliar / Texto do Professor (Opcional):",
                                placeholder="Cole aqui exercícios ou notícias extras...",
                                height=90,
                                key=f"recorte_aula_lab_{v}"
                            )

                            pacote_recorte_aula = ""
                            if txt_lab_teo_ext: pacote_recorte_aula += f"--- PÁGINAS DE TEORIA ---\n{txt_lab_teo_ext}\n\n"
                            if txt_lab_ex_ext: pacote_recorte_aula += f"--- PÁGINAS DE EXERCÍCIOS ---\n{txt_lab_ex_ext}\n\n"
                            if recorte_exercicios_livro.strip(): pacote_recorte_aula += f"--- TEXTO AUXILIAR DO PROFESSOR ---\n{recorte_exercicios_livro.strip()}\n\n"

                            links_web_aula = st.text_area("Enriquecimento por Links da Web / URL no Drive:", value=base_herdada if "https" in base_herdada else "", key=f"links_web_lab_{v}")

                            c_f_btn1, c_f_btn2, c_f_btn3 = st.columns([1.5, 1.5, 1.2])

                            if c_f_btn1.button("🚀 Iniciar Forja Guiada por Etapas", use_container_width=True, type="primary", key=f"btn_guiada_lab_{v}"):
                                fa['info'] = {
                                    "ano": ano_lab, "semana_ref": sem_lab, "aula_alvo": aula_alvo_prod,
                                    "roteiro": roteiro_especifico, "habilidade": ai.extrair_tag(plano_txt, "HABILIDADE_BNCC"),
                                    "objetivos": ai.extrair_tag(plano_txt, "OBJETIVOS_ENSINO"), "base": base_herdada,
                                    "trimestre": trim_real, "recorte_livro": pacote_recorte_aula
                                }
                                fa['links_web'] = links_web_aula
                                fa['qtd_q'] = qtd_q_prod
                                fa['fase'] = 2
                                st.rerun()

                            if c_f_btn2.button("⚡ FORJA TURBO COMPLETA (1-CLIQUE)", use_container_width=True, key=f"btn_turbo_lab_{v}"):
                                with st.status("⚡ Executando Forja Turbo Completa...", expanded=True) as status_turbo:
                                    info_turbo = {
                                        "ano": ano_lab, "semana_ref": sem_lab, "aula_alvo": aula_alvo_prod,
                                        "roteiro": roteiro_especifico, "habilidade": ai.extrair_tag(plano_txt, "HABILIDADE_BNCC"),
                                        "objetivos": ai.extrair_tag(plano_txt, "OBJETIVOS_ENSINO"), "base": base_herdada,
                                        "trimestre": trim_real, "recorte_livro": pacote_recorte_aula
                                    }
                                    
                                    status_turbo.write("👨‍🏫 1/3 Gerando Guia do Professor (Início ➔ Meio ➔ Fim)...")
                                    prompt_teoria = f"SÉRIE: {ano_lab}º Ano. ASSUNTO: {aula_alvo_prod}.\nHABILIDADE: {info_turbo['habilidade']}\nROTEIRO: {roteiro_especifico}\nBASE LIVRO: {base_herdada}"
                                    res_teoria = ai.gerar_ia("FORJA_AULA_TEORIA", prompt_teoria, url_drive=base_herdada if "http" in base_herdada else None, recorte_livro=pacote_recorte_aula)
                                    fa['teoria'] = ai.extrair_tag(res_teoria, "PROFESSOR") or res_teoria

                                    status_turbo.write("📝 2/3 Gerando Folha do Aluno e Gabarito (BNCC/SAEB)...")
                                    prompt_ex = f"SÉRIE: {ano_lab}º Ano. QUANTIDADE: {qtd_q_prod}.\nTEORIA:\n{fa['teoria']}"
                                    res_ex = ai.gerar_ia("FORJA_AULA_EXERCICIOS", prompt_ex)
                                    fa['reg_q'] = ai.extrair_tag(res_ex, "ALUNO") or res_ex
                                    fa['reg_gab'] = ai.extrair_tag(res_ex, "GABARITO") or "Gabarito não formatado."

                                    status_turbo.write("♿ 3/3 Gerando Adaptações PEI Ancoradas no Tema...")
                                    prompt_pei = f"Adapte para PEI N1 e PEI N3 (Ancorado no Tema):\n{fa['reg_q']}"
                                    res_pei = ai.gerar_ia("FORJA_AULA_PEI", prompt_pei)
                                    fa['pei_1'] = ai.extrair_tag(res_pei, "PEI_NIVEL_1") or res_pei
                                    fa['pei_3'] = ai.extrair_tag(res_pei, "PEI_NIVEL_3") or "PEI N3 não formatado."

                                    fa['info'] = info_turbo
                                    fa['fase'] = 5
                                    status_turbo.update(label="✅ Forja Turbo Concluída! Avance para finalizar.", state="complete")
                                    st.balloons(); time.sleep(1); st.rerun()

                            with c_f_btn3.popover("📖 Baixa Burocrática (Livro/Lousa)"):
                                st.caption("Gaste 0 tokens: Registre que a aula desta semana foi ministrada pelo Livro Didático/Lousa.")
                                det_livro_input = st.text_input("Detalhes (Ex: Livro Págs. 184 a 188):", key=f"inp_baixa_lab_{v}")
                                dt_baixa_lab = st.date_input("Data:", date.today(), format="DD/MM/YYYY", key=f"dt_baixa_lab_{v}")
                                
                                if st.button("💾 DAR BAIXA E SUMIR COM ESTA SEMANA", type="primary", use_container_width=True, key=f"btn_baixa_direct_lab_{v}"):
                                    dt_str_lab = dt_baixa_lab.strftime("%d/%m/%Y")
                                    db.dar_baixa_aula_livro_offline(
                                        semana=sem_lab, 
                                        ano=f"{ano_lab}º", 
                                        turma=trim_real, 
                                        data_str=dt_str_lab, 
                                        detalhes_livro=det_livro_input
                                    )
                                    st.success(f"✅ Aula de {sem_lab} registrada no Diário e removida das pendências!")
                                    st.balloons(); time.sleep(1); st.rerun()

                elif "Projeto" in tipo_criacao:
                    fa['tipo_material'] = 'PROJETO'
                    with st.container(border=True):
                        st.markdown("#### 🔬 Parâmetros de Pesquisa Interdisciplinar")
                        c1, c2, c3 = st.columns([2, 1, 1])
                        natureza_p = c1.selectbox("Abordagem:", ["Semanário Temático", "Projeto de Identidade (Itabuna)", "Investigação Científica"], key=f"proj_nat_{v}")
                        ano_t = c2.selectbox("Série Alvo:", [6, 7, 8, 9], key=f"proj_ano_{v}")
                        modo_t = c3.selectbox("Modo:", ["Individual", "Equipes"], key=f"proj_modo_{v}")

                        tema_t = st.text_input("Tema do Projeto:", placeholder="Ex: Matemática do Cacau e da Sustentabilidade", key=f"proj_tema_{v}")
                        valor_t = st.number_input("Valor (0 a 10.0):", 0.0, 10.0, 2.0, key=f"proj_val_{v}")
                        
                        df_cur_t = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_t))] if not df_curriculo.empty else pd.DataFrame()
                        conts_t = st.multiselect("Conteúdos da Matriz para Integrar:", sorted(df_cur_t["CONTEUDO_ESPECIFICO"].unique().tolist()) if not df_cur_t.empty and "CONTEUDO_ESPECIFICO" in df_cur_t.columns else [], key=f"proj_conts_{v}")
                        instr_extra_p = st.text_area("Instruções Adicionais de Pesquisa:", key=f"proj_instr_{v}")

                        if st.button("Gerar Projeto de Pesquisa", use_container_width=True, type="primary", key=f"btn_gen_proj_{v}"):
                            if not tema_t: st.error("Preencha o tema do projeto.")
                            else:
                                with st.spinner("Forjando Roteiro de Investigação..."):
                                    nome_legivel = util.gerar_nome_material_elite(ano_t, "Projeto", tema_t)
                                    st.session_state.sosa_id_atual = nome_legivel
                                    st.session_state.lab_meta = {"ano": ano_t, "trimestre": "I Trimestre", "tipo": "PROJETO", "semana_ref": "PROJETO"}
                                    
                                    prompt_t = f"ID_FORNECIDO: {nome_legivel}\nSÉRIE: {ano_t}º. TEMA: {tema_t}. NATUREZA: {natureza_p}.\nCONTEÚDOS: {', '.join(conts_t)}.\nVALOR: {valor_t}.\nEXTRAS: {instr_extra_p}."
                                    st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_CIENTIFICO_V33", prompt_t, usar_busca=True)
                                    st.rerun()

                else:
                    fa['tipo_material'] = 'LISTA'
                    with st.container(border=True):
                        st.markdown("#### ⚙️ Configuração da Fábrica de Listas Híbridas (com Memória do Livro)")
                        c1, c2 = st.columns([1, 2])
                        ano_alvo = c1.selectbox("Série Alvo:", [6, 7, 8, 9], key=f"lab_list_ano_{v}")
                        trim_lista = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"lab_list_trim_{v}")
                        
                        puxar_memoria_lista = st.toggle("🧠 Autocarregar Aulas & Páginas do Livro (Diário de Bordo)", value=True, key=f"tog_mem_list_{v}")
                        contexto_aulas = ""
                        
                        if puxar_memoria_lista:
                            memoria_lista_txt, temas_aulas_lista = extrair_memoria_aulas_trimestre(f"{ano_alvo}º Ano", trim_lista)
                            if memoria_lista_txt:
                                st.success("✅ Memória de Aulas e Páginas do Livro resgatada com sucesso do Diário!")
                                contexto_aulas = memoria_lista_txt
                            else:
                                st.warning("Ainda não há aulas concluídas no Diário para este trimestre.")

                        df_aulas_ano = df_aulas[df_aulas['ANO'].str.contains(str(ano_alvo))] if not df_aulas.empty else pd.DataFrame()
                        aulas_opcoes = df_aulas_ano['TIPO_MATERIAL'].tolist() if not df_aulas_ano.empty else []
                        aulas_sel = st.multiselect("Selecione temas adicionais de aulas passadas:", aulas_opcoes, key=f"ms_aulas_lab_{v}")
                        
                        for a_n in aulas_sel:
                            match_sel = df_aulas_ano[df_aulas_ano['TIPO_MATERIAL'] == a_n]
                            if not match_sel.empty:
                                contexto_aulas += str(match_sel.iloc[0]['CONTEUDO']) + "\n"

                        tem_revisao_central = any(x in str(aulas_sel).upper() for x in ["REVISAO", "REVISÃO", "RECOMPOSICAO", "RECOMPOSIÇÃO", "RAIO-X", "AVALIAÇÃO", "AVALIACAO"])

                        if tem_revisao_central:
                            st.success("🎯 **Detectado Material Já Forjado na Central de Avaliações!**")
                            st.info("💡 Como você selecionou a Revisão/Avaliação da Central, não há necessidade de gerar nenhum PDF novo ou novas questões.")

                        c_q1, c_q2 = st.columns(2)
                        qtd_total_list = c_q1.slider("Quantidade Total de Questões:", 5, 30, 10, step=5, key=f"sld_qtd_list_{v}")
                        exigir_graficos = c_q2.checkbox("Forçar suporte visual em questões elegíveis?", value=True, key=f"chk_graf_list_{v}")
                        
                        c_btn_l1, c_btn_l2 = st.columns(2)

                        if tem_revisao_central:
                            if c_btn_l1.button("🛑 REGISTRAR SEM GERAR PDF (ISENÇÃO DE IA)", type="primary", use_container_width=True, key=f"btn_isencao_direct_{v}"):
                                nome_revisao_sel = [a for a in aulas_sel if any(x in a.upper() for x in ["REVISAO", "REVISÃO", "RECOMPOSICAO", "AVALIAÇÃO"])][0]
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                    datetime.now().strftime("%d/%m/%Y"), "CONSOLIDAÇÃO", f"{ano_alvo}º Ano - Registro de Revisão ({nome_revisao_sel})",
                                    f"[PROFESSOR]\nAULA DE REVISÃO REGISTRADA\nMaterial Utilizado: {nome_revisao_sel}\n\n[ALUNO]\nResolução do Caderno de Recomposição da Central de Avaliações.\n\n--- LINKS ---\nRegular(N/A)",
                                    f"{ano_alvo}º", "N/A"
                                ])
                                db.arquivar_plano_produzido("CONSOLIDAÇÃO", f"{ano_alvo}º")
                                st.toast("✅ Registro concluído com sucesso! Nenhum PDF novo foi gerado.", icon="🛡️")
                                st.balloons(); time.sleep(1); reset_laboratorio()

                        label_btn_montagem = "🚀 INICIALIZAR LINHA DE MONTAGEM (FORJAR NOVA LISTA)" if tem_revisao_central else "🚀 INICIALIZAR LINHA DE MONTAGEM DE LISTA"
                        
                        if c_btn_l2.button(label_btn_montagem, use_container_width=True, key=f"btn_init_list_{v}"):
                            if not contexto_aulas.strip() and not aulas_sel:
                                st.error("⚠️ Selecione pelo menos um tema de aula ou ative o resgate de memória.")
                            else:
                                with st.spinner("Estruturando mapa lógico do caderno..."):
                                    s_id_l = util.gerar_sosa_id("LISTA", ano_alvo, trim_lista.split()[0])
                                    nome_elite_c = f"{ano_alvo}º Ano - Lista Híbrida - {s_id_l}"
                                    
                                    gabarito_mapa = util.gerar_gabarito_balanceado(qtd_total_list)
                                    mapa_itens = []
                                    for idx_item in range(1, qtd_total_list + 1):
                                        tem_imagem = exigir_graficos and (idx_item <= 10)
                                        mapa_itens.append({
                                            'q': idx_item,
                                            'tema': f"Tópico da Aula / Livro Didático (Item {idx_item})",
                                            'dificuldade': 'Fácil' if idx_item <= (qtd_total_list*0.3) else ('Difícil' if idx_item >= (qtd_total_list*0.8) else 'Média'),
                                            'gabarito': gabarito_mapa[idx_item-1],
                                            'suporte_visual': tem_imagem,
                                            'status': 'pendente',
                                            'dados': {}
                                        })
                                    
                                    fa['mapa_lista'] = mapa_itens
                                    fa['info'] = {
                                        'ano': ano_alvo, 'trimestre': trim_lista, 'tipo': 'LISTA_HIBRIDA', 
                                        'semana_ref': 'CONSOLIDAÇÃO', 'id_lista': nome_elite_c, 'contexto': contexto_aulas,
                                        'qtd': qtd_total_list
                                    }
                                    fa['fase'] = 2
                                    st.rerun()

            elif fa['fase'] == 2:
                if fa.get('info', {}).get('tipo') == 'LISTA_HIBRIDA' and any(x in str(fa.get('info', {}).get('id_lista', '')).upper() for x in ["REVISAO", "REVISÃO", "RECOMPOSICAO", "RECOMPOSIÇÃO", "RAIO-X"]):
                    st.success("✅ **Material de Revisão Herdado da Central de Avaliações!**")
                    st.info("💡 Este material utiliza as questões espelho já forjadas. Não há necessidade de gerar novos itens por lote.")
                    
                    if st.button("💾 CONFIRMAR E REGISTRAR AULA NO ACERVO", type="primary", use_container_width=True, key=f"btn_bypass_rev_f2_{v}"):
                        nome_rev_salvar = fa['info']['id_lista']
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_rev_salvar,
                            fa['info']['contexto'], f"{fa['info']['ano']}º", "N/A"
                        ])
                        db.arquivar_plano_produzido("CONSOLIDAÇÃO", f"{fa['info']['ano']}º")
                        st.success("✅ Registro de Revisão concluído com sucesso!")
                        st.balloons(); time.sleep(1); reset_laboratorio()
                
                elif fa.get('tipo_material') == 'AULA':
                    st.markdown("### Fase 2: Tratado Didático & Roteiro de Lousa (Início ➔ Meio ➔ Fim)")
                    if not fa['teoria']:
                        with st.spinner("Gerando explicação didática com leitura das páginas do Livro..."):
                            prompt_teoria = (
                                f"SÉRIE: {fa['info']['ano']}º Ano.\nASSUNTO: {fa['info']['aula_alvo']}.\n"
                                f"HABILIDADE: {fa['info']['habilidade']}\nROTEIRO DO PROFESSOR: {fa['info']['roteiro']}\n"
                                f"BASE DO LIVRO: {fa['info'].get('base', '')}\n"
                                f"🚨 RESPONDA OBRIGATORIAMENTE DENTRO DA TAG [PROFESSOR]"
                            )
                            url_livro = fa['links_web'].strip() if "http" in fa['links_web'] else None
                            recorte_txt = fa['info'].get('recorte_livro', '')
                            
                            res_teoria = ai.gerar_ia("FORJA_AULA_TEORIA", prompt_teoria, url_drive=url_livro, usar_busca=False, recorte_livro=recorte_txt)
                            if "ERRO" in res_teoria.upper() or "⚠️" in res_teoria:
                                st.error(f"Falha na IA: {res_teoria}")
                                if st.button("Tentar Novamente", key=f"btn_retry_teo_{v}"): st.rerun()
                            else:
                                fa['teoria'] = ai.extrair_tag(res_teoria, "PROFESSOR") or res_teoria
                                st.rerun()
                    else:
                        with st.container(border=True):
                            modo_leitura = st.toggle("👁️ Visualização Real (Renderizar Matemática)", value=True, key=f"read_mode_f2_{v}")
                            if modo_leitura: st.markdown(preparar_para_leitura(fa['teoria']))
                            else: fa['teoria'] = st.text_area("Edição Manual da Teoria:", value=fa['teoria'], height=350, key=f"ed_teo_manual_{v}")
                        
                        inst_t = st.text_input("Ajuste da IA (Ex: 'Incorpore um gancho de notícia sobre tecnologia no Início'):", key=f"inst_t_{v}")
                        c_b1, c_b2 = st.columns(2)
                        
                        if c_b1.button("Aprovar Teoria e Avançar", type="primary", use_container_width=True, key=f"btn_apr_teo_{v}"):
                            fa['fase'] = 3; st.rerun()
                        if c_b2.button("Regerar Teoria", use_container_width=True, key=f"btn_regerar_teo_{v}"):
                            with st.spinner("Ajustando teoria..."):
                                prompt_teoria = f"SÉRIE: {fa['info']['ano']}º Ano.\nASSUNTO: {fa['info']['aula_alvo']}.\nAJUSTE: {inst_t}\nTEORIA ANTERIOR:\n{fa['teoria']}\n🚨 RESPONDA OBRIGATORIAMENTE DENTRO DA TAG [PROFESSOR]"
                                res_teoria = ai.gerar_ia("FORJA_AULA_TEORIA", prompt_teoria, usar_busca=False)
                                fa['teoria'] = ai.extrair_tag(res_teoria, "PROFESSOR") or res_teoria
                                st.rerun()

                else:
                    st.markdown(f"### Linha de Montagem: {fa['info']['id_lista']}")
                    pendentes = [item for item in fa['mapa_lista'] if item['status'] == 'pendente']
                    if pendentes:
                        micro_lote = pendentes[:10]
                        if st.button(f"🚀 GERAR PRÓXIMO LOTE EM MASSA ({len(micro_lote)} ITENS PENDENTES)", type="primary", use_container_width=True, key=f"btn_gen_lote_lista_{v}"):
                            with st.status(f"Forjando lote de {len(micro_lote)} itens...") as status:
                                historico_temas = [item['dados'].get('ENUNCIADO', '')[:150] for item in fa['mapa_lista'] if item['status'] in ['aprovado', 'revisao']]
                                resumo_hist = "\n".join(historico_temas) if historico_temas else "Nenhum item gerado ainda."
                                
                                prompt_lote = f"SÉRIE: {fa['info']['ano']}º Ano. CONTEXTO E PÁGINAS DO LIVRO:\n{fa['info']['contexto']}\n\n"
                                prompt_lote += f"🚨 HISTÓRICO DE QUESTÕES JÁ GERADAS:\n{resumo_hist}\n\n"
                                
                                for item in micro_lote:
                                    img_req = "REQUER SUPORTE VISUAL COM UM PROMPT DE IMAGEM TOTALMENTE DETALHADO EM INGLÊS." if item['suporte_visual'] else "Foco textual."
                                    prompt_lote += f"QUESTÃO {item['q']}:\n- COMPLEXIDADE: {item['dificuldade']}\n- GABARITO EXIGIDO: {item['gabarito']}\n- DIRETRIZ: {img_req}\n\n"
                                
                                res_json = ai.gerar_ia_json("FORJA_LOTE_JSON", prompt_lote)
                                
                                if "erro" in res_json:
                                    status.update(label="Falha no lote. Tente novamente.", state="error")
                                    st.error(res_json["erro"])
                                else:
                                    questoes_retornadas = res_json.get("questoes", [])
                                    for idx_lote, q_data in enumerate(questoes_retornadas):
                                        if idx_lote < len(micro_lote):
                                            item = micro_lote[idx_lote]
                                            enunciado = q_data.get('enunciado', '')
                                            if item['suporte_visual'] and "[ PROMPT IMAGEM:" not in enunciado:
                                                enunciado += f"\n\n[ PROMPT IMAGEM: A4 portrait math worksheet, clean black and white line art, completely white background, no colors, no shadows, high contrast, perfect for printing... ]"
                                                
                                            item['dados'] = {
                                                'ENUNCIADO': enunciado, 'ALT_A': q_data.get('alt_a', ''),
                                                'ALT_B': q_data.get('alt_b', ''), 'ALT_C': q_data.get('alt_c', ''),
                                                'ALT_D': q_data.get('alt_d', ''), 'ALT_E': q_data.get('alt_e', ''),
                                                'HABILIDADE': q_data.get('habilidade', 'EF06MA01'), 'JUSTIFICATIVA': q_data.get('justificativa', ''),
                                                'DISTRATORES': q_data.get('distratores', ''), 'GABARITO': item['gabarito']
                                            }
                                            item['status'] = 'revisao'
                                    st.rerun()

                    st.markdown("---")
                    todas_aprovadas = True
                    modo_leitura_list = st.toggle("👁️ Modo Leitura (Renderizar LaTeX)", value=True, key=f"read_list_{v}")

                    for i, item in enumerate(fa['mapa_lista']):
                        label_status = "Aprovada" if item['status'] == 'aprovado' else ("Revisão" if item['status'] == 'revisao' else "Pendente")
                        is_expanded = item['status'] != 'aprovado'
                        
                        with st.expander(f"Item {item['q']:02d} | Gabarito: {item['gabarito']} ({label_status})", expanded=is_expanded):
                            if item['status'] == 'pendente':
                                todas_aprovadas = False
                                st.info("Item aguardando geração.")
                            elif item['status'] == 'revisao':
                                todas_aprovadas = False
                                d = item['dados']
                                if modo_leitura_list:
                                    st.markdown(preparar_para_leitura(d['ENUNCIADO']))
                                    st.markdown(f"**(A)** {preparar_para_leitura(d['ALT_A'])} | **(B)** {preparar_para_leitura(d['ALT_B'])} | **(C)** {preparar_para_leitura(d['ALT_C'])} | **(D)** {preparar_para_leitura(d['ALT_D'])} | **(E)** {preparar_para_leitura(d['ALT_E'])}")
                                
                                col_b1, col_b2 = st.columns(2)
                                if col_b1.button(f"Aprovar Item {item['q']}", type="primary", key=f"btn_apr_l_{i}_{v}", use_container_width=True):
                                    item['status'] = 'aprovado'; st.rerun()
                            elif item['status'] == 'aprovado':
                                d = item['dados']
                                st.text(d['ENUNCIADO'])

                    if todas_aprovadas:
                        st.success("Toda a carga da lista foi aprovada!")
                        if st.button("Avançar para a Cartilha PEI", type="primary", use_container_width=True, key=f"btn_f2_to_f3_{v}"):
                            fa['fase'] = 3; st.rerun()

            elif fa['fase'] == 3:
                st.markdown("### Fase 3: Exercícios Regulares (Letramento Matemático BNCC/SAEB)")
                
                # BADGE VISUAL DE LETRAMENTO MATEMÁTICO
                st.markdown("Selo BNCC: `[🧠 FORMULAR CONCEITOS]` | `[⚙️ EMPREGAR ALGORITMOS]` | `[💬 INTERPRETAR DADOS]`")
                
                if not fa['reg_q']:
                    with st.spinner("Gerando folha de exercícios com contextos reais e tabelas Markdown..."):
                        prompt_ex = f"SÉRIE: {fa['info']['ano']}º Ano. QUANTIDADE: {fa['qtd_q']}.\nTEORIA DA AULA:\n{fa['teoria']}\n🚨 USE AS TAGS [ALUNO] e [GABARITO]"
                        res_ex = ai.gerar_ia("FORJA_AULA_EXERCICIOS", prompt_ex)
                        fa['reg_q'] = ai.extrair_tag(res_ex, "ALUNO") or res_ex
                        fa['reg_gab'] = ai.extrair_tag(res_ex, "GABARITO") or "Gabarito não formatado."
                        st.rerun()
                else:
                    modo_leitura_ex = st.toggle("👁️ Visualização Real", value=True, key=f"tog_ex_{v}")
                    t_q, t_g = st.tabs(["Folha do Aluno", "Gabarito & Resoluções"])
                    with t_q:
                        if modo_leitura_ex: st.markdown(preparar_para_leitura(fa['reg_q']))
                        else: fa['reg_q'] = st.text_area("Exercícios (Aluno):", value=fa['reg_q'], height=300, key=f"ed_reg_q_{v}")
                    with t_g:
                        if modo_leitura_ex: st.markdown(preparar_para_leitura(fa['reg_gab']))
                        else: fa['reg_gab'] = st.text_area("Resoluções comentadas:", value=fa['reg_gab'], height=200, key=f"ed_reg_gab_{v}")
                    
                    if st.button("Aprovar Exercícios e Avançar para Adaptação PEI", type="primary", use_container_width=True, key=f"btn_f3_to_f4_{v}"):
                        fa['fase'] = 4; st.rerun()

            elif fa['fase'] == 4:
                st.markdown("### Fase 4: Adaptação PEI On-Demand (Ancorada no Tema da Aula)")
                st.caption("Selecione EXCLUSIVAMENTE os níveis PEI necessários para esta turma para economizar tokens e arquivos:")

                with st.container(border=True):
                    niveis_lab_sel = st.pills(
                        "Níveis PEI Desejados:",
                        ["🔵 PEI Nível 1 (Apoio Leve - 3 Opções)", "🔴 PEI Nível 3 (Suporte Severo - 100% no Papel Ancorado)"],
                        default=["🔵 PEI Nível 1 (Apoio Leve - 3 Opções)", "🔴 PEI Nível 3 (Suporte Severo - 100% no Papel Ancorado)"],
                        selection_mode="multi",
                        key=f"pills_pei_lab_{v}"
                    )

                pede_lab_n1 = any("Nível 1" in n for n in niveis_lab_sel)
                pede_lab_n3 = any("Nível 3" in n for n in niveis_lab_sel)

                if st.button("🧠 FORJAR APENAS NÍVEIS PEI SELECIONADOS", type="primary", use_container_width=True, key=f"btn_gen_pei_f4_{v}"):
                    with st.spinner("Adaptando exercícios para os níveis selecionados com estrita ancoragem no tema da aula..."):
                        prompt_pei = f"Adapte as questões abaixo para PEI N1 e PEI N3 (Ancorado 100% no Tema da Aula):\n{fa['reg_q']}\n\nTEORIA DA AULA:\n{fa['teoria']}\n🚨 USE AS TAGS [PEI_NIVEL_1], [PEI_NIVEL_3] e [GABARITO_PEI]"
                        res_pei = ai.gerar_ia("FORJA_AULA_PEI", prompt_pei)
                        
                        if pede_lab_n1: fa['pei_1'] = ai.extrair_tag(res_pei, "PEI_NIVEL_1") or res_pei
                        else: fa['pei_1'] = ""
                        
                        if pede_lab_n3: fa['pei_3'] = ai.extrair_tag(res_pei, "PEI_NIVEL_3") or "PEI N3 não formatado."
                        else: fa['pei_3'] = ""
                        
                        fa['pei_gab'] = ai.extrair_tag(res_pei, "GABARITO_PEI") or "Gabarito não formatado."
                        st.rerun()

                if fa.get('pei_1') or fa.get('pei_3'):
                    modo_leitura_pei = st.toggle("👁️ Visualização Real PEI", value=True, key=f"tog_pei_view_lab_{v}")
                    t_p1, t_p3 = st.tabs(["🔵 PEI Nível 1 (Apoio Leve)", "🔴 PEI Nível 3 (10 Bento Boxes no Papel)"])
                    
                    with t_p1: 
                        if modo_leitura_pei: st.markdown(preparar_para_leitura(fa['pei_1']))
                        else: fa['pei_1'] = st.text_area("Nível 1:", value=fa['pei_1'], height=250, key=f"ed_p1_area_f4_{v}")
                        
                    with t_p3: 
                        if modo_leitura_pei: st.markdown(preparar_para_leitura(fa['pei_3']))
                        else: fa['pei_3'] = st.text_area("Nível 3 (Ancorado no Tema):", value=fa['pei_3'], height=250, key=f"ed_p3_area_f4_{v}")
                    
                    if st.button("Aprovar PEI e Avançar para Compilação", type="primary", use_container_width=True, key=f"btn_f4_to_f5_{v}"):
                        fa['fase'] = 5; st.rerun()

            elif fa['fase'] == 5:
                st.markdown("### Fase 5: Compilação e Custódia no Google Drive")
                nome_sugerido = util.gerar_nome_material_elite(fa['info']['ano'], fa['info']['aula_alvo'], fa['info']['semana_ref'])
                nome_arq = st.text_input("Nome do Material no Cofre Digital:", value=nome_sugerido, key=f"nome_arq_f5_{v}")
                
                if st.button("Finalizar e Sincronizar Tudo no Google Drive", type="primary", use_container_width=True, key=f"btn_finalizar_f5_{v}"):
                    with st.status("Gerando Documentos Oficiais Word...", expanded=True) as status:
                        trim_real = fa['info'].get('trimestre', 'I Trimestre')
                        info_doc = {"ano": f"{fa['info']['ano']}º", "trimestre": trim_real, "semana": fa['info']['semana_ref']}

                        status.write("📄 Gerando Folha de Exercícios do Aluno Word...")
                        doc_alu = exporter.gerar_docx_aluno_v24(nome_arq, fa['reg_q'], info_doc)
                        link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_arq}_ALUNO", modo="AULA")
                        
                        link_pei1 = "N/A"
                        if fa.get('pei_1'):
                            status.write("🔵 Gerando Caderno PEI Nível 1 Word...")
                            doc_pei1 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N1", fa['pei_1'], info_doc)
                            link_pei1 = db.subir_e_converter_para_google_docs(doc_pei1, f"{nome_arq}_PEI_N1", modo="AULA")
                        
                        link_pei3 = "N/A"
                        if fa.get('pei_3'):
                            status.write("🔴 Gerando Caderno PEI Nível 3 Word (Bento Cards + Rubrica)...")
                            doc_pei3 = exporter.gerar_docx_pei_qualitativa(f"{nome_arq}_PEI_N3", fa['pei_3'], info_doc)
                            link_pei3 = db.subir_e_converter_para_google_docs(doc_pei3, f"{nome_arq}_PEI_N3", modo="AULA")
                        
                        status.write("👨‍🏫 Gerando Guia do Professor Word...")
                        guia_prof = f"{fa['teoria']}\n\n[GABARITO]\n{fa['reg_gab']}\n\n[GABARITO_PEI]\n{fa['pei_gab']}"
                        doc_prof = exporter.gerar_docx_professor_v25(nome_arq, guia_prof, info_doc)
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_arq}_PROF", modo="AULA")
                        
                        links_f = f"--- LINKS ---\nRegular({link_alu})\nPEI_N1({link_pei1})\nPEI_N3({link_pei3})\nProf({link_prof})"
                        conteudo_final = f"[PROFESSOR]\n{fa['teoria']}\n\n[ALUNO]\n{fa['reg_q']}\n\n[GABARITO]\n{fa['reg_gab']}\n\n[PEI_NIVEL_1]\n{fa.get('pei_1','')}\n\n[PEI_NIVEL_3]\n{fa.get('pei_3','')}\n\n[GABARITO_PEI]\n{fa.get('pei_gab','')}\n\n{links_f}"
                        
                        db.salvar_no_banco("DB_AULAS_PRONTAS",[
                            datetime.now().strftime("%d/%m/%Y"), fa['info']['semana_ref'], nome_arq, conteudo_final, f"{fa['info']['ano']}º", link_alu
                        ])
                        
                        status.update(label="✅ Materiais sincronizados com sucesso no Drive!", state="complete")
                        st.balloons(); time.sleep(1.2); reset_laboratorio()

    # ==============================================================================
    # ABA 2: ACERVO DIGITAL & HUB DE PRODUÇÃO
    # ==============================================================================
    with tab_acervo_lab:
        st.markdown("### Hub de Produção & Acervo de Aulas")
        
        if not df_planos.empty:
            planos_ativos_hub = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]
            if not planos_ativos_hub.empty:
                st.markdown("#### ⏳ Planos Pendentes de Produção (Hub)")
                for _, r_hub in planos_ativos_hub.iterrows():
                    with st.container(border=True):
                        c_h1, c_h2, c_h3, c_h4 = st.columns([2, 1, 1.2, 1])
                        c_h1.markdown(f"**{r_hub['SEMANA']}** | Série: {r_hub['ANO']}")
                        c_h1.caption("Status: ⏳ PENDENTE DE MATERIAL")
                        
                        if c_h2.button("🚀 Gerar com IA", key=f"gen_ia_hub_{r_hub.name}", use_container_width=True):
                            st.session_state.lab_temp = str(r_hub["PLANO_TEXTO"])
                            st.session_state.sosa_id_atual = util.gerar_sosa_id("AULA", r_hub['ANO'], r_hub["TURMA"])
                            st.session_state.lab_meta = {"ano": str(r_hub['ANO']).replace("º",""), "trimestre": r_hub["TURMA"], "tipo": "PRODUÇÃO_HUB", "semana_ref": r_hub['SEMANA']}
                            st.rerun()

                        with c_h3.popover("📦 Registro Offline / Livro"):
                            st.info("💡 **Conclusão sem uso de IA:** Registre os detalhes da aula ministrada com o Livro Didático ou Atividade Manual.")
                            txt_obs_manual = st.text_input("Detalhes (Ex: Livro Didático - Págs. 45 a 48):", key=f"txt_man_obs_{r_hub.name}")
                            
                            if st.button("💾 CONFIRMAR CONCLUSÃO MANUAL", type="primary", key=f"btn_conf_man_{r_hub.name}"):
                                nome_aula_man = f"{r_hub['ANO']} - Aula Livro ({r_hub['SEMANA']})"
                                txt_conteudo_man = f"[PROFESSOR]\nAULA OFFLINE / LIVRO DIDÁTICO\nDetalhamento: {txt_obs_manual}\n\n[ALUNO]\nResolução dos exercícios do Livro Didático conforme orientação do professor.\n\n--- LINKS ---\nRegular(N/A)"
                                
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                    datetime.now().strftime("%d/%m/%Y"), r_hub['SEMANA'], nome_aula_man, txt_conteudo_man, str(r_hub['ANO']), "N/A"
                                ])
                                db.arquivar_plano_produzido(r_hub['SEMANA'], r_hub['ANO'])
                                st.success("✅ Aula offline arquivada com sucesso sem uso de IA!")
                                st.balloons(); time.sleep(1); st.rerun()

                        if c_h4.button("Concluir", key=f"fin_hub_direct_{r_hub.name}", use_container_width=True):
                            if db.arquivar_plano_produzido(r_hub['SEMANA'], r_hub['ANO']): st.rerun()

        st.markdown("---")
        st.markdown("#### 📖 Acervo de Materiais Didáticos Salvos")
        
        if not df_aulas.empty:
            df_m_acervo = df_aulas[~df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy()
            termos_proibidos = ["TESTE", "PROVA", "SONDA", "RECUPERAÇÃO", "2ª CHAMADA"]
            df_m_acervo = df_m_acervo[~df_m_acervo['TIPO_MATERIAL'].str.upper().str.contains('|'.join(termos_proibidos), na=False)].iloc[::-1]

            for _, row in df_m_acervo.iterrows():
                with st.container(border=True):
                    txt_f = str(row.get('CONTEUDO', ''))
                    identificador = str(row.get('TIPO_MATERIAL', 'Material Didático'))
                    ano_exib = str(row.get('ANO', '6º'))
                    data_exib = str(row.get('DATA', 'N/A'))
                    sem_ref_exib = str(row.get('SEMANA_REF', 'Geral'))
                    
                    st.markdown(f"##### {identificador}")
                    st.caption(f"Série: {ano_exib} | Data: {data_exib} | Status: ✅ DOCX DRIVE SINCRONIZADO")
                    
                    def extrair_link_seguro(t, k):
                        m = re.search(rf"{k}\s*\(\s*(https://docs\.google\.com/document/d/[^\s\)]+)\s*\)", t, re.IGNORECASE)
                        return m.group(1).strip() if m else "N/A"

                    l_alu = extrair_link_seguro(txt_f, "Regular")
                    if l_alu == "N/A" and "https://docs.google.com" in str(row.get('LINK_DRIVE', '')):
                        l_alu = str(row.get('LINK_DRIVE'))
                        
                    l_pei1 = extrair_link_seguro(txt_f, "PEI_N1")
                    if l_pei1 == "N/A": l_pei1 = extrair_link_seguro(txt_f, "PEI")
                    
                    l_pei3 = extrair_link_seguro(txt_f, "PEI_N3")
                    l_prof = extrair_link_seguro(txt_f, "Prof")

                    c_b1, c_b2, c_b3, c_b4, c_b5, c_b6 = st.columns(6)
                    
                    if l_alu and "http" in str(l_alu): c_b1.link_button("📄 Aluno", str(l_alu), use_container_width=True)
                    else: c_b1.caption("Offline/Livro")
                    
                    if l_pei1 and "http" in str(l_pei1): c_b2.link_button("🔵 PEI N1", str(l_pei1), use_container_width=True)
                    else: c_b2.caption("Sem N1")
                    
                    if l_pei3 and "http" in str(l_pei3): c_b3.link_button("🔴 PEI N3", str(l_pei3), use_container_width=True)
                    else: c_b3.caption("Sem N3")
                    
                    if l_prof and "http" in str(l_prof): c_b4.link_button("👨‍🏫 Guia Prof", str(l_prof), use_container_width=True)
                    else: c_b4.caption("Sem Guia")
                    
                    if c_b5.button("✏️ Refinar", key=f"ref_ac_{row.name}", use_container_width=True):
                        st.session_state.lab_temp = txt_f
                        st.session_state.sosa_id_atual = identificador
                        st.session_state.lab_meta = {"ano": str(row["ANO"]).replace("º",""), "semana_ref": row['SEMANA_REF']}
                        st.rerun()
                        
                    if c_b6.button("🗑️ Apagar", key=f"del_ac_{row.name}", use_container_width=True):
                        if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", identificador): st.rerun()

                    with st.expander("🎨 Re-compilar e Adequar ao Padrão Exporter V2026", expanded=False):
                        st.info("💡 **Adequação Automática:** Esta ferramenta gera novos arquivos DOCX aplicando a limpeza de LaTeX (`$$`), os Bento Cards e a Tabela Oficial de Rubricas para o PEI N3 no Google Drive.")
                        
                        if st.button("🚀 EXECUTAR RE-COMPILAÇÃO COMPLETA NO EXPORTER V2026", type="primary", use_container_width=True, key=f"btn_recompila_{row.name}"):
                            with st.status("Re-compilando materiais no padrão Exporter V2026...", expanded=True) as status_rec:
                                ano_str_rec = str(row['ANO'])
                                sem_ref_rec = str(row['SEMANA_REF'])
                                info_doc_rec = {"ano": ano_str_rec, "trimestre": "I Trimestre", "semana": sem_ref_rec}
                                
                                ed_prof_r = ai.extrair_tag(txt_f, "PROFESSOR")
                                ed_alu_r = ai.extrair_tag(txt_f, "ALUNO")
                                ed_pei1_r = ai.extrair_tag(txt_f, "PEI_NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                                ed_pei3_r = ai.extrair_tag(txt_f, "PEI_NIVEL_3")
                                ed_gab_r = ai.extrair_tag(txt_f, "GABARITO")
                                ed_gab_pei_r = ai.extrair_tag(txt_f, "GABARITO_PEI")
                                ed_img_r = ai.extrair_tag(txt_f, "IMAGENS")

                                status_rec.write("📄 Re-gerando Folha do Aluno Word...")
                                doc_alu_r = exporter.gerar_docx_aluno_v24(identificador, ed_alu_r, info_doc_rec)
                                link_alu_r = db.subir_e_converter_para_google_docs(doc_alu_r, f"{identificador}_ALUNO", modo="AULA")
                                
                                link_pei1_r = "N/A"
                                if ed_pei1_r:
                                    status_rec.write("🔵 Re-gerando PEI Nível 1 Word...")
                                    doc_pei1_r = exporter.gerar_docx_pei_v25(f"{identificador}_PEI_N1", ed_pei1_r, info_doc_rec)
                                    link_pei1_r = db.subir_e_converter_para_google_docs(doc_pei1_r, f"{identificador}_PEI_N1", modo="AULA")
                                
                                link_pei3_r = "N/A"
                                if ed_pei3_r:
                                    status_rec.write("🔴 Re-gerando PEI Nível 3 (Bento Cards + Rubricas) Word...")
                                    doc_pei3_r = exporter.gerar_docx_pei_qualitativa(f"{identificador}_PEI_N3", ed_pei3_r, info_doc_rec)
                                    link_pei3_r = db.subir_e_converter_para_google_docs(doc_pei3_r, f"{identificador}_PEI_N3", modo="AULA")

                                status_rec.write("👨‍🏫 Re-gerando Guia do Professor Word...")
                                guia_prof_r = f"{ed_prof_r}\n\n[GABARITO]\n{ed_gab_r}\n\n[GABARITO_PEI]\n{ed_gab_pei_r}"
                                doc_prof_r = exporter.gerar_docx_professor_v25(identificador, guia_prof_r, info_doc_rec)
                                link_prof_r = db.subir_e_converter_para_google_docs(doc_prof_r, f"{identificador}_PROF", modo="AULA")
                                
                                links_f_r = f"--- LINKS ---\nRegular({link_alu_r})\nPEI_N1({link_pei1_r})\nPEI_N3({link_pei3_r})\nProf({link_prof_r})"
                                conteudo_final_r = f"[PROFESSOR]\n{ed_prof_r}\n\n[ALUNO]\n{ed_alu_r}\n\n[GABARITO]\n{ed_gab_r}\n\n[PEI_NIVEL_1]\n{ed_pei1_r}\n\n[PEI_NIVEL_3]\n{ed_pei3_r}\n\n[GABARITO_PEI]\n{ed_gab_pei_r}\n\n{links_f_r}"
                                
                                db.excluir_registro("DB_AULAS_PRONTAS", identificador)
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                    row['DATA'], sem_ref_rec, identificador, conteudo_final_r, ano_str_rec, link_alu_r
                                ])
                                
                                status_rec.update(label="✅ Materiais re-compilados e atualizados no Drive!", state="complete")
                                st.balloons(); time.sleep(1.2); st.rerun()







# ==============================================================================
# MÓDULO: CENTRAL DE AVALIAÇÕES - V2026.ULTIMATE
# (LINHA DE MONTAGEM, PERÍCIA TRI, ESTEIRA FLUIDA DE RECOMPOSIÇÃO E EXPEDIÇÃO XEROX)
# ==============================================================================
elif menu == "📝 Central de Avaliações":
    st.title("📝 Central de Avaliações (Padrão ENEM / SAEB / BNCC)")
    st.caption("Arquitetura de Avaliação de Alta Performance: Ancoragem no Livro/Lousa, Perícia TRI de Distratores, Tríade PEI On-Demand, Esteira Fluida de Recomposição e Expedição de E-mail para Xerox.")
    st.markdown("---")

    if "v_av" not in st.session_state: 
        st.session_state.v_av = int(time.time())
    v = st.session_state.v_av

    if "forja" not in st.session_state:
        st.session_state.forja = {
            'fase': 1, 'mapa': [], 'info': {}, 'pei_1': '', 'pei_2': '', 'pei_3': '', 
            'prova_final_txt': '', 'contexto_base': '', 'pincamento_lousa': ''
        }
    
    f = st.session_state.forja

    def reset_forja():
        st.session_state.forja = {
            'fase': 1, 'mapa': [], 'info': {}, 'pei_1': '', 'pei_2': '', 'pei_3': '', 
            'prova_final_txt': '', 'contexto_base': '', 'pincamento_lousa': ''
        }
        st.session_state.v_av = int(time.time())
        st.rerun()

    def render_indicador_fases(fase_atual):
        etapas = [
            ("1. Briefing & Seleção", 1),
            ("2. Forja Regular (TRI)", 2),
            ("3. PEI On-Demand", 3),
            ("4. Custódia & Drive", 4),
            ("5. Conclusão", 5)
        ]
        html_steps = []
        for nome, f_num in etapas:
            if fase_atual == f_num:
                color = "#2962FF"; f_weight = "bold"; border = "border-bottom: 3px solid #2962FF;"
            elif fase_atual > f_num:
                color = "#2ECC71"; f_weight = "bold"; border = "border-bottom: 3px solid #2ECC71;"
            else:
                color = "gray"; f_weight = "normal"; border = "border-bottom: 3px solid gray;"
            html_steps.append(f"<div style='flex: 1; text-align: center; padding-bottom: 8px; color: {color}; font-weight: {f_weight}; {border}'>{nome}</div>")
        st.markdown(f"<div style='display: flex; justify-content: space-between; margin-bottom: 25px;'>{''.join(html_steps)}</div>", unsafe_allow_html=True)

    tab_forja, tab_acervo_av, tab_recomposicao, tab_expedicao = st.tabs([
        "📝 Linha de Montagem de Provas", 
        "📖 Acervo de Provas & Perícia TRI", 
        "🔄 Recomposição & Cadernos de Revisão",
        "📧 Expedição de E-mail, PDFs & Acervo Trimestral"
    ])

    # ==============================================================================
    # ABA 1: LINHA DE MONTAGEM DE PROVAS
    # ==============================================================================
    with tab_forja:
        if 1 < f['fase'] <= 5:
            render_indicador_fases(f['fase'])
            if st.button("🗑️ Descartar Edição Atual e Voltar ao Início", use_container_width=True, key=f"btn_disc_av_{v}"): 
                reset_forja()
            st.markdown("---")

        if f['fase'] == 1:
            st.markdown("### 📋 Fase 1: Briefing & Seleção de Conteúdos da Turma")
            st.caption("Monte exames alinhados às matrizes legais (BNCC/SAEB) extraindo automaticamente os tópicos ministrados no seu diário/plano.")
            
            modo_arq = st.pills(
                "Selecione a Abordagem do Instrumento:", 
                ["Nova Avaliação (Inédita ENEM/SAEB)", "Sonda Diagnóstica", "Variante Anti-Fraude (Clonagem)", "Recuperação Cirúrgica (Data-Driven)"], 
                default="Nova Avaliação (Inédita ENEM/SAEB)",
                key=f"pills_modo_av_{v}"
            )
            st.markdown("---")

            if "Inédita" in modo_arq or "Sonda" in modo_arq:
                with st.container(border=True):
                    st.markdown("#### 1. Parâmetros da Turma e Rigor Psicométrico")
                    c1, c2, c3, c4 = st.columns(4)
                    ano_av = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_av_sel_{v}")
                    trim_filtro = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"trim_av_sel_{v}")
                    v_total = c3.number_input("Valor Total da Prova (pts):", 0.0, 10.0, 4.0 if "Inédita" in modo_arq else 10.0, step=0.5, key=f"v_tot_input_{v}")
                    qtd_q = c4.number_input("Quantidade de Questões:", 1, 30, 10, key=f"qtd_q_input_{v}")

                    perfil_rigor = st.segmented_control(
                        "Equilíbrio TRI & Rigor Cognitivo:", 
                        ["⚖️ Padrão SAEB (30% F | 50% M | 20% D)", "🚀 Alta Performance (OBMEP)", "🧱 Recomposição (Acessível)"], 
                        default="⚖️ Padrão SAEB (30% F | 50% M | 20% D)",
                        key=f"rigor_pop_{v}"
                    )

                with st.container(border=True):
                    st.markdown("#### 2. Mineração de Fontes e Ancoragem no Livro Didático")
                    
                    fontes_ativas = st.pills(
                        "Fontes de Dados para Extração:", 
                        ["📚 Acervo de Aulas SOSA", "📖 Recorte do Livro Didático (PDF)", "✍️ Injeção Auxiliar do Professor"], 
                        default=["📖 Recorte do Livro Didático (PDF)"],
                        selection_mode="multi",
                        key=f"pills_fontes_av_{v}"
                    )
                    
                    mats_selecionados = []
                    txt_av_teo_ext, txt_av_ex_ext = "", ""
                    recorte_provas_livro = ""

                    c_safra1, c_safra2 = st.columns(2)

                    if "📚 Acervo de Aulas SOSA" in fontes_ativas:
                        df_ref = df_aulas[df_aulas['ANO'].astype(str).str.contains(str(ano_av))].copy() if not df_aulas.empty else pd.DataFrame()
                        if not df_ref.empty:
                            termos_proibidos = ["APLICAÇÃO", "TESTE", "PROVA", "SONDA", "AVALIAÇÃO", "REVISÃO", "2ª CHAMADA"]
                            df_ref = df_ref[~df_ref['TIPO_MATERIAL'].str.upper().str.contains('|'.join(termos_proibidos))]
                            mats_selecionados = c_safra1.multiselect("Aulas Ministradas do Acervo:", options=df_ref["TIPO_MATERIAL"].tolist(), key=f"mats_sel_av_{v}")

                    if "📖 Recorte do Livro Didático (PDF)" in fontes_ativas:
                        livros_av_disp = df_materiais[df_materiais['TIPO'].str.contains(str(ano_av), na=False)]['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
                        sel_livro_av = c_safra2.selectbox("Livro do Cofre Digital:", [""] + livros_av_disp, key=f"sel_livro_av_{v}")
                        
                        if sel_livro_av:
                            uri_livro_av = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_livro_av].iloc[0]['URI_ARQUIVO']
                            c_p_av1, c_p_av2 = st.columns(2)
                            pags_teo_av = c_p_av1.text_input("📘 Páginas de Teoria (Leitura):", placeholder="Ex: 184-186, 189", key=f"pags_teo_av_{v}")
                            pags_ex_av = c_p_av2.text_input("📝 Páginas de Exercícios (Fixação):", placeholder="Ex: 187-188, 190-192", key=f"pags_ex_av_{v}")
                            
                            list_p_av_teo = util.processar_intervalos_paginas(pags_teo_av)
                            list_p_av_ex = util.processar_intervalos_paginas(pags_ex_av)
                            
                            if list_p_av_teo or list_p_av_ex:
                                with st.spinner("🔍 Fatiando páginas do livro no Drive..."):
                                    bytes_pdf_av = db.baixar_bytes_arquivo_drive(uri_livro_av)
                                    if bytes_pdf_av:
                                        if list_p_av_teo: txt_av_teo_ext = util.extrair_texto_pdf_por_paginas(bytes_pdf_av, list_p_av_teo)
                                        if list_p_av_ex: txt_av_ex_ext = util.extrair_texto_pdf_por_paginas(bytes_pdf_av, list_p_av_ex)

                    st.markdown("##### 📌 Pinçamento da Prática Real (Lousa e Caderno)")
                    pincamento_pratica = st.text_area(
                        "Exercícios ou exemplos que os alunos resolveram no quadro/caderno (para criar Questões Espelho):",
                        placeholder="Ex: Pág. 185: exercícios 2, 4 e 5. Exemplo do quadro sobre desconto de 20% no comércio de Itabuna.",
                        height=75, key=f"pincamento_pratica_input_{v}"
                    )

                    if "✍️ Injeção Auxiliar do Professor" in fontes_ativas:
                        recorte_provas_livro = st.text_area(
                            "📖 Exercícios Autorais ou Textos do Professor:",
                            placeholder="Cole aqui textos ou questões autorais extras...",
                            height=75, key=f"recorte_provas_input_{v}"
                        )

                    topicos_candidatos = []
                    TERMOS_PROIBIDOS_ASSUNTO = r"(?i)(?:REVIS[AÃ]O|PROVA|TESTE|SONDA|DOSSI[EÊ]|RAIO-X|AVALIA[CÇ][AÃ]O|APLICA[CÇ][AÃ]O|2[ªA]\s*CHAMADA|RECUPERA[CÇ][AÃ]O|GABARITO|AULA\s*\d+|SEMANA\s*\d+)"

                    if pincamento_pratica.strip():
                        partes_lousa = re.split(r'[;\n•,]', pincamento_pratica)
                        for p_l in partes_lousa:
                            p_l_clean = re.sub(r'[*#\[\]]', '', p_l).strip()
                            if len(p_l_clean) > 3 and not re.search(TERMOS_PROIBIDOS_ASSUNTO, p_l_clean):
                                topicos_candidatos.append(p_l_clean)

                    if not df_planos.empty:
                        planos_trim = df_planos[
                            (df_planos['ANO'].astype(str).str.contains(str(ano_av))) & 
                            (df_planos['TURMA'].astype(str).str.upper().str.contains(trim_filtro.upper()))
                        ]
                        for _, r_plano in planos_trim.iterrows():
                            txt_p = str(r_plano.get('PLANO_TEXTO', ''))
                            c_espec = (
                                ai.extrair_tag(txt_p, "CONTEUDOS_ESPECIFICOS") or 
                                ai.extrair_tag(txt_p, "OBJETO_CONHECIMENTO") or 
                                ai.extrair_tag(txt_p, "HABILIDADE_BNCC")
                            )
                            if c_espec:
                                partes = re.split(r'[;\n•]', c_espec)
                                for p in partes:
                                    p_clean = re.sub(r'\[cite:.*?\]|[*#\[\]]', '', p).strip()
                                    if len(p_clean) > 3 and not re.search(TERMOS_PROIBIDOS_ASSUNTO, p_clean):
                                        topicos_candidatos.append(p_clean)

                    if not df_curriculo.empty:
                        col_ano_c = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None)
                        col_trim_c = next((c for c in df_curriculo.columns if trim_filtro.upper() in c.upper()), None)
                        
                        if col_ano_c and col_trim_c:
                            df_curr_trim = df_curriculo[df_curriculo[col_ano_c].astype(str).str.contains(str(ano_av))].copy()
                            for _, r_curr in df_curr_trim.iterrows():
                                txt_c = str(r_curr.get(col_trim_c, ''))
                                if txt_c and txt_c.upper() != "NAN":
                                    partes_c = re.split(r'[;\n•]', txt_c)
                                    for p_c in partes_c:
                                        p_c_clean = re.sub(r'\[cite:.*?\]|[*#\[\]]', '', p_c).strip()
                                        if len(p_c_clean) > 3 and not re.search(TERMOS_PROIBIDOS_ASSUNTO, p_c_clean):
                                            topicos_candidatos.append(p_c_clean)

                    topicos_candidatos_unicos = []
                    for t_item in topicos_candidatos:
                        if t_item not in topicos_candidatos_unicos and not re.search(TERMOS_PROIBIDOS_ASSUNTO, t_item):
                            topicos_candidatos_unicos.append(t_item)

                    if not topicos_candidatos_unicos:
                        topicos_candidatos_unicos = [f"Conteúdo Curricular de Matemática {ano_av}º Ano - {trim_filtro}"]

                    contexto_base_texto = ""
                    if pincamento_pratica.strip(): contexto_base_texto += f"--- PINÇAMENTO DA PRÁTICA REAL (RESOLVIDO EM SALA) ---\n{pincamento_pratica.strip()}\n\n"
                    if txt_av_teo_ext: contexto_base_texto += f"--- PÁGINAS DE TEORIA DO LIVRO DIDÁTICO ---\n{txt_av_teo_ext}\n\n"
                    if txt_av_ex_ext: contexto_base_texto += f"--- PÁGINAS DE EXERCÍCIOS DO LIVRO DIDÁTICO ---\n{txt_av_ex_ext}\n\n"
                    if recorte_provas_livro.strip(): contexto_base_texto += f"--- EXERCÍCIOS DO PROFESSOR ---\n{recorte_provas_livro.strip()}\n\n"

            with st.container(border=True):
                st.markdown(f"#### 3. 📋 Seletor Interativo de Conteúdos por Unidades Temáticas BNCC ({ano_av}º Ano - {trim_filtro})")
                st.caption("Marque exclusivamente os tópicos que você EFETIVAMENTE LECIONOU em sala para a IA gerar questões fiéis:")
                
                assuntos_marcados_prof = st.multiselect(
                    "Selecione os Conteúdos Ministrados:",
                    options=topicos_candidatos_unicos,
                    default=topicos_candidatos_unicos[:min(qtd_q, len(topicos_candidatos_unicos))],
                    key=f"ms_topicos_prof_{v}"
                )

                topico_autoral_extra = st.text_input(
                    "✍️ Adicionar outro conteúdo trabalhado não listado acima (Opcional):",
                    placeholder="Ex: Leitura de gráficos da Campanha Maio Laranja no comércio local",
                    key=f"topico_extra_input_{v}"
                )

                if topico_autoral_extra.strip():
                    if topico_autoral_extra.strip() not in assuntos_marcados_prof:
                        assuntos_marcados_prof.insert(0, topico_autoral_extra.strip())

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Iniciar Linha de Montagem de Itens (Avançar para Fase 2)", type="primary", use_container_width=True, key=f"btn_fase1_av_{v}"):
                if not assuntos_marcados_prof:
                    st.error("⚠️ Marque ao menos um conteúdo no seletor acima para forjar a prova.")
                else:
                    gabarito_mestre = util.gerar_gabarito_balanceado(qtd_q)
                    mapa_inicial = []
                    
                    for i in range(qtd_q):
                        assunto_item = assuntos_marcados_prof[i % len(assuntos_marcados_prof)]
                        mapa_inicial.append({
                            'q': i + 1, 
                            'tema': assunto_item,
                            'dificuldade': "Fácil" if i < (qtd_q*0.3) else ("Difícil" if i >= (qtd_q*0.8) else "Média"),
                            'gabarito': gabarito_mestre[i], 
                            'status': 'pendente', 
                            'dados': {} 
                        })
                    f['mapa'] = mapa_inicial
                    f['info'] = {'ano': f"{ano_av}º", 'trimestre': trim_filtro, 'valor': v_total, 'qtd': qtd_q, 'tipo_prova': "AVALIAÇÃO", 'rigor': perfil_rigor}
                    f['contexto_base'] = contexto_base_texto 
                    f['pincamento_lousa'] = pincamento_pratica
                    f['fase'] = 2
                    st.rerun()

            elif "Variante" in modo_arq:
                with st.container(border=True):
                    st.markdown("#### Parâmetros de Clonagem (Variante Anti-Fraude)")
                    c_cl1, c_cl2 = st.columns([1, 2])
                    ano_clone = c_cl1.selectbox("Série:", [6, 7, 8, 9], key=f"ano_clone_sel_{v}")
                    df_provas = df_aulas[(df_aulas['ANO'].astype(str).str.contains(str(ano_clone))) & (df_aulas['SEMANA_REF'] == "AVALIAÇÃO")] if not df_aulas.empty else pd.DataFrame()
                    
                    opcoes_provas = []
                    if not df_provas.empty:
                        opcoes_provas = [p for p in df_provas['TIPO_MATERIAL'].tolist() if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", str(p), re.IGNORECASE)]
                    
                    prova_base_sel = c_cl2.selectbox("Selecione a Prova de Origem:", [""] + opcoes_provas, key=f"p_base_sel_{v}")
                
                if prova_base_sel:
                    match_clone = df_provas[df_provas['TIPO_MATERIAL'] == prova_base_sel]
                    txt_base = str(match_clone.iloc[0].get('CONTEUDO', '')) if not match_clone.empty else ""
                    q_reg = ai.extrair_tag(txt_base, "QUESTOES")
                    qtd_detectada = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_reg)) or 10
                    st.success(f"Prova localizada com {qtd_detectada} questões.")
                    
                    if st.button("🚀 Forjar Variante Tipo B (Embaralhada)", type="primary", use_container_width=True, key=f"btn_clone_exe_{v}"):
                        with st.status("Forjando caderno variante...") as status:
                            info_clone = {'ano': f"{ano_clone}º", 'trimestre': "I Trimestre", 'valor': 4.0, 'qtd': qtd_detectada}
                            existentes = df_aulas[df_aulas['TIPO_MATERIAL'].str.startswith(prova_base_sel + " - TIPO", na=False)] if not df_aulas.empty else pd.DataFrame()
                            letra = chr(66 + len(existentes))
                            nome_var = f"{prova_base_sel} - TIPO {letra}"
                            
                            prompt = f"PROVA ORIGINAL:\n[QUESTOES]\n{q_reg}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(txt_base, 'GRADE_DE_CORRECAO')}"
                            res_hydra = ai.gerar_ia("ARQUITETO_VARIANTES_V100", prompt)
                            
                            texto_final_var = f"[VALOR: 4.0]\n\n[QUESTOES]\n{ai.extrair_tag(res_hydra, 'QUESTOES')}\n\n[GABARITO_TEXTO]\n{ai.extrair_tag(res_hydra, 'GABARITO_TEXTO')}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(res_hydra, 'GRADE_DE_CORRECAO')}\n\n[PEI_NIVEL_1]\n{ai.extrair_tag(txt_base, 'PEI_NIVEL_1')}\n\n[PEI_NIVEL_2]\n{ai.extrair_tag(txt_base, 'PEI_NIVEL_2')}\n\n[PEI_NIVEL_3]\n{ai.extrair_tag(txt_base, 'PEI_NIVEL_3')}\n\n"
                            doc_var = exporter.gerar_docx_prova_v25(nome_var, texto_final_var, info_clone)
                            link_var = db.subir_e_converter_para_google_docs(doc_var, nome_var, modo="AVALIACAO")
                            
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_var, texto_final_var + f"\n--- LINKS ---\nRegular({link_var})", f"{ano_clone}º", link_var])
                            status.update(label="Variante homologada e salva no Drive!", state="complete")
                        st.balloons(); time.sleep(1); st.rerun()

        elif f['fase'] == 2:
            st.markdown("### 🔬 Fase 2: Forja, Perícia & Lapidação dos Itens Regulares (TRI)")
            st.caption("Revise, edite a perícia de distratores e aprove cada item regular ANTES de avançar para a Tríade PEI.")

            total_q = len(f['mapa'])
            facil_c = sum(1 for item in f['mapa'] if item['dificuldade'] == "Fácil")
            media_c = sum(1 for item in f['mapa'] if item['dificuldade'] == "Média")
            dificil_c = sum(1 for item in f['mapa'] if item['dificuldade'] == "Difícil")
            
            perc_facil = (facil_c / total_q) * 100 if total_q > 0 else 0
            perc_media = (media_c / total_q) * 100 if total_q > 0 else 0
            perc_dificil = (dificil_c / total_q) * 100 if total_q > 0 else 0

            with st.container(border=True):
                st.markdown("##### 📊 Régua de Equilíbrio Psicométrico da Prova (TRI)")
                col_tri1, col_tri2, col_tri3, col_tri4 = st.columns(4)
                col_tri1.metric("Total de Itens", total_q)
                col_tri2.metric("🔵 Fáceis (30%)", f"{facil_c} ({perc_facil:.0f}%)")
                col_tri3.metric("🟡 Médias (50%)", f"{media_c} ({perc_media:.0f}%)")
                col_tri4.metric("🔴 Difíceis (20%)", f"{dificil_c} ({perc_dificil:.0f}%)")

            st.markdown("<br>", unsafe_allow_html=True)
            modo_leitura_forja = st.toggle("👁️ Modo Leitura Real (Renderizar Matemática LaTeX e Prompts)", value=True, key=f"tog_read_forja_{v}")

            pendentes = [item for item in f['mapa'] if item['status'] == 'pendente']

            if pendentes:
                if st.button(f"🚀 GERAR LOTE DE {len(pendentes)} QUESTÕES REGULARES (ZERO-ALUCINAÇÃO VIA GEMINI 3.6 FLASH)", type="primary", use_container_width=True, key=f"btn_lote_av_{v}"):
                    with st.spinner("Forjando itens ancorados estritamente nos assuntos do seu plano e na prática real..."):
                        prompt_lote = (
                            f"SÉRIE: {f['info']['ano']}\n"
                            f"VALOR TOTAL DA PROVA: {f['info']['valor']}\n\n"
                            f"🚨 REGRAS INQUEBRÁVEIS DE ANCORAGEM:\n"
                            f"- Crie cada questão estritamente focada no TEMA ESPECÍFICO atribuído a ela abaixo.\n"
                            f"- É PROIBIDO inventar assuntos fora da matriz e da prática do professor.\n\n"
                        )
                        for item in pendentes:
                            prompt_lote += f"QUESTÃO {item['q']}:\n- TEMA ESPECÍFICO EXIGIDO: {item['tema']}\n- COMPLEXIDADE: {item['dificuldade']}\n- GABARITO EXIGIDO: Letra {item['gabarito']}\n\n"
                        
                        prompt_lote += f"--- CONTEXTO E PINÇAMENTO DA PRÁTICA REAL (OBRIGATÓRIO USAR) ---\n{f.get('contexto_base', 'Usar a matriz do ' + str(f['info']['ano']) + ' Ano e o contexto de Itabuna/BA.')}\n"
                        
                        res_json = ai.gerar_ia_json("FORJA_LOTE_JSON", prompt_lote)
                        if "erro" in res_json:
                            st.error(f"⚠️ Erro ao processar o lote: {res_json['erro']}")
                        else:
                            TERMOS_PROIBIDOS_ASSUNTO = r"(?i)(?:REVIS[AÃ]O|PROVA|TESTE|SONDA|DOSSI[EÊ]|RAIO-X|AVALIA[CÇ][AÃ]O|APLICA[CÇ][AÃ]O|2[ªA]\s*CHAMADA|RECUPERA[CÇ][AÃ]O|GABARITO|AULA\s*\d+|SEMANA\s*\d+)"
                            for q_data in res_json.get("questoes", []):
                                q_num = int(q_data.get("q", 0))
                                for item in f['mapa']:
                                    if item['q'] == q_num:
                                        descritor_real = q_data.get('habilidade', '')
                                        if descritor_real and len(descritor_real) > 2 and not re.search(TERMOS_PROIBIDOS_ASSUNTO, descritor_real):
                                            item['tema'] = f"{descritor_real} - {item['tema']}" if "D" in descritor_real[:3] or "EF" in descritor_real[:3] else descritor_real
                                        
                                        item['dados'] = {
                                            'ENUNCIADO': q_data.get('enunciado', ''),
                                            'ALT_A': q_data.get('alt_a', ''),
                                            'ALT_B': q_data.get('alt_b', ''),
                                            'ALT_C': q_data.get('alt_c', ''),
                                            'ALT_D': q_data.get('alt_d', ''),
                                            'ALT_E': q_data.get('alt_e', ''),
                                            'HABILIDADE': descritor_real if descritor_real else item['tema'],
                                            'JUSTIFICATIVA': q_data.get('justificativa', ''),
                                            'DISTRATORES': q_data.get('distratores', ''),
                                            'GABARITO': item['gabarito']
                                        }
                                        item['status'] = 'revisao'
                            st.rerun()

            st.markdown("---")
            todas_aprovadas = True

            for i, item in enumerate(f['mapa']):
                label_status = "✅ Aprovado" if item['status'] == 'aprovado' else ("🔍 Em Revisão" if item['status'] == 'revisao' else "⏳ Pendente")
                assunto_exibicao = item['tema'] if item['tema'] and item['tema'].strip() not in ["**", ""] and not re.search(r"(?i)^(?:REVIS[AÃ]O|PROVA|TESTE|DOSSI[EÊ])", item['tema']) else f"Tópico Curricular de Matemática - Item {item['q']:02d}"

                with st.container(border=True):
                    c_card_head1, c_card_head2 = st.columns([3, 1])
                    c_card_head1.markdown(f"**📌 ITEM {item['q']:02d} | Nível: {item['dificuldade']}**")
                    c_card_head2.caption(f"Status: **{label_status}** | Gabarito: **({item['gabarito']})**")

                    if item['status'] == 'pendente':
                        todas_aprovadas = False
                        c_t1, c_t2 = st.columns([3, 1])
                        tema_q = c_t1.text_input("Assunto / Contexto Específico do Item:", value=assunto_exibicao, key=f"t_{i}_{v}")
                        item['tema'] = tema_q
                        dif_q = c_t2.selectbox("Complexidade TRI:", ["Fácil", "Média", "Difícil"], index=["Fácil", "Média", "Difícil"].index(item['dificuldade']), key=f"d_{i}_{v}")
                        
                        if st.button(f"Forjar Item {item['q']} Individualmente", key=f"btn_gen_ind_{i}_{v}", use_container_width=True):
                            with st.spinner("Desenhando item ancorado no seu assunto..."):
                                prompt = f"SÉRIE: {f['info']['ano']}\nTEMA ESPECÍFICO: {tema_q}. DIFICULDADE: {dif_q}. GABARITO: {item['gabarito']}.\n🚨 USE EXCLUSIVAMENTE O CONTEXTO FORNECIDO:\n{f.get('contexto_base', '')}"
                                res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                ext = {tag: ai.extrair_tag(res_item, tag) for tag in ['ENUNCIADO', 'ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E', 'HABILIDADE', 'JUSTIFICATIVA', 'DISTRATORES']}
                                
                                descritor_ind = ext['HABILIDADE'] if ext['HABILIDADE'] else tema_q
                                item['tema'] = descritor_ind
                                item['dados'] = {
                                    'ENUNCIADO': ext['ENUNCIADO'], 'ALT_A': ext['ALT_A'], 'ALT_B': ext['ALT_B'], 'ALT_C': ext['ALT_C'],
                                    'ALT_D': ext['ALT_D'], 'ALT_E': ext['ALT_E'], 'HABILIDADE': descritor_ind, 'JUSTIFICATIVA': ext['JUSTIFICATIVA'],
                                    'DISTRATORES': ext['DISTRATORES'], 'GABARITO': item['gabarito']
                                }
                                item['status'] = 'revisao'
                                st.rerun()

                    elif item['status'] in ['revisao', 'aprovado']:
                        if item['status'] == 'revisao': todas_aprovadas = False
                        d = item['dados']

                        if modo_leitura_forja:
                            with st.container(border=True):
                                st.markdown(f"**Assunto:** `{assunto_exibicao}`")
                                st.markdown(preparar_para_leitura(f"**QUESTÃO {item['q']:02d} -** {d['ENUNCIADO']}"))
                                
                                mark_a = "✅ " if d['GABARITO'] == 'A' else ""
                                mark_b = "✅ " if d['GABARITO'] == 'B' else ""
                                mark_c = "✅ " if d['GABARITO'] == 'C' else ""
                                mark_d = "✅ " if d['GABARITO'] == 'D' else ""
                                mark_e = "✅ " if d['GABARITO'] == 'E' else ""

                                col_alt_a, col_alt_b = st.columns(2)
                                col_alt_a.markdown(f"**(A)** {mark_a}{preparar_para_leitura(d['ALT_A'])}")
                                col_alt_b.markdown(f"**(B)** {mark_b}{preparar_para_leitura(d['ALT_B'])}")
                                col_alt_a.markdown(f"**(C)** {mark_c}{preparar_para_leitura(d['ALT_C'])}")
                                col_alt_b.markdown(f"**(D)** {mark_d}{preparar_para_leitura(d['ALT_D'])}")
                                if d.get('ALT_E'): st.markdown(f"**(E)** {mark_e}{preparar_para_leitura(d['ALT_E'])}")

                        with st.expander("🔬 Ver Perícia TRI e Análise Científica de Distratores", expanded=False):
                            st.caption(f"🆔 **Descritor SAEB/BNCC:** {d.get('HABILIDADE', assunto_exibicao)}")
                            st.write(f"🎯 **Gabarito Justificado:** {d.get('JUSTIFICATIVA', 'Não especificada')}")
                            st.warning(f"🧠 **Distratores Científicos (Erros Mapeados):**\n{d.get('DISTRATORES', 'Não especificados')}")

                        with st.expander("✏️ Editar Enunciado, Alternativas, Descritor e Gabarito", expanded=False):
                            item['tema'] = st.text_input("Assunto do Card:", value=assunto_exibicao, key=f"ed_tema_inp_{i}_{v}")
                            d['ENUNCIADO'] = st.text_area("Enunciado:", value=d['ENUNCIADO'], height=100, key=f"ed_en_{i}_{v}")
                            
                            c_a1, c_a2 = st.columns(2)
                            d['ALT_A'] = c_a1.text_input("(A):", value=d['ALT_A'], key=f"ed_a_{i}_{v}")
                            d['ALT_B'] = c_a2.text_input("(B):", value=d['ALT_B'], key=f"ed_b_{i}_{v}")
                            d['ALT_C'] = c_a1.text_input("(C):", value=d['ALT_C'], key=f"ed_c_{i}_{v}")
                            d['ALT_D'] = c_a2.text_input("(D):", value=d['ALT_D'], key=f"ed_d_{i}_{v}")
                            d['ALT_E'] = c_a1.text_input("(E):", value=d['ALT_E'], key=f"ed_e_{i}_{v}")
                            
                            d['GABARITO'] = st.selectbox("Gabarito Oficial:", ["A", "B", "C", "D", "E"], index=["A", "B", "C", "D", "E"].index(d['GABARITO']), key=f"ed_gab_sel_{i}_{v}")
                            d['HABILIDADE'] = st.text_input("Descritor SAEB/BNCC:", value=d.get('HABILIDADE', assunto_exibicao), key=f"ed_hab_{i}_{v}")
                            d['JUSTIFICATIVA'] = st.text_area("Justificativa do Gabarito:", value=d.get('JUSTIFICATIVA', ''), height=60, key=f"ed_just_{i}_{v}")

                        inst_ref = st.text_input("Refinar esta questão com IA (Ex: 'Incorpore a produção de cacau de Itabuna'):", key=f"inst_ref_{i}_{v}")
                        col_b1, col_b2 = st.columns(2)
                        
                        if item['status'] == 'revisao':
                            if col_b1.button(f"✅ Aprovar Item {item['q']}", type="primary", key=f"btn_apr_{i}_{v}", use_container_width=True):
                                item['status'] = 'aprovado'
                                st.rerun()
                        else:
                            if col_b1.button(f"✏️ Reabrir Item {item['q']} para Revisão", key=f"btn_reabrir_{i}_{v}", use_container_width=True):
                                item['status'] = 'revisao'
                                st.rerun()

                        if col_b2.button(f"🔄 Regerar Item {item['q']} com IA", key=f"btn_ref_{i}_{v}", use_container_width=True):
                            with st.spinner("Reestruturando item sem alucinação..."):
                                prompt = f"SÉRIE: {f['info']['ano']}\nTEMA ESPECÍFICO: {assunto_exibicao}. GABARITO: {item['gabarito']}.\nAJUSTE SOLICITADO: {inst_ref}\nENUNCIADO ANTERIOR:\n{d['ENUNCIADO']}\n\n🚨 CONTEXTO OBRIGATÓRIO:\n{f.get('contexto_base', '')}"
                                res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                ext = {tag: ai.extrair_tag(res_item, tag) for tag in ['ENUNCIADO', 'ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E', 'HABILIDADE', 'JUSTIFICATIVA', 'DISTRATORES']}
                                item['dados'] = {
                                    'ENUNCIADO': ext['ENUNCIADO'], 'ALT_A': ext['ALT_A'], 'ALT_B': ext['ALT_B'], 'ALT_C': ext['ALT_C'],
                                    'ALT_D': ext['ALT_D'], 'ALT_E': ext['ALT_E'], 'HABILIDADE': ext['HABILIDADE'], 'JUSTIFICATIVA': ext['JUSTIFICATIVA'],
                                    'DISTRATORES': ext['DISTRATORES'], 'GABARITO': item['gabarito']
                                }
                                item['status'] = 'revisao'
                                st.rerun()

            if todas_aprovadas and len(f['mapa']) > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.success("🎉 **Caderno Regular 100% Homologado!** Clique abaixo para avançar para a Tríade PEI On-Demand.")
                if st.button("🚀 APROVAR CADERNO REGULAR COMPLETO E AVANÇAR PARA FASE 3 (PEI ON-DEMAND)", type="primary", use_container_width=True, key=f"btn_fase2_next_{v}"):
                    f['fase'] = 3
                    st.rerun()

        elif f['fase'] == 3:
            st.markdown("### ♿ Fase 3: Tríade Inclusiva PEI On-Demand")
            st.caption("Gere EXCLUSIVAMENTE os cadernos PEI que você necessita para esta turma. Níveis não marcados serão ignorados economizando tempo e arquivos.")

            with st.container(border=True):
                st.markdown("#### 🎯 Marque os Níveis PEI Necessários para esta Turma:")
                
                niveis_selecionados = st.pills(
                    "Selecione os Níveis Desejados:",
                    ["🔵 PEI Nível 1 (Apoio Leve - 3 Opções)", "🟡 PEI Nível 2 (Apoio Moderado - Passo a Passo)", "🔴 PEI Nível 3 (Suporte Severo - 100% no Papel)"],
                    default=["🔵 PEI Nível 1 (Apoio Leve - 3 Opções)", "🔴 PEI Nível 3 (Suporte Severo - 100% no Papel)"],
                    selection_mode="multi",
                    key=f"pills_niveis_pei_{v}"
                )

            st.markdown("<br>", unsafe_allow_html=True)
            
            pede_n1 = any("Nível 1" in n for n in niveis_selecionados)
            pede_n2 = any("Nível 2" in n for n in niveis_selecionados)
            pede_n3 = any("Nível 3" in n for n in niveis_selecionados)

            if st.button("🧠 FORJAR APENAS OS NÍVEIS PEI SELECIONADOS", type="primary", use_container_width=True, key=f"btn_gen_triade_f3_{v}"):
                with st.status("Construindo materiais de inclusão selecionados...", expanded=True) as status:
                    texto_base_reg = f"[VALOR: {f['info']['valor']}]\n\n"
                    for item in f['mapa']:
                        d = item['dados']
                        texto_base_reg += f"**QUESTÃO {item['q']:02d} -** {d['ENUNCIADO']}\n(A) {d['ALT_A']}\n(B) {d['ALT_B']}\n(C) {d['ALT_C']}\n(D) {d['ALT_D']}\n(E) {d['ALT_E']}\n\n"

                    if pede_n1:
                        status.write("🔵 Forjando PEI Nível 1 (Apoio Leve - 3 Alternativas A, B, C)...")
                        f['pei_1'] = ai.gerar_ia("FORJA_PEI_N1", f"REGULAR:\n{texto_base_reg}")
                    else: f['pei_1'] = ""

                    if pede_n2:
                        status.write("🟡 Forjando PEI Nível 2 (Apoio Moderado - Passo a Passo)...")
                        f['pei_2'] = ai.gerar_ia("FORJA_PEI_N2", f"REGULAR:\n{texto_base_reg}")
                    else: f['pei_2'] = ""

                    if pede_n3:
                        status.write("🔴 Forjando PEI Nível 3 (10 Atividades Impressas no Papel: Pintar/Ligar/Pontilhado)...")
                        f['pei_3'] = ai.gerar_ia("FORJA_PEI_N3", f"REGULAR:\n{texto_base_reg}")
                    else: f['pei_3'] = ""

                    status.update(label="✅ Materiais PEI Selecionados Forjados!", state="complete")
                    st.rerun()

            if f.get('pei_1') or f.get('pei_2') or f.get('pei_3'):
                modo_leitura_pei = st.toggle("👁️ Visualização Real PEI (Renderizar LaTeX)", value=True, key=f"read_pei_tog_{v}")
                
                abas_existentes_pei = []
                if pede_n1 or f.get('pei_1'): abas_existentes_pei.append("🔵 PEI Nível 1")
                if pede_n2 or f.get('pei_2'): abas_existentes_pei.append("🟡 PEI Nível 2")
                if pede_n3 or f.get('pei_3'): abas_existentes_pei.append("🔴 PEI Nível 3 (Papel)")

                tabs_pei = st.tabs(abas_existentes_pei)
                
                tab_idx = 0
                if "🔵 PEI Nível 1" in abas_existentes_pei:
                    with tabs_pei[tab_idx]:
                        if modo_leitura_pei:
                            with st.container(border=True): st.markdown(preparar_para_leitura(f['pei_1']))
                        f['pei_1'] = st.text_area("Edição Manual PEI N1 (3 Alternativas A, B, C):", value=f['pei_1'], height=250, key=f"ed_p1_area_{v}")
                    tab_idx += 1

                if "🟡 PEI Nível 2" in abas_existentes_pei:
                    with tabs_pei[tab_idx]:
                        if modo_leitura_pei:
                            with st.container(border=True): st.markdown(preparar_para_leitura(f['pei_2']))
                        f['pei_2'] = st.text_area("Edição Manual PEI N2 (Com Dica + Passo a Passo):", value=f['pei_2'], height=250, key=f"ed_p2_area_{v}")
                    tab_idx += 1

                if "🔴 PEI Nível 3 (Papel)" in abas_existentes_pei:
                    with tabs_pei[tab_idx]:
                        if modo_leitura_pei:
                            with st.container(border=True):
                                st.markdown("#### 📦 Estrutura dos 10 Bento Boxes (Atividades no Papel)")
                                st.markdown(preparar_para_leitura(f['pei_3']))
                        f['pei_3'] = st.text_area("Edição Manual PEI N3 (10 BOXES + Rubrica de Observação):", value=f['pei_3'], height=250, key=f"ed_p3_area_{v}")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ APROVAR MATERIAIS PEI E AVANÇAR PARA FASE 4 (CUSTÓDIA & DRIVE)", type="primary", use_container_width=True, key=f"btn_fase3_next_{v}"):
                    f['fase'] = 4
                    st.rerun()

        elif f['fase'] == 4:
            st.markdown("### 💾 Fase 4: Custódia & Sincronia Google Drive")
            st.caption("Geração de arquivos oficiais no Word com Cartão OMR Fiducial, Bento Cards e links de acesso direto.")

            tipo_nome = f['info'].get('tipo_prova', 'AVALIAÇÃO').upper().replace(' ', '_')
            nome_sugerido = f"{tipo_nome}_{f['info']['ano'].replace('º','')}ANO_{f['info']['trimestre'].replace(' ', '')}"
            nome_arq = st.text_input("Identificador Técnico no Cofre Digital:", value=nome_sugerido, key=f"nome_arq_f4_{v}")

            if st.button("💾 FINALIZAR E SINCRONIZAR TUDO NO GOOGLE DRIVE", type="primary", use_container_width=True, key=f"btn_fase4_sync_{v}"):
                with st.status("Gerando Documentos Word e Enviando para o Drive...", expanded=True) as status:
                    txt_regular = f"[VALOR: {f['info']['valor']}]\n\n[QUESTOES]\n"
                    txt_gabarito = "[GABARITO_TEXTO]\n"
                    txt_grade = "[GRADE_DE_CORRECAO]\n"

                    for item in f['mapa']:
                        d = item['dados']
                        txt_regular += f"**QUESTÃO {item['q']:02d} -** {d['ENUNCIADO']}\n(A) {d['ALT_A']}\n(B) {d['ALT_B']}\n(C) {d['ALT_C']}\n(D) {d['ALT_D']}\n(E) {d['ALT_E']}\n\n"
                        txt_gabarito += f"QUESTÃO {item['q']:02d}: {d['GABARITO']}\n"
                        txt_grade += f"QUESTÃO {item['q']:02d}: [DESCRITOR_SAEB: {d['HABILIDADE']}] | JUSTIFICATIVA: {d['JUSTIFICATIVA']} | DISTRATORES_CIENTIFICOS: {d['DISTRATORES']}\n"

                    texto_final_padrao = txt_regular + txt_gabarito + txt_grade

                    status.write("📄 Gerando Caderno Regular Word (OMR Fiducial)...")
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, texto_final_padrao, f['info'])
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, modo="AVALIACAO")

                    link_p1, link_p2, link_p3 = "N/A", "N/A", "N/A"

                    if f.get('pei_1'):
                        status.write("🔵 Gerando Caderno PEI Nível 1 Word...")
                        doc_p1 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N1", f['pei_1'], f['info'])
                        link_p1 = db.subir_e_converter_para_google_docs(doc_p1, f"{nome_arq}_PEI_N1", modo="AVALIACAO")

                    if f.get('pei_2'):
                        status.write("🟡 Gerando Caderno PEI Nível 2 Word...")
                        doc_p2 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N2", f['pei_2'], f['info'])
                        link_p2 = db.subir_e_converter_para_google_docs(doc_p2, f"{nome_arq}_PEI_N2", modo="AVALIACAO")

                    if f.get('pei_3'):
                        status.write("🔴 Gerando Caderno PEI Nível 3 Word (Bento Cards + Rubrica)...")
                        doc_p3 = exporter.gerar_docx_pei_qualitativa(f"{nome_arq}_PEI_N3", f['pei_3'], f['info'])
                        link_p3 = db.subir_e_converter_para_google_docs(doc_p3, f"{nome_arq}_PEI_N3", modo="AVALIACAO")

                    links_f = f"--- LINKS ---\nRegular({link_reg}) PEI_N1({link_p1}) PEI_N2({link_p2}) PEI_N3({link_p3})"
                    
                    conteudo_banco = (
                        f"{texto_final_padrao}\n\n"
                        f"[PEI_NIVEL_1]\n{f.get('pei_1', '')}\n\n"
                        f"[PEI_NIVEL_2]\n{f.get('pei_2', '')}\n\n"
                        f"[PEI_NIVEL_3]\n{f.get('pei_3', '')}\n\n"
                        f"{links_f}"
                    )

                    db.salvar_no_banco("DB_AULAS_PRONTAS", [
                        datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_arq,
                        conteudo_banco, f['info']['ano'], link_reg
                    ])

                    f['prova_final_txt'] = texto_final_padrao
                    f['nome_base'] = nome_arq
                    status.update(label="✅ Avaliação homologada e sincronizada no Drive!", state="complete")
                    st.balloons(); f['fase'] = 5; time.sleep(1); st.rerun()

        elif f['fase'] == 5:
            st.success(f"🏆 Avaliação **{f.get('nome_base', '')}** homologada com sucesso no Acervo!")
            st.markdown("### 🔄 Processo Concluído com Sucesso!")
            st.info("💡 Para gerar o Caderno de Recomposição/Revisão para os alunos, acesse a **Aba 3 (Recomposição & Cadernos de Revisão)** ou vá na **Aba 4 (Expedição)** para gerar o e-mail de remessa para a xerox.")

            if st.button("🎉 Concluir e Voltar ao Início", use_container_width=True, key=f"btn_fin_f5_{v}"):
                reset_forja()

    # ==============================================================================
    # ABA 2: ACERVO DE PROVAS & PERÍCIA TRI (VACINA ANTI-KEYERROR V2026)
    # ==============================================================================
    with tab_acervo_av:
        st.markdown("### 📖 Acervo de Instrumentos Avaliativos & Perícia TRI")
        
        with st.container(border=True):
            c_h1, c_h2, c_h3 = st.columns(3)
            f_trim_h = c_h1.selectbox("Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key=f"h_trim_av_{v}")
            f_ano_h = c_h2.selectbox("Série:", ["Todos", "6º", "7º", "8º", "9º"], key=f"h_ano_av_{v}")
            f_tipo_h = c_h3.selectbox("Tipo:", ["Todos", "AVALIAÇÃO", "REVISÃO"], key=f"h_tipo_av_{v}")

        df_exames = pd.DataFrame()
        if not df_aulas.empty and 'SEMANA_REF' in df_aulas.columns:
            df_exames = df_aulas[df_aulas['SEMANA_REF'].astype(str).str.upper().isin(["AVALIAÇÃO", "REVISÃO"])].copy()

        if not df_exames.empty:
            if f_trim_h != "Todos" and 'CONTEUDO' in df_exames.columns:
                df_exames = df_exames[df_exames['CONTEUDO'].astype(str).str.contains(f_trim_h, na=False)]
            if f_ano_h != "Todos" and 'ANO' in df_exames.columns:
                df_exames = df_exames[df_exames['ANO'].astype(str) == f_ano_h]
            if f_tipo_h != "Todos" and 'SEMANA_REF' in df_exames.columns:
                df_exames = df_exames[df_exames['SEMANA_REF'].astype(str).str.upper() == f_tipo_h.upper()]

            df_exames = df_exames.iloc[::-1]

        if df_exames.empty:
            st.info("Nenhum instrumento avaliativo localizado no acervo.")
        else:
            for idx_av, (_, row) in enumerate(df_exames.iterrows()):
                with st.container(border=True):
                    txt_f = str(row.get('CONTEUDO', ''))
                    identificador = str(row.get('TIPO_MATERIAL', 'AVALIAÇÃO'))
                    ano_exibicao = str(row.get('ANO', '6º'))
                    data_exibicao = str(row.get('DATA', 'N/A'))
                    semana_ref_exibicao = str(row.get('SEMANA_REF', 'AVALIAÇÃO'))

                    val_raw = ai.extrair_tag(txt_f, "VALOR")
                    val_num = util.sosa_to_float(val_raw)
                    val_ex = f"{val_num:.1f} pts" if val_num > 0 else "4.0 pts"
                    
                    st.markdown(f"##### 📋 {identificador}")
                    st.caption(f"Série: {ano_exibicao} | Data: {data_exibicao} | Status: 🔒 COFRE DIGITAL DRIVE SINCRONIZADO")
                    
                    def extrair_link_acervo(t, tag):
                        m = re.search(rf"{tag}\((https://docs\.google\.com/document/d/[^\s\)]+)\)", t, re.IGNORECASE)
                        return m.group(1).strip() if m else None

                    l_reg = extrair_link_acervo(txt_f, "Regular") or row.get('LINK_DRIVE')
                    l_pei1 = extrair_link_acervo(txt_f, "PEI_N1") or extrair_link_acervo(txt_f, "PEI")
                    l_pei2 = extrair_link_acervo(txt_f, "PEI_N2")
                    l_pei3 = extrair_link_acervo(txt_f, "PEI_N3")

                    c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
                    
                    if l_reg and "http" in str(l_reg): c_b1.link_button("📄 Regular", str(l_reg), use_container_width=True, type="primary")
                    else: c_b1.button("Sem Doc", disabled=True, use_container_width=True, key=f"no_reg_{row.name}_{idx_av}_{v}")
                    
                    if l_pei1 and "http" in str(l_pei1): c_b2.link_button("🔵 PEI N1", str(l_pei1), use_container_width=True)
                    else: c_b2.button("Sem N1", disabled=True, use_container_width=True, key=f"no_p1_{row.name}_{idx_av}_{v}")
                    
                    if l_pei2 and "http" in str(l_pei2): c_b3.link_button("🟡 PEI N2", str(l_pei2), use_container_width=True)
                    else: c_b3.button("Sem N2", disabled=True, use_container_width=True, key=f"no_p2_{row.name}_{idx_av}_{v}")
                    
                    if l_pei3 and "http" in str(l_pei3): c_b4.link_button("🔴 PEI N3", str(l_pei3), use_container_width=True)
                    else: c_b4.button("Sem N3", disabled=True, use_container_width=True, key=f"no_p3_{row.name}_{idx_av}_{v}")
                    
                    if c_b5.button("🗑️ Apagar", key=f"del_ac_{row.name}_{idx_av}_{v}", use_container_width=True):
                        if db.excluir_avaliacao_completa(identificador, semana_ref_exibicao): st.rerun()

                    with st.popover("🚀 Injetar no Ponto ID (Gerar Plano de Aula da Semana)"):
                        st.caption("A IA analisará as questões deste material para gerar um Plano de Aula Semanal 100% coerente, rico e padronizado no Ponto ID.")
                        
                        todas_semanas_inj_a2 = util.gerar_semanas()
                        sem_dest_a2 = st.selectbox("Selecione a Semana da Aula:", [s.split(" (")[0] for s in todas_semanas_inj_a2 if "Jornada" not in s], key=f"sel_sem_inj_a2_{row.name}_{v}")
                        trim_dest_a2 = st.selectbox("Trimestre Alvo:", ["I Trimestre", "II Trimestre", "III Trimestre"], index=1 if "II" in txt_f or "IITrimestre" in identificador else 0, key=f"sel_trim_inj_a2_{row.name}_{v}")
                        
                        if st.button("🚀 CONFIRMAR E GERAR PLANO COERENTE NO PONTO ID", type="primary", use_container_width=True, key=f"btn_inj_acervo_{row.name}_{v}"):
                            with st.spinner("Analisando as questões do material e redigindo o Plano de Aula Padronizado..."):
                                prompt_plano_revisao = (
                                    f"SÉRIE: {ano_exibicao} Ano.\n"
                                    f"SEMANA: {sem_dest_a2}. TRIMESTRE: {trim_dest_a2}.\n"
                                    f"IDENTIFICADOR DO MATERIAL: {identificador}.\n\n"
                                    f"SITUAÇÃO: O professor já criou o Caderno de Revisão e está aplicando em sala. Analise o texto do material abaixo e extraia os descritores SAEB reais, tópicos de matemática e elabore um Plano de Aula Semanal COERENTE, TÉCNICO E PADRONIZADO.\n\n"
                                    f"TEXTO DO MATERIAL DE REVISÃO:\n{txt_f[:3500]}\n\n"
                                    f"🚨 REDIJA UTILIZANDO ESTRITAMENTE AS TAGS COM COLCHETES:\n"
                                    f"[HABILIDADE_BNCC] (Liste as Habilidades BNCC e Descritores SAEB reais extraídos das questões do material)\n"
                                    f"[COMPETENCIAS_FOCO] Competência Específica 2 (Raciocínio Lógico) e 6 (Enfrentar Situações-Problema)\n"
                                    f"[OBJETO_CONHECIMENTO] RECOMPOSIÇÃO DE APRENDIZAGEM & REVISÃO DE MATEMÁTICA\n"
                                    f"[CONTEUDOS_ESPECIFICOS] (Liste de forma clara os tópicos matemáticos reais abordados nas questões: ex: Divisibilidade, Frações, Porcentagem, Perímetro, etc.)\n"
                                    f"[OBJETIVOS_ENSINO] Consolidar os objetos de conhecimento e superar as lacunas observadas nas avaliações do trimestre.\n"
                                    f"[JUSTIFICATIVA_PEDAGOGICA] Recomposição e revisão contínua de aprendizagem regimental.\n"
                                    f"[AULA_1] INÍCIO (Sensibilização - 10 min): Acolhimento da turma, apresentação dos objetivos e orientação sobre o Caderno de Revisão.\nMEIO (Fundamentação - 25 min): Resolução comentada no quadro das questões do Caderno de Revisão com foco nos descritores críticos.\nFIM (Fixação - 15 min): Síntese das estratégias e verificação das dúvidas.\n"
                                    f"[AULA_2] INÍCIO (10 min): Orientações para resolução autônoma do Caderno de Revisão.\nMEIO (35 min): Acompanhamento e suporte mediado aos estudantes (incluindo cadernos adaptados PEI N1, N2 e N3).\nFIM (5 min): Visto nos cadernos e consolidação do roteiro.\n"
                                    f"[SABADO_LETIVO] N/A\n"
                                    f"[AVALIACAO_DE_MERITO] Observação direta do engajamento e visto na resolução das questões do caderno de revisão.\n"
                                    f"[ESTRATEGIA_DUA_PEI] Utilização de cadernos adaptados (PEI N1, N2 e N3) com suporte visual e mediação individualizada."
                                )

                                plano_inj_txt = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_plano_revisao, usar_busca=False)

                                try:
                                    wb_inj = db.conectar()
                                    ws_aulas_inj = wb_inj.worksheet("DB_AULAS_PRONTAS")
                                    dados_aulas_inj = ws_aulas_inj.get_all_values()
                                    for idx_a_inj, row_a_inj in enumerate(dados_aulas_inj):
                                        if idx_a_inj > 0 and len(row_a_inj) > 2 and row_a_inj[2] == identificador:
                                            ws_aulas_inj.update_cell(idx_a_inj + 1, 2, sem_dest_a2)
                                            break
                                except Exception as e_inj:
                                    print(f"Aviso no vinculo da semana: {e_inj}")

                                st.session_state.p_temp = plano_inj_txt
                                st.session_state.p_meta = {
                                    "semana": sem_dest_a2,
                                    "trimestre": trim_dest_a2,
                                    "ano": ano_exibicao,
                                    "base": f"Material de Revisão: {identificador}",
                                    "status_final": "PRODUZIDO"
                                }
                                
                                st.toast("✅ Plano de Aula coerente gerado e vinculado à semana!", icon="🚀")
                                st.cache_data.clear()
                                time.sleep(0.8)
                                navegar_para("📅 Planejamento (Ponto ID)")

                    with st.expander("🔄 Re-gerar / Re-exportar Documentos (DOCX) no Drive", expanded=False):
                        st.info("💡 **Re-exportação Direta:** Clique abaixo para re-gerar os arquivos DOCX no Google Drive utilizando o texto preservado no banco de dados.")
                        
                        if st.button("🚀 EXECUTAR RE-EXPORTAÇÃO COMPLETA NO DRIVE", type="primary", use_container_width=True, key=f"btn_reexp_{row.name}_{idx_av}_{v}"):
                            with st.status("Re-gerando documentos Word com a vacina no Drive...", expanded=True) as status_reexp:
                                info_reexp = {
                                    'ano': ano_exibicao, 
                                    'trimestre': f_trim_h if f_trim_h != "Todos" else 'I Trimestre', 
                                    'valor': val_ex if val_ex else '4.0',
                                    'qtd': len(re.findall(r'(?i)QUESTÃO\s+\d+', txt_f)) or 10
                                }
                                
                                status_reexp.write("📄 Re-gerando Caderno Regular Word...")
                                doc_reg_r = exporter.gerar_docx_prova_v25(identificador, txt_f, info_reexp)
                                link_reg_r = db.subir_e_converter_para_google_docs(doc_reg_r, identificador, modo="AVALIACAO")
                                
                                pei1_txt_r = ai.extrair_tag(txt_f, "PEI_NIVEL_1") or ai.extrair_tag(txt_f, "NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                                link_p1_r = "N/A"
                                if pei1_txt_r:
                                    status_reexp.write("🔵 Re-gerando Caderno PEI Nível 1 Word...")
                                    doc_p1_r = exporter.gerar_docx_pei_v25(f"{identificador}_PEI_N1", pei1_txt_r, info_reexp)
                                    link_p1_r = db.subir_e_converter_para_google_docs(doc_p1_r, f"{identificador}_PEI_N1", modo="AVALIACAO")
                                
                                pei3_txt_r = ai.extrair_tag(txt_f, "PEI_NIVEL_3")
                                link_p3_r = "N/A"
                                if pei3_txt_r:
                                    status_reexp.write("🔴 Re-gerando Caderno PEI Nível 3 Word (Bento Cards)...")
                                    doc_p3_r = exporter.gerar_docx_pei_qualitativa(f"{identificador}_PEI_N3", pei3_txt_r, info_reexp)
                                    link_p3_r = db.subir_e_converter_para_google_docs(doc_p3_r, f"{identificador}_PEI_N3", modo="AVALIACAO")
                                
                                links_f_r = f"--- LINKS ---\nRegular({link_reg_r}) PEI_N1({link_p1_r}) PEI_N3({link_p3_r})"
                                txt_sem_links = txt_f.split("--- LINKS ---")[0].strip()
                                novo_conteudo_banco = f"{txt_sem_links}\n\n{links_f_r}"
                                
                                db.excluir_registro("DB_AULAS_PRONTAS", identificador)
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                    data_exibicao, semana_ref_exibicao, identificador, novo_conteudo_banco, ano_exibicao, link_reg_r
                                ])
                                
                                status_reexp.update(label="✅ Prova re-exportada e link atualizado!", state="complete")
                                st.balloons(); time.sleep(1.2); st.rerun()

                    with st.expander("👁️ Analisar Estrutura Psicométrica & Análise de Distratores (TRI)", expanded=False):
                        t_gab, t_ques, t_pei_v = st.tabs(["Perícia Regular", "Caderno Regular", "Inclusão PEI"])
                        
                        with t_gab:
                            st.markdown("**🔬 Grade de Perícia e Análise de Distratores (TRI)**")
                            grade_raw = ai.extrair_tag(txt_f, "GRADE_DE_CORRECAO")
                            if grade_raw:
                                questoes_grade = re.split(r"(?i)QUEST[AÃ]O\s*0?(\d+)", grade_raw)
                                if len(questoes_grade) > 1:
                                    for idx_g in range(1, len(questoes_grade), 2):
                                        q_num, q_txt = questoes_grade[idx_g], questoes_grade[idx_g+1]
                                        q_txt_limpo = re.sub(r'[*#]', '', q_txt).strip()
                                        
                                        m_hab = re.search(r"(?i)(?:DESCRITOR_SAEB|HABILIDADE|BNCC|DESCRITOR).*?[:\-]\s*(.*?)(?=JUSTIFICATIVA|DISTRATORES|$)", q_txt_limpo, re.DOTALL)
                                        m_just = re.search(r"(?i)(?:JUSTIFICATIVA).*?[:\-]\s*(.*?)(?=DISTRATORES|$)", q_txt_limpo, re.DOTALL)
                                        m_peri = re.search(r"(?i)(?:DISTRATORES_CIENTIFICOS|DISTRATORES).*?[:\-]\s*(.*)", q_txt_limpo, re.DOTALL)
                                        
                                        with st.container(border=True):
                                            st.markdown(f"**Item {q_num}**")
                                            if m_hab: st.caption(f"🆔 **Descritor SAEB/BNCC:** {m_hab.group(1).strip()}")
                                            if m_just: st.write(f"🎯 **Gabarito Justificado:** {m_just.group(1).strip()}")
                                            if m_peri: st.warning(f"🧠 **Distratores Científicos:** {m_peri.group(1).strip()}")
                                else: st.text(grade_raw)
                            else: st.warning("Perícia indisponível.")

                        with t_ques:
                            st.markdown("**📋 Enunciados do Caderno de Prova**")
                            questoes_reg = ai.extrair_tag(txt_f, "QUESTOES")
                            if questoes_reg:
                                st.write(preparar_para_leitura(questoes_reg))

                        with t_pei_v:
                            st.markdown("**♿ Estrutura PEI Adaptada**")
                            pei_txt = ai.extrair_tag(txt_f, "PEI_NIVEL_1") or ai.extrair_tag(txt_f, "NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                            if pei_txt:
                                st.write(preparar_para_leitura(pei_txt))

    # ==============================================================================
    # ABA 3: RECOMPOSIÇÃO & CADERNOS DE REVISÃO DO ACERVO
    # ==============================================================================
    with tab_recomposicao:
        st.markdown("### 🔄 Módulo Dedicado de Recomposição & Cadernos de Revisão")
        st.caption("Selecione qualquer avaliação da sua biblioteca para forjar o Caderno de Recomposição Padronizado (Regular + PEI N1, N2 e N3).")

        df_provas_para_revisao = df_aulas[df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy() if not df_aulas.empty else pd.DataFrame()

        if df_provas_para_revisao.empty:
            st.info("Nenhuma avaliação cadastrada no acervo para gerar caderno de recomposição.")
        else:
            with st.container(border=True):
                c_rev1, c_rev2 = st.columns([2, 1])
                opcoes_provas_origem = sorted(df_provas_para_revisao['TIPO_MATERIAL'].unique().tolist())
                prova_sel_recomposicao = c_rev1.selectbox("📋 Selecione a Avaliação de Origem no Acervo:", opcoes_provas_origem, key=f"sel_p_recomp_{v}")
                ano_rev_sel = c_rev2.selectbox("Série/Ano do Material:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"], key=f"sel_ano_recomp_{v}")

            if prova_sel_recomposicao:
                row_prova_orig_m = df_provas_para_revisao[df_provas_para_revisao['TIPO_MATERIAL'] == prova_sel_recomposicao]
                txt_prova_orig = str(row_prova_orig_m.iloc[0].get('CONTEUDO', '')) if not row_prova_orig_m.empty else ""

                with st.container(border=True):
                    st.markdown("#### ⚙️ Parâmetros do Caderno de Recomposição Padronizado")
                    c_aut_r1, c_aut_r2 = st.columns([1, 1])
                    
                    qtd_q_recomp = c_aut_r1.pills(
                        "Nº de Questões Espelho Desejado:",
                        ["3 Questões (Rápida)", "5 Questões (Padrão)", "10 Questões (Completa)"],
                        default="10 Questões (Completa)",
                        key=f"pills_qtd_recomp_{v}"
                    )
                    
                    estrat_recomp = c_aut_r2.pills(
                        "Estratégia Pedagógica:",
                        ["Exercícios Espelho Diretos (SAEB)", "Clínica de Erros Comentada", "Guia de Estudo Dirigido"],
                        default="Exercícios Espelho Diretos (SAEB)",
                        key=f"pills_estrat_recomp_{v}"
                    )

                st.markdown("---")
                
                if st.button("🚀 FORJAR CADERNO DE RECOMPOSIÇÃO COMPLETO (REGULAR + PEI)", type="primary", use_container_width=True, key=f"btn_exe_recomp_{v}"):
                    with st.status("Analisando descritores e forjando material de recomposição completo...", expanded=True) as status_rec:
                        num_q_num = int(re.search(r'\d+', qtd_q_recomp).group(0)) if re.search(r'\d+', qtd_q_recomp) else 10
                        
                        nome_limpo_origem = prova_sel_recomposicao.replace("REVISAO_", "").replace("AVALIAÇÃO_", "").replace("PROVA_", "")
                        nome_recomposicao_arq = f"REVISAO_{nome_limpo_origem}_{num_q_num}Q"
                        info_recomp = {"ano": ano_rev_sel, "trimestre": "II Trimestre" if "IITrimestre" in prova_sel_recomposicao else "I Trimestre", "semana": "RECOMPOSIÇÃO", "valor": "4.0"}

                        status_rec.write("🧠 1/4 Forjando Caderno Regular e Guia do Professor...")
                        prompt_recomposicao = (
                            f"PROVA BASE DE ORIGEM:\n{txt_prova_orig}\n\n"
                            f"SÉRIE: {ano_rev_sel}.\n"
                            f"QUANTIDADE EXIGIDA DE QUESTÕES ESPELHO: {num_q_num} questões.\n"
                            f"ESTRATÉGIA SELECIONADA: {estrat_recomp}.\n\n"
                            f"MISSÃO: Crie o Caderno de Recomposição com Roteiro do Professor ([PROFESSOR]), Exercícios Espelho para os Alunos ([ALUNO]), Gabarito ([GABARITO_TEXTO]), Perícia TRI ([GRADE_DE_CORRECAO]), PEI N1 ([PEI_NIVEL_1]), PEI N2 ([PEI_NIVEL_2]) e PEI N3 em 10 Bento Boxes ([PEI_NIVEL_3])."
                        )
                        res_recomposicao = ai.gerar_ia("ARQUITETO_REVISAO_V29", prompt_recomposicao)
                        
                        txt_prof = ai.extrair_tag(res_recomposicao, "PROFESSOR") or ai.extrair_tag(res_recomposicao, "ROTEIRO_DO_PROFESSOR") or "Guia do Professor."
                        txt_alu = ai.extrair_tag(res_recomposicao, "ALUNO") or ai.extrair_tag(res_recomposicao, "QUESTOES") or "Exercícios da Recomposição."
                        txt_gab = ai.extrair_tag(res_recomposicao, "GABARITO_TEXTO") or ai.extrair_tag(res_recomposicao, "GABARITO") or "Gabarito."
                        txt_grade = ai.extrair_tag(res_recomposicao, "GRADE_DE_CORRECAO") or "Grade."
                        txt_pei1 = ai.extrair_tag(res_recomposicao, "PEI_NIVEL_1") or "PEI N1."
                        txt_pei2 = ai.extrair_tag(res_recomposicao, "PEI_NIVEL_2") or "PEI N2."
                        txt_pei3 = ai.extrair_tag(res_recomposicao, "PEI_NIVEL_3") or "PEI N3."

                        status_rec.write("📄 2/4 Gerando Caderno Regular Word (OMR Fiducial)...")
                        txt_prova_completo_reg = f"[VALOR: 4.0]\n\n[QUESTOES]\n{txt_alu}\n\n[GABARITO_TEXTO]\n{txt_gab}\n\n[GRADE_DE_CORRECAO]\n{txt_grade}"
                        doc_alu_rev = exporter.gerar_docx_prova_v25(nome_recomposicao_arq, txt_prova_completo_reg, info_recomp)
                        link_alu_rev = db.subir_e_converter_para_google_docs(doc_alu_rev, nome_recomposicao_arq, modo="AVALIACAO")

                        status_rec.write("🔵 3/4 Gerando Cadernos PEI Adaptados (N1, N2 e N3)...")
                        doc_p1 = exporter.gerar_docx_pei_v25(f"{nome_recomposicao_arq}_PEI_N1", txt_pei1, info_recomp)
                        link_p1 = db.subir_e_converter_para_google_docs(doc_p1, f"{nome_recomposicao_arq}_PEI_N1", modo="AVALIACAO")

                        doc_p3 = exporter.gerar_docx_pei_qualitativa(f"{nome_recomposicao_arq}_PEI_N3", txt_pei3, info_recomp)
                        link_p3 = db.subir_e_converter_para_google_docs(doc_p3, f"{nome_recomposicao_arq}_PEI_N3", modo="AVALIACAO")

                        status_rec.write("👨‍🏫 4/4 Gerando Guia do Professor Word...")
                        doc_prof_rev = exporter.gerar_docx_professor_v25(nome_recomposicao_arq, txt_prof, info_recomp)
                        link_prof_rev = db.subir_e_converter_para_google_docs(doc_prof_rev, f"{nome_recomposicao_arq}_PROF", modo="AVALIACAO")

                        links_f = f"--- LINKS ---\nRegular({link_alu_rev}) PEI_N1({link_p1}) PEI_N3({link_p3}) Prof({link_prof_rev})"
                        conteudo_final_recomp = f"{txt_prova_completo_reg}\n\n[PROFESSOR]\n{txt_prof}\n\n[PEI_NIVEL_1]\n{txt_pei1}\n\n[PEI_NIVEL_2]\n{txt_pei2}\n\n[PEI_NIVEL_3]\n{txt_pei3}\n\n{links_f}"

                        db.excluir_registro("DB_AULAS_PRONTAS", nome_recomposicao_arq)
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_recomposicao_arq,
                            conteudo_final_recomp, ano_rev_sel, link_alu_rev
                        ])

                        st.session_state[f"recomp_gerada_{v}"] = {
                            'texto': conteudo_final_recomp, 'link_alu': link_alu_rev, 
                            'nome': nome_recomposicao_arq, 'ano': ano_rev_sel,
                            'trimestre': info_recomp['trimestre']
                        }
                        status_rec.update(label="✅ Caderno de Recomposição gerado e sincronizado no Drive!", state="complete")
                        st.balloons(); st.rerun()

                if f"recomp_gerada_{v}" in st.session_state:
                    rec_data = st.session_state[f"recomp_gerada_{v}"]
                    st.success(f"🏆 Caderno **{rec_data['nome']}** homologado com sucesso no acervo!")
                    
                    c_link1, c_link2 = st.columns(2)
                    c_link1.link_button("📂 ABRIR CADERNO DO ALUNO NO DRIVE", rec_data['link_alu'], type="primary", use_container_width=True)
                    
                    with c_link2.popover("🚀 INJETAR REVISÃO NO PONTO ID (PLANO DA SEMANA)"):
                        st.caption("Envie este Caderno de Recomposição como Plano para a Semana Selecionada no Ponto ID. Ele será gravado como PRODUZIDO, isentando a semana no Criador de Aulas.")
                        
                        todas_semanas_inj = util.gerar_semanas()
                        sem_destino_inj = st.selectbox("Selecione a Semana de Destino do Plano:", [s.split(" (")[0] for s in todas_semanas_inj if "Jornada" not in s], key=f"sel_sem_inj_{v}")
                        trim_destino_inj = st.selectbox("Trimestre Alvo:", ["I Trimestre", "II Trimestre", "III Trimestre"], index=["I Trimestre", "II Trimestre", "III Trimestre"].index(rec_data['trimestre']) if rec_data['trimestre'] in ["I Trimestre", "II Trimestre", "III Trimestre"] else 0, key=f"sel_trim_inj_{v}")
                        
                        if st.button("🚀 ENVIAR PLANO PARA O PONTO ID E CONCLUIR", type="primary", use_container_width=True, key=f"btn_conf_inj_{v}"):
                            txt_prof_rec = ai.extrair_tag(rec_data['texto'], "PROFESSOR") or "Orientação pedagógica de recomposição."
                            txt_alu_rec = ai.extrair_tag(rec_data['texto'], "ALUNO") or ai.extrair_tag(rec_data['texto'], "QUESTOES") or "Exercícios da recomposição."
                            
                            roteiro_a1 = f"AULA 01 - DEVOLUTIVA PEDAGÓGICA E RECOMPOSIÇÃO:\nINÍCIO: Análise dos descritores críticos da avaliação e devolutiva dos resultados aos estudantes.\nMEIO: Resolução comentada no quadro dos exercícios do Caderno de Recomposição ({rec_data['nome']}).\nFIM: Síntese e tiragem de dúvidas."
                            roteiro_a2 = f"AULA 02 - FIXAÇÃO DOS DESCRITORES CRÍTICOS:\nINÍCIO: Orientação para resolução autônoma do Caderno de Recomposição.\nMEIO: Acompanhamento individual e mediação para os estudantes do Grupo 1 (PEI N1, N2 e N3).\nFIM: Encerramento com verificação dos vistos nos cadernos."

                            plano_texto_rascunho = (
                                f"[HABILIDADE_BNCC] Habilidades e Descritores SAEB do Caderno {rec_data['nome']}\n"
                                f"[COMPETENCIAS_FOCO] Competência Específica 2 (Raciocínio Lógico) e 6 (Enfrentar Situações-Problema)\n"
                                f"[OBJETO_CONHECIMENTO] RECOMPOSIÇÃO DE APRENDIZAGEM - {rec_data['nome']}\n"
                                f"[CONTEUDOS_ESPECIFICOS] Consolidação dos conteúdos e descritores com menor índice de acerto na avaliação.\n"
                                f"[OBJETIVOS_ENSINO] Superar as lacunas cognitivas identificadas e consolidar as habilidades do {rec_data['ano']}.\n"
                                f"[JUSTIFICATIVA_PEDAGOGICA] Recomposição contínua de aprendizagem orientada por dados.\n"
                                f"[AULA_1] {roteiro_a1}\n"
                                f"[AULA_2] {roteiro_a2}\n"
                                f"[SABADO_LETIVO] N/A\n"
                                f"[AVALIACAO_DE_MERITO] Observação direta do engajamento e visto na resolução do Caderno de Recomposição.\n"
                                f"[ESTRATEGIA_DUA_PEI] Provas e cadernos adaptados (PEI N1, N2 e N3) com suporte visual e mediação individualizada."
                            )

                            st.session_state.p_temp = plano_texto_rascunho
                            st.session_state.p_meta = {
                                "semana": sem_destino_inj, 
                                "trimestre": trim_destino_inj, 
                                "ano": f"{rec_data['ano']}º" if "º" not in str(rec_data['ano']) else str(rec_data['ano']), 
                                "base": f"Caderno de Recomposição: {rec_data['nome']}",
                                "status_final": "PRODUZIDO"
                            }
                            
                            st.toast("✅ Caderno injetado no Ponto ID e marcado como PRODUZIDO!", icon="🚀")
                            time.sleep(0.8)
                            navegar_para("📅 Planejamento (Ponto ID)")

    # ==============================================================================
    # ABA 4: EXPEDIÇÃO DE E-MAIL, PDFS & ACERVO TRIMESTRAL
    # ==============================================================================
    with tab_expedicao:
        @st.fragment
        def renderizar_expedicao_fragmento():
            st.markdown("### 📧 Expedição de E-mail, PDFs & Acervo Trimestral")
            st.caption("Gerador automático do e-mail oficial de remessa para a escola/xerox com discriminação por turma, alunos PEI nomeados e congelamento de PDFs por trimestre.")

            c_exp1, c_exp2 = st.columns([1, 2])
            trim_exp_sel = c_exp1.selectbox("📅 Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"exp_trim_sel_{v}")

            turmas_disp_exp = sorted(df_alunos['TURMA'].unique().tolist()) if not df_alunos.empty else []
            turmas_sel_exp = c_exp2.multiselect("👥 Selecione as Turmas para Envio:", options=turmas_disp_exp, default=turmas_disp_exp[:min(3, len(turmas_disp_exp))], key=f"exp_turmas_sel_{v}")

            if not turmas_sel_exp:
                st.info("Selecione ao menos uma turma para compor a remessa de e-mail e xerox.")
            else:
                df_provas_exp = df_aulas[df_aulas['SEMANA_REF'] == "AVALIAÇÃO"] if not df_aulas.empty else pd.DataFrame()
                opcoes_provas_exp = sorted(df_provas_exp['TIPO_MATERIAL'].unique().tolist()) if not df_provas_exp.empty else []
                nome_exame_email = st.selectbox("📋 Nome da Avaliação a Enviar:", options=["AVALIAÇÃO TRIMESTRAL DE MATEMÁTICA"] + opcoes_provas_exp, key=f"exp_exame_nome_{v}")

                tot_reg_geral = 0
                tot_p1_geral = 0
                tot_p2_geral = 0
                tot_p3_geral = 0

                linhas_email_turmas = []

                for t_item in turmas_sel_exp:
                    df_t_alu = df_alunos[df_alunos['TURMA'] == t_item].sort_values(by="NOME_ALUNO") if not df_alunos.empty else pd.DataFrame()
                    
                    reg_count = 0
                    p1_names = []
                    p2_names = []
                    p3_names = []

                    for _, al_r in df_t_alu.iterrows():
                        nec_raw = str(al_r.get('NECESSIDADES', '')).upper().strip()
                        nome_a = al_r.get('NOME_ALUNO', 'Estudante')
                        
                        if any(x in nec_raw for x in ["PEI N1", "PEI 1", "NÍVEL 1", "NIVEL 1", "(PEI N1)"]):
                            p1_names.append(nome_a)
                        elif any(x in nec_raw for x in ["PEI N2", "PEI 2", "NÍVEL 2", "NIVEL 2", "(PEI N2)"]):
                            p2_names.append(nome_a)
                        elif any(x in nec_raw for x in ["PEI N3", "PEI 3", "NÍVEL 3", "NIVEL 3", "(PEI N3)"]):
                            p3_names.append(nome_a)
                        else:
                            reg_count += 1

                    tot_reg_geral += reg_count
                    tot_p1_geral += len(p1_names)
                    tot_p2_geral += len(p2_names)
                    tot_p3_geral += len(p3_names)

                    bloco_t = f"📍 TURMA {t_item.upper()}:\n"
                    bloco_t += f"• Provas Regulares: {reg_count:02d} cópias\n"
                    if p1_names:
                        bloco_t += f"• Prova PEI Nível 1: {len(p1_names):02d} cópia(s) (Aluno(s): {', '.join(p1_names)})\n"
                    if p2_names:
                        bloco_t += f"• Prova PEI Nível 2: {len(p2_names):02d} cópia(s) (Aluno(s): {', '.join(p2_names)})\n"
                    if p3_names:
                        bloco_t += f"• Prova PEI Nível 3 (Qualitativa): {len(p3_names):02d} cópia(s) (Aluno(s): {', '.join(p3_names)})\n"

                    linhas_email_turmas.append(bloco_t)

                tot_geral_copias = tot_reg_geral + tot_p1_geral + tot_p2_geral + tot_p3_geral

                corpo_email_oficial = f"""Prezados(as) da Direção, Coordenação e Setor de Impressão (Xerox),

Espero que estejam bem.

Segue em anexo o arquivo em PDF das avaliações do {trim_exp_sel} ({nome_exame_email}) para impressão.

Solicito a gentileza de providenciar as impressões conforme o detalhamento por turma abaixo:

""" + "\n".join(linhas_email_turmas) + f"""
==================================================
📊 RESUMO CONSOLIDADO DE IMPRESSÃO (TOTAL GERAL):
• Total de Provas Regulares: {tot_reg_geral:02d}
• Total de Provas PEI Nível 1: {tot_p1_geral:02d}
• Total de Provas PEI Nível 2: {tot_p2_geral:02d}
• Total de Provas PEI Nível 3: {tot_p3_geral:02d}
• TOTAL GERAL DE CÓPIAS A IMPRIMIR: {tot_geral_copias:02d} cópias

Atenciosamente,
Prof. Ronaldo Gomes — Componente Curricular de Matemática
Escola Municipal Flávio José Simões Costa
"""

                st.markdown("#### 📧 E-mail Oficial de Remessa (Pronto para Copiar & Enviar)")
                st.code(corpo_email_oficial, language=None)

                with st.container(border=True):
                    st.markdown("##### 📊 Resumo de Carga de Impressão")
                    c_k1, c_k2, c_k3, c_k4, c_k5 = st.columns(5)
                    c_k1.metric("📄 Regulares", tot_reg_geral)
                    c_k2.metric("🔵 PEI N1", tot_p1_geral)
                    c_k3.metric("🟡 PEI N2", tot_p2_geral)
                    c_k4.metric("🔴 PEI N3", tot_p3_geral)
                    c_k5.metric("🖨️ TOTAL CÓPIAS", tot_geral_copias)

                st.markdown("---")
                st.markdown(f"#### 🔒 Acervo Trimestral de Segurança ({trim_exp_sel})")
                st.caption("Arquivos em DOCX e PDF armazenados no Drive para acesso permanente sem risco de perda.")

                if not df_aulas.empty and 'SEMANA_REF' in df_aulas.columns and 'CONTEUDO' in df_aulas.columns:
                    padrao_regex_trim_exp = util.obter_regex_trimestre(trim_exp_sel)
                    df_provas_trim_acervo = df_aulas[(df_aulas['SEMANA_REF'] == "AVALIAÇÃO") & (df_aulas['CONTEUDO'].str.contains(padrao_regex_trim_exp, regex=True, case=False, na=False))]
                else:
                    df_provas_trim_acervo = pd.DataFrame()

                if df_provas_trim_acervo.empty:
                    st.info(f"Nenhum exame cadastrado no acervo do {trim_exp_sel} ainda.")
                else:
                    for idx_exp, (_, row_ac) in enumerate(df_provas_trim_acervo.iterrows()):
                        with st.container(border=True):
                            c_a1, c_a2, c_a3 = st.columns([2, 1, 1])
                            mat_nome = str(row_ac.get('TIPO_MATERIAL', 'AVALIAÇÃO'))
                            ano_nome = str(row_ac.get('ANO', '6º'))
                            data_nome = str(row_ac.get('DATA', 'N/A'))
                            
                            c_a1.markdown(f"**📋 {mat_nome}**")
                            c_a1.caption(f"Série: {ano_nome} | Data: {data_nome}")
                            
                            l_docx = row_ac.get('LINK_DRIVE', '#')
                            if l_docx and "http" in str(l_docx):
                                c_a2.link_button("📝 Abrir DOCX Editável", str(l_docx), use_container_width=True)
                            else:
                                c_a2.caption("DOCX Indisponível")

                            if c_a3.button("📄 Congelar PDF no Drive", key=f"btn_pdf_freeze_{row_ac.name}_{idx_exp}_{v}", use_container_width=True):
                                with st.spinner("Gerando PDF congelado e salvando no Drive..."):
                                    txt_ac = str(row_ac.get('CONTEUDO', ''))
                                    doc_stream_p = exporter.gerar_docx_prova_v25(mat_nome, txt_ac, {"ano": ano_nome, "trimestre": trim_exp_sel})
                                    link_pdf = db.subir_e_converter_para_google_docs(doc_stream_p, f"{mat_nome}_CONGELADO", trimestre=trim_exp_sel, categoria=ano_nome, modo="SCANNER")
                                    st.success("✅ PDF Congelado no Drive!")
                                    st.link_button("📂 ABRIR PDF NO DRIVE", link_pdf, type="primary", use_container_width=True)

        renderizar_expedicao_fragmento()









# ==============================================================================
# MÓDULO: CENTRAL DE INTELIGÊNCIA DE RESULTADOS (CIR / SCANNER DE GABARITOS)
# (V2026.ULTIMATE - UNIFICAÇÃO DE ACERVO REAL & CHAVES ÚNICAS)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("Central de Inteligência de Resultados (CIR)")
    st.caption("Mesa de triagem de exames, leitor fiducial, regra do cálculo 50% (*), espelho split-screen, perícia de distratores TRI e ponte de recomposição.")
    st.markdown("---")

    if "v_scan" not in st.session_state: 
        st.session_state.v_scan = int(time.time())
    v = st.session_state.v_scan

    lista_turmas_cir = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais_cir = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_cir = sorted(turmas_reais_cir['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_cir = sorted(df_alunos['TURMA'].unique())

    def obter_regex_trimestre(trimestre_str):
        if not trimestre_str or trimestre_str == "Todos": return r".*"
        t_upper = str(trimestre_str).upper()
        if "III" in t_upper or "TERCEIRO" in t_upper: return r"(?<!I)III(?![I])"
        elif "II" in t_upper or "SEGUNDO" in t_upper: return r"(?<!I)II(?![I])"
        else: return r"(?<!I)I(?![I])"

    # MOTOR UNIFICADO DE BUSCA DE AVALIAÇÕES (AULAS + GABARITOS REAIS DO BANCO)
    def obter_avaliacoes_unificadas_cir(turma, trimestre_nome):
        if not turma or not trimestre_nome: return []
        padrao_regex_trim = obter_regex_trimestre(trimestre_nome)
        serie_num = "".join(filter(str.isdigit, str(turma)))
        
        opcoes_encontradas = set()

        if not df_diagnosticos.empty and 'TURMA' in df_diagnosticos.columns and 'ID_AVALIACAO' in df_diagnosticos.columns:
            mask_diag = (df_diagnosticos['TURMA'] == turma) & (
                df_diagnosticos['ID_AVALIACAO'].astype(str).str.contains(padrao_regex_trim, regex=True, case=False, na=False) |
                (trimestre_nome == "Todos")
            )
            for av_id in df_diagnosticos[mask_diag]['ID_AVALIACAO'].dropna().unique():
                av_clean = re.sub(r'\s*\(\s*VARIANTE.*?\)', '', str(av_id), flags=re.IGNORECASE).strip()
                if av_clean and not re.search(r"2[ªA]|CHAMADA", av_clean, re.IGNORECASE):
                    opcoes_encontradas.add(av_clean)

        if not df_aulas.empty and 'ANO' in df_aulas.columns and 'TIPO_MATERIAL' in df_aulas.columns:
            df_f = df_aulas[df_aulas['ANO'].astype(str).str.contains(serie_num)].copy()
            permitidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]
            proibidos = ["REVISAO", "REVISÃO", "APLICAÇÃO", "CORREÇÃO", "DOSSIÊ", "AULA"]
            
            mask_p = df_f['TIPO_MATERIAL'].astype(str).str.upper().str.contains('|'.join(permitidos)) & \
                     (~df_f['TIPO_MATERIAL'].astype(str).str.upper().str.contains('|'.join(proibidos)))
            
            df_f = df_f[mask_p]
            mask_t = df_f['CONTEUDO'].astype(str).str.contains(padrao_regex_trim, regex=True, na=False, case=False) | \
                     df_f['TIPO_MATERIAL'].astype(str).str.contains(padrao_regex_trim, regex=True, na=False, case=False)
            
            for av_mat in df_f[mask_t]['TIPO_MATERIAL'].dropna().unique():
                av_clean = re.sub(r'\s*\(\s*VARIANTE.*?\)', '', str(av_mat), flags=re.IGNORECASE).strip()
                if av_clean and not re.search(r"2[ªA]|CHAMADA", av_clean, re.IGNORECASE):
                    opcoes_encontradas.add(av_clean)

        return sorted(list(opcoes_encontradas))

    # DIALOGS DECLARADOS FORA DE FRAGMENTS (LEI #25)
    @st.dialog("⚖️ Homologação de Atestados & Justificativas", width="large")
    def dialog_atestados_modal(alunos_turma_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog):
        st.info("💡 Se o aluno entregou atestado depois ou se houve erro ao dar falta, ajuste o status abaixo.")
        aluno_homolog_nome = st.selectbox("Selecione o Estudante:", alunos_turma_dialog['NOME_ALUNO'].tolist() if not alunos_turma_dialog.empty else [], key=f"homolog_modal_sel_{v}")
        
        if aluno_homolog_nome:
            match_h = alunos_turma_dialog[alunos_turma_dialog['NOME_ALUNO'] == aluno_homolog_nome]
            id_homolog = db.limpar_id(match_h.iloc[0]['ID']) if not match_h.empty else ""
            
            c_hom1, c_hom2 = st.columns([1.5, 1])
            novo_status_ausencia = c_hom1.radio(
                "Definir Novo Status:",
                [
                    "📑 Falta Justificada (Atestado / Licença - Liberado para 2ª Chamada)",
                    "❌ Falta Injustificada (Zero Definitivo - Prazo Expirado)",
                    "🔄 Restaurar para Fila do Scanner (Remover Registros)"
                ],
                key=f"rad_modal_{id_homolog}_{v}"
            )
            motivo_detalhado = c_hom2.text_input("Motivo / Observação:", placeholder="Ex: Atestado entregue em 15/04", key=f"txt_mot_modal_{id_homolog}_{v}")

            if st.button("💾 CONFIRMAR HOMOLOGAÇÃO", type="primary", use_container_width=True, key=f"btn_conf_homolog_{v}"):
                with st.spinner("Atualizando registros..."):
                    db.excluir_registro("DB_GABARITOS_ALUNOS", id_homolog)
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    
                    if "Justificada" in novo_status_ausencia:
                        motivo_save = motivo_detalhado if motivo_detalhado.strip() else "Atestado Médico / Licença"
                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [data_hoje, id_homolog, aluno_homolog_nome, t_sel_dialog, av_alvo_dialog, f"FALTOU_JUSTIFICADO|{motivo_save}", "0,00", "N/A"])
                        db.salvar_no_banco("DB_RELATORIOS", [data_hoje, id_homolog, aluno_homolog_nome, "JUSTIFICATIVA_AUSENCIA", f"Avaliação: {av_alvo_dialog} | Status: JUSTIFICADO | Motivo: {motivo_save}"])
                    elif "Injustificada" in novo_status_ausencia:
                        motivo_save = motivo_detalhado if motivo_detalhado.strip() else "Prazo Regimental Expirado"
                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [data_hoje, id_homolog, aluno_homolog_nome, t_sel_dialog, av_alvo_dialog, f"FALTOU_INJUSTIFICADO|{motivo_save}", "0,00", "N/A"])
                        db.salvar_no_banco("DB_RELATORIOS", [data_hoje, id_homolog, aluno_homolog_nome, "JUSTIFICATIVA_AUSENCIA", f"Avaliação: {av_alvo_dialog} | Status: INJUSTIFICADO | Motivo: {motivo_save}"])

                    db.limpar_notas_turma_trimestre(t_sel_dialog, tr_sel_dialog)
                    st.cache_data.clear()
                    st.success("✅ Status homologado e boletim recalculado!"); time.sleep(0.5); st.rerun()

    @st.dialog("👤 Perícia & Lançamento de 2ª Chamada por Estudante", width="large")
    def dialog_pericia_modal(dados_soberania_dialog, alunos_turma_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog, gab_oficial_dialog, v_total_dialog, nome_curto_av_dialog):
        st.caption("Acesse a folha de respostas ou lance a nota de 2ª Chamada para qualquer estudante da turma.")
        
        todos_estudantes_nomes = [r.get('Estudante', '') for r in dados_soberania_dialog]
        
        if not todos_estudantes_nomes: 
            st.info("Nenum aluno cadastrado nesta turma.")
        else:
            aluno_pericia_nome = st.selectbox("Selecione o Estudante:", todos_estudantes_nomes, key=f"pericia_modal_sel_{v}")
            if aluno_pericia_nome:
                al_data = next((r for r in dados_soberania_dialog if r.get('Estudante') == aluno_pericia_nome), {})
                id_al_pericia = al_data.get('ID', '')
                resp_raw = str(al_data.get('_Respostas', ''))
                grupo_membros = str(al_data.get('Dupla / Grupo', 'Individual'))
                foto_atual_link = str(al_data.get('Evidência', ''))
                sit_atual = str(al_data.get('Situação', ''))
                
                if "JUSTIFICADO" in sit_atual or "FALTOU" in sit_atual or sit_atual == "✍️ PENDENTE":
                    st.warning(f"📌 Status Atual do Aluno: **{sit_atual}**. Ao salvar abaixo, a ausência será convertida em **Nota Real de 2ª Chamada**.")
                
                c_f1, c_f2 = st.columns([1, 2])
                if "http" in foto_atual_link: c_f1.link_button("🔗 Ver Foto no Drive", foto_atual_link, use_container_width=True)
                else: c_f1.caption("Sem foto anexada.")
                
                nova_foto_pericia = c_f2.file_uploader("Substituir / Anexar Foto JPG:", type=["jpg", "jpeg", "png"], key=f"up_modal_foto_{id_al_pericia}_{v}")

                resp_limpa = resp_raw.split('|GRUPO:')[0] if '|GRUPO:' in resp_raw else resp_raw
                respostas_lista = resp_limpa.split(';') if (not resp_limpa.startswith("FALTOU") and not resp_limpa.startswith("QUALITATIVA") and resp_limpa != "MANUAL") else []
                
                grid_pericia = []
                for idx_q in range(len(gab_oficial_dialog)):
                    item_str = respostas_lista[idx_q].strip().upper() if idx_q < len(respostas_lista) else "?"
                    letra_aluno = item_str.replace("*", "")
                    if letra_aluno not in ["A", "B", "C", "D", "E", "X", "?"]: letra_aluno = "?"
                    tem_calculo = "*" not in item_str
                    correta_q = gab_oficial_dialog.get(idx_q + 1, "?")
                    grid_pericia.append({"Questão": f"Q{idx_q+1:02d}", "Gabarito Oficial": correta_q, "Letra do Aluno": letra_aluno, "🧮 Tem Cálculo?": tem_calculo})
                
                df_pericia_ed = st.data_editor(
                    pd.DataFrame(grid_pericia), hide_index=True, use_container_width=True,
                    column_config={"Questão": st.column_config.TextColumn(disabled=True), "Gabarito Oficial": st.column_config.TextColumn(disabled=True), "Letra do Aluno": st.column_config.SelectboxColumn("Letra Marcada", options=["A", "B", "C", "D", "E", "X", "?"], required=True), "🧮 Tem Cálculo?": st.column_config.CheckboxColumn("Cálculo OK?")},
                    key=f"grid_modal_ind_{id_al_pericia}_{v}"
                )
                
                novas_res_pericia = []
                nota_pericia_calc = 0.0
                peso_q_pericia = v_total_dialog / len(gab_oficial_dialog) if len(gab_oficial_dialog) > 0 else 0
                for i_p, r_p in df_pericia_ed.iterrows():
                    l_p = r_p["Letra do Aluno"]
                    c_p = r_p["🧮 Tem Cálculo?"]
                    g_p = gab_oficial_dialog.get(i_p + 1, "?")
                    if l_p == g_p or g_p == "🚫 ANULADA": nota_pericia_calc += peso_q_pericia if c_p else (peso_q_pericia / 2)
                    flag_letra_p = f"{l_p}*" if (not c_p and l_p in ["A","B","C","D","E"]) else l_p
                    novas_res_pericia.append(flag_letra_p)
                    
                st.metric("Nota Recalculada", f"{min(v_total_dialog, nota_pericia_calc):.1f} / {v_total_dialog:.1f}")
                
                if st.button("💾 SALVAR PROVA / 2ª CHAMADA DO ESTUDANTE", type="primary", use_container_width=True, key=f"btn_save_pericia_ind_{v}"):
                    with st.spinner("Apagando registros de falta antigos e salvando nota real..."):
                        link_foto_final = foto_atual_link
                        if nova_foto_pericia is not None:
                            link_foto_final = db.subir_e_converter_para_google_docs(nova_foto_pericia.getvalue(), aluno_pericia_nome.replace(" ","_"), trimestre=tr_sel_dialog, categoria=t_sel_dialog, semana=av_alvo_dialog, modo="SCANNER")

                        alvos_a = [aluno_pericia_nome] if grupo_membros == "Individual" else [n.strip() for n in grupo_membros.split(',')]
                        grupo_tag = f"|GRUPO:{grupo_membros}" if grupo_membros != "Individual" else ""
                        respostas_salvar_ind = f"{';'.join(novas_res_pericia)}{grupo_tag}"

                        wb_p = db.conectar()
                        ws_p = wb_p.worksheet("DB_GABARITOS_ALUNOS")
                        dados_p = ws_p.get_all_values()
                        
                        for idx_row_p in range(len(dados_p) - 1, 0, -1):
                            row_p = dados_p[idx_row_p]
                            if len(row_p) > 4 and row_p[3] == t_sel_dialog and nome_curto_av_dialog in row_p[4]:
                                if row_p[2] in alvos_a:
                                    ws_p.delete_rows(idx_row_p + 1)

                        for al_nome_item in alvos_a:
                            match_al_item = alunos_turma_dialog[alunos_turma_dialog['NOME_ALUNO'] == al_nome_item] if not alunos_turma_dialog.empty else pd.DataFrame()
                            if not match_al_item.empty:
                                id_item = db.limpar_id(match_al_item.iloc[0]['ID'])
                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_item, al_nome_item, t_sel_dialog, av_alvo_dialog, respostas_salvar_ind, util.sosa_to_str(nota_pericia_calc), link_foto_final])

                        db.limpar_notas_turma_trimestre(t_sel_dialog, tr_sel_dialog)
                        st.cache_data.clear(); st.success("✅ Prova de 2ª Chamada homologada com sucesso!"); time.sleep(0.5); st.rerun()

    @st.dialog("🚑 Digitação Manual Global (Lázaro)", width="large")
    def dialog_lazaro_modal(dados_soberania_dialog, gab_oficial_dialog, v_total_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog):
        df_perdidos = pd.DataFrame([r for r in dados_soberania_dialog if str(r.get('_Respostas', '')).startswith("MANUAL") and r.get('Situação') == "✅ REALIZADA"])
        if not df_perdidos.empty:
            st.info("Digite as respostas dos alunos separadas por ponto e vírgula (ex: A;B;C;D;E).")
            df_lazaro = st.data_editor(
                pd.DataFrame([{"ID": r.get('ID', ''), "Estudante": r.get('Estudante', ''), "Respostas": ""} for _, r in df_perdidos.iterrows()]),
                hide_index=True, use_container_width=True, key=f"laz_grid_modal_{v}"
            )
            if st.button("💾 Processar Lázaro", type="primary", use_container_width=True, key=f"btn_proc_laz_{v}"):
                with st.spinner("Processando..."):
                    for _, row_laz in df_lazaro.iterrows():
                        resp_dig = str(row_laz["Respostas"]).strip().upper()
                        if resp_dig:
                            respostas_lista = [r for r in re.split(r'[;\s,]', resp_dig) if r]
                            acertos = sum(1 for i, r in enumerate(respostas_lista) if i+1 in gab_oficial_dialog and r == gab_oficial_dialog[i+1])
                            nota_calc = (acertos / len(gab_oficial_dialog)) * v_total_dialog if len(gab_oficial_dialog) > 0 else 0.0
                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), row_laz["ID"], row_laz["Estudante"], t_sel_dialog, av_alvo_dialog, ";".join(respostas_lista), util.sosa_to_str(nota_calc), "N/A"])
                    st.cache_data.clear(); st.success("✅ Processado!"); time.sleep(0.5); st.rerun()
        else: st.success("🎉 Nenhum registro pendente.")

    tab_correcao, tab_auditoria, tab_raiox = st.tabs([
        "Mesa de Correção", "Tribunal de Auditoria", "Raio-X Pedagógico"
    ])

    # ==============================================================================
    # ABA 1: MESA DE CORREÇÃO
    # ==============================================================================
    with tab_correcao:
        modo_lancamento = st.pills(
            "Selecione a Atividade para Lançar:", 
            ["📸 Provas (Scanner/Manual)", "✍️ Trabalhos & Projetos (Lote)"], 
            default="📸 Provas (Scanner/Manual)",
            key=f"pills_modo_cir_{v}"
        )
        st.markdown("---")

        if "Provas" in modo_lancamento:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                t_sel = c1.selectbox("👥 Turma:", [""] + lista_turmas_cir, key=f"t_p_{v}")
                tr_sel = c2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_p_{v}")
                
                opcoes_base = obter_avaliacoes_unificadas_cir(t_sel, tr_sel)
                at_sel = c3.selectbox("📋 Avaliação Base (Slot):", [""] + opcoes_base, key=f"at_p_{v}")

            if not t_sel or not at_sel:
                st.info("Selecione a Turma e a Avaliação Base para abrir a Mesa de Correção.")
            else:
                nome_filtro_pendente = at_sel.split("-")[0].strip()
                df_diag_turma = df_diagnosticos[df_diagnosticos['TURMA'] == t_sel] if not df_diagnosticos.empty else pd.DataFrame()
                padrao_trim = obter_regex_trimestre(tr_sel)
                tipo_base = at_sel.split("-")[0].strip().upper()
                serie_num = "".join(filter(str.isdigit, t_sel))

                col_fila, col_mesa = st.columns([1.2, 1.8])

                with col_fila:
                    with st.container(border=True):
                        st.markdown("##### Fila de Triagem")
                        
                        alunos_turma_df = df_alunos[df_alunos['TURMA'] == t_sel].sort_values(by="NOME_ALUNO") if not df_alunos.empty else pd.DataFrame()
                        total_turma = len(alunos_turma_df)
                        
                        diag_slot = df_diag_turma[df_diag_turma['ID_AVALIACAO'].str.startswith(nome_filtro_pendente, na=False)] if not df_diag_turma.empty else pd.DataFrame()
                        
                        mapa_status_aluno = {}
                        if not diag_slot.empty:
                            for id_al_raw, group in diag_slot.groupby('ID_ALUNO'):
                                id_al_clean = db.limpar_id(id_al_raw)
                                ultimo_registro = str(group.iloc[-1].get('RESPOSTAS_ALUNO', ''))
                                mapa_status_aluno[id_al_clean] = ultimo_registro

                        opcoes_pendentes_puros, opcoes_atestados, opcoes_faltas, opcoes_todos = [], [], [], []
                        mapa_rotulo_nome = {}

                        for _, r_p in alunos_turma_df.iterrows():
                            id_p_str = db.limpar_id(r_p.get('ID', ''))
                            nome_real = str(r_p.get('NOME_ALUNO', 'Estudante'))
                            status_banco = mapa_status_aluno.get(id_p_str, None)
                            
                            if status_banco is None:
                                rotulo = nome_real
                                opcoes_pendentes_puros.append(rotulo)
                                opcoes_todos.append(rotulo)
                            elif status_banco.startswith("FALTOU_JUSTIFICADO"):
                                rotulo = f"📑 {nome_real} (2ª Chamada Autorizada / Atestado)"
                                opcoes_atestados.append(rotulo)
                                opcoes_todos.append(rotulo)
                            elif status_banco.startswith("FALTOU"):
                                rotulo = f"❌ {nome_real} (Ausência Registrada)"
                                opcoes_faltas.append(rotulo)
                                opcoes_todos.append(rotulo)
                            else:
                                rotulo = f"✅ {nome_real} (Prova Corrigida)"
                                opcoes_todos.append(rotulo)
                                
                            mapa_rotulo_nome[rotulo] = nome_real

                        total_processados = total_turma - len(opcoes_pendentes_puros)

                        filtro_fila = st.selectbox(
                            "📋 Filtrar Fila:",
                            ["Pendentes Nativos", "📑 Atestados (2ª Chamada)", "❌ Faltas Registradas", "🌐 Todos da Turma"],
                            key=f"flt_fila_cir_{v}"
                        )
                        
                        if filtro_fila == "Pendentes Nativos": opcoes_triagem_exibir = opcoes_pendentes_puros
                        elif filtro_fila == "📑 Atestados (2ª Chamada)": opcoes_triagem_exibir = opcoes_atestados
                        elif filtro_fila == "❌ Faltas Registradas": opcoes_triagem_exibir = opcoes_faltas
                        else: opcoes_triagem_exibir = opcoes_todos

                        progresso = total_processados / total_turma if total_turma > 0 else 0.0
                        st.progress(min(1.0, max(0.0, progresso)))
                        st.caption(f"**{total_processados} de {total_turma}** alunos processados na turma.")
                        
                        modo_dupla = st.toggle("👥 Prova Realizada em Dupla / Grupo", value=False, key=f"dupla_tog_{v}")
                        
                        alunos_alvo = []
                        if opcoes_triagem_exibir:
                            if modo_dupla:
                                rotulos_sel = st.multiselect("Selecione a Dupla (Máx 3):", options=opcoes_triagem_exibir, max_selections=3, key=f"pilha_dupla_{v}")
                                alunos_alvo = [mapa_rotulo_nome[r] for r in rotulos_sel if r in mapa_rotulo_nome]
                            else:
                                rotulo_sel_single = st.selectbox("Selecione o Estudante:", [""] + opcoes_triagem_exibir, key=f"pilha_single_{v}")
                                if rotulo_sel_single and rotulo_sel_single in mapa_rotulo_nome:
                                    alunos_alvo = [mapa_rotulo_nome[rotulo_sel_single]]

                with col_mesa:
                    if alunos_alvo:
                        @st.fragment
                        def renderizar_mesa_correcao_fragmento():
                            with st.container(border=True):
                                if len(alunos_alvo) > 1: st.markdown(f"##### 👥 Correção em Dupla: {', '.join(alunos_alvo)}")
                                else: st.markdown(f"##### 👤 Estudante: {alunos_alvo[0]}")
                                
                                tem_pei_na_dupla = False
                                perfis_dupla = []
                                for nome_a in alunos_alvo:
                                    al_info = alunos_turma_df[alunos_turma_df['NOME_ALUNO'] == nome_a].iloc[0]
                                    id_aluno_atual = db.limpar_id(al_info.get('ID', ''))
                                    nec_aluno = str(al_info.get('NECESSIDADES', 'TÍPICO')).upper().strip()
                                    perfis_dupla.append((nome_a, id_aluno_atual, nec_aluno))
                                    
                                    if "(PEI N3)" in nec_aluno: st.caption("Status: 🔴 PEI NÍVEL 3 (QUALITATIVA)")
                                    elif "(PEI N2)" in nec_aluno: st.caption("Status: 🟡 PEI NÍVEL 2 (APOIO MODERADO)")
                                    elif "(PEI N1)" in nec_aluno: st.caption("Status: 🔵 PEI NÍVEL 1 (APOIO LEVE)")
                                    elif nec_aluno not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]:
                                        tem_pei_na_dupla = True
                                        st.warning(f"⚠️ Perfil Clínico ({nome_a}): {nec_aluno}")
                                    else: st.caption("Status: 📝 PERFIL REGULAR / TÍPICO")

                            primeira_nec = perfis_dupla[0][2] if perfis_dupla else ""
                            if "(PEI N3)" in primeira_nec or "NÍVEL 3" in primeira_nec: idx_lente_default = 3
                            elif "(PEI N2)" in primeira_nec or "NÍVEL 2" in primeira_nec: idx_lente_default = 2
                            elif "(PEI N1)" in primeira_nec or "NÍVEL 1" in primeira_nec: idx_lente_default = 1
                            elif tem_pei_na_dupla: idx_lente_default = 1
                            else: idx_lente_default = 0
                                
                            opcoes_lentes = ["Regular (Padrão ou Variante)", "PEI Nível 1 (Apoio Leve)", "PEI Nível 2 (Apoio Moderado)", "PEI Nível 3 / Qualitativa (Manual)"]
                            
                            with st.container(border=True):
                                lente_corr = st.segmented_control(
                                    "Lente de Correção (Controle Manual Total):", 
                                    opcoes_lentes,
                                    default=opcoes_lentes[idx_lente_default],
                                    key=f"lente_seg_{'_'.join([str(p[1]) for p in perfis_dupla])}_{v}"
                                )

                            material_ref = None
                            lente_upper = str(lente_corr).upper()
                            is_pei_grading = "NÍVEL 1" in lente_upper or "NIVEL 1" in lente_upper or "NÍVEL 2" in lente_upper or "NIVEL 2" in lente_upper
                            nivel_alvo_pei = "NIVEL_1" if ("NÍVEL 1" in lente_upper or "NIVEL 1" in lente_upper) else "NIVEL_2"
                            is_qualitativa = "NÍVEL 3" in lente_upper or "NIVEL 3" in lente_upper or "QUALITATIVA" in lente_upper
                            modo_2a = False
                            
                            if "REGULAR" in lente_upper:
                                c_reg1, c_reg2 = st.columns(2)
                                modo_2a = c_reg1.toggle("2ª Chamada Discursiva", key=f"t2a_{v}")
                                
                                if modo_2a:
                                    df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(padrao_trim, regex=True, case=False)) & (df_aulas['ANO'].str.contains(serie_num))] if not df_aulas.empty else pd.DataFrame()
                                    at_segunda = c_reg2.selectbox("Caderno de 2ª Chamada:", [""] + df_2a['TIPO_MATERIAL'].unique().tolist() if not df_2a.empty else [""], key=f"s2a_{v}")
                                    if at_segunda:
                                        df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_segunda]
                                        if not df_busca.empty: material_ref = df_busca.iloc[0]
                                else:
                                    df_variantes = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains(tipo_base, regex=False)) & (df_aulas['TIPO_MATERIAL'].str.upper().str.contains("TIPO")) & (df_aulas['ANO'].str.contains(serie_num))] if not df_aulas.empty else pd.DataFrame()
                                    versao_variante = c_reg2.selectbox("Caderno/Variante:", ["Padrão (Tipo A)"] + (df_variantes['TIPO_MATERIAL'].unique().tolist() if not df_variantes.empty else []), key=f"var_{v}")
                                    df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == (at_sel if versao_variante == "Padrão (Tipo A)" else versao_variante)] if not df_aulas.empty else pd.DataFrame()
                                    if not df_busca.empty: material_ref = df_busca.iloc[0]
                                        
                            elif is_pei_grading or is_qualitativa:
                                df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel] if not df_aulas.empty else pd.DataFrame()
                                if not df_busca.empty: material_ref = df_busca.iloc[0]

                            if material_ref is not None:
                                txt_ref = str(material_ref.get('CONTEUDO', ''))
                                val_tag = ai.extrair_tag(txt_ref, "VALOR")
                                if not val_tag or util.sosa_to_float(val_tag) == 0:
                                    m_v = re.search(r"VALOR\s*[:\-]*\s*([\d\.,]+)", txt_ref, re.IGNORECASE)
                                    val_tag = m_v.group(1) if m_v else "3.0"
                                v_total_at = util.sosa_to_float(val_tag) if util.sosa_to_float(val_tag) > 0 else 3.0

                                gab_alvo = ai.extrair_gab_universal_com_fallback(txt_ref, is_pei_grading, nivel_alvo_pei)
                                if not gab_alvo:
                                    q_raw_check = ai.extrair_tag(txt_ref, "QUESTOES") or txt_ref
                                    qtd_q_estimada = len(re.findall(r"(?i)QUESTÃO\s*0?\d+", q_raw_check)) or 10
                                    gab_alvo = ["A"] * qtd_q_estimada

                                tag_grade_ref = "GRADE_DE_CORRECAO_PEI" if is_pei_grading else "GRADE_DE_CORRECAO"
                                grade_raw_ref = ai.extrair_tag(txt_ref, tag_grade_ref) or ai.extrair_tag(txt_ref, "GRADE_DE_CORRECAO")

                                with st.popover("⚙️ Conferir / Editar Gabarito Base da Prova", use_container_width=True):
                                    st.caption(f"Gabarito oficial ({len(gab_alvo)} questões | Valor Total: {v_total_at:.1f} pts).")
                                    grid_gab_pre = [{"Q": f"{i+1:02d}", "Letra": gab_alvo[i] if i < len(gab_alvo) else "A"} for i in range(len(gab_alvo))]
                                    df_gab_pre = st.data_editor(
                                        pd.DataFrame(grid_gab_pre), hide_index=True, use_container_width=True,
                                        column_config={"Q": st.column_config.TextColumn(disabled=True), "Letra": st.column_config.SelectboxColumn("Gabarito Oficial", options=["A", "B", "C", "D", "E"], required=True)},
                                        key=f"ed_pre_gab_{v}_{nivel_alvo_pei}"
                                    )
                                    if not df_gab_pre.empty and "Letra" in df_gab_pre.columns:
                                        gab_alvo = df_gab_pre["Letra"].tolist()

                                if is_pei_grading or "REGULAR" in lente_upper:
                                    c_m1, c_m2 = st.columns([2, 1])
                                    modo_correcao = c_m1.pills("Método de Correção:", ["📸 Scanner Câmera", "✍️ Digitação Manual (Speed Grader)"], default="📸 Scanner Câmera", key=f"mc_pills_{v}")
                                    
                                    if c_m2.button("Ausência", use_container_width=True, key=f"btn_aus_single_{v}"):
                                        for aluno_nome in alunos_alvo:
                                            match_al_aus = alunos_turma_df[alunos_turma_df['NOME_ALUNO'] == aluno_nome]
                                            if not match_al_aus.empty:
                                                id_al = db.limpar_id(match_al_aus.iloc[0].get('ID', ''))
                                                db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                        st.rerun()

                                    if "Scanner" in str(modo_correcao):
                                        img_file = st.file_uploader("Carregar foto do gabarito (.jpg/.png):", type=["jpg", "jpeg", "png"], key=f"up_{v}")
                                        img_cam = st.camera_input("Capturar via Câmera:", key=f"cam_{v}")
                                        img = img_file if img_file else img_cam

                                        if img and "current_scan_res" not in st.session_state:
                                            with st.spinner("Analisando marcações via Visão Computacional Gemini..."):
                                                res_json = ai.analisar_gabarito_vision(img.getvalue())
                                                st.session_state.current_scan_res = [res_json.get(f"{i+1:02d}", "?") for i in range(len(gab_alvo))]
                                                st.session_state.current_scan_img = img.getvalue(); st.rerun()

                                        if "current_scan_res" in st.session_state:
                                            with st.popover("🔍 Lente Ampliadora de Zoom (Conferir Foto)"):
                                                st.image(st.session_state.current_scan_img, caption="Gabarito Original Capturado", use_container_width=True)

                                            res_lidas = st.session_state.current_scan_res
                                            dados_pericia = []
                                            for i, lido in enumerate(res_lidas):
                                                if i < len(gab_alvo):
                                                    status = "✅ ACERTO" if lido == gab_alvo[i] else ("🚫 DUPLA" if lido == "X" else "❌ ERRO")
                                                    dados_pericia.append({"Q": f"{i+1:02d}", "Lido": lido, "Status": status, "🧮 Cálculo OK?": True})
                                            
                                            df_mesa = st.data_editor(
                                                pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                                                column_config={
                                                    "Q": st.column_config.TextColumn(disabled=True), 
                                                    "Lido": st.column_config.SelectboxColumn("Ajustar", options=["A", "B", "C", "D", "E", "X", "?"], required=True), 
                                                    "Status": st.column_config.TextColumn(disabled=True),
                                                    "🧮 Cálculo OK?": st.column_config.CheckboxColumn("Cálculo OK?", default=True, help="Desmarque caso o aluno não tenha apresentado o cálculo no papel (Aplica 50% da nota na questão)")
                                                },
                                                key=f"ed_turbo_{v}"
                                            )
                                            
                                            novas_res = df_mesa["Lido"].tolist()
                                            calculos_ok = df_mesa["🧮 Cálculo OK?"].tolist()
                                            
                                            peso_q = v_total_at / len(gab_alvo) if len(gab_alvo) > 0 else 0.3
                                            nota_f = 0.0
                                            acertos = 0
                                            respostas_com_flag = []
                                            erros_detalhados_tri = []
                                            
                                            for i, r in enumerate(novas_res):
                                                has_calc = calculos_ok[i] if i < len(calculos_ok) else True
                                                if i < len(gab_alvo) and r == gab_alvo[i]:
                                                    acertos += 1
                                                    nota_f += peso_q if has_calc else (peso_q / 2)
                                                else:
                                                    q_idx_n = i + 1
                                                    padrao_q_p = rf"(?si)QUEST[AÃ]O\s*0?{q_idx_n}\b.*?(?=\n\s*QUEST[AÃ]O|$)"
                                                    m_p_item = re.search(padrao_q_p, grade_raw_ref)
                                                    desc_dist = m_p_item.group(0).strip() if m_p_item else f"Erro no item Q{q_idx_n:02d}."
                                                    erros_detalhados_tri.append(f"**Q{q_idx_n:02d} (Marcou {r} | Certo {gab_alvo[i]}):** {desc_dist}")
                                                
                                                flag_letra = f"{r}*" if (not has_calc and r in ["A","B","C","D","E"]) else r
                                                respostas_com_flag.append(flag_letra)
                                                    
                                            st.metric("Nota Final Calculada (Proporcional)", f"{nota_f:.1f} / {v_total_at:.1f}", delta=f"{acertos}/{len(gab_alvo)} acertos (Dupla: {len(alunos_alvo)} alunos)")
                                            
                                            if erros_detalhados_tri:
                                                with st.expander("🧠 Diagnóstico TRI de Erros Encontrados na Correção", expanded=False):
                                                    for err_txt in erros_detalhados_tri:
                                                        st.warning(preparar_para_leitura(err_txt))

                                            col_s1, col_s2 = st.columns(2)
                                            if col_s1.button("Gravar Correção", type="primary", use_container_width=True, key=f"btn_save_corr_{v}"):
                                                with st.spinner("Enviando foto JPG para o Drive e salvando nota no banco..."):
                                                    mat_nome_ref = str(material_ref.get('TIPO_MATERIAL', at_sel))
                                                    link_foto_jpg = db.subir_e_converter_para_google_docs(
                                                        st.session_state.current_scan_img, 
                                                        alunos_alvo[0].replace(" ","_"), 
                                                        trimestre=tr_sel, 
                                                        categoria=t_sel, 
                                                        semana=mat_nome_ref, 
                                                        modo="SCANNER"
                                                    )
                                                    
                                                    grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                                    respostas_salvar = ";".join(respostas_com_flag) + grupo_str
                                                    
                                                    df_turma_completa = df_alunos[df_alunos['TURMA'] == t_sel] if not df_alunos.empty else pd.DataFrame()
                                                    for aluno_nome in alunos_alvo:
                                                        match_al = df_turma_completa[df_turma_completa['NOME_ALUNO'] == aluno_nome]
                                                        if not match_al.empty:
                                                            id_al = db.limpar_id(match_al.iloc[0].get('ID', ''))
                                                            
                                                            try:
                                                                wb_del = db.conectar()
                                                                ws_del = wb_del.worksheet("DB_GABARITOS_ALUNOS")
                                                                dados_del = ws_del.get_all_values()
                                                                for idx_d in range(len(dados_del) - 1, 0, -1):
                                                                    row_d = dados_del[idx_d]
                                                                    if len(row_d) > 4 and db.limpar_id(row_d[1]) == id_al and at_sel.split('-')[0].strip() in row_d[4]:
                                                                        ws_del.delete_rows(idx_d + 1)
                                                            except: pass
                                                            
                                                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                                                datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, mat_nome_ref, respostas_salvar, util.sosa_to_str(nota_f), link_foto_jpg
                                                            ])
                                                    
                                                    db.limpar_notas_turma_trimestre(t_sel, tr_sel)
                                                    del st.session_state.current_scan_res
                                                    del st.session_state.current_scan_img
                                                    st.success("✅ Prova gravada e nota computada com sucesso!")
                                                    time.sleep(0.5)
                                                    st.rerun()

                                            if col_s2.button("Descartar", use_container_width=True, key=f"btn_disc_corr_{v}"):
                                                del st.session_state.current_scan_res
                                                del st.session_state.current_scan_img
                                                st.rerun()

                                    else:
                                        opcoes_letras = ["A", "B", "C", "X", "?"] if is_pei_grading else ["A", "B", "C", "D", "E", "X", "?"]
                                        dados_manual = [{"Q": f"{i+1:02d}", "Gabarito": gab_alvo[i], "Resposta": "?", "Cálculo": True} for i in range(len(gab_alvo))]
                                        
                                        img_manual_file = st.file_uploader("📷 Anexar Foto da Prova (.jpg) - Opcional:", type=["jpg", "jpeg", "png"], key=f"up_man_{v}")
                                        
                                        df_manual = st.data_editor(
                                            pd.DataFrame(dados_manual), hide_index=True, use_container_width=True,
                                            column_config={"Q": st.column_config.TextColumn(disabled=True), "Gabarito": st.column_config.TextColumn(disabled=True), "Resposta": st.column_config.SelectboxColumn(options=opcoes_letras, required=True), "Cálculo": st.column_config.CheckboxColumn("Cálculo OK")},
                                            key=f"manual_grid_{v}"
                                        )
                                        
                                        peso_q = v_total_at / len(gab_alvo) if len(gab_alvo) > 0 else 0.3
                                        nota_calc = 0.0
                                        respostas_finais = []
                                        for i, row in df_manual.iterrows():
                                            resp = row["Resposta"]
                                            has_calc_m = row["Cálculo"]
                                            if resp == row["Gabarito"]:
                                                nota_calc += peso_q if has_calc_m else (peso_q / 2)
                                            flag_m = f"{resp}*" if (not has_calc_m and resp in ["A","B","C","D","E"]) else resp
                                            respostas_finais.append(flag_m)
                                                
                                        st.metric("Nota Calculada (Proporcional)", f"{nota_calc:.1f} / {v_total_at:.1f}")
                                        if st.button("Gravar Correção Manual", type="primary", use_container_width=True, key=f"btn_save_man_{v}"):
                                            mat_nome_ref = str(material_ref.get('TIPO_MATERIAL', at_sel))
                                            link_foto_man = "N/A"
                                            if img_manual_file is not None:
                                                with st.spinner("Enviando foto JPG da prova para o Drive..."):
                                                    link_foto_man = db.subir_e_converter_para_google_docs(
                                                        img_manual_file.getvalue(), 
                                                        alunos_alvo[0].replace(" ","_"), 
                                                        trimestre=tr_sel, categoria=t_sel, semana=mat_nome_ref, modo="SCANNER"
                                                    )

                                            grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                            respostas_salvar = ";".join(respostas_finais) + grupo_str
                                            
                                            df_turma_completa = df_alunos[df_alunos['TURMA'] == t_sel] if not df_alunos.empty else pd.DataFrame()
                                            for aluno_nome in alunos_alvo:
                                                match_al_man = df_turma_completa[df_turma_completa['NOME_ALUNO'] == aluno_nome]
                                                if not match_al_man.empty:
                                                    id_al = db.limpar_id(match_al_man.iloc[0].get('ID', ''))
                                                    db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, mat_nome_ref, respostas_salvar, util.sosa_to_str(nota_calc), link_foto_man])
                                            
                                            db.limpar_notas_turma_trimestre(t_sel, tr_sel)
                                            st.success("✅ Salvo com sucesso!"); time.sleep(0.5); st.rerun()

                                elif is_qualitativa:
                                    st.warning("Avaliação Qualitativa PEI N3: Avaliação baseada em rubricas de mediação pedagógica.")
                                    nivel3_txt = re.split(r"--- LINKS ---", ai.extrair_tag(txt_ref, "NIVEL_3"), flags=re.IGNORECASE)[0].strip() if ai.extrair_tag(txt_ref, "NIVEL_3") else ""
                                    rubricas_encontradas = []
                                    
                                    if nivel3_txt:
                                        m_rubrica = re.search(r"(?i)RUBRICA.*?(?:\n)(.*)", nivel3_txt, re.DOTALL)
                                        if m_rubrica:
                                            for linha in m_rubrica.group(1).split('\n'):
                                                linha_limpa = re.sub(r'^[-*•]\s*', '', linha).replace('**', '').strip()
                                                if linha_limpa and len(linha_limpa) > 5 and "http" not in linha_limpa.lower():
                                                    rubricas_encontradas.append(linha_limpa)
                                    
                                    if not rubricas_encontradas:
                                        rubricas_encontradas = [
                                            "1. Autonomia Executiva (Realiza atividades com independência)",
                                            "2. Compreensão de Comandos (Atende a instruções diretas)",
                                            "3. Percepção Visual e Espacial (Identifica símbolos e formas)",
                                            "4. Raciocínio Lógico-Proporcional (Associa quantidades)"
                                        ]

                                    c_q1, c_q2 = st.columns([1, 1.5])
                                    nota_qual = c_q1.number_input("Nota Atribuída (Proporcional):", 0.0, v_total_at, v_total_at, step=0.5, key=f"nq_{v}")
                                    respostas_rubrica = []
                                    
                                    with c_q2:
                                        st.markdown("**Rubricas Pedagógicas de Observação:**")
                                        for i_r, rubrica in enumerate(rubricas_encontradas):
                                            st.markdown(f"**{rubrica}**")
                                            resp = st.selectbox("Status:", ["✅ Autônomo", "🤝 Com Apoio", "❌ Não Realizado"], key=f"rub_{v}_{i_r}", label_visibility="collapsed")
                                            respostas_rubrica.append(f"- {rubrica}: {resp}")
                                        obs_extra = st.text_area("Notas extras do professor:", height=60, key=f"oq_extra_{v}")
                                        parecer_final = "\n".join(respostas_rubrica) + (f"\nObs: {obs_extra}" if obs_extra.strip() else "")
                                            
                                    if st.button("Salvar Avaliação PEI N3", type="primary", use_container_width=True, key=f"btn_save_pei3_{v}"):
                                        grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                        df_turma_completa = df_alunos[df_alunos['TURMA'] == t_sel] if not df_alunos.empty else pd.DataFrame()
                                        for aluno_nome in alunos_alvo:
                                            match_al_q = df_turma_completa[df_turma_completa['NOME_ALUNO'] == aluno_nome]
                                            if not match_al_q.empty:
                                                id_al = db.limpar_id(match_al_q.iloc[0].get('ID', ''))
                                                db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, at_sel, f"QUALITATIVA|{parecer_final}{grupo_str}", util.sosa_to_str(nota_qual), "N/A"])
                                                db.salvar_no_banco("DB_RELATORIOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, "AVALIACAO_QUALITATIVA", f"Avaliação: {at_sel}\nNota: {nota_qual}\nParecer:\n{parecer_final}"])
                                        db.limpar_notas_turma_trimestre(t_sel, tr_sel)
                                        st.success("✅ Avaliação PEI N3 salva com sucesso!"); time.sleep(0.5); st.rerun()

                        renderizar_mesa_correcao_fragmento()

        # ==============================================================================
        # ABA 2: TRIBUNAL DE AUDITORIA (UNIFICADO COM BANCO REAL DO ALUNO)
        # ==============================================================================
        with tab_auditoria:
            st.markdown("### Tribunal de Auditoria de Resultados")
            with st.container(border=True):
                c_h1, c_h2 = st.columns(2)
                t_sel_h = c_h1.selectbox("👥 Selecione a Turma:", [""] + lista_turmas_cir, key=f"t_h_{v}")
                tr_sel_h = c_h2.selectbox("📅 Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_h_{v}")

            if t_sel_h and tr_sel_h:
                padrao_regex_trim = obter_regex_trimestre(tr_sel_h)
                serie_num = "".join(filter(str.isdigit, t_sel_h))
                
                df_prova_trib = pd.DataFrame()
                gab_oficial_trib = {}
                v_total_av = 10.0
                
                opcoes_base = obter_avaliacoes_unificadas_cir(t_sel_h, tr_sel_h)
                av_alvo_h = st.selectbox("📋 Avaliação Alvo:", [""] + opcoes_base, key=f"av_h_{v}")

                if av_alvo_h:
                    is_sonda = "SONDA" in av_alvo_h.upper() or "DIAGNÓSTICA" in av_alvo_h.upper()
                    nome_curto_av = av_alvo_h.split("-")[0].strip()
                    
                    df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'] == av_alvo_h] if not df_aulas.empty else pd.DataFrame()
                    if not df_prova_trib.empty:
                        txt_prova_trib = str(df_prova_trib.iloc[0].get('CONTEUDO', ''))
                        gab_oficial_trib_list = ai.extrair_gab_universal_com_fallback(txt_prova_trib, is_pei=False)
                        gab_oficial_trib = {i+1: letra for i, letra in enumerate(gab_oficial_trib_list)}
                        val_tag = ai.extrair_tag(txt_prova_trib, "VALOR")
                        if val_tag: v_total_av = util.sosa_to_float(val_tag)

                    gabaritos_lidos = pd.DataFrame()
                    if not df_diagnosticos.empty and 'TURMA' in df_diagnosticos.columns and 'ID_AVALIACAO' in df_diagnosticos.columns:
                        mask_diag_h = (df_diagnosticos['TURMA'] == t_sel_h) & (
                            df_diagnosticos['ID_AVALIACAO'].astype(str).str.contains(nome_curto_av, case=False, na=False)
                        )
                        gabaritos_lidos = df_diagnosticos[mask_diag_h]

                    alunos_turma_h = df_alunos[df_alunos['TURMA'] == t_sel_h].sort_values(by="NOME_ALUNO") if not df_alunos.empty else pd.DataFrame()
                    
                    dados_soberania = []
                    for _, alu in alunos_turma_h.iterrows():
                        id_a = db.limpar_id(alu.get('ID', ''))
                        nome_alu_f = str(alu.get('NOME_ALUNO', 'Estudante'))
                        nec_alu_f = str(alu.get('NECESSIDADES', 'TÍPICO'))
                        
                        leitura = pd.DataFrame()
                        if not gabaritos_lidos.empty and 'ID_ALUNO' in gabaritos_lidos.columns:
                            leitura = gabaritos_lidos[gabaritos_lidos['ID_ALUNO'].apply(db.limpar_id) == id_a]
                            
                        situacao_txt, versao_prova, nota_atual, link_ev, respostas_salvas, grupo_parceiros = "✍️ PENDENTE", "PROVA ORIGINAL", 0.0, "", "MANUAL", ""

                        if not leitura.empty:
                            reg = leitura.iloc[-1]
                            nota_atual = util.sosa_to_float(reg.get('NOTA_CALCULADA', 0.0))
                            link_ev = str(reg.get('LINK_FOTO_DRIVE', ''))
                            respostas_salvas = str(reg.get('RESPOSTAS_ALUNO', 'MANUAL'))
                            id_av_banco = str(reg.get('ID_AVALIACAO', '')).upper()
                            
                            if "|GRUPO:" in respostas_salvas:
                                partes = respostas_salvas.split("|GRUPO:")
                                respostas_salvas = partes[0]
                                grupo_parceiros = partes[1]
                            
                            if respostas_salvas.startswith("FALTOU_JUSTIFICADO"):
                                motivo_j = respostas_salvas.split("|")[1] if "|" in respostas_salvas else "Atestado Médico"
                                situacao_txt, versao_prova = f"📑 JUSTIFICADO ({motivo_j})", "2ª CHAMADA PENDENTE"
                            elif respostas_salvas.startswith("FALTOU_INJUSTIFICADO"):
                                situacao_txt, versao_prova = "❌ FALTA INJUSTIFICADA", "ZERO REGIMENTAL"
                            elif respostas_salvas == "FALTOU":
                                situacao_txt, versao_prova = "❌ FALTOU", "N/A"
                            elif "2ª" in id_av_banco or "2CHAMADA" in id_av_banco:
                                situacao_txt, versao_prova = "✅ REALIZADA", "SEGUNDA CHAMADA"
                            elif "TIPO" in id_av_banco:
                                situacao_txt, versao_prova = "✅ REALIZADA", f"VARIANTE ({id_av_banco.split('-')[-1].strip()})"
                            else:
                                situacao_txt, versao_prova = "✅ REALIZADA", "PROVA ORIGINAL"

                        dados_soberania.append({
                            "ID": id_a, "Estudante": nome_alu_f, "Perfil": "♿ PEI" if nec_alu_f.upper().strip() not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"] else "📝 REGULAR",
                            "Situação": situacao_txt, "Versão": versao_prova, "Nota": nota_atual, "Dupla / Grupo": grupo_parceiros if grupo_parceiros else "Individual", "Evidência": link_ev, "_Respostas": respostas_salvas
                        })

                    st.markdown("#### ⚡ Ações Rápidas de Auditoria")
                    c_act1, c_act2, c_act3 = st.columns(3)

                    if c_act1.button("⚖️ Atestados & Justificativas", use_container_width=True, key=f"btn_act_atest_{v}"):
                        dialog_atestados_modal(alunos_turma_h, t_sel_h, tr_sel_h, av_alvo_h)
                        
                    if c_act2.button("👤 Perícia por Estudante", use_container_width=True, key=f"btn_act_peric_{v}"):
                        dialog_pericia_modal(dados_soberania, alunos_turma_h, t_sel_h, tr_sel_h, av_alvo_h, gab_oficial_trib, v_total_av, nome_curto_av)
                        
                    if c_act3.button("🚑 Digitação Manual (Lázaro)", use_container_width=True, key=f"btn_act_laz_{v}"):
                        dialog_lazaro_modal(dados_soberania, gab_oficial_trib, v_total_av, t_sel_h, tr_sel_h, av_alvo_h)

                    st.markdown("---")

                    @st.fragment
                    def renderizar_espelho_tribunal_fragmento():
                        st.markdown("#### 🔍 Inspeção de Espelho de Gabarito & Raio-X de Itens")
                        
                        opcoes_cadernos_visuais = ["📝 Regular (Tipo A)", "🧬 Variante (Tipo B)", "🔵 PEI Nível 1 (Apoio Leve)", "🟡 PEI Nível 2 (Apoio Moderado)"]
                        caderno_sel_tab = st.pills("Selecione o Caderno para Auditar:", opcoes_cadernos_visuais, default="📝 Regular (Tipo A)", key=f"pills_caderno_inspect_audit_{v}")
                        
                        is_pei_cad = "PEI" in str(caderno_sel_tab)
                        nivel_pei_tag = "NIVEL_1" if "Nível 1" in str(caderno_sel_tab) else "NIVEL_2"
                        
                        nome_busca_caderno = av_alvo_h
                        if "Tipo B" in str(caderno_sel_tab):
                            nome_busca_caderno = f"{av_alvo_h} - TIPO B"

                        df_prova_cad = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_busca_caderno] if not df_aulas.empty else pd.DataFrame()
                        if df_prova_cad.empty: df_prova_cad = df_prova_trib

                        txt_cad_conteudo = str(df_prova_cad.iloc[0].get('CONTEUDO', '')) if not df_prova_cad.empty else ""
                        gab_caderno_ativo = ai.extrair_gab_universal_com_fallback(txt_cad_conteudo, is_pei_cad, nivel_pei_tag)

                        col_espelho, col_raiox = st.columns([1.2, 1.8])

                        with col_espelho:
                            with st.container(border=True):
                                st.markdown("##### 📌 Espelho de Gabarito Adotado")
                                st.caption(f"Exibindo chave oficial para: **{caderno_sel_tab}**")
                                
                                grid_espelho = []
                                for q_i, l_g in enumerate(gab_caderno_ativo):
                                    grid_espelho.append({
                                        "Questão": f"Q{q_i+1:02d}",
                                        "Gabarito Atual": l_g,
                                        "Novo Gabarito / Ação": l_g
                                    })
                                
                                df_espelho_ed = st.data_editor(
                                    pd.DataFrame(grid_espelho), hide_index=True, use_container_width=True, height=280,
                                    column_config={
                                        "Questão": st.column_config.TextColumn(disabled=True, width="small"),
                                        "Gabarito Atual": st.column_config.TextColumn(disabled=True, width="small"),
                                        "Novo Gabarito / Ação": st.column_config.SelectboxColumn("Ajustar Resposta", options=["A", "B", "C", "D", "E", "🚫 ANULADA"], required=True)
                                    },
                                    key=f"ed_espelho_split_audit_{str(caderno_sel_tab).replace(' ','_')}_{v}"
                                )

                                peso_q_espelho = v_total_av / len(gab_caderno_ativo) if len(gab_caderno_ativo) > 0 else 0
                                st.caption(f"• **Total de Questões:** {len(gab_caderno_ativo)} | **Valor por Item:** {peso_q_espelho:.2f} pts")

                                if st.button("⚡ SALVAR NOVO ESPELHO E RECALCULAR TURMA", type="primary", use_container_width=True, key=f"btn_save_espelho_audit_{v}"):
                                    with st.status("Recalculando notas para este caderno...", expanded=True) as status_rec:
                                        novos_gabs_map = {}
                                        for _, r_e in df_espelho_ed.iterrows():
                                            num_q_e = int(r_e["Questão"].replace("Q", ""))
                                            novos_gabs_map[num_q_e] = r_e["Novo Gabarito / Ação"]

                                        wb_s = db.conectar()
                                        ws_g = wb_s.worksheet("DB_GABARITOS_ALUNOS")
                                        d_g = ws_g.get_all_values()
                                        
                                        for idx_row in range(1, len(d_g)):
                                            row_b = d_g[idx_row]
                                            if len(row_b) > 4 and row_b[3] == t_sel_h and nome_curto_av in row_b[4]:
                                                resp_bruta = str(row_b[5])
                                                if not resp_bruta.startswith("FALTOU") and not resp_bruta.startswith("QUALITATIVA") and resp_bruta != "MANUAL":
                                                    if "|GRUPO:" in resp_bruta:
                                                        respostas_letras = resp_bruta.split("|GRUPO:")[0].split(';')
                                                    else:
                                                        respostas_letras = resp_bruta.split(';')

                                                    nova_nota_a = 0.0
                                                    for q_idx in range(len(novos_gabs_map)):
                                                        q_num = q_idx + 1
                                                        letra_c = novos_gabs_map.get(q_num)
                                                        item_a = respostas_letras[q_idx].strip().upper() if q_idx < len(respostas_letras) else "?"
                                                        letra_a = item_a.replace("*", "")
                                                        tem_calc = "*" not in item_a

                                                        if letra_c == "🚫 ANULADA": nova_nota_a += peso_q_espelho
                                                        elif letra_a == letra_c: nova_nota_a += peso_q_espelho if tem_calc else (peso_q_espelho / 2)

                                                    ws_g.update_cell(idx_row + 1, 7, util.sosa_to_str(min(v_total_av, nova_nota_a)))

                                        db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                        st.cache_data.clear()
                                        wb_s_fresh = db.conectar()
                                        d_g_fresh = wb_s_fresh.worksheet("DB_GABARITOS_ALUNOS").get_all_values()
                                        map_novas = {db.limpar_id(r[1]): util.sosa_to_float(r[6]) for r in d_g_fresh[1:] if len(r) > 6 and r[3] == t_sel_h and nome_curto_av in r[4]}
                                        
                                        lista_boletim_novas = []
                                        for _, alu in alunos_turma_h.iterrows():
                                            id_l = db.limpar_id(alu.get('ID', ''))
                                            nome_l = str(alu.get('NOME_ALUNO', 'Estudante'))
                                            reg_atual = df_notas[(df_notas['TURMA'] == t_sel_h) & (df_notas['TRIMESTRE'] == tr_sel_h) & (df_notas['ID_ALUNO'].apply(db.limpar_id) == id_l)] if not df_notas.empty else pd.DataFrame()
                                            v_vistos = reg_atual.iloc[0].get('NOTA_VISTOS', '0,0') if not reg_atual.empty else "0,0"
                                            v_teste = reg_atual.iloc[0].get('NOTA_TESTE', '0,0') if not reg_atual.empty else "0,0"
                                            v_prova = reg_atual.iloc[0].get('NOTA_PROVA', '0,0') if not reg_atual.empty else "0,0"
                                            v_rec = reg_atual.iloc[0].get('NOTA_REC', '0,0') if not reg_atual.empty else "0,0"
                                            
                                            if id_l in map_novas:
                                                nota_recalculada_str = util.sosa_to_str(map_novas[id_l])
                                                if "TESTE" in av_alvo_h.upper(): v_teste = nota_recalculada_str
                                                else: v_prova = nota_recalculada_str

                                            nova_media = min(10.0, util.sosa_to_float(v_vistos) + util.sosa_to_float(v_teste) + util.sosa_to_float(v_prova))
                                            if util.sosa_to_float(v_rec) > 0: nova_media = max(nova_media, util.sosa_to_float(v_rec))
                                            lista_boletim_novas.append([id_l, nome_l, t_sel_h, tr_sel_h, util.sosa_to_str(v_vistos), util.sosa_to_str(v_teste), util.sosa_to_str(v_prova), util.sosa_to_str(v_rec), util.sosa_to_str(nova_media)])

                                        db.salvar_lote("DB_NOTAS", lista_boletim_novas)
                                        status_rec.update(label="✅ Espelho atualizado e notas recalculadas!", state="complete")
                                        st.balloons(); time.sleep(1.2); st.rerun()

                        with col_raiox:
                            with st.container(border=True):
                                st.markdown("##### 🔍 Raio-X dos Enunciados e Distratores (TRI)")
                                
                                if not gab_caderno_ativo:
                                    st.info("Selecione uma avaliação para carregar o Raio-X.")
                                else:
                                    num_q_inspect = st.selectbox("Selecione o Item para Leitura Clínica:", [f"Questão {i+1:02d}" for i in range(len(gab_caderno_ativo))], key=f"sel_q_inspect_audit_{v}")
                                    q_idx_inspect = int(num_q_inspect.replace("Questão ", ""))
                                    
                                    tag_questoes_cad = nivel_pei_tag if is_pei_cad else "QUESTOES"
                                    q_raw_text = ai.extrair_tag(txt_cad_conteudo, tag_questoes_cad) or ai.extrair_tag(txt_cad_conteudo, "QUESTOES")
                                    
                                    prefixo_q = r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)"
                                    padrao_q = rf"(?si)({prefixo_q}\s*0?{q_idx_inspect}\b.*?)(?={prefixo_q}\s*0?{q_idx_inspect+1}\b|GABARITO|RESPOSTAS|GRADE|$)"
                                    m_q = re.search(padrao_q, q_raw_text, re.IGNORECASE | re.DOTALL)
                                    
                                    tag_grade_cad = "GRADE_DE_CORRECAO_PEI" if is_pei_cad else "GRADE_DE_CORRECAO"
                                    grade_raw_text = ai.extrair_tag(txt_cad_conteudo, tag_grade_cad) or ai.extrair_tag(txt_cad_conteudo, "GRADE_DE_CORRECAO")
                                    m_p = re.search(padrao_q, grade_raw_text, re.IGNORECASE | re.DOTALL)
                                    
                                    st.markdown(f"**📄 Enunciado Oficial ({num_q_inspect}):**")
                                    if m_q: st.write(preparar_para_leitura(m_q.group(1).strip()))
                                    else: st.info("Enunciado da questão disponível na impressão oficial.")
                                    
                                    st.divider()
                                    st.markdown("**🧠 Perícia Pedagógica (Descritor SAEB & Distratores):**")
                                    if m_p:
                                        p_texto = re.sub(r'[*#]', '', m_p.group(1).strip())
                                        st.info(preparar_para_leitura(p_texto))
                                    else: st.caption("Perícia de distratores não vinculada a esta questão.")

                    renderizar_espelho_tribunal_fragmento()

                    st.markdown("---")
                    st.markdown("#### 📋 Visão Geral da Turma e Notas Auditadas")
                    
                    df_soberano_ed = st.data_editor(
                        pd.DataFrame(dados_soberania), hide_index=True, use_container_width=True, key=f"ed_sob_{v}",
                        column_config={
                            "ID": None, "_Respostas": None, 
                            "Estudante": st.column_config.TextColumn(disabled=True), 
                            "Perfil": st.column_config.TextColumn(disabled=True), 
                            "Situação": st.column_config.SelectboxColumn(options=["✅ REALIZADA", "❌ FALTOU", "✍️ PENDENTE"], required=True), 
                            "Versão": st.column_config.TextColumn(disabled=True), 
                            "Dupla / Grupo": st.column_config.TextColumn(disabled=True),
                            "Nota": st.column_config.NumberColumn(format="%.1f"), 
                            "Evidência": st.column_config.LinkColumn("🔗 Ver Prova")
                        }
                    )

                    if st.button("Homologar Ajustes Manuais na Tabela", use_container_width=True, type="primary", key=f"btn_homolog_sob_{v}"):
                        with st.status("Gravando...") as status_h:
                            wb_s = db.conectar()
                            ws_g = wb_s.worksheet("DB_GABARITOS_ALUNOS")
                            d_g = ws_g.get_all_values()
                            
                            ids_na_tabela = df_soberano_ed['ID'].astype(str).tolist()
                            dados_atualizados = [d_g[0]]
                            for i in range(1, len(d_g)):
                                row = d_g[i]
                                if len(row) > 4 and db.limpar_id(row[1]) in ids_na_tabela and nome_curto_av in row[4]: continue
                                dados_atualizados.append(row)
                            
                            lista_boletim = []
                            notas_atuais = df_notas[(df_notas['TURMA'] == t_sel_h) & (df_notas['TRIMESTRE'] == tr_sel_h)] if not df_notas.empty else pd.DataFrame()
                            
                            for _, r in df_soberano_ed.iterrows():
                                id_l, nota_s, nome_limpo, resp_originais = str(r['ID']), util.sosa_to_str(r['Nota']), r['Estudante'], r['_Respostas']
                                grupo_str = f"|GRUPO:{r['Dupla / Grupo']}" if r['Dupla / Grupo'] != "Individual" else ""
                                resp_final_gravar = f"{resp_originais}{grupo_str}"
                                
                                if r['Situação'] == "✅ REALIZADA":
                                    id_f = av_alvo_h if r['Versão'] == "PROVA ORIGINAL" else f"{av_alvo_h} ({r['Versão']})"
                                    dados_atualizados.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, id_f, "MANUAL" if resp_originais.startswith("FALTOU") else resp_final_gravar, nota_s, r['Evidência'] or "N/A"])
                                elif r['Situação'] == "❌ FALTOU":
                                    dados_atualizados.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, av_alvo_h, "FALTOU", "0,00", "N/A"])
                                
                                if not is_sonda and r['Situação'] != "✍️ PENDENTE":
                                    reg_atual = notas_atuais[notas_atuais['ID_ALUNO'].apply(db.limpar_id) == id_l] if not notas_atuais.empty else pd.DataFrame()
                                    v_vistos = reg_atual.iloc[0].get('NOTA_VISTOS', '0,0') if not reg_atual.empty else "0,0"
                                    v_teste = reg_atual.iloc[0].get('NOTA_TESTE', '0,0') if not reg_atual.empty else "0,0"
                                    v_prova = reg_atual.iloc[0].get('NOTA_PROVA', '0,0') if not reg_atual.empty else "0,0"
                                    v_rec = reg_atual.iloc[0].get('NOTA_REC', '0,0') if not reg_atual.empty else "0,0"
                                    
                                    nota_boletim = nota_s if r['Situação'] == "✅ REALIZADA" else "0,00"
                                    if "TESTE" in av_alvo_h.upper(): v_teste = nota_boletim
                                    else: v_prova = nota_boletim
                                        
                                    nova_media_final = min(10.0, util.sosa_to_float(v_vistos) + util.sosa_to_float(v_teste) + util.sosa_to_float(v_prova))
                                    if util.sosa_to_float(v_rec) > 0: nova_media_final = max(nova_media_final, util.sosa_to_float(v_rec))
                                    lista_boletim.append([id_l, nome_limpo, t_sel_h, tr_sel_h, v_vistos, v_teste, v_prova, v_rec, util.sosa_to_str(nova_media_final)])
                            
                            ws_g.clear(); ws_g.update(values=dados_atualizados, range_name='A1')
                            if not is_sonda and lista_boletim:
                                db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                db.salvar_lote("DB_NOTAS", lista_boletim)
                            status_h.update(label="Notas e gabaritos auditados!", state="complete"); time.sleep(0.5); st.rerun()

        # ==============================================================================
        # ABA 3: RAIO-X PEDAGÓGICO & PONTE DE RECOMPOSIÇÃO PÓS-PROVA (UNIFICADO & CHAVES ÚNICAS)
        # ==============================================================================
        with tab_raiox:
            st.markdown("### Raio-X Pedagógico: Autópsia por Item & Recomposição")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                t_sel_r = c1.selectbox("Selecione a Turma:", [""] + lista_turmas_cir, key=f"t_r_v90_{v}")
                tr_sel_r = c2.selectbox("Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_r_v90_{v}")
                
                opcoes_base_r = obter_avaliacoes_unificadas_cir(t_sel_r, tr_sel_r)
                at_sel_r = c3.selectbox("Selecione a Avaliação Base:", [""] + opcoes_base_r, key=f"at_r_v90_{v}")

            if not t_sel_r or not at_sel_r:
                st.info("Selecione a Turma e a Avaliação Base acima para carregar o Raio-X Pedagógico.")
            else:
                nome_curto_av = at_sel_r.split("-")[0].strip()
                padrao_regex_trim = obter_regex_trimestre(tr_sel_r)
                serie_num_r = "".join(filter(str.isdigit, t_sel_r))
                
                mask_diag = (df_diagnosticos['TURMA'] == t_sel_r) & (
                    df_diagnosticos['ID_AVALIACAO'].astype(str).str.contains(nome_curto_av, case=False, na=False)
                ) if not df_diagnosticos.empty and 'TURMA' in df_diagnosticos.columns and 'ID_AVALIACAO' in df_diagnosticos.columns else pd.Series()
                
                respostas_brutas = df_diagnosticos[mask_diag].copy() if not df_diagnosticos.empty and not mask_diag.empty else pd.DataFrame()

                if respostas_brutas.empty:
                    st.warning("⚠️ Nenhuma resposta de aluno encontrada para esta avaliação no trimestre selecionado.")
                else:
                    df_alunos_min = df_alunos[['ID', 'NECESSIDADES']].copy() if not df_alunos.empty and 'ID' in df_alunos.columns and 'NECESSIDADES' in df_alunos.columns else pd.DataFrame()
                    if not df_alunos_min.empty:
                        df_alunos_min['ID'] = df_alunos_min['ID'].apply(db.limpar_id)
                        respostas_brutas['ID_ALUNO_L'] = respostas_brutas['ID_ALUNO'].apply(db.limpar_id)
                        df_analise = pd.merge(respostas_brutas, df_alunos_min, left_on='ID_ALUNO_L', right_on='ID', how='left')
                    else:
                        df_analise = respostas_brutas.copy()
                    
                    def classificar_caderno(row):
                        resp_crua = str(row.get('RESPOSTAS_ALUNO', '')).upper()
                        resp = resp_crua.split("|GRUPO:")[0] if "|GRUPO:" in resp_crua else resp_crua
                        id_av = str(row.get('ID_AVALIACAO', '')).upper()
                        nec = str(row.get('NECESSIDADES', '')).upper()
                        
                        if resp.startswith("FALTOU"): return "FALTOU"
                        if resp.startswith("QUALITATIVA"): return "🔴 PEI Nível 3 (Qualitativa)"
                        if "2ª" in id_av or "2CHAMADA" in id_av: return "🔄 2ª Chamada (Discursiva)"
                        if "TIPO" in id_av: return f"🧬 Variante ({id_av.split('-')[-1].strip()})"
                        
                        is_pei = nec not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE", "PENDENTE", "SUSPEITA", "DEFASAGEM LEITURA", "DEFASAGEM MATEMÁTICA"]
                        if is_pei:
                            qtd_respostas = len(resp.split(';'))
                            if qtd_respostas <= 10: return "🔵 PEI Nível 1 (Apoio Leve)"
                            
                        return "📝 Prova Padrão (Tipo A)"

                    df_analise['CADERNO_FEITO'] = df_analise.apply(classificar_caderno, axis=1)
                    cadernos_disponiveis = sorted([c for c in df_analise['CADERNO_FEITO'].unique() if c != "FALTOU"])
                    
                    if not cadernos_disponiveis:
                        st.info("Todos os alunos faltaram a esta avaliação.")
                    else:
                        with st.container(border=True):
                            caderno_alvo = st.pills("🔍 Selecione o Caderno Específico para Análise:", cadernos_disponiveis, default=cadernos_disponiveis[0], key=f"cad_alvo_pills_raiox_{v}")
                        
                        df_filtrado = df_analise[df_analise['CADERNO_FEITO'] == caderno_alvo]
                        
                        material_ref = None
                        is_pei_view = "PEI" in str(caderno_alvo)
                        is_2a_chamada = "2ª Chamada" in str(caderno_alvo)
                        
                        if is_2a_chamada:
                            df_busca = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(padrao_regex_trim, regex=True, case=False)) & (df_aulas['ANO'].str.contains(serie_num_r))] if not df_aulas.empty else pd.DataFrame()
                            if not df_busca.empty: material_ref = df_busca.iloc[0]
                        elif "Variante" in str(caderno_alvo):
                            tipo_letra = str(caderno_alvo).split("TIPO")[-1].replace(")", "").strip()
                            df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == f"{at_sel_r} - TIPO {tipo_letra}"] if not df_aulas.empty else pd.DataFrame()
                            if not df_busca.empty: material_ref = df_busca.iloc[0]
                        else:
                            df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_r] if not df_aulas.empty else pd.DataFrame()
                            if not df_busca.empty: material_ref = df_busca.iloc[0]

                        txt_prova_base = str(material_ref.get('CONTEUDO', '')) if material_ref is not None else ""
                        gab_ativo_list = ai.extrair_gab_universal_com_fallback(txt_prova_base, is_pei_view) if txt_prova_base else []
                        gab_ativo = {i+1: letra for i, letra in enumerate(gab_ativo_list)}
                            
                        stats_list = []
                        if is_2a_chamada:
                            q_raw = ai.extrair_tag(txt_prova_base, "QUESTOES")
                            num_q_total = len(re.findall(r"(?i)QUESTÃO\s*0?\d+", q_raw)) or 10
                            matriz_respostas = [str(r.get('RESPOSTAS_ALUNO', '')).split('|GRUPO:')[0].split(';') for _, r in df_filtrado.iterrows()]
                            
                            for i in range(1, num_q_total + 1):
                                votos = [res[i-1] if len(res) >= i else "?" for res in matriz_respostas]
                                acertos_integrais = votos.count("✅ Acerto Integral")
                                acertos_parciais = votos.count("⚠️ Acerto Parcial")
                                pontos_obtidos = acertos_integrais + (acertos_parciais * 0.5)
                                perc = (pontos_obtidos / len(votos)) * 100 if len(votos) > 0 else 0
                                stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": "Discursiva"})
                        elif "Qualitativa" in str(caderno_alvo):
                            st.info("♿ **Modo Qualitativo:** Avaliação baseada em parecer descritivo no Dossiê do Aluno.")
                        else:
                            num_q_total = len(gab_ativo) if gab_ativo else 10
                            for i in range(1, num_q_total + 1):
                                acertos = 0
                                validos = 0
                                for _, row_aluno in df_filtrado.iterrows():
                                    resp_limpa = str(row_aluno.get('RESPOSTAS_ALUNO', '')).split('|GRUPO:')[0]
                                    respostas_lista = resp_limpa.upper().split(';')
                                    if len(respostas_lista) >= i:
                                        validos += 1
                                        letra_aluno_clean = respostas_lista[i-1].replace("*", "")
                                        if gab_ativo and letra_aluno_clean == gab_ativo.get(i, "?"): acertos += 1
                                
                                perc = (acertos / validos) * 100 if validos > 0 else 0.0
                                stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": gab_ativo.get(i, "?") if gab_ativo else "?"})
                            
                        df_stats_global = pd.DataFrame(stats_list)
                        
                        if not df_stats_global.empty:
                            worst_q = df_stats_global.loc[df_stats_global['Acerto %'].idxmin()]
                            best_q = df_stats_global.loc[df_stats_global['Acerto %'].idxmax()]
                            avg_ret = df_stats_global['Acerto %'].mean()
                            
                            st.markdown(f"""
                            <div style='display: flex; gap: 10px; margin-bottom: 20px;'>
                                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center;'>
                                    <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>📉 Calcanhar de Aquiles</span><br>
                                    <span style='font-size: 18px; color: #E74C3C; font-weight: 800;'>{worst_q['Questão']} ({worst_q['Acerto %']:.1f}%)</span>
                                </div>
                                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center;'>
                                    <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>🏆 Domínio Consolidado</span><br>
                                    <span style='font-size: 18px; color: #2ECC71; font-weight: 800;'>{best_q['Questão']} ({best_q['Acerto %']:.1f}%)</span>
                                </div>
                                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center;'>
                                    <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>📊 Retenção Média</span><br>
                                    <span style='font-size: 18px; color: #2962FF; font-weight: 800;'>{avg_ret:.1f}%</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                            st.markdown(f"#### Histograma de Desempenho: **{caderno_alvo}**")
                            fig_global = px.bar(df_stats_global, x="Questão", y="Acerto %", text_auto='.0f', color="Acerto %", color_continuous_scale="RdYlGn")
                            fig_global.update_layout(yaxis_range=[0, 110], height=280, margin=dict(l=20, r=20, t=30, b=20))
                            st.plotly_chart(fig_global, use_container_width=True)

                            st.markdown("---")
                            
                            c_aut1, c_aut2 = st.columns([1.5, 1.5])
                            
                            with c_aut1:
                                st.markdown("#### 🔬 Autópsia Clínica do Item")
                                c_sel, c_btn = st.columns([2, 1])
                                q_sel = c_sel.selectbox("Selecione a Questão:", df_stats_global["Questão"].tolist(), key=f"sel_q_inspect_raiox_{v}", label_visibility="collapsed")
                                
                                @st.dialog("🔬 Autópsia Clínica do Item", width="large")
                                def dialog_autopsia(q_str, stats_row):
                                    idx_num = int(q_str.replace("Q", ""))
                                    prefixo_q = r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)"
                                    padrao_q = rf"(?si)({prefixo_q}\s*0?{idx_num}\b.*?)(?={prefixo_q}\s*0?{idx_num+1}\b|GABARITO|RESPOSTAS|GRADE|$)"
                                    
                                    if "Nível 1" in str(caderno_alvo): tag_questoes = "NIVEL_1"
                                    elif "Nível 2" in str(caderno_alvo): tag_questoes = "NIVEL_2"
                                    elif is_pei_view: tag_questoes = "PEI"
                                    else: tag_questoes = "QUESTOES"
                                    
                                    q_raw_reg = ai.extrair_tag(txt_prova_base, tag_questoes) or ai.extrair_tag(txt_prova_base, "QUESTOES")
                                    m_q_reg = re.search(padrao_q, q_raw_reg, re.IGNORECASE | re.DOTALL)
                                    
                                    tag_grade = "GRADE_DE_CORRECAO_PEI" if is_pei_view else "GRADE_DE_CORRECAO"
                                    grade_raw = ai.extrair_tag(txt_prova_base, tag_grade)
                                    m_p_reg = re.search(padrao_q, grade_raw, re.IGNORECASE | re.DOTALL)
                                    
                                    c_left, c_right = st.columns([1.5, 1])
                                    with c_left:
                                        st.markdown(f"### 📄 Enunciado Oficial ({q_str})")
                                        if m_q_reg: st.write(preparar_para_leitura(m_q_reg.group(1).strip()))
                                        else: st.info("Enunciado da questão disponível na impressão oficial.")
                                    
                                    with c_right:
                                        st.markdown("### 📊 Desempenho")
                                        acerto_perc = stats_row['Acerto %']
                                        cor_acerto = "normal" if acerto_perc >= 60 else "inverse"
                                        st.metric("Índice de Acerto", f"{acerto_perc:.1f}%", delta="Atenção" if acerto_perc < 50 else "Adequado", delta_color=cor_acerto)
                                        st.metric("Gabarito Oficial", stats_row['Gabarito'])
                                        
                                        st.markdown("---")
                                        st.markdown("### 🧠 Perícia Pedagógica (Descritor SAEB & Distratores)")
                                        if m_p_reg:
                                            p_completa = re.sub(r'[*#]', '', m_p_reg.group(1).strip())
                                            st.info(preparar_para_leitura(p_completa))
                                        else: st.caption("Perícia de distratores não localizada.")

                                if c_btn.button("🔍 Analisar Item", use_container_width=True, key=f"btn_autopsia_item_raiox_{v}"):
                                    stats_row = df_stats_global[df_stats_global['Questão'] == q_sel].iloc[0]
                                    dialog_autopsia(q_sel, stats_row)

                            with c_aut2:
                                st.markdown("#### 🧠 Inteligência Preditiva & Recomposição")
                                c_pr1, c_pr2 = st.columns(2)
                                
                                if c_pr1.button("Diagnóstico Preditivo", use_container_width=True, key=f"btn_gen_prog_raiox_{v}"):
                                    with st.spinner("Analisando lacunas..."):
                                        worst_3 = df_stats_global.sort_values(by="Acerto %").head(3)
                                        stats_str = "\n".join([f"{r['Questão']}: {r['Acerto %']:.1f}% de acerto" for _, r in worst_3.iterrows()])
                                        
                                        contexto_str = ""
                                        tag_grade = "GRADE_DE_CORRECAO_PEI" if is_pei_view else "GRADE_DE_CORRECAO"
                                        grade_raw = ai.extrair_tag(txt_prova_base, tag_grade)
                                        prefixo_q = r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)"
                                        
                                        for _, r in worst_3.iterrows():
                                            idx_num = int(r['Questão'].replace("Q", ""))
                                            padrao_q = rf"(?si)({prefixo_q}\s*0?{idx_num}\b.*?)(?={prefixo_q}\s*0?{idx_num+1}\b|GABARITO|RESPOSTAS|GRADE|$)"
                                            m_p_reg = re.search(padrao_q, grade_raw, re.IGNORECASE | re.DOTALL)
                                            if m_p_reg: contexto_str += f"Erro na {r['Questão']}: {re.sub(r'[*#]', '', m_p_reg.group(1).strip())}\n"
                                        
                                        res_prog = ai.gerar_prognostico_pedagogico(stats_str, contexto_str)
                                        st.session_state[f"prog_{v}"] = res_prog

                                if c_pr2.button("🚀 Forjar Recomposição (3 Itens Mais Errados)", type="primary", use_container_width=True, key=f"btn_ponte_recomp_raiox_{v}"):
                                    with st.status("Extraindo os 3 itens com menor índice de acerto e gerando caderno de recomposição...", expanded=True) as status_rec_auto:
                                        worst_3 = df_stats_global.sort_values(by="Acerto %").head(3)
                                        itens_criticos_str = ", ".join(worst_3['Questão'].tolist())
                                        
                                        prompt_recomp_auto = (
                                            f"PROVA ORIGINAL:\n{txt_prova_base}\n\n"
                                            f"ITENS CRÍTICOS COM MAIOR ÍNDICE DE ERRO NA TURMA {t_sel_r}: {itens_criticos_str}.\n"
                                            f"SÉRIE: {t_sel_r}.\n"
                                            f"MISSÃO: Crie o Caderno de Recomposição FOCADO ESTRITAMENTE nesses 3 itens críticos, gerando Roteiro do Professor e Exercícios Espelho para os alunos."
                                        )
                                        res_recomp_auto = ai.gerar_ia("ARQUITETO_REVISAO_V29", prompt_recomp_auto)
                                        
                                        nome_recomp_auto = f"RECOMPO_{at_sel_r}_LACUNAS"
                                        info_recomp_auto = {"ano": f"{serie_num_r}º", "trimestre": tr_sel_r, "semana": "RECOMPOSIÇÃO"}

                                        status_rec_auto.write("📄 Gerando Caderno de Exercícios do Aluno...")
                                        doc_alu_rec = exporter.gerar_docx_aluno_v24(nome_recomp_auto, ai.extrair_tag(res_recomp_auto, "ALUNO"), info_recomp_auto)
                                        link_alu_rec = db.subir_e_converter_para_google_docs(doc_alu_rec, f"{nome_recomp_auto}_ALUNO", modo="AULA")

                                        status_rec_auto.write("👨‍🏫 Gerando Guia do Professor...")
                                        doc_prof_rec = exporter.gerar_docx_professor_v25(nome_recomp_auto, ai.extrair_tag(res_recomp_auto, "PROFESSOR"), info_recomp_auto)
                                        link_prof_rec = db.subir_e_converter_para_google_docs(doc_prof_rec, f"{nome_recomp_auto}_PROF", modo="AULA")

                                        conteudo_final_rec = f"{res_recomp_auto}\n\n--- LINKS ---\nRegular({link_alu_rec}) Prof({link_prof_rec})"

                                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                            datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_recomp_auto,
                                            conteudo_final_rec, f"{serie_num_r}º", link_alu_rec
                                        ])

                                        status_rec_auto.update(label="✅ Caderno de Recomposição Forjado e Sincronizado no Drive!", state="complete")
                                        st.balloons()
                                        st.link_button("📂 ABRIR CADERNO DE RECOMPOSIÇÃO NO DRIVE", link_alu_rec, type="primary", use_container_width=True)

                            if f"prog_{v}" in st.session_state:
                                st.success(f"💡 **Prognóstico de Intervenção:**\n\n{st.session_state[f'prog_{v}']}")










# ==============================================================================
# MÓDULO: BIOGRAFIA DO ESTUDANTE - V2026.ULTIMATE
# (DOSSIÊ 360°, FILTRO ATIVOS X INATIVOS/TRANSFERIDOS, CERTIDÃO DE PRODUÇÃO DOCX)
# ==============================================================================
elif menu == "👤 Biografia do Estudante":
    st.title("👤 Biografia do Estudante: Dossiê 360°")
    st.caption("Dashboard executivo para reuniões de pais, certidão de transferência/inativos, linha do tempo e sincronia ao vivo.")
    st.markdown("---")

    def obter_regex_trimestre_local(trimestre_str):
        if not trimestre_str or trimestre_str == "Todos": return r".*"
        t_upper = str(trimestre_str).upper()
        if "III" in t_upper or "TERCEIRO" in t_upper: return r"(?<!I)III(?![I])"
        elif "II" in t_upper or "SEGUNDO" in t_upper: return r"(?<!I)II(?![I])"
        else: return r"(?<!I)I(?![I])"

    if "v_bio" not in st.session_state: 
        st.session_state.v_bio = int(time.time())
    v = st.session_state.v_bio

    # LEI 25: DIALOGS DECLARADOS NO NÍVEL SUPERIOR
    @st.dialog("⚖️ Tribunal de Recursos", width="large")
    def dialog_tribunal(id_aluno_dialog, nome_aluno_dialog, is_pei_dialog, df_diag_dialog):
        opcoes_av_tribunal = df_diag_dialog['ID_AVALIACAO'].tolist() if not df_diag_dialog.empty else []
        if not opcoes_av_tribunal:
            st.info("Nenhuma avaliação escaneada encontrada para este aluno.")
        else:
            av_contestada = st.selectbox("1️⃣ Selecione a Avaliação Questionada:", opcoes_av_tribunal, key=f"trib_av_pop_{v}")
            if av_contestada:
                reg_av_trib = df_diag_dialog[df_diag_dialog['ID_AVALIACAO'] == av_contestada].iloc[0]
                respostas_aluno_trib = str(reg_av_trib['RESPOSTAS_ALUNO']).split(';')
                link_foto_trib = reg_av_trib.get('LINK_FOTO_DRIVE', '')
                
                nome_base_av = av_contestada.replace(" (2ª CHAMADA)", "")
                if "VARIANTE" in nome_base_av.upper() or "TIPO" in nome_base_av.upper():
                    tipo_letra = re.search(r'TIPO\s*([A-Z])', nome_base_av, re.IGNORECASE)
                    letra = tipo_letra.group(1) if tipo_letra else "B"
                    nome_busca = f"{nome_base_av.split('(')[0].strip()} - TIPO {letra}"
                else: nome_busca = nome_base_av
                    
                df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_busca] if not df_aulas.empty else pd.DataFrame()
                
                if not df_prova_trib.empty:
                    txt_prova_trib = str(df_prova_trib.iloc[0]['CONTEUDO'])
                    tag_gab_trib = "GABARITO_PEI" if is_pei_dialog else "GABARITO_TEXTO"
                    tag_grade_trib = "GRADE_DE_CORRECAO_PEI" if is_pei_dialog else "GRADE_DE_CORRECAO"
                    tag_questoes_trib = "PEI" if is_pei_dialog else "QUESTOES"
                    
                    gab_raw_trib = ai.extrair_tag(txt_prova_trib, tag_gab_trib) or ai.extrair_tag(txt_prova_trib, "GABARITO")
                    grade_raw_trib = re.sub(r'[*#]', '', ai.extrair_tag(txt_prova_trib, tag_grade_trib) or ai.extrair_tag(txt_prova_trib, "GRADE_DE_CORRECAO"))
                    questoes_raw_trib = ai.extrair_tag(txt_prova_trib, tag_questoes_trib)
                    
                    matches_gab = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", gab_raw_trib.upper())
                    if matches_gab: gab_oficial_trib = {int(num): letra for num, letra in matches_gab}
                    else:
                        letras = re.findall(r"\b[A-E]\b", gab_raw_trib.upper())
                        gab_oficial_trib = {i+1: letra for i, letra in enumerate(letras)}
                        
                    qtd_questoes_trib = len(gab_oficial_trib)
                    
                    q_contestada = st.selectbox("2️⃣ Selecione a Questão:", [f"Questão {i}" for i in range(1, qtd_questoes_trib + 1)], key=f"trib_q_pop_{v}")
                    q_num_trib = int(q_contestada.split(" ")[1])
                    
                    letra_marcada_trib = respostas_aluno_trib[q_num_trib - 1] if q_num_trib <= len(respostas_aluno_trib) else "?"
                    letra_correta_trib = gab_oficial_trib.get(q_num_trib, "?")
                    
                    prefixo_q_trib = "QUEST[AÃ]O\\s*PEI" if is_pei_dialog else "QUEST[AÃ]O"
                    padrao_q_trib = rf"(?si)({prefixo_q_trib}\s*0?{q_num_trib}\b.*?)(?={prefixo_q_trib}\s*0?{q_num_trib+1}\b|GABARITO|$)"
                    m_q_trib = re.search(padrao_q_trib, questoes_raw_trib)
                    enunciado_trib = m_q_trib.group(1).strip() if m_q_trib else "Enunciado não localizado."
                    
                    padrao_p_trib = rf"(?si){prefixo_q_trib}\s*0?{q_num_trib}\b.*?(?={prefixo_q_trib}\s*0?{q_num_trib+1}\b|GABARITO|RESPOSTAS|$)"
                    m_p_trib = re.search(padrao_p_trib, grade_raw_trib)
                    pericia_trib = m_p_trib.group(0).strip() if m_p_trib else "Perícia não localizada."
                    
                    st.markdown("#### 📸 Card de Evidências (Para Print)")
                    with st.container(border=True):
                        c_ev1, c_ev2 = st.columns([3, 1])
                        c_ev1.markdown(f"**Estudante:** {nome_aluno_dialog} | **Avaliação:** {nome_base_av}")
                        if "http" in link_foto_trib: c_ev2.link_button("📸 Ver Foto do Gabarito", link_foto_trib, use_container_width=True)
                        
                        st.divider()
                        st.info(preparar_para_leitura(enunciado_trib).replace('\n', '\n\n'))
                        
                        c_res1, c_res2 = st.columns(2)
                        c_res1.error(f"**❌ O aluno marcou:** {letra_marcada_trib}")
                        c_res2.success(f"**✅ Gabarito Oficial:** {letra_correta_trib}")
                        
                        st.warning(f"**🔬 Análise do Erro (Perícia):**\n{preparar_para_leitura(pericia_trib)}")
                        
                    st.markdown("#### ⚖️ O Veredito")
                    c_ver1, c_ver2 = st.columns(2)
                    
                    if c_ver1.button("🔴 A Nota Fica (Gerar Defesa Pedagógica)", use_container_width=True, key=f"btn_def_trib_pop_{v}"):
                        with st.spinner("Redigindo defesa pedagógica..."):
                            prompt_defesa = f"VEREDITO: MANTER NOTA.\nALUNO: {nome_aluno_dialog}.\nQUESTÃO: {q_num_trib}.\nMARCOU: {letra_marcada_trib}. CORRETA: {letra_correta_trib}.\nPERÍCIA/ERRO: {pericia_trib}.\nENUNCIADO: {enunciado_trib}."
                            st.session_state.msg_tribunal = ai.gerar_ia("DEFENSOR_PEDAGOGICO", prompt_defesa)
                            
                    if c_ver2.button("🟢 O Pai Tem Razão (Corrigir Nota)", use_container_width=True, key=f"btn_corr_trib_pop_{v}"):
                        st.session_state.modo_correcao_tribunal = True
                        
                    if st.session_state.get("modo_correcao_tribunal", False):
                        with st.container(border=True):
                            st.success("🛠️ **Modo de Correção Ativado**")
                            nova_letra = st.selectbox("Qual letra o aluno realmente marcou?", ["A", "B", "C", "D", "E"], index=["A", "B", "C", "D", "E"].index(letra_correta_trib) if letra_correta_trib in ["A", "B", "C", "D", "E"] else 0, key=f"sel_letra_trib_pop_{v}")
                            
                            if st.button("💾 Confirmar Correção e Recalcular Média", type="primary", key=f"btn_conf_trib_pop_{v}"):
                                with st.spinner("Corrigindo gabarito e recalculando boletim..."):
                                    novas_respostas = respostas_aluno_trib.copy()
                                    if q_num_trib - 1 < len(novas_respostas): novas_respostas[q_num_trib - 1] = nova_letra
                                    else: novas_respostas.append(nova_letra)
                                        
                                    acertos_novos = sum(1 for i, r in enumerate(novas_respostas) if i+1 in gab_oficial_trib and r == gab_oficial_trib[i+1])
                                    val_total_prova = util.sosa_to_float(ai.extrair_tag(txt_prova_trib, "VALOR")) or 10.0
                                    nova_nota_prova = (acertos_novos / qtd_questoes_trib) * val_total_prova if qtd_questoes_trib > 0 else 0.0
                                    
                                    try:
                                        wb = db.conectar()
                                        ws_gab = wb.worksheet("DB_GABARITOS_ALUNOS")
                                        dados_gab = ws_gab.get_all_values()
                                        for i, row in enumerate(dados_gab):
                                            if i > 0 and db.limpar_id(row[1]) == id_aluno_dialog and row[4] == av_contestada:
                                                ws_gab.update_cell(i+1, 6, ";".join(novas_respostas))
                                                ws_gab.update_cell(i+1, 7, util.sosa_to_str(nova_nota_prova))
                                                break
                                    except Exception as e: st.error(f"Erro ao atualizar gabarito: {e}")
                                        
                                    st.cache_data.clear()
                                    prompt_retratacao = f"VEREDITO: CORRIGIR NOTA.\nALUNO: {nome_aluno_dialog}.\nQUESTÃO: {q_num_trib}.\nNOVA NOTA DA AVALIAÇÃO: {nova_nota_prova:.1f}."
                                    st.session_state.msg_tribunal = ai.gerar_ia("DEFENSOR_PEDAGOGICO", prompt_retratacao)
                                    st.session_state.modo_correcao_tribunal = False
                                    st.rerun()
                                    
                    if "msg_tribunal" in st.session_state:
                        st.markdown("#### 📱 Resposta para o WhatsApp")
                        st.info("Copie o texto abaixo e envie para o responsável junto com o print do Card de Evidências.")
                        st.code(st.session_state.msg_tribunal, language=None)
                else: st.warning("A prova original não foi encontrada no acervo para realizar a perícia.")

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Cadastre as turmas na Gestão da Turma.")
    else:
        hoje_dt = date.today()
        if hoje_dt <= date(2026, 5, 22): idx_trim_bio_default = 1
        elif hoje_dt <= date(2026, 9, 4): idx_trim_bio_default = 2
        else: idx_trim_bio_default = 3

        opcoes_periodo_bio = ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"]

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 1.2, 1.5, 1])
            
            lista_turmas_bio = []
            if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
                turmas_reais_bio = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
                lista_turmas_bio = sorted(turmas_reais_bio['ID_TURMA'].unique())
            elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
                lista_turmas_bio = sorted(df_alunos['TURMA'].unique())
            
            turma_b = c1.selectbox("👥 Turma:", lista_turmas_bio, key=f"bio_t_{v}")
            
            # FILTRO NOVO: ATIVOS X TRANSFERIDOS / EVADIDOS
            flt_status_bio = c2.pills("Filtro de Status:", ["🟢 Ativos", "👻 Inativos/Transferidos"], default="🟢 Ativos", key=f"pills_flt_status_{v}")
            
            df_alunos_turma_raw = df_alunos[df_alunos['TURMA'] == turma_b].copy()
            if 'STATUS' not in df_alunos_turma_raw.columns: df_alunos_turma_raw['STATUS'] = "ATIVO"
            
            if flt_status_bio == "🟢 Ativos":
                lista_alunos = df_alunos_turma_raw[~df_alunos_turma_raw['STATUS'].astype(str).str.upper().isin(["TRANSFERIDO", "EVADIDO", "INATIVO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")
            else:
                lista_alunos = df_alunos_turma_raw[df_alunos_turma_raw['STATUS'].astype(str).str.upper().isin(["TRANSFERIDO", "EVADIDO", "INATIVO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")

            if lista_alunos.empty:
                st.warning("Nenhum aluno encontrado para esse filtro nesta turma.")
                st.stop()
            
            def definir_icone_status(nec):
                n = str(nec).upper().strip()
                if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                if "DEFASAGEM LEITURA" in n: return "🧱"
                if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
                if "ALTA PERFORMANCE" in n: return "🚀"
                if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                return "♿"

            lista_alunos['STATUS_ICON'] = lista_alunos['NECESSIDADES'].apply(definir_icone_status)
            lista_alunos['LABEL'] = lista_alunos.apply(lambda x: f"{x['STATUS_ICON']} {x['NOME_ALUNO']}", axis=1)
                
            aluno_b_label = c3.selectbox("🎓 Estudante:", lista_alunos['LABEL'].tolist(), key=f"bio_a_{v}")
            trim_b = c4.selectbox("📅 Período (Auto):", opcoes_periodo_bio, index=idx_trim_bio_default, key=f"bio_trim_{v}")

        if trim_b == "I Trimestre": dt_ini, dt_fim = date(2026, 2, 9), date(2026, 5, 22)
        elif trim_b == "II Trimestre": dt_ini, dt_fim = date(2026, 5, 25), date(2026, 9, 4)
        elif trim_b == "III Trimestre": dt_ini, dt_fim = date(2026, 9, 8), date(2026, 12, 17)
        else: dt_ini, dt_fim = date(2026, 1, 1), date(2026, 12, 31)

        nome_limpo = aluno_b_label.split(" ", 1)[1].strip() 
        info_alu = lista_alunos[lista_alunos['NOME_ALUNO'] == nome_limpo].iloc[0]
        id_alu = db.limpar_id(info_alu['ID'])
        perfil_atual = str(info_alu['NECESSIDADES']).upper().strip()
        status_atual_aluno = str(info_alu.get('STATUS', 'ATIVO')).upper().strip()
        is_pei_or_gap = perfil_atual not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]
        
        n_alu = df_notas[df_notas['ID_ALUNO'].apply(db.limpar_id) == id_alu] if not df_notas.empty else pd.DataFrame()

        d_alu_f = pd.DataFrame()
        if not df_diario.empty:
            d_alu = df_diario[((df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu) | (df_diario['ID_ALUNO'] == "GLOBAL")) & (df_diario['TURMA'] == turma_b)].copy()
            if not d_alu.empty:
                d_alu['DATA_DT'] = pd.to_datetime(d_alu['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                d_alu_f = d_alu[(d_alu['DATA_DT'] >= dt_ini) & (d_alu['DATA_DT'] <= dt_fim)]

        diag_alu_f = pd.DataFrame()
        if not df_diagnosticos.empty:
            diag_alu = df_diagnosticos[df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu].copy()
            if trim_b != "Todos" and not diag_alu.empty:
                padrao_trim_regex = obter_regex_trimestre_local(trim_b)
                diag_alu_f = diag_alu[diag_alu['ID_AVALIACAO'].str.contains(padrao_trim_regex, regex=True, case=False, na=False)]
            else:
                diag_alu_f = diag_alu.copy()

        # CÁLCULO AO VIVO DE VISTOS E BÔNUS
        aulas_com_visto_hero, perc_visto_hero, bonus_total_hero = 0, 0, 0.0
        faltas_hero, perc_presenca_hero = 0, 100
        
        vistos_live_by_trim = {}
        bonus_live_by_trim = {}
        
        calendario_trims = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
            "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
        }

        if not df_diario.empty:
            df_d_aluno_all = df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diario['TURMA'] == turma_b)].copy()
            if not df_d_aluno_all.empty:
                df_d_aluno_all['DATA_DT'] = pd.to_datetime(df_d_aluno_all['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                
                for t_nome, (t_i, t_f) in calendario_trims.items():
                    df_d_t_sub = df_d_aluno_all[(df_d_aluno_all['DATA_DT'] >= t_i) & (df_d_aluno_all['DATA_DT'] <= t_f)]
                    if not df_d_t_sub.empty:
                        d_validas = df_d_t_sub[df_d_t_sub['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                        v_ok = len(d_validas[d_validas['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                        tot_v = len(d_validas)
                        vistos_live_by_trim[t_nome] = round((v_ok / tot_v * 3.0), 2) if tot_v > 0 else 0.0
                        bonus_live_by_trim[t_nome] = df_d_t_sub['BONUS'].apply(util.sosa_to_float).sum()

            if not d_alu_f.empty:
                d_alu_validas_hero = d_alu_f[~d_alu_f['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])]
                total_aulas_hero = len(d_alu_validas_hero)
                faltas_hero = len(d_alu_validas_hero[d_alu_validas_hero['TAGS'] == "AUSÊNCIA"])
                perc_presenca_hero = ((total_aulas_hero - faltas_hero) / total_aulas_hero) * 100 if total_aulas_hero > 0 else 100
                
                d_vistos_hero = d_alu_validas_hero[d_alu_validas_hero['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                tot_vistos_hero = len(d_vistos_hero)
                vistos_ok_hero = len(d_vistos_hero[d_vistos_hero['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                perc_visto_hero = (vistos_ok_hero / tot_vistos_hero) * 100 if tot_vistos_hero > 0 else 0
                bonus_total_hero = d_alu_f['BONUS'].apply(util.sosa_to_float).sum()

        soma_anual_live = 0.0
        trims_ativos_cnt = 0

        for t_k in ["I Trimestre", "II Trimestre", "III Trimestre"]:
            reg_t = n_alu[n_alu['TRIMESTRE'] == t_k] if not n_alu.empty else pd.DataFrame()
            v_c1 = vistos_live_by_trim.get(t_k, 0.0)
            if v_c1 == 0 and not reg_t.empty: v_c1 = util.sosa_to_float(reg_t.iloc[0]['NOTA_VISTOS'])
            
            v_c2 = util.sosa_to_float(reg_t.iloc[0]['NOTA_TESTE']) if not reg_t.empty else 0.0
            v_c3 = util.sosa_to_float(reg_t.iloc[0]['NOTA_PROVA']) if not reg_t.empty else 0.0
            
            if not df_diagnosticos.empty:
                padrao_t_reg = obter_regex_trimestre_local(t_k)
                scanned_t = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diagnosticos['TURMA'] == turma_b) & (df_diagnosticos['ID_AVALIACAO'].str.contains(padrao_t_reg, regex=True, case=False, na=False))]
                if not scanned_t.empty:
                    st_teste = scanned_t[scanned_t['ID_AVALIACAO'].str.upper().str.contains("TESTE")]
                    if not st_teste.empty and v_c2 == 0: v_c2 = util.sosa_to_float(st_teste.iloc[-1]['NOTA_CALCULADA'])
                    st_prova = scanned_t[scanned_t['ID_AVALIACAO'].str.upper().str.contains("PROVA")]
                    if not st_prova.empty and v_c3 == 0: v_c3 = util.sosa_to_float(st_prova.iloc[-1]['NOTA_CALCULADA'])

            b_diario_t = bonus_live_by_trim.get(t_k, 0.0)
            
            c1_fin = min(3.0, v_c1 + b_diario_t)
            rem_b = b_diario_t - (c1_fin - v_c1)
            c2_fin = min(3.0, v_c2 + max(0.0, rem_b))
            rem_b -= (c2_fin - v_c2)
            c3_fin = min(4.0, v_c3 + max(0.0, rem_b))

            m_live_t = min(10.0, round((c1_fin + c2_fin + c3_fin) * 2) / 2)
            if m_live_t > 0 or not reg_t.empty:
                trims_ativos_cnt += 1
                soma_anual_live += m_live_t

        meta_parcial_top = (trims_ativos_cnt or 1) * 6.0

        # CARTÃO BENTO DE TOPO
        with st.container(border=True):
            c_h1, c_h2, c_h3, c_h4 = st.columns([2, 1, 1, 1])
            
            with c_h1:
                st.markdown(f"<h3 style='margin-bottom: 0px;'>{nome_limpo}</h3>", unsafe_allow_html=True)
                st.caption(f"**ID:** {id_alu} | **Turma:** {turma_b} | **Status:** `{status_atual_aluno}`")
                
                if "PENDENTE" in perfil_atual or "SUSPEITA" in perfil_atual: st.caption(f"Perfil: 🟠 RADAR DE INVESTIGAÇÃO ({perfil_atual})")
                elif "DEFASAGEM" in perfil_atual: st.caption(f"Perfil: 🧱 BARREIRA DE APRENDIZAGEM ({perfil_atual})")
                elif "ALTA PERFORMANCE" in perfil_atual: st.caption(f"Perfil: 🚀 DESTAQUE COGNITIVO ({perfil_atual})")
                elif is_pei_or_gap: st.caption(f"Perfil: ♿ CONDIÇÃO CLÍNICA PEI ({perfil_atual})")
                else: st.caption("Perfil: 👤 PERFIL TÍPICO / PADRÃO")
                
            c_h2.metric("Soma Parcial", f"{soma_anual_live:.1f}", f"Meta Parcial: {meta_parcial_top:.1f} pts")
            c_h3.metric("Assiduidade", f"{perc_presenca_hero:.0f}%", f"{faltas_hero} falta(s)", delta_color="inverse" if faltas_hero > 0 else "normal")
            c_h4.metric("Engajamento Caderno", f"{perc_visto_hero:.0f}%", f"{bonus_total_hero:+.1f} pts bônus")

        # MODAIS
        @st.dialog("📱 Extrato para WhatsApp (Pais ou Direção)")
        def dialog_whatsapp():
            st.info("Copie o texto abaixo e envie para o responsável ou para a Direção/Coordenação.")
            
            atestados_info = ""
            hist_atestados = df_relatorios[(df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_relatorios['TIPO'] == 'JUSTIFICATIVA_AUSENCIA')] if not df_relatorios.empty else pd.DataFrame()
            if not hist_atestados.empty:
                atestados_info = "\n📌 ATESTADOS / JUSTIFICATIVAS:\n"
                for _, r_at in hist_atestados.iterrows():
                    atestados_info += f"• {r_at['DATA']}: {r_at['CONTEUDO']}\n"

            msg_zap = f"""Olá! Tudo bem? Aqui é o professor Ronaldo Gomes. 🏫
Compartilho o Extrato Oficial de Produção do(a) estudante {nome_limpo} ({turma_b}).

📌 STATUS REGIMENTAL: {status_atual_aluno}
📊 SOMA PARCIAL ACUMULADA: {soma_anual_live:.1f} pts (Meta parcial: {meta_parcial_top:.1f} pts)
{atestados_info}
🎯 FREQUÊNCIA E ENGAJAMENTO:
• Assiduidade: {perc_presenca_hero:.0f}% ({faltas_hero} faltas registradas).
• Vistos de Caderno (C1): {perc_visto_hero:.0f}% das tarefas concluídas.
• Bônus Atitudinais Conquistados: {bonus_total_hero:+.1f} pts!

Documento mantido sob guarda do Componente Curricular de Matemática. 🚀"""
            st.code(msg_zap, language=None)

        c_act_b1, c_act_b2, c_act_b3 = st.columns(3)
        
        if c_act_b1.button("📱 Gerar Extrato para WhatsApp", use_container_width=True, key=f"btn_zap_bio_{v}"):
            dialog_whatsapp()

        if c_act_b2.button("🖨️ Imprimir Ficha de Rendimento A4", use_container_width=True, key=f"btn_docx_bio_{v}"):
            with st.spinner("Compilando Ficha de Rendimento..."):
                dados_ficha = [{
                    "nome": nome_limpo,
                    "vistos": f"{perc_visto_hero:.0f}%",
                    "teste": "Sincronizado",
                    "prova": "Sincronizado",
                    "bonus": f"{bonus_total_hero:+.1f}",
                    "media": f"{soma_anual_live:.1f}",
                    "status": f"Assiduidade: {perc_presenca_hero:.0f}% ({faltas_hero} faltas)"
                }]
                info_ficha = {"turma": turma_b, "trimestre": trim_b}
                nome_arq_ficha = f"FICHA_ALUNO_{nome_limpo.replace(' ','_')}_{trim_b.replace(' ','')}"
                
                doc_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_ficha, dados_ficha, info_ficha)
                link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_ficha, trimestre=trim_b, categoria=turma_b, modo="PLANEJAMENTO")
                
                if "https" in link_doc:
                    st.success("✅ Ficha gerada com sucesso!")
                    st.link_button("📂 ABRIR FICHA NO DRIVE", link_doc, type="primary", use_container_width=True)
                    st.balloons()
                else: st.error(f"Erro ao salvar no Drive: {link_doc}")

        # RECURSO NOVO: CERTIDÃO OFICIAL DE PRODUÇÃO (DOCX A4) PARA ALUNOS TRANSFERIDOS/EVADIDOS
        if c_act_b3.button("📜 CERTIDÃO DE PRODUÇÃO (TRANSFERÊNCIA)", type="primary", use_container_width=True, key=f"btn_certidao_transf_{v}"):
            with st.spinner("Compilando Certidão Oficial de Produção e Rendimento A4 para a Direção..."):
                lista_notas_trimestres = []
                for t_k in ["I Trimestre", "II Trimestre", "III Trimestre"]:
                    reg_t = n_alu[n_alu['TRIMESTRE'] == t_k] if not n_alu.empty else pd.DataFrame()
                    c1_v = vistos_live_by_trim.get(t_k, 0.0)
                    if c1_v == 0 and not reg_t.empty: c1_v = util.sosa_to_float(reg_t.iloc[0]['NOTA_VISTOS'])
                    c2_v = util.sosa_to_float(reg_t.iloc[0]['NOTA_TESTE']) if not reg_t.empty else 0.0
                    c3_v = util.sosa_to_float(reg_t.iloc[0]['NOTA_PROVA']) if not reg_t.empty else 0.0
                    rec_v = util.sosa_to_float(reg_t.iloc[0]['NOTA_REC']) if not reg_t.empty else -1.0
                    m_f = min(10.0, c1_v + c2_v + c3_v)
                    if rec_v > 0: m_f = max(m_f, (m_f + rec_v)/2)
                    
                    lista_notas_trimestres.append({
                        "periodo": t_k, "c1": c1_v, "c2": c2_v, "c3": c3_v,
                        "rec": f"{rec_v:.1f}" if rec_v > 0 else "-", "media": m_f
                    })

                dados_aluno_certidao = {
                    "nome": nome_limpo, "id": id_alu, "turma": turma_b,
                    "status": status_atual_aluno, "perfil": perfil_atual,
                    "assiduidade": f"{perc_presenca_hero:.0f}%", "faltas": faltas_hero,
                    "vistos_perc": f"{perc_visto_hero:.0f}%", "bonus": f"{bonus_total_hero:+.1f}",
                    "parecer": f"Certificamos que o(a) estudante esteve matriculado(a) na turma {turma_b} sob regência do Prof. Ronaldo Gomes. Registrou-se uma soma acumulada de {soma_anual_live:.1f} pontos no período em que esteve ativo no componente de Matemática."
                }
                
                info_escola_certidao = {"ano": turma_b, "trimestre": "Conselho/Regência"}
                nome_arq_certidao = f"CERTIDAO_PRODUCAO_{nome_limpo.replace(' ','_')}_{turma_b}"
                
                doc_cert_stream = exporter.gerar_docx_certidao_producao(nome_arq_certidao, dados_aluno_certidao, lista_notas_trimestres, info_escola_certidao)
                link_cert_doc = db.subir_e_converter_para_google_docs(doc_cert_stream, nome_arq_certidao, trimestre="Conselho", categoria=turma_b, modo="PLANEJAMENTO")
                
                if "https" in link_cert_doc:
                    st.success("✅ Certidão Oficial de Produção gerada no Drive!")
                    st.link_button("📂 ABRIR CERTIDÃO OFICIAL (DOCX A4)", link_cert_doc, type="primary", use_container_width=True)
                    st.balloons()

        st.markdown("---")

        @st.fragment
        def renderizar_dossie_bio_fragmento():
            abas_bio = ["📊 Visão Geral & Boletim", "🕰️ Linha do Tempo (Atitude)", "📈 Evolução & Lacunas", "⚖️ Auditoria & Tribunal"]
            if is_pei_or_gap: abas_bio.append("♿ Dossiê Clínico (PEI)")
            
            tabs = st.tabs(abas_bio)

            with tabs[0]:
                st.markdown(f"#### 🧾 Extrato Analítico de Notas (Ao Vivo)")
                with st.container(border=True):
                    dados_notas = []
                    trims_para_exibir = ["I Trimestre", "II Trimestre", "III Trimestre"] if trim_b == "Todos" else [trim_b]
                    
                    for t_e in trims_para_exibir:
                        reg_e = n_alu[n_alu['TRIMESTRE'] == t_e] if not n_alu.empty else pd.DataFrame()
                        
                        v_c1 = vistos_live_by_trim.get(t_e, 0.0)
                        if v_c1 == 0 and not reg_e.empty: v_c1 = util.sosa_to_float(reg_e.iloc[0]['NOTA_VISTOS'])
                        
                        v_c2 = util.sosa_to_float(reg_e.iloc[0]['NOTA_TESTE']) if not reg_e.empty else 0.0
                        v_c3 = util.sosa_to_float(reg_e.iloc[0]['NOTA_PROVA']) if not reg_e.empty else 0.0
                        v_rec = util.sosa_to_float(reg_e.iloc[0]['NOTA_REC']) if not reg_e.empty else -1.0
                        
                        if not df_diagnosticos.empty:
                            padrao_t_e = obter_regex_trimestre_local(t_e)
                            scanned_e = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diagnosticos['TURMA'] == turma_b) & (df_diagnosticos['ID_AVALIACAO'].str.contains(padrao_t_e, regex=True, case=False, na=False))]
                            if not scanned_e.empty:
                                st_t = scanned_e[scanned_e['ID_AVALIACAO'].str.upper().str.contains("TESTE")]
                                if not st_t.empty and v_c2 == 0: v_c2 = util.sosa_to_float(st_t.iloc[-1]['NOTA_CALCULADA'])
                                st_p = scanned_e[scanned_e['ID_AVALIACAO'].str.upper().str.contains("PROVA")]
                                if not st_p.empty and v_c3 == 0: v_c3 = util.sosa_to_float(st_p.iloc[-1]['NOTA_CALCULADA'])

                        b_diario_e = bonus_live_by_trim.get(t_e, 0.0)
                        
                        c1_f = min(3.0, v_c1 + b_diario_e)
                        rem_e = b_diario_e - (c1_f - v_c1)
                        c2_f = min(3.0, v_c2 + max(0.0, rem_e))
                        rem_e -= (c2_f - v_c2)
                        c3_f = min(4.0, v_c3 + max(0.0, rem_e))

                        media_f_e = min(10.0, round((c1_f + c2_f + c3_f) * 2) / 2)
                        if v_rec > 0: media_f_e = max(media_f_e, (media_f_e + v_rec) / 2)

                        dados_notas.append({
                            "Trimestre": t_e,
                            "C1 (Vistos)": c1_f,
                            "C2 (Teste)": c2_f,
                            "C3 (Prova)": c3_f,
                            "Rec.": f"{v_rec:.1f}" if v_rec > 0 else "-",
                            "Média Final": media_f_e,
                            "Status": "✅ DENTRO DA META" if media_f_e >= 6.0 else "⚠️ RECOMPOSIÇÃO"
                        })
                        
                    if dados_notas:
                        def style_status_bio(v):
                            if "DENTRO" in str(v): return 'color: #2ECC71; font-weight: bold;'
                            return 'color: #E74C3C; font-weight: bold;'
                        
                        st.dataframe(
                            pd.DataFrame(dados_notas).style.map(style_status_bio, subset=['Status']), 
                            use_container_width=True, hide_index=True,
                            column_config={
                                "Trimestre": st.column_config.TextColumn("Trimestre", width="medium"),
                                "C1 (Vistos)": st.column_config.NumberColumn("C1 (Vistos)", format="%.1f", width="small"),
                                "C2 (Teste)": st.column_config.NumberColumn("C2 (Teste)", format="%.1f", width="small"),
                                "C3 (Prova)": st.column_config.NumberColumn("C3 (Prova)", format="%.1f", width="small"),
                                "Rec.": st.column_config.TextColumn("Rec.", width="small"),
                                "Média Final": st.column_config.NumberColumn("Média Final", format="%.1f", width="small"),
                                "Status": st.column_config.TextColumn("Status", width="medium")
                            }
                        )
                    else: st.info(f"📭 Sem registros para o {trim_b}.")

            with tabs[1]:
                st.markdown("#### 🕰️ Linha do Tempo da Vida Escolar (Histórico de Atitude)")
                st.caption("Provas concretas para apresentação aos pais na reunião.")
                
                with st.container(border=True):
                    if not d_alu_f.empty:
                        mask_obs = (d_alu_f['TAGS'] != "") | (d_alu_f['OBSERVACOES'] != "") | (d_alu_f['BONUS'].apply(util.sosa_to_float) != 0)
                        tags_obs = d_alu_f[mask_obs].copy()
                        
                        if not tags_obs.empty:
                            for _, row in tags_obs.tail(10).iloc[::-1].iterrows():
                                tag_str = str(row['TAGS']).upper()
                                obs_str = str(row['OBSERVACOES'])
                                bonus_val = util.sosa_to_float(row.get('BONUS', 0))
                                
                                if tag_str == "DIA NÃO LETIVO": 
                                    st.caption(f"🛑 **{row['DATA']}** | Dia Não Letivo - *{obs_str}*")
                                elif "ARGUIÇÃO" in tag_str or bonus_val > 0:
                                    bonus_txt = f" [{bonus_val:+.1f} pts]" if bonus_val != 0 else ""
                                    st.success(f"⭐ **{row['DATA']}** | {tag_str}{bonus_txt} - *{obs_str}*")
                                elif "AUSÊNCIA" in tag_str or "FALTOU" in tag_str:
                                    st.error(f"❌ **{row['DATA']}** | Ausência registrada em sala de aula")
                                elif bonus_val < 0 or any(x in tag_str for x in ["INDISCIPLINA", "CELULAR", "CONVERSA", "ATRASO"]):
                                    st.warning(f"⚠️ **{row['DATA']}** | {tag_str} [{bonus_val:+.1f} pts] - *{obs_str}*")
                                else:
                                    st.info(f"📓 **{row['DATA']}** | {tag_str} - *{obs_str}*")
                        else: st.success("✅ Nenhuma ocorrência negativa ou bônus registrado.")
                    else: st.info("📭 Sem registros no Diário de Bordo para o período.")

            with tabs[2]:
                st.markdown(f"### 📈 Evolução de Desempenho ({trim_b})")
                with st.container(border=True):
                    if not diag_alu_f.empty:
                        diag_alu_f['DATA_DT'] = pd.to_datetime(diag_alu_f['DATA'], format="%d/%m/%Y", errors='coerce')
                        diag_ordenado = diag_alu_f.sort_values(by='DATA_DT', ascending=False)
                        
                        dados_grafico = []
                        for _, row_av in diag_ordenado.iloc[::-1].iterrows(): 
                            av_id_bruto = row_av['ID_AVALIACAO']
                            nota_av = util.sosa_to_float(row_av['NOTA_CALCULADA'])
                            data_av = row_av['DATA']
                            nome_limpo_av = re.sub(r'(_\d+ANO_I{1,3}TRIMESTRE)', '', av_id_bruto).strip()
                            nome_limpo_av = nome_limpo_av.replace("VARIANTE", "").replace("(", "").replace(")", "").strip()
                            
                            if not str(row_av['RESPOSTAS_ALUNO']).upper().startswith("FALTOU"):
                                dados_grafico.append({"Data": data_av, "Avaliação": nome_limpo_av, "Nota": nota_av})
                        
                        if dados_grafico:
                            df_grafico = pd.DataFrame(dados_grafico)
                            fig = px.line(df_grafico, x="Avaliação", y="Nota", text="Nota", markers=True, title="Curva de Aprendizagem (Notas em Avaliações)", hover_data=["Data"])
                            fig.update_traces(textposition="bottom right", line=dict(color="#2962FF", width=3), marker=dict(size=10))
                            fig.update_layout(yaxis_range=[0, 10.5], height=320, margin=dict(l=20, r=20, t=30, b=20))
                            fig.add_hline(y=6.0, line_dash="dash", line_color="red", annotation_text="Meta (6.0)", annotation_position="bottom right")
                            st.plotly_chart(fig, use_container_width=True)
                        else: st.info("O aluno esteve ausente ou possui atestado registrado nas avaliações deste período.")
                    else: st.info("📭 Aguardando avaliações escaneadas para gerar o gráfico de evolução.")

                st.markdown(f"### 🧠 Mapa de Lacunas e Dificuldades ({trim_b})")
                with st.container(border=True):
                    if not diag_alu_f.empty:
                        todas_as_lacunas = []
                        for _, reg_av in diag_alu_f.iterrows():
                            nome_av_real = str(reg_av['ID_AVALIACAO']).replace(" (2ª CHAMADA)", "").strip()
                            m_ref_query = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_av_real.split('_')[0], case=False, na=False)] if not df_aulas.empty else pd.DataFrame()
                            
                            if not m_ref_query.empty:
                                m_ref = m_ref_query.iloc[0]
                                txt_p = str(m_ref['CONTEUDO'])
                                is_pei_alu = is_pei_or_gap and "TIPICO" not in perfil_atual
                                tag_grade = "GRADE_DE_CORRECAO_PEI" if is_pei_alu else "GRADE_DE_CORRECAO"
                                grade = ai.extrair_tag(txt_p, tag_grade) or ai.extrair_tag(txt_p, "GRADE_DE_CORRECAO")
                                tag_g = "GABARITO_PEI" if is_pei_alu else "GABARITO_TEXTO"
                                gab_raw = ai.extrair_tag(txt_p, tag_g) or ai.extrair_tag(txt_p, "GABARITO")
                                gab_oficial = re.findall(r"\b[A-E]\b", gab_raw.upper())
                                respostas_aluno = str(reg_av['RESPOSTAS_ALUNO']).split(';')
                                
                                for i, r in enumerate(respostas_aluno):
                                    if i < len(gab_oficial) and r != gab_oficial[i] and not r.startswith("FALTOU") and r not in ["?", "X"] and not r.startswith("QUALITATIVA"):
                                        q_n = i + 1
                                        padrao_h = rf"(?si)QUEST[AÃ]O\s*(?:PEI\s*)?0?{q_n}\b.*?(?:[:\-])\s*(.*?)(?=\.?\s*(?:JUSTIFICATIVA|PERÍCIA|ANÁLISE|DISTRATORES|$))"
                                        m_h = re.search(padrao_h, grade)
                                        if m_h:
                                            txt_limpo = re.sub(r'[*#\[\]]', '', m_h.group(1)).strip()
                                            todas_as_lacunas.append(f"Questão {q_n:02d}: {txt_limpo}")
                        
                        if todas_as_lacunas:
                            lacunas_unicas = list(dict.fromkeys(todas_as_lacunas))
                            st.warning(f"⚠️ **{len(lacunas_unicas)} questão(ões)** com resposta incorreta nesta avaliação.")
                            with st.expander("🔍 Ver Detalhamento das Lacunas por Questão", expanded=True):
                                for l in lacunas_unicas: st.error(f"❌ {l}")
                        else: st.success("✅ Excelente desempenho nas questões realizadas.")
                    else: st.info("📭 Aguardando avaliações escaneadas para gerar o mapa de lacunas.")

            with tabs[3]:
                st.markdown(f"### 🎯 Histórico de Avaliações & Atestados (Sincronizado)")
                
                if not diag_alu_f.empty:
                    if st.button("⚖️ Abrir Tribunal de Recursos", type="primary", use_container_width=True, key=f"btn_trib_open_{v}"):
                        dialog_tribunal(id_alu, nome_limpo, is_pei_or_gap and "TIPICO" not in perfil_atual, diag_alu_f)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    diag_alu_f['DATA_DT'] = pd.to_datetime(diag_alu_f['DATA'], format="%d/%m/%Y", errors='coerce')
                    diag_ordenado = diag_alu_f.sort_values(by='DATA_DT', ascending=False)
                    
                    dados_av = []
                    for _, row_av in diag_ordenado.iterrows():
                        av_id_bruto = str(row_av['ID_AVALIACAO'])
                        nota_av = util.sosa_to_float(row_av['NOTA_CALCULADA'])
                        respostas_aluno = str(row_av['RESPOSTAS_ALUNO'])
                        link_foto = row_av.get('LINK_FOTO_DRIVE', '')
                        data_av = row_av['DATA']
                        
                        nome_limpo_av = re.sub(r'(_\d+ANO_I{1,3}TRIMESTRE)', '', av_id_bruto).strip()
                        nome_limpo_av = nome_limpo_av.replace("VARIANTE", "").replace("(", "").replace(")", "").strip()
                        
                        if "SONDA" in nome_limpo_av: icone = "🔍"
                        elif "TESTE" in nome_limpo_av: icone = "📝"
                        elif "PROVA" in nome_limpo_av: icone = "📄"
                        else: icone = "📋"
                        
                        if respostas_aluno.startswith("FALTOU_JUSTIFICADO"):
                            motivo_j = respostas_aluno.split("|")[1] if "|" in respostas_aluno else "Atestado Médico"
                            status_av = f"📑 JUSTIFICADO ({motivo_j})"
                        elif respostas_aluno.startswith("FALTOU_INJUSTIFICADO"):
                            status_av = "❌ FALTA INJUSTIFICADA"
                        elif respostas_aluno.upper() == "FALTOU":
                            status_av, nota_av = "❌ FALTOU", 0.0
                        elif respostas_aluno.upper().startswith("QUALITATIVA"):
                            status_av = "🎨 QUALITATIVA (PEI)"
                        elif "MANUAL" in respostas_aluno.upper():
                            status_av = "✍️ LANÇAMENTO MANUAL"
                        else:
                            status_av = "✅ ESCANEADA"
                            
                        dados_av.append({
                            "Tipo": icone, "Avaliação": nome_limpo_av, "Data": data_av,
                            "Nota": nota_av, "Status": status_av, "Evidência": link_foto if "http" in link_foto else None
                        })
                        
                    st.dataframe(
                        pd.DataFrame(dados_av), use_container_width=True, hide_index=True,
                        column_config={
                            "Tipo": st.column_config.TextColumn("", width="small"),
                            "Avaliação": st.column_config.TextColumn("Avaliação", width="medium"),
                            "Data": st.column_config.TextColumn("Data", width="small"),
                            "Nota": st.column_config.NumberColumn("Nota", format="%.1f", width="small"),
                            "Status": st.column_config.TextColumn("Status", width="medium"),
                            "Evidência": st.column_config.LinkColumn("🔗 Ver Prova", width="small")
                        }
                    )
                else:
                    st.info("📭 Nenhuma avaliação escaneada para este aluno no período selecionado.")

            if is_pei_or_gap:
                with tabs[4]:
                    st.markdown(f"### ♿ Dossiê Clínico e Adaptações (PEI)")
                    st.caption("Resumo do Repositório Vivo do aluno.")
                    
                    hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_alu] if not df_relatorios.empty else pd.DataFrame()
                    rel_master = hist_aluno[hist_aluno['TIPO'] == 'DOSSIE_MASTER_PEI'] if not hist_aluno.empty else pd.DataFrame()
                    
                    if not rel_master.empty:
                        master_text = str(rel_master.iloc[-1]['CONTEUDO'])
                        v_diag = ai.extrair_tag(master_text, "DIAGNOSTICO_GERAL")
                        v_diretrizes = ai.extrair_tag(master_text, "DIRETRIZES_CURRICULARES")
                        
                        st.markdown("#### 🧠 Diagnóstico Geral (Status de Safra)")
                        st.info(v_diag if v_diag else "Diagnóstico não preenchido.")
                        
                        st.markdown("#### 🎯 Diretrizes Curriculares Sugeridas")
                        st.warning(v_diretrizes if v_diretrizes else "Diretrizes não preenchidas.")
                    else: st.info("📭 Nenhum Dossiê Master gerado para este aluno ainda.")

        renderizar_dossie_bio_fragmento()
        st.caption(f"Dossiê 360° atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")









# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO - V2026.ULTIMATE (INTELIGÊNCIA TEMPORAL)
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Inteligência de Conselho e Resultados")
    st.caption("Visão panorâmica e ponderada do ano letivo para decisões estratégicas no Conselho de Classe.")
    st.markdown("---")

    if "v_bol" not in st.session_state: 
        st.session_state.v_bol = int(time.time())
    v = st.session_state.v_bol

    if df_notas.empty:
        st.warning("⚠️ Sem notas lançadas no sistema. O Boletim Anual será ativado assim que houver dados.")
    else:
        lista_turmas_bol = []
        if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
            turmas_reais_bol = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_bol = sorted(turmas_reais_bol['ID_TURMA'].unique())
        elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
            lista_turmas_bol = sorted(df_alunos['TURMA'].unique())
        
        if not lista_turmas_bol:
            st.warning("Nenhuma turma cadastrada.")
        else:
            with st.container(border=True):
                c_bol1, c_bol2 = st.columns([2, 1])
                turma_sel = c_bol1.selectbox("🎯 Selecione a Turma para Análise:", lista_turmas_bol, key=f"bol_turma_clean_{v}")
                
                with c_bol2.popover("📜 Registrar Ata do Conselho de Classe"):
                    st.caption("Registre deliberações e pareceres do Conselho de Classe.")
                    tipo_ata = st.selectbox("Tipo de Conselho:", ["Conselho Parcial (I Tri)", "Conselho Parcial (II Tri)", "Conselho Final (III Tri)"], key=f"pop_ata_tipo_{v}")
                    texto_ata = st.text_area("Texto da Ata / Parecer da Turma:", placeholder="Ex: A turma demonstrou evolução satisfatória. Alunos em recuperação foram orientados...", height=120, key=f"pop_ata_txt_{v}")
                    
                    if st.button("💾 Salvar Ata no Banco", type="primary", use_container_width=True, key=f"btn_save_ata_{v}"):
                        if texto_ata.strip():
                            data_hoje_ata = datetime.now().strftime("%d/%m/%Y")
                            db.salvar_ata_conselho(data_hoje_ata, turma_sel, tipo_ata, texto_ata)
                            st.success("✅ Ata do Conselho salva com sucesso!")
                            time.sleep(1); st.rerun()
                        else: st.error("Digite o texto da ata.")

            @st.fragment
            def renderizar_boletim_anual_fragmento():
                df_t = df_notas[df_notas['TURMA'] == turma_sel].copy()
                
                if df_t.empty:
                    st.info(f"📭 Nenhuma nota lançada para a turma {turma_sel} ainda.")
                else:
                    pivot = df_t.pivot_table(
                        index=["ID_ALUNO", "NOME_ALUNO"], 
                        columns="TRIMESTRE", 
                        values=["MEDIA_FINAL", "NOTA_REC"], 
                        aggfunc='first'
                    ).reset_index()

                    pivot.columns = [f"{col[0]}_{col[1]}".strip('_') for col in pivot.columns.values]

                    trims = ["I Trimestre", "II Trimestre", "III Trimestre"]
                    for t in trims:
                        if f"MEDIA_FINAL_{t}" not in pivot.columns: pivot[f"MEDIA_FINAL_{t}"] = 0.0
                        if f"NOTA_REC_{t}" in pivot.columns:
                            pivot[f"NOTA_REC_{t}"] = pivot[f"NOTA_REC_{t}"].fillna(-1.0)
                        else:
                            pivot[f"NOTA_REC_{t}"] = -1.0

                    rec_f_data = df_t[df_t['TRIMESTRE'].str.contains("REC_FINAL|FINAL", na=False, case=False)]
                    if not rec_f_data.empty:
                        rec_f_min = rec_f_data[['ID_ALUNO', 'MEDIA_FINAL']].rename(columns={'MEDIA_FINAL': 'RF'})
                        pivot = pd.merge(pivot, rec_f_min, on='ID_ALUNO', how='left')
                        pivot['RF'] = pivot['RF'].fillna(-1.0)
                    else:
                        pivot['RF'] = -1.0
                    
                    # CÁLCULO DE FALTAS TOTAIS
                    faltas_df = df_diario[(df_diario['TURMA'] == turma_sel) & (df_diario['TAGS'] == "AUSÊNCIA")] if not df_diario.empty else pd.DataFrame()
                    
                    if not faltas_df.empty:
                        faltas_count = faltas_df.groupby('ID_ALUNO').size().reset_index(name='FALTAS')
                        faltas_count['ID_ALUNO'] = faltas_count['ID_ALUNO'].apply(db.limpar_id)
                        
                        pivot['ID_ALUNO_CLEAN'] = pivot['ID_ALUNO'].apply(db.limpar_id)
                        pivot = pd.merge(pivot, faltas_count, left_on='ID_ALUNO_CLEAN', right_on='ID_ALUNO', how='left')
                        
                        if 'ID_ALUNO_y' in pivot.columns: pivot = pivot.drop(columns=['ID_ALUNO_y'])
                        if 'ID_ALUNO_CLEAN' in pivot.columns: pivot = pivot.drop(columns=['ID_ALUNO_CLEAN'])
                        if 'ID_ALUNO_x' in pivot.columns: pivot = pivot.rename(columns={'ID_ALUNO_x': 'ID_ALUNO'})
                            
                        pivot['FALTAS'] = pivot['FALTAS'].fillna(0).astype(int)
                    else:
                        pivot['FALTAS'] = 0

                    pivot = pivot.fillna(0.0)

                    # INTELIGÊNCIA TEMPORAL: Detecta trimestres ativos
                    has_t1 = pivot['MEDIA_FINAL_I Trimestre'].sum() > 0
                    has_t2 = pivot['MEDIA_FINAL_II Trimestre'].sum() > 0
                    has_t3 = pivot['MEDIA_FINAL_III Trimestre'].sum() > 0
                    
                    trimestres_ativos = sum([has_t1, has_t2, has_t3])
                    if trimestres_ativos == 0: trimestres_ativos = 1

                    meta_acumulada_parcial = trimestres_ativos * 6.0

                    dias_validos = df_diario[(df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(['DIA NÃO LETIVO', 'BONUS_CONSELHO', 'SISTEMA_NOTA']))] if not df_diario.empty else pd.DataFrame()
                    total_dias_letivos = dias_validos['DATA'].nunique() if not dias_validos.empty else 1
                    if total_dias_letivos == 0: total_dias_letivos = 1
                    limite_faltas = int(total_dias_letivos * 0.25)
                    if limite_faltas == 0: limite_faltas = 1 

                    # CÁLCULO DA SITUAÇÃO ANUAL PONDERADA
                    def calcular_situacao_anual(row):
                        t1 = util.sosa_to_float(row.get("MEDIA_FINAL_I Trimestre", 0))
                        t2 = util.sosa_to_float(row.get("MEDIA_FINAL_II Trimestre", 0))
                        t3 = util.sosa_to_float(row.get("MEDIA_FINAL_III Trimestre", 0))
                        rf = util.sosa_to_float(row.get("RF", -1.0))
                        faltas_aluno = row.get("FALTAS", 0)
                        
                        soma = t1 + t2 + t3
                        media_parcial = soma / trimestres_ativos
                        
                        aluno_match = df_alunos[df_alunos['ID'].apply(db.limpar_id) == db.limpar_id(row['ID_ALUNO'])] if not df_alunos.empty else pd.DataFrame()
                        if not aluno_match.empty:
                            aluno_info = aluno_match.iloc[0]
                            nec_raw = str(aluno_info['NECESSIDADES']).upper().strip()
                            if "PENDENTE" in nec_raw or "SUSPEITA" in nec_raw: pei = "🟠"
                            elif "DEFASAGEM LEITURA" in nec_raw: pei = "🧱"
                            elif "DEFASAGEM MATEMÁTICA" in nec_raw or "DEFASAGEM MATEMATICA" in nec_raw: pei = "🧮"
                            elif "ALTA PERFORMANCE" in nec_raw: pei = "🚀"
                            elif nec_raw not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: pei = "♿"
                            else: pei = "👤"
                        else:
                            pei = "👤"
                        
                        if faltas_aluno >= (total_dias_letivos * 0.5) and soma == 0: 
                            status = "👻 EVASÃO"
                        elif faltas_aluno > limite_faltas:
                            status = "🚨 REPROV. FALTA"
                        elif trimestres_ativos == 3:
                            if soma >= 18.0: status = "✅ APROVADO"
                            elif rf >= 6.0: status = "🔄 APROV. REC"
                            else: status = "❌ REPROVADO"
                        else:
                            if media_parcial >= 6.0:
                                status = "🟢 NA MÉDIA"
                            elif media_parcial >= 4.5:
                                status = "🟡 RISCO DE NOTA"
                            else:
                                status = "🔴 RISCO CRÍTICO"
                        
                        return pd.Series([pei, soma, media_parcial, status])

                    pivot[['P', 'Σ', 'MÉDIA_PARCIAL', 'SITUAÇÃO']] = pivot.apply(calcular_situacao_anual, axis=1)

                    # KPIs DO TOPO PONDERADOS
                    st.markdown(f"#### 📊 Termômetro do Conselho (Ponderado: {trimestres_ativos} Trimestre(s) Ativo(s))")
                    
                    media_geral_parcial = pivot['MÉDIA_PARCIAL'].mean() if len(pivot) > 0 else 0.0
                    na_media_count = len(pivot[pivot['SITUAÇÃO'].isin(["✅ APROVADO", "🟢 NA MÉDIA", "🔄 APROV. REC"])])
                    taxa_sucesso = (na_media_count / len(pivot)) * 100 if len(pivot) > 0 else 0
                    risco_nota_count = len(pivot[pivot['SITUAÇÃO'].isin(["🟡 RISCO DE NOTA", "🔴 RISCO CRÍTICO"])])
                    risco_faltas_count = len(pivot[pivot['SITUAÇÃO'] == "🚨 REPROV. FALTA"])
                    evasao_count = len(pivot[pivot['SITUAÇÃO'] == "👻 EVASÃO"])

                    with st.container(border=True):
                        k1, k2, k3, k4 = st.columns(4)
                        k1.metric("📊 Média Parcial Turma", f"{media_geral_parcial:.1f}")
                        k2.metric("🟢 Na Média / Aprovados", f"{na_media_count} ({taxa_sucesso:.0f}%)", f"{len(pivot)} alunos")
                        k3.metric("🟡 Risco de Nota", risco_nota_count, delta_color="inverse" if risco_nota_count > 0 else "normal")
                        k4.metric("🚨 Risco de Faltas", risco_faltas_count, delta_color="inverse" if risco_faltas_count > 0 else "normal")

                    st.markdown("---")

                    # FILTROS SEMÂNTICOS DE CONSELHO
                    filtro_conselho = st.pills(
                        "🔍 Filtrar Classe para a Reunião de Conselho:",
                        ["Todos os Estudantes", "🟢 Na Média", "🟡 Risco de Nota", "🚨 Risco de Faltas", "👻 Evasão / Abandono"],
                        default="Todos os Estudantes",
                        key=f"pills_cons_flt_{v}"
                    )

                    pivot_exibir = pivot.copy()
                    if filtro_conselho == "🟢 Na Média":
                        pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'].isin(["✅ APROVADO", "🟢 NA MÉDIA", "🔄 APROV. REC"])]
                    elif filtro_conselho == "🟡 Risco de Nota":
                        pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'].isin(["🟡 RISCO DE NOTA", "🔴 RISCO CRÍTICO"])]
                    elif filtro_conselho == "🚨 Risco de Faltas":
                        pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'] == "🚨 REPROV. FALTA"]
                    elif filtro_conselho == "👻 Evasão / Abandono":
                        pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'] == "👻 EVASÃO"]

                    st.caption(f"Exibindo **{len(pivot_exibir)} de {len(pivot)}** estudantes.")

                    # ESTILIZAÇÃO SEMÂNTICA
                    def style_status_anual(v):
                        if "APROV" in str(v) or "NA MÉDIA" in str(v): return 'color: #2ECC71; font-weight: bold;'
                        if "EVASÃO" in str(v) or "REPROV" in str(v) or "CRÍTICO" in str(v): return 'color: #E74C3C; font-weight: bold;'
                        if "RISCO DE NOTA" in str(v): return 'color: #F1C40F; font-weight: bold;'
                        return 'color: gray;'

                    def formatar_rec(val):
                        if pd.isna(val) or val < 0 or val == 0: return "-"
                        return f"{val:.1f}"

                    def formatar_media(val):
                        if pd.isna(val) or val == 0: return "-"
                        return f"{val:.1f}"

                    st.dataframe(
                        pivot_exibir[['P', 'NOME_ALUNO', 
                               'MEDIA_FINAL_I Trimestre', 'NOTA_REC_I Trimestre',
                               'MEDIA_FINAL_II Trimestre', 'NOTA_REC_II Trimestre',
                               'MEDIA_FINAL_III Trimestre', 'NOTA_REC_III Trimestre',
                               'Σ', 'RF', 'FALTAS', 'SITUAÇÃO']]
                        .style.map(style_status_anual, subset=['SITUAÇÃO'])
                        .format(formatar_media, subset=['MEDIA_FINAL_I Trimestre', 'MEDIA_FINAL_II Trimestre', 'MEDIA_FINAL_III Trimestre'])
                        .format(formatar_rec, subset=['NOTA_REC_I Trimestre', 'NOTA_REC_II Trimestre', 'NOTA_REC_III Trimestre', 'RF']),
                        use_container_width=True, hide_index=True,
                        column_config={
                            "P": st.column_config.TextColumn("P", width="small", help="Perfil do Aluno"),
                            "NOME_ALUNO": st.column_config.TextColumn("Estudante", width="medium"),
                            "MEDIA_FINAL_I Trimestre": st.column_config.TextColumn("I", width="small"),
                            "NOTA_REC_I Trimestre": st.column_config.TextColumn("R1", width="small"),
                            "MEDIA_FINAL_II Trimestre": st.column_config.TextColumn("II", width="small"),
                            "NOTA_REC_II Trimestre": st.column_config.TextColumn("R2", width="small"),
                            "MEDIA_FINAL_III Trimestre": st.column_config.TextColumn("III", width="small"),
                            "NOTA_REC_III Trimestre": st.column_config.TextColumn("R3", width="small"),
                            "Σ": st.column_config.ProgressColumn("Σ (Soma)", help=f"Soma acumulada (Meta parcial: {meta_acumulada_parcial:.1f} pts)", format="%.1f", min_value=0.0, max_value=meta_acumulada_parcial if meta_acumulada_parcial > 0 else 18.0),
                            "RF": st.column_config.TextColumn("RF", width="small", help="Recuperação Final"),
                            "FALTAS": st.column_config.ProgressColumn("Faltas", help=f"Limite máximo: {limite_faltas}", format="%d", min_value=0, max_value=max(limite_faltas, 1)),
                            "SITUAÇÃO": st.column_config.TextColumn("Status", width="medium")
                        }
                    )
                    
                    st.caption(f"📌 **Legenda:** I, II, III (Médias) | R1, R2, R3 (Recuperações) | Σ (Soma Parcial / Meta: **{meta_acumulada_parcial:.1f}** pts) | Limite Faltas: **{limite_faltas}**.")

                    st.markdown("---")
                    
                    # GERADOR DA ATA DOCX
                    if st.button("🖨️ GERAR ATA OFICIAL DO CONSELHO DE CLASSE (DOCX)", type="primary", use_container_width=True, key=f"btn_gen_ata_docx_{v}"):
                        with st.spinner("Compilando documento oficial da Ata..."):
                            dados_ata_export = []
                            for _, r_p in pivot.iterrows():
                                dados_ata_export.append({
                                    "nome": r_p['NOME_ALUNO'],
                                    "soma": f"{r_p['Σ']:.1f}",
                                    "media_parcial": f"{r_p['MÉDIA_PARCIAL']:.1f}",
                                    "faltas": str(r_p['FALTAS']),
                                    "status": r_p['SITUAÇÃO']
                                })
                            
                            info_ata = {"turma": turma_sel, "trimestres_ativos": trimestres_ativos}
                            nome_arq_ata = f"ATA_CONSELHO_{turma_sel.replace(' ', '')}_2026"
                            
                            doc_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_ata, dados_ata_export, info_ata)
                            link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_ata, trimestre="Conselho", categoria=turma_sel, modo="PLANEJAMENTO")
                            
                            if "https" in link_doc:
                                st.success("✅ Ata do Conselho gerada com sucesso!")
                                st.link_button("📂 ABRIR ATA OFICIAL NO DRIVE", link_doc, type="primary", use_container_width=True)
                                st.balloons()
                            else: st.error(f"Erro ao salvar no Drive: {link_doc}")

            renderizar_boletim_anual_fragmento()






# ==============================================================================
# MÓDULO: GESTÃO DA TURMA (COCKPIT DE REGÊNCIA 360°) - V2026.ULTIMATE
# (BARRA DE ALERTAS NO TOPO, CHAMADA EXPRESS, ROLETA COM EQUIDADE E DOCX DA COORDENAÇÃO)
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Cockpit de Regência: Gestão 360°")
    st.caption("Central de comando operacional: alertas de risco no topo, abertura de aula com chamada express, roleta equitativa e relatório para coordenação.")
    st.markdown("---")

    if "v_gestao" not in st.session_state: 
        st.session_state.v_gestao = int(time.time())
    v = st.session_state.v_gestao

    lista_turmas_segura = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_segura = sorted(turmas_reais['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_segura = sorted(df_alunos['TURMA'].unique())

    if not lista_turmas_segura:
        st.warning("⚠️ Nenhuma turma regular cadastrada. Cadastre as turmas na aba Secretaria.")
    else:
        # INTELIGÊNCIA TEMPORAL DE TRIMESTRE COM SELEÇÃO LIVRE
        hoje_dt = date.today()
        if hoje_dt <= date(2026, 5, 22): trim_detectado = "I Trimestre"
        elif hoje_dt <= date(2026, 9, 4): trim_detectado = "II Trimestre"
        else: trim_detectado = "III Trimestre"

        with st.container(border=True):
            c_head1, c_head2 = st.columns([1.5, 2])
            turma_foco = c_head1.selectbox("🎯 Selecione a Turma:", lista_turmas_segura, key=f"foco_t_{v}")
            
            trim_ativo_gestao = c_head2.segmented_control(
                "📅 Navegar Trimestres (I, II, III):",
                ["I Trimestre", "II Trimestre", "III Trimestre"],
                default=trim_detectado,
                key=f"seg_trim_gestao_{v}",
                help="Clique para visualizar ou editar trimestres passados ou futuros!"
            )
            if not trim_ativo_gestao: trim_ativo_gestao = trim_detectado

            # MÉTRICA DE SAFRA
            aulas_dadas_trim = df_registro_aulas[(df_registro_aulas['TURMA'] == turma_foco) & (df_registro_aulas['STATUS_CURRICULO'] != "NÃO LETIVO")]['DATA'].nunique() if not df_registro_aulas.empty else 0
            aulas_meta_trim = 32
            perc_safra = min(100.0, (aulas_dadas_trim / aulas_meta_trim) * 100) if aulas_meta_trim > 0 else 0
            
            st.caption(f"📊 **Safra do {trim_ativo_gestao}:** {aulas_dadas_trim} de {aulas_meta_trim} Aulas Cumpridas ({perc_safra:.0f}%)")

        alunos_t = df_alunos[df_alunos['TURMA'] == turma_foco].sort_values(by="NOME_ALUNO") if not df_alunos.empty else pd.DataFrame()
        ano_num = "".join(filter(str.isdigit, turma_foco))
        ano_str_ref = f"{ano_num}º"

        df_p_atual = df_planos[df_planos['ANO'] == ano_str_ref].copy() if not df_planos.empty else pd.DataFrame()
        df_mats_ano = df_aulas[df_aulas['ANO'].str.contains(ano_num)].iloc[::-1] if not df_aulas.empty else pd.DataFrame()
        historico_turma = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco].copy() if not df_registro_aulas.empty else pd.DataFrame()

        # MELHORIA 1 APROVADA: BARRA DE ALERTAS CRÍTICOS NO TOPO DO COCKPIT
        df_d_foco = df_diario[df_diario['TURMA'] == turma_foco] if not df_diario.empty else pd.DataFrame()
        df_n_foco = df_notas[(df_notas['TURMA'] == turma_foco) & (df_notas['TRIMESTRE'] == trim_ativo_gestao)] if not df_notas.empty else pd.DataFrame()
        
        cnt_uti = 0
        cnt_evasao = 0
        cnt_atestados = 0
        
        if not df_n_foco.empty:
            cnt_uti = len(df_n_foco[df_n_foco['MEDIA_FINAL'].apply(util.sosa_to_float) < 6.0])
            
        if not df_d_foco.empty:
            df_validas_ev = df_d_foco[~df_d_foco['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])]
            tot_dias_ev = df_validas_ev['DATA'].nunique() if not df_validas_ev.empty else 1
            if tot_dias_ev == 0: tot_dias_ev = 1
            
            faltas_por_aluno = df_validas_ev[df_validas_ev['TAGS'] == "AUSÊNCIA"].groupby('NOME_ALUNO').size()
            cnt_evasao = sum(1 for f_c in faltas_por_aluno if (f_c / tot_dias_ev) >= 0.20)

        if not df_relatorios.empty:
            cnt_atestados = len(df_relatorios[(df_relatorios['TIPO'] == 'JUSTIFICATIVA_AUSENCIA') & (df_relatorios['CONTEUDO'].str.contains(turma_foco, na=False))])

        if cnt_uti > 0 or cnt_evasao > 0 or cnt_atestados > 0:
            with st.container(border=True):
                st.markdown("##### 🚨 Painel de Alertas de Risco & Ocorrências da Turma")
                c_al1, c_al2, c_al3 = st.columns(3)
                
                if cnt_evasao > 0: c_al1.error(f"🚨 **{cnt_evasao} Aluno(s)** em Risco de Evasão (>=20% faltas)")
                else: c_al1.success("✅ Nenhum aluno em risco de evasão")

                if cnt_uti > 0: c_al2.warning(f"🚑 **{cnt_uti} Aluno(s)** na UTI Pedagógica (<6.0)")
                else: c_al2.success("✅ Nenhum aluno na UTI de notas")

                if cnt_atestados > 0: c_al3.info(f"📑 **{cnt_atestados} Registro(s)** de Atestados / 2ª Chamada")
                else: c_al3.caption("Nenhum atestado pendente")

        # LEI 25: MODAIS DECLARADOS FORA DE FRAGMENTS
        @st.dialog("🎲 Esquadrão de Arguição (Com Ranking de Equidade)", width="large")
        def dialog_roleta(t_roleta):
            c_rol1, c_rol2, c_rol3 = st.columns([1, 1, 1])
            data_roleta = c_rol1.date_input("📅 Data da Arguição:", date.today(), format="DD/MM/YYYY", key=f"rol_d_{v}")
            data_roleta_str = data_roleta.strftime("%d/%m/%Y")
            qtd_sorteio = c_rol2.number_input("Quantos alunos chamar?", 1, 4, 3, key=f"rol_qtd_{v}")
            
            with c_rol3.expander("⚙️ Configurar Pontuação"):
                pt_acerto = st.number_input("Pontos por Acertar (+):", 0.0, 5.0, 0.5, step=0.1, key=f"pt_ac_{v}")
                pt_recusa = st.number_input("Punição por Recusa (-):", -5.0, 0.0, -0.5, step=0.1, key=f"pt_rec_{v}")

            alunos_roleta = df_alunos[df_alunos['TURMA'] == t_roleta].sort_values(by="NOME_ALUNO").copy()
            if alunos_roleta.empty: st.warning("Nenhum aluno cadastrado."); return
            
            # MELHORIA 4 APROVADA: RANKING DE EQUIDADE NA ROLETA DE ARGUIÇÃO
            freq_arguicao = {}
            if not df_diario.empty:
                df_arg_hist = df_diario[(df_diario['TURMA'] == t_roleta) & (df_diario['TAGS'] == "ARGUIÇÃO")]
                if not df_arg_hist.empty:
                    freq_counts = df_arg_hist.groupby('ID_ALUNO').size().to_dict()
                    for id_al_raw, cnt_f in freq_counts.items():
                        freq_arguicao[db.limpar_id(id_al_raw)] = cnt_f

            def definir_icone_status(nec):
                n = str(nec).upper().strip()
                if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                if "DEFASAGEM LEITURA" in n: return "🧱"
                if "DEFASAGEM MATEMÁTICA" in n: return "🧮"
                if "ALTA PERFORMANCE" in n: return "🚀"
                if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                return "♿"

            alunos_roleta['ICONE'] = alunos_roleta['NECESSIDADES'].apply(definir_icone_status)
            chave_lista = f"lista_roleta_{t_roleta}_{data_roleta_str}"
            chave_sorteados = f"alunos_sorteados_{t_roleta}_{data_roleta_str}"
            
            if chave_lista not in st.session_state:
                diario_dia = df_diario[(df_diario['DATA'] == data_roleta_str) & (df_diario['TURMA'] == t_roleta)] if not df_diario.empty else pd.DataFrame()
                lista_inicial = []
                for _, row in alunos_roleta.iterrows():
                    id_a, nome_a, icone_a = db.limpar_id(row['ID']), row['NOME_ALUNO'], row['ICONE']
                    v_freq = freq_arguicao.get(id_a, 0)
                    
                    status_inicial, obs_inicial, pts_inicial = "⏳ Pendente", "", 0.0
                    
                    if not diario_dia.empty:
                        reg_aluno = diario_dia[diario_dia['ID_ALUNO'].apply(db.limpar_id) == id_a]
                        if not reg_aluno.empty:
                            if any(reg_aluno['TAGS'] == "AUSÊNCIA"):
                                status_inicial, obs_inicial = "⏭️ Faltou", "Ausente no Diário."
                            elif any(reg_aluno['TAGS'] == "ARGUIÇÃO"):
                                reg_arg = reg_aluno[reg_aluno['TAGS'] == "ARGUIÇÃO"].iloc[-1]
                                obs_inicial = reg_arg['OBSERVACOES'].replace("Quadro Negro: ", "")
                                pts_inicial = util.sosa_to_float(reg_arg['BONUS'])
                                if pts_inicial > 0: status_inicial = "✅ Dominou"
                                elif pts_inicial < 0: status_inicial = "❌ Recusou"
                                elif "Isento" in obs_inicial: status_inicial = "♿ Isento"
                                else: status_inicial = "🤝 Tentou"
                    lista_inicial.append({"ID": id_a, "Estudante": f"{icone_a} {nome_a}", "Status": status_inicial, "Diagnóstico": obs_inicial, "Pontos": pts_inicial, "Chamadas": v_freq})
                st.session_state[chave_lista] = lista_inicial
                
            if chave_sorteados not in st.session_state: st.session_state[chave_sorteados] = []

            st.markdown("---")
            pendentes = [a for a in st.session_state[chave_lista] if a["Status"] == "⏳ Pendente"]
            
            c_btn_sort, c_btn_reset = st.columns([2, 1])
            if c_btn_sort.button("🎲 SORTEAR ESQUADRÃO (PRIORIZANDO MENOS CHAMADOS)", type="primary", use_container_width=True, key=f"btn_sort_{v}"):
                if not pendentes: st.success("Todos chamados!")
                else: 
                    # Ordena priorizando alunos com menor número de chamadas prévias
                    pendentes_ordenados = sorted(pendentes, key=lambda x: x["Chamadas"])
                    grupo_candidatos = pendentes_ordenados[:max(qtd_sorteio * 2, len(pendentes_ordenados))]
                    qtd_real = min(qtd_sorteio, len(grupo_candidatos))
                    st.session_state[chave_sorteados] = [p["ID"] for p in random.sample(grupo_candidatos, qtd_real)]
                    st.rerun()
                    
            if c_btn_reset.button("🔄 Resetar Lista", use_container_width=True, key=f"btn_res_rol_{v}"):
                del st.session_state[chave_lista]; st.session_state[chave_sorteados] = []; st.rerun()
                
            if st.session_state[chave_sorteados]:
                st.markdown("#### 🎯 Esquadrão no Quadro")
                cols = st.columns(len(st.session_state[chave_sorteados]))
                
                for idx, id_atual in enumerate(st.session_state[chave_sorteados]):
                    with cols[idx]:
                        aluno_atual = next(a for a in st.session_state[chave_lista] if a["ID"] == id_atual)
                        aluno_db = alunos_roleta[alunos_roleta['ID'].apply(db.limpar_id) == id_atual].iloc[0]
                        
                        with st.container(border=True):
                            st.markdown(f"<h5 style='text-align: center; margin-bottom: 0px;'>{aluno_atual['Estudante']}</h5>", unsafe_allow_html=True)
                            st.caption(f"Perfil: {aluno_db['NECESSIDADES']} | Chamadas no Tri: **{aluno_atual['Chamadas']}**")
                            anotacao = st.text_area("📝 Diagnóstico:", value=aluno_atual["Diagnóstico"], key=f"anotacao_{id_atual}_{v}", height=68)
                            
                            def registrar_arguicao(id_al, status_label, pontos, obs_padrao, anot):
                                obs_final = anot.strip() if anot.strip() else obs_padrao
                                for a in st.session_state[chave_lista]:
                                    if a["ID"] == id_al:
                                        a["Status"], a["Pontos"], a["Diagnóstico"] = status_label, pontos, obs_final
                                        break
                                nome_limpo = aluno_db['NOME_ALUNO'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                                
                                try:
                                    wb = db.conectar()
                                    ws = wb.worksheet("DB_DIARIO_BORDO")
                                    dados = ws.get_all_values()
                                    for i in range(len(dados)-1, 0, -1):
                                        if dados[i][0] == data_roleta_str and db.limpar_id(dados[i][1]) == id_al and dados[i][5] == "ARGUIÇÃO": ws.delete_rows(i+1)
                                    ws.append_row([data_roleta_str, id_al, nome_limpo, t_roleta, "TRUE", "ARGUIÇÃO", f"Quadro Negro: {obs_final}", util.sosa_to_str(pontos)], value_input_option="USER_ENTERED")
                                    st.cache_data.clear()
                                except: pass
                                st.session_state[chave_sorteados].remove(id_al)
                            
                            if st.button(f"✅ Dominou (+{pt_acerto})", key=f"btn_dom_{id_atual}_{v}", use_container_width=True): 
                                registrar_arguicao(id_atual, "✅ Dominou", pt_acerto, "Resolveu corretamente.", anotacao); st.rerun()
                            if st.button("🤝 Tentou (0.0)", key=f"btn_ten_{id_atual}_{v}", use_container_width=True): 
                                registrar_arguicao(id_atual, "🤝 Tentou", 0.0, "Apresentou dificuldades.", anotacao); st.rerun()
                            if st.button(f"❌ Recusou ({pt_recusa})", key=f"btn_rec_{id_atual}_{v}", use_container_width=True): 
                                registrar_arguicao(id_atual, "❌ Recusou", pt_recusa, "Recusou-se a participar.", anotacao); st.rerun()
                            if st.button("⏭️ Pular/Isento", key=f"btn_pul_{id_atual}_{v}", use_container_width=True):
                                for a in st.session_state[chave_lista]:
                                    if a["ID"] == id_atual: a["Status"] = "⏭️ Faltou/Isento"
                                st.session_state[chave_sorteados].remove(id_atual); st.rerun()

            st.markdown("---")
            with st.expander("📋 Ver Lista Completa da Turma & Frequência de Chamadas"):
                st.data_editor(
                    pd.DataFrame(st.session_state[chave_lista]), hide_index=True, use_container_width=True, height=280,
                    column_config={"ID": None, "Estudante": st.column_config.TextColumn(disabled=True), "Status": st.column_config.TextColumn(disabled=True), "Pontos": st.column_config.NumberColumn(disabled=True), "Chamadas": st.column_config.NumberColumn("Vezes Chamado", disabled=True)},
                    key=f"ed_rol_{t_roleta}_{data_roleta_str}_{v}"
                )

        @st.dialog("🛑 Registrar Dia Não Letivo")
        def dialog_dia_nao_letivo(t_foco):
            st.caption("Registre paralisações, feriados ou eventos. Bloqueia chamadas de falta.")
            data_nl = st.date_input("Data do Evento:", date.today(), format="DD/MM/YYYY", key=f"nl_dt_{v}")
            motivo_nl = st.text_input("Motivo:", placeholder="Ex: Paralisação Sindical / Conselho de Classe", key=f"nl_mot_{v}")
            if st.button("Confirmar Dia Não Letivo", type="primary", use_container_width=True, key=f"btn_conf_nl_{v}"):
                if motivo_nl:
                    data_nl_str = data_nl.strftime("%d/%m/%Y")
                    db.limpar_diario_data_turma(data_nl_str, t_foco)
                    db.excluir_aula_aberta(data_nl_str, t_foco)
                    db.salvar_no_banco("DB_DIARIO_BORDO", [data_nl_str, "GLOBAL", "TODOS OS ALUNOS", t_foco, "ISENTO", "DIA NÃO LETIVO", motivo_nl, "0,00"])
                    db.salvar_no_banco("DB_REGISTRO_AULAS", [data_nl_str, "AVULSA", t_foco, f"DIA NÃO LETIVO: {motivo_nl}", "N/A", "N/A", "NÃO LETIVO", "", ""])
                    st.success("Registrado com sucesso!"); time.sleep(1); st.rerun()
                else: st.error("Digite o motivo.")

        tab_cockpit, tab_maquina, tab_inteligencia, tab_secretaria = st.tabs([
            "🚀 1. Cockpit & Abertura (Com Chamada Express)", 
            "🕰️ 2. Máquina do Tempo 2.0 (Edição Total)", 
            "🧠 3. Radiografia & Métricas de Safra", 
            "⚙️ 4. Secretaria, Matrículas & Calendário"
        ])

        # ==============================================================================
        # SUB-ABA 1: COCKPIT DE ABERTURA & CHAMADA EXPRESS (ITEM 2 APROVADO)
        # ==============================================================================
        with tab_cockpit:
            @st.fragment
            def renderizar_cockpit_fragmento():
                total_alunos_turma = len(alunos_t)
                def classificar_macro_perfil(nec):
                    n = str(nec).upper().strip()
                    if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "TIPICO"
                    if "DEFASAGEM" in n: return "DEFASAGEM"
                    if "PENDENTE" in n or "SUSPEITA" in n: return "RADAR"
                    if "ALTA PERFORMANCE" in n: return "ALTA"
                    return "PEI"
                    
                perfis_macro = alunos_t['NECESSIDADES'].apply(classificar_macro_perfil)
                qtd_pei = len(perfis_macro[perfis_macro == "PEI"])
                qtd_defasagem = len(perfis_macro[perfis_macro == "DEFASAGEM"])
                
                with st.container(border=True):
                    c_m1, c_m2, c_m3, c_btn1, c_btn2 = st.columns([1, 1, 1, 1.5, 1.5])
                    c_m1.caption(f"Status: 👥 ALUNOS ({total_alunos_turma})")
                    c_m2.caption(f"Status: ♿ PEI LAUDADO ({qtd_pei})")
                    c_m3.caption(f"Status: 🧱 DEFASAGEM ({qtd_defasagem})")
                    
                    if c_btn1.button("🎲 Roleta de Arguição", use_container_width=True, key=f"btn_open_rol_{v}"): dialog_roleta(turma_foco)
                    if c_btn2.button("🛑 Dia Não Letivo", use_container_width=True, key=f"btn_open_nl_{v}"): dialog_dia_nao_letivo(turma_foco)

                st.markdown("### 🕒 Abertura Inteligente de Aula (Hoje)")
                
                planos_usados = historico_turma['SEMANA'].unique().tolist() if not historico_turma.empty else []
                plano_sugerido = "Nenhum"
                
                if not df_p_atual.empty:
                    df_p_sugestao = df_p_atual[~df_p_atual['SEMANA'].isin(planos_usados)]
                    df_p_sugestao = df_p_sugestao[df_p_sugestao['EIXO'] == 'HUB_ATIVO']
                    if not df_p_sugestao.empty: plano_sugerido = df_p_sugestao.iloc[0]['SEMANA']

                with st.container(border=True):
                    col_ab1, col_ab2 = st.columns(2)
                    
                    with col_ab1:
                        data_aula = st.date_input("Data da Aula:", date.today(), format="DD/MM/YYYY", key=f"dt_reg_{v}")
                        data_aula_str = data_aula.strftime("%d/%m/%Y")
                        aula_existente = historico_turma[historico_turma['DATA'] == data_aula_str] if not historico_turma.empty else pd.DataFrame()
                        
                        if not aula_existente.empty:
                            st.success(f"✅ **Aula já registrada!** Status: {aula_existente.iloc[0].get('STATUS_EXECUCAO', 'Pendente')}")
                        else:
                            if plano_sugerido != "Nenhum": st.info(f"💡 **Sugestão do Sistema:** {plano_sugerido}")
                            else: st.success("✅ Todos os planos ativos já foram aplicados!")

                    with col_ab2:
                        if not aula_existente.empty:
                            st.info(f"📦 **Material Vinculado:**\n{aula_existente.iloc[0]['CONTEUDO_MINISTRADO']}")
                        else:
                            mats_disp_bruto = df_mats_ano['TIPO_MATERIAL'].tolist() if not df_mats_ano.empty else []
                            default_mats = []
                            if plano_sugerido != "Nenhum" and not df_aulas.empty:
                                mats_sugeridos = df_aulas[(df_aulas['ANO'].str.contains(ano_num)) & (df_aulas['SEMANA_REF'] == plano_sugerido)]['TIPO_MATERIAL'].tolist()
                                default_mats = [m for m in mats_sugeridos if m in mats_disp_bruto][:2]
                                
                            mats_sel = st.multiselect("📦 Selecione o Material (Máx 2):", options=mats_disp_bruto, default=default_mats, max_selections=2, key=f"mats_reg_{v}")

                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("💾 CONFIRMAR ABERTURA DE AULA", use_container_width=True, type="primary", key=f"btn_conf_abertura_{v}"):
                                if not mats_sel: st.error("⚠️ Selecione ao menos um material.")
                                else:
                                    mat_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == mats_sel[0]].iloc[0]
                                    db.excluir_aula_aberta(data_aula_str, turma_foco)
                                    db.salvar_no_banco("DB_REGISTRO_AULAS", [data_aula_str, mat_ref['SEMANA_REF'], turma_foco, " + ".join(mats_sel), "PENDENTE", "ABERTA"])
                                    st.success("✅ Aula aberta com sucesso!"); time.sleep(0.5); st.rerun()

                # MELHORIA 2 APROVADA: CHAMADA EXPRESS E VISTOS DIRETO NO COCKPIT
                if not aula_existente.empty:
                    with st.expander("⚡ Chamada Express & Vistos da Aula de Hoje", expanded=True):
                        st.caption(f"Lançamento tátil de presença e vistos para **{data_aula_str}**:")
                        
                        diario_hoje_cockpit = df_diario[(df_diario['DATA'] == data_aula_str) & (df_diario['TURMA'] == turma_foco)] if not df_diario.empty else pd.DataFrame()
                        
                        grid_express = []
                        for _, al_exp in alunos_t.iterrows():
                            id_l_exp = db.limpar_id(al_exp['ID'])
                            reg_exp = diario_hoje_cockpit[diario_hoje_cockpit['ID_ALUNO'].apply(db.limpar_id) == id_l_exp] if not diario_hoje_cockpit.empty else pd.DataFrame()
                            
                            p_exp = True
                            v_exp = False
                            o_exp = ""
                            if not reg_exp.empty:
                                p_exp = False if str(reg_exp.iloc[-1]['TAGS']) == "AUSÊNCIA" else True
                                v_exp = True if str(reg_exp.iloc[-1]['VISTO_ATIVIDADE']).upper() == "TRUE" else False
                                o_exp = str(reg_exp.iloc[-1]['OBSERVACOES']) if str(reg_exp.iloc[-1]['TAGS']) != "AUSÊNCIA" else ""
                                
                            grid_express.append({
                                "ID": id_l_exp, "Estudante": al_exp['NOME_ALUNO'],
                                "Presente?": p_exp, "Visto OK?": v_exp, "Observação": o_exp
                            })

                        df_express_ed = st.data_editor(
                            pd.DataFrame(grid_express), hide_index=True, use_container_width=True, height=280,
                            column_config={
                                "ID": None, "Estudante": st.column_config.TextColumn(disabled=True),
                                "Presente?": st.column_config.CheckboxColumn("Presente?"),
                                "Visto OK?": st.column_config.CheckboxColumn("Visto OK?"),
                                "Observação": st.column_config.TextColumn("Observação Rápida")
                            }, key=f"ed_express_cockpit_{data_aula_str}_{v}"
                        )

                        if st.button("💾 CONSOLIDAR CHAMADA EXPRESS", type="primary", use_container_width=True, key=f"btn_save_express_{v}"):
                            with st.spinner("Gravando no diário de bordo..."):
                                linhas_express_save = []
                                total_vistos_exp = sum(1 for _, r_e in df_express_ed.iterrows() if r_e['Visto OK?'] and r_e['Presente?'])
                                
                                for _, r_e in df_express_ed.iterrows():
                                    id_al_e = r_e['ID']
                                    nome_e = r_e['Estudante']
                                    p_e = r_e['Presente?']
                                    v_e = r_e['Visto OK?']
                                    o_e = str(r_e['Observação']).strip()
                                    
                                    if not p_e:
                                        tag_e = "AUSÊNCIA"
                                        v_e_str = "FALSE"
                                    else:
                                        tag_e = ""
                                        v_e_str = "ISENTO" if total_vistos_exp == 0 else ("TRUE" if v_e else "FALSE")
                                        
                                    linhas_express_save.append([data_aula_str, id_al_e, nome_e, turma_foco, v_e_str, tag_e, o_e, "0,00"])

                                if linhas_express_save:
                                    db.limpar_diario_data_turma(data_aula_str, turma_foco)
                                    db.salvar_lote("DB_DIARIO_BORDO", linhas_express_save)
                                    st.success("✅ Chamada Express consolidada!"); time.sleep(0.5); st.rerun()

                with st.expander("✏️ Auditoria e Edição Rápida de Aulas Passadas", expanded=False):
                    historico_turma_auditoria = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco].copy() if not df_registro_aulas.empty else pd.DataFrame()
                    if not historico_turma_auditoria.empty:
                        historico_turma_auditoria['DATA_DT'] = pd.to_datetime(historico_turma_auditoria['DATA'], format="%d/%m/%Y", errors='coerce')
                        aulas_abertas = historico_turma_auditoria.sort_values(by='DATA_DT', ascending=False).head(10)
                        
                        for i_a, (idx, row_aula) in enumerate(aulas_abertas.iterrows()):
                            with st.container(border=True):
                                st.markdown(f"**{row_aula['DATA']}** - {str(row_aula['CONTEUDO_MINISTRADO'])}")
                                c_aud_1, c_aud_2, c_aud_3 = st.columns([1, 1, 2])
                                novo_status = c_aud_1.selectbox("Status:", ["🟢 Concluído (100%)", "🟡 Parcial (Pendência)", "🔴 Bloqueado (Crítico)", "ABERTA", "NÃO LETIVO"], index=0 if "Concluído" in str(row_aula.get('STATUS_EXECUCAO', '')) else 3, key=f"aud_stat_{i_a}_{v}")
                                opcoes_semanas = ["AVULSA"] + (df_planos[df_planos['ANO'] == ano_str_ref]['SEMANA'].unique().tolist() if not df_planos.empty else [])
                                nova_semana = c_aud_2.selectbox("Semana:", opcoes_semanas, index=opcoes_semanas.index(row_aula['SEMANA']) if row_aula['SEMANA'] in opcoes_semanas else 0, key=f"aud_sem_{i_a}_{v}")
                                mats_atuais = [m.strip() for m in str(row_aula['CONTEUDO_MINISTRADO']).split('+')]
                                novo_mat_sel = c_aud_3.multiselect("Material:", options=df_mats_ano['TIPO_MATERIAL'].tolist() if not df_mats_ano.empty else [], default=[m for m in mats_atuais if not df_mats_ano.empty and m in df_mats_ano['TIPO_MATERIAL'].tolist()], key=f"aud_mat_{i_a}_{v}")
                                
                                c_btn_save, c_btn_del, _ = st.columns([1, 1, 2])
                                if c_btn_save.button("Salvar Alteração", key=f"aud_save_{i_a}_{v}", type="primary"):
                                    novo_conteudo = " + ".join(novo_mat_sel) if novo_mat_sel else "Registro via Diário"
                                    try:
                                        wb = db.conectar()
                                        ws = wb.worksheet("DB_REGISTRO_AULAS")
                                        dados = ws.get_all_values()
                                        for j, row in enumerate(dados):
                                            if j > 0 and len(row) >= 3 and row[0] == row_aula['DATA'] and row[2] == turma_foco:
                                                ws.update_cell(j + 1, 2, nova_semana); ws.update_cell(j + 1, 4, novo_conteudo); ws.update_cell(j + 1, 7, novo_status)
                                                break
                                        st.cache_data.clear(); st.success("Atualizado!"); time.sleep(0.5); st.rerun()
                                    except: pass
                                if c_btn_del.button("Apagar Registro", key=f"aud_del_{i_a}_{v}"):
                                    if db.excluir_aula_aberta(row_aula['DATA'], turma_foco): st.rerun()
                    else: st.info("Nenhuma aula registrada.")

            renderizar_cockpit_fragmento()

        # ==============================================================================
        # SUB-ABA 2: MÁQUINA DO TEMPO 2.0 (RADAR DEDICADO DE FALTOSOS PARA A ESCOLA)
        # ==============================================================================
        with tab_maquina:
            @st.fragment
            def renderizar_maquina_tempo_fragmento():
                st.markdown("### 🕰️ Super Máquina do Tempo 2.0 (Edição Total)")
                st.caption("Inspecione, edite e corrija qualquer aula do passado. Radar de faltosos em cartões de alto contraste para passar para o sistema da escola.")
                
                df_d_maq = df_diario[(df_diario['TURMA'] == turma_foco) & (~df_diario['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"]))] if not df_diario.empty else pd.DataFrame()
                
                if df_d_maq.empty:
                    st.info(f"📭 Nenhum registro de aula encontrado para a turma {turma_foco}.")
                else:
                    datas_disponiveis = sorted(df_d_maq['DATA'].unique(), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)
                    data_maq = st.selectbox("📅 Selecione a Data da Aula para Editar / Lançar Faltas:", datas_disponiveis, key=f"maq_d_{v}")
                    
                    st.markdown("---")
                    df_dia = df_d_maq[df_d_maq['DATA'] == data_maq].copy()
                    df_dia['ID_ALUNO_CLEAN'] = df_dia['ID_ALUNO'].apply(db.limpar_id)
                    
                    aula_info = df_registro_aulas[(df_registro_aulas['DATA'] == data_maq) & (df_registro_aulas['TURMA'] == turma_foco)] if not df_registro_aulas.empty else pd.DataFrame()
                    
                    conteudo_aula = aula_info.iloc[0]['CONTEUDO_MINISTRADO'] if not aula_info.empty else "Registro via Diário Rápido"
                    clima_aula = aula_info.iloc[0]['CLIMA_TURMA'] if not aula_info.empty else "Não registrado"
                    status_aula = aula_info.iloc[0]['STATUS_EXECUCAO'] if not aula_info.empty else "Concluído"
                    
                    total_alunos_turma = len(alunos_t)
                    ids_ausentes = df_dia[df_dia['TAGS'] == "AUSÊNCIA"]['ID_ALUNO_CLEAN'].unique()
                    qtd_ausentes = len(ids_ausentes)
                    qtd_presentes = total_alunos_turma - qtd_ausentes
                    
                    ids_vistos = df_dia[df_dia['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]['ID_ALUNO_CLEAN'].unique()
                    qtd_vistos = len(ids_vistos)
                    
                    df_dia['BONUS_FLOAT'] = df_dia['BONUS'].apply(util.sosa_to_float)
                    df_bonus = df_dia[df_dia['BONUS_FLOAT'] > 0].groupby('NOME_ALUNO')['BONUS_FLOAT'].sum().reset_index()
                    
                    with st.container(border=True):
                        st.markdown("#### ✏️ Edição do Registro da Aula")
                        c_m_edit1, c_m_edit2 = st.columns([2, 1])
                        novo_conteudo_maq = c_m_edit1.text_input("Conteúdo Ministrado:", value=conteudo_aula, key=f"inp_cont_maq_{v}")
                        novo_status_maq = c_m_edit2.selectbox("Status:", ["🟢 Concluído (100%)", "🟡 Parcial", "🔴 Bloqueado", "ABERTA"], index=0 if "Concluído" in status_aula else 1, key=f"sel_stat_maq_{v}")
                        
                        if st.button("💾 Salvar Alteração do Conteúdo", type="primary", key=f"btn_save_cont_maq_{v}"):
                            try:
                                wb = db.conectar()
                                ws_r = wb.worksheet("DB_REGISTRO_AULAS")
                                dados_r = ws_r.get_all_values()
                                for j_r, r_r in enumerate(dados_r):
                                    if j_r > 0 and len(r_r) >= 3 and r_r[0] == data_maq and r_r[2] == turma_foco:
                                        ws_r.update_cell(j_r + 1, 4, novo_conteudo_maq)
                                        ws_r.update_cell(j_r + 1, 7, novo_status_maq)
                                        break
                                st.cache_data.clear(); st.success("✅ Conteúdo atualizado!"); time.sleep(0.5); st.rerun()
                            except Exception as e: st.error(f"Erro: {e}")

                    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
                    c_k1.metric("🟢 Presentes", qtd_presentes)
                    c_k2.metric("🔴 Ausentes (Faltosos)", qtd_ausentes)
                    c_k3.metric("📘 Vistos Dados", qtd_vistos)
                    c_k4.metric("⭐ Alunos Bonificados", len(df_bonus))
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # RADAR DEDICADO DE FALTOSOS
                    with st.container(border=True):
                        st.markdown(f"#### 🔴 Ausentes no Dia {data_maq} ({qtd_ausentes} faltosos de {total_alunos_turma} alunos)")
                        st.caption("ℹ️ Use este bloco no celular para lançar facilmente as faltas no sistema da prefeitura/escola:")
                        
                        if qtd_ausentes == 0:
                            st.success("🎉 **100% DE PRESENÇA NESTA AULA!** Nenhum aluno faltou.")
                        else:
                            alunos_faltosos_df = alunos_t[alunos_t['ID'].apply(db.limpar_id).isin(ids_ausentes)]
                            
                            for idx_f, (_, r_faltoso) in enumerate(alunos_faltosos_df.iterrows()):
                                id_f_al = db.limpar_id(r_faltoso['ID'])
                                nome_f_al = r_faltoso['NOME_ALUNO']
                                
                                with st.container(border=True):
                                    c_m_f1, c_m_f2 = st.columns([2.5, 1])
                                    c_m_f1.markdown(f"**🔴 {nome_f_al}**")
                                    c_m_f1.caption(f"ID: {id_f_al} | Perfil: {r_faltoso['NECESSIDADES']}")
                                    
                                    if c_m_f2.button("🟢 Dar Presença", key=f"btn_pres_fal_{id_f_al}_{data_maq}_{v}", use_container_width=True):
                                        db.salvar_no_banco("DB_DIARIO_BORDO", [
                                            data_maq, id_f_al, nome_f_al, turma_foco, "TRUE", "", "[PRESENÇA RETIFICADA]", "0,00"
                                        ])
                                        st.toast(f"Presença atribuída a {nome_f_al}!")
                                        st.cache_data.clear(); time.sleep(0.5); st.rerun()

                            lista_nomes_faltantes = [f"• {r['NOME_ALUNO']}" for _, r in alunos_faltosos_df.iterrows()]
                            texto_copia_faltas = f"📌 FALTAS - {turma_foco} - AULA DO DIA {data_maq}:\n" + "\n".join(lista_nomes_faltantes)
                            
                            with st.expander("📋 Ver Lista de Faltas Formatada para Copiar / WhatsApp"):
                                st.code(texto_copia_faltas, language=None)

                    st.markdown("---")

                    st.markdown("#### 📱 Edição Tátil Completa da Chamada desta Aula")
                    st.caption("Ajuste presenças, vistos ou atestados referentes a este dia no passado:")
                    
                    grid_maq_dados = []
                    for _, alu_m in alunos_t.iterrows():
                        id_l_m = db.limpar_id(alu_m['ID'])
                        reg_m = df_dia[df_dia['ID_ALUNO_CLEAN'] == id_l_m]
                        
                        is_p_m = True if id_l_m not in ids_ausentes else False
                        is_v_m = True if id_l_m in ids_vistos else False
                        tag_m = str(reg_m.iloc[-1]['TAGS']) if not reg_m.empty else ""
                        obs_m = str(reg_m.iloc[-1]['OBSERVACOES']) if not reg_m.empty else ""
                        
                        grid_maq_dados.append({
                            "ID": id_l_m, "Estudante": alu_m['NOME_ALUNO'],
                            "Presente?": is_p_m, "Visto OK?": is_v_m,
                            "Ocorrência": tag_m if tag_m != "AUSÊNCIA" else "", "Observação": obs_m
                        })

                    df_maq_ed = st.data_editor(
                        pd.DataFrame(grid_maq_dados), hide_index=True, use_container_width=True, height=350,
                        column_config={
                            "ID": None, "Estudante": st.column_config.TextColumn(disabled=True),
                            "Presente?": st.column_config.CheckboxColumn("Presente?"),
                            "Visto OK?": st.column_config.CheckboxColumn("Visto OK?"),
                            "Ocorrência": st.column_config.SelectboxColumn("Ocorrência", options=["", "ARGUIÇÃO", "INDISCIPLINA", "CELULAR", "CONVERSA", "ATRASO"]),
                            "Observação": st.column_config.TextColumn("Observação")
                        }, key=f"ed_grid_maq_{data_maq}_{v}"
                    )

                    if st.button("💾 GRAVAR CORREÇÕES DESTA AULA NO BANCO", type="primary", use_container_width=True, key=f"btn_save_maq_grid_{v}"):
                        with st.spinner("Reescrevendo diário da aula no banco (UPSERT)..."):
                            linhas_maq_save = []
                            for _, r_m in df_maq_ed.iterrows():
                                al_id_m = r_m['ID']
                                nome_m = r_m['Estudante']
                                p_m = r_m['Presente?']
                                v_m = "TRUE" if r_m['Visto OK?'] else "FALSE"
                                t_m = str(r_m['Ocorrência']).strip()
                                o_m = str(r_m['Observação']).strip()
                                
                                if not p_m:
                                    t_m = "AUSÊNCIA"
                                    v_m = "FALSE"
                                    
                                linhas_maq_save.append([data_maq, al_id_m, nome_m, turma_foco, v_m, t_m, o_m, "0,00"])

                            if linhas_maq_save:
                                db.limpar_diario_data_turma(data_maq, turma_foco)
                                db.salvar_lote("DB_DIARIO_BORDO", linhas_maq_save)
                                st.success("✅ Chamada do passado corrigida com sucesso!")
                                st.cache_data.clear(); time.sleep(1); st.rerun()

            renderizar_maquina_tempo_fragmento()

        # ==============================================================================
        # SUB-ABA 3: RADIOGRAFIA, MÉTRICAS DE SAFRA & FICHA DA COORDENAÇÃO (DOCX)
        # ==============================================================================
        with tab_inteligencia:
            @st.fragment
            def renderizar_radiografia_fragmento():
                st.markdown("### 🧠 Radiografia Cognitiva & Saúde da Turma")
                
                df_d_rad = df_diario[df_diario['TURMA'] == turma_foco].copy() if not df_diario.empty else pd.DataFrame()
                df_diag_rad = df_diagnosticos[df_diagnosticos['TURMA'] == turma_foco].copy() if not df_diagnosticos.empty else pd.DataFrame()
                df_notas_rad = df_notas[(df_notas['TURMA'] == turma_foco) & (df_notas['TRIMESTRE'] == trim_ativo_gestao)].copy() if not df_notas.empty else pd.DataFrame()

                taxa_assiduidade, taxa_engajamento, media_geral_av = 0.0, 0.0, 0.0
                if not df_d_rad.empty:
                    df_d_rad_validas = df_d_rad[~df_d_rad['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])]
                    total_registros = len(df_d_rad_validas)
                    faltas = len(df_d_rad_validas[df_d_rad_validas['TAGS'] == "AUSÊNCIA"])
                    taxa_assiduidade = ((total_registros - faltas) / total_registros) * 100 if total_registros > 0 else 0
                    
                    df_vistos = df_d_rad_validas[df_d_rad_validas['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                    vistos_possiveis = len(df_vistos)
                    vistos_dados = len(df_vistos[df_vistos['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    taxa_engajamento = (vistos_dados / vistos_possiveis) * 100 if vistos_possiveis > 0 else 0
                
                if not df_diag_rad.empty: media_geral_av = df_diag_rad['NOTA_CALCULADA'].apply(util.sosa_to_float).mean()
                
                with st.container(border=True):
                    c_k1, c_k2, c_k3 = st.columns(3)
                    c_k1.metric("📅 Assiduidade da Classe", f"{taxa_assiduidade:.1f}%")
                    c_k2.metric("📓 Engajamento de Caderno", f"{taxa_engajamento:.1f}%")
                    c_k3.metric("📈 Média das Provas (Scanner)", f"{media_geral_av:.1f}")

                # MELHORIA 5 APROVADA: EXPORTADOR DA FICHA DA TURMA PARA A COORDENAÇÃO (DOCX)
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🖨️ EXPORTAR FICHA DA TURMA PARA A COORDENAÇÃO (DOCX A4)", type="primary", use_container_width=True, key=f"btn_exp_coord_{v}"):
                    with st.spinner("Compilando Ficha de Regência da Turma para a Coordenação Pedagógica..."):
                        dados_export_coord = []
                        for _, al_c in alunos_t.iterrows():
                            id_al_c = db.limpar_id(al_c['ID'])
                            reg_n = df_notas_rad[df_notas_rad['ID_ALUNO'].apply(db.limpar_id) == id_al_c] if not df_notas_rad.empty else pd.DataFrame()
                            m_final_c = util.sosa_to_float(reg_n.iloc[0]['MEDIA_FINAL']) if not reg_n.empty else 0.0
                            
                            faltas_al = 0
                            if not df_d_rad.empty:
                                d_al_sub = df_d_rad[df_d_rad['ID_ALUNO'].apply(db.limpar_id) == id_al_c]
                                faltas_al = len(d_al_sub[d_al_sub['TAGS'] == "AUSÊNCIA"])
                                
                            status_c = "✅ NA MÉDIA" if m_final_c >= 6.0 else "⚠️ RECOMPOSIÇÃO"
                            if faltas_al >= 10: status_c += " / 🚨 RISCO FALTAS"
                            
                            dados_export_coord.append({
                                "nome": al_c['NOME_ALUNO'],
                                "vistos": f"{taxa_engajamento:.0f}%",
                                "teste": "Sincronizado",
                                "prova": "Sincronizado",
                                "bonus": "0.0",
                                "media": f"{m_final_c:.1f}",
                                "status": status_c
                            })
                            
                        info_coord = {"turma": turma_foco, "trimestre": trim_ativo_gestao}
                        nome_arq_coord = f"RELATORIO_REGENCIA_{turma_foco.replace(' ','_')}_{trim_ativo_gestao.replace(' ','')}"
                        
                        doc_coord_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_coord, dados_export_coord, info_coord)
                        link_coord_doc = db.subir_e_converter_para_google_docs(doc_coord_stream, nome_arq_coord, trimestre=trim_ativo_gestao, categoria=turma_foco, modo="PLANEJAMENTO")
                        
                        if "https" in link_coord_doc:
                            st.success("✅ Ficha de Regência gerada para a Coordenação!")
                            st.link_button("📂 ABRIR RELATÓRIO DA COORDENAÇÃO NO DRIVE", link_coord_doc, type="primary", use_container_width=True)
                            st.balloons()

                st.markdown("---")
                if not df_d_rad.empty:
                    df_d_rad['DATA_DT'] = pd.to_datetime(df_d_rad['DATA'], format="%d/%m/%Y", errors='coerce')
                    df_d_clean = df_d_rad[~df_d_rad['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])].dropna(subset=['DATA_DT'])
                    
                    if not df_d_clean.empty:
                        daily_pres = df_d_clean.groupby('DATA_DT').apply(lambda g: (len(g[g['TAGS'] != "AUSÊNCIA"]) / len(g)) * 100 if len(g)>0 else 100).reset_index(name="Presença %")
                        daily_pres = daily_pres.sort_values(by="DATA_DT")
                        
                        fig_pres = px.line(daily_pres, x="DATA_DT", y="Presença %", title="Evolução Diária de Assiduidade da Turma", markers=True)
                        fig_pres.update_traces(line=dict(color="#2962FF", width=3), marker=dict(size=8))
                        fig_pres.update_layout(yaxis_range=[0, 105], height=280, margin=dict(l=20, r=20, t=30, b=20))
                        st.plotly_chart(fig_pres, use_container_width=True)

                col_uti, col_evasao = st.columns(2)
                
                with col_uti:
                    st.markdown("#### 🚑 UTI Pedagógica (Notas)")
                    if not df_notas_rad.empty:
                        alunos_uti = []
                        for _, r in df_notas_rad.iterrows():
                            media_f = util.sosa_to_float(r['MEDIA_FINAL'])
                            if media_f < 6.0: alunos_uti.append({"Estudante": r['NOME_ALUNO'], "Média": media_f, "Falta": 6.0 - media_f})
                        
                        if alunos_uti:
                            df_uti = pd.DataFrame(alunos_uti).sort_values(by="Média")
                            st.dataframe(
                                df_uti, hide_index=True, use_container_width=True, height=220,
                                column_config={
                                    "Estudante": st.column_config.TextColumn(width="medium"),
                                    "Média": st.column_config.NumberColumn(format="%.1f"),
                                    "Falta": st.column_config.ProgressColumn("Precisa de", format="%.1f", min_value=0.0, max_value=6.0)
                                }
                            )
                        else: st.success("🎉 Nenhum aluno em recuperação!")
                    else: st.info("Aguardando consolidação de notas.")

                with col_evasao:
                    st.markdown("#### 🚨 Radar de Evasão (Faltas)")
                    if not df_d_rad.empty:
                        dias_nao_letivos = df_d_rad[df_d_rad['TAGS'] == "DIA NÃO LETIVO"]['DATA'].unique()
                        df_d_clean_ev = df_d_rad[df_d_rad['ID_ALUNO'] != "GLOBAL"].drop_duplicates(subset=['DATA', 'ID_ALUNO'], keep='last')
                        datas_aulas_ev = sorted(df_d_clean_ev['DATA_DT'].unique())
                        total_aulas_validas = len([d for d in [dt.strftime("%d/%m/%Y") for dt in datas_aulas_ev if pd.notna(dt)] if d not in dias_nao_letivos])
                        
                        stats_evasao = []
                        for aluno in alunos_t['NOME_ALUNO'].tolist():
                            df_aluno = df_d_clean_ev[(df_d_clean_ev['NOME_ALUNO'] == aluno) & (~df_d_clean_ev['DATA'].isin(dias_nao_letivos))]
                            faltas_a = len(df_aluno[df_aluno['TAGS'] == 'AUSÊNCIA'])
                            perc_falta = (faltas_a / total_aulas_validas) * 100 if total_aulas_validas > 0 else 0
                            if perc_falta >= 20: stats_evasao.append({"Estudante": aluno, "Faltas": faltas_a, "Ausência": perc_falta})
                                
                        if stats_evasao:
                            df_evasao = pd.DataFrame(stats_evasao).sort_values(by="Ausência", ascending=False)
                            st.dataframe(
                                df_evasao, hide_index=True, use_container_width=True, height=220,
                                column_config={
                                    "Estudante": st.column_config.TextColumn(width="medium"),
                                    "Faltas": st.column_config.NumberColumn(),
                                    "Ausência": st.column_config.ProgressColumn("% Ausência", format="%.0f%%", min_value=0, max_value=100)
                                }
                            )
                        else: st.success("✅ Nenhum aluno em risco de evasão.")
                    else: st.info("Aguardando registros de chamada.")

            renderizar_radiografia_fragmento()

        # ==============================================================================
        # SUB-ABA 4: SECRETARIA, MATRÍCULAS & CALENDÁRIO
        # ==============================================================================
        with tab_secretaria:
            st.markdown("### ⚙️ Secretaria, Matrículas & Calendário")
            
            modo_sec = st.segmented_control(
                "Selecione a Operação:", 
                ["🏗️ Criar Turmas/Horários", "➕ Povoar Alunos", "✏️ Edição em Cascata", "📅 Gestor de Semanas & Recessos"],
                default="🏗️ Criar Turmas/Horários",
                key=f"seg_sec_{v}"
            )
            st.markdown("---")

            if modo_sec == "🏗️ Criar Turmas/Horários":
                tipo_cadastro = st.pills(
                    "O que deseja alocar na grade?", 
                    ["📚 Turma Regular (Alunos)", "⚙️ Planejamento (PI / PC)"], 
                    default="📚 Turma Regular (Alunos)",
                    key=f"pills_tipo_cad_{v}"
                )
                with st.container(border=True):
                    if "Regular" in tipo_cadastro:
                        c1, c2, c3 = st.columns(3)
                        ano_t = c1.selectbox("Série/Ano:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key=f"ano_cad_{v}")
                        letra_t = c2.selectbox("Letra:", ["A", "B", "C", "D", "E", "F", "G"], key=f"letra_cad_{v}")
                        turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"], key=f"turno_cad_{v}")
                        sigla_final, nome_final = f"{ano_t}ª {turno_t[0].upper()}{letra_t}", f"{ano_t}º Ano {letra_t}"
                    else:
                        c1, c2, c3 = st.columns([1, 2, 1])
                        sigla_plan = c1.selectbox("Sigla:", ["PI", "PC", "AC", "HTPC", "OUTRO"], key=f"sigla_plan_{v}")
                        desc_plan = c2.text_input("Descrição:", placeholder="Ex: Planejamento Individual", key=f"desc_plan_{v}")
                        turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"], key=f"turno_plan_{v}")
                        sigla_final, nome_final = sigla_plan, desc_plan if desc_plan else "Planejamento"

                dias_aula = st.multiselect("Selecione a grade de horários:", ["Segunda (1º Tempo)", "Segunda (2º Tempo)", "Terça (1º Tempo)", "Terça (2º Tempo)", "Quarta (1º Tempo)", "Quarta (2º Tempo)", "Quinta (1º Tempo)", "Quinta (2º Tempo)", "Sexta (1º Tempo)", "Sexta (2º Tempo)"], key=f"dias_cad_{v}")
                if st.button("💾 ALOCAR NA GRADE OFICIAL", use_container_width=True, type="primary", key=f"btn_save_turma_{v}"):
                    if not dias_aula: st.error("Selecione pelo menos um horário.")
                    else:
                        if db.salvar_no_banco("DB_TURMAS", [sigla_final, nome_final, turno_t, " / ".join(dias_aula), "N/A", "ATIVO"]):
                            st.success(f"✅ {sigla_final} alocado com sucesso!"); time.sleep(1); st.rerun()

            elif modo_sec == "➕ Povoar Alunos":
                if not lista_turmas_segura: st.warning("Cadastre uma turma primeiro.")
                else:
                    t_dest = st.selectbox("Turma de Destino:", lista_turmas_segura, key=f"dest_pov_{v}")
                    if t_dest:
                        t1_man, t2_lote = st.tabs(["✍️ Cadastro Manual", "📄 Importação em Lote (CSV)"])
                        with t1_man:
                            with st.form("f_manual_povoar"):
                                nome_a = st.text_input("Nome Completo:").upper()
                                perfil_base = st.multiselect("Perfil / Necessidades:", ["TÍPICO", "TEA", "TDAH", "DISLEXIA", "DEF. INTELECTUAL", "TOD", "BAIXA VISÃO", "SURDEZ", "PEI - PENDENTE", "OUTRO"], default=["TÍPICO"])
                                if st.form_submit_button("💾 SALVAR ALUNO"):
                                    if not nome_a: st.error("Digite o nome do aluno.")
                                    else:
                                        if "TÍPICO" in perfil_base and len(perfil_base) > 1: perfil_base.remove("TÍPICO")
                                        perfil_str = " + ".join(perfil_base) if perfil_base else "TÍPICO"
                                        if db.salvar_no_banco("DB_ALUNOS", [db.gerar_proximo_id(df_alunos), nome_a, t_dest, "ATIVO", perfil_str, "MANUAL"]):
                                            st.success(f"✅ {nome_a} cadastrado!"); st.rerun()
                        with t2_lote:
                            st.info("💡 Cole a lista de alunos. Se o aluno tiver um asterisco (*) no final do nome, o sistema detectará automaticamente como PEI.")
                            texto_lote = st.text_area("Cole os dados CSV aqui (NOME, PERFIL):", height=200, placeholder="ADRIEL VINICIUS ALVES MARTINS,TÍPICO\nJOSE LEVI BRONZE SANTOS*,PEI - PENDENTE", key=f"txt_lote_{v}")
                            if st.button("🚀 PROCESSAR IMPORTAÇÃO EM LOTE", type="primary", use_container_width=True, key=f"btn_lote_alu_{v}"):
                                if texto_lote.strip():
                                    linhas = texto_lote.strip().split('\n')
                                    novos_alunos = []
                                    id_atual = db.gerar_proximo_id(df_alunos)
                                    with st.status("Importando alunos...") as status:
                                        for linha in linhas:
                                            if not linha.strip(): continue
                                            partes = linha.split(',')
                                            nome_bruto = partes[0].strip().upper()
                                            if "*" in nome_bruto: nome_limpo, perfil = nome_bruto.replace("*", "").strip(), "PEI - PENDENTE"
                                            else: nome_limpo, perfil = nome_bruto, partes[1].strip().upper() if len(partes) > 1 else "TÍPICO"
                                            novos_alunos.append([id_atual, nome_limpo, t_dest, "ATIVO", perfil, "LOTE"])
                                            id_atual += 1 
                                        if db.salvar_lote("DB_ALUNOS", novos_alunos):
                                            status.update(label=f"✅ {len(novos_alunos)} alunos importados!", state="complete")
                                            st.balloons(); time.sleep(1); st.rerun()

            elif modo_sec == "✏️ Edição em Cascata":
                t_origem = st.selectbox("Selecione a Turma Atual:", [""] + sorted(df_alunos['TURMA'].unique().tolist()) if not df_alunos.empty else [""], key=f"orig_ed_{v}")
                if t_origem:
                    alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO")
                    aluno_sel_nome = st.selectbox("Selecione o Aluno:", alunos_opcoes['NOME_ALUNO'].tolist(), key=f"alu_ed_{v}")
                    dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
                    
                    st.markdown("#### ⚡ Diagnóstico Rápido (1-Click)")
                    c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
                    if c_btn1.button("📚 Defasagem Leitura", use_container_width=True, key=f"btn_diag_dl_{v}"):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "DEFASAGEM LEITURA"); st.rerun()
                    if c_btn2.button("🧮 Defasagem Matemática", use_container_width=True, key=f"btn_diag_dm_{v}"):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "DEFASAGEM MATEMÁTICA"); st.rerun()
                    if c_btn3.button("🚀 Alta Performance", use_container_width=True, key=f"btn_diag_ap_{v}"):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "ALTA PERFORMANCE"); st.rerun()
                    if c_btn4.button("👤 Típico (Limpar)", use_container_width=True, key=f"btn_diag_tip_{v}"):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "TÍPICO"); st.rerun()
                    
                    st.markdown("---")
                    with st.form("form_edicao"):
                        novo_nome = st.text_input("Nome Completo:", value=dados_atuais['NOME_ALUNO']).upper()
                        nova_turma = st.selectbox("Turma de Destino (Transferência):", lista_turmas_segura, index=lista_turmas_segura.index(t_origem) if t_origem in lista_turmas_segura else 0)
                        nova_nec = st.text_input("Necessidades / CIDs / PEI:", value=dados_atuais['NECESSIDADES']).upper()
                        
                        # CAMPO NOVO: STATUS DO ALUNO
                        status_opcoes = ["ATIVO", "TRANSFERIDO", "EVADIDO", "INATIVO"]
                        status_atual_val = str(dados_atuais.get('STATUS', 'ATIVO')).upper()
                        idx_status = status_opcoes.index(status_atual_val) if status_atual_val in status_opcoes else 0
                        novo_status = st.selectbox("Status Regimental do Estudante:", status_opcoes, index=idx_status)

                        if st.form_submit_button("💾 SALVAR E ATUALIZAR HISTÓRICO EM CASCATA"):
                            with st.spinner("Atualizando cadastro e histórico do aluno..."):
                                # Atualiza status no banco
                                try:
                                    wb = db.conectar()
                                    ws = wb.worksheet("DB_ALUNOS")
                                    cell = ws.find(str(dados_atuais['ID']))
                                    if cell:
                                        ws.update_cell(cell.row, 4, novo_status) # Coluna STATUS
                                except: pass

                                if db.atualizar_aluno_cascata(dados_atuais['ID'], novo_nome, nova_turma, nova_nec):
                                    st.success("✅ Cadastro e Status atualizados!"); time.sleep(1); st.rerun()

            elif modo_sec == "📅 Gestor de Semanas & Recessos":
                st.markdown("#### 📅 Configuração Dinâmica de Semanas & Recessos")
                c_cal1, c_cal2 = st.columns([2, 1])
                
                todas_semanas_cal = util.gerar_semanas()
                semana_alvo_cal = c_cal1.selectbox("Selecione a Semana:", todas_semanas_cal, key=f"cal_sem_sel_{v}")
                status_semana_cal = c_cal2.selectbox("Status da Semana:", [
                    "🟢 Semana Letiva Normal",
                    "🏖️ RECESSO ESCOLAR",
                    "🎉 FERIADO PROLONGADO",
                    "📑 SEMANA DE PROVAS OFICIAIS",
                    "🤝 JORNADA PEDAGÓGICA / PLANEJAMENTO"
                ], key=f"cal_stat_sel_{v}")
                
                motivo_semana_cal = st.text_input("Descrição / Observação:", placeholder="Ex: Recesso Junino / Semana de Provas Globais", key=f"cal_mot_{v}")
                
                if st.button("💾 GRAVAR STATUS DA SEMANA NO CALENDÁRIO", type="primary", use_container_width=True, key=f"btn_save_cal_{v}"):
                    with st.spinner("Atualizando calendário de semanas..."):
                        sem_limpa_cal = semana_alvo_cal.split(" (")[0].strip()
                        db.excluir_registro("DB_RELATORIOS", f"CONFIG_SEMANA_{sem_limpa_cal}")
                        
                        status_txt_save = f"CONFIG_SEMANA_{sem_limpa_cal}"
                        conteudo_cal = f"{status_semana_cal}|{motivo_semana_cal}"
                        
                        db.salvar_no_banco("DB_RELATORIOS", [
                            datetime.now().strftime("%d/%m/%Y"), 
                            "GLOBAL", 
                            "SISTEMA", 
                            status_txt_save, 
                            conteudo_cal
                        ])
                        st.success(f"✅ {sem_limpa_cal} configurada como '{status_semana_cal}'!")
                        st.cache_data.clear(); time.sleep(1); st.rerun()

                st.markdown("---")
                st.markdown("##### 📌 Semanas com Status Especial Cadastradas")
                config_semanas = df_relatorios[df_relatorios['TIPO'].str.startswith('CONFIG_SEMANA_', na=False)] if not df_relatorios.empty else pd.DataFrame()
                
                if config_semanas.empty:
                    st.info("Nenhuma semana com status especial cadastrada.")
                else:
                    for _, r_c in config_semanas.iterrows():
                        sem_nome = r_c['TIPO'].replace("CONFIG_SEMANA_", "")
                        partes_c = str(r_c['CONTEUDO']).split('|')
                        stat_c = partes_c[0]
                        obs_c = partes_c[1] if len(partes_c) > 1 else ""
                        
                        with st.container(border=True):
                            c_s1, c_s2, c_s3 = st.columns([2, 2, 1])
                            c_s1.markdown(f"**{sem_nome}**")
                            c_s2.markdown(f"**Status:** {stat_c} " + (f"(*{obs_c}*)" if obs_c else ""))
                            if c_s3.button("🗑️ Remover", key=f"del_cal_{r_c.name}_{v}"):
                                db.excluir_registro("DB_RELATORIOS", r_c['TIPO'])
                                st.success("Status removido!"); time.sleep(0.5); st.rerun()








elif menu == "📚 Base de Conhecimento":
    st.title("📚 Biblioteca Digital de Soberania (Cofre Digital)")
    st.caption("Repositório central de livros didáticos, referenciais curriculares e diretrizes PEI sincronizados no Google Drive.")
    st.markdown("---")
    
    # 🚨 INICIALIZAÇÃO SEGURA DA VARIÁVEL V
    if "v_bib" not in st.session_state: 
        st.session_state.v_bib = int(time.time())
    v = st.session_state.v_bib

    tab_upload, tab_acervo_lib = st.tabs(["📤 Novo Upload (Drive)", "📖 Acervo Permanente"])
    
    with tab_upload:
        with st.form("form_upload_drive", clear_on_submit=True):
            st.markdown("#### 📤 Armazenar Material no Cofre Digital")
            c1, c2 = st.columns(2)
            tipo_doc = c1.selectbox("Categoria:", ["Livro Didático", "Referencial Curricular", "Documento PEI", "Outros"], key=f"up_cat_{v}")
            ano_doc = c2.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "Geral"], key=f"up_ano_{v}")
            
            nome_arq = st.text_input("Nome de Exibição do Material:", placeholder="Ex: Livro A Conquista da Matemática 6º Ano", key=f"up_nome_{v}")
            uploaded_file = st.file_uploader("Selecione o arquivo PDF:", type=["pdf"], key=f"up_pdf_{v}")
            
            if st.form_submit_button("🚀 SALVAR NO GOOGLE DRIVE"):
                if uploaded_file and nome_arq:
                    with st.spinner("Enviando para o seu Cofre Digital via SOSA Bridge..."):
                        link_drive = db.subir_e_converter_para_google_docs(
                            uploaded_file, 
                            nome_arq, 
                            categoria=ano_doc, 
                            modo="BIBLIOTECA"
                        )
                        
                        if "http" in link_drive:
                            db.salvar_no_banco("DB_MATERIAIS", [
                                datetime.now().strftime("%d/%m/%Y"), 
                                nome_arq, 
                                link_drive, 
                                f"{tipo_doc} - {ano_doc}"
                            ])
                            st.success(f"✅ '{nome_arq}' guardado com segurança no Drive!")
                            st.balloons(); time.sleep(1); st.rerun()
                        else:
                            st.error(f"Erro no upload: {link_drive}")
                else:
                    st.warning("Preencha o nome do material e selecione o arquivo PDF.")

    with tab_acervo_lib:
        # 🚨 ACERVO DA BIBLIOTECA ISOLADO EM FRAGMENTO (FILTRAGEM RÁPIDA)
        @st.fragment
        def renderizar_acervo_biblioteca_fragmento():
            st.markdown("#### 📖 Acervo de Obras Guardadas")
            
            if not df_materiais.empty:
                # 🚨 UI NOVA GERAÇÃO: ST.PILLS PARA FILTRO DE CATEGORIAS
                filtro_cat_lib = st.pills(
                    "Filtrar por Categoria:", 
                    ["Todos", "Livro Didático", "Referencial Curricular", "Documento PEI", "Outros"], 
                    default="Todos",
                    key=f"pills_lib_cat_{v}"
                )
                
                df_lib_filtrado = df_materiais.copy()
                if filtro_cat_lib != "Todos":
                    df_lib_filtrado = df_lib_filtrado[df_lib_filtrado['TIPO'].str.contains(filtro_cat_lib, case=False, na=False)]
                
                st.caption(f"**{len(df_lib_filtrado)} de {len(df_materiais)}** obras exibidas no Cofre Digital.")
                st.markdown("---")
                
                if df_lib_filtrado.empty:
                    st.info("Nenhum material encontrado para a categoria selecionada.")
                else:
                    for _, row in df_lib_filtrado.iloc[::-1].iterrows():
                        with st.container(border=True):
                            c_icon, c_txt, c_btn1, c_btn2 = st.columns([0.5, 2.5, 1, 1])
                            c_icon.markdown("# 📕")
                            
                            nome_m = row['NOME_ARQUIVO']
                            tipo_m = str(row['TIPO'])
                            
                            c_txt.markdown(f"**{nome_m}**")
                            c_txt.caption(f"📅 Upload: {row.get('DATA_UPLOAD', 'N/A')} | Categoria: {tipo_m}")
                            
                            c_btn1.link_button("👁️ Ver no Drive", row['URI_ARQUIVO'], use_container_width=True)
                            
                            if c_btn2.button("🗑️ Apagar", key=f"del_mat_{row.name}_{v}", use_container_width=True):
                                if db.excluir_registro_com_drive("DB_MATERIAIS", nome_m):
                                    st.success("Material removido!"); time.sleep(0.5); st.rerun()
            else:
                st.info("📭 Sua biblioteca está vazia. Faça o upload de livros didáticos no formulário ao lado.")

        renderizar_acervo_biblioteca_fragmento()




# ==============================================================================
# MÓDULO: CENTRO DE COMANDO DA INCLUSÃO (RELATÓRIOS PEI / PERFIL IA)
# (V2026.ULTIMATE - LÓGICA INVERSA UNIVERSAL & REGEX CID-10: BLINDAGEM PERMANENTE)
# ==============================================================================
elif menu == "♿ Relatórios PEI / Perfil IA":
    st.title("🧠 Centro de Comando da Inclusão (PEI / Perfil IA)")
    st.caption("Gestão de suporte clínico, triagem de provas adaptadas x regulares, pareceres descritivos trimestrais e matriz curricular.")
    st.markdown("---")

    if "v_pei" not in st.session_state: 
        st.session_state.v_pei = int(time.time())
    v = st.session_state.v_pei

    # FUNÇÃO DE SALVAMENTO SEM DUPLICIDADE POR TRIMESTRE
    def salvar_relatorio_pei_sem_duplicidade(id_aluno, nome_aluno, tipo_rel, conteudo_rel):
        try:
            wb = db.conectar()
            ws = wb.worksheet("DB_RELATORIOS")
            dados = ws.get_all_values()
            for i in range(len(dados)-1, 0, -1):
                if len(dados[i]) > 3 and db.limpar_id(dados[i][1]) == str(id_aluno) and dados[i][3] == tipo_rel:
                    ws.delete_rows(i+1)
            ws.append_row([datetime.now().strftime("%d/%m/%Y"), id_aluno, nome_aluno, tipo_rel, conteudo_rel], value_input_option="USER_ENTERED")
            st.cache_data.clear()
            return True
        except Exception as e:
            st.error(f"Erro ao salvar no banco: {e}")
            return False

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Cadastre alunos na Gestão da Turma.")
    else:
        # INTELIGÊNCIA TEMPORAL DE TRIMESTRE
        hoje_dt = date.today()
        if hoje_dt <= date(2026, 5, 22): trim_detectado = "I Trimestre"
        elif hoje_dt <= date(2026, 9, 4): trim_detectado = "II Trimestre"
        else: trim_detectado = "III Trimestre"

        turmas_reais_pei = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])] if not df_turmas.empty else pd.DataFrame()
        lista_turmas = sorted(turmas_reais_pei['ID_TURMA'].unique()) if not turmas_reais_pei.empty else sorted(df_alunos['TURMA'].unique())
        
        with st.container(border=True):
            c_top1, c_top2 = st.columns([1.2, 2])
            turma_pei = c_top1.selectbox("🎯 Selecione a Turma:", lista_turmas, key=f"pei_t_clean_{v}")
            
            trim_ativo_pei = c_top2.segmented_control(
                "📅 Selecione o Trimestre Ativo:",
                ["I Trimestre", "II Trimestre", "III Trimestre"],
                default=trim_detectado,
                key=f"seg_trim_pei_{v}"
            )
            if not trim_ativo_pei: trim_ativo_pei = trim_detectado

            # FILTRO CRUCIAL: APENAS ALUNOS ATIVOS DA TURMA
            df_turma_raw = df_alunos[df_alunos['TURMA'] == turma_pei].copy()
            if 'STATUS' not in df_turma_raw.columns: df_turma_raw['STATUS'] = "ATIVO"
            
            df_turma_foco = df_turma_raw[~df_turma_raw['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].copy()

        if df_turma_foco.empty:
            st.warning(f"⚠️ Nenhum aluno ativo cadastrado na turma {turma_pei}.")
            st.stop()

        # LÓGICA INVERSA UNIVERSAL & REGEX CID-10 (INFALÍVEL PARA O FUTURO)
        def elegivel_prova_adaptada_universal(nec_str):
            n = str(nec_str).upper().strip()
            if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: 
                return False
            
            # Se for EXCLUSIVAMENTE defasagem de sala sem qualquer CID, laudo ou suspeita médica:
            tem_cid_medico = bool(re.search(r'\b[A-Z]\d{2}(?:\.\d+)?\b', n))
            tem_palavra_laudo = any(x in n for x in [
                "LAUDO", "TEA", "TDAH", "DISLEXIA", "DEF", "SURDEZ", "CEGUEIRA", 
                "TOD", "SÍNDROME", "SINDROME", "DOWN", "PEI", "PENDENTE", "SUSPEITA", 
                "INVESTIGAÇÃO", "INVESTIGACAO", "ANÁLISE", "ANALISE", "AUTISMO"
            ])
            
            e_pure_defasagem = ("DEFASAGEM" in n or "DIFICULDADE" in n) and (not tem_cid_medico) and (not tem_palavra_laudo)
            
            if e_pure_defasagem:
                return False
                
            # Todo o resto (quaisquer CIDs A00-Z99, laudos novos, suspeitas ou tags PEI) vai para o Grupo 1!
            return True

        df_turma_foco['ELEGIVEL_PEI'] = df_turma_foco['NECESSIDADES'].apply(elegivel_prova_adaptada_universal)
        
        # Grupo 1: Laudados / CIDs / Suspeitos ATIVOS (Elegíveis para Prova Adaptada N1, N2, N3)
        df_laudados = df_turma_foco[df_turma_foco['ELEGIVEL_PEI']].copy()
        
        # Grupo 2: Apenas Defasagem Pedagógica ATIVA (Prova Regular)
        df_defasagem = df_turma_foco[~df_turma_foco['ELEGIVEL_PEI']].copy()
        df_defasagem = df_defasagem[df_defasagem['NECESSIDADES'].astype(str).str.upper().str.contains("DEFASAGEM|DIFICULDADE", regex=True, na=False)]

        # DASHBOARD TERMÔMETRO DE SUPORTE
        qtd_n1 = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PEI N1", case=False, na=False)])
        qtd_n2 = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PEI N2", case=False, na=False)])
        qtd_n3 = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PEI N3", case=False, na=False)])
        qtd_pendentes_suspeitos = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PENDENTE|SUSPEITA|INVESTIG", case=False, na=False)])

        with st.container(border=True):
            st.markdown(f"##### 📊 Termômetro de Inclusão da Turma {turma_pei} ({trim_ativo_pei}) — Alunos Ativos")
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("👥 Ativos Turma", len(df_turma_foco))
            k2.metric("🩺 Laudados / CIDs", len(df_laudados), f"{qtd_pendentes_suspeitos} com laudo em andamento")
            k3.metric("🔵 PEI N1", qtd_n1)
            k4.metric("🟡 PEI N2", qtd_n2)
            k5.metric("🔴 PEI N3", qtd_n3)

        st.markdown("---")

        tab_matriz, tab_forja, tab_provas_pei, tab_curriculo = st.tabs([
            "🎛️ 1. Triagem & Níveis PEI (Custo Zero)", 
            "✍️ 2. Dossiê Descritivo do Trimestre", 
            "🎯 3. Raio-X de Provas PEI",
            "📖 4. Currículo & PEI Oficial"
        ])

        # ==============================================================================
        # ABA 1: TRIAGEM RÁPIDA DE NÍVEIS (100% MANUAL / ZERO TOKEN)
        # ==============================================================================
        with tab_matriz:
            @st.fragment
            def renderizar_matriz_inclusao_fragmento():
                st.markdown("### 🎛️ Triagem de Níveis PEI & Barreiras (Zero Token)")
                st.caption("Altere os níveis das provas adaptadas em 1 clique sem gastar IA. O Scanner e a Central de Provas lerão este painel.")
                
                # CARTÃO 1: ALUNOS LAUDADOS OU SOB SUSPEITA ATIVOS (PROVA ADAPTADA GARANTIDA POR LEI)
                with st.container(border=True):
                    st.markdown("#### 🩺 Grupo 1: Estudantes Laudados / CIDs / Suspeitos ATIVOS (Prova Adaptada Garantida)")
                    st.caption("Defina o nível do caderno adaptado. Salva instantaneamente no banco de dados.")
                    
                    if df_laudados.empty:
                        st.info("Nenhum aluno ativo com laudo médico ou suspeita pendente cadastrado nesta turma.")
                    else:
                        def extrair_nivel(nec):
                            if "(PEI N1)" in nec: return "Nível 1 (Apoio Leve)"
                            if "(PEI N2)" in nec: return "Nível 2 (Apoio Moderado)"
                            if "(PEI N3)" in nec: return "Nível 3 (Qualitativa)"
                            return "Pendente (Definir)"

                        def limpar_nec(nec):
                            return re.sub(r'\s*\(PEI N[1-3]\)', '', nec).strip()

                        df_laudados['NIVEL_ATUAL'] = df_laudados['NECESSIDADES'].apply(extrair_nivel)
                        df_laudados['PERFIL_BASE'] = df_laudados['NECESSIDADES'].apply(limpar_nec)

                        dados_matriz_laudo = []
                        for _, r in df_laudados.iterrows():
                            dados_matriz_laudo.append({
                                "ID": r['ID'],
                                "Estudante": r['NOME_ALUNO'],
                                "Laudo / CID / Suspeita": r['PERFIL_BASE'],
                                "Nível de Prova Adaptada": r['NIVEL_ATUAL']
                            })
                        
                        df_laudo_ed = st.data_editor(
                            pd.DataFrame(dados_matriz_laudo), hide_index=True, use_container_width=True,
                            column_config={
                                "ID": None,
                                "Estudante": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Laudo / CID / Suspeita": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Nível de Prova Adaptada": st.column_config.SelectboxColumn(
                                    "Nível da Prova Adaptada",
                                    options=["Pendente (Definir)", "Nível 1 (Apoio Leve)", "Nível 2 (Apoio Moderado)", "Nível 3 (Qualitativa)"],
                                    required=True, width="large"
                                )
                            }, key=f"matriz_laudo_ed_{v}"
                        )

                        if st.button("💾 SALVAR NÍVEIS PEI E ATUALIZAR SCANNER (0.1s)", type="primary", use_container_width=True, key=f"btn_save_matriz_pei_{v}"):
                            with st.spinner("Atualizando cadastro em cascata..."):
                                for _, r in df_laudo_ed.iterrows():
                                    nivel_sel = r["Nível de Prova Adaptada"]
                                    tag_nivel = ""
                                    if "Nível 1" in nivel_sel: tag_nivel = " (PEI N1)"
                                    elif "Nível 2" in nivel_sel: tag_nivel = " (PEI N2)"
                                    elif "Nível 3" in nivel_sel: tag_nivel = " (PEI N3)"
                                    
                                    nova_nec = f"{r['Laudo / CID / Suspeita']}{tag_nivel}"
                                    db.atualizar_aluno_cascata(r['ID'], r['Estudante'], turma_pei, nova_nec)
                                
                                st.success("✅ Níveis salvos com sucesso! O Scanner CIR e a Central de Provas foram sincronizados.")
                                time.sleep(0.5); st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                # CARTÃO 2: ALUNOS APENAS COM DEFASAGEM SIMPLES ATIVOS (PROVA REGULAR)
                with st.container(border=True):
                    st.markdown("#### 🧱 Grupo 2: Estudantes Apenas com Defasagem Pedagógica ATIVOS (Prova Regular / Sem Suspeita Médica)")
                    st.caption("ℹ️ **Regra Legal:** Alunos sem suspeita médica ou laudo realizam a Prova Regular com acompanhamento pedagógico de sala.")
                    
                    if df_defasagem.empty:
                        st.info("Nenhum aluno ativo apenas com defasagem pedagógica mapeado nesta turma.")
                    else:
                        dados_matriz_def = []
                        for _, r_d in df_defasagem.iterrows():
                            dados_matriz_def.append({
                                "Estudante": r_d['NOME_ALUNO'],
                                "Barreira Mapeada": r_d['NECESSIDADES'],
                                "Tipo de Avaliação": "📝 PROVA REGULAR (Sem Adaptação)"
                            })
                            
                        st.dataframe(
                            pd.DataFrame(dados_matriz_def), hide_index=True, use_container_width=True,
                            column_config={
                                "Estudante": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Barreira Mapeada": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Tipo de Avaliação": st.column_config.TextColumn(disabled=True, width="large")
                            }
                        )

            renderizar_matriz_inclusao_fragmento()

        # ==============================================================================
        # ABA 2: DOSSIÊ DESCRITIVO POR TRIMESTRE (EDIÇÃO RÁPIDA E LEVE)
        # ==============================================================================
        with tab_forja:
            @st.fragment
            def renderizar_forja_dossie_fragmento():
                st.markdown(f"### ✍️ Dossiê Descritivo — {trim_ativo_pei}")
                st.caption("Edite ou redija o relatório descritivo do trimestre ativo. Os dados são salvos separadamente por período.")
                
                df_todos_relatorio = pd.concat([df_laudados, df_defasagem]).drop_duplicates(subset=['ID']) if not df_laudados.empty or not df_defasagem.empty else pd.DataFrame()
                
                if df_todos_relatorio.empty:
                    st.info("Nenhum estudante ativo selecionado para relatório nesta turma.")
                else:
                    aluno_foco = st.selectbox("🎓 Selecione o Estudante para o Dossiê:", df_todos_relatorio['NOME_ALUNO'].tolist(), key=f"foco_pei_dossie_{v}")
                    dados_a = df_todos_relatorio[df_todos_relatorio['NOME_ALUNO'] == aluno_foco].iloc[0]
                    id_a = db.limpar_id(dados_a['ID'])
                    perfil_atual = str(dados_a['NECESSIDADES']).upper().strip()

                    # 1. NOTAS DO TRIMESTRE ATIVO
                    n_alu = df_notas[(df_notas['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_notas['TRIMESTRE'] == trim_ativo_pei)] if not df_notas.empty else pd.DataFrame()
                    if not n_alu.empty:
                        nota_c1 = util.sosa_to_float(n_alu.iloc[0]['NOTA_VISTOS'])
                        nota_c2 = util.sosa_to_float(n_alu.iloc[0]['NOTA_TESTE'])
                        nota_c3 = util.sosa_to_float(n_alu.iloc[0]['NOTA_PROVA'])
                        media_trim_f = util.sosa_to_float(n_alu.iloc[0]['MEDIA_FINAL'])
                        notas_str = f"• C1 (Vistos): {nota_c1:.1f} | C2 (Teste): {nota_c2:.1f} | C3 (Prova): {nota_c3:.1f} ➔ Média: {media_trim_f:.1f} pts"
                    else:
                        notas_str = f"Nenhuma nota lançada no boletim para o {trim_ativo_pei}."

                    # 2. OCORRÊNCIAS DO DIÁRIO DO TRIMESTRE ATIVO
                    if trim_ativo_pei == "I Trimestre": dt_i, dt_f = date(2026, 2, 9), date(2026, 5, 22)
                    elif trim_ativo_pei == "II Trimestre": dt_i, dt_f = date(2026, 5, 25), date(2026, 9, 4)
                    else: dt_i, dt_f = date(2026, 9, 8), date(2026, 12, 17)

                    ocorrencias_diario = []
                    faltas_cnt = 0
                    if not df_diario.empty:
                        d_alu = df_diario[((df_diario['ID_ALUNO'].apply(db.limpar_id) == id_a) | (df_diario['ID_ALUNO'] == "GLOBAL")) & (df_diario['TURMA'] == turma_pei)].copy()
                        if not d_alu.empty:
                            d_alu['DATA_DT'] = pd.to_datetime(d_alu['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                            d_alu_sub = d_alu[(d_alu['DATA_DT'] >= dt_i) & (d_alu['DATA_DT'] <= dt_f)]
                            faltas_cnt = len(d_alu_sub[d_alu_sub['TAGS'] == "AUSÊNCIA"])
                            
                            mask_oc = (d_alu_sub['TAGS'] != "") & (~d_alu_sub['TAGS'].isin(["DIA NÃO LETIVO", "SISTEMA_NOTA", "AUSÊNCIA"]))
                            for _, r_d in d_alu_sub[mask_oc].tail(6).iterrows():
                                ocorrencias_diario.append(f"• {r_d['DATA']}: {r_d['TAGS']} ({r_d['OBSERVACOES']})")

                    oc_str = "\n".join(ocorrencias_diario) if ocorrencias_diario else "Nenhuma ocorrência registrada no período."

                    with st.container(border=True):
                        st.markdown(f"##### 📊 Evidências do {trim_ativo_pei}: **{aluno_foco}**")
                        c_ctx1, c_ctx2 = st.columns([1.2, 1.8])
                        c_ctx1.info(f"**Desempenho em Matemática:**\n{notas_str}\n\n**Faltas no {trim_ativo_pei}:** {faltas_cnt}")
                        c_ctx2.warning(f"**Atitudes & Ocorrências no Diário:**\n{oc_str}")

                    # CHAVE ÚNICA DO RELATÓRIO TRIMESTRAL
                    tipo_relatorio_chave = f"DOSSIE_PEI_{trim_ativo_pei.replace(' ', '_').upper()}"
                    
                    hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_a] if not df_relatorios.empty else pd.DataFrame()
                    rel_master = hist_aluno[hist_aluno['TIPO'] == tipo_relatorio_chave] if not hist_aluno.empty else pd.DataFrame()
                    
                    text_dossie_salvo = str(rel_master.iloc[-1]['CONTEUDO']) if not rel_master.empty else ""

                    st.markdown("---")
                    st.markdown(f"#### 📄 Redação do Dossiê Descritivo ({trim_ativo_pei})")

                    # BOTÃO OPCIONAL DE GERAR COM IA
                    if st.button(f"🧠 Rascunhar Dossiê do {trim_ativo_pei} com IA (Opcional)", use_container_width=True, key=f"btn_ghost_exe_{v}"):
                        with st.spinner("A IA está analisando as evidências e redigindo um rascunho..."):
                            prompt_ghost = (
                                f"Aja como um Psicopedagogo e Especialista em Inclusão. Redija um parecer descritivo empático e técnico para o {trim_ativo_pei}.\n"
                                f"ESTUDANTE: {aluno_foco} | PERFIL: {perfil_atual}\n"
                                f"EVIDÊNCIAS DO {trim_ativo_pei.upper()}:\n"
                                f"1. DESEMPENHO: {notas_str} | FALTAS: {faltas_cnt}\n"
                                f"2. DIÁRIO: {oc_str}\n\n"
                                f"🚨 REDIJA UTILIZANDO ESTRITAMENTE AS TAGS COM COLCHETES:\n"
                                f"[DIAGNOSTICO_GERAL] (Relatório descritivo do {trim_ativo_pei})\n"
                                f"[SOCIAIS] (Interação no período)\n"
                                f"[COMUNICATIVAS] (Expressão verbal/escrita)\n"
                                f"[EMOCIONAIS] (Autorregulação)\n"
                                f"[FUNCIONAIS] (Autonomia)\n"
                                f"[DIRETRIZES_CURRICULARES] (Orientações pedagógicas)"
                            )
                            res_master = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_ghost)
                            salvar_relatorio_pei_sem_duplicidade(id_a, aluno_foco, tipo_relatorio_chave, res_master)
                            st.success("✅ Rascunho gerado!"); time.sleep(0.5); st.rerun()

                    # CAMPOS DE EDIÇÃO MANUAL DIRETA E FÁCIL
                    ed_diag = st.text_area("1. Diagnóstico e Evolução Geral do Trimestre:", ai.extrair_tag(text_dossie_salvo, "DIAGNOSTICO_GERAL"), height=150, key=f"ed_diag_ghost_{v}")
                    
                    c_h1, c_h2 = st.columns(2)
                    ed_soc = c_h1.text_area("2. Habilidades Sociais:", ai.extrair_tag(text_dossie_salvo, "SOCIAIS"), height=90, key=f"ed_soc_ghost_{v}")
                    ed_com = c_h2.text_area("3. Habilidades Comunicativas:", ai.extrair_tag(text_dossie_salvo, "COMUNICATIVAS"), height=90, key=f"ed_com_ghost_{v}")
                    ed_emo = c_h1.text_area("4. Habilidades Emocionais:", ai.extrair_tag(text_dossie_salvo, "EMOCIONAIS"), height=90, key=f"ed_emo_ghost_{v}")
                    ed_fun = c_h2.text_area("5. Habilidades Funcionais:", ai.extrair_tag(text_dossie_salvo, "FUNCIONAIS"), height=90, key=f"ed_fun_ghost_{v}")
                    
                    ed_dir = st.text_area("6. Diretrizes Curriculares e Adaptações Recomendadas:", ai.extrair_tag(text_dossie_salvo, "DIRETRIZES_CURRICULARES"), height=110, key=f"ed_dir_ghost_{v}")
                    
                    if st.button(f"💾 SALVAR DOSSIÊ DO {trim_ativo_pei.upper()}", type="primary", use_container_width=True, key=f"btn_save_man_dossie_{v}"):
                        texto_consolidado = f"[DIAGNOSTICO_GERAL]\n{ed_diag}\n\n[SOCIAIS]\n{ed_soc}\n\n[COMUNICATIVAS]\n{ed_com}\n\n[EMOCIONAIS]\n{ed_emo}\n\n[FUNCIONAIS]\n{ed_fun}\n\n[DIRETRIZES_CURRICULARES]\n{ed_dir}"
                        salvar_relatorio_pei_sem_duplicidade(id_a, aluno_foco, tipo_relatorio_chave, texto_consolidado)
                        st.success(f"✅ Dossiê do {trim_ativo_pei} salvo com sucesso no banco!"); time.sleep(0.5); st.rerun()

            renderizar_forja_dossie_fragmento()

        # ==============================================================================
        # ABA 3: PARECER PARA PAIS (WHATSAPP & DOCX A4 DO TRIMESTRE)
        # ==============================================================================
        with tab_provas_pei:
            @st.fragment
            def renderizar_parecer_pais_fragmento():
                st.markdown(f"### 📱 Parecer Descritivo do {trim_ativo_pei} para os Pais")
                st.caption("Exporte o relatório em linguagem acolhedora para envio no WhatsApp ou impressão oficial em Word A4.")
                
                df_todos_relatorio = pd.concat([df_laudados, df_defasagem]).drop_duplicates(subset=['ID']) if not df_laudados.empty or not df_defasagem.empty else pd.DataFrame()
                
                if df_todos_relatorio.empty:
                    st.info("Nenhum estudante ativo selecionado.")
                else:
                    aluno_p_sel = st.selectbox("Selecione o Estudante:", df_todos_relatorio['NOME_ALUNO'].tolist(), key=f"foco_pei_parecer_{v}")
                    id_p = db.limpar_id(df_todos_relatorio[df_todos_relatorio['NOME_ALUNO'] == aluno_p_sel].iloc[0]['ID'])
                    perfil_p = str(df_todos_relatorio[df_todos_relatorio['NOME_ALUNO'] == aluno_p_sel].iloc[0]['NECESSIDADES']).upper()
                    
                    tipo_relatorio_chave = f"DOSSIE_PEI_{trim_ativo_pei.replace(' ', '_').upper()}"
                    hist_p = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_p] if not df_relatorios.empty else pd.DataFrame()
                    rel_p = hist_p[hist_p['TIPO'] == tipo_relatorio_chave] if not hist_p.empty else pd.DataFrame()
                    
                    txt_p_salvo = str(rel_p.iloc[-1]['CONTEUDO']) if not rel_p.empty else ""
                    p_diag = ai.extrair_tag(txt_p_salvo, "DIAGNOSTICO_GERAL") or "Parecer ainda não preenchido para este trimestre."
                    p_dir = ai.extrair_tag(txt_p_salvo, "DIRETRIZES_CURRICULARES") or "Sem recomendações registradas."

                    # MODAL WHATSAPP
                    @st.dialog(f"📱 Parecer Acolhedor - {trim_ativo_pei}")
                    def dialog_zap_parecer():
                        st.info("Copie o texto acolhedor abaixo e envie para a família no WhatsApp na Reunião de Pais.")
                        msg_zap_pei = f"""Olá! Tudo bem? Aqui é o professor Ronaldo Gomes. 🏫
Compartilho o Parecer Descritivo do(a) estudante {aluno_p_sel} referente ao {trim_ativo_pei}.

📌 EVOLUÇÃO E DESEMPENHO NO TRIMESTRE:
{p_diag}

🎯 RECOMENDAÇÕES PEDAGÓGICAS:
{p_dir}

Qualquer dúvida, estou à disposição na escola! Um abraço! 🚀"""
                        st.code(msg_zap_pei, language=None)

                    c_act1, c_act2 = st.columns(2)
                    
                    if c_act1.button("📱 Gerar Texto para WhatsApp dos Pais", use_container_width=True, key=f"btn_zap_par_{v}"):
                        dialog_zap_parecer()

                    if c_act2.button("🖨️ Imprimir Parecer A4 do Trimestre (DOCX)", type="primary", use_container_width=True, key=f"btn_docx_par_{v}"):
                        with st.spinner("Compilando Parecer Descritivo A4..."):
                            texto_parecer_docx = (
                                f"PARECER DESCRITIVO DE ACOMPANHAMENTO PEDAGÓGICO - {trim_ativo_pei.upper()}\n\n"
                                f"Estudante: {aluno_p_sel} | Turma: {turma_pei} | Perfil: {perfil_p}\n\n"
                                f"1. AVALIAÇÃO DESCRITIVA DO DESEMPENHO:\n{p_diag}\n\n"
                                f"2. RECOMENDAÇÕES E DIRETRIZES PARA O PRÓXIMO CICLO:\n{p_dir}"
                            )
                            nome_arq_parecer = f"PARECER_{aluno_p_sel.replace(' ','_')}_{trim_ativo_pei.replace(' ','')}"
                            doc_p = exporter.gerar_docx_aluno_v24(nome_arq_parecer, texto_parecer_docx, {"ano": turma_pei, "trimestre": trim_ativo_pei})
                            link_p = db.subir_e_converter_para_google_docs(doc_p, nome_arq_parecer, modo="AULA")
                            
                            if "https" in link_p:
                                st.success("✅ Parecer A4 gerado com sucesso!")
                                st.link_button("📂 ABRIR PARECER NO DRIVE (DOCX)", link_p, type="primary", use_container_width=True)
                                st.balloons()

            renderizar_parecer_pais_fragmento()

        # ==============================================================================
        # ABA 4: CURRÍCULO ADAPTADO & PEI OFICIAL DA PREFEITURA
        # ==============================================================================
        with tab_curriculo:
            @st.fragment
            def renderizar_curriculo_exportacao_fragmento():
                st.markdown(f"### 📖 Adaptação Curricular & PEI Oficial — {trim_ativo_pei}")
                st.caption("Planejamento de acessibilidade e exportação da ficha oficial da Secretaria de Educação.")
                
                df_laudados_secao = df_laudados if not df_laudados.empty else pd.DataFrame()
                
                if df_laudados_secao.empty:
                    st.info("Nenhum aluno ativo com laudo médico ou suspeita cadastrado nesta turma para receber o PEI Oficial da Prefeitura.")
                else:
                    aluno_exp = st.selectbox("Selecione o Estudante Laudado / Suspeito:", df_laudados_secao['NOME_ALUNO'].tolist(), key=f"exp_alu_sel_{v}")
                    
                    id_exp = db.limpar_id(df_laudados_secao[df_laudados_secao['NOME_ALUNO'] == aluno_exp].iloc[0]['ID'])
                    perfil_exp = str(df_laudados_secao[df_laudados_secao['NOME_ALUNO'] == aluno_exp].iloc[0]['NECESSIDADES']).upper()
                    
                    hist_exp = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_exp] if not df_relatorios.empty else pd.DataFrame()
                    rel_master_exp = hist_exp[hist_exp['TIPO'] == f"DOSSIE_PEI_{trim_ativo_pei.replace(' ', '_').upper()}"] if not hist_exp.empty else pd.DataFrame()
                    v_diretrizes_exp = ai.extrair_tag(str(rel_master_exp.iloc[-1]['CONTEUDO']), "DIRETRIZES_CURRICULARES") if not rel_master_exp.empty else "Sem diretrizes salvas."
                    
                    curr_records = hist_exp[hist_exp['TIPO'] == f"CURRICULO_ADAPTADO_{trim_ativo_pei}"] if not hist_exp.empty else pd.DataFrame()
                    if not curr_records.empty:
                        try: df_curr_atual = pd.read_json(io.StringIO(curr_records.iloc[-1]['CONTEUDO']), orient='records')
                        except: df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])
                    else: df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])

                    with st.popover("⚙️ Adaptar Matriz Curricular do Município (IA Opcional)", use_container_width=True):
                        st.caption("Selecione os conteúdos da prefeitura para traduzir para o perfil do aluno.")
                        ano_aluno = "".join(filter(str.isdigit, turma_pei))
                        df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == ano_aluno].copy() if not df_curriculo.empty else pd.DataFrame()
                        
                        if not df_matriz_ano.empty:
                            col_trim_mat = next((c for c in df_matriz_ano.columns if str(trim_ativo_pei).upper() in c.upper()), None)
                            col_eixo_mat = next((c for c in df_matriz_ano.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO'])), None)
                            
                            opcoes_conteudo = []
                            if col_trim_mat and col_eixo_mat:
                                for _, r_mat in df_matriz_ano.iterrows():
                                    c_bruto = str(r_mat[col_trim_mat])
                                    if pd.notna(c_bruto) and c_bruto.strip() != "":
                                        for t_item in c_bruto.split(';'):
                                            t_cl = re.sub(r'\[cite:.*?\]', '', t_item).strip()
                                            if t_cl and len(t_cl) > 3:
                                                opcoes_conteudo.append(f"[{r_mat[col_eixo_mat]}] {t_cl}")
                            
                            selecionados = st.multiselect("Escolha os conteúdos para adaptar:", sorted(list(set(opcoes_conteudo))), key=f"sel_mat_pop_{v}")
                            
                            if st.button("🚀 Gerar Adaptação Curricular", type="primary", use_container_width=True, key=f"btn_gen_curr_pop_{v}"):
                                if selecionados:
                                    with st.spinner("Adaptando matriz..."):
                                        prompt_curr = f"ESTUDANTE: {aluno_exp}. PERFIL: {perfil_exp}.\nDIRETRIZES: {v_diretrizes_exp}\nCONTEÚDOS ESCOLHIDOS: {', '.join(selecionados)}.\nGere os itens adaptados para o PEI."
                                        res_ia = ai.gerar_ia("TRADUTOR_CURRICULAR_V39", prompt_curr)
                                        
                                        blocos = re.findall(r"\[ITEM\](.*?)\[/ITEM\]", res_ia, re.DOTALL)
                                        novas_linhas = [{"Objetivos de Aprendizagem": ai.extrair_tag(b, "OBJETIVO"), "Estratégias Metodológicas": ai.extrair_tag(b, "ESTRATEGIA"), "Recursos Materiais": ai.extrair_tag(b, "RECURSO")} for b in blocos]
                                        
                                        if novas_linhas:
                                            df_curr_atual = pd.concat([df_curr_atual, pd.DataFrame(novas_linhas)], ignore_index=True)
                                            salvar_relatorio_pei_sem_duplicidade(id_exp, aluno_exp, f"CURRICULO_ADAPTADO_{trim_ativo_pei}", df_curr_atual.to_json(orient='records'))
                                            st.rerun()

                    st.markdown("**Tabela de Planejamento Adaptado (Editável)**")
                    df_editado_curr = st.data_editor(
                        df_curr_atual, num_rows="dynamic", use_container_width=True, key=f"ed_curr_frag_{v}",
                        column_config={"Objetivos de Aprendizagem": st.column_config.TextColumn(width="large"), "Estratégias Metodológicas": st.column_config.TextColumn(width="large"), "Recursos Materiais": st.column_config.TextColumn(width="medium")}
                    )
                    
                    st.markdown("---")
                    c_btn_save, c_btn_exp = st.columns(2)
                    
                    if c_btn_save.button("💾 Salvar Tabela de Planejamento", use_container_width=True, key=f"btn_save_tab_curr_{v}"):
                        salvar_relatorio_pei_sem_duplicidade(id_exp, aluno_exp, f"CURRICULO_ADAPTADO_{trim_ativo_pei}", df_editado_curr.to_json(orient='records'))
                        st.success("Tabela salva com sucesso!"); time.sleep(0.5); st.rerun()
                        
                    if c_btn_exp.button("🖨️ GERAR PEI OFICIAL DA PREFEITURA (DOCX)", type="primary", use_container_width=True, key=f"btn_gen_pei_docx_{v}"):
                        with st.spinner("Compilando Dossiê Oficial no padrão da Secretaria..."):
                            dados_aluno = {"nome": aluno_exp, "turma": turma_pei, "cid": perfil_exp}
                            
                            if not rel_master_exp.empty:
                                m_txt = str(rel_master_exp.iloc[-1]['CONTEUDO'])
                                habilidades = {"Habilidades Sociais": ai.extrair_tag(m_txt, "SOCIAIS"), "Habilidades Comunicativas": ai.extrair_tag(m_txt, "COMUNICATIVAS"), "Habilidades Emocionais": ai.extrair_tag(m_txt, "EMOCIONAIS"), "Habilidades Funcionais": ai.extrair_tag(m_txt, "FUNCIONAIS")}
                            else:
                                habilidades = {"Habilidades Sociais": "", "Habilidades Comunicativas": "", "Habilidades Emocionais": "", "Habilidades Funcionais": ""}
                            
                            nome_arq_pei = f"PEI_OFICIAL_{aluno_exp.replace(' ', '_')}_{trim_ativo_pei.replace(' ', '')}"
                            doc_stream = exporter.gerar_docx_pei_oficial(nome_arq_pei, dados_aluno, habilidades, df_editado_curr)
                            link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_pei, trimestre=trim_ativo_pei, categoria=turma_pei, modo="PLANEJAMENTO")
                            
                            if "https" in link_doc:
                                salvar_relatorio_pei_sem_duplicidade(id_exp, aluno_exp, "PEI_EXPORTADO", f"Link: {link_doc}")
                                st.success("✅ PEI Oficial gerado e salvo no Drive!")
                                st.link_button("📂 ABRIR PEI OFICIAL NO DRIVE", link_doc, type="primary", use_container_width=True)
                                st.balloons()
                            else: st.error(f"Erro ao salvar no Drive: {link_doc}")

            renderizar_curriculo_exportacao_fragmento()
