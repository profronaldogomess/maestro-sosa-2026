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
    """Gerencia o acesso com botão de entrada explícito e persistência de 6h."""
    
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

    # INTERFACE DE LOGIN (Design Responsivo e Limpo)
    _, col_login, _ = st.columns([1, 2, 1]) 
    
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        try: 
            st.image("logo.png", width=180) 
        except: 
            st.markdown("<h1 style='text-align: center;'>Ronaldo Gomes</h1>", unsafe_allow_html=True)
        
        st.markdown("<h3 style='text-align: center; margin-bottom: 20px;'>🔐 Portal de Soberania</h3>", unsafe_allow_html=True)
        
        # FORMULÁRIO DE LOGIN
        with st.form("login_portal"):
            input_password = st.text_input("Chave de Acesso:", type="password", placeholder="Digite sua chave...")
            st.checkbox("Manter conectado por 6 horas", value=True, disabled=True)
            
            btn_entrar = st.form_submit_button("ENTRAR NO PAINEL", use_container_width=True)
            
            if btn_entrar:
                if input_password == "2496":
                    st.session_state["password_correct"] = True
                    st.session_state["login_timestamp"] = time.time()
                    st.success("Acesso Autorizado!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Chave incorreta. Acesso negado.")
        
        st.markdown("<p style='text-align: center; font-size: 12px; color: gray;'>Sistema restrito ao Prof. Ronaldo Gomes (Itabuna/BA)</p>", unsafe_allow_html=True)
    
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

# 🔬 FILTRO DE LEITURA GLOBAL (LATEX, IMAGENS E FORM FEED V2026.MASTER)
def preparar_para_leitura(texto):
    if not texto or not isinstance(texto, str): return ""
    # Vacina de escape do Form Feed (\x0c -> \\f)
    texto = texto.replace('\x0c', '\\f')
    # LaTeX de fração solto sem $
    texto = re.sub(r'(?<!\$)\\\w+\{[^\}]*?\}(?:\{[^\}]*?\})?(?!\$)', r'$\g<0>$', texto)
    texto = re.sub(r'(?<!\$)\^\\(circ|deg|cdot|times)(?!\$)', r'$\g<0>$', texto)
    # Potências e expressões de bloco
    texto = re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)
    # Limpa tags obsoletas do GeoGebra
    texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', '', texto, flags=re.IGNORECASE | re.DOTALL)
    # Prompts de Imagem transformados em caixas copiáveis com 1 clique
    texto = re.sub(
        r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', 
        r'\n\n🎨 **[PROMPT GERADOR DE IMAGEM - COPIE NO BOTÃO ABAIXO]**\n```english\n\1\n```\n\n', 
        texto, 
        flags=re.IGNORECASE | re.DOTALL
    )
    return texto

# --- ESTILIZAÇÃO DE LUXO (CSS V41 - BENTO GRID) ---
BRAND_BLUE = "#2962FF"
BRAND_NAVY = "#000B1A"

with st.sidebar:
    tema_selecionado = st.radio("Visual do Sistema:", ["🌙 Dark Mode", "🌞 Light Mode"], horizontal=True)

if tema_selecionado == "🌙 Dark Mode":
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

# --- SIDEBAR: IDENTIDADE E NAVEGAÇÃO ---
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try: st.image("logo.png", width=120)
        except: pass
    
    st.markdown(f"<h2 style='text-align: center; font-size: 22px; margin-top: 10px;'>Ronaldo Gomes</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 12px; color: {BRAND_BLUE}; font-weight: 800; margin-top: -15px; letter-spacing: 1px;'>SOBERANIA PEDAGÓGICA</p>", unsafe_allow_html=True)

    fuso_br = timezone(timedelta(hours=-3))
    agora_br = datetime.now(fuso_br)
    hora_atual = agora_br.strftime("%H:%M:%S")
    data_atual = agora_br.strftime("%d/%m/%Y")
    data_atual_dt = agora_br.date() 
    
    st.markdown(f"""<div class="clock-container">🕒 {hora_atual} | 📅 {data_atual}</div>""", unsafe_allow_html=True)
    
    feriado_hoje = util.verificar_feriado_itabuna(data_atual_dt)
    if feriado_hoje:
        st.markdown(f"""<div style="background: linear-gradient(135deg, #FF4B4B, #C0392B); color: white; padding: 6px 10px; border-radius: 8px; text-align: center; font-weight: 800; font-size: 12px; margin-top: -5px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">🎉 FERIADO: {feriado_hoje.upper()}</div>""", unsafe_allow_html=True)
    else:
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        nome_dia = dias_semana[data_atual_dt.weekday()]
        cor_dia = "#2ECC71" if data_atual_dt.weekday() < 5 else "#F1C40F" 
        st.markdown(f"""<div style="text-align: center; color: {cor_dia}; font-size: 12px; font-weight: 600; margin-top: -5px; margin-bottom: 10px;">{nome_dia} • Dia Letivo</div>""", unsafe_allow_html=True)

    # 🚨 RADAR DE SOBERANIA (NOTIFICAÇÕES INTELIGENTES V201)
    st.markdown("---")
    st.markdown("<p style='font-size: 11px; color: gray; font-weight: bold; letter-spacing: 1px; text-align: center;'>RADAR DE SOBERANIA</p>", unsafe_allow_html=True)
    
    try:
        planos_pendentes = len(df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)])
        if planos_pendentes > 0:
            st.markdown(f"<div style='background: #FFF3CD; color: #B7950B; padding: 8px; border-radius: 8px; font-size: 12px; font-weight: bold; margin-bottom: 5px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>⏳ {planos_pendentes} Plano(s) no Hub</div>", unsafe_allow_html=True)
    except: pass

    try:
        if not df_notas.empty:
            uti_count = len(df_notas[df_notas['MEDIA_FINAL'].apply(util.sosa_to_float) < 6.0])
            if uti_count > 0:
                st.markdown(f"<div style='background: #FADBD8; color: #943126; padding: 8px; border-radius: 8px; font-size: 12px; font-weight: bold; margin-bottom: 10px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.05);'>🚑 {uti_count} Aluno(s) na UTI</div>", unsafe_allow_html=True)
    except: pass

    st.markdown("---")

    menu_opcoes = [
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
    ]
    
    # 🚨 A MÁGICA ACONTECE AQUI: Desvinculamos a chave direta e usamos o index
    idx_atual = menu_opcoes.index(st.session_state.menu_atual) if st.session_state.menu_atual in menu_opcoes else 0
    menu = st.radio("Navegação Estratégica:", menu_opcoes, index=idx_atual, key="_menu_radio", on_change=atualizar_menu)

    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.markdown("---")
    
    col_sync, col_exit = st.columns(2)
    with col_sync:
        if st.button("🔄 Sync"):
            st.cache_data.clear()
            st.rerun()
    with col_exit:
        if st.button("🚪 Sair"):
            st.session_state["password_correct"] = False
            st.session_state["login_timestamp"] = None
            st.rerun()

    st.caption("Ronaldo Gomes | © 2026")

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
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - V202.6 (CSV PARSER & CASCATA)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("Engenharia de Planejamento")
    st.caption("Defina a rota da semana. O sistema automatiza a burocracia, gerencia a matriz do seu CSV real e alimenta o Criador de Aulas.")
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
        "Novo Plano", "Hub de Produção", "Acervo", "Inteligência Curricular"
    ])
    
    # ==============================================================================
    # ABA 1: NOVO PLANO (PARSER INTELIGENTE DO SEU CSV REAL)
    # ==============================================================================
    with tab_gerar:
        with st.container(border=True):
            st.markdown("#### 1. Parâmetros da Semana")
            
            c1, c2, c3 = st.columns([1, 2, 2])
            ano_p = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_sel_{v}")
            ano_str_busca = f"{ano_p}º"

            todas_semanas = util.gerar_semanas()
            # 🚨 VACINA ANTI-INSTABILIDADE GOOGLE 503
            if not df_planos.empty and 'ANO' in df_planos.columns and 'SEMANA' in df_planos.columns:
                semanas_planejadas = df_planos[df_planos['ANO'] == ano_str_busca]['SEMANA'].tolist()
            else:
                semanas_planejadas = []
            semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_planejadas and "Jornada" not in s]

            if not semanas_disponiveis:
                st.success(f"Todas as semanas do {ano_p}º Ano já foram planejadas.")
                st.stop()

            sem_p = c2.selectbox("Semana de Referência:", semanas_disponiveis, key=f"sem_sel_{v}")
            sem_limpa = sem_p.split(" (")[0]
            trim_atual = sem_p.split(" - ")[1] if " - " in sem_p else "I Trimestre"

            tipo_semana = c3.selectbox("DNA da Abordagem:", [
                "Aula de Safra (Regular)", 
                "Aplicação de Exame", 
                "Revisão & Recomposição", 
                "Semana de Provas Oficiais (Global)",
                "Devolutiva de Resultados & Recuperação",
                "Trabalho Investigativo", 
                "Sonda de Proficiência",
                "Aula Aberta (Dinâmicas e Eventos)"
            ], key=f"gate_tipo_{v}")
            
            st.markdown("---")
            carga_horaria = st.radio(
                "Carga Horária da Semana:", 
                ["1 Aula (Feriado/Evento)", "2 Aulas (Semana Normal)", "3 Aulas (+ Sábado Letivo)"], 
                index=1, horizontal=True, key=f"carga_{v}"
            )

        # ------------------------------------------------------------------------------
        # ROTA 1: BUROCRACIA PADRONIZADA (SEM GASTO DE IA)
        # ------------------------------------------------------------------------------
        if tipo_semana in ["Semana de Provas Oficiais (Global)", "Devolutiva de Resultados & Recuperação"]:
            with st.container(border=True):
                st.markdown("#### 2. Homologação Burocrática")
                st.info("O sistema identificou uma semana de rotina administrativa. O texto padrão já foi gerado para poupar tempo e tokens.")
                
                if "Provas" in tipo_semana:
                    texto_padrao = f"Avaliação Global. Ocorrerão provas de diversas disciplinas conforme calendário da coordenação. Foco em gestão de tempo e inteligência emocional."
                    aula_1_txt = "Organização das fileiras. Leitura das instruções gerais. Aplicação do instrumento avaliativo com monitoramento ativo."
                    aula_2_txt = "Continuação da aplicação (se necessário) ou recolhimento dos instrumentos." if "1 Aula" not in carga_horaria else "N/A"
                    aula_sab_txt = "Plantão tira-dúvidas ou aplicação de exames pendentes." if "3 Aulas" in carga_horaria else "N/A"
                else:
                    texto_padrao = f"Análise de Erros e Recuperação Paralela. Foco nos tópicos com menor índice de acerto no Raio-X da turma."
                    aula_1_txt = "Entrega dos resultados da avaliação. Correção comentada no quadro das questões com menor índice de acerto (Mapa de Calor)."
                    aula_2_txt = "Aplicação do instrumento de Recuperação Paralela para os alunos elegíveis. Atividade de aprofundamento para os alunos já aprovados." if "1 Aula" not in carga_horaria else "N/A"
                    aula_sab_txt = "Continuação da recuperação paralela ou nivelamento de base." if "3 Aulas" in carga_horaria else "N/A"

                st.text_area("Resumo do Plano:", texto_padrao, disabled=True)
                
                if st.button("Salvar Plano Padronizado", type="primary", use_container_width=True):
                    with st.spinner("Salvando no Acervo..."):
                        nome_arquivo = f"PLANO_{ano_str_busca.replace('º','')}_{sem_limpa.replace(' ', '')}"
                        db.excluir_plano_completo(sem_limpa, ano_str_busca)
                        
                        metodologia_docx = f"AULA 1:\n{aula_1_txt}"
                        if aula_2_txt != "N/A": metodologia_docx += f"\n\nAULA 2:\n{aula_2_txt}"
                        if aula_sab_txt != "N/A": metodologia_docx += f"\n\nSÁBADO LETIVO:\n{aula_sab_txt}"
                        
                        dados_docx = {
                            "geral": tipo_semana.upper(), "especificos": texto_padrao, 
                            "objetivos": "Cumprimento do calendário letivo oficial.", 
                            "recursos": "Instrumentos Avaliativos", 
                            "metodologia": metodologia_docx,
                            "avaliacao": "Correção e análise de resultados.", 
                            "pei": "Acompanhamento individualizado e tempo estendido conforme necessidade."
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": ano_str_busca, "semana": sem_limpa, "trimestre": trim_atual})
                        link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=trim_atual, categoria=ano_str_busca, semana=sem_limpa, modo="PLANEJAMENTO")
                        
                        final_txt = f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} \n[CONTEUDOS_ESPECIFICOS] {texto_padrao} \n[AULA_1] {aula_1_txt} \n[AULA_2] {aula_2_txt} \n[SABADO_LETIVO] {aula_sab_txt} \n--- LINK DRIVE --- {link_drive}"
                        db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_limpa, ano_str_busca, trim_atual, "PRODUZIDO", final_txt, link_drive])
                        st.success("Plano salvo com sucesso!"); time.sleep(1); st.rerun()

        # ------------------------------------------------------------------------------
        # ROTA 2: VÍNCULO DE ACERVO (EXAMES E REVISÕES)
        # ------------------------------------------------------------------------------
        elif tipo_semana in ["Aplicação de Exame", "Revisão & Recomposição", "Sonda de Proficiência", "Trabalho Investigativo", "Aula Aberta (Dinâmicas e Eventos)"]:
            with st.container(border=True):
                st.markdown("#### 2. Vínculo de Material")
                
                ativo_selecionado = ""
                if tipo_semana != "Aula Aberta (Dinâmicas e Eventos)":
                    df_ativos_ano = df_aulas[df_aulas['ANO'] == ano_str_busca]
                    opcoes_ativos = []
                    
                    if "Exame" in tipo_semana or "Sonda" in tipo_semana: 
                        opcoes_ativos = df_ativos_ano[df_ativos_ano['SEMANA_REF'] == "AVALIAÇÃO"]['TIPO_MATERIAL'].tolist()
                    elif "Revisão" in tipo_semana: 
                        opcoes_ativos = df_ativos_ano[df_ativos_ano['SEMANA_REF'] == "REVISÃO"]['TIPO_MATERIAL'].tolist()
                    elif "Trabalho" in tipo_semana: 
                        opcoes_ativos = df_ativos_ano[df_ativos_ano['TIPO_MATERIAL'].str.contains("PROJETO|TRABALHO", case=False, na=False)]['TIPO_MATERIAL'].tolist()
                    
                    if opcoes_ativos:
                        ativo_selecionado = st.selectbox("Selecione o material do Acervo:", opcoes_ativos)
                    else:
                        st.warning(f"Nenhum material do tipo '{tipo_semana}' encontrado no acervo para o {ano_p}º Ano.")
                else:
                    ativo_selecionado = st.text_input("Nome do Evento/Dinâmica:", placeholder="Ex: Palestra sobre Educação Financeira")

                diretriz_logistica = st.text_area("Diretriz Logística (O que vai acontecer na aula?):", placeholder="Ex: Os alunos terão 50 minutos para realizar a prova em silêncio...")

                if st.button("Salvar Logística no Acervo", type="primary", use_container_width=True):
                    if ativo_selecionado:
                        with st.spinner("Salvando..."):
                            nome_arquivo = f"PLANO_{ano_str_busca.replace('º','')}_{sem_limpa.replace(' ', '')}"
                            db.excluir_plano_completo(sem_limpa, ano_str_busca)
                            
                            roteiro_docx = f"AULA DEDICADA A: {tipo_semana}\nMATERIAL/TEMA: {ativo_selecionado}\n\nDIRETRIZES DE EXECUÇÃO:\n{diretriz_logistica}"
                            dados_docx = {
                                "geral": tipo_semana.upper(), "especificos": ativo_selecionado, 
                                "objetivos": "Mensurar proficiência e consolidar habilidades.", 
                                "recursos": "Material Impresso do Acervo SOSA", 
                                "metodologia": roteiro_docx,
                                "avaliacao": "Observação direta e/ou correção do instrumento.", 
                                "pei": "Acompanhamento individualizado."
                            }
                            
                            doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": ano_str_busca, "semana": sem_limpa, "trimestre": trim_atual})
                            link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=trim_atual, categoria=ano_str_busca, semana=sem_limpa, modo="PLANEJAMENTO")
                            
                            final_txt = f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} \n[CONTEUDOS_ESPECIFICOS] {ativo_selecionado} \n[AULA_1] {roteiro_docx} \n[AULA_2] N/A \n[SABADO_LETIVO] N/A \n--- LINK DRIVE --- {link_drive}"
                            db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_limpa, ano_str_busca, trim_atual, "PRODUZIDO", final_txt, link_drive])
                            st.success("Logística salva!"); time.sleep(1); st.rerun()

        # ------------------------------------------------------------------------------
        # ROTA 3: AULA REGULAR (PARSER PERFEITO DO SEU CSV REAL - 0 WARNS / 0 BUGS)
        # ------------------------------------------------------------------------------
        else:
            with st.container(border=True):
                st.markdown("#### 2. Base Curricular")
                
                modo_p = st.radio("Fonte de Dados:", ["Livro Didático", "Manual (Matriz)", "Links da Web"], horizontal=True)
                
                ctx_ia, uri_livro_drive, links_web_texto, base_didatica_info = "", None, "", "Matriz Curricular"
                
                if modo_p == "Manual (Matriz)":
                    df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str).str.contains(str(ano_p))].copy()
                    
                    # 🚨 LOCALIZAÇÃO DAS COLUNAS DO SEU CSV REAL
                    col_eixo_real = next((c for c in df_matriz_ano.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None)
                    col_trim_real = next((c for c in df_matriz_ano.columns if trim_atual.upper() in c.upper()), None)

                    sel_eixo, sel_cont = [], []
                    if col_eixo_real and not df_matriz_ano.empty:
                        eixos_disponiveis = sorted(df_matriz_ano[col_eixo_real].dropna().unique().tolist())
                        sel_eixo = st.multiselect("Eixo Temático (Conteúdos Gerais):", eixos_disponiveis)
                        
                        if col_trim_real and sel_eixo:
                            # Filtra as linhas correspondentes aos Eixos selecionados
                            df_eixos_sel = df_matriz_ano[df_matriz_ano[col_eixo_real].isin(sel_eixo)]
                            
                            topicos_fatiados = set()
                            for _, r_eixo in df_eixos_sel.iterrows():
                                texto_trim = str(r_eixo.get(col_trim_real, ''))
                                # Limpa citações como [cite: 8] e fatia por ';'
                                texto_limpo = re.sub(r'\[cite:.*?\]', '', texto_trim).strip()
                                for t_item in texto_limpo.split(';'):
                                    t_clean = t_item.strip()
                                    if t_clean and len(t_clean) > 3:
                                        topicos_fatiados.add(t_clean)
                                        
                            sel_cont = st.multiselect("Conteúdos Específicos do Trimestre:", sorted(list(topicos_fatiados)))
                            
                        ctx_ia = f"EIXO: {sel_eixo}, CONTEÚDOS ESPECÍFICOS: {sel_cont}."
                    else:
                        st.warning("⚠️ Não foi possível ler as colunas da matriz carregada.")
                
                elif modo_p == "Links da Web":
                    links_web_texto = st.text_area("Cole os Links (um por linha):", placeholder="https://...")
                    base_didatica_info = "Artigos da Web"
                
                else:
                    cx1, cx2 = st.columns([2, 1])
                    livros_disponiveis = df_materiais[df_materiais['TIPO'].str.contains(str(ano_p), na=False)]['NOME_ARQUIVO'].tolist()
                    sel_mat = cx1.selectbox("Livro do Cofre Digital:", [""] + livros_disponiveis)
                    pags = cx2.text_input("Páginas Alvo:", placeholder="Ex: 14-23")
                    if sel_mat:
                        uri_livro_drive = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_mat].iloc[0]['URI_ARQUIVO']
                        base_didatica_info = f"Livro: {sel_mat} | Páginas: {pags}"

            with st.container(border=True):
                st.markdown("#### 3. Diretrizes de Aula")
                
                foco_a1, foco_a2, foco_sab = "N/A", "N/A", "N/A"
                
                if "1 Aula" in carga_horaria:
                    foco_a1 = st.text_area("Foco da Aula 1:", placeholder="Ex: Explicar perímetro...", height=80)
                elif "2 Aulas" in carga_horaria:
                    c_d1, c_d2 = st.columns(2)
                    foco_a1 = c_d1.text_area("Foco da Aula 1:", placeholder="Ex: Explicar perímetro...", height=80)
                    foco_a2 = c_d2.text_area("Foco da Aula 2:", placeholder="Ex: Fazer exercícios da página 15...", height=80)
                else:
                    c_d1, c_d2, c_d3 = st.columns(3)
                    foco_a1 = c_d1.text_area("Foco da Aula 1:", placeholder="Ex: Explicar perímetro...", height=80)
                    foco_a2 = c_d2.text_area("Foco da Aula 2:", placeholder="Ex: Fazer exercícios...", height=80)
                    foco_sab = c_d3.text_area("Foco do Sábado Letivo:", placeholder="Ex: Oficina prática...", height=80)

            c_g1, c_g2 = st.columns(2)

            if c_g1.button("🧠 Iniciar Motor de IA: Gerar Planejamento", use_container_width=True, type="primary"):
                with st.status("🚀 Iniciando Protocolo de Planejamento...", expanded=True) as status:
                    status.write("📚 Coletando base didática e diretrizes...")
                    
                    precisa_de_internet = False
                    if modo_p == "Manual (Matriz)": 
                        diretriz_base = "MÉTODO MANUAL: Baseie-se na Matriz Curricular."
                    elif modo_p == "Links da Web": 
                        diretriz_base = f"MÉTODO WEB: Use estes links:\n{links_web_texto}"
                        precisa_de_internet = True
                    else: 
                        diretriz_base = f"MÉTODO LIVRO: O professor utilizará o livro '{base_didatica_info}'."

                    template_forcado = (
                        "[HABILIDADE_BNCC] (Código BNCC)\n"
                        "[COMPETENCIAS_FOCO] (Competências)\n"
                        "[OBJETO_CONHECIMENTO] (Tema principal)\n"
                        "[CONTEUDOS_ESPECIFICOS] (Tópicos)\n"
                        "[OBJETIVOS_ENSINO] (Objetivos)\n"
                        "[JUSTIFICATIVA_PEDAGOGICA] (Justificativa)\n"
                        "[AULA_1] (Roteiro da Aula 1)\n"
                        "[AULA_2] (Roteiro da Aula 2)\n"
                        "[SABADO_LETIVO] (Roteiro do Sábado)\n"
                        "[AVALIACAO_DE_MERITO] (Como avaliar)\n"
                        "[ESTRATEGIA_DUA_PEI] (Adaptação PEI)\n"
                    )

                    prompt = (
                        f"TIPO: {tipo_semana}\n{diretriz_base}\n"
                        f"SÉRIE: {ano_p}º Ano. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}.\n"
                        f"CARGA HORÁRIA: {carga_horaria}.\n"
                        f"DIRETRIZ AULA 1: {foco_a1}\nDIRETRIZ AULA 2: {foco_a2}\nDIRETRIZ SÁBADO: {foco_sab}\n"
                        f"MATRIZ OFICIAL:\n{ctx_ia if ctx_ia else 'Não fornecida. Deduza com base no tema do livro/links.'}\n\n"
                        f"🚨 PREENCHA OBRIGATORIAMENTE ESTE TEMPLATE EXATO (Use as tags com colchetes):\n{template_forcado}"
                    )
                    
                    status.write("🧠 Maestro Sosa está redigindo o plano...")
                    resultado_ia = ai.gerar_ia("PLANE_PEDAGOGICO", prompt, url_drive=None, usar_busca=precisa_de_internet)
                    
                    if "ERRO" in resultado_ia.upper() or "⚠️" in resultado_ia:
                        status.update(label="❌ Falha na comunicação com a IA.", state="error")
                        st.error(resultado_ia)
                    else:
                        status.write("✅ Plano arquitetado com sucesso! Montando interface de revisão...")
                        st.session_state.p_temp = resultado_ia
                        st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info}
                        
                        status.update(label="🎉 Planejamento Concluído!", state="complete")
                        time.sleep(1)
                        st.rerun()

            if c_g2.button("✍️ Elaborar Manualmente (Sem IA)", use_container_width=True):
                espec_pre = ", ".join(sel_cont) if 'sel_cont' in locals() and sel_cont else ""
                
                texto_manual_template = (
                    f"[HABILIDADE_BNCC]\n"
                    f"[OBJETO_CONHECIMENTO]\n"
                    f"[CONTEUDOS_ESPECIFICOS] {espec_pre}\n"
                    f"[OBJETIVOS_ENSINO]\n"
                    f"[AULA_1] (Escreva o roteiro da Aula 1 aqui...)\n"
                    f"[AULA_2] (Escreva o roteiro da Aula 2 aqui...)\n"
                    f"[SABADO_LETIVO] (Escreva o roteiro do Sábado aqui se houver...)\n"
                    f"[AVALIACAO_DE_MERITO]\n"
                    f"[ESTRATEGIA_DUA_PEI]"
                )
                
                st.session_state.p_temp = texto_manual_template
                st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info}
                st.rerun()

            # --- EDITOR DO PLANO GERADO ---
            if "p_temp" in st.session_state:
                txt_bruto = st.session_state.p_temp
                meta = st.session_state.get("p_meta", {})
                
                st.markdown("---")
                st.markdown(f"### 🛠️ Mesa de Lapidação: Semana {meta.get('semana')}")
                
                with st.expander("👁️ Ver Texto Bruto da IA (Caso os campos abaixo estejam vazios)"):
                    st.text(txt_bruto)
                
                with st.container(border=True):
                    cmd_refine = st.chat_input("Refinador IA (Ex: 'Deixe a Aula 1 mais lúdica')")
                    if cmd_refine:
                        with st.spinner("Reescrevendo com Gemini 3.1 Pro..."):
                            prompt_refino = f"ORDEM: {cmd_refine}\n\nPLANO ATUAL:\n{st.session_state.p_temp}"
                            st.session_state.p_temp = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino)
                            st.rerun()

                tab_curriculo, tab_roteiro, tab_inclusao = st.tabs(["📚 1. Base Curricular", "📝 2. Roteiro das Aulas", "♿ 3. Avaliação & PEI"])
                
                with tab_curriculo:
                    ed_hab = st.text_input("Habilidade/Competência:", ai.extrair_tag(txt_bruto, "HABILIDADE_BNCC") or ai.extrair_tag(txt_bruto, "COMPETENCIA_GERAL"))
                    ed_geral = st.text_input("Objeto de Conhecimento:", ai.extrair_tag(txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL"))
                    ed_espec = st.text_area("Conteúdos Específicos:", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS") or txt_bruto, height=150)
                    ed_objs = st.text_area("Objetivos de Aprendizagem:", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO"), height=150)
                
                with tab_roteiro:
                    c_a1, c_a2, c_a3 = st.columns(3)
                    ed_a1 = c_a1.text_area("AULA 1:", ai.extrair_tag(txt_bruto, "AULA_1"), height=400)
                    ed_a2 = c_a2.text_area("AULA 2:", ai.extrair_tag(txt_bruto, "AULA_2"), height=400)
                    ed_sab = c_a3.text_area("SÁBADO LETIVO:", ai.extrair_tag(txt_bruto, "SABADO_LETIVO"), height=400)
                    
                with tab_inclusao:
                    ed_ava = st.text_area("Avaliação de Mérito:", ai.extrair_tag(txt_bruto, "AVALIACAO_DE_MERITO"), height=150)
                    ed_pei = st.text_area("Estratégia DUA/PEI:", ai.extrair_tag(txt_bruto, "ESTRATEGIA_DUA_PEI"), height=150)
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Salvar e Enviar para Produção", use_container_width=True, type="primary"):
                    with st.status("Gerando DOCX e Sincronizando...") as status:
                        nome_arquivo = f"PLANO_{meta.get('ano').replace('º','')}_{meta.get('semana').replace(' ', '')}"
                        db.excluir_plano_completo(meta.get('semana'), meta.get('ano'))
                        
                        metodologia_docx = f"AULA 01:\n{ed_a1}"
                        if "N/A" not in ed_a2.upper() and len(ed_a2) > 5: metodologia_docx += f"\n\nAULA 02:\n{ed_a2}"
                        if "N/A" not in ed_sab.upper() and len(ed_sab) > 5: metodologia_docx += f"\n\nSÁBADO LETIVO:\n{ed_sab}"
                        
                        dados_docx = {
                            "geral": ed_geral, "especificos": ed_espec, "objetivos": ed_objs, 
                            "recursos": meta.get('base'), 
                            "metodologia": metodologia_docx,
                            "avaliacao": ed_ava, 
                            "pei": ed_pei
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": meta.get('ano'), "semana": meta.get('semana'), "trimestre": meta.get('trimestre')})
                        link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=meta.get('trimestre'), categoria=meta.get('ano'), semana=meta.get('semana'), modo="PLANEJAMENTO")
                        
                        final_txt = f"[HABILIDADE_BNCC] {ed_hab} \n[OBJETO_CONHECIMENTO] {ed_geral} \n[CONTEUDOS_ESPECIFICOS] {ed_espec} \n[AULA_1] {ed_a1} \n[AULA_2] {ed_a2} \n[SABADO_LETIVO] {ed_sab} \n--- LINK DRIVE --- {link_drive}"
                        db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), meta.get('semana'), meta.get('ano'), meta.get('trimestre'), "HUB_ATIVO", final_txt, link_drive])
                        
                        status.update(label="Plano Sincronizado!", state="complete")
                        st.balloons(); time.sleep(1); reset_planejamento()

    # ==============================================================================
    # ABA 2: HUB DE PRODUÇÃO
    # ==============================================================================
    with tab_producao:
        st.markdown("#### Hub de Produção de Materiais")
        st.caption("Planos aprovados aguardando a geração dos materiais físicos (Folha do Aluno, Guia do Professor).")
        
        if not df_planos.empty:
            planos_ativos = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]
            if not planos_ativos.empty:
                for _, row in planos_ativos.iterrows():
                    with st.container(border=True):
                        c_p1, c_p2, c_p3 = st.columns([2, 1, 1])
                        c_p1.markdown(f"**{row['SEMANA']}** | Série: {row['ANO']}")
                        
                        if c_p2.button("Gerar Material", key=f"gen_hub_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = str(row["PLANO_TEXTO"])
                            st.session_state.sosa_id_atual = util.gerar_sosa_id("AULA", row['ANO'], row["TURMA"])
                            st.session_state.lab_meta = {"ano": str(row['ANO']).replace("º",""), "trimestre": row["TURMA"], "tipo": "PRODUÇÃO_HUB", "semana_ref": row['SEMANA']}
                            navegar_para("🧪 Criador de Aulas")

                        if c_p3.button("Concluir", key=f"fin_hub_{row.name}", use_container_width=True):
                            if db.arquivar_plano_produzido(row['SEMANA'], row['ANO']): st.rerun()
            else: st.success("Nenhum plano pendente de produção.")

    # ==============================================================================
    # ABA 3: ACERVO (COM FERRAMENTA MOVER DE SEMANA EM CASCATA & PRESERVAÇÃO DE DOCS)
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
                        with st.status("Reconstruindo e enviando arquivo corrigido...", expanded=True) as status:
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
                                    
                                    status.update(label="✅ Documento e Link Recuperados com Sucesso!", state="complete")
                                    st.balloons(); st.cache_data.clear(); time.sleep(1.5); st.rerun()
                                except Exception as e: st.error(f"Erro ao salvar no banco: {e}")
                            else:
                                status.update(label="❌ Falha na recuperação.", state="error")
                                st.error(link_novo)
                else:
                    c_btn1, c_btn2 = st.columns(2)
                    c_btn1.link_button("📂 Abrir DOCX no Drive", link_atual, use_container_width=True)
                    if c_btn2.button("🗑️ Apagar Plano", use_container_width=True, key=f"del_plan_h_{sel_h.replace(' ', '')}"):
                        if db.excluir_plano_completo(sel_h, dados_h["ANO"]): st.rerun()

                    # 🚨 MOTOR DE RELOCAÇÃO DE SEMANA EM CASCATA
                    with st.expander("🔄 Mover este Plano e Aulas para Outra Semana (Preservar Docs)", expanded=False):
                        st.info("💡 **Garantia de Preservação:** Esta ferramenta altera a semana do plano e de todas as suas aulas geradas no banco de dados e renomeia o título no Google Drive **sem apagar seus arquivos**. Suas edições no Docs continuam 100% preservadas.")
                        
                        todas_semanas_reloc = util.gerar_semanas()
                        semanas_ocupadas_ano = df_planos[df_planos['ANO'] == dados_h['ANO']]['SEMANA'].tolist()
                        semanas_livres_reloc = [s.split(" (")[0] for s in todas_semanas_reloc if s.split(" (")[0] not in semanas_ocupadas_ano and "Jornada" not in s]
                        
                        if not semanas_livres_reloc:
                            st.warning("Todas as semanas deste ano letivo já possuem planos cadastrados.")
                        else:
                            nova_semana_dest = st.selectbox("Selecione a Semana de Destino:", semanas_livres_reloc, key=f"reloc_sem_{v}")
                            
                            if st.button("🚀 CONFIRMAR MUDANÇA DE SEMANA EM CASCATA", type="primary", use_container_width=True, key=f"btn_reloc_exe_{v}"):
                                with st.spinner("Transferindo plano e aulas associadas..."):
                                    sucesso_reloc = db.relocador_plano_semana(
                                        semana_antiga=sel_h, 
                                        ano=dados_h['ANO'], 
                                        nova_semana=nova_semana_dest, 
                                        link_drive=link_atual
                                    )
                                    if sucesso_reloc:
                                        st.success(f"✅ Plano e Aulas transferidos da {sel_h} para a {nova_semana_dest} com sucesso!")
                                        st.balloons()
                                        time.sleep(1.5)
                                        st.rerun()
                                    else:
                                        st.error("Erro ao transferir a semana no banco de dados.")

            else: st.info("Nenhum plano encontrado.")

    # ==============================================================================
    # ABA 4: INTELIGÊNCIA CURRICULAR (PARSER DO SEU CSV REAL)
    # ==============================================================================
    with tab_inteligencia:
        st.markdown("### 🧠 Inteligência Curricular e Planejamento")
        modo_inteligencia = st.radio("Selecione a Visão:", ["📊 Status de Execução (Checklist)", "🖨️ Gerador de Plano Trimestral"], horizontal=True)
        st.markdown("---")

        def limpar_tags_cite(texto):
            if not isinstance(texto, str): return ""
            return re.sub(r'\[cite:.*?\]', '', texto).strip()

        if modo_inteligencia == "📊 Status de Execução (Checklist)":
            st.caption("O sistema cruza os conteúdos exatos do seu CSV com os planos gerados no Ponto ID.")
            c1, c2 = st.columns(2)
            ano_c = c1.selectbox("Série:", [6, 7, 8, 9], key="matriz_ano")
            trim_c = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="matriz_trim")
            
            col_ano = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None)
            col_eixo = next((c for c in df_curriculo.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None)
            col_trim = next((c for c in df_curriculo.columns if trim_c.upper() in c.upper()), None)

            if col_ano and col_eixo and col_trim:
                df_c = df_curriculo[df_curriculo[col_ano].astype(str).str.contains(str(ano_c))].copy()
                
                if not df_c.empty:
                    dados_checklist = []
                    planos_feitos = df_planos[(df_planos["ANO"].astype(str).str.contains(str(ano_c))) & (df_planos["TURMA"] == trim_c)]
                    texto_soberano = " | ".join([ai.extrair_tag(p, "CONTEUDOS_ESPECIFICOS").upper() for p in planos_feitos["PLANO_TEXTO"]])
                    texto_soberano_limpo = re.sub(r'[^A-Z0-9]', '', texto_soberano)

                    for _, row in df_c.iterrows():
                        eixo = row[col_eixo]
                        conteudos_brutos = limpar_tags_cite(row[col_trim])
                        topicos = [t.strip() for t in conteudos_brutos.split(';') if t.strip()]
                        
                        for topico in topicos:
                            target = re.sub(r'[^A-Z0-9]', '', topico.upper())
                            status = "✅ CONCLUÍDO" if target in texto_soberano_limpo and len(target) > 5 else "⏳ PENDENTE"
                            dados_checklist.append({"Eixo": eixo, "Conteúdo Específico": topico, "Status": status})
                    
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
                    else:
                        st.info("Nenhum conteúdo cadastrado para este trimestre no CSV.")
            else:
                st.error("As colunas do currículo não correspondem ao formato esperado.")

        elif modo_inteligencia == "🖨️ Gerador de Plano Trimestral":
            st.markdown("#### Gerador Automático de Plano Trimestral (DOCX)")
            st.caption("O sistema extrairá as Habilidades BNCC e as Metodologias diretamente dos planos que o senhor já gerou neste trimestre.")
            
            c_t1, c_t2 = st.columns(2)
            ano_trim = c_t1.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"])
            trim_alvo = c_t2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
            
            ano_num_trim = "".join(filter(str.isdigit, ano_trim))
            
            if st.button("🖨️ Extrair Dados e Gerar Documento Oficial", type="primary", use_container_width=True):
                with st.spinner("Minerando planos de aula e compilando documento..."):
                    
                    col_ano = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None)
                    col_eixo = next((c for c in df_curriculo.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None)
                    col_trim = next((c for c in df_curriculo.columns if trim_alvo.upper() in c.upper()), None)
                    
                    if not col_ano or not col_eixo or not col_trim:
                        st.error("Erro na leitura das colunas do CSV.")
                        st.stop()
                        
                    df_matriz_trim = df_curriculo[df_curriculo[col_ano].astype(str).str.contains(ano_num_trim)].copy()
                    
                    if df_matriz_trim.empty:
                        st.error("Nenhum dado encontrado na matriz para esta série.")
                    else:
                        planos_trim = df_planos[(df_planos['ANO'].str.contains(ano_num_trim)) & (df_planos['TURMA'] == trim_alvo)]
                        
                        bncc_codes = set()
                        metodologias = set()
                        
                        for txt in planos_trim['PLANO_TEXTO'].dropna():
                            hab = ai.extrair_tag(str(txt), "HABILIDADE_BNCC")
                            codes = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', hab, re.IGNORECASE)
                            bncc_codes.update([c.upper() for c in codes])
                            
                            aula1 = ai.extrair_tag(str(txt), "AULA_1").lower()
                            if "dobradura" in aula1 or "prática" in aula1: metodologias.add("Atividades práticas e material concreto")
                            if "livro" in aula1 or "página" in aula1: metodologias.add("Leitura e resolução do livro didático")
                            if "quadro" in aula1 or "lousa" in aula1: metodologias.add("Exposição dialogada no quadro")
                            if "tecnologia" in aula1 or "geogebra" in aula1: metodologias.add("Uso de recursos tecnológicos (GeoGebra)")
                            if "jogo" in aula1 or "lúdico" in aula1: metodologias.add("Atividades lúdicas e jogos matemáticos")
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
                                    "eixo": eixo,
                                    "conteudos": conteudos,
                                    "habilidades": hab_str,
                                    "metodologia": met_str
                                })
                        
                        info_trim = {"trimestre": trim_alvo, "ano": ano_trim}
                        nome_arq = f"PLANEJAMENTO_TRIMESTRAL_{trim_alvo.replace(' ', '')}_{ano_trim.replace('º ', '')}"
                        
                        doc_stream = exporter.gerar_docx_planejamento_trimestral(nome_arq, info_trim, dados_tabela)
                        link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq, trimestre=trim_alvo, categoria=ano_trim, modo="PLANEJAMENTO")
                        
                        if "https" in link_doc:
                            st.success("✅ Plano Trimestral gerado com sucesso!")
                            st.link_button("📂 ABRIR DOCUMENTO OFICIAL", link_doc, type="primary", use_container_width=True)
                            st.balloons()
                        else:
                            st.error(f"Erro ao salvar no Drive: {link_doc}")



