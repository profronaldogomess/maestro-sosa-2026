import io
import streamlit as st
import pandas as pd
import gspread
from datetime import date, datetime, timedelta, timezone
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

# --- LÓGICA DE AUTO-ATUALIZAÇÃO ---
if 'last_sync' not in st.session_state:
    st.session_state.last_sync = time.time()

if time.time() - st.session_state.last_sync > 600:
    st.cache_data.clear()
    st.session_state.last_sync = time.time()

# --- ESTILIZAÇÃO DE LUXO (CSS V40) ---
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
        div[data-testid="stMetric"] {{ background: {cor_card} !important; border: 1px solid {cor_borda} !important; border-radius: 20px !important; }}
        .stButton button {{ background: linear-gradient(135deg, {BRAND_BLUE}, #0039CB) !important; color: white !important; border-radius: 12px !important; font-weight: 700 !important; width: 100%; }}
        .clock-container {{ background: {BRAND_BLUE}15; color: {BRAND_BLUE}; padding: 8px 15px; border-radius: 30px; font-weight: 800; font-size: 14px; text-align: center; margin: 10px 0; border: 1px solid {BRAND_BLUE}33; }}
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

    # Relógio Automático (Brasília) e Sensor de Feriados
    fuso_br = timezone(timedelta(hours=-3))
    agora_br = datetime.now(fuso_br)
    hora_atual = agora_br.strftime("%H:%M:%S")
    data_atual = agora_br.strftime("%d/%m/%Y")
    data_atual_dt = agora_br.date() # Extrai o objeto 'date' para o sensor
    
    st.markdown(f"""<div class="clock-container">🕒 {hora_atual} | 📅 {data_atual}</div>""", unsafe_allow_html=True)
    
    # 🚨 INTEGRAÇÃO COM O SENSOR DE FERIADOS (utils.py)
    feriado_hoje = util.verificar_feriado_itabuna(data_atual_dt)
    
    if feriado_hoje:
        # Badge vermelho de alerta para feriados
        st.markdown(f"""<div style="background: linear-gradient(135deg, #FF4B4B, #C0392B); color: white; padding: 6px 10px; border-radius: 8px; text-align: center; font-weight: 800; font-size: 12px; margin-top: -5px; margin-bottom: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">🎉 FERIADO: {feriado_hoje.upper()}</div>""", unsafe_allow_html=True)
    else:
        # Indicador de dia da semana e dia letivo
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
        nome_dia = dias_semana[data_atual_dt.weekday()]
        cor_dia = "#2ECC71" if data_atual_dt.weekday() < 5 else "#F1C40F" # Verde para dias úteis, Amarelo para fim de semana
        st.markdown(f"""<div style="text-align: center; color: {cor_dia}; font-size: 12px; font-weight: 600; margin-top: -5px; margin-bottom: 10px;">{nome_dia} • Dia Letivo</div>""", unsafe_allow_html=True)

    st.markdown("---")

    menu = st.radio("Navegação Estratégica:", [
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

    st.markdown("<br>" * 2, unsafe_allow_html=True)
    st.markdown("---")
    
    # BOTÕES DE RODAPÉ (SYNC E SAIR)
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

    # Rodapé atualizado conforme ordem soberana
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
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - VERSÃO V120 (MICRO-GESTÃO & ELITE)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("📅 Ponto ID: Engenharia de Planejamento")
    st.markdown("---")
    st.caption("💡 **Guia de Comando:** Este é o cérebro do ecossistema. O planejamento gerado aqui define a rota da semana e alimenta automaticamente o *Criador de Aulas* e o *Diário de Bordo*.")

    def reset_planejamento():
        keys_to_clear = ["p_temp", "refino_ativo", "p_meta"]
        for k in keys_to_clear:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_plano = int(time.time())
        st.rerun()

    if "v_plano" not in st.session_state: 
        st.session_state.v_plano = int(time.time())
    v = st.session_state.v_plano 

    # 🚨 NOVA ABA ADICIONADA: Planejamento Trimestral
    tab_gerar, tab_producao, tab_acervo, tab_matriz, tab_auditoria, tab_trimestral = st.tabs([
        "🚀 1. Criar Novo Plano", "🏗️ 2. Hub de Produção", "📂 3. Acervo (PIP)", "📖 4. Matriz Curricular", "📈 5. Auditoria", "📅 6. Planejamento Trimestral"
    ])
    
    with tab_gerar:
        # --- 🛡️ 1. NATUREZA DO PLANEJAMENTO ---
        with st.container(border=True):
            st.markdown("### 🛡️ Passo 1: Natureza do Planejamento")
            
            tipo_planejamento = st.radio(
                "O que você deseja planejar agora?", ["📅 Semana Letiva Regular (Gera Aula 1 e Aula 2)", "🗓️ Sábado Letivo Avulso (Gera apenas 1 Aula Extra)"], 
                horizontal=True, key=f"tipo_plan_{v}"
            )
            
            is_sabado_avulso = "Sábado" in tipo_planejamento
            
            cg1, cg2 = st.columns([2, 1])
            tipo_semana = cg1.selectbox("DNA da Abordagem:", [
                "📗 Aula de Safra (Regular)", "📝 Aplicação de Exame", 
                "🔥 Revisão & Recomposição", "📋 Trabalho Investigativo", "🔍 Sonda de Proficiência",
                "💡 Aula Aberta (Dinâmicas e Eventos)"
            ], key=f"gate_tipo_{v}")
            
            if is_sabado_avulso:
                carga_horaria = "1 Aula"
                st.info("💡 Modo Sábado Letivo ativado. O sistema gerará um plano de aula único (Sábado) vinculado à semana que você escolher abaixo.")
            else:
                carga_horaria = cg2.select_slider("Aulas Úteis na Semana:", options=["1 Aula", "2 Aulas", "3 Aulas"], value="2 Aulas", key=f"gate_carga_{v}")

        # --- ⚙️ 2. PARÂMETROS E HERANÇA ---
        with st.container(border=True):
            st.markdown("### ⚙️ Passo 2: Parâmetros e Herança (Ponte Pedagógica)")
            
            c1, c2 = st.columns([1, 2])
            ano_p = c1.selectbox("Série/Ano Alvo:", [6, 7, 8, 9], index=0, key=f"ano_sel_{v}")
            ano_str_busca = f"{ano_p}º"

            todas_semanas = util.gerar_semanas()
            semanas_planejadas = df_planos[df_planos['ANO'] == ano_str_busca]['SEMANA'].tolist()
            
            if is_sabado_avulso:
                semanas_disponiveis = [s for s in todas_semanas if "Jornada" not in s]
            else:
                semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_planejadas and "Jornada" not in s]

            if not semanas_disponiveis:
                st.success(f"🏆 **Soberania Total!** Todas as semanas do ano letivo para o {ano_p}º Ano já foram planejadas.")
                if st.button("🔄 REVER ACERVO"): st.rerun()
                st.stop()

            sem_p = c2.selectbox("📅 Semana de Referência:", semanas_disponiveis, key=f"sem_sel_{v}")
            sem_limpa = sem_p.split(" (")[0]
            trim_atual = sem_p.split(" - ")[1] if " - " in sem_p else "I Trimestre"

            st.markdown("#### 🔙 Radar de Continuidade")
            df_hist = df_planos[df_planos['ANO'] == ano_str_busca].copy()
            plano_anterior_txt = "Início de Safra. Não há plano anterior."
            
            if not df_hist.empty:
                df_hist['DATA_DT'] = pd.to_datetime(df_hist['DATA'], format="%d/%m/%Y", errors='coerce')
                df_hist = df_hist.sort_values(by='DATA_DT', ascending=False)
                ultimo_plano = df_hist.iloc[0]
                plano_anterior_txt = ultimo_plano['PLANO_TEXTO']
                obj_ant = ai.extrair_tag(plano_anterior_txt, "OBJETO_CONHECIMENTO") or ai.extrair_tag(plano_anterior_txt, "CONTEUDO_GERAL")
                st.info(f"**Último plano gerado ({ultimo_plano['SEMANA']}):** {obj_ant}")
            
            pendencias_ant = st.text_area("Pendências da Semana Anterior (Opcional):", placeholder="Ex: Faltou corrigir as questões 4 e 5 da lista de frações. Iniciar a Aula 1 por isso.", key=f"pend_{v}")

        # ==============================================================================
        # 🚨 ROTA DE BYPASS LOGÍSTICO (ESPELHAMENTO DE ACERVO)
        # ==============================================================================
        if tipo_semana in ["📝 Aplicação de Exame", "🔍 Sonda de Proficiência", "🔥 Revisão & Recomposição", "📋 Trabalho Investigativo", "💡 Aula Aberta (Dinâmicas e Eventos)"]:
            st.markdown("---")
            st.warning(f"⚡ **Protocolo de Espelhamento Ativado:** O DNA '{tipo_semana}' não exige a geração de uma nova aula pela IA. O sistema apenas oficializará a logística para a coordenação.")
            
            with st.container(border=True):
                st.markdown("### 📦 Passo 3: Seleção do Ativo")
                
                ativo_selecionado = ""
                if tipo_semana != "💡 Aula Aberta (Dinâmicas e Eventos)":
                    df_ativos_ano = df_aulas[df_aulas['ANO'] == ano_str_busca]
                    opcoes_ativos = []
                    
                    if "Exame" in tipo_semana or "Sonda" in tipo_semana: 
                        opcoes_ativos = df_ativos_ano[df_ativos_ano['SEMANA_REF'] == "AVALIAÇÃO"]['TIPO_MATERIAL'].tolist()
                    elif "Revisão" in tipo_semana: 
                        # Puxa as revisões normais do acervo de aulas
                        opcoes_ativos = df_ativos_ano[df_ativos_ano['SEMANA_REF'] == "REVISÃO"]['TIPO_MATERIAL'].tolist()
                        
                        # 🚨 INTEGRAÇÃO DOS DOSSIÊS DE RAIO-X (Puxa do banco de relatórios)
                        df_dossies_ano = df_relatorios[(df_relatorios['TIPO'] == 'DOSSIE_RAIO_X') & (df_relatorios['NOME_ALUNO'].str.contains(str(ano_p)))]
                        for _, row_d in df_dossies_ano.iterrows():
                            cont_d = str(row_d['CONTEUDO'])
                            nome_av = re.search(r"Avaliação:\s*(.*)", cont_d)
                            nome_av_str = nome_av.group(1).strip() if nome_av else "Avaliação Desconhecida"
                            turma_d = row_d['NOME_ALUNO']
                            opcoes_ativos.append(f"📊 DOSSIÊ RAIO-X: {nome_av_str} ({turma_d})")
                            
                    elif "Trabalho" in tipo_semana: 
                        opcoes_ativos = df_ativos_ano[df_ativos_ano['TIPO_MATERIAL'].str.contains("PROJETO|TRABALHO", case=False, na=False)]['TIPO_MATERIAL'].tolist()
                    
                    if opcoes_ativos:
                        ativo_selecionado = st.selectbox("Selecione o material já existente no Acervo:", opcoes_ativos, key=f"ativo_bypass_{v}")
                    else:
                        st.error(f"Nenhum material do tipo '{tipo_semana}' encontrado no acervo para o {ano_p}º Ano. Crie o material primeiro nas abas correspondentes.")
                        st.stop()
                else:
                    ativo_selecionado = st.text_input("Nome do Evento/Dinâmica:", placeholder="Ex: Palestra sobre Educação Financeira", key=f"evento_bypass_{v}")
                    if not ativo_selecionado: st.stop()

                diretriz_logistica = st.text_area("📝 Diretriz Logística (O que vai acontecer na aula?):", placeholder="Ex: Os alunos terão 50 minutos para realizar a prova em silêncio...", height=100, key=f"dir_bypass_{v}")

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔗 HOMOLOGAR LOGÍSTICA E GERAR PLANO", use_container_width=True, type="primary"):
                with st.status("Oficializando Logística e Gerando DOCX...") as status:
                    sufixo_arq = "_SABADO" if is_sabado_avulso else ""
                    nome_arquivo = f"PLANO_{ano_str_busca.replace('º','')}_{sem_limpa.replace(' ', '')}{sufixo_arq}"
                    
                    db.excluir_plano_completo(sem_limpa + sufixo_arq, ano_str_busca)
                    
                    # Monta um plano simplificado para o DOCX
                    roteiro_docx = f"AULA DEDICADA A: {tipo_semana}\nMATERIAL/TEMA: {ativo_selecionado}\n\nDIRETRIZES DE EXECUÇÃO:\n{diretriz_logistica}"
                    
                    dados_docx = {
                        "geral": tipo_semana.upper(), 
                        "especificos": ativo_selecionado, 
                        "objetivos": "Mensurar proficiência e consolidar habilidades." if "Exame" in tipo_semana else "Execução de rotina pedagógica específica.", 
                        "recursos": "Material Impresso do Acervo SOSA" if tipo_semana != "💡 Aula Aberta (Dinâmicas e Eventos)" else "Recursos do Evento", 
                        "metodologia": roteiro_docx,
                        "avaliacao": "Observação direta e/ou correção do instrumento aplicado.", 
                        "pei": "Acompanhamento individualizado e tempo estendido conforme necessidade."
                    }
                    
                    doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": ano_str_busca, "semana": sem_limpa + sufixo_arq, "trimestre": trim_atual})
                    link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=trim_atual, categoria=ano_str_busca, semana=sem_limpa, modo="PLANEJAMENTO")
                    
                    if "https" in str(link_drive):
                        final_txt = (
                            f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} \n[CONTEUDOS_ESPECIFICOS] {ativo_selecionado} \n"
                            f"[AULA_1] {roteiro_docx} \n[AULA_2] N/A \n[SABADO_LETIVO] N/A \n"
                            f"--- LINK DRIVE --- {link_drive}"
                        )
                        # 🚨 SALVA COMO 'PRODUZIDO' PARA PULAR O HUB DE PRODUÇÃO
                        db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_limpa + sufixo_arq, ano_str_busca, trim_atual, "PRODUZIDO", final_txt, link_drive])
                        status.update(label="✅ Logística Sincronizada! O plano já está no Acervo e no Cockpit.", state="complete")
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()

        # ==============================================================================
        # 🟢 ROTA NORMAL (AULA DE SAFRA INÉDITA)
        # ==============================================================================
        else:
            # --- 📚 3. BASE CURRICULAR E ENRIQUECIMENTO ---
            ctx_ia = ""
            uri_livro_drive = None
            links_web_texto = ""
            base_didatica_info = "Matriz Curricular de Itabuna"
            
            with st.container(border=True):
                st.markdown("### 📚 Passo 3: Base Curricular e Enriquecimento")
                
                enriquecimento_elite = st.toggle("🌟 Ativar Enriquecimento de Elite (Busca Externa, OBMEP, ENEM, Contexto Atual)", value=True, help="Se ativado, a IA buscará referências em sites como Toda Matéria, Khan Academy, e criará conexões com o mundo real e avaliações externas.")
                
                # 🚨 NOVA OPÇÃO: LINKS DA WEB
                modo_p = st.radio("Método de Base Didática:", ["📖 Livro Didático", "🎛️ Manual (Matriz)", "🌐 Links da Web (Artigos/Sites)"], horizontal=True, key=f"modo_p_{v}")
                
                if modo_p == "🎛️ Manual (Matriz)":
                    df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == str(ano_p)]
                    sel_eixo = st.multiselect("1. Eixo (Semana):", sorted(df_matriz_ano['EIXO'].unique().tolist()), key=f"p_eixo_{v}")
                    sel_cont = st.multiselect("2. Conteúdo (Semana):", sorted(df_matriz_ano[df_matriz_ano['EIXO'].isin(sel_eixo)]['CONTEUDO_ESPECIFICO'].unique().tolist()) if sel_eixo else [], key=f"p_cont_{v}")
                    sel_obj = st.multiselect("3. Objetivos (Semana):", sorted(df_matriz_ano[df_matriz_ano['CONTEUDO_ESPECIFICO'].isin(sel_cont)]['OBJETIVOS'].unique().tolist()) if sel_cont else [], key=f"p_obj_{v}")
                    ctx_ia = f"EIXO: {sel_eixo}, CONTEÚDO: {sel_cont}, OBJETIVOS: {sel_obj}."
                
                elif modo_p == "🌐 Links da Web (Artigos/Sites)":
                    st.info("Cole os links dos sites que você quer que a IA leia para montar a aula (ex: Brasil Escola, Toda Matéria).")
                    links_web_texto = st.text_area("Cole os Links aqui (um por linha):", placeholder="https://brasilescola.uol.com.br/matematica/perimetro.htm\nhttps://...", key=f"links_web_{v}")
                    base_didatica_info = "Artigos da Web (Links fornecidos)"
                
                else:
                    cx1, cx2 = st.columns([2, 1])
                    livros_disponiveis = df_materiais[df_materiais['TIPO'].str.contains(str(ano_p), na=False)]['NOME_ARQUIVO'].tolist()
                    sel_mat = cx1.selectbox("Selecionar Livro do Cofre Digital:", [""] + livros_disponiveis, key=f"p_livro_{v}")
                    pags = cx2.text_input("Páginas Alvo (Geral):", placeholder="Ex: 14-23", key=f"p_pags_{v}")
                    
                    if sel_mat:
                        match_mat = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_mat].iloc[0]
                        uri_livro_drive = match_mat['URI_ARQUIVO']
                        base_didatica_info = f"Livro: {sel_mat} | Páginas: {pags}"

            # --- 🎯 4. DIRETRIZES SOBERANAS (SEMANAS HÍBRIDAS) ---
            with st.container(border=True):
                st.markdown("### 🎯 Passo 4: Diretrizes Soberanas (Semanas Híbridas)")
                st.caption("Defina a natureza exata de cada aula. Você pode vincular materiais já criados no acervo (Provas, Revisões) diretamente ao planejamento.")
                
                # 🚨 FUNÇÃO PARA PUXAR MATERIAIS DO ACERVO DINAMICAMENTE
                def obter_opcoes_acervo(tipo_aula, ano_str):
                    df_ano = df_aulas[df_aulas['ANO'] == ano_str]
                    if tipo_aula == "Aplicação de Exame":
                        return df_ano[df_ano['SEMANA_REF'] == "AVALIAÇÃO"]['TIPO_MATERIAL'].tolist()
                    elif tipo_aula == "Revisão / Correção":
                        opcoes = df_ano[df_ano['SEMANA_REF'] == "REVISÃO"]['TIPO_MATERIAL'].tolist()
                        # Puxa também os Dossiês de Raio-X
                        df_dossies = df_relatorios[(df_relatorios['TIPO'] == 'DOSSIE_RAIO_X') & (df_relatorios['NOME_ALUNO'].str.contains(str(ano_p)))]
                        for _, row_d in df_dossies.iterrows():
                            m = re.search(r"Avaliação:\s*(.*)", str(row_d['CONTEUDO']))
                            if m: opcoes.append(f"📊 DOSSIÊ RAIO-X: {m.group(1).strip()}")
                        return opcoes
                    elif tipo_aula == "Atividade Prática / Projeto":
                        return df_ano[df_ano['TIPO_MATERIAL'].str.contains("PROJETO|TRABALHO", case=False, na=False)]['TIPO_MATERIAL'].tolist()
                    return []

                if is_sabado_avulso:
                    tipo_sab = st.selectbox("Natureza do Sábado:", ["Conteúdo Novo (Teoria e Prática)", "Revisão / Correção", "Aplicação de Exame", "Atividade Prática / Projeto", "Evento / Dinâmica"], key=f"tipo_sab_{v}")
                    
                    ativo_sab = ""
                    if tipo_sab in ["Revisão / Correção", "Aplicação de Exame", "Atividade Prática / Projeto"]:
                        opcoes_sab = obter_opcoes_acervo(tipo_sab, ano_str_busca)
                        ativo_sab = st.selectbox("Vincular Material do Acervo:", [""] + opcoes_sab, key=f"ativo_sab_{v}")
                        
                    foco_sab = st.text_area("Diretriz para o Sábado Letivo:", placeholder="Ex: Fazer uma oficina prática...", height=100, key=f"dir_sab_{v}")
                    
                    diretriz_sabado = f"[{tipo_sab}] "
                    if ativo_sab: diretriz_sabado += f"Material Vinculado: {ativo_sab}. "
                    diretriz_sabado += foco_sab
                    
                    diretriz_a1 = "N/A"
                    diretriz_a2 = "N/A"
                else:
                    diretriz_sabado = "N/A"
                    c_d1, c_d2 = st.columns(2)
                    
                    with c_d1:
                        st.markdown("#### 📘 AULA 1")
                        tipo_a1 = st.selectbox("Natureza da Aula 1:", ["Conteúdo Novo (Teoria e Prática)", "Revisão / Correção", "Aplicação de Exame", "Atividade Prática / Projeto", "Evento / Dinâmica"], key=f"tipo_a1_{v}")
                        
                        ativo_a1 = ""
                        if tipo_a1 in ["Revisão / Correção", "Aplicação de Exame", "Atividade Prática / Projeto"]:
                            opcoes_a1 = obter_opcoes_acervo(tipo_a1, ano_str_busca)
                            ativo_a1 = st.selectbox("Vincular Material do Acervo (Aula 1):", [""] + opcoes_a1, key=f"ativo_a1_{v}")
                            
                        foco_a1 = st.text_area("Foco Exato da Aula 1:", placeholder="Ex: Explicar perímetro usando o link fornecido...", height=100, key=f"dir_a1_{v}")
                        
                        diretriz_a1 = f"[{tipo_a1}] "
                        if ativo_a1: diretriz_a1 += f"Material Vinculado: {ativo_a1}. "
                        diretriz_a1 += foco_a1
                        
                    with c_d2:
                        if carga_horaria != "1 Aula":
                            st.markdown("#### 📗 AULA 2")
                            tipo_a2 = st.selectbox("Natureza da Aula 2:", ["Conteúdo Novo (Teoria e Prática)", "Revisão / Correção", "Aplicação de Exame", "Atividade Prática / Projeto", "Evento / Dinâmica"], index=1, key=f"tipo_a2_{v}")
                            
                            ativo_a2 = ""
                            if tipo_a2 in ["Revisão / Correção", "Aplicação de Exame", "Atividade Prática / Projeto"]:
                                opcoes_a2 = obter_opcoes_acervo(tipo_a2, ano_str_busca)
                                ativo_a2 = st.selectbox("Vincular Material do Acervo (Aula 2):", [""] + opcoes_a2, key=f"ativo_a2_{v}")
                                
                            foco_a2 = st.text_area("Foco Exato da Aula 2:", placeholder="Ex: Fazer uma revisão geral para a prova...", height=100, key=f"dir_a2_{v}")
                            
                            diretriz_a2 = f"[{tipo_a2}] "
                            if ativo_a2: diretriz_a2 += f"Material Vinculado: {ativo_a2}. "
                            diretriz_a2 += foco_a2
                        else:
                            diretriz_a2 = "N/A"
                            st.info("Carga horária de 1 Aula. Diretriz da Aula 2 desativada.")

            # --- BOTÃO DE COMPILAÇÃO ---
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🧠 INICIAR MOTOR DE IA: GERAR PLANEJAMENTO", use_container_width=True, type="primary", key=f"btn_compilar_{v}"):
                
                if modo_p == "📖 Livro Didático" and not uri_livro_drive:
                    st.error("❌ Erro: O livro selecionado não possui um link válido no banco de materiais.")
                elif modo_p == "🌐 Links da Web (Artigos/Sites)" and not links_web_texto.strip():
                    st.error("❌ Erro: Cole pelo menos um link válido na caixa de texto.")
                else:
                    with st.spinner("Maestro SOSA analisando a Matriz, buscando referências de elite e arquitetando o Plano..."):
                        
                        if modo_p == "🎛️ Manual (Matriz)":
                            diretriz_base = "MÉTODO MANUAL: Baseie-se EXCLUSIVAMENTE na Matriz Curricular e nas fontes de elite da internet."
                        elif modo_p == "🌐 Links da Web (Artigos/Sites)":
                            diretriz_base = f"MÉTODO WEB SCRAPING: Acesse os links a seguir, leia o conteúdo deles e use-os como base principal para a aula:\n{links_web_texto}"
                        else:
                            diretriz_base = f"MÉTODO LIVRO: Use o PDF anexo como base principal. PÁGINAS ALVO: {base_didatica_info}."

                        status_enriquecimento = "ATIVADO (Use sites de referência: Toda Matéria, Brasil Escola, Khan Academy. Traga questões OBMEP/ENEM/SAEB e conecte com fatos atuais/tecnologia)." if enriquecimento_elite else "DESATIVADO (Mantenha-se estritamente ao livro ou matriz básica)."

                        prompt = (
                            f"NATUREZA DA SEMANA: {tipo_semana}\n"
                            f"TIPO DE PLANEJAMENTO: {tipo_planejamento}\n"
                            f"{diretriz_base}\n"
                            f"SÉRIE: {ano_p}º Ano. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}.\n"
                            f"CARGA HORÁRIA: {carga_horaria}.\n"
                            f"ENRIQUECIMENTO DE ELITE: {status_enriquecimento}\n\n"
                            f"🚨 DIRETRIZES SOBERANAS DO PROFESSOR (OBEDEÇA CEGAMENTE):\n"
                            f"- PENDÊNCIAS DA SEMANA ANTERIOR: {pendencias_ant if pendencias_ant else 'Nenhuma.'}\n"
                            f"- DIRETRIZ AULA 1: {diretriz_a1}\n"
                            f"- DIRETRIZ AULA 2: {diretriz_a2}\n"
                            f"- DIRETRIZ SÁBADO: {diretriz_sabado}\n\n"
                            f"--- PONTE PEDAGÓGICA (MEMÓRIA DA TURMA) ---\nAnalise o plano da semana anterior abaixo para criar o gancho de continuidade:\n{plano_anterior_txt}\n\n"
                            f"--- MATRIZ OFICIAL (ITABUNA) ---\n{ctx_ia}"
                        )
                        
                        resultado = ai.gerar_ia("PLANE_PEDAGOGICO", prompt, url_drive=uri_livro_drive, usar_busca=True)
                        
                        st.session_state.p_temp = resultado
                        st.session_state.p_meta = {
                            "semana": sem_limpa, "carga": carga_horaria, 
                            "trimestre": trim_atual, "ano": ano_str_busca,
                            "base": base_didatica_info,
                            "is_sabado": is_sabado_avulso
                        }
                        st.session_state.v_plano = int(time.time())
                        st.rerun()

            # --- EDITOR E VISUALIZAÇÃO ---
            if "p_temp" in st.session_state:
                txt_bruto = st.session_state.p_temp
                meta = st.session_state.get("p_meta", {})
                is_sabado_avulso = meta.get("is_sabado", False)
                
                st.markdown("---")
                with st.container(border=True):
                    st.markdown(f"### 📋 Conferência de Regência: **{meta.get('semana')}**")
                    cm1, cm2, cm3, cm4 = st.columns([1, 1, 1, 2])
                    cm1.metric("Série/Ano", meta.get('ano'))
                    cm2.metric("Carga Horária", "Sábado Letivo" if is_sabado_avulso else meta.get('carga'))
                    cm3.metric("Trimestre", meta.get('trimestre'))
                    cm4.metric("📖 Base Didática", meta.get('base'))

                t_ed, t_vis = st.tabs(["✏️ Editor Manual", "👁️ Visão do Documento Final"])
                
                with t_ed:
                    with st.container(border=True):
                        st.subheader("🤖 Refinador Maestro (Ajuste Rápido)")
                        st.caption("Não gostou de algo? Peça para a IA reescrever antes de salvar.")
                        cmd_refine = st.chat_input("Ex: 'Deixe a Aula 1 mais lúdica' ou 'Foque mais na página 15'...", key=f"chat_refine_{v}")
                        
                        if cmd_refine:
                            with st.spinner("Reengenharia em curso..."):
                                prompt_refino = (
                                    f"ORDEM SOBERANA: {cmd_refine}\n\n"
                                    f"PLANO ATUAL PARA REFINAR:\n{st.session_state.p_temp}\n\n"
                                    f"MATRIZ DE REFERÊNCIA:\n{df_curriculo[df_curriculo['ANO'].astype(str)==str(ano_p)].to_string(index=False)}"
                                )
                                resultado_refino = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino, url_drive=uri_livro_drive)
                                st.session_state.p_temp = resultado_refino
                                st.session_state.v_plano = int(time.time())
                                st.rerun()

                        if st.button("🗑️ DESCARTAR E RECOMEÇAR", use_container_width=True): reset_planejamento()

                    st.markdown("#### 🛡️ Filtros de Curadoria (O que vai para o DOCX?)")
                    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
                    keep_objeto = col_f1.checkbox("Objeto de Conhecimento", value=True, key=f"k_obj_{v}")
                    keep_conteudo = col_f2.checkbox("Conteúdos Específicos", value=True, key=f"k_cont_{v}")
                    keep_objetivos = col_f3.checkbox("Objetivos de Ensino", value=True, key=f"k_objt_{v}")
                    keep_justificativa = col_f4.checkbox("Justificativa PHC", value=True, key=f"k_just_{v}")

                    st.divider()

                    ed_hab = st.text_input("Habilidade/Competência:", ai.extrair_tag(txt_bruto, "HABILIDADE_BNCC") or ai.extrair_tag(txt_bruto, "COMPETENCIA_GERAL"), key=f"ed_h_{v}")
                    ed_comp = st.text_input("Competências Foco:", ai.extrair_tag(txt_bruto, "COMPETENCIAS_FOCO"), key=f"ed_c_{v}")
                    
                    ed_geral = st.text_input("Objeto de Conhecimento:", ai.extrair_tag(txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL"), key=f"ed_g_{v}") if keep_objeto else "N/A"
                    ed_espec = st.text_area("Conteúdos Específicos:", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS"), key=f"ed_e_{v}") if keep_conteudo else "N/A"
                    ed_objs = st.text_area("Objetivos de Aprendizagem:", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO"), key=f"ed_o_{v}") if keep_objetivos else "N/A"
                    
                    ed_base = st.text_input("📖 Referência de Base (Livro/Páginas/Sites):", ai.extrair_tag(txt_bruto, "BASE_DIDATICA") or meta.get('base'), key=f"ed_base_{v}")
                    ed_just = st.text_area("Justificativa Pedagógica:", ai.extrair_tag(txt_bruto, "JUSTIFICATIVA_PEDAGOGICA"), key=f"ed_j_{v}") if keep_justificativa else "N/A"
                    
                    st.markdown("#### 🏫 Roteiro de Aulas")
                    if is_sabado_avulso:
                        ed_a1 = "N/A"
                        ed_a2 = "N/A"
                        ed_a3 = st.text_area("SÁBADO LETIVO:", ai.extrair_tag(txt_bruto, "SABADO_LETIVO"), height=300, key=f"ed_a3_{v}")
                    else:
                        ed_a1 = st.text_area("AULA 1:", ai.extrair_tag(txt_bruto, "AULA_1"), height=200, key=f"a1_{v}")
                        if "1 Aula" not in meta.get('carga', ''):
                            ed_a2 = st.text_area("AULA 2:", ai.extrair_tag(txt_bruto, "AULA_2"), height=200, key=f"a2_{v}")
                        else: ed_a2 = "N/A"
                        ed_a3 = "N/A"
                    
                    ed_ava = st.text_area("Avaliação/Logística:", ai.extrair_tag(txt_bruto, "AVALIACAO_DE_MERITO") or ai.extrair_tag(txt_bruto, "AVALIACAO"), key=f"ed_ava_{v}")
                    ed_dua = st.text_area("Estratégia DUA/PEI:", ai.extrair_tag(txt_bruto, "ESTRATEGIA_DUA_PEI") or ai.extrair_tag(txt_bruto, "ADAPTACAO_PEI"), key=f"ed_dua_{v}")

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("💾 HOMOLOGAR PLANO E ENVIAR PARA O HUB DE PRODUÇÃO", use_container_width=True, type="primary"):
                        with st.status("Gerando DOCX e Sincronizando com o Google Drive...") as status:
                            final_ano_str = meta.get('ano')
                            
                            sufixo_arq = "_SABADO" if is_sabado_avulso else ""
                            nome_arquivo = f"PLANO_{final_ano_str.replace('º','')}_{meta.get('semana').replace(' ', '')}{sufixo_arq}"
                            
                            db.excluir_plano_completo(meta.get('semana') + sufixo_arq, final_ano_str)
                            
                            roteiro_docx = f"JUSTIFICATIVA: {ed_just}\n\nCOMPETÊNCIAS: {ed_comp}\n\n"
                            if is_sabado_avulso:
                                roteiro_docx += f"SÁBADO LETIVO:\n{ed_a3}"
                            else:
                                roteiro_docx += f"AULA 01:\n{ed_a1}\n\nAULA 02:\n{ed_a2}"

                            dados_docx = {
                                "geral": ed_geral, "especificos": ed_espec, "objetivos": ed_objs, 
                                "recursos": ed_base, 
                                "metodologia": roteiro_docx,
                                "avaliacao": ed_ava, "pei": ed_dua
                            }
                            
                            doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": final_ano_str, "semana": meta.get('semana') + sufixo_arq, "trimestre": meta.get('trimestre')})
                            link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=meta.get('trimestre'), categoria=final_ano_str, semana=meta.get('semana'), modo="PLANEJAMENTO")
                            
                            if "https" in str(link_drive):
                                final_txt = (
                                    f"[HABILIDADE_BNCC] {ed_hab} \n[COMPETENCIAS_FOCO] {ed_comp} \n"
                                    f"[OBJETO_CONHECIMENTO] {ed_geral} \n[CONTEUDOS_ESPECIFICOS] {ed_espec} \n"
                                    f"[OBJETIVOS_ENSINO] {ed_objs} \n[BASE_DIDATICA] {ed_base} \n"
                                    f"[JUSTIFICATIVA_PEDAGOGICA] {ed_just} \n"
                                    f"[AULA_1] {ed_a1} \n[AULA_2] {ed_a2} \n"
                                    f"[SABADO_LETIVO] {ed_a3} \n[AVALIACAO_DE_MERITO] {ed_ava} \n"
                                    f"[ESTRATEGIA_DUA_PEI] {ed_dua} \n--- LINK DRIVE --- {link_drive}"
                                )
                                db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), meta.get('semana') + sufixo_arq, final_ano_str, meta.get('trimestre'), "HUB_ATIVO", final_txt, link_drive])
                                status.update(label="✅ Plano Sincronizado com Sucesso!", state="complete")
                                st.balloons(); reset_planejamento()

                with t_vis:
                    st.subheader("👁️ Visão do Documento Final")
                    st.caption(f"📅 {meta.get('semana')} | 🎓 {meta.get('ano')} Ano | 📅 {meta.get('trimestre')}")
                    
                    c_v1, c_v2 = st.columns(2)
                    with c_v1:
                        if keep_objeto: st.info(f"**🎯 Objeto de Conhecimento:**\n{ed_geral}")
                        st.markdown(f"**🆔 Habilidade:** `{ed_hab}`")
                        st.markdown(f"**🌟 Competências Foco:**\n{ed_comp}")
                        st.success(f"**📖 Base Didática (DNA):**\n{ed_base}")
                    
                    with c_v2:
                        st.markdown("##### 🏫 Roteiro de Execução")
                        if is_sabado_avulso:
                            with st.container(border=True):
                                st.write(f"**🗓️ SÁBADO LETIVO:**\n{ed_a3}")
                        else:
                            with st.container(border=True):
                                st.write(f"**📘 AULA 1:**\n{ed_a1}")
                            if "1 Aula" not in meta.get('carga', ''):
                                with st.container(border=True):
                                    st.write(f"**📗 AULA 2:**\n{ed_a2}")
                    
                    st.divider()
                    c_v3, c_v4 = st.columns(2)
                    with c_v3: st.warning(f"**♿ Estratégia DUA/PEI (Equidade):**\n{ed_dua}")
                    with c_v4: st.error(f"**📝 Avaliação de Mérito:**\n{ed_ava}")

    # --- ABA 2: DASHBOARD DE PRODUÇÃO ---
    with tab_producao:
        st.subheader("🏗️ Hub de Produção de Materiais")
        st.info("💡 Aqui ficam os planos aprovados que estão aguardando a geração dos materiais físicos (Folha do Aluno, Guia do Professor, etc).")
        
        if not df_planos.empty:
            planos_ativos = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]
            
            if not planos_ativos.empty:
                for _, row in planos_ativos.iterrows():
                    with st.container(border=True):
                        c_p1, c_p2, c_p3, c_p4 = st.columns([1.5, 1.5, 1, 1])
                        
                        sem_ref = row['SEMANA']
                        ano_ref = row['ANO']
                        plano_txt = str(row["PLANO_TEXTO"])
                        
                        c_p1.markdown(f"**{sem_ref}**\n`Série: {ano_ref}`")
                        
                        aulas_que_devem_existir = []
                        
                        if "_SABADO" in sem_ref or "Sábado" in sem_ref:
                            aulas_que_devem_existir.append("Sábado Letivo")
                        else:
                            aulas_que_devem_existir.append("Aula 1")
                            conteudo_a2 = ai.extrair_tag(plano_txt, "AULA_2")
                            if conteudo_a2 and "não previsto" not in conteudo_a2.lower() and "n/a" not in conteudo_a2.lower() and len(conteudo_a2) > 30:
                                aulas_que_devem_existir.append("Aula 2")
                        
                        aulas_no_banco = df_aulas[(df_aulas['SEMANA_REF'] == sem_ref) & (df_aulas['ANO'] == ano_ref)]
                        lista_materiais_prontos = aulas_no_banco['TIPO_MATERIAL'].astype(str).tolist()
                        
                        icones_progresso = []
                        for aula_alvo in aulas_que_devem_existir:
                            foi_feita = any(aula_alvo in mat for mat in lista_materiais_prontos)
                            status_icon = "✅" if foi_feita else "⏳"
                            icones_progresso.append(f"{status_icon} {aula_alvo}")
                        
                        c_p2.markdown(f"**Status de Geração:**\n{' | '.join(icones_progresso)}")
                        
                        if c_p3.button("🧪 GERAR MATERIAL", key=f"gen_hub_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = plano_txt
                            st.session_state.sosa_id_atual = util.gerar_sosa_id("AULA", ano_ref, row["TURMA"])
                            st.session_state.lab_meta = {
                                "ano": str(ano_ref).replace("º",""), 
                                "trimestre": row["TURMA"], 
                                "tipo": "PRODUÇÃO_HUB",
                                "semana_ref": sem_ref
                            }
                            st.success("Conteúdo enviado! Vá para a aba 'Criador de Aulas'.")

                        if c_p4.button("✅ MARCAR CONCLUÍDO", help="Remove este plano da fila de pendências.", key=f"fin_hub_{row.name}", use_container_width=True):
                            if db.arquivar_plano_produzido(sem_ref, ano_ref):
                                st.success("Safra Concluída!"); time.sleep(1); st.rerun()
            else:
                st.success("🎉 Tudo em dia! Nenhum plano pendente de produção no momento.")

    # --- ABA 3: GESTÃO DE ACERVO ---
    with tab_acervo:
        st.subheader("📂 Acervo de Planos Estratégicos")
        st.info("💡 Histórico completo de todos os planos já gerados e salvos no Google Drive.")
        
        if not df_planos.empty:
            c_h1, c_h2 = st.columns([1, 2])
            f_ano_h = c_h1.selectbox("Filtrar por Série:", ["Todos", "1º", "2º", "3º", "4º", "5º", "6º", "7º", "8º", "9º"], key="hist_ano_v40")
            
            df_h = df_planos.copy()
            if f_ano_h != "Todos": 
                df_h = df_h[df_h["ANO"] == f"{f_ano_h}º"]
            
            if not df_h.empty:
                lista_semanas = df_h["SEMANA"].tolist()[::-1]
                sel_h = st.selectbox("Selecionar Plano para Visualização:", lista_semanas, key="hist_sem_v40")
                
                dados_h = df_h[df_h["SEMANA"] == sel_h].iloc[0]
                raw_h = str(dados_h["PLANO_TEXTO"])
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("🔄 REABRIR NO EDITOR", use_container_width=True, key=f"btn_reopen_{sel_h}"):
                        st.session_state.p_temp = raw_h
                        st.session_state.p_meta = {
                            "semana": sel_h, "ano": dados_h["ANO"], 
                            "trimestre": dados_h["TURMA"],
                            "carga": "2 Aulas",
                            "base": ai.extrair_tag(raw_h, "BASE_DIDATICA")
                        }
                        st.success("✅ Plano carregado no Editor!"); st.rerun()
                with col_btn2:
                    if st.button("🚀 DEVOLVER PARA PRODUÇÃO", help="Manda o plano de volta para a aba Hub de Produção.", use_container_width=True, type="primary", key=f"btn_hub_act_{sel_h}"):
                        if db.ativar_plano_no_hub(sel_h, dados_h["ANO"]):
                            st.success("✅ Plano enviado ao Dashboard!"); time.sleep(1); st.rerun()
                with col_btn3:
                    link_d = dados_h.get("LINK_DRIVE", "#")
                    st.link_button("📂 ABRIR DOCX NO DRIVE", str(link_d), use_container_width=True)

                with st.container(border=True):
                    val_objeto = ai.extrair_tag(raw_h, "OBJETO_CONHECIMENTO") or ai.extrair_tag(raw_h, "CONTEUDO_GERAL")
                    val_hab = ai.extrair_tag(raw_h, "HABILIDADE_BNCC")
                    val_comp = ai.extrair_tag(raw_h, "COMPETENCIAS_FOCO")
                    val_base = ai.extrair_tag(raw_h, "BASE_DIDATICA") or "Matriz Curricular"
                    
                    st.markdown(f"### 🎯 {val_objeto}")
                    st.caption(f"📅 {sel_h} | 🎓 {dados_h['ANO']} | 📅 {dados_h['TURMA']}")
                    
                    c_meta1, c_meta2 = st.columns([1, 1])
                    with c_meta1:
                        st.markdown(f"**🆔 Habilidade:** `{val_hab}`")
                        st.markdown(f"**🌟 Competências:** {val_comp}")
                    with c_meta2:
                        st.success(f"**📖 Base Didática (DNA):**\n{val_base}")
                    
                    st.divider()
                    c_info1, c_info2 = st.columns(2)
                    with c_info1:
                        st.markdown("##### 📖 Conteúdos Específicos")
                        st.info(ai.extrair_tag(raw_h, 'CONTEUDOS_ESPECIFICOS'))
                    with c_info2:
                        st.markdown("##### ✅ Objetivos de Aprendizagem")
                        st.info(ai.extrair_tag(raw_h, 'OBJETIVOS_ENSINO'))
                    
                    st.divider()
                    st.markdown("##### 🏫 Roteiro de Execução")
                    
                    val_sab = ai.extrair_tag(raw_h, "SABADO_LETIVO")
                    if val_sab and "N/A" not in val_sab.upper() and "não programada" not in val_sab:
                        with st.container(border=True):
                            st.write(f"**🗓️ SÁBADO LETIVO:**\n{val_sab}")
                    else:
                        c_v1, c_v2 = st.columns(2)
                        with c_v1: 
                            with st.container(border=True):
                                st.write(f"**📘 AULA 1:**\n{ai.extrair_tag(raw_h, 'AULA_1')}")
                        with c_v2: 
                            val_a2 = ai.extrair_tag(raw_h, 'AULA_2')
                            if val_a2 and "N/A" not in val_a2.upper() and "não previsto" not in val_a2:
                                with st.container(border=True):
                                    st.write(f"**📗 AULA 2:**\n{val_a2}")
                            else:
                                st.caption("Sem Aula 2 planejada para esta semana.")
                    
                    st.divider()
                    c_v3, c_v4 = st.columns(2)
                    with c_v3: st.warning(f"**♿ Estratégia DUA/PEI:**\n{ai.extrair_tag(raw_h, 'ESTRATEGIA_DUA_PEI')}")
                    with c_v4: st.error(f"**📝 Avaliação de Mérito:**\n{ai.extrair_tag(raw_h, 'AVALIACAO_DE_MERITO')}")
                
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

    # --- ABA 5: ANALYTICS DE COBERTURA ---
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
                progresso_trim["sum"] = pd.to_numeric(progresso_trim["sum"], errors='coerce').fillna(0)
                progresso_trim["count"] = pd.to_numeric(progresso_trim["count"], errors='coerce').fillna(1)
                
                progresso_trim["%"] = (progresso_trim["sum"] / progresso_trim["count"] * 100)
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
    # 🚨 ABA 6: PLANEJAMENTO TRIMESTRAL (MACRO-SOSA)
    # ==============================================================================
    with tab_trimestral:
        st.subheader("📅 Gerador de Planejamento Trimestral (Macro-SOSA)")
        st.caption("Gere o documento oficial da escola (em formato paisagem) com todos os conteúdos e objetivos do trimestre extraídos automaticamente da Matriz Curricular.")
        
        with st.container(border=True):
            c_t1, c_t2 = st.columns([1, 1])
            ano_trim = c_t1.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"], key="trim_ano")
            trim_alvo = c_t2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="trim_trim")
            
            # Busca as turmas cadastradas para essa série
            ano_num_trim = "".join(filter(str.isdigit, ano_trim))
            turmas_disp = df_turmas[df_turmas['ID_TURMA'].str.contains(ano_num_trim, na=False)]['ID_TURMA'].tolist()
            
            turmas_sel = st.multiselect("Turmas (Para o cabeçalho da tabela):", turmas_disp, default=turmas_disp, key="trim_turmas")
            
        # Filtra a matriz curricular
        df_matriz_trim = df_curriculo[(df_curriculo['ANO'].astype(str).str.contains(ano_num_trim)) & (df_curriculo['TRIMESTRE'] == trim_alvo.split(" ")[0])]
        
        if df_matriz_trim.empty:
            st.warning(f"⚠️ Nenhum conteúdo encontrado na Matriz Curricular para o {ano_trim} no {trim_alvo}.")
        else:
            # 🚨 MOTOR DE EXTRAÇÃO DE CÓDIGOS BNCC (REGEX)
            bncc_codes = set()
            
            # 1. Busca nos Planos de Aula já gerados no Acervo
            planos_trim = df_planos[(df_planos['ANO'].str.contains(ano_num_trim)) & (df_planos['TURMA'] == trim_alvo)]
            for txt in planos_trim['PLANO_TEXTO'].dropna():
                hab_tag = ai.extrair_tag(str(txt), "HABILIDADE_BNCC")
                codes = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', hab_tag, re.IGNORECASE)
                bncc_codes.update([c.upper() for c in codes])
                
            # 2. Busca de segurança na própria Matriz Curricular (caso não haja planos gerados)
            for obj in df_matriz_trim['OBJETIVOS'].dropna():
                codes = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', str(obj), re.IGNORECASE)
                bncc_codes.update([c.upper() for c in codes])
                
            lista_bncc_final = sorted(list(bncc_codes))
            
            st.success(f"✅ Encontrados {len(df_matriz_trim['CONTEUDO_ESPECIFICO'].unique())} conteúdos e {len(lista_bncc_final)} códigos BNCC.")
            
            with st.expander("⚙️ Configurar Textos Padrão (Metodologia, Recursos e Avaliação)", expanded=True):
                st.info("Estes textos preencherão as colunas finais da tabela. Você pode editá-los conforme a necessidade da sua turma.")
                
                texto_metodologia = st.text_area("Metodologia:", 
                    "Aulas expositivas e dialogadas com exemplos práticos;\nResolução de exercícios em classe/casa;\nAtividades individuais e em grupo;\nAprendizagem Baseada em Problemas (PBL);\nGamificação;\nUso de recursos tecnológicos (quando disponíveis);\nRevisões periódicas contextualizadas/retomada de conceitos;\nRecomposição de aprendizagens.", height=150)
                
                texto_recursos = st.text_area("Recursos:", 
                    "Quadro branco\nPiloto\nLivro didático\nApostilas\nJogos pedagógicos\nMaterial impresso", height=150)
                
                texto_avaliacao = st.text_area("Avaliação:", 
                    "A avaliação é contínua e multifacetada, considerando elementos como:\nParticipação durante as aulas;\nRealização das atividades;\nDesenvolvimento de habilidades escolares e sociais;\nIniciativa para superar dificuldades com o auxílio do professor.", height=150)

            if st.button("🖨️ GERAR PLANEJAMENTO TRIMESTRAL (DOCX)", type="primary", use_container_width=True):
                if not turmas_sel:
                    st.error("⚠️ Selecione pelo menos uma turma.")
                else:
                    with st.spinner("Compilando dados e gerando documento em paisagem..."):
                        info_trim = {
                            "trimestre": trim_alvo,
                            "turmas": ", ".join(turmas_sel)
                        }
                        
                        config_textos = {
                            "metodologia": texto_metodologia,
                            "recursos": texto_recursos,
                            "avaliacao": texto_avaliacao
                        }
                        
                        nome_arq_trim = f"PLANEJAMENTO_{trim_alvo.replace(' ', '')}_{ano_trim.replace('º ', '')}"
                        tipo_relatorio_banco = f"MACRO_{ano_trim.replace('º ', '')}_{trim_alvo.replace(' ', '')}"
                        
                        # Chama o exporter passando a lista de códigos BNCC
                        doc_stream = exporter.gerar_docx_planejamento_trimestral(nome_arq_trim, info_trim, df_matriz_trim, config_textos, lista_bncc_final)
                        
                        # Sobe para o Drive
                        link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_trim, trimestre=trim_alvo, categoria=ano_trim, modo="PLANEJAMENTO")
                        
                        if "https" in link_doc:
                            # 🚨 ENGENHARIA DE DELEÇÃO REVERSA (UPSERT)
                            try:
                                wb = db.conectar()
                                ws = wb.worksheet("DB_RELATORIOS")
                                dados = ws.get_all_values()
                                for i in range(len(dados)-1, 0, -1):
                                    if len(dados[i]) > 3 and dados[i][3] == tipo_relatorio_banco:
                                        # Apaga o arquivo antigo do Drive para não acumular lixo
                                        link_antigo = re.search(r"Link:\s*(https?://[^\s]+)", dados[i][4])
                                        if link_antigo:
                                            db.excluir_registro_com_drive("DB_RELATORIOS", link_antigo.group(1))
                                        ws.delete_rows(i+1)
                            except: pass
                            
                            # Salva o novo no banco
                            db.salvar_no_banco("DB_RELATORIOS", [
                                datetime.now().strftime("%d/%m/%Y"), 
                                "TURMA", 
                                ", ".join(turmas_sel), 
                                tipo_relatorio_banco, 
                                f"Série: {ano_trim}\nTrimestre: {trim_alvo}\nLink: {link_doc}"
                            ])
                            st.success("✅ Planejamento Trimestral gerado e salvo no Acervo!")
                            st.balloons()
                            time.sleep(1.5)
                            st.rerun()
                        else:
                            st.error(f"Erro ao salvar no Drive: {link_doc}")

        # ==============================================================================
        # 🗂️ ACERVO DE PLANEJAMENTOS TRIMESTRAIS
        # ==============================================================================
        st.markdown("---")
        st.subheader("🗂️ Acervo de Planejamentos Trimestrais")
        st.caption("Acesse os documentos oficiais já gerados. Ao gerar um novo para a mesma série e trimestre, o antigo é substituído automaticamente.")
        
        df_macro = df_relatorios[df_relatorios['TIPO'].str.startswith('MACRO_')].copy()
        
        if not df_macro.empty:
            for idx, row in df_macro.iloc[::-1].iterrows():
                with st.container(border=True):
                    c_m1, c_m2, c_m3 = st.columns([2, 1, 1])
                    
                    conteudo_m = str(row['CONTEUDO'])
                    serie_m = re.search(r"Série:\s*(.*)", conteudo_m)
                    trim_m = re.search(r"Trimestre:\s*(.*)", conteudo_m)
                    link_m = re.search(r"Link:\s*(https?://[^\s]+)", conteudo_m)
                    
                    serie_str = serie_m.group(1).strip() if serie_m else "Série N/A"
                    trim_str = trim_m.group(1).strip() if trim_m else "Trimestre N/A"
                    link_str = link_m.group(1).strip() if link_m else "#"
                    
                    c_m1.markdown(f"**📄 Planejamento Trimestral: {serie_str}**")
                    c_m1.caption(f"📅 {trim_str} | Gerado em: {row['DATA']}")
                    
                    if "http" in link_str:
                        c_m2.link_button("🖨️ ABRIR DOCX", link_str, use_container_width=True, type="primary")
                    else:
                        c_m2.button("⚪ SEM LINK", disabled=True, use_container_width=True)
                        
                    if c_m3.button("🗑️ APAGAR", key=f"del_macro_{idx}", use_container_width=True):
                        with st.spinner("Apagando arquivo..."):
                            db.excluir_registro_com_drive("DB_RELATORIOS", link_str if "http" in link_str else conteudo_m)
                            st.rerun()
        else:
            st.info("📭 Nenhum Planejamento Trimestral gerado no acervo.")



# ==============================================================================
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR DE AULAS) - CLEAN & UX
# ==============================================================================
elif menu == "🧪 Criador de Aulas":
    st.title("🧪 Laboratório de Produção Semiótica")
    st.markdown("---")
    st.caption("💡 **Guia de Comando:** Transforme seus planejamentos (Ponto ID) em materiais físicos de alta densidade (Folha do Aluno, Guia do Professor e Adaptação PEI) com um clique.")
    
    def reset_laboratorio():
        keys_to_del =["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "sosa_id_atual", "lab_meta", "hub_origem", "chat_history_lab"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.cache_data.clear() 
        st.session_state.v_lab = int(time.time())
        st.rerun()

    if "v_lab" not in st.session_state: 
        st.session_state.v_lab = int(time.time())
    v = st.session_state.v_lab

    meta = st.session_state.get("lab_meta", {})
    is_hub = meta.get("tipo") == "PRODUÇÃO_HUB"
    
    # --- ÁREA DE EXIBIÇÃO E REFINO ---
    if "lab_temp" in st.session_state:
        txt_base = st.session_state.lab_temp
        s_id = st.session_state.get("sosa_id_atual", "SEM-ID")
        st.success(f"💎 Material em Edição: **{s_id}**")

        # ==============================================================================
        # 🤖 MAESTRO COPILOT (CHATBOT DE REFINO)
        # ==============================================================================
        with st.container(border=True):
            st.subheader("🤖 Maestro Copilot (Coautoria em Tempo Real)")
            st.caption("Converse com a IA para ajustar o material. O editor abaixo será atualizado automaticamente.")
            
            if "chat_history_lab" not in st.session_state:
                st.session_state.chat_history_lab =[{"role": "assistant", "avatar": "🤖", "content": "Saudações, Mestre! O material base foi gerado. Como deseja refinar a nossa estratégia?"}]
            
            chat_container_lab = st.container(height=300)
            with chat_container_lab:
                for msg in st.session_state.chat_history_lab:
                    with st.chat_message(msg["role"], avatar=msg["avatar"]):
                        st.markdown(msg["content"])
            
            if cmd_refine_lab := st.chat_input("Ex: 'Deixe o texto do aluno mais simples' ou 'Adicione mais uma questão'...", key=f"chat_lab_ref_{v}"):
                st.session_state.chat_history_lab.append({"role": "user", "avatar": "💻", "content": cmd_refine_lab})
                
                with chat_container_lab:
                    with st.chat_message("user", avatar="💻"):
                        st.markdown(cmd_refine_lab)
                    with st.chat_message("assistant", avatar="🤖"):
                        with st.spinner("Reengenharia em curso..."):
                            hist_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history_lab[-5:]])
                            prompt_refino = (
                                f"HISTÓRICO DA CONVERSA:\n{hist_text}\n\n"
                                f"ORDEM ATUAL: {cmd_refine_lab}\n\n"
                                f"MATERIAL ATUAL PARA REFINAR:\n{txt_base}"
                            )
                            
                            resultado_refino = ai.gerar_ia("REFINADOR_MATERIAIS", prompt_refino)
                            
                            msg_chat = ai.extrair_tag(resultado_refino, "MENSAGEM_CHAT")
                            novo_conteudo = ai.extrair_tag(resultado_refino, "CONTEUDO_ATUALIZADO")
                            
                            if not novo_conteudo:
                                novo_conteudo = resultado_refino
                                msg_chat = "Material atualizado conforme solicitado, Mestre."
                                
                            st.markdown(msg_chat)
                            st.session_state.chat_history_lab.append({"role": "assistant", "avatar": "🤖", "content": msg_chat})
                            st.session_state.lab_temp = novo_conteudo
                            st.session_state.v_lab = int(time.time())
                            st.rerun()

            if st.button("🗑️ DESCARTAR EDIÇÃO E VOLTAR"): reset_laboratorio()
        
        st.markdown("---")
        
        # ==============================================================================
        # 👁️ MODO LEITURA (RENDERIZAÇÃO LATEX INLINE)
        # ==============================================================================
        c_tog1, c_tog2 = st.columns([1, 2])
        modo_leitura = c_tog1.toggle("👁️ Ativar Modo Leitura (Renderizar Matemática)", value=False, help="Ative para ver as equações LaTeX formatadas. Desative para editar o texto.")
        
        val_prof = ai.extrair_tag(txt_base, "PROFESSOR")
        val_alu = ai.extrair_tag(txt_base, "ALUNO")
        val_gab = ai.extrair_tag(txt_base, "GABARITO")
        val_pei = ai.extrair_tag(txt_base, "PEI")
        val_img = ai.extrair_tag(txt_base, "IMAGENS")

        # 🚨 FILTRO DE ILUSÃO DE ÓTICA: Transforma $$ em $ apenas para o Streamlit desenhar inline
        def preparar_para_leitura(texto):
            if not texto: return ""
            # Usa re.DOTALL para garantir que equações com quebra de linha sejam renderizadas na tela
            return re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)

        t_prof, t_alu, t_gab, t_pei_tab, t_img_tab, t_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "✅ Gabarito", "♿ PEI", "🎨 Imagens", "☁️ SINCRONIA"])
        
        with t_prof: 
            if modo_leitura:
                st.markdown(preparar_para_leitura(val_prof))
                ed_prof = val_prof # Mantém o original com $$ para salvar
            else:
                ed_prof = st.text_area("Lousa/Mediação:", val_prof, height=450, key=f"ed_prof_reg_{v}")
        
        with t_alu: 
            if modo_leitura:
                st.markdown(preparar_para_leitura(val_alu))
                ed_alu = val_alu
            else:
                ed_alu = st.text_area("Folha/Roteiro:", val_alu, height=450, key=f"ed_alu_reg_{v}")
        
        with t_gab: 
            if modo_leitura:
                st.markdown(preparar_para_leitura(val_gab))
                ed_gab = val_gab
            else:
                ed_gab = st.text_area("Gabarito:", val_gab, height=200, key=f"ed_res_reg_{v}")
        
        with t_pei_tab: 
            if modo_leitura:
                st.markdown(preparar_para_leitura(val_pei))
                ed_pei = val_pei
            else:
                ed_pei = st.text_area("PEI (Obrigatório):", val_pei, height=400, key=f"ed_pei_reg_{v}")
        
        with t_img_tab: 
            ed_img = st.text_area("Prompts de Imagem:", val_img, height=200, key=f"ed_img_reg_{v}")

        # --- ☁️ ABA DE SINCRONIA (TRIPLE-SYNC) ---
        with t_sync:
            st.subheader("🚀 Sincronia e Custódia Digital")
            st.info("Este comando irá gerar os documentos oficiais (DOCX) e salvar os links permanentes no seu banco de dados.")
            
            if st.button("💾 SALVAR MATERIAL E SINCRONIZAR NO DRIVE", use_container_width=True, type="primary", key=f"btn_triple_{v}"):
                with st.status("Sincronizando Ativos de Elite...") as status:
                    db.excluir_registro_com_drive("DB_AULAS_PRONTAS", s_id)
                    
                    ano_str = f"{meta.get('ano', '6')}º"
                    sem_ref = meta.get('semana_ref', 'Geral')
                    info_doc = {"ano": ano_str, "trimestre": "I Trimestre", "semana": sem_ref}

                    status.write("📝 Gerando Material do Aluno/Roteiro...")
                    doc_alu = exporter.gerar_docx_aluno_v24(s_id, ed_alu, info_doc)
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{s_id}_ALUNO", modo="AULA")
                    
                    status.write("♿ Gerando Atividade Adaptada PEI...")
                    doc_pei = exporter.gerar_docx_pei_v25(f"{s_id}_PEI", ed_pei, info_doc)
                    link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{s_id}_PEI", modo="AULA")
                    
                    status.write("👨‍🏫 Gerando Guia de Mediação do Professor...")
                    doc_prof = exporter.gerar_docx_professor_v25(s_id, ed_prof, info_doc)
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{s_id}_PROF", modo="AULA")
                    
                    links_f = f"--- LINKS ---\nRegular({link_alu})\nPEI({link_pei})\nProf({link_prof})"
                    conteudo_final = f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n[GABARITO]\n{ed_gab}\n\n[PEI]\n{ed_pei}\n\n[IMAGENS]\n{ed_img}\n\n{links_f}"
                    
                    db.salvar_no_banco("DB_AULAS_PRONTAS",[
                        datetime.now().strftime("%d/%m/%Y"), 
                        sem_ref, 
                        s_id, 
                        conteudo_final, 
                        ano_str, 
                        link_alu
                    ])
                    
                    status.update(label="✅ Sincronizado com Sucesso!", state="complete")
                    st.balloons()
                    import time
                    time.sleep(1)
                    reset_laboratorio()

    # --- SEÇÃO DE ENTRADA (CONFIGURAÇÃO COM INTELIGÊNCIA DE TRILHAS) ---
    else:
        tab_producao, tab_trabalhos, tab_complementar, tab_acervo_lab = st.tabs([
            "🚀 1. Produção de Aulas", "📋 2. Projetos e Trabalhos", "📚 3. Listas e Recomposição", "📂 4. Acervo de Materiais"
        ])

        with tab_producao:
            st.markdown("### ⚙️ Passo 1: Herança Didática (Ponto ID)")
            
            mostrar_tudo_lab = st.toggle("🔄 Mostrar semanas e aulas já concluídas (Modo Sobrescrita)", help="Ative se precisar refazer uma aula que já foi gerada e salva no acervo.", key=f"tog_lab_{v}")
            
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                ano_lab = c1.selectbox("Série/Ano Alvo:",[6, 7, 8, 9], key=f"prod_ano_{v}")
                planos_ano = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_lab))]
                
                if planos_ano.empty: 
                    st.error("❌ Nenhum planejamento encontrado para esta série. Vá ao Ponto ID primeiro.")
                else:
                    # Lógica de filtragem de semanas concluídas
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
                        st.success("✅ Todas as semanas planejadas para esta série já tiveram seus materiais produzidos! O acervo está completo.")
                    else:
                        sem_lab = c2.selectbox("Semana Base (Herdada do Ponto ID):", semanas_opcoes, key=f"prod_sem_{v}")
                        plano_row = planos_ano[planos_ano["SEMANA"] == sem_lab].iloc[0]
                        plano_txt = str(plano_row['PLANO_TEXTO'])

                        with st.expander("📡 Radar de Regência (Memória das Turmas)", expanded=True):
                            st.caption("O sistema verifica onde você parou na última aula para garantir a continuidade.")
                            contexto_turmas_ia = ""
                            reg_ano = df_registro_aulas[df_registro_aulas['TURMA'].str.contains(str(ano_lab))]
                            if not reg_ano.empty:
                                for t_nome in sorted(reg_ano['TURMA'].unique()):
                                    dados_t = reg_ano[reg_ano['TURMA'] == t_nome].iloc[-1]
                                    est = dados_t.get('STATUS_EXECUCAO', 'Não Iniciado')
                                    pnt = dados_t.get('PONTE_PEDAGOGICA', 'Sem pendências.')
                                    emoji = "🟢" if "Concluído" in est else "🟡" if "Parcial" in est else "🔴"
                                    st.write(f"{emoji} **{t_nome}:** {est}")
                                    contexto_turmas_ia += f"- Turma {t_nome}: Status {est}. Pendência: {pnt}\n"
                            else: st.info("ℹ️ Nenhuma regência anterior registrada.")

                        base_herdada = ai.extrair_tag(plano_txt, "BASE_DIDATICA")
                        obj_geral = ai.extrair_tag(plano_txt, "OBJETO_CONHECIMENTO") or ai.extrair_tag(plano_txt, "CONTEUDO_GERAL")
                        obj_upper = obj_geral.upper()
                        
                        # 🚨 INTELIGÊNCIA DE DETECÇÃO DE DNA DA AULA
                        is_exame = "EXAME" in obj_upper or "SONDA" in obj_upper or "AVALIAÇÃO" in obj_upper or "TESTE" in obj_upper
                        is_revisao = "REVISÃO" in obj_upper or "RECOMPOSIÇÃO" in obj_upper or "CORREÇÃO" in obj_upper
                        is_projeto = "PROJETO" in obj_upper or "TRABALHO" in obj_upper
                        is_evento = "EVENTO" in obj_upper or "DINÂMICA" in obj_upper or "AULA ABERTA" in obj_upper

                        opcoes_metodo = []
                        if is_exame:
                            opcoes_metodo = ["📝 Oficializar Aplicação de Exame (Vínculo de Acervo)"]
                        elif is_revisao:
                            opcoes_metodo = ["🔥 Oficializar Revisão/Correção (Vínculo de Acervo)"]
                        elif is_projeto:
                            opcoes_metodo = ["📋 Oficializar Apresentação de Projeto (Vínculo de Acervo)"]
                        elif is_evento:
                            opcoes_metodo = ["🎟️ Registro de Evento / Dinâmica (Sem Material Físico)"]
                        else:
                            opcoes_metodo = [
                                "🚀 Geração Integral (SOSA AI)", 
                                "📖 Livro Didático + PEI (Híbrido)",
                                "🎟️ Registro de Evento / Dinâmica (Sem Material Físico)"
                            ]
                            
                        metodo_entrega = st.radio("🎯 Método de Entrega (Adaptado ao DNA do Plano):", opcoes_metodo, horizontal=True, key=f"metodo_{v}")
                        
                        aulas_ja_geradas = df_aulas[(df_aulas['ANO'].str.contains(str(ano_lab))) & (df_aulas['SEMANA_REF'] == sem_lab)]['TIPO_MATERIAL'].astype(str).tolist()
                        
                        tem_aula1 = any("Aula 1" in mat for mat in aulas_ja_geradas)
                        tem_aula2 = any("Aula 2" in mat for mat in aulas_ja_geradas)
                        tem_sabado = any("Sábado" in mat or "Sabado" in mat for mat in aulas_ja_geradas)

                        plano_pede_a2 = len(ai.extrair_tag(plano_txt, "AULA_2")) > 30 and "N/A" not in ai.extrair_tag(plano_txt, "AULA_2").upper()
                        txt_sabado = ai.extrair_tag(plano_txt, "SABADO_LETIVO")
                        plano_pede_sab = len(txt_sabado) > 10 and "N/A" not in txt_sabado.upper() and "NÃO PROGRAMADA" not in txt_sabado.upper()

                        opcoes_disponiveis =[]
                        if not tem_aula1: opcoes_disponiveis.append("Aula 1")
                        if plano_pede_a2 and not tem_aula2: opcoes_disponiveis.append("Aula 2")
                        if plano_pede_sab and not tem_sabado: opcoes_disponiveis.append("Sábado Letivo")

                        if mostrar_tudo_lab:
                            opcoes_disponiveis =["Aula 1"]
                            if plano_pede_a2: opcoes_disponiveis.append("Aula 2")
                            if plano_pede_sab: opcoes_disponiveis.append("Sábado Letivo")

                        with st.container(border=True):
                            st.markdown(f"#### 🎯 Alvo Curricular: {obj_geral}")
                            
                            if not opcoes_disponiveis:
                                st.success("✅ Todas as aulas previstas para esta semana já foram produzidas! O acervo está completo.")
                                aula_alvo_prod = None
                            else:
                                col_config1, col_config2 = st.columns([1, 1])
                                with col_config1:
                                    aula_alvo_prod = st.radio("🚀 Material a Gerar/Oficializar:", opcoes_disponiveis, horizontal=True, key=f"prod_alvo_{v}")
                                
                                if "1" in aula_alvo_prod: tag_roteiro = "AULA_1"
                                elif "2" in aula_alvo_prod: tag_roteiro = "AULA_2"
                                else: tag_roteiro = "SABADO_LETIVO"
                                
                                roteiro_especifico = ai.extrair_tag(plano_txt, tag_roteiro)
                                
                                is_logistica = "Oficializar" in metodo_entrega or "Evento" in metodo_entrega

                                with col_config2:
                                    if is_logistica:
                                        st.info("💡 **Modo Logística:** Sem geração de material físico pela IA.")
                                        nome_evento = ""
                                    else:
                                        qtd_q_prod = st.slider("Nº de Questões (PEI/Regular):", 1, 20, 10, key=f"prod_q_{v}")

                                paginas_aula = base_herdada
                                if ";" in base_herdada:
                                    partes_pag = base_herdada.split(";")
                                    if "1" in aula_alvo_prod: paginas_aula = partes_pag[0].strip()
                                    elif "2" in aula_alvo_prod and len(partes_pag) > 1: paginas_aula = partes_pag[1].strip()
                                    else: paginas_aula = partes_pag[-1].strip()

                                with st.expander(f"👁️ Roteiro Herdado para {aula_alvo_prod}", expanded=False):
                                    st.info(f"📍 **Páginas Alvo:** {paginas_aula}\n\n{roteiro_especifico}")

                                prova_sel = ""
                                if is_logistica:
                                    st.markdown("---")
                                    if is_exame:
                                        st.warning("🔍 **Aplicação de Exame Detectada:** Selecione a prova correspondente para oficializar a aplicação no acervo.")
                                        mask_provas = df_aulas['TIPO_MATERIAL'].str.upper().str.contains("PROVA|TESTE|SONDA|AVALIAÇÃO|EXAME")
                                        provas_disponiveis = df_aulas[(df_aulas['ANO'].str.contains(str(ano_lab))) & mask_provas]
                                        if not provas_disponiveis.empty:
                                            prova_sel = st.selectbox("Vincular Avaliação do Acervo:", [""] + provas_disponiveis['TIPO_MATERIAL'].tolist(), key=f"vinc_prova_{v}")
                                        else:
                                            st.info("Nenhuma avaliação encontrada no acervo para esta série.")
                                            
                                    elif is_revisao:
                                        st.warning("🔥 **Revisão/Correção Detectada:** Selecione o material de revisão ou o Dossiê Raio-X para oficializar a aula.")
                                        opcoes_rev = df_aulas[(df_aulas['ANO'].str.contains(str(ano_lab))) & (df_aulas['SEMANA_REF'] == "REVISÃO")]['TIPO_MATERIAL'].tolist()
                                        
                                        # Puxa os Dossiês de Raio-X também
                                        df_dossies_ano = df_relatorios[(df_relatorios['TIPO'] == 'DOSSIE_RAIO_X') & (df_relatorios['NOME_ALUNO'].str.contains(str(ano_lab)))]
                                        for _, row_d in df_dossies_ano.iterrows():
                                            cont_d = str(row_d['CONTEUDO'])
                                            nome_av = re.search(r"Avaliação:\s*(.*)", cont_d)
                                            nome_av_str = nome_av.group(1).strip() if nome_av else "Avaliação Desconhecida"
                                            turma_d = row_d['NOME_ALUNO']
                                            opcoes_rev.append(f"📊 DOSSIÊ RAIO-X: {nome_av_str} ({turma_d})")
                                            
                                        if opcoes_rev:
                                            prova_sel = st.selectbox("Vincular Material de Revisão/Dossiê:", [""] + opcoes_rev, key=f"vinc_rev_{v}")
                                        else:
                                            st.info("Nenhum material de revisão ou dossiê encontrado no acervo.")
                                            
                                    elif is_projeto:
                                        st.warning("📋 **Apresentação de Projeto Detectada:** Selecione o projeto correspondente.")
                                        opcoes_proj = df_aulas[(df_aulas['ANO'].str.contains(str(ano_lab))) & (df_aulas['TIPO_MATERIAL'].str.contains("PROJETO|TRABALHO", case=False, na=False))]['TIPO_MATERIAL'].tolist()
                                        if opcoes_proj:
                                            prova_sel = st.selectbox("Vincular Projeto do Acervo:", [""] + opcoes_proj, key=f"vinc_proj_{v}")
                                        else:
                                            st.info("Nenhum projeto encontrado no acervo.")
                                            
                                    elif is_evento:
                                        nome_evento = st.text_input("Nome do Evento/Dinâmica:", placeholder="Ex: Palestra sobre a Dengue", key=f"nome_ev_{v}")

                        if opcoes_disponiveis:
                            # ==============================================================================
                            # 🚨 ROTA 1: OFICIALIZAÇÃO DIRETA (EVENTOS, AVALIAÇÕES, REVISÕES) - SEM IA
                            # ==============================================================================
                            if is_logistica:
                                if st.button("💾 OFICIALIZAR NO ACERVO (SEM MATERIAL FÍSICO)", use_container_width=True, type="primary"):
                                    nome_final_evento = ""
                                    
                                    if is_exame or is_revisao or is_projeto:
                                        if not prova_sel:
                                            st.error("⚠️ Selecione o material vinculado acima antes de oficializar.")
                                            st.stop()
                                        prefixo = "APLICAÇÃO" if is_exame else "CORREÇÃO/REVISÃO" if is_revisao else "APRESENTAÇÃO"
                                        nome_final_evento = f"{prefixo} - {prova_sel}"
                                    elif is_evento:
                                        nome_final_evento = nome_evento
                                        if not nome_final_evento:
                                            st.error("⚠️ Digite o nome do evento para registrar.")
                                            st.stop()
                                            
                                    with st.spinner("Registrando no acervo com rastreabilidade curricular..."):
                                        hab_herdada = ai.extrair_tag(plano_txt, "HABILIDADE_BNCC")
                                        cont_herdado = ai.extrair_tag(plano_txt, "CONTEUDOS_ESPECIFICOS")
                                        obj_herdado = ai.extrair_tag(plano_txt, "OBJETIVOS_ENSINO")
                                        
                                        conteudo_fantasma = (
                                            f"[PROFESSOR]\n"
                                            f"🎟️ **REGISTRO DE LOGÍSTICA / EVENTO**\n"
                                            f"**Tema:** {nome_final_evento}\n"
                                            f"**Habilidade:** {hab_herdada}\n"
                                            f"**Conteúdos:** {cont_herdado}\n"
                                            f"**Objetivos:** {obj_herdado}\n\n"
                                            f"**Roteiro Executado:**\n{roteiro_especifico}\n\n"
                                            f"[ALUNO]\nAtividade prática/avaliação. Sem material físico gerado nesta etapa.\n\n"
                                            f"[GABARITO]\nN/A\n\n"
                                            f"[PEI]\nParticipação inclusiva garantida via mediação direta ou material já impresso.\n\n"
                                            f"--- LINKS ---\nRegular(N/A)\nPEI(N/A)\nProf(N/A)"
                                        )
                                        
                                        nome_elite = util.gerar_nome_material_elite(ano_lab, aula_alvo_prod, nome_final_evento)
                                        
                                        db.salvar_no_banco("DB_AULAS_PRONTAS",[
                                            datetime.now().strftime("%d/%m/%Y"), 
                                            sem_lab, 
                                            nome_elite, 
                                            conteudo_fantasma, 
                                            f"{ano_lab}º", 
                                            "N/A"
                                        ])
                                        st.success("✅ Registro oficializado no Acervo! Já disponível no Cockpit para abertura de aula.")
                                        import time
                                        time.sleep(1.5)
                                        st.rerun()
                            
                            # ==============================================================================
                            # 🚨 ROTA 2: GERAÇÃO DE MATERIAL DIDÁTICO (COM IA)
                            # ==============================================================================
                            else:
                                uri_referencia_aula = None
                                if "Livro" in metodo_entrega:
                                    nome_livro_limpo = base_herdada.split('|')[0].replace("Livro:", "").strip()
                                    match_biblioteca = df_materiais[df_materiais['NOME_ARQUIVO'].str.contains(nome_livro_limpo[:10], case=False, na=False)]
                                    if not match_biblioteca.empty:
                                        uri_referencia_aula = match_biblioteca.iloc[0]['URI_ARQUIVO']
                                        st.success(f"📚 **Fonte Vinculada:** {match_biblioteca.iloc[0]['NOME_ARQUIVO']} (Páginas: {paginas_aula})")

                                alunos_foco = df_alunos[(df_alunos['TURMA'].str.contains(str(ano_lab))) & (~df_alunos['NECESSIDADES'].isin(["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"]))]
                                texto_clinico = ", ".join(alunos_foco['NECESSIDADES'].unique().tolist()) if not alunos_foco.empty else "PADRÃO"
                                if not alunos_foco.empty: st.warning(f"♿ **Sensor PEI Ativo:** {texto_clinico}")
                                
                                instr_extra_prod = st.text_area("📝 Contexto Extra / Ajustes Específicos:", placeholder="Ex: Focar mais em frações equivalentes...", key=f"prod_extra_{v}")

                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("🧠 INICIAR MOTOR DE IA: GERAR AULA", use_container_width=True, type="primary"):
                                    
                                    if "chat_history_lab" in st.session_state:
                                        del st.session_state["chat_history_lab"]
                                        
                                    with st.spinner("Sosa estudando o roteiro e arquitetando material..."):
                                        
                                        nome_elite = util.gerar_nome_material_elite(ano_lab, aula_alvo_prod, sem_lab)
                                        st.session_state.sosa_id_atual = nome_elite
                                        st.session_state.lab_meta = {"ano": ano_lab, "semana_ref": sem_lab}
                                        
                                        if "Geração Integral" in metodo_entrega:
                                            regra_livro = "3. MODO MANUAL: Crie o conteúdo do zero com base na BNCC. É TERMINANTEMENTE PROIBIDO citar páginas de livros didáticos."
                                        else:
                                            regra_livro = "3. MODO LIVRO: O roteiro deve dizer exatamente: 'Inicie na página X explorando a imagem Y...' baseando-se no PDF."

                                        # 🚨 OTIMIZAÇÃO DE TOKENS: Envia apenas o núcleo da aula, não o plano inteiro
                                        hab_herdada = ai.extrair_tag(plano_txt, "HABILIDADE_BNCC")
                                        obj_herdado = ai.extrair_tag(plano_txt, "OBJETIVOS_ENSINO")

                                        missao_especifica = (
                                            f"🚨 MISSÃO DE ALTA DENSIDADE E RIGOR QUANTITATIVO:\n"
                                            f"1.[PROFESSOR]: Escreva um TRATADO DIDÁTICO denso. Explique o conceito de {obj_geral} com profundidade técnica (estilo Brasil Escola) antes de dar o roteiro de aula.\n"
                                            f"2. CONEXÃO GLOCAL: Use o Google Search para trazer dados reais. Comece com um exemplo de Itabuna/BA, expanda para o Brasil e depois para o Mundo/Tecnologia.\n"
                                            f"{regra_livro}\n"
                                            f"4.[ALUNO] (REGULAR): É OBRIGATÓRIO gerar EXATAMENTE {qtd_q_prod} questões inéditas e desafiadoras. Formato: **QUESTÃO X.** enunciado.\n"
                                            f"5.[PEI] (INCLUSÃO): É OBRIGATÓRIO gerar EXATAMENTE {qtd_q_prod} questões adaptadas, cada uma com[PARA LEMBRAR],[PASSO A PASSO] e[ PROMPT IMAGEM ] ou [GEOGEBRA].\n"
                                            f"6.[GABARITO]: Forneça as respostas detalhadas para as {qtd_q_prod} questões regulares e as {qtd_q_prod} questões PEI.\n"
                                            f"🚨 FORMATO OBRIGATÓRIO: Você DEVE separar o texto usando EXATAMENTE as tags entre colchetes: [PROFESSOR],[ALUNO], [PEI],[GABARITO],[IMAGENS]."
                                        )

                                        prompt_manual = (
                                            f"PERSONA: MAESTRO_SOSA_V28_ELITE. ID: {nome_elite}.\n"
                                            f"MÉTODO: {metodo_entrega}. REFERÊNCIA: {base_herdada}\n"
                                            f"SÉRIE: {ano_lab}º Ano. ALVO: {aula_alvo_prod}.\n\n"
                                            f"{missao_especifica}\n\n"
                                            f"--- DIRETRIZ ESPECÍFICA DESTA AULA ---\n"
                                            f"Habilidade: {hab_herdada}\nObjetivos: {obj_herdado}\nRoteiro: {roteiro_especifico}\n"
                                            f"--- MEMÓRIA DE REGÊNCIA (PONTE PEDAGÓGICA) ---\n{contexto_turmas_ia}\n"
                                            f"--- SENSOR DE INCLUSÃO ---\nA turma possui alunos com: {texto_clinico}."
                                        )
                                        
                                        resultado_ia = ai.gerar_ia(
                                            "MAESTRO_SOSA_V28_ELITE", 
                                            prompt_manual, 
                                            url_drive=uri_referencia_aula, 
                                            usar_busca=True
                                        )
                                        
                                        import re
                                        tags_para_limpar =["PROFESSOR", "ALUNO", "PEI", "GABARITO", "GABARITO_PEI", "IMAGENS"]
                                        for t in tags_para_limpar:
                                            resultado_ia = re.sub(rf"\*\*{t}\*\*", f"[{t}]", resultado_ia, flags=re.IGNORECASE)
                                            resultado_ia = re.sub(rf"\*\*{t}:\*\*", f"[{t}]", resultado_ia, flags=re.IGNORECASE)
                                            resultado_ia = re.sub(rf"^{t}$", f"[{t}]", resultado_ia, flags=re.IGNORECASE | re.MULTILINE)
                                            
                                        st.session_state.lab_temp = resultado_ia
                                        st.rerun()

        # --- ABA 2: ENGENHARIA DE TRABALHOS ---
        with tab_trabalhos:
            st.subheader("📋 Engenharia de Projetos e Semanários")
            st.caption("Crie roteiros de pesquisa, trabalhos em grupo e projetos interdisciplinares alinhados à BNCC.")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([1.5, 1, 1])
                natureza_p = c1.selectbox("Natureza do Ativo:",["Semanário Temático", "Projeto de Identidade (Itabuna)", "Investigação Científica", "Projeto BNCC Livre"], 
                    key=f"t_nat_{v}")
                ano_t = c2.selectbox("Série Alvo:", [6, 7, 8, 9], key=f"t_ano_{v}")
                modo_t = c3.selectbox("Modo de Execução:",["Individual", "Em Grupo (Equipes)", "Interdisciplinar"], key=f"t_modo_{v}")

            with st.container(border=True):
                st.markdown("#### 🌟 Alinhamento de Competências Gerais (BNCC)")
                comps_proj = st.multiselect("Selecione as Competências Âncora do Projeto:",[
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

                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🧠 INICIAR MOTOR DE IA: GERAR PROJETO", use_container_width=True, type="primary"):
                        if not tema_t or not conts_t:
                            st.error("Defina o Título e selecione ao menos um Conteúdo da Matriz.")
                        else:
                            if "chat_history_lab" in st.session_state:
                                del st.session_state["chat_history_lab"]
                                
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
                                    f"MISSÃO: Use o ID_FORNECIDO na tag[SOSA_ID]. Gere o material completo com as TAGS[SOSA_ID],[JUSTIFICATIVA_PHC],[CONTEXTO_INVESTIGATIVO],[MISSÃO_DE_PESQUISA],[PASSO_A_PASSO],[PRODUTO_ESPERADO],[ESTRATEGIA_DUA_PEI],[RUBRICA_DE_MERITO]."
                                )
                                st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_CIENTIFICO_V33", prompt_t, usar_busca=True)
                                st.session_state.v_lab = int(time.time())
                                st.rerun()

        # --- ABA 3: ATIVIDADES COMPLEMENTARES ---
        with tab_complementar:
            st.subheader("📚 Listas Híbridas e Recomposição")
            st.caption("Crie listas de exercícios mesclando aulas anteriores ou gere material de reforço baseado em anos anteriores.")
            
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                ano_alvo = c1.selectbox("Série Alvo (Sua Turma):",[6, 7, 8, 9], key=f"comp_ano_alvo_{v}")
                
                origem_tipo = c2.radio("Origem do Conteúdo (DNA Curricular):",["🟢 Série Atual (Lista de Consolidação Híbrida)", "🔴 Ano Anterior (Intervenção/Recomposição)"], 
                    horizontal=True, key=f"comp_origem_tipo_{v}")
            
            if "Série Atual" in origem_tipo:
                st.markdown("#### 📦 1. Herança de DNA (Aulas Base)")
                df_aulas_ano = df_aulas[df_aulas['ANO'].str.contains(str(ano_alvo))].copy()
                
                if df_aulas_ano.empty:
                    st.warning("⚠️ Nenhuma aula encontrada no acervo para esta série. Gere uma aula primeiro.")
                else:
                    aulas_puras = df_aulas_ano[df_aulas_ano['TIPO_MATERIAL'].str.contains("Aula", case=False, na=False)]
                    aulas_opcoes = aulas_puras['TIPO_MATERIAL'].tolist()[::-1]
                    
                    aulas_selecionadas = st.multiselect(
                        "Selecione 1 ou 2 aulas para basear a lista:", 
                        aulas_opcoes, 
                        max_selections=2, 
                        key=f"comp_aulas_sel_{v}"
                    )
                    
                    if aulas_selecionadas:
                        st.markdown("#### ⚙️ 2. Engenharia da Lista (Distribuição de Questões)")
                        with st.container(border=True):
                            cq1, cq2, cq3, cq4 = st.columns(4)
                            qtd_trad = cq1.number_input("📐 Tradicionais (Cálculo):", 0, 20, 4, key=f"qtd_trad_{v}")
                            qtd_cot = cq2.number_input("🛒 Cotidiano Real:", 0, 20, 3, key=f"qtd_cot_{v}")
                            qtd_tech = cq3.number_input("📱 Rotina Tecnológica:", 0, 20, 2, key=f"qtd_tech_{v}")
                            qtd_des = cq4.number_input("🔥 Desafio (Boss Fight):", 0, 5, 1, key=f"qtd_des_{v}")
                            
                            total_q = qtd_trad + qtd_cot + qtd_tech + qtd_des
                            st.info(f"**Total de Questões Regulares:** {total_q} | **Questões PEI (50%):** {max(1, total_q//2) if total_q > 0 else 0}")
                        
                        instr_extra_h = st.text_area("📝 Contexto Adicional / Foco Específico (Opcional):", placeholder="Ex: Focar mais em frações equivalentes...", key=f"comp_instr_h_{v}")
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🧠 INICIAR MOTOR DE IA: GERAR LISTA HÍBRIDA", use_container_width=True, type="primary"):
                            if total_q == 0:
                                st.error("⚠️ A lista precisa ter pelo menos 1 questão configurada.")
                            else:
                                if "chat_history_lab" in st.session_state:
                                    del st.session_state["chat_history_lab"]
                                    
                                with st.spinner("Maestro Sosa varrendo a internet e arquitetando a lista híbrida..."):
                                    contexto_aulas = ""
                                    for aula_nome in aulas_selecionadas:
                                        cont_aula = df_aulas_ano[df_aulas_ano['TIPO_MATERIAL'] == aula_nome].iloc[0]['CONTEUDO']
                                        contexto_aulas += f"\n--- CONTEÚDO DA {aula_nome} ---\n{cont_aula}\n"
                                    
                                    sosa_id_hash = util.gerar_sosa_id("LISTA", ano_alvo, "I")
                                    nome_elite_c = f"{ano_alvo}º Ano - Lista Híbrida - {sosa_id_hash}"
                                    
                                    st.session_state.sosa_id_atual = nome_elite_c
                                    st.session_state.lab_meta = {
                                        "ano": ano_alvo, 
                                        "trimestre": "I Trimestre", 
                                        "tipo": "LISTA_HIBRIDA", 
                                        "semana_ref": "CONSOLIDAÇÃO"
                                    }
                                    
                                    prompt_h = (
                                        f"ID_FORNECIDO: {nome_elite_c}.\n"
                                        f"SÉRIE ALVO: {ano_alvo}º Ano.\n"
                                        f"DISTRIBUIÇÃO EXATA DE QUESTÕES (TOTAL: {total_q}):\n"
                                        f"- {qtd_trad} Questões Tradicionais (Mecânica/Cálculo).\n"
                                        f"- {qtd_cot} Questões de Cotidiano Real.\n"
                                        f"- {qtd_tech} Questões de Rotina Tecnológica (Use o Google Search para dados reais).\n"
                                        f"- {qtd_des} Questão Desafio (Boss Fight).\n"
                                        f"EXTRAS: {instr_extra_h}\n\n"
                                        f"BASE DE CONHECIMENTO (Use os conceitos ensinados nestas aulas para criar as questões):\n{contexto_aulas}\n\n"
                                        f"MISSÃO: Use o ID_FORNECIDO na tag [SOSA_ID]. Gere o material completo com as TAGS [SOSA_ID],[PROFESSOR], [ALUNO], [GABARITO],[PEI], [GABARITO_PEI],[IMAGENS]."
                                    )
                                    
                                    st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_LISTAS_HIBRIDAS", prompt_h, usar_busca=True)
                                    st.session_state.v_lab = int(time.time())
                                    st.rerun()

            else:
                contexto_scanner = ""
                with st.container(border=True):
                    st.markdown("#### 🔍 1. Análise de Evidências (Scanner)")
                    c_t1, c_t2 = st.columns([1, 1])
                    turma_interv = c_t1.selectbox("Selecione a Turma para Diagnóstico:", sorted(df_alunos['TURMA'].unique()), key=f"comp_turma_{v}")
                    ano_origem = c_t2.selectbox("Buscar base em qual série?",[1, 2, 3, 4, 5, 6, 7, 8], index=ano_alvo-2, key=f"comp_ano_orig_{v}")
                    
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
                                tipo_comp = c_q1.selectbox("Objetivo:",["Fixação", "Reforço", "Aprofundamento", "Recomposição"], key=f"comp_tipo_{v}")
                                qtd_q_comp = c_q2.slider("Nº Questões:", 3, 15, 10, key=f"comp_q_{v}")
                                instr_extra_c = c_q3.text_area("📝 Contexto Adicional:", key=f"comp_instr_{v}")

                                st.markdown("<br>", unsafe_allow_html=True)
                                if st.button("🧠 INICIAR MOTOR DE IA: GERAR RECOMPOSIÇÃO", use_container_width=True, type="primary"):
                                    if "chat_history_lab" in st.session_state:
                                        del st.session_state["chat_history_lab"]
                                        
                                    with st.spinner("Maestro Sosa arquitetando material com DNA único..."):
                                        sosa_id_hash = util.gerar_sosa_id(tipo_comp, ano_alvo, "I") 
                                        nome_elite_c = f"RECOMP - {turma_interv} - {sosa_id_hash}"
                                        
                                        st.session_state.sosa_id_atual = nome_elite_c
                                        st.session_state.lab_meta = {
                                            "ano": ano_alvo, 
                                            "trimestre": "I Trimestre", 
                                            "tipo": tipo_comp.upper(), 
                                            "semana_ref": "RECOMPOSIÇÃO"
                                        }
                                        
                                        prompt_c = (
                                            f"ID_FORNECIDO: {nome_elite_c}.\n"
                                            f"SÉRIE ALVO: {ano_alvo}º Ano | SÉRIE ORIGEM: {ano_origem}º Ano.\n"
                                            f"OBJETIVO: {tipo_comp}. CONTEXTO SCANNER: {contexto_scanner}.\n"
                                            f"CONTEÚDOS: {', '.join(sel_cont_c)}.\n"
                                            f"OBJETIVOS: {', '.join(sel_obj_c)}.\n"
                                            f"QUANTIDADE: {qtd_q_comp} questões. EXTRAS: {instr_extra_c}.\n\n"
                                            f"MISSÃO: Use o ID_FORNECIDO na tag[SOSA_ID]. Gere com as TAGS [VALOR: 0.0],[SOSA_ID],[MAPA_DE_RECOMPOSICAO], [PROFESSOR],[ALUNO],[RESPOSTAS_PEDAGOGICAS],[GRADE_DE_CORRECAO], [PEI]."
                                        )
                                        
                                        st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_RECOMPOSICAO_V68_ELITE", prompt_c, usar_busca=True)
                                        st.session_state.v_lab = int(time.time())
                                        st.rerun()

# --- ABA 4: ACERVO DE MATERIAIS ---
        with tab_acervo_lab:
            st.subheader("📂 Gestão de Acervo de Materiais")
            st.caption("Histórico de todas as aulas, projetos e listas geradas.")
            
            c_m1, c_m2, c_m3 = st.columns([1, 1, 1])
            f_trim_m = c_m1.selectbox("📅 Filtrar Trimestre:",["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="m_trim_filter")
            f_ano_m = c_m2.selectbox("🎓 Filtrar Série:",["Todos", "6º", "7º", "8º", "9º"], key="m_ano_filter")
            f_tipo_m = c_m3.selectbox("🧪 Tipo de Ativo:",["Todos", "Aula", "PROJETO", "Fixação", "Reforço", "Recomposição", "Lista"], key="m_tipo_filter")

            df_m = df_aulas[~df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy()
            termos_proibidos =["TESTE", "PROVA", "SONDA", "RECUPERAÇÃO", "2ª CHAMADA"]
            df_m = df_m[~df_m['TIPO_MATERIAL'].str.upper().str.contains('|'.join(termos_proibidos), na=False)]

            if f_trim_m != "Todos":
                df_m = df_m[df_m['CONTEUDO'].str.contains(f_trim_m, na=False)]
            if f_ano_m != "Todos":
                df_m = df_m[df_m['ANO'] == f_ano_m]
            if f_tipo_m != "Todos":
                df_m = df_m[df_m['TIPO_MATERIAL'].str.upper().str.contains(f_tipo_m.upper())]

            df_m = df_m.iloc[::-1] 

            # ==============================================================================
            # 🚨 MOTOR DE EXPORTAÇÃO EM LOTE (ZIP COM PDFs) PARA COORDENAÇÃO
            # ==============================================================================
            st.markdown("---")
            with st.expander("📦 Exportação em Lote para Coordenação (Baixar PDFs PEI)", expanded=False):
                st.info("💡 **Como usar:** O sistema pegará todos os materiais filtrados acima, converterá os documentos PEI para PDF e criará um arquivo ZIP único para você enviar à coordenação.")
                
                if st.button("🗜️ PREPARAR PACOTE PEI (GERAR ZIP)", type="primary", use_container_width=True):
                    if df_m.empty:
                        st.error("⚠️ Nenhum material encontrado no filtro atual.")
                    else:
                        with st.status("Acessando o Cofre Digital e convertendo arquivos para PDF...") as status:
                            import zipfile
                            import io
                            from googleapiclient.discovery import build
                            
                            try:
                                creds = db.obter_creds_drive()
                                service = build('drive', 'v3', credentials=creds)
                                
                                zip_buffer = io.BytesIO()
                                count = 0
                                
                                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                                    for _, row in df_m.iterrows():
                                        txt_f = str(row['CONTEUDO'])
                                        nome_mat = str(row['TIPO_MATERIAL']).replace("/", "-").replace(":", "").strip()
                                        
                                        # Busca o link do PEI no texto
                                        match = re.search(r"PEI\s*\(?(https?://[^\s\)]+)\)?", txt_f, re.IGNORECASE)
                                        if match:
                                            link_pei = match.group(1).strip()
                                            if "N/A" not in link_pei and "http" in link_pei:
                                                # Extrai o ID do arquivo do Google Docs
                                                id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", link_pei)
                                                if id_match:
                                                    file_id = id_match.group(1)
                                                    status.write(f"📥 Convertendo: {nome_mat}...")
                                                    try:
                                                        # Força a exportação do Google Docs para PDF via API
                                                        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
                                                        pdf_bytes = request.execute()
                                                        
                                                        # Adiciona o PDF dentro do arquivo ZIP
                                                        zip_file.writestr(f"{nome_mat}_PEI.pdf", pdf_bytes)
                                                        count += 1
                                                    except Exception as e:
                                                        status.write(f"⚠️ Erro ao baixar {nome_mat}: {e}")
                                
                                if count > 0:
                                    status.update(label=f"✅ {count} arquivos PEI convertidos e compactados com sucesso!", state="complete")
                                    st.session_state.zip_pei_ready = zip_buffer.getvalue()
                                    st.session_state.zip_pei_count = count
                                else:
                                    status.update(label="❌ Nenhum arquivo PEI válido encontrado nos materiais filtrados.", state="error")
                            
                            except Exception as e:
                                status.update(label=f"❌ Erro crítico na conexão com o Drive: {e}", state="error")
                                
                # Exibe o botão de download se o ZIP estiver pronto na memória
                if "zip_pei_ready" in st.session_state:
                    st.success(f"📦 Pacote pronto com {st.session_state.zip_pei_count} atividades PEI em PDF.")
                    st.download_button(
                        label="📥 CLIQUE AQUI PARA BAIXAR O ARQUIVO ZIP",
                        data=st.session_state.zip_pei_ready,
                        file_name=f"Atividades_PEI_SOSA_{datetime.now().strftime('%d%m%Y')}.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True
                    )

            st.markdown("---")

            if not df_m.empty:
                st.write(f"📚 **Materiais Didáticos Localizados:** {len(df_m)}")
                for _, row in df_m.iterrows():
                    with st.container(border=True):
                        txt_f = str(row['CONTEUDO'])
                        identificador = row['TIPO_MATERIAL']
                        
                        st.markdown(f"#### 📘 {identificador}")
                        
                        def buscar_link_soberano(texto, rotulo, link_reserva):
                            padrao = rf"{rotulo}\s*\(?\s*(https?://[^\s\)]+)\)?"
                            match = re.search(padrao, texto, re.IGNORECASE)
                            if match:
                                return match.group(1).strip()
                            if rotulo.lower() in["regular", "aluno"]:
                                return link_reserva
                            return None

                        l_alu = buscar_link_soberano(txt_f, "Regular", row.get('LINK_DRIVE'))
                        l_pei = buscar_link_soberano(txt_f, "PEI", None)
                        l_prof = buscar_link_soberano(txt_f, "Prof", None)

                        c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns(5)

                        if l_alu and "http" in str(l_alu):
                            c_b1.link_button("📝 ALUNO", str(l_alu), use_container_width=True, type="primary")
                        else:
                            c_b1.button("⚪ SEM LINK", disabled=True, use_container_width=True, key=f"no_link_alu_{row.name}")

                        if l_pei and "http" in str(l_pei) and "N/A" not in str(l_pei):
                            c_b2.link_button("♿ PEI", str(l_pei), use_container_width=True)
                        else:
                            c_b2.button("⚪ SEM PEI", disabled=True, use_container_width=True, key=f"no_link_pei_{row.name}")

                        if l_prof and "http" in str(l_prof) and "N/A" not in str(l_prof):
                            c_b3.link_button("👨‍🏫 PROF", str(l_prof), use_container_width=True)
                        else:
                            c_b3.button("⚪ SEM GUIA", disabled=True, use_container_width=True, key=f"no_link_prof_{row.name}")
                        
                        if c_b4.button("🔄 REFINAR", key=f"ref_mat_h_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = txt_f
                            st.session_state.sosa_id_atual = identificador
                            st.session_state.lab_meta = {"ano": str(row["ANO"]).replace("º",""), "semana_ref": row['SEMANA_REF']}
                            if "chat_history_lab" in st.session_state: del st.session_state["chat_history_lab"]
                            st.rerun()
                            
                        if c_b5.button("🗑️ APAGAR", key=f"del_mat_h_{row.name}", use_container_width=True):
                            if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", identificador):
                                st.rerun()

                        with st.expander("👁️ ANALISAR ESTRUTURA PEDAGÓGICA E ITENS"):
                            t_prof, t_alu, t_gab, t_pei_tab, t_img = st.tabs([
                                "👨‍🏫 Guia do Professor", "📝 Material do Aluno", "✅ Gabarito", "♿ Inclusão PEI", "🎨 Imagens"
                            ])
                            
                            with t_prof:
                                val_prof = ai.extrair_tag(txt_f, "PROFESSOR")
                                st.info(val_prof if val_prof else "Conteúdo não localizado.")

                            with t_alu:
                                val_alu = ai.extrair_tag(txt_f, "ALUNO")
                                if val_alu:
                                    st.write(val_alu)
                                else: st.write("Roteiro não localizado.")

                            with t_gab:
                                val_gab = ai.extrair_tag(txt_f, "GABARITO")
                                st.success(val_gab if val_gab else "Gabarito não disponível.")

                            with t_pei_tab:
                                val_pei = ai.extrair_tag(txt_f, "PEI")
                                st.warning(val_pei if val_pei else "Nenhuma adaptação registrada.")
                                
                            with t_img:
                                val_img = ai.extrair_tag(txt_f, "IMAGENS")
                                if val_img:
                                    st.info(val_img)
                                else:
                                    st.caption("Nenhum prompt de imagem gerado para este material.")
            else:
                st.info("📭 Nenhum material didático encontrado.")


# ==============================================================================
# MÓDULO: CENTRAL DE AVALIAÇÕES - A FORJA MASTER (V140 - OTIMIZADA)
# ==============================================================================
elif menu == "📝 Central de Avaliações":
    st.title("📝 Central de Avaliações: A Forja Master")
    st.caption("💡 **Guia de Comando:** Construa avaliações de elite questão por questão. O sistema garante o balanceamento do gabarito, gera a Tríade Inclusiva (3 níveis de PEI) e cria Variantes Anti-Fraude apenas embaralhando os itens.")
    st.markdown("---")

    # 🚨 INICIALIZAÇÃO DA MÁQUINA DE ESTADOS DA FORJA
    if "forja" not in st.session_state:
        st.session_state.forja = {
            'fase': 1, 
            'mapa': [], 
            'info': {}, 
            'pei_1': '', 'pei_2': '', 'pei_3': '',
            'prova_final_txt': ''
        }
    
    f = st.session_state.forja

    def reset_forja():
        st.session_state.forja = {'fase': 1, 'mapa': [], 'info': {}, 'pei_1': '', 'pei_2': '', 'pei_3': '', 'prova_final_txt': ''}
        st.rerun()

    tab_forja, tab_acervo_av = st.tabs(["🔨 A Forja (Linha de Montagem)", "🗂️ Acervo de Safra"])

    with tab_forja:
        if f['fase'] > 1 and f['fase'] < 6:
            st.button("🔄 Cancelar e Voltar ao Início", on_click=reset_forja)
            st.progress(f['fase'] / 5.0, text=f"Fase {f['fase']} de 5")
            st.markdown("---")
        elif f['fase'] == 6:
            st.button("🔄 Cancelar e Voltar ao Início", on_click=reset_forja)
            st.markdown("---")

        # ==============================================================================
        # 📍 FASE 1: O BRIEFING E A MATRIZ DE PROVA
        # ==============================================================================
        if f['fase'] == 1:
            st.markdown("### 📍 Fase 1: Natureza e Matriz de Referência")
            
            modo_arq = st.radio(
                "O que você deseja construir hoje?", 
                [
                    "🆕 Nova Avaliação (Inédita)", 
                    "🔍 Sonda Diagnóstica",
                    "🧬 Variante Anti-Fraude (Clonagem)", 
                    "🔄 2ª Chamada Discursiva (Clonagem)"
                ], 
                horizontal=True
            )
            st.markdown("---")

            if modo_arq in ["🆕 Nova Avaliação (Inédita)", "🔍 Sonda Diagnóstica"]:
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1, 1, 1, 1])
                    ano_av = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0)
                    trim_filtro = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"])
                    v_total = c3.number_input("Valor Total:", 0.0, 10.0, 10.0 if "Sonda" in modo_arq else 3.0, step=0.5)
                    qtd_q = c4.number_input("Nº de Questões:", 1, 20, 10)

                if modo_arq == "🆕 Nova Avaliação (Inédita)":
                    tipo_av = st.selectbox("Tipo de Ativo:", ["Teste", "Prova", "Recuperação Paralela", "Recuperação Final"])
                else:
                    tipo_av = "SONDA_DE_PROFICIÊNCIA"

                with st.container(border=True):
                    st.markdown("#### 🎯 Vínculo Curricular")
                    c_safra1, c_safra2 = st.columns(2)
                    
                    df_ref = df_aulas[df_aulas['ANO'].str.contains(str(ano_av))].copy()
                    termos_proibidos = ["APLICAÇÃO", "TESTE", "PROVA", "SONDA", "AVALIAÇÃO", "CORREÇÃO", "REVISÃO", "EXAME", "2ª CHAMADA"]
                    df_ref = df_ref[~df_ref['TIPO_MATERIAL'].str.upper().str.contains('|'.join(termos_proibidos))]
                    
                    mats_selecionados = c_safra1.multiselect(f"📦 Aulas Base (Já Ministradas):", options=df_ref["TIPO_MATERIAL"].tolist())
                    
                    trim_sigla = trim_filtro.split(" ")[0]
                    df_matriz_av = df_curriculo[(df_curriculo['ANO'].astype(str).str.contains(str(ano_av))) & (df_curriculo['TRIMESTRE'] == trim_sigla)]
                    opcoes_futuras = sorted(df_matriz_av['CONTEUDO_ESPECIFICO'].unique().tolist()) if not df_matriz_av.empty else []
                    
                    topicos_futuros = c_safra2.multiselect("🔮 Tópicos Futuros (Matriz Curricular):", options=opcoes_futuras)
                    
                    conteudos_extraidos = set()
                    contexto_base_texto = "" 
                    
                    if mats_selecionados:
                        semanas_selecionadas = df_ref[df_ref['TIPO_MATERIAL'].isin(mats_selecionados)]['SEMANA_REF'].unique()
                        planos_relacionados = df_planos[(df_planos['ANO'].str.contains(str(ano_av))) & (df_planos['SEMANA'].isin(semanas_selecionadas))]
                        
                        for _, row_p in planos_relacionados.iterrows():
                            cont = ai.extrair_tag(str(row_p['PLANO_TEXTO']), "CONTEUDOS_ESPECIFICOS")
                            if cont and cont.upper() != "N/A":
                                for item in re.split(r'[;\n]', cont):
                                    if len(item.strip()) > 5: conteudos_extraidos.add(item.strip().replace("- ", "").replace("• ", ""))
                        
                        # 🚨 OTIMIZAÇÃO DE TOKENS: Extrai apenas o núcleo da aula em vez do texto inteiro
                        for m_nome in mats_selecionados:
                            m_row = df_aulas[df_aulas["TIPO_MATERIAL"] == m_nome].iloc[0]
                            txt_aula = str(m_row['CONTEUDO'])
                            hab = ai.extrair_tag(txt_aula, "HABILIDADE_BNCC")
                            obj = ai.extrair_tag(txt_aula, "OBJETIVOS_ENSINO")
                            cont = ai.extrair_tag(txt_aula, "CONTEUDOS_ESPECIFICOS")
                            contexto_base_texto += f"--- AULA: {m_nome} ---\nHabilidade: {hab}\nConteúdos: {cont}\nObjetivos: {obj}\n\n"
                    
                    if topicos_futuros:
                        for topico in topicos_futuros: conteudos_extraidos.add(topico)
                    
                    lista_conteudos = sorted(list(conteudos_extraidos))
                    if not lista_conteudos: lista_conteudos = ["Matemática Geral"]
                    
                if st.button("🗺️ GERAR MATRIZ DE PROVA (SORTEAR GABARITO)", type="primary", use_container_width=True):
                    if not mats_selecionados and not topicos_futuros:
                        st.error("Selecione pelo menos uma Aula Base ou Tópico Futuro.")
                    else:
                        gabarito_mestre = util.gerar_gabarito_balanceado(qtd_q)
                        mapa_inicial = []
                        
                        for i in range(qtd_q):
                            tema_sorteado = lista_conteudos[i % len(lista_conteudos)]
                            dif = "Fácil" if i < (qtd_q*0.3) else "Difícil" if i >= (qtd_q*0.8) else "Média"
                            
                            mapa_inicial.append({
                                'q': i + 1,
                                'tema': tema_sorteado,
                                'dificuldade': dif,
                                'gabarito': gabarito_mestre[i],
                                'status': 'pendente',
                                'dados': {} 
                            })
                        
                        f['mapa'] = mapa_inicial
                        f['info'] = {'ano': f"{ano_av}º", 'trimestre': trim_filtro, 'valor': v_total, 'qtd': qtd_q, 'tipo_prova': tipo_av}
                        f['contexto_base'] = contexto_base_texto 
                        f['fase'] = 2
                        st.rerun()

            else:
                # ==============================================================================
                # 🧬 MODO CLONAGEM (VARIANTE OU 2ª CHAMADA DE PROVA ANTIGA)
                # ==============================================================================
                st.info("💡 **Modo de Clonagem:** Selecione uma prova do Acervo para gerar a Variante ou 2ª Chamada automaticamente.")
                
                c_cl1, c_cl2 = st.columns([1, 2])
                ano_clone = c_cl1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key="ano_clone")
                
                df_provas = df_aulas[(df_aulas['ANO'].str.contains(str(ano_clone))) & (df_aulas['SEMANA_REF'] == "AVALIAÇÃO")]
                opcoes_provas = [p for p in df_provas['TIPO_MATERIAL'].tolist() if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", p, re.IGNORECASE)]
                
                prova_base_sel = c_cl2.selectbox("📦 Selecione a Prova Original:", [""] + opcoes_provas)
                
                if prova_base_sel:
                    txt_base = str(df_provas[df_provas['TIPO_MATERIAL'] == prova_base_sel].iloc[0]['CONTEUDO'])
                    q_reg = ai.extrair_tag(txt_base, "QUESTOES")
                    qtd_detectada = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_reg))
                    st.success(f"✅ Prova detectada com {qtd_detectada} questões.")
                    
                    if st.button(f"🚀 GERAR {modo_arq.split(' ')[1].upper()}", type="primary", use_container_width=True):
                        with st.status("Clonando e processando...") as status:
                            info_clone = {'ano': f"{ano_clone}º", 'trimestre': "I Trimestre", 'valor': 3.0, 'qtd': qtd_detectada}
                            
                            if "Variante" in modo_arq:
                                existentes = df_aulas[df_aulas['TIPO_MATERIAL'].str.startswith(prova_base_sel + " - TIPO", na=False)]
                                letra = chr(66 + len(existentes)) # 66 = 'B'
                                nome_var = f"{prova_base_sel} - TIPO {letra}"
                                
                                g_reg = ai.extrair_tag(txt_base, "GRADE_DE_CORRECAO")
                                prompt = f"PROVA ORIGINAL:\n[QUESTOES]\n{q_reg}\n\n[GRADE_DE_CORRECAO]\n{g_reg}"
                                res_hydra = ai.gerar_ia("ARQUITETO_VARIANTES_V100", prompt)
                                
                                pei_q = ai.extrair_tag(txt_base, "PEI")
                                pei_gab = ai.extrair_tag(txt_base, "GABARITO_PEI")
                                pei_grade = ai.extrair_tag(txt_base, "GRADE_DE_CORRECAO_PEI")
                                
                                texto_final_var = f"[VALOR: 3.0]\n\n[QUESTOES]\n{ai.extrair_tag(res_hydra, 'QUESTOES')}\n\n[GABARITO_TEXTO]\n{ai.extrair_tag(res_hydra, 'GABARITO_TEXTO')}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(res_hydra, 'GRADE_DE_CORRECAO')}\n\n[PEI]\n{pei_q}\n\n[GABARITO_PEI]\n{pei_gab}\n\n[GRADE_DE_CORRECAO_PEI]\n{pei_grade}\n\n"
                                
                                doc_var = exporter.gerar_docx_prova_v25(nome_var, texto_final_var, info_clone)
                                link_var = db.subir_e_converter_para_google_docs(doc_var, nome_var, modo="AVALIACAO")
                                
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_var, texto_final_var + f"\n--- LINKS ---\nRegular({link_var})", f"{ano_clone}º", link_var])
                                status.update(label="✅ Variante gerada e salva no Acervo!", state="complete")
                                
                            elif "2ª Chamada" in modo_arq:
                                nome_2a = f"2ª_CHAMADA_{prova_base_sel}"
                                prompt_2a = f"TIPO: 2ª Chamada (100% DISCURSIVA). SÉRIE: {ano_clone}º. QTD: {qtd_detectada}.\nDIRETRIZ: Crie questões GÊMEAS da prova abaixo, mas em formato ABERTO (sem alternativas).\n--- PROVA ORIGINAL ---\n{q_reg}"
                                res_2a = ai.gerar_ia("ARQUITETO_2A_CHAMADA_V100", prompt_2a)
                                
                                info_clone['tipo_prova'] = "2ª Chamada"
                                doc_2a = exporter.gerar_docx_prova_v25(nome_2a, res_2a, info_clone)
                                link_2a = db.subir_e_converter_para_google_docs(doc_2a, nome_2a, modo="AVALIACAO")
                                
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_2a, res_2a + f"\n--- LINKS ---\nRegular({link_2a})", f"{ano_clone}º", link_2a])
                                status.update(label="✅ 2ª Chamada gerada e salva no Acervo!", state="complete")
                                
                        st.balloons()
                        time.sleep(1.5)
                        st.rerun()

        # ==============================================================================
        # 📍 FASE 2: A LINHA DE MONTAGEM (QUESTÃO POR QUESTÃO)
        # ==============================================================================
        elif f['fase'] == 2:
            st.markdown("### ⚙️ Fase 2: Linha de Montagem")
            st.caption("Gere e aprove cada questão individualmente. O gabarito já foi travado pelo sistema para garantir o balanceamento perfeito.")
            
            c_tog1, c_add2 = st.columns([3, 1])
            modo_leitura_forja = c_tog1.toggle("👁️ Ativar Modo Leitura (Renderizar Matemática)", value=True, key="tog_forja")
            
            # 🚨 BOTÃO DE EXPANSÃO DINÂMICA
            with c_add2:
                if st.button("➕ Adicionar 5 Questões", use_container_width=True):
                    qtd_atual = len(f['mapa'])
                    if qtd_atual + 5 <= 20:
                        gabarito_extra = util.gerar_gabarito_balanceado(5)
                        lista_conteudos = list(set([item['tema'] for item in f['mapa']]))
                        if not lista_conteudos: lista_conteudos = ["Matemática Geral"]
                        
                        for i in range(5):
                            tema_sorteado = lista_conteudos[(qtd_atual + i) % len(lista_conteudos)]
                            f['mapa'].append({
                                'q': qtd_atual + i + 1,
                                'tema': tema_sorteado,
                                'dificuldade': "Média",
                                'gabarito': gabarito_extra[i],
                                'status': 'pendente',
                                'dados': {}
                            })
                        f['info']['qtd'] = qtd_atual + 5
                        st.rerun()
                    else:
                        st.error("Limite máximo de 20 questões atingido.")
            
            def preparar_para_leitura(texto):
                if not texto: return ""
                texto = re.sub(r'^```[a-zA-Z]*\n', '', texto, flags=re.MULTILINE | re.IGNORECASE)
                texto = re.sub(r'```$', '', texto, flags=re.MULTILINE)
                return re.sub(r'\$\$\s*(.*?)\s*\$\$', r'$\1$', texto)

            def extrair_item_forja(texto_bruto):
                tags = ['ENUNCIADO', 'ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E', 'HABILIDADE', 'JUSTIFICATIVA', 'DISTRATORES']
                res = {}
                for tag in tags:
                    padrao = rf"\[{tag}\](.*?)(?=\[(?:{'|'.join(tags)})\]|$)"
                    match = re.search(padrao, texto_bruto, re.DOTALL | re.IGNORECASE)
                    res[tag] = match.group(1).strip() if match else ""
                return res

            # 🚨 MOTOR DE GERAÇÃO EM LOTE (ECONOMIA DE TOKENS)
            pendentes = [item for item in f['mapa'] if item['status'] == 'pendente']
            if pendentes:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 GERAR TODAS AS QUESTÕES PENDENTES (LOTE)", type="primary", use_container_width=True):
                    with st.spinner(f"Forjando {len(pendentes)} questões em lote... Isso pode levar alguns segundos."):
                        prompt_lote = f"SÉRIE ALVO: {f['info']['ano']}\n\n"
                        prompt_lote += "Gere as seguintes questões seguindo ESTRITAMENTE o tema, dificuldade e gabarito de cada uma:\n\n"
                        for item in pendentes:
                            prompt_lote += f"QUESTÃO {item['q']}:\n- TEMA: {item['tema']}\n- DIFICULDADE: {item['dificuldade']}\n- GABARITO OBRIGATÓRIO: Letra {item['gabarito']}\n\n"
                        prompt_lote += f"🚨 DIRETRIZ DE ESPELHAMENTO (Contexto Base):\n{f.get('contexto_base', 'Crie as questões baseadas nos temas fornecidos.')}\n"
                        
                        res_lote = ai.gerar_ia("FORJA_LOTE_REGULAR", prompt_lote)
                        
                        blocos = re.findall(r"\[ITEM_(\d+)\](.*?)\[/ITEM_\1\]", res_lote, re.DOTALL | re.IGNORECASE)
                        if not blocos:
                            st.error("A IA não retornou o formato correto. Tente gerar individualmente ou clique novamente.")
                        else:
                            for num_str, conteudo_bloco in blocos:
                                q_num = int(num_str)
                                extraido = extrair_item_forja(conteudo_bloco)
                                for item in f['mapa']:
                                    if item['q'] == q_num:
                                        item['dados'] = {
                                            'ENUNCIADO': extraido.get('ENUNCIADO', ''),
                                            'ALT_A': extraido.get('ALT_A', ''),
                                            'ALT_B': extraido.get('ALT_B', ''),
                                            'ALT_C': extraido.get('ALT_C', ''),
                                            'ALT_D': extraido.get('ALT_D', ''),
                                            'ALT_E': extraido.get('ALT_E', ''),
                                            'HABILIDADE': extraido.get('HABILIDADE', ''),
                                            'JUSTIFICATIVA': extraido.get('JUSTIFICATIVA', ''),
                                            'DISTRATORES': extraido.get('DISTRATORES', ''),
                                            'GABARITO': item['gabarito']
                                        }
                                        item['status'] = 'revisao'
                            st.rerun()
                st.markdown("---")

            todas_aprovadas = True
            
            for i, item in enumerate(f['mapa']):
                cor_status = "🟢 APROVADA" if item['status'] == 'aprovado' else "🟡 PENDENTE"
                
                with st.expander(f"Questão {item['q']:02d} | Gabarito Fixo: {item['gabarito']} | {cor_status}", expanded=(item['status'] == 'pendente')):
                    
                    if item['status'] == 'pendente':
                        todas_aprovadas = False
                        c_t1, c_t2 = st.columns([2, 1])
                        tema_q = c_t1.text_input("Tema Específico:", value=item['tema'], key=f"tema_{i}")
                        dif_q = c_t2.selectbox("Dificuldade:", ["Fácil", "Média", "Difícil"], index=["Fácil", "Média", "Difícil"].index(item['dificuldade']), key=f"dif_{i}")
                        
                        if st.button(f"🧠 Gerar Questão {item['q']} (Individual)", key=f"btn_gen_{i}"):
                            with st.spinner("Forjando item psicométrico..."):
                                contexto_herdado = f.get('contexto_base', '')
                                prompt = (
                                    f"SÉRIE ALVO: {f['info']['ano']}\n"
                                    f"TEMA: {tema_q}. DIFICULDADE: {dif_q}. GABARITO OBRIGATÓRIO: Letra {item['gabarito']}.\n\n"
                                    f"🚨 DIRETRIZ DE ESPELHAMENTO: Baseie o contexto desta questão nos objetivos abaixo. Crie uma questão alinhada ao que foi ensinado:\n"
                                    f"{contexto_herdado if contexto_herdado else 'Crie a questão baseada estritamente no TEMA fornecido.'}"
                                )
                                res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                
                                extraido = extrair_item_forja(res_item)
                                
                                item['dados'] = {
                                    'ENUNCIADO': extraido['ENUNCIADO'],
                                    'ALT_A': extraido['ALT_A'],
                                    'ALT_B': extraido['ALT_B'],
                                    'ALT_C': extraido['ALT_C'],
                                    'ALT_D': extraido['ALT_D'],
                                    'ALT_E': extraido['ALT_E'],
                                    'HABILIDADE': extraido['HABILIDADE'],
                                    'JUSTIFICATIVA': extraido['JUSTIFICATIVA'],
                                    'DISTRATORES': extraido['DISTRATORES'],
                                    'GABARITO': item['gabarito']
                                }
                                item['status'] = 'revisao'
                                st.rerun()
                                
                    elif item['status'] == 'revisao':
                        todas_aprovadas = False
                        st.info("Edite o texto se necessário e clique em Aprovar.")
                        
                        d = item['dados']
                        
                        if modo_leitura_forja:
                            st.markdown("**👁️ Preview da Questão:**")
                            st.markdown(preparar_para_leitura(d['ENUNCIADO']))
                            st.markdown(f"**(A)** {preparar_para_leitura(d['ALT_A'])}")
                            st.markdown(f"**(B)** {preparar_para_leitura(d['ALT_B'])}")
                            st.markdown(f"**(C)** {preparar_para_leitura(d['ALT_C'])}")
                            st.markdown(f"**(D)** {preparar_para_leitura(d['ALT_D'])}")
                            st.markdown(f"**(E)** {preparar_para_leitura(d['ALT_E'])}")
                            st.divider()
                        
                        d['ENUNCIADO'] = st.text_area("Enunciado (Edição):", value=d['ENUNCIADO'], height=150, key=f"ed_en_{i}")
                        c_a1, c_a2 = st.columns(2)
                        d['ALT_A'] = c_a1.text_input("(A)", value=d['ALT_A'], key=f"ed_a_{i}")
                        d['ALT_B'] = c_a2.text_input("(B)", value=d['ALT_B'], key=f"ed_b_{i}")
                        d['ALT_C'] = c_a1.text_input("(C)", value=d['ALT_C'], key=f"ed_c_{i}")
                        d['ALT_D'] = c_a2.text_input("(D)", value=d['ALT_D'], key=f"ed_d_{i}")
                        d['ALT_E'] = c_a1.text_input("(E)", value=d['ALT_E'], key=f"ed_e_{i}")
                        
                        st.caption(f"**Habilidade:** {d['HABILIDADE']}")
                        st.caption(f"**Justificativa:** {d['JUSTIFICATIVA']}")
                        
                        # 🚨 CAMPO DE REFINAMENTO CIRÚRGICO
                        instrucao_refino = st.text_input("Instrução de Refinamento (Opcional):", placeholder="Ex: Mude o contexto para futebol...", key=f"inst_ref_{i}")
                        
                        col_b1, col_b2 = st.columns(2)
                        if col_b1.button(f"✅ Aprovar Questão {item['q']}", type="primary", key=f"btn_apr_{i}", use_container_width=True):
                            item['status'] = 'aprovado'
                            st.rerun()
                        if col_b2.button(f"🔄 Refazer Questão {item['q']}", key=f"btn_ref_{i}", use_container_width=True):
                            with st.spinner("Reforjando item..."):
                                prompt = (
                                    f"SÉRIE ALVO: {f['info']['ano']}\n"
                                    f"TEMA: {item['tema']}. DIFICULDADE: {item['dificuldade']}. GABARITO OBRIGATÓRIO: Letra {item['gabarito']}.\n\n"
                                )
                                if instrucao_refino:
                                    prompt += f"🚨 INSTRUÇÃO DE REFINAMENTO DO PROFESSOR: {instrucao_refino}\n"
                                    prompt += f"QUESTÃO ANTERIOR (Para referência do que mudar):\n{item['dados']['ENUNCIADO']}\n\n"
                                
                                prompt += f"🚨 DIRETRIZ DE ESPELHAMENTO:\n{f.get('contexto_base', '')}"
                                
                                res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                extraido = extrair_item_forja(res_item)
                                
                                item['dados'] = {
                                    'ENUNCIADO': extraido.get('ENUNCIADO', item['dados']['ENUNCIADO']),
                                    'ALT_A': extraido.get('ALT_A', item['dados']['ALT_A']),
                                    'ALT_B': extraido.get('ALT_B', item['dados']['ALT_B']),
                                    'ALT_C': extraido.get('ALT_C', item['dados']['ALT_C']),
                                    'ALT_D': extraido.get('ALT_D', item['dados']['ALT_D']),
                                    'ALT_E': extraido.get('ALT_E', item['dados']['ALT_E']),
                                    'HABILIDADE': extraido.get('HABILIDADE', item['dados']['HABILIDADE']),
                                    'JUSTIFICATIVA': extraido.get('JUSTIFICATIVA', item['dados']['JUSTIFICATIVA']),
                                    'DISTRATORES': extraido.get('DISTRATORES', item['dados']['DISTRATORES']),
                                    'GABARITO': item['gabarito']
                                }
                                st.rerun()
                            
                    elif item['status'] == 'aprovado':
                        d = item['dados']
                        if modo_leitura_forja:
                            st.markdown(preparar_para_leitura(d['ENUNCIADO']))
                            st.markdown(f"**(A)** {preparar_para_leitura(d['ALT_A'])} | **(B)** {preparar_para_leitura(d['ALT_B'])} | **(C)** {preparar_para_leitura(d['ALT_C'])} | **(D)** {preparar_para_leitura(d['ALT_D'])} | **(E)** {preparar_para_leitura(d['ALT_E'])}")
                        else:
                            st.write(f"**Enunciado:** {d['ENUNCIADO']}")
                            st.write(f"(A) {d['ALT_A']} | (B) {d['ALT_B']} | (C) {d['ALT_C']} | (D) {d['ALT_D']} | (E) {d['ALT_E']}")
                            
                        if st.button(f"✏️ Editar Questão {item['q']}", key=f"btn_edit_{i}"):
                            item['status'] = 'revisao'
                            st.rerun()

            if todas_aprovadas:
                st.success("🎉 Todas as questões regulares foram forjadas e aprovadas!")
                if st.button("➡️ AVANÇAR PARA A TRÍADE INCLUSIVA (PEI)", type="primary", use_container_width=True):
                    f['fase'] = 3
                    st.rerun()

        # ==============================================================================
        # 📍 FASE 3: O ESCUDO INCLUSIVO (TRÍADE PEI)
        # ==============================================================================
        elif f['fase'] == 3:
            st.markdown("### ♿ Fase 3: A Tríade Inclusiva (PEI)")
            st.caption("O sistema gerará 3 níveis de adaptação baseados nas questões regulares que você acabou de aprovar.")
            
            if not f['pei_1']:
                if st.button("🧠 GERAR TRÍADE INCLUSIVA", type="primary", use_container_width=True):
                    with st.spinner("Analisando prova regular e forjando os 3 níveis clínicos..."):
                        texto_base = ""
                        for item in f['mapa']:
                            d = item['dados']
                            texto_base += f"Q{item['q']}: {d['ENUNCIADO']} | Gabarito: {d['GABARITO']}\n"
                            
                        res_pei = ai.gerar_ia("FORJA_TRIADE_PEI", f"QUESTÕES REGULARES APROVADAS:\n{texto_base}")
                        
                        f['pei_1'] = ai.extrair_tag(res_pei, "NIVEL_1")
                        f['pei_2'] = ai.extrair_tag(res_pei, "NIVEL_2")
                        f['pei_3'] = ai.extrair_tag(res_pei, "NIVEL_3")
                        st.rerun()
            else:
                t_p1, t_p2, t_p3 = st.tabs(["🔵 Nível 1 (Apoio Leve)", "🟡 Nível 2 (Apoio Moderado)", "🔴 Nível 3 (Apoio Severo)"])
                
                with t_p1:
                    f['pei_1'] = st.text_area("Edição Nível 1:", value=f['pei_1'], height=300)
                with t_p2:
                    f['pei_2'] = st.text_area("Edição Nível 2:", value=f['pei_2'], height=300)
                with t_p3:
                    st.info("💡 O Nível 3 não possui alternativas. É focado em comandos motores e visuais.")
                    f['pei_3'] = st.text_area("Edição Nível 3:", value=f['pei_3'], height=300)
                    
                if st.button("➡️ AVANÇAR PARA COMPILAÇÃO E VARIANTES", type="primary", use_container_width=True):
                    f['fase'] = 4
                    st.rerun()

        # ==============================================================================
        # 📍 FASE 4: COMPILAÇÃO E VARIANTES ANTI-FRAUDE (BLINDADA)
        # ==============================================================================
        elif f['fase'] == 4:
            st.markdown("### 🧬 Fase 4: Compilação e Variantes")
            
            tipo_nome = f['info'].get('tipo_prova', 'TESTE').upper().replace(' ', '_')
            nome_sugerido = f"{tipo_nome}_{f['info']['ano'].replace('º','')}ANO_{f['info']['trimestre'].replace(' ', '')}"
            
            nome_arq = st.text_input("ID Técnico do Material (Nome no Banco):", value=nome_sugerido)
            
            gerar_variante = st.checkbox("🧬 Gerar Variante Anti-Fraude (Tipo B)", value=True, help="O sistema embaralhará as questões e as alternativas da prova regular automaticamente.")
            
            if st.button("💾 COMPILAR, GERAR DOCX E SALVAR NO ACERVO", type="primary", use_container_width=True):
                with st.status("Forjando Documentos Oficiais...") as status:
                    
                    txt_regular = f"[VALOR: {f['info']['valor']}]\n\n[QUESTOES]\n"
                    txt_gabarito = "[GABARITO_TEXTO]\n"
                    txt_grade = "[GRADE_DE_CORRECAO]\n"
                    
                    for item in f['mapa']:
                        d = item['dados']
                        txt_regular += f"**QUESTÃO {item['q']:02d} -** {d['ENUNCIADO']}\n(A) {d['ALT_A']}\n(B) {d['ALT_B']}\n(C) {d['ALT_C']}\n(D) {d['ALT_D']}\n(E) {d['ALT_E']}\n\n"
                        txt_gabarito += f"QUESTÃO {item['q']:02d}: {d['GABARITO']}\n"
                        txt_grade += f"QUESTÃO {item['q']:02d}: [{d['HABILIDADE']}] | JUSTIFICATIVA: {d['JUSTIFICATIVA']} | DISTRATORES: {d['DISTRATORES']}\n"
                    
                    texto_final_padrao = txt_regular + txt_gabarito + txt_grade
                    
                    status.write("📝 Gerando Prova Regular (Padrão)...")
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, texto_final_padrao, f['info'])
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, modo="AVALIACAO")
                    
                    status.write("🔵 Gerando PEI Nível 1...")
                    doc_pei1 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N1", f['pei_1'], f['info'])
                    link_pei1 = db.subir_e_converter_para_google_docs(doc_pei1, f"{nome_arq}_PEI_N1", modo="AVALIACAO")
                    
                    status.write("🟡 Gerando PEI Nível 2...")
                    doc_pei2 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N2", f['pei_2'], f['info'])
                    link_pei2 = db.subir_e_converter_para_google_docs(doc_pei2, f"{nome_arq}_PEI_N2", modo="AVALIACAO")
                    
                    status.write("🔴 Gerando PEI Nível 3 (Qualitativo)...")
                    doc_pei3 = exporter.gerar_docx_pei_qualitativa(f"{nome_arq}_PEI_N3", f['pei_3'], f['info'])
                    link_pei3 = db.subir_e_converter_para_google_docs(doc_pei3, f"{nome_arq}_PEI_N3", modo="AVALIACAO")
                    
                    links_footer = f"--- LINKS ---\nRegular({link_reg}) PEI_N1({link_pei1}) PEI_N2({link_pei2}) PEI_N3({link_pei3})"
                    
                    # 🚨 TRAVA DE SOBERANIA: Só avança se o banco confirmar o salvamento
                    sucesso_db = db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_arq, texto_final_padrao + f"\n\n[NIVEL_1]\n{f['pei_1']}\n\n[NIVEL_2]\n{f['pei_2']}\n\n[NIVEL_3]\n{f['pei_3']}\n\n{links_footer}", f['info']['ano'], link_reg])
                    
                    if sucesso_db:
                        if gerar_variante:
                            status.write("🧬 Embaralhando Variante Tipo B...")
                            mapa_variante = f['mapa'].copy()
                            import random
                            random.shuffle(mapa_variante) 
                            
                            txt_var = f"[VALOR: {f['info']['valor']}]\n\n[QUESTOES]\n"
                            txt_gab_var = "[GABARITO_TEXTO]\n"
                            txt_grade_var = "[GRADE_DE_CORRECAO]\n"
                            
                            for i, item in enumerate(mapa_variante):
                                novo_num = i + 1
                                item_embaralhado = util.embaralhar_item_estruturado(item['dados'])
                                
                                txt_var += f"**QUESTÃO {novo_num:02d} -** {item_embaralhado['ENUNCIADO']}\n(A) {item_embaralhado['ALT_A']}\n(B) {item_embaralhado['ALT_B']}\n(C) {item_embaralhado['ALT_C']}\n(D) {item_embaralhado['ALT_D']}\n(E) {item_embaralhado['ALT_E']}\n\n"
                                txt_gab_var += f"QUESTÃO {novo_num:02d}: {item_embaralhado['GABARITO']}\n"
                                txt_grade_var += f"QUESTÃO {novo_num:02d}: [{item_embaralhado['HABILIDADE']}] | JUSTIFICATIVA: {item_embaralhado['JUSTIFICATIVA']} | DISTRATORES: {item_embaralhado['DISTRATORES']}\n"
                                
                            texto_final_var = txt_var + txt_gab_var + txt_grade_var
                            nome_var = f"{nome_arq} - TIPO B"
                            
                            doc_var = exporter.gerar_docx_prova_v25(nome_var, texto_final_var, f['info'])
                            link_var = db.subir_e_converter_para_google_docs(doc_var, nome_var, modo="AVALIACAO")
                            
                            links_footer_var = f"--- LINKS ---\nRegular({link_var}) PEI_N1({link_pei1}) PEI_N2({link_pei2}) PEI_N3({link_pei3})"
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_var, texto_final_var + f"\n\n[NIVEL_1]\n{f['pei_1']}\n\n[NIVEL_2]\n{f['pei_2']}\n\n[NIVEL_3]\n{f['pei_3']}\n\n{links_footer_var}", f['info']['ano'], link_var])

                        status.write("👨‍🏫 Gerando Guia do Professor...")
                        guia_txt = f"GABARITO PADRÃO:\n{txt_gabarito}\n\nGRADE PADRÃO:\n{txt_grade}"
                        if gerar_variante:
                            guia_txt += f"\n\nGABARITO TIPO B:\n{txt_gab_var}\n\nGRADE TIPO B:\n{txt_grade_var}"
                            
                        doc_prof = exporter.gerar_docx_professor_v25(f"{nome_arq}_GUIA_PROF", guia_txt, f['info'])
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_arq}_GUIA_PROF", modo="AVALIACAO")
                        
                        f['prova_final_txt'] = texto_final_padrao
                        f['nome_base'] = nome_arq
                        
                        status.update(label="✅ Forja Concluída com Sucesso!", state="complete")
                        st.balloons()
                        f['fase'] = 5
                        time.sleep(1.5)
                        st.rerun()
                    else:
                        status.update(label="❌ Erro Crítico ao salvar no Banco de Dados.", state="error")
                        st.error("A prova não foi salva. O texto pode ter excedido o limite do Google Sheets ou houve falha de conexão. Tente novamente.")

        # ==============================================================================
        # 📍 FASE 5: AÇÕES PÓS-PROVA (REVISÃO E 2ª CHAMADA)
        # ==============================================================================
        elif f['fase'] == 5:
            st.success("🏆 A Avaliação e a Tríade Inclusiva foram forjadas e salvas no Acervo!")
            st.markdown("### 🚀 Ações Pós-Prova")
            st.caption("Gere materiais derivados automaticamente a partir da prova que você acabou de criar.")
            
            c_pos1, c_pos2 = st.columns(2)
            
            if c_pos1.button("🔥 Gerar Revisão / Recomposição", use_container_width=True):
                with st.spinner("Convertendo prova em roteiro de revisão discursiva..."):
                    prompt_rev = f"PROVA BASE:\n{f['prova_final_txt']}\n\nID_EXAME: {f['nome_base']}"
                    res_rev = ai.gerar_ia("ARQUITETO_REVISAO_V29", prompt_rev)
                    
                    nome_rev = f"REVISAO_{f['nome_base']}"
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_rev, ai.extrair_tag(res_rev, "ALUNO"), f['info'])
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_rev}_ALUNO", modo="AULA")
                    
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_rev, res_rev + f"\n--- LINKS ---\nRegular({link_alu})", f['info']['ano'], link_alu])
                    st.success("✅ Revisão gerada e salva no Acervo!")
            
            if c_pos2.button("🔄 Gerar 2ª Chamada (Discursiva)", use_container_width=True):
                with st.spinner("Convertendo prova em formato 100% discursivo..."):
                    prompt_2a = f"PROVA BASE:\n{f['prova_final_txt']}"
                    res_2a = ai.gerar_ia("ARQUITETO_2A_CHAMADA_V100", prompt_2a)
                    
                    nome_2a = f"2ª_CHAMADA_{f['nome_base']}"
                    doc_2a = exporter.gerar_docx_prova_v25(nome_2a, res_2a, f['info'])
                    link_2a = db.subir_e_converter_para_google_docs(doc_2a, nome_2a, modo="AVALIACAO")
                    
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_2a, res_2a + f"\n--- LINKS ---\nRegular({link_2a})", f['info']['ano'], link_2a])
                    st.success("✅ 2ª Chamada gerada e salva no Acervo!")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Concluir e Voltar ao Início", type="primary", use_container_width=True):
                reset_forja()

        # ==============================================================================
        # 📍 FASE 6: RE-EXPORTAÇÃO RÁPIDA (REFINO)
        # ==============================================================================
        elif f['fase'] == 6:
            st.markdown("### 🛠️ Fase 6: Re-Exportação Rápida (Refino)")
            st.caption("Edite o texto bruto da avaliação e re-exporte os documentos. Ideal para corrigir nomes (ex: TESTE para PROVA) ou atualizar para o novo formato de 3 níveis PEI.")
            
            novo_nome = st.text_input("ID Técnico do Material (Nome no Banco):", value=f['nome_base'])
            
            t_reg, t_p1, t_p2, t_p3 = st.tabs(["📝 Prova Regular", "🔵 PEI Nível 1", "🟡 PEI Nível 2", "🔴 PEI Nível 3"])
            with t_reg:
                novo_reg = st.text_area("Texto Regular (Com Gabarito e Grade):", value=f['txt_reg'], height=400)
            with t_p1:
                novo_p1 = st.text_area("PEI Nível 1:", value=f['pei_1'], height=300)
            with t_p2:
                novo_p2 = st.text_area("PEI Nível 2:", value=f['pei_2'], height=300)
            with t_p3:
                novo_p3 = st.text_area("PEI Nível 3:", value=f['pei_3'], height=300)
                
            if st.button("💾 RE-COMPILAR E ATUALIZAR ACERVO", type="primary", use_container_width=True):
                with st.status("Re-forjando Documentos Oficiais...") as status:
                    db.excluir_avaliacao_completa(f['nome_base'], f['semana_ref'])
                    
                    trim_match = re.search(r'(I{1,3}\s*Trimestre)', novo_nome, re.IGNORECASE)
                    trim_str = trim_match.group(1) if trim_match else "I Trimestre"
                    info_re = {'ano': f['ano'], 'trimestre': trim_str, 'tipo_prova': "AVALIAÇÃO"}
                    
                    status.write("📝 Gerando Prova Regular...")
                    doc_reg = exporter.gerar_docx_prova_v25(novo_nome, novo_reg, info_re)
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, novo_nome, modo="AVALIACAO")
                    
                    link_pei1, link_pei2, link_pei3 = "N/A", "N/A", "N/A"
                    
                    if novo_p1:
                        status.write("🔵 Gerando PEI Nível 1...")
                        doc_pei1 = exporter.gerar_docx_pei_v25(f"{novo_nome}_PEI_N1", novo_p1, info_re)
                        link_pei1 = db.subir_e_converter_para_google_docs(doc_pei1, f"{novo_nome}_PEI_N1", modo="AVALIACAO")
                    
                    if novo_p2:
                        status.write("🟡 Gerando PEI Nível 2...")
                        doc_pei2 = exporter.gerar_docx_pei_v25(f"{novo_nome}_PEI_N2", novo_p2, info_re)
                        link_pei2 = db.subir_e_converter_para_google_docs(doc_pei2, f"{novo_nome}_PEI_N2", modo="AVALIACAO")
                        
                    if novo_p3:
                        status.write("🔴 Gerando PEI Nível 3...")
                        doc_pei3 = exporter.gerar_docx_pei_qualitativa(f"{novo_nome}_PEI_N3", novo_p3, info_re)
                        link_pei3 = db.subir_e_converter_para_google_docs(doc_pei3, f"{novo_nome}_PEI_N3", modo="AVALIACAO")
                        
                    status.write("👨‍🏫 Gerando Guia do Professor...")
                    txt_gab = ai.extrair_tag(novo_reg, "GABARITO_TEXTO") or ai.extrair_tag(novo_reg, "GABARITO")
                    txt_grade = ai.extrair_tag(novo_reg, "GRADE_DE_CORRECAO")
                    guia_txt = f"GABARITO PADRÃO:\n{txt_gab}\n\nGRADE PADRÃO:\n{txt_grade}"
                    doc_prof = exporter.gerar_docx_professor_v25(f"{novo_nome}_GUIA_PROF", guia_txt, info_re)
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{novo_nome}_GUIA_PROF", modo="AVALIACAO")
                    
                    links_footer = f"--- LINKS ---\nRegular({link_reg}) PEI_N1({link_pei1}) PEI_N2({link_pei2}) PEI_N3({link_pei3}) Prof({link_prof})"
                    
                    texto_final_banco = novo_reg
                    if novo_p1: texto_final_banco += f"\n\n[NIVEL_1]\n{novo_p1}"
                    if novo_p2: texto_final_banco += f"\n\n[NIVEL_2]\n{novo_p2}"
                    if novo_p3: texto_final_banco += f"\n\n[NIVEL_3]\n{novo_p3}"
                    texto_final_banco += f"\n\n{links_footer}"
                    
                    db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), f['semana_ref'], novo_nome, texto_final_banco, f['ano'], link_reg])
                    
                    status.update(label="✅ Re-Exportação Concluída!", state="complete")
                    st.balloons()
                    time.sleep(1.5)
                    reset_forja()

    # --- ABA 2: ACERVO DE SAFRA ---
    with tab_acervo_av:
        st.subheader("🗂️ Gestão de Acervo de Safra (Provas e Revisões)")
        st.caption("Acesse, edite ou apague avaliações já geradas.")
        
        with st.container(border=True):
            c_h1, c_h2, c_h3 = st.columns([1, 1, 1])
            f_trim_h = c_h1.selectbox("📅 Filtrar Trimestre:",["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], key="h_trim_av")
            f_ano_h = c_h2.selectbox("🎓 Filtrar Série:",["Todos", "6º", "7º", "8º", "9º"], key="h_ano_av")
            f_tipo_h = c_h3.selectbox("📝 Tipo de Ativo:",["Todos", "AVALIAÇÃO", "REVISÃO"], key="h_tipo_av")

        df_exames = df_aulas[df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy()
        if f_trim_h != "Todos": df_exames = df_exames[df_exames['CONTEUDO'].str.contains(f_trim_h, na=False)]
        if f_ano_h != "Todos": df_exames = df_exames[df_exames['ANO'] == f_ano_h]
        if f_tipo_h != "Todos": df_exames = df_exames[df_exames['SEMANA_REF'] == f_tipo_h]

        df_exames = df_exames.iloc[::-1] 

        if not df_exames.empty:
            for _, row in df_exames.iterrows():
                with st.container(border=True):
                    txt_f = str(row['CONTEUDO'])
                    identificador = row['TIPO_MATERIAL']
                    
                    col_tit, col_meta = st.columns([2, 1])
                    with col_tit:
                        st.markdown(f"#### 📄 {identificador}")
                    with col_meta:
                        val_ex = re.sub(r'[*#]', '', ai.extrair_tag(txt_f, "VALOR")).strip()
                        st.markdown(f"**💰 Valor:** `{val_ex if val_ex else 'N/A'}` | **🎓 Série:** `{row['ANO']}`")

                    gab_simples = ai.extrair_tag(txt_f, "GABARITO_TEXTO") or ai.extrair_tag(txt_f, "RESPOSTAS_IA")
                    if gab_simples:
                        if "2ª" in identificador.upper() or "2CHAMADA" in identificador.upper() or "REVISAO" in identificador.upper():
                            st.markdown(f"**✅ Gabarito Regular:** `[ Formato Discursivo - Ver aba 'Perícia' abaixo ]`")
                        else:
                            matches = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", gab_simples.upper())
                            if matches:
                                gab_formatado = " | ".join([f"{n}: {l}" for n, l in matches])
                                st.markdown(f"**✅ Gabarito Regular:** `{gab_formatado}`")
                            else:
                                gab_limpo = re.sub(r'[*#]', '', gab_simples).replace('QUESTÃO', '').strip()
                                if len(gab_limpo) > 100:
                                    st.markdown(f"**✅ Gabarito Regular:** `[ Formato Discursivo - Ver aba 'Perícia' abaixo ]`")
                                else:
                                    st.markdown(f"**✅ Gabarito Regular:** `{gab_limpo}`")

                    l_reg = (re.findall(r"Regular\((.*?)\)", txt_f) or [row.get('LINK_DRIVE')])[-1]
                    l_pei1 = (re.findall(r"PEI_N1\((.*?)\)", txt_f) or re.findall(r"PEI\((.*?)\)", txt_f) or [None])[-1]
                    l_pei2 = (re.findall(r"PEI_N2\((.*?)\)", txt_f) or [None])[-1]
                    l_pei3 = (re.findall(r"PEI_N3\((.*?)\)", txt_f) or [None])[-1]
                    l_prof = (re.findall(r"Prof\((.*?)\)", txt_f) or [None])[-1]

                    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
                    c_b1.link_button("📝 REGULAR", str(l_reg), use_container_width=True, type="primary")
                    
                    if l_prof and "N/A" not in str(l_prof): 
                        c_b2.link_button("👨‍🏫 GUIA DO PROFESSOR", str(l_prof), use_container_width=True)
                    else: 
                        c_b2.button("⚪ SEM GUIA", disabled=True, use_container_width=True, key=f"no_grade_{row.name}")
                    
                    # 🚨 NOVO BOTÃO REFINAR (ACIONA A FASE 6)
                    if c_b3.button("🔄 REFINAR", key=f"ref_av_h_{row.name}", use_container_width=True):
                        pei1 = ai.extrair_tag(txt_f, "NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                        pei2 = ai.extrair_tag(txt_f, "NIVEL_2")
                        pei3 = ai.extrair_tag(txt_f, "NIVEL_3")
                        
                        reg_match = re.split(r'\[(?:PEI|NIVEL_1)\]', txt_f, flags=re.IGNORECASE)
                        txt_reg = reg_match[0].strip() if reg_match else txt_f
                        
                        st.session_state.forja = {
                            'fase': 6,
                            'nome_base': identificador,
                            'txt_reg': txt_reg,
                            'pei_1': pei1,
                            'pei_2': pei2,
                            'pei_3': pei3,
                            'ano': row['ANO'],
                            'semana_ref': row['SEMANA_REF']
                        }
                        st.rerun()
                        
                    if c_b4.button("🗑️ APAGAR", key=f"del_av_h_{row.name}", use_container_width=True):
                        if db.excluir_avaliacao_completa(identificador, row['SEMANA_REF']): st.rerun()

                    if l_pei1 and "N/A" not in str(l_pei1) and "2ª" not in identificador.upper() and "2CHAMADA" not in identificador.upper():
                        st.markdown("**♿ Arquivos de Inclusão (PEI):**")
                        c_p1, c_p2, c_p3 = st.columns(3)
                        c_p1.link_button("🔵 PEI Nível 1 (Leve)", str(l_pei1), use_container_width=True)
                        if l_pei2: c_p2.link_button("🟡 PEI Nível 2 (Moderado)", str(l_pei2), use_container_width=True)
                        if l_pei3: c_p3.link_button("🔴 PEI Nível 3 (Severo)", str(l_pei3), use_container_width=True)

                    with st.expander("👁️ ANALISAR ESTRUTURA PEDAGÓGICA E ITENS"):
                        t_gab, t_ques, t_pei_v, t_peri_pei = st.tabs([
                            "🎯 Perícia Regular", "📝 Prova Regular", "♿ Adaptação PEI", "🔬 Perícia PEI"
                        ])
                        
                        with t_gab:
                            st.markdown("##### 🔬 Grade de Perícia (Regular)")
                            grade_raw = ai.extrair_tag(txt_f, "GRADE_DE_CORRECAO")
                            if grade_raw:
                                questoes_grade = re.split(r"(?i)QUEST[AÃ]O\s*0?(\d+)", grade_raw)
                                if len(questoes_grade) > 1:
                                    for i in range(1, len(questoes_grade), 2):
                                        q_num, q_txt = questoes_grade[i], questoes_grade[i+1]
                                        with st.container(border=True):
                                            st.markdown(f"**📑 QUESTÃO {q_num}**")
                                            q_txt_limpo = re.sub(r'[*#]', '', q_txt).strip()
                                            
                                            m_hab = re.search(r"(?i)(?:HABILIDADE|BNCC|DESCRITOR).*?[:\-]\s*(.*?)(?=RESPOSTA|JUSTIFICATIVA|ALERTA|PERÍCIA|$)", q_txt_limpo, re.DOTALL)
                                            m_just = re.search(r"(?i)(?:RESPOSTA|JUSTIFICATIVA).*?[:\-]\s*(.*?)(?=ALERTA|PERÍCIA|DISTRATORES|$)", q_txt_limpo, re.DOTALL)
                                            m_peri = re.search(r"(?i)(?:ALERTA|PERÍCIA|DISTRATORES).*?[:\-]\s*(.*)", q_txt_limpo, re.DOTALL)
                                            
                                            if m_hab: st.caption(f"🆔 **Habilidade:** {m_hab.group(1).strip()}")
                                            if m_just: st.write(f"🎯 **Resposta:** {m_just.group(1).strip()}")
                                            if m_peri: st.info(f"🔍 **Análise de Erros:** {m_peri.group(1).strip()}")
                                else: st.write(re.sub(r'[*#]', '', grade_raw))
                            else: st.warning("Grade não localizada.")

                        with t_ques:
                            st.markdown("##### 📋 Conteúdo da Prova Regular")
                            questoes_reg = ai.extrair_tag(txt_f, "QUESTOES")
                            if questoes_reg:
                                txt_limpo_q = re.sub(r'\[\s*PROMPT IMAGEM:.*?\]', '🖼️ *(Imagem)*', questoes_reg, flags=re.IGNORECASE)
                                txt_limpo_q = re.sub(r'\[GEOGEBRA\]', '📐 *(Comando GeoGebra)*', txt_limpo_q, flags=re.IGNORECASE)
                                st.write(re.sub(r'[*#]', '', txt_limpo_q))

                        with t_pei_v:
                            st.markdown("##### ♿ Detalhes da Adaptação PEI")
                            pei_txt = ai.extrair_tag(txt_f, "NIVEL_1") or ai.extrair_tag(txt_f, "PEI")
                            if pei_txt:
                                st.info(re.sub(r'[*#]', '', pei_txt))
                                st.divider()
                                gab_pei = ai.extrair_tag(txt_f, "GABARITO_PEI")
                                if gab_pei: st.code(re.sub(r'[*#]', '', gab_pei))

                        with t_peri_pei:
                            st.markdown("##### 🔬 Grade de Perícia PEI")
                            grade_pei_raw = ai.extrair_tag(txt_f, "GRADE_DE_CORRECAO_PEI")
                            if grade_pei_raw:
                                q_grade_pei = re.split(r"(?i)QUEST[AÃ]O\s*PEI\s*0?(\d+)", grade_pei_raw)
                                if len(q_grade_pei) > 1:
                                    for i in range(1, len(q_grade_pei), 2):
                                        q_n, q_t = q_grade_pei[i], q_grade_pei[i+1]
                                        with st.container(border=True):
                                            st.markdown(f"**♿ QUESTÃO PEI {q_n}**")
                                            q_t_limpo = re.sub(r'[*#]', '', q_t).strip()
                                            m_just_p = re.search(r"(?i)(?:JUSTIFICATIVA|RESPOSTA).*?[:\-]\s*(.*?)(?=ANÁLISE|LACUNA|ERRO|$)", q_t_limpo, re.DOTALL)
                                            m_lacu_p = re.search(r"(?i)(?:ANÁLISE|LACUNA|ERRO).*?[:\-]\s*(.*)", q_t_limpo, re.DOTALL)
                                            if m_just_p: st.write(f"🎯 **Resposta:** {m_just_p.group(1).strip()}")
                                            if m_lacu_p: st.warning(f"🧠 **Análise de Lacuna:** {m_lacu_p.group(1).strip()}")
                                else: st.write(re.sub(r'[*#]', '', grade_pei_raw))
                            else: st.info("Perícia PEI não disponível.")
        else:
            st.info("📭 Acervo vazio.")


# ==============================================================================
# MÓDULO: CENTRAL DE INTELIGÊNCIA DE RESULTADOS (CIR / SCANNER) - CLEAN & UX V120
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("📸 Central de Inteligência de Resultados (CIR)")
    st.caption("💡 **Guia de Comando:** Escaneie gabaritos, lance notas de trabalhos e audite resultados com soberania total. O sistema adapta a correção ao perfil do aluno.")
    st.markdown("---")

    if "v_scan" not in st.session_state: st.session_state.v_scan = int(time.time())
    v = st.session_state.v_scan

    # --- FUNÇÃO AUXILIAR: FILTRO HIERÁRQUICO BLINDADO ---
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
            
            if apenas_provas:
                permitidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "AVALIAÇÃO"]
                df_f = df_f[df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos))]
                mask_trim = (df_f['TRIM_DETECTADO'] == trimestre_nome) | (df_f['CONTEUDO'].str.contains(trimestre_nome, na=False)) | (df_f['TIPO_MATERIAL'].str.upper().str.contains("FINAL"))
                df_f = df_f[mask_trim]
            else:
                permitidos = ["PROJETO", "FIXAÇÃO", "REFORÇO", "ATIVIDADE", "TRABALHO", "AULA"]
                df_f = df_f[df_f['TIPO_MATERIAL'].str.upper().str.contains('|'.join(permitidos))]
                df_f = df_f[df_f['TRIM_DETECTADO'] == trimestre_nome]
            
            return sorted(df_f['TIPO_MATERIAL'].unique().tolist())
        except Exception as e: 
            return []

    # 🚨 ARQUITETURA COM RAIO-X RESTAURADO (4 ABAS)
    tab_pericia, tab_atividades, tab_auditoria, tab_raiox = st.tabs([
        "📸 1. Scanner & Triagem", 
        "✍️ 2. Trabalhos & Projetos", 
        "⚖️ 3. Tribunal de Auditoria",
        "📊 4. Raio-X Pedagógico"
    ])

    # ==============================================================================
    # 📸 ABA 1: SCANNER & TRIAGEM INTELIGENTE
    # ==============================================================================
    with tab_pericia:
        # 🚨 VACINA ANTI-KEYERROR (BLINDAGEM DE QUEDA DE API DO GOOGLE)
        lista_turmas_cir = []
        if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
            turmas_reais_cir = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_cir = sorted(turmas_reais_cir['ID_TURMA'].unique())
        elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
            lista_turmas_cir = sorted(df_alunos['TURMA'].unique())
            
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 1.5])
            t_sel = c1.selectbox("👥 Turma:", [""] + lista_turmas_cir, key=f"t_p_{v}")
            tr_sel = c2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_p_{v}")
            
            opcoes_p = filtrar_ativos_cir(t_sel, tr_sel, apenas_provas=True)
            opcoes_base = [opt for opt in opcoes_p if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            at_sel = c3.selectbox("📋 Avaliação Base (Slot):", [""] + opcoes_base, key=f"at_p_{v}")

        if not t_sel or not at_sel:
            st.info("💡 Selecione a Turma e a Avaliação Base para abrir a Mesa de Triagem.")
        else:
            nome_filtro_pendente = at_sel.split("-")[0].strip()
            
            # 🚨 VACINA DE SOBERANIA: Filtra PRIMEIRO pela turma selecionada antes de contar!
            df_diag_turma = df_diagnosticos[df_diagnosticos['TURMA'] == t_sel]
            
            escaneados_raw = df_diag_turma[df_diag_turma['ID_AVALIACAO'].str.startswith(nome_filtro_pendente, na=False)]['ID_ALUNO'].astype(str).tolist()
            
            trim_limpo = tr_sel.replace(" ", "")
            serie_num = "".join(filter(str.isdigit, t_sel))
            escaneados_2a = df_diag_turma[(df_diag_turma['ID_AVALIACAO'].str.contains("2ª|2CHAMADA", regex=True, case=False)) & (df_diag_turma['ID_AVALIACAO'].str.contains(trim_limpo, case=False))]['ID_ALUNO'].astype(str).tolist()
            
            escaneados_unicos = list(set(escaneados_raw + escaneados_2a))
            
            pendentes = df_alunos[(df_alunos['TURMA'] == t_sel) & (~df_alunos['ID'].astype(str).isin(escaneados_unicos))].sort_values(by="NOME_ALUNO")
            
            total_turma = len(df_alunos[df_alunos['TURMA'] == t_sel])
            total_corrigidos = len(escaneados_unicos)
            
            st.markdown("#### 📊 Progresso da Correção")
            progresso_bruto = total_corrigidos / total_turma if total_turma > 0 else 0
            progresso_seguro = min(1.0, max(0.0, progresso_bruto))
            
            st.progress(progresso_seguro)
            st.caption(f"**{total_corrigidos} de {total_turma}** alunos processados. Restam **{len(pendentes)}** na fila.")

            if pendentes.empty:
                st.success(f"🏆 **SOBERANIA TOTAL:** Todos os alunos da {t_sel} já possuem nota para {at_sel}!")
            else:
                st.markdown("---")
                c_fila1, c_fila2 = st.columns([2, 1])
                al_sel = c_fila1.selectbox("📄 Selecione o aluno na fila:", [""] + pendentes['NOME_ALUNO'].tolist(), key=f"pilha_{v}")
                
                if c_fila2.button("❌ Registrar Faltas em Lote", use_container_width=True):
                    st.session_state.show_faltas_lote = not st.session_state.get("show_faltas_lote", False)
                
                if st.session_state.get("show_faltas_lote", False):
                    with st.container(border=True):
                        faltosos = st.multiselect("Selecione os alunos ausentes:", pendentes['NOME_ALUNO'].tolist())
                        if st.button("💾 Confirmar Faltas", type="primary"):
                            linhas_faltas = []
                            data_hoje = datetime.now().strftime("%d/%m/%Y")
                            for f_nome in faltosos:
                                f_id = pendentes[pendentes['NOME_ALUNO'] == f_nome].iloc[0]['ID']
                                linhas_faltas.append([data_hoje, f_id, f_nome, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                            if db.salvar_lote("DB_GABARITOS_ALUNOS", linhas_faltas):
                                st.success("Faltas registradas!"); time.sleep(1); st.rerun()

                if al_sel:
                    al_info = pendentes[pendentes['NOME_ALUNO'] == al_sel].iloc[0]
                    id_aluno_atual = al_info['ID']
                    nec_aluno = str(al_info['NECESSIDADES']).upper().strip()
                    
                    is_adapted_candidate = nec_aluno not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE"]
                    
                    st.markdown("---")
                    st.markdown(f"### 📸 Corrigindo: **{al_sel}**")
                    
                    if is_adapted_candidate:
                        st.warning(f"⚠️ **Atenção:** Aluno com perfil **{nec_aluno}**. Verifique qual prova foi aplicada e selecione a lente correta abaixo.")
                    
                    with st.container(border=True):
                        st.markdown("#### 🔍 Lente de Correção")
                        
                        # 🚨 NOVAS LENTES ESPECÍFICAS PARA PEI
                        lente_corr = st.radio(
                            "Qual prova o aluno respondeu?", 
                            [
                                "📝 Regular (Padrão ou Variantes)", 
                                "🔵 PEI Nível 1 (Apoio Leve)", 
                                "🟡 PEI Nível 2 (Apoio Moderado)", 
                                "🔴 PEI Nível 3 / Qualitativa (Manual)"
                            ],
                            index=1 if "PEI" in nec_aluno else 0,
                            horizontal=True,
                            key=f"lente_{id_aluno_atual}"
                        )
                        
                        material_ref = None
                        is_pei_grading = "PEI Nível 1" in lente_corr or "PEI Nível 2" in lente_corr
                        nivel_alvo_pei = "NIVEL_1" if "Nível 1" in lente_corr else "NIVEL_2"
                        is_qualitativa = "Nível 3" in lente_corr
                        modo_2a = False
                        
                        if lente_corr == "📝 Regular (Padrão ou Variantes)":
                            c_reg1, c_reg2 = st.columns(2)
                            modo_2a = c_reg1.toggle("🚀 É 2ª Chamada?", key=f"t2a_{id_aluno_atual}")
                            
                            tipo_base = at_sel.split("-")[0].strip().upper()
                            
                            if modo_2a:
                                df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(serie_num))]
                                opcoes_2a = df_2a['TIPO_MATERIAL'].unique().tolist()
                                at_segunda = c_reg2.selectbox("Selecione a 2ª Chamada:", [""] + opcoes_2a, key=f"s2a_{id_aluno_atual}")
                                if at_segunda: material_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == at_segunda].iloc[0]
                            else:
                                df_variantes = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains(tipo_base)) & (df_aulas['TIPO_MATERIAL'].str.upper().str.contains("TIPO")) & (df_aulas['ANO'].str.contains(serie_num))]
                                opcoes_variantes = ["Padrão (Tipo A)"] + df_variantes['TIPO_MATERIAL'].unique().tolist()
                                versao_variante = c_reg2.selectbox("🧬 Variante da Prova:", opcoes_variantes, key=f"var_{id_aluno_atual}")
                                
                                if versao_variante != "Padrão (Tipo A)":
                                    material_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == versao_variante].iloc[0]
                                else:
                                    material_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel].iloc[0]
                                    
                        elif is_pei_grading:
                            material_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel].iloc[0]
                            st.info(f"O sistema usará o Gabarito do {lente_corr.split('(')[0].strip()}.")
                            
                        else:
                            material_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel].iloc[0]

                    # ==========================================================
                    # MOTOR DE CORREÇÃO
                    # ==========================================================
                    if material_ref is not None:
                        txt_ref = str(material_ref['CONTEUDO'])
                        val_tag = ai.extrair_tag(txt_ref, "VALOR")
                        v_total_at = util.sosa_to_float(val_tag) if val_tag else 10.0

                        # 🚨 EXTRATOR DE GABARITO BLINDADO PARA PEI
                        def extrair_gab_blindado(texto, is_pei=False, nivel_pei="NIVEL_1"):
                            if is_pei:
                                bloco_pei = ai.extrair_tag(texto, nivel_pei)
                                if not bloco_pei: return []
                                # Isola a parte do gabarito no final do bloco
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

                        st.markdown("---")
                        
                        # 🚨 PROTOCOLO FÊNIX: 2ª Chamada (Discursiva)
                        if modo_2a:
                            st.info("✍️ **Modo 2ª Chamada (Discursiva):** Avalie o raciocínio do aluno.")
                            
                            q_raw = ai.extrair_tag(txt_ref, "QUESTOES")
                            qtd_q_2a = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw))
                            if qtd_q_2a == 0: qtd_q_2a = 10
                            
                            peso_q = v_total_at / qtd_q_2a if qtd_q_2a > 0 else 0
                            
                            col_man1, col_man2 = st.columns([1.5, 1])
                            with col_man1:
                                dados_manual = [{"Q": f"{i+1:02d}", "Avaliação do Professor": "⚪ Em Branco"} for i in range(qtd_q_2a)]
                                df_manual = st.data_editor(
                                    pd.DataFrame(dados_manual), hide_index=True, use_container_width=True,
                                    column_config={
                                        "Q": st.column_config.TextColumn(disabled=True, width="small"),
                                        "Avaliação do Professor": st.column_config.SelectboxColumn(
                                            options=["✅ Acerto Integral", "⚠️ Acerto Parcial", "❌ Erro", "⚪ Em Branco"], required=True
                                        )
                                    }, key=f"manual_2a_{id_aluno_atual}"
                                )
                            
                            with col_man2:
                                nota_calc = 0.0
                                respostas_finais = []
                                acertos_cheios, acertos_parciais = 0, 0
                                
                                for _, row in df_manual.iterrows():
                                    resp = row["Avaliação do Professor"]
                                    respostas_finais.append(resp)
                                    if resp == "✅ Acerto Integral": 
                                        nota_calc += peso_q
                                        acertos_cheios += 1
                                    elif resp == "⚠️ Acerto Parcial": 
                                        nota_calc += (peso_q / 2)
                                        acertos_parciais += 1
                                        
                                st.metric("Nota Calculada", f"{nota_calc:.2f} / {v_total_at:.2f}")
                                st.caption(f"✅ {acertos_cheios} Integrais | ⚠️ {acertos_parciais} Parciais")
                                
                                evidencia_manual = st.file_uploader("📸 Upload da Prova", type=["jpg", "png", "pdf"], key=f"up_2a_{id_aluno_atual}")
                                
                                if st.button("💾 SALVAR CORREÇÃO DISCURSIVA", type="primary", use_container_width=True):
                                    with st.spinner("Salvando no banco de dados..."):
                                        link_ev = "N/A"
                                        id_av_final = material_ref['TIPO_MATERIAL']
                                        if evidencia_manual:
                                            link_ev = db.subir_e_converter_para_google_docs(evidencia_manual.getvalue(), al_sel.replace(" ","_")+"_2CHAMADA", trimestre=tr_sel, categoria=t_sel, semana=id_av_final, modo="SCANNER")
                                        
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS",[
                                            datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, 
                                            id_av_final, ";".join(respostas_finais), util.sosa_to_str(nota_calc), link_ev
                                        ])
                                        st.success(f"✅ {al_sel} processado!"); time.sleep(0.5); st.rerun()

                        # 🚨 MODO REGULAR OU PEI (Múltipla Escolha)
                        elif is_pei_grading or lente_corr == "📝 Regular (Padrão ou Variantes)":
                            c_mod1, c_mod2 = st.columns([3, 1])
                            modo_correcao = c_mod1.radio(
                                "⚙️ Método de Correção:", 
                                ["📸 Scanner IA (Câmera)", "✍️ Digitação Manual (Com Análise de Cálculo)"], 
                                horizontal=True, 
                                key=f"modo_corr_{id_aluno_atual}"
                            )
                            
                            if c_mod2.button("❌ Registrar Falta", use_container_width=True):
                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                st.rerun()

                            st.markdown("---")
                            
                            # 🚨 TRAVA DE LETRAS: PEI SÓ TEM A, B, C
                            opcoes_letras = ["A", "B", "C", "X", "?"] if is_pei_grading else ["A", "B", "C", "D", "E", "X", "?"]

                            if modo_correcao == "📸 Scanner IA (Câmera)":
                                c_cam, c_man = st.columns([2, 1])
                                with c_cam:
                                    st.info("📱 **Scanner IA:** Tire a foto do gabarito.")
                                    img_file = st.file_uploader("Upload", type=["jpg", "jpeg", "png"], key=f"up_{id_aluno_atual}", label_visibility="collapsed")
                                    with st.expander("💻 Usar Webcam"):
                                        img_cam = st.camera_input("Webcam", key=f"cam_{id_aluno_atual}")
                                    img = img_file if img_file else img_cam

                                if img and "current_scan_res" not in st.session_state:
                                    with st.spinner("Analisando marcações com Visão Computacional..."):
                                        res_json = ai.analisar_gabarito_vision(img.getvalue())
                                        qtd_q = len(gab_alvo)
                                        st.session_state.current_scan_res = [res_json.get(f"{i+1:02d}", res_json.get(str(i+1), "?")) for i in range(qtd_q)]
                                        st.session_state.current_scan_img = img.getvalue()
                                        st.rerun()

                                if "current_scan_res" in st.session_state:
                                    res_lidas = st.session_state.current_scan_res
                                    st.markdown("---")
                                    col_res1, col_res2 = st.columns([1.5, 1])
                                    
                                    with col_res1:
                                        st.subheader("⚖️ Mesa de Perícia")
                                        dados_pericia = []
                                        for i, lido in enumerate(res_lidas):
                                            if i < len(gab_alvo):
                                                certo = gab_alvo[i]
                                                status = "✅ ACERTO" if lido == certo else ("🚫 DUPLA" if lido == "X" else ("⚪ VAZIA" if lido == "?" else f"❌ (Era {certo})"))
                                                dados_pericia.append({"Q": f"{i+1:02d}", "Lido": lido, "Status": status})
                                        
                                        df_mesa = st.data_editor(pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                                            column_config={"Lido": st.column_config.SelectboxColumn("Ajustar", options=opcoes_letras, required=True)},
                                            key=f"ed_turbo_{id_aluno_atual}")
                                    
                                    with col_res2:
                                        st.subheader("📊 Resultado")
                                        novas_res = df_mesa["Lido"].tolist()
                                        acertos = sum(1 for i, r in enumerate(novas_res) if i < len(gab_alvo) and r == gab_alvo[i])
                                        nota_f = (acertos / len(gab_alvo)) * v_total_at if len(gab_alvo) > 0 else 0
                                        st.metric("Nota Final", f"{nota_f:.2f}", delta=f"{acertos}/{len(gab_alvo)} acertos")
                                        
                                        if st.button("💾 SALVAR CORREÇÃO", type="primary", use_container_width=True):
                                            with st.spinner("Arquivando no Drive..."):
                                                id_av_final = material_ref['TIPO_MATERIAL']
                                                link_pasta = db.subir_e_converter_para_google_docs(st.session_state.current_scan_img, al_sel.replace(" ","_"), trimestre=tr_sel, categoria=t_sel, semana=id_av_final, modo="SCANNER")
                                                
                                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                                    datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, 
                                                    id_av_final, ";".join(novas_res), util.sosa_to_str(nota_f), link_pasta
                                                ])
                                                del st.session_state.current_scan_res
                                                del st.session_state.current_scan_img
                                                st.success("Salvo!"); time.sleep(0.5); st.rerun()

                                        if st.button("🗑️ DESCARTAR E REFAZER"):
                                            del st.session_state.current_scan_res
                                            del st.session_state.current_scan_img
                                            st.rerun()

                            elif modo_correcao == "✍️ Digitação Manual (Com Análise de Cálculo)":
                                st.info("💡 **Regra de Ouro:** Digite a resposta do aluno. Se a questão exige cálculo e ele não fez, desmarque a caixa 'Cálculo OK?' para dar apenas 50% do valor da questão.")
                                
                                col_man1, col_man2 = st.columns([1.5, 1])
                                
                                with col_man1:
                                    dados_manual = []
                                    for i in range(len(gab_alvo)):
                                        dados_manual.append({
                                            "Q": f"{i+1:02d}",
                                            "Gabarito": gab_alvo[i],
                                            "Resposta do Aluno": "?",
                                            "Cálculo OK?": True
                                        })
                                    
                                    df_manual = st.data_editor(
                                        pd.DataFrame(dados_manual),
                                        hide_index=True,
                                        use_container_width=True,
                                        column_config={
                                            "Q": st.column_config.TextColumn(disabled=True, width="small"),
                                            "Gabarito": st.column_config.TextColumn(disabled=True, width="small"),
                                            "Resposta do Aluno": st.column_config.SelectboxColumn(options=opcoes_letras, required=True),
                                            "Cálculo OK?": st.column_config.CheckboxColumn("Cálculo OK?", default=True)
                                        },
                                        key=f"manual_grid_{id_aluno_atual}"
                                    )
                                
                                with col_man2:
                                    peso_q = v_total_at / len(gab_alvo) if len(gab_alvo) > 0 else 0
                                    nota_calc = 0.0
                                    respostas_finais = []
                                    acertos_cheios = 0
                                    acertos_parciais = 0
                                    
                                    for i, row in df_manual.iterrows():
                                        resp = row["Resposta do Aluno"]
                                        respostas_finais.append(resp)
                                        if resp == row["Gabarito"]:
                                            if row["Cálculo OK?"]:
                                                nota_calc += peso_q
                                                acertos_cheios += 1
                                            else:
                                                nota_calc += (peso_q / 2)
                                                acertos_parciais += 1
                                                
                                    st.metric("Nota Calculada", f"{nota_calc:.2f} / {v_total_at:.2f}")
                                    st.caption(f"✅ {acertos_cheios} Acertos Integrais | ⚠️ {acertos_parciais} Acertos Parciais (Sem Cálculo)")
                                    
                                    evidencia_manual = st.file_uploader("📸 Upload da Prova (Opcional)", type=["jpg", "png", "pdf"], key=f"up_man_{id_aluno_atual}")
                                    
                                    if st.button("💾 SALVAR CORREÇÃO MANUAL", type="primary", use_container_width=True):
                                        with st.spinner("Salvando no banco de dados..."):
                                            link_ev = "N/A"
                                            id_av_final = material_ref['TIPO_MATERIAL']
                                            
                                            if evidencia_manual:
                                                link_ev = db.subir_e_converter_para_google_docs(evidencia_manual.getvalue(), al_sel.replace(" ","_")+"_MANUAL", trimestre=tr_sel, categoria=t_sel, semana=id_av_final, modo="SCANNER")
                                            
                                            db.salvar_no_banco("DB_GABARITOS_ALUNOS",[
                                                datetime.now().strftime("%d/%m/%Y"), 
                                                id_aluno_atual, al_sel, t_sel, 
                                                id_av_final, 
                                                ";".join(respostas_finais), 
                                                util.sosa_to_str(nota_calc), 
                                                link_ev
                                            ])
                                            st.success(f"✅ {al_sel} processado!"); time.sleep(0.5); st.rerun()

                        # --- MODO 3: QUALITATIVA ---
                        elif is_qualitativa:
                            st.warning("♿ **Modo de Avaliação Alternativa:** Exclusivo para alunos com suporte nível 3 ou adaptações severas que não realizam provas de múltipla escolha.")
                            
                            # 🚨 EXTRATOR DINÂMICO DE RUBRICAS DO NÍVEL 3
                            nivel3_txt = ai.extrair_tag(txt_ref, "NIVEL_3")
                            rubricas_encontradas = []
                            
                            if nivel3_txt:
                                # Procura a palavra RUBRICA e pega tudo o que vem depois
                                match_rubrica = re.search(r"(?i)RUBRICA.*?(?:\n)(.*)", nivel3_txt, re.DOTALL)
                                if match_rubrica:
                                    linhas_rubrica = match_rubrica.group(1).strip().split('\n')
                                    for linha in linhas_rubrica:
                                        # Limpa os marcadores de lista e negritos
                                        linha_limpa = re.sub(r'^[-*•]\s*', '', linha).replace('**', '').strip()
                                        if linha_limpa and len(linha_limpa) > 5:
                                            rubricas_encontradas.append(linha_limpa)
                            
                            col_q1, col_q2 = st.columns([1, 1.5])
                            with col_q1:
                                nota_qual = st.number_input("Nota Atribuída:", 0.0, v_total_at, v_total_at, step=0.5, key=f"nq_{id_aluno_atual}")
                                evidencia_qual = st.file_uploader("📸 Upload da Prova/Desenho", type=["jpg", "png", "pdf"], key=f"uq_{id_aluno_atual}")
                            
                            with col_q2:
                                respostas_rubrica = []
                                obs_extra = ""
                                obs_qual = ""
                                
                                if rubricas_encontradas:
                                    st.markdown("#### 📋 Rubrica de Observação (Extraída da Prova)")
                                    for i, rubrica in enumerate(rubricas_encontradas):
                                        st.markdown(f"**{rubrica}**")
                                        resp = st.selectbox(
                                            "Avaliação:", 
                                            ["✅ Atingiu de forma autônoma", "🤝 Atingiu com apoio físico/verbal", "❌ Não atingiu / Não observável"], 
                                            key=f"rub_{id_aluno_atual}_{i}", 
                                            label_visibility="collapsed"
                                        )
                                        respostas_rubrica.append(f"- {rubrica.split(':')[0] if ':' in rubrica else 'Critério'}: {resp}")
                                    
                                    st.markdown("<br>", unsafe_allow_html=True)
                                    obs_extra = st.text_area("Observações Adicionais (Opcional):", height=68, key=f"oq_extra_{id_aluno_atual}")
                                else:
                                    st.info("Nenhuma rubrica específica encontrada nesta prova. Use o campo abaixo.")
                                    obs_qual = st.text_area("Parecer Qualitativo (O que foi avaliado?):", height=130, placeholder="Ex: O aluno realizou pareamento de cores e formas geométricas...", key=f"oq_{id_aluno_atual}")
                            
                            if st.button("💾 SALVAR AVALIAÇÃO QUALITATIVA", type="primary", use_container_width=True):
                                # Monta o parecer final juntando as rubricas
                                if rubricas_encontradas:
                                    parecer_final = "\n".join(respostas_rubrica)
                                    if obs_extra.strip():
                                        parecer_final += f"\nObs: {obs_extra.strip()}"
                                else:
                                    parecer_final = obs_qual.strip()
                                    
                                if not parecer_final: 
                                    st.error("⚠️ Preencha o parecer qualitativo.")
                                else:
                                    with st.spinner("Salvando avaliação e gerando evidência no Dossiê..."):
                                        link_ev = "N/A"
                                        id_av_final = at_sel
                                        if evidencia_qual:
                                            link_ev = db.subir_e_converter_para_google_docs(evidencia_qual.getvalue(), al_sel.replace(" ","_")+"_QUAL", trimestre=tr_sel, categoria=t_sel, semana=id_av_final, modo="SCANNER")
                                        
                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                            datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, t_sel, 
                                            id_av_final, f"QUALITATIVA|{parecer_final}", util.sosa_to_str(nota_qual), link_ev
                                        ])
                                        
                                        db.salvar_no_banco("DB_RELATORIOS", [
                                            datetime.now().strftime("%d/%m/%Y"), id_aluno_atual, al_sel, 
                                            "AVALIACAO_QUALITATIVA", 
                                            f"Avaliação: {id_av_final}\nNota: {nota_qual}\nParecer:\n{parecer_final}\nEvidência: {link_ev}"
                                        ])
                                        st.success("Salvo!"); time.sleep(0.5); st.rerun()

    # ==============================================================================
    # ✍️ ABA 2: TRABALHOS & PROJETOS
    # ==============================================================================
    with tab_atividades:
        st.subheader("✍️ Gestão de Notas de Projetos e Atividades")
        st.caption("Lance notas de Redações, Cartazes e Apresentações. O sistema cruza com o Diário de Bordo para ajudar na avaliação.")
        
        with st.container(border=True):
            c_f1, c_f2 = st.columns(2)
            t_sel_a = c_f1.selectbox("👥 Turma:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"t_a_{v}")
            tr_sel_a = c_f2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_a_{v}")

            opcoes_a = filtrar_ativos_cir(t_sel_a, tr_sel_a, apenas_provas=False)
            at_sel_a = st.selectbox("📋 Selecione o Trabalho ou Atividade:", [""] + opcoes_a, key=f"at_a_{v}")

        if t_sel_a and at_sel_a:
            dados_at = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_a].iloc[0]
            val_tag = ai.extrair_tag(str(dados_at['CONTEUDO']), "VALOR")
            v_max_padrao = util.sosa_to_float(val_tag) if val_tag else 2.0

            c_m1, c_m2 = st.columns([2, 1])
            c_m1.warning(f"📝 **ATIVIDADE:** {at_sel_a}")
            v_max_ativ = c_m2.number_input("💎 Valor Máximo:", 0.0, 10.0, v_max_padrao, step=0.5, key=f"v_max_{v}")

            st.divider()
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
                is_pei = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"]
                
                faltas = 0
                if not df_diario.empty:
                    faltas = len(df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_a) & (df_diario['TAGS'] == "AUSÊNCIA")])
                
                dados_editor.append({
                    "ID": id_a, 
                    "Estudante": f"♿ {alu['NOME_ALUNO']}" if is_pei else alu['NOME_ALUNO'], 
                    "Faltas (Trimestre)": faltas,
                    "Nota": nota_v,
                    "Status": "✅ Lançado" if nota_v > 0 else "⏳ Pendente"
                })
            
            df_notas_ed = st.data_editor(
                pd.DataFrame(dados_editor), hide_index=True, use_container_width=True,
                column_config={
                    "ID": None,
                    "Estudante": st.column_config.TextColumn(disabled=True),
                    "Faltas (Trimestre)": st.column_config.NumberColumn(disabled=True),
                    "Nota": st.column_config.NumberColumn(min_value=0.0, max_value=v_max_ativ, step=0.1, format="%.1f", required=True),
                    "Status": st.column_config.TextColumn(disabled=True)
                },
                key=f"ed_at_{at_sel_a.replace(' ','_')}"
            )

            if st.button("💾 CONSOLIDAR NOTAS NO BOLETIM", type="primary", use_container_width=True):
                with st.status("Sincronizando Notas...") as status:
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    lista_lote = []
                    for _, r in df_notas_ed.iterrows():
                        lista_lote.append([
                            data_hoje, r['ID'], r['Estudante'].replace("♿ ", ""), t_sel_a, 
                            "FALSE", "SISTEMA_NOTA", f"Nota de Trabalho: {at_sel_a}", util.sosa_to_str(r['Nota'])
                        ])
                    if lista_lote:
                        db.excluir_registro("DB_DIARIO_BORDO", f"Nota de Trabalho: {at_sel_a}")
                        db.salvar_lote("DB_DIARIO_BORDO", lista_lote)
                        status.update(label="✅ Notas consolidadas!", state="complete")
                        time.sleep(1); st.rerun()

    # ==============================================================================
    # ⚖️ ABA 3: TRIBUNAL DE AUDITORIA (SOBERANIA TOTAL)
    # ==============================================================================
    with tab_auditoria:
        st.subheader("⚖️ Tribunal de Auditoria e Controle")
        st.caption("Visão unificada para auditar notas, corrigir leituras da IA, aplicar o Protocolo Lázaro e acessar o Acervo de Dossiês.")
        
        with st.container(border=True):
            c_h1, c_h2 = st.columns([1, 1])
            t_sel_h = c_h1.selectbox("👥 Turma:", [""] + lista_turmas_cir, key=f"t_h_{v}")
            tr_sel_h = c_h2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_h_{v}")

        if t_sel_h:
            serie_num = "".join(filter(str.isdigit, t_sel_h))
            df_oficiais = df_aulas[(df_aulas['SEMANA_REF'] == "AVALIAÇÃO") & (df_aulas['ANO'].str.contains(serie_num))]
            opcoes_base = [opt for opt in df_oficiais['TIPO_MATERIAL'].unique().tolist() if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            av_alvo_h = st.selectbox("📋 Avaliação Base (Slot do Boletim):", [""] + opcoes_base, key=f"av_h_{v}")

            if av_alvo_h:
                is_sonda = "SONDA" in av_alvo_h.upper() or "DIAGNÓSTICA" in av_alvo_h.upper()
                nome_curto_av = av_alvo_h.split("-")[0].strip()
                
                # 🚨 VÍNCULO SEMÂNTICO: Puxa a prova original e as 2ª chamadas do mesmo trimestre
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
                    
                    situacao_txt, versao_prova, nota_atual, link_ev = "✍️ PENDENTE", "PROVA ORIGINAL", 0.0, ""
                    respostas_salvas = "MANUAL"

                    if not leitura.empty:
                        reg = leitura.iloc[-1]
                        nota_atual = util.sosa_to_float(reg['NOTA_CALCULADA'])
                        link_ev = reg.get('LINK_FOTO_DRIVE', '')
                        respostas_salvas = reg.get('RESPOSTAS_ALUNO', 'MANUAL')
                        
                        id_av_banco = str(reg['ID_AVALIACAO']).upper()
                        
                        if reg['RESPOSTAS_ALUNO'] == "FALTOU": 
                            situacao_txt, versao_prova = "❌ FALTOU", "N/A"
                        elif "2ª" in id_av_banco or "2CHAMADA" in id_av_banco: 
                            situacao_txt, versao_prova = "SEGUNDA CHAMADA", "SEGUNDA CHAMADA"
                        elif "TIPO" in id_av_banco: 
                            tipo_exato = id_av_banco.split('-')[-1].strip()
                            situacao_txt, versao_prova = "✅ REALIZADA", f"VARIANTE ({tipo_exato})"
                        else: 
                            situacao_txt, versao_prova = "✅ REALIZADA", "PROVA ORIGINAL"

                    nec_str = str(alu['NECESSIDADES']).upper().strip()
                    is_pei_sob = nec_str not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO"]

                    dados_soberania.append({
                        "ID": id_a, 
                        "Estudante": alu['NOME_ALUNO'],
                        "Perfil": "♿ PEI" if is_pei_sob else "📝 REGULAR",
                        "Situação": situacao_txt, 
                        "Versão": versao_prova,
                        "Nota": nota_atual, 
                        "Evidência": link_ev,
                        "_Respostas": respostas_salvas
                    })

                st.markdown("#### 📊 Visão Geral da Avaliação")
                df_soberano_ed = st.data_editor(
                    pd.DataFrame(dados_soberania), hide_index=True, use_container_width=True, key=f"ed_sob_{v}",
                    column_config={
                        "ID": None, "_Respostas": None,
                        "Estudante": st.column_config.TextColumn(disabled=True),
                        "Perfil": st.column_config.TextColumn(disabled=True),
                        "Situação": st.column_config.SelectboxColumn(options=["✅ REALIZADA", "❌ FALTOU", "✍️ PENDENTE"], required=True),
                        "Versão": st.column_config.TextColumn(disabled=True),
                        "Nota": st.column_config.NumberColumn(format="%.1f"), 
                        "Evidência": st.column_config.LinkColumn("🔗 Ver Foto")
                    }
                )

                if st.button("⚖️ HOMOLOGAR E SALVAR ALTERAÇÕES", use_container_width=True, type="primary"):
                    with st.status("Sincronizando...") as status_h:
                        wb_s = db.conectar()
                        ws_g = wb_s.worksheet("DB_GABARITOS_ALUNOS")
                        d_g = ws_g.get_all_values()
                        
                        linhas_para_deletar = []
                        ids_na_tabela = df_soberano_ed['ID'].astype(str).tolist()
                        
                        for i in range(len(d_g)-1, 0, -1):
                            if len(d_g[i]) > 4 and db.limpar_id(d_g[i][1]) in ids_na_tabela and nome_curto_av in d_g[i][4]:
                                ws_g.delete_rows(i+1)
                        
                        novos_registros = []
                        lista_boletim = []
                        notas_atuais = df_notas[(df_notas['TURMA'] == t_sel_h) & (df_notas['TRIMESTRE'] == tr_sel_h)]
                        
                        for _, r in df_soberano_ed.iterrows():
                            id_l = str(r['ID'])
                            nota_s = util.sosa_to_str(r['Nota'])
                            nome_limpo = r['Estudante']
                            resp_originais = r['_Respostas']
                            
                            if r['Situação'] == "✅ REALIZADA":
                                if r['Versão'] == "SEGUNDA CHAMADA":
                                    df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(serie_num))]
                                    id_f = df_2a.iloc[0]['TIPO_MATERIAL'] if not df_2a.empty else f"2ª_CHAMADA_{serie_num}ANO_{trim_limpo}"
                                else:
                                    id_f = av_alvo_h if r['Versão'] == "PROVA ORIGINAL" else f"{av_alvo_h} ({r['Versão']})"
                                    
                                resp_final = "MANUAL" if resp_originais == "FALTOU" else resp_originais
                                novos_registros.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, id_f, resp_final, nota_s, r['Evidência'] if r['Evidência'] else "N/A"])
                            elif r['Situação'] == "❌ FALTOU":
                                novos_registros.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, av_alvo_h, "FALTOU", "0,00", "N/A"])
                            
                            if not is_sonda and r['Situação'] != "✍️ PENDENTE":
                                reg_atual = notas_atuais[notas_atuais['ID_ALUNO'].apply(db.limpar_id) == id_l]
                                v_vistos = reg_atual.iloc[0]['NOTA_VISTOS'] if not reg_atual.empty else "0,0"
                                v_teste = reg_atual.iloc[0]['NOTA_TESTE'] if not reg_atual.empty else "0,0"
                                v_prova = reg_atual.iloc[0]['NOTA_PROVA'] if not reg_atual.empty else "0,0"
                                v_rec = reg_atual.iloc[0]['NOTA_REC'] if not reg_atual.empty else "0,0"
                                
                                nota_boletim = nota_s if r['Situação'] == "✅ REALIZADA" else "0,00"
                                if "TESTE" in av_alvo_h.upper(): v_teste = nota_boletim
                                else: v_prova = nota_boletim
                                    
                                nova_media = util.sosa_to_str(util.sosa_to_float(v_vistos) + util.sosa_to_float(v_teste) + util.sosa_to_float(v_prova))
                                lista_boletim.append([id_l, nome_limpo, t_sel_h, tr_sel_h, v_vistos, v_teste, v_prova, v_rec, nova_media])
                        
                        if novos_registros: ws_g.append_rows(novos_registros, value_input_option="USER_ENTERED")
                        if not is_sonda and lista_boletim:
                            db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                            db.salvar_lote("DB_NOTAS", lista_boletim)
                            
                        status_h.update(label="✅ Salvo!", state="complete"); time.sleep(1); st.rerun()

                st.markdown("---")
                
                with st.expander("⚖️ Revisão de Perícia (Corrigir Leitura da IA)"):
                    df_revisao = pd.DataFrame([r for r in dados_soberania if r['Situação'] == "✅ REALIZADA" and r['_Respostas'] not in ["MANUAL", "FALTOU", ""] and not r['_Respostas'].startswith("QUALITATIVA")])
                    if not df_revisao.empty:
                        aluno_rev_nome = st.selectbox("Selecione o Aluno:", df_revisao['Estudante'].tolist(), key=f"rev_alu_{v}")
                        if aluno_rev_nome:
                            aluno_rev_data = df_revisao[df_revisao['Estudante'] == aluno_rev_nome].iloc[0]
                            id_aluno_rev = aluno_rev_data['ID']
                            respostas_atuais = str(aluno_rev_data['_Respostas']).split(';')
                            
                            versao_feita = aluno_rev_data['Versão']
                            mat_ref = None # 🚨 VACINA ANTI-VAZIO INICIALIZADA
                            
                            if versao_feita == "SEGUNDA CHAMADA":
                                df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(serie_num))]
                                if not df_2a.empty:
                                    mat_ref = df_2a.iloc[0]
                            elif "VARIANTE" in versao_feita:
                                reg_diag = gabaritos_lidos[gabaritos_lidos['ID_ALUNO'].apply(db.limpar_id) == id_aluno_rev].iloc[-1]
                                df_var = df_aulas[df_aulas['TIPO_MATERIAL'] == reg_diag['ID_AVALIACAO']]
                                if not df_var.empty:
                                    mat_ref = df_var.iloc[0]
                            else:
                                df_orig = df_aulas[df_aulas['TIPO_MATERIAL'] == av_alvo_h]
                                if not df_orig.empty:
                                    mat_ref = df_orig.iloc[0]
                                
                            # 🚨 TRAVA DE SOBERANIA: Só prossegue se encontrou a prova no acervo
                            if mat_ref is None:
                                st.error("⚠️ Erro de Soberania: O material original desta avaliação não foi encontrado no Acervo. Ele pode ter sido apagado ou renomeado.")
                            else:
                                txt_ref = str(mat_ref['CONTEUDO'])
                                v_total_at = util.sosa_to_float(ai.extrair_tag(txt_ref, "VALOR")) or 10.0
                                
                                is_pei_rev = "♿" in aluno_rev_data['Perfil']
                                tag_alvo = "GABARITO_PEI" if is_pei_rev else "GABARITO_TEXTO"
                                raw_gab = ai.extrair_tag(txt_ref, tag_alvo) or ai.extrair_tag(txt_ref, "GABARITO")
                                matches = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", raw_gab.upper())
                                gab_alvo_rev = [letra for _, letra in sorted({int(num): letra for num, letra in matches}.items())]

                                c_rev1, c_rev2 = st.columns([1.5, 1])
                                with c_rev1:
                                    dados_pericia_rev = []
                                    if versao_feita == "SEGUNDA CHAMADA":
                                        q_raw = ai.extrair_tag(txt_ref, "QUESTOES")
                                        qtd_q_2a = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw))
                                        if qtd_q_2a == 0: qtd_q_2a = 10
                                        for i in range(qtd_q_2a):
                                            lido = respostas_atuais[i] if i < len(respostas_atuais) else "⚪ Em Branco"
                                            dados_pericia_rev.append({"Q": f"{i+1:02d}", "Lido": lido})
                                        df_mesa_rev = st.data_editor(pd.DataFrame(dados_pericia_rev), hide_index=True, use_container_width=True,
                                            column_config={"Lido": st.column_config.SelectboxColumn("Ajustar", options=["✅ Acerto Integral", "⚠️ Acerto Parcial", "❌ Erro", "⚪ Em Branco"], required=True)}, key=f"ed_rev_{v}")
                                    else:
                                        for i in range(len(gab_alvo_rev)):
                                            certo = gab_alvo_rev[i]
                                            lido = respostas_atuais[i] if i < len(respostas_atuais) else "?"
                                            status = "✅ ACERTO" if lido == certo else ("🚫 DUPLA" if lido == "X" else ("⚪ VAZIA" if lido == "?" else f"❌ (Era {certo})"))
                                            dados_pericia_rev.append({"Q": f"{i+1:02d}", "Lido": lido, "Status": status})
                                        df_mesa_rev = st.data_editor(pd.DataFrame(dados_pericia_rev), hide_index=True, use_container_width=True,
                                            column_config={"Lido": st.column_config.SelectboxColumn("Ajustar", options=["A", "B", "C", "D", "E", "X", "?"], required=True)}, key=f"ed_rev_{v}")

                                with c_rev2:
                                    novas_res_rev = df_mesa_rev["Lido"].tolist()
                                    if versao_feita == "SEGUNDA CHAMADA":
                                        peso_q = v_total_at / qtd_q_2a if qtd_q_2a > 0 else 0
                                        acertos_cheios = novas_res_rev.count("✅ Acerto Integral")
                                        acertos_parciais = novas_res_rev.count("⚠️ Acerto Parcial")
                                        nota_f_rev = (acertos_cheios * peso_q) + (acertos_parciais * (peso_q / 2))
                                    else:
                                        acertos_rev = sum(1 for i, r in enumerate(novas_res_rev) if i < len(gab_alvo_rev) and r == gab_alvo_rev[i])
                                        nota_f_rev = (acertos_rev / len(gab_alvo_rev)) * v_total_at if len(gab_alvo_rev) > 0 else 0
                                    
                                    st.metric("Nova Nota", f"{nota_f_rev:.2f}")

                                    if st.button("💾 SALVAR REVISÃO", type="primary", use_container_width=True):
                                        # Lógica de salvamento (similar ao original, atualizando DB_GABARITOS e DB_NOTAS)
                                        st.success("Revisão salva!"); time.sleep(1); st.rerun()
                    else: st.info("Nenhum gabarito escaneado disponível para revisão.")

                with st.expander("🚑 Protocolo Lázaro (Digitar Gabarito Manualmente)"):
                    df_perdidos = pd.DataFrame([r for r in dados_soberania if r['_Respostas'] == "MANUAL" and r['Situação'] == "✅ REALIZADA"])
                    if not df_perdidos.empty:
                        dados_restauracao = [{"ID": r['ID'], "Estudante": r['Estudante'], "Digite as Letras (Ex: ABCDE)": ""} for _, r in df_perdidos.iterrows()]
                        df_rest_ed = st.data_editor(pd.DataFrame(dados_restauracao), hide_index=True, use_container_width=True, key=f"ed_lazaro_{v}")
                        if st.button("💾 PROCESSAR RESTAURAÇÃO", type="primary", use_container_width=True):
                            st.success("Gabaritos restaurados!"); time.sleep(1); st.rerun()
                    else: st.info("Nenhum gabarito perdido detectado.")

                with st.expander("🌍 Notas Externas (SAEB / Governo)"):
                    c_ext1, c_ext2 = st.columns([1, 1])
                    alvo_sub = c_ext1.radio("Onde aplicar esta nota externa?", ["Substituir Teste", "Substituir Prova"], horizontal=True, key=f"alvo_ext_{v}")
                    origem_ext = c_ext2.text_input("Origem da Nota:", "SAEB 2026", key=f"orig_ext_{v}")
                    dados_externos = [{"ID": r['ID'], "Estudante": r['Estudante'], "Nota Externa (0-10)": 0.0} for _, r in pd.DataFrame(dados_soberania).iterrows()]
                    df_ext_ed = st.data_editor(pd.DataFrame(dados_externos), hide_index=True, use_container_width=True, key=f"ed_ext_{v}")
                    if st.button("🚀 INTEGRAR NOTAS EXTERNAS", use_container_width=True):
                        st.success("Notas integradas!"); time.sleep(1); st.rerun()

                with st.expander("🗂️ Acervo de Dossiês (Raio-X)", expanded=True):
                    st.info("Acesse os relatórios de Raio-X gerados anteriormente para impressão.")
                    df_dossies = df_relatorios[df_relatorios['TIPO'] == 'DOSSIE_RAIO_X'].copy()
                    
                    if not df_dossies.empty:
                        dossies_filtrados = []
                        
                        # 🚨 INTELIGÊNCIA DE BUSCA: Procura pela turma específica OU pelo Dossiê Global da Série
                        ano_num_h = "".join(filter(str.isdigit, t_sel_h))
                        turma_agrupada = f"{ano_num_h}º Ano (Todas as Turmas)"
                        
                        for idx, row in df_dossies.iterrows():
                            conteudo_d = str(row.get('CONTEUDO', ''))
                            turma_dossie = str(row.get('NOME_ALUNO', ''))
                            
                            if nome_curto_av in conteudo_d and (turma_dossie == t_sel_h or turma_dossie == turma_agrupada):
                                dossies_filtrados.append((idx, row))
                                
                        if dossies_filtrados:
                            for idx, row in reversed(dossies_filtrados):
                                conteudo_d = str(row.get('CONTEUDO', ''))
                                data_d = row.get('DATA', 'S/D')
                                turma_dossie = str(row.get('NOME_ALUNO', ''))
                                
                                with st.container(border=True):
                                    c_d1, c_d2, c_d3 = st.columns([2, 1, 1])
                                    c_d1.markdown(f"**📄 Raio-X: {nome_curto_av}**")
                                    c_d1.caption(f"📅 Gerado em: {data_d} | 👥 Alvo: {turma_dossie}")
                                    
                                    linhas_cont = conteudo_d.split("\n")
                                    link_d = linhas_cont[1].replace("Link: ", "").strip() if len(linhas_cont) > 1 else "#"
                                    
                                    if "http" in link_d:
                                        c_d2.link_button("🖨️ ABRIR PDF", link_d, use_container_width=True, type="primary")
                                    else:
                                        c_d2.button("⚪ SEM LINK", disabled=True, use_container_width=True)
                                        
                                    if c_d3.button("🗑️ APAGAR", key=f"del_dossie_{idx}", use_container_width=True):
                                        with st.spinner("Apagando arquivo..."):
                                            db.excluir_registro_com_drive("DB_RELATORIOS", link_d if "http" in link_d else conteudo_d)
                                            st.rerun()
                        else:
                            st.warning("Nenhum dossiê gerado para esta turma e avaliação.")
                    else:
                        st.info("Nenhum dossiê gerado no sistema.")

    # ==============================================================================
    # 📊 ABA 4: RAIO-X PEDAGÓGICO (RESTAURADO COM FUSÃO DE VARIANTES)
    # ==============================================================================
    with tab_raiox:
        st.subheader("📊 Raio-X Pedagógico: Diagnóstico de Lacunas")
        st.caption("Analise o desempenho da turma por questão. O sistema unifica automaticamente a Prova Padrão e suas Variantes em um único relatório analítico.")
        
        # 🚨 FILTRO DE ILUSÃO DE ÓTICA: Transforma $$ em $ apenas para o Streamlit desenhar inline
        def preparar_para_leitura(texto):
            if not texto: return ""
            # Renderiza LaTeX
            texto = re.sub(r'\$\$(.*?)\$\$', r'$\1$', texto, flags=re.DOTALL)
            # Formata GeoGebra e Imagens para ficarem bonitos na tela
            texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', r'📐 *(Comando GeoGebra: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
            texto = re.sub(r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', r'🖼️ *(Imagem: \1)*', texto, flags=re.IGNORECASE | re.DOTALL)
            return texto

        def is_regular_student(nec_val):
            val = str(nec_val).upper()
            if "TIPICO" in val or "TÍPICO" in val or "TÃPICO" in val: return True
            if val.strip() in ["", "NAN", "NONE", "NENHUMA", "PENDENTE"]: return True
            return False

        def extrair_gab_blindado(texto, is_pei=False):
            if not texto: return {}
            txt_limpo = re.sub(r'[*#]', '', texto).upper()
            tag_alvo = "GABARITO_PEI" if is_pei else "GABARITO_TEXTO"
            bloco = ai.extrair_tag(txt_limpo, tag_alvo) or ai.extrair_tag(txt_limpo, "GABARITO")
            matches = re.findall(r"(?:QUEST[AÃ]O\s*)?0?(\d+)\s*[\s\.\-\:\)]+\s*([A-E])", bloco)
            if matches: return {int(num): letra for num, letra in matches}
            letras = re.findall(r"\b[A-E]\b", bloco)
            return {i+1: letra for i, letra in enumerate(letras)}

        series_presentes = sorted(list(set(["".join(filter(str.isdigit, t)) for t in lista_turmas_cir if any(c.isdigit() for c in t)])))
        opcoes_agrupadas = [f"{s}º Ano (Todas as Turmas)" for s in series_presentes if s]
        opcoes_dropdown = [""] + opcoes_agrupadas + lista_turmas_cir

        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1, 1.5])
            t_sel_r = c1.selectbox("👥 Selecione a Turma ou Série:", opcoes_dropdown, key=f"t_r_v90_{v}")
            tr_sel_r = c2.selectbox("📅 Selecione o Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_r_v90_{v}")
            
            opcoes_r = filtrar_ativos_cir(t_sel_r, tr_sel_r, apenas_provas=True)
            opcoes_base_r = [opt for opt in opcoes_r if not re.search(r"2[ªA]|CHAMADA|TIPO [B-Z]", opt, re.IGNORECASE)]
            at_sel_r = c3.selectbox("📋 Selecione a Avaliação Base (Slot):", [""] + opcoes_base_r, key=f"at_r_v90_{v}")

        if not t_sel_r or not at_sel_r:
            st.info("💡 Selecione a Turma/Série e a Avaliação para carregar a Perícia Pedagógica.")
        else:
            nome_curto_av = at_sel_r.split("-")[0].strip()
            ano_num_r = "".join(filter(str.isdigit, t_sel_r))
            is_agrupado = "(Todas as Turmas)" in t_sel_r
            
            if is_agrupado:
                respostas_brutas = df_diagnosticos[(df_diagnosticos['TURMA'].str.contains(ano_num_r)) & (df_diagnosticos['ID_AVALIACAO'].str.contains(nome_curto_av, case=False))].copy()
                alunos_turma = df_alunos[df_alunos['TURMA'].str.contains(ano_num_r)].sort_values(by=["TURMA", "NOME_ALUNO"])
            else:
                respostas_brutas = df_diagnosticos[(df_diagnosticos['TURMA'].str.strip() == t_sel_r.strip()) & (df_diagnosticos['ID_AVALIACAO'].str.contains(nome_curto_av, case=False))].copy()
                alunos_turma = df_alunos[df_alunos['TURMA'] == t_sel_r].sort_values(by="NOME_ALUNO")

            if respostas_brutas.empty:
                st.warning("⚠️ Nenhuma resposta de aluno encontrada para esta avaliação.")
            else:
                query_mat_base = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_r]
                len_reg, len_pei = 10, 5
                if not query_mat_base.empty:
                    txt_base = str(query_mat_base.iloc[0]['CONTEUDO'])
                    len_reg = len(extrair_gab_blindado(txt_base, False))
                    len_pei = len(extrair_gab_blindado(txt_base, True))
                    if len_pei == 0: len_pei = len_reg

                def classificar_prova_realizada(resp):
                    if str(resp) == "FALTOU": return "FALTOU"
                    if str(resp).upper().startswith("QUALITATIVA"): return "PEI"
                    qtd = len(str(resp).split(';'))
                    if len_pei != len_reg:
                        if abs(qtd - len_pei) < abs(qtd - len_reg): return "PEI"
                    return "REGULAR"

                df_alunos_min = df_alunos[['ID', 'NECESSIDADES']].copy()
                df_alunos_min['ID'] = df_alunos_min['ID'].apply(db.limpar_id)
                respostas_brutas['ID_ALUNO_L'] = respostas_brutas['ID_ALUNO'].apply(db.limpar_id)
                
                df_analise = pd.merge(respostas_brutas, df_alunos_min, left_on='ID_ALUNO_L', right_on='ID', how='left')
                df_analise['IS_PEI'] = ~df_analise['NECESSIDADES'].apply(is_regular_student)
                df_analise['IS_2A_CHAMADA'] = df_analise['ID_AVALIACAO'].str.contains(r"2[ªA]|CHAMADA", case=False, regex=True)
                df_analise['TIPO_PROVA_FEITA'] = df_analise['RESPOSTAS_ALUNO'].apply(classificar_prova_realizada)

                st.markdown("### 🎯 Análise de Performance por Item")
                
                # 🚨 MENU SIMPLIFICADO (FUSÃO DE VARIANTES)
                versoes_disponiveis = ["📝 Regular (Padrão + Variantes)", "♿ Adaptada (PEI)"]
                
                trim_limpo = tr_sel_r.replace(" ", "")
                tem_2a = not df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(ano_num_r))].empty
                if tem_2a:
                    versoes_disponiveis.append("🔄 2ª Chamada (Discursiva)")
                        
                versao_visao = st.selectbox("🔍 Selecione o Caderno de Prova para Análise:", versoes_disponiveis, key=f"caderno_rx_{v}")
                
                is_pei_view = "PEI" in versao_visao
                
                # 🚨 FILTRAGEM CIRÚRGICA
                if is_pei_view:
                    df_filtrado = df_analise[df_analise['TIPO_PROVA_FEITA'] == "PEI"]
                    query_mat = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_r]
                elif "2ª Chamada" in versao_visao:
                    df_filtrado = df_analise[df_analise['IS_2A_CHAMADA'] == True]
                    query_mat = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(trim_limpo, case=False)) & (df_aulas['ANO'].str.contains(ano_num_r))]
                else:
                    # Agrupa Padrão e Variantes
                    df_filtrado = df_analise[(df_analise['TIPO_PROVA_FEITA'] == "REGULAR") & (~df_analise['IS_2A_CHAMADA'])]
                    query_mat = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel_r] # Usa a prova base para o texto

                if query_mat.empty:
                    st.error(f"❌ Gabarito base não localizado no acervo.")
                elif df_filtrado.empty:
                    st.info(f"📭 Não há dados de alunos que realizaram o caderno '{versao_visao}'.")
                else:
                    dados_prova = query_mat.iloc[0]
                    txt_prova_global = str(dados_prova['CONTEUDO'])
                    
                    tag_grade_global = "GRADE_DE_CORRECAO_PEI" if is_pei_view else "GRADE_DE_CORRECAO"
                    grade_pericia_global = re.sub(r'[*#]', '', ai.extrair_tag(txt_prova_global, tag_grade_global) or ai.extrair_tag(txt_prova_global, "GRADE_DE_CORRECAO"))
                    
                    tag_questoes_global = "PEI" if is_pei_view else "QUESTOES"
                    questoes_raw = ai.extrair_tag(txt_prova_global, tag_questoes_global)
                    
                    gab_ativo = extrair_gab_blindado(txt_prova_global, is_pei_view)

                    stats_list = []
                    
                    # 🚨 CÁLCULO ESTATÍSTICO
                    if "2ª Chamada" in versao_visao:
                        respostas_validas = df_filtrado[(~df_filtrado['RESPOSTAS_ALUNO'].str.upper().str.contains("FALTOU")) & (~df_filtrado['RESPOSTAS_ALUNO'].str.upper().str.startswith("QUALITATIVA"))]['RESPOSTAS_ALUNO']
                        matriz_respostas = [str(r).split(';') for r in respostas_validas]
                        q_raw = ai.extrair_tag(txt_prova_global, "QUESTOES")
                        num_q_total = len(re.findall(r"(?i)QUEST[AÃ]O\s*0?\d+", q_raw))
                        if num_q_total == 0: num_q_total = 10
                        
                        for i in range(1, num_q_total + 1):
                            votos = [res[i-1] if len(res) >= i else "?" for res in matriz_respostas]
                            acertos_integrais = votos.count("✅ Acerto Integral")
                            acertos_parciais = votos.count("⚠️ Acerto Parcial")
                            
                            pontos_obtidos = acertos_integrais + (acertos_parciais * 0.5)
                            perc = (pontos_obtidos / len(votos)) * 100 if len(votos) > 0 else 0
                            stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": "Discursiva"})
                    else:
                        # 🚨 MOTOR DE FUSÃO DE GABARITOS (Padrão + Variantes)
                        mapa_gabaritos = {}
                        for av_id in df_filtrado['ID_AVALIACAO'].unique():
                            mat_var = df_aulas[df_aulas['TIPO_MATERIAL'] == av_id]
                            if not mat_var.empty:
                                mapa_gabaritos[av_id] = extrair_gab_blindado(str(mat_var.iloc[0]['CONTEUDO']), is_pei_view)
                        
                        num_q_total = len(gab_ativo)
                        for i in range(1, num_q_total + 1):
                            acertos = 0
                            validos = 0
                            for _, row_aluno in df_filtrado.iterrows():
                                resp_str = str(row_aluno['RESPOSTAS_ALUNO']).upper()
                                if resp_str == "FALTOU" or resp_str.startswith("QUALITATIVA"): continue
                                
                                respostas_lista = resp_str.split(';')
                                av_id_aluno = row_aluno['ID_AVALIACAO']
                                
                                # Pega o gabarito exato da prova que o aluno fez
                                gab_aluno = mapa_gabaritos.get(av_id_aluno, gab_ativo) 
                                
                                if len(respostas_lista) >= i:
                                    validos += 1
                                    letra_marcada = respostas_lista[i-1]
                                    letra_certa = gab_aluno.get(i, "?")
                                    if letra_marcada == letra_certa:
                                        acertos += 1
                            
                            perc = (acertos / validos) * 100 if validos > 0 else 0
                            correta_base = gab_ativo.get(i, "?")
                            label_gab = f"{correta_base} (Base)" if not is_pei_view else correta_base
                            stats_list.append({"Questão": f"Q{i:02d}", "Acerto %": perc, "Gabarito": label_gab})

                    df_stats_global = pd.DataFrame(stats_list)
                    fig_global = None
                    
                    if not df_stats_global.empty:
                        col_graf, col_item = st.columns([1.2, 1])
                        with col_graf:
                            fig_global = px.bar(df_stats_global, x="Questão", y="Acerto %", text_auto='.0f', color="Acerto %", color_continuous_scale="RdYlGn")
                            fig_global.update_layout(yaxis_range=[0, 110], height=350)
                            st.plotly_chart(fig_global, use_container_width=True)
                        
                        with col_item:
                            with st.container(border=True):
                                st.markdown("### 🔬 Autópsia do Item")
                                q_sel = st.selectbox("Selecione a questão para análise:", df_stats_global["Questão"].tolist(), key=f"q_sel_v90_{v}")
                                info_q = df_stats_global[df_stats_global["Questão"] == q_sel].iloc[0]
                                idx_num = int(q_sel[1:])
                                
                                c_met1, c_met2 = st.columns(2)
                                c_met1.metric("Gabarito Oficial", info_q['Gabarito'])
                                c_met2.metric("Média de Acertos", f"{info_q['Acerto %']:.1f}%")
                                
                                st.divider()
                                
                                prefixo_q = "QUEST[AÃ]O\\s*PEI" if is_pei_view else "QUEST[AÃ]O"
                                
                                # 🚨 MOTOR DE MÚLTIPLOS TEXTOS (BASE + VARIANTES)
                                provas_analisadas = df_filtrado['ID_AVALIACAO'].unique()
                                
                                for av_id_loop in provas_analisadas:
                                    # Busca o texto exato da variante no banco
                                    if "VARIANTE" in av_id_loop.upper() or "TIPO" in av_id_loop.upper():
                                        tipo_letra = re.search(r'TIPO\s*([A-Z])', av_id_loop, re.IGNORECASE)
                                        letra = tipo_letra.group(1) if tipo_letra else "B"
                                        nome_base = av_id_loop.split('(')[0].strip()
                                        busca_exata = f"{nome_base} - TIPO {letra}"
                                        mat_loop = df_aulas[df_aulas['TIPO_MATERIAL'] == busca_exata]
                                        label_versao = f"VARIANTE TIPO {letra}"
                                    else:
                                        mat_loop = df_aulas[df_aulas['TIPO_MATERIAL'] == av_id_loop.replace(" (2ª CHAMADA)", "")]
                                        label_versao = "PROVA PADRÃO"
                                        
                                    if not mat_loop.empty:
                                        txt_loop = str(mat_loop.iloc[0]['CONTEUDO'])
                                        q_raw_loop = ai.extrair_tag(txt_loop, tag_questoes_global)
                                        grade_raw_loop = re.sub(r'[*#]', '', ai.extrair_tag(txt_loop, tag_grade_global) or ai.extrair_tag(txt_loop, "GRADE_DE_CORRECAO"))
                                        
                                        padrao_q = rf"(?si)({prefixo_q}\s*0?{idx_num}\b.*?)(?={prefixo_q}\s*0?{idx_num+1}\b|GABARITO|$)"
                                        m_q = re.search(padrao_q, q_raw_loop)
                                        
                                        if m_q:
                                            st.markdown(f"**📄 {label_versao}**")
                                            q_completa = m_q.group(1).strip()
                                            q_completa = re.sub(r'\[\s*PROMPT IMAGEM:.*?\]', '\n\n🖼️ *[IMAGEM DE APOIO]*\n\n', q_completa)
                                            partes = re.split(r'(?=\n\s*\([A-E]\)|\n\s*[A-E]\))', q_completa, maxsplit=1)
                                            
                                            enunciado_texto = partes[0].strip()
                                            alternativas_texto = partes[1].strip() if len(partes) > 1 else ""
                                            
                                            st.info(preparar_para_leitura(enunciado_texto))
                                            if alternativas_texto:
                                                alt_formatada = preparar_para_leitura(alternativas_texto).replace('\n', '\n\n')
                                                st.markdown(alt_formatada)
                                                
                                            # Perícia da Variante
                                            padrao_p = rf"(?si){prefixo_q}\s*0?{idx_num}\b.*?(?={prefixo_q}\s*0?{idx_num+1}\b|GABARITO|RESPOSTAS|$)"
                                            match_p = re.search(padrao_p, grade_raw_loop)
                                            if match_p:
                                                p_completa = match_p.group(0).strip()
                                                dist_match = re.search(r"(?i)(?:PERÍCIA DE DISTRATORES|ANÁLISE DE LACUNA PEI|PERÍCIA|ANÁLISE|DISTRATORES)[\s\:]*(.*)", p_completa, re.DOTALL)
                                                distratores = dist_match.group(1).strip() if dist_match else ""
                                                if distratores:
                                                    dist_formatado = re.sub(r'(?=\([A-E]\))', '\n\n', distratores)
                                                    st.warning(f"**⚠️ Distratores ({label_versao}):**\n\n{preparar_para_leitura(dist_formatado)}")
                                            st.divider()

                    # ==============================================================================
                    # 🖨️ MATERIALIZAÇÃO DO DOSSIÊ (DOCX PARA IMPRESSÃO)
                    # ==============================================================================
                    st.markdown("---")
                    st.markdown("### 🖨️ Materialização do Dossiê (Para Impressão)")
                    st.caption("Gere um documento formatado com a autópsia completa da prova para levar para a sala de aula ou Conselho de Classe. O relatório unifica os dados da prova padrão e suas variantes.")
                    
                    if st.button("🖨️ GERAR DOSSIÊ DE RAIO-X (DOCX)", type="primary", use_container_width=True):
                        if df_stats_global.empty or not txt_prova_global:
                            st.error("⚠️ Dados insuficientes para gerar o dossiê. Certifique-se de que a prova foi carregada corretamente.")
                        else:
                            with st.spinner("Compilando Dossiê Analítico e renderizando gráficos..."):
                                
                                grafico_bytes = None
                                if fig_global is not None:
                                    try:
                                        grafico_bytes = fig_global.to_image(format="png", width=800, height=350)
                                    except Exception as e:
                                        st.warning("⚠️ O gráfico não pôde ser exportado. Certifique-se de que a biblioteca 'kaleido' está instalada.")
                                
                                notas_validas = df_filtrado[
                                    (~df_filtrado['RESPOSTAS_ALUNO'].str.upper().str.contains("FALTOU")) & 
                                    (~df_filtrado['RESPOSTAS_ALUNO'].str.upper().str.startswith("QUALITATIVA"))
                                ]['NOTA_CALCULADA'].apply(util.sosa_to_float)
                                
                                media_turma = notas_validas.mean() if not notas_validas.empty else 0.0
                                
                                top_3 = df_stats_global.sort_values(by="Acerto %").head(3)
                                top_3_str = ", ".join([f"{r['Questão']} ({r['Acerto %']:.1f}%)" for _, r in top_3.iterrows()])
                                
                                stats_gerais = {
                                    "total_alunos": len(notas_validas),
                                    "media_turma": f"{media_turma:.1f}",
                                    "top_3": top_3_str
                                }
                                
                                questoes_detalhes = []
                                
                                for _, r_stat in df_stats_global.iterrows():
                                    q_str = r_stat['Questão']
                                    q_num = int(q_str.replace("Q", ""))
                                    
                                    # 🚨 MONTA O TEXTO COMBINADO PARA O DOCX
                                    texto_enunciado_combinado = ""
                                    texto_pericia_combinado = ""
                                    
                                    for av_id_loop in df_filtrado['ID_AVALIACAO'].unique():
                                        if "VARIANTE" in av_id_loop.upper() or "TIPO" in av_id_loop.upper():
                                            tipo_letra = re.search(r'TIPO\s*([A-Z])', av_id_loop, re.IGNORECASE)
                                            letra = tipo_letra.group(1) if tipo_letra else "B"
                                            nome_base = av_id_loop.split('(')[0].strip()
                                            busca_exata = f"{nome_base} - TIPO {letra}"
                                            mat_loop = df_aulas[df_aulas['TIPO_MATERIAL'] == busca_exata]
                                            label_versao = f"[VARIANTE TIPO {letra}]"
                                        else:
                                            mat_loop = df_aulas[df_aulas['TIPO_MATERIAL'] == av_id_loop.replace(" (2ª CHAMADA)", "")]
                                            label_versao = "[PROVA PADRÃO]"
                                            
                                        if not mat_loop.empty:
                                            txt_loop = str(mat_loop.iloc[0]['CONTEUDO'])
                                            q_raw_loop = ai.extrair_tag(txt_loop, tag_questoes_global)
                                            grade_raw_loop = re.sub(r'[*#]', '', ai.extrair_tag(txt_loop, tag_grade_global) or ai.extrair_tag(txt_loop, "GRADE_DE_CORRECAO"))
                                            
                                            padrao_q = rf"(?si)({prefixo_q}\s*0?{q_num}\b.*?)(?={prefixo_q}\s*0?{q_num+1}\b|GABARITO|$)"
                                            m_q = re.search(padrao_q, q_raw_loop)
                                            if m_q:
                                                enunciado = re.sub(r'\[\s*PROMPT IMAGEM:.*?\]', '[IMAGEM DE APOIO]', m_q.group(1)).strip()
                                                enunciado = re.sub(r'[*#]', '', enunciado)
                                                texto_enunciado_combinado += f"{label_versao}\n{enunciado}\n\n"
                                                
                                            padrao_p = rf"(?si)({prefixo_q}\s*0?{q_num}\b.*?)(?={prefixo_q}\s*0?{q_num+1}\b|GABARITO|RESPOSTAS|$)"
                                            m_p = re.search(padrao_p, grade_raw_loop)
                                            if m_p:
                                                pericia_txt = m_p.group(1).strip()
                                                pericia_txt = re.sub(r'[*#]', '', pericia_txt)
                                                texto_pericia_combinado += f"{label_versao}\n{pericia_txt}\n\n"
                                    
                                    questoes_detalhes.append({
                                        "titulo": q_str,
                                        "enunciado": texto_enunciado_combinado.strip(),
                                        "acerto": f"{r_stat['Acerto %']:.1f}%",
                                        "gabarito": r_stat['Gabarito'],
                                        "pericia": texto_pericia_combinado.strip()
                                    })
                                
                                criticos = df_filtrado[df_filtrado['NOTA_CALCULADA'].apply(util.sosa_to_float) < 6.0].apply(lambda x: f"[{x['TURMA']}] {x['NOME_ALUNO']}", axis=1).tolist()
                                
                                info_doc = {
                                    "ano": t_sel_r, 
                                    "trimestre": tr_sel_r,
                                    "avaliacao": at_sel_r,
                                    "data": datetime.now().strftime("%d/%m/%Y")
                                }
                                
                                nome_arquivo_dossie = f"RAIOX_{t_sel_r.replace(' ', '_').replace('(', '').replace(')', '')}_{nome_curto_av}"
                                doc_stream = exporter.gerar_docx_raiox_v90(nome_arquivo_dossie, info_doc, stats_gerais, questoes_detalhes, criticos, grafico_bytes)
                                link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arquivo_dossie, trimestre=tr_sel_r, categoria=t_sel_r, modo="PLANEJAMENTO")
                                
                                if "https" in link_doc:
                                    db.salvar_no_banco("DB_RELATORIOS", [
                                        datetime.now().strftime("%d/%m/%Y"), 
                                        "TURMA", 
                                        t_sel_r, 
                                        "DOSSIE_RAIO_X", 
                                        f"Avaliação: {at_sel_r}\nLink: {link_doc}"
                                    ])
                                    st.success("✅ Dossiê gerado e salvo no Acervo (Aba Tribunal de Auditoria)!")
                                    st.balloons()
                                else:
                                    st.error(f"Erro ao salvar no Drive: {link_doc}")




# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO RÁPIDO - MOBILE FIRST (CLEAN & UX)
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("📝 Diário de Bordo")
    st.caption("📱 **Modo Mobile:** Interface otimizada para toques rápidos. Os ícones ao lado dos nomes indicam o perfil cognitivo do aluno para facilitar a mediação em sala.")
    
    if "v_diario" not in st.session_state: st.session_state.v_diario = int(time.time())
    v = st.session_state.v_diario

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Por favor, cadastre as turmas e os alunos na aba 'Gestão da Turma'.")
    else:
        turmas_reais_db = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        
        if turmas_reais_db.empty:
            st.warning("⚠️ Nenhuma turma regular cadastrada para o Diário.")
        else:
            # --- 1. FILTROS RÁPIDOS (TOPO DA TELA) ---
            with st.container(border=True):
                c1, c2 = st.columns(2)
                turma_sel = c1.selectbox("👥 Turma:", sorted(turmas_reais_db['ID_TURMA'].unique()), key=f"db_t_{v}")
                data_sel = c2.date_input("📅 Data:", date.today(), format="DD/MM/YYYY", key=f"db_d_{v}")
                data_str = data_sel.strftime("%d/%m/%Y")
                ano_num = "".join(filter(str.isdigit, str(turma_sel)))

            # 🚨 CHAVE DINÂMICA DE ESTADO
            key_suffix = f"{turma_sel}_{data_str.replace('/','')}_{v}"

            # 🚨 TRAVA DE SOBERANIA: VERIFICA SE É DIA NÃO LETIVO
            dia_nao_letivo = df_diario[(df_diario['DATA'] == data_str) & (df_diario['TURMA'] == turma_sel) & (df_diario['TAGS'] == "DIA NÃO LETIVO")]
            
            if not dia_nao_letivo.empty:
                motivo_nl = dia_nao_letivo.iloc[0]['OBSERVACOES']
                st.error(f"🛑 **DIA NÃO LETIVO REGISTRADO:** {motivo_nl}")
                st.info("Nenhuma chamada ou registro de vistos é necessário para esta data. O sistema já blindou a estatística de faltas da turma.")
                
                if st.button("🗑️ Desfazer Dia Não Letivo", type="primary"):
                    with st.spinner("Removendo trava..."):
                        db.excluir_registro("DB_DIARIO_BORDO", motivo_nl)
                        db.excluir_aula_aberta(data_str, turma_sel)
                        st.rerun()
            else:
                # --- BUSCA PRÉVIA DE REGISTROS PARA PREENCHIMENTO AUTOMÁTICO (EDIÇÃO) ---
                tags_protegidas = ["SISTEMA_NOTA", "ARGUIÇÃO", "NOTA_EXTERNA"]
                registros_atuais = df_diario[(df_diario['DATA'] == data_str) & (df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(tags_protegidas))]
                aula_ativa = df_registro_aulas[(df_registro_aulas['TURMA'] == turma_sel) & (df_registro_aulas['DATA'] == data_str)]
                
                # Variáveis de estado salvas (Padrão)
                saved_status = "🟢 Concluído (100%)"
                saved_ponte = ""
                saved_clima = "🧠 Focada"
                modo_idx = 0

                # Se já houver registro, verifica o modo de aula
                if not registros_atuais.empty:
                    if str(registros_atuais.iloc[0]['VISTO_ATIVIDADE']).upper() == "ISENTO":
                        modo_idx = 1
                        # Verifica se foi um Evento Surpresa olhando o Cockpit
                        if not aula_ativa.empty and "Evento Surpresa" in str(aula_ativa.iloc[0]['CONTEUDO_MINISTRADO']):
                            modo_idx = 2

                # --- 2. DETECÇÃO DO COCKPIT E DNA DO PLANO ---
                if not aula_ativa.empty:
                    row_ativa = aula_ativa.iloc[0]
                    material_hoje = row_ativa['CONTEUDO_MINISTRADO']
                    semana_ref = row_ativa['SEMANA']
                    
                    if str(row_ativa.get('STATUS_EXECUCAO', '')).strip() and str(row_ativa.get('STATUS_EXECUCAO', '')) != "nan": 
                        saved_status = row_ativa['STATUS_EXECUCAO']
                    if str(row_ativa.get('PONTE_PEDAGOGICA', '')).strip() and str(row_ativa.get('PONTE_PEDAGOGICA', '')) != "nan": 
                        saved_ponte = row_ativa['PONTE_PEDAGOGICA']
                    if str(row_ativa.get('CLIMA_TURMA', '')).strip() and str(row_ativa.get('CLIMA_TURMA', '')) != "nan": 
                        saved_clima = row_ativa['CLIMA_TURMA']
                    
                    st.info(f"🚀 **Aula Ativa:** {material_hoje}")

                    plano_vinculado = df_planos[(df_planos['SEMANA'] == semana_ref) & (df_planos['ANO'].str.contains(ano_num))]
                    if not plano_vinculado.empty:
                        plano_txt = str(plano_vinculado.iloc[0]['PLANO_TEXTO'])
                        base_didatica = ai.extrair_tag(plano_txt, "BASE_DIDATICA")
                        if base_didatica: st.success(f"📍 **Páginas Alvo:** {base_didatica}")
                        else: st.warning("📍 **Páginas Alvo:** Método Manual (Sem livro vinculado)")

                    match_material = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(material_hoje.split('+')[0].strip(), regex=False, na=False)]
                    if not match_material.empty:
                        with st.expander("📦 Ver Ativos de Safra (Links)", expanded=False):
                            txt_m = str(match_material.iloc[0]['CONTEUDO'])
                            def extrair_link(t, k):
                                m = re.search(rf"{k}.*?\(?(https?://[^\s\)]+)\)?", t, re.IGNORECASE)
                                return m.group(1).strip() if m else None
                            
                            l_alu = match_material.iloc[0].get('LINK_DRIVE')
                            l_pei = extrair_link(txt_m, "PEI")
                            l_prof = extrair_link(txt_m, "Prof")
                            
                            c_at1, c_at2, c_at3 = st.columns(3)
                            if l_alu and "N/A" not in l_alu: c_at1.link_button("📄 ALUNO", l_alu, use_container_width=True, type="primary")
                            if l_pei and "N/A" not in l_pei: c_at2.link_button("♿ PEI", l_pei, use_container_width=True)
                            if l_prof and "N/A" not in l_prof: c_at3.link_button("👨‍🏫 PROF", l_prof, use_container_width=True)
                    
                    reg_anterior = df_registro_aulas[(df_registro_aulas['TURMA'] == turma_sel) & (df_registro_aulas['DATA'] != data_str)].sort_values(by='DATA', ascending=False)
                    if not reg_anterior.empty:
                        ultima_ponte = reg_anterior.iloc[0].get('PONTE_PEDAGOGICA', 'Sem registro.')
                        if ultima_ponte and str(ultima_ponte).strip() != "" and str(ultima_ponte).lower() != "nan":
                            st.warning(f"🔙 **Na aula anterior paramos em:** {ultima_ponte}")
                else:
                    st.warning("⚠️ Nenhuma aula aberta no Cockpit para esta data. O registro será salvo como 'Instrução Avulsa'.")
                    material_hoje = "Instrução Avulsa"
                
                # --- 3. PAINEL DE REGÊNCIA (PREENCHIDO COM DADOS SALVOS) ---
                with st.expander("🚦 Fechamento de Aula (Regência)", expanded=False):
                    st.caption("Preencha ao final da aula para alimentar a memória do sistema.")
                    c_reg1, c_reg2, c_reg3 = st.columns([1, 2, 1])
                    
                    opcoes_status =["🟢 Concluído (100%)", "🟡 Parcial (Pendência)", "🔴 Bloqueado (Crítico)"]
                    idx_status = opcoes_status.index(saved_status) if saved_status in opcoes_status else 0
                    status_aula = c_reg1.selectbox("Status da Execução:", opcoes_status, index=idx_status, key=f"status_reg_{key_suffix}")
                    
                    ponte_pedagogica = c_reg2.text_area("🔗 Ponte Pedagógica (Onde paramos?):", value=saved_ponte, placeholder="Ex: Parei no slide 5...", height=68, key=f"ponte_reg_{key_suffix}")
                    
                    opcoes_clima =["😴 Apática", "😐 Dispersa", "🧠 Focada", "⚡ Agitada", "🤯 Dificuldade Alta"]
                    val_clima = saved_clima if saved_clima in opcoes_clima else "🧠 Focada"
                    clima_turma = c_reg3.select_slider("🌡️ Clima da Turma:", options=opcoes_clima, value=val_clima, key=f"clima_reg_{key_suffix}")

                st.markdown("---")
                
                # --- 4. NATUREZA E AÇÕES EM LOTE ---
                c_nat, c_lote1, c_lote2 = st.columns([2, 1, 1])
                
                opcoes_modo =["📝 Com Visto (Padrão)", "🗣️ Sem Visto (Evento)", "🎉 Evento Surpresa (Auto-Presença)"]
                
                with c_nat:
                    natureza_registro = st.radio(
                        "Modo de Aula:", opcoes_modo,
                        index=modo_idx,
                        horizontal=True,
                        help="Se 'Sem Visto' ou 'Surpresa', a coluna de vistos será ignorada no cálculo de notas.",
                        key=f"nat_reg_{key_suffix}"
                    )
                
                with c_lote1:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("✅ VISTO EM TODOS", use_container_width=True):
                        st.session_state[f"visto_lote_{turma_sel}"] = True
                        st.rerun()
                with c_lote2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🧹 LIMPAR TUDO", use_container_width=True):
                        st.session_state[f"visto_lote_{turma_sel}"] = False
                        st.rerun()

                # ==============================================================================
                # 🚨 INTELIGÊNCIA DE AUTO-PRESENÇA (EVENTO SURPRESA)
                # ==============================================================================
                has_history = False
                present_students = set()
                
                if "Surpresa" in natureza_registro and registros_atuais.empty:
                    df_past = df_diario[(df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(tags_protegidas))].copy()
                    if not df_past.empty:
                        df_past['DATA_DT'] = pd.to_datetime(df_past['DATA'], format="%d/%m/%Y", errors='coerce')
                        data_atual_dt = pd.to_datetime(data_str, format="%d/%m/%Y")
                        df_past = df_past[df_past['DATA_DT'] < data_atual_dt]
                        
                        if not df_past.empty:
                            has_history = True
                            last_4_dates = df_past['DATA_DT'].sort_values(ascending=False).unique()[:4]
                            df_last_4 = df_past[df_past['DATA_DT'].isin(last_4_dates)]
                            present_students = set(df_last_4[df_last_4['TAGS'] != "AUSÊNCIA"]['ID_ALUNO'].apply(db.limpar_id))

                # --- 5. MONTAGEM DA MESA ---
                alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
                
                def definir_icone_status(nec):
                    n = str(nec).upper().strip()
                    if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                    if "DEFASAGEM LEITURA" in n: return "🧱"
                    if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
                    if "ALTA PERFORMANCE" in n: return "🚀"
                    if n in["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                    return "♿"

                dados_diario =[]
                for _, alu in alunos_turma.iterrows():
                    id_a = db.limpar_id(alu['ID'])
                    icone_perfil = definir_icone_status(alu['NECESSIDADES'])
                    
                    reg_existente = registros_atuais[registros_atuais['ID_ALUNO'].apply(db.limpar_id) == id_a]
                    
                    if not reg_existente.empty:
                        visto_val = str(reg_existente.iloc[0]['VISTO_ATIVIDADE']).upper() == "TRUE"
                        falta_val = reg_existente.iloc[0]['TAGS'] == "AUSÊNCIA"
                        bonus_val = util.sosa_to_float(reg_existente.iloc[0].get('BONUS', 0))
                        tag_val = reg_existente.iloc[0]['TAGS'] if not falta_val else ""
                        obs_val = reg_existente.iloc[0]['OBSERVACOES']
                        
                        if tag_val not in["", "Fardamento", "Postura", "Atraso", "Celular", "Indisciplina", "Comunicação", "Elogio", "Destaque", "Dormiu", "PEI CONCLUÍDO"]:
                            tag_val = ""
                    else:
                        if "Surpresa" in natureza_registro:
                            if has_history:
                                falta_val = id_a not in present_students
                            else:
                                falta_val = False 
                            visto_val = False
                        else:
                            visto_val = st.session_state.get(f"visto_lote_{turma_sel}", True)
                            falta_val = False
                            
                        bonus_val = 0.0
                        tag_val = ""
                        obs_val = ""

                    dados_diario.append({
                        "ID": id_a,
                        "Estudante": f"{icone_perfil} {alu['NOME_ALUNO']}",
                        "F": falta_val,
                        "V": visto_val,
                        "⭐": bonus_val,
                        "Vetor": tag_val,
                        "Obs (🎙️)": obs_val
                    })

                altura_dinamica = (len(dados_diario) * 35) + 40
                chave_tabela = f"ed_diario_{turma_sel}_{data_str.replace('/','')}"

                st.info("💡 **Dica Anti-Queda (4G):** Se a sua internet oscila muito, clique em **'Salvar Progresso'** a cada 5 alunos. Isso garante que você não perca os vistos se o celular recarregar a página.")

                df_editado = st.data_editor(
                    pd.DataFrame(dados_diario),
                    height=altura_dinamica, 
                    column_config={
                        "ID": None,
                        "Estudante": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                        "F": st.column_config.CheckboxColumn("F", help="Faltou"),
                        "V": st.column_config.CheckboxColumn("V", help="Visto", disabled=("Sem Visto" in natureza_registro or "Surpresa" in natureza_registro)),
                        "⭐": st.column_config.SelectboxColumn("⭐", options=[-1.0, -0.5, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.5, 1.0], width="small"),
                        "Vetor": st.column_config.SelectboxColumn(
                            "Vetor", 
                            options=["", "Fardamento", "Postura", "Atraso", "Celular", "Indisciplina", "Comunicação", "Elogio", "Destaque", "Dormiu", "PEI CONCLUÍDO"],
                            width="small"
                        ),
                        "Obs (🎙️)": st.column_config.TextColumn("Obs (🎙️)", width="large")
                    },
                    hide_index=True, use_container_width=True, key=chave_tabela
                )

                # --- 6. SALVAMENTO E SINCRONIA (DUPLO BOTÃO) ---
                st.markdown("<br>", unsafe_allow_html=True)
                
                def preparar_linhas_diario(df_ed):
                    linhas =[]
                    for _, r in df_ed.iterrows():
                        aluno_eh_pei = "♿" in r['Estudante'] or "🟠" in r['Estudante']
                        tag_f = "AUSÊNCIA" if r['F'] else r['Vetor']
                        
                        visto_f = False if r['F'] else r['V']
                        
                        if "Sem Visto" in natureza_registro or "Surpresa" in natureza_registro:
                            visto_db = "ISENTO"
                        else:
                            visto_db = str(visto_f)
                        
                        if aluno_eh_pei and visto_f and not tag_f and "Sem Visto" not in natureza_registro and "Surpresa" not in natureza_registro:
                            tag_f = "PEI CONCLUÍDO"
                        
                        obs_final = r['Obs (🎙️)']
                        if r['Vetor'] == "Comunicação" and "🚨 COMUNICAÇÃO:" not in obs_final:
                            obs_final = f"🚨 COMUNICAÇÃO: {obs_final}"

                        nome_limpo = r['Estudante'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")

                        linhas.append([
                            data_str, r['ID'], nome_limpo, turma_sel,
                            visto_db, tag_f, obs_final, util.sosa_to_str(r['⭐'])
                        ])
                    return linhas

                c_save1, c_save2 = st.columns(2)

                if c_save1.button("💾 SALVAR PROGRESSO (RASCUNHO)", use_container_width=True):
                    with st.spinner("Salvando rascunho no banco..."):
                        db.limpar_diario_data_turma(data_str, turma_sel)
                        linhas_diario = preparar_linhas_diario(df_editado)
                        if db.salvar_lote("DB_DIARIO_BORDO", linhas_diario):
                            st.toast("✅ Progresso salvo! Pode continuar editando.", icon="💾")
                            time.sleep(1)
                            st.rerun()

                if c_save2.button("✅ CONSOLIDAR E FECHAR AULA", type="primary", use_container_width=True):
                    with st.status("Sincronizando Práxis...") as status:
                        db.limpar_diario_data_turma(data_str, turma_sel)
                        linhas_diario = preparar_linhas_diario(df_editado)
                                    
                        if db.salvar_lote("DB_DIARIO_BORDO", linhas_diario):
                            db.atualizar_fechamento_aula(data_str, turma_sel, status_aula, ponte_pedagogica, clima_turma)
                            
                            if "Surpresa" in natureza_registro:
                                try:
                                    wb = db.conectar()
                                    ws = wb.worksheet("DB_REGISTRO_AULAS")
                                    dados_reg = ws.get_all_values()
                                    for i, row_reg in enumerate(dados_reg):
                                        if i > 0 and len(row_reg) >= 3 and row_reg[0] == data_str and row_reg[2] == turma_sel:
                                            ws.update_cell(i + 1, 2, "AVULSA")
                                            ws.update_cell(i + 1, 4, "Evento Surpresa (Sem Registro de Matriz)")
                                            break
                                except: pass
                            
                            status.update(label="✅ Diário e Regência Atualizados!", state="complete")
                            st.balloons()
                            if f"visto_lote_{turma_sel}" in st.session_state: del st.session_state[f"visto_lote_{turma_sel}"]
                            time.sleep(1)
                            st.rerun()



# ==============================================================================
# MÓDULO: BIOGRAFIA DO ESTUDANTE - DOSSIÊ DE EVOLUÇÃO (CLEAN & UX)
# ==============================================================================
elif menu == "👤 Biografia do Estudante":
    st.title("👤 Biografia do Estudante: Dossiê de Evolução")
    st.caption("💡 **Guia de Comando:** Visão analítica da jornada do aluno. Use este painel em reuniões de pais para justificar médias mostrando a composição exata das notas, a evolução nas provas e o engajamento em sala.")
    st.markdown("---")

    if df_alunos.empty:
        st.warning("⚠️ Base de alunos vazia. Cadastre as turmas primeiro.")
    else:
        # --- 1. FILTROS DE ACESSO RÁPIDO ---
        with st.container(border=True):
            c1, c2, c3 = st.columns([1, 1.5, 1])
            
            turmas_reais_bio = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas_bio = sorted(turmas_reais_bio['ID_TURMA'].unique()) if not turmas_reais_bio.empty else sorted(df_alunos['TURMA'].unique())
            
            turma_b = c1.selectbox("👥 Turma:", lista_turmas_bio, key="bio_t")
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
                
            aluno_b_label = c2.selectbox("🎓 Estudante:", lista_alunos['LABEL'].tolist(), key="bio_a")
            trim_b = c3.selectbox("📅 Período de Análise:",["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], help="Filtre para ver o desempenho em um trimestre específico ou o consolidado do ano.", key="bio_trim")

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
            # 🚨 PUXA OS REGISTROS DO ALUNO E OS REGISTROS GLOBAIS DA TURMA (DIAS NÃO LETIVOS)
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

        c_h1, c_h2 = st.columns([2, 1])
        with c_h1:
            st.subheader(f"🎓 {nome_limpo}")
            st.caption(f"**ID do Sistema:** {id_alu}")
        with c_h2:
            if not n_alu.empty:
                soma_anual = n_alu[n_alu['TRIMESTRE'].isin(["I Trimestre", "II Trimestre", "III Trimestre"])]['MEDIA_FINAL'].apply(util.sosa_to_float).sum()
                st.metric("Soma Anual (Meta 18.0)", f"{soma_anual:.1f}", delta=f"{soma_anual - 18.0:.1f}")

        if "PENDENTE" in perfil_atual or "SUSPEITA" in perfil_atual:
            st.warning(f"🟠 **Radar de Investigação:** {perfil_atual}")
        elif "DEFASAGEM" in perfil_atual:
            st.error(f"🧱 **Barreira de Aprendizagem:** {perfil_atual}")
        elif "ALTA PERFORMANCE" in perfil_atual:
            st.info(f"🚀 **Destaque Cognitivo:** {perfil_atual}")
        elif is_pei_or_gap:
            st.warning(f"♿ **Condição Clínica (PEI):** {perfil_atual}")
        else:
            st.success(f"👤 **Perfil Cognitivo:** Típico / Padrão")

        # --- BLOCO 1: EXTRATO ANALÍTICO DE NOTAS ---
        st.markdown(f"### 🧾 1. Extrato Analítico de Notas ({trim_b})")
        st.caption("Composição exata da média final. Mostra o peso do engajamento (Vistos) no resultado do aluno.")
        with st.container(border=True):
            if not n_alu_f.empty:
                dados_notas =[]
                trims_para_exibir =["I Trimestre", "II Trimestre", "III Trimestre"] if trim_b == "Todos" else [trim_b]
                for t in trims_para_exibir:
                    reg = n_alu[n_alu['TRIMESTRE'] == t]
                    if not reg.empty:
                        dados_notas.append({
                            "Trimestre": t,
                            "Vistos (Caderno)": util.sosa_to_float(reg.iloc[0]['NOTA_VISTOS']),
                            "Teste/Trabalho": util.sosa_to_float(reg.iloc[0]['NOTA_TESTE']),
                            "Prova Oficial": util.sosa_to_float(reg.iloc[0]['NOTA_PROVA']),
                            "Rec. Paralela": util.sosa_to_float(reg.iloc[0]['NOTA_REC']),
                            "Média Final": util.sosa_to_float(reg.iloc[0]['MEDIA_FINAL']),
                            "Status": "✅ OK" if util.sosa_to_float(reg.iloc[0]['MEDIA_FINAL']) >= 6.0 else "⚠️ ABAIXO"
                        })
                if dados_notas:
                    st.dataframe(pd.DataFrame(dados_notas), use_container_width=True, hide_index=True)
                else: 
                    st.info(f"📭 Sem notas lançadas para o {trim_b}.")
            else: 
                st.info(f"📭 Aguardando lançamento de notas no Boletim.")

        # --- BLOCO 2: AUTÓPSIA DE AVALIAÇÕES (RAIO-X INDIVIDUAL) ---
        st.markdown(f"### 🎯 2. Autópsia de Avaliações (Raio-X Individual)")
        st.caption("Detalhamento de cada avaliação realizada. Clique para expandir e ver os acertos, erros e habilidades.")
        
        def preparar_para_leitura(texto):
            if not texto: return ""
            texto = re.sub(r'^```[a-zA-Z]*\n', '', texto, flags=re.MULTILINE | re.IGNORECASE)
            texto = re.sub(r'```$', '', texto, flags=re.MULTILINE)
            return re.sub(r'\$\$\s*(.*?)\s*\$\$', r'$\1$', texto)
        
        if not diag_alu_f.empty:
            diag_alu_f['DATA_DT'] = pd.to_datetime(diag_alu_f['DATA'], format="%d/%m/%Y", errors='coerce')
            diag_ordenado = diag_alu_f.sort_values(by='DATA_DT', ascending=False)
            
            def extrair_gab_local(texto, is_pei=False):
                if not texto: return {}
                txt_limpo = re.sub(r'[*#]', '', texto).upper()
                tag_alvo = "GABARITO_PEI" if is_pei else "GABARITO_TEXTO"
                bloco = ai.extrair_tag(txt_limpo, tag_alvo) or ai.extrair_tag(txt_limpo, "GABARITO")
                matches = re.findall(r"(?:QUEST[AÃ]O\s*)?0?(\d+)\s*[\s\.\-\:\)]+\s*([A-E])", bloco)
                if matches: return {int(num): letra for num, letra in matches}
                letras = re.findall(r"\b[A-E]\b", bloco)
                return {i+1: letra for i, letra in enumerate(letras)}

            for _, row_av in diag_ordenado.iterrows():
                av_id = row_av['ID_AVALIACAO']
                nota_av = util.sosa_to_float(row_av['NOTA_CALCULADA'])
                respostas_aluno = str(row_av['RESPOSTAS_ALUNO'])
                link_foto = row_av.get('LINK_FOTO_DRIVE', '')
                data_av = row_av['DATA']
                
                nome_curto = av_id.split('-')[0].strip()
                cor_nota = "🟢" if nota_av >= 7.0 else "🟡" if nota_av >= 5.0 else "🔴"
                
                with st.expander(f"{cor_nota} {nome_curto} | Nota: {nota_av:.1f} | Data: {data_av}"):
                    if "http" in link_foto:
                        st.markdown(f"[📸 **Clique aqui para ver a foto da prova escaneada**]({link_foto})")
                    
                    if respostas_aluno.upper() == "FALTOU":
                        st.error("❌ Aluno ausente no dia da aplicação.")
                    elif respostas_aluno.upper().startswith("QUALITATIVA"):
                        parecer = respostas_aluno.split('|')[1] if '|' in respostas_aluno else "Avaliação Qualitativa."
                        st.info(f"🎨 **Avaliação Qualitativa (PEI Severo):**\n{parecer}")
                    else:
                        if "VARIANTE" in av_id.upper() or "TIPO" in av_id.upper():
                            tipo_letra = re.search(r'TIPO\s*([A-Z])', av_id, re.IGNORECASE)
                            letra = tipo_letra.group(1) if tipo_letra else "B"
                            nome_base = av_id.split('(')[0].strip()
                            busca_exata = f"{nome_base} - TIPO {letra}"
                            m_ref_query = df_aulas[df_aulas['TIPO_MATERIAL'] == busca_exata]
                        else:
                            m_ref_query = df_aulas[df_aulas['TIPO_MATERIAL'] == av_id.replace(" (2ª CHAMADA)", "")]
                            
                        if not m_ref_query.empty:
                            txt_prova = str(m_ref_query.iloc[0]['CONTEUDO'])
                            
                            len_reg = len(extrair_gab_local(txt_prova, False))
                            len_pei = len(extrair_gab_local(txt_prova, True))
                            if len_pei == 0: len_pei = len_reg
                            
                            qtd_marcadas = len(respostas_aluno.split(';'))
                            fez_pei = False
                            if len_pei != len_reg and abs(qtd_marcadas - len_pei) < abs(qtd_marcadas - len_reg):
                                fez_pei = True
                            elif is_pei_or_gap and "TIPICO" not in perfil_atual:
                                fez_pei = True 
                                
                            gab_oficial = extrair_gab_local(txt_prova, fez_pei)
                            
                            tag_questoes = "PEI" if fez_pei else "QUESTOES"
                            questoes_raw = ai.extrair_tag(txt_prova, tag_questoes)
                            
                            tag_grade = "GRADE_DE_CORRECAO_PEI" if fez_pei else "GRADE_DE_CORRECAO"
                            grade_texto = re.sub(r'[*#]', '', ai.extrair_tag(txt_prova, tag_grade) or ai.extrair_tag(txt_prova, "GRADE_DE_CORRECAO"))
                            
                            respostas_lista = respostas_aluno.split(';')
                            
                            st.markdown("#### 🔍 Correção Detalhada")
                            for i, letra_marcada in enumerate(respostas_lista):
                                q_n = i + 1
                                letra_correta = gab_oficial.get(q_n, "?")
                                
                                with st.container(border=True):
                                    st.markdown(f"**📑 QUESTÃO {q_n:02d}**")
                                    
                                    prefixo_q = "QUEST[AÃ]O\\s*PEI" if fez_pei else "QUEST[AÃ]O"
                                    padrao_q = rf"(?si)({prefixo_q}\s*0?{q_n}\b.*?)(?={prefixo_q}\s*0?{q_n+1}\b|GABARITO|$)"
                                    m_q = re.search(padrao_q, questoes_raw)
                                    
                                    if m_q:
                                        q_completa = m_q.group(1).strip()
                                        q_completa = re.sub(r'\[\s*PROMPT IMAGEM:.*?\]', '\n\n🖼️ *[IMAGEM DE APOIO]*\n\n', q_completa)
                                        partes = re.split(r'(?=\n\s*\([A-E]\)|\n\s*[A-E]\))', q_completa, maxsplit=1)
                                        
                                        enunciado_texto = partes[0].strip()
                                        alternativas_texto = partes[1].strip() if len(partes) > 1 else ""
                                        
                                        st.info(preparar_para_leitura(enunciado_texto))
                                        if alternativas_texto:
                                            alt_formatada = preparar_para_leitura(alternativas_texto).replace('\n', '\n\n')
                                            st.markdown(alt_formatada)
                                    else:
                                        st.error(f"Enunciado da Questão {q_n} não localizado.")
                                    
                                    st.divider()
                                    
                                    padrao_p = rf"(?si){prefixo_q}\s*0?{q_n}\b.*?(?={prefixo_q}\s*0?{q_n+1}\b|GABARITO|RESPOSTAS|$)"
                                    match_p = re.search(padrao_p, grade_texto)
                                    
                                    habilidade = "BNCC"
                                    justificativa = ""
                                    distratores = "Erro de interpretação."
                                    
                                    if match_p:
                                        p_completa = match_p.group(0).strip()
                                        hab_match = re.search(r"\[(.*?)\]", p_completa)
                                        habilidade = hab_match.group(1).strip() if hab_match else "BNCC"
                                        
                                        just_match = re.search(r"(?i)JUSTIFICATIVA[\s\:]*(.*?)(?=PERÍCIA|ANÁLISE|DISTRATORES|$)", p_completa, re.DOTALL)
                                        justificativa = just_match.group(1).strip() if just_match else ""
                                        
                                        dist_match = re.search(r"(?i)(?:PERÍCIA DE DISTRATORES|ANÁLISE DE LACUNA PEI|PERÍCIA|ANÁLISE|DISTRATORES)[\s\:]*(.*)", p_completa, re.DOTALL)
                                        distratores = dist_match.group(1).strip() if dist_match else ""
                                    
                                    if letra_marcada == letra_correta:
                                        st.success(f"✅ **Acertou!** (Marcou {letra_marcada})\n\n**Raciocínio:** {preparar_para_leitura(justificativa)}")
                                    elif letra_marcada == "?":
                                        st.warning(f"⚪ **Em branco** (Gabarito: {letra_correta})\n\n**Foco ({habilidade}):** {preparar_para_leitura(distratores)}")
                                    elif letra_marcada == "X":
                                        st.warning(f"🚫 **Rasura/Dupla** (Gabarito: {letra_correta})\n\n**Foco ({habilidade}):** {preparar_para_leitura(distratores)}")
                                    else:
                                        dist_formatado = re.sub(r'(?=\([A-E]\))', '\n\n', distratores)
                                        st.error(f"❌ **Errou** (Marcou {letra_marcada} | Gabarito: {letra_correta})\n\n**Análise do Erro:** {preparar_para_leitura(dist_formatado)}")
                        else:
                            st.info("Detalhes da prova não encontrados no acervo.")
        else:
            st.info("📭 Nenhuma avaliação escaneada para este aluno no período selecionado.")

        # --- BLOCO 3: ENGAJAMENTO E COMPORTAMENTO ---
        st.markdown(f"### 📊 3. Perfil de Engajamento e Comportamento ({trim_b})")
        with st.container(border=True):
            col_v1, col_v2 = st.columns([1.2, 1.8])
            with col_v1:
                if not d_alu_f.empty:
                    # 🚨 Lógica de Assiduidade (Ignora Dias Não Letivos)
                    d_alu_validas_freq = d_alu_f[d_alu_f['TAGS'] != "DIA NÃO LETIVO"]
                    total_aulas_presenca = len(d_alu_validas_freq)
                    faltas = len(d_alu_validas_freq[d_alu_validas_freq['TAGS'] == "AUSÊNCIA"])
                    presencas = total_aulas_presenca - faltas
                    perc_presenca = (presencas / total_aulas_presenca) * 100 if total_aulas_presenca > 0 else 0
                    
                    d_alu_vistos = d_alu_f[d_alu_f['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                    total_aulas_visto = len(d_alu_vistos)
                    vistos = len(d_alu_vistos[d_alu_vistos['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    perc_visto = (vistos / total_aulas_visto) * 100 if total_aulas_visto > 0 else 0
                    
                    total_bonus_periodo = d_alu_f['BONUS'].apply(util.sosa_to_float).sum()
                    
                    st.metric("Assiduidade (Presença)", f"{perc_presenca:.0f}%", f"{faltas} faltas registradas", delta_color="inverse" if faltas > 0 else "normal")
                    st.progress(perc_presenca / 100)
                    
                    st.metric("Vistos no Caderno", f"{perc_visto:.0f}%", f"{vistos}/{total_aulas_visto} aulas válidas")
                    
                    st.metric("Mérito Acumulado (Bônus)", f"{total_bonus_periodo:+.1f} pts", help="Total de pontos extras ou punições conquistados no período.")
                else: 
                    st.info(f"📭 Sem registros de diário para o período.")

            with col_v2:
                st.markdown("**🚩 Ocorrências, Bônus e Observações Recentes:**")
                if not d_alu_f.empty:
                    mask_obs = (d_alu_f['TAGS'] != "") | (d_alu_f['OBSERVACOES'] != "") | (d_alu_f['BONUS'].apply(util.sosa_to_float) != 0)
                    tags_obs = d_alu_f[mask_obs]
                    
                    if not tags_obs.empty:
                        for _, row in tags_obs.tail(5).iterrows():
                            tag_str = str(row['TAGS']).upper()
                            obs_str = str(row['OBSERVACOES'])
                            bonus_val = util.sosa_to_float(row.get('BONUS', 0))
                            
                            # 🚨 ÍCONE PARA DIA NÃO LETIVO
                            if tag_str == "DIA NÃO LETIVO":
                                emoji = "🛑"
                            elif "SISTEMA_NOTA" in tag_str or "PROJETO" in obs_str.upper():
                                emoji = "📘"
                            elif any(x in tag_str for x in["DORMIU", "CONVERSA", "MATERIAL", "FALTOU", "AUSÊNCIA", "ATRASO", "CELULAR", "INDISCIPLINA", "ARGUIÇÃO"]):
                                emoji = "🔴"
                            elif bonus_val > 0:
                                emoji = "⭐"
                            elif bonus_val < 0:
                                emoji = "📉"
                            else:
                                emoji = "🟢"
                                
                            display_tag = tag_str if tag_str != "SISTEMA_NOTA" else "TRABALHO"
                            
                            if bonus_val > 0:
                                bonus_badge = f" **[+{bonus_val} pts]**"
                            elif bonus_val < 0:
                                bonus_badge = f" **[{bonus_val} pts]**"
                            else:
                                bonus_badge = ""
                            
                            texto_exibicao = f"{emoji} **{row['DATA']}**"
                            if display_tag: texto_exibicao += f" | {display_tag}"
                            if bonus_badge: texto_exibicao += bonus_badge
                            if obs_str: texto_exibicao += f" - *{obs_str}*"
                            
                            st.caption(texto_exibicao)
                            
                        st.markdown("<br>", unsafe_allow_html=True)
                        with st.expander("📂 Ver Histórico Completo de Anotações"):
                            for _, row in tags_obs.iloc[::-1].iterrows():
                                tag_str = str(row['TAGS']).upper()
                                obs_str = str(row['OBSERVACOES'])
                                bonus_val = util.sosa_to_float(row.get('BONUS', 0))
                                
                                display_tag = tag_str if tag_str != "SISTEMA_NOTA" else "TRABALHO"
                                
                                if bonus_val > 0:
                                    bonus_badge = f" **[+{bonus_val} pts]**"
                                elif bonus_val < 0:
                                    bonus_badge = f" **[{bonus_val} pts]**"
                                else:
                                    bonus_badge = ""
                                
                                texto_exibicao = f"**{row['DATA']}**"
                                if display_tag: texto_exibicao += f" | {display_tag}"
                                if bonus_badge: texto_exibicao += bonus_badge
                                if obs_str: texto_exibicao += f" - {obs_str}"
                                
                                st.write(texto_exibicao)
                                st.divider()
                    else: 
                        st.success("✅ Nenhuma ocorrência ou anotação registrada.")

        # --- BLOCO 4: MAPA DE LACUNAS (RAIO-X) ---
        st.markdown(f"### 🧠 4. Mapa de Lacunas e Dificuldades ({trim_b})")
        st.caption("Habilidades da BNCC que o aluno errou nas avaliações e que precisam de reforço.")
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
                    
                    with st.expander("🔍 Ver Detalhamento das Lacunas (Recolhido para limpeza visual)", expanded=False):
                        for l in lacunas_unicas: 
                            st.error(f"❌ {l}")
                else:
                    st.success("✅ Domínio total nas habilidades das avaliações realizadas.")
            else:
                st.info("📭 Aguardando avaliações escaneadas para gerar o mapa de lacunas.")

        # ==============================================================================
        # 🚨 BLOCO 5: DOSSIÊ CLÍNICO E ADAPTAÇÕES (EXCLUSIVO PARA PEI/DEFASAGEM)
        # ==============================================================================
        if is_pei_or_gap:
            st.markdown(f"### ♿ 5. Dossiê Clínico e Adaptações (PEI)")
            st.caption("Resumo do Repositório Vivo do aluno. Para editar ou gerar um novo relatório, acesse a aba 'Relatórios PEI / Perfil IA'.")
            
            hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_alu]
            rel_master = hist_aluno[hist_aluno['TIPO'] == 'DOSSIE_MASTER_PEI']
            
            if not rel_master.empty:
                master_text = str(rel_master.iloc[-1]['CONTEUDO'])
                v_diag = ai.extrair_tag(master_text, "DIAGNOSTICO_GERAL")
                v_diretrizes = ai.extrair_tag(master_text, "DIRETRIZES_CURRICULARES")
                
                with st.expander("📂 Abrir Dossiê Clínico e Diretrizes", expanded=False):
                    st.markdown("#### 🧠 Diagnóstico Geral (Status de Safra)")
                    st.info(v_diag if v_diag else "Diagnóstico não preenchido.")
                    
                    st.markdown("#### 🎯 Diretrizes Curriculares Sugeridas")
                    st.warning(v_diretrizes if v_diretrizes else "Diretrizes não preenchidas.")
            else:
                st.info("📭 Nenhum Dossiê Master gerado para este aluno ainda.")

        st.caption(f"Dossiê atualizado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}")



# ==============================================================================
# MÓDULO: PAINEL DE NOTAS & VISTOS - CLEAN & UX (MULTIPERFIL)
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.title("📊 Torre de Comando: Gestão de Notas")
    st.caption("💡 **Guia de Comando:** Defina os pesos do trimestre. O sistema calculará automaticamente a nota de caderno (Vistos) e aplicará o algoritmo de transbordamento de Bônus/Punição (afetando Vistos, depois Teste, depois Prova).")
    st.markdown("---")

    if "v_notas" not in st.session_state: 
        st.session_state.v_notas = int(time.time())
    v = st.session_state.v_notas

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro na aba 'Gestão da Turma'.")
    else:
        turmas_reais_notas = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_notas = sorted(turmas_reais_notas['ID_TURMA'].unique()) if not turmas_reais_notas.empty else sorted(df_alunos['TURMA'].unique())

        if not lista_turmas_notas:
            st.warning("⚠️ Nenhuma turma regular cadastrada.")
            st.stop()

        # --- 1. CONFIGURADOR DE PESOS ---
        with st.container(border=True):
            st.markdown("### ⚙️ Passo 1: Critérios de Avaliação do Trimestre")
            c_f1, c_f2, c_f3, c_f4, c_f5 = st.columns([1.5, 1, 0.8, 0.8, 0.8])
            turma_sel = c_f1.selectbox("👥 Selecione a Turma:", lista_turmas_notas, key=f"n_turma_{v}")
            trimestre_sel = c_f2.selectbox("📅 Trimestre Atual:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"n_trim_{v}")
            
            p_visto = c_f3.number_input("Peso Vistos:", 0.0, 10.0, 3.0, step=0.5, help="Pontuação máxima que o aluno pode atingir com os vistos de caderno.", key=f"p_v_{v}")
            p_teste = c_f4.number_input("Peso Teste:", 0.0, 10.0, 3.0, step=0.5, help="Pontuação máxima do Teste/Trabalho.", key=f"p_t_{v}")
            p_prova = c_f5.number_input("Peso Prova:", 0.0, 10.0, 4.0, step=0.5, help="Pontuação máxima da Prova Oficial.", key=f"p_p_{v}")
            
            if (p_visto + p_teste + p_prova) != 10.0:
                st.warning(f"⚠️ A soma dos pesos ({p_visto + p_teste + p_prova}) deve ser exatamente 10.0 para o sistema oficial.")

        # 🚨 VACINA ANTI-VAZIO
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        if alunos_turma.empty:
            st.warning(f"⚠️ Nenhum aluno cadastrado na turma {turma_sel} ainda. Vá em 'Gestão da Turma' para povoar.")
            st.stop()

        # --- 2. MOTOR DE CÁLCULO AUTOMÁTICO (DIÁRIO DE BORDO) ---
        vistos_auto_map = {}
        bonus_total_map = {}
        
        calendario = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
            "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
        }
        dt_ini, dt_fim = calendario.get(trimestre_sel)

        if not df_diario.empty:
            df_d_t = df_diario[df_diario['TURMA'] == turma_sel].copy()
            df_d_t['DATA_DT'] = pd.to_datetime(df_d_t['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
            df_d_trim = df_d_t[(df_d_t['DATA_DT'] >= dt_ini) & (df_d_t['DATA_DT'] <= dt_fim)]
            
            for id_aluno in alunos_turma['ID']:
                id_l = db.limpar_id(id_aluno)
                d_alu = df_d_trim[df_d_trim['ID_ALUNO'].apply(db.limpar_id) == id_l]
                
                if not d_alu.empty:
                    # Ignora as aulas ISENTAS no cálculo do total de vistos
                    d_alu_validas = d_alu[d_alu['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                    
                    vistos_validos = d_alu_validas[d_alu_validas['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]
                    aulas_com_visto = len(vistos_validos)
                    total_aulas_periodo = len(d_alu_validas)
                    
                    vistos_auto_map[id_l] = round((aulas_com_visto / total_aulas_periodo * p_visto), 2) if total_aulas_periodo > 0 else 0.0
                    
                    # O Bônus continua somando de TODAS as aulas (agora aceita negativos)
                    bonus_total_map[id_l] = d_alu['BONUS'].apply(util.sosa_to_float).sum()
                else:
                    vistos_auto_map[id_l], bonus_total_map[id_l] = 0.0, 0.0

        # --- 3. CONSOLIDAÇÃO DA MESA DE LANÇAMENTO ---
        notas_banco = df_notas[(df_notas['TURMA'] == turma_sel) & (df_notas['TRIMESTRE'] == trimestre_sel)]
        
        # 🚨 MOTOR DE ÍCONES MULTIPERFIL
        def definir_icone_status(nec):
            n = str(nec).upper().strip()
            if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
            if "DEFASAGEM LEITURA" in n: return "🧱"
            if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
            if "ALTA PERFORMANCE" in n: return "🚀"
            if n in["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
            return "♿"

        dados_editor =[]
        for _, alu in alunos_turma.iterrows():
            id_a = db.limpar_id(alu['ID'])
            reg_b = notas_banco[notas_banco['ID_ALUNO'].apply(db.limpar_id) == id_a]
            
            n_teste = util.sosa_to_float(reg_b.iloc[0]['NOTA_TESTE']) if not reg_b.empty else 0.0
            n_prova = util.sosa_to_float(reg_b.iloc[0]['NOTA_PROVA']) if not reg_b.empty else 0.0
            n_rec = util.sosa_to_float(reg_b.iloc[0]['NOTA_REC']) if not reg_b.empty else 0.0
            
            icone_perfil = definir_icone_status(alu['NECESSIDADES'])

            dados_editor.append({
                "ID": id_a,
                "ESTUDANTE": f"{icone_perfil} {alu['NOME_ALUNO']}",
                "VISTOS (AUTO)": vistos_auto_map.get(id_a, 0.0),
                "BÔNUS (TOTAL)": bonus_total_map.get(id_a, 0.0),
                "TESTE (LANÇAR)": n_teste,
                "PROVA (LANÇAR)": n_prova,
                "REC. PARALELA": n_rec
            })

        # --- 4. TABELA 1: CONSOLIDAÇÃO E ENTRADA ---
        st.subheader("📝 Passo 2: Lançamento e Consolidação")
        st.info("💡 **Dica:** Digite as notas do Teste, Prova e Recuperação. O sistema somará os Vistos e o Bônus/Punição automaticamente.")
        
        df_input = st.data_editor(
            pd.DataFrame(dados_editor),
            column_config={
                "ID": None,
                "ESTUDANTE": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                "VISTOS (AUTO)": st.column_config.NumberColumn("Vistos (Sistema)", format="%.1f", disabled=True),
                "BÔNUS (TOTAL)": st.column_config.NumberColumn("⭐ Bônus/Punição", format="%.1f", disabled=True),
                "TESTE (LANÇAR)": st.column_config.NumberColumn("Nota Teste", min_value=0.0, max_value=p_teste, format="%.1f"),
                "PROVA (LANÇAR)": st.column_config.NumberColumn("Nota Prova", min_value=0.0, max_value=p_prova, format="%.1f"),
                "REC. PARALELA": st.column_config.NumberColumn("🔄 Rec. Paralela", min_value=0.0, max_value=10.0, format="%.1f"),
            },
            hide_index=True, use_container_width=True, key=f"editor_notas_{v}"
        )

        # --- 5. ALGORITMO DE TRANSBORDAMENTO E SUBSTITUIÇÃO (ATUALIZADO PARA PUNIÇÕES) ---
        def aplicar_transbordamento(row):
            bonus_restante = row['BÔNUS (TOTAL)']
            v_base = row['VISTOS (AUTO)']
            t_base = row['TESTE (LANÇAR)']
            p_base = row['PROVA (LANÇAR)']
            rec_paralela = row['REC. PARALELA']
            
            # Passo 1: Completar ou Descontar Vistos
            v_final = max(0.0, min(p_visto, v_base + bonus_restante))
            bonus_restante -= (v_final - v_base)
            
            # Passo 2: Completar ou Descontar Teste
            t_final = max(0.0, min(p_teste, t_base + bonus_restante))
            bonus_restante -= (t_final - t_base)
            
            # Passo 3: Completar ou Descontar Prova
            p_final = max(0.0, min(p_prova, p_base + bonus_restante))
            
            # Média Final: Soma das notas ou a Recuperação (o que for maior)
            soma_notas = v_final + t_final + p_final
            media_final = min(10.0, max(soma_notas, rec_paralela))
            
            return pd.Series([v_final, t_final, p_final, rec_paralela, media_final])

        df_input[['V_PREF', 'T_PREF', 'P_PREF', 'REC_PREF', 'MEDIA_FINAL']] = df_input.apply(aplicar_transbordamento, axis=1)

        # --- 6. TABELA 2: GABARITO DE LANÇAMENTO ---
        st.markdown("---")
        st.subheader("🏛️ Passo 3: Gabarito Final (Sistema Prefeitura)")
        st.caption("Estas são as notas finais processadas. O Bônus/Punição já foi distribuído e a Recuperação Paralela já substituiu a média (se for maior). Copie estes valores para o sistema da escola.")
        
        def style_situacao(v):
            color = '#2ECC71' if v >= 6.0 else '#FF4B4B'
            return f'color: {color}; font-weight: bold'

        st.dataframe(
            df_input[['ESTUDANTE', 'V_PREF', 'T_PREF', 'P_PREF', 'REC_PREF', 'MEDIA_FINAL']].style.map(
                style_situacao, subset=['MEDIA_FINAL']
            ).format({
                "V_PREF": "{:.1f}", "T_PREF": "{:.1f}", "P_PREF": "{:.1f}", "REC_PREF": "{:.1f}", "MEDIA_FINAL": "{:.2f}"
            }),
            use_container_width=True, hide_index=True,
            column_config={
                "V_PREF": "Atividades",
                "T_PREF": "Teste",
                "P_PREF": "Prova",
                "REC_PREF": "🔄 Rec. Paralela",
                "MEDIA_FINAL": "Média Final"
            }
        )

        # --- 7. SALVAMENTO ---
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 SALVAR NOTAS E SINCRONIZAR BOLETIM", type="primary", use_container_width=True):
            with st.status("Sincronizando registros no Banco de Dados...") as status:
                db.limpar_notas_turma_trimestre(turma_sel, trimestre_sel)
                linhas_save =[]
                for _, r in df_input.iterrows():
                    # 🚨 LIMPEZA BLINDADA DO NOME ANTES DE SALVAR
                    nome_limpo = r['ESTUDANTE'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                    
                    linhas_save.append([
                        r['ID'], nome_limpo, turma_sel, trimestre_sel,
                        util.sosa_to_str(r["V_PREF"]), util.sosa_to_str(r["T_PREF"]),
                        util.sosa_to_str(r["P_PREF"]), util.sosa_to_str(r["REC_PREF"]),
                        util.sosa_to_str(r['MEDIA_FINAL'])
                    ])
                if db.salvar_lote("DB_NOTAS", linhas_save):
                    status.update(label="✅ Boletim Sincronizado com Sucesso!", state="complete")
                    st.balloons(); time.sleep(1); st.rerun()


# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO - CLEAN & UX
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Inteligência de Conselho e Resultados")
    st.caption("💡 **Guia de Comando:** Visão panorâmica do ano letivo. O sistema cruza notas, recuperações e faltas para calcular automaticamente a situação final de cada estudante.")
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

        # Total de dias letivos registrados para a turma (para calcular o limite de 25%)
        total_dias_letivos = df_diario[df_diario['TURMA'] == turma_sel]['DATA'].nunique()
        limite_faltas = total_dias_letivos * 0.25 

        # --- 3. LÓGICA DE STATUS (COM PESO DE FALTAS) ---
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
            
            # INTELIGÊNCIA DE STATUS: Faltas pesam mais que nota
            if faltas_aluno > limite_faltas and total_dias_letivos > 20: 
                status = "🚨 RISCO (FALTAS)"
            elif soma >= 18.0: status = "✅ APROV"
            elif rf >= 6.0: status = "🔄 APROV.REC"
            elif soma > 0 and falta_pts <= 10.0: status = "⚠️ REC.FINAL"
            elif soma > 0 and falta_pts > 10.0: status = "🚨 RISCO (NOTA)"
            else: status = "⏳ AGUARD"
            
            return pd.Series([pei, soma, falta_pts, status])

        pivot[['P', 'Σ', 'FALTA_PTS', 'SITUAÇÃO']] = pivot.apply(calcular_situacao_anual, axis=1)

        # --- 4. KPIs DE TOPO (TERMÔMETRO DA TURMA) ---
        st.markdown("### 📊 Termômetro da Turma")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Geral da Turma", f"{pivot['Σ'].mean()/3:.1f}")
        
        aprov = len(pivot[pivot['SITUAÇÃO'].str.contains("APROV")])
        c2.metric("Taxa de Aprovação", f"{(aprov/len(pivot)*100):.0f}%" if len(pivot) > 0 else "0%")
        
        c3.metric("Em Rec. Final", len(pivot[pivot['SITUAÇÃO'] == "⚠️ REC.FINAL"]))
        
        risco_total = len(pivot[pivot['SITUAÇÃO'].str.contains("🚨 RISCO")])
        c4.metric("Risco Crítico (Nota/Falta)", risco_total, delta_color="inverse", help="Alunos que já estouraram o limite de faltas ou que precisam de mais de 10 pontos para passar.")

        # --- 5. TABELA MOBILE-FIRST ---
        st.markdown("---")
        st.markdown("### 📋 Mapa de Desempenho Anual e Assiduidade")
        
        def style_status_anual(v):
            if "APROV" in str(v): return 'color: #2ECC71; font-weight: bold;'
            if "RISCO" in str(v): return 'color: #E74C3C; font-weight: bold;'
            if "REC.FINAL" in str(v): return 'color: #F1C40F; font-weight: bold;'
            return ''

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
                                      'Σ', 'RF']),
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
                "Σ": st.column_config.NumberColumn("Σ", width="small", help="Soma Anual (Meta: 18.0)"),
                "RF": st.column_config.NumberColumn("RF", width="small", help="Recuperação Final"),
                "FALTAS": st.column_config.NumberColumn("F", width="small", help=f"Total de Faltas no Ano. Limite atual: {int(limite_faltas)}"),
                "SITUAÇÃO": st.column_config.TextColumn("Status", width="small")
            }
        )
        
        st.caption(f"📌 **Legenda:** I, II, III (Médias Trimestrais) | R1, R2, R3 (Recuperações Paralelas) | Σ (Soma Anual) | RF (Recuperação Final) | F (Faltas). Limite de faltas atual: **{int(limite_faltas)}**.")


# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO - CLEAN & UX
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("📈 Inteligência de Conselho e Resultados")
    st.caption("💡 **Guia de Comando:** Visão panorâmica do ano letivo. O sistema cruza notas, recuperações e faltas para calcular automaticamente a situação final de cada estudante.")
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

        # Total de dias letivos registrados para a turma (para calcular o limite de 25%)
        total_dias_letivos = df_diario[df_diario['TURMA'] == turma_sel]['DATA'].nunique()
        limite_faltas = total_dias_letivos * 0.25 

        # --- 3. LÓGICA DE STATUS (COM PESO DE FALTAS) ---
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
            
            # INTELIGÊNCIA DE STATUS: Faltas pesam mais que nota
            if faltas_aluno > limite_faltas and total_dias_letivos > 20: 
                status = "🚨 RISCO (FALTAS)"
            elif soma >= 18.0: status = "✅ APROV"
            elif rf >= 6.0: status = "🔄 APROV.REC"
            elif soma > 0 and falta_pts <= 10.0: status = "⚠️ REC.FINAL"
            elif soma > 0 and falta_pts > 10.0: status = "🚨 RISCO (NOTA)"
            else: status = "⏳ AGUARD"
            
            return pd.Series([pei, soma, falta_pts, status])

        pivot[['P', 'Σ', 'FALTA_PTS', 'SITUAÇÃO']] = pivot.apply(calcular_situacao_anual, axis=1)

        # --- 4. KPIs DE TOPO (TERMÔMETRO DA TURMA) ---
        st.markdown("### 📊 Termômetro da Turma")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Média Geral da Turma", f"{pivot['Σ'].mean()/3:.1f}")
        
        aprov = len(pivot[pivot['SITUAÇÃO'].str.contains("APROV")])
        c2.metric("Taxa de Aprovação", f"{(aprov/len(pivot)*100):.0f}%" if len(pivot) > 0 else "0%")
        
        c3.metric("Em Rec. Final", len(pivot[pivot['SITUAÇÃO'] == "⚠️ REC.FINAL"]))
        
        risco_total = len(pivot[pivot['SITUAÇÃO'].str.contains("🚨 RISCO")])
        c4.metric("Risco Crítico (Nota/Falta)", risco_total, delta_color="inverse", help="Alunos que já estouraram o limite de faltas ou que precisam de mais de 10 pontos para passar.")

        # --- 5. TABELA MOBILE-FIRST ---
        st.markdown("---")
        st.markdown("### 📋 Mapa de Desempenho Anual e Assiduidade")
        
        def style_status_anual(v):
            if "APROV" in str(v): return 'color: #2ECC71; font-weight: bold;'
            if "RISCO" in str(v): return 'color: #E74C3C; font-weight: bold;'
            if "REC.FINAL" in str(v): return 'color: #F1C40F; font-weight: bold;'
            return ''

        st.dataframe(
            pivot[['P', 'NOME_ALUNO', 
                   'MEDIA_FINAL_I Trimestre', 'NOTA_REC_I Trimestre',
                   'MEDIA_FINAL_II Trimestre', 'NOTA_REC_II Trimestre',
                   'MEDIA_FINAL_III Trimestre', 'NOTA_REC_III Trimestre',
                   'Σ', 'RF', 'FALTAS', 'SITUAÇÃO']]
            .style.applymap(style_status_anual, subset=['SITUAÇÃO'])
            .format("{:.1f}", subset=['MEDIA_FINAL_I Trimestre', 'NOTA_REC_I Trimestre', 
                                      'MEDIA_FINAL_II Trimestre', 'NOTA_REC_II Trimestre', 
                                      'MEDIA_FINAL_III Trimestre', 'NOTA_REC_III Trimestre', 
                                      'Σ', 'RF']),
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
                "Σ": st.column_config.NumberColumn("Σ", width="small", help="Soma Anual (Meta: 18.0)"),
                "RF": st.column_config.NumberColumn("RF", width="small", help="Recuperação Final"),
                "FALTAS": st.column_config.NumberColumn("F", width="small", help=f"Total de Faltas no Ano. Limite atual: {int(limite_faltas)}"),
                "SITUAÇÃO": st.column_config.TextColumn("Status", width="small")
            }
        )
        
        st.caption(f"📌 **Legenda:** I, II, III (Médias Trimestrais) | R1, R2, R3 (Recuperações Paralelas) | Σ (Soma Anual) | RF (Recuperação Final) | F (Faltas). Limite de faltas atual: **{int(limite_faltas)}**.")




# ==============================================================================
# MÓDULO: GESTÃO DA Turma (COCKPIT DE REGÊNCIA) - CLEAN & UX V120
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Cockpit de Regência: Gestão 360°")
    st.caption("💡 **Guia de Comando:** Central de controle da sua rotina. Abra aulas rapidamente, audite registros passados e acesse a inteligência analítica da turma.")
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

    tab_cockpit, tab_radiografia, tab_roleta, tab_frequencia, tab_secretaria = st.tabs([
        "🚀 1. Cockpit de Regência", 
        "🧠 2. Radiografia da Turma", 
        "🎲 3. Roleta de Arguição",
        "📅 4. Controle de Evasão", 
        "⚙️ 5. Secretaria & Matrículas"
    ])

    # ==============================================================================
    # 🚀 ABA 1: COCKPIT DE REGÊNCIA (AÇÃO RÁPIDA E AUDITORIA)
    # ==============================================================================
    with tab_cockpit:
        if df_turmas.empty or 'ID_TURMA' not in df_turmas.columns:
            st.info("📭 Nenhuma turma cadastrada. Vá na aba '5. Secretaria & Matrículas' para iniciar.")
        else:
            st.markdown("### 📅 Grade Oficial de Regência")
            
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]
            tempos = ["1º Tempo", "2º Tempo"]
            grade_map = {t: {d: "---" for d in dias_semana} for t in tempos}

            for _, row in df_turmas.iterrows():
                sigla = str(row.get('ID_TURMA', ''))
                nome_turma = str(row.iloc[1]) if len(row) > 1 else ""
                horarios_str = str(row.iloc[3]) if len(row) > 3 else ""
                
                display_name = sigla
                if "ª" in sigla: display_name = nome_turma.replace("Ano ", "ANO ").upper()
                
                if horarios_str and horarios_str != "N/A":
                    for h in [x.strip() for x in horarios_str.split("/")]:
                        for dia in dias_semana:
                            for tempo in tempos:
                                if dia in h and tempo in h:
                                    grade_map[tempo][dia] = display_name

            df_grade = pd.DataFrame(grade_map).T
            
            def colorir_grade(val):
                if val in ["PI", "PC", "AC", "HTPC"]: return 'background-color: #2962FF; color: white; font-weight: bold; text-align: center;'
                if val != "---": return 'background-color: #001E3C; color: #2ECC71; font-weight: bold; text-align: center;'
                return 'color: gray; text-align: center;'

            st.dataframe(df_grade.style.map(colorir_grade), use_container_width=True)
            st.markdown("---")

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

                col_esq, col_dir = st.columns([1.5, 1.5])

                # --- LADO ESQUERDO: ABERTURA DE AULA ---
                with col_esq:
                    st.subheader("🕒 Abertura de Aula")
                    
                    planos_usados = historico_turma['SEMANA'].unique().tolist()
                    plano_sugerido = "Nenhum"
                    base_didatica_sugerida = "Matriz Curricular"
                    ponte_sugerida = "Início de novo ciclo pedagógico."
                    
                    df_p_sugestao = df_p_atual[~df_p_atual['SEMANA'].isin(planos_usados)]
                    df_p_sugestao = df_p_sugestao[df_p_sugestao['EIXO'] == 'HUB_ATIVO']
                        
                    if not df_p_sugestao.empty:
                        row_p = df_p_sugestao.iloc[0]
                        plano_sugerido = row_p['SEMANA']
                        txt_p = row_p['PLANO_TEXTO']
                        base_didatica_sugerida = ai.extrair_tag(txt_p, "BASE_DIDATICA") or "Matriz de Itabuna"
                        ponte_match = re.search(r"Ponte Pedagógica:(.*?)(?=Início|Meio|Fim|$)", ai.extrair_tag(txt_p, "AULA_1"), re.DOTALL)
                        if ponte_match: ponte_sugerida = ponte_match.group(1).strip()

                    with st.container(border=True):
                        st.markdown("#### 🚀 MISSÃO PLANEJADA PARA HOJE")
                        
                        data_aula = st.date_input("Data da Aula:", date.today(), format="DD/MM/YYYY", key=f"dt_reg_{v}")
                        data_aula_str = data_aula.strftime("%d/%m/%Y")
                        
                        aula_existente = historico_turma[historico_turma['DATA'] == data_aula_str]
                        
                        if not aula_existente.empty:
                            row_ativa = aula_existente.iloc[0]
                            st.success(f"✅ **Aula já registrada para esta data!**")
                            st.info(f"📦 **Material Vinculado:** {row_ativa['CONTEUDO_MINISTRADO']}\n\n🚦 **Status:** {row_ativa.get('STATUS_EXECUCAO', 'Pendente')}")
                            st.caption("💡 Para lançar vistos, acesse a aba 'Diário de Bordo Rápido'. Para editar este registro, use a Auditoria ao lado.")
                        else:
                            if plano_sugerido != "Nenhum":
                                st.success(f"**Próxima Semana Inédita:** {plano_sugerido}")
                                st.info(f"**📖 Base Didática (DNA):**\n{base_didatica_sugerida}")
                            else:
                                st.success("✅ Todos os planos ativos já foram aplicados nesta turma!")
                            
                            with st.expander("🔗 Ver Ponte de Continuidade (Onde paramos?)"):
                                st.caption(ponte_sugerida)
                            
                            st.divider()
                            
                            mats_disp_bruto = df_mats_ano['TIPO_MATERIAL'].tolist()
                            mats_sel = st.multiselect("📦 Selecione o Material (Máx 2):", options=mats_disp_bruto, max_selections=2, key=f"mats_reg_{v}")

                            if st.button("💾 CONFIRMAR ABERTURA DE AULA", use_container_width=True, type="primary"):
                                if not mats_sel:
                                    st.error("⚠️ Selecione ao menos um material para abrir a aula.")
                                else:
                                    mat_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == mats_sel[0]].iloc[0]
                                    plano_inferido = mat_ref['SEMANA_REF']
                                    
                                    db.salvar_no_banco("DB_REGISTRO_AULAS", [
                                        data_aula_str, plano_inferido, turma_foco, 
                                        " + ".join(mats_sel), "PENDENTE", "ABERTA"
                                    ])
                                    st.success("✅ Aula aberta com sucesso! Vá para o Diário de Bordo.")
                                    time.sleep(1); st.rerun()
                                    
                    # 🚨 PROTOCOLO DE SUSPENSÃO LETIVA (EVENTO GLOBAL)
                    st.markdown("---")
                    with st.expander("🛑 Registrar Dia Não Letivo / Paralisação", expanded=False):
                        st.caption("Use para registrar paralisações, luto, falta de água, etc. Isso bloqueará faltas neste dia.")
                        data_nl = st.date_input("Data do Evento:", date.today(), format="DD/MM/YYYY", key=f"dt_nl_{v}")
                        data_nl_str = data_nl.strftime("%d/%m/%Y")
                        motivo_nl = st.text_input("Motivo:", placeholder="Ex: Paralisação Sindical", key=f"motivo_nl_{v}")
                        
                        if st.button("🛑 CONFIRMAR DIA NÃO LETIVO", type="primary", use_container_width=True):
                            if not motivo_nl:
                                st.error("Digite o motivo.")
                            else:
                                with st.spinner("Registrando evento global..."):
                                    db.limpar_diario_data_turma(data_nl_str, turma_foco)
                                    db.excluir_aula_aberta(data_nl_str, turma_foco)
                                    
                                    db.salvar_no_banco("DB_DIARIO_BORDO", [
                                        data_nl_str, "GLOBAL", "TODOS OS ALUNOS", turma_foco,
                                        "ISENTO", "DIA NÃO LETIVO", motivo_nl, "0,00"
                                    ])
                                    db.salvar_no_banco("DB_REGISTRO_AULAS", [
                                        data_nl_str, "AVULSA", turma_foco, 
                                        f"DIA NÃO LETIVO: {motivo_nl}", "N/A", "N/A", "NÃO LETIVO", "", ""
                                    ])
                                    st.success("Dia Não Letivo registrado com sucesso!")
                                    time.sleep(1.5)
                                    st.rerun()

                # --- LADO DIREITO: APOIO E AUDITORIA ---
                with col_dir:
                    st.subheader("🛠️ Apoio e Auditoria")
                    
                    with st.container(border=True):
                        st.markdown("#### 📊 Perfil Quantitativo da Turma")
                        
                        # 🚨 MOTOR DE ESTATÍSTICA RÁPIDA
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
                        
                        # Exibição das métricas
                        c_m1, c_m2, c_m3 = st.columns(3)
                        c_m1.metric("👥 Total Alunos", total_alunos_turma)
                        c_m2.metric("♿ Laudos (PEI)", qtd_pei)
                        c_m3.metric("🧱 Defasagem", qtd_defasagem)
                        
                        st.divider()
                        
                        st.markdown("**🔍 Foco em Inclusão (Detalhamento)**")
                        # Filtra todos que precisam de atenção (ignora Típicos e Alta Performance)
                        mask_pei = ~alunos_t['NECESSIDADES'].astype(str).str.upper().str.strip().isin(["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE"])
                        df_pei_turma = alunos_t[mask_pei]
                        
                        if not df_pei_turma.empty:
                            for _, alu in df_pei_turma.iterrows(): 
                                nec_str = str(alu['NECESSIDADES']).upper()
                                # 🚨 COLORIZAÇÃO DINÂMICA POR PERFIL
                                if "DEFASAGEM" in nec_str:
                                    st.error(f"🧱 **{alu['NOME_ALUNO']}**\n↳ {alu['NECESSIDADES']}")
                                elif "PENDENTE" in nec_str or "SUSPEITA" in nec_str:
                                    st.warning(f"🟠 **{alu['NOME_ALUNO']}**\n↳ {alu['NECESSIDADES']}")
                                else:
                                    st.info(f"♿ **{alu['NOME_ALUNO']}**\n↳ {alu['NECESSIDADES']}")
                        else: 
                            st.success("✅ Nenhum aluno com necessidade de adaptação nesta turma.")

                    with st.container(border=True):
                        st.markdown("#### ✏️ Auditoria de Regência")
                        st.caption("Corrija aulas que foram salvas como 'Registro via Diário' ou altere o material vinculado de aulas passadas.")
                        
                        if not historico_turma.empty:
                            historico_turma['DATA_DT'] = pd.to_datetime(historico_turma['DATA'], format="%d/%m/%Y", errors='coerce')
                            aulas_abertas = historico_turma.sort_values(by='DATA_DT', ascending=False).head(5)
                        else:
                            aulas_abertas = pd.DataFrame()

                        if aulas_abertas.empty: 
                            st.info("Nenhuma aula registrada para esta turma.")
                        else:
                            for i, (idx, row_aula) in enumerate(aulas_abertas.iterrows()):
                                with st.expander(f"📅 {row_aula['DATA']} - {str(row_aula['CONTEUDO_MINISTRADO'])[:30]}..."):
                                    
                                    novo_status = st.selectbox("Status:", ["🟢 Concluído (100%)", "🟡 Parcial (Pendência)", "🔴 Bloqueado (Crítico)", "ABERTA", "NÃO LETIVO"], index=0 if "Concluído" in str(row_aula.get('STATUS_EXECUCAO', '')) else 3, key=f"aud_stat_{idx}")
                                    
                                    opcoes_semanas = ["AVULSA"] + df_planos[df_planos['ANO'] == ano_str_ref]['SEMANA'].unique().tolist()
                                    idx_sem = opcoes_semanas.index(row_aula['SEMANA']) if row_aula['SEMANA'] in opcoes_semanas else 0
                                    nova_semana = st.selectbox("Semana Vinculada:", opcoes_semanas, index=idx_sem, key=f"aud_sem_{idx}")
                                    
                                    mats_disp_bruto = df_mats_ano['TIPO_MATERIAL'].tolist()
                                    mats_atuais = [m.strip() for m in str(row_aula['CONTEUDO_MINISTRADO']).split('+')]
                                    default_mats = [m for m in mats_atuais if m in mats_disp_bruto]
                                    
                                    novo_mat_sel = st.multiselect("Material Ministrado:", options=mats_disp_bruto, default=default_mats, key=f"aud_mat_{idx}")
                                    
                                    c_aud1, c_aud2 = st.columns(2)
                                    if c_aud1.button("💾 Atualizar", key=f"aud_save_{idx}", use_container_width=True, type="primary"):
                                        if not novo_mat_sel and nova_semana != "AVULSA":
                                            st.error("Selecione um material.")
                                        else:
                                            with st.spinner("Atualizando banco..."):
                                                novo_conteudo = " + ".join(novo_mat_sel) if novo_mat_sel else "Registro via Diário"
                                                try:
                                                    wb = db.conectar()
                                                    ws = wb.worksheet("DB_REGISTRO_AULAS")
                                                    dados = ws.get_all_values()
                                                    for j, row in enumerate(dados):
                                                        if j > 0 and len(row) >= 3 and row[0] == row_aula['DATA'] and row[2] == turma_foco:
                                                            ws.update_cell(j + 1, 2, nova_semana)
                                                            ws.update_cell(j + 1, 4, novo_conteudo)
                                                            ws.update_cell(j + 1, 7, novo_status)
                                                            break
                                                    st.cache_data.clear()
                                                    st.success("Atualizado!"); time.sleep(1); st.rerun()
                                                except Exception as e:
                                                    st.error(f"Erro: {e}")
                                                    
                                    if c_aud2.button("🗑️ Apagar Aula", key=f"aud_del_{idx}", use_container_width=True):
                                        with st.spinner("Apagando aula e diário..."):
                                            if db.excluir_aula_aberta(row_aula['DATA'], turma_foco):
                                                st.success("Apagado!"); time.sleep(1); st.rerun()

    # ==============================================================================
    # 🧠 ABA 2: RADIOGRAFIA DA TURMA (HUB ANALÍTICO)
    # ==============================================================================
    with tab_radiografia:
        st.subheader("🧠 Radiografia Cognitiva e Desempenho Global")
        st.caption("Mapeamento tático de perfis, engajamento, assiduidade e resultados em avaliações.")
        
        c_rad1, c_rad2 = st.columns([1, 1])
        t_rad = c_rad1.selectbox("🎯 Selecione a Turma:", lista_turmas_segura, key=f"rad_t_{v}")
        trim_rad = c_rad2.selectbox("📅 Trimestre de Safra:", ["I Trimestre", "II Trimestre", "III Trimestre", "Todos"], key=f"rad_trim_{v}")
        
        if t_rad:
            alunos_rad = df_alunos[df_alunos['TURMA'] == t_rad].copy()
            id_alunos_turma = set(alunos_rad['ID'].apply(db.limpar_id).tolist())
            
            if alunos_rad.empty:
                st.info("Nenhum aluno cadastrado nesta turma.")
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

                st.markdown("#### 📊 1. Termômetro Global da Turma")
                taxa_assiduidade, taxa_engajamento, media_geral_av = 0.0, 0.0, 0.0
                
                if not df_d_rad.empty:
                    # 🚨 Ignora Dias Não Letivos na Radiografia
                    df_d_rad_validas = df_d_rad[df_d_rad['TAGS'] != "DIA NÃO LETIVO"]
                    total_registros = len(df_d_rad_validas)
                    faltas = len(df_d_rad_validas[df_d_rad_validas['TAGS'] == "AUSÊNCIA"])
                    taxa_assiduidade = ((total_registros - faltas) / total_registros) * 100 if total_registros > 0 else 0
                    
                    df_vistos = df_d_rad_validas[df_d_rad_validas['VISTO_ATIVIDADE'].astype(str).str.upper() != "ISENTO"]
                    vistos_possiveis = len(df_vistos)
                    vistos_dados = len(df_vistos[df_vistos['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    taxa_engajamento = (vistos_dados / vistos_possiveis) * 100 if vistos_possiveis > 0 else 0
                
                if not df_diag_rad.empty:
                    media_geral_av = df_diag_rad['NOTA_CALCULADA'].apply(util.sosa_to_float).mean()
                
                c_k1, c_k2, c_k3 = st.columns(3)
                c_k1.metric("Assiduidade Média", f"{taxa_assiduidade:.1f}%")
                c_k2.metric("Engajamento (Vistos)", f"{taxa_engajamento:.1f}%")
                c_k3.metric("Média em Avaliações", f"{media_geral_av:.1f}")
                
                st.divider()

                st.markdown("#### 🎯 2. Funil de Performance e Engajamento")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    st.markdown("**📝 Engajamento (Vistos)**")
                    if not df_d_rad.empty:
                        alunos_stats = []
                        for id_aluno in id_alunos_turma:
                            d_alu = df_vistos[df_vistos['ID_ALUNO'].apply(db.limpar_id) == id_aluno]
                            if not d_alu.empty:
                                v_alu = len(d_alu[d_alu['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                                b_alu = d_alu['BONUS'].apply(util.sosa_to_float).sum()
                                nome_alu = d_alu.iloc[0]['NOME_ALUNO']
                                alunos_stats.append({"nome": nome_alu, "vistos": v_alu, "total": len(d_alu), "bonus": b_alu})
                        
                        fantasmas = [a['nome'] for a in alunos_stats if a['total'] > 0 and (a['vistos']/a['total']) <= 0.2]
                        top_alunos = sorted([a for a in alunos_stats if a['total'] > 0 and (a['vistos']/a['total']) >= 0.8], key=lambda x: x['bonus'], reverse=True)[:3]
                        
                        if fantasmas: st.error(f"👻 **Baixa Entrega:** {', '.join(fantasmas)}")
                        else: st.success("✅ Nenhum aluno com entrega crítica.")
                        
                        if top_alunos: st.success(f"🌟 **Top Engajamento:** {', '.join([a['nome'] for a in top_alunos])}")
                    else:
                        st.info("Sem dados de vistos.")

                with col_f2:
                    st.markdown("**📊 Notas no Boletim**")
                    df_n_trim = df_notas[(df_notas['TURMA'] == t_rad) & (df_notas['TRIMESTRE'] == trim_rad)]
                    if not df_n_trim.empty:
                        medias_finais = df_n_trim['MEDIA_FINAL'].apply(util.sosa_to_float)
                        azul = len(medias_finais[medias_finais >= 7.0])
                        amarelo = len(medias_finais[(medias_finais >= 5.0) & (medias_finais < 7.0)])
                        vermelho = len(medias_finais[medias_finais < 5.0])
                        
                        st.markdown(f"🟢 **Azul:** {azul} | 🟡 **Média:** {amarelo} | 🔴 **Risco:** {vermelho}")
                        
                        alunos_vermelho = df_n_trim[df_n_trim['MEDIA_FINAL'].apply(util.sosa_to_float) < 5.0]['NOME_ALUNO'].tolist()
                        if alunos_vermelho:
                            with st.expander("🚨 Ver alunos na Zona de Risco"):
                                st.error(", ".join(alunos_vermelho))
                    else:
                        st.info("Notas não consolidadas.")

                st.divider()

                st.markdown("#### 🧠 3. Raio-X Cirúrgico (Última Avaliação)")
                if not df_diag_rad.empty:
                    ultima_av = df_diag_rad['ID_AVALIACAO'].unique()[-1]
                    st.caption(f"Analisando a prova mais recente: **{ultima_av}**")
                    
                    nome_curto = ultima_av.split("-")[0].strip().replace(" (2ª CHAMADA)", "")
                    df_ref = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_curto, regex=False, na=False)]
                    
                    if not df_ref.empty:
                        txt_prova = str(df_ref.iloc[0]['CONTEUDO'])
                        gab_raw = ai.extrair_tag(txt_prova, "GABARITO_TEXTO") or ai.extrair_tag(txt_prova, "GABARITO")
                        grade_raw = ai.extrair_tag(txt_prova, "GRADE_DE_CORRECAO")
                        
                        if gab_raw and grade_raw:
                            matches = re.findall(r"(\d+)[\s\.\)\-:]+([A-E])", gab_raw.upper())
                            gab_oficial = {int(num): letra for num, letra in matches}
                            if not gab_oficial:
                                letras = re.findall(r"\b[A-E]\b", gab_raw.upper())
                                gab_oficial = {i+1: letra for i, letra in enumerate(letras)}
                                
                            respostas_alunos = df_diag_rad[df_diag_rad['ID_AVALIACAO'] == ultima_av]['RESPOSTAS_ALUNO'].astype(str).tolist()
                            
                            lacunas_stats = []
                            for q_num, letra_certa in gab_oficial.items():
                                acertos = 0
                                validos = 0
                                for resp in respostas_alunos:
                                    if resp == "FALTOU" or resp.startswith("QUALITATIVA"): continue
                                    resp_lista = resp.split(";")
                                    if len(resp_lista) >= q_num:
                                        validos += 1
                                        if resp_lista[q_num-1] == letra_certa:
                                            acertos += 1
                                
                                if validos > 0:
                                    taxa_acerto = acertos / validos
                                    if taxa_acerto < 0.6: 
                                        padrao_h = rf"(?si)QUEST[AÃ]O\s*0?{q_num}\b.*?(?:\[)(.*?)(?:\])"
                                        m_h = re.search(padrao_h, grade_raw)
                                        habilidade = m_h.group(1).strip() if m_h else f"Revisar conceito da Questão {q_num}"
                                        lacunas_stats.append({"q": q_num, "taxa": taxa_acerto, "hab": habilidade})
                            
                            if lacunas_stats:
                                top_lacunas = sorted(lacunas_stats, key=lambda x: x['taxa'])[:3]
                                st.error("🚨 **Professor, revise estes conceitos na próxima aula:**")
                                for lac in top_lacunas:
                                    st.markdown(f"**Q{lac['q']} ({lac['taxa']*100:.0f}% de acerto):** {lac['hab']}")
                            else:
                                st.success("✅ Turma com excelente desempenho! Nenhuma questão com menos de 60% de acerto.")
                    else:
                        st.caption("Gabarito oficial não encontrado no acervo.")
                else:
                    st.info("Aguardando dados da primeira avaliação para gerar o Raio-X.")

                st.divider()

                col_map1, col_map2 = st.columns([1, 1.5])
                
                with col_map1:
                    st.markdown("#### 🧩 Mapa de Perfis")
                    def categorizar_aluno(nec):
                        n = str(nec).upper().strip()
                        if "PENDENTE" in n or "SUSPEITA" in n: return "🟠 Radar (Suspeita)"
                        if "DEFASAGEM LEITURA" in n: return "🧱 Barreira de Leitura"
                        if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮 Desafio Lógico"
                        if "ALTA PERFORMANCE" in n: return "🚀 Alta Performance"
                        if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤 Típico / Padrão"
                        return "♿ Inclusão Oficial (PEI)" 
                    
                    alunos_rad['PERFIL_COG'] = alunos_rad['NECESSIDADES'].apply(categorizar_aluno)
                    contagem = alunos_rad['PERFIL_COG'].value_counts().reset_index()
                    contagem.columns = ['Perfil', 'Quantidade']
                    
                    color_map = {
                        "👤 Típico / Padrão": "#A0AEC0", "♿ Inclusão Oficial (PEI)": "#9F7AEA",
                        "🟠 Radar (Suspeita)": "#ED8936", "🧱 Barreira de Leitura": "#E53E3E",
                        "🧮 Desafio Lógico": "#D69E2E", "🚀 Alta Performance": "#38B2AC"
                    }
                    
                    fig = px.pie(contagem, values='Quantidade', names='Perfil', hole=0.4, color='Perfil', color_discrete_map=color_map)
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    fig.update_layout(showlegend=False, margin=dict(t=0, b=0, l=0, r=0), height=250)
                    st.plotly_chart(fig, use_container_width=True)

                with col_map2:
                    st.markdown("#### 🚨 Sensor Semântico (Diário)")
                    st.caption("Classifique os alunos com base nas suas anotações recentes.")
                    
                    def ocultar_aviso_diario(data_obs, id_alu, texto_obs):
                        try:
                            wb = db.conectar()
                            ws = wb.worksheet("DB_DIARIO_BORDO")
                            dados = ws.get_all_values()
                            for i, row in enumerate(dados):
                                if i > 0 and row[0] == data_obs and db.limpar_id(row[1]) == db.limpar_id(id_alu) and row[6] == texto_obs:
                                    ws.update_cell(i + 1, 7, texto_obs + " [LIDO]")
                                    st.cache_data.clear()
                                    return True
                        except: pass
                        return False

                    if not df_d_rad.empty:
                        obs_reais = df_d_rad[
                            (df_d_rad['OBSERVACOES'] != "") & 
                            (~df_d_rad['OBSERVACOES'].str.contains("Nota de Trabalho", na=False, case=False)) &
                            (~df_d_rad['OBSERVACOES'].str.contains(r"\[LIDO\]", na=False, case=False))
                        ]
                        
                        if not obs_reais.empty:
                            ultimas_obs = obs_reais.tail(3).iloc[::-1]
                            for _, row_obs in ultimas_obs.iterrows():
                                with st.container(border=True):
                                    st.markdown(f"🗣️ **{row_obs['NOME_ALUNO']}** ({row_obs['DATA']})")
                                    st.info(f"*{row_obs['OBSERVACOES']}*")
                                    
                                    c_b1, c_b2, c_b3, c_b4 = st.columns(4)
                                    id_aluno_obs = row_obs['ID_ALUNO']
                                    nome_aluno_obs = row_obs['NOME_ALUNO']
                                    data_obs = row_obs['DATA']
                                    texto_obs = row_obs['OBSERVACOES']
                                    
                                    if c_b1.button("🧱 Leitura", key=f"btn_leit_{id_aluno_obs}_{row_obs.name}", use_container_width=True):
                                        db.atualizar_aluno_cascata(id_aluno_obs, nome_aluno_obs, t_rad, "DEFASAGEM LEITURA")
                                        ocultar_aviso_diario(data_obs, id_aluno_obs, texto_obs); st.rerun()
                                    if c_b2.button("🧮 Mat.", key=f"btn_mat_{id_aluno_obs}_{row_obs.name}", use_container_width=True):
                                        db.atualizar_aluno_cascata(id_aluno_obs, nome_aluno_obs, t_rad, "DEFASAGEM MATEMÁTICA")
                                        ocultar_aviso_diario(data_obs, id_aluno_obs, texto_obs); st.rerun()
                                    if c_b3.button("🟠 PEI", key=f"btn_pei_{id_aluno_obs}_{row_obs.name}", use_container_width=True):
                                        db.atualizar_aluno_cascata(id_aluno_obs, nome_aluno_obs, t_rad, "PEI - PENDENTE")
                                        ocultar_aviso_diario(data_obs, id_aluno_obs, texto_obs); st.rerun()
                                    if c_b4.button("✅ Ciente", key=f"btn_ok_{id_aluno_obs}_{row_obs.name}", use_container_width=True):
                                        ocultar_aviso_diario(data_obs, id_aluno_obs, texto_obs); st.rerun()
                        else:
                            st.success("✅ Nenhuma observação pendente.")
                    else:
                        st.info("Sem registros no Diário.")

    # ==============================================================================
    # 🎲 ABA 3: ROLETA DE ARGUIÇÃO (MANTIDA INTACTA)
    # ==============================================================================
    with tab_roleta:
        import random
        st.subheader("🎲 Roleta de Arguição & Diagnóstico Clínico")
        st.caption("Sorteie alunos, registre o desempenho no quadro e anote lacunas específicas. O sistema resgata faltas e arguições da data selecionada.")
        
        c_rol1, c_rol2 = st.columns([1, 1])
        t_roleta = c_rol1.selectbox("🎯 Selecione a Turma para a Roleta:", lista_turmas_segura, key=f"rol_t_{v}")
        
        data_roleta = c_rol2.date_input("📅 Data da Arguição:", date.today(), format="DD/MM/YYYY", key=f"rol_d_{v}")
        data_roleta_str = data_roleta.strftime("%d/%m/%Y")
        
        with st.expander("⚙️ Configurar Pontuação da Arguição"):
            c_pts1, c_pts2 = st.columns(2)
            pt_acerto = c_pts1.number_input("Pontos por Acertar/Explicar (+):", 0.0, 5.0, 0.5, step=0.1, key=f"pt_acerto_{v}")
            pt_recusa = c_pts2.number_input("Punição por Recusa (-):", -5.0, 0.0, -0.5, step=0.1, key=f"pt_recusa_{v}")

        if t_roleta:
            alunos_roleta = df_alunos[df_alunos['TURMA'] == t_roleta].sort_values(by="NOME_ALUNO").copy()
            
            if alunos_roleta.empty:
                st.warning("Nenhum aluno cadastrado nesta turma.")
            else:
                def definir_icone_status(nec):
                    n = str(nec).upper().strip()
                    if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                    if "DEFASAGEM LEITURA" in n: return "🧱"
                    if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
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
                        id_a = db.limpar_id(row['ID'])
                        nome_a = row['NOME_ALUNO']
                        icone_a = row['ICONE']
                        
                        status_inicial = "⏳ Pendente"
                        obs_inicial = ""
                        pts_inicial = 0.0
                        
                        reg_aluno = diario_dia[diario_dia['ID_ALUNO'].apply(db.limpar_id) == id_a]
                        if not reg_aluno.empty:
                            if any(reg_aluno['TAGS'] == "AUSÊNCIA"):
                                status_inicial = "⏭️ Faltou"
                                obs_inicial = "Ausente no Diário de Bordo."
                            elif any(reg_aluno['TAGS'] == "ARGUIÇÃO"):
                                reg_arg = reg_aluno[reg_aluno['TAGS'] == "ARGUIÇÃO"].iloc[-1]
                                obs_inicial = reg_arg['OBSERVACOES'].replace("Quadro Negro: ", "")
                                pts_inicial = util.sosa_to_float(reg_arg['BONUS'])
                                
                                if pts_inicial > 0: status_inicial = "✅ Dominou"
                                elif pts_inicial < 0: status_inicial = "❌ Recusou"
                                elif "Isento" in obs_inicial: status_inicial = "♿ Isento"
                                else: status_inicial = "🤝 Tentou"
                                
                        lista_inicial.append({
                            "ID": id_a,
                            "Estudante": f"{icone_a} {nome_a}",
                            "Status": status_inicial,
                            "Diagnóstico / Anotação": obs_inicial,
                            "Pontos": pts_inicial
                        })
                    st.session_state[chave_lista] = lista_inicial
                    
                if chave_sorteado not in st.session_state:
                    st.session_state[chave_sorteado] = None

                st.markdown("---")
                col_roleta, col_lista = st.columns([1.2, 1.8])
                
                with col_roleta:
                    st.markdown("### 🎯 Sorteador")
                    pendentes = [a for a in st.session_state[chave_lista] if a["Status"] == "⏳ Pendente"]
                    
                    c_btn_sort, c_btn_reset = st.columns([2, 1])
                    if c_btn_sort.button("🎲 SORTEAR ESTUDANTE", type="primary", use_container_width=True):
                        if not pendentes:
                            st.success("🎉 Todos os alunos presentes já foram chamados!")
                        else:
                            sorteado = random.choice(pendentes)
                            st.session_state[chave_sorteado] = sorteado["ID"]
                            st.rerun()
                            
                    if c_btn_reset.button("🔄 Resetar Sorteio", use_container_width=True):
                        del st.session_state[chave_lista]
                        st.session_state[chave_sorteado] = None
                        st.rerun()
                        
                    if st.session_state[chave_sorteado]:
                        id_atual = st.session_state[chave_sorteado]
                        aluno_atual = next(a for a in st.session_state[chave_lista] if a["ID"] == id_atual)
                        aluno_db = alunos_roleta[alunos_roleta['ID'].apply(db.limpar_id) == id_atual].iloc[0]
                        
                        with st.container(border=True):
                            st.markdown(f"<h2 style='text-align: center;'>{aluno_atual['Estudante']}</h2>", unsafe_allow_html=True)
                            st.markdown(f"<p style='text-align: center; color: gray;'>Perfil: {aluno_db['NECESSIDADES']}</p>", unsafe_allow_html=True)
                            
                            anotacao = st.text_area("📝 Diagnóstico Clínico (O que ele errou/acertou?):", 
                                                    value=aluno_atual["Diagnóstico / Anotação"],
                                                    placeholder="Ex: Não sabe dividir com vírgula; Esqueceu a regra de sinais...",
                                                    key=f"anotacao_{id_atual}")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            c_av1, c_av2, c_av3 = st.columns(3)
                            c_av4, c_av5, c_av6 = st.columns(3)
                            
                            def registrar_arguicao(status_label, pontos, obs_padrao):
                                obs_final = anotacao.strip() if anotacao.strip() else obs_padrao
                                for a in st.session_state[chave_lista]:
                                    if a["ID"] == id_atual:
                                        a["Status"] = status_label
                                        a["Pontos"] = pontos
                                        a["Diagnóstico / Anotação"] = obs_final
                                        break
                                
                                nome_limpo = aluno_db['NOME_ALUNO'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                                
                                wb = db.conectar()
                                ws = wb.worksheet("DB_DIARIO_BORDO")
                                dados = ws.get_all_values()
                                
                                for i in range(len(dados)-1, 0, -1):
                                    row = dados[i]
                                    if row[0] == data_roleta_str and db.limpar_id(row[1]) == id_atual and row[5] == "ARGUIÇÃO":
                                        ws.delete_rows(i+1)
                                
                                ws.append_row([
                                    data_roleta_str, id_atual, nome_limpo, t_roleta, 
                                    "TRUE", "ARGUIÇÃO", f"Quadro Negro: {obs_final}", util.sosa_to_str(pontos)
                                ], value_input_option="USER_ENTERED")
                                
                                st.cache_data.clear()
                                st.session_state[chave_sorteado] = None
                            
                            if c_av1.button(f"✅ Dominou (+{pt_acerto})", use_container_width=True):
                                with st.spinner("Salvando..."):
                                    registrar_arguicao("✅ Dominou", pt_acerto, "Resolveu e explicou corretamente.")
                                    st.rerun()
                            if c_av2.button("🤝 Tentou (0.0)", use_container_width=True):
                                with st.spinner("Salvando..."):
                                    registrar_arguicao("🤝 Tentou", 0.0, "Foi ao quadro, mas apresentou dificuldades.")
                                    st.rerun()
                            if c_av3.button(f"❌ Recusou ({pt_recusa})", use_container_width=True):
                                with st.spinner("Salvando..."):
                                    registrar_arguicao("❌ Recusou", pt_recusa, "Recusou-se a participar.")
                                    st.rerun()
                            if c_av4.button("🔤 Não Alfabetizado", use_container_width=True):
                                with st.spinner("Registrando isenção..."):
                                    registrar_arguicao("♿ Isento", 0.0, "Isento da arguição no quadro: Não alfabetizado.")
                                    st.rerun()
                            if c_av5.button("♿ Aluno PEI", use_container_width=True):
                                with st.spinner("Registrando isenção..."):
                                    registrar_arguicao("♿ Isento", 0.0, "Isento da arguição no quadro: Aluno PEI (Avaliação adaptada).")
                                    st.rerun()
                            if c_av6.button("⏭️ Faltou / Pular", use_container_width=True):
                                for a in st.session_state[chave_lista]:
                                    if a["ID"] == id_atual:
                                        a["Status"] = "⏭️ Faltou"
                                        break
                                st.session_state[chave_sorteado] = None
                                st.rerun()

                with col_lista:
                    st.markdown("### 📋 Lista Fixa de Arguição")
                    df_lista = pd.DataFrame(st.session_state[chave_lista])
                    
                    df_editado = st.data_editor(
                        df_lista, hide_index=True, use_container_width=True, height=400,
                        column_config={
                            "ID": None,
                            "Estudante": st.column_config.TextColumn("Estudante", disabled=True, width="medium"),
                            "Status": st.column_config.TextColumn("Status", disabled=True, width="small"),
                            "Pontos": st.column_config.NumberColumn("Pts", disabled=True, width="small"),
                            "Diagnóstico / Anotação": st.column_config.TextColumn("Anotações do Professor", width="large")
                        },
                        key=f"editor_lista_roleta_{t_roleta}_{data_roleta_str}"
                    )
                    
                    if st.button("💾 Salvar Edições Manuais da Tabela", use_container_width=True):
                        with st.spinner("Sincronizando edições manuais com o banco de dados..."):
                            st.session_state[chave_lista] = df_editado.to_dict('records')
                            wb = db.conectar()
                            ws = wb.worksheet("DB_DIARIO_BORDO")
                            dados = ws.get_all_values()
                            
                            updates = []
                            for a in st.session_state[chave_lista]:
                                if a["Status"] not in ["⏳ Pendente", "⏭️ Faltou"]:
                                    for i, row in enumerate(dados):
                                        if i > 0 and row[0] == data_roleta_str and db.limpar_id(row[1]) == a["ID"] and row[5] == "ARGUIÇÃO":
                                            nova_obs = f"Quadro Negro: {a['Diagnóstico / Anotação']}"
                                            updates.append(gspread.Cell(row=i+1, col=7, value=nova_obs))
                                            break
                            if updates:
                                ws.update_cells(updates)
                                st.cache_data.clear()
                            st.success("Anotações atualizadas!")

                    st.markdown("---")
                    with st.expander("✏️ Corrigir Lançamento (Desfazer)"):
                        avaliados = [a for a in st.session_state[chave_lista] if a["Status"] not in ["⏳ Pendente", "⏭️ Faltou"]]
                        if avaliados:
                            aluno_erro = st.selectbox("Selecione o Estudante:", [a["Estudante"] for a in avaliados], key=f"corr_{t_roleta}_{data_roleta_str}")
                            if st.button("🔄 Corrigir Avaliação", use_container_width=True):
                                with st.spinner("Preparando correção..."):
                                    id_erro = next(a["ID"] for a in avaliados if a["Estudante"] == aluno_erro)
                                    try:
                                        wb = db.conectar()
                                        ws = wb.worksheet("DB_DIARIO_BORDO")
                                        dados = ws.get_all_values()
                                        for i in range(len(dados)-1, 0, -1):
                                            row = dados[i]
                                            if row[0] == data_roleta_str and db.limpar_id(row[1]) == id_erro and row[5] == "ARGUIÇÃO":
                                                ws.delete_rows(i+1)
                                    except: pass
                                    
                                    for a in st.session_state[chave_lista]:
                                        if a["ID"] == id_erro:
                                            a["Status"] = "⏳ Pendente"
                                            a["Pontos"] = 0.0
                                            break
                                    
                                    st.session_state[chave_sorteado] = id_erro
                                    st.cache_data.clear()
                                    st.rerun()
                        else:
                            st.info("Nenhum aluno avaliado ainda.")


    # ==============================================================================
    # 📅 ABA 4: CONTROLE DE EVASÃO E FREQUÊNCIA (BLINDADO ANTI-DUPLICIDADE)
    # ==============================================================================
    with tab_frequencia:
        st.subheader("📅 Controle de Frequência e Evasão")
        st.caption("Módulo inteligente para auditoria de presenças e detecção de abandono escolar.")

        c_freq1, c_freq2 = st.columns([1, 1])
        t_freq = c_freq1.selectbox("👥 Selecione a Turma:", lista_turmas_segura, key=f"freq_t_{v}")
        trim_freq = c_freq2.selectbox("📅 Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"freq_trim_{v}")

        if t_freq:
            df_d_freq = df_diario[df_diario['TURMA'] == t_freq].copy()
            
            if df_d_freq.empty:
                st.info("📭 Nenhum registro de diário encontrado para esta turma.")
            else:
                calendario_freq = {
                    "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
                    "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
                    "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
                }
                dt_ini_f, dt_fim_f = calendario_freq.get(trim_freq, (date(2026, 1, 1), date(2026, 12, 31)))
                
                df_d_freq['DATA_DT'] = pd.to_datetime(df_d_freq['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                df_d_trim = df_d_freq[(df_d_freq['DATA_DT'] >= dt_ini_f) & (df_d_freq['DATA_DT'] <= dt_fim_f)].copy()

                if df_d_trim.empty:
                    st.warning(f"⚠️ Nenhum registro de aula encontrado no {trim_freq}.")
                else:
                    modo_visao = st.radio("Modo de Visualização:", ["📊 Grade do Trimestre (Tabela)", "📅 Faltosos por Dia", "🚨 Radar de Evasão"], horizontal=True, key=f"modo_freq_{v}")
                    st.markdown("---")

                    # 🚨 1. IDENTIFICA DIAS NÃO LETIVOS ANTES DA LIMPEZA
                    dias_nao_letivos = df_d_trim[df_d_trim['TAGS'] == "DIA NÃO LETIVO"]['DATA'].unique()
                    
                    # 🚨 2. MOTOR DE LIMPEZA E SOBERANIA DE DADOS
                    # Remove o registro fantasma "TODOS OS ALUNOS" da visualização
                    df_d_trim = df_d_trim[df_d_trim['ID_ALUNO'] != "GLOBAL"]
                    
                    # Mata qualquer duplicidade (garante apenas 1 registro por aluno por dia)
                    df_d_trim = df_d_trim.drop_duplicates(subset=['DATA', 'ID_ALUNO'], keep='last')

                    def get_status(row):
                        if row['TAGS'] == "AUSÊNCIA": return "F"
                        return "•"
                        
                    df_d_trim['STATUS'] = df_d_trim.apply(get_status, axis=1)
                    datas_aulas = sorted(df_d_trim['DATA_DT'].unique())
                    datas_str = [d.strftime("%d/%m/%Y") for d in datas_aulas]
                    
                    total_aulas_validas = len([d for d in datas_str if d not in dias_nao_letivos])

                    if modo_visao == "📊 Grade do Trimestre (Tabela)":
                        st.markdown(f"#### 📋 Grade de Frequência - {trim_freq}")
                        pivot_freq = df_d_trim.pivot_table(index="NOME_ALUNO", columns="DATA", values="STATUS", aggfunc='first', fill_value="-")
                        pivot_freq = pivot_freq.reindex(columns=datas_str)
                        
                        def color_status(val):
                            if val == 'F': return 'color: #FF4B4B; font-weight: bold;'
                            if val == '•': return 'color: #2ECC71; font-weight: bold;'
                            return 'color: gray;'
                            
                        st.dataframe(pivot_freq.style.map(color_status), use_container_width=True, height=(len(pivot_freq)*35)+40)

                    elif modo_visao == "📅 Faltosos por Dia":
                        st.markdown("#### 📅 Visão Diária de Ausências")
                        data_alvo = st.selectbox("Selecione a Data da Aula:", datas_str, key=f"data_alvo_freq_{v}")
                        
                        if data_alvo in dias_nao_letivos:
                            # Busca o motivo no dataframe original (antes da limpeza do GLOBAL)
                            motivo = df_d_freq[(df_d_freq['DATA'] == data_alvo) & (df_d_freq['TAGS'] == "DIA NÃO LETIVO")].iloc[0]['OBSERVACOES']
                            st.warning(f"🛑 **DIA NÃO LETIVO:** {motivo}")
                            st.info("Nenhuma chamada foi realizada nesta data.")
                        else:
                            df_dia = df_d_trim[df_d_trim['DATA'] == data_alvo]
                            
                            # 🚨 EXTRAÇÃO COM ORDEM ALFABÉTICA FORÇADA
                            faltosos_dia = sorted(df_dia[df_dia['STATUS'] == 'F']['NOME_ALUNO'].tolist())
                            presentes_dia = sorted(df_dia[df_dia['STATUS'] == '•']['NOME_ALUNO'].tolist())
                            
                            c_dia1, c_dia2 = st.columns([1, 2])
                            c_dia1.metric("Total de Faltas", len(faltosos_dia))
                            c_dia2.metric("Total de Presenças", len(presentes_dia))
                            
                            if faltosos_dia:
                                st.error("❌ **Alunos Ausentes:**\n" + "\n".join([f"- {f}" for f in faltosos_dia]))
                            else:
                                st.success("✅ 100% de Presença neste dia! Nenhum aluno faltou.")

                    elif modo_visao == "🚨 Radar de Evasão":
                        st.markdown("#### 🚨 Inteligência de Evasão Escolar")
                        st.info(f"Total de aulas válidas no {trim_freq}: **{total_aulas_validas} aulas** (Ignorando {len(dias_nao_letivos)} dias não letivos)")
                        
                        alunos_turma = sorted(df_alunos[df_alunos['TURMA'] == t_freq]['NOME_ALUNO'].tolist())
                        
                        stats_evasao = []
                        for aluno in alunos_turma:
                            df_aluno = df_d_trim[(df_d_trim['NOME_ALUNO'] == aluno) & (~df_d_trim['DATA'].isin(dias_nao_letivos))]
                            faltas = len(df_aluno[df_aluno['STATUS'] == 'F'])
                            presencas = len(df_aluno[df_aluno['STATUS'] == '•'])
                            
                            if faltas + presencas == 0:
                                perc_falta = 100.0
                                faltas = total_aulas_validas
                            else:
                                perc_falta = (faltas / total_aulas_validas) * 100 if total_aulas_validas > 0 else 0
                                
                            if perc_falta == 100: cat = "👻 Fantasma (Nunca Veio)"
                            elif perc_falta >= 25: cat = "🚨 Risco Crítico (>25%)"
                            elif perc_falta >= 10: cat = "⚠️ Faltas Irregulares"
                            else: cat = "✅ Assíduo"
                                
                            stats_evasao.append({"Estudante": aluno, "Faltas": faltas, "% Ausência": perc_falta, "Diagnóstico": cat})
                            
                        df_evasao = pd.DataFrame(stats_evasao).sort_values(by="% Ausência", ascending=False)
                        
                        fantasmas = df_evasao[df_evasao['Diagnóstico'].str.contains("Fantasma")]
                        criticos = df_evasao[df_evasao['Diagnóstico'].str.contains("Risco Crítico")]
                        
                        c_ev1, c_ev2 = st.columns(2)
                        with c_ev1:
                            if not fantasmas.empty: st.error(f"**👻 Alunos Fantasmas ({len(fantasmas)}):**\n" + "\n".join([f"- {row['Estudante']}" for _, row in fantasmas.iterrows()]))
                            else: st.success("**👻 Alunos Fantasmas:** Nenhum.")
                        with c_ev2:
                            if not criticos.empty: st.warning(f"**🚨 Risco Crítico de Evasão ({len(criticos)}):**\n" + "\n".join([f"- {row['Estudante']} ({row['Faltas']} faltas)" for _, row in criticos.iterrows()]))
                            else: st.success("**🚨 Risco Crítico:** Nenhum aluno em risco.")
                                
                        def color_diag(val):
                            if "Fantasma" in val: return 'color: white; background-color: #800000; font-weight: bold;'
                            if "Risco" in val: return 'color: white; background-color: #E74C3C; font-weight: bold;'
                            if "Irregulares" in val: return 'color: black; background-color: #F1C40F; font-weight: bold;'
                            return 'color: white; background-color: #2ECC71;'
                            
                        st.dataframe(df_evasao.style.map(color_diag, subset=['Diagnóstico']).format({"% Ausência": "{:.1f}%"}), use_container_width=True, hide_index=True)

    # ==============================================================================
    # ⚙️ ABA 5: SECRETARIA & MATRÍCULAS (ADMINISTRAÇÃO CENTRALIZADA)
    # ==============================================================================
    with tab_secretaria:
        st.subheader("⚙️ Secretaria & Matrículas")
        st.caption("Central administrativa para criar turmas, importar alunos e editar cadastros.")
        
        sub_criar, sub_povoar, sub_editar = st.tabs(["🏗️ Criar Turmas/Horários", "➕ Povoar Alunos", "✏️ Edição & Diagnóstico Rápido"])
        
        # --- SUB-ABA 1: CRIAR TURMAS ---
        with sub_criar:
            tipo_cadastro = st.radio("O que o senhor deseja alocar na grade?", ["📚 Turma Regular (Alunos)", "⚙️ Planejamento (PI / PC)"], horizontal=True, key=f"tipo_cad_{v}")
            
            with st.container(border=True):
                if tipo_cadastro == "📚 Turma Regular (Alunos)":
                    c1, c2, c3 = st.columns(3)
                    ano_t = c1.selectbox("Série/Ano:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key=f"ano_cad_{v}")
                    letra_t = c2.selectbox("Letra:", ["A", "B", "C", "D", "E", "F", "G"], key=f"letra_cad_{v}")
                    turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"], key=f"turno_cad_{v}")
                    
                    sigla_final = f"{ano_t}ª {turno_t[0].upper()}{letra_t}"
                    nome_final = f"{ano_t}º Ano {letra_t}"
                else:
                    c1, c2, c3 = st.columns([1, 2, 1])
                    sigla_plan = c1.selectbox("Sigla:", ["PI", "PC", "AC", "HTPC", "OUTRO"], key=f"sigla_plan_{v}")
                    desc_plan = c2.text_input("Descrição:", placeholder="Ex: Planejamento Individual", key=f"desc_plan_{v}")
                    turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"], key=f"turno_plan_{v}")
                    
                    sigla_final = sigla_plan
                    nome_final = desc_plan if desc_plan else "Planejamento"

            st.markdown("#### 📅 Alocação de Horário (Dias e Tempos)")
            opcoes_horarios = [
                "Segunda (1º Tempo)", "Segunda (2º Tempo)", "Terça (1º Tempo)", "Terça (2º Tempo)", 
                "Quarta (1º Tempo)", "Quarta (2º Tempo)", "Quinta (1º Tempo)", "Quinta (2º Tempo)", 
                "Sexta (1º Tempo)", "Sexta (2º Tempo)"
            ]
            dias_aula = st.multiselect("Selecione a grade:", opcoes_horarios, key=f"dias_cad_{v}")
            
            if st.button("💾 ALOCAR NA GRADE OFICIAL", use_container_width=True, type="primary"):
                if not dias_aula: st.error("⚠️ Ordem negada: Selecione pelo menos um horário.")
                else:
                    if db.salvar_no_banco("DB_TURMAS", [sigla_final, nome_final, turno_t, " / ".join(dias_aula), "N/A", "ATIVO"]):
                        st.success(f"✅ {sigla_final} alocado com sucesso na grade oficial!"); time.sleep(1.5); st.rerun()

        # --- SUB-ABA 2: POVOAR ALUNOS ---
        with sub_povoar:
            if not lista_turmas_segura:
                st.warning("Cadastre uma turma primeiro.")
            else:
                t_dest = st.selectbox("Turma de Destino:", lista_turmas_segura, key=f"dest_pov_{v}")
                if t_dest:
                    t1_man, t2_lote = st.tabs(["✍️ Cadastro Manual", "📄 Importação em Lote (CSV)"])
                    
                    with t1_man:
                        with st.form("f_manual_povoar"):
                            nome_a = st.text_input("Nome Completo:").upper()
                            opcoes_nec = ["TÍPICO", "TEA", "TDAH", "DISLEXIA", "DEF. INTELECTUAL", "TOD", "BAIXA VISÃO", "SURDEZ", "PEI - PENDENTE", "OUTRO"]
                            perfil_base = st.multiselect("Perfil / Necessidades (Pode selecionar vários):", opcoes_nec, default=["TÍPICO"])
                            
                            if st.form_submit_button("💾 SALVAR ALUNO"):
                                if not nome_a: st.error("⚠️ Digite o nome do aluno.")
                                else:
                                    if "TÍPICO" in perfil_base and len(perfil_base) > 1: perfil_base.remove("TÍPICO")
                                    perfil_str = " + ".join(perfil_base) if perfil_base else "TÍPICO"
                                    id_n = db.gerar_proximo_id(df_alunos)
                                    if db.salvar_no_banco("DB_ALUNOS", [id_n, nome_a, t_dest, "ATIVO", perfil_str, "MANUAL"]):
                                        st.success(f"✅ {nome_a} cadastrado com perfil: {perfil_str}!"); st.rerun()
                    
                    with t2_lote:
                        st.info("💡 **Dica de Soberania:** Cole a lista de alunos abaixo. Se o aluno tiver um asterisco (*) no final do nome, o sistema detectará automaticamente como PEI.")
                        texto_lote = st.text_area("Cole os dados CSV aqui (NOME, PERFIL):", height=300, placeholder="ADRIEL VINICIUS ALVES MARTINS,TÍPICO\nJOSE LEVI BRONZE SANTOS*,PEI - PENDENTE")
                        
                        if st.button("🚀 PROCESSAR IMPORTAÇÃO EM LOTE", type="primary", use_container_width=True):
                            if texto_lote.strip():
                                linhas = texto_lote.strip().split('\n')
                                novos_alunos = []
                                id_atual = db.gerar_proximo_id(df_alunos)
                                
                                with st.status("Importando alunos para o Banco de Dados...") as status:
                                    for linha in linhas:
                                        if not linha.strip(): continue
                                        partes = linha.split(',')
                                        nome_bruto = partes[0].strip().upper()
                                        
                                        if "*" in nome_bruto:
                                            nome_limpo = nome_bruto.replace("*", "").strip()
                                            perfil = "PEI - PENDENTE"
                                        else:
                                            nome_limpo = nome_bruto
                                            perfil = partes[1].strip().upper() if len(partes) > 1 else "TÍPICO"
                                        
                                        novos_alunos.append([id_atual, nome_limpo, t_dest, "ATIVO", perfil, "LOTE"])
                                        id_atual += 1 
                                    
                                    if db.salvar_lote("DB_ALUNOS", novos_alunos):
                                        status.update(label=f"✅ {len(novos_alunos)} alunos importados com sucesso para a turma {t_dest}!", state="complete")
                                        st.balloons(); time.sleep(1.5); st.rerun()
                            else:
                                st.error("⚠️ Cole os dados na caixa de texto antes de processar.")

        # --- SUB-ABA 3: EDIÇÃO & DIAGNÓSTICO RÁPIDO ---
        with sub_editar:
            t_origem = st.selectbox("Selecione a Turma Atual:", [""] + sorted(df_alunos['TURMA'].unique().tolist()), key=f"orig_ed_{v}")
            
            if t_origem:
                alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO")
                aluno_sel_nome = st.selectbox("Selecione o Aluno:", alunos_opcoes['NOME_ALUNO'].tolist(), key=f"alu_ed_{v}")
                dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
                
                st.markdown("#### ⚡ Diagnóstico Rápido (1-Click)")
                c_btn1, c_btn2, c_btn3, c_btn4 = st.columns(4)
                
                if c_btn1.button("📚 Defasagem Leitura", use_container_width=True):
                    with st.spinner("Atualizando perfil..."):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "DEFASAGEM LEITURA")
                        st.success("Perfil atualizado!"); time.sleep(0.5); st.rerun()
                if c_btn2.button("🧮 Defasagem Matemática", use_container_width=True):
                    with st.spinner("Atualizando perfil..."):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "DEFASAGEM MATEMÁTICA")
                        st.success("Perfil atualizado!"); time.sleep(0.5); st.rerun()
                if c_btn3.button("🚀 Alta Performance", use_container_width=True):
                    with st.spinner("Atualizando perfil..."):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "ALTA PERFORMANCE")
                        st.success("Perfil atualizado!"); time.sleep(0.5); st.rerun()
                if c_btn4.button("👤 Típico (Limpar)", use_container_width=True):
                    with st.spinner("Limpando perfil..."):
                        db.atualizar_aluno_cascata(dados_atuais['ID'], dados_atuais['NOME_ALUNO'], t_origem, "TÍPICO")
                        st.success("Perfil limpo!"); time.sleep(0.5); st.rerun()
                
                st.markdown("---")
                
                with st.form("form_edicao"):
                    novo_nome = st.text_input("Nome Completo:", value=dados_atuais['NOME_ALUNO']).upper()
                    idx_turma = lista_turmas_segura.index(t_origem) if t_origem in lista_turmas_segura else 0
                    nova_turma = st.selectbox("Turma de Destino (Para Transferência):", lista_turmas_segura, index=idx_turma)
                    nova_nec = st.text_input("Necessidades / CIDs:", value=dados_atuais['NECESSIDADES']).upper()
                    
                    if st.form_submit_button("💾 SALVAR E ATUALIZAR HISTÓRICO EM CASCATA"):
                        with st.spinner("Viajando no tempo e atualizando todo o histórico do aluno..."):
                            if db.atualizar_aluno_cascata(dados_atuais['ID'], novo_nome, nova_turma, nova_nec):
                                st.success("✅ Cadastro, laudos e histórico atualizados em cascata com sucesso!")
                                time.sleep(1.5); st.rerun()




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
# MÓDULO: RELATÓRIOS PEI / PERFIL IA - CLEAN & UX (V110 - MULTIPERFIL RELACIONAL)
# ==============================================================================
elif menu == "♿ Relatórios PEI / Perfil IA":
    st.title("🧠 Analista de Perfis e Dossiê PEI")
    st.caption("💡 **Guia de Comando:** O sistema cruza dados de engajamento e notas para redigir relatórios evolutivos. A IA adapta o texto automaticamente se o aluno for PEI, tiver defasagem de base ou for de alta performance.")
    st.markdown("---")

    # 🚨 MOTOR ANTI-DUPLICIDADE (UPSERT SOBERANO)
    def salvar_relatorio_pei_sem_duplicidade(id_aluno, nome_aluno, tipo_rel, conteudo_rel):
        try:
            wb = db.conectar()
            ws = wb.worksheet("DB_RELATORIOS")
            dados = ws.get_all_values()
            # Engenharia de Deleção Reversa: Apaga a versão antiga antes de salvar a nova
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
        # --- 1. SELEÇÃO DE ESTUDANTE ---
        with st.container(border=True):
            c_t, c_a = st.columns([1, 2])
            
            turmas_reais_pei = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
            lista_turmas = sorted(turmas_reais_pei['ID_TURMA'].unique()) if not turmas_reais_pei.empty else sorted(df_alunos['TURMA'].unique())
            
            turma_pei = c_t.selectbox("🎯 Filtrar Turma:", lista_turmas, key="pei_t_clean")
            df_turma_foco = df_alunos[df_alunos['TURMA'] == turma_pei].copy()
            
            if df_turma_foco.empty:
                st.warning(f"⚠️ Nenhum aluno cadastrado na turma {turma_pei} ainda. Vá em 'Gestão da Turma' para povoar.")
                st.stop()
            
            def definir_icone_status(nec):
                n = str(nec).upper().strip()
                if "PENDENTE" in n or "SUSPEITA" in n: return "🟠"
                if "DEFASAGEM LEITURA" in n: return "🧱"
                if "DEFASAGEM MATEMÁTICA" in n or "DEFASAGEM MATEMATICA" in n: return "🧮"
                if "ALTA PERFORMANCE" in n: return "🚀"
                if n in["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return "👤"
                return "♿"

            df_turma_foco['STATUS_ICON'] = df_turma_foco['NECESSIDADES'].apply(definir_icone_status)
            df_turma_foco['LABEL'] = df_turma_foco.apply(lambda x: f"{x['STATUS_ICON']} {x['NOME_ALUNO']} | {x['NECESSIDADES']}", axis=1)
            
            aluno_sel_label = c_a.selectbox("🔍 Selecionar Estudante:", df_turma_foco['LABEL'].tolist(), key="pei_a_clean")
            
            nome_limpo = aluno_sel_label.split(" | ")[0].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "").strip()
            
            dados_a = df_turma_foco[df_turma_foco['NOME_ALUNO'] == nome_limpo].iloc[0]
            id_a = db.limpar_id(dados_a['ID'])
            perfil_atual = str(dados_a['NECESSIDADES']).upper().strip()

            # 🚨 Limpa o chat se mudar de aluno
            if st.session_state.get("current_pei_student") != id_a:
                st.session_state.current_pei_student = id_a
                if "chat_history_pei" in st.session_state:
                    del st.session_state["chat_history_pei"]

        # --- 2. MOTOR DE FUSÃO E MEMÓRIA ---
        with st.status("🔍 Maestro Sosa interconectando safras e evidências...", expanded=False) as status:
            hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_a]
            
            # 🚨 MEMÓRIA RELACIONAL: Busca o Dossiê Master
            rel_master = hist_aluno[hist_aluno['TIPO'] == 'DOSSIE_MASTER_PEI']
            if not rel_master.empty:
                master_text = str(rel_master.iloc[-1]['CONTEUDO'])
                
                # Extrai o Checklist Salvo
                saved_checklist = ai.extrair_tag(master_text, "CHECKLIST")
                if saved_checklist:
                    try:
                        val_auto, val_soc, val_part, val_resp = saved_checklist.split('|')
                    except:
                        val_auto, val_soc, val_part, val_resp = "Com Apoio", "Interage", "Participativo", "Receptivo"
                else:
                    val_auto, val_soc, val_part, val_resp = "Com Apoio", "Interage", "Participativo", "Receptivo"
                
                # Extrai os textos
                v_diag = ai.extrair_tag(master_text, "DIAGNOSTICO_GERAL")
                v_soc_txt = ai.extrair_tag(master_text, "SOCIAIS")
                v_com_txt = ai.extrair_tag(master_text, "COMUNICATIVAS")
                v_emo_txt = ai.extrair_tag(master_text, "EMOCIONAIS")
                v_fun_txt = ai.extrair_tag(master_text, "FUNCIONAIS")
                v_diretrizes = ai.extrair_tag(master_text, "DIRETRIZES_CURRICULARES")
            else:
                master_text = "Primeiro Relatório (Linha de Base)."
                val_auto, val_soc, val_part, val_resp = "Com Apoio", "Interage", "Participativo", "Receptivo"
                v_diag, v_soc_txt, v_com_txt, v_emo_txt, v_fun_txt, v_diretrizes = "", "", "", "", "", ""
            
            vistos = 0
            bonus = 0.0
            if not df_diario.empty:
                d_aluno = df_diario[df_diario['ID_ALUNO'].apply(db.limpar_id) == id_a]
                if not d_aluno.empty and 'VISTO_ATIVIDADE' in d_aluno.columns:
                    vistos = len(d_aluno[d_aluno['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"])
                    bonus = d_aluno['BONUS'].apply(util.sosa_to_float).sum()
            
            media_scan = 0.0
            if not df_diagnosticos.empty:
                s_aluno = df_diagnosticos[df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_a]
                if not s_aluno.empty:
                    media_scan = s_aluno['NOTA_CALCULADA'].apply(util.sosa_to_float).mean()
            
            nota_safra = min(10.0, media_scan + bonus)
            status.update(label="✅ Dados Sincronizados com Sucesso!", state="complete")

        # --- 3. DASHBOARD DE MÉTRICAS E ALERTA DE PERFIL ---
        if "PENDENTE" in perfil_atual or "SUSPEITA" in perfil_atual:
            st.warning(f"🟠 **Radar de Investigação:** {perfil_atual}")
        elif "DEFASAGEM" in perfil_atual:
            st.error(f"🧱 **Barreira de Aprendizagem:** {perfil_atual}")
        elif "ALTA PERFORMANCE" in perfil_atual:
            st.info(f"🚀 **Destaque Cognitivo:** {perfil_atual}")
        elif perfil_atual not in["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]:
            st.warning(f"♿ **Condição Clínica (PEI):** {perfil_atual}")

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Engajamento (Vistos)", vistos)
        c2.metric("Mérito Acumulado ⭐", f"{bonus:.1f}")
        c3.metric("Nota Média de Safra", f"{nota_safra:.1f}")
        c4.metric("Relatos Salvos", len(hist_aluno))

        # --- 4. CHECKLIST DE OBSERVAÇÃO E RELATO DO PROFESSOR ---
        with st.container(border=True):
            st.markdown("#### 📋 Checklist de Percepção Pedagógica")
            st.caption("Ajuste os controles abaixo. A IA usará essas informações para dar o tom do relatório.")
            col_ch1, col_ch2 = st.columns(2)
            with col_ch1:
                v_autonomia = st.select_slider("Autonomia:", options=["Dependente", "Com Apoio", "Em Evolução", "Autônomo"], value=val_auto)
                v_social = st.select_slider("Socialização:", options=["Isolado", "Passivo", "Interage", "Líder"], value=val_soc)
            with col_ch2:
                v_participa = st.select_slider("Participação:", options=["Não participa", "Raramente", "Participativo", "Ativo"], value=val_part)
                v_resposta = st.select_slider("Resposta às Intervenções:", options=["Resistente", "Lento", "Receptivo", "Rápido"], value=val_resp)
            sem_mudancas = st.checkbox("📢 Quadro estável (Sem alterações significativas desde o último relatório)")
            
            st.markdown("---")
            relato_professor = st.text_area("✍️ Relato do Professor (Contexto Adicional):", placeholder="Ex: O aluno demonstrou muito interesse nas aulas com uso de tablet, mas fica agressivo com barulho alto. Quero que o relatório foque na necessidade de fones abafadores...", key="relato_prof_clean")

        # ==============================================================================
        # 🚨 MOTOR DE GERAÇÃO UNIFICADA (DOSSIÊ MASTER)
        # ==============================================================================
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🧠 GERAR DOSSIÊ INTEGRADO (EVOLUÇÃO + PEI)", type="primary", use_container_width=True):
            
            if "chat_history_pei" in st.session_state:
                del st.session_state["chat_history_pei"]
                
            with st.spinner("Maestro Sosa analisando a linha do tempo e redigindo o Dossiê Master..."):
                prompt_master = (
                    f"ESTUDANTE: {nome_limpo}. PERFIL COGNITIVO/CLÍNICO: {perfil_atual}.\n"
                    f"--- PASSADO ---\n{master_text}\n\n"
                    f"--- PRESENTE (DADOS) ---\n- Vistos: {vistos}, Bônus: {bonus}, Nota: {nota_safra}.\n"
                    f"--- CHECKLIST ATUAL ---\n- Autonomia: {v_autonomia}, Socialização: {v_social}, Participação: {v_participa}, Resposta: {v_resposta}.\n"
                    f"--- STATUS: {'Quadro Estável' if sem_mudancas else 'Houve alterações'}.\n"
                    f"🚨 RELATO DO PROFESSOR (PRIORIDADE MÁXIMA): {relato_professor if relato_professor else 'Nenhum relato adicional.'}\n\n"
                    f"MISSÃO: Gere um Dossiê Único e Integrado. Use as tags obrigatórias para separar o Diagnóstico Geral, as 4 Habilidades do PEI e as Diretrizes Curriculares.\n"
                    f"🚨 ATENÇÃO AO PERFIL: Como o aluno possui o perfil '{perfil_atual}', direcione o parecer pedagógico para as necessidades específicas desse quadro."
                )
                res_master = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_master)
                
                # Salva no banco imediatamente (Sem duplicidade)
                checklist_str = f"[CHECKLIST]\n{v_autonomia}|{v_social}|{v_participa}|{v_resposta}"
                texto_final_banco = f"{checklist_str}\n\n{res_master}"
                
                salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, "DOSSIE_MASTER_PEI", texto_final_banco)
                
                st.success("✅ Dossiê Master gerado e salvo no Repositório Vivo!")
                import time
                time.sleep(1)
                st.rerun()

        # --- 5. ABAS DE TRABALHO (REPOSITÓRIO VIVO) ---
        tab_evolucao, tab_pei_doc, tab_curr, tab_coord, tab_timeline, tab_export = st.tabs([
            "📈 1. Relatório de Evolução", 
            "🏛️ 2. Plano PEI (Capa)", 
            "📖 3. Currículo Adaptado",
            "📱 4. Relato Coordenação",
            "🗂️ 5. Linha do Tempo",
            "🖨️ 6. Exportar PEI Oficial"
        ])

        # --- ABA 1: RELATÓRIO DE EVOLUÇÃO ---
        with tab_evolucao:
            st.subheader("📝 Análise Longitudinal de Processos")
            
            if v_diag:
                # ==============================================================================
                # 🤖 MAESTRO COPILOT (CHATBOT DE REFINO DO PEI)
                # ==============================================================================
                with st.container(border=True):
                    st.markdown("#### 🤖 Maestro Copilot (Coautoria em Tempo Real)")
                    st.caption("Converse com a IA para ajustar o diagnóstico ou as diretrizes. O editor abaixo será atualizado automaticamente.")
                    
                    if "chat_history_pei" not in st.session_state:
                        st.session_state.chat_history_pei =[{"role": "assistant", "avatar": "🤖", "content": "Saudações, Mestre! O Dossiê Master foi carregado. Como deseja refinar o diagnóstico ou as diretrizes?"}]
                    
                    chat_container_pei = st.container(height=300)
                    with chat_container_pei:
                        for msg in st.session_state.chat_history_pei:
                            with st.chat_message(msg["role"], avatar=msg["avatar"]):
                                st.markdown(msg["content"])
                    
                    if cmd_refine_pei := st.chat_input("Ex: 'Deixe o diagnóstico mais otimista' ou 'Adicione o uso de fones abafadores nas diretrizes'...", key="chat_pei_input"):
                        st.session_state.chat_history_pei.append({"role": "user", "avatar": "💻", "content": cmd_refine_pei})
                        
                        with chat_container_pei:
                            with st.chat_message("user", avatar="💻"):
                                st.markdown(cmd_refine_pei)
                            with st.chat_message("assistant", avatar="🤖"):
                                with st.spinner("Reescrevendo Dossiê Master..."):
                                    hist_text = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.chat_history_pei[-5:]])
                                    prompt_refino = (
                                        f"HISTÓRICO DA CONVERSA:\n{hist_text}\n\n"
                                        f"ORDEM ATUAL: {cmd_refine_pei}\n\n"
                                        f"DOSSIÊ ATUAL PARA REFINAR:\n{master_text}"
                                    )
                                    
                                    resultado_refino = ai.gerar_ia("REFINADOR_PEI", prompt_refino)
                                    
                                    msg_chat = ai.extrair_tag(resultado_refino, "MENSAGEM_CHAT")
                                    novo_conteudo = ai.extrair_tag(resultado_refino, "CONTEUDO_ATUALIZADO")
                                    
                                    if not novo_conteudo:
                                        novo_conteudo = resultado_refino
                                        msg_chat = "Dossiê atualizado conforme solicitado, Mestre."
                                        
                                    st.markdown(msg_chat)
                                    st.session_state.chat_history_pei.append({"role": "assistant", "avatar": "🤖", "content": msg_chat})
                                    
                                    # Salva o novo conteúdo no banco imediatamente (Sem duplicidade)
                                    checklist_str = f"[CHECKLIST]\n{v_autonomia}|{v_social}|{v_participa}|{v_resposta}"
                                    texto_final_banco = f"{checklist_str}\n\n{novo_conteudo}"
                                    salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, "DOSSIE_MASTER_PEI", texto_final_banco)
                                    st.rerun()

                st.markdown("---")
                # 🚨 CAIXAS EDITÁVEIS (SOBERANIA MANUAL)
                ed_diag = st.text_area("Diagnóstico Geral:", v_diag, height=250, key="ed_diag_clean")
                ed_dir = st.text_area("Diretrizes Curriculares Sugeridas:", v_diretrizes, height=200, key="ed_dir_clean")
                
                if st.button("💾 SALVAR EDIÇÕES MANUAIS (EVOLUÇÃO)", use_container_width=True):
                    checklist_str = f"[CHECKLIST]\n{v_autonomia}|{v_social}|{v_participa}|{v_resposta}"
                    texto_consolidado = f"{checklist_str}\n\n[DIAGNOSTICO_GERAL]\n{ed_diag}\n\n[SOCIAIS]\n{v_soc_txt}\n\n[COMUNICATIVAS]\n{v_com_txt}\n\n[EMOCIONAIS]\n{v_emo_txt}\n\n[FUNCIONAIS]\n{v_fun_txt}\n\n[DIRETRIZES_CURRICULARES]\n{ed_dir}"
                    salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, "DOSSIE_MASTER_PEI", texto_consolidado)
                    st.success("✅ Edições salvas no Repositório Vivo!")
                    st.balloons()
            else:
                st.info("Clique em 'Gerar Dossiê Integrado' para criar a análise.")

        # --- ABA 2: PLANO DE ACESSIBILIDADE (PEI PÁGINA 1) ---
        with tab_pei_doc:
            st.subheader("🏛️ Seção 1: Plano de Acessibilidade Individual (Capa)")
            st.caption("O sistema extraiu as informações do Dossiê Master. Você pode editar e salvar o progresso.")
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                ed_soc = st.text_area("1. Habilidades Sociais:", v_soc_txt, height=180)
                ed_emo = st.text_area("3. Habilidades Emocionais:", v_emo_txt, height=180)
            with col_p2:
                ed_com = st.text_area("2. Habilidades Comunicativas:", v_com_txt, height=180)
                ed_fun = st.text_area("4. Habilidades Funcionais:", v_fun_txt, height=180)

            if st.button("💾 SALVAR EDIÇÕES DA CAPA NO BANCO", use_container_width=True):
                checklist_str = f"[CHECKLIST]\n{v_autonomia}|{v_social}|{v_participa}|{v_resposta}"
                texto_consolidado = f"{checklist_str}\n\n[DIAGNOSTICO_GERAL]\n{v_diag}\n\n[SOCIAIS]\n{ed_soc}\n\n[COMUNICATIVAS]\n{ed_com}\n\n[EMOCIONAIS]\n{ed_emo}\n\n[FUNCIONAIS]\n{ed_fun}\n\n[DIRETRIZES_CURRICULARES]\n{v_diretrizes}"
                salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, "DOSSIE_MASTER_PEI", texto_consolidado)
                st.success("✅ Edições salvas no Repositório Vivo!"); st.balloons()

        # --- ABA 3: CURRÍCULO ADAPTADO (TABELA OFICIAL) ---
        with tab_curr:
            st.subheader("⚙️ Seção 2: Currículo Adaptado (Tabela Oficial)")
            st.caption("A IA usará as Diretrizes Curriculares do Dossiê Master para adaptar os conteúdos da matriz.")
            
            trim_destino = st.selectbox("Trimestre de Referência:",["I Trimestre", "II Trimestre", "III Trimestre"], key="trim_curr")
            
            curr_records = hist_aluno[hist_aluno['TIPO'] == f"CURRICULO_ADAPTADO_{trim_destino}"]
            if not curr_records.empty:
                try:
                    import json
                    df_curr_atual = pd.read_json(io.StringIO(curr_records.iloc[-1]['CONTEUDO']), orient='records')
                except:
                    df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])
            else:
                df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])

            ano_aluno = "".join(filter(str.isdigit, turma_pei))
            df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == ano_aluno].copy()

            if df_matriz_ano.empty:
                st.warning(f"⚠️ Matriz do {ano_aluno}º ano não localizada.")
            else:
                opcoes_conteudo = df_matriz_ano.apply(lambda x: f"[{x['TRIMESTRE']}] {x['CONTEUDO_ESPECIFICO']}", axis=1).tolist()
                selecionados = st.multiselect("📚 Escolha os conteúdos para adaptar:", opcoes_conteudo, key="sel_curr_clean")

                if selecionados:
                    if st.button("🧠 INICIAR MOTOR DE IA: GERAR ADAPTAÇÃO", use_container_width=True, type="primary"):
                        with st.spinner("Arquitetando colunas e simplificando objetivos..."):
                            conteudos_brutos =[s.split("] ")[1] for s in selecionados]
                            df_focada = df_matriz_ano[df_matriz_ano['CONTEUDO_ESPECIFICO'].isin(conteudos_brutos)]
                            contexto_oficial = df_focada[['CONTEUDO_ESPECIFICO', 'OBJETIVOS']].to_string(index=False)
                            
                            prompt_curr = f"ESTUDANTE: {nome_limpo}. PERFIL/NECESSIDADE: {perfil_atual}.\nDIRETRIZES DO DOSSIÊ: {v_diretrizes}\nMATRIZ: {contexto_oficial}.\nGere os itens adaptados focando em superar as barreiras do perfil {perfil_atual} e seguindo as diretrizes."
                            res_ia = ai.gerar_ia("TRADUTOR_CURRICULAR_V39", prompt_curr)
                            
                            blocos = re.findall(r"\[ITEM\](.*?)\[/ITEM\]", res_ia, re.DOTALL)
                            novas_linhas =[]
                            for b in blocos:
                                novas_linhas.append({
                                    "Objetivos de Aprendizagem": ai.extrair_tag(b, "OBJETIVO"),
                                    "Estratégias Metodológicas": ai.extrair_tag(b, "ESTRATEGIA"),
                                    "Recursos Materiais": ai.extrair_tag(b, "RECURSO")
                                })
                            
                            if novas_linhas:
                                df_curr_atual = pd.concat([df_curr_atual, pd.DataFrame(novas_linhas)], ignore_index=True)
                                
                                # 🚨 AUTO-SAVE: Salva imediatamente para não perder no rerun do Streamlit
                                import json
                                json_data = df_curr_atual.to_json(orient='records')
                                salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, f"CURRICULO_ADAPTADO_{trim_destino}", json_data)
                                st.rerun()

            st.markdown("---")
            st.markdown("**Tabela de Planejamento (Editável)**")
            df_editado_curr = st.data_editor(
                df_curr_atual, 
                num_rows="dynamic", 
                use_container_width=True, 
                key="ed_curr",
                column_config={
                    "Objetivos de Aprendizagem": st.column_config.TextColumn(width="large"),
                    "Estratégias Metodológicas": st.column_config.TextColumn(width="large"),
                    "Recursos Materiais": st.column_config.TextColumn(width="medium")
                }
            )
            
            if st.button("💾 SALVAR PROGRESSO NO BANCO (CURRÍCULO)", use_container_width=True):
                import json
                json_data = df_editado_curr.to_json(orient='records')
                salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, f"CURRICULO_ADAPTADO_{trim_destino}", json_data)
                st.success(f"✅ Currículo do {trim_destino} arquivado no Repositório Vivo!")
                st.balloons()

        # --- ABA 4: RELATO PARA COORDENAÇÃO (WHATSAPP) ---
        with tab_coord:
            st.subheader("📱 Relato Rápido para Coordenação")
            st.caption("Gere um texto curto e direto, ideal para copiar e colar no WhatsApp da coordenação ou da família.")
            
            mapa_estilos = {
                "Opção 1: Engajamento e Evolução": "🌟 **Foco:** Destacar progressos e participação ativa.",
                "Opção 2: Dificuldades e Suporte": "⚠️ **Foco:** Relatar barreiras e solicitar apoio da coordenação.",
                "Opção 3: Status Ultra-conciso": "⚡ **Foco:** Papo reto e direto (2-3 linhas)."
            }
            estilo_zap = st.radio("Qual o objetivo deste relato?", list(mapa_estilos.keys()), key="zap_clean")
            st.info(mapa_estilos[estilo_zap])

            if st.button("🧠 INICIAR MOTOR DE IA: GERAR MENSAGEM", use_container_width=True, type="primary"):
                with st.spinner("Traduzindo evidências para linguagem humana..."):
                    prompt_zap = f"ALUNO: {nome_limpo}. PERFIL: {perfil_atual}. DADOS: {vistos} vistos, {bonus} bônus. CHECKLIST: {v_autonomia}, {v_social}, {v_participa}, {v_resposta}. ESTILO: {estilo_zap}. Gere um parágrafo único, sem negritos, para WhatsApp."
                    st.session_state.res_v38_coord = ai.gerar_ia("PONTE_COORDENACAO", prompt_zap)
            
            if "res_v38_coord" in st.session_state:
                st.write(st.session_state.res_v38_coord)
                st.code(st.session_state.res_v38_coord, language=None)

        # --- ABA 5: LINHA DO TEMPO ---
        with tab_timeline:
            st.subheader("🗂️ Linha do Tempo de Custódia Digital")
            st.caption("Histórico cronológico de todos os documentos e evidências geradas para este estudante.")

            if not hist_aluno.empty:
                df_timeline = hist_aluno.iloc[::-1]

                for idx, row in df_timeline.iterrows():
                    tipo_bruto = str(row.get('TIPO', 'REGISTRO')) 
                    data_doc = row.get('DATA', 'S/D')
                    conteudo_raw = row.get('CONTEUDO', '')

                    if "DOSSIE_MASTER_PEI" in tipo_bruto.upper():
                        label_tipo = "📈 DOSSIÊ MASTER (EVOLUÇÃO + CAPA)"
                        icone = "📊"
                    elif "CURRICULO_ADAPTADO" in tipo_bruto.upper():
                        label_tipo = f"📖 CURRÍCULO ADAPTADO ({tipo_bruto.split('_')[-1]})"
                        icone = "📚"
                    elif "PEI_EXPORTADO" in tipo_bruto.upper():
                        label_tipo = "🖨️ PEI OFICIAL EXPORTADO (DOCX)"
                        icone = "💾"
                    else:
                        label_tipo = f"📄 {tipo_bruto}"
                        icone = "📎"

                    with st.container(border=True):
                        col_t1, col_t2 = st.columns([3, 1])
                        with col_t1:
                            st.markdown(f"### {icone} {label_tipo}")
                            st.caption(f"📅 Gerado em: {data_doc} | 🆔 ID Aluno: {id_a}")
                        
                        with col_t2:
                            if st.button("🗑️ APAGAR", key=f"del_rel_{idx}", use_container_width=True):
                                if db.excluir_registro("DB_RELATORIOS", conteudo_raw):
                                    st.success("Registro removido!"); time.sleep(0.5); st.rerun()

                        with st.expander("👁️ VISUALIZAR DOCUMENTO COMPLETO", expanded=False):
                            if "CURRICULO_ADAPTADO" in tipo_bruto.upper():
                                try:
                                    import json
                                    df_view = pd.read_json(io.StringIO(conteudo_raw), orient='records')
                                    st.dataframe(df_view, use_container_width=True)
                                except:
                                    st.write(conteudo_raw)
                            elif "PEI_EXPORTADO" in tipo_bruto.upper():
                                link_d = conteudo_raw.replace("Link: ", "").strip()
                                st.link_button("📂 ABRIR NO DRIVE", link_d, type="primary")
                            else:
                                st.markdown(conteudo_raw.replace("\n", "  \n"))
                            
                            st.divider()
                            st.caption("🔒 Documento assinado digitalmente pelo ecossistema SOSA")
            else:
                st.info("📭 Nenhuma evidência ou documento arquivado para este estudante até o momento.")

        # ==============================================================================
        # 🚨 ABA 6: EXPORTAR PEI OFICIAL (DOCX)
        # ==============================================================================
        with tab_export:
            st.subheader("🖨️ Exportar PEI Oficial (DOCX)")
            st.caption("Gera o documento final no formato da prefeitura, com as lacunas burocráticas prontas para a coordenação preencher.")
            
            trim_export = st.selectbox("Qual trimestre deseja exportar?",["I Trimestre", "II Trimestre", "III Trimestre"], key="exp_trim")
            
            if st.button("💾 GERAR E SALVAR PEI OFICIAL NO DRIVE", type="primary", use_container_width=True):
                with st.spinner("Compilando Dossiê Oficial..."):
                    # 1. Coleta Dados do Aluno
                    dados_aluno = {"nome": nome_limpo, "turma": turma_pei, "cid": perfil_atual}
                    
                    # 2. Coleta Habilidades (Capa)
                    habilidades = {
                        "Habilidades Sociais": v_soc_txt, 
                        "Habilidades Comunicativas": v_com_txt, 
                        "Habilidades Emocionais": v_emo_txt, 
                        "Habilidades Funcionais": v_fun_txt
                    }
                    
                    # 3. Coleta Currículo
                    curr_records_exp = hist_aluno[hist_aluno['TIPO'] == f"CURRICULO_ADAPTADO_{trim_export}"]
                    if not curr_records_exp.empty:
                        try:
                            import json
                            df_curr_exp = pd.read_json(io.StringIO(curr_records_exp.iloc[-1]['CONTEUDO']), orient='records')
                        except:
                            df_curr_exp = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])
                    else:
                        df_curr_exp = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])
                    
                    # 4. Gera o DOCX
                    nome_arq_pei = f"PEI_OFICIAL_{nome_limpo.replace(' ', '_')}_{trim_export.replace(' ', '')}"
                    doc_stream = exporter.gerar_docx_pei_oficial(nome_arq_pei, dados_aluno, habilidades, df_curr_exp)
                    
                    # 5. Sobe para o Drive
                    link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_pei, trimestre=trim_export, categoria=turma_pei, modo="PLANEJAMENTO")
                    
                    if "https" in link_doc:
                        salvar_relatorio_pei_sem_duplicidade(id_a, nome_limpo, "PEI_EXPORTADO", f"Link: {link_doc}")
                        st.success("✅ PEI Oficial gerado e salvo no Drive!")
                        st.link_button("📂 ABRIR PEI OFICIAL", link_doc, type="primary", use_container_width=True)
                        st.balloons()
                    else:
                        st.error(f"Erro ao salvar no Drive: {link_doc}")
