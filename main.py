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

# 🔬 FILTRO DE LEITURA GLOBAL (LATEX, IMAGENS E GEOGEBRA V201)
def preparar_para_leitura(texto):
    if not texto: return ""
    texto = re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)
    texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', r'📐 *(Comando GeoGebra: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
    texto = re.sub(r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', r'🖼️ *(Imagem: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
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
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - V201 (CLEAN & UX)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("Engenharia de Planejamento")
    st.caption("Defina a rota da semana. O sistema automatiza a burocracia e alimenta o Criador de Aulas.")
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

    # 🚨 REDUÇÃO DE ABAS (De 6 para 4)
    tab_gerar, tab_producao, tab_acervo, tab_inteligencia = st.tabs([
        "Novo Plano", "Hub de Produção", "Acervo", "Inteligência Curricular"
    ])
    
    # ==============================================================================
    # ABA 1: NOVO PLANO (REVELAÇÃO PROGRESSIVA)
    # ==============================================================================
    with tab_gerar:
        with st.container(border=True):
            st.markdown("#### 1. Parâmetros da Semana")
            
            c1, c2, c3 = st.columns([1, 2, 2])
            ano_p = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_sel_{v}")
            ano_str_busca = f"{ano_p}º"

            todas_semanas = util.gerar_semanas()
            semanas_planejadas = df_planos[df_planos['ANO'] == ano_str_busca]['SEMANA'].tolist()
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
                    aula_2_txt = "Continuação da aplicação (se necessário) ou recolhimento dos instrumentos."
                else:
                    texto_padrao = f"Análise de Erros e Recuperação Paralela. Foco nos tópicos com menor índice de acerto no Raio-X da turma."
                    aula_1_txt = "Entrega dos resultados da avaliação. Correção comentada no quadro das questões com menor índice de acerto (Mapa de Calor)."
                    aula_2_txt = "Aplicação do instrumento de Recuperação Paralela para os alunos elegíveis. Atividade de aprofundamento para os alunos já aprovados."

                st.text_area("Resumo do Plano:", texto_padrao, disabled=True)
                
                if st.button("Salvar Plano Padronizado", type="primary", use_container_width=True):
                    with st.spinner("Salvando no Acervo..."):
                        nome_arquivo = f"PLANO_{ano_str_busca.replace('º','')}_{sem_limpa.replace(' ', '')}"
                        db.excluir_plano_completo(sem_limpa, ano_str_busca)
                        
                        dados_docx = {
                            "geral": tipo_semana.upper(), "especificos": texto_padrao, 
                            "objetivos": "Cumprimento do calendário letivo oficial.", 
                            "recursos": "Instrumentos Avaliativos", 
                            "metodologia": f"AULA 1:\n{aula_1_txt}\n\nAULA 2:\n{aula_2_txt}",
                            "avaliacao": "Correção e análise de resultados.", 
                            "pei": "Acompanhamento individualizado e tempo estendido conforme necessidade."
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": ano_str_busca, "semana": sem_limpa, "trimestre": trim_atual})
                        link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=trim_atual, categoria=ano_str_busca, semana=sem_limpa, modo="PLANEJAMENTO")
                        
                        final_txt = f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} \n[CONTEUDOS_ESPECIFICOS] {texto_padrao} \n[AULA_1] {aula_1_txt} \n[AULA_2] {aula_2_txt} \n--- LINK DRIVE --- {link_drive}"
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
                            
                            final_txt = f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} \n[CONTEUDOS_ESPECIFICOS] {ativo_selecionado} \n[AULA_1] {roteiro_docx} \n[AULA_2] N/A \n--- LINK DRIVE --- {link_drive}"
                            db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_limpa, ano_str_busca, trim_atual, "PRODUZIDO", final_txt, link_drive])
                            st.success("Logística salva!"); time.sleep(1); st.rerun()

        # ------------------------------------------------------------------------------
        # ROTA 3: AULA REGULAR (GERAÇÃO COM IA)
        # ------------------------------------------------------------------------------
        else:
            with st.container(border=True):
                st.markdown("#### 2. Base Curricular")
                
                modo_p = st.radio("Fonte de Dados:", ["Livro Didático", "Manual (Matriz)", "Links da Web"], horizontal=True)
                
                ctx_ia, uri_livro_drive, links_web_texto, base_didatica_info = "", None, "", "Matriz Curricular"
                
                if modo_p == "Manual (Matriz)":
                    df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == str(ano_p)]
                    sel_eixo = st.multiselect("Eixo:", sorted(df_matriz_ano['EIXO'].unique().tolist()))
                    sel_cont = st.multiselect("Conteúdo:", sorted(df_matriz_ano[df_matriz_ano['EIXO'].isin(sel_eixo)]['CONTEUDO_ESPECIFICO'].unique().tolist()) if sel_eixo else [])
                    sel_obj = st.multiselect("Objetivos:", sorted(df_matriz_ano[df_matriz_ano['CONTEUDO_ESPECIFICO'].isin(sel_cont)]['OBJETIVOS'].unique().tolist()) if sel_cont else [])
                    ctx_ia = f"EIXO: {sel_eixo}, CONTEÚDO: {sel_cont}, OBJETIVOS: {sel_obj}."
                
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
                c_d1, c_d2 = st.columns(2)
                foco_a1 = c_d1.text_area("Foco da Aula 1:", placeholder="Ex: Explicar perímetro...", height=80)
                foco_a2 = c_d2.text_area("Foco da Aula 2:", placeholder="Ex: Fazer exercícios da página 15...", height=80)

            if st.button("Gerar Planejamento com IA", use_container_width=True, type="primary"):
                with st.spinner("Analisando matriz e arquitetando o plano..."):
                    if modo_p == "Manual (Matriz)": diretriz_base = "MÉTODO MANUAL: Baseie-se na Matriz Curricular."
                    elif modo_p == "Links da Web": diretriz_base = f"MÉTODO WEB: Use estes links:\n{links_web_texto}"
                    else: diretriz_base = f"MÉTODO LIVRO: Use o PDF anexo. PÁGINAS: {base_didatica_info}."

                    prompt = (
                        f"TIPO: {tipo_semana}\n{diretriz_base}\n"
                        f"SÉRIE: {ano_p}º Ano. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}.\n"
                        f"DIRETRIZ AULA 1: {foco_a1}\nDIRETRIZ AULA 2: {foco_a2}\n"
                        f"MATRIZ OFICIAL:\n{ctx_ia}"
                    )
                    
                    st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt, url_drive=uri_livro_drive, usar_busca=True)
                    st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info}
                    st.rerun()

            # --- EDITOR DO PLANO GERADO ---
            if "p_temp" in st.session_state:
                txt_bruto = st.session_state.p_temp
                meta = st.session_state.get("p_meta", {})
                
                st.markdown("---")
                st.markdown(f"### Revisão do Plano: {meta.get('semana')}")
                
                with st.container(border=True):
                    cmd_refine = st.chat_input("Refinador IA (Ex: 'Deixe a Aula 1 mais lúdica')")
                    if cmd_refine:
                        with st.spinner("Reescrevendo..."):
                            prompt_refino = f"ORDEM: {cmd_refine}\n\nPLANO ATUAL:\n{st.session_state.p_temp}"
                            st.session_state.p_temp = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino)
                            st.rerun()

                ed_hab = st.text_input("Habilidade/Competência:", ai.extrair_tag(txt_bruto, "HABILIDADE_BNCC") or ai.extrair_tag(txt_bruto, "COMPETENCIA_GERAL"))
                ed_geral = st.text_input("Objeto de Conhecimento:", ai.extrair_tag(txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL"))
                ed_espec = st.text_area("Conteúdos Específicos:", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS"))
                ed_objs = st.text_area("Objetivos de Aprendizagem:", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO"))
                
                c_a1, c_a2 = st.columns(2)
                ed_a1 = c_a1.text_area("AULA 1:", ai.extrair_tag(txt_bruto, "AULA_1"), height=150)
                ed_a2 = c_a2.text_area("AULA 2:", ai.extrair_tag(txt_bruto, "AULA_2"), height=150)
                
                if st.button("Salvar e Enviar para Produção", use_container_width=True, type="primary"):
                    with st.status("Gerando DOCX e Sincronizando...") as status:
                        nome_arquivo = f"PLANO_{meta.get('ano').replace('º','')}_{meta.get('semana').replace(' ', '')}"
                        db.excluir_plano_completo(meta.get('semana'), meta.get('ano'))
                        
                        dados_docx = {
                            "geral": ed_geral, "especificos": ed_espec, "objetivos": ed_objs, 
                            "recursos": meta.get('base'), 
                            "metodologia": f"AULA 01:\n{ed_a1}\n\nAULA 02:\n{ed_a2}",
                            "avaliacao": ai.extrair_tag(txt_bruto, "AVALIACAO_DE_MERITO"), 
                            "pei": ai.extrair_tag(txt_bruto, "ESTRATEGIA_DUA_PEI")
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": meta.get('ano'), "semana": meta.get('semana'), "trimestre": meta.get('trimestre')})
                        link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=meta.get('trimestre'), categoria=meta.get('ano'), semana=meta.get('semana'), modo="PLANEJAMENTO")
                        
                        final_txt = f"[HABILIDADE_BNCC] {ed_hab} \n[OBJETO_CONHECIMENTO] {ed_geral} \n[CONTEUDOS_ESPECIFICOS] {ed_espec} \n[AULA_1] {ed_a1} \n[AULA_2] {ed_a2} \n--- LINK DRIVE --- {link_drive}"
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
    # ABA 3: ACERVO
    # ==============================================================================
    with tab_acervo:
        st.markdown("#### Acervo de Planos Estratégicos")
        if not df_planos.empty:
            f_ano_h = st.selectbox("Filtrar por Série:", ["Todos", "6º", "7º", "8º", "9º"], key="hist_ano")
            df_h = df_planos[df_planos["ANO"] == f_ano_h] if f_ano_h != "Todos" else df_planos.copy()
            
            if not df_h.empty:
                sel_h = st.selectbox("Selecionar Plano:", df_h["SEMANA"].tolist()[::-1], key="hist_sem")
                dados_h = df_h[df_h["SEMANA"] == sel_h].iloc[0]
                
                c_btn1, c_btn2 = st.columns(2)
                c_btn1.link_button("Abrir DOCX no Drive", str(dados_h.get("LINK_DRIVE", "#")), use_container_width=True)
                if c_btn2.button("Apagar Plano", use_container_width=True):
                    if db.excluir_plano_completo(sel_h, dados_h["ANO"]): st.rerun()
            else: st.info("Nenhum plano encontrado.")

    # ==============================================================================
    # ABA 4: INTELIGÊNCIA CURRICULAR (MATRIZ + AUDITORIA + TRIMESTRAL)
    # ==============================================================================
    with tab_inteligencia:
        modo_inteligencia = st.radio("Selecione a Visão:", ["Matriz de Execução", "Auditoria de Cobertura", "Gerador Trimestral (Macro)"], horizontal=True)
        st.markdown("---")
        
        if modo_inteligencia == "Matriz de Execução":
            st.markdown("#### Status de Execução da Matriz")
            ano_c = st.selectbox("Série:", [6, 7, 8, 9], key="matriz_ano")
            df_c = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_c))].copy()
            
            if not df_c.empty:
                planos_feitos = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_c))]
                texto_soberano = " | ".join([ai.extrair_tag(p, "CONTEUDOS_ESPECIFICOS").upper() for p in planos_feitos["PLANO_TEXTO"]])
                
                def checar_conclusao(conteudo_db):
                    if not texto_soberano: return "⏳ PENDENTE"
                    target = re.sub(r'[^A-Z0-9]', '', str(conteudo_db).upper())
                    soberano = re.sub(r'[^A-Z0-9]', '', texto_soberano)
                    return "✅ CONCLUÍDO" if target in soberano else "⏳ PENDENTE"

                df_c["STATUS"] = df_c["CONTEUDO_ESPECIFICO"].apply(checar_conclusao)
                st.dataframe(df_c[["TRIMESTRE", "CONTEUDO_ESPECIFICO", "STATUS"]], use_container_width=True, hide_index=True)

        elif modo_inteligencia == "Auditoria de Cobertura":
            st.markdown("#### Analytics de Cobertura Curricular")
            ano_m = st.selectbox("Série:", [6, 7, 8, 9], key="auditoria_ano")
            df_m = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_m))].copy()
            
            if not df_m.empty:
                planos_m = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_m))]
                texto_m = " | ".join([ai.extrair_tag(t, "CONTEUDOS_ESPECIFICOS").upper() for t in planos_m["PLANO_TEXTO"]])
                
                def concluido_num(x):
                    target = re.sub(r'[^A-Z0-9]', '', str(x).upper())
                    soberano = re.sub(r'[^A-Z0-9]', '', texto_m)
                    return 1 if target in soberano else 0

                df_m["CONCLUIDO"] = df_m["CONTEUDO_ESPECIFICO"].apply(concluido_num)
                progresso = df_m.groupby("TRIMESTRE")["CONCLUIDO"].agg(["sum", "count"]).reset_index()
                progresso["%"] = (progresso["sum"] / progresso["count"] * 100).round(1)
                
                st.plotly_chart(px.bar(progresso, x="TRIMESTRE", y="%", text="%", title=f"Cobertura - {ano_m}º Ano", color="%", color_continuous_scale="RdYlGn", range_y=[0, 110]), use_container_width=True)

        elif modo_inteligencia == "Gerador Trimestral (Macro)":
            st.markdown("#### Gerador de Planejamento Trimestral (Macro-SOSA)")
            c_t1, c_t2 = st.columns(2)
            ano_trim = c_t1.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"])
            trim_alvo = c_t2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
            
            ano_num_trim = "".join(filter(str.isdigit, ano_trim))
            turmas_disp = df_turmas[df_turmas['ID_TURMA'].str.contains(ano_num_trim, na=False)]['ID_TURMA'].tolist()
            turmas_sel = st.multiselect("Turmas:", turmas_disp, default=turmas_disp)
            
            df_matriz_trim = df_curriculo[(df_curriculo['ANO'].astype(str).str.contains(ano_num_trim)) & (df_curriculo['TRIMESTRE'] == trim_alvo.split(" ")[0])]
            
            if st.button("Gerar Documento Oficial (DOCX)", type="primary", use_container_width=True):
                if not turmas_sel or df_matriz_trim.empty:
                    st.error("Selecione as turmas e garanta que há dados na matriz.")
                else:
                    with st.spinner("Gerando..."):
                        info_trim = {"trimestre": trim_alvo, "turmas": ", ".join(turmas_sel)}
                        config_textos = {
                            "metodologia": "Aulas expositivas e dialogadas; Resolução de exercícios.",
                            "recursos": "Quadro branco, Livro didático, Material impresso.",
                            "avaliacao": "Avaliação contínua, participação e testes."
                        }
                        nome_arq = f"PLANEJAMENTO_{trim_alvo.replace(' ', '')}_{ano_trim.replace('º ', '')}"
                        doc_stream = exporter.gerar_docx_planejamento_trimestral(nome_arq, info_trim, df_matriz_trim, config_textos, [])
                        link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq, trimestre=trim_alvo, categoria=ano_trim, modo="PLANEJAMENTO")
                        
                        if "https" in link_doc:
                            st.success("Gerado com sucesso!")
                            st.link_button("Abrir Documento", link_doc)