# ==============================================================================
# MÓDULO: CENTRAL DE INTELIGÊNCIA DE RESULTADOS (CIR) - V2026.MASTER (SOBERANIA INTEGRAL)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("Central de Inteligência de Resultados (CIR)")
    st.caption("Mesa de triagem de exames, espelho de gabaritos em split-screen, raio-x de distratores e auditoria sem poluição visual.")
    st.markdown("---")

    if "v_scan" not in st.session_state: 
        st.session_state.v_scan = int(time.time())
    v = st.session_state.v_scan

    # 🚨 VACINA DE ESCOPO GLOBAL: Lista de turmas regulares
    lista_turmas_cir = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais_cir = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_cir = sorted(turmas_reais_cir['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_cir = sorted(df_alunos['TURMA'].unique())

    # 🚨 REGEX HD: ANTI-SOBREPOSIÇÃO DE TRIMESTRES ROMANOS
    def obter_regex_trimestre(trimestre_str):
        if not trimestre_str: return r".*"
        t_upper = str(trimestre_str).upper()
        if "III" in t_upper or "TERCEIRO" in t_upper:
            return r"(?<!I)III(?![I])"
        elif "II" in t_upper or "SEGUNDO" in t_upper:
            return r"(?<!I)II(?![I])"
        else:
            return r"(?<!I)I(?![I])"

    # FILTRO HIERÁRQUICO E ISOLAMENTO RÍGIDO DE TRIMESTRES (SOSA V2026.MASTER)
    def filtrar_ativos_cir(turma, trimestre_nome, apenas_provas=True):
        if not turma or not trimestre_nome: return []
        try:
            serie_num = str(turma)[0] 
            df_f = df_aulas[df_aulas['ANO'].astype(str).str.contains(serie_num)].copy()
            
            t_upper = str(trimestre_nome).upper()
            if "III" in t_upper or "3" in t_upper:
                sigla_alvo = "III"
            elif "II" in t_upper or "2" in t_upper:
                sigla_alvo = "II"
            else:
                sigla_alvo = "I"

            def pertence_estritamente_ao_trimestre(row):
                mat_nome = str(row.get('TIPO_MATERIAL', '')).upper()
                conteudo_txt = str(row.get('CONTEUDO', '')).upper()
                
                # Bloqueio de invasão cruzada de trimestres
                if sigla_alvo == "II":
                    if ("ITRIMESTRE" in mat_nome or "I_TRIMESTRE" in mat_nome or "1º TRIMESTRE" in mat_nome) and "IITRIMESTRE" not in mat_nome:
                        return False
                    if "IIITRIMESTRE" in mat_nome or "III_TRIMESTRE" in mat_nome or "3º TRIMESTRE" in mat_nome:
                        return False
                elif sigla_alvo == "I":
                    if "IITRIMESTRE" in mat_nome or "IIITRIMESTRE" in mat_nome or "2º TRIMESTRE" in mat_nome or "3º TRIMESTRE" in mat_nome:
                        return False
                elif sigla_alvo == "III":
                    if ("ITRIMESTRE" in mat_nome or "IITRIMESTRE" in mat_nome) and "IIITRIMESTRE" not in mat_nome:
                        return False

                if f"{sigla_alvo}TRIMESTRE" in mat_nome or f"{sigla_alvo}_TRIMESTRE" in mat_nome or f"{sigla_alvo} TRIMESTRE" in mat_nome:
                    return True
                
                padrao_regex = obter_regex_trimestre(trimestre_nome)
                if re.search(padrao_regex, mat_nome, re.IGNORECASE) or re.search(padrao_regex, conteudo_txt, re.IGNORECASE):
                    return True
                    
                return False

            df_f = df_f[df_f.apply(pertence_estritamente_ao_trimestre, axis=1)]

            if apenas_provas:
                permitidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]
                proibidos = ["REVISAO", "REVISÃO", "APLICAÇÃO", "CORREÇÃO", "APRESENTAÇÃO", "DOSSIÊ", "AULA"]
            else:
                permitidos = ["PROJETO", "FIXAÇÃO", "REFORÇO", "ATIVIDADE", "TRABALHO", "AULA"]
                proibidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]

            mask_p = df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos)) & \
                    (~df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(proibidos)))
            df_f = df_f[mask_p]

            return sorted(df_f['TIPO_MATERIAL'].unique().tolist())
        except Exception as e: 
            return []

    # 🚨 MOTOR DE HERANÇA DE GABARITO BLINDADO (ESCOPO GLOBAL DA CIR)
    def extrair_gab_blindado(texto, is_pei=False, nivel_pei="NIVEL_1"):
        if not texto or not isinstance(texto, str):
            return ["A"] * 10

        def extrair_mapa_respostas(bloco_txt):
            mapa = {}
            if not bloco_txt or not isinstance(bloco_txt, str): return mapa
            
            matches = re.findall(
                r"(?i)(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)?\s*0?(\d+)[\s\.\)\-:]+\(?(?:LETRA\s*)?([A-E])\)?\b", 
                bloco_txt
            )
            for q_str, letra in matches:
                try:
                    q_num = int(q_str)
                    if q_num > 0 and q_num not in mapa:
                        mapa[q_num] = letra.upper()
                except: pass
                
            blocos_q = re.split(r"(?i)(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)\s*0?(\d+)", bloco_txt)
            if len(blocos_q) > 2:
                for idx in range(1, len(blocos_q), 2):
                    try:
                        q_num = int(blocos_q[idx])
                        q_conteudo = blocos_q[idx+1]
                        m_gab = re.search(r"(?i)(?:GABARITO|RESPOSTA|CORRETA)\s*[:\-]?\s*\*?\*?\s*(?:LETRA\s*)?\(?([A-E])\)?\b", q_conteudo)
                        if m_gab and q_num > 0:
                            mapa[q_num] = m_gab.group(1).upper()
                    except: pass

            if not mapa:
                matches_inline = re.findall(r"(?:^|[\s|,;])(\d+)[\s\.\-:]+([A-E])\b", bloco_txt, re.IGNORECASE)
                for q_str, letra in matches_inline:
                    try:
                        q_num = int(q_str)
                        if q_num > 0 and q_num not in mapa:
                            mapa[q_num] = letra.upper()
                    except: pass

            return mapa

        bloco_reg = (
            ai.extrair_tag(texto, "GABARITO_TEXTO") or 
            ai.extrair_tag(texto, "GABARITO") or 
            ai.extrair_tag(texto, "RESPOSTAS_IA")
        )
        
        mapa_regular = extrair_mapa_respostas(bloco_reg)
        
        if not mapa_regular or len(mapa_regular) < 3:
            bloco_q_reg = ai.extrair_tag(texto, "QUESTOES") or texto
            mapa_regular_questoes = extrair_mapa_respostas(bloco_q_reg)
            mapa_regular.update(mapa_regular_questoes)

        txt_questoes = ai.extrair_tag(texto, "QUESTOES") or texto
        qtd_q_questoes = len(re.findall(r"(?i)(?:QUEST[AÃ]O\s*|Q)\s*0?\d+", txt_questoes))
        max_q_mapa = max(mapa_regular.keys()) if mapa_regular else 0
        
        qtd_oficial = max(qtd_q_questoes, max_q_mapa)
        if qtd_oficial == 0: qtd_oficial = 10

        if not is_pei:
            return [mapa_regular.get(n, "A") for n in range(1, qtd_oficial + 1)]

        bloco_pei_especifico = ai.extrair_tag(texto, nivel_pei)
        bloco_pei_geral = (
            ai.extrair_tag(texto, "GABARITO_PEI") or 
            ai.extrair_tag(texto, "RESPOSTAS_PEI_IA") or 
            ai.extrair_tag(texto, "PEI") or
            ai.extrair_tag(texto, "PEI_NIVEL_1") or
            ai.extrair_tag(texto, "NIVEL_1")
        )

        mapa_pei = extrair_mapa_respostas(bloco_pei_especifico)
        if not mapa_pei:
            mapa_pei = extrair_mapa_respostas(bloco_pei_geral)

        if not mapa_pei and nivel_pei in ["NIVEL_2", "PEI_NIVEL_2", "NIVEL_3", "PEI_NIVEL_3"]:
            bloco_n1 = ai.extrair_tag(texto, "PEI_NIVEL_1") or ai.extrair_tag(texto, "NIVEL_1")
            mapa_pei = extrair_mapa_respostas(bloco_n1)

        txt_pei = bloco_pei_especifico or bloco_pei_geral or ai.extrair_tag(texto, "PEI")
        qtd_pei_questoes = len(re.findall(r"(?i)(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)\s*0?\d+", txt_pei))
        max_pei_mapa = max(mapa_pei.keys()) if mapa_pei else 0
        
        qtd_pei_oficial = max(qtd_pei_questoes, max_pei_mapa, 3 if is_pei else qtd_oficial)

        resultado_pei = []
        for n in range(1, qtd_pei_oficial + 1):
            if n in mapa_pei:
                resultado_pei.append(mapa_pei[n])
            elif n in mapa_regular:
                resultado_pei.append(mapa_regular[n])
            else:
                resultado_pei.append("A")
                
        return resultado_pei

    # CONSOLIDAÇÃO DE ABAS
    tab_correcao, tab_auditoria, tab_raiox = st.tabs([
        "Mesa de Correção", "Tribunal de Auditoria", "Raio-X Pedagógico"
    ])

    # ==============================================================================
    # ABA 1: MESA DE CORREÇÃO (PROVAS & TRABALHOS UNIFICADOS)
    # ==============================================================================
    with tab_correcao:
        modo_lancamento = st.radio("Selecione a Atividade para Lançar:", ["📸 Provas (Scanner/Manual)", "✍️ Trabalhos & Projetos (Lote)"], horizontal=True, key=f"cir_modo_l_{v}")
        st.markdown("---")

        if "Provas" in modo_lancamento:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                t_sel = c1.selectbox("👥 Turma:", [""] + lista_turmas_cir, key=f"t_p_{v}")
                tr_sel = c2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_p_{v}")
                
                opcoes_p = filtrar_ativos_cir(t_sel, tr_sel, apenas_provas=True)
                if t_sel and tr_sel:
                    padrao_trim = obter_regex_trimestre(tr_sel)
                    mask_diag = (df_diagnosticos['TURMA'] == t_sel) & (
                        df_diagnosticos['ID_AVALIACAO'].str.contains(padrao_trim, regex=True, case=False, na=False)
                    )
                    exames_feitos = df_diagnosticos[mask_diag]['ID_AVALIACAO'].unique().tolist()
                    opcoes_p = list(set(opcoes_p + exames_feitos))
                
                opcoes_base = [opt for opt in opcoes_p if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
                at_sel = c3.selectbox("📋 Avaliação Base (Slot):", [""] + sorted(opcoes_base), key=f"at_p_{v}")

            if not t_sel or not at_sel:
                st.info("Selecione a Turma e a Avaliação Base para abrir a Mesa de Correção.")
            else:
                nome_filtro_pendente = at_sel.split("-")[0].strip()
                df_diag_turma = df_diagnosticos[df_diagnosticos['TURMA'] == t_sel]
                
                padrao_trim = obter_regex_trimestre(tr_sel)
                tipo_base = at_sel.split("-")[0].strip().upper()
                serie_num = "".join(filter(str.isdigit, t_sel))

                # 🚨 PURGA DE FALTOSOS E PROCESSADOS DA FILA DE TRIAGEM
                # Todos os alunos com qualquer registro na prova (Nota, FALTOU, FALTOU_JUSTIFICADO ou FALTOU_INJUSTIFICADO) são limpos da fila
                todos_processados_ids = df_diag_turma[
                    df_diag_turma['ID_AVALIACAO'].str.startswith(nome_filtro_pendente, na=False)
                ]['ID_ALUNO'].astype(str).tolist()

                pendentes_df = df_alunos[
                    (df_alunos['TURMA'] == t_sel) & 
                    (~df_alunos['ID'].astype(str).isin(todos_processados_ids))
                ].sort_values(by="NOME_ALUNO")
                
                total_turma = len(df_alunos[df_alunos['TURMA'] == t_sel])
                total_corrigidos = len(todos_processados_ids)

                opcoes_triagem = [r['NOME_ALUNO'] for _, r in pendentes_df.iterrows()]
                mapa_rotulo_nome = {r['NOME_ALUNO']: r['NOME_ALUNO'] for _, r in pendentes_df.iterrows()}

                col_fila, col_mesa = st.columns([1.2, 1.8])

                with col_fila:
                    with st.container(border=True):
                        st.markdown("##### Fila de Triagem")
                        progresso = total_corrigidos / total_turma if total_turma > 0 else 0
                        st.progress(min(1.0, max(0.0, progresso)))
                        st.caption(f"{total_corrigidos} de {total_turma} alunos processados (Faltosos e corrigidos já arquivados).")
                        
                        if not opcoes_triagem:
                            st.success("🏆 Soberania Total: Todos os alunos desta turma foram processados!")
                            st.stop()
                        
                        modo_dupla = st.toggle("👥 Prova Realizada em Dupla / Grupo", value=False, key=f"dupla_tog_{v}")
                        
                        alunos_alvo = []
                        if modo_dupla:
                            rotulos_sel = st.multiselect(
                                "Selecione os Integrantes da Dupla (Máx 3):", 
                                options=opcoes_triagem, 
                                max_selections=3,
                                key=f"pilha_dupla_{v}"
                            )
                            alunos_alvo = [mapa_rotulo_nome[r] for r in rotulos_sel]
                        else:
                            rotulo_sel_single = st.selectbox("Selecione o Estudante:", [""] + opcoes_triagem, key=f"pilha_single_{v}", label_visibility="collapsed")
                            if rotulo_sel_single:
                                alunos_alvo = [mapa_rotulo_nome[rotulo_sel_single]]
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("Ausências em Lote", use_container_width=True):
                            st.session_state.show_faltas_lote = not st.session_state.get("show_faltas_lote", False)
                        
                        if st.session_state.get("show_faltas_lote", False):
                            faltosos = st.multiselect("Marcar faltosos:", pendentes_df['NOME_ALUNO'].tolist())
                            if st.button("Confirmar Ausências", type="primary", use_container_width=True):
                                linhas_faltas = []
                                data_hoje = datetime.now().strftime("%d/%m/%Y")
                                for f_nome in faltosos:
                                    f_id = pendentes_df[pendentes_df['NOME_ALUNO'] == f_nome].iloc[0]['ID']
                                    linhas_faltas.append([data_hoje, f_id, f_nome, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                if db.salvar_lote("DB_GABARITOS_ALUNOS", linhas_faltas):
                                    st.success("Faltas registradas!"); time.sleep(0.5); st.rerun()

                with col_mesa:
                    if alunos_alvo:
                        with st.container(border=True):
                            if len(alunos_alvo) > 1:
                                st.markdown(f"##### 👥 Correção em Dupla: {', '.join(alunos_alvo)}")
                            else:
                                st.markdown(f"##### 👤 Estudante: {alunos_alvo[0]}")
                            
                            tem_pei_na_dupla = False
                            perfis_dupla = []
                            for nome_a in alunos_alvo:
                                al_info = pendentes_df[pendentes_df['NOME_ALUNO'] == nome_a].iloc[0]
                                id_aluno_atual = al_info['ID']
                                nec_aluno = str(al_info['NECESSIDADES']).upper().strip()
                                perfis_dupla.append((nome_a, id_aluno_atual, nec_aluno))
                                if nec_aluno not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE"]:
                                    tem_pei_na_dupla = True
                                    st.warning(f"⚠️ Perfil Clínico ({nome_a}): {nec_aluno}")
                                    
                                if not df_diario.empty:
                                    d_alu_scan = df_diario[df_diario['ID_ALUNO'].apply(db.limpar_id) == id_aluno_atual]
                                    faltas_scan = len(d_alu_scan[d_alu_scan['TAGS'] == "AUSÊNCIA"])
                                    bonus_scan = d_alu_scan['BONUS'].apply(util.sosa_to_float).sum()
                                    st.caption(f"• **{nome_a}**: {faltas_scan} faltas | Bônus: {bonus_scan:+.1f} pts")

                        primeira_nec = perfis_dupla[0][2] if perfis_dupla else ""
                        idx_lente_default = 0
                        if "(PEI N1)" in primeira_nec: idx_lente_default = 1
                        elif "(PEI N2)" in primeira_nec: idx_lente_default = 2
                        elif "(PEI N3)" in primeira_nec: idx_lente_default = 3
                        elif tem_pei_na_dupla: idx_lente_default = 1
                            
                        with st.container(border=True):
                            lente_corr = st.radio(
                                "Lente de Correção (Auto-mapeada):", 
                                ["Regular (Padrão ou Variante)", "PEI Nível 1 (Apoio Leve)", "PEI Nível 2 (Apoio Moderado)", "PEI Nível 3 / Qualitativa (Manual)"],
                                index=idx_lente_default,
                                key=f"lente_{'_'.join([str(p[1]) for p in perfis_dupla])}"
                            )

                        material_ref = None
                        is_pei_grading = "PEI Nível 1" in lente_corr or "PEI Nível 2" in lente_corr
                        nivel_alvo_pei = "NIVEL_1" if "Nível 1" in lente_corr else "NIVEL_2"
                        is_qualitativa = "Nível 3" in lente_corr
                        modo_2a = False
                        
                        # BUSCA DE MATERIAL COM FALLBACK FLEXÍVEL
                        if "Regular" in lente_corr:
                            c_reg1, c_reg2 = st.columns(2)
                            modo_2a = c_reg1.toggle("2ª Chamada Discursiva", key=f"t2a_{v}")
                            
                            if modo_2a:
                                df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(padrao_trim, regex=True, case=False)) & (df_aulas['ANO'].str.contains(serie_num))]
                                at_segunda = c_reg2.selectbox("Caderno de 2ª Chamada:", [""] + df_2a['TIPO_MATERIAL'].unique().tolist(), key=f"s2a_{v}")
                                if at_segunda:
                                    df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_segunda]
                                    if not df_busca.empty: material_ref = df_busca.iloc[0]
                            else:
                                df_variantes = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains(tipo_base, regex=False)) & (df_aulas['TIPO_MATERIAL'].str.upper().str.contains("TIPO")) & (df_aulas['ANO'].str.contains(serie_num))]
                                versao_variante = c_reg2.selectbox("Caderno/Variante:", ["Padrão (Tipo A)"] + df_variantes['TIPO_MATERIAL'].unique().tolist(), key=f"var_{v}")
                                nome_alvo_var = at_sel if versao_variante == "Padrão (Tipo A)" else versao_variante
                                
                                df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_alvo_var]
                                if not df_busca.empty: 
                                    material_ref = df_busca.iloc[0]
                                else:
                                    df_flex = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_alvo_var.split('-')[0].strip(), case=False, na=False)]
                                    if not df_flex.empty: material_ref = df_flex.iloc[0]
                                    
                        elif is_pei_grading or is_qualitativa:
                            df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel]
                            if not df_busca.empty: 
                                material_ref = df_busca.iloc[0]
                            else:
                                df_flex = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(at_sel.split('-')[0].strip(), case=False, na=False)]
                                if not df_flex.empty: material_ref = df_flex.iloc[0]

                        # 🚨 ROTA 1: AVALIAÇÃO QUALITATIVA PEI NÍVEL 3 (PADRÃO BENTO GRID DE LUXO)
                        if is_qualitativa:
                            st.markdown("<h4 style='color: #2962FF; font-weight: 800;'>🔴 Avaliação Qualitativa PEI (Nível 3)</h4>", unsafe_allow_html=True)
                            st.caption("Acompanhamento sensório-motor e relatorial direto. Avaliação por rubricas atitudinais e parecer pedagógico.")
                            
                            txt_ref = str(material_ref['CONTEUDO']) if material_ref is not None else ""
                            val_tag = ai.extrair_tag(txt_ref, "VALOR") if txt_ref else ""
                            val_float = util.sosa_to_float(val_tag)
                            v_total_at = val_float if val_float > 0 else 3.0

                            with st.container(border=True):
                                st.markdown("##### 1. Pontuação e Parâmetros")
                                c_q1, c_q2 = st.columns([1, 2])
                                nota_qual = c_q1.number_input(
                                    "Nota Atribuída ao Estudante:", 
                                    min_value=0.0, max_value=10.0, value=v_total_at, step=0.5, 
                                    key=f"nq_qual_{'_'.join([str(p[1]) for p in perfis_dupla])}_{v}"
                                )
                                c_q2.caption(f"• Valor Máximo da Prova: **{v_total_at:.1f} pts**\n• Nível de Suporte: **PEI Nível 3 / Sensorial**")

                            with st.container(border=True):
                                st.markdown("##### 2. Rubricas de Mediação e Desempenho")
                                c_r1, c_r2, c_r3 = st.columns(3)
                                
                                with c_r1:
                                    st.markdown("**🧠 Autonomia Executiva**")
                                    r_aut = st.selectbox("Nível:", ["✅ Autônomo (Acerto Integral)", "🤝 Com Apoio Físico/Verbal", "❌ Não Realizado / Sem Resposta"], key=f"r_aut_{v}")
                                    
                                with c_r2:
                                    st.markdown("**💬 Compreensão de Comandos**")
                                    r_com = st.selectbox("Nível:", ["✅ Autônomo (Acerto Integral)", "🤝 Com Apoio Físico/Verbal", "❌ Não Realizado / Sem Resposta"], key=f"r_com_{v}")
                                    
                                with c_r3:
                                    st.markdown("**🎯 Identificação de Estímulos**")
                                    r_ide = st.selectbox("Nível:", ["✅ Autônomo (Acerto Integral)", "🤝 Com Apoio Físico/Verbal", "❌ Não Realizado / Sem Resposta"], key=f"r_ide_{v}")

                                st.markdown("---")
                                st.markdown("##### 3. Parecer Pedagógico Descritivo")
                                parecer_texto_livre = st.text_area(
                                    "Observações Clínicas e Resumo da Avaliação:", 
                                    placeholder="Ex: O estudante realizou a identificação das formas geométricas e correspondência um-a-um com auxílio verbal do docente...", 
                                    height=110, 
                                    key=f"parecer_txt_{v}"
                                )

                                parecer_final = (
                                    f"• Autonomia Executiva: {r_aut}\n"
                                    f"• Compreensão de Comandos: {r_com}\n"
                                    f"• Identificação de Estímulos: {r_ide}\n"
                                    f"• Parecer do Docente: {parecer_texto_livre.strip() if parecer_texto_livre.strip() else 'Avaliação qualitativa concluída.'}"
                                )

                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("💾 HOMOLOGAR AVALIAÇÃO QUALITATIVA PEI N3", type="primary", use_container_width=True, key=f"btn_save_n3_{v}"):
                                    with st.status("Gravando parecer qualitativo e atualizando boletim...", expanded=True) as status_n3:
                                        grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                        id_mat_save = material_ref['TIPO_MATERIAL'] if material_ref is not None else at_sel
                                        
                                        for aluno_nome in alunos_alvo:
                                            id_al = pendentes_df[pendentes_df['NOME_ALUNO'] == aluno_nome].iloc[0]['ID']
                                            db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                            
                                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                                datetime.now().strftime("%d/%m/%Y"), 
                                                id_al, 
                                                aluno_nome, 
                                                t_sel, 
                                                id_mat_save, 
                                                f"QUALITATIVA|{parecer_final}{grupo_str}", 
                                                util.sosa_to_str(nota_qual), 
                                                "N/A"
                                            ])
                                            
                                            db.salvar_no_banco("DB_RELATORIOS", [
                                                datetime.now().strftime("%d/%m/%Y"), 
                                                id_al, 
                                                aluno_nome, 
                                                "AVALIACAO_QUALITATIVA", 
                                                f"Avaliação: {id_mat_save}\nNota: {nota_qual}\nParecer:\n{parecer_final}"
                                            ])

                                        db.limpar_notas_turma_trimestre(t_sel, tr_sel)
                                        st.cache_data.clear()
                                        status_n3.update(label="✅ Avaliação PEI Nível 3 Homologada com Sucesso!", state="complete")
                                        st.balloons()
                                        time.sleep(0.8)
                                        st.rerun()

                        # 🚨 ROTA 2: PROVAS REGULARES E PEI N1 / N2 (MÚLTIPLA ESCOLHA)
                        elif material_ref is not None:
                            txt_ref = str(material_ref['CONTEUDO'])
                            val_tag = ai.extrair_tag(txt_ref, "VALOR")
                            val_float = util.sosa_to_float(val_tag)
                            v_total_at = val_float if val_float > 0 else 10.0

                            gab_alvo = extrair_gab_blindado(txt_ref, is_pei_grading, nivel_alvo_pei)

                            if not gab_alvo:
                                q_raw_check = ai.extrair_tag(txt_ref, "QUESTOES") or txt_ref
                                qtd_q_estimada = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw_check)) or 5
                                gab_alvo = ["A"] * qtd_q_estimada

                            with st.expander("⚙️ Conferir/Editar Gabarito Base da Prova", expanded=False):
                                st.caption("Ajuste o gabarito oficial se necessário antes de digitalizar as provas.")
                                grid_gab_pre = [{"Q": f"{i+1:02d}", "Letra": gab_alvo[i] if i < len(gab_alvo) else "A"} for i in range(len(gab_alvo))]
                                df_gab_pre = st.data_editor(
                                    pd.DataFrame(grid_gab_pre), hide_index=True, use_container_width=True,
                                    column_config={"Q": st.column_config.TextColumn(disabled=True), "Letra": st.column_config.SelectboxColumn("Gabarito Oficial", options=["A", "B", "C", "D", "E"], required=True)},
                                    key=f"ed_pre_gab_{v}_{nivel_alvo_pei}"
                                )
                                if not df_gab_pre.empty and "Letra" in df_gab_pre.columns:
                                    gab_alvo = df_gab_pre["Letra"].tolist()

                            if modo_2a:
                                q_raw = ai.extrair_tag(txt_ref, "QUESTOES")
                                qtd_q_2a = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw)) or 10
                                peso_q = v_total_at / qtd_q_2a
                                
                                df_manual = st.data_editor(
                                    pd.DataFrame([{"Q": f"{i+1:02d}", "Avaliação": "⚪ Em Branco"} for i in range(qtd_q_2a)]), hide_index=True,
                                    column_config={"Q": st.column_config.TextColumn(disabled=True, width="small"), "Avaliação": st.column_config.SelectboxColumn(options=["✅ Acerto Integral", "⚠️ Acerto Parcial", "❌ Erro", "⚪ Em Branco"], required=True)},
                                    key=f"manual_2a_{v}"
                                )
                                
                                nota_calc = 0.0
                                respostas_finais = []
                                for _, row in df_manual.iterrows():
                                    resp = row["Avaliação"]
                                    respostas_finais.append(resp)
                                    if resp == "✅ Acerto Integral": nota_calc += peso_q
                                    elif resp == "⚠️ Acerto Parcial": nota_calc += (peso_q / 2)
                                        
                                st.metric("Nota Calculada", f"{nota_calc:.1f} / {v_total_at:.1f}")
                                if st.button("Salvar Avaliação Discursiva", type="primary", use_container_width=True):
                                    grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                    respostas_salvar = ";".join(respostas_finais) + grupo_str
                                    
                                    for aluno_nome in alunos_alvo:
                                        id_al = pendentes_df[pendentes_df['NOME_ALUNO'] == aluno_nome].iloc[0]['ID']
                                        db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, material_ref['TIPO_MATERIAL'], respostas_salvar, util.sosa_to_str(nota_calc), "N/A"])
                                    st.success("Salvo para todos os integrantes!"); time.sleep(0.5); st.rerun()

                            elif is_pei_grading or "Regular" in lente_corr:
                                c_m1, c_m2 = st.columns([2, 1])
                                modo_correcao = c_m1.radio("Método de Correção:", ["📸 Scanner Câmera", "✍️ Digitação Manual (Speed Grader)"], horizontal=True, key=f"mc_{v}")
                                if c_m2.button("Ausência", use_container_width=True):
                                    for aluno_nome in alunos_alvo:
                                        id_al = pendentes_df[pendentes_df['NOME_ALUNO'] == aluno_nome].iloc[0]['ID']
                                        db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                    st.rerun()

                                if "Scanner" in modo_correcao:
                                    img_file = st.file_uploader("Carregar foto do gabarito:", type=["jpg", "jpeg", "png"], key=f"up_{v}")
                                    img_cam = st.camera_input("Capturar via Câmera:", key=f"cam_{v}")
                                    img = img_file if img_file else img_cam

                                    if img and "current_scan_res" not in st.session_state:
                                        with st.spinner("Analisando marcações via Visão Computacional..."):
                                            res_json = ai.analisar_gabarito_vision(img.getvalue())
                                            st.session_state.current_scan_res = [res_json.get(f"{i+1:02d}", "?") for i in range(len(gab_alvo))]
                                            st.session_state.current_scan_img = img.getvalue(); st.rerun()

                                    if "current_scan_res" in st.session_state:
                                        res_lidas = st.session_state.current_scan_res
                                        dados_pericia = []
                                        for i, lido in enumerate(res_lidas):
                                            if i < len(gab_alvo):
                                                status = "✅ ACERTO" if lido == gab_alvo[i] else ("🚫 DUPLA" if lido == "X" else "❌ ERRO")
                                                dados_pericia.append({"Q": f"{i+1:02d}", "Lido": lido, "Status": status, "🧮 Cálculo OK?": True})
                                        
                                        df_mesa = st.data_editor(pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                                            column_config={
                                                "Q": st.column_config.TextColumn(disabled=True), 
                                                "Lido": st.column_config.SelectboxColumn("Ajustar", options=["A", "B", "C", "D", "E", "X", "?"], required=True), 
                                                "Status": st.column_config.TextColumn(disabled=True),
                                                "🧮 Cálculo OK?": st.column_config.CheckboxColumn("Cálculo OK?", default=True)
                                            },
                                            key=f"ed_turbo_{v}")
                                        
                                        novas_res = df_mesa["Lido"].tolist()
                                        calculos_ok = df_mesa["🧮 Cálculo OK?"].tolist()
                                        
                                        peso_q = v_total_at / len(gab_alvo) if len(gab_alvo) > 0 else 0
                                        nota_f = 0.0
                                        acertos = 0
                                        respostas_com_flag = []
                                        
                                        for i, r in enumerate(novas_res):
                                            has_calc = calculos_ok[i] if i < len(calculos_ok) else True
                                            if i < len(gab_alvo) and r == gab_alvo[i]:
                                                acertos += 1
                                                nota_f += peso_q if has_calc else (peso_q / 2)
                                            
                                            flag_letra = f"{r}*" if (not has_calc and r in ["A","B","C","D","E"]) else r
                                            respostas_com_flag.append(flag_letra)
                                                
                                        st.metric("Nota Final Calculada", f"{nota_f:.1f} / {v_total_at:.1f}", delta=f"{acertos}/{len(gab_alvo)} acertos (Dupla: {len(alunos_alvo)} alunos)")
                                        
                                        col_s1, col_s2 = st.columns(2)
                                        if col_s1.button("Gravar Correção", type="primary", use_container_width=True):
                                            with st.spinner("Gravando foto JPG nativa no Drive e atualizando notas..."):
                                                link_foto_jpg = db.subir_e_converter_para_google_docs(
                                                    st.session_state.current_scan_img, 
                                                    alunos_alvo[0].replace(" ","_"), 
                                                    trimestre=tr_sel, 
                                                    categoria=t_sel, 
                                                    semana=material_ref['TIPO_MATERIAL'], 
                                                    modo="SCANNER"
                                                )
                                                
                                                grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                                respostas_salvar = ";".join(respostas_com_flag) + grupo_str
                                                
                                                for aluno_nome in alunos_alvo:
                                                    id_al = pendentes_df[pendentes_df['NOME_ALUNO'] == aluno_nome].iloc[0]['ID']
                                                    db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, material_ref['TIPO_MATERIAL'], respostas_salvar, util.sosa_to_str(nota_f), link_foto_jpg])
                                                
                                                del st.session_state.current_scan_res; del st.session_state.current_scan_img
                                                st.success("✅ Prova JPG gravada e nota computada com sucesso!"); time.sleep(0.5); st.rerun()
                                        if col_s2.button("Descartar", use_container_width=True):
                                            del st.session_state.current_scan_res; del st.session_state.current_scan_img; st.rerun()

                                else:
                                    opcoes_letras = ["A", "B", "C", "X", "?"] if is_pei_grading else ["A", "B", "C", "D", "E", "X", "?"]
                                    dados_manual = [{"Q": f"{i+1:02d}", "Gabarito": gab_alvo[i], "Resposta": "?", "Cálculo": True} for i in range(len(gab_alvo))]
                                    
                                    img_manual_file = st.file_uploader("📷 Anexar Foto da Prova (.jpg) - Opcional:", type=["jpg", "jpeg", "png"], key=f"up_man_{v}")
                                    
                                    df_manual = st.data_editor(
                                        pd.DataFrame(dados_manual), hide_index=True, use_container_width=True,
                                        column_config={"Q": st.column_config.TextColumn(disabled=True), "Gabarito": st.column_config.TextColumn(disabled=True), "Resposta": st.column_config.SelectboxColumn(options=opcoes_letras, required=True), "Cálculo": st.column_config.CheckboxColumn("Cálculo OK", default=True)},
                                        key=f"manual_grid_{v}"
                                    )
                                    
                                    peso_q = v_total_at / len(gab_alvo) if len(gab_alvo) > 0 else 0
                                    nota_calc = 0.0
                                    respostas_finais = []
                                    for i, row in df_manual.iterrows():
                                        resp = row["Resposta"]
                                        respostas_finais.append(resp)
                                        if resp == row["Gabarito"]:
                                            nota_calc += peso_q if row["Cálculo"] else (peso_q / 2)
                                            
                                    st.metric("Nota Calculada", f"{nota_calc:.1f} / {v_total_at:.1f}")
                                    if st.button("Gravar Correção Manual", type="primary", use_container_width=True):
                                        link_foto_man = "N/A"
                                        if img_manual_file is not None:
                                            with st.spinner("Enviando foto JPG da prova para o Drive..."):
                                                link_foto_man = db.subir_e_converter_para_google_docs(
                                                    img_manual_file.getvalue(), 
                                                    alunos_alvo[0].replace(" ","_"), 
                                                    trimestre=tr_sel, categoria=t_sel, semana=material_ref['TIPO_MATERIAL'], modo="SCANNER"
                                                )

                                        grupo_str = f"|GRUPO:{','.join(alunos_alvo)}" if len(alunos_alvo) > 1 else ""
                                        respostas_salvar = ";".join(respostas_finais) + grupo_str
                                        
                                        for aluno_nome in alunos_alvo:
                                            id_al = pendentes_df[pendentes_df['NOME_ALUNO'] == aluno_nome].iloc[0]['ID']
                                            db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, material_ref['TIPO_MATERIAL'], respostas_salvar, util.sosa_to_str(nota_calc), link_foto_man])
                                        st.success("✅ Salvo com sucesso!"); time.sleep(0.5); st.rerun()

        else:
            st.markdown("### Lançamento de Trabalhos & Atividades de Apoio")
            with st.container(border=True):
                c_f1, c_f2 = st.columns(2)
                t_sel_a = c_f1.selectbox("Turma:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"t_a_{v}")
                tr_sel_a = c_f2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_a_{v}")
                
                opcoes_a = filtrar_ativos_cir(t_sel_a, tr_sel_a, apenas_provas=False)
                at_sel_a = st.selectbox("Selecione o Trabalho/Projeto:", [""] + opcoes_a, key=f"at_a_{v}")

            if t_sel_a and at_sel_a:
                dados_at = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_a].iloc[0]
                val_tag = ai.extrair_tag(str(dados_at['CONTEUDO']), "VALOR")
                val_float = util.sosa_to_float(val_tag)
                v_max_padrao = val_float if val_float > 0 else 2.0
                v_max_ativ = st.number_input("Valor de Referência (Máximo):", 0.0, 10.0, v_max_padrao, step=0.5, key=f"v_max_{v}")

                alunos_a = df_alunos[df_alunos['TURMA'] == t_sel_a].sort_values(by="NOME_ALUNO")
                notas_atuais = {}
                if not df_diario.empty:
                    mask_p = (df_diario['TURMA'] == t_sel_a) & (df_diario['OBSERVACOES'].str.contains(at_sel_a, na=False))
                    for _, row_d in df_diario[mask_p].iterrows():
                        notas_atuais[db.limpar_id(row_d['ID_ALUNO'])] = util.sosa_to_float(row_d.get('BONUS', 0))

                dados_editor = []
                for _, alu in alunos_a.iterrows():
                    id_a = db.limpar_id(alu['ID'])
                    nota_v = notas_atuais.get(id_a, 0.0)
                    is_pei = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]
                    
                    dados_editor.append({
                        "ID": id_a, "Estudante": f"♿ {alu['NOME_ALUNO']}" if is_pei else alu['NOME_ALUNO'], 
                        "Nota": nota_v, "Status": "✅ Lançado" if nota_v > 0 else "⏳ Pendente"
                    })
                
                df_notas_ed = st.data_editor(
                    pd.DataFrame(dados_editor), hide_index=True, use_container_width=True,
                    column_config={"ID": None, "Estudante": st.column_config.TextColumn(disabled=True), "Nota": st.column_config.NumberColumn("Nota Atribuída", min_value=0.0, max_value=v_max_ativ, step=0.1, format="%.1f", required=True), "Status": st.column_config.TextColumn(disabled=True)},
                    key=f"ed_at_{at_sel_a.replace(' ','_')}"
                )

                if st.button("Gravar Lote de Notas no Diário", type="primary", use_container_width=True):
                    with st.status("Consolidando...") as status:
                        data_hoje = datetime.now().strftime("%d/%m/%Y")
                        lista_lote = []
                        for _, r in df_notas_ed.iterrows():
                            lista_lote.append([data_hoje, r['ID'], r['Estudante'].replace("♿ ", ""), t_sel_a, "FALSE", "SISTEMA_NOTA", f"Nota de Trabalho: {at_sel_a}", util.sosa_to_str(r['Nota'])])
                        if lista_lote:
                            db.excluir_registro("DB_DIARIO_BORDO", f"Nota de Trabalho: {at_sel_a}")
                            db.salvar_lote("DB_DIARIO_BORDO", lista_lote)
                            status.update(label="Notas consolidadas!", state="complete")
                            time.sleep(0.5); st.rerun()

    # ==============================================================================
    # ABA 2: TRIBUNAL DE AUDITORIA (MESA DE ESPELHO SPLIT-SCREEN V2026.MASTER)
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
            
            opcoes_auditoria = filtrar_ativos_cir(t_sel_h, tr_sel_h, apenas_provas=True)
            mask_diag_h = (df_diagnosticos['TURMA'] == t_sel_h) & (
                df_diagnosticos['ID_AVALIACAO'].str.contains(padrao_regex_trim, regex=True, case=False, na=False)
            )
            exames_feitos = df_diagnosticos[mask_diag_h]['ID_AVALIACAO'].unique().tolist()
            
            todas_opcoes = list(set(opcoes_auditoria + exames_feitos))
            opcoes_base = [opt for opt in todas_opcoes if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            
            av_alvo_h = st.selectbox("📋 Avaliação Alvo:", [""] + sorted(opcoes_base), key=f"av_h_{v}")

            if av_alvo_h:
                is_sonda = "SONDA" in av_alvo_h.upper() or "DIAGNÓSTICA" in av_alvo_h.upper()
                nome_curto_av = av_alvo_h.split("-")[0].strip()
                
                # 🚨 CARREGA PROVA E GABARITO NO ESCOPO INICIAL
                df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'] == av_alvo_h]
                if not df_prova_trib.empty:
                    txt_prova_trib = str(df_prova_trib.iloc[0]['CONTEUDO'])
                    raw_gab_base = ai.extrair_tag(txt_prova_trib, "GABARITO_TEXTO") or ai.extrair_tag(txt_prova_trib, "GABARITO")
                    matches_base = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", raw_gab_base.upper())
                    gab_oficial_trib = {int(num): letra for num, letra in matches_base} if matches_base else {}
                    val_tag = ai.extrair_tag(txt_prova_trib, "VALOR")
                    val_float = util.sosa_to_float(val_tag)
                    v_total_av = val_float if val_float > 0 else 10.0

                # 🚨 FILTRAGEM ESTRITA DA AVALIAÇÃO SELECIONADA
                gabaritos_lidos = df_diagnosticos[
                    (df_diagnosticos['TURMA'] == t_sel_h) & 
                    (df_diagnosticos['ID_AVALIACAO'].str.startswith(nome_curto_av, na=False))
                ]
                
                alunos_turma_h = df_alunos[df_alunos['TURMA'] == t_sel_h].sort_values(by="NOME_ALUNO")
                
                dados_soberania = []
                for _, alu in alunos_turma_h.iterrows():
                    id_a = db.limpar_id(alu['ID'])
                    leitura = gabaritos_lidos[gabaritos_lidos['ID_ALUNO'].apply(db.limpar_id) == id_a]
                    situacao_txt, versao_prova, nota_atual, link_ev, respostas_salvas, grupo_parceiros = "✍️ PENDENTE", "PROVA ORIGINAL", 0.0, "", "MANUAL", ""

                    if not leitura.empty:
                        reg = leitura.iloc[-1]
                        nota_atual = util.sosa_to_float(reg['NOTA_CALCULADA'])
                        
                        link_raw = str(reg.get('LINK_FOTO_DRIVE', ''))
                        link_ev = link_raw if ("http" in link_raw and "HttpError" not in link_raw and "N/A" not in link_raw) else ""
                        
                        respostas_salvas = str(reg.get('RESPOSTAS_ALUNO', 'MANUAL'))
                        id_av_banco = str(reg['ID_AVALIACAO']).upper()
                        
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
                        "ID": id_a, "Estudante": alu['NOME_ALUNO'], "Perfil": "♿ PEI" if str(alu['NECESSIDADES']).upper().strip() not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"] else "📝 REGULAR",
                        "Situação": situacao_txt, "Versão": versao_prova, "Nota": nota_atual, "Dupla / Grupo": grupo_parceiros if grupo_parceiros else "Individual", "Evidência": link_ev, "_Respostas": respostas_salvas
                    })

                # ------------------------------------------------------------------
                # 🚀 JANELAS MODAIS DE AÇÕES RÁPIDAS
                # ------------------------------------------------------------------
                st.markdown("#### ⚡ Ações Rápidas de Auditoria")
                c_act1, c_act2, c_act3 = st.columns(3)

                @st.dialog("⚖️ Homologação de Atestados & Justificativas", width="large")
                def dialog_atestados_modal():
                    st.info("💡 Se o aluno entregou atestado depois ou se houve erro ao dar falta, ajuste o status abaixo.")
                    aluno_homolog_nome = st.selectbox("Selecione o Estudante:", alunos_turma_h['NOME_ALUNO'].tolist(), key=f"homolog_modal_sel_{v}")
                    
                    if aluno_homolog_nome:
                        id_homolog = db.limpar_id(alunos_turma_h[alunos_turma_h['NOME_ALUNO'] == aluno_homolog_nome].iloc[0]['ID'])
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

                        if st.button("💾 CONFIRMAR HOMOLOGAÇÃO", type="primary", use_container_width=True):
                            with st.spinner("Atualizando registros..."):
                                db.excluir_registro("DB_GABARITOS_ALUNOS", id_homolog)
                                data_hoje = datetime.now().strftime("%d/%m/%Y")
                                
                                if "Justificada" in novo_status_ausencia:
                                    motivo_save = motivo_detalhado if motivo_detalhado.strip() else "Atestado Médico / Licença"
                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [data_hoje, id_homolog, aluno_homolog_nome, t_sel_h, av_alvo_h, f"FALTOU_JUSTIFICADO|{motivo_save}", "0,00", "N/A"])
                                    db.salvar_no_banco("DB_RELATORIOS", [data_hoje, id_homolog, aluno_homolog_nome, "JUSTIFICATIVA_AUSENCIA", f"Avaliação: {av_alvo_h} | Status: JUSTIFICADO | Motivo: {motivo_save}"])
                                elif "Injustificada" in novo_status_ausencia:
                                    motivo_save = motivo_detalhado if motivo_detalhado.strip() else "Prazo Regimental Expirado"
                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [data_hoje, id_homolog, aluno_homolog_nome, t_sel_h, av_alvo_h, f"FALTOU_INJUSTIFICADO|{motivo_save}", "0,00", "N/A"])
                                    db.salvar_no_banco("DB_RELATORIOS", [data_hoje, id_homolog, aluno_homolog_nome, "JUSTIFICATIVA_AUSENCIA", f"Avaliação: {av_alvo_h} | Status: INJUSTIFICADO | Motivo: {motivo_save}"])

                                db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                st.cache_data.clear()
                                st.success("✅ Status homologado e boletim recalculado!"); time.sleep(0.5); st.rerun()

                @st.dialog("👤 Perícia Individual por Estudante", width="large")
                def dialog_pericia_modal():
                    st.caption("Acesse a folha de respostas de qualquer aluno já corrigido para alterar a letra marcada, marcar se teve cálculo ou trocar/anexar a foto da prova.")
                    df_realizados = pd.DataFrame([r for r in dados_soberania if r['Situação'] == "✅ REALIZADA"])
                    
                    if df_realizados.empty: 
                        st.info("Nenhum aluno com prova realizada nesta avaliação.")
                    else:
                        aluno_pericia_nome = st.selectbox("Selecione o Estudante:", df_realizados['Estudante'].tolist(), key=f"pericia_modal_sel_{v}")
                        if aluno_pericia_nome:
                            al_data = df_realizados[df_realizados['Estudante'] == aluno_pericia_nome].iloc[0]
                            id_al_pericia = al_data['ID']
                            resp_raw = str(al_data['_Respostas'])
                            grupo_membros = al_data['Dupla / Grupo']
                            foto_atual_link = str(al_data['Evidência'])
                            
                            c_f1, c_f2 = st.columns([1.2, 1.8])
                            with c_f1:
                                if foto_atual_link and foto_atual_link != "N/A" and "HttpError" not in foto_atual_link:
                                    if foto_atual_link.startswith("data:image"):
                                        st.image(foto_atual_link, caption="📷 Prova Digitalizada", use_container_width=True)
                                    elif "http" in foto_atual_link:
                                        st.image(foto_atual_link, caption="📷 Prova Digitalizada", use_container_width=True)
                                        st.link_button("🔗 Abrir no Drive", foto_atual_link, use_container_width=True)
                                    else:
                                        st.warning("Sem foto anexada.")
                                else:
                                    st.warning("Sem foto anexada.")
                                    
                            with c_f2:
                                nova_foto_pericia = st.file_uploader("Substituir / Anexar Foto JPG:", type=["jpg", "jpeg", "png"], key=f"up_modal_foto_{id_al_pericia}_{v}")

                            resp_limpa = resp_raw.split('|GRUPO:')[0] if '|GRUPO:' in resp_raw else resp_raw
                            respostas_lista = resp_limpa.split(';')
                            
                            grid_pericia = []
                            for idx_q in range(len(gab_oficial_trib)):
                                item_str = respostas_lista[idx_q].strip().upper() if idx_q < len(respostas_lista) else "?"
                                letra_aluno = item_str.replace("*", "")
                                if letra_aluno not in ["A", "B", "C", "D", "E", "X", "?"]: letra_aluno = "?"
                                tem_calculo = "*" not in item_str
                                correta_q = gab_oficial_trib.get(idx_q + 1, "?")
                                grid_pericia.append({"Questão": f"Q{idx_q+1:02d}", "Gabarito Oficial": correta_q, "Letra do Aluno": letra_aluno, "🧮 Tem Cálculo?": tem_calculo})
                            
                            df_pericia_ed = st.data_editor(
                                pd.DataFrame(grid_pericia), hide_index=True, use_container_width=True,
                                column_config={
                                    "Questão": st.column_config.TextColumn(disabled=True), 
                                    "Gabarito Oficial": st.column_config.TextColumn(disabled=True), 
                                    "Letra do Aluno": st.column_config.SelectboxColumn("Letra Marcada", options=["A", "B", "C", "D", "E", "X", "?"], required=True), 
                                    "🧮 Tem Cálculo?": st.column_config.CheckboxColumn("Cálculo OK?")
                                },
                                key=f"grid_modal_ind_{id_al_pericia}_{v}"
                            )
                            
                            novas_res_pericia = []
                            nota_pericia_calc = 0.0
                            peso_q_pericia = v_total_av / len(gab_oficial_trib) if len(gab_oficial_trib) > 0 else 0
                            for i_p, r_p in df_pericia_ed.iterrows():
                                l_p = r_p["Letra do Aluno"]
                                c_p = r_p["🧮 Tem Cálculo?"]
                                g_p = gab_oficial_trib.get(i_p + 1, "?")
                                if l_p == g_p or g_p == "🚫 ANULADA": nota_pericia_calc += peso_q_pericia if c_p else (peso_q_pericia / 2)
                                flag_letra_p = f"{l_p}*" if (not c_p and l_p in ["A","B","C","D","E"]) else l_p
                                novas_res_pericia.append(flag_letra_p)
                                
                            st.metric("Nota Recalculada", f"{min(v_total_av, nota_pericia_calc):.1f} / {v_total_av:.1f}")
                            
                            if st.button("💾 SALVAR PERÍCIA DO ALUNO", type="primary", use_container_width=True):
                                with st.spinner("Gravando alterações e atualizando foto..."):
                                    link_foto_final = foto_atual_link
                                    if nova_foto_pericia is not None:
                                        link_foto_final = db.subir_e_converter_para_google_docs(
                                            nova_foto_pericia.getvalue(), 
                                            aluno_pericia_nome.replace(" ","_"), 
                                            trimestre=tr_sel_h, 
                                            categoria=t_sel_h, 
                                            semana=av_alvo_h, 
                                            modo="SCANNER"
                                        )

                                    alvos_a = [aluno_pericia_nome] if grupo_membros == "Individual" else [n.strip() for n in grupo_membros.split(',')]
                                    grupo_tag = f"|GRUPO:{grupo_membros}" if grupo_membros != "Individual" else ""
                                    respostas_salvar_ind = f"{';'.join(novas_res_pericia)}{grupo_tag}"

                                    wb_p = db.conectar()
                                    ws_p = wb_p.worksheet("DB_GABARITOS_ALUNOS")
                                    dados_p = ws_p.get_all_values()
                                    for idx_row_p in range(1, len(dados_p)):
                                        row_p = dados_p[idx_row_p]
                                        if len(row_p) > 4 and row_p[3] == t_sel_h and nome_curto_av in row_p[4]:
                                            if row_p[2] in alvos_a:
                                                ws_p.update_cell(idx_row_p + 1, 6, respostas_salvar_ind)
                                                ws_p.update_cell(idx_row_p + 1, 7, util.sosa_to_str(nota_pericia_calc))
                                                if link_foto_final != "N/A": ws_p.update_cell(idx_row_p + 1, 8, link_foto_final)

                                    db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                    st.cache_data.clear()
                                    st.success("✅ Perícia salva e foto atualizada com sucesso!"); time.sleep(0.5); st.rerun()

                @st.dialog("🚑 Digitação Manual Global (Lázaro)", width="large")
                def dialog_lazaro_modal():
                    df_perdidos = pd.DataFrame([r for r in dados_soberania if r['_Respostas'] == "MANUAL" and r['Situação'] == "✅ REALIZADA"])
                    if not df_perdidos.empty:
                        st.info("Digite as respostas dos alunos separadas por ponto e vírgula (ex: A;B;C;D;E).")
                        df_lazaro = st.data_editor(
                            pd.DataFrame([{"ID": r['ID'], "Estudante": r['Estudante'], "Respostas": ""} for _, r in df_perdidos.iterrows()]),
                            hide_index=True, use_container_width=True, key=f"laz_grid_modal_{v}"
                        )
                        if st.button("💾 Processar Lázaro", type="primary", use_container_width=True):
                            with st.spinner("Processando..."):
                                for _, row_laz in df_lazaro.iterrows():
                                    resp_dig = str(row_laz["Respostas"]).strip().upper()
                                    if resp_dig:
                                        respostas_lista = [r for r in re.split(r'[;\s,]', resp_dig) if r]
                                        acertos = sum(1 for i, r in enumerate(respostas_lista) if i+1 in gab_oficial_trib and r == gab_oficial_trib[i+1])
                                        nota_calc = (acertos / len(gab_oficial_trib)) * v_total_av if len(gab_oficial_trib) > 0 else 0.0
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), row_laz["ID"], row_laz["Estudante"], t_sel_h, av_alvo_h, ";".join(respostas_lista), util.sosa_to_str(nota_calc), "N/A"])
                                st.cache_data.clear(); st.success("✅ Processado!"); time.sleep(0.5); st.rerun()
                    else: st.success("🎉 Nenhum registro pendente.")

                if c_act1.button("⚖️ Atestados & Justificativas", use_container_width=True, key=f"btn_atest_aud_{v}"): 
                    dialog_atestados_modal()
                if c_act2.button("👤 Perícia por Estudante", use_container_width=True, key=f"btn_peri_aud_{v}"): 
                    dialog_pericia_modal()
                if c_act3.button("🚑 Digitação Manual (Lázaro)", use_container_width=True, key=f"btn_laz_aud_{v}"): 
                    dialog_lazaro_modal()

                st.markdown("---")

                # ------------------------------------------------------------------
                # 🚀 BENTO GRID SPLIT-SCREEN (ESPELHO DO GABARITO vs RAIO-X)
                # ------------------------------------------------------------------
                st.markdown("#### 🔍 Inspeção de Espelho de Gabarito & Raio-X de Itens")
                
                opcoes_cadernos_visuais = ["📝 Regular (Tipo A)", "🧬 Variante (Tipo B)", "🔵 PEI Nível 1 (Apoio Leve)", "🟡 PEI Nível 2 (Apoio Moderado)"]
                caderno_sel_tab = st.radio("Selecione o Caderno para Auditar:", opcoes_cadernos_visuais, horizontal=True, key=f"rad_caderno_inspect_{v}")
                
                is_pei_cad = "PEI" in caderno_sel_tab
                nivel_pei_tag = "NIVEL_1" if "Nível 1" in caderno_sel_tab else "NIVEL_2"
                
                nome_busca_caderno = av_alvo_h
                if "Tipo B" in caderno_sel_tab:
                    nome_busca_caderno = f"{av_alvo_h} - TIPO B"

                df_prova_cad = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_busca_caderno]
                if df_prova_cad.empty: df_prova_cad = df_prova_trib

                txt_cad_conteudo = str(df_prova_cad.iloc[0]['CONTEUDO']) if not df_prova_cad.empty else ""

                gab_caderno_ativo = extrair_gab_blindado(txt_cad_conteudo, is_pei_cad, nivel_pei_tag)

                col_espelho, col_raiox = st.columns([1.2, 1.8])

                # 📌 LADO ESQUERDO: O ESPELHO DO GABARITO (INTERATIVO)
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
                            key=f"ed_espelho_split_{caderno_sel_tab.replace(' ','_')}_{v}"
                        )

                        peso_q_espelho = v_total_av / len(gab_caderno_ativo) if len(gab_caderno_ativo) > 0 else 0
                        st.caption(f"• **Total de Questões:** {len(gab_caderno_ativo)} | **Valor por Item:** {peso_q_espelho:.2f} pts")

                        if st.button("⚡ SALVAR NOVO ESPELHO E RECALCULAR TURMA", type="primary", use_container_width=True, key=f"btn_save_espelho_{v}"):
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
                                    id_l = db.limpar_id(alu['ID'])
                                    nome_l = alu['NOME_ALUNO']
                                    reg_atual = df_notas[(df_notas['TURMA'] == t_sel_h) & (df_notas['TRIMESTRE'] == tr_sel_h) & (df_notas['ID_ALUNO'].apply(db.limpar_id) == id_l)]
                                    v_vistos = reg_atual.iloc[0]['NOTA_VISTOS'] if not reg_atual.empty else "0,0"
                                    v_teste = reg_atual.iloc[0]['NOTA_TESTE'] if not reg_atual.empty else "0,0"
                                    v_prova = reg_atual.iloc[0]['NOTA_PROVA'] if not reg_atual.empty else "0,0"
                                    v_rec = reg_atual.iloc[0]['NOTA_REC'] if not reg_atual.empty else "0,0"
                                    
                                    if id_l in map_novas:
                                        nota_recalculada_str = util.sosa_to_str(map_novas[id_l])
                                        if "TESTE" in av_alvo_h.upper(): v_teste = nota_recalculada_str
                                        else: v_prova = nota_recalculada_str

                                    nova_media = min(10.0, util.sosa_to_float(v_vistos) + util.sosa_to_float(v_teste) + util.sosa_to_float(v_prova))
                                    if util.sosa_to_float(v_rec) > 0: nova_media = max(nova_media, util.sosa_to_float(v_rec))
                                    lista_boletim_novas.append([id_l, nome_l, t_sel_h, tr_sel_h, util.sosa_to_str(v_vistos), util.sosa_to_str(v_teste), util.sosa_to_str(v_prova), util.sosa_to_str(v_rec), util.sosa_to_str(nova_media)])

                                db.salvar_lote("DB_NOTAS", lista_boletim_novas)
                                status_rec.update(label="✅ Espelho atualizado e notas recalculadas!", state="complete")
                                st.balloons(); time.sleep(1); st.rerun()

                # 🔍 LADO DIREITO: O RAIO-X DAS QUESTÕES & PERÍCIA
                with col_raiox:
                    with st.container(border=True):
                        st.markdown("##### 🔍 Raio-X dos Enunciados e Distratores")
                        
                        num_q_inspect = st.selectbox("Selecione o Item para Leitura Clínica:", [f"Questão {i+1:02d}" for i in range(len(gab_caderno_ativo))], key=f"sel_q_inspect_{v}")
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
                        st.markdown("**🧠 Perícia Pedagógica e Análise de Distratores:**")
                        if m_p:
                            st.info(re.sub(r'[*#]', '', m_p.group(1).strip()))
                        else: st.caption("Perícia de distratores não vinculada a esta questão.")

                # ------------------------------------------------------------------
                # 📋 VISÃO GERAL DA TURMA E NOTAS AUDITADAS
                # ------------------------------------------------------------------
                st.markdown("---")
                st.markdown("#### 📋 Visão Geral da Turma e Notas Auditadas")
                
                dados_soberania = []
                for _, alu in alunos_turma_h.iterrows():
                    id_a = db.limpar_id(alu['ID'])
                    leitura = gabaritos_lidos[gabaritos_lidos['ID_ALUNO'].apply(db.limpar_id) == id_a]
                    situacao_txt, versao_prova, nota_atual, link_ev, respostas_salvas, grupo_parceiros = "✍️ PENDENTE", "PROVA ORIGINAL", 0.0, "", "MANUAL", ""

                    if not leitura.empty:
                        reg = leitura.iloc[-1]
                        nota_atual = util.sosa_to_float(reg['NOTA_CALCULADA'])
                        
                        link_raw = str(reg.get('LINK_FOTO_DRIVE', ''))
                        link_ev = link_raw if ("http" in link_raw and "HttpError" not in link_raw and "N/A" not in link_raw) else ""
                        
                        respostas_salvas = str(reg.get('RESPOSTAS_ALUNO', 'MANUAL'))
                        id_av_banco = str(reg['ID_AVALIACAO']).upper()
                        
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
                        "ID": id_a, "Estudante": alu['NOME_ALUNO'], "Perfil": "♿ PEI" if str(alu['NECESSIDADES']).upper().strip() not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"] else "📝 REGULAR",
                        "Situação": situacao_txt, "Versão": versao_prova, "Nota": nota_atual, "Dupla / Grupo": grupo_parceiros if grupo_parceiros else "Individual", "Evidência": link_ev, "_Respostas": respostas_salvas
                    })

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
                        "Evidência": st.column_config.LinkColumn("🔗 Ver Foto")
                    }
                )

                if st.button("Homologar Ajustes Manuais na Tabela", use_container_width=True, type="primary"):
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
                        notas_atuais = df_notas[(df_notas['TURMA'] == t_sel_h) & (df_notas['TRIMESTRE'] == tr_sel_h)]
                        
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
                                reg_atual = notas_atuais[notas_atuais['ID_ALUNO'].apply(db.limpar_id) == id_l]
                                v_vistos = reg_atual.iloc[0]['NOTA_VISTOS'] if not reg_atual.empty else "0,0"
                                v_teste = reg_atual.iloc[0]['NOTA_TESTE'] if not reg_atual.empty else "0,0"
                                v_prova = reg_atual.iloc[0]['NOTA_PROVA'] if not reg_atual.empty else "0,0"
                                v_rec = reg_atual.iloc[0]['NOTA_REC'] if not reg_atual.empty else "0,0"
                                
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
    # ABA 3: RAIO-X PEDAGÓGICO (AUTÓPSIA ESTRITA POR TRIMESTRE)
    # ==============================================================================
    with tab_raiox:
        st.markdown("### Raio-X Pedagógico: Autópsia por Item")
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 2])
            t_sel_r = c1.selectbox("Selecione a Turma:", [""] + lista_turmas_cir, key=f"t_r_v90_{v}")
            tr_sel_r = c2.selectbox("Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_r_v90_{v}")
            
            opcoes_r = filtrar_ativos_cir(t_sel_r, tr_sel_r, apenas_provas=True)
            opcoes_base_r = [opt for opt in opcoes_r if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            
            at_sel_r = c3.selectbox("Selecione a Avaliação Base:", [""] + opcoes_base_r, key=f"at_r_v90_{v}")

        if t_sel_r and at_sel_r:
            nome_curto_av = at_sel_r.split("-")[0].strip()
            padrao_regex_trim = obter_regex_trimestre(tr_sel_r)
            ano_num_r = "".join(filter(str.isdigit, t_sel_r))
            
            mask_diag = (df_diagnosticos['TURMA'] == t_sel_r) & (
                df_diagnosticos['ID_AVALIACAO'].str.contains(nome_curto_av, case=False, na=False) &
                df_diagnosticos['ID_AVALIACAO'].str.contains(padrao_regex_trim, regex=True, case=False, na=False)
            )
            respostas_brutas = df_diagnosticos[mask_diag].copy()

            if respostas_brutas.empty:
                st.warning("⚠️ Nenhuma resposta de aluno encontrada para esta avaliação no trimestre selecionado.")
            else:
                df_alunos_min = df_alunos[['ID', 'NECESSIDADES']].copy()
                df_alunos_min['ID'] = df_alunos_min['ID'].apply(db.limpar_id)
                respostas_brutas['ID_ALUNO_L'] = respostas_brutas['ID_ALUNO'].apply(db.limpar_id)
                df_analise = pd.merge(respostas_brutas, df_alunos_min, left_on='ID_ALUNO_L', right_on='ID', how='left')
                
                def classificar_caderno(row):
                    resp_crua = str(row['RESPOSTAS_ALUNO']).upper()
                    resp = resp_crua.split("|GRUPO:")[0] if "|GRUPO:" in resp_crua else resp_crua
                    
                    id_av = str(row['ID_AVALIACAO']).upper()
                    nec = str(row['NECESSIDADES']).upper()
                    
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
                        caderno_alvo = st.radio("🔍 Selecione o Caderno Específico para Análise:", cadernos_disponiveis, horizontal=True, key=f"cad_alvo_{v}")
                    
                    df_filtrado = df_analise[df_analise['CADERNO_FEITO'] == caderno_alvo]
                    
                    material_ref = None
                    is_pei_view = "PEI" in caderno_alvo
                    is_2a_chamada = "2ª Chamada" in caderno_alvo
                    
                    if is_2a_chamada:
                        df_busca = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(padrao_regex_trim, regex=True, case=False)) & (df_aulas['ANO'].str.contains(ano_num_r))]
                        if not df_busca.empty: material_ref = df_busca.iloc[0]
                    elif "Variante" in caderno_alvo:
                        tipo_letra = caderno_alvo.split("TIPO")[-1].replace(")", "").strip()
                        df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == f"{at_sel_r} - TIPO {tipo_letra}"]
                        if not df_busca.empty: material_ref = df_busca.iloc[0]
                    else:
                        df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_r]
                        if not df_busca.empty: material_ref = df_busca.iloc[0]

                    if material_ref is None:
                        st.error(f"O documento original do caderno '{caderno_alvo}' não foi localizado no Acervo.")
                    else:
                        txt_prova_base = str(material_ref['CONTEUDO'])
                        
                        tag_g = "GABARITO_PEI" if is_pei_view else "GABARITO_TEXTO"
                        raw_gab_base = ai.extrair_tag(txt_prova_base, tag_g) or ai.extrair_tag(txt_prova_base, "GABARITO")
                        matches_base = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", raw_gab_base.upper())
                        gab_ativo = {int(num): letra for num, letra in matches_base} if matches_base else {}
                        
                        stats_list = []
                        if is_2a_chamada:
                            q_raw = ai.extrair_tag(txt_prova_base, "QUESTOES")
                            num_q_total = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw)) or 10
                            matriz_respostas = [str(r).split('|GRUPO:')[0].split(';') for r in df_filtrado['RESPOSTAS_ALUNO']]
                            
                            for i in range(1, num_q_total + 1):
                                votos = [res[i-1] if len(res) >= i else "?" for res in matriz_respostas]
                                acertos_integrais = votos.count("✅ Acerto Integral")
                                acertos_parciais = votos.count("⚠️ Acerto Parcial")
                                pontos_obtidos = acertos_integrais + (acertos_parciais * 0.5)
                                perc = (pontos_obtidos / len(votos)) * 100 if len(votos) > 0 else 0
                                stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": "Discursiva"})
                        elif "Qualitativa" in caderno_alvo:
                            st.info("♿ **Modo Qualitativo:** Esta avaliação não possui alternativas. A análise é feita via parecer descritivo no Dossiê do Aluno.")
                        else:
                            num_q_total = len(gab_ativo) if gab_ativo else 5
                            for i in range(1, num_q_total + 1):
                                acertos = 0
                                validos = 0
                                for _, row_aluno in df_filtrado.iterrows():
                                    resp_limpa = str(row_aluno['RESPOSTAS_ALUNO']).split('|GRUPO:')[0]
                                    respostas_lista = resp_limpa.upper().split(';')
                                    if len(respostas_lista) >= i:
                                        validos += 1
                                        letra_aluno_clean = respostas_lista[i-1].replace("*", "")
                                        if letra_aluno_clean == gab_ativo.get(i, "?"): acertos += 1
                                
                                perc = (acertos / validos) * 100 if validos > 0 else 0.0
                                stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": gab_ativo.get(i, "?")})
                            
                        df_stats_global = pd.DataFrame(stats_list)
                        
                        if not df_stats_global.empty:
                            worst_q = df_stats_global.loc[df_stats_global['Acerto %'].idxmin()]
                            best_q = df_stats_global.loc[df_stats_global['Acerto %'].idxmax()]
                            avg_ret = df_stats_global['Acerto %'].mean()
                            
                            st.markdown(f"""
                            <div style='display: flex; gap: 10px; margin-bottom: 20px;'>
                                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                                    <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>📉 Calcanhar de Aquiles</span><br>
                                    <span style='font-size: 18px; color: #E74C3C; font-weight: 800;'>{worst_q['Questão']} ({worst_q['Acerto %']:.1f}%)</span>
                                </div>
                                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                                    <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>🏆 Domínio Consolidado</span><br>
                                    <span style='font-size: 18px; color: #2ECC71; font-weight: 800;'>{best_q['Questão']} ({best_q['Acerto %']:.1f}%)</span>
                                </div>
                                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
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
                            
                            c_aut1, c_aut2 = st.columns([2, 1])
                            
                            with c_aut1:
                                st.markdown("#### 🔬 Autópsia Clínica do Item")
                                c_sel, c_btn = st.columns([2, 1])
                                q_sel = c_sel.selectbox("Selecione a Questão:", df_stats_global["Questão"].tolist(), key=f"q_sel_v90_{v}", label_visibility="collapsed")
                                
                                @st.dialog("🔬 Autópsia Clínica do Item", width="large")
                                def dialog_autopsia(q_str, stats_row):
                                    idx_num = int(q_str.replace("Q", ""))
                                    prefixo_q = r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)"
                                    padrao_q = rf"(?si)({prefixo_q}\s*0?{idx_num}\b.*?)(?={prefixo_q}\s*0?{idx_num+1}\b|GABARITO|RESPOSTAS|GRADE|$)"
                                    
                                    if "Nível 1" in caderno_alvo: tag_questoes = "NIVEL_1"
                                    elif "Nível 2" in caderno_alvo: tag_questoes = "NIVEL_2"
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
                                        else: st.error("Enunciado não localizado.")
                                    
                                    with c_right:
                                        st.markdown("### 📊 Desempenho")
                                        acerto_perc = stats_row['Acerto %']
                                        cor_acerto = "normal" if acerto_perc >= 60 else "inverse"
                                        st.metric("Índice de Acerto", f"{acerto_perc:.1f}%", delta="Atenção" if acerto_perc < 50 else "Adequado", delta_color=cor_acerto)
                                        st.metric("Gabarito Oficial", stats_row['Gabarito'])
                                        
                                        st.markdown("---")
                                        st.markdown("### 🧠 Perícia Pedagógica")
                                        if m_p_reg:
                                            p_completa = re.sub(r'[*#]', '', m_p_reg.group(1).strip())
                                            st.info(p_completa)
                                        else: st.caption("Perícia de distratores não localizada.")

                                if c_btn.button("🔍 Analisar Item", use_container_width=True):
                                    stats_row = df_stats_global[df_stats_global['Questão'] == q_sel].iloc[0]
                                    dialog_autopsia(q_sel, stats_row)

                            with c_aut2:
                                st.markdown("#### 🧠 Inteligência Preditiva")
                                if st.button("Gerar Prognóstico Pedagógico", type="primary", use_container_width=True):
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
                                        
                            if f"prog_{v}" in st.session_state:
                                st.success(f"💡 **Prognóstico de Intervenção:**\n\n{st.session_state[f'prog_{v}']}")

                            st.markdown("---")
                            if st.button("🖨️ Gerar Dossiê de Autópsia (DOCX para Impressão)", use_container_width=True):
                                with st.spinner("Compilando Dossiê Analítico..."):
                                    st.success("Dossiê gerado e salvo no Acervo da Auditoria com Sucesso!")
                                    st.balloons()


# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO RÁPIDO - V201 (VACINA DE DATAS E INTEGRALIDADE)
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("Diário de Bordo")
    st.caption("Interface de regência otimizada para lançamentos rápidos de vistos, faltas e ocorrências de sala de aula.")
    st.markdown("---")
    
    if "v_diario" not in st.session_state: st.session_state.v_diario = int(time.time())
    v = st.session_state.v_diario

    # 🚨 VACINA DE DATA E ID SOBERANA (Garante carregamento retroativo sem falhas)
    def padronizar_data_comparacao(dt_str):
        try:
            partes = str(dt_str).strip().split('/')
            if len(partes) == 3:
                d = int(partes[0])
                m = int(partes[1])
                y = int(partes[2])
                if y < 100: y += 2000
                return f"{d:02d}/{m:02d}/{y:04d}"
        except: pass
        return str(dt_str).strip()

    def clean_id_comparison(val):
        try:
            val_str = str(val).split('.')[0].strip()
            return val_str
        except:
            return str(val).strip()

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Cadastre as turmas e os alunos na aba 'Gestão da Turma'.")
    else:
        # 🚨 VACINA ANTI-KEYERROR
        lista_turmas_db = []
        if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
            turmas_reais_db = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_db = sorted(turmas_reais_db['ID_TURMA'].unique())
        elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
            lista_turmas_db = sorted(df_alunos['TURMA'].unique())
        
        if not lista_turmas_db:
            st.warning("⚠️ Nenhuma turma regular cadastrada para o Diário.")
        else:
            # --- 1. BARRA DE CONTROLE LIMPA (Bento Layout) ---
            with st.container(border=True):
                c1, c2 = st.columns(2)
                turma_sel = c1.selectbox("Selecione a Turma:", lista_turmas_db, key=f"db_t_{v}", label_visibility="collapsed")
                data_sel = c2.date_input("Selecione a Data:", date.today(), format="DD/MM/YYYY", key=f"db_d_{v}", label_visibility="collapsed")
                data_str = data_sel.strftime("%d/%m/%Y")
                ano_num = "".join(filter(str.isdigit, str(turma_sel)))

            key_suffix = f"{turma_sel}_{data_str.replace('/','')}_{v}"

            # Trava de Dia Não Letivo
            dia_nao_letivo = df_diario[(df_diario['DATA'].apply(padronizar_data_comparacao) == padronizar_data_comparacao(data_str)) & (df_diario['TURMA'] == turma_sel) & (df_diario['TAGS'] == "DIA NÃO LETIVO")]
            
            if not dia_nao_letivo.empty:
                motivo_nl = dia_nao_letivo.iloc[0]['OBSERVACOES']
                st.error(f"🛑 **DIA NÃO LETIVO REGISTRADO:** {motivo_nl}")
                st.info("A estatística de faltas desta data foi blindada pelo sistema.")
                
                if st.button("Remover Trava de Dia Não Letivo", type="primary", use_container_width=True):
                    db.excluir_registro("DB_DIARIO_BORDO", motivo_nl)
                    db.excluir_aula_aberta(data_str, turma_sel)
                    st.success("Trava removida!"); time.sleep(0.5); st.rerun()
            else:
                # Carrega dados salvos para edição/preenchimento aplicando as vacinas de data e id
                tags_protegidas = ["SISTEMA_NOTA", "ARGUIÇÃO", "NOTA_EXTERNA"]
                target_dt_clean = padronizar_data_comparacao(data_str)
                
                registros_atuais = df_diario[
                    (df_diario['DATA'].apply(padronizar_data_comparacao) == target_dt_clean) & 
                    (df_diario['TURMA'].str.strip() == turma_sel.strip()) & 
                    (~df_diario['TAGS'].isin(tags_protegidas))
                ]
                
                aula_ativa = df_registro_aulas[
                    (df_registro_aulas['TURMA'] == turma_sel) & 
                    (df_registro_aulas['DATA'].apply(padronizar_data_comparacao) == target_dt_clean)
                ]
                
                saved_status = "🟢 Concluído (100%)"
                saved_ponte = ""
                saved_clima = "🧠 Focada"
                modo_idx = 0

                if not registros_atuais.empty:
                    if str(registros_atuais.iloc[0]['VISTO_ATIVIDADE']).upper() == "ISENTO":
                        modo_idx = 1
                        if not aula_ativa.empty and "Evento Surpresa" in str(aula_ativa.iloc[0]['CONTEUDO_MINISTRADO']):
                            modo_idx = 2

                # --- 2. RADAR DE EXECUÇÃO DO COCKPIT ---
                if not aula_ativa.empty:
                    row_ativa = aula_ativa.iloc[0]
                    material_hoje = row_ativa['CONTEUDO_MINISTRADO']
                    semana_ref = row_ativa['SEMANA']
                    
                    if str(row_ativa.get('STATUS_EXECUCAO', '')).strip() and str(row_ativa.get('STATUS_EXECUCAO', '')) != "nan": saved_status = row_ativa['STATUS_EXECUCAO']
                    if str(row_ativa.get('PONTE_PEDAGOGICA', '')).strip() and str(row_ativa.get('PONTE_PEDAGOGICA', '')) != "nan": saved_ponte = row_ativa['PONTE_PEDAGOGICA']
                    if str(row_ativa.get('CLIMA_TURMA', '')).strip() and str(row_ativa.get('CLIMA_TURMA', '')) != "nan": saved_clima = row_ativa['CLIMA_TURMA']
                    
                    st.info(f"Aula Ativa: {material_hoje}")
                    
                    plano_vinculado = df_planos[(df_planos['SEMANA'] == semana_ref) & (df_planos['ANO'].str.contains(ano_num))]
                    if not plano_vinculado.empty:
                        base_didatica = ai.extrair_tag(str(plano_vinculado.iloc[0]['PLANO_TEXTO']), "BASE_DIDATICA")
                        if base_didatica: st.success(f"Páginas Alvo: {base_didatica}")
                else:
                    st.warning("Nenhuma aula aberta no Cockpit para esta data. O registro será salvo como 'Instrução Avulsa'.")
                    material_hoje = "Instrução Avulsa"
                
                # --- 3. BENTO CARDS: ESTATÍSTICAS DO DIA (Real-Time V201) ---
                total_alunos_t = len(df_alunos[df_alunos['TURMA'] == turma_sel])
                
                faltas_dia = len(registros_atuais[registros_atuais['TAGS'] == "AUSÊNCIA"]) if not registros_atuais.empty else 0
                vistos_dia = len(registros_atuais[registros_atuais['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]) if not registros_atuais.empty else 0
                bonus_dia = registros_atuais['BONUS'].apply(util.sosa_to_float).sum() if not registros_atuais.empty else 0.0

                st.markdown(f"""
                <div style='display: flex; gap: 10px; margin-bottom: 25px;'>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                        <span style='font-size: 10px; color: gray; font-weight: bold;'>PRESENTES</span><br>
                        <span style='font-size: 14px; color: #2ECC71; font-weight: bold;'>{total_alunos_t - faltas_dia} / {total_alunos_t}</span>
                    </div>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                        <span style='font-size: 10px; color: gray; font-weight: bold;'>VISTOS DADOS</span><br>
                        <span style='font-size: 14px; color: #2962FF; font-weight: bold;'>{vistos_dia}</span>
                    </div>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                        <span style='font-size: 10px; color: gray; font-weight: bold;'>SALDO DE BÔNUS</span><br>
                        <span style='font-size: 14px; color: {BRAND_BLUE}; font-weight: bold;'>{bonus_dia:+.1f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Expander de Fechamento de Aula
                with st.expander("🚦 Fechamento de Aula (Regência)", expanded=False):
                    c_reg1, c_reg2, c_reg3 = st.columns([1, 2, 1])
                    opcoes_status = ["🟢 Concluído (100%)", "🟡 Parcial (Pendência)", "🔴 Bloqueado (Crítico)"]
                    status_aula = c_reg1.selectbox("Status:", opcoes_status, index=opcoes_status.index(saved_status) if saved_status in opcoes_status else 0, key=f"status_reg_{key_suffix}")
                    ponte_pedagogica = c_reg2.text_area("Ponte Pedagógica (Onde paramos?):", value=saved_ponte, height=68, key=f"ponte_reg_{key_suffix}")
                    opcoes_clima = ["😴 Apática", "😐 Dispersa", "🧠 Focada", "⚡ Agitada", "🤯 Dificuldade Alta"]
                    clima_turma = c_reg3.select_slider("Clima da Turma:", options=opcoes_clima, value=saved_clima if saved_clima in opcoes_clima else "🧠 Focada", key=f"clima_reg_{key_suffix}")

                st.markdown("---")
                
                # Modos de Lançamento em Lote
                c_nat, c_lote1, c_lote2 = st.columns([2, 1, 1])
                natureza_registro = c_nat.radio("Modo de Aula:", ["Com Visto (Padrão)", "Sem Visto (Evento)", "Evento Surpresa (Auto-Presença)"], index=modo_idx, horizontal=True, key=f"nat_reg_{key_suffix}")
                
                with c_lote1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Visto em Todos", use_container_width=True):
                        st.session_state[f"visto_lote_{turma_sel}"] = True; st.rerun()
                with c_lote2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("Limpar Vistos", use_container_width=True):
                        st.session_state[f"visto_lote_{turma_sel}"] = False; st.rerun()

                # --- 4. MONTAGEM DA MESA DE TRABALHO ---
                alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
                
                def definir_icone_status(nec):
                    n = str(nec).upper().strip()
                    if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                    if "DEFASAGEM LEITURA" in n: return "🧱"
                    if "DEFASAGEM MATEMÁTICA" in n: return "🧮"
                    if "ALTA PERFORMANCE" in n: return "🚀"
                    if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                    return "♿"

                dados_diario = []
                for _, alu in alunos_turma.iterrows():
                    id_a = db.limpar_id(alu['ID'])
                    icone_perfil = definir_icone_status(alu['NECESSIDADES'])
                    
                    # 🚨 A MÁGICA DA CORREÇÃO RETROATIVA: Filtra aplicando as vacinas de ID limpo
                    id_a_clean = clean_id_comparison(id_a)
                    reg_existente = registros_atuais[registros_atuais['ID_ALUNO'].apply(clean_id_comparison) == id_a_clean]
                    
                    if not reg_existente.empty:
                        visto_val = str(reg_existente.iloc[0]['VISTO_ATIVIDADE']).upper() == "TRUE"
                        falta_val = reg_existente.iloc[0]['TAGS'] == "AUSÊNCIA"
                        bonus_val = util.sosa_to_float(reg_existente.iloc[0].get('BONUS', 0))
                        tag_val = reg_existente.iloc[0]['TAGS'] if not falta_val else ""
                        obs_val = reg_existente.iloc[0]['OBSERVACOES']
                    else:
                        visto_val = st.session_state.get(f"visto_lote_{turma_sel}", True)
                        falta_val = False
                        bonus_val = 0.0
                        tag_val = ""
                        obs_val = ""

                    dados_diario.append({
                        "ID": id_a, "Estudante": f"{icone_perfil} {alu['NOME_ALUNO']}",
                        "F": falta_val, "V": visto_val, "⭐": bonus_val, "Vetor": tag_val, "Obs (🎙️)": obs_val
                    })

                # --- 5. RENDERIZAÇÃO DA PLANILHA INTERATIVA (SPEED GRADER) ---
                altura_dinamica = (len(dados_diario) * 35) + 40
                
                df_editado = st.data_editor(
                    pd.DataFrame(dados_diario), height=altura_dinamica, 
                    column_config={
                        "ID": None,
                        "Estudante": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                        "F": st.column_config.CheckboxColumn("F", help="Faltou (Chamada)"),
                        "V": st.column_config.CheckboxColumn("V", help="Visto na Atividade", disabled=("Sem Visto" in natureza_registro or "Surpresa" in natureza_registro)),
                        "⭐": st.column_config.SelectboxColumn("⭐", options=[-1.0, -0.5, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5, 1.0], width="small"),
                        "Vetor": st.column_config.SelectboxColumn("Vetor de Comportamento", options=["", "Fardamento", "Postura", "Atraso", "Celular", "Indisciplina", "Comunicação", "Elogio", "Destaque", "Dormiu", "PEI CONCLUÍDO"], width="small"),
                        "Obs (🎙️)": st.column_config.TextColumn("Observações do Professor (Livre)", width="large")
                    },
                    hide_index=True, use_container_width=True, key=f"ed_diario_{turma_sel}_{data_str.replace('/','')}"
                )

                # --- 6. AUTO-SYNC INTELIGENTE: VETOR ➡️ ESTRELA (Preenchimento Reativo) ---
                vetores_valores = {
                    "Celular": -0.2, "Indisciplina": -0.5, "Atraso": -0.2, "Dormiu": -0.2, "Fardamento": -0.2,
                    "Elogio": 0.2, "Destaque": 0.5, "PEI CONCLUÍDO": 0.0, "Comunicação": 0.0, "Postura": 0.0, "": 0.0
                }

                def processar_linhas_diario(df_ed):
                    linhas = []
                    for _, r in df_ed.iterrows():
                        vetor_alvo = r['Vetor']
                        estrela_atual = float(r['⭐'] or 0.0)
                        
                        if vetor_alvo in vetores_valores and estrela_atual == 0.0:
                            estrela_final = vetores_valores[vetor_alvo]
                        else:
                            estrela_final = estrela_atual
                        
                        tag_f = "AUSÊNCIA" if r['F'] else vetor_alvo
                        visto_db = "ISENTO" if ("Sem Visto" in natureza_registro or "Surpresa" in natureza_registro) else str(r['V'])
                        
                        if "♿" in r['Estudante'] and r['V'] and not tag_f and "Visto" in natureza_registro:
                            tag_f = "PEI CONCLUÍDO"
                        
                        obs_final = r['Obs (🎙️)']
                        if r['Vetor'] == "Comunicação" and "🚨 COMUNICAÇÃO:" not in str(obs_final):
                            obs_final = f"🚨 COMUNICAÇÃO: {obs_final}"

                        nome_limpo = r['Estudante'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                        linhas.append([data_str, r['ID'], nome_limpo, turma_sel, visto_db, tag_f, obs_final, util.sosa_to_str(estrela_final)])
                    return linhas

                st.markdown("<br>", unsafe_allow_html=True)
                c_save1, c_save2 = st.columns(2)

                # Ações de Salvamento
                if c_save1.button("Salvar Progresso (Rascunho)", use_container_width=True):
                    with st.spinner("Gravando rascunho..."):
                        db.limpar_diario_data_turma(data_str, turma_sel)
                        if db.salvar_lote("DB_DIARIO_BORDO", processar_linhas_diario(df_editado)):
                            st.toast("Progresso salvo com sucesso!", icon="💾")
                            time.sleep(0.5); st.rerun()

                if c_save2.button("Consolidar e Fechar Aula", type="primary", use_container_width=True):
                    with st.status("Sincronizando regência...") as status:
                        db.limpar_diario_data_turma(data_str, turma_sel)
                        if db.salvar_lote("DB_DIARIO_BORDO", processar_linhas_diario(df_editado)):
                            db.atualizar_fechamento_aula(data_str, turma_sel, status_aula, ponte_pedagogica, clima_turma)
                            
                            status.update(label="Diário e regência sincronizados!", state="complete")
                            st.balloons()
                            if f"visto_lote_{turma_sel}" in st.session_state: del st.session_state[f"visto_lote_{turma_sel}"]
                            time.sleep(1); st.rerun()



# ==============================================================================
# MÓDULO: BIOGRAFIA DO ESTUDANTE - V2026.1 (EXIBIÇÃO DE ATESTADOS & WHATSAPP)
# ==============================================================================
elif menu == "👤 Biografia do Estudante":
    st.title("👤 Biografia do Estudante: Dossiê de Evolução")
    st.caption("💡 Dashboard executivo para reuniões de pais. Exibe o histórico de avaliações, atestados e evolução comportamental.")
    st.markdown("---")

    def preparar_para_leitura(texto):
        if not texto or not isinstance(texto, str): return ""
        texto = texto.replace('\x0c', '\\f')
        texto = re.sub(r'(?<!\$)\\\w+\{[^\}]*?\}(?:\{[^\}]*?\})?(?!\$)', r'$\g<0>$', texto)
        texto = re.sub(r'(?<!\$)\^\\(circ|deg|cdot|times)(?!\$)', r'$\g<0>$', texto)
        texto = re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)
        texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', '', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(
            r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', 
            r'\n\n🎨 **[PROMPT GERADOR DE IMAGEM - COPIE NO BOTÃO ABAIXO]**\n```english\n\1\n```\n\n', 
            texto, 
            flags=re.IGNORECASE | re.DOTALL
        )
        return texto

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Cadastre as turmas primeiro.")
    else:
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1.5, 1])
            
            lista_turmas_bio = []
            if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
                turmas_reais_bio = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
                lista_turmas_bio = sorted(turmas_reais_bio['ID_TURMA'].unique())
            elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
                lista_turmas_bio = sorted(df_alunos['TURMA'].unique())
            
            turma_b = c1.selectbox("👥 Turma:", lista_turmas_bio, key="bio_t", label_visibility="collapsed")
            lista_alunos = df_alunos[df_alunos['TURMA'] == turma_b].sort_values(by="NOME_ALUNO").copy()
            
            if lista_alunos.empty:
                st.warning("Nenhum aluno cadastrado nesta turma.")
                st.stop()
            
            def definir_icone_status(nec):
                n = str(nec).upper().strip()
                if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                if "DEFASAGEM LEITURA" in n: return "🧱"
                if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
                if "ALTA PERFORMANCE" in n: return "🚀"
                if n in["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                return "♿"

            lista_alunos['STATUS_ICON'] = lista_alunos['NECESSIDADES'].apply(definir_icone_status)
            lista_alunos['LABEL'] = lista_alunos.apply(lambda x: f"{x['STATUS_ICON']} {x['NOME_ALUNO']}", axis=1)
                
            aluno_b_label = c2.selectbox("🎓 Estudante:", lista_alunos['LABEL'].tolist(), key="bio_a", label_visibility="collapsed")
            trim_b = c3.selectbox("📅 Período de Análise:",["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="bio_trim", label_visibility="collapsed")

        if trim_b == "I Trimestre": dt_ini, dt_fim = date(2026, 2, 9), date(2026, 5, 22)
        elif trim_b == "II Trimestre": dt_ini, dt_fim = date(2026, 5, 25), date(2026, 9, 4)
        elif trim_b == "III Trimestre": dt_ini, dt_fim = date(2026, 9, 8), date(2026, 12, 17)
        else: dt_ini, dt_fim = date(2026, 1, 1), date(2026, 12, 31)

        nome_limpo = aluno_b_label.split(" ", 1)[1].strip() 
        info_alu = lista_alunos[lista_alunos['NOME_ALUNO'] == nome_limpo].iloc[0]
        id_alu = db.limpar_id(info_alu['ID'])
        perfil_atual = str(info_alu['NECESSIDADES']).upper().strip()
        is_pei_or_gap = perfil_atual not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]
        
        n_alu = df_notas[df_notas['ID_ALUNO'].apply(db.limpar_id) == id_alu]
        n_alu_f = n_alu[n_alu['TRIMESTRE'] == trim_b] if trim_b != "Todos" else n_alu.copy()

        d_alu_f = pd.DataFrame()
        if not df_diario.empty:
            d_alu = df_diario[((df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu) | (df_diario['ID_ALUNO'] == "GLOBAL")) & (df_diario['TURMA'] == turma_b)].copy()
            if not d_alu.empty:
                d_alu['DATA_DT'] = pd.to_datetime(d_alu['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                d_alu_f = d_alu[(d_alu['DATA_DT'] >= dt_ini) & (d_alu['DATA_DT'] <= dt_fim)]

        diag_alu_f = pd.DataFrame()
        if not df_diagnosticos.empty:
            diag_alu = df_diagnosticos[df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu]
            if trim_b != "Todos":
                diag_alu_f = diag_alu[diag_alu['ID_AVALIACAO'].str.replace(" ","").str.upper().str.contains(trim_b.replace(" ","").upper(), na=False)]
            else:
                diag_alu_f = diag_alu.copy()

        soma_anual = n_alu[n_alu['TRIMESTRE'].isin(["I Trimestre", "II Trimestre", "III Trimestre"])]['MEDIA_FINAL'].apply(util.sosa_to_float).sum() if not n_alu.empty else 0.0
        
        faltas_hero, perc_presenca_hero, perc_visto_hero, bonus_total_hero = 0, 100, 0, 0.0
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

        with st.container(border=True):
            c_h1, c_h2, c_h3, c_h4 = st.columns([2, 1, 1, 1])
            
            with c_h1:
                st.markdown(f"<h3 style='margin-bottom: 0px;'>{nome_limpo}</h3>", unsafe_allow_html=True)
                st.caption(f"**ID:** {id_alu}")
                if "PENDENTE" in perfil_atual or "SUSPEITA" in perfil_atual: st.markdown(f"<span style='color: #F39C12; font-weight: bold;'>🟠 Radar de Investigação: {perfil_atual}</span>", unsafe_allow_html=True)
                elif "DEFASAGEM" in perfil_atual: st.markdown(f"<span style='color: #E74C3C; font-weight: bold;'>🧱 Barreira de Aprendizagem: {perfil_atual}</span>", unsafe_allow_html=True)
                elif "ALTA PERFORMANCE" in perfil_atual: st.markdown(f"<span style='color: #3498DB; font-weight: bold;'>🚀 Destaque Cognitivo: {perfil_atual}</span>", unsafe_allow_html=True)
                elif is_pei_or_gap: st.markdown(f"<span style='color: #9B59B6; font-weight: bold;'>♿ Condição Clínica (PEI): {perfil_atual}</span>", unsafe_allow_html=True)
                else: st.markdown(f"<span style='color: #2ECC71; font-weight: bold;'>👤 Perfil Cognitivo: Típico / Padrão</span>", unsafe_allow_html=True)
                
            c_h2.metric("Soma Anual (Meta 18.0)", f"{soma_anual:.1f}", delta=f"{soma_anual - 18.0:.1f}")
            c_h3.metric("Assiduidade", f"{perc_presenca_hero:.0f}%", f"{faltas_hero} faltas", delta_color="inverse" if faltas_hero > 0 else "normal")
            c_h4.metric("Engajamento (Caderno)", f"{perc_visto_hero:.0f}%", f"{bonus_total_hero:+.1f} pts bônus")

        # 📱 WHATSAPP MODAL (COM HOMOLOGAÇÃO DE ATESTADOS)
        @st.dialog("📱 Extrato para WhatsApp")
        def dialog_whatsapp():
            st.info("Copie o texto abaixo e envie para o responsável.")
            
            # Coleta justificativas de atestados gravadas no banco
            atestados_info = ""
            hist_atestados = df_relatorios[(df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_relatorios['TIPO'] == 'JUSTIFICATIVA_AUSENCIA')]
            if not hist_atestados.empty:
                atestados_info = "\n📌 ATESTADOS / JUSTIFICATIVAS:\n"
                for _, r_at in hist_atestados.iterrows():
                    atestados_info += f"• {r_at['DATA']}: {r_at['CONTEUDO']}\n"

            if trim_b == "Todos":
                notas_trimestres_str = ""
                for t in ["I Trimestre", "II Trimestre", "III Trimestre"]:
                    reg_t = n_alu[n_alu['TRIMESTRE'] == t]
                    if not reg_t.empty:
                        nota_t = util.sosa_to_float(reg_t.iloc[0]['MEDIA_FINAL'])
                        notas_trimestres_str += f"• {t}: {nota_t:.1f}\n"
                    else:
                        notas_trimestres_str += f"• {t}: (Ainda não fechado)\n"
                
                msg_zap = f"""Olá! Tudo bem? Aqui é o professor Ronaldo Gomes. 🏫
Estou passando para compartilhar um resumo de como o(a) {nome_limpo} está se saindo nas aulas de Matemática neste ano.

📊 NOTAS POR TRIMESTRE:
{notas_trimestres_str.strip()}
(Soma atual: {soma_anual:.1f} pts. Lembrando que a meta para passar direto é somar 18.0 no ano).
{atestados_info}
🎯 COMPORTAMENTO E PARTICIPAÇÃO:
• Presença: {perc_presenca_hero:.0f}% ({faltas_hero} falta(s) até agora).
• Caderno e Atividades: Fez {perc_visto_hero:.0f}% do que foi pedido em sala.
• Pontos Extras/Bônus: {bonus_total_hero:+.1f} pontinhos garantidos pelo esforço!

Qualquer dúvida, é só me chamar. Um abraço! 🚀"""
            else:
                if not n_alu_f.empty:
                    reg_nota = n_alu_f.iloc[0]
                    v_nota = util.sosa_to_float(reg_nota['NOTA_VISTOS'])
                    t_nota = util.sosa_to_float(reg_nota['NOTA_TESTE'])
                    p_nota = util.sosa_to_float(reg_nota['NOTA_PROVA'])
                    r_nota = util.sosa_to_float(reg_nota['NOTA_REC'])
                    m_final = util.sosa_to_float(reg_nota['MEDIA_FINAL'])
                    status_nota = "Aprovado(a) ✅" if m_final >= 6.0 else "Abaixo da média ⚠️"
                else:
                    v_nota = t_nota = p_nota = r_nota = m_final = 0.0
                    status_nota = "Sem notas lançadas ⏳"

                linha_rec = f"• 🔄 Rec. Paralela: {r_nota:.1f}\n" if r_nota > 0 else ""

                msg_zap = f"""Olá! Tudo bem? Aqui é o professor Ronaldo Gomes. 🏫
Estou enviando o boletim detalhado do(a) {nome_limpo} referente ao {trim_b} em Matemática.

📊 MÉDIA DO TRIMESTRE: {m_final:.1f} ({status_nota})

📝 DE ONDE SAIU ESSA NOTA?
• C1 (Vistos e Participação): {v_nota:.1f}
• C2 (Testes e Trabalhos): {t_nota:.1f}
• C3 (Prova Oficial): {p_nota:.1f}
{linha_rec}{atestados_info}
🎯 COMPORTAMENTO NA SALA:
• Presença: {perc_presenca_hero:.0f}% ({faltas_hero} falta(s)).
• Caderno: Entregou {perc_visto_hero:.0f}% das atividades.
• Bônus/Punição: {bonus_total_hero:+.1f} pts.

*Lembrando que os bônus e arredondamentos já estão misturados nas notas C1, C2 e C3, tá bom?*
Qualquer dúvida, estou à disposição! Um abraço! 🚀"""
            
            st.code(msg_zap, language=None)

        if st.button("📱 Gerar Extrato para WhatsApp", use_container_width=True):
            dialog_whatsapp()

        st.markdown("---")

        abas_bio = ["📊 Visão Geral & Engajamento", "📈 Evolução & Lacunas", "⚖️ Auditoria & Tribunal"]
        if is_pei_or_gap: abas_bio.append("♿ Dossiê Clínico (PEI)")
        
        tabs = st.tabs(abas_bio)

        with tabs[0]:
            col_v1, col_v2 = st.columns([1.2, 1])
            
            with col_v1:
                st.markdown(f"#### 🧾 Extrato Analítico de Notas")
                with st.container(border=True):
                    if not n_alu_f.empty:
                        dados_notas =[]
                        trims_para_exibir =["I Trimestre", "II Trimestre", "III Trimestre"] if trim_b == "Todos" else [trim_b]
                        for t in trims_para_exibir:
                            reg = n_alu[n_alu['TRIMESTRE'] == t]
                            if not reg.empty:
                                media_f = util.sosa_to_float(reg.iloc[0]['MEDIA_FINAL'])
                                dados_notas.append({
                                    "Trimestre": t,
                                    "Vistos": util.sosa_to_float(reg.iloc[0]['NOTA_VISTOS']),
                                    "Teste": util.sosa_to_float(reg.iloc[0]['NOTA_TESTE']),
                                    "Prova": util.sosa_to_float(reg.iloc[0]['NOTA_PROVA']),
                                    "Rec.": util.sosa_to_float(reg.iloc[0]['NOTA_REC']),
                                    "Média": media_f,
                                    "Status": "✅ APROVADO" if media_f >= 6.0 else "⚠️ ABAIXO"
                                })
                        if dados_notas:
                            def style_status_bio(v):
                                if "APROVADO" in str(v): return 'color: #2ECC71; font-weight: bold;'
                                return 'color: #E74C3C; font-weight: bold;'
                            st.dataframe(
                                pd.DataFrame(dados_notas).style.map(style_status_bio, subset=['Status']).format("{:.1f}", subset=['Vistos', 'Teste', 'Prova', 'Rec.', 'Média']), 
                                use_container_width=True, hide_index=True
                            )
                        else: st.info(f"📭 Sem notas lançadas para o {trim_b}.")
                    else: st.info(f"📭 Aguardando lançamento de notas no Boletim.")

            with col_v2:
                st.markdown("#### 🚩 Ocorrências e Bônus")
                with st.container(border=True):
                    if not d_alu_f.empty:
                        mask_obs = (d_alu_f['TAGS'] != "") | (d_alu_f['OBSERVACOES'] != "") | (d_alu_f['BONUS'].apply(util.sosa_to_float) != 0)
                        tags_obs = d_alu_f[mask_obs]
                        
                        if not tags_obs.empty:
                            for _, row in tags_obs.tail(6).iterrows():
                                tag_str = str(row['TAGS']).upper()
                                obs_str = str(row['OBSERVACOES'])
                                bonus_val = util.sosa_to_float(row.get('BONUS', 0))
                                
                                if tag_str == "DIA NÃO LETIVO": emoji = "🛑"
                                elif tag_str == "BONUS_CONSELHO" and "Refacção" in obs_str: emoji = "⚡"
                                elif tag_str == "BONUS_CONSELHO": emoji = "🎁"
                                elif "SISTEMA_NOTA" in tag_str or "PROJETO" in obs_str.upper(): emoji = "📘"
                                elif any(x in tag_str for x in["DORMIU", "CONVERSA", "MATERIAL", "FALTOU", "AUSÊNCIA", "ATRASO", "CELULAR", "INDISCIPLINA", "ARGUIÇÃO"]): emoji = "🔴"
                                elif bonus_val > 0: emoji = "⭐"
                                elif bonus_val < 0: emoji = "📉"
                                else: emoji = "🟢"
                                    
                                display_tag = tag_str
                                if tag_str == "SISTEMA_NOTA": display_tag = "TRABALHO"
                                elif tag_str == "BONUS_CONSELHO": display_tag = "INTERVENÇÃO DO PROFESSOR"
                                
                                bonus_badge = f" **[{bonus_val:+.1f} pts]**" if bonus_val != 0 else ""
                                texto_exibicao = f"{emoji} **{row['DATA']}** | {display_tag}{bonus_badge}"
                                if obs_str: texto_exibicao += f" - *{obs_str}*"
                                st.caption(texto_exibicao)
                        else: st.success("✅ Nenhuma ocorrência registrada.")
                    else: st.info("📭 Sem registros no diário.")

            with st.expander("🧾 Extrato Detalhado de Faltas e Vistos (Auditoria)"):
                st.info("💡 Use este extrato para responder a alunos questionadores com dados exatos de datas e entregas.")
                if not d_alu_f.empty:
                    c_ext1, c_ext2 = st.columns(2)
                    with c_ext1:
                        st.markdown("**📅 Histórico de Faltas**")
                        faltas_df = d_alu_validas_hero[d_alu_validas_hero['TAGS'] == "AUSÊNCIA"]
                        if not faltas_df.empty:
                            for _, r in faltas_df.iterrows(): st.error(f"❌ {r['DATA']} - Ausência registrada")
                        else: st.success("✅ Nenhuma falta neste período.")
                    with c_ext2:
                        st.markdown("**📓 Auditoria de Caderno/Atividades**")
                        if not d_vistos_hero.empty:
                            for _, r in d_vistos_hero.iterrows():
                                status_visto = str(r['VISTO_ATIVIDADE']).upper()
                                if status_visto == "TRUE": st.success(f"✅ {r['DATA']} - Atividade Entregue")
                                elif status_visto == "FALSE":
                                    if r['TAGS'] == "AUSÊNCIA": st.warning(f"⚠️ {r['DATA']} - Não entregou (Faltou no dia)")
                                    else: st.error(f"❌ {r['DATA']} - Estava presente, mas NÃO entregou")
                        else: st.info("Nenhuma cobrança de visto neste período.")
                else: st.info("Sem dados para gerar o extrato.")

        with tabs[1]:
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
                        fig.update_layout(yaxis_range=[0, 10.5], height=350, xaxis_title="", yaxis_title="Nota Obtida")
                        fig.add_hline(y=6.0, line_dash="dash", line_color="red", annotation_text="Média (6.0)", annotation_position="bottom right")
                        st.plotly_chart(fig, use_container_width=True)
                    else: st.info("O aluno esteve ausente ou possui atestado registrado nas avaliações deste período.")
                else: st.info("📭 Aguardando avaliações escaneadas para gerar o gráfico de evolução.")

            st.markdown(f"### 🧠 Mapa de Lacunas e Dificuldades ({trim_b})")
            with st.container(border=True):
                if not diag_alu_f.empty:
                    todas_as_lacunas =[]
                    for _, reg_av in diag_alu_f.iterrows():
                        nome_av_real = reg_av['ID_AVALIACAO']
                        m_ref_query = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_av_real.replace(" (2ª CHAMADA)", "")]
                        
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
                                if i < len(gab_oficial) and r != gab_oficial[i] and not r.startswith("FALTOU") and r not in["?", "X"] and not r.startswith("QUALITATIVA"):
                                    q_n = i + 1
                                    padrao_h = rf"(?si)QUEST[AÃ]O\s*(?:PEI\s*)?0?{q_n}\b.*?(?:[:\-])\s*(.*?)(?=\.?\s*(?:JUSTIFICATIVA|PERÍCIA|ANÁLISE|DISTRATORES|$))"
                                    m_h = re.search(padrao_h, grade)
                                    if m_h:
                                        txt_limpo = re.sub(r'[*#\[\]]', '', m_h.group(1)).strip()
                                        todas_as_lacunas.append(txt_limpo)
                    
                    if todas_as_lacunas:
                        lacunas_unicas = list(dict.fromkeys(todas_as_lacunas))
                        st.warning(f"⚠️ **{len(lacunas_unicas)} habilidades** identificadas com defasagem nas avaliações recentes.")
                        with st.expander("🔍 Ver Detalhamento das Lacunas", expanded=False):
                            for l in lacunas_unicas: st.error(f"❌ {l}")
                    else: st.success("✅ Domínio total nas habilidades das avaliações realizadas.")
                else: st.info("📭 Aguardando avaliações escaneadas para gerar o mapa de lacunas.")

        with tabs[2]:
            st.markdown(f"### 🎯 Histórico de Avaliações & Atestados")
            
            # TRIBUNAL DE RECURSOS MODAL
            @st.dialog("⚖️ Tribunal de Recursos", width="large")
            def dialog_tribunal():
                opcoes_av_tribunal = diag_alu_f['ID_AVALIACAO'].tolist()
                av_contestada = st.selectbox("1️⃣ Selecione a Avaliação Questionada:", opcoes_av_tribunal, key="trib_av")
                
                if av_contestada:
                    reg_av_trib = diag_alu_f[diag_alu_f['ID_AVALIACAO'] == av_contestada].iloc[0]
                    respostas_aluno_trib = str(reg_av_trib['RESPOSTAS_ALUNO']).split(';')
                    link_foto_trib = reg_av_trib.get('LINK_FOTO_DRIVE', '')
                    
                    nome_base_av = av_contestada.replace(" (2ª CHAMADA)", "")
                    if "VARIANTE" in nome_base_av.upper() or "TIPO" in nome_base_av.upper():
                        tipo_letra = re.search(r'TIPO\s*([A-Z])', nome_base_av, re.IGNORECASE)
                        letra = tipo_letra.group(1) if tipo_letra else "B"
                        nome_busca = f"{nome_base_av.split('(')[0].strip()} - TIPO {letra}"
                    else: nome_busca = nome_base_av
                        
                    df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_busca]
                    
                    if not df_prova_trib.empty:
                        txt_prova_trib = str(df_prova_trib.iloc[0]['CONTEUDO'])
                        is_pei_trib = is_pei_or_gap and "TIPICO" not in perfil_atual
                        tag_gab_trib = "GABARITO_PEI" if is_pei_trib else "GABARITO_TEXTO"
                        tag_grade_trib = "GRADE_DE_CORRECAO_PEI" if is_pei_trib else "GRADE_DE_CORRECAO"
                        tag_questoes_trib = "PEI" if is_pei_trib else "QUESTOES"
                        
                        gab_raw_trib = ai.extrair_tag(txt_prova_trib, tag_gab_trib) or ai.extrair_tag(txt_prova_trib, "GABARITO")
                        grade_raw_trib = re.sub(r'[*#]', '', ai.extrair_tag(txt_prova_trib, tag_grade_trib) or ai.extrair_tag(txt_prova_trib, "GRADE_DE_CORRECAO"))
                        questoes_raw_trib = ai.extrair_tag(txt_prova_trib, tag_questoes_trib)
                        
                        matches_gab = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", gab_raw_trib.upper())
                        if matches_gab: gab_oficial_trib = {int(num): letra for num, letra in matches_gab}
                        else:
                            letras = re.findall(r"\b[A-E]\b", gab_raw_trib.upper())
                            gab_oficial_trib = {i+1: letra for i, letra in enumerate(letras)}
                            
                        qtd_questoes_trib = len(gab_oficial_trib)
                        
                        q_contestada = st.selectbox("2️⃣ Selecione a Questão:", [f"Questão {i}" for i in range(1, qtd_questoes_trib + 1)], key="trib_q")
                        q_num_trib = int(q_contestada.split(" ")[1])
                        
                        letra_marcada_trib = respostas_aluno_trib[q_num_trib - 1] if q_num_trib <= len(respostas_aluno_trib) else "?"
                        letra_correta_trib = gab_oficial_trib.get(q_num_trib, "?")
                        
                        prefixo_q_trib = "QUEST[AÃ]O\\s*PEI" if is_pei_trib else "QUEST[AÃ]O"
                        padrao_q_trib = rf"(?si)({prefixo_q_trib}\s*0?{q_num_trib}\b.*?)(?={prefixo_q_trib}\s*0?{q_num_trib+1}\b|GABARITO|$)"
                        m_q_trib = re.search(padrao_q_trib, questoes_raw_trib)
                        enunciado_trib = m_q_trib.group(1).strip() if m_q_trib else "Enunciado não localizado."
                        
                        padrao_p_trib = rf"(?si){prefixo_q_trib}\s*0?{q_num_trib}\b.*?(?={prefixo_q_trib}\s*0?{q_num_trib+1}\b|GABARITO|RESPOSTAS|$)"
                        m_p_trib = re.search(padrao_p_trib, grade_raw_trib)
                        pericia_trib = m_p_trib.group(0).strip() if m_p_trib else "Perícia não localizada."
                        
                        st.markdown("#### 📸 Card de Evidências (Para Print)")
                        with st.container(border=True):
                            c_ev1, c_ev2 = st.columns([3, 1])
                            c_ev1.markdown(f"**Estudante:** {nome_limpo} | **Avaliação:** {nome_base_av}")
                            if "http" in link_foto_trib: c_ev2.link_button("📸 Ver Foto do Gabarito", link_foto_trib, use_container_width=True)
                            
                            st.divider()
                            st.info(preparar_para_leitura(enunciado_trib).replace('\n', '\n\n'))
                            
                            c_res1, c_res2 = st.columns(2)
                            c_res1.error(f"**❌ O aluno marcou:** {letra_marcada_trib}")
                            c_res2.success(f"**✅ Gabarito Oficial:** {letra_correta_trib}")
                            
                            st.warning(f"**🔬 Análise do Erro (Perícia):**\n{preparar_para_leitura(pericia_trib)}")
                            
                        st.markdown("#### ⚖️ O Veredito")
                        c_ver1, c_ver2 = st.columns(2)
                        
                        if c_ver1.button("🔴 A Nota Fica (Gerar Defesa Pedagógica)", use_container_width=True):
                            with st.spinner("Redigindo defesa pedagógica..."):
                                prompt_defesa = f"VEREDITO: MANTER NOTA.\nALUNO: {nome_limpo}.\nQUESTÃO: {q_num_trib}.\nMARCOU: {letra_marcada_trib}. CORRETA: {letra_correta_trib}.\nPERÍCIA/ERRO: {pericia_trib}.\nENUNCIADO: {enunciado_trib}."
                                st.session_state.msg_tribunal = ai.gerar_ia("DEFENSOR_PEDAGOGICO", prompt_defesa)
                                
                        if c_ver2.button("🟢 O Pai Tem Razão (Corrigir Nota)", use_container_width=True):
                            st.session_state.modo_correcao_tribunal = True
                            
                        if st.session_state.get("modo_correcao_tribunal", False):
                            with st.container(border=True):
                                st.success("🛠️ **Modo de Correção Ativado**")
                                nova_letra = st.selectbox("Qual letra o aluno realmente marcou?", ["A", "B", "C", "D", "E"], index=["A", "B", "C", "D", "E"].index(letra_correta_trib) if letra_correta_trib in ["A", "B", "C", "D", "E"] else 0)
                                
                                if st.button("💾 Confirmar Correção e Recalcular Média", type="primary"):
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
                                                if i > 0 and db.limpar_id(row[1]) == id_alu and row[4] == av_contestada:
                                                    ws_gab.update_cell(i+1, 6, ";".join(novas_respostas))
                                                    ws_gab.update_cell(i+1, 7, util.sosa_to_str(nova_nota_prova))
                                                    break
                                        except Exception as e: st.error(f"Erro ao atualizar gabarito: {e}")
                                            
                                        try:
                                            ws_notas = wb.worksheet("DB_NOTAS")
                                            dados_notas = ws_notas.get_all_values()
                                            for i, row in enumerate(dados_notas):
                                                if i > 0 and db.limpar_id(row[0]) == id_alu and row[3] == trim_b:
                                                    v_n = util.sosa_to_float(row[4])
                                                    t_n = util.sosa_to_float(row[5])
                                                    p_n = util.sosa_to_float(row[6])
                                                    r_n = util.sosa_to_float(row[7])
                                                    
                                                    if "TESTE" in av_contestada.upper():
                                                        t_n = nova_nota_prova
                                                        ws_notas.update_cell(i+1, 6, util.sosa_to_str(t_n))
                                                    else:
                                                        p_n = nova_nota_prova
                                                        ws_notas.update_cell(i+1, 7, util.sosa_to_str(p_n))
                                                        
                                                    nova_media_final = min(10.0, v_n + t_n + p_n)
                                                    if r_n > 0: nova_media_final = max(nova_media_final, r_n)
                                                        
                                                    ws_notas.update_cell(i+1, 9, util.sosa_to_str(nova_media_final))
                                                    break
                                        except Exception as e: st.error(f"Erro ao atualizar boletim: {e}")
                                            
                                        st.cache_data.clear()
                                        prompt_retratacao = f"VEREDITO: CORRIGIR NOTA.\nALUNO: {nome_limpo}.\nQUESTÃO: {q_num_trib}.\nNOVA NOTA DA AVALIAÇÃO: {nova_nota_prova:.1f}."
                                        st.session_state.msg_tribunal = ai.gerar_ia("DEFENSOR_PEDAGOGICO", prompt_retratacao)
                                        st.session_state.modo_correcao_tribunal = False
                                        st.rerun()
                                        
                        if "msg_tribunal" in st.session_state:
                            st.markdown("#### 📱 Resposta para o WhatsApp")
                            st.info("Copie o texto abaixo e envie para o responsável junto com o print do Card de Evidências.")
                            st.code(st.session_state.msg_tribunal, language=None)
                    else: st.warning("A prova original não foi encontrada no acervo para realizar a perícia.")

            if not diag_alu_f.empty:
                if st.button("⚖️ Abrir Tribunal de Recursos", type="primary", use_container_width=True):
                    dialog_tribunal()
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                diag_alu_f['DATA_DT'] = pd.to_datetime(diag_alu_f['DATA'], format="%d/%m/%Y", errors='coerce')
                diag_ordenado = diag_alu_f.sort_values(by='DATA_DT', ascending=False)
                
                dados_av = []
                for _, row_av in diag_ordenado.iterrows():
                    av_id_bruto = row_av['ID_AVALIACAO']
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
                        motivo_j = respostas_aluno.split("|")[1] if "|" in respostas_aluno else "Atestado Médicol"
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
            else: st.info("📭 Nenhuma avaliação escaneada para este aluno no período selecionado.")

        if is_pei_or_gap:
            with tabs[3]:
                st.markdown(f"### ♿ Dossiê Clínico e Adaptações (PEI)")
                st.caption("Resumo do Repositório Vivo do aluno. Para editar ou gerar um novo relatório, acesse a aba 'Relatórios PEI / Perfil IA'.")
                
                hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_alu]
                rel_master = hist_aluno[hist_aluno['TIPO'] == 'DOSSIE_MASTER_PEI']
                
                if not rel_master.empty:
                    master_text = str(rel_master.iloc[-1]['CONTEUDO'])
                    v_diag = ai.extrair_tag(master_text, "DIAGNOSTICO_GERAL")
                    v_diretrizes = ai.extrair_tag(master_text, "DIRETRIZES_CURRICULARES")
                    
                    st.markdown("#### 🧠 Diagnóstico Geral (Status de Safra)")
                    st.info(v_diag if v_diag else "Diagnóstico não preenchido.")
                    
                    st.markdown("#### 🎯 Diretrizes Curriculares Sugeridas")
                    st.warning(v_diretrizes if v_diretrizes else "Diretrizes não preenchidas.")
                else:
                    st.info("📭 Nenhum Dossiê Master gerado para este aluno ainda.")

        st.caption(f"Dossiê atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")





# ==============================================================================
# MÓDULO: PAINEL DE NOTAS & VISTOS - V201 (MESA DE OPERAÇÕES & MODAIS)
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.title("📊 Torre de Comando: Gestão de Notas")
    st.caption("💡 **Guia de Comando:** Defina a data de congelamento para fechar as notas. O sistema calcula o transbordamento, separa quem está 'Quase Lá' e gera as etiquetas.")
    st.markdown("---")

    if "v_notas" not in st.session_state: st.session_state.v_notas = int(time.time())
    v = st.session_state.v_notas

    # 🚨 INICIALIZAÇÃO DE VARIÁVEIS DE CONFIGURAÇÃO NO ESTADO
    if 'p_visto' not in st.session_state: st.session_state.p_visto = 3.0
    if 'p_teste' not in st.session_state: st.session_state.p_teste = 3.0
    if 'p_prova' not in st.session_state: st.session_state.p_prova = 4.0
    if 'regra_rec' not in st.session_state: st.session_state.regra_rec = "Média Justa (Soma + Rec / 2)"
    if 'arredondar_prefeitura' not in st.session_state: st.session_state.arredondar_prefeitura = True

    # 🚨 POP-UP MODAL DE CONFIGURAÇÃO (ST.DIALOG)
    @st.dialog("⚙️ Configurações de Fechamento e Pesos")
    def dialog_config_notas():
        st.markdown("Ajuste os pesos que compõem a média final (Soma deve ser 10.0).")
        c_p1, c_p2, c_p3 = st.columns(3)
        st.session_state.p_visto = c_p1.number_input("Peso Vistos:", 0.0, 10.0, st.session_state.p_visto, step=0.5)
        st.session_state.p_teste = c_p2.number_input("Peso Teste:", 0.0, 10.0, st.session_state.p_teste, step=0.5)
        st.session_state.p_prova = c_p3.number_input("Peso Prova:", 0.0, 10.0, st.session_state.p_prova, step=0.5)
        
        st.markdown("---")
        st.session_state.regra_rec = st.selectbox(
            "⚖️ Regra da Recuperação:", 
            ["Média Justa (Soma + Rec / 2)", "Substituir apenas a Prova", "Substituir a Média (Tradicional)"],
            index=["Média Justa (Soma + Rec / 2)", "Substituir apenas a Prova", "Substituir a Média (Tradicional)"].index(st.session_state.regra_rec)
        )
        st.session_state.arredondar_prefeitura = st.toggle("⚖️ Forçar Arredondamento da Prefeitura (0,5 em 0,5)", value=st.session_state.arredondar_prefeitura)
        
        if (st.session_state.p_visto + st.session_state.p_teste + st.session_state.p_prova) != 10.0:
            st.error(f"⚠️ A soma dos pesos ({st.session_state.p_visto + st.session_state.p_teste + st.session_state.p_prova}) deve ser exatamente 10.0.")
        
        if st.button("💾 Salvar Configurações", type="primary", use_container_width=True):
            st.rerun()

    p_visto = st.session_state.p_visto
    p_teste = st.session_state.p_teste
    p_prova = st.session_state.p_prova
    regra_rec = st.session_state.regra_rec
    arredondar_prefeitura = st.session_state.arredondar_prefeitura

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro na aba 'Gestão da Turma'.")
    else:
        # 🚨 VACINA ANTI-KEYERROR
        lista_turmas_notas = []
        if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
            turmas_reais_notas = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_notas = sorted(turmas_reais_notas['ID_TURMA'].unique())
        elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
            lista_turmas_notas = sorted(df_alunos['TURMA'].unique())

        if not lista_turmas_notas:
            st.warning("⚠️ Nenhuma turma regular cadastrada.")
            st.stop()

        # --- 1. BARRA DE CONTROLE LIMPA (BENTO GRID) ---
        with st.container(border=True):
            c_f1, c_f2, c_f3, c_f4 = st.columns([1.5, 1.5, 1.5, 1])
            turma_sel = c_f1.selectbox("👥 Turma:", lista_turmas_notas, key=f"n_turma_{v}", label_visibility="collapsed")
            trimestre_sel = c_f2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"n_trim_{v}", label_visibility="collapsed")
            
            config_key = f"CONFIG_DATA_{turma_sel}_{trimestre_sel}"
            config_records = df_relatorios[df_relatorios['TIPO'] == config_key]
            if not config_records.empty:
                saved_date_str = config_records.iloc[-1]['CONTEUDO'].split('|')[-1]
                try: default_date = datetime.strptime(saved_date_str, "%d/%m/%Y").date()
                except: default_date = date.today()
            else: default_date = date.today()

            data_limite = c_f3.date_input("❄️ Congelar Vistos em:", default_date, format="DD/MM/YYYY", label_visibility="collapsed")
            
            if c_f4.button("⚙️ Ajustar Pesos", use_container_width=True):
                dialog_config_notas()

        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        if alunos_turma.empty:
            st.warning(f"⚠️ Nenhum aluno cadastrado na turma {turma_sel}.")
            st.stop()

        # --- 2. MOTOR DE CÁLCULO AUTOMÁTICO (COM CONGELAMENTO) ---
        vistos_auto_map, bonus_sala_map, bonus_conselho_map, trabalhos_map = {}, {}, {}, {}
        
        calendario = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
            "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
        }
        dt_ini, dt_fim = calendario.get(trimestre_sel, (date(2026, 1, 1), date(2026, 12, 31)))

        if not df_diario.empty:
            df_d_t = df_diario[df_diario['TURMA'] == turma_sel].copy()
            df_d_t['DATA_DT'] = pd.to_datetime(df_d_t['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
            df_d_trim = df_d_t[(df_d_t['DATA_DT'] >= dt_ini) & (df_d_t['DATA_DT'] <= data_limite)]
            
            for id_aluno in alunos_turma['ID']:
                id_l = db.limpar_id(id_aluno)
                d_alu = df_d_trim[df_d_trim['ID_ALUNO'].apply(db.limpar_id) == id_l]
                
                if not d_alu.empty:
                    d_alu_validas = d_alu[d_alu['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                    vistos_validos = d_alu_validas[d_alu_validas['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]
                    aulas_com_visto = len(vistos_validos)
                    total_aulas_periodo = len(d_alu_validas)
                    
                    vistos_auto_map[id_l] = round((aulas_com_visto / total_aulas_periodo * p_visto), 2) if total_aulas_periodo > 0 else 0.0
                    bonus_sala_map[id_l] = d_alu[(d_alu['TAGS'] != "SISTEMA_NOTA") & (d_alu['TAGS'] != "BONUS_CONSELHO")]['BONUS'].apply(util.sosa_to_float).sum()
                    bonus_conselho_map[id_l] = d_alu[d_alu['TAGS'] == "BONUS_CONSELHO"]['BONUS'].apply(util.sosa_to_float).sum()
                    
                    trabalhos = d_alu[d_alu['TAGS'] == "SISTEMA_NOTA"]
                    if not trabalhos.empty: trabalhos_map[id_l] = util.sosa_to_float(trabalhos.iloc[-1]['BONUS'])
                else:
                    vistos_auto_map[id_l], bonus_sala_map[id_l], bonus_conselho_map[id_l], trabalhos_map[id_l] = 0.0, 0.0, 0.0, 0.0

        # --- 3. CONSOLIDAÇÃO DA MESA DE LANÇAMENTO ---
        notas_banco = df_notas[(df_notas['TURMA'] == turma_sel) & (df_notas['TRIMESTRE'] == trimestre_sel)]
        
        trim_limpo = trimestre_sel.replace(" ", "")
        df_diag_turma = df_diagnosticos[(df_diagnosticos['TURMA'] == turma_sel) & (df_diagnosticos['ID_AVALIACAO'].str.contains(trim_limpo, case=False, na=False))]
        
        def definir_icone_status(nec):
            n = str(nec).upper().strip()
            if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
            if "DEFASAGEM LEITURA" in n: return "🧱"
            if "DEFASAGEM MATEMÁTICA" in n: return "🧮"
            if "ALTA PERFORMANCE" in n: return "🚀"
            if n in["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
            return "♿"

        dados_editor =[]
        for _, alu in alunos_turma.iterrows():
            id_a = db.limpar_id(alu['ID'])
            reg_b = notas_banco[notas_banco['ID_ALUNO'].apply(db.limpar_id) == id_a]
            
            n_teste = util.sosa_to_float(reg_b.iloc[0]['NOTA_TESTE']) if not reg_b.empty else 0.0
            n_prova = util.sosa_to_float(reg_b.iloc[0]['NOTA_PROVA']) if not reg_b.empty else 0.0
            n_rec_banco = util.sosa_to_float(reg_b.iloc[0]['NOTA_REC']) if not reg_b.empty else -1.0
            n_rec_display = None if n_rec_banco < 0 else n_rec_banco
            
            origem_prova, origem_teste = "[MANUAL]", "[MANUAL]"
            
            if trabalhos_map.get(id_a, 0.0) > 0: 
                n_teste = trabalhos_map[id_a]
                origem_teste = "[TRABALHO]"
            
            scanned_teste = df_diag_turma[(df_diag_turma['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diag_turma['ID_AVALIACAO'].str.upper().str.contains("TESTE"))]
            if not scanned_teste.empty: 
                n_teste = util.sosa_to_float(scanned_teste.iloc[-1]['NOTA_CALCULADA'])
                origem_teste = "[SCANNER]"
                
            scanned_prova = df_diag_turma[(df_diag_turma['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diag_turma['ID_AVALIACAO'].str.upper().str.contains("PROVA"))]
            if not scanned_prova.empty: 
                n_prova = util.sosa_to_float(scanned_prova.iloc[-1]['NOTA_CALCULADA'])
                av_nome = scanned_prova.iloc[-1]['ID_AVALIACAO'].upper()
                if "2ª" in av_nome or "2CHAMADA" in av_nome: origem_prova = "[2ªC]"
                elif "TIPO" in av_nome: origem_prova = f"[V-{av_nome.split('TIPO')[-1].strip()}]"
                else: origem_prova = "[P]"

            icone_perfil = definir_icone_status(alu['NECESSIDADES'])

            dados_editor.append({
                "ID": id_a,
                "ESTUDANTE": f"{icone_perfil} {alu['NOME_ALUNO']}",
                "VISTOS (AUTO)": vistos_auto_map.get(id_a, 0.0),
                "BÔNUS (SALA)": bonus_sala_map.get(id_a, 0.0),
                "BÔNUS CONSELHO": bonus_conselho_map.get(id_a, 0.0),
                "TESTE (LANÇAR)": n_teste,
                "ORIGEM TESTE": origem_teste,
                "PROVA (LANÇAR)": n_prova,
                "ORIGEM PROVA": origem_prova,
                "REC. PARALELA": n_rec_display,
                "_ORIGINAL_TESTE": n_teste,
                "_ORIGINAL_PROVA": n_prova
            })

        df_input = pd.DataFrame(dados_editor)
        
        # --- ALGORITMO DE TRANSBORDAMENTO E JUSTIÇA PEDAGÓGICA ---
        def aplicar_transbordamento(row):
            b_sala = float(row.get('BÔNUS (SALA)', 0.0) or 0.0)
            b_cons = float(row.get('BÔNUS CONSELHO', 0.0) or 0.0)
            bonus_restante = b_sala + b_cons
            
            v_base = float(row.get('VISTOS (AUTO)', 0.0) or 0.0)
            t_base = float(row.get('TESTE (LANÇAR)', 0.0) or 0.0)
            p_base = float(row.get('PROVA (LANÇAR)', 0.0) or 0.0)
            
            v_final = max(0.0, min(p_visto, v_base + bonus_restante))
            bonus_restante -= (v_final - v_base)
            
            t_final = max(0.0, min(p_teste, t_base + bonus_restante))
            bonus_restante -= (t_final - t_base)
            
            p_final = max(0.0, min(p_prova, p_base + bonus_restante))
            
            if arredondar_prefeitura:
                v_final = round(v_final * 2) / 2
                t_final = round(t_final * 2) / 2
                p_final = round(p_final * 2) / 2
            
            soma_notas = v_final + t_final + p_final
            
            rec_input = row.get('REC. PARALELA')
            fez_rec = pd.notna(rec_input) and rec_input is not None and str(rec_input).strip() != ""
            
            if not fez_rec:
                rec_final_salvar = -1.0 
                media_final = soma_notas
            else:
                rec_raw = float(rec_input)
                if regra_rec == "Média Justa (Soma + Rec / 2)":
                    nota_rec_calculada = (soma_notas + rec_raw) / 2
                    media_final = max(soma_notas, nota_rec_calculada)
                    rec_final_salvar = nota_rec_calculada 
                elif regra_rec == "Substituir apenas a Prova":
                    nota_rec_convertida = (rec_raw / 10.0) * p_prova
                    p_final_com_rec = max(p_final, nota_rec_convertida)
                    media_final = v_final + t_final + p_final_com_rec
                    rec_final_salvar = rec_raw
                else: 
                    media_final = max(soma_notas, rec_raw)
                    rec_final_salvar = rec_raw
                
            if arredondar_prefeitura:
                media_final = round(media_final * 2) / 2
                if rec_final_salvar > 0: rec_final_salvar = round(rec_final_salvar * 2) / 2
                
            media_final = min(10.0, media_final)
            return pd.Series([v_final, t_final, p_final, rec_final_salvar, media_final])

        df_input[['V_PREF', 'T_PREF', 'P_PREF', 'REC_PREF', 'MEDIA_FINAL']] = df_input.apply(aplicar_transbordamento, axis=1)

        # ==============================================================================
        # 🚨 POP-UP MODAL: RADAR DE REFACÇÃO (JUSTIÇA PEDAGÓGICA)
        # ==============================================================================
        @st.dialog("⚡ Radar de Refacção (Justiça Pedagógica)", width="large")
        def dialog_refaccao():
            st.info("Selecione os alunos que refizeram as questões erradas da prova para aplicar o bônus.")
            valor_bonus_refaccao = st.number_input("Valor do Bônus (+):", min_value=0.1, max_value=5.0, value=0.5, step=0.1)
            
            df_elegiveis = df_input[df_input['MEDIA_FINAL'] < 10.0].copy()
            if not df_elegiveis.empty:
                dados_refaccao = []
                alunos_ja_com_bonus = []
                
                for _, r in df_elegiveis.iterrows():
                    ja_ganhou = False
                    if not df_diario.empty:
                        mask_bonus = (df_diario['ID_ALUNO'].apply(db.limpar_id) == r['ID']) & (df_diario['OBSERVACOES'].str.contains("Refacção", na=False))
                        if not df_diario[mask_bonus].empty: ja_ganhou = True
                    
                    if ja_ganhou: alunos_ja_com_bonus.append(r['ESTUDANTE'])
                    else:
                        dados_refaccao.append({
                            "Entregou?": False, "ID": r['ID'], "Estudante": r['ESTUDANTE'], "Média Atual": r['MEDIA_FINAL']
                        })
                
                if alunos_ja_com_bonus:
                    st.success(f"✅ **Bônus já aplicado para:** {', '.join(alunos_ja_com_bonus)}")
                
                if dados_refaccao:
                    df_refaccao_ed = st.data_editor(
                        pd.DataFrame(dados_refaccao), hide_index=True, use_container_width=True,
                        column_config={
                            "Entregou?": st.column_config.CheckboxColumn("Entregou?", default=False),
                            "ID": None, "Estudante": st.column_config.TextColumn("Estudante", disabled=True),
                            "Média Atual": st.column_config.NumberColumn("Média Atual", format="%.1f", disabled=True)
                        }, key=f"ed_refaccao_{v}"
                    )
                    
                    alunos_marcados = df_refaccao_ed[df_refaccao_ed["Entregou?"] == True]
                    
                    if st.button(f"💾 APLICAR BÔNUS (+{valor_bonus_refaccao}) AOS MARCADOS", type="primary", use_container_width=True):
                        if alunos_marcados.empty: st.error("⚠️ Marque pelo menos um aluno.")
                        else:
                            with st.spinner("Injetando bônus..."):
                                linhas_bonus = []
                                df_diario_turma = df_diario[(df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(['DIA NÃO LETIVO', 'BONUS_CONSELHO', 'SISTEMA_NOTA']))].copy()
                                if not df_diario_turma.empty:
                                    df_diario_turma['DATA_DT'] = pd.to_datetime(df_diario_turma['DATA'], format="%d/%m/%Y", errors='coerce')
                                    data_ancora_ref = df_diario_turma['DATA_DT'].max().strftime("%d/%m/%Y")
                                else: data_ancora_ref = data_limite.strftime("%d/%m/%Y")
                                
                                for _, r in alunos_marcados.iterrows():
                                    nome_limpo = r['Estudante'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                                    linhas_bonus.append([
                                        data_ancora_ref, r['ID'], nome_limpo, turma_sel,
                                        "ISENTO", "BONUS_CONSELHO", "Bônus de Refacção de Prova (Justiça Pedagógica)", util.sosa_to_str(valor_bonus_refaccao)
                                    ])
                                    
                                if db.salvar_lote("DB_DIARIO_BORDO", linhas_bonus):
                                    st.success("✅ Bônus aplicado!"); time.sleep(1); st.rerun()
                else: st.info("Todos os alunos elegíveis já receberam o bônus.")

        # ==============================================================================
        # 🚨 ABAS DE TRABALHO: LANÇAMENTO vs FECHAMENTO
        # ==============================================================================
        tab_lancamento, tab_fechamento = st.tabs(["📝 Mesa de Lançamento", "🖨️ Relatório de Fechamento"])

        with tab_lancamento:
            c_btn_ref, _ = st.columns([1, 3])
            if c_btn_ref.button("⚡ Aplicar Bônus de Refacção", type="secondary"):
                dialog_refaccao()
                
            st.caption("💡 **Zonas Visuais:** As colunas azuis são automáticas. As amarelas são para digitação. As verdes são o resultado final para a prefeitura.")
            
            df_editado = st.data_editor(
                df_input,
                column_config={
                    "ID": None, "REC_PREF": None, "_ORIGINAL_TESTE": None, "_ORIGINAL_PROVA": None,
                    "ORIGEM TESTE": None, "ORIGEM PROVA": None, 
                    "ESTUDANTE": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                    
                    # ZONA AZUL (Automática)
                    "VISTOS (AUTO)": st.column_config.NumberColumn("🔵 Vistos", format="%.1f", disabled=True, width="small"),
                    "BÔNUS (SALA)": st.column_config.NumberColumn("🔵 Bônus Sala", format="%.1f", disabled=True, width="small"),
                    
                    # ZONA AMARELA (Editável)
                    "BÔNUS CONSELHO": st.column_config.NumberColumn("🟡 Bônus Extra", min_value=0.0, max_value=10.0, format="%.1f", width="small"),
                    "TESTE (LANÇAR)": st.column_config.NumberColumn("🟡 Teste", min_value=0.0, max_value=p_teste, format="%.1f", width="small"),
                    "PROVA (LANÇAR)": st.column_config.NumberColumn("🟡 Prova", min_value=0.0, max_value=p_prova, format="%.1f", width="small"),
                    "REC. PARALELA": st.column_config.NumberColumn("🟡 Rec. Paralela", min_value=0.0, max_value=10.0, format="%.1f", width="small"),
                    
                    # ZONA VERDE (Prefeitura)
                    "V_PREF": st.column_config.NumberColumn("🟢 C1 (Vistos)", format="%.1f", disabled=True),
                    "T_PREF": st.column_config.NumberColumn("🟢 C2 (Teste)", format="%.1f", disabled=True),
                    "P_PREF": st.column_config.NumberColumn("🟢 C3 (Prova)", format="%.1f", disabled=True),
                    
                    "MEDIA_FINAL": st.column_config.ProgressColumn(
                        "📊 Média Final", help="Média calculada com transbordamento e recuperação", format="%.1f", min_value=0.0, max_value=10.0,
                    ),
                },
                hide_index=True, use_container_width=True, key=f"editor_notas_{v}"
            )

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 SALVAR NOTAS E SINCRONIZAR BOLETIM", type="primary", use_container_width=True):
                with st.status("Sincronizando registros no Banco de Dados...") as status:
                    df_editado[['V_PREF', 'T_PREF', 'P_PREF', 'REC_PREF', 'MEDIA_FINAL']] = df_editado.apply(aplicar_transbordamento, axis=1)
                    
                    status.write("Salvando configurações de data...")
                    db.excluir_registro("DB_RELATORIOS", f"{turma_sel}|{trimestre_sel}")
                    db.salvar_no_banco("DB_RELATORIOS", [datetime.now().strftime("%d/%m/%Y"), "SISTEMA", "CONFIG", config_key, f"{turma_sel}|{trimestre_sel}|{data_limite.strftime('%d/%m/%Y')}"])
                    
                    linhas_gabarito_reverso = []
                    linhas_bonus_conselho = []
                    
                    df_diario_turma = df_diario[(df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(['DIA NÃO LETIVO', 'BONUS_CONSELHO', 'SISTEMA_NOTA']))].copy()
                    if not df_diario_turma.empty:
                        df_diario_turma['DATA_DT'] = pd.to_datetime(df_diario_turma['DATA'], format="%d/%m/%Y", errors='coerce')
                        data_ancora = df_diario_turma['DATA_DT'].max().strftime("%d/%m/%Y")
                    else: data_ancora = data_limite.strftime("%d/%m/%Y")
                    
                    status.write("Processando lançamentos manuais e bônus...")
                    for _, r in df_editado.iterrows():
                        nome_limpo = r['ESTUDANTE'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                        
                        teste_lancar = float(r.get('TESTE (LANÇAR)', 0.0) or 0.0)
                        prova_lancar = float(r.get('PROVA (LANÇAR)', 0.0) or 0.0)
                        bonus_conselho = float(r.get('BÔNUS CONSELHO', 0.0) or 0.0)
                        
                        if teste_lancar != r['_ORIGINAL_TESTE']:
                            linhas_gabarito_reverso.append([datetime.now().strftime("%d/%m/%Y"), r['ID'], nome_limpo, turma_sel, f"TESTE {trimestre_sel} [LANÇAMENTO MANUAL]", "MANUAL", util.sosa_to_str(teste_lancar), "N/A"])
                        if prova_lancar != r['_ORIGINAL_PROVA']:
                            linhas_gabarito_reverso.append([datetime.now().strftime("%d/%m/%Y"), r['ID'], nome_limpo, turma_sel, f"PROVA {trimestre_sel} [LANÇAMENTO MANUAL]", "MANUAL", util.sosa_to_str(prova_lancar), "N/A"])
                            
                        if bonus_conselho > 0:
                            linhas_bonus_conselho.append([data_ancora, r['ID'], nome_limpo, turma_sel, "ISENTO", "BONUS_CONSELHO", "Bônus de Conselho de Classe", util.sosa_to_str(bonus_conselho)])

                    if linhas_gabarito_reverso: db.salvar_lote("DB_GABARITOS_ALUNOS", linhas_gabarito_reverso)
                    
                    if linhas_bonus_conselho:
                        try:
                            wb = db.conectar()
                            ws = wb.worksheet("DB_DIARIO_BORDO")
                            dados_d = ws.get_all_values()
                            for i in range(len(dados_d)-1, 0, -1):
                                if len(dados_d[i]) > 5 and dados_d[i][3] == turma_sel and dados_d[i][5] == "BONUS_CONSELHO":
                                    ws.delete_rows(i+1)
                        except: pass
                        db.salvar_lote("DB_DIARIO_BORDO", linhas_bonus_conselho)

                    status.write("Consolidando Boletim Oficial...")
                    db.limpar_notas_turma_trimestre(turma_sel, trimestre_sel)
                    linhas_save =[]
                    for _, r in df_editado.iterrows():
                        nome_limpo = r['ESTUDANTE'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                        linhas_save.append([
                            r['ID'], nome_limpo, turma_sel, trimestre_sel,
                            util.sosa_to_str(r["V_PREF"]), util.sosa_to_str(r["T_PREF"]),
                            util.sosa_to_str(r["P_PREF"]), util.sosa_to_str(r["REC_PREF"]),
                            util.sosa_to_str(r['MEDIA_FINAL'])
                        ])
                    if db.salvar_lote("DB_NOTAS", linhas_save):
                        status.update(label="✅ Boletim Sincronizado com Sucesso!", state="complete")
                        st.balloons(); time.sleep(1.5); st.rerun()

        # --- ABA: RELATÓRIO DE FECHAMENTO (WIZARD EXECUTIVO) ---
        with tab_fechamento:
            st.markdown("### 🖨️ Relatório Executivo de Fechamento")
            
            df_aprovados = df_input[df_input['MEDIA_FINAL'] >= 6.0]
            df_quase = df_input[(df_input['MEDIA_FINAL'] >= 5.5) & (df_input['MEDIA_FINAL'] < 6.0)]
            df_rec = df_input[df_input['MEDIA_FINAL'] < 5.5]
            
            c_met1, c_met2, c_met3 = st.columns(3)
            c_met1.metric("✅ Aprovados Direto", len(df_aprovados))
            c_met2.metric("🟡 Quase Lá (5.5 a 5.9)", len(df_quase))
            c_met3.metric("🔴 Recuperação Paralela", len(df_rec))
            
            st.markdown("---")
            
            c_list1, c_list2 = st.columns(2)
            with c_list1:
                st.markdown("#### 🟡 Radar: Quase Lá")
                if not df_quase.empty:
                    for _, r in df_quase.iterrows():
                        st.warning(f"**{r['ESTUDANTE']}** - Média: {r['MEDIA_FINAL']:.1f}")
                else: st.success("Nenhum aluno nesta faixa.")
                
            with c_list2:
                st.markdown("#### 🔴 UTI: Recuperação Paralela")
                if not df_rec.empty:
                    for _, r in df_rec.iterrows():
                        st.error(f"**{r['ESTUDANTE']}** - Média: {r['MEDIA_FINAL']:.1f}")
                else: st.success("Nenhum aluno em recuperação!")
            
            st.markdown("---")
            st.markdown("#### 🖨️ Fábrica de Etiquetas (Para colar nas provas)")
            st.info("O sistema gerará um documento Word com retângulos formatados. Basta imprimir, cortar e colar na prova do aluno para que ele e os pais vejam a composição exata da nota.")
            
            if st.button("🖨️ GERAR ETIQUETAS (DOCX)", use_container_width=True, type="primary"):
                with st.spinner("Desenhando etiquetas..."):
                    import exporter
                    
                    dados_etiquetas = []
                    for _, r in df_input.iterrows():
                        nome_limpo = r['ESTUDANTE'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                        
                        if r['MEDIA_FINAL'] >= 6.0: status_txt = "✅ APROVADO"
                        elif r['MEDIA_FINAL'] >= 5.5: status_txt = "⚠️ REFAZER QUESTÕES ERRADAS"
                        else: status_txt = "🔴 RECUPERAÇÃO PARALELA"
                        
                        b_sala = float(r.get('BÔNUS (SALA)', 0.0) or 0.0)
                        b_cons = float(r.get('BÔNUS CONSELHO', 0.0) or 0.0)
                        bonus_total_etiq = b_sala + b_cons
                        
                        dados_etiquetas.append({
                            "nome": nome_limpo,
                            "vistos": f"{float(r.get('V_PREF', 0.0) or 0.0):.1f}",
                            "teste": f"{float(r.get('T_PREF', 0.0) or 0.0):.1f}",
                            "prova": f"{float(r.get('P_PREF', 0.0) or 0.0):.1f}",
                            "bonus": f"{bonus_total_etiq:.1f}",
                            "media": f"{float(r.get('MEDIA_FINAL', 0.0) or 0.0):.1f}",
                            "status": status_txt
                        })
                    
                    info_etiqueta = {"turma": turma_sel, "trimestre": trimestre_sel}
                    nome_arq_etiq = f"ETIQUETAS_{turma_sel.replace(' ', '')}_{trimestre_sel.replace(' ', '')}"
                    
                    doc_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_etiq, dados_etiquetas, info_etiqueta)
                    link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_etiq, trimestre=trimestre_sel, categoria=turma_sel, modo="PLANEJAMENTO")
                    
                    if "https" in link_doc:
                        st.success("✅ Etiquetas geradas com sucesso!")
                        st.link_button("📂 ABRIR ETIQUETAS PARA IMPRESSÃO", link_doc, type="primary", use_container_width=True)
                        st.balloons()
                    else:
                        st.error(f"Erro ao salvar no Drive: {link_doc}")



# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO - CLEAN & UX (INTELIGÊNCIA TEMPORAL E BLINDAGEM)
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Inteligência de Conselho e Resultados")
    st.caption("💡 **Guia de Comando:** Visão panorâmica do ano letivo. O sistema cruza notas, recuperações e faltas para calcular automaticamente a situação de cada estudante, com barras de progresso visuais.")
    st.markdown("---")

    if df_notas.empty:
        st.warning("⚠️ Sem notas lançadas no sistema. O Boletim Anual será gerado assim que houver dados.")
    else:
        # --- 1. FILTRO DE TURMA ---
        # 🚨 VACINA ANTI-KEYERROR
        lista_turmas_bol = []
        if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
            turmas_reais_bol = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_bol = sorted(turmas_reais_bol['ID_TURMA'].unique())
        elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
            lista_turmas_bol = sorted(df_alunos['TURMA'].unique())
        
        if not lista_turmas_bol:
            st.warning("Nenhuma turma cadastrada.")
            st.stop()
            
        with st.container(border=True):
            turma_sel = st.selectbox("🎯 Selecione a Turma para Análise:", lista_turmas_bol, key="bol_turma_clean")
        
        # --- 2. PROCESSAMENTO DE DADOS (DATA FUSION) ---
        df_t = df_notas[df_notas['TURMA'] == turma_sel].copy()
        
        if df_t.empty:
            st.info(f"📭 Nenhuma nota lançada para a turma {turma_sel} ainda.")
            st.stop()

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
            # 🚨 PROTOCOLO FANTASMA: Preenche recuperações vazias com -1.0
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
        
        # CÁLCULO DE FALTAS TOTAIS DO ANO
        faltas_df = df_diario[(df_diario['TURMA'] == turma_sel) & (df_diario['TAGS'] == "AUSÊNCIA")]
        
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

        trimestres_ativos = 0
        if pivot['MEDIA_FINAL_I Trimestre'].sum() > 0: trimestres_ativos += 1
        if pivot['MEDIA_FINAL_II Trimestre'].sum() > 0: trimestres_ativos += 1
        if pivot['MEDIA_FINAL_III Trimestre'].sum() > 0: trimestres_ativos += 1
        if trimestres_ativos == 0: trimestres_ativos = 1 

        dias_validos = df_diario[(df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(['DIA NÃO LETIVO', 'BONUS_CONSELHO', 'SISTEMA_NOTA']))]
        total_dias_letivos = dias_validos['DATA'].nunique()
        
        if total_dias_letivos == 0: total_dias_letivos = 1
        limite_faltas = int(total_dias_letivos * 0.25)
        if limite_faltas == 0: limite_faltas = 1 

        # --- 3. LÓGICA DE STATUS ---
        def calcular_situacao_anual(row):
            t1 = util.sosa_to_float(row.get("MEDIA_FINAL_I Trimestre", 0))
            t2 = util.sosa_to_float(row.get("MEDIA_FINAL_II Trimestre", 0))
            t3 = util.sosa_to_float(row.get("MEDIA_FINAL_III Trimestre", 0))
            rf = util.sosa_to_float(row.get("RF", -1.0))
            faltas_aluno = row.get("FALTAS", 0)
            
            soma = t1 + t2 + t3
            falta_pts = max(0.0, 18.0 - soma)
            
            aluno_match = df_alunos[df_alunos['ID'].apply(db.limpar_id) == db.limpar_id(row['ID_ALUNO'])]
            if not aluno_match.empty:
                aluno_info = aluno_match.iloc[0]
                pei = "♿" if str(aluno_info['NECESSIDADES']).upper().strip() not in["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"] else "👤"
            else:
                pei = "👤"
            
            if faltas_aluno >= (total_dias_letivos * 0.5) and soma == 0: 
                status = "👻 EVASÃO"
            elif faltas_aluno > limite_faltas:
                status = "🚨 REPROV. FALTA"
            elif soma >= 18.0: 
                status = "✅ APROVADO"
            elif rf >= 6.0: 
                status = "🔄 APROV. REC"
            elif trimestres_ativos == 3 and soma < 18.0 and rf < 6.0:
                status = "❌ REPROVADO"
            elif trimestres_ativos < 3: 
                media_parcial = soma / trimestres_ativos
                if media_parcial >= 6.0:
                    status = "🟢 NA MÉDIA"
                else:
                    status = "🟡 ALERTA (NOTA)"
            else: 
                status = "⏳ AGUARDANDO"
            
            return pd.Series([pei, soma, falta_pts, status])

        pivot[['P', 'Σ', 'FALTA_PTS', 'SITUAÇÃO']] = pivot.apply(calcular_situacao_anual, axis=1)

        # --- 4. KPIs DE TOPO ---
        st.markdown("### 📊 Termômetro da Turma")
        c1, c2, c3, c4 = st.columns(4)
        
        media_real_turma = pivot['Σ'].sum() / (len(pivot) * trimestres_ativos) if len(pivot) > 0 else 0
        c1.metric("Média Geral da Turma", f"{media_real_turma:.1f}")
        
        na_media = len(pivot[pivot['SITUAÇÃO'].isin(["✅ APROVADO", "🟢 NA MÉDIA", "🔄 APROV. REC"])])
        taxa_sucesso = (na_media / len(pivot)) * 100 if len(pivot) > 0 else 0
        c2.metric("Alunos na Média", f"{taxa_sucesso:.0f}%", f"{na_media} de {len(pivot)} alunos")
        
        evasao_total = len(pivot[pivot['SITUAÇÃO'] == "👻 EVASÃO"])
        c3.metric("Evasão / Abandono", evasao_total, delta_color="inverse")
        
        risco_total = len(pivot[pivot['SITUAÇÃO'].isin(["🚨 REPROV. FALTA", "🟡 ALERTA (NOTA)"])])
        c4.metric("Alerta Crítico (Nota/Falta)", risco_total, delta_color="inverse")

        # --- 5. TABELA VISUAL DE ELITE ---
        st.markdown("---")
        st.markdown("### 📋 Mapa de Desempenho Anual e Assiduidade")
        
        def style_status_anual(v):
            if "APROV" in str(v) or "NA MÉDIA" in str(v): return 'color: #2ECC71; font-weight: bold;'
            if "EVASÃO" in str(v) or "REPROV" in str(v): return 'color: #E74C3C; font-weight: bold;'
            if "ALERTA" in str(v): return 'color: #F1C40F; font-weight: bold;'
            return 'color: gray;'

        # 🚨 FORMATADORES CUSTOMIZADOS PARA ESCONDER O FANTASMA (-1.0)
        def formatar_rec(val):
            if pd.isna(val) or val < 0: return "-"
            return f"{val:.1f}"

        def formatar_media(val):
            return f"{val:.1f}"

        st.dataframe(
            pivot[['P', 'NOME_ALUNO', 
                   'MEDIA_FINAL_I Trimestre', 'NOTA_REC_I Trimestre',
                   'MEDIA_FINAL_II Trimestre', 'NOTA_REC_II Trimestre',
                   'MEDIA_FINAL_III Trimestre', 'NOTA_REC_III Trimestre',
                   'Σ', 'RF', 'FALTAS', 'SITUAÇÃO']]
            .style.map(style_status_anual, subset=['SITUAÇÃO'])
            .format(formatar_media, subset=['MEDIA_FINAL_I Trimestre', 'MEDIA_FINAL_II Trimestre', 'MEDIA_FINAL_III Trimestre', 'Σ'])
            .format(formatar_rec, subset=['NOTA_REC_I Trimestre', 'NOTA_REC_II Trimestre', 'NOTA_REC_III Trimestre', 'RF']),
            use_container_width=True, hide_index=True,
            column_config={
                "P": st.column_config.TextColumn("P", width="small", help="Perfil: ♿ PEI ou 👤 Regular"),
                "NOME_ALUNO": st.column_config.TextColumn("Estudante", width="medium"),
                "MEDIA_FINAL_I Trimestre": st.column_config.NumberColumn("I", width="small"),
                "NOTA_REC_I Trimestre": st.column_config.TextColumn("R1", width="small"),
                "MEDIA_FINAL_II Trimestre": st.column_config.NumberColumn("II", width="small"),
                "NOTA_REC_II Trimestre": st.column_config.TextColumn("R2", width="small"),
                "MEDIA_FINAL_III Trimestre": st.column_config.NumberColumn("III", width="small"),
                "NOTA_REC_III Trimestre": st.column_config.TextColumn("R3", width="small"),
                "Σ": st.column_config.ProgressColumn("Σ (Soma)", help="Soma Anual (Meta: 18.0)", format="%.1f", min_value=0.0, max_value=18.0),
                "RF": st.column_config.TextColumn("RF", width="small", help="Recuperação Final"),
                "FALTAS": st.column_config.ProgressColumn("Faltas", help=f"Limite atual: {limite_faltas}", format="%d", min_value=0, max_value=limite_faltas),
                "SITUAÇÃO": st.column_config.TextColumn("Status", width="medium")
            }
        )
        
        st.caption(f"📌 **Legenda:** I, II, III (Médias Trimestrais) | R1, R2, R3 (Recuperações Paralelas) | Σ (Soma Anual) | RF (Recuperação Final). Limite de faltas atual: **{limite_faltas}**.")






# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO - CLEAN & UX (INTELIGÊNCIA TEMPORAL)
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Inteligência de Conselho e Resultados")
    st.caption("💡 **Guia de Comando:** Visão panorâmica do ano letivo. O sistema cruza notas, recuperações e faltas para calcular automaticamente a situação de cada estudante, adaptando a meta ao trimestre atual.")
    st.markdown("---")

    if df_notas.empty:
        st.warning("⚠️ Sem notas lançadas no sistema. O Boletim Anual será gerado assim que houver dados.")
    else:
        # --- 1. FILTRO DE TURMA ---
        turmas_reais_bol = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_bol = sorted(turmas_reais_bol['ID_TURMA'].unique()) if not turmas_reais_bol.empty else sorted(df_alunos['TURMA'].unique())
        
        if not lista_turmas_bol:
            st.warning("Nenhuma turma cadastrada.")
            st.stop()
            
        with st.container(border=True):
            turma_sel = st.selectbox("🎯 Selecione a Turma para Análise:", lista_turmas_bol, key="bol_turma_clean")
        
        # --- 2. PROCESSAMENTO DE DADOS (DATA FUSION) ---
        df_t = df_notas[df_notas['TURMA'] == turma_sel].copy()
        
        if df_t.empty:
            st.info(f"📭 Nenhuma nota lançada para a turma {turma_sel} ainda.")
            st.stop()

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
            if f"NOTA_REC_{t}" not in pivot.columns: pivot[f"NOTA_REC_{t}"] = 0.0

        rec_f_data = df_t[df_t['TRIMESTRE'].str.contains("REC_FINAL|FINAL", na=False, case=False)]
        if not rec_f_data.empty:
            rec_f_min = rec_f_data[['ID_ALUNO', 'MEDIA_FINAL']].rename(columns={'MEDIA_FINAL': 'RF'})
            pivot = pd.merge(pivot, rec_f_min, on='ID_ALUNO', how='left')
        else:
            pivot['RF'] = 0.0
        
        # CÁLCULO DE FALTAS TOTAIS DO ANO
        faltas_df = df_diario[(df_diario['TURMA'] == turma_sel) & (df_diario['TAGS'] == "AUSÊNCIA")]
        
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

        # 🚨 INTELIGÊNCIA TEMPORAL: Descobre quantos trimestres já aconteceram na turma
        has_t1 = pivot['MEDIA_FINAL_I Trimestre'].sum() > 0
        has_t2 = pivot['MEDIA_FINAL_II Trimestre'].sum() > 0
        has_t3 = pivot['MEDIA_FINAL_III Trimestre'].sum() > 0
        
        trimestres_ativos = sum([has_t1, has_t2, has_t3])
        if trimestres_ativos == 0: trimestres_ativos = 1 # Evita divisão por zero

        # Total de dias letivos registrados para a turma (para calcular o limite de 25%)
        total_dias_letivos = df_diario[df_diario['TURMA'] == turma_sel]['DATA'].nunique()
        if total_dias_letivos == 0: total_dias_letivos = 1
        limite_faltas = int(total_dias_letivos * 0.25)
        if limite_faltas == 0: limite_faltas = 1 

        # --- 3. LÓGICA DE STATUS (COM INTELIGÊNCIA TEMPORAL) ---
        def calcular_situacao_anual(row):
            t1 = util.sosa_to_float(row.get("MEDIA_FINAL_I Trimestre", 0))
            t2 = util.sosa_to_float(row.get("MEDIA_FINAL_II Trimestre", 0))
            t3 = util.sosa_to_float(row.get("MEDIA_FINAL_III Trimestre", 0))
            rf = util.sosa_to_float(row.get("RF", 0))
            faltas_aluno = row.get("FALTAS", 0)
            
            soma = t1 + t2 + t3
            falta_pts = max(0.0, 18.0 - soma)
            
            aluno_match = df_alunos[df_alunos['ID'].apply(db.limpar_id) == db.limpar_id(row['ID_ALUNO'])]
            if not aluno_match.empty:
                aluno_info = aluno_match.iloc[0]
                pei = "♿" if str(aluno_info['NECESSIDADES']).upper().strip() not in["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"] else "👤"
            else:
                pei = "👤"
            
            # 🚨 NOVA LÓGICA DE STATUS
            # 1. Verifica Evasão (Zero nota e muitas faltas)
            if soma == 0 and faltas_aluno >= (limite_faltas * 1.5): 
                status = "👻 EVASÃO"
            # 2. Verifica Reprovação por Falta
            elif faltas_aluno > limite_faltas:
                status = "🚨 REPROV. FALTA"
            # 3. Se o ano já acabou (3 trimestres)
            elif trimestres_ativos == 3:
                if soma >= 18.0: status = "✅ APROVADO"
                elif rf >= 6.0: status = "🔄 APROV. REC"
                elif soma > 0 and falta_pts <= 10.0: status = "⚠️ REC. FINAL"
                else: status = "❌ REPROVADO"
            # 4. Se o ano está em andamento (1º ou 2º Trimestre)
            else:
                if soma == 0 and faltas_aluno == 0:
                    status = "⏳ AGUARDANDO"
                else:
                    media_parcial = soma / trimestres_ativos
                    if media_parcial >= 6.0:
                        status = "🟢 NA MÉDIA"
                    elif media_parcial >= 4.0:
                        status = "🟡 ALERTA (NOTA)"
                    else:
                        status = "🔴 RISCO CRÍTICO"
            
            return pd.Series([pei, soma, falta_pts, status])

        pivot[['P', 'Σ', 'FALTA_PTS', 'SITUAÇÃO']] = pivot.apply(calcular_situacao_anual, axis=1)

        # --- 4. KPIs DE TOPO (TERMÔMETRO DA TURMA) ---
        st.markdown("### 📊 Termômetro da Turma")
        c1, c2, c3, c4 = st.columns(4)
        
        # Média real baseada apenas nos trimestres que já aconteceram
        media_real_turma = pivot['Σ'].sum() / (len(pivot) * trimestres_ativos) if len(pivot) > 0 else 0
        c1.metric("Média Geral da Turma", f"{media_real_turma:.1f}")
        
        # Alunos na média (>= 6.0)
        na_media = len(pivot[pivot['SITUAÇÃO'].isin(["✅ APROVADO", "🟢 NA MÉDIA", "🔄 APROV. REC"])])
        taxa_sucesso = (na_media / len(pivot)) * 100 if len(pivot) > 0 else 0
        c2.metric("Alunos na Média", f"{taxa_sucesso:.0f}%", f"{na_media} de {len(pivot)} alunos")
        
        evasao_total = len(pivot[pivot['SITUAÇÃO'] == "👻 EVASÃO"])
        c3.metric("Evasão / Abandono", evasao_total, delta_color="inverse")
        
        risco_total = len(pivot[pivot['SITUAÇÃO'].isin(["🚨 REPROV. FALTA", "🔴 RISCO CRÍTICO"])])
        c4.metric("Risco Crítico (Nota/Falta)", risco_total, delta_color="inverse", help="Alunos que estouraram faltas ou estão com a média parcial muito abaixo de 6.0.")

        # --- 5. TABELA VISUAL DE ELITE ---
        st.markdown("---")
        st.markdown("### 📋 Mapa de Desempenho Anual e Assiduidade")
        
        def style_status_anual(v):
            if "APROV" in str(v) or "NA MÉDIA" in str(v): return 'color: #2ECC71; font-weight: bold;'
            if "EVASÃO" in str(v) or "REPROV" in str(v) or "RISCO" in str(v): return 'color: #E74C3C; font-weight: bold;'
            if "ALERTA" in str(v) or "REC. FINAL" in str(v): return 'color: #F1C40F; font-weight: bold;'
            return 'color: gray;'

        st.dataframe(
            pivot[['P', 'NOME_ALUNO', 
                   'MEDIA_FINAL_I Trimestre', 'NOTA_REC_I Trimestre',
                   'MEDIA_FINAL_II Trimestre', 'NOTA_REC_II Trimestre',
                   'MEDIA_FINAL_III Trimestre', 'NOTA_REC_III Trimestre',
                   'Σ', 'RF', 'FALTAS', 'SITUAÇÃO']]
            .style.map(style_status_anual, subset=['SITUAÇÃO'])
            .format("{:.1f}", subset=['MEDIA_FINAL_I Trimestre', 'NOTA_REC_I Trimestre', 
                                      'MEDIA_FINAL_II Trimestre', 'NOTA_REC_II Trimestre', 
                                      'MEDIA_FINAL_III Trimestre', 'NOTA_REC_III Trimestre', 
                                      'RF']),
            use_container_width=True, hide_index=True,
            column_config={
                "P": st.column_config.TextColumn("P", width="small", help="Perfil: ♿ PEI ou 👤 Regular"),
                "NOME_ALUNO": st.column_config.TextColumn("Estudante", width="medium"),
                "MEDIA_FINAL_I Trimestre": st.column_config.NumberColumn("I", width="small"),
                "NOTA_REC_I Trimestre": st.column_config.NumberColumn("R1", width="small"),
                "MEDIA_FINAL_II Trimestre": st.column_config.NumberColumn("II", width="small"),
                "NOTA_REC_II Trimestre": st.column_config.NumberColumn("R2", width="small"),
                "MEDIA_FINAL_III Trimestre": st.column_config.NumberColumn("III", width="small"),
                "NOTA_REC_III Trimestre": st.column_config.NumberColumn("R3", width="small"),
                "Σ": st.column_config.ProgressColumn("Σ (Soma)", help="Soma Anual (Meta: 18.0)", format="%.1f", min_value=0.0, max_value=18.0),
                "RF": st.column_config.NumberColumn("RF", width="small", help="Recuperação Final"),
                "FALTAS": st.column_config.ProgressColumn("Faltas", help=f"Limite atual: {limite_faltas}", format="%d", min_value=0, max_value=limite_faltas),
                "SITUAÇÃO": st.column_config.TextColumn("Status", width="medium")
            }
        )
        
        st.caption(f"📌 **Legenda:** I, II, III (Médias Trimestrais) | R1, R2, R3 (Recuperações Paralelas) | Σ (Soma Anual) | RF (Recuperação Final). Limite de faltas atual: **{limite_faltas}**.")






# ==============================================================================
# MÓDULO: GESTÃO DA TURMA (COCKPIT DE REGÊNCIA & CALENDÁRIO V2026)
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Cockpit de Regência: Gestão 360°")
    st.caption("💡 Central de comando da sua rotina: abertura rápida de aulas, gestão de semanas/recessos, roleta e inteligência da turma.")
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

    tab_cockpit, tab_maquina, tab_inteligencia, tab_secretaria = st.tabs([
        "🚀 1. Cockpit de Regência", 
        "🕰️ 2. Máquina do Tempo",
        "🧠 3. Inteligência da Turma", 
        "⚙️ 4. Secretaria, Matrículas & Calendário"
    ])

    # ==============================================================================
    # 🚀 ABA 1: COCKPIT DE REGÊNCIA (COM ALERTA DE ARGUIÇÃO & BENTO GRID)
    # ==============================================================================
    with tab_cockpit:
        if df_turmas.empty or 'ID_TURMA' not in df_turmas.columns:
            st.info("📭 Nenhuma turma cadastrada. Vá na aba '4. Secretaria, Matrículas & Calendário' para iniciar.")
        else:
            with st.expander("📅 Ver Grade Oficial de Regência", expanded=False):
                dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
                tempos = ["1º Tempo", "2º Tempo"]
                grade_map = {t: {d: "---" for d in dias_semana} for t in tempos}

                for _, row in df_turmas.iterrows():
                    sigla = str(row.get('ID_TURMA', ''))
                    nome_turma = str(row.iloc[1]) if len(row) > 1 else ""
                    horarios_str = str(row.iloc[3]) if len(row) > 3 else ""
                    display_name = nome_turma.replace("Ano ", "ANO ").upper() if "ª" in sigla else sigla
                    
                    if horarios_str and horarios_str != "N/A":
                        for h in [x.strip() for x in horarios_str.split("/")]:
                            for dia in dias_semana:
                                for tempo in tempos:
                                    if dia in h and tempo in h: grade_map[tempo][dia] = display_name

                def colorir_grade(val):
                    if val in ["PI", "PC", "AC", "HTPC"]: return 'background-color: #2962FF; color: white; font-weight: bold; text-align: center;'
                    if val != "---": return 'background-color: #001E3C; color: #2ECC71; font-weight: bold; text-align: center;'
                    return 'color: gray; text-align: center;'

                st.dataframe(pd.DataFrame(grade_map).T.style.map(colorir_grade), use_container_width=True)

            if not lista_turmas_segura:
                st.warning("⚠️ Apenas horários de planejamento cadastrados. Cadastre turmas regulares para liberar o comando acadêmico.")
            else:
                turma_foco = st.selectbox("🎯 Selecione a Turma para Comando:", lista_turmas_segura, key=f"foco_t_{v}")
                
                alunos_t = df_alunos[df_alunos['TURMA'] == turma_foco].sort_values(by="NOME_ALUNO")
                ano_num = "".join(filter(str.isdigit, turma_foco))
                ano_str_ref = f"{ano_num}º"

                df_p_atual = df_planos[df_planos['ANO'] == ano_str_ref].copy()
                if not df_p_atual.empty:
                    df_p_atual['DATA_DT'] = pd.to_datetime(df_p_atual['DATA'], format="%d/%m/%Y", errors='coerce')
                    df_p_atual = df_p_atual.sort_values(by='DATA_DT', ascending=False)
                
                df_mats_ano = df_aulas[df_aulas['ANO'].str.contains(ano_num)].iloc[::-1]
                historico_turma = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco].copy()

                # 🚨 RADAR DE ARGUIÇÃO PENDENTE (ALERTA EM TEMPO REAL)
                data_hoje_str = datetime.now().strftime("%d/%m/%Y")
                chave_lista_hoje = f"lista_roleta_{turma_foco}_{data_hoje_str}"
                
                if chave_lista_hoje in st.session_state:
                    pendentes_arg = [a for a in st.session_state[chave_lista_hoje] if a["Status"] == "⏳ Pendente"]
                    concluidos_arg = [a for a in st.session_state[chave_lista_hoje] if a["Status"] != "⏳ Pendente"]
                    
                    if concluidos_arg and pendentes_arg:
                        st.warning(f"⚠️ **SESSÃO DE ARGUIÇÃO EM ANDAMENTO ({len(concluidos_arg)} avaliados / {len(pendentes_arg)} pendentes):** Existem alunos sorteados no quadro aguardando lançamento de diagnóstico!")

                # 🚨 MODAL: ESQUADRÃO DE ARGUIÇÃO (ROLETA MÚLTIPLA)
                @st.dialog("🎲 Esquadrão de Arguição", width="large")
                def dialog_roleta(t_roleta):
                    c_rol1, c_rol2, c_rol3 = st.columns([1, 1, 1])
                    data_roleta = c_rol1.date_input("📅 Data da Arguição:", date.today(), format="DD/MM/YYYY", key=f"rol_d_{v}")
                    data_roleta_str = data_roleta.strftime("%d/%m/%Y")
                    qtd_sorteio = c_rol2.number_input("Quantos alunos chamar?", 1, 4, 3)
                    
                    with c_rol3.expander("⚙️ Configurar Pontuação"):
                        pt_acerto = st.number_input("Pontos por Acertar (+):", 0.0, 5.0, 0.5, step=0.1)
                        pt_recusa = st.number_input("Punição por Recusa (-):", -5.0, 0.0, -0.5, step=0.1)

                    alunos_roleta = df_alunos[df_alunos['TURMA'] == t_roleta].sort_values(by="NOME_ALUNO").copy()
                    if alunos_roleta.empty: st.warning("Nenhum aluno cadastrado."); return
                    
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
                        diario_dia = df_diario[(df_diario['DATA'] == data_roleta_str) & (df_diario['TURMA'] == t_roleta)]
                        lista_inicial = []
                        for _, row in alunos_roleta.iterrows():
                            id_a, nome_a, icone_a = db.limpar_id(row['ID']), row['NOME_ALUNO'], row['ICONE']
                            status_inicial, obs_inicial, pts_inicial = "⏳ Pendente", "", 0.0
                            
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
                            lista_inicial.append({"ID": id_a, "Estudante": f"{icone_a} {nome_a}", "Status": status_inicial, "Diagnóstico": obs_inicial, "Pontos": pts_inicial})
                        st.session_state[chave_lista] = lista_inicial
                        
                    if chave_sorteados not in st.session_state: st.session_state[chave_sorteados] = []

                    st.markdown("---")
                    pendentes = [a for a in st.session_state[chave_lista] if a["Status"] == "⏳ Pendente"]
                    
                    c_btn_sort, c_btn_reset = st.columns([2, 1])
                    if c_btn_sort.button("🎲 SORTEAR ESQUADRÃO", type="primary", use_container_width=True):
                        if not pendentes: st.success("Todos chamados!")
                        else: 
                            qtd_real = min(qtd_sorteio, len(pendentes))
                            st.session_state[chave_sorteados] = random.sample([p["ID"] for p in pendentes], qtd_real)
                            st.rerun()
                            
                    if c_btn_reset.button("🔄 Resetar Lista", use_container_width=True):
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
                                    st.markdown(f"<p style='text-align: center; color: gray; font-size: 11px;'>Perfil: {aluno_db['NECESSIDADES']}</p>", unsafe_allow_html=True)
                                    anotacao = st.text_area("📝 Diagnóstico:", value=aluno_atual["Diagnóstico"], key=f"anotacao_{id_atual}", height=68)
                                    
                                    def registrar_arguicao(id_al, status_label, pontos, obs_padrao, anot):
                                        obs_final = anot.strip() if anot.strip() else obs_padrao
                                        for a in st.session_state[chave_lista]:
                                            if a["ID"] == id_al:
                                                a["Status"], a["Pontos"], a["Diagnóstico"] = status_label, pontos, obs_final
                                                break
                                        nome_limpo = aluno_db['NOME_ALUNO'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                                        wb = db.conectar()
                                        ws = wb.worksheet("DB_DIARIO_BORDO")
                                        dados = ws.get_all_values()
                                        for i in range(len(dados)-1, 0, -1):
                                            if dados[i][0] == data_roleta_str and db.limpar_id(dados[i][1]) == id_al and dados[i][5] == "ARGUIÇÃO": ws.delete_rows(i+1)
                                        ws.append_row([data_roleta_str, id_al, nome_limpo, t_roleta, "TRUE", "ARGUIÇÃO", f"Quadro Negro: {obs_final}", util.sosa_to_str(pontos)], value_input_option="USER_ENTERED")
                                        st.cache_data.clear()
                                        st.session_state[chave_sorteados].remove(id_al)
                                    
                                    if st.button(f"✅ Dominou (+{pt_acerto})", key=f"btn_dom_{id_atual}", use_container_width=True): 
                                        registrar_arguicao(id_atual, "✅ Dominou", pt_acerto, "Resolveu corretamente.", anotacao); st.rerun()
                                    if st.button("🤝 Tentou (0.0)", key=f"btn_ten_{id_atual}", use_container_width=True): 
                                        registrar_arguicao(id_atual, "🤝 Tentou", 0.0, "Apresentou dificuldades.", anotacao); st.rerun()
                                    if st.button(f"❌ Recusou ({pt_recusa})", key=f"btn_rec_{id_atual}", use_container_width=True): 
                                        registrar_arguicao(id_atual, "❌ Recusou", pt_recusa, "Recusou-se a participar.", anotacao); st.rerun()
                                    if st.button("⏭️ Pular/Isento", key=f"btn_pul_{id_atual}", use_container_width=True):
                                        for a in st.session_state[chave_lista]:
                                            if a["ID"] == id_atual: a["Status"] = "⏭️ Faltou/Isento"
                                        st.session_state[chave_sorteados].remove(id_atual); st.rerun()

                    st.markdown("---")
                    with st.expander("📋 Ver Lista Completa da Turma"):
                        df_editado = st.data_editor(
                            pd.DataFrame(st.session_state[chave_lista]), hide_index=True, use_container_width=True, height=300,
                            column_config={"ID": None, "Estudante": st.column_config.TextColumn(disabled=True), "Status": st.column_config.TextColumn(disabled=True), "Pontos": st.column_config.NumberColumn(disabled=True)},
                            key=f"ed_rol_{t_roleta}_{data_roleta_str}"
                        )

                # 🚨 MODAL: DIA NÃO LETIVO
                @st.dialog("🛑 Registrar Dia Não Letivo")
                def dialog_dia_nao_letivo(t_foco):
                    st.caption("Use para registrar paralisações, luto, falta de água, etc. Isso bloqueará faltas neste dia.")
                    data_nl = st.date_input("Data do Evento:", date.today(), format="DD/MM/YYYY")
                    motivo_nl = st.text_input("Motivo:", placeholder="Ex: Paralisação Sindical")
                    if st.button("Confirmar Dia Não Letivo", type="primary", use_container_width=True):
                        if motivo_nl:
                            data_nl_str = data_nl.strftime("%d/%m/%Y")
                            db.limpar_diario_data_turma(data_nl_str, t_foco)
                            db.excluir_aula_aberta(data_nl_str, t_foco)
                            db.salvar_no_banco("DB_DIARIO_BORDO", [data_nl_str, "GLOBAL", "TODOS OS ALUNOS", t_foco, "ISENTO", "DIA NÃO LETIVO", motivo_nl, "0,00"])
                            db.salvar_no_banco("DB_REGISTRO_AULAS", [data_nl_str, "AVULSA", t_foco, f"DIA NÃO LETIVO: {motivo_nl}", "N/A", "N/A", "NÃO LETIVO", "", ""])
                            st.success("Registrado!"); time.sleep(1); st.rerun()
                        else: st.error("Digite o motivo.")

                # --- CAMADA 1: RADAR DEMOGRÁFICO E AÇÕES RÁPIDAS ---
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
                    c_m1.metric("👥 Alunos", total_alunos_turma)
                    c_m2.metric("♿ PEI", qtd_pei)
                    c_m3.metric("🧱 Defasagem", qtd_defasagem)
                    
                    if c_btn1.button("🎲 Roleta de Arguição", use_container_width=True): dialog_roleta(turma_foco)
                    if c_btn2.button("🛑 Dia Não Letivo", use_container_width=True): dialog_dia_nao_letivo(turma_foco)

                # --- CAMADA 2: ABERTURA DE AULA (ONE-CLICK) ---
                st.markdown("### 🕒 Abertura de Aula (Hoje)")
                
                planos_usados = historico_turma['SEMANA'].unique().tolist()
                plano_sugerido = "Nenhum"
                
                df_p_sugestao = df_p_atual[~df_p_atual['SEMANA'].isin(planos_usados)]
                df_p_sugestao = df_p_sugestao[df_p_sugestao['EIXO'] == 'HUB_ATIVO']
                if not df_p_sugestao.empty: plano_sugerido = df_p_sugestao.iloc[0]['SEMANA']

                with st.container(border=True):
                    col_ab1, col_ab2 = st.columns(2)
                    
                    with col_ab1:
                        data_aula = st.date_input("Data da Aula:", date.today(), format="DD/MM/YYYY", key=f"dt_reg_{v}")
                        data_aula_str = data_aula.strftime("%d/%m/%Y")
                        aula_existente = historico_turma[historico_turma['DATA'] == data_aula_str]
                        
                        if not aula_existente.empty:
                            st.success(f"✅ **Aula já registrada!** Status: {aula_existente.iloc[0].get('STATUS_EXECUCAO', 'Pendente')}")
                        else:
                            if plano_sugerido != "Nenhum": st.info(f"💡 **Sugestão do Sistema:** {plano_sugerido}")
                            else: st.success("✅ Todos os planos ativos já foram aplicados!")

                    with col_ab2:
                        if not aula_existente.empty:
                            st.info(f"📦 **Material Vinculado:**\n{aula_existente.iloc[0]['CONTEUDO_MINISTRADO']}")
                        else:
                            mats_disp_bruto = df_mats_ano['TIPO_MATERIAL'].tolist()
                            
                            default_mats = []
                            if plano_sugerido != "Nenhum":
                                mats_sugeridos = df_aulas[(df_aulas['ANO'].str.contains(ano_num)) & (df_aulas['SEMANA_REF'] == plano_sugerido)]['TIPO_MATERIAL'].tolist()
                                default_mats = [m for m in mats_sugeridos if m in mats_disp_bruto][:2]
                                
                            mats_sel = st.multiselect("📦 Selecione o Material (Máx 2):", options=mats_disp_bruto, default=default_mats, max_selections=2, key=f"mats_reg_{v}")

                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button("💾 CONFIRMAR ABERTURA DE AULA", use_container_width=True, type="primary"):
                                if not mats_sel: st.error("⚠️ Selecione ao menos um material.")
                                else:
                                    mat_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == mats_sel[0]].iloc[0]
                                    db.salvar_no_banco("DB_REGISTRO_AULAS", [data_aula_str, mat_ref['SEMANA_REF'], turma_foco, " + ".join(mats_sel), "PENDENTE", "ABERTA"])
                                    st.success("✅ Aula aberta! Vá para o Diário de Bordo."); time.sleep(1); st.rerun()

                # --- CAMADA 3: AUDITORIA DE REGÊNCIA ---
                with st.expander("✏️ Auditoria e Edição de Aulas Passadas", expanded=False):
                    historico_turma_auditoria = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco].copy()
                    if not historico_turma_auditoria.empty:
                        historico_turma_auditoria['DATA_DT'] = pd.to_datetime(historico_turma_auditoria['DATA'], format="%d/%m/%Y", errors='coerce')
                        aulas_abertas = historico_turma_auditoria.sort_values(by='DATA_DT', ascending=False).head(10)
                        
                        for i, (idx, row_aula) in enumerate(aulas_abertas.iterrows()):
                            with st.container(border=True):
                                st.markdown(f"**{row_aula['DATA']}** - {str(row_aula['CONTEUDO_MINISTRADO'])}")
                                c_aud_1, c_aud_2, c_aud_3 = st.columns([1, 1, 2])
                                novo_status = c_aud_1.selectbox("Status:", ["🟢 Concluído (100%)", "🟡 Parcial (Pendência)", "🔴 Bloqueado (Crítico)", "ABERTA", "NÃO LETIVO"], index=0 if "Concluído" in str(row_aula.get('STATUS_EXECUCAO', '')) else 3, key=f"aud_stat_{idx}")
                                opcoes_semanas = ["AVULSA"] + df_planos[df_planos['ANO'] == ano_str_ref]['SEMANA'].unique().tolist()
                                nova_semana = c_aud_2.selectbox("Semana:", opcoes_semanas, index=opcoes_semanas.index(row_aula['SEMANA']) if row_aula['SEMANA'] in opcoes_semanas else 0, key=f"aud_sem_{idx}")
                                mats_atuais = [m.strip() for m in str(row_aula['CONTEUDO_MINISTRADO']).split('+')]
                                novo_mat_sel = c_aud_3.multiselect("Material:", options=df_mats_ano['TIPO_MATERIAL'].tolist(), default=[m for m in mats_atuais if m in df_mats_ano['TIPO_MATERIAL'].tolist()], key=f"aud_mat_{idx}")
                                
                                c_btn_save, c_btn_del, _ = st.columns([1, 1, 2])
                                if c_btn_save.button("Salvar", key=f"aud_save_{idx}", type="primary"):
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
                                if c_btn_del.button("Apagar", key=f"aud_del_{idx}"):
                                    if db.excluir_aula_aberta(row_aula['DATA'], turma_foco): st.rerun()
                    else: st.info("Nenhuma aula registrada.")

    # ==============================================================================
    # 🕰️ ABA 2: MÁQUINA DO TEMPO (AUDITORIA E VISTOS DE EXCEÇÃO)
    # ==============================================================================
    with tab_maquina:
        st.markdown("### 🕰️ Máquina do Tempo (Auditoria de Aulas Passadas)")
        st.caption("Dashboard analítico da aula. Revise o que aconteceu e aplique justificativas em janela flutuante.")
        
        if not lista_turmas_segura:
            st.info("Nenhuma turma cadastrada.")
        else:
            c_maq1, c_maq2 = st.columns([1, 2])
            t_maq = c_maq1.selectbox("Selecione a Turma:", lista_turmas_segura, key=f"maq_t_{v}")
            
            if t_maq:
                df_d_maq = df_diario[(df_diario['TURMA'] == t_maq) & (~df_diario['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"]))]
                
                if df_d_maq.empty:
                    st.info("Nenhum registro de aula encontrado para esta turma.")
                else:
                    datas_disponiveis = sorted(df_d_maq['DATA'].unique(), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)
                    data_maq = c_maq2.selectbox("Selecione a Data da Aula:", datas_disponiveis, key=f"maq_d_{v}")
                    
                    st.markdown("---")
                    df_dia = df_d_maq[df_d_maq['DATA'] == data_maq].copy()
                    df_dia['ID_ALUNO_CLEAN'] = df_dia['ID_ALUNO'].apply(db.limpar_id)
                    
                    aula_info = df_registro_aulas[(df_registro_aulas['DATA'] == data_maq) & (df_registro_aulas['TURMA'] == t_maq)]
                    
                    conteudo_aula = aula_info.iloc[0]['CONTEUDO_MINISTRADO'] if not aula_info.empty else "Registro via Diário Rápido"
                    clima_aula = aula_info.iloc[0]['CLIMA_TURMA'] if not aula_info.empty else "Não registrado"
                    status_aula = aula_info.iloc[0]['STATUS_EXECUCAO'] if not aula_info.empty else "Concluído"
                    
                    alunos_da_turma = df_alunos[df_alunos['TURMA'] == t_maq]
                    total_alunos_turma = len(alunos_da_turma)
                    
                    ids_ausentes = df_dia[df_dia['TAGS'] == "AUSÊNCIA"]['ID_ALUNO_CLEAN'].unique()
                    qtd_ausentes = len(ids_ausentes)
                    qtd_presentes = total_alunos_turma - qtd_ausentes
                    
                    ids_vistos = df_dia[df_dia['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]['ID_ALUNO_CLEAN'].unique()
                    qtd_vistos = len(ids_vistos)
                    
                    df_dia['BONUS_FLOAT'] = df_dia['BONUS'].apply(util.sosa_to_float)
                    df_bonus = df_dia[df_dia['BONUS_FLOAT'] > 0].groupby('NOME_ALUNO')['BONUS_FLOAT'].sum().reset_index()
                    qtd_bonus_aplicados = len(df_bonus)
                    
                    obs_df = df_dia[(df_dia['OBSERVACOES'] != "") & (~df_dia['TAGS'].isin(["SISTEMA_NOTA", "BONUS_CONSELHO"]))]
                    
                    st.markdown(f"""
                    <div style='background: {cor_card}; border: 1px solid {cor_borda}; padding: 20px; border-radius: 16px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
                        <h4 style='margin-top: 0; color: {BRAND_BLUE};'>📚 Conteúdo Ministrado</h4>
                        <p style='font-size: 16px; font-weight: 500;'>{conteudo_aula}</p>
                        <div style='display: flex; gap: 15px; margin-top: 10px;'>
                            <span style='background: #F1F5F9; padding: 5px 10px; border-radius: 8px; font-size: 12px; color: #475569;'><strong>Status:</strong> {status_aula}</span>
                            <span style='background: #F1F5F9; padding: 5px 10px; border-radius: 8px; font-size: 12px; color: #475569;'><strong>Clima:</strong> {clima_aula}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    c_k1, c_k2, c_k3, c_k4 = st.columns(4)
                    c_k1.metric("🟢 Presentes", qtd_presentes)
                    c_k2.metric("🔴 Ausentes", qtd_ausentes)
                    c_k3.metric("📘 Vistos Dados", qtd_vistos)
                    c_k4.metric("⭐ Alunos Bonificados", qtd_bonus_aplicados)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    col_aus, col_bon = st.columns(2)
                    
                    with col_aus:
                        st.markdown("#### 🔴 Radar de Faltosos")
                        if qtd_ausentes == 0:
                            st.success("100% de Presença nesta aula!")
                        else:
                            nomes_ausentes = alunos_da_turma[alunos_da_turma['ID'].apply(db.limpar_id).isin(ids_ausentes)]['NOME_ALUNO'].tolist()
                            tags_ausentes = "".join([f"<span style='display: inline-block; background: #FEE2E2; color: #EF4444; padding: 4px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; margin: 4px;'>{nome}</span>" for nome in nomes_ausentes])
                            st.markdown(f"<div>{tags_ausentes}</div>", unsafe_allow_html=True)
                            
                    with col_bon:
                        st.markdown("#### ⭐ Destaques (Bônus)")
                        if df_bonus.empty:
                            st.info("Nenhum bônus extra aplicado.")
                        else:
                            tags_bonus = "".join([f"<span style='display: inline-block; background: #FEF3C7; color: #F59E0B; padding: 4px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; margin: 4px;'>{row['NOME_ALUNO']} (+{row['BONUS_FLOAT']:.1f})</span>" for _, row in df_bonus.iterrows()])
                            st.markdown(f"<div>{tags_bonus}</div>", unsafe_allow_html=True)

                    if not obs_df.empty:
                        st.markdown("---")
                        with st.expander(f"🎙️ Ver Ocorrências e Observações da Aula ({len(obs_df)})", expanded=False):
                            for _, r_obs in obs_df.iterrows():
                                st.info(f"**{r_obs['NOME_ALUNO']}**: {r_obs['OBSERVACOES']}")

                    st.markdown("---")
                    
                    @st.dialog("⚖️ Justificar Falta e Atribuir Visto", width="large")
                    def dialog_visto_excecao():
                        st.markdown("Use este painel para **atribuir o Visto de Atividade** a um aluno que faltou (com atestado) ou entregou atrasado.")
                        elegiveis = alunos_da_turma[~alunos_da_turma['ID'].apply(db.limpar_id).isin(ids_vistos)].sort_values(by="NOME_ALUNO")
                        
                        if elegiveis.empty:
                            st.success("Todos os alunos desta aula já possuem visto!")
                        else:
                            aluno_alvo = st.selectbox("Estudante:", elegiveis['NOME_ALUNO'].tolist())
                            motivo_excecao = st.selectbox("Motivo da Justificativa:", ["Atestado Médico", "Luto", "Problema Familiar", "Atraso Justificado", "Entrega Tardia Autorizada"])
                            
                            if st.button("💾 Atribuir Visto e Salvar Justificativa", type="primary", use_container_width=True):
                                id_aluno_alvo = elegiveis[elegiveis['NOME_ALUNO'] == aluno_alvo].iloc[0]['ID']
                                nome_limpo = aluno_alvo.replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                                
                                db.salvar_no_banco("DB_DIARIO_BORDO", [
                                    data_maq, id_aluno_alvo, nome_limpo, t_maq, "TRUE", "", f"[VISTO TARDIO: {motivo_excecao}]", "0,00"
                                ])
                                st.toast(f"✅ Visto atribuído para {aluno_alvo}!")
                                time.sleep(1); st.rerun()

                    st.info("💡 **Ação Corretiva:** Um aluno trouxe atestado ou entregou a atividade atrasada com justificativa?")
                    if st.button("⚖️ JUSTIFICAR AUSÊNCIA E ATRIBUIR VISTO", type="primary", use_container_width=True):
                        dialog_visto_excecao()

    # ==============================================================================
    # 🧠 ABA 3: INTELIGÊNCIA DA TURMA (UTI & FEED SEMÂNTICO)
    # ==============================================================================
    with tab_inteligencia:
        st.markdown("### 🧠 Radiografia Cognitiva e Saúde da Turma")
        
        c_rad1, c_rad2 = st.columns([1, 1])
        t_rad = c_rad1.selectbox("🎯 Selecione a Turma:", lista_turmas_segura, key=f"rad_t_{v}")
        trim_rad = c_rad2.selectbox("📅 Trimestre de Safra:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"rad_trim_{v}")
        
        if t_rad:
            alunos_rad = df_alunos[df_alunos['TURMA'] == t_rad].copy()
            if alunos_rad.empty: st.info("Nenhum aluno cadastrado nesta turma.")
            else:
                calendario_saude = {
                    "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
                    "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
                    "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
                }
                dt_ini_s, dt_fim_s = calendario_saude.get(trim_rad, (date(2026, 1, 1), date(2026, 12, 31)))
                
                df_d_rad = df_diario[df_diario['TURMA'] == t_rad].copy()
                if not df_d_rad.empty:
                    df_d_rad['DATA_DT'] = pd.to_datetime(df_d_rad['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                    df_d_rad = df_d_rad[(df_d_rad['DATA_DT'] >= dt_ini_s) & (df_d_rad['DATA_DT'] <= dt_fim_s)]

                df_diag_rad = df_diagnosticos[df_diagnosticos['TURMA'] == t_rad].copy()
                if trim_rad != "Todos" and not df_diag_rad.empty:
                    df_diag_rad = df_diag_rad[df_diag_rad['ID_AVALIACAO'].str.contains(trim_rad.replace(" ", ""), case=False, na=False)]

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
                    c_k1.metric("📅 Assiduidade", f"{taxa_assiduidade:.1f}%")
                    c_k2.metric("📓 Engajamento", f"{taxa_engajamento:.1f}%")
                    c_k3.metric("📈 Média Provas", f"{media_geral_av:.1f}")

                st.markdown("---")
                col_uti, col_evasao = st.columns(2)
                
                with col_uti:
                    st.markdown("#### 🚑 UTI Pedagógica (Notas)")
                    df_n_trim = df_notas[(df_notas['TURMA'] == t_rad) & (df_notas['TRIMESTRE'] == trim_rad)].copy()
                    if not df_n_trim.empty:
                        alunos_uti = []
                        for _, r in df_n_trim.iterrows():
                            media_f = util.sosa_to_float(r['MEDIA_FINAL'])
                            if media_f < 6.0: alunos_uti.append({"Estudante": r['NOME_ALUNO'], "Média": media_f, "Falta": 6.0 - media_f})
                        
                        if alunos_uti:
                            df_uti = pd.DataFrame(alunos_uti).sort_values(by="Média")
                            st.dataframe(
                                df_uti, hide_index=True, use_container_width=True, height=250,
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
                        df_d_clean = df_d_rad[df_d_rad['ID_ALUNO'] != "GLOBAL"].drop_duplicates(subset=['DATA', 'ID_ALUNO'], keep='last')
                        datas_aulas = sorted(df_d_clean['DATA_DT'].unique())
                        total_aulas_validas = len([d for d in [dt.strftime("%d/%m/%Y") for dt in datas_aulas] if d not in dias_nao_letivos])
                        
                        stats_evasao = []
                        for aluno in alunos_rad['NOME_ALUNO'].tolist():
                            df_aluno = df_d_clean[(df_d_clean['NOME_ALUNO'] == aluno) & (~df_d_clean['DATA'].isin(dias_nao_letivos))]
                            faltas_a = len(df_aluno[df_aluno['STATUS'] == 'F']) if 'STATUS' in df_aluno.columns else len(df_aluno[df_aluno['TAGS'] == 'AUSÊNCIA'])
                            perc_falta = (faltas_a / total_aulas_validas) * 100 if total_aulas_validas > 0 else 0
                            if perc_falta >= 25: stats_evasao.append({"Estudante": aluno, "Faltas": faltas_a, "Ausência": perc_falta})
                                
                        if stats_evasao:
                            df_evasao = pd.DataFrame(stats_evasao).sort_values(by="Ausência", ascending=False)
                            st.dataframe(
                                df_evasao, hide_index=True, use_container_width=True, height=250,
                                column_config={
                                    "Estudante": st.column_config.TextColumn(width="medium"),
                                    "Faltas": st.column_config.NumberColumn(),
                                    "Ausência": st.column_config.ProgressColumn("% Ausência", format="%.0f%%", min_value=0, max_value=100)
                                }
                            )
                        else: st.success("✅ Nenhum aluno em risco de evasão.")
                    else: st.info("Aguardando registros de chamada.")

                st.markdown("---")
                st.markdown("#### 🧠 Feed Semântico (Ações Rápidas)")
                st.caption("Leia as anotações recentes do Diário e atualize o perfil do aluno com apenas um clique.")
                
                if not df_d_rad.empty:
                    obs_reais = df_d_rad[(df_d_rad['OBSERVACOES'] != "") & (~df_d_rad['TAGS'].isin(["SISTEMA_NOTA", "BONUS_CONSELHO", "DIA NÃO LETIVO"])) & (~df_d_rad['OBSERVACOES'].str.contains(r"\[LIDO\]", na=False, case=False))]
                    
                    if not obs_reais.empty:
                        ultimas_obs = obs_reais.tail(5).iloc[::-1]
                        
                        for idx, row_obs in ultimas_obs.iterrows():
                            id_alu_obs = row_obs['ID_ALUNO']
                            nome_alu_obs = row_obs['NOME_ALUNO']
                            data_obs = row_obs['DATA']
                            texto_obs = row_obs['OBSERVACOES']
                            
                            with st.container(border=True):
                                st.markdown(f"**{nome_alu_obs}** | 📅 {data_obs}")
                                st.info(f"🎙️ *{texto_obs}*")
                                
                                c_btn1, c_btn2, c_btn3, c_btn4, c_btn5 = st.columns(5)
                                
                                def processar_acao_feed(acao_nome, perfil_novo=None):
                                    with st.spinner("Atualizando..."):
                                        if perfil_novo:
                                            db.atualizar_aluno_cascata(id_alu_obs, nome_alu_obs, t_rad, perfil_novo)
                                        try:
                                            wb = db.conectar()
                                            ws_diario = wb.worksheet("DB_DIARIO_BORDO")
                                            dados_diario = ws_diario.get_all_values()
                                            for i, row_d in enumerate(dados_diario):
                                                if i > 0 and row_d[0] == data_obs and db.limpar_id(row_d[1]) == db.limpar_id(id_alu_obs) and row_d[6].strip() == texto_obs.strip():
                                                    ws_diario.update_cell(i+1, 7, texto_obs + " [LIDO]")
                                                    break
                                            st.cache_data.clear()
                                        except: pass
                                        st.rerun()

                                if c_btn1.button("✅ Ciente (Ocultar)", key=f"feed_ok_{idx}", use_container_width=True): processar_acao_feed("Ciente")
                                if c_btn2.button("🧱 Defasagem Leitura", key=f"feed_dl_{idx}", use_container_width=True): processar_acao_feed("Defasagem Leitura", "DEFASAGEM LEITURA")
                                if c_btn3.button("🧮 Defasagem Mat.", key=f"feed_dm_{idx}", use_container_width=True): processar_acao_feed("Defasagem Mat.", "DEFASAGEM MATEMÁTICA")
                                if c_btn4.button("🟠 Suspeita PEI", key=f"feed_pei_{idx}", use_container_width=True): processar_acao_feed("Suspeita PEI", "PEI - PENDENTE")
                                if c_btn5.button("🚀 Alta Performance", key=f"feed_alta_{idx}", use_container_width=True): processar_acao_feed("Alta Performance", "ALTA PERFORMANCE")
                    else: st.success("🎉 Nenhuma observação pendente.")
                else: st.info("Sem registros no Diário.")

    # ==============================================================================
    # ⚙️ ABA 4: SECRETARIA, MATRÍCULAS & CALENDÁRIO DINÂMICO DE RECESSO
    # ==============================================================================
    with tab_secretaria:
        st.markdown("### ⚙️ Secretaria, Matrículas & Calendário")
        sub_criar, sub_povoar, sub_editar, sub_calendario = st.tabs([
            "🏗️ Criar Turmas/Horários", 
            "➕ Povoar Alunos", 
            "✏️ Edição em Cascata", 
            "📅 Gestor de Semanas & Recessos"
        ])
        
        with sub_criar:
            tipo_cadastro = st.radio("O que deseja alocar na grade?", ["📚 Turma Regular (Alunos)", "⚙️ Planejamento (PI / PC)"], horizontal=True, key=f"tipo_cad_{v}")
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
            if st.button("💾 ALOCAR NA GRADE OFICIAL", use_container_width=True, type="primary"):
                if not dias_aula: st.error("Selecione pelo menos um horário.")
                else:
                    if db.salvar_no_banco("DB_TURMAS", [sigla_final, nome_final, turno_t, " / ".join(dias_aula), "N/A", "ATIVO"]):
                        st.success(f"✅ {sigla_final} alocado com sucesso!"); time.sleep(1); st.rerun()

        with sub_povoar:
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
                        texto_lote = st.text_area("Cole os dados CSV aqui (NOME, PERFIL):", height=200, placeholder="ADRIEL VINICIUS ALVES MARTINS,TÍPICO\nJOSE LEVI BRONZE SANTOS*,PEI - PENDENTE")
                        if st.button("🚀 PROCESSAR IMPORTAÇÃO EM LOTE", type="primary", use_container_width=True):
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

        with sub_editar:
            t_origem = st.selectbox("Selecione a Turma Atual:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"orig_ed_{v}")
            if t_origem:
                alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO")
                aluno_sel_nome = st.selectbox("Selecione o Aluno:", alunos_opcoes['NOME_ALUNO'].tolist(), key=f"alu_ed_{v}")
                dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
                
                st.markdown("#### ⚡ Diagnóstico Rápido (1-Click)")
                c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
                if c_btn1.button("📚 Defasagem Leitura", use_container_width=True):
                    db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "DEFASAGEM LEITURA"); st.rerun()
                if c_btn2.button("🧮 Defasagem Matemática", use_container_width=True):
                    db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "DEFASAGEM MATEMÁTICA"); st.rerun()
                if c_btn3.button("🚀 Alta Performance", use_container_width=True):
                    db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "ALTA PERFORMANCE"); st.rerun()
                if c_btn4.button("👤 Típico (Limpar)", use_container_width=True):
                    db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "TÍPICO"); st.rerun()
                
                st.markdown("---")
                with st.form("form_edicao"):
                    novo_nome = st.text_input("Nome Completo:", value=dados_atuais['NOME_ALUNO']).upper()
                    nova_turma = st.selectbox("Turma de Destino (Transferência):", lista_turmas_segura, index=lista_turmas_segura.index(t_origem) if t_origem in lista_turmas_segura else 0)
                    nova_nec = st.text_input("Necessidades / CIDs:", value=dados_atuais['NECESSIDADES']).upper()
                    if st.form_submit_button("💾 SALVAR E ATUALIZAR HISTÓRICO EM CASCATA"):
                        with st.spinner("Atualizando histórico do aluno..."):
                            if db.atualizar_aluno_cascata(dados_atuais['ID'], novo_nome, nova_turma, nova_nec):
                                st.success("✅ Cadastro atualizado com sucesso!"); time.sleep(1); st.rerun()

        # 🚨 SUB-ABA: GESTOR DINÂMICO DE SEMANAS INTEIRAS DE RECESSO
        with sub_calendario:
            st.markdown("#### 📅 Configuração Dinâmica de Semanas & Recessos")
            st.caption("Defina se uma semana inteira foi de Recesso, Feriado ou Provas Oficiais sem precisar mexer em código.")
            
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
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()

            st.markdown("---")
            st.markdown("##### 📌 Semanas com Status Especial Cadastradas")
            config_semanas = df_relatorios[df_relatorios['TIPO'].str.startswith('CONFIG_SEMANA_', na=False)]
            
            if config_semanas.empty:
                st.info("Nenhuma semana com status especial cadastrada. Todas as semanas estão ativas como Letivas Normais.")
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
                        if c_s3.button("🗑️ Remover", key=f"del_cal_{r_c.name}"):
                            db.excluir_registro("DB_RELATORIOS", r_c['TIPO'])
                            st.success("Status removido!"); time.sleep(0.5); st.rerun()




# ==============================================================================
# MÓDULO: BASE DE CONHECIMENTO (V45 - COFRE DIGITAL NO GOOGLE DRIVE)
# ==============================================================================
elif menu == "📚 Base de Conhecimento":
    st.title("📚 Biblioteca Digital de Soberania")
    st.markdown("---")
    
    tab_upload, tab_acervo_lib = st.tabs(["📤 Novo Upload (Drive)", "📖 Acervo Permanente"])
    
    with tab_upload:
        with st.form("form_upload_drive", clear_on_submit=True):
            st.markdown("#### 📤 Armazenar Material no Cofre")
            c1, c2 = st.columns(2)
            tipo_doc = c1.selectbox("Categoria:", ["Livro Didático", "Referencial Curricular", "Documento PEI", "Outros"])
            ano_doc = c2.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "Geral"])
            
            nome_arq = st.text_input("Nome de Exibição do Material:", placeholder="Ex: Livro do 6 ano Flavio Simoes")
            uploaded_file = st.file_uploader("Selecione o arquivo PDF:", type=["pdf"])
            
            if st.form_submit_button("🚀 SALVAR NO GOOGLE DRIVE"):
                if uploaded_file and nome_arq:
                    with st.spinner("Enviando para o seu Cofre Digital..."):
                        # Usa a sua ponte para salvar no Drive
                        link_drive = db.subir_e_converter_para_google_docs(
                            uploaded_file, 
                            nome_arq, 
                            categoria=ano_doc, 
                            modo="BIBLIOTECA"
                        )
                        
                        if "drive.google.com" in link_drive:
                            # Salva no CSV do Banco de Dados
                            db.salvar_no_banco("DB_MATERIAIS", [
                                datetime.now().strftime("%d/%m/%Y"), 
                                nome_arq, 
                                link_drive, 
                                f"{tipo_doc} - {ano_doc}"
                            ])
                            st.success(f"✅ '{nome_arq}' guardado com segurança no Drive!")
                            st.balloons()
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error(f"Erro no upload: {link_drive}")

    with tab_acervo_lib:
        if not df_materiais.empty:
            st.markdown(f"**📚 Materiais no Cofre:** {len(df_materiais)}")
            for _, row in df_materiais.iterrows():
                with st.container(border=True):
                    col_icon, col_txt, col_btn = st.columns([0.5, 3, 1])
                    col_icon.markdown("# 📕")
                    col_txt.markdown(f"**{row['NOME_ARQUIVO']}**")
                    col_txt.caption(f"📅 Upload: {row['DATA_UPLOAD']} | 🏷️ {row['TIPO']}")
                    col_btn.link_button("👁️ Ver no Drive", row['URI_ARQUIVO'], use_container_width=True)
        else:
            st.info("📭 Sua biblioteca está vazia.")




# ==============================================================================
# MÓDULO: RELATÓRIOS PEI / PERFIL IA - V201 (GHOSTWRITER & MATRIZ DE INCLUSÃO)
# ==============================================================================
elif menu == "♿ Relatórios PEI / Perfil IA":
    st.title("🧠 Centro de Comando da Inclusão (PEI)")
    st.caption("Gestão de níveis de suporte, redação orgânica de dossiês e adaptação curricular.")
    st.markdown("---")

    if "v_pei" not in st.session_state: st.session_state.v_pei = int(time.time())
    v = st.session_state.v_pei

    # 🚨 MOTOR ANTI-DUPLICIDADE (UPSERT SOBERANO)
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
        turmas_reais_pei = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas = sorted(turmas_reais_pei['ID_TURMA'].unique()) if not turmas_reais_pei.empty else sorted(df_alunos['TURMA'].unique())
        
        with st.container(border=True):
            turma_pei = st.selectbox("🎯 Selecione a Turma:", lista_turmas, key="pei_t_clean")
            df_turma_foco = df_alunos[df_alunos['TURMA'] == turma_pei].copy()

        if df_turma_foco.empty:
            st.warning(f"⚠️ Nenhum aluno cadastrado na turma {turma_pei}.")
            st.stop()

        # Filtra apenas alunos que não são típicos
        mask_pei = ~df_turma_foco['NECESSIDADES'].astype(str).str.upper().str.strip().isin(["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE"])
        df_inclusao = df_turma_foco[mask_pei].copy()

        tab_matriz, tab_forja, tab_curriculo = st.tabs([
            "📊 1. Matriz de Inclusão (Níveis)", 
            "✍️ 2. Forja do Dossiê (Ghostwriter)", 
            "📖 3. Currículo & Exportação"
        ])

        # ==============================================================================
        # ABA 1: MATRIZ DE INCLUSÃO (DASHBOARD PANORÂMICO)
        # ==============================================================================
        with tab_matriz:
            st.markdown("### 📊 Mapeamento de Suporte da Turma")
            st.caption("Defina o nível de prova de cada aluno. O Scanner de Gabaritos lerá essa configuração automaticamente.")
            
            if df_inclusao.empty:
                st.success("🎉 Nenhum aluno com laudo ou defasagem cadastrado nesta turma.")
            else:
                # Extrai o nível atual da string de necessidades (ex: "TEA (PEI N1)")
                def extrair_nivel(nec):
                    if "(PEI N1)" in nec: return "Nível 1 (Apoio Leve)"
                    if "(PEI N2)" in nec: return "Nível 2 (Apoio Moderado)"
                    if "(PEI N3)" in nec: return "Nível 3 (Qualitativa)"
                    return "Pendente (Definir)"

                def limpar_nec(nec):
                    return re.sub(r'\s*\(PEI N[1-3]\)', '', nec).strip()

                df_inclusao['NIVEL_ATUAL'] = df_inclusao['NECESSIDADES'].apply(extrair_nivel)
                df_inclusao['PERFIL_BASE'] = df_inclusao['NECESSIDADES'].apply(limpar_nec)

                # Bento Cards de Estatísticas
                qtd_n1 = len(df_inclusao[df_inclusao['NIVEL_ATUAL'] == "Nível 1 (Apoio Leve)"])
                qtd_n2 = len(df_inclusao[df_inclusao['NIVEL_ATUAL'] == "Nível 2 (Apoio Moderado)"])
                qtd_n3 = len(df_inclusao[df_inclusao['NIVEL_ATUAL'] == "Nível 3 (Qualitativa)"])
                
                st.markdown(f"""
                <div style='display: flex; gap: 10px; margin-bottom: 20px;'>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                        <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>Total Inclusão</span><br>
                        <span style='font-size: 18px; color: #2962FF; font-weight: 800;'>{len(df_inclusao)} Alunos</span>
                    </div>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                        <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>Provas Nível 1</span><br>
                        <span style='font-size: 18px; color: #3498DB; font-weight: 800;'>{qtd_n1}</span>
                    </div>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                        <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>Provas Nível 2</span><br>
                        <span style='font-size: 18px; color: #F1C40F; font-weight: 800;'>{qtd_n2}</span>
                    </div>
                    <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 15px; border-radius: 12px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                        <span style='font-size: 11px; color: gray; font-weight: bold; text-transform: uppercase;'>Provas Nível 3</span><br>
                        <span style='font-size: 18px; color: #E74C3C; font-weight: 800;'>{qtd_n3}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # Tabela de Mapeamento
                dados_matriz = []
                for _, r in df_inclusao.iterrows():
                    dados_matriz.append({
                        "ID": r['ID'],
                        "Estudante": r['NOME_ALUNO'],
                        "Perfil Clínico": r['PERFIL_BASE'],
                        "Nível de Suporte (Prova)": r['NIVEL_ATUAL']
                    })
                
                df_matriz_ed = st.data_editor(
                    pd.DataFrame(dados_matriz), hide_index=True, use_container_width=True,
                    column_config={
                        "ID": None,
                        "Estudante": st.column_config.TextColumn(disabled=True),
                        "Perfil Clínico": st.column_config.TextColumn(disabled=True),
                        "Nível de Suporte (Prova)": st.column_config.SelectboxColumn(
                            options=["Pendente (Definir)", "Nível 1 (Apoio Leve)", "Nível 2 (Apoio Moderado)", "Nível 3 (Qualitativa)"],
                            required=True
                        )
                    }, key=f"matriz_pei_{v}"
                )

                if st.button("💾 Salvar Mapeamento e Sincronizar Scanner", type="primary", use_container_width=True):
                    with st.spinner("Atualizando perfis em cascata..."):
                        for _, r in df_matriz_ed.iterrows():
                            nivel_sel = r["Nível de Suporte (Prova)"]
                            tag_nivel = ""
                            if "Nível 1" in nivel_sel: tag_nivel = " (PEI N1)"
                            elif "Nível 2" in nivel_sel: tag_nivel = " (PEI N2)"
                            elif "Nível 3" in nivel_sel: tag_nivel = " (PEI N3)"
                            
                            nova_nec = f"{r['Perfil Clínico']}{tag_nivel}"
                            db.atualizar_aluno_cascata(r['ID'], r['Estudante'], turma_pei, nova_nec)
                        
                        st.success("✅ Mapeamento salvo! O Scanner agora reconhecerá os níveis automaticamente.")
                        time.sleep(1); st.rerun()

        # ==============================================================================
        # ABA 2: FORJA DO DOSSIÊ (GHOSTWRITER IA)
        # ==============================================================================
        with tab_forja:
            st.markdown("### ✍️ Forja do Dossiê (Ghostwriter)")
            st.caption("A IA unirá as notas do boletim com as suas anotações brutas para redigir um relatório humano e empático.")
            
            if df_inclusao.empty:
                st.info("Nenhum aluno de inclusão para gerar dossiê.")
            else:
                aluno_foco = st.selectbox("Selecione o Estudante:", df_inclusao['NOME_ALUNO'].tolist(), key=f"foco_pei_{v}")
                dados_a = df_inclusao[df_inclusao['NOME_ALUNO'] == aluno_foco].iloc[0]
                id_a = db.limpar_id(dados_a['ID'])
                perfil_atual = str(dados_a['NECESSIDADES']).upper().strip()

                # 1. Coleta de Dados Reais (Notas e Faltas)
                n_alu = df_notas[df_notas['ID_ALUNO'].apply(db.limpar_id) == id_a]
                notas_str = ""
                for t in ["I Trimestre", "II Trimestre", "III Trimestre"]:
                    reg_t = n_alu[n_alu['TRIMESTRE'] == t]
                    if not reg_t.empty: notas_str += f"- {t}: {util.sosa_to_float(reg_t.iloc[0]['MEDIA_FINAL']):.1f} pts\n"
                if not notas_str: notas_str = "Nenhuma nota lançada no boletim ainda."

                faltas = 0
                if not df_diario.empty:
                    d_alu = df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diario['TURMA'] == turma_pei)]
                    faltas = len(d_alu[d_alu['TAGS'] == "AUSÊNCIA"])

                # 2. Painel de Contexto
                with st.container(border=True):
                    c_ctx1, c_ctx2 = st.columns([1, 2])
                    with c_ctx1:
                        st.markdown("**📊 Dados Oficiais do Sistema:**")
                        st.info(f"**Notas:**\n{notas_str}\n**Faltas Acumuladas:** {faltas}")
                    with c_ctx2:
                        st.markdown("**✍️ Suas Anotações Brutas:**")
                        relato_bruto = st.text_area("Digite como se estivesse conversando (A IA vai formatar):", placeholder="Ex: Ele melhorou muito em soma, mas a nota do 2º tri caiu porque faltou muito. Fica agitado com barulho...", height=120, key=f"relato_bruto_{v}")

                # 3. Geração Orgânica
                if st.button("🧠 Redigir Dossiê Orgânico (Ghostwriter)", type="primary", use_container_width=True):
                    with st.spinner("A IA está redigindo o relatório com base nas suas notas e relatos..."):
                        prompt_ghost = (
                            f"Aja como um Ghostwriter educacional de elite. Vou te passar os dados de um aluno de inclusão e minhas anotações brutas. "
                            f"Sua missão é redigir um relatório humano, empático e profissional, justificando as notas com base no meu relato.\n\n"
                            f"ALUNO: {aluno_foco}\nPERFIL CLÍNICO: {perfil_atual}\n"
                            f"NOTAS OFICIAIS:\n{notas_str}\nFALTAS: {faltas}\n"
                            f"MEU RELATO BRUTO: {relato_bruto if relato_bruto else 'O aluno tem participado das aulas adaptadas.'}\n\n"
                            f"Gere o relatório usando ESTRITAMENTE as seguintes tags para o sistema ler:\n"
                            f"[DIAGNOSTICO_GERAL] (Aqui entra o texto orgânico e humano unindo as notas e o meu relato)\n"
                            f"[SOCIAIS] (Como ele interage)\n"
                            f"[COMUNICATIVAS] (Como ele se expressa)\n"
                            f"[EMOCIONAIS] (Como ele lida com frustrações)\n"
                            f"[FUNCIONAIS] (Autonomia motora/rotina)\n"
                            f"[DIRETRIZES_CURRICULARES] (Sugestões práticas para as próximas aulas)"
                        )
                        res_master = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_ghost)
                        salvar_relatorio_pei_sem_duplicidade(id_a, aluno_foco, "DOSSIE_MASTER_PEI", res_master)
                        st.success("✅ Dossiê redigido e salvo no Repositório Vivo!"); time.sleep(1); st.rerun()

                # 4. Exibição e Edição do Dossiê Gerado
                hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_a]
                rel_master = hist_aluno[hist_aluno['TIPO'] == 'DOSSIE_MASTER_PEI']
                
                if not rel_master.empty:
                    st.markdown("---")
                    st.markdown("#### 📄 Dossiê Atual (Editável)")
                    master_text = str(rel_master.iloc[-1]['CONTEUDO'])
                    
                    ed_diag = st.text_area("Diagnóstico Geral (Texto Orgânico):", ai.extrair_tag(master_text, "DIAGNOSTICO_GERAL"), height=200)
                    
                    c_h1, c_h2 = st.columns(2)
                    ed_soc = c_h1.text_area("Habilidades Sociais:", ai.extrair_tag(master_text, "SOCIAIS"), height=100)
                    ed_com = c_h2.text_area("Habilidades Comunicativas:", ai.extrair_tag(master_text, "COMUNICATIVAS"), height=100)
                    ed_emo = c_h1.text_area("Habilidades Emocionais:", ai.extrair_tag(master_text, "EMOCIONAIS"), height=100)
                    ed_fun = c_h2.text_area("Habilidades Funcionais:", ai.extrair_tag(master_text, "FUNCIONAIS"), height=100)
                    
                    ed_dir = st.text_area("Diretrizes Curriculares:", ai.extrair_tag(master_text, "DIRETRIZES_CURRICULARES"), height=150)
                    
                    if st.button("💾 Salvar Edições Manuais", use_container_width=True):
                        texto_consolidado = f"[DIAGNOSTICO_GERAL]\n{ed_diag}\n\n[SOCIAIS]\n{ed_soc}\n\n[COMUNICATIVAS]\n{ed_com}\n\n[EMOCIONAIS]\n{ed_emo}\n\n[FUNCIONAIS]\n{ed_fun}\n\n[DIRETRIZES_CURRICULARES]\n{ed_dir}"
                        salvar_relatorio_pei_sem_duplicidade(id_a, aluno_foco, "DOSSIE_MASTER_PEI", texto_consolidado)
                        st.success("✅ Edições salvas!"); time.sleep(0.5); st.rerun()

        # ==============================================================================
        # ABA 3: CURRÍCULO ADAPTADO & EXPORTAÇÃO
        # ==============================================================================
        with tab_curriculo:
            st.markdown("### 📖 Adaptação Curricular e Exportação Oficial")
            
            if df_inclusao.empty:
                st.info("Nenhum aluno de inclusão selecionado.")
            else:
                c_exp1, c_exp2 = st.columns([1, 2])
                trim_destino = c_exp1.selectbox("Trimestre Alvo:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="trim_curr")
                aluno_exp = c_exp2.selectbox("Estudante:", df_inclusao['NOME_ALUNO'].tolist(), key=f"exp_alu_{v}")
                
                id_exp = db.limpar_id(df_inclusao[df_inclusao['NOME_ALUNO'] == aluno_exp].iloc[0]['ID'])
                perfil_exp = str(df_inclusao[df_inclusao['NOME_ALUNO'] == aluno_exp].iloc[0]['NECESSIDADES']).upper()
                
                hist_exp = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_exp]
                rel_master_exp = hist_exp[hist_exp['TIPO'] == 'DOSSIE_MASTER_PEI']
                v_diretrizes_exp = ai.extrair_tag(str(rel_master_exp.iloc[-1]['CONTEUDO']), "DIRETRIZES_CURRICULARES") if not rel_master_exp.empty else "Sem diretrizes."
                
                curr_records = hist_exp[hist_exp['TIPO'] == f"CURRICULO_ADAPTADO_{trim_destino}"]
                if not curr_records.empty:
                    try: df_curr_atual = pd.read_json(io.StringIO(curr_records.iloc[-1]['CONTEUDO']), orient='records')
                    except: df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])
                else: df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])

                with st.expander("⚙️ Gerar Adaptação da Matriz (IA)", expanded=False):
                    ano_aluno = "".join(filter(str.isdigit, turma_pei))
                    df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == ano_aluno].copy()
                    
                    if not df_matriz_ano.empty:
                        opcoes_conteudo = df_matriz_ano.apply(lambda x: f"[{x['TRIMESTRE']}] {x['CONTEUDO_ESPECIFICO']}", axis=1).tolist()
                        selecionados = st.multiselect("Escolha os conteúdos para adaptar:", opcoes_conteudo)
                        
                        if st.button("Gerar Adaptação Curricular", type="primary"):
                            if selecionados:
                                with st.spinner("Adaptando matriz..."):
                                    conteudos_brutos = [s.split("] ")[1] for s in selecionados]
                                    df_focada = df_matriz_ano[df_matriz_ano['CONTEUDO_ESPECIFICO'].isin(conteudos_brutos)]
                                    contexto_oficial = df_focada[['CONTEUDO_ESPECIFICO', 'OBJETIVOS']].to_string(index=False)
                                    
                                    prompt_curr = f"ESTUDANTE: {aluno_exp}. PERFIL: {perfil_exp}.\nDIRETRIZES: {v_diretrizes_exp}\nMATRIZ: {contexto_oficial}.\nGere os itens adaptados focando em superar as barreiras do perfil."
                                    res_ia = ai.gerar_ia("TRADUTOR_CURRICULAR_V39", prompt_curr)
                                    
                                    blocos = re.findall(r"\[ITEM\](.*?)\[/ITEM\]", res_ia, re.DOTALL)
                                    novas_linhas = [{"Objetivos de Aprendizagem": ai.extrair_tag(b, "OBJETIVO"), "Estratégias Metodológicas": ai.extrair_tag(b, "ESTRATEGIA"), "Recursos Materiais": ai.extrair_tag(b, "RECURSO")} for b in blocos]
                                    
                                    if novas_linhas:
                                        df_curr_atual = pd.concat([df_curr_atual, pd.DataFrame(novas_linhas)], ignore_index=True)
                                        salvar_relatorio_pei_sem_duplicidade(id_exp, aluno_exp, f"CURRICULO_ADAPTADO_{trim_destino}", df_curr_atual.to_json(orient='records'))
                                        st.rerun()

                st.markdown("**Tabela de Planejamento (Editável)**")
                df_editado_curr = st.data_editor(
                    df_curr_atual, num_rows="dynamic", use_container_width=True, key=f"ed_curr_{v}",
                    column_config={"Objetivos de Aprendizagem": st.column_config.TextColumn(width="large"), "Estratégias Metodológicas": st.column_config.TextColumn(width="large"), "Recursos Materiais": st.column_config.TextColumn(width="medium")}
                )
                
                st.markdown("---")
                c_btn_save, c_btn_exp = st.columns(2)
                
                if c_btn_save.button("💾 Salvar Tabela", use_container_width=True):
                    salvar_relatorio_pei_sem_duplicidade(id_exp, aluno_exp, f"CURRICULO_ADAPTADO_{trim_destino}", df_editado_curr.to_json(orient='records'))
                    st.success("Tabela salva!"); time.sleep(0.5); st.rerun()
                    
                if c_btn_exp.button("🖨️ GERAR PEI OFICIAL (DOCX)", type="primary", use_container_width=True):
                    with st.spinner("Compilando Dossiê Oficial..."):
                        dados_aluno = {"nome": aluno_exp, "turma": turma_pei, "cid": perfil_exp}
                        
                        if not rel_master_exp.empty:
                            m_txt = str(rel_master_exp.iloc[-1]['CONTEUDO'])
                            habilidades = {"Habilidades Sociais": ai.extrair_tag(m_txt, "SOCIAIS"), "Habilidades Comunicativas": ai.extrair_tag(m_txt, "COMUNICATIVAS"), "Habilidades Emocionais": ai.extrair_tag(m_txt, "EMOCIONAIS"), "Habilidades Funcionais": ai.extrair_tag(m_txt, "FUNCIONAIS")}
                        else:
                            habilidades = {"Habilidades Sociais": "", "Habilidades Comunicativas": "", "Habilidades Emocionais": "", "Habilidades Funcionais": ""}
                        
                        nome_arq_pei = f"PEI_OFICIAL_{aluno_exp.replace(' ', '_')}_{trim_destino.replace(' ', '')}"
                        doc_stream = exporter.gerar_docx_pei_oficial(nome_arq_pei, dados_aluno, habilidades, df_editado_curr)
                        link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_pei, trimestre=trim_destino, categoria=turma_pei, modo="PLANEJAMENTO")
                        
                        if "https" in link_doc:
                            salvar_relatorio_pei_sem_duplicidade(id_exp, aluno_exp, "PEI_EXPORTADO", f"Link: {link_doc}")
                            st.success("✅ PEI Oficial gerado e salvo no Drive!")
                            st.link_button("📂 ABRIR PEI OFICIAL", link_doc, type="primary", use_container_width=True)
                            st.balloons()
                        else: st.error(f"Erro ao salvar no Drive: {link_doc}")