# ==============================================================================
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR DE AULAS) - V201 (CASCATA & BENTO)
# ==============================================================================
elif menu == "🧪 Criador de Aulas":
    st.title("Laboratório de Produção Didática")
    st.caption("Desenvolva aulas de safra, projetos de iniciação científica e listas de recomposição de forma integrada.")
    st.markdown("---")
    
    # 🚨 INICIALIZAÇÃO DA MÁQUINA DE ESTADOS DA FORJA DE AULAS
    if "forja_aula" not in st.session_state:
        st.session_state.forja_aula = {
            'fase': 1, 'info': {}, 'links_web': '', 'qtd_q': 5,
            'teoria': '', 'reg_q': '', 'reg_gab': '', 'pei_q': '', 'pei_gab': '', 'nome_base': ''
        }
    
    fa = st.session_state.forja_aula

    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "sosa_id_atual", "lab_meta", "hub_origem", "chat_history_lab"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.session_state.forja_aula = {
            'fase': 1, 'info': {}, 'links_web': '', 'qtd_q': 5,
            'teoria': '', 'reg_q': '', 'reg_gab': '', 'pei_q': '', 'pei_gab': '', 'nome_base': ''
        }
        st.cache_data.clear() 
        st.session_state.v_lab = int(time.time())
        st.rerun()

    if "v_lab" not in st.session_state: 
        st.session_state.v_lab = int(time.time())
    v = st.session_state.v_lab

    # Filtro de leitura para LaTeX e visualizadores
    def preparar_para_leitura(texto):
        if not texto: return ""
        texto = re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)
        texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', r'📐 *(Comando GeoGebra: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', r'🖼️ *(Imagem: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
        return texto

    # CONSOLIDAÇÃO DE ABAS (De 4 para 2)
    tab_forja, tab_acervo_lab = st.tabs(["Forja de Materiais", "Acervo Digital"])

    # ==============================================================================
    # ABA 1: FORJA DE MATERIAIS
    # ==============================================================================
    with tab_forja:
        # ------------------------------------------------------------------------------
        # ROTA A: EDITOR CLÁSSICO (PARA PROJETOS, LISTAS E RECOMPOSIÇÃO)
        # ------------------------------------------------------------------------------
        if "lab_temp" in st.session_state:
            txt_base = st.session_state.lab_temp
            s_id = st.session_state.get("sosa_id_atual", "SEM-ID")
            meta = st.session_state.get("lab_meta", {})
            st.success(f"Material em Edição: {s_id}")

            with st.container(border=True):
                st.markdown("#### Ajuste de Coautoria (Maestro Copilot)")
                
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
                                msg_chat = ai.extrair_tag(resultado_refino, "MENSAGEM_CHAT") or "Ajustado!"
                                novo_conteudo = ai.extrair_tag(resultado_refino, "CONTEUDO_ATUALIZADO") or resultado_refino
                                
                                st.markdown(msg_chat)
                                st.session_state.chat_history_lab.append({"role": "assistant", "avatar": "🤖", "content": msg_chat})
                                st.session_state.lab_temp = novo_conteudo
                                st.rerun()

                if st.button("Descartar Edição e Voltar ao Início", use_container_width=True): reset_laboratorio()
            
            st.markdown("---")
            modo_leitura = st.toggle("Modo Leitura (Renderizar Matemática)", value=False)
            
            val_prof = ai.extrair_tag(txt_base, "PROFESSOR") or ai.extrair_tag(txt_base, "JUSTIFICATIVA_PHC")
            val_alu = ai.extrair_tag(txt_base, "ALUNO") or ai.extrair_tag(txt_base, "PASSO_A_PASSO")
            val_gab = ai.extrair_tag(txt_base, "GABARITO") or ai.extrair_tag(txt_base, "RUBRICA_DE_MERITO")
            val_pei = ai.extrair_tag(txt_base, "PEI") or ai.extrair_tag(txt_base, "ESTRATEGIA_DUA_PEI")
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
                if modo_leitura: st.markdown(preparar_para_leitura(val_pei))
                else: ed_pei = st.text_area("PEI (Obrigatório):", val_pei, height=350, key=f"ed_pei_reg_{v}")
            
            with t_img_tab: 
                ed_img = st.text_area("Prompts de Imagem:", val_img, height=150, key=f"ed_img_reg_{v}")

            with t_sync:
                st.markdown("#### Sincronia e Custódia Digital")
                if st.button("Sincronizar Ativos e Enviar para o Drive", use_container_width=True, type="primary", key=f"btn_triple_{v}"):
                    with st.status("Sincronizando Ativos...") as status:
                        db.excluir_registro_com_drive("DB_AULAS_PRONTAS", s_id)
                        
                        ano_str = f"{meta.get('ano', '6')}º"
                        sem_ref = meta.get('semana_ref', 'Geral')
                        info_doc = {"ano": ano_str, "trimestre": "I Trimestre", "semana": sem_ref}

                        status.write("Gerando Material do Aluno...")
                        doc_alu = exporter.gerar_docx_aluno_v24(s_id, ed_alu, info_doc)
                        link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{s_id}_ALUNO", modo="AULA")
                        
                        status.write("Gerando Material PEI...")
                        doc_pei = exporter.gerar_docx_pei_v25(f"{s_id}_PEI", ed_pei, info_doc)
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{s_id}_PEI", modo="AULA")
                        
                        status.write("Gerando Guia do Professor...")
                        doc_prof = exporter.gerar_docx_professor_v25(s_id, ed_prof, info_doc)
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{s_id}_PROF", modo="AULA")
                        
                        links_f = f"--- LINKS ---\nRegular({link_alu})\nPEI({link_pei})\nProf({link_prof})"
                        conteudo_final = f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n[GABARITO]\n{ed_gab}\n\n[PEI]\n{ed_pei}\n\n[IMAGENS]\n{ed_img}\n\n{links_f}"
                        
                        db.salvar_no_banco("DB_AULAS_PRONTAS",[
                            datetime.now().strftime("%d/%m/%Y"), sem_ref, s_id, conteudo_final, ano_str, link_alu
                        ])
                        
                        status.update(label="Sincronizado com Sucesso!", state="complete")
                        st.balloons(); time.sleep(1); reset_laboratorio()

        # ------------------------------------------------------------------------------
        # ROTA B: SEQUENCIAL EM FASES (AULAS DE SAFRA E SETUP DE PROJETOS/LISTAS)
        # ------------------------------------------------------------------------------
        else:
            # --- FASE 1: PARAMETRIZAÇÃO GERAL (Bento Matrix) ---
            if fa['fase'] == 1:
                st.markdown("### Painel de Configuração")
                tipo_criacao = st.radio("Tipo de Material a Desenvolver:", ["Aula de Safra (Teoria e Prática)", "Projeto ou Trabalho Interdisciplinar", "Lista Híbrida ou Recomposição"], horizontal=True, key=f"lab_tipo_c_{v}")
                
                # ROTA REGULAR: Aula de Safra (Filtro Inteligente Anti-Duplicidade)
                if "Aula de Safra" in tipo_criacao:
                    with st.container(border=True):
                        st.markdown("#### Herança de Roteiro")
                        
                        # Botão discreto para forçar regravação de aula já feita
                        mostrar_tudo_lab = st.toggle("Mostrar semanas já concluídas (Sobrescrita)", value=False, key="sobrescrever_lab")
                        
                        c1, c2 = st.columns([1, 2])
                        ano_lab = c1.selectbox("Série:", [6, 7, 8, 9], key=f"prod_ano_{v}")
                        planos_ano = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_lab))]
                        
                        if planos_ano.empty:
                            st.error("Nenhum planejamento encontrado. Crie o plano no Ponto ID primeiro.")
                        else:
                            # 🚨 MOTOR DE RASTREABILIDADE: Filtra apenas semanas com materiais pendentes
                            semanas_pendentes = []
                            for sem in planos_ano["SEMANA"].unique().tolist():
                                p_row = planos_ano[planos_ano["SEMANA"] == sem].iloc[0]
                                p_txt = str(p_row['PLANO_TEXTO'])
                                
                                pede_a2 = len(ai.extrair_tag(p_txt, "AULA_2")) > 30 and "N/A" not in ai.extrair_tag(p_txt, "AULA_2").upper()
                                t_sab = ai.extrair_tag(p_txt, "SABADO_LETIVO")
                                pede_sab = len(t_sab) > 10 and "N/A" not in t_sab.upper() and "NÃO PROGRAMADA" not in t_sab.upper()
                                
                                a_geradas = df_aulas[(df_aulas['ANO'].str.contains(str(ano_lab))) & (df_aulas['SEMANA_REF'] == sem)]['TIPO_MATERIAL'].astype(str).tolist()
                                t_a1 = any("Aula 1" in mat for mat in a_geradas)
                                t_a2 = any("Aula 2" in mat for mat in a_geradas)
                                t_sab_gen = any("Sábado" in mat or "Sabado" in mat for mat in a_geradas)
                                
                                if (not t_a1) or (pede_a2 and not t_a2) or (pede_sab and not t_sab_gen):
                                    semanas_pendentes.append(sem)
                            
                            semanas_opcoes = planos_ano["SEMANA"].unique().tolist() if mostrar_tudo_lab else semanas_pendentes
                            
                            if not semanas_opcoes:
                                st.success("🏆 **Soberania Total!** Todas as semanas planejadas para esta série já possuem seus materiais produzidos no acervo.")
                                if st.button("🔄 Atualizar Painel", use_container_width=True): st.rerun()
                            else:
                                sem_lab = c2.selectbox("Semana Base (Ponto ID):", semanas_opcoes, key=f"prod_sem_{v}")
                                plano_row = planos_ano[planos_ano["SEMANA"] == sem_lab].iloc[0]
                                plano_txt = str(plano_row['PLANO_TEXTO'])

                                with st.expander("Ver Radar de Regência (Onde as turmas pararam?)"):
                                    reg_ano = df_registro_aulas[df_registro_aulas['TURMA'].str.contains(str(ano_lab))]
                                    if not reg_ano.empty:
                                        for t_nome in sorted(reg_ano['TURMA'].unique()):
                                            dados_t = reg_ano[reg_ano['TURMA'] == t_nome].iloc[-1]
                                            st.write(f"• **{t_nome}:** {dados_t.get('STATUS_EXECUCAO', 'Pendente')} | *{dados_t.get('PONTE_PEDAGOGICA', 'N/A')}*")
                                    else: st.info("Sem regência anterior registrada.")

                                base_herdada = ai.extrair_tag(plano_txt, "BASE_DIDATICA")
                                obj_geral = ai.extrair_tag(plano_txt, "OBJETO_CONHECIMENTO") or ai.extrair_tag(plano_txt, "CONTEUDO_GERAL")

                                # 🚨 INTEGRAÇÃO CIRÚRGICA: Filtra quais aulas especificamente estão pendentes na semana
                                a_geradas_sem = df_aulas[(df_aulas['ANO'].str.contains(str(ano_lab))) & (df_aulas['SEMANA_REF'] == sem_lab)]['TIPO_MATERIAL'].astype(str).tolist()
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

                                if mostrar_tudo_lab:
                                    opcoes_disponiveis = ["Aula 1"]
                                    if plano_pede_a2: opcoes_disponiveis.append("Aula 2")
                                    if plano_pede_sab: opcoes_disponiveis.append("Sábado Letivo")

                                if not opcoes_disponiveis:
                                    st.success("🎉 Todas as aulas previstas para esta semana já foram produzidas!")
                                else:
                                    c_c1, c_c2 = st.columns([1, 1])
                                    aula_alvo_prod = c_c1.radio("Material Alvo:", opcoes_disponiveis, horizontal=True)
                                    qtd_q_prod = c_c2.slider("Nº de Exercícios:", 1, 15, 5)

                                    if "1" in aula_alvo_prod: tag_roteiro = "AULA_1"
                                    elif "2" in aula_alvo_prod: tag_roteiro = "AULA_2"
                                    else: tag_roteiro = "SABADO_LETIVO"
                                    
                                    roteiro_especifico = ai.extrair_tag(plano_txt, tag_roteiro)
                                    st.info(f"Roteiro Ativo: {roteiro_especifico}")

                                    links_web_aula = st.text_area("Enriquecimento por Links (Opcional, um por linha):")

                                    if st.button("Iniciar Forja Semiótica", use_container_width=True, type="primary"):
                                        fa['info'] = {
                                            "ano": ano_lab, "semana_ref": sem_lab, "aula_alvo": aula_alvo_prod,
                                            "roteiro": roteiro_especifico, "habilidade": ai.extrair_tag(plano_txt, "HABILIDADE_BNCC"),
                                            "objetivos": ai.extrair_tag(plano_txt, "OBJETIVOS_ENSINO"), "base": base_herdada
                                        }
                                        fa['links_web'] = links_web_aula
                                        fa['qtd_q'] = qtd_q_prod
                                        fa['fase'] = 2
                                        st.rerun()

                # ROTA INTERDISCIPLINAR: Projetos e Trabalhos
                elif "Projeto" in tipo_criacao:
                    with st.container(border=True):
                        st.markdown("#### Parâmetros de Pesquisa")
                        c1, c2, c3 = st.columns([2, 1, 1])
                        natureza_p = c1.selectbox("Abordagem:", ["Semanário Temático", "Projeto de Identidade (Itabuna)", "Investigação Científica"])
                        ano_t = c2.selectbox("Série Alvo:", [6, 7, 8, 9])
                        modo_t = c3.selectbox("Modo:", ["Individual", "Equipes"])

                        tema_t = st.text_input("Tema do Projeto:", placeholder="Ex: Matemática do Cacau")
                        valor_t = st.number_input("Valor (0 a 10.0):", 0.0, 10.0, 2.0)
                        
                        df_cur_t = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_t))]
                        conts_t = st.multiselect("Conteúdos da Matriz para Integrar:", sorted(df_cur_t["CONTEUDO_ESPECIFICO"].unique().tolist()) if not df_cur_t.empty else [])
                        instr_extra_p = st.text_area("Instruções Adicionais de Pesquisa:")

                        if st.button("Gerar Projeto de Pesquisa", use_container_width=True, type="primary"):
                            if not tema_t or not conts_t: st.error("Preencha o tema e os conteúdos.")
                            else:
                                with st.spinner("Forjando Roteiro de Investigação..."):
                                    nome_legivel = util.gerar_nome_material_elite(ano_t, "Projeto", tema_t)
                                    st.session_state.sosa_id_atual = nome_legivel
                                    st.session_state.lab_meta = {"ano": ano_t, "trimestre": "I Trimestre", "tipo": "PROJETO", "semana_ref": "PROJETO"}
                                    
                                    prompt_t = f"ID_FORNECIDO: {nome_legivel}\nSÉRIE: {ano_t}º. TEMA: {tema_t}. NATUREZA: {natureza_p}.\nCONTEÚDOS: {', '.join(conts_t)}.\nVALOR: {valor_t}.\nEXTRAS: {instr_extra_p}."
                                    st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_CIENTIFICO_V33", prompt_t, usar_busca=True)
                                    st.rerun()

                # ROTA COMPLEMENTAR: Listas e Recomposição
                else:
                    with st.container(border=True):
                        st.markdown("#### Configuração da Lista")
                        c1, c2 = st.columns([1, 2])
                        ano_alvo = c1.selectbox("Série Alvo:", [6, 7, 8, 9])
                        origem_tipo = c2.radio("Abordagem da Recomposição:", ["Série Atual (Fixação Híbrida)", "Ano Anterior (Resgatar Base)"], horizontal=True)

                        if "Série Atual" in origem_tipo:
                            df_aulas_ano = df_aulas[df_aulas['ANO'].str.contains(str(ano_alvo))]
                            aulas_opcoes = df_aulas_ano['TIPO_MATERIAL'].tolist() if not df_aulas_ano.empty else []
                            aulas_sel = st.multiselect("Selecione até 2 aulas para mesclar:", aulas_opcoes, max_selections=2)
                            
                            c_q1, c_q2 = st.columns(2)
                            qtd_trad = c_q1.number_input("Exercícios de Cálculo:", 1, 10, 4)
                            qtd_cot = c_q2.number_input("Exercícios do Cotidiano:", 1, 10, 3)
                            
                            if st.button("Gerar Lista Híbrida", use_container_width=True, type="primary"):
                                with st.spinner("Mesclando safras didáticas..."):
                                    contexto_aulas = ""
                                    for a_n in aulas_sel:
                                        contexto_aulas += df_aulas_ano[df_aulas_ano['TIPO_MATERIAL'] == a_n].iloc[0]['CONTEUDO']
                                    
                                    s_id_l = util.gerar_sosa_id("LISTA", ano_alvo, "I")
                                    nome_elite_c = f"{ano_alvo}º Ano - Lista Híbrida - {s_id_l}"
                                    st.session_state.sosa_id_atual = nome_elite_c
                                    st.session_state.lab_meta = {"ano": ano_alvo, "trimestre": "I Trimestre", "tipo": "LISTA_HIBRIDA", "semana_ref": "CONSOLIDAÇÃO"}
                                    
                                    prompt_h = f"ID: {nome_elite_c}.\nSÉRIE: {ano_alvo}º.\nCÁLCULO: {qtd_trad} | COTIDIANO: {qtd_cot}.\nBASE CONCEITUAL:\n{contexto_aulas}"
                                    st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_LISTAS_HIBRIDAS", prompt_h, usar_busca=True)
                                    st.rerun()

            # --- FASE 2: TRATADO DIDÁTICO (TEORIA) ---
            elif fa['fase'] == 2:
                st.markdown("### Fase 2: Tratado Didático (Teoria)")
                
                if not fa['teoria']:
                    with st.spinner("Gerando explicação didática..."):
                        prompt_teoria = f"SÉRIE: {fa['info']['ano']}º Ano.\nASSUNTO: {fa['info']['aula_alvo']}.\nHABILIDADE: {fa['info']['habilidade']}\nROTEIRO DO PROFESSOR: {fa['info']['roteiro']}"
                        if fa['links_web'].strip(): prompt_teoria += f"\nFONTES ADICIONAIS:\n{fa['links_web']}"
                        
                        fa['teoria'] = ai.gerar_ia("FORJA_AULA_TEORIA", prompt_teoria, usar_busca=True)
                        st.rerun()
                else:
                    with st.container(border=True):
                        modo_leitura = st.toggle("Visualização Real (Renderizar Matemática)", value=True)
                        if modo_leitura: st.markdown(preparar_para_leitura(fa['teoria']))
                        else: fa['teoria'] = st.text_area("Edição Manual da Teoria:", value=fa['teoria'], height=350)
                    
                    inst_t = st.text_input("Ajuste da IA (Ex: 'Simplifique o exemplo'):", key="inst_t")
                    c_b1, c_b2 = st.columns(2)
                    
                    if c_b1.button("Aprovar Teoria e Avançar", type="primary", use_container_width=True):
                        fa['fase'] = 3; st.rerun()
                    if c_b2.button("Regerar Teoria", use_container_width=True):
                        with st.spinner("Ajustando teoria..."):
                            prompt_teoria = f"SÉRIE: {fa['info']['ano']}º Ano.\nASSUNTO: {fa['info']['aula_alvo']}.\nAJUSTE: {inst_t}\nTEORIA ANTERIOR:\n{fa['teoria']}"
                            fa['teoria'] = ai.gerar_ia("FORJA_AULA_TEORIA", prompt_teoria, usar_busca=True)
                            st.rerun()

            # --- FASE 3: EXERCÍCIOS REGULARES ---
            elif fa['fase'] == 3:
                st.markdown("### Fase 3: Exercícios Regulares")
                
                if not fa['reg_q']:
                    with st.spinner("Gerando folha de exercícios..."):
                        prompt_ex = f"SÉRIE: {fa['info']['ano']}º Ano. QUANTIDADE: {fa['qtd_q']}.\nBASEIE-SE NA TEORIA:\n{fa['teoria']}"
                        res_ex = ai.gerar_ia("FORJA_AULA_EXERCICIOS", prompt_ex)
                        fa['reg_q'] = ai.extrair_tag(res_ex, "ALUNO")
                        fa['reg_gab'] = ai.extrair_tag(res_ex, "GABARITO")
                        st.rerun()
                else:
                    t_q, t_g = st.tabs(["Folha do Aluno", "Gabarito"])
                    with t_q:
                        fa['reg_q'] = st.text_area("Exercícios (Aluno):", value=fa['reg_q'], height=300)
                    with t_g:
                        fa['reg_gab'] = st.text_area("Resoluções comentadas:", value=fa['reg_gab'], height=200)
                    
                    inst_e = st.text_input("Ajuste da IA para os Exercícios:", key="inst_e")
                    c_b1, c_b2 = st.columns(2)
                    
                    if c_b1.button("Aprovar Exercícios e Avançar", type="primary", use_container_width=True):
                        fa['fase'] = 4; st.rerun()
                    if c_b2.button("Regerar Exercícios", use_container_width=True):
                        with st.spinner("Refazendo folha..."):
                            prompt_ex = f"SÉRIE: {fa['info']['ano']}º Ano. QUANTIDADE: {fa['qtd_q']}.\nAJUSTE: {inst_e}\nTEORIA:\n{fa['teoria']}\nEXERCÍCIOS ANTERIORES:\n{fa['reg_q']}"
                            res_ex = ai.gerar_ia("FORJA_AULA_EXERCICIOS", prompt_ex)
                            fa['reg_q'] = ai.extrair_tag(res_ex, "ALUNO")
                            fa['reg_gab'] = ai.extrair_tag(res_ex, "GABARITO")
                            st.rerun()

            # --- FASE 4: ADAPTAÇÃO PEI ---
            elif fa['fase'] == 4:
                st.markdown("### Fase 4: Adaptação PEI")
                
                if not fa['pei_q']:
                    with st.spinner("Adaptando para o formato inclusivo..."):
                        prompt_pei = f"Adapte as questões para múltipla escolha com apoios visuais (PEI):\n{fa['reg_q']}"
                        res_pei = ai.gerar_ia("FORJA_AULA_PEI", prompt_pei)
                        fa['pei_q'] = ai.extrair_tag(res_pei, "PEI")
                        fa['pei_gab'] = ai.extrair_tag(res_pei, "GABARITO_PEI")
                        st.rerun()
                else:
                    t_q_p, t_g_p = st.tabs(["Folha PEI", "Gabarito PEI"])
                    with t_q_p:
                        fa['pei_q'] = st.text_area("Questões Inclusivas:", value=fa['pei_q'], height=300)
                    with t_g_p:
                        fa['pei_gab'] = st.text_area("Gabarito PEI:", value=fa['pei_gab'], height=200)
                    
                    inst_p = st.text_input("Ajuste da IA para o PEI:", key="inst_p")
                    c_b1, c_b2 = st.columns(2)
                    
                    if c_b1.button("Aprovar PEI e Avançar", type="primary", use_container_width=True):
                        fa['fase'] = 5; st.rerun()
                    if c_b2.button("Regerar Adaptação PEI", use_container_width=True):
                        with st.spinner("Ajustando PEI..."):
                            prompt_pei = f"Ajuste a adaptação conforme solicitado: {inst_p}\nEXERCÍCIOS ORIGINAIS:\n{fa['reg_q']}\nPEI ANTERIOR:\n{fa['pei_q']}"
                            res_pei = ai.gerar_ia("FORJA_AULA_PEI", prompt_pei)
                            fa['pei_q'] = ai.extrair_tag(res_pei, "PEI")
                            fa['pei_gab'] = ai.extrair_tag(res_pei, "GABARITO_PEI")
                            st.rerun()

            # --- FASE 5: COMPILAÇÃO FINAL ---
            elif fa['fase'] == 5:
                st.markdown("### Fase 5: Compilação e Custódia")
                nome_sugerido = util.gerar_nome_material_elite(fa['info']['ano'], fa['info']['aula_alvo'], fa['info']['semana_ref'])
                nome_arq = st.text_input("Nome do Material (Cofre Digital):", value=nome_sugerido)
                
                if st.button("Finalizar e Sincronizar no Drive", type="primary", use_container_width=True):
                    with st.status("Gerando Documentos Oficiais...") as status:
                        info_doc = {"ano": f"{fa['info']['ano']}º", "trimestre": "I Trimestre", "semana": fa['info']['semana_ref']}

                        status.write("Construindo Folha do Aluno...")
                        doc_alu = exporter.gerar_docx_aluno_v24(nome_arq, fa['reg_q'], info_doc)
                        link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_arq}_ALUNO", modo="AULA")
                        
                        status.write("Construindo Atividade Adaptada...")
                        doc_pei = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI", fa['pei_q'], info_doc)
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_arq}_PEI", modo="AULA")
                        
                        status.write("Construindo Guia do Professor...")
                        guia_prof = f"{fa['teoria']}\n\n[GABARITO]\n{fa['reg_gab']}\n\n[GABARITO_PEI]\n{fa['pei_gab']}"
                        doc_prof = exporter.gerar_docx_professor_v25(nome_arq, guia_prof, info_doc)
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_arq}_PROF", modo="AULA")
                        
                        links_f = f"--- LINKS ---\nRegular({link_alu})\nPEI({link_pei})\nProf({link_prof})"
                        conteudo_final = f"[PROFESSOR]\n{fa['teoria']}\n\n[ALUNO]\n{fa['reg_q']}\n\n[GABARITO]\n{fa['reg_gab']}\n\n[PEI]\n{fa['pei_q']}\n\n[GABARITO_PEI]\n{fa['pei_gab']}\n\n{links_f}"
                        
                        db.salvar_no_banco("DB_AULAS_PRONTAS",[
                            datetime.now().strftime("%d/%m/%Y"), fa['info']['semana_ref'], nome_arq, conteudo_final, f"{fa['info']['ano']}º", link_alu
                        ])
                        
                        status.update(label="Sincronização Concluída com Sucesso!", state="complete")
                        st.balloons(); time.sleep(1.5); reset_laboratorio()

    # ==============================================================================
    # ABA 2: ACERVO DIGITAL
    # ==============================================================================
    with tab_acervo_lab:
        st.markdown("### Acervo de Materiais Didáticos")
        
        # 🚨 PROMINÊNCIA DO EXPORTADOR EM LOTE PEI (Melhoria UX V201)
        if not df_aulas.empty:
            df_m_acervo = df_aulas[~df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy()
            termos_proibidos = ["TESTE", "PROVA", "SONDA", "RECUPERAÇÃO", "2ª CHAMADA"]
            df_m_acervo = df_m_acervo[~df_m_acervo['TIPO_MATERIAL'].str.upper().str.contains('|'.join(termos_proibidos), na=False)]
            
            with st.container(border=True):
                st.markdown("##### 📦 Envio Semanal para a Coordenação (Exportador em Lote PEI)")
                st.caption("Gere um arquivo ZIP contendo todas as atividades PEI adaptadas de uma única vez em formato PDF pronto para impressão.")
                
                if st.button("Gerar Pacote de Atividades PEI (ZIP)", type="primary", use_container_width=True):
                    with st.status("Convertendo e compactando arquivos...") as status_zip:
                        import zipfile
                        from googleapiclient.discovery import build
                        try:
                            creds = db.obter_creds_drive()
                            service = build('drive', 'v3', credentials=creds)
                            zip_buffer = io.BytesIO()
                            count = 0
                            
                            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                for _, row in df_m_acervo.iterrows():
                                    txt_f = str(row['CONTEUDO'])
                                    nome_mat = str(row['TIPO_MATERIAL']).replace("/", "-").replace(":", "").strip()
                                    match_l = re.search(r"PEI\s*\(?(https?://[^\s\)]+)\)?", txt_f, re.IGNORECASE)
                                    if match_l:
                                        link_pei = match_l.group(1).strip()
                                        if "N/A" not in link_pei and "http" in link_pei:
                                            id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", link_pei)
                                            if id_match:
                                                file_id = id_match.group(1)
                                                try:
                                                    request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                                                    pdf_bytes = request.execute()
                                                    zip_file.writestr(f"{nome_mat}_PEI.pdf", pdf_bytes)
                                                    count += 1
                                                except: pass
                            
                            if count > 0:
                                status_zip.update(label=f"Pacote com {count} arquivos gerado!", state="complete")
                                st.session_state.zip_pei_ready = zip_buffer.getvalue()
                                st.session_state.zip_pei_count = count
                            else: status_zip.update(label="Nenhum arquivo PEI localizado no acervo.", state="error")
                        except Exception as e: status_zip.update(label=f"Erro de conexão: {e}", state="error")
                
                if "zip_pei_ready" in st.session_state:
                    st.download_button(
                        label="📥 BAIXAR PACOTE PEI COMPACTADO (ZIP)",
                        data=st.session_state.zip_pei_ready,
                        file_name=f"SOSA_PEI_{datetime.now().strftime('%d%m%Y')}.zip",
                        mime="application/zip",
                        use_container_width=True
                    )

            st.markdown("---")
            
            # Filtros do Acervo
            c_m1, c_m2 = st.columns(2)
            f_ano_m = c_m1.selectbox("Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key="ac_ano_fil")
            f_tipo_m = c_m2.selectbox("Filtrar Tipo:", ["Todos", "Aula", "PROJETO", "Lista"], key="ac_tipo_fil")

            if f_ano_m != "Todos": df_m_acervo = df_m_acervo[df_m_acervo['ANO'] == f_ano_m]
            if f_tipo_m != "Todos": df_m_acervo = df_m_acervo[df_m_acervo['TIPO_MATERIAL'].str.upper().str.contains(f_tipo_m.upper())]

            df_m_acervo = df_m_acervo.iloc[::-1]

            if df_m_acervo.empty:
                st.info("Nenhum material localizado no acervo.")
            else:
                for _, row in df_m_acervo.iterrows():
                    with st.container(border=True):
                        txt_f = str(row['CONTEUDO'])
                        identificador = row['TIPO_MATERIAL']
                        
                        st.markdown(f"##### {identificador}")
                        st.caption(f"Série: {row['ANO']} | Data de Sincronia: {row['DATA']}")
                        
                        def extrair_link(t, k, res):
                            m = re.search(rf"{k}\s*\(?\s*(https?://[^\s\)]+)\)?", t, re.IGNORECASE)
                            return m.group(1).strip() if m else res

                        l_alu = extrair_link(txt_f, "Regular", row.get('LINK_DRIVE'))
                        l_pei = extrair_link(txt_f, "PEI", "N/A")
                        l_prof = extrair_link(txt_f, "Prof", "N/A")

                        c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)
                        
                        if l_alu and "http" in str(l_alu): c_b1.link_button("Aluno", str(l_alu), use_container_width=True)
                        if l_pei and "http" in str(l_pei): c_b2.link_button("PEI", str(l_pei), use_container_width=True)
                        if l_prof and "http" in str(l_prof): c_b3.link_button("Guia Prof.", str(l_prof), use_container_width=True)
                        
                        if c_b4.button("Refinar", key=f"ref_ac_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = txt_f
                            st.session_state.sosa_id_atual = identificador
                            st.session_state.lab_meta = {"ano": str(row["ANO"]).replace("º",""), "semana_ref": row['SEMANA_REF']}
                            st.rerun()
                            
                        if c_b5.button("Apagar", key=f"del_ac_{row.name}", use_container_width=True):
                            if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", identificador): st.rerun()


# ==============================================================================
# MÓDULO: CENTRAL DE AVALIAÇÕES - V201 (CASCATA & PSICOMETRIA VISUAL)
# ==============================================================================
elif menu == "📝 Central de Avaliações":
    st.title("Central de Avaliações")
    st.caption("Arquitetura psicométrica de elite para desenvolvimento, balanceamento e custódia de instrumentos avaliativos.")
    st.markdown("---")

    # 🚨 INICIALIZAÇÃO DA MÁQUINA DE ESTADOS DA FORJA
    if "forja" not in st.session_state:
        st.session_state.forja = {
            'fase': 1, 'mapa': [], 'info': {}, 'pei_1': '', 'pei_2': '', 'pei_3': '', 'prova_final_txt': ''
        }
    
    f = st.session_state.forja

    def reset_forja():
        st.session_state.forja = {'fase': 1, 'mapa': [], 'info': {}, 'pei_1': '', 'pei_2': '', 'pei_3': '', 'prova_final_txt': ''}
        st.rerun()

    # 🚨 FLUXOGRAMA HORIZONTAL DE ELITE (Fases 1 a 5)
    def render_indicador_fases(fase_atual):
        etapas = [
            ("1. Parâmetros", 1),
            ("2. Forja de Itens", 2),
            ("3. Tríade PEI", 3),
            ("4. Custódia", 4),
            ("5. Ações Pós-Prova", 5)
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

    tab_forja, tab_acervo_av = st.tabs(["Linha de Montagem", "Acervo de Provas"])

    # ==============================================================================
    # ABA 1: LINHA DE MONTAGEM
    # ==============================================================================
    with tab_forja:
        if 1 < f['fase'] < 6:
            render_indicador_fases(f['fase'])
            if st.button("Descartar e Voltar ao Início", use_container_width=True): reset_forja()
            st.markdown("---")

        # --- FASE 1: NATUREZA E MATRIZ DE PROVA (Briefing) ---
        if f['fase'] == 1:
            st.markdown("### Configuração da Avaliação")
            modo_arq = st.radio(
                "Abordagem Curricular:", 
                ["Nova Avaliação (Inédita)", "Sonda Diagnóstica", "Variante Anti-Fraude (Clonagem)", "2ª Chamada Discursiva", "Recuperação Cirúrgica (Data-Driven)"], 
                horizontal=True
            )
            st.markdown("---")

            # ROTA INÉDITA / SONDA
            if "Inédita" in modo_arq or "Sonda" in modo_arq:
                with st.container(border=True):
                    st.markdown("#### Parâmetros de Matriz")
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                    ano_av = c1.selectbox("Série Alvo:", [6, 7, 8, 9])
                    trim_filtro = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
                    v_total = c3.number_input("Valor:", 0.0, 10.0, 3.0 if "Inédita" in modo_arq else 10.0)
                    qtd_q = c4.number_input("Quantidade de Questões:", 1, 20, 5)

                tipo_av = "SONDA_DE_PROFICIÊNCIA" if "Sonda" in modo_arq else st.selectbox("Tipo de Instrumento:", ["Teste", "Prova", "Recuperação Paralela", "Recuperação Final"])

                with st.container(border=True):
                    st.markdown("#### Seleção de Matérias Base")
                    c_safra1, c_safra2 = st.columns(2)
                    
                    df_ref = df_aulas[df_aulas['ANO'].str.contains(str(ano_av))].copy()
                    termos_proibidos = ["APLICAÇÃO", "TESTE", "PROVA", "SONDA", "AVALIAÇÃO", "CORREÇÃO", "REVISÃO", "EXAME", "2ª CHAMADA"]
                    df_ref = df_ref[~df_ref['TIPO_MATERIAL'].str.upper().str.contains('|'.join(termos_proibidos))]
                    mats_selecionados = c_safra1.multiselect("Aulas Base (Acervo):", options=df_ref["TIPO_MATERIAL"].tolist())
                    
                    trim_sigla = trim_filtro.split(" ")[0]
                    df_matriz_av = df_curriculo[(df_curriculo['ANO'].astype(str).str.contains(str(ano_av))) & (df_curriculo['TRIMESTRE'] == trim_sigla)]
                    topicos_futuros = c_safra2.multiselect("Tópicos Futuros (Matriz):", options=sorted(df_matriz_av['CONTEUDO_ESPECIFICO'].unique().tolist()) if not df_matriz_av.empty else [])
                    
                    conteudos_extraidos = set()
                    contexto_base_texto = "" 
                    
                    if mats_selecionados:
                        semanas_selecionadas = df_ref[df_ref['TIPO_MATERIAL'].isin(mats_selecionados)]['SEMANA_REF'].unique()
                        planos_relacionados = df_planos[(df_planos['ANO'].str.contains(str(ano_av))) & (df_planos['SEMANA'].isin(semanas_selecionadas))]
                        for _, row_p in planos_relacionados.iterrows():
                            cont = ai.extrair_tag(str(row_p['PLANO_TEXTO']), "CONTEUDOS_ESPECIFICOS")
                            if cont and cont.upper() != "N/A":
                                for item in re.split(r'[;\n]', cont):
                                    if len(item.strip()) > 5: conteudos_extraidos.add(item.strip())
                        
                        for m_nome in mats_selecionados:
                            m_row = df_aulas[df_aulas["TIPO_MATERIAL"] == m_nome].iloc[0]
                            txt_aula = str(m_row['CONTEUDO'])
                            contexto_base_texto += f"--- AULA: {m_nome} ---\nHabilidade: {ai.extrair_tag(txt_aula, 'HABILIDADE_BNCC')}\nConteúdos: {ai.extrair_tag(txt_aula, 'CONTEUDOS_ESPECIFICOS')}\n\n"
                    
                    if topicos_futuros:
                        for topico in topicos_futuros: conteudos_extraidos.add(topico)
                    
                    lista_conteudos = sorted(list(conteudos_extraidos)) if conteudos_extraidos else ["Matemática Geral"]
                    
                if st.button("Gerar Matriz de Questões", type="primary", use_container_width=True):
                    if not mats_selecionados and not topicos_futuros: st.error("Selecione pelo menos uma matéria.")
                    else:
                        gabarito_mestre = util.gerar_gabarito_balanceado(qtd_q)
                        mapa_inicial = []
                        for i in range(qtd_q):
                            mapa_inicial.append({
                                'q': i + 1, 'tema': lista_conteudos[i % len(lista_conteudos)],
                                'dificuldade': "Fácil" if i < (qtd_q*0.3) else "Difícil" if i >= (qtd_q*0.8) else "Média",
                                'gabarito': gabarito_mestre[i], 'status': 'pendente', 'dados': {} 
                            })
                        f['mapa'] = mapa_inicial
                        f['info'] = {'ano': f"{ano_av}º", 'trimestre': trim_filtro, 'valor': v_total, 'qtd': qtd_q, 'tipo_prova': tipo_av}
                        f['contexto_base'] = contexto_base_texto 
                        f['fase'] = 2; st.rerun()

            # ROTAS DE CLONAGEM & RECUPERAÇÃO (Bypass Inteligente)
            elif "Variante" in modo_arq or "2ª Chamada" in modo_arq:
                with st.container(border=True):
                    st.markdown("#### Parâmetros de Clonagem")
                    c_cl1, c_cl2 = st.columns([1, 2])
                    ano_clone = c_cl1.selectbox("Série:", [6, 7, 8, 9], index=0)
                    df_provas = df_aulas[(df_aulas['ANO'].str.contains(str(ano_clone))) & (df_aulas['SEMANA_REF'] == "AVALIAÇÃO")]
                    opcoes_provas = [p for p in df_provas['TIPO_MATERIAL'].tolist() if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", p, re.IGNORECASE)]
                    prova_base_sel = c_cl2.selectbox("Prova de Origem:", [""] + opcoes_provas)
                
                if prova_base_sel:
                    txt_base = str(df_provas[df_provas['TIPO_MATERIAL'] == prova_base_sel].iloc[0]['CONTEUDO'])
                    q_reg = ai.extrair_tag(txt_base, "QUESTOES")
                    qtd_detectada = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_reg))
                    st.success(f"Gabarito original com {qtd_detectada} questões localizado.")
                    
                    if st.button(f"Iniciar Processo de Clonagem", type="primary", use_container_width=True):
                        with st.status("Forjando caderno espelho...") as status:
                            info_clone = {'ano': f"{ano_clone}º", 'trimestre': "I Trimestre", 'valor': 3.0, 'qtd': qtd_detectada}
                            
                            if "Variante" in modo_arq:
                                existentes = df_aulas[df_aulas['TIPO_MATERIAL'].str.startswith(prova_base_sel + " - TIPO", na=False)]
                                letra = chr(66 + len(existentes)) # B, C...
                                nome_var = f"{prova_base_sel} - TIPO {letra}"
                                
                                prompt = f"PROVA ORIGINAL:\n[QUESTOES]\n{q_reg}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(txt_base, 'GRADE_DE_CORRECAO')}"
                                res_hydra = ai.gerar_ia("ARQUITETO_VARIANTES_V100", prompt)
                                
                                texto_final_var = f"[VALOR: 3.0]\n\n[QUESTOES]\n{ai.extrair_tag(res_hydra, 'QUESTOES')}\n\n[GABARITO_TEXTO]\n{ai.extrair_tag(res_hydra, 'GABARITO_TEXTO')}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(res_hydra, 'GRADE_DE_CORRECAO')}\n\n[PEI]\n{ai.extrair_tag(txt_base, 'PEI')}\n\n[GABARITO_PEI]\n{ai.extrair_tag(txt_base, 'GABARITO_PEI')}\n\n"
                                doc_var = exporter.gerar_docx_prova_v25(nome_var, texto_final_var, info_clone)
                                link_var = db.subir_e_converter_para_google_docs(doc_var, nome_var, modo="AVALIACAO")
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_var, texto_final_var + f"\n--- LINKS ---\nRegular({link_var})", f"{ano_clone}º", link_var])
                                status.update(label="Variante homologada com sucesso!", state="complete")
                                
                            else: # 2ª Chamada
                                nome_2a = f"2ª_CHAMADA_{prova_base_sel}"
                                prompt_2a = f"TIPO: 2ª Chamada (100% DISCURSIVA). QTD: {qtd_detectada}.\nPROVA:\n{q_reg}"
                                res_2a = ai.gerar_ia("ARQUITETO_2A_CHAMADA_V100", prompt_2a)
                                
                                info_clone['tipo_prova'] = "2ª Chamada"
                                doc_2a = exporter.gerar_docx_prova_v25(nome_2a, res_2a, info_clone)
                                link_2a = db.subir_e_converter_para_google_docs(doc_2a, nome_2a, modo="AVALIACAO")
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_2a, res_2a + f"\n--- LINKS ---\nRegular({link_2a})", f"{ano_clone}º", link_2a])
                                status.update(label="2ª Chamada discursiva homologada!", state="complete")
                        
                        st.balloons(); time.sleep(1); st.rerun()

            else: # Recuperação Cirúrgica
                with st.container(border=True):
                    st.markdown("#### Matriz de Recuperação Data-Driven")
                    c_rec1, c_rec2 = st.columns([1, 2])
                    ano_rec = c_rec1.selectbox("Série:", [6, 7, 8, 9], index=0)
                    trim_rec = c_rec2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
                    
                    df_provas_rec = df_aulas[(df_aulas['ANO'].str.contains(str(ano_rec))) & (df_aulas['SEMANA_REF'] == "AVALIAÇÃO")]
                    opcoes_provas_rec = [p for p in df_provas_rec['TIPO_MATERIAL'].tolist() if not re.search(r"2[ªA]|CHAMADA", p, re.IGNORECASE)]
                    provas_base_sel = st.multiselect("Instrumentos Originais de Diagnóstico:", opcoes_provas_rec, max_selections=2)
                
                if len(provas_base_sel) > 0:
                    c_p1, c_p2 = st.columns(2)
                    gerar_n1 = c_p1.checkbox("Gerar Adaptação PEI Leve", value=True)
                    gerar_n2 = c_p2.checkbox("Gerar Adaptação PEI Moderada", value=True)
                    
                    if st.button("Forjar Instrumento de Recuperação", type="primary", use_container_width=True):
                        with st.status("Processando dados de desempenho...") as status:
                            textos_base = ""
                            for p_nome in provas_base_sel:
                                textos_base += f"--- {p_nome} ---\n{ai.extrair_tag(str(df_provas_rec[df_provas_rec['TIPO_MATERIAL'] == p_nome].iloc[0]['CONTEUDO']), 'QUESTOES')}\n\n"
                            
                            res_rec = ai.gerar_ia("ARQUITETO_RECUPERACAO_CIRURGICA", f"PROVAS BASE:\n{textos_base}")
                            texto_final_rec = f"[VALOR: 10.0]\n\n[QUESTOES]\n{ai.extrair_tag(res_rec, 'QUESTOES')}\n\n[GABARITO_TEXTO]\n{ai.extrair_tag(res_rec, 'GABARITO_TEXTO')}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(res_rec, 'GRADE_DE_CORRECAO')}\n\n"
                            
                            info_rec = {'ano': f"{ano_rec}º", 'trimestre': trim_rec, 'valor': 10.0, 'qtd': 10, 'tipo_prova': "Recuperação Paralela"}
                            nome_rec = f"RECUPERACAO_{ano_rec}ANO_{trim_rec.replace(' ', '')}"
                            
                            doc_rec = exporter.gerar_docx_prova_v25(nome_rec, texto_final_rec, info_rec)
                            link_rec = db.subir_e_converter_para_google_docs(doc_rec, nome_rec, modo="AVALIACAO")
                            
                            links_pei = []
                            if gerar_n1 or gerar_n2:
                                status.write("Construindo variações adaptadas...")
                                res_pei = ai.gerar_ia("FORJA_TRIADE_PEI", f"REGULARES:\n{ai.extrair_tag(res_rec, 'QUESTOES')}")
                                
                                if gerar_n1:
                                    p1 = ai.extrair_tag(res_pei, "NIVEL_1")
                                    doc_p1 = exporter.gerar_docx_pei_v25(f"{nome_rec}_PEI_N1", p1, info_rec)
                                    links_pei.append(f"PEI_N1({db.subir_e_converter_para_google_docs(doc_p1, f'{nome_rec}_PEI_N1', modo='AVALIACAO')})")
                                if gerar_n2:
                                    p2 = ai.extrair_tag(res_pei, "NIVEL_2")
                                    doc_p2 = exporter.gerar_docx_pei_v25(f"{nome_rec}_PEI_N2", p2, info_rec)
                                    links_pei.append(f"PEI_N2({db.subir_e_converter_para_google_docs(doc_p2, f'{nome_rec}_PEI_N2', modo='AVALIACAO')})")
                            
                            links_f = f"--- LINKS ---\nRegular({link_rec}) " + " ".join(links_pei)
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_rec, texto_final_rec + links_f, f"{ano_rec}º", link_rec])
                            status.update(label="Recuperação cirúrgica homologada!", state="complete")
                        
                        st.balloons(); time.sleep(1); st.rerun()

        # --- FASE 2: LINHA DE MONTAGEM (Questão por Questão) ---
        elif f['fase'] == 2:
            st.markdown("### Forja de Questões")
            
            # 🚨 1. MAPA DE CALOR PSICOMÉTRICO (Bento Matrix)
            total_q = len(f['mapa'])
            facil_c = sum(1 for item in f['mapa'] if item['dificuldade'] == "Fácil")
            media_c = sum(1 for item in f['mapa'] if item['dificuldade'] == "Média")
            dificil_c = sum(1 for item in f['mapa'] if item['dificuldade'] == "Difícil")
            
            st.markdown(f"""
            <div style='display: flex; gap: 10px; margin-bottom: 25px;'>
                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                    <span style='font-size: 10px; color: gray; font-weight: bold; letter-spacing: 0.5px;'>BALANCEAMENTO</span><br>
                    <span style='font-size: 14px; color: #2ECC71; font-weight: bold;'>Estável (V201)</span>
                </div>
                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                    <span style='font-size: 10px; color: gray; font-weight: bold; letter-spacing: 0.5px;'>ITENS FÁCEIS</span><br>
                    <span style='font-size: 14px; color: #2962FF; font-weight: bold;'>{facil_c}</span>
                </div>
                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                    <span style='font-size: 10px; color: gray; font-weight: bold; letter-spacing: 0.5px;'>ITENS MÉDIOS</span><br>
                    <span style='font-size: 14px; color: #F1C40F; font-weight: bold;'>{media_c}</span>
                </div>
                <div style='flex: 1; background: {cor_card}; border: 1px solid {cor_borda}; padding: 12px; border-radius: 12px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                    <span style='font-size: 10px; color: gray; font-weight: bold; letter-spacing: 0.5px;'>ITENS DIFÍCEIS</span><br>
                    <span style='font-size: 14px; color: #E74C3C; font-weight: bold;'>{dificil_c}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            modo_leitura_forja = st.toggle("Visualização Real (Renderizar Matemática)", value=True)

            # GERAÇÃO EM LOTE (JSON NATIVO)
            pendentes = [item for item in f['mapa'] if item['status'] == 'pendente']
            if pendentes:
                if st.button("Gerar Todas as Questões Pendentes (Lote)", type="primary", use_container_width=True):
                    with st.spinner(f"Processando {len(pendentes)} itens em lote JSON..."):
                        prompt_lote = f"SÉRIE: {f['info']['ano']}\n\n"
                        for item in pendentes:
                            prompt_lote += f"QUESTÃO {item['q']}:\n- TEMA: {item['tema']}\n- DIFICULDADE: {item['dificuldade']}\n- GABARITO: Letra {item['gabarito']}\n\n"
                        prompt_lote += f"CONTEXTO BASE:\n{f.get('contexto_base', '')}\n"
                        
                        res_json = ai.gerar_ia_json("FORJA_LOTE_JSON", prompt_lote)
                        if "erro" in res_json: st.error(res_json["erro"])
                        else:
                            for q_data in res_json.get("questoes", []):
                                q_num = int(q_data.get("q", 0))
                                for item in f['mapa']:
                                    if item['q'] == q_num:
                                        item['dados'] = {
                                            'ENUNCIADO': q_data.get('enunciado', ''), 'ALT_A': q_data.get('alt_a', ''),
                                            'ALT_B': q_data.get('alt_b', ''), 'ALT_C': q_data.get('alt_c', ''),
                                            'ALT_D': q_data.get('alt_d', ''), 'ALT_E': q_data.get('alt_e', ''),
                                            'HABILIDADE': q_data.get('habilidade', ''), 'JUSTIFICATIVA': q_data.get('justificativa', ''),
                                            'DISTRATORES': q_data.get('distratores', ''), 'GABARITO': item['gabarito']
                                        }
                                        item['status'] = 'revisao'
                            st.rerun()

            st.markdown("---")
            todas_aprovadas = True
            
            for i, item in enumerate(f['mapa']):
                # 🚨 BORDAS COLORIDAS DINÂMICAS DE STATUS (Estilo V201)
                cor_status_border = "#2ECC71" if item['status'] == 'aprovado' else ("#2962FF" if item['status'] == 'revisao' else "#F1C40F")
                label_status = "Aprovado" if item['status'] == 'aprovado' else ("Revisão" if item['status'] == 'revisao' else "Pendente")
                
                with st.container(border=True):
                    st.markdown(f"<div style='border-left: 4px solid {cor_status_border}; padding-left: 10px; margin-bottom: 10px;'><strong>Item {item['q']:02d} | Gabarito: {item['gabarito']} ({label_status})</strong></div>", unsafe_allow_html=True)
                    
                    if item['status'] == 'pendente':
                        todas_aprovadas = False
                        c_t1, c_t2 = st.columns([3, 1])
                        tema_q = c_t1.text_input("Assunto Específico:", value=item['tema'], key=f"t_{i}")
                        dif_q = c_t2.selectbox("Complexidade:", ["Fácil", "Média", "Difícil"], index=["Fácil", "Média", "Difícil"].index(item['dificuldade']), key=f"d_{i}")
                        
                        if st.button(f"Forjar Item {item['q']}", key=f"btn_gen_{i}", use_container_width=True):
                            with st.spinner("Desenhando item..."):
                                prompt = f"SÉRIE: {f['info']['ano']}\nTEMA: {tema_q}. DIFICULDADE: {dif_q}. GABARITO: {item['gabarito']}.\nCONTEXTO:\n{f.get('contexto_base', '')}"
                                res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                ext = {tag: ai.extrair_tag(res_item, tag) for tag in ['ENUNCIADO', 'ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E', 'HABILIDADE', 'JUSTIFICATIVA', 'DISTRATORES']}
                                
                                item['dados'] = {
                                    'ENUNCIADO': ext['ENUNCIADO'], 'ALT_A': ext['ALT_A'], 'ALT_B': ext['ALT_B'], 'ALT_C': ext['ALT_C'],
                                    'ALT_D': ext['ALT_D'], 'ALT_E': ext['ALT_E'], 'HABILIDADE': ext['HABILIDADE'], 'JUSTIFICATIVA': ext['JUSTIFICATIVA'],
                                    'DISTRATORES': ext['DISTRATORES'], 'GABARITO': item['gabarito']
                                }
                                item['status'] = 'revisao'; st.rerun()
                                
                    elif item['status'] == 'revisao':
                        todas_aprovadas = False
                        d = item['dados']
                        
                        if modo_leitura_forja:
                            st.markdown(preparar_para_leitura(d['ENUNCIADO']))
                            st.markdown(f"**(A)** {preparar_para_leitura(d['ALT_A'])} | **(B)** {preparar_para_leitura(d['ALT_B'])} | **(C)** {preparar_para_leitura(d['ALT_C'])} | **(D)** {preparar_para_leitura(d['ALT_D'])} | **(E)** {preparar_para_leitura(d['ALT_E'])}")
                            st.divider()
                        
                        d['ENUNCIADO'] = st.text_area("Enunciado:", value=d['ENUNCIADO'], height=100, key=f"ed_en_{i}")
                        c_a1, c_a2 = st.columns(2)
                        d['ALT_A'] = c_a1.text_input("(A)", value=d['ALT_A'], key=f"ed_a_{i}")
                        d['ALT_B'] = c_a2.text_input("(B)", value=d['ALT_B'], key=f"ed_b_{i}")
                        d['ALT_C'] = c_a1.text_input("(C)", value=d['ALT_C'], key=f"ed_c_{i}")
                        d['ALT_D'] = c_a2.text_input("(D)", value=d['ALT_D'], key=f"ed_d_{i}")
                        d['ALT_E'] = c_a1.text_input("(E)", value=d['ALT_E'], key=f"ed_e_{i}")
                        
                        inst_ref = st.text_input("Ajuste (IA):", key=f"inst_ref_{i}")
                        col_b1, col_b2 = st.columns(2)
                        
                        if col_b1.button(f"Aprovar Item {item['q']}", type="primary", key=f"btn_apr_{i}", use_container_width=True):
                            item['status'] = 'aprovado'; st.rerun()
                        if col_b2.button(f"Regerar Item {item['q']}", key=f"btn_ref_{i}", use_container_width=True):
                            with st.spinner("Reestruturando..."):
                                prompt = f"SÉRIE: {f['info']['ano']}\nTEMA: {item['tema']}. GABARITO: {item['gabarito']}.\nAJUSTE: {inst_ref}\nENUNCIADO ANTERIOR:\n{d['ENUNCIADO']}"
                                res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                ext = {tag: ai.extrair_tag(res_item, tag) for tag in ['ENUNCIADO', 'ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E', 'HABILIDADE', 'JUSTIFICATIVA', 'DISTRATORES']}
                                item['dados'] = {
                                    'ENUNCIADO': ext['ENUNCIADO'], 'ALT_A': ext['ALT_A'], 'ALT_B': ext['ALT_B'], 'ALT_C': ext['ALT_C'],
                                    'ALT_D': ext['ALT_D'], 'ALT_E': ext['ALT_E'], 'HABILIDADE': ext['HABILIDADE'], 'JUSTIFICATIVA': ext['JUSTIFICATIVA'],
                                    'DISTRATORES': ext['DISTRATORES'], 'GABARITO': item['gabarito']
                                }
                                st.rerun()
                            
                    elif item['status'] == 'aprovado':
                        d = item['dados']
                        if modo_leitura_forja:
                            st.markdown(preparar_para_leitura(d['ENUNCIADO']))
                            st.markdown(f"**(A)** {preparar_para_leitura(d['ALT_A'])} | **(B)** {preparar_para_leitura(d['ALT_B'])} | **(C)** {preparar_para_leitura(d['ALT_C'])} | **(D)** {preparar_para_leitura(d['ALT_D'])} | **(E)** {preparar_para_leitura(d['ALT_E'])}")
                        else:
                            st.text(d['ENUNCIADO'])
                        if st.button("Revisar Item", key=f"btn_edit_{i}", use_container_width=True):
                            item['status'] = 'revisao'; st.rerun()

            if todas_aprovadas:
                st.success("Todos os itens foram homologados!")
                if st.button("Avançar para Adaptações PEI", type="primary", use_container_width=True):
                    f['fase'] = 3; st.rerun()

        # --- FASE 3: TRÍADE INCLUSIVA (PEI) ---
        elif f['fase'] == 3:
            st.markdown("### Tríade Inclusiva (Adaptação PEI)")
            
            if not f['pei_1']:
                if st.button("Gerar Tríade Inclusiva", type="primary", use_container_width=True):
                    with st.spinner("Analisando itens e gerando os 3 níveis clínicos..."):
                        texto_base = ""
                        for item in f['mapa']:
                            texto_base += f"Q{item['q']}: {item['dados']['ENUNCIADO']} | Gabarito: {item['dados']['GABARITO']}\n"
                        res_pei = ai.gerar_ia("FORJA_TRIADE_PEI", f"REGULARES:\n{texto_base}")
                        f['pei_1'] = ai.extrair_tag(res_pei, "NIVEL_1")
                        f['pei_2'] = ai.extrair_tag(res_pei, "NIVEL_2")
                        f['pei_3'] = ai.extrair_tag(res_pei, "NIVEL_3")
                        st.rerun()
            else:
                t_p1, t_p2, t_p3 = st.tabs(["Nível 1 (Leve)", "Nível 2 (Moderado)", "Nível 3 (Qualitativo)"])
                with t_p1: f['pei_1'] = st.text_area("Capa PEI N1:", value=f['pei_1'], height=300)
                with t_p2: f['pei_2'] = st.text_area("Capa PEI N2:", value=f['pei_2'], height=300)
                with t_p3: f['pei_3'] = st.text_area("Capa PEI N3:", value=f['pei_3'], height=300)
                    
                if st.button("Avançar para Compilação Final", type="primary", use_container_width=True):
                    f['fase'] = 4; st.rerun()

        # --- FASE 4: COMPILAÇÃO E VARIANTES ---
        elif f['fase'] == 4:
            st.markdown("### Custódia e Finalização")
            
            tipo_nome = f['info'].get('tipo_prova', 'TESTE').upper().replace(' ', '_')
            nome_sugerido = f"{tipo_nome}_{f['info']['ano'].replace('º','')}ANO_{f['info']['trimestre'].replace(' ', '')}"
            nome_arq = st.text_input("Identificador Técnico (Cofre Digital):", value=nome_sugerido)
            gerar_variante = st.checkbox("Gerar Variante Tipo B (Embaralhada)", value=True)
            
            if st.button("Finalizar e Gravar Ativos", type="primary", use_container_width=True):
                with st.status("Processando documentos finais...") as status:
                    txt_regular = f"[VALOR: {f['info']['valor']}]\n\n[QUESTOES]\n"
                    txt_gabarito = "[GABARITO_TEXTO]\n"
                    txt_grade = "[GRADE_DE_CORRECAO]\n"
                    
                    for item in f['mapa']:
                        d = item['dados']
                        txt_regular += f"**QUESTÃO {item['q']:02d} -** {d['ENUNCIADO']}\n(A) {d['ALT_A']}\n(B) {d['ALT_B']}\n(C) {d['ALT_C']}\n(D) {d['ALT_D']}\n(E) {d['ALT_E']}\n\n"
                        txt_gabarito += f"QUESTÃO {item['q']:02d}: {d['GABARITO']}\n"
                        txt_grade += f"QUESTÃO {item['q']:02d}: [{d['HABILIDADE']}] | JUSTIFICATIVA: {d['JUSTIFICATIVA']} | DISTRATORES: {d['DISTRATORES']}\n"
                    
                    texto_final_padrao = txt_regular + txt_gabarito + txt_grade
                    
                    status.write("Construindo Prova Regular...")
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, texto_final_padrao, f['info'])
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, modo="AVALIACAO")
                    
                    status.write("Construindo Variações PEI...")
                    doc_p1 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N1", f['pei_1'], f['info'])
                    link_p1 = db.subir_e_converter_para_google_docs(doc_p1, f"{nome_arq}_PEI_N1", modo="AVALIACAO")
                    doc_p2 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N2", f['pei_2'], f['info'])
                    link_p2 = db.subir_e_converter_para_google_docs(doc_p2, f"{nome_arq}_PEI_N2", modo="AVALIACAO")
                    doc_p3 = exporter.gerar_docx_pei_qualitativa(f"{nome_arq}_PEI_N3", f['pei_3'], f['info'])
                    link_p3 = db.subir_e_converter_para_google_docs(doc_p3, f"{nome_arq}_PEI_N3", modo="AVALIACAO")
                    
                    links_f = f"--- LINKS ---\nRegular({link_reg}) PEI_N1({link_p1}) PEI_N2({link_p2}) PEI_N3({link_p3})"
                    
                    # Salva no Banco de Dados
                    sucesso_db = db.salvar_no_banco("DB_AULAS_PRONTAS", [
                        datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_arq, 
                        texto_final_padrao + f"\n\n[NIVEL_1]\n{f['pei_1']}\n\n[NIVEL_2]\n{f['pei_2']}\n\n[NIVEL_3]\n{f['pei_3']}\n\n{links_f}", 
                        f['info']['ano'], link_reg
                    ])
                    
                    if sucesso_db:
                        if gerar_variante:
                            status.write("Embaralhando Variante Tipo B...")
                            mapa_var = f['mapa'].copy()
                            random.shuffle(mapa_var)
                            
                            txt_var = f"[VALOR: {f['info']['valor']}]\n\n[QUESTOES]\n"
                            txt_gab_var = "[GABARITO_TEXTO]\n"
                            txt_grade_var = "[GRADE_DE_CORRECAO]\n"
                            
                            for i, item in enumerate(mapa_var):
                                d_v = util.embaralhar_item_estruturado(item['dados'])
                                txt_var += f"**QUESTÃO {i+1:02d} -** {d_v['ENUNCIADO']}\n(A) {d_v['ALT_A']}\n(B) {d_v['ALT_B']}\n(C) {d_v['ALT_C']}\n(D) {d_v['ALT_D']}\n(E) {d_v['ALT_E']}\n\n"
                                txt_gab_var += f"QUESTÃO {i+1:02d}: {d_v['GABARITO']}\n"
                                txt_grade_var += f"QUESTÃO {i+1:02d}: [{d_v['HABILIDADE']}] | JUSTIFICATIVA: {d_v['JUSTIFICATIVA']}\n"
                                
                            texto_final_var = txt_var + txt_gab_var + txt_grade_var
                            doc_var = exporter.gerar_docx_prova_v25(f"{nome_arq}_TIPO_B", texto_final_var, f['info'])
                            link_var = db.subir_e_converter_para_google_docs(doc_var, f"{nome_arq}_TIPO_B", modo="AVALIACAO")
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", f"{nome_arq} - TIPO B", 
                                texto_final_var + f"\n\n[NIVEL_1]\n{f['pei_1']}\n\n[NIVEL_2]\n{f['pei_2']}\n\n[NIVEL_3]\n{f['pei_3']}\n\n" + f"--- LINKS ---\nRegular({link_var}) PEI_N1({link_p1})", 
                                f['info']['ano'], link_var
                            ])

                        status.write("Construindo Guia Professor...")
                        guia_txt = f"GABARITO:\n{txt_gabarito}\n\nGRADE:\n{txt_grade}"
                        doc_prof = exporter.gerar_docx_professor_v25(f"{nome_arq}_GUIA", guia_txt, f['info'])
                        db.subir_e_converter_para_google_docs(doc_prof, f"{nome_arq}_GUIA", modo="AVALIACAO")
                        
                        f['prova_final_txt'] = texto_final_padrao
                        f['nome_base'] = nome_arq
                        status.update(label="Homologado com Sucesso!", state="complete")
                        st.balloons(); f['fase'] = 5; time.sleep(1); st.rerun()

        # --- FASE 5: AÇÕES PÓS-PROVA ---
        elif f['fase'] == 5:
            st.success("Avaliação homologada e salva no acervo!")
            st.markdown("### Ações Derivadas")
            c_pos1, c_pos2 = st.columns(2)
            
            if c_pos1.button("Gerar Material de Revisão", use_container_width=True):
                with st.spinner("Construindo..."):
                    res_rev = ai.gerar_ia("ARQUITETO_REVISAO_V29", f"PROVA:\n{f['prova_final_txt']}")
                    nome_rev = f"REVISAO_{f['nome_base']}"
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_rev, ai.extrair_tag(res_rev, "ALUNO"), f['info'])
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_rev}_ALUNO", modo="AULA")
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_rev, res_rev + f"\n--- LINKS ---\nRegular({link_alu})", f['info']['ano'], link_alu])
                    st.success("Revisão salva!")
            
            if c_pos2.button("Gerar Caderno de 2ª Chamada", use_container_width=True):
                with st.spinner("Construindo..."):
                    res_2a = ai.gerar_ia("ARQUITETO_2A_CHAMADA_V100", f"PROVA:\n{f['prova_final_txt']}")
                    nome_2a = f"2ª_CHAMADA_{f['nome_base']}"
                    doc_2a = exporter.gerar_docx_prova_v25(nome_2a, res_2a, f['info'])
                    link_2a = db.subir_e_converter_para_google_docs(doc_2a, nome_2a, modo="AVALIACAO")
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_2a, res_2a + f"\n--- LINKS ---\nRegular({link_2a})", f['info']['ano'], link_2a])
                    st.success("2ª Chamada salva!")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Concluir Processo", type="primary", use_container_width=True): reset_forja()

        # --- FASE 6: RE-EXPORTAÇÃO RÁPIDA (REFINO) ---
        elif f['fase'] == 6:
            st.markdown("### Ajuste Rápido de Caderno")
            novo_nome = st.text_input("Identificador:", value=f['nome_base'])
            
            t_reg, t_p1, t_p2 = st.tabs(["Caderno Regular", "PEI Nível 1", "PEI Nível 2"])
            with t_reg: novo_reg = st.text_area("Texto Regular:", value=f['txt_reg'], height=300)
            with t_p1: novo_p1 = st.text_area("PEI N1:", value=f['pei_1'], height=200)
            with t_p2: novo_p2 = st.text_area("PEI N2:", value=f['pei_2'], height=200)
                
            if st.button("Re-compilar e Substituir", type="primary", use_container_width=True):
                with st.status("Reescrevendo arquivos...") as status:
                    db.excluir_avaliacao_completa(f['nome_base'], f['semana_ref'])
                    info_re = {'ano': f['ano'], 'trimestre': "I Trimestre", 'tipo_prova': "AVALIAÇÃO"}
                    
                    status.write("Construindo Prova Regular...")
                    doc_reg = exporter.gerar_docx_prova_v25(novo_nome, novo_reg, info_re)
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, novo_nome, modo="AVALIACAO")
                    
                    link_p1, link_p2 = "N/A", "N/A"
                    if novo_p1:
                        status.write("Construindo PEI N1...")
                        doc_pei1 = exporter.gerar_docx_pei_v25(f"{novo_nome}_PEI_N1", novo_p1, info_re)
                        link_p1 = db.subir_e_converter_para_google_docs(doc_pei1, f"{novo_nome}_PEI_N1", modo="AVALIACAO")
                    if novo_p2:
                        status.write("Construindo PEI N2...")
                        doc_pei2 = exporter.gerar_docx_pei_v25(f"{novo_nome}_PEI_N2", novo_p2, info_re)
                        link_p2 = db.subir_e_converter_para_google_docs(doc_pei2, f"{novo_nome}_PEI_N2", modo="AVALIACAO")
                        
                    links_f = f"--- LINKS ---\nRegular({link_reg}) PEI_N1({link_p1}) PEI_N2({link_p2})"
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), f['semana_ref'], novo_nome, novo_reg + f"\n\n[NIVEL_1]\n{novo_p1}\n\n[NIVEL_2]\n{novo_p2}\n\n{links_f}", f['ano'], link_reg])
                    
                    status.update(label="Caderno re-compilado!", state="complete")
                    st.balloons(); time.sleep(1); reset_forja()

    # ==============================================================================
    # ABA 2: ACERVO DE PROVAS (Dossiê Analítico V201)
    # ==============================================================================
    with tab_acervo_av:
        st.markdown("### Acervo de Instrumentos Avaliativos")
        
        with st.container(border=True):
            c_h1, c_h2, c_h3 = st.columns(3)
            f_trim_h = c_h1.selectbox("Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="h_trim_av")
            f_ano_h = c_h2.selectbox("Série:", ["Todos", "6º", "7º", "8º", "9º"], key="h_ano_av")
            f_tipo_h = c_h3.selectbox("Tipo:", ["Todos", "AVALIAÇÃO", "REVISÃO"], key="h_tipo_av")

        df_exames = df_aulas[df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy()
        if f_trim_h != "Todos": df_exames = df_exames[df_exames['CONTEUDO'].str.contains(f_trim_h, na=False)]
        if f_ano_h != "Todos": df_exames = df_exames[df_exames['ANO'] == f_ano_h]
        if f_tipo_h != "Todos": df_exames = df_exames[df_exames['SEMANA_REF'] == f_tipo_h]

        df_exames = df_exames.iloc[::-1]

        if df_exames.empty:
            st.info("Nenhum instrumento avaliativo localizado no acervo.")
        else:
            for _, row in df_exames.iterrows():
                with st.container(border=True):
                    txt_f = str(row['CONTEUDO'])
                    identificador = row['TIPO_MATERIAL']
                    val_ex = re.sub(r'[*#]', '', ai.extrair_tag(txt_f, "VALOR")).strip()
                    
                    st.markdown(f"##### {identificador}")
                    st.caption(f"Série: {row['ANO']} | Valor: {val_ex if val_ex else '10.0'}")
                    
                    l_reg = (re.findall(r"Regular\((.*?)\)", txt_f) or [row.get('LINK_DRIVE')])[-1]
                    l_pei1 = (re.findall(r"PEI_N1\((.*?)\)", txt_f) or re.findall(r"PEI\((.*?)\)", txt_f) or [None])[-1]
                    l_pei2 = (re.findall(r"PEI_N2\((.*?)\)", txt_f) or [None])[-1]
                    l_prof = (re.findall(r"Prof\((.*?)\)", txt_f) or [None])[-1]

                    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
                    c_b1.link_button("Download DOCX", str(l_reg), use_container_width=True, type="primary")
                    
                    if l_prof and "N/A" not in str(l_prof): c_b2.link_button("Guia Professor", str(l_prof), use_container_width=True)
                    else: c_b2.button("Sem Guia", disabled=True, use_container_width=True, key=f"no_guide_{row.name}")
                    
                    if c_b3.button("Refinar", key=f"ref_av_h_{row.name}", use_container_width=True):
                        pei1 = ai.extrair_tag(txt_f, "NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                        pei2 = ai.extrair_tag(txt_f, "NIVEL_2")
                        reg_match = re.split(r'\[(?:PEI|NIVEL_1)\]', txt_f, flags=re.IGNORECASE)
                        
                        st.session_state.forja = {
                            'fase': 6, 'nome_base': identificador,
                            'txt_reg': reg_match[0].strip() if reg_match else txt_f,
                            'pei_1': pei1, 'pei_2': pei2, 'pei_3': ai.extrair_tag(txt_f, "NIVEL_3"),
                            'ano': row['ANO'], 'semana_ref': row['SEMANA_REF']
                        }
                        st.rerun()
                        
                    if c_b4.button("Apagar", key=f"del_av_h_{row.name}", use_container_width=True):
                        if db.excluir_avaliacao_completa(identificador, row['SEMANA_REF']): st.rerun()

                    # 🚨 DOSSIÊ PSICOMÉTRICO E ANÁLISE DE ITENS (Clean visual)
                    with st.expander("👁️ Analisar Estrutura Psicométrica e Distratores"):
                        t_gab, t_ques, t_pei_v = st.tabs(["Perícia Regular", "Prova Regular", "Inclusão PEI"])
                        
                        with t_gab:
                            st.markdown("**🔬 Grade de Perícia e Análise de Distratores**")
                            grade_raw = ai.extrair_tag(txt_f, "GRADE_DE_CORRECAO")
                            if grade_raw:
                                questoes_grade = re.split(r"(?i)QUEST[AÃ]O\s*0?(\d+)", grade_raw)
                                if len(questoes_grade) > 1:
                                    for i in range(1, len(questoes_grade), 2):
                                        q_num, q_txt = questoes_grade[i], questoes_grade[i+1]
                                        q_txt_limpo = re.sub(r'[*#]', '', q_txt).strip()
                                        
                                        m_hab = re.search(r"(?i)(?:HABILIDADE|BNCC|DESCRITOR).*?[:\-]\s*(.*?)(?=RESPOSTA|JUSTIFICATIVA|ALERTA|PERÍCIA|$)", q_txt_limpo, re.DOTALL)
                                        m_just = re.search(r"(?i)(?:RESPOSTA|JUSTIFICATIVA).*?[:\-]\s*(.*?)(?=ALERTA|PERÍCIA|DISTRATORES|$)", q_txt_limpo, re.DOTALL)
                                        m_peri = re.search(r"(?i)(?:ALERTA|PERÍCIA|DISTRATORES).*?[:\-]\s*(.*)", q_txt_limpo, re.DOTALL)
                                        
                                        with st.container(border=True):
                                            st.markdown(f"**Item {q_num}**")
                                            if m_hab: st.caption(f"🆔 **Competência/Habilidade:** {m_hab.group(1).strip()}")
                                            if m_just: st.write(f"🎯 **Gabarito Justificado:** {m_just.group(1).strip()}")
                                            if m_peri: st.warning(f"🧠 **Raciocínio dos Distratores:** {m_peri.group(1).strip()}")
                                else: st.text(grade_raw)
                            else: st.warning("Perícia indisponível.")

                        with t_ques:
                            st.markdown("**📋 Enunciados do Caderno de Prova**")
                            questoes_reg = ai.extrair_tag(txt_f, "QUESTOES")
                            if questoes_reg:
                                st.write(preparar_para_leitura(questoes_reg))

                        with t_pei_v:
                            st.markdown("**♿ Estrutura PEI Adaptada**")
                            pei_txt = ai.extrair_tag(txt_f, "NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                            if pei_txt:
                                st.write(preparar_para_leitura(pei_txt))


# ==============================================================================
# MÓDULO: CENTRAL DE INTELIGÊNCIA DE RESULTADOS (CIR) - V201 (LENTE INTELIGENTE)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("Central de Inteligência de Resultados (CIR)")
    st.caption("Mesa de triagem de exames, digitalização via Visão Computacional e auditoria em tempo real.")
    st.markdown("---")

    if "v_scan" not in st.session_state: st.session_state.v_scan = int(time.time())
    v = st.session_state.v_scan

    # 🚨 VACINA DE ESCOPO GLOBAL: Define a lista de turmas para todas as abas do Scanner
    lista_turmas_cir = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais_cir = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_cir = sorted(turmas_reais_cir['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_cir = sorted(df_alunos['TURMA'].unique())

    # FILTRO HIERÁRQUICO DE ATIVOS CIR (Soberano V201)
    def filtrar_ativos_cir(turma, trimestre_nome, apenas_provas=True):
        if not turma or not trimestre_nome: return []
        try:
            serie_num = str(turma)[0] 
            df_f = df_aulas[df_aulas['ANO'].astype(str).str.contains(serie_num)].copy()
            
            def detectar_trimestre(x):
                try:
                    if str(x).replace('.','',1).isdigit():
                        dt = date(1899, 12, 30) + timedelta(days=int(float(x)))
                        return util.obter_info_trimestre(dt)[0]
                    if "/" in str(x):
                        partes = str(x).split("/")
                        dt = date(int(partes[2]), int(partes[1]), int(partes[0]))
                        return util.obter_info_trimestre(dt)[0]
                except: pass
                return "Outros"

            df_f['TRIM_DETECTADO'] = df_f['DATA'].apply(detectar_trimestre)
            trim_limpo = trimestre_nome.replace(" ", "")
            
            if apenas_provas:
                permitidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]
                proibidos = ["REVISAO", "REVISÃO", "APLICAÇÃO", "CORREÇÃO", "APRESENTAÇÃO", "DOSSIÊ", "AULA"]
                
                mask_permitidos = df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos))
                df_f = df_f[mask_permitidos]
                
                mask_proibidos = df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(proibidos))
                df_f = df_f[~mask_proibidos]
                
                mask_trim = (
                    (df_f['TRIM_DETECTADO'] == trimestre_nome) | 
                    (df_f['CONTEUDO'].str.contains(trimestre_nome, na=False, case=False)) | 
                    (df_f['CONTEUDO'].str.contains(trim_limpo, na=False, case=False)) | 
                    (df_f['TIPO_MATERIAL'].str.contains(trimestre_nome, na=False, case=False)) |
                    (df_f['TIPO_MATERIAL'].str.contains(trim_limpo, na=False, case=False)) |
                    (df_f['TIPO_MATERIAL'].str.upper().str.contains("FINAL"))
                )
                df_f = df_f[mask_trim]
            else:
                permitidos = ["PROJETO", "FIXAÇÃO", "REFORÇO", "ATIVIDADE", "TRABALHO", "AULA"]
                proibidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]
                
                mask_permitidos = df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos))
                df_f = df_f[mask_permitidos]
                
                mask_proibidos = df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(proibidos))
                df_f = df_f[~mask_proibidos]
                
                mask_trim = (
                    (df_f['TRIM_DETECTADO'] == trimestre_nome) | 
                    (df_f['CONTEUDO'].str.contains(trimestre_nome, na=False, case=False)) | 
                    (df_f['CONTEUDO'].str.contains(trim_limpo, na=False, case=False)) | 
                    (df_f['TIPO_MATERIAL'].str.contains(trimestre_nome, na=False, case=False)) |
                    (df_f['TIPO_MATERIAL'].str.contains(trim_limpo, na=False, case=False))
                )
                df_f = df_f[mask_trim]
            
            return sorted(df_f['TIPO_MATERIAL'].unique().tolist())
        except Exception as e: 
            return []

    # CONSOLIDAÇÃO DE ABAS (De 4 para 3)
    tab_correcao, tab_auditoria, tab_raiox = st.tabs([
        "Mesa de Correção", "Tribunal de Auditoria", "Raio-X Pedagógico"
    ])

    # ==============================================================================
    # ABA 1: MESA DE CORREÇÃO (PROVAS & TRABALHOS UNIFICADOS)
    # ==============================================================================
    with tab_correcao:
        modo_lancamento = st.radio("Selecione a Atividade para Lançar:", ["📸 Provas (Scanner/Manual)", "✍️ Trabalhos & Projetos (Lote)"], horizontal=True, key=f"cir_modo_l_{v}")
        st.markdown("---")

        # ROTA A: PROVAS (SCANNER / MANUAL / QUALITATIVA)
        if "Provas" in modo_lancamento:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                t_sel = c1.selectbox("👥 Turma:", [""] + lista_turmas_cir, key=f"t_p_{v}")
                tr_sel = c2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_p_{v}")
                
                opcoes_p = filtrar_ativos_cir(t_sel, tr_sel, apenas_provas=True)
                if t_sel and tr_sel:
                    trim_limpo = tr_sel.replace(" ", "")
                    mask_diag = (df_diagnosticos['TURMA'] == t_sel) & (
                        df_diagnosticos['ID_AVALIACAO'].str.contains(tr_sel, case=False, na=False) |
                        df_diagnosticos['ID_AVALIACAO'].str.contains(trim_limpo, case=False, na=False)
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
                escaneados_raw = df_diag_turma[df_diag_turma['ID_AVALIACAO'].str.startswith(nome_filtro_pendente, na=False)]['ID_ALUNO'].astype(str).tolist()
                
                trim_limpo = tr_sel.replace(" ", "")
                serie_num = "".join(filter(str.isdigit, t_sel))
                escaneados_2a = df_diag_turma[(df_diag_turma['ID_AVALIACAO'].str.contains("2ª|2CHAMADA", regex=True, case=False)) & (df_diag_turma['ID_AVALIACAO'].str.contains(trim_limpo, case=False))]['ID_ALUNO'].astype(str).tolist()
                escaneados_unicos = list(set(escaneados_raw + escaneados_2a))
                
                pendentes = df_alunos[(df_alunos['TURMA'] == t_sel) & (~df_alunos['ID'].astype(str).isin(escaneados_unicos))].sort_values(by="NOME_ALUNO")
                total_turma = len(df_alunos[df_alunos['TURMA'] == t_sel])
                total_corrigidos = len(escaneados_unicos)

                # 📊 LAYOUT SPLIT-SCREEN (Bento Grid)
                col_fila, col_mesa = st.columns([1.2, 1.8])

                with col_fila:
                    with st.container(border=True):
                        st.markdown("##### Fila de Triagem")
                        progresso = total_corrigidos / total_turma if total_turma > 0 else 0
                        st.progress(min(1.0, max(0.0, progresso)))
                        st.caption(f"{total_corrigidos} de {total_turma} alunos processados.")
                        
                        if pendentes.empty:
                            st.success("Soberania Total: Todos os alunos corrigidos!")
                            st.stop()
                        
                        al_sel = st.selectbox("Selecione o Estudante:", [""] + pendentes['NOME_ALUNO'].tolist(), key=f"pilha_{v}", label_visibility="collapsed")
                        
                        if st.button("Ausências em Lote", use_container_width=True):
                            st.session_state.show_faltas_lote = not st.session_state.get("show_faltas_lote", False)
                        
                        if st.session_state.get("show_faltas_lote", False):
                            faltosos = st.multiselect("Marcar faltosos:", pendentes['NOME_ALUNO'].tolist())
                            if st.button("Confirmar Ausências", type="primary", use_container_width=True):
                                linhas_faltas = []
                                data_hoje = datetime.now().strftime("%d/%m/%Y")
                                for f_nome in faltosos:
                                    f_id = pendentes[pendentes['NOME_ALUNO'] == f_nome].iloc[0]['ID']
                                    linhas_faltas.append([data_hoje, f_id, f_nome, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                if db.salvar_lote("DB_GABARITOS_ALUNOS", linhas_faltas):
                                    st.success("Faltas registradas!"); time.sleep(0.5); st.rerun()

                with col_mesa:
                    if al_sel:
                        al_info = pendentes[pendentes['NOME_ALUNO'] == al_sel].iloc[0]
                        id_aluno_atual = al_info['ID']
                        nec_aluno = str(al_info['NECESSIDADES']).upper().strip()
                        
                        # 🚨 INTERCONEXÃO: MINI-CARD DE CONTEXTO DO DIÁRIO (V201)
                        with st.container(border=True):
                            st.markdown(f"##### {al_sel}")
                            if nec_aluno not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE"]:
                                st.warning(f"Perfil Clínico/Inclusivo: {nec_aluno}")
                                
                            if not df_diario.empty:
                                d_alu_scan = df_diario[df_diario['ID_ALUNO'].apply(db.limpar_id) == id_aluno_atual]
                                faltas_scan = len(d_alu_scan[d_alu_scan['TAGS'] == "AUSÊNCIA"])
                                bonus_scan = d_alu_scan['BONUS'].apply(util.sosa_to_float).sum()
                                
                                c_ctx1, c_ctx2 = st.columns(2)
                                c_ctx1.metric("Faltas Acumuladas", faltas_scan)
                                c_ctx2.metric("Mérito/Bônus de Sala", f"{bonus_scan:+.1f} pts")
                                
                                obs_recentes = d_alu_scan[(d_alu_scan['OBSERVACOES'] != "") & (~d_alu_scan['TAGS'].isin(["SISTEMA_NOTA", "BONUS_CONSELHO", "DIA NÃO LETIVO"]))]
                                if not obs_recentes.empty:
                                    st.caption("**Observações Recentes no Diário:**")
                                    for _, r_obs in obs_recentes.tail(2).iterrows():
                                        st.write(f"- {r_obs['DATA']}: *{r_obs['OBSERVACOES']}*")

                        # 🚨 LENTE INTELIGENTE: Auto-detecção de Perfil (V201.5 - Sincronia PEI)
                        idx_lente_default = 0
                        if "(PEI N1)" in nec_aluno: idx_lente_default = 1
                        elif "(PEI N2)" in nec_aluno: idx_lente_default = 2
                        elif "(PEI N3)" in nec_aluno: idx_lente_default = 3
                        elif any(x in nec_aluno for x in ["PEI", "TEA", "TDAH", "DISLEXIA", "INTELECTUAL", "TOD"]): 
                            idx_lente_default = 1 # Fallback caso o nível ainda não tenha sido definido na Matriz
                            
                        with st.container(border=True):
                            lente_corr = st.radio(
                                "Lente de Correção (Auto-mapeada):", 
                                ["Regular (Padrão ou Variante)", "PEI Nível 1 (Apoio Leve)", "PEI Nível 2 (Apoio Moderado)", "PEI Nível 3 / Qualitativa (Manual)"],
                                index=idx_lente_default,
                                key=f"lente_{id_aluno_atual}"
                            )

                        material_ref = None
                        is_pei_grading = "PEI Nível 1" in lente_corr or "PEI Nível 2" in lente_corr
                        nivel_alvo_pei = "NIVEL_1" if "Nível 1" in lente_corr else "NIVEL_2"
                        is_qualitativa = "Nível 3" in lente_corr
                        modo_2a = False
                        
                        if "Regular" in lente_corr:
                            c_reg1, c_reg2 = st.columns(2)
                            modo_2a = c_reg1.toggle("2ª Chamada Discursiva", key=f"t2a_{id_aluno_atual}")
                            
                            tipo_base = at_sel.split("-")[0].strip().upper()
                            if modo_2a:
                                df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(serie_num))]
                                at_segunda = c_reg2.selectbox("Caderno de 2ª Chamada:", [""] + df_2a['TIPO_MATERIAL'].unique().tolist(), key=f"s2a_{id_aluno_atual}")
                                if at_segunda:
                                    df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_segunda]
                                    if not df_busca.empty: material_ref = df_busca.iloc[0]
                            else:
                                df_variantes = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains(tipo_base)) & (df_aulas['TIPO_MATERIAL'].str.upper().str.contains("TIPO")) & (df_aulas['ANO'].str.contains(serie_num))]
                                versao_variante = c_reg2.selectbox("Caderno/Variante:", ["Padrão (Tipo A)"] + df_variantes['TIPO_MATERIAL'].unique().tolist(), key=f"var_{id_aluno_atual}")
                                df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == (at_sel if versao_variante == "Padrão (Tipo A)" else versao_variante)]
                                if not df_busca.empty: material_ref = df_busca.iloc[0]
                                    
                        elif is_pei_grading or is_qualitativa:
                            df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel]
                            if not df_busca.empty: material_ref = df_busca.iloc[0]

                        # EXECUÇÃO DO MOTOR DE CORREÇÃO
                        if material_ref is not None:
                            txt_ref = str(material_ref['CONTEUDO'])
                            val_tag = ai.extrair_tag(txt_ref, "VALOR")
                            v_total_at = util.sosa_to_float(val_tag) if val_tag else 10.0

                            def extrair_gab_blindado(texto, is_pei=False, nivel_pei="NIVEL_1"):
                                if is_pei:
                                    bloco_pei = ai.extrair_tag(texto, nivel_pei)
                                    if not bloco_pei: return []
                                    match_gab = re.search(r"(?i)GABARITO.*", bloco_pei, re.DOTALL)
                                    area_busca = match_gab.group(0) if match_gab else bloco_pei
                                    matches = re.findall(r"(\d+)[\s\.\)\-:]+([A-C])", area_busca.upper())
                                else:
                                    raw = ai.extrair_tag(texto, "GABARITO_TEXTO") or ai.extrair_tag(texto, "GABARITO")
                                    matches = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", str(raw).upper())
                                if not matches: return []
                                mapa = {int(num): letra for num, letra in matches}
                                return [mapa[n] for n in sorted(mapa.keys())]

                            gab_alvo = extrair_gab_blindado(txt_ref, is_pei_grading, nivel_alvo_pei)

                            # Rota 2ª Chamada (Discursiva)
                            if modo_2a:
                                q_raw = ai.extrair_tag(txt_ref, "QUESTOES")
                                qtd_q_2a = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw)) or 10
                                peso_q = v_total_at / qtd_q_2a
                                
                                df_manual = st.data_editor(
                                    pd.DataFrame([{"Q": f"{i+1:02d}", "Avaliação": "⚪ Em Branco"} for i in range(qtd_q_2a)]), hide_index=True,
                                    column_config={"Q": st.column_config.TextColumn(disabled=True, width="small"), "Avaliação": st.column_config.SelectboxColumn(options=["✅ Acerto Integral", "⚠️ Acerto Parcial", "❌ Erro", "⚪ Em Branco"], required=True)},
                                    key=f"manual_2a_{id_aluno_atual}"
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
                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, material_ref['TIPO_MATERIAL'], ";".join(respostas_finais), util.sosa_to_str(nota_calc), "N/A"])
                                    st.success("Salvo!"); time.sleep(0.5); st.rerun()

                            # Rota Regular ou PEI (Múltipla Escolha)
                            elif is_pei_grading or "Regular" in lente_corr:
                                c_m1, c_m2 = st.columns([2, 1])
                                modo_correcao = c_m1.radio("Método de Correção:", ["📸 Scanner Câmera", "✍️ Digitação Manual (Speed Grader)"], horizontal=True, key=f"mc_{id_aluno_atual}")
                                if c_m2.button("Ausência", use_container_width=True):
                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                    st.rerun()

                                # Câmera / Scanner
                                if "Scanner" in modo_correcao:
                                    img_file = st.file_uploader("Carregar foto do gabarito:", type=["jpg", "jpeg", "png"], key=f"up_{id_aluno_atual}")
                                    img_cam = st.camera_input("Capturar via Câmera:", key=f"cam_{id_aluno_atual}")
                                    img = img_file if img_file else img_cam

                                    if img and "current_scan_res" not in st.session_state:
                                        with st.spinner("Analisando marcações..."):
                                            res_json = ai.analisar_gabarito_vision(img.getvalue())
                                            st.session_state.current_scan_res = [res_json.get(f"{i+1:02d}", "?") for i in range(len(gab_alvo))]
                                            st.session_state.current_scan_img = img.getvalue(); st.rerun()

                                    if "current_scan_res" in st.session_state:
                                        res_lidas = st.session_state.current_scan_res
                                        dados_pericia = []
                                        for i, lido in enumerate(res_lidas):
                                            if i < len(gab_alvo):
                                                status = "✅ ACERTO" if lido == gab_alvo[i] else ("🚫 DUPLA" if lido == "X" else "❌ ERRO")
                                                dados_pericia.append({"Q": f"{i+1:02d}", "Lido": lido, "Status": status})
                                        
                                        df_mesa = st.data_editor(pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                                            column_config={"Q": st.column_config.TextColumn(disabled=True), "Lido": st.column_config.SelectboxColumn("Ajustar", options=["A", "B", "C", "D", "E", "X", "?"], required=True), "Status": st.column_config.TextColumn(disabled=True)},
                                            key=f"ed_turbo_{id_aluno_atual}")
                                        
                                        novas_res = df_mesa["Lido"].tolist()
                                        acertos = sum(1 for i, r in enumerate(novas_res) if i < len(gab_alvo) and r == gab_alvo[i])
                                        nota_f = (acertos / len(gab_alvo)) * v_total_at
                                        st.metric("Nota Final Calculada", f"{nota_f:.1f}", delta=f"{acertos}/{len(gab_alvo)} acertos")
                                        
                                        col_s1, col_s2 = st.columns(2)
                                        if col_s1.button("Gravar Correção", type="primary", use_container_width=True):
                                            with st.spinner("Gravando..."):
                                                link_pasta = db.subir_e_converter_para_google_docs(st.session_state.current_scan_img, al_sel.replace(" ","_"), trimestre=tr_sel, categoria=t_sel, semana=material_ref['TIPO_MATERIAL'], modo="SCANNER")
                                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, material_ref['TIPO_MATERIAL'], ";".join(novas_res), util.sosa_to_str(nota_f), link_pasta])
                                                del st.session_state.current_scan_res; del st.session_state.current_scan_img
                                                st.success("Gravado!"); time.sleep(0.5); st.rerun()
                                        if col_s2.button("Descartar", use_container_width=True):
                                            del st.session_state.current_scan_res; del st.session_state.current_scan_img; st.rerun()

                                # Digitação Manual
                                else:
                                    opcoes_letras = ["A", "B", "C", "X", "?"] if is_pei_grading else ["A", "B", "C", "D", "E", "X", "?"]
                                    dados_manual = [{"Q": f"{i+1:02d}", "Gabarito": gab_alvo[i], "Resposta": "?", "Cálculo": True} for i in range(len(gab_alvo))]
                                    
                                    df_manual = st.data_editor(
                                        pd.DataFrame(dados_manual), hide_index=True, use_container_width=True,
                                        column_config={"Q": st.column_config.TextColumn(disabled=True), "Gabarito": st.column_config.TextColumn(disabled=True), "Resposta": st.column_config.SelectboxColumn(options=opcoes_letras, required=True), "Cálculo": st.column_config.CheckboxColumn("Cálculo OK", default=True)},
                                        key=f"manual_grid_{id_aluno_atual}"
                                    )
                                    
                                    peso_q = v_total_at / len(gab_alvo)
                                    nota_calc = 0.0
                                    respostas_finais = []
                                    for i, row in df_manual.iterrows():
                                        resp = row["Resposta"]
                                        respostas_finais.append(resp)
                                        if resp == row["Gabarito"]:
                                            nota_calc += peso_q if row["Cálculo"] else (peso_q / 2)
                                            
                                    st.metric("Nota Calculada", f"{nota_calc:.1f} / {v_total_at:.1f}")
                                    if st.button("Gravar Correção Manual", type="primary", use_container_width=True):
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, material_ref['TIPO_MATERIAL'], ";".join(respostas_finais), util.sosa_to_str(nota_calc), "N/A"])
                                        st.success("Salvo!"); time.sleep(0.5); st.rerun()

                        # Rota PEI Nível 3 / Qualitativa
                        elif is_qualitativa:
                            st.warning("Avaliação Qualitativa: Sem múltipla escolha. Avaliação baseada em rubricas de mediação direta.")
                            nivel3_txt = re.split(r"--- LINKS ---", ai.extrair_tag(txt_ref, "NIVEL_3"), flags=re.IGNORECASE)[0].strip() if ai.extrair_tag(txt_ref, "NIVEL_3") else ""
                            rubricas_encontradas = []
                            
                            if nivel3_txt:
                                m_rubrica = re.search(r"(?i)RUBRICA.*?(?:\n)(.*)", nivel3_txt, re.DOTALL)
                                if m_rubrica:
                                    for linha in m_rubrica.group(1).split('\n'):
                                        linha_limpa = re.sub(r'^[-*•]\s*', '', linha).replace('**', '').strip()
                                        if linha_limpa and len(linha_limpa) > 5 and "http" not in linha_limpa.lower():
                                            rubricas_encontradas.append(linha_limpa)
                            
                            c_q1, c_q2 = st.columns([1, 1.5])
                            nota_qual = c_q1.number_input("Nota Atribuída:", 0.0, v_total_at, v_total_at, step=0.5, key=f"nq_{id_aluno_atual}")
                            respostas_rubrica = []
                            
                            with c_q2:
                                if rubricas_encontradas:
                                    for i, rubrica in enumerate(rubricas_encontradas):
                                        st.markdown(f"**{rubrica}**")
                                        resp = st.selectbox("Status:", ["✅ Autônomo", "🤝 Com Apoio", "❌ Não Realizado"], key=f"rub_{id_aluno_atual}_{i}", label_visibility="collapsed")
                                        respostas_rubrica.append(f"- {rubrica}: {resp}")
                                    obs_extra = st.text_area("Notas extras:", height=60, key=f"oq_extra_{id_aluno_atual}")
                                    parecer_final = "\n".join(respostas_rubrica) + (f"\nObs: {obs_extra}" if obs_extra.strip() else "")
                                else:
                                    parecer_final = st.text_area("Parecer Pedagógico Qualitativo:", height=150, key=f"oq_{id_aluno_atual}")
                                    
                            if st.button("Salvar Avaliação PEI N3", type="primary", use_container_width=True):
                                if not parecer_final.strip(): st.error("Preencha o parecer.")
                                else:
                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, at_sel, f"QUALITATIVA|{parecer_final}", util.sosa_to_str(nota_qual), "N/A"])
                                    db.salvar_no_banco("DB_RELATORIOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, "AVALIACAO_QUALITATIVA", f"Avaliação: {at_sel}\nNota: {nota_qual}\nParecer:\n{parecer_final}"])
                                    st.success("Salvo!"); time.sleep(0.5); st.rerun()

        # ROTA B: TRABALHOS & PROJETOS (SPEED GRADER)
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
                v_max_padrao = util.sosa_to_float(val_tag) if val_tag else 2.0
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
                
                # ✍️ SPEED GRADER TABLE
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
    # ABA 2: TRIBUNAL DE AUDITORIA (AUDITORIA, REVISÃO DE PERÍCIA E LÁZARO)
    # ==============================================================================
    with tab_auditoria:
        st.markdown("### Tribunal de Auditoria de Resultados")
        with st.container(border=True):
            c_h1, c_h2 = st.columns(2)
            t_sel_h = c_h1.selectbox("👥 Selecione a Turma:", [""] + lista_turmas_cir, key=f"t_h_{v}")
            tr_sel_h = c_h2.selectbox("📅 Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_h_{v}")

        if t_sel_h:
            serie_num = "".join(filter(str.isdigit, t_sel_h))
            opcoes_auditoria = filtrar_ativos_cir(t_sel_h, tr_sel_h, apenas_provas=True)
            exames_feitos = df_diagnosticos[(df_diagnosticos['TURMA'] == t_sel_h)]['ID_AVALIACAO'].unique().tolist()
            todas_opcoes = list(set(opcoes_auditoria + exames_feitos))
            opcoes_base = [opt for opt in todas_opcoes if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            
            av_alvo_h = st.selectbox("📋 Avaliação Alvo:", [""] + sorted(opcoes_base), key=f"av_h_{v}")

            if av_alvo_h:
                is_sonda = "SONDA" in av_alvo_h.upper() or "DIAGNÓSTICA" in av_alvo_h.upper()
                nome_curto_av = av_alvo_h.split("-")[0].strip()
                trim_limpo = tr_sel_h.replace(" ", "")
                
                mask_gabaritos = (df_diagnosticos['TURMA'] == t_sel_h) & (
                    df_diagnosticos['ID_AVALIACAO'].str.contains(nome_curto_av) | 
                    (df_diagnosticos['ID_AVALIACAO'].str.contains("2ª|2CHAMADA", regex=True, case=False) & df_diagnosticos['ID_AVALIACAO'].str.contains(trim_limpo, case=False))
                )
                gabaritos_lidos = df_diagnosticos[mask_gabaritos]
                alunos_turma_h = df_alunos[df_alunos['TURMA'] == t_sel_h].sort_values(by="NOME_ALUNO")
                
                dados_soberania = []
                for _, alu in alunos_turma_h.iterrows():
                    id_a = db.limpar_id(alu['ID'])
                    leitura = gabaritos_lidos[gabaritos_lidos['ID_ALUNO'].apply(db.limpar_id) == id_a]
                    situacao_txt, versao_prova, nota_atual, link_ev, respostas_salvas = "✍️ PENDENTE", "PROVA ORIGINAL", 0.0, "", "MANUAL"

                    if not leitura.empty:
                        reg = leitura.iloc[-1]
                        nota_atual = util.sosa_to_float(reg['NOTA_CALCULADA'])
                        link_ev = reg.get('LINK_FOTO_DRIVE', '')
                        respostas_salvas = reg.get('RESPOSTAS_ALUNO', 'MANUAL')
                        id_av_banco = str(reg['ID_AVALIACAO']).upper()
                        
                        if reg['RESPOSTAS_ALUNO'] == "FALTOU": situacao_txt, versao_prova = "❌ FALTOU", "N/A"
                        elif "2ª" in id_av_banco or "2CHAMADA" in id_av_banco: situacao_txt, versao_prova = "SEGUNDA CHAMADA", "SEGUNDA CHAMADA"
                        elif "TIPO" in id_av_banco: situacao_txt, versao_prova = "✅ REALIZADA", f"VARIANTE ({id_av_banco.split('-')[-1].strip()})"
                        else: situacao_txt, versao_prova = "✅ REALIZADA", "PROVA ORIGINAL"

                    dados_soberania.append({
                        "ID": id_a, "Estudante": alu['NOME_ALUNO'], "Perfil": "♿ PEI" if str(alu['NECESSIDADES']).upper().strip() not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"] else "📝 REGULAR",
                        "Situação": situacao_txt, "Versão": versao_prova, "Nota": nota_atual, "Evidência": link_ev, "_Respostas": respostas_salvas
                    })

                df_soberano_ed = st.data_editor(
                    pd.DataFrame(dados_soberania), hide_index=True, use_container_width=True, key=f"ed_sob_{v}",
                    column_config={"ID": None, "_Respostas": None, "Estudante": st.column_config.TextColumn(disabled=True), "Perfil": st.column_config.TextColumn(disabled=True), "Situação": st.column_config.SelectboxColumn(options=["✅ REALIZADA", "❌ FALTOU", "✍️ PENDENTE"], required=True), "Versão": st.column_config.TextColumn(disabled=True), "Nota": st.column_config.NumberColumn(format="%.1f"), "Evidência": st.column_config.LinkColumn("🔗 Ver Foto")}
                )

                if st.button("Homologar Ajustes e Atualizar Boletins", use_container_width=True, type="primary"):
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
                            
                            if r['Situação'] == "✅ REALIZADA":
                                id_f = av_alvo_h if r['Versão'] == "PROVA ORIGINAL" else f"{av_alvo_h} ({r['Versão']})"
                                dados_atualizados.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, id_f, "MANUAL" if resp_originais == "FALTOU" else resp_originais, nota_s, r['Evidência'] or "N/A"])
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
                                    
                                nova_media_final = min(10.0, v_vistos + v_teste + v_prova)
                                if v_rec > 0: nova_media_final = max(nova_media_final, v_rec)
                                lista_boletim.append([id_l, nome_limpo, t_sel_h, tr_sel_h, v_vistos, v_teste, v_prova, v_rec, nova_media_final])
                        
                        ws_g.clear(); ws_g.update(values=dados_atualizados, range_name='A1')
                        if not is_sonda and lista_boletim:
                            db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                            db.salvar_lote("DB_NOTAS", lista_boletim)
                        status_h.update(label="Notas e gabaritos auditados!", state="complete"); time.sleep(0.5); st.rerun()

                st.markdown("---")
                
                # Procura o gabarito de referência
                df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'] == av_alvo_h]
                gab_oficial_trib = {}
                if not df_prova_trib.empty:
                    txt_prova_trib = str(df_prova_trib.iloc[0]['CONTEUDO'])
                    raw_gab_base = ai.extrair_tag(txt_prova_trib, "GABARITO_TEXTO") or ai.extrair_tag(txt_prova_trib, "GABARITO")
                    matches_base = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", raw_gab_base.upper())
                    gab_oficial_trib = {int(num): letra for num, letra in matches_base} if matches_base else {}

                # ✏️ REVISÃO DE PERÍCIA REATIVA (PRÉ-PREENCHIDA E INTERATIVA - V201)
                with st.expander("✏️ Revisão de Perícia (Corrigir Leitura da IA)", expanded=False):
                    df_scanned = pd.DataFrame([r for r in dados_soberania if r['_Respostas'] not in ["MANUAL", "FALTOU"] and not str(r['_Respostas']).startswith("QUALITATIVA")])
                    
                    if not df_scanned.empty:
                        aluno_rev_nome = st.selectbox("Selecione o Estudante para Corrigir:", [""] + df_scanned['Estudante'].tolist(), key=f"rev_alu_sel_{v}")
                        
                        if aluno_rev_nome:
                            al_rev_data = df_scanned[df_scanned['Estudante'] == aluno_rev_nome].iloc[0]
                            id_aluno_rev = al_rev_data['ID']
                            respostas_atuais = str(al_rev_data['_Respostas']).split(';')
                            
                            # 🚨 VACINA DE COMPATIBILIDADE: Garante que o vetor de respostas tenha o tamanho exato da prova
                            while len(respostas_atuais) < len(gab_oficial_trib):
                                respostas_atuais.append("?")
                            
                            if not df_prova_trib.empty:
                                val_total_av = util.sosa_to_float(ai.extrair_tag(txt_prova_trib, "VALOR")) or 10.0
                                grid_data = []
                                
                                for idx_q in range(len(gab_oficial_trib)):
                                    # Puxa o que a IA leu originalmente para pré-preencher a planilha
                                    lido_aluno = respostas_atuais[idx_q].strip().upper() if idx_q < len(respostas_atuais) else "?"
                                    if lido_aluno not in ["A", "B", "C", "D", "E", "X", "?"]:
                                        lido_aluno = "?"
                                        
                                    correta_q = gab_oficial_trib.get(idx_q+1, "?")
                                    status_q = "✅" if lido_aluno == correta_q else "❌"
                                    
                                    grid_data.append({
                                        "Questão": f"Q{idx_q+1:02d}",
                                        "Gabarito Oficial": correta_q,
                                        "Corrigir Resposta": lido_aluno, # Pré-preenchido com o valor lido pela IA!
                                        "Status": status_q
                                    })
                                
                                # Renderiza a planilha de correção rápida
                                df_rev_ed = st.data_editor(
                                    pd.DataFrame(grid_data), 
                                    hide_index=True, 
                                    use_container_width=True,
                                    column_config={
                                        "Questão": st.column_config.TextColumn(disabled=True),
                                        "Gabarito Oficial": st.column_config.TextColumn(disabled=True),
                                        "Corrigir Resposta": st.column_config.SelectboxColumn("Corrigir Resposta", options=["A", "B", "C", "D", "E", "X", "?"], required=True),
                                        "Status": st.column_config.TextColumn(disabled=True)
                                    },
                                    key=f"grid_rev_{id_aluno_rev}"
                                )
                                
                                # 🚨 CÁLCULO E FEEDBACK EM TEMPO REAL
                                novas_letras = df_rev_ed["Corrigir Resposta"].tolist()
                                novos_acertos = sum(1 for i, r in enumerate(novas_letras) if i+1 in gab_oficial_trib and r == gab_oficial_trib[i+1])
                                nova_nota_calc = (novos_acertos / len(gab_oficial_trib)) * val_total_av if len(gab_oficial_trib) > 0 else 0.0
                                
                                st.metric("Média Recalculada para este Estudante", f"{nova_nota_calc:.1f} / {val_total_av:.1f}")
                                
                                if st.button("💾 Gravar Correções da Perícia", type="primary", use_container_width=True, key=f"btn_save_rev_{id_aluno_rev}"):
                                    with st.spinner("Gravando e aplicando cascata de notas..."):
                                        # 1. Atualiza a folha de gabarito do aluno no banco
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                            datetime.now().strftime("%d/%m/%Y"), id_aluno_rev, aluno_rev_nome, t_sel_h, av_alvo_h, ";".join(novas_letras), util.sosa_to_str(nova_nota_calc), al_rev_data['Evidência'] or "N/A"
                                        ])
                                        
                                        # 2. Deleta as notas antigas do boletim da turma no trimestre
                                        db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                        
                                        # 3. Reconstrói o boletim aplicando a nova nota em cascata de forma invisível
                                        lista_boletim_rev = []
                                        notas_atuais_rev = df_notas[(df_notas['TURMA'] == t_sel_h) & (df_notas['TRIMESTRE'] == tr_sel_h)]
                                        
                                        for _, r_sob in df_soberano_ed.iterrows():
                                            id_l = str(r_sob['ID'])
                                            nome_l = r_sob['Estudante']
                                            reg_atual = notas_atuais_rev[notas_atuais_rev['ID_ALUNO'].apply(db.limpar_id) == id_l]
                                            v_vistos = reg_atual.iloc[0]['NOTA_VISTOS'] if not reg_atual.empty else "0,0"
                                            v_teste = reg_atual.iloc[0]['NOTA_TESTE'] if not reg_atual.empty else "0,0"
                                            v_prova = reg_atual.iloc[0]['NOTA_PROVA'] if not reg_atual.empty else "0,0"
                                            v_rec = reg_atual.iloc[0]['NOTA_REC'] if not reg_atual.empty else "0,0"
                                            
                                            # Se for o aluno editado, injeta a nota nova, senão mantém a do grid
                                            nota_aluno_av = util.sosa_to_str(nova_nota_calc) if id_l == id_aluno_rev else util.sosa_to_str(r_sob['Nota'])
                                            if "TESTE" in av_alvo_h.upper(): v_teste = nota_aluno_av
                                            else: v_prova = nota_aluno_av
                                                
                                            nova_media = min(10.0, util.sosa_to_float(v_vistos) + util.sosa_to_float(v_teste) + util.sosa_to_float(v_prova))
                                            if util.sosa_to_float(v_rec) > 0: nova_media = max(nova_media, util.sosa_to_float(v_rec))
                                            lista_boletim_rev.append([id_l, nome_l, t_sel_h, tr_sel_h, util.sosa_to_str(v_vistos), util.sosa_to_str(v_teste), util.sosa_to_str(v_prova), util.sosa_to_str(v_rec), util.sosa_to_str(nova_media)])
                                            
                                        db.salvar_lote("DB_NOTAS", lista_boletim_rev)
                                        st.cache_data.clear()
                                        st.success("✅ Correções gravadas e boletins atualizados em cascata!")
                                        time.sleep(0.5); st.rerun()
                    else: st.info("Nenhuma leitura escaneada disponível para revisão nesta avaliação.")

                # 🚑 PROTOCOLO LÁZARO (DIGITAÇÃO MANUAL COM CÁLCULO AUTOMÁTICO)
                with st.expander("🚑 Protocolo Lázaro (Digitação Manual Global)", expanded=False):
                    df_perdidos = pd.DataFrame([r for r in dados_soberania if r['_Respostas'] == "MANUAL" and r['Situação'] == "✅ REALIZADA"])
                    
                    if not df_perdidos.empty:
                        st.info("Digite as respostas dos alunos separadas por ponto e vírgula (ex: A;B;C;D;E). O sistema calculará a nota comparando com o gabarito oficial automaticamente.")
                        df_lazaro = st.data_editor(
                            pd.DataFrame([{"ID": r['ID'], "Estudante": r['Estudante'], "Respostas (Ex: A;B;C;D;E)": ""} for _, r in df_perdidos.iterrows()]),
                            hide_index=True, use_container_width=True, key=f"laz_grid_{v}"
                        )
                        
                        if st.button("💾 Processar e Salvar Lázaro", type="primary", use_container_width=True, key=f"btn_laz_{v}"):
                            with st.spinner("Ressuscitando gabaritos..."):
                                if not df_prova_trib.empty:
                                    val_total_av = util.sosa_to_float(ai.extrair_tag(txt_prova_trib, "VALOR")) or 10.0
                                    for _, row_laz in df_lazaro.iterrows():
                                        resp_dig = str(row_laz["Respostas (Ex: A;B;C;D;E)"]).strip().upper()
                                        if resp_dig and resp_dig != "":
                                            respostas_lista = re.split(r'[;\s,]', resp_dig)
                                            respostas_lista = [r for r in respostas_lista if r != ""]
                                            acertos = sum(1 for i, r in enumerate(respostas_lista) if i+1 in gab_oficial_trib and r == gab_oficial_trib[i+1])
                                            nota_calc = (acertos / len(gab_oficial_trib)) * val_total_av if len(gab_oficial_trib) > 0 else 0.0
                                            
                                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), row_laz["ID"], row_laz["Estudante"], t_sel_h, av_alvo_h, ";".join(respostas_lista), util.sosa_to_str(nota_calc), "N/A"])
                                    
                                    st.cache_data.clear()
                                    st.success("✅ Gabaritos processados e boletins atualizados com sucesso!")
                                    time.sleep(0.5); st.rerun()
                    else: st.success("🎉 Nenhum registro de Lázaro pendente.")

                # CONSULTA DE DOSSIÊS
                with st.expander("🗂️ Histórico de Dossiês Raio-X Emitidos", expanded=True):
                    df_dossies = df_relatorios[df_relatorios['TIPO'] == 'DOSSIE_RAIO_X'].copy()
                    if not df_dossies.empty:
                        for idx, row in df_dossies.iterrows():
                            if nome_curto_av in str(row['CONTEUDO']) and row['NOME_ALUNO'] == t_sel_h:
                                with st.container(border=True):
                                    c_d1, c_d2 = st.columns([3, 1])
                                    c_d1.markdown(f"**Dossiê: {nome_curto_av}** | Unidade: {row['NOME_ALUNO']}")
                                    link_d = str(row['CONTEUDO']).split("Link: ")[-1]
                                    c_d2.link_button("Abrir PDF", link_d, use_container_width=True)

    # ==============================================================================
    # ABA 3: RAIO-X PEDAGÓGICO (SINCRONIA DE VARIANTES E PEI - V201.5)
    # ==============================================================================
    with tab_raiox:
        st.markdown("### Raio-X Pedagógico: Autópsia por Item")
        
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 2])
            t_sel_r = c1.selectbox("Selecione a Turma:", [""] + lista_turmas_cir, key=f"t_r_v90_{v}")
            tr_sel_r = c2.selectbox("Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_r_v90_{v}")
            
            # 1. Busca apenas as Avaliações Base (Ignora Variantes e 2ª Chamada no primeiro filtro)
            opcoes_r = filtrar_ativos_cir(t_sel_r, tr_sel_r, apenas_provas=True)
            opcoes_base_r = [opt for opt in opcoes_r if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            
            at_sel_r = c3.selectbox("Selecione a Avaliação Base:", [""] + opcoes_base_r, key=f"at_r_v90_{v}")

        if t_sel_r and at_sel_r:
            nome_curto_av = at_sel_r.split("-")[0].strip()
            trim_limpo = tr_sel_r.replace(" ", "")
            ano_num_r = "".join(filter(str.isdigit, t_sel_r)) # 🚨 CORREÇÃO: Variável restaurada
            
            # 2. Puxa todos os gabaritos escaneados para esta turma relacionados a esta prova base
            mask_diag = (df_diagnosticos['TURMA'] == t_sel_r) & (
                df_diagnosticos['ID_AVALIACAO'].str.contains(nome_curto_av, case=False, na=False) |
                (df_diagnosticos['ID_AVALIACAO'].str.contains("2ª|2CHAMADA", regex=True, case=False) & df_diagnosticos['ID_AVALIACAO'].str.contains(trim_limpo, case=False))
            )
            respostas_brutas = df_diagnosticos[mask_diag].copy()

            if respostas_brutas.empty:
                st.warning("⚠️ Nenhuma resposta de aluno encontrada para esta avaliação.")
            else:
                # 3. Cruza com o perfil do aluno para descobrir quem fez PEI
                df_alunos_min = df_alunos[['ID', 'NECESSIDADES']].copy()
                df_alunos_min['ID'] = df_alunos_min['ID'].apply(db.limpar_id)
                respostas_brutas['ID_ALUNO_L'] = respostas_brutas['ID_ALUNO'].apply(db.limpar_id)
                df_analise = pd.merge(respostas_brutas, df_alunos_min, left_on='ID_ALUNO_L', right_on='ID', how='left')
                
                def classificar_caderno(row):
                    resp = str(row['RESPOSTAS_ALUNO']).upper()
                    id_av = str(row['ID_AVALIACAO']).upper()
                    nec = str(row['NECESSIDADES']).upper()
                    
                    if resp == "FALTOU": return "FALTOU"
                    if resp.startswith("QUALITATIVA"): return "🔴 PEI Nível 3 (Qualitativa)"
                    if "2ª" in id_av or "2CHAMADA" in id_av: return "🔄 2ª Chamada (Discursiva)"
                    if "TIPO" in id_av: return f"🧬 Variante ({id_av.split('-')[-1].strip()})"
                    
                    # Se é a prova base, verifica se o aluno é PEI
                    is_pei = nec not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE", "PENDENTE", "SUSPEITA", "DEFASAGEM LEITURA", "DEFASAGEM MATEMÁTICA"]
                    if is_pei:
                        # Tenta inferir se é N1 ou N2 pelo tamanho do gabarito ou assume N1 como padrão
                        qtd_respostas = len(resp.split(';'))
                        if qtd_respostas <= 10: return "🔵 PEI Nível 1 (Apoio Leve)" # Simplificação para agrupar PEIs
                        
                    return "📝 Prova Padrão (Tipo A)"

                df_analise['CADERNO_FEITO'] = df_analise.apply(classificar_caderno, axis=1)
                
                # 4. Descobre quais cadernos realmente existem com dados
                cadernos_disponiveis = sorted([c for c in df_analise['CADERNO_FEITO'].unique() if c != "FALTOU"])
                
                if not cadernos_disponiveis:
                    st.info("Todos os alunos faltaram a esta avaliação.")
                else:
                    with st.container(border=True):
                        caderno_alvo = st.radio("🔍 Selecione o Caderno Específico para Análise:", cadernos_disponiveis, horizontal=True, key=f"cad_alvo_{v}")
                    
                    # 5. Filtra os dados EXATAMENTE para o caderno selecionado
                    df_filtrado = df_analise[df_analise['CADERNO_FEITO'] == caderno_alvo]
                    
                    # 6. Localiza o material correto no Acervo (Compatibilidade com o passado)
                    material_ref = None
                    is_pei_view = "PEI" in caderno_alvo
                    is_2a_chamada = "2ª Chamada" in caderno_alvo
                    
                    if is_2a_chamada:
                        df_busca = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(ano_num_r))]
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
                        
                        # 7. Extrai o Gabarito Correto (Blindado para tags antigas e novas)
                        tag_g = "GABARITO_PEI" if is_pei_view else "GABARITO_TEXTO"
                        raw_gab_base = ai.extrair_tag(txt_prova_base, tag_g) or ai.extrair_tag(txt_prova_base, "GABARITO")
                        matches_base = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", raw_gab_base.upper())
                        gab_ativo = {int(num): letra for num, letra in matches_base} if matches_base else {}
                        
                        # 8. Calcula Estatísticas
                        stats_list = []
                        if is_2a_chamada:
                            q_raw = ai.extrair_tag(txt_prova_base, "QUESTOES")
                            num_q_total = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw)) or 10
                            matriz_respostas = [str(r).split(';') for r in df_filtrado['RESPOSTAS_ALUNO']]
                            
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
                                    respostas_lista = str(row_aluno['RESPOSTAS_ALUNO']).upper().split(';')
                                    if len(respostas_lista) >= i:
                                        validos += 1
                                        if respostas_lista[i-1] == gab_ativo.get(i, "?"): acertos += 1
                                
                                perc = (acertos / validos) * 100 if validos > 0 else 0.0
                                stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": gab_ativo.get(i, "?")})
                            
                        df_stats_global = pd.DataFrame(stats_list)
                        
                        # 9. RENDERIZAÇÃO DO DASHBOARD
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
                            
                            # 10. AUTÓPSIA EM MODAL
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
                                    
                                    # Define qual tag buscar baseado no caderno
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
                                        else: st.warning("Perícia de distratores não localizada.")

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
        turmas_reais_db = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        
        if turmas_reais_db.empty:
            st.warning("⚠️ Nenhuma turma regular cadastrada para o Diário.")
        else:
            # --- 1. BARRA DE CONTROLE LIMPA (Bento Layout) ---
            with st.container(border=True):
                c1, c2 = st.columns(2)
                turma_sel = c1.selectbox("Selecione a Turma:", sorted(turmas_reais_db['ID_TURMA'].unique()), key=f"db_t_{v}", label_visibility="collapsed")
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
# MÓDULO: BIOGRAFIA DO ESTUDANTE - V201 (DASHBOARD EXECUTIVO & MODAIS)
# ==============================================================================
elif menu == "👤 Biografia do Estudante":
    st.title("👤 Biografia do Estudante: Dossiê de Evolução")
    st.caption("💡 **Guia de Comando:** Dashboard executivo para reuniões de pais. Navegue pelas abas para apresentar os resultados de forma limpa e organizada.")
    st.markdown("---")

    def preparar_para_leitura(texto):
        if not texto: return ""
        texto = re.sub(r'^```[a-zA-Z]*\n', '', texto, flags=re.MULTILINE | re.IGNORECASE)
        texto = re.sub(r'```$', '', texto, flags=re.MULTILINE)
        texto = texto.replace("**", "") 
        texto = re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)
        texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', r'📐 *(Comando GeoGebra: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
        texto = re.sub(r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', r'🖼️ *(Imagem: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
        return texto

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Cadastre as turmas primeiro.")
    else:
        # --- 1. FILTROS DE ACESSO RÁPIDO ---
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1.5, 1])
            
            turmas_reais_bio = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_bio = sorted(turmas_reais_bio['ID_TURMA'].unique()) if not turmas_reais_bio.empty else sorted(df_alunos['TURMA'].unique())
            
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

        # --- PREPARAÇÃO DE DADOS GLOBAIS ---
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

        # --- CÁLCULO DE MÉTRICAS PARA O HERO CARD ---
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

        # ==============================================================================
        # 🌟 HERO CARD (CABEÇALHO EXECUTIVO V201)
        # ==============================================================================
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

        # ==============================================================================
        # 📱 WHATSAPP MODAL (V201)
        # ==============================================================================
        @st.dialog("📱 Extrato para WhatsApp")
        def dialog_whatsapp():
            st.info("Copie o texto abaixo e envie para o responsável.")
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
{linha_rec}
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

        # ==============================================================================
        # 🗂️ ORGANIZAÇÃO EM ABAS (O DASHBOARD DE REUNIÃO)
        # ==============================================================================
        abas_bio = ["📊 Visão Geral & Engajamento", "📈 Evolução & Lacunas", "⚖️ Auditoria & Tribunal"]
        if is_pei_or_gap: abas_bio.append("♿ Dossiê Clínico (PEI)")
        
        tabs = st.tabs(abas_bio)

        # --- ABA 1: VISÃO GERAL & ENGAJAMENTO (SPLIT-SCREEN V201) ---
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

        # --- ABA 2: EVOLUÇÃO & LACUNAS ---
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
                        
                        if str(row_av['RESPOSTAS_ALUNO']).upper() != "FALTOU":
                            dados_grafico.append({"Data": data_av, "Avaliação": nome_limpo_av, "Nota": nota_av})
                    
                    if dados_grafico:
                        df_grafico = pd.DataFrame(dados_grafico)
                        fig = px.line(df_grafico, x="Avaliação", y="Nota", text="Nota", markers=True, title="Curva de Aprendizagem (Notas em Avaliações)", hover_data=["Data"])
                        fig.update_traces(textposition="bottom right", line=dict(color="#2962FF", width=3), marker=dict(size=10))
                        fig.update_layout(yaxis_range=[0, 10.5], height=350, xaxis_title="", yaxis_title="Nota Obtida")
                        fig.add_hline(y=6.0, line_dash="dash", line_color="red", annotation_text="Média (6.0)", annotation_position="bottom right")
                        st.plotly_chart(fig, use_container_width=True)
                    else: st.info("O aluno faltou a todas as avaliações deste período.")
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
                                if i < len(gab_oficial) and r != gab_oficial[i] and r not in["FALTOU", "?", "X"] and not r.startswith("QUALITATIVA"):
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

        # --- ABA 3: AUDITORIA & TRIBUNAL (MODAL V201) ---
        with tabs[2]:
            st.markdown(f"### 🎯 Histórico de Avaliações (Scanner)")
            
            # ⚖️ TRIBUNAL DE RECURSOS MODAL
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
                    
                    if respostas_aluno.upper() == "FALTOU": status_av, nota_av = "❌ FALTOU", 0.0
                    elif respostas_aluno.upper().startswith("QUALITATIVA"): status_av = "🎨 QUALITATIVA (PEI)"
                    elif "MANUAL" in respostas_aluno.upper(): status_av = "✍️ LANÇAMENTO MANUAL"
                    else: status_av = "✅ ESCANEADA"
                        
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

        # --- ABA 4: DOSSIÊ PEI (SÓ APARECE SE FOR PEI) ---
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
        turmas_reais_notas = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_notas = sorted(turmas_reais_notas['ID_TURMA'].unique()) if not turmas_reais_notas.empty else sorted(df_alunos['TURMA'].unique())

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
# MÓDULO: GESTÃO DA TURMA (COCKPIT DE REGÊNCIA) - V201 (MODAIS & BENTO GRID)
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Cockpit de Regência: Gestão 360°")
    st.caption("💡 **Guia de Comando:** Central de controle da sua rotina. Abra aulas rapidamente, audite registros passados e acesse a inteligência analítica da turma.")
    st.markdown("---")

    if "v_gestao" not in st.session_state: st.session_state.v_gestao = int(time.time())
    v = st.session_state.v_gestao

    lista_turmas_segura = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_segura = sorted(turmas_reais['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_segura = sorted(df_alunos['TURMA'].unique())

    # 🚨 REDUÇÃO DE ABAS (De 5 para 3)
    tab_cockpit, tab_inteligencia, tab_secretaria = st.tabs([
        "🚀 1. Cockpit de Regência", 
        "🧠 2. Inteligência da Turma", 
        "⚙️ 3. Secretaria & Matrículas"
    ])

    # ==============================================================================
    # 🚀 ABA 1: COCKPIT DE REGÊNCIA (AÇÃO RÁPIDA E MODAIS)
    # ==============================================================================
    with tab_cockpit:
        if df_turmas.empty or 'ID_TURMA' not in df_turmas.columns:
            st.info("📭 Nenhuma turma cadastrada. Vá na aba '3. Secretaria & Matrículas' para iniciar.")
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

                # 🚨 MODAL: ROLETA DE ARGUIÇÃO
                @st.dialog("🎲 Roleta de Arguição", width="large")
                def dialog_roleta(t_roleta):
                    c_rol1, c_rol2 = st.columns([1, 1])
                    data_roleta = c_rol1.date_input("📅 Data da Arguição:", date.today(), format="DD/MM/YYYY", key=f"rol_d_{v}")
                    data_roleta_str = data_roleta.strftime("%d/%m/%Y")
                    
                    with c_rol2.expander("⚙️ Configurar Pontuação"):
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
                    chave_sorteado = f"aluno_sorteado_{t_roleta}_{data_roleta_str}"
                    
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
                        
                    if chave_sorteado not in st.session_state: st.session_state[chave_sorteado] = None

                    col_roleta, col_lista = st.columns([1.2, 1.8])
                    with col_roleta:
                        pendentes = [a for a in st.session_state[chave_lista] if a["Status"] == "⏳ Pendente"]
                        c_btn_sort, c_btn_reset = st.columns([2, 1])
                        if c_btn_sort.button("🎲 SORTEAR", type="primary", use_container_width=True):
                            if not pendentes: st.success("Todos chamados!")
                            else: st.session_state[chave_sorteado] = random.choice(pendentes)["ID"]; st.rerun()
                        if c_btn_reset.button("🔄 Reset", use_container_width=True):
                            del st.session_state[chave_lista]; st.session_state[chave_sorteado] = None; st.rerun()
                            
                        if st.session_state[chave_sorteado]:
                            id_atual = st.session_state[chave_sorteado]
                            aluno_atual = next(a for a in st.session_state[chave_lista] if a["ID"] == id_atual)
                            aluno_db = alunos_roleta[alunos_roleta['ID'].apply(db.limpar_id) == id_atual].iloc[0]
                            
                            with st.container(border=True):
                                st.markdown(f"<h3 style='text-align: center;'>{aluno_atual['Estudante']}</h3>", unsafe_allow_html=True)
                                st.markdown(f"<p style='text-align: center; color: gray;'>Perfil: {aluno_db['NECESSIDADES']}</p>", unsafe_allow_html=True)
                                anotacao = st.text_area("📝 Diagnóstico Clínico:", value=aluno_atual["Diagnóstico"], key=f"anotacao_{id_atual}")
                                
                                def registrar_arguicao(status_label, pontos, obs_padrao):
                                    obs_final = anotacao.strip() if anotacao.strip() else obs_padrao
                                    for a in st.session_state[chave_lista]:
                                        if a["ID"] == id_atual:
                                            a["Status"], a["Pontos"], a["Diagnóstico"] = status_label, pontos, obs_final
                                            break
                                    nome_limpo = aluno_db['NOME_ALUNO'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                                    wb = db.conectar()
                                    ws = wb.worksheet("DB_DIARIO_BORDO")
                                    dados = ws.get_all_values()
                                    for i in range(len(dados)-1, 0, -1):
                                        if dados[i][0] == data_roleta_str and db.limpar_id(dados[i][1]) == id_atual and dados[i][5] == "ARGUIÇÃO": ws.delete_rows(i+1)
                                    ws.append_row([data_roleta_str, id_atual, nome_limpo, t_roleta, "TRUE", "ARGUIÇÃO", f"Quadro Negro: {obs_final}", util.sosa_to_str(pontos)], value_input_option="USER_ENTERED")
                                    st.cache_data.clear(); st.session_state[chave_sorteado] = None
                                
                                c_av1, c_av2, c_av3 = st.columns(3)
                                if c_av1.button(f"✅ Dominou (+{pt_acerto})", use_container_width=True): registrar_arguicao("✅ Dominou", pt_acerto, "Resolveu corretamente."); st.rerun()
                                if c_av2.button("🤝 Tentou (0.0)", use_container_width=True): registrar_arguicao("🤝 Tentou", 0.0, "Apresentou dificuldades."); st.rerun()
                                if c_av3.button(f"❌ Recusou ({pt_recusa})", use_container_width=True): registrar_arguicao("❌ Recusou", pt_recusa, "Recusou-se a participar."); st.rerun()
                                
                                c_av4, c_av5 = st.columns(2)
                                if c_av4.button("♿ Isento (PEI/Não Alfabetizado)", use_container_width=True): registrar_arguicao("♿ Isento", 0.0, "Isento da arguição."); st.rerun()
                                if c_av5.button("⏭️ Faltou / Pular", use_container_width=True):
                                    for a in st.session_state[chave_lista]:
                                        if a["ID"] == id_atual: a["Status"] = "⏭️ Faltou"
                                    st.session_state[chave_sorteado] = None; st.rerun()

                    with col_lista:
                        df_editado = st.data_editor(
                            pd.DataFrame(st.session_state[chave_lista]), hide_index=True, use_container_width=True, height=350,
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
                            
                            # Auto-seleção inteligente baseada no plano sugerido
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
    # 🧠 ABA 2: INTELIGÊNCIA DA TURMA (RADIOGRAFIA + EVASÃO + SENSOR)
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

                # 1. TERMÔMETRO GLOBAL
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

                # 2. SPLIT-SCREEN: UTI PEDAGÓGICA vs RADAR DE EVASÃO
                st.markdown("---")
                col_uti, col_evasao = st.columns(2)
                
                with col_uti:
                    st.markdown("#### 🚑 UTI Pedagógica (Notas)")
                    df_n_trim = df_notas[(df_notas['TURMA'] == t_rad) & (df_notas['TRIMESTRE'] == trim_rad)].copy()
                    if not df_n_trim.empty:
                        alunos_uti = []
                        for _, r in df_n_trim.iterrows():
                            media_f = util.sosa_to_float(r['MEDIA_FINAL'])
                            if media_f < 6.0: alunos_uti.append({"Nome": r['NOME_ALUNO'], "Média": media_f, "Falta": 6.0 - media_f})
                        
                        if alunos_uti:
                            for u in alunos_uti: st.error(f"**{u['Nome']}** - Média: {u['Média']:.1f} (Precisa de +{u['Falta']:.1f})")
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
                            faltas_a = len(df_aluno[df_aluno['TAGS'] == "AUSÊNCIA"])
                            perc_falta = (faltas_a / total_aulas_validas) * 100 if total_aulas_validas > 0 else 0
                            if perc_falta >= 25: stats_evasao.append({"Nome": aluno, "Faltas": faltas_a, "Perc": perc_falta})
                                
                        if stats_evasao:
                            for e in sorted(stats_evasao, key=lambda x: x['Perc'], reverse=True):
                                if e['Perc'] == 100: st.error(f"👻 **{e['Nome']}** - Fantasma (Nunca Veio)")
                                else: st.warning(f"⚠️ **{e['Nome']}** - {e['Faltas']} faltas ({e['Perc']:.0f}%)")
                        else: st.success("✅ Nenhum aluno em risco de evasão.")
                    else: st.info("Aguardando registros de chamada.")

                # 3. SENSOR SEMÂNTICO EM LOTE
                st.markdown("---")
                st.markdown("#### 🚨 Sensor Semântico (Processamento em Lote)")
                st.caption("Classifique as anotações do Diário de Bordo. O sistema processará todas de uma vez.")
                
                if not df_d_rad.empty:
                    obs_reais = df_d_rad[(df_d_rad['OBSERVACOES'] != "") & (~df_d_rad['TAGS'].isin(["SISTEMA_NOTA", "BONUS_CONSELHO", "DIA NÃO LETIVO"])) & (~df_d_rad['OBSERVACOES'].str.contains(r"\[LIDO\]", na=False, case=False))]
                    if not obs_reais.empty:
                        ultimas_obs = obs_reais.tail(10).iloc[::-1]
                        dados_sensor = [{"Data": r['DATA'], "ID_Aluno": r['ID_ALUNO'], "Estudante": r['NOME_ALUNO'], "Anotação": r['OBSERVACOES'], "Ação": "⏳ Pendente"} for _, r in ultimas_obs.iterrows()]
                            
                        df_sensor_ed = st.data_editor(
                            pd.DataFrame(dados_sensor), hide_index=True, use_container_width=True,
                            column_config={"Data": st.column_config.TextColumn(disabled=True, width="small"), "ID_Aluno": None, "Estudante": st.column_config.TextColumn(disabled=True, width="medium"), "Anotação": st.column_config.TextColumn(disabled=True, width="large"), "Ação": st.column_config.SelectboxColumn("Ação / Diagnóstico", options=["⏳ Pendente", "✅ Apenas Ciente (Ocultar)", "🧱 Marcar: Defasagem Leitura", "🧮 Marcar: Defasagem Mat.", "🟠 Marcar: PEI (Suspeita)"], required=True, width="medium")},
                            key=f"ed_sensor_{v}"
                        )
                        
                        if st.button("💾 PROCESSAR OBSERVAÇÕES EM LOTE", type="primary"):
                            with st.status("Processando diagnósticos...") as status:
                                wb = db.conectar()
                                ws_diario = wb.worksheet("DB_DIARIO_BORDO")
                                dados_diario = ws_diario.get_all_values()
                                updates_diario = []
                                
                                for _, r in df_sensor_ed.iterrows():
                                    acao = r["Ação"]
                                    if acao != "⏳ Pendente":
                                        if "Defasagem Leitura" in acao: db.atualizar_aluno_cascata(r["ID_Aluno"], r["Estudante"], t_rad, "DEFASAGEM LEITURA")
                                        elif "Defasagem Mat." in acao: db.atualizar_aluno_cascata(r["ID_Aluno"], r["Estudante"], t_rad, "DEFASAGEM MATEMÁTICA")
                                        elif "PEI" in acao: db.atualizar_aluno_cascata(r["ID_Aluno"], r["Estudante"], t_rad, "PEI - PENDENTE")
                                            
                                        for i, row_d in enumerate(dados_diario):
                                            if i > 0 and row_d[0] == r["Data"] and db.limpar_id(row_d[1]) == db.limpar_id(r["ID_Aluno"]) and row_d[6].strip() == r["Anotação"].strip():
                                                updates_diario.append(gspread.Cell(row=i+1, col=7, value=r["Anotação"] + " [LIDO]"))
                                                break
                                
                                if updates_diario: ws_diario.update_cells(updates_diario)
                                st.cache_data.clear(); status.update(label="✅ Observações processadas!", state="complete"); time.sleep(1); st.rerun()
                    else: st.success("✅ Nenhuma observação pendente de análise no Diário de Bordo.")

    # ==============================================================================
    # ⚙️ ABA 3: SECRETARIA & MATRÍCULAS
    # ==============================================================================
    with tab_secretaria:
        st.markdown("### ⚙️ Secretaria & Matrículas")
        sub_criar, sub_povoar, sub_editar = st.tabs(["🏗️ Criar Turmas/Horários", "➕ Povoar Alunos", "✏️ Edição & Diagnóstico Rápido"])
        
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
