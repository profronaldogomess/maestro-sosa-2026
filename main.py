import io
import time
import os
import re
import random
from datetime import date, datetime, timedelta, timezone
import streamlit as st
import pandas as pd
import plotly.express as px
import database as db
import ai_engine as ai
import utils as util
import exporter

# --- CONFIGURAÇÃO DE ALTA PERFORMANCE (BRANDING EXCLUSIVO) ---
st.set_page_config(
    page_title="Ronaldo Gomes", 
    layout="wide", 
    page_icon="💻",
    initial_sidebar_state="expanded"
)

# --- SISTEMA DE BLINDAGEM E PERSISTÊNCIA (6 HORAS) ---
def check_password():
    """Gerencia o acesso com card Glassmorphism executivo e persistência de 6h."""
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
    if "login_timestamp" not in st.session_state:
        st.session_state["login_timestamp"] = None

    if st.session_state["password_correct"]:
        tempo_decorrido = time.time() - st.session_state["login_timestamp"]
        if tempo_decorrido < 21600: # 6 horas de sessão persistente
            return True
        else:
            st.session_state["password_correct"] = False
            st.warning("Sessão expirada. Por favor, acesse novamente.")

    # INTERFACE DE LOGIN EXECUTIVA (Glassmorphism Bento Card)
    _, col_login, _ = st.columns([1, 1.8, 1]) 
    
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
            with col_l2:
                try: st.image("logo.png", width=130) 
                except: st.markdown("<h2 style='text-align: center; margin: 0;'>Ronaldo Gomes</h2>", unsafe_allow_html=True)
            
            st.markdown("<h3 style='text-align: center; margin-top: 10px; margin-bottom: 2px; font-weight: 800;'>Portal de Soberania Docente</h3>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 13px; margin-bottom: 15px;'>Gestão Pedagógica 360° & Regência de Alta Performance</p>", unsafe_allow_html=True)
            
            st.pills("Perfil de Acesso:", ["Prof. Ronaldo Gomes"], default="Prof. Ronaldo Gomes", key="pills_login_profile")
            
            with st.form("login_portal_form"):
                input_password = st.text_input("Chave de Segurança:", type="password", placeholder="Digite sua chave de acesso...")
                st.checkbox("Manter sessão ativa por 6 horas", value=True, disabled=True)
                
                btn_entrar = st.form_submit_button("Acessar Painel", use_container_width=True, type="primary")
                
                if btn_entrar:
                    if input_password == "2496":
                        st.session_state["password_correct"] = True
                        st.session_state["login_timestamp"] = time.time()
                        st.toast("Acesso autorizado com sucesso!", icon="✅")
                        time.sleep(0.4)
                        st.rerun()
                    else:
                        st.error("Chave de segurança incorreta.")
            
            st.caption("SOSA Bridge V45.9 • Servidor Online • Criptografia Ativa • Itabuna/BA")
    
    return False

if not check_password():
    st.stop()

# --- CARREGAMENTO DE DADOS GLOBAL SOBERANO ---
wb, (df_alunos, df_curriculo, df_materiais, df_planos, df_aulas, df_notas, df_diario, df_turmas, df_relatorios, df_horarios, df_registro_aulas, df_diagnosticos) = db.carregar_tudo()

# --- MOTOR DE NAVEGAÇÃO ONE-CLICK (GLOBAL) ---
if "menu_atual" not in st.session_state:
    st.session_state.menu_atual = "📅 Planejamento (Ponto ID)"

def navegar_para(destino):
    st.session_state.menu_atual = destino
    st.rerun()

def atualizar_menu():
    st.session_state.menu_atual = st.session_state._menu_radio

# Centraliza helpers do utils globalmente
preparar_para_leitura = util.preparar_para_leitura
extrair_valor_real_prova = util.extrair_valor_real_prova

# --- ESTILIZAÇÃO EXECUTIVA & DESIGN SYSTEM GLASSMORPHISM ---
BRAND_BLUE = "#2962FF"
BRAND_NAVY = "#000B1A"

if "tema_sistema" not in st.session_state:
    st.session_state.tema_sistema = "Dark"

if st.session_state.tema_sistema == "Dark":
    cor_fundo, cor_texto, cor_sidebar, cor_card = BRAND_NAVY, "#FFFFFF", "#001226", "#001E3C"
    cor_borda = "#003366"
else:
    cor_fundo, cor_texto, cor_sidebar, cor_card = "#F8FAFC", "#0F172A", "#FFFFFF", "#FFFFFF"
    cor_borda = "#E2E8F0"

st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
        * {{ font-family: 'Plus Jakarta Sans', sans-serif; }}
        .stApp {{ background-color: {cor_fundo} !important; color: {cor_texto} !important; }}
        [data-testid="stSidebar"] {{ background-color: {cor_sidebar} !important; border-right: 1px solid {cor_borda}; }}
        div[data-testid="stMetric"] {{ background: {cor_card} !important; border: 1px solid {cor_borda} !important; border-radius: 12px !important; padding: 14px !important; box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important; }}
        .stButton button {{ border-radius: 10px !important; font-weight: 600 !important; transition: all 0.2s ease; }}
        .stButton button:hover {{ transform: translateY(-1px); }}
        div[data-testid="stVerticalBlock"] > div[style*="border"] {{ border-radius: 14px !important; box-shadow: 0 2px 8px rgba(0,0,0,0.02) !important; background: {cor_card}; border-color: {cor_borda} !important; }}
    </style>
""", unsafe_allow_html=True)

# --- SIDEBAR: IDENTIDADE, RELÓGIO & NAVEGAÇÃO ESTRATÉGICA ---
with st.sidebar:
    try: st.logo("logo.png", icon_image="logo.png")
    except: pass
    
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        try: st.image("logo.png", width=95)
        except: pass
    
    st.markdown("<h3 style='text-align: center; font-size: 18px; margin-top: 4px; margin-bottom: 0px; font-weight: 800;'>Ronaldo Gomes</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center; font-size: 11px; color: {BRAND_BLUE}; font-weight: 700; letter-spacing: 0.5px;'>SOBERANIA PEDAGÓGICA</p>", unsafe_allow_html=True)

    tema_sel_pills = st.segmented_control("Aparência:", ["Dark", "Light"], default=st.session_state.tema_sistema, key="seg_tema_sidebar")
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
        st.markdown(f"<div style='text-align: center; font-weight: 700; font-size: 12px; color: {BRAND_BLUE};'>{hora_atual} • {data_atual}</div>", unsafe_allow_html=True)
        
        feriado_hoje = util.verificar_feriado_itabuna(data_atual_dt)
        if feriado_hoje:
            st.caption(f"Feriado: {feriado_hoje.upper()}")
        else:
            dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            nome_dia = dias_semana[data_atual_dt.weekday()]
            st.caption(f"{nome_dia}-feira • Dia Letivo")

    # RADAR EXECUTIVO DE SOBERANIA
    with st.expander("Radar de Notificações", expanded=False):
        try:
            planos_pendentes = len(df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)]) if not df_planos.empty else 0
            if planos_pendentes > 0:
                st.warning(f"{planos_pendentes} Plano(s) pendente(s) no Hub")
            else: st.success("Planejamento em dia")
        except: pass

        try:
            if not df_notas.empty:
                uti_count = len(df_notas[df_notas['MEDIA_FINAL'].apply(util.sosa_to_float) < 6.0])
                if uti_count > 0:
                    st.error(f"{uti_count} Estudante(s) abaixo da média")
                else: st.success("Nenhum estudante em risco")
        except: pass

    st.markdown("---")

    # NAVEGAÇÃO EM 3 MÓDULOS ESTRATÉGICOS
    st.markdown("<p style='font-size: 11px; color: gray; font-weight: 700; letter-spacing: 0.5px;'>ÁREA DE ATUAÇÃO:</p>", unsafe_allow_html=True)
    
    modulos_map = {
        "📅 Planejamento (Ponto ID)": "Aulas",
        "🧪 Criador de Aulas": "Aulas",
        "📚 Base de Conhecimento": "Aulas",
        
        "📝 Central de Avaliações": "Provas",
        "📸 Scanner de Gabaritos": "Provas",
        "📊 Painel de Notas & Vistos": "Provas",
        "📈 Boletim Anual & Conselho": "Provas",
        
        "📝 Diário de Bordo Rápido": "Regência",
        "👤 Biografia do Estudante": "Regência",
        "👥 Gestão da Turma": "Regência",
        "♿ Relatórios PEI / Perfil IA": "Regência"
    }
    
    modulo_default = modulos_map.get(st.session_state.menu_atual, "Aulas")
    
    modulo_ativo = st.segmented_control(
        "Módulo:", 
        ["Aulas", "Provas", "Regência"], 
        default=modulo_default,
        key="seg_modulo_sidebar"
    )

    paginas_por_modulo = {
        "Aulas": [
            "📅 Planejamento (Ponto ID)",
            "🧪 Criador de Aulas",
            "📚 Base de Conhecimento"
        ],
        "Provas": [
            "📝 Central de Avaliações",
            "📸 Scanner de Gabaritos",
            "📊 Painel de Notas & Vistos",
            "📈 Boletim Anual & Conselho"
        ],
        "Regência": [
            "📝 Diário de Bordo Rápido",
            "👤 Biografia do Estudante",
            "👥 Gestão da Turma",
            "♿ Relatórios PEI / Perfil IA"
        ]
    }

    paginas_disponiveis = paginas_por_modulo.get(modulo_ativo, paginas_por_modulo["Aulas"])
    idx_pag = paginas_disponiveis.index(st.session_state.menu_atual) if st.session_state.menu_atual in paginas_disponiveis else 0
    
    pagina_selecionada = st.pills(
        "Painel:", 
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
    
    with st.popover("Conta & Sessão", use_container_width=True):
        st.caption("👑 **Prof. Ronaldo Gomes**")
        st.caption("Licença Ativa • SOSA 2026")
        st.markdown("---")
        
        c_pop1, c_pop2 = st.columns(2)
        if c_pop1.button("Sincronizar", use_container_width=True, key="btn_pop_sync"):
            st.cache_data.clear()
            st.rerun()
            
        if c_pop2.button("Sair", use_container_width=True, key="btn_pop_sair"):
            st.session_state["password_correct"] = False
            st.session_state["login_timestamp"] = None
            st.rerun()

    st.caption("Itabuna/BA • © 2026")

# --- FUNÇÕES AUXILIARES DE PROCESSAMENTO ---
def prensa_hidraulica_texto(texto, label):
    limpo = texto.replace(label, "").replace(label.upper(), "").replace(label.lower(), "")
    if limpo.startswith(":") or limpo.startswith(" :"):
        limpo = limpo.split(":", 1)[-1]
    return limpo.strip()

def exibir_material_estruturado(texto_raw, key_prefix, dados_plano=None, info_aula=None):
    if info_aula is None: info_aula = {}
    
    f_aula = info_aula.get("aula", "Aula Geral")
    f_ano = info_aula.get("ano", "6")
    f_semana = info_aula.get("semana", "Semana Geral")
    f_trimestre = info_aula.get("trimestre", "I Trimestre")
    f_categoria = f"{f_ano}ano"

    if dados_plano:
        ed_met = ai.extrair_tag(texto_raw, "METODOLOGIA")
        ed_obj = ai.extrair_tag(texto_raw, "OBJETIVOS_ENSINO")
        ed_ava = ai.extrair_tag(texto_raw, "AVALIACAO")
        ed_pei_plan = ai.extrair_tag(texto_raw, "ADAPTACAO_PEI")
        
        t1, t2, t3, t4, t_exp = st.tabs(["Metodologia", "Objetivos", "Avaliação", "Acessibilidade PEI", "Sincronização"])
        
        with t1: st.text_area("Roteiro:", ed_met, height=360, key=f"{key_prefix}_met")
        with t2: st.text_area("Objetivos:", ed_obj, height=360, key=f"{key_prefix}_obj")
        with t3: st.text_area("Avaliação:", ed_ava, height=180, key=f"{key_prefix}_ava")
        with t4: st.text_area("Acessibilidade:", ed_pei_plan, height=260, key=f"{key_prefix}_pei_plan")
        
        modo_sync = "PLANEJAMENTO"
        nome_base = f"PLANO_{f_ano}ANO_{f_semana.replace(' ', '')}"
        ed_prof_para_banco = texto_raw 

    else:
        ed_prof = ai.extrair_tag(texto_raw, "PROFESSOR")
        ed_alu = ai.extrair_tag(texto_raw, "ALUNO")
        
        t1, t2, t3, t4, t5, t_exp = st.tabs(["Guia Docente", "Folha do Estudante", "Gabarito", "Ilustrações", "Acessibilidade PEI", "Sincronização"])
        
        with t1: st.text_area("Guia Docente:", ed_prof, height=360, key=f"{key_prefix}_lousa")
        with t2: st.text_area("Folha do Estudante:", ed_alu, height=360, key=f"{key_prefix}_folha")
        with t3: st.text_area("Gabarito:", ai.extrair_tag(texto_raw, "GABARITO"), height=180, key=f"{key_prefix}_gab")
        with t4: st.text_area("Ilustrações:", ai.extrair_tag(texto_raw, "IMAGENS"), height=140, key=f"{key_prefix}_img")
        
        with t5:
            st.subheader("Adaptação Inclusiva (PEI)")
            if "lab_pei" not in st.session_state:
                if st.button("Gerar Adaptação PEI", use_container_width=True, key=f"{key_prefix}_gen_pei"):
                    st.session_state.lab_pei = ai.gerar_ia("ARQUITETO_PEI_V24", f"ADAPTE: {ed_alu}")
                    st.rerun()
            else:
                st.session_state.lab_pei = st.text_area("PEI:", st.session_state.lab_pei, height=360, key=f"{key_prefix}_pei_area")
        
        modo_sync = "AULA"
        nome_base = f"AULA_{f_aula.replace(' ','')}_{f_ano}ANO_{datetime.now().strftime('%d%m')}"
        ed_prof_para_banco = ed_prof

    with t_exp:
        st.subheader("Custódia & Sincronização Google Drive")
        
        if modo_sync == "PLANEJAMENTO":
            nome_base = f"PLANO_{f_ano}ANO_{f_semana.replace(' ', '')}"
        else:
            nome_base = f"AULA_{f_aula.replace(' ','')}_{f_ano}ANO_{datetime.now().strftime('%d%m')}"

        if st.button("Sincronizar no Google Drive", use_container_width=True, type="primary", key=f"{key_prefix}_btn_sync"):
            with st.status("Iniciando sincronização e custódia...", expanded=True) as status:
                status.write("Verificando versões anteriores...")
                if modo_sync == "PLANEJAMENTO":
                    filtro = df_planos[(df_planos['SEMANA'] == f_semana) & (df_planos['ANO'] == f"{f_ano}º")]
                    for _, row_antiga in filtro.iterrows():
                        db.excluir_registro_com_drive("DB_PLANOS", row_antiga['PLANO_TEXTO'])
                else:
                    filtro = df_aulas[(df_aulas['SEMANA_REF'] == f_semana) & (df_aulas['TIPO_MATERIAL'].str.contains(f_aula))]
                    for _, row_antiga in filtro.iterrows():
                        db.excluir_registro_com_drive("DB_AULAS_PRONTAS", row_antiga['CONTEUDO'])

                if modo_sync == "PLANEJAMENTO":
                    doc_plano = exporter.gerar_docx_plano_pedagogico_ELITE(nome_base, dados_plano, {"ano": f"{f_ano}º", "semana": f_semana, "trimestre": f_trimestre})
                    status.write("Enviando plano para o Drive...")
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
                            status.update(label="Plano sincronizado com sucesso!", state="complete")
                            st.balloons()
                    else:
                        status.update(label="Falha no envio para o Drive.", state="error")
                        st.error(link)

                else:
                    status.write("Compilando materiais oficiais...")
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_base, ed_alu, {"ano": f"{f_ano}º", "trimestre": f_trimestre})
                    doc_prof = exporter.gerar_docx_professor_v25(nome_base, ed_prof, {"ano": f"{f_ano}º", "semana": f_semana, "trimestre": f_trimestre})
                    
                    status.write("Enviando Folha do Estudante...")
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_base}_ALUNO", trimestre=f_trimestre, categoria=f_categoria, semana=f_semana, modo="AULA")
                    
                    status.write("Enviando Guia Docente...")
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_base}_PROF", trimestre=f_trimestre, categoria=f_categoria, semana=f_semana, modo="AULA")
                    
                    link_pei = "N/A"
                    if "lab_pei" in st.session_state:
                        status.write("Enviando material adaptado PEI...")
                        doc_pei = exporter.gerar_docx_pei_v25(f"{nome_base}_PEI", st.session_state.lab_pei, {"ano": f"{f_ano}º", "trimestre": f_trimestre})
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_base}_PEI", trimestre=f_trimestre, categoria=f_categoria, semana=f_semana, modo="AULA")

                    if "https" in str(link_alu) and "https" in str(link_prof):
                        conteudo_banco = f"[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI({link_pei})"
                        
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), f_semana, f"{f_aula}", conteudo_banco, f"{f_ano}º", link_alu
                        ])
                        status.update(label="Material sincronizado com sucesso!", state="complete")
                        st.balloons()
                    else:
                        status.update(label="Erro no upload do material.", state="error")
                        st.error("Falha no envio dos arquivos.")
                       







# ==============================================================================
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - V2026.PRO_EXECUTIVE
# (AULAS EXPOSITIVAS OBJETIVAS, FATIADOR DE PDF VISUAL, UNIDADES TEMÁTICAS BNCC)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("Planejamento Pedagógico (Ponto ID)")
    st.caption("Arquitetura semanal estruturada: alinhamento curricular BNCC, aulas expositivas (Início, Meio, Fim) e ancoragem em livros didáticos.")
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
        "Novo Planejamento", "Hub de Produção", "Acervo de Planos", "Inteligência Curricular & Conciliação"
    ])
    
    # ==============================================================================
    # ABA 1: NOVO PLANEJAMENTO (PONTO ID)
    # ==============================================================================
    with tab_gerar:
        with st.container(border=True):
            st.markdown("#### 1. Parâmetros da Semana & Carga Horária")
            
            c1, c2, c3 = st.columns([1, 2, 2])
            ano_p = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_sel_{v}")
            ano_str_busca = f"{ano_p}º"

            todas_semanas_geral = [s for s in util.gerar_semanas() if "Jornada" not in s]
            total_semanas_ano = len(todas_semanas_geral)
            
            planos_ano_atuais = df_planos[df_planos['ANO'] == ano_str_busca]['SEMANA'].tolist() if not df_planos.empty and 'ANO' in df_planos.columns and 'SEMANA' in df_planos.columns else []
            planos_concluidos_cnt = len(set([s.split(" (")[0] for s in planos_ano_atuais]))
            perc_safra_planos = min(100, int((planos_concluidos_cnt / max(total_semanas_ano, 1)) * 100))

            todas_semanas = util.gerar_semanas()
            sobrescrever_planos = st.toggle("Exibir semanas já concluídas (Permitir Edição)", value=False, key=f"tog_sobrescrever_{v}")
            
            if not df_planos.empty and 'ANO' in df_planos.columns and 'SEMANA' in df_planos.columns:
                semanas_planejadas = df_planos[df_planos['ANO'] == ano_str_busca]['SEMANA'].tolist()
            else:
                semanas_planejadas = []
                
            if sobrescrever_planos:
                semanas_disponiveis = [s for s in todas_semanas if "Jornada" not in s]
            else:
                semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_planejadas and "Jornada" not in s]

            if not semanas_disponiveis:
                st.success(f"Todas as semanas do {ano_p}º Ano já foram planejadas!")
                st.info("Ative a opção 'Permitir Edição' acima caso deseje reestruturar alguma semana.")
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
                st.info(f"Status no Calendário Escolar: **{status_especial_sem}** " + (f"(*{motivo_especial_sem}*)" if motivo_especial_sem else ""))

            tipo_semana = c3.selectbox("Natureza Pedagógica:", [
                "Aula Regular de Safra", 
                "Recesso Escolar / Feriado",
                "Aplicação de Avaliação", 
                "Revisão & Recomposição", 
                "Semana de Provas Globais",
                "Devolutiva & Recuperação",
                "Trabalho Investigativo", 
                "Sonda de Proficiência",
                "Dinâmica Aberta / Evento Institucional"
            ], key=f"gate_tipo_{v}")
            
            st.markdown("---")
            
            c_sf1, c_sf2 = st.columns([3, 1])
            c_sf1.progress(perc_safra_planos / 100.0, text=f"**Safra Pedagógica ({ano_p}º Ano): {planos_concluidos_cnt} de {total_semanas_ano} Semanas Planejadas** ({perc_safra_planos}%)")
            c_sf2.metric("Semanas Restantes", total_semanas_ano - planos_concluidos_cnt)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            carga_horaria = st.pills(
                "Carga Horária Semanal:", 
                ["1 Aula (Carga Reduzida)", "2 Aulas (Semana Padrão)", "3 Aulas (+ Sábado Letivo)"], 
                default="2 Aulas (Semana Padrão)",
                key=f"carga_pills_{v}"
            )

        # BAIXA EM RECESSO / FERIADO
        if "Recesso" in tipo_semana or "Férias" in tipo_semana or "Feriado" in tipo_semana:
            with st.container(border=True):
                st.markdown("#### Registro de Recesso / Feriado")
                st.caption(f"A semana **{sem_limpa}** será arquivada no planejamento sem pendências no Criador de Aulas.")
                
                motivo_recesso_txt = st.text_input("Descrição do Evento:", value="Recesso Escolar / Feriado Institucional", key=f"obs_rec_ponto_{v}")
                
                if st.button("Registrar Recesso Escolar", type="primary", use_container_width=True, key=f"btn_baixa_rec_{v}"):
                    with st.spinner("Registrando recesso no planejamento..."):
                        db.dar_baixa_plano_evento(
                            semana=sem_limpa, 
                            ano=ano_str_busca, 
                            motivo_ou_status=motivo_recesso_txt
                        )
                        st.success(f"Semana {sem_limpa} registrada como Recesso com sucesso!")
                        time.sleep(0.8); st.rerun()

        elif tipo_semana in ["Aplicação de Avaliação", "Semana de Provas Globais", "Sonda de Proficiência", "Devolutiva & Recuperação"]:
            with st.container(border=True):
                st.markdown("#### 2. Vínculo de Avaliação do Acervo & Descritores")
                st.caption("Selecione o instrumento avaliativo para extração automática de habilidades BNCC e descritores SAEB.")

                df_ativos_ano = df_aulas[df_aulas['ANO'].astype(str).str.contains(str(ano_p))] if not df_aulas.empty and 'ANO' in df_aulas.columns else pd.DataFrame()
                
                opcoes_ativos = []
                if not df_ativos_ano.empty and 'SEMANA_REF' in df_ativos_ano.columns and 'TIPO_MATERIAL' in df_ativos_ano.columns:
                    mask_ex = (df_ativos_ano['SEMANA_REF'] == "AVALIAÇÃO") | (df_ativos_ano['TIPO_MATERIAL'].str.contains("PROVA|TESTE|SONDA|AVALIAÇÃO|AVALIACAO|EXAME", case=False, na=False))
                    opcoes_ativos = sorted(df_ativos_ano[mask_ex]['TIPO_MATERIAL'].unique().tolist())
                
                c_ex1, c_ex2 = st.columns([2, 1])
                exame_selecionado = c_ex1.selectbox("Selecione o Instrumento no Acervo:", [""] + opcoes_ativos, key=f"sel_mat_vinculo_{v}")
                pincamento_exame_manual = c_ex2.text_input("ou Descreva a Avaliação:", placeholder="Ex: Avaliação Bimestral de Números Decimais", key=f"inp_exame_manual_{v}")

                habilidades_extraidas = ""
                conteudos_extraidos = ""
                texto_prova_completo = ""

                if exame_selecionado and not df_ativos_ano.empty and 'TIPO_MATERIAL' in df_ativos_ano.columns:
                    match_ex = df_ativos_ano[df_ativos_ano['TIPO_MATERIAL'] == exame_selecionado]
                    if not match_ex.empty:
                        texto_prova_completo = str(match_ex.iloc[0].get('CONTEUDO', ''))
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
                    conteudos_extraidos = pincamento_exame_manual if pincamento_exame_manual.strip() else (exame_selecionado if exame_selecionado else f"Aplicação de Avaliação de Matemática - {sem_limpa}")

                if not habilidades_extraidas:
                    habilidades_extraidas = f"EF0{ano_p}MA01 - Habilidades curriculares do {ano_p}º Ano."

                diretriz_logistica = st.text_area(
                    "Diretrizes e Roteiro da Aplicação (Editável):",
                    value=(
                        f"INÍCIO (10 min): Acolhimento dos estudantes, ambientação e leitura orientada das instruções do exame.\n"
                        f"MEIO (35 min): Aplicação supervisionada da avaliação ({exame_selecionado if exame_selecionado else conteudos_extraidos}). Mediação individualizada aos estudantes com necessidades educacionais específicas (PEI).\n"
                        f"FIM (5 min): Recolhimento dos cadernos de respostas para leitura óptica no Scanner CIR."
                    ),
                    height=130,
                    key=f"txt_rot_exec_{v}_{hash(exame_selecionado or pincamento_exame_manual)}"
                )

                c_save_ex1, c_save_ex2 = st.columns(2)

                if c_save_ex1.button("Estruturar Plano da Avaliação", type="primary", use_container_width=True, key=f"btn_gen_exame_plan_{v}"):
                    nome_exame_tit = exame_selecionado if exame_selecionado else conteudos_extraidos
                    
                    if "1 Aula" in carga_horaria:
                        roteiro_a1 = diretriz_logistica
                        roteiro_a2 = "N/A (Carga horária de 1 Aula)"
                        roteiro_sab = "N/A"
                    elif "2 Aulas" in carga_horaria:
                        roteiro_a1 = f"AULA 01 - APLICAÇÃO DA AVALIAÇÃO:\n{diretriz_logistica}"
                        roteiro_a2 = f"AULA 02 - SEGUNDA CHAMADA E DEVOLUTIVA:\nINÍCIO: Acolhimento e atendimento a ausentes.\nMEIO: Aplicação de 2ª chamada e correção comentada das questões com menor taxa de acerto.\nFIM: Síntese dos resultados."
                        roteiro_sab = "N/A"
                    else:
                        roteiro_a1 = f"AULA 01 - APLICAÇÃO DA AVALIAÇÃO:\n{diretriz_logistica}"
                        roteiro_a2 = "AULA 02 - CONTINUIDADE / SEGUNDA CHAMADA"
                        roteiro_sab = "SÁBADO LETIVO - RECOMPOSIÇÃO"

                    plano_formatado_exame = (
                        f"[HABILIDADE_BNCC] {habilidades_extraidas}\n"
                        f"[COMPETENCIAS_FOCO] Competência Específica 2 (Raciocínio Lógico) e 6 (Enfrentar Situações-Problema)\n"
                        f"[OBJETO_CONHECIMENTO] {tipo_semana.upper()} - {nome_exame_tit}\n"
                        f"[CONTEUDOS_ESPECIFICOS] {conteudos_extraidos}\n"
                        f"[OBJETIVOS_ENSINO] Mensurar o nível de consolidação dos objetos de conhecimento do {ano_p}º Ano.\n"
                        f"[JUSTIFICATIVA_PEDAGOGICA] Verificação de aprendizagem regimental do {trim_atual}.\n"
                        f"[AULA_1] {roteiro_a1}\n"
                        f"[AULA_2] {roteiro_a2}\n"
                        f"[SABADO_LETIVO] {roteiro_sab}\n"
                        f"[AVALIACAO_DE_MERITO] Correção automatizada via Scanner CIR com perícia de distratores.\n"
                        f"[ESTRATEGIA_DUA_PEI] Aplicação de cadernos adaptados (PEI N1, N2 e N3) com tempo ampliado."
                    )

                    st.session_state.p_temp = plano_formatado_exame
                    st.session_state.p_meta = {
                        "semana": sem_limpa, 
                        "trimestre": trim_atual, 
                        "ano": ano_str_busca, 
                        "base": f"Avaliação: {nome_exame_tit}",
                        "status_final": "PRODUZIDO"
                    }
                    st.toast("Plano estruturado com sucesso!", icon="✅")
                    st.rerun()

                if c_save_ex2.button("Salvar e Sincronizar Diretamente", use_container_width=True, key=f"btn_direct_save_ex_{v}"):
                    with st.spinner("Sincronizando plano de avaliação no Google Drive..."):
                        nome_exame_tit = exame_selecionado if exame_selecionado else conteudos_extraidos
                        nome_arquivo = f"PLANO_{ano_str_busca.replace('º','')}_{sem_limpa.replace(' ', '')}"
                        
                        db.excluir_plano_completo(sem_limpa, ano_str_busca)
                        
                        dados_docx = {
                            "geral": f"{tipo_semana.upper()} - {nome_exame_tit}",
                            "especificos": conteudos_extraidos,
                            "objetivos": "Mensurar proficiência e consolidação de habilidades.",
                            "recursos": f"Material Impresso / Avaliação: {nome_exame_tit}",
                            "metodologia": diretriz_logistica,
                            "avaliacao": "Scanner CIR (TRI) e observação da aplicação.",
                            "pei": "Cadernos adaptados (PEI N1, N2 e N3) conforme perfil dos estudantes."
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
                        
                        st.success(f"Plano para {sem_limpa} salvo e sincronizado com sucesso!")
                        time.sleep(0.8); st.rerun()

        else:
            with st.container(border=True):
                st.markdown("#### 2. Base Curricular & Livro Didático")
                st.caption(f"Carga Horária Selecionada: **{carga_horaria}**")
                
                modo_p = st.segmented_control(
                    "Fonte Curricular:", 
                    ["Livro Didático (Cofre Digital)", "Matriz Curricular (Manual)", "Links da Web"], 
                    default="Livro Didático (Cofre Digital)",
                    key=f"pills_fonte_{v}"
                )
                
                ctx_ia, uri_livro_drive, links_web_texto, base_didatica_info = "", None, "", "Matriz Curricular"
                texto_teoria_extraido, texto_exercicios_extraido = "", ""
                bytes_pdf_fatiado_teo, bytes_pdf_fatiado_ex = None, None
                
                if modo_p == "Matriz Curricular (Manual)":
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
                    else: st.warning("Não foi possível ler as colunas da matriz curricular.")
                
                elif modo_p == "Links da Web":
                    links_web_texto = st.text_area("Artigos ou Notícias de Referência (URLs):", placeholder="https://...", key=f"ta_links_web_{v}")
                    base_didatica_info = "Artigos e Notícias da Web"
                
                else:
                    cx1, cx2, cx3 = st.columns([2, 1.5, 1.5])
                    livros_disponiveis = df_materiais[df_materiais['TIPO'].str.contains(str(ano_p), na=False)]['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
                    sel_mat = cx1.selectbox("Livro Didático Cadastrado:", [""] + livros_disponiveis, key=f"sel_livro_ponto_{v}")
                    
                    pags_teoria_input = cx2.text_input("Páginas de Teoria:", placeholder="Ex: 184-186, 189", key=f"pags_teo_ponto_{v}")
                    pags_ex_input = cx3.text_input("Páginas de Exercícios:", placeholder="Ex: 187-188, 190-192", key=f"pags_ex_ponto_{v}")

                    if sel_mat:
                        uri_livro_drive = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_mat].iloc[0]['URI_ARQUIVO']
                        base_didatica_info = f"Livro: {sel_mat} | Teoria: {pags_teoria_input if pags_teoria_input else 'Geral'} | Exercícios: {pags_ex_input if pags_ex_input else 'Geral'}"

                        list_pags_teo = util.processar_intervalos_paginas(pags_teoria_input)
                        list_pags_ex = util.processar_intervalos_paginas(pags_ex_input)

                        if list_pags_teo or list_pags_ex:
                            with st.spinner("Fatiando páginas selecionadas do livro..."):
                                bytes_pdf = db.baixar_bytes_arquivo_drive(uri_livro_drive)
                                if bytes_pdf:
                                    if list_pags_teo:
                                        texto_teoria_extraido = util.extrair_texto_pdf_por_paginas(bytes_pdf, list_pags_teo)
                                        bytes_pdf_fatiado_teo = util.fatiar_pdf_bytes_por_paginas(bytes_pdf, list_pags_teo)
                                    if list_pags_ex:
                                        texto_exercicios_extraido = util.extrair_texto_pdf_por_paginas(bytes_pdf, list_pags_ex)
                                        bytes_pdf_fatiado_ex = util.fatiar_pdf_bytes_por_paginas(bytes_pdf, list_pags_ex)

                    recorte_livro_texto = st.text_area(
                        "Texto Complementar / Exercícios Autorais do Professor (Opcional):",
                        placeholder="Insira anotações complementares ou exercícios específicos do seu caderno de regência...",
                        height=85,
                        key=f"recorte_ponto_id_{v}"
                    )

                    if texto_teoria_extraido or texto_exercicios_extraido or recorte_livro_texto.strip() or bytes_pdf_fatiado_teo:
                        with st.expander("Inspeção de Conteúdo Lido do Livro", expanded=False):
                            t_insp1, t_insp2, t_insp3 = st.tabs(["Teoria Lida", "Exercícios Lidos", "Texto Complementar"])
                            
                            with t_insp1:
                                if bytes_pdf_fatiado_teo:
                                    v_modo_teo = st.segmented_control("Modo:", ["Visualizador PDF", "Texto Extraído"], default="Visualizador PDF", key=f"v_teo_mode_{v}")
                                    if "PDF" in v_modo_teo:
                                        util.renderizar_pdf_iframe(bytes_pdf_fatiado_teo, altura=440)
                                    else:
                                        st.text_area("Teoria:", texto_teoria_extraido, height=220, disabled=True, key=f"ta_insp_teo_{v}")
                                elif texto_teoria_extraido:
                                    st.text_area("Teoria:", texto_teoria_extraido, height=220, disabled=True, key=f"ta_insp_teo_{v}")
                                else:
                                    st.info("Nenhuma página de teoria fatiada.")
                                    
                            with t_insp2:
                                if bytes_pdf_fatiado_ex:
                                    v_modo_ex = st.segmented_control("Modo:", ["Visualizador PDF", "Texto Extraído"], default="Visualizador PDF", key=f"v_ex_mode_{v}")
                                    if "PDF" in v_modo_ex:
                                        util.renderizar_pdf_iframe(bytes_pdf_fatiado_ex, altura=440)
                                    else:
                                        st.text_area("Exercícios:", texto_exercicios_extraido, height=220, disabled=True, key=f"ta_insp_ex_{v}")
                                elif texto_exercicios_extraido:
                                    st.text_area("Exercícios:", texto_exercicios_extraido, height=220, disabled=True, key=f"ta_insp_ex_{v}")
                                else:
                                    st.info("Nenhuma página de exercício fatiada.")
                                    
                            with t_insp3:
                                if recorte_livro_texto.strip(): st.text_area("Texto Autorizado:", recorte_livro_texto, height=130, disabled=True, key=f"ta_insp_aux_{v}")
                                else: st.info("Nenhum texto complementar informado.")

            foco_a1, foco_a2, foco_sab = "N/A", "N/A", "N/A"
            with st.popover("Configurações Avançadas das Aulas (Opcional)", use_container_width=True):
                st.caption("Especifique o tema central ou gancho de contextualização para cada aula:")
                if "1 Aula" in carga_horaria:
                    foco_a1 = st.text_area("Diretriz da Aula Única:", placeholder="Ex: Contextualização sobre finanças e resolução de operações...", height=80, key=f"foco_a1_p1_{v}")
                elif "2 Aulas" in carga_horaria:
                    foco_a1 = st.text_area("Diretriz Aula 1 (Conceituação & Contexto):", placeholder="Ex: Demonstração do algoritmo e contexto cotidiano...", height=80, key=f"foco_a1_p2_{v}")
                    foco_a2 = st.text_area("Diretriz Aula 2 (Fixação & Prática):", placeholder="Ex: Resolução comentada dos exercícios da página 185...", height=80, key=f"foco_a2_p2_{v}")
                else:
                    foco_a1 = st.text_area("Diretriz Aula 1:", placeholder="Ex: Apresentação do conceito...", height=80, key=f"foco_a1_p3_{v}")
                    foco_a2 = st.text_area("Diretriz Aula 2:", placeholder="Ex: Resolução de problemas...", height=80, key=f"foco_a2_p3_{v}")
                    foco_sab = st.text_area("Diretriz Sábado Letivo:", placeholder="Ex: Oficina prática...", height=80, key=f"foco_sab_p3_{v}")

            c_g1, c_g2 = st.columns(2)

            if c_g1.button("Gerar Planejamento Estruturado", use_container_width=True, type="primary", key=f"btn_gen_ia_ponto_{v}"):
                with st.status("Arquitetando plano de aula estruturado...", expanded=True) as status:
                    status.write("Consolidando recortes do livro, diretrizes e matriz curricular...")
                    
                    precisa_de_internet = False
                    if modo_p == "Matriz Curricular (Manual)": diretriz_base = "MÉTODO MANUAL: Baseie-se na Matriz Curricular."
                    elif modo_p == "Links da Web": diretriz_base = f"MÉTODO WEB: Use estes links:\n{links_web_texto}"; precisa_de_internet = True
                    else: diretriz_base = f"MÉTODO LIVRO DIDÁTICO: O professor utilizará o livro '{base_didatica_info}'."

                    if "1 Aula" in carga_horaria:
                        diretriz_carga_promp = (
                            "CARGA HORÁRIA: 1 AULA NA SEMANA.\n"
                            "- Concentre toda a explicação e prática na AULA 1 (INÍCIO, MEIO e FIM).\n"
                            "- As tags [AULA_2] e [SABADO_LETIVO] devem conter 'N/A (Carga horária de 1 Aula)'."
                        )
                    elif "2 Aulas" in carga_horaria:
                        diretriz_carga_promp = (
                            "CARGA HORÁRIA: 2 AULAS NA SEMANA.\n"
                            "- Distribua a teoria na AULA 1 e a fixação na AULA 2 (ambas em INÍCIO, MEIO e FIM).\n"
                            "- Tag [SABADO_LETIVO] deve conter 'N/A'."
                        )
                    else:
                        diretriz_carga_promp = "CARGA HORÁRIA: 3 AULAS NA SEMANA. Distribua o conteúdo na AULA 1, AULA 2 e SÁBADO LETIVO no formato INÍCIO, MEIO e FIM."

                    template_forcado = (
                        "[HABILIDADE_BNCC] (Código BNCC alfanumérico ex: EF06MA01)\n"
                        "[COMPETENCIAS_FOCO] (Competências Específicas de Matemática 1 a 8 da Pág. 267 da BNCC)\n"
                        "[OBJETO_CONHECIMENTO] (Tema principal e Unidade Temática BNCC)\n"
                        "[CONTEUDOS_ESPECIFICOS] (Tópicos matemáticos)\n"
                        "[OBJETIVOS_ENSINO] (Objetivos pedagógicos)\n"
                        "[JUSTIFICATIVA_PEDAGOGICA] (Justificativa técnica)\n"
                        "[AULA_1] INÍCIO (10 min): ...\nMEIO (25 min): ...\nFIM (15 min): ...\n"
                        "[AULA_2] (AULA 2 no mesmo formato ou N/A se for 1 aula)\n"
                        "[SABADO_LETIVO] (SÁBADO no mesmo formato ou N/A)\n"
                        "[AVALIACAO_DE_MERITO] (Critérios de avaliação)\n"
                        "[ESTRATEGIA_DUA_PEI] (Adaptações de acessibilidade)\n"
                    )

                    pacote_recorte_completo = ""
                    if texto_teoria_extraido: pacote_recorte_completo += f"--- PÁGINAS DE TEORIA ---\n{texto_teoria_extraido}\n\n"
                    if texto_exercicios_extraido: pacote_recorte_completo += f"--- PÁGINAS DE EXERCÍCIOS ---\n{texto_exercicios_extraido}\n\n"
                    if recorte_livro_texto.strip(): pacote_recorte_completo += f"--- TEXTO COMPLEMENTAR DO PROFESSOR ---\n{recorte_livro_texto.strip()}\n\n"

                    prompt = (
                        f"TIPO: {tipo_semana}\n{diretriz_base}\n"
                        f"SÉRIE: {ano_p}º Ano. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}.\n"
                        f"{diretriz_carga_promp}\n"
                        f"BASE DIDÁTICA: {base_didatica_info}\n"
                        f"DIRETRIZ AULA 1: {foco_a1}\nDIRETRIZ AULA 2: {foco_a2}\nDIRETRIZ SÁBADO: {foco_sab}\n"
                        f"MATRIZ OFICIAL:\n{ctx_ia if ctx_ia else 'Baseada na leitura direta das páginas do Livro Didático.'}\n\n"
                        f"PREENCHA OBRIGATORIAMENTE ESTE TEMPLATE:\n{template_forcado}"
                    )
                    
                    status.write("Processando com Gemini 3.7 Flash...")
                    resultado_ia = ai.gerar_ia("PLANE_PEDAGOGICO", prompt, url_drive=uri_livro_drive, usar_busca=precisa_de_internet, recorte_livro=pacote_recorte_completo)
                    
                    if "ERRO" in resultado_ia.upper() or "⚠️" in resultado_ia:
                        status.update(label="Falha na comunicação com a IA.", state="error")
                        st.error(resultado_ia)
                    else:
                        st.session_state.p_temp = resultado_ia
                        st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info, "status_final": "HUB_ATIVO"}
                        status.update(label="Planejamento concluído com sucesso!", state="complete")
                        time.sleep(0.6)
                        st.rerun()

            if c_g2.button("Estruturar Plano Manual", use_container_width=True, key=f"btn_manual_ponto_{v}"):
                espec_pre = ", ".join(sel_cont) if 'sel_cont' in locals() and sel_cont else ""
                
                texto_manual_template = (
                    f"[HABILIDADE_BNCC] EF0{ano_p}MA01\n"
                    f"[COMPETENCIAS_FOCO] Competência Específica 2 (Raciocínio Lógico e Argumentação)\n"
                    f"[OBJETO_CONHECIMENTO] Unidade Temática: Números / Álgebra\n"
                    f"[CONTEUDOS_ESPECIFICOS] {espec_pre}\n"
                    f"[OBJETIVOS_ENSINO]\n"
                    f"[AULA_1] INÍCIO (10 min):\nMEIO (25 min):\nFIM (15 min):\n"
                    f"[AULA_2] INÍCIO:\nMEIO:\nFIM:\n"
                    f"[SABADO_LETIVO] N/A\n"
                    f"[AVALIACAO_DE_MERITO]\n"
                    f"[ESTRATEGIA_DUA_PEI]"
                )
                
                st.session_state.p_temp = texto_manual_template
                st.session_state.p_meta = {"semana": sem_limpa, "trimestre": trim_atual, "ano": ano_str_busca, "base": base_didatica_info, "status_final": "HUB_ATIVO"}
                st.rerun()

    # MESA DE LAPIDAÇÃO
    @st.fragment
    def renderizar_mesa_lapidacao_plano():
        if "p_temp" in st.session_state:
            txt_bruto = st.session_state.p_temp
            meta = st.session_state.get("p_meta", {})
            semana_nome = meta.get('semana', 'Atual')
            
            unidade_bncc = "NÚMEROS"
            if any(x in txt_bruto.upper() for x in ["ÁLGEBRA", "ALGEBRA", "EQUAÇÃO", "VARIÁVEL", "FUNÇÃO"]):
                unidade_bncc = "ÁLGEBRA"
            elif any(x in txt_bruto.upper() for x in ["GEOMETRIA", "ÂNGULO", "TRIÂNGULO", "POLÍGONO", "PLANO CARTESIANO"]):
                unidade_bncc = "GEOMETRIA"
            elif any(x in txt_bruto.upper() for x in ["GRANDEZAS", "MEDIDAS", "PERÍMETRO", "ÁREA", "VOLUME", "CAPACIDADE"]):
                unidade_bncc = "GRANDEZAS E MEDIDAS"
            elif any(x in txt_bruto.upper() for x in ["PROBABILIDADE", "ESTATÍSTICA", "GRÁFICO", "TABELA", "AMOSTRA"]):
                unidade_bncc = "PROBABILIDADE E ESTATÍSTICA"

            st.markdown("---")
            
            with st.container(border=True):
                st.markdown(f"### Mesa de Lapidação: **{semana_nome}**")
                
                c_bad1, c_bad2 = st.columns([1.5, 2.5])
                c_bad1.markdown(f"**Unidade Temática BNCC:** `{unidade_bncc}`")
                comp_foco_txt = ai.extrair_tag(txt_bruto, "COMPETENCIAS_FOCO") or "Competência Específica 2 (Raciocínio Lógico)"
                c_bad2.markdown(f"**Competência Foco:** `{comp_foco_txt[:55]}...`")
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                c_lap1, c_lap2 = st.columns([1.5, 1])
                if c_lap1.button("Harmonizar com Linguagem BNCC", use_container_width=True, key=f"btn_harm_plan_{v}"):
                    with st.spinner("Refinando linguagem pedagógica..."):
                        prompt_harm = (
                            f"REESCREVA O PLANO ABAIXO EM LINGUAGEM PEDAGÓGICA OFICIAL DA BNCC/SAEB.\n"
                            f"Mantenha todas as tags [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS], [OBJETIVOS_ENSINO], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO] e [ESTRATEGIA_DUA_PEI].\n\n"
                            f"PLANO ATUAL:\n{txt_bruto}"
                        )
                        st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_harm, usar_busca=False)
                        st.toast("Plano harmonizado com sucesso!", icon="✨")
                        st.rerun()

                with c_lap2.popover("Copiar Plano Formatado"):
                    st.caption("Texto formatado para área de transferência:")
                    st.code(st.session_state.p_temp, language=None)

                cmd_refine = st.chat_input("Instruções de ajuste para a IA (ex: 'Aprofunde a contextualização inicial da Aula 1')", key=f"chat_refine_ponto_{v}")
                if cmd_refine:
                    with st.spinner("Ajustando plano..."):
                        prompt_refino = f"ORDEM DE AJUSTE: {cmd_refine}\n\nPLANO ATUAL:\n{st.session_state.p_temp}"
                        st.session_state.p_temp = ai.gerar_ia("REFINADOR_PEDAGOGICO", prompt_refino, usar_busca=False)
                        st.rerun()

            tab_curriculo, tab_roteiro, tab_inclusao = st.tabs([
                "1. Matriz Curricular & BNCC", 
                "2. Roteiro Pedagógico", 
                "3. Avaliação & Acessibilidade DUA"
            ])
            
            with tab_curriculo:
                ed_hab = st.text_input("Habilidade BNCC / Descritores:", ai.extrair_tag(txt_bruto, "HABILIDADE_BNCC") or "EF06MA01", key=f"frag_hab_{v}")
                ed_comp = st.text_input("Competências Específicas BNCC:", ai.extrair_tag(txt_bruto, "COMPETENCIAS_FOCO") or "Competência Específica 2 (Raciocínio Lógico) e 6 (Enfrentar Situações-Problema)", key=f"frag_comp_{v}")
                ed_geral = st.text_input("Objeto de Conhecimento / Unidade Temática:", ai.extrair_tag(txt_bruto, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL") or "PLANEJAMENTO SEMANAL", key=f"frag_geral_{v}")
                ed_espec = st.text_area("Conteúdos Específicos:", ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS") or txt_bruto, height=120, key=f"frag_espec_{v}")
                ed_objs = st.text_area("Objetivos de Aprendizagem:", ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO") or "Consolidar objetos de conhecimento e superar lacunas diagnosticadas.", height=120, key=f"frag_objs_{v}")
            
            with tab_roteiro:
                c_a1, c_a2, c_a3 = st.columns(3)
                ed_a1 = c_a1.text_area("AULA 1 (Início, Meio, Fim):", ai.extrair_tag(txt_bruto, "AULA_1"), height=360, key=f"frag_a1_{v}")
                ed_a2 = c_a2.text_area("AULA 2 (Início, Meio, Fim):", ai.extrair_tag(txt_bruto, "AULA_2"), height=360, key=f"frag_a2_{v}")
                ed_sab = c_a3.text_area("SÁBADO LETIVO:", ai.extrair_tag(txt_bruto, "SABADO_LETIVO") or "N/A", height=360, key=f"frag_sab_{v}")
                
            with tab_inclusao:
                ed_ava = st.text_area("Critérios de Avaliação:", ai.extrair_tag(txt_bruto, "AVALIACAO_DE_MERITO") or "Acompanhamento formativo e correção de exercícios do caderno.", height=140, key=f"frag_ava_{v}")
                ed_pei = st.text_area("Estratégias de Acessibilidade (DUA/PEI):", ai.extrair_tag(txt_bruto, "ESTRATEGIA_DUA_PEI") or "Uso de cadernos adaptados (PEI N1, N2 e N3) com suporte visual e mediação individualizada.", height=140, key=f"frag_pei_{v}")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            if st.button("Sincronizar Plano no Google Drive", use_container_width=True, type="primary", key=f"frag_btn_save_{v}"):
                with st.status("Gerando documento oficial e sincronizando no Google Drive...", expanded=True) as status:
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
                    
                    status.write("Compilando arquivo DOCX oficial...")
                    doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(
                        nome_arquivo, dados_docx, {"ano": ano_fmt_s, "semana": sem_fmt_s, "trimestre": trim_fmt_s}
                    )
                    
                    status.write("Enviando para a pasta oficial do Google Drive...")
                    link_drive = db.subir_e_converter_para_google_docs(
                        doc_io, nome_arquivo, trimestre=trim_fmt_s, categoria=ano_fmt_s, semana=sem_fmt_s, modo="PLANEJAMENTO"
                    )
                    
                    status_banco = meta.get("status_final", "HUB_ATIVO")

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
                    
                    status.update(label="Plano sincronizado com sucesso!", state="complete")
                    st.balloons()
                    time.sleep(0.8)
                    reset_planejamento()

    renderizar_mesa_lapidacao_plano()

    # ==============================================================================
    # ABA 2: HUB DE PRODUÇÃO & BAIXA OFFLINE
    # ==============================================================================
    with tab_producao:
        st.markdown("#### Hub de Produção de Materiais")
        st.caption("Planos aprovados aguardando geração de materiais com IA ou registro de aula presencial.")
        
        planos_ativos = pd.DataFrame()
        if not df_planos.empty and 'EIXO' in df_planos.columns:
            planos_ativos = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]

        if not planos_ativos.empty:
            for _, row in planos_ativos.iterrows():
                with st.container(border=True):
                    c_p1, c_p2, c_p3, c_p4 = st.columns([2, 1.2, 1.2, 1])
                    c_p1.markdown(f"**{row.get('SEMANA', 'Semana')}** | Série: {row.get('ANO', '6º')} ({row.get('TURMA', 'I Trimestre')})")
                    c_p1.caption("Status: Pendente de Produção")
                    
                    if c_p2.button("Gerar Material com IA", key=f"gen_hub_{row.name}", use_container_width=True):
                        st.session_state.lab_temp = str(row.get("PLANO_TEXTO", ""))
                        st.session_state.sosa_id_atual = util.gerar_sosa_id("AULA", row.get('ANO', '6º'), row.get("TURMA", "I Trimestre"))
                        st.session_state.lab_meta = {
                            "ano": str(row.get('ANO', '6')).replace("º",""), 
                            "trimestre": str(row.get("TURMA", "I Trimestre")), 
                            "tipo": "PRODUÇÃO_HUB", 
                            "semana_ref": str(row.get('SEMANA', 'Semana'))
                        }
                        navegar_para("🧪 Criador de Aulas")

                    with c_p3.popover("Registrar Aula Presencial"):
                        st.caption("Registre a aula ministrada com Livro Didático sem gerar arquivos adicionais.")
                        txt_obs_manual = st.text_input("Detalhamento:", placeholder="Ex: Livro Didático - Págs. 184 a 187", key=f"txt_man_obs_hub_{row.name}")
                        data_exec_livro = st.date_input("Data de Aplicação:", date.today(), format="DD/MM/YYYY", key=f"dt_livro_hub_{row.name}")
                        
                        if st.button("Confirmar Registro Presencial", type="primary", key=f"btn_conf_man_hub_{row.name}"):
                            dt_str_livro = data_exec_livro.strftime("%d/%m/%Y")
                            db.dar_baixa_aula_livro_offline(
                                semana=str(row.get('SEMANA', 'Semana')), 
                                ano=str(row.get('ANO', '6º')), 
                                turma=str(row.get('TURMA', 'I Trimestre')), 
                                data_str=dt_str_livro, 
                                detalhes_livro=txt_obs_manual
                            )
                            st.success("Aula registrada no diário e plano concluído!")
                            time.sleep(0.6); st.rerun()

                    with c_p4.popover("Registrar Evento"):
                        st.caption("Arquive esta semana devido a recesso ou avaliação institucional.")
                        motivo_evento = st.selectbox("Motivo:", ["Recesso Escolar / Feriado", "Semana de Provas Globais", "Conselho de Classe / Evento"], key=f"mot_ev_hub_{row.name}")
                        
                        if st.button("Arquivar Semana", key=f"fin_hub_ev_{row.name}", use_container_width=True):
                            db.dar_baixa_plano_evento(
                                semana=str(row.get('SEMANA', 'Semana')), 
                                ano=str(row.get('ANO', '6º')), 
                                motivo_ou_status=motivo_evento
                            )
                            st.success("Semana arquivada no planejamento!")
                            time.sleep(0.6); st.rerun()
        else:
            st.success("Todos os planos pedagógicos estão em dia. Nenhum material pendente no Hub de Produção.")
            
            if not df_planos.empty and 'SEMANA' in df_planos.columns:
                with st.expander("Histórico de Planos Cadastrados no Banco", expanded=False):
                    df_planos_exibicao = df_planos[['DATA', 'SEMANA', 'ANO', 'TURMA', 'EIXO']].copy()
                    st.dataframe(df_planos_exibicao, use_container_width=True, hide_index=True)

    # ==============================================================================
    # ABA 3: ACERVO DE PLANOS & RELOCADOR DE SEMANAS
    # ==============================================================================
    with tab_acervo:
        st.markdown("#### Acervo de Planos Estratégicos")
        st.caption("Consulte, gerencie e reindexe os planos armazenados na biblioteca.")
        
        if not df_planos.empty and 'ANO' in df_planos.columns and 'SEMANA' in df_planos.columns:
            f_ano_h = st.segmented_control("Filtrar por Série:", ["Todos", "6º", "7º", "8º", "9º"], default="Todos", key=f"hist_ano_{v}")
            df_h = df_planos[df_planos["ANO"] == f"{f_ano_h}º"] if f_ano_h != "Todos" else df_planos.copy()
            
            if not df_h.empty:
                semanas_lista_ac = df_h["SEMANA"].dropna().unique().tolist()[::-1]
                sel_h = st.selectbox("Selecione o Plano:", semanas_lista_ac, key=f"hist_sem_{v}")
                match_h = df_h[df_h["SEMANA"] == sel_h]
                
                if not match_h.empty:
                    dados_h = match_h.iloc[0]
                    link_atual = str(dados_h.get("LINK_DRIVE", ""))
                    is_corrupted = "html" in link_atual.lower() or "Page Not Found" in link_atual or not link_atual.startswith("http")
                    
                    if is_corrupted:
                        st.warning("O link deste documento necessita de recuperação.")
                        if st.button("Reconstruir Documento no Drive", type="primary", use_container_width=True, key=f"heal_btn_{sel_h.replace(' ','')}_{v}"):
                            with st.status("Reconstruindo documento...", expanded=True) as status:
                                plano_txt_bruto = str(dados_h.get('PLANO_TEXTO', ''))
                                
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
                                
                                nome_arquivo = f"PLANO_{str(dados_h.get('ANO','6')).replace('º','')}_{sel_h.replace(' ', '')}"
                                doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": str(dados_h.get('ANO','6º')), "semana": sel_h, "trimestre": str(dados_h.get('TURMA','I Trimestre'))})
                                
                                link_novo = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=str(dados_h.get('TURMA','I Trimestre')), categoria=str(dados_h.get('ANO','6º')), semana=sel_h, modo="PLANEJAMENTO")
                                
                                if "https" in link_novo and len(link_novo) < 250:
                                    try:
                                        wb = db.conectar()
                                        ws = wb.worksheet("DB_PLANOS")
                                        dados_sheet = ws.get_all_values()
                                        
                                        for row_idx, row in enumerate(dados_sheet):
                                            if row_idx > 0 and row[1] == sel_h and row[2] == str(dados_h.get('ANO','')):
                                                ws.update_cell(row_idx+1, 7, link_novo)
                                                novo_plano_texto = plano_txt_bruto.split("--- LINK DRIVE ---")[0] + f"--- LINK DRIVE --- {link_novo}"
                                                ws.update_cell(row_idx+1, 6, novo_plano_texto)
                                                break
                                        
                                        status.update(label="Documento reconstruído com sucesso!", state="complete")
                                        st.cache_data.clear(); time.sleep(0.8); st.rerun()
                                    except Exception as e: st.error(f"Erro ao atualizar banco: {e}")
                                else:
                                    status.update(label="Falha na reconstrução.", state="error")
                                    st.error(link_novo)
                    else:
                        c_btn1, c_btn2 = st.columns([2, 1])
                        c_btn1.link_button("Abrir Documento no Drive", link_atual, use_container_width=True)
                        if c_btn2.button("Excluir Plano", use_container_width=True, key=f"del_plan_h_{sel_h.replace(' ', '')}_{v}"):
                            if db.excluir_plano_completo(sel_h, str(dados_h.get("ANO", ""))): st.rerun()

                        @st.fragment
                        def renderizar_relocador_fragmento():
                            with st.expander("Reindexar Plano para Outra Semana", expanded=False):
                                st.caption("Transfere a semana do plano e de todas as aulas no banco preservando os arquivos originais no Drive.")
                                
                                todas_semanas_reloc = util.gerar_semanas()
                                semanas_ocupadas_ano = df_planos[df_planos['ANO'] == str(dados_h.get('ANO',''))]['SEMANA'].tolist() if 'ANO' in df_planos.columns else []
                                semanas_livres_reloc = [s.split(" (")[0] for s in todas_semanas_reloc if s.split(" (")[0] not in semanas_ocupadas_ano and "Jornada" not in s]
                                
                                if not semanas_livres_reloc:
                                    st.info("Todas as semanas deste ano letivo já possuem planos cadastrados.")
                                else:
                                    nova_semana_dest = st.selectbox("Semana de Destino:", semanas_livres_reloc, key=f"reloc_sem_{sel_h.replace(' ','')}_{v}")
                                    
                                    if st.button("Confirmar Reindexação", type="primary", use_container_width=True, key=f"btn_reloc_exe_{sel_h.replace(' ','')}_{v}"):
                                        with st.spinner("Reindexando plano e materiais em cascata..."):
                                            sucesso_reloc = db.relocador_plano_semana(
                                                semana_antiga=sel_h, 
                                                ano=str(dados_h.get('ANO','')), 
                                                nova_semana=nova_semana_dest, 
                                                link_drive=link_atual
                                            )
                                            if sucesso_reloc:
                                                st.success(f"Plano transferido para {nova_semana_dest} com sucesso!")
                                                time.sleep(0.8); st.rerun()
                                            else: st.error("Erro ao transferir a semana.")

                        renderizar_relocador_fragmento()
            else:
                st.info(f"Nenhum plano cadastrado para o {f_ano_h}º Ano no acervo.")
        else:
            st.info("Nenhum plano cadastrado no acervo.")

    # ==============================================================================
    # ABA 4: INTELIGÊNCIA CURRICULAR & CONCILIAÇÃO CRONOLÓGICA
    # ==============================================================================
    with tab_inteligencia:
        st.markdown("### Inteligência Curricular & Planejamento Trimestral")
        
        modo_inteligencia = st.segmented_control(
            "Selecione a Visão:", 
            ["Status de Execução (Checklist)", "Gerador de Plano Trimestral", "Conciliador Cronológico"], 
            default="Status de Execução (Checklist)",
            key=f"seg_intel_{v}"
        )
        st.markdown("---")

        def limpar_tags_cite(texto):
            if not isinstance(texto, str): return ""
            return re.sub(r'\[cite:.*?\]', '', texto).strip()

        if modo_inteligencia == "Status de Execução (Checklist)":
            st.caption("Cruzamento automatizado e semântico entre os tópicos da matriz curricular e os planos homologados no Ponto ID.")
            
            c1, c2 = st.columns([1, 1])
            ano_c = c1.selectbox("Série:", [6, 7, 8, 9], key=f"matriz_ano_{v}")
            trim_c = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"matriz_trim_{v}")
            
            col_ano = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None) if not df_curriculo.empty else None
            col_eixo = next((c for c in df_curriculo.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None) if not df_curriculo.empty else None
            col_trim = next((c for c in df_curriculo.columns if trim_c.upper() in c.upper()), None) if not df_curriculo.empty else None

            if col_ano and col_eixo and col_trim:
                df_c = df_curriculo[df_curriculo[col_ano].astype(str).str.contains(str(ano_c))].copy()
                
                if not df_c.empty:
                    # 1. MINERAÇÃO INTEGRAL DE TODOS OS PLANOS DO TRIMESTRE
                    planos_feitos = df_planos[(df_planos["ANO"].astype(str).str.contains(str(ano_c))) & (df_planos["TURMA"] == trim_c)] if not df_planos.empty and 'ANO' in df_planos.columns and 'TURMA' in df_planos.columns else pd.DataFrame()
                    
                    # Concatena 100% do texto dos planos daquele trimestre
                    todos_planos_texto = ""
                    if not planos_feitos.empty and 'PLANO_TEXTO' in planos_feitos.columns:
                        todos_planos_texto = " \n ".join([str(p).upper() for p in planos_feitos['PLANO_TEXTO'].dropna()])
                    
                    import unicodedata
                    def normalizar_para_busca(txt):
                        if not txt or not isinstance(txt, str): return ""
                        nfkd = unicodedata.normalize('NFKD', txt.upper())
                        sem_acento = "".join([c for c in nfkd if not unicodedata.combining(c)])
                        return re.sub(r'[^A-Z0-9\s]', ' ', sem_acento)

                    planos_texto_norm = normalizar_para_busca(todos_planos_texto)

                    # 2. MOTOR DE RECONHECIMENTO SEMÂNTICO E PSICOMÉTRICO
                    def verificar_conclusao_topico(topico_raw, planos_norm):
                        if not topico_raw or not planos_norm: return False
                        
                        # Camada 1: Checagem por Código BNCC (ex: EF06MA01, EF06MA02)
                        codigos_bncc = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', topico_raw, re.IGNORECASE)
                        for cod in codigos_bncc:
                            if cod.upper() in planos_norm:
                                return True
                                
                        topico_norm = normalizar_para_busca(topico_raw)
                        topico_alpha = re.sub(r'[^A-Z0-9]', '', topico_norm)
                        planos_alpha = re.sub(r'[^A-Z0-9]', '', planos_norm)
                        
                        # Camada 2: Checagem por Substring Exata
                        if len(topico_alpha) >= 8 and topico_alpha in planos_alpha:
                            return True
                            
                        # Camada 3: Checagem por Palavras-Chave Conceituais
                        stopwords = {
                            'A', 'O', 'AS', 'OS', 'DE', 'DA', 'DO', 'DAS', 'DOS', 'EM', 'NO', 'NA', 
                            'NOS', 'NAS', 'POR', 'PARA', 'COM', 'SEM', 'SOB', 'SOBRE', 'E', 'OU', 
                            'UM', 'UMA', 'UNS', 'UMAS', 'SEU', 'SUA', 'QUE', 'COMO', 'AO', 'AOS',
                            'VALOR', 'FORMA', 'USO', 'NUMERO', 'NUMEROS'
                        }
                        
                        topico_sem_cod = re.sub(r'EF\d{2}MA\d{2}[A-Z]?', '', topico_norm)
                        palavras = [w for w in topico_sem_cod.split() if w not in stopwords and len(w) >= 4]
                        
                        if not palavras: return False
                        
                        palavras_encontradas = [w for w in palavras if w in planos_norm]
                        taxa = len(palavras_encontradas) / len(palavras)
                        
                        # Se 50% ou mais das palavras-chave estiverem presentes no plano
                        if taxa >= 0.5 or len(palavras_encontradas) >= 2:
                            return True
                            
                        return False

                    dados_checklist = []
                    for _, row in df_c.iterrows():
                        eixo = row.get(col_eixo, 'Geral')
                        conteudos_brutos = limpar_tags_cite(row.get(col_trim, ''))
                        topicos = [t.strip() for t in conteudos_brutos.split(';') if t.strip()]
                        
                        for topico in topicos:
                            status = "CONCLUÍDO" if verificar_conclusao_topico(topico, planos_texto_norm) else "PENDENTE"
                            dados_checklist.append({
                                "Unidade Temática (Eixo)": eixo, 
                                "Conteúdo Específico": topico, 
                                "Status": status
                            })
                    
                    if dados_checklist:
                        df_check = pd.DataFrame(dados_checklist)
                        concluidos = len(df_check[df_check['Status'] == "CONCLUÍDO"])
                        total = len(df_check)
                        progresso = (concluidos / total) * 100 if total > 0 else 0
                        
                        with st.container(border=True):
                            c_prog1, c_prog2 = st.columns([3, 1])
                            c_prog1.progress(progresso / 100, text=f"**Progresso Curricular do Trimestre:** {concluidos} de {total} tópicos ministrados ({progresso:.1f}%)")
                            c_prog2.metric("Tópicos Restantes", total - concluidos)
                        
                        st.markdown("<br>", unsafe_allow_html=True)

                        def colorir_status(val):
                            if "CONCLUÍDO" in str(val): return 'color: #2ECC71; font-weight: bold;'
                            return 'color: #F1C40F; font-weight: bold;'
                            
                        st.dataframe(
                            df_check.style.map(colorir_status, subset=['Status']), 
                            use_container_width=True, 
                            hide_index=True
                        )
                    else: 
                        st.info("Nenhum conteúdo cadastrado para este trimestre na matriz curricular.")
            else: 
                st.error("Estrutura de colunas da matriz curricular não reconhecida.")

        elif modo_inteligencia == "Gerador de Plano Trimestral":
            st.markdown("#### Compilador Oficial de Planejamento (DOCX)")
            st.caption("Gere o Plano Trimestral ou o Plano Anual Completo em formato Paisagem A4 com blindagem de início de ano letivo (opera mesmo sem planos prévios).")
            
            c_t1, c_t2 = st.columns([1, 1])
            ano_trim = c_t1.selectbox("Série Alvo:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"], key=f"sel_ano_trim_{v}")
            
            opcoes_escopo_plano = [
                "Plano Anual Completo (I, II e III Trimestres)",
                "I Trimestre", 
                "II Trimestre", 
                "III Trimestre"
            ]
            trim_alvo = c_t2.selectbox("Escopo do Documento:", opcoes_escopo_plano, key=f"sel_trim_alvo_{v}")
            ano_num_trim = "".join(filter(str.isdigit, ano_trim))
            
            is_anual_plano = "Anual" in trim_alvo
            chave_rel_trim = f"PLANO_ANUAL_COMPLETO_{ano_num_trim}ANO" if is_anual_plano else f"PLANO_TRIMESTRAL_{trim_alvo.replace(' ', '_').upper()}_{ano_num_trim}ANO"
            
            # 1. VERIFICAÇÃO DE DOCUMENTO JÁ EXISTENTE NO ACERVO
            link_existente = None
            data_geracao = None
            if not df_relatorios.empty and 'TIPO' in df_relatorios.columns and 'CONTEUDO' in df_relatorios.columns:
                match_rel = df_relatorios[df_relatorios['TIPO'] == chave_rel_trim]
                if not match_rel.empty:
                    link_existente = str(match_rel.iloc[-1]['CONTEUDO'])
                    data_geracao = str(match_rel.iloc[-1].get('DATA', 'N/A'))

            st.markdown("<br>", unsafe_allow_html=True)

            # STATUS DE COLD-START / REALIZADO
            planos_existentes_cnt = len(df_planos[df_planos['ANO'].astype(str).str.contains(ano_num_trim)]) if not df_planos.empty else 0
            if planos_existentes_cnt > 0:
                st.caption(f"Status do Banco: **{planos_existentes_cnt} semana(s) de aula integradas** na compilação.")
            else:
                st.info("Status de Início de Ano (Janeiro): **Nenhum plano semanal lançado ainda.** O sistema compilará a **Projeção Oficial da Matriz Municipal de Itabuna + BNCC**.")

            if link_existente and "http" in link_existente:
                with st.container(border=True):
                    c_card1, c_card2 = st.columns([2.5, 1.2])
                    c_card1.markdown(f"##### Documento Oficial Compilado")
                    c_card1.caption(f"Série: **{ano_trim}** | Escopo: **{trim_alvo}** | Última Sincronização: **{data_geracao}**")
                    
                    c_card2.link_button("Abrir Documento no Drive", link_existente, type="primary", use_container_width=True)

                st.markdown("<br>", unsafe_allow_html=True)
                with st.expander("Recompilar ou Atualizar Documento no Drive", expanded=False):
                    st.caption("Clique abaixo para recompilar o DOCX oficial no Google Drive:")
                    btn_executar_compilacao = st.button("Recompilar e Atualizar Documento", key=f"btn_regen_{chave_rel_trim}_{v}", use_container_width=True)
            else:
                rotulo_botao_gerar = "Gerar Plano Anual Completo (DOCX)" if is_anual_plano else f"Gerar Plano do {trim_alvo} (DOCX)"
                btn_executar_compilacao = st.button(rotulo_botao_gerar, type="primary", use_container_width=True, key=f"btn_gen_plan_trim_{v}")

            # 2. MOTOR DE COMPILAÇÃO COM BLINDAGEM DE INÍCIO DE ANO
            if btn_executar_compilacao:
                with st.status("Compilando documento institucional com blindagem curricular...", expanded=True) as status_comp:
                    col_ano = next((c for c in df_curriculo.columns if 'ANO' in c.upper()), None) if not df_curriculo.empty else None
                    col_eixo = next((c for c in df_curriculo.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO', 'DOMÍNIO'])), None) if not df_curriculo.empty else None
                    
                    if not col_ano or not col_eixo:
                        status_comp.update(label="Matriz curricular indisponível no banco.", state="error")
                        st.stop()
                        
                    df_matriz_ano = df_curriculo[df_curriculo[col_ano].astype(str).str.contains(ano_num_trim)].copy()
                    
                    if df_matriz_ano.empty:
                        status_comp.update(label="Nenhum dado curricular para esta série.", state="error")
                    else:
                        trims_processar = ["I Trimestre", "II Trimestre", "III Trimestre"] if is_anual_plano else [trim_alvo]
                        dados_tabela = []
                        
                        for t_nome in trims_processar:
                            col_trim = next((c for c in df_matriz_ano.columns if t_nome.upper() in c.upper()), None)
                            if not col_trim: continue
                            
                            # Busca planos reais se existirem
                            planos_trim = df_planos[(df_planos['ANO'].astype(str).str.contains(ano_num_trim)) & (df_planos['TURMA'] == t_nome)] if not df_planos.empty and 'ANO' in df_planos.columns and 'TURMA' in df_planos.columns else pd.DataFrame()
                            todos_planos_raw = " ".join([str(p) for p in planos_trim.get('PLANO_TEXTO', pd.Series()).dropna()])
                            
                            for _, row in df_matriz_ano.iterrows():
                                eixo = str(row.get(col_eixo, 'Geral')).strip()
                                if is_anual_plano:
                                    eixo_label = f"[{t_nome.upper()}] {eixo}"
                                else:
                                    eixo_label = eixo
                                    
                                conteudos = limpar_tags_cite(row.get(col_trim, '')).replace(";", ";\n")
                                
                                if conteudos and conteudos.upper() != "NAN":
                                    # Extrai habilidades BNCC da matriz
                                    codes_no_conteudo = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', conteudos, re.IGNORECASE)
                                    
                                    # Se houver planos reais, extrai códigos dos planos
                                    if not codes_no_conteudo and not planos_trim.empty:
                                        planos_do_eixo = [str(p) for p in planos_trim['PLANO_TEXTO'] if eixo.upper() in str(p).upper() or any(w.strip().upper() in str(p).upper() for w in conteudos.split('\n') if len(w.strip()) > 4)]
                                        text_eixo_planos = " ".join(planos_do_eixo) if planos_do_eixo else todos_planos_raw
                                        codes_no_conteudo = re.findall(r'EF\d{2}MA\d{2}[A-Z]?', text_eixo_planos, re.IGNORECASE)
                                    
                                    # Mapeamento infalível de fallback se for início de ano
                                    if not codes_no_conteudo:
                                        if "NÚMERO" in eixo.upper(): codes_no_conteudo = [f"EF0{ano_num_trim}MA01", f"EF0{ano_num_trim}MA02", f"EF0{ano_num_trim}MA03"]
                                        elif "ÁLGEBRA" in eixo.upper(): codes_no_conteudo = [f"EF0{ano_num_trim}MA04", f"EF0{ano_num_trim}MA05"]
                                        elif "GEOMETRIA" in eixo.upper(): codes_no_conteudo = [f"EF0{ano_num_trim}MA16", f"EF0{ano_num_trim}MA22"]
                                        elif "GRANDEZA" in eixo.upper(): codes_no_conteudo = [f"EF0{ano_num_trim}MA24", f"EF0{ano_num_trim}MA29"]
                                        else: codes_no_conteudo = [f"EF0{ano_num_trim}MA31", f"EF0{ano_num_trim}MA32"]

                                    codes_unicos = sorted(list(set([c.upper() for c in codes_no_conteudo])))
                                    hab_str = ", ".join(codes_unicos)
                                    
                                    # Metodologias (mineradas dos planos ou projetadas institucionalmente)
                                    metodologias = set()
                                    text_busca_met = todos_planos_raw.lower() if todos_planos_raw else ""
                                    
                                    if "quadro" in text_busca_met or "exposição" in text_busca_met or not text_busca_met: 
                                        metodologias.add("Exposição dialogada e resolução estruturada de problemas no quadro")
                                    if "livro" in text_busca_met or "conquista" in text_busca_met or not text_busca_met: 
                                        metodologias.add("Leitura orientada e exercícios de fixação no livro didático adotado")
                                    if "material dourado" in text_busca_met or "concreto" in text_busca_met: 
                                        metodologias.add("Uso de recursos manipulativos e representação visual concreta")
                                    if "transferidor" in text_busca_met or "malha" in text_busca_met or "geom" in eixo.lower(): 
                                        metodologias.add("Construções geométricas, malhas quadriculadas e instrumentos de medição")
                                    if "cotidiano" in text_busca_met or "itabuna" in text_busca_met or not text_busca_met: 
                                        metodologias.add("Contextualização com situações-problema do cotidiano e dados locais")
                                    if "revisão" in text_busca_met or "recomposição" in text_busca_met: 
                                        metodologias.add("Recomposição contínua de aprendizagem e análise formativa de erros")
                                    
                                    met_str = "• " + "\n• ".join(sorted(list(metodologias)))
                                    
                                    dados_tabela.append({
                                        "eixo": eixo_label, 
                                        "conteudos": conteudos,
                                        "habilidades": hab_str, 
                                        "metodologia": met_str
                                    })
                        
                        info_trim = {"trimestre": "PLANEJAMENTO ANUAL INTEGRADO" if is_anual_plano else trim_alvo, "ano": ano_trim}
                        nome_arq = f"PLANEJAMENTO_ANUAL_{ano_trim.replace('º ', '')}" if is_anual_plano else f"PLANEJAMENTO_TRIMESTRAL_{trim_alvo.replace(' ', '')}_{ano_trim.replace('º ', '')}"
                        
                        status_comp.write("Gerando arquivo DOCX Paisagem A4...")
                        doc_stream = exporter.gerar_docx_planejamento_trimestral(nome_arq, info_trim, dados_tabela)
                        
                        status_comp.write("Sincronizando com o Google Drive...")
                        link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq, trimestre="Conselho" if is_anual_plano else trim_alvo, categoria=ano_trim, modo="PLANEJAMENTO")
                        
                        if "https" in link_doc:
                            data_hoje_comp = datetime.now().strftime("%d/%m/%Y")
                            db.excluir_registro("DB_RELATORIOS", chave_rel_trim)
                            db.salvar_no_banco("DB_RELATORIOS", [
                                data_hoje_comp, "GLOBAL", "SISTEMA", chave_rel_trim, link_doc
                            ])
                            
                            status_comp.update(label="Documento oficial compilado e sincronizado com sucesso!", state="complete")
                            st.balloons()
                            time.sleep(0.8)
                            st.rerun()
                        else: 
                            status_comp.update(label="Falha no envio para o Google Drive.", state="error")
                            st.error(f"Erro: {link_doc}")

        elif modo_inteligencia == "Conciliador Cronológico":
            with st.container(border=True):
                st.markdown("#### Assistente de Conciliação e Reindexação de Semanas")
                st.caption("Reorganiza cronologicamente as semanas do planejamento e vincula automaticamente as aulas avulsas do diário de bordo.")
                
                c_conc1, c_conc2 = st.columns([1, 1])
                ano_conc_sel = c_conc1.selectbox("Série para Conciliação:", ["6º", "7º", "8º", "9º"], key=f"sel_ano_conc_{v}")
                
                if c_conc2.button("Executar Conciliação Cronológica", type="primary", use_container_width=True, key=f"btn_run_conc_{v}"):
                    with st.status(f"Conciliando semanas do {ano_conc_sel} Ano...", expanded=True) as status_conc:
                        status_conc.write("Reordenando cronologicamente e associando aulas...")
                        sucesso_c = db.conciliar_calendario_e_planos_cronologicos(ano_conc_sel)
                        
                        if sucesso_c:
                            status_conc.update(label="Semanas reindexadas e diários vinculados com sucesso!", state="complete")
                            st.balloons(); time.sleep(0.8); st.rerun()
                        else:
                            status_conc.update(label="Erro ao conciliar dados ou nenhum registro localizado.", state="error")








# ==============================================================================
# MÓDULO: LABORATÓRIO PEDAGÓGICO (CRIADOR DE AULAS & FORJA SEMIÓTICA)
# (V2026.PRO_INFINITY - TRÍADE SOSA: GUIA DOCENTE, FOLHA DO ALUNO & PEI ON-DEMAND)
# ==============================================================================
elif menu == "🧪 Criador de Aulas":
    st.title("Criador de Aulas & Forja Semiótica")
    st.caption("Forja estruturada de materiais didáticos: Guia Docente de Lousa (Início, Meio, Fim), Folha do Estudante com tabelas nativas, Gabarito Comentado e Adaptações PEI.")
    st.markdown("---")

    if "v_lab" not in st.session_state:
        st.session_state.v_lab = int(time.time())
    v_l = st.session_state.v_lab

    if "lab_temp" not in st.session_state:
        st.session_state.lab_temp = ""
    if "sosa_id_atual" not in st.session_state:
        st.session_state.sosa_id_atual = ""
    if "lab_meta" not in st.session_state:
        st.session_state.lab_meta = {}

    tab_criar, tab_acervo_aulas = st.tabs(["Forja de Aula (Tríade SOSA)", "Acervo de Aulas Prontas"])

    # --------------------------------------------------------------------------
    # ABA 1: FORJA DE AULA (TRÍADE SOSA)
    # --------------------------------------------------------------------------
    with tab_criar:
        with st.container(border=True):
            st.markdown("#### 1. Parâmetros da Aula & Vinculação Curricular")
            
            c_l1, c_l2, c_l3, c_l4 = st.columns([1, 1.2, 1.5, 1.5])
            ano_lab = c_l1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_lab_{v_l}")
            trim_lab = c_l2.segmented_control("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], default="I Trimestre", key=f"trim_lab_{v_l}")
            if not trim_lab: trim_lab = "I Trimestre"

            origem_lab = c_l3.selectbox("Origem do Conteúdo:", ["Plano do Ponto ID (Hub Ativo)", "Livro Didático (Cofre Digital)", "Tema Livre / Autoral"], key=f"orig_lab_{v_l}")
            tipo_aula_lab = c_l4.selectbox("Tipo de Material:", ["Aula 1 (Conceito & Prática)", "Aula 2 (Fixação & Exercícios)", "Sábado Letivo (Oficina)", "Aula Única"], key=f"tipo_lab_{v_l}")

        # Configurações de Origem
        contexto_plano_lab = ""
        uri_livro_lab = None
        texto_teoria_lab = ""
        texto_exercicios_lab = ""

        if origem_lab == "Plano do Ponto ID (Hub Ativo)":
            planos_ativos_ano = df_planos[(df_planos['ANO'] == f"{ano_lab}º") & (df_planos['TURMA'] == trim_lab)] if not df_planos.empty else pd.DataFrame()
            if planos_ativos_ano.empty:
                st.info(f"Nenhum plano cadastrado no Ponto ID para o {ano_lab}º Ano ({trim_lab}). Você pode forjar via Livro Didático ou Tema Livre.")
            else:
                opcoes_planos = [f"{r['SEMANA']} — {ai.extrair_tag(str(r['PLANO_TEXTO']), 'OBJETO_CONHECIMENTO') or 'Plano'}" for _, r in planos_ativos_ano.iterrows()]
                sel_plano_hub = st.selectbox("Selecione o Plano Base:", opcoes_planos, key=f"sel_plano_hub_{v_l}")
                
                if sel_plano_hub:
                    idx_p = opcoes_planos.index(sel_plano_hub)
                    row_plano_sel = planos_ativos_ano.iloc[idx_p]
                    contexto_plano_lab = str(row_plano_sel.get('PLANO_TEXTO', ''))
                    semana_ref_lab = str(row_plano_sel.get('SEMANA', 'Semana Geral'))

        elif origem_lab == "Livro Didático (Cofre Digital)":
            semana_ref_lab = st.text_input("Identificador da Semana (ex: Semana 05):", value="Semana 01", key=f"sem_ref_livro_{v_l}")
            livros_disp_lab = df_materiais[df_materiais['TIPO'].str.contains(str(ano_lab), na=False)]['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
            
            c_liv1, c_liv2, c_liv3 = st.columns([2, 1, 1])
            sel_livro_f = c_liv1.selectbox("Livro Didático:", [""] + livros_disp_lab, key=f"sel_liv_f_{v_l}")
            pags_teo_f = c_liv2.text_input("Páginas de Teoria:", placeholder="Ex: 184-186", key=f"pags_teo_f_{v_l}")
            pags_ex_f = c_liv3.text_input("Páginas de Exercícios:", placeholder="Ex: 187-188", key=f"pags_ex_f_{v_l}")

            if sel_livro_f:
                uri_livro_lab = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_livro_f].iloc[0]['URI_ARQUIVO']
                list_p_teo = util.processar_intervalos_paginas(pags_teo_f)
                list_p_ex = util.processar_intervalos_paginas(pags_ex_f)
                
                if list_p_teo or list_p_ex:
                    with st.spinner("Fatiando páginas selecionadas do livro didático..."):
                        bytes_pdf_l = db.baixar_bytes_arquivo_drive(uri_livro_lab)
                        if bytes_pdf_l:
                            if list_p_teo: texto_teoria_lab = util.extrair_texto_pdf_por_paginas(bytes_pdf_l, list_p_teo)
                            if list_p_ex: texto_exercicios_lab = util.extrair_texto_pdf_por_paginas(bytes_pdf_l, list_p_ex)
        else:
            semana_ref_lab = st.text_input("Identificador da Semana:", value="Semana 01", key=f"sem_ref_livre_{v_l}")
            tema_autoral_txt = st.text_area("Tema da Aula & Diretrizes Pedagógicas:", placeholder="Ex: Operações com frações aplicadas a receitas culinárias regionais de Itabuna...", height=80, key=f"ta_autoral_{v_l}")
            contexto_plano_lab = f"[OBJETO_CONHECIMENTO] {tema_autoral_txt}\n[CONTEUDOS_ESPECIFICOS] {tema_autoral_txt}"

        recorte_adicional_lab = st.text_area(
            "Exercícios Adicionais ou Anotações do Quadro (Opcional):",
            placeholder="Insira exercícios adicionais que deseja incluir na folha do estudante...",
            height=70, key=f"recorte_add_lab_{v_l}"
        )

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Forjar Aula com IA (Tríade SOSA)", type="primary", use_container_width=True, key=f"btn_forjar_aula_{v_l}"):
            with st.status("Forjando materiais estruturados com IA...", expanded=True) as status_forja:
                dna_sosa = util.gerar_sosa_id("AULA", ano_lab, trim_lab)
                st.session_state.sosa_id_atual = dna_sosa

                pacote_contexto = ""
                if contexto_plano_lab: pacote_contexto += f"--- PLANO DE AULA ---\n{contexto_plano_lab}\n\n"
                if texto_teoria_lab: pacote_contexto += f"--- TEORIA DO LIVRO DIDÁTICO ---\n{texto_teoria_lab}\n\n"
                if texto_exercicios_lab: pacote_contexto += f"--- EXERCÍCIOS DO LIVRO ---\n{texto_exercicios_lab}\n\n"
                if recorte_adicional_lab.strip(): pacote_contexto += f"--- ANOTAÇÕES DO PROFESSOR ---\n{recorte_adicional_lab.strip()}\n\n"

                # 1. Guia Docente de Lousa
                status_forja.write("1/3 Estruturando Guia Docente de Lousa (Início, Meio, Fim)...")
                prompt_prof = (
                    f"SÉRIE: {ano_lab}º Ano. TRIMESTRE: {trim_lab}. TIPO DE AULA: {tipo_aula_lab}.\n"
                    f"ESTRUTURA: [PROFESSOR] com INÍCIO (Gatilho 10 min), MEIO (Fundamentação & Livro 25 min) e FIM (Exercícios no Quadro 15 min).\n\n"
                    f"CONTEXTO:\n{pacote_contexto}"
                )
                txt_prof_res = ai.gerar_ia("FORJA_AULA_TEORIA", prompt_prof, url_drive=uri_livro_lab, usar_busca=False)

                # 2. Folha do Estudante & Gabarito
                status_forja.write("2/3 Estruturando Folha do Estudante com Tabelas Markdown...")
                prompt_alu = (
                    f"SÉRIE: {ano_lab}º Ano. TRIMESTRE: {trim_lab}.\n"
                    f"MISSÃO: Crie a lista de exercícios para os alunos regulares ([ALUNO]) com tabelas Markdown quando houver dados e o gabarito comentado ([GABARITO]).\n\n"
                    f"CONTEXTO:\n{pacote_contexto}"
                )
                txt_alu_res = ai.gerar_ia("FORJA_AULA_EXERCICIOS", prompt_alu, url_drive=uri_livro_lab, usar_busca=False)

                # 3. Adaptações Inclusivas PEI
                status_forja.write("3/3 Estruturando Tríade PEI On-Demand (N1, N2 e 10 Bento Boxes N3 no Papel)...")
                prompt_pei = (
                    f"SÉRIE: {ano_lab}º Ano.\n"
                    f"MISSÃO: Adapte os exercícios regulares abaixo para PEI Nível 1 ([PEI_NIVEL_1] - 3 opções A, B, C), PEI Nível 2 ([PEI_NIVEL_2] - Passo a Passo) e PEI Nível 3 ([PEI_NIVEL_3] - 10 Bento Boxes de ações no papel: pintar, ligar, cobrir pontilhado) + [RUBRICA_DE_OBSERVACAO] e [GABARITO_PEI].\n\n"
                    f"EXERCÍCIOS REGULARES:\n{ai.extrair_tag(txt_alu_res, 'ALUNO') or txt_alu_res}"
                )
                txt_pei_res = ai.gerar_ia("FORJA_AULA_PEI", prompt_pei, usar_busca=False)

                conteudo_final_forja = f"[SOSA_ID: {dna_sosa}]\n\n{txt_prof_res}\n\n{txt_alu_res}\n\n{txt_pei_res}"
                st.session_state.lab_temp = conteudo_final_forja
                st.session_state.lab_meta = {
                    "ano": f"{ano_lab}º",
                    "trimestre": trim_lab,
                    "semana": semana_ref_lab if 'semana_ref_lab' in locals() else "Semana Geral",
                    "tipo_aula": tipo_aula_lab,
                    "sosa_id": dna_sosa
                }
                status_forja.update(label="Tríade de Materiais forjada com sucesso!", state="complete")
                st.balloons(); time.sleep(0.6); st.rerun()

        # Mesa de Edição da Aula Forjada
        if st.session_state.lab_temp:
            txt_lab_atual = st.session_state.lab_temp
            meta_lab = st.session_state.get("lab_meta", {})
            
            st.markdown("---")
            st.markdown(f"### Mesa de Lapidação da Aula — `{meta_lab.get('sosa_id', 'DNA-SOSA')}`")
            
            t_guia, t_folha, t_gab, t_pei_lab, t_sync_lab = st.tabs([
                "Guia Docente (Lousa)", "Folha do Estudante", "Gabarito Comentado", "Adaptações PEI", "Sincronização Drive"
            ])

            with t_guia:
                ed_prof_lab = st.text_area("Roteiro do Professor ([PROFESSOR]):", ai.extrair_tag(txt_lab_atual, "PROFESSOR") or txt_lab_atual, height=340, key=f"ta_guia_{v_l}")
            
            with t_folha:
                ed_alu_lab = st.text_area("Folha do Estudante ([ALUNO]):", ai.extrair_tag(txt_lab_atual, "ALUNO"), height=340, key=f"ta_folha_{v_l}")
            
            with t_gab:
                ed_gab_lab = st.text_area("Gabarito Comentado ([GABARITO]):", ai.extrair_tag(txt_lab_atual, "GABARITO") or ai.extrair_tag(txt_lab_atual, "GABARITO_TEXTO"), height=240, key=f"ta_gab_{v_l}")

            with t_pei_lab:
                t_p1_l, t_p2_l, t_p3_l = st.tabs(["PEI Nível 1", "PEI Nível 2", "PEI Nível 3 (Bento Boxes)"])
                with t_p1_l:
                    ed_p1_lab = st.text_area("PEI N1 (3 Alternativas A, B, C):", ai.extrair_tag(txt_lab_atual, "PEI_NIVEL_1"), height=260, key=f"ta_p1_{v_l}")
                with t_p2_l:
                    ed_p2_lab = st.text_area("PEI N2 (Passo a Passo):", ai.extrair_tag(txt_lab_atual, "PEI_NIVEL_2"), height=260, key=f"ta_p2_{v_l}")
                with t_p3_l:
                    ed_p3_lab = st.text_area("PEI N3 (10 Boxes no Papel):", ai.extrair_tag(txt_lab_atual, "PEI_NIVEL_3"), height=260, key=f"ta_p3_{v_l}")

            with t_sync_lab:
                st.markdown("#### Custódia & Sincronização Google Drive")
                st.caption("Compilação automática dos documentos oficiais Word (.docx) com cabeçalhos institucionais.")

                nome_base_lab = f"AULA_{meta_lab.get('tipo_aula','AULA').replace(' ','_')}_{meta_lab.get('ano','6º').replace('º','')}_{datetime.now().strftime('%d%m')}"
                nome_arq_sync = st.text_input("Identificador do Arquivo no Drive:", value=nome_base_lab, key=f"inp_sync_name_{v_l}")

                if st.button("Sincronizar Todos os Materiais no Google Drive", type="primary", use_container_width=True, key=f"btn_sync_aula_drive_{v_l}"):
                    with st.status("Compilando arquivos oficiais e sincronizando no Drive...", expanded=True) as status_sync:
                        info_exp_lab = {
                            "ano": meta_lab.get("ano", "6º"),
                            "trimestre": meta_lab.get("trimestre", "I Trimestre"),
                            "semana": meta_lab.get("semana", "Semana Geral")
                        }

                        # 1. Folha do Estudante Regular DOCX
                        status_sync.write("Compilando Folha do Estudante DOCX...")
                        doc_alu = exporter.gerar_docx_aluno_v24(nome_arq_sync, ed_alu_lab, info_exp_lab)
                        link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_arq_sync}_ALUNO", trimestre=info_exp_lab['trimestre'], categoria=info_exp_lab['ano'], semana=info_exp_lab['semana'], modo="AULA")

                        # 2. Guia Docente DOCX
                        status_sync.write("Compilando Guia Docente DOCX...")
                        doc_prof = exporter.gerar_docx_professor_v25(nome_arq_sync, ed_prof_lab, info_exp_lab)
                        link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_arq_sync}_PROF", trimestre=info_exp_lab['trimestre'], categoria=info_exp_lab['ano'], semana=info_exp_lab['semana'], modo="AULA")

                        # 3. PEI Nível 1 DOCX
                        link_p1 = "N/A"
                        if ed_p1_lab:
                            status_sync.write("Compilando PEI Nível 1 DOCX...")
                            doc_p1 = exporter.gerar_docx_pei_v25(f"{nome_arq_sync}_PEI_N1", ed_p1_lab, info_exp_lab)
                            link_p1 = db.subir_e_converter_para_google_docs(doc_p1, f"{nome_arq_sync}_PEI_N1", trimestre=info_exp_lab['trimestre'], categoria=info_exp_lab['ano'], semana=info_exp_lab['semana'], modo="AULA")

                        # 4. PEI Nível 3 DOCX
                        link_p3 = "N/A"
                        if ed_p3_lab:
                            status_sync.write("Compilando PEI Nível 3 DOCX (10 Bento Boxes)...")
                            doc_p3 = exporter.gerar_docx_pei_qualitativa(f"{nome_arq_sync}_PEI_N3", ed_p3_lab, info_exp_lab)
                            link_p3 = db.subir_e_converter_para_google_docs(doc_p3, f"{nome_arq_sync}_PEI_N3", trimestre=info_exp_lab['trimestre'], categoria=info_exp_lab['ano'], semana=info_exp_lab['semana'], modo="AULA")

                        links_final_str = f"--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI_N1({link_p1}) PEI_N3({link_p3})"

                        conteudo_banco_aula = (
                            f"[SOSA_ID: {meta_lab.get('sosa_id', 'DNA')}]\n\n"
                            f"[PROFESSOR]\n{ed_prof_lab}\n\n"
                            f"[ALUNO]\n{ed_alu_lab}\n\n"
                            f"[GABARITO]\n{ed_gab_lab}\n\n"
                            f"[PEI_NIVEL_1]\n{ed_p1_lab}\n\n"
                            f"[PEI_NIVEL_2]\n{ed_p2_lab}\n\n"
                            f"[PEI_NIVEL_3]\n{ed_p3_lab}\n\n"
                            f"{links_final_str}"
                        )

                        # Remove duplicatas e salva no banco
                        db.excluir_aula_pronta_canonica(info_exp_lab['semana'], meta_lab.get('tipo_aula', 'Aula'), info_exp_lab['ano'])
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), info_exp_lab['semana'],
                            f"{meta_lab.get('tipo_aula', 'Aula')} - {nome_arq_sync}",
                            conteudo_banco_aula, info_exp_lab['ano'], link_alu
                        ])

                        # Arquiva o plano no Ponto ID como PRODUZIDO
                        db.arquivar_plano_produzido(info_exp_lab['semana'], info_exp_lab['ano'])

                        status_sync.update(label="Material sincronizado e homologado no Google Drive!", state="complete")
                        st.balloons(); time.sleep(0.8); st.rerun()

    # --------------------------------------------------------------------------
    # ABA 2: ACERVO DE AULAS PRONTAS
    # --------------------------------------------------------------------------
    with tab_acervo_aulas:
        st.markdown("### Acervo de Aulas & Roteiros Prontos")
        st.caption("Consulte materiais de aula já forjados, baixe documentos DOCX e acesse os links no Google Drive.")

        df_aulas_reais = df_aulas[~df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "AVALIACAO", "REVISÃO"])].copy() if not df_aulas.empty else pd.DataFrame()
        
        if df_aulas_reais.empty:
            st.info("Nenhuma aula cadastrada no acervo.")
        else:
            c_f_a1, c_f_a2 = st.columns(2)
            f_ano_ac_aula = c_f_a1.segmented_control("Filtrar Série:", ["Todas", "6º", "7º", "8º", "9º"], default="Todas", key=f"f_ano_ac_a_{v_l}")
            
            df_aulas_view = df_aulas_reais.copy()
            if f_ano_ac_aula != "Todas":
                df_aulas_view = df_aulas_view[df_aulas_view['ANO'].astype(str).str.contains(f_ano_ac_aula.replace("º",""))]

            for _, row_aula in df_aulas_view.iloc[::-1].iterrows():
                with st.container(border=True):
                    tit_aula = str(row_aula.get('TIPO_MATERIAL', 'Aula'))
                    sem_aula = str(row_aula.get('SEMANA_REF', 'Semana'))
                    ano_aula = str(row_aula.get('ANO', '6º'))
                    data_aula = str(row_aula.get('DATA', 'N/A'))
                    txt_aula_c = str(row_aula.get('CONTEUDO', ''))

                    c_a_h1, c_a_h2 = st.columns([3, 1])
                    c_a_h1.markdown(f"#### {tit_aula}")
                    c_a_h1.caption(f"Série: **{ano_aula}** | Semana: **{sem_aula}** | Data: **{data_aula}**")

                    # Extração de Links
                    def extrair_link_safe(t, tag):
                        m = re.search(rf"{tag}\s*\(\s*(https://docs\.google\.com/document/d/[^\s\)]+)\s*\)", t, re.IGNORECASE)
                        return m.group(1).strip() if m else None

                    l_alu = extrair_link_safe(txt_aula_c, "Aluno") or row_aula.get('LINK_DRIVE')
                    l_prof = extrair_link_safe(txt_aula_c, "Prof")
                    l_p1 = extrair_link_safe(txt_aula_c, "PEI_N1") or extrair_link_safe(txt_aula_c, "PEI")
                    l_p3 = extrair_link_safe(txt_aula_c, "PEI_N3")

                    c_l_btns = st.columns(4)
                    if l_alu and "http" in str(l_alu): c_l_btns[0].link_button("Folha do Estudante", str(l_alu), type="primary", use_container_width=True)
                    if l_prof and "http" in str(l_prof): c_l_btns[1].link_button("Guia Docente", str(l_prof), use_container_width=True)
                    if l_p1 and "http" in str(l_p1): c_l_btns[2].link_button("PEI Nível 1", str(l_p1), use_container_width=True)
                    if l_p3 and "http" in str(l_p3): c_l_btns[3].link_button("PEI Nível 3", str(l_p3), use_container_width=True)

                    with st.expander("Visualizar Conteúdo da Aula", expanded=False):
                        st.markdown(preparar_para_leitura(ai.extrair_tag(txt_aula_c, "PROFESSOR") or txt_aula_c[:1200]))







# ==============================================================================
# MÓDULO: CENTRAL DE AVALIAÇÕES - V2026.PRO_INFINITY_ULTIMATE
# (FORJA DISCURSIVA PARA RECUPERAÇÃO, ITENS TRI, PEI E CONEXÃO COM SCANNER CIR)
# ==============================================================================
elif menu == "📝 Central de Avaliações":
    st.title("Central de Avaliações")
    st.caption("Arquitetura de instrumentos avaliativos: linha de montagem, recuperação paralela discursiva vinculada, perícia psicométrica TRI e dashboard visual de impressão.")
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
            ("1. Parâmetros", 1),
            ("2. Caderno Regular", 2),
            ("3. Adaptação PEI", 3),
            ("4. Sincronização", 4),
            ("5. Conclusão", 5)
        ]
        html_steps = []
        for nome, f_num in etapas:
            if fase_atual == f_num:
                color = "#2962FF"; f_weight = "bold"; border = "border-bottom: 3px solid #2962FF;"
            elif fase_atual > f_num:
                color = "#2ECC71"; f_weight = "bold"; border = "border-bottom: 3px solid #2ECC71;"
            else:
                color = "gray"; f_weight = "normal"; border = "border-bottom: 3px solid #334155;"
            html_steps.append(f"<div style='flex: 1; text-align: center; padding-bottom: 6px; color: {color}; font-weight: {f_weight}; font-size: 13px; {border}'>{nome}</div>")
        st.markdown(f"<div style='display: flex; justify-content: space-between; margin-bottom: 20px;'>{''.join(html_steps)}</div>", unsafe_allow_html=True)

    tab_forja, tab_acervo_av, tab_recomposicao, tab_expedicao = st.tabs([
        "Linha de Montagem", 
        "Acervo de Avaliações", 
        "Recomposição de Aprendizagem",
        "Dashboard de Impressão (Cópias)"
    ])

    # ==============================================================================
    # ABA 1: LINHA DE MONTAGEM DE PROVAS & RECUPERAÇÃO DISCURSIVA
    # ==============================================================================
    with tab_forja:
        if 1 < f['fase'] <= 5:
            render_indicador_fases(f['fase'])
            if st.button("Descartar Produção e Retornar ao Início", use_container_width=True, key=f"btn_disc_av_{v}"): 
                reset_forja()
            st.markdown("---")

        if f['fase'] == 1:
            st.markdown("### Parâmetros e Seleção Curricular")
            st.caption("Defina os critérios psicométricos e selecione os objetos de conhecimento ministrados em sala de aula.")
            
            modo_arq = st.segmented_control(
                "Abordagem do Instrumento:", 
                ["Avaliação Regular", "Segunda Chamada", "Variante Tipo B", "Recuperação Paralela", "Recuperação Final (Anual)"], 
                default="Recuperação Paralela" if "recuperacao" in str(st.session_state.get("menu_sub_modo", "")).lower() else "Avaliação Regular",
                key=f"pills_modo_av_{v}"
            )
            st.markdown("---")

            is_rec_final = (modo_arq == "Recuperação Final (Anual)")
            is_2a_chamada = (modo_arq == "Segunda Chamada")
            is_rec_paralela = (modo_arq == "Recuperação Paralela")
            is_variante = (modo_arq == "Variante Tipo B")

            # SEGUNDA CHAMADA VINCULADA
            if is_2a_chamada:
                with st.container(border=True):
                    st.markdown("#### Configuração de Segunda Chamada Vinculada")
                    st.caption("Selecione a avaliação oficial que os estudantes perderam. O sistema herda a pontuação e disponibiliza os cadernos PEI automaticamente:")
                    
                    c_sc1, c_sc2, c_sc3 = st.columns([1, 1.2, 2])
                    ano_sc = c_sc1.selectbox("Série Alvo:", [6, 7, 8, 9], key=f"ano_sc_sel_{v}")
                    trim_sc = c_sc2.segmented_control("Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], default="Todos", key=f"trim_sc_filter_{v}")
                    if not trim_sc: trim_sc = "Todos"

                    termos_busca_exames = r"(?i)(?:AVALIA[CÇ][AÃ]O|PROVA|TESTE|SONDA|EXAME)"
                    termos_ignorar_origem = r"(?i)(?:2[ªA]|CHAMADA|TIPO\s+[B-Z]|REVISAO_LACUNAS|DOSSI[EÊ])"

                    opcoes_encontradas_sc = set()
                    if not df_aulas.empty and 'ANO' in df_aulas.columns and 'TIPO_MATERIAL' in df_aulas.columns:
                        df_ano_aulas = df_aulas[df_aulas['ANO'].astype(str).str.contains(str(ano_sc))]
                        for _, r_a in df_ano_aulas.iterrows():
                            mat_nome = str(r_a.get('TIPO_MATERIAL', '')).strip()
                            sem_ref_n = str(r_a.get('SEMANA_REF', '')).strip()
                            conteudo_txt = str(r_a.get('CONTEUDO', ''))
                            if (re.search(termos_busca_exames, mat_nome) or sem_ref_n.upper() in ["AVALIAÇÃO", "AVALIACAO"]) and not re.search(termos_ignorar_origem, mat_nome):
                                if trim_sc == "Todos" or re.search(util.obter_regex_trimestre(trim_sc), mat_nome) or re.search(util.obter_regex_trimestre(trim_sc), conteudo_txt):
                                    opcoes_encontradas_sc.add(mat_nome)

                    opcoes_provas_sc = sorted(list(opcoes_encontradas_sc))
                    prova_origem_sc = c_sc3.selectbox("Avaliação Oficial de Origem (Prova Perdida):", [""] + opcoes_provas_sc, key=f"p_origem_sc_sel_{v}")

                if prova_origem_sc:
                    match_sc = df_aulas[(df_aulas['ANO'].astype(str).str.contains(str(ano_sc))) & (df_aulas['TIPO_MATERIAL'] == prova_origem_sc)] if not df_aulas.empty else pd.DataFrame()
                    txt_origem_sc = str(match_sc.iloc[0].get('CONTEUDO', '')) if not match_sc.empty else ""
                    val_origem = util.extrair_valor_real_prova(txt_origem_sc, prova_origem_sc)
                    q_origem_raw = ai.extrair_tag(txt_origem_sc, "QUESTOES") or txt_origem_sc
                    qtd_detectada_sc = len(re.findall(r"(?i)QUESTÃO\s*0?\d+", q_origem_raw)) or 10

                    with st.container(border=True):
                        st.markdown(f"##### Diagnóstico da Avaliação de Origem: **{prova_origem_sc}**")
                        c_inf1, c_inf2, c_inf3 = st.columns(3)
                        c_inf1.metric("Pontuação Herdada", f"{val_origem:.1f} pts")
                        c_inf2.metric("Itens da Prova", f"{qtd_detectada_sc} questões")
                        c_inf3.metric("Cadernos PEI", "Reuso Automático no Drive")

                    nome_segunda_chamada = f"2ª_CHAMADA_{prova_origem_sc}"
                    if st.button("Gerar Caderno de 2ª Chamada Regular", type="primary", use_container_width=True, key=f"btn_gen_2a_chamada_exe_{v}"):
                        with st.status("Forjando questões espelho inéditas para a 2ª Chamada...", expanded=True) as status_sc:
                            prompt_sc = (
                                f"PROVA ORIGINAL DE ORIGEM:\n{txt_origem_sc}\n\n"
                                f"SÉRIE: {ano_sc}º Ano.\n"
                                f"VALOR TOTAL: {val_origem} pontos.\n"
                                f"MISSÃO: Crie a SEGUNDA CHAMADA para estudantes regulares baseada EXCLUSIVAMENTE nos mesmos descritores da prova original, com dados numéricos inéditos (questões espelho).\n"
                                f"Gere as tags: [VALOR: {val_origem}], [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO]."
                            )
                            res_sc = ai.gerar_ia("ARQUITETO_RECUPERACAO_DISCURSIVA", prompt_sc, usar_busca=False)
                            texto_final_2a = f"[VALOR: {val_origem}]\n\n[QUESTOES]\n{ai.extrair_tag(res_sc, 'QUESTOES') or res_sc}\n\n[GABARITO_TEXTO]\n{ai.extrair_tag(res_sc, 'GABARITO_TEXTO')}\n\n[GRADE_DE_CORRECAO]\n{ai.extrair_tag(res_sc, 'GRADE_DE_CORRECAO')}\n\n"
                            
                            trim_sc_str = 'I Trimestre' if 'ITrimestre' in prova_origem_sc else ('II Trimestre' if 'IITrimestre' in prova_origem_sc else 'III Trimestre')
                            info_sc_doc = {'ano': f"{ano_sc}º", 'trimestre': trim_sc_str, 'valor': str(val_origem), 'tipo_prova': '2ª CHAMADA', 'qtd': qtd_detectada_sc}
                            
                            doc_2a = exporter.gerar_docx_prova_v25(nome_segunda_chamada, texto_final_2a, info_sc_doc)
                            link_2a = db.subir_e_converter_para_google_docs(doc_2a, nome_segunda_chamada, modo="AVALIACAO")
                            
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_segunda_chamada,
                                texto_final_2a + f"\n--- LINKS ---\nRegular({link_2a})", f"{ano_sc}º", link_2a
                            ])
                            status_sc.update(label="Segunda Chamada gerada e sincronizada no Google Drive!", state="complete")
                            st.balloons(); time.sleep(0.8); st.rerun()

            # REGULAR / RECUPERAÇÃO PARALELA / RECUPERAÇÃO FINAL
            elif "Regular" in modo_arq or "Sonda" in modo_arq or is_rec_paralela or is_rec_final:
                with st.container(border=True):
                    st.markdown("#### 1. Parâmetros da Turma & Pontuação Oficial")
                    c1, c2, c3, c4 = st.columns(4)
                    ano_av = c1.selectbox("Série Alvo:", [6, 7, 8, 9], index=0, key=f"ano_av_sel_{v}")
                    
                    if is_rec_final:
                        trim_filtro = "Anual (I, II e III Trimestres)"
                        c2.text_input("Escopo:", value="Ano Completo (I, II e III Tri)", disabled=True)
                        v_total = c3.number_input("Pontuação Total:", 0.0, 10.0, 10.0, disabled=True, key=f"v_tot_input_{v}")
                    elif is_rec_paralela:
                        trim_filtro = c2.selectbox("Trimestre:", ["II Trimestre", "I Trimestre", "III Trimestre"], index=0, key=f"trim_av_sel_{v}")
                        v_total = c3.number_input("Pontuação Total (Escala 0 a 10):", 0.0, 10.0, 10.0, disabled=True, key=f"v_tot_input_{v}")
                    else:
                        trim_filtro = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"trim_av_sel_{v}")
                        v_total = c3.number_input("Pontuação Total:", 0.0, 10.0, 4.0, step=0.5, key=f"v_tot_input_{v}")
                    
                    qtd_q = c4.number_input("Quantidade de Questões:", 1, 30, 10, key=f"qtd_q_input_{v}")

                    if is_rec_paralela:
                        st.info("ℹ️ **Recuperação Paralela Discursiva (0 a 10 pontos):** Questões abertas para os alunos regulares e prova adaptada (A, B, C e 10 Bento Boxes) para alunos PEI. A nota comporá a fórmula oficial com arredondamento 0,5.")
                        perfil_rigor = "Recuperação Paralela Discursiva"
                    elif is_rec_final:
                        st.info("ℹ️ **Recuperação Final Anual:** Escopo de todo o ano letivo (10,0 pts).")
                        perfil_rigor = "Recuperação Final Anual"
                    else:
                        perfil_rigor = st.segmented_control(
                            "Equilíbrio TRI:", 
                            ["Padrão SAEB (30% Fácil | 50% Médio | 20% Difícil)", "Olimpíada / Aprofundamento", "Recomposição (Acessível)"], 
                            default="Padrão SAEB (30% Fácil | 50% Médio | 20% Difícil)",
                            key=f"rigor_pop_{v}"
                        )

                with st.container(border=True):
                    st.markdown("#### 2. Fontes Curriculares & Prova de Origem")
                    
                    txt_av_origem_puxada = ""
                    topicos_extraidos_da_prova = []
                    
                    if is_rec_paralela:
                        padrao_trim_rec = util.obter_regex_trimestre(trim_filtro)
                        termos_busca_exames_rec = r"(?i)(?:AVALIA[CÇ][AÃ]O|PROVA|TESTE|SIMULADO|EXAME|REVISAO|REVISÃO)"
                        
                        opcoes_provas_para_rec_set = set()
                        if not df_aulas.empty and 'ANO' in df_aulas.columns and 'TIPO_MATERIAL' in df_aulas.columns:
                            df_ano_aulas_rec = df_aulas[df_aulas['ANO'].astype(str).str.contains(str(ano_av))]
                            for _, r_a in df_ano_aulas_rec.iterrows():
                                mat_nome = str(r_a.get('TIPO_MATERIAL', '')).strip()
                                sem_ref_n = str(r_a.get('SEMANA_REF', '')).strip()
                                conteudo_txt = str(r_a.get('CONTEUDO', ''))
                                
                                if re.search(termos_busca_exames_rec, mat_nome) or sem_ref_n.upper() in ["AVALIAÇÃO", "AVALIACAO", "REVISÃO"]:
                                    if re.search(padrao_trim_rec, mat_nome) or re.search(padrao_trim_rec, conteudo_txt) or re.search(padrao_trim_rec, sem_ref_n):
                                        opcoes_provas_para_rec_set.add(mat_nome)

                        opcoes_provas_para_rec = sorted(list(opcoes_provas_para_rec_set))
                        
                        c_p_rec1, c_p_rec2 = st.columns([2.5, 1])
                        prova_rec_base_sel = c_p_rec1.selectbox(
                            "Avaliação / Teste de Origem a ser Recuperado:",
                            [""] + opcoes_provas_para_rec,
                            key=f"sel_prova_rec_orig_{v}",
                            help="Selecione a avaliação oficial para minerar automaticamente os itens e descritores."
                        )
                        
                        if prova_rec_base_sel:
                            m_orig = df_aulas[(df_aulas['ANO'].astype(str).str.contains(str(ano_av))) & (df_aulas['TIPO_MATERIAL'] == prova_rec_base_sel)]
                            if not m_orig.empty:
                                txt_av_origem_puxada = str(m_orig.iloc[0].get('CONTEUDO', ''))
                                c_p_rec2.success("Prova Minerada!")
                                
                                grade_orig_p = ai.extrair_tag(txt_av_origem_puxada, "GRADE_DE_CORRECAO") or ai.extrair_tag(txt_av_origem_puxada, "GRADE_DE_CORRECAO_PEI")
                                if grade_orig_p:
                                    itens_grade = re.findall(r'(?i)(?:DESCRITOR_SAEB|HABILIDADE|BNCC|DESCRITOR)\s*:\s*([^|\]\n]+)', grade_orig_p)
                                    for ig in itens_grade:
                                        ig_clean = re.sub(r'[*#\[\]]', '', ig).strip()
                                        if len(ig_clean) > 3 and ig_clean not in topicos_extraidos_da_prova:
                                            topicos_extraidos_da_prova.append(ig_clean)
                                            
                                if not topicos_extraidos_da_prova:
                                    questoes_orig_raw = ai.extrair_tag(txt_av_origem_puxada, "QUESTOES")
                                    if questoes_orig_raw:
                                        linhas_q = [l.strip() for l in questoes_orig_raw.split('\n') if l.strip().upper().startswith('**QUESTÃO')]
                                        for lq in linhas_q:
                                            lq_clean = re.sub(r'^\*\*QUEST[AÃ]O\s*\d+.*?\*\*\s*[-:]*\s*', '', lq).strip()
                                            t_curto = lq_clean.split('.')[0][:75].strip()
                                            if t_curto and t_curto not in topicos_extraidos_da_prova:
                                                topicos_extraidos_da_prova.append(t_curto)

                    fontes_ativas = st.pills(
                        "Fontes Complementares:", 
                        ["Acervo de Aulas SOSA", "Livro Didático (PDF)", "Exercícios Complementares"], 
                        default=["Acervo de Aulas SOSA"],
                        selection_mode="multi",
                        key=f"pills_fontes_av_{v}"
                    )
                    
                    txt_av_teo_ext = ""
                    if "Livro Didático (PDF)" in fontes_ativas:
                        livros_av_disp = df_materiais[df_materiais['TIPO'].str.contains(str(ano_av), na=False)]['NOME_ARQUIVO'].tolist() if not df_materiais.empty else []
                        c_safra1, c_safra2 = st.columns(2)
                        sel_livro_av = c_safra2.selectbox("Livro do Cofre Digital:", [""] + livros_av_disp, key=f"sel_livro_av_{v}")
                        
                        if sel_livro_av:
                            uri_livro_av = df_materiais[df_materiais['NOME_ARQUIVO'] == sel_livro_av].iloc[0]['URI_ARQUIVO']
                            pags_teo_av = st.text_input("Páginas do Livro (Teoria e Exercícios):", placeholder="Ex: 132-191", key=f"pags_teo_av_{v}")
                            list_p_av = util.processar_intervalos_paginas(pags_teo_av)
                            if list_p_av:
                                with st.spinner("Fatiando páginas do livro..."):
                                    bytes_pdf_av = db.baixar_bytes_arquivo_drive(uri_livro_av)
                                    if bytes_pdf_av:
                                        txt_av_teo_ext = util.extrair_texto_pdf_por_paginas(bytes_pdf_av, list_p_av)

                    if topicos_extraidos_da_prova:
                        topicos_candidatos_unicos = topicos_extraidos_da_prova
                        texto_padrao_pratica = f"Recuperação Paralela (Escala 0 a 10) baseada nos itens da prova '{prova_rec_base_sel}'."
                    else:
                        topicos_candidatos_unicos = [
                            "Frações: Conceito de parte-todo, equivalência e leitura",
                            "Adição e Subtração de Frações com Denominadores Diferentes (MMC)",
                            "Multiplicação de Frações e Fração de uma Fração",
                            "Frações Impróprias e Conversão para Números Mistos",
                            "Divisão com Números na Forma Decimal",
                            "Cálculo de Perímetro e Área de Figuras Planas",
                            "Interpretação de Gráficos de Colunas, Barras e Tabelas"
                        ]
                        texto_padrao_pratica = "Recuperação Paralela - II Trimestre: Frações, Números Mistos, Decimais, Área/Perímetro e Gráficos."

                    st.markdown("##### Prática de Sala de Aula (Questões Espelho / Diretrizes)")
                    pincamento_pratica = st.text_area(
                        "Diretrizes da Recuperação:",
                        value=texto_padrao_pratica,
                        height=75, key=f"pincamento_pratica_input_{v}"
                    )

                    contexto_base_texto = ""
                    if txt_av_origem_puxada:
                        txt_limpo_origem = re.sub(r'\[\s*VALOR\s*[:\-]?\s*[\d\.,]+\s*\]', '[VALOR: 10.0]', txt_av_origem_puxada, flags=re.IGNORECASE)
                        contexto_base_texto += f"--- PROVA ORIGINAL A SER RECUPERADA (VALOR TOTAL: 10.0 PONTOS) ---\n{txt_limpo_origem}\n\n"
                    if pincamento_pratica.strip(): contexto_base_texto += f"--- DIRETRIZES DO PROFESSOR ---\n{pincamento_pratica.strip()}\n\n"
                    if txt_av_teo_ext: contexto_base_texto += f"--- CONTEÚDO DO LIVRO DIDÁTICO ---\n{txt_av_teo_ext}\n\n"

                with st.container(border=True):
                    st.markdown(f"#### 3. Conteúdos da Avaliação ({ano_av}º Ano)")
                    st.caption("Os conteúdos da prova selecionada já estão pré-marcados abaixo. Desmarque apenas o que não quiser cobrar:")
                    
                    assuntos_marcados_prof = st.multiselect(
                        "Conteúdos Selecionados para a Recuperação:",
                        options=topicos_candidatos_unicos,
                        default=topicos_candidatos_unicos[:min(qtd_q, len(topicos_candidatos_unicos))],
                        key=f"ms_topicos_prof_{v}"
                    )

                    topico_autoral_extra = st.text_input(
                        "Adicionar Conteúdo Específico (Opcional):",
                        placeholder="Ex: Operações com números decimais e cálculo de perímetro",
                        key=f"topico_extra_input_{v}"
                    )

                    if topico_autoral_extra.strip() and topico_autoral_extra.strip() not in assuntos_marcados_prof:
                        assuntos_marcados_prof.insert(0, topico_autoral_extra.strip())

            st.markdown("<br>", unsafe_allow_html=True)
            if "Regular" in modo_arq or "Sonda" in modo_arq or is_rec_paralela or is_rec_final:
                rotulo_btn_inicio = f"Iniciar Linha de Montagem ({modo_arq})"
                
                if st.button(rotulo_btn_inicio, type="primary", use_container_width=True, key=f"btn_fase1_av_{v}"):
                    if not assuntos_marcados_prof:
                        st.error("Selecione ao menos um conteúdo no painel acima.")
                    else:
                        gabarito_mestre = util.gerar_gabarito_balanceado(qtd_q)
                        mapa_inicial = []
                        tipo_prova_tag = "RECUPERAÇÃO FINAL" if is_rec_final else ("RECUPERAÇÃO" if is_rec_paralela else "AVALIAÇÃO")
                        valor_final_travado = 10.0 if (is_rec_paralela or is_rec_final) else v_total
                        
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
                        f['info'] = {
                            'ano': f"{ano_av}º", 
                            'trimestre': trim_filtro, 
                            'valor': valor_final_travado, 
                            'qtd': qtd_q, 
                            'tipo_prova': tipo_prova_tag, 
                            'rigor': perfil_rigor,
                            'is_rec_final': is_rec_final,
                            'is_rec_paralela': is_rec_paralela
                        }
                        f['contexto_base'] = contexto_base_texto 
                        f['pincamento_lousa'] = pincamento_pratica
                        f['fase'] = 2
                        st.rerun()

        # ======================================================================
        # FASE 2: FORJA DISCURSIVA / ABERTA
        # ======================================================================
        elif f['fase'] == 2:
            is_rec_paralela_fase2 = f['info'].get('is_rec_paralela', False)
            
            st.markdown(f"### Fase 2: Forja & Lapidação de Itens — `{f['info']['tipo_prova']}`")
            if is_rec_paralela_fase2:
                st.caption(f"✍️ **Modalidade Discursiva Aberta:** Questões com memória de cálculo (sem alternativas) valendo de 0,0 a {f['info']['valor']:.1f} pontos.")
            else:
                st.caption(f"Série: **{f['info']['ano']}** | Período: **{f['info']['trimestre']}** | Pontuação Total: **{f['info']['valor']:.1f} pts**")

            total_q = len(f['mapa'])
            valor_por_item = f['info']['valor'] / max(total_q, 1)

            with st.container(border=True):
                col_tri1, col_tri2, col_tri3 = st.columns(3)
                col_tri1.metric("Total de Questões", total_q)
                col_tri2.metric("Valor por Questão", f"{valor_por_item:.2f} pts")
                col_tri3.metric("Formato da Prova", "Discursiva Aberta" if is_rec_paralela_fase2 else "Objetiva Múltipla Escolha")

            pendentes = [item for item in f['mapa'] if item['status'] == 'pendente']

            if pendentes:
                rotulo_btn_lote = "Gerar Lote de Questões Discursivas Abertas com IA" if is_rec_paralela_fase2 else f"Gerar Lote de {len(pendentes)} Itens com IA"
                
                if st.button(rotulo_btn_lote, type="primary", use_container_width=True, key=f"btn_lote_av_{v}"):
                    with st.status("Estruturando itens abertos com memória de cálculo e perícia...", expanded=True) as status_lote:
                        if is_rec_paralela_fase2:
                            prompt_disc_rec = (
                                f"SÉRIE: {f['info']['ano']}\n"
                                f"VALOR TOTAL DA AVALIAÇÃO: {f['info']['valor']} pontos (Distribuir {valor_por_item:.2f} pts por questão).\n"
                                f"NATUREZA: AVALIAÇÃO DISCURSIVA / ABERTA DE RECUPERAÇÃO PARALELA.\n\n"
                                f"🚨 REGRAS INQUEBRÁVEIS:\n"
                                f"1. É ESTRITAMENTE PROIBIDO incluir alternativas de múltipla escolha (A, B, C, D, E). Todas as questões DEVEM ser abertas.\n"
                                f"2. Cada questão deve exigir do aluno a resolução por etapas, a apresentação da MEMÓRIA DE CÁLCULO e a declaração da RESPOSTA FINAL com unidade de medida.\n"
                                f"3. Utilize tabelas em Markdown quando houver dados comparativos.\n\n"
                                f"LISTA DE TÓPICOS PARA AS QUESTÕES:\n"
                            )
                            for item in pendentes:
                                prompt_disc_rec += f"QUESTÃO {item['q']:02d}: {item['tema']} (Valor: {valor_por_item:.2f} pts)\n"
                            
                            prompt_disc_rec += f"\n--- PROVA ORIGINAL DE REFERÊNCIA ---\n{f.get('contexto_base', '')}\n"
                            
                            status_lote.write("Processando questões abertas com Gemini 3.7 Flash...")
                            res_disc = ai.gerar_ia("ARQUITETO_RECUPERACAO_DISCURSIVA", prompt_disc_rec, usar_busca=False)
                            
                            texto_questoes_disc = ai.extrair_tag(res_disc, "QUESTOES") or res_disc
                            blocos_q = re.split(r"(?i)\*\*QUEST[AÃ]O\s*0?(\d+)[^\-\n]*[\-\:]\*\*", texto_questoes_disc)
                            
                            if len(blocos_q) > 2:
                                for idx_b in range(1, len(blocos_q), 2):
                                    q_nr = int(blocos_q[idx_b])
                                    q_enunciado = blocos_q[idx_b+1].strip()
                                    for item in f['mapa']:
                                        if item['q'] == q_nr:
                                            item['dados'] = {
                                                'ENUNCIADO': q_enunciado,
                                                'ALT_A': '', 'ALT_B': '', 'ALT_C': '', 'ALT_D': '', 'ALT_E': '',
                                                'HABILIDADE': item['tema'],
                                                'JUSTIFICATIVA': f"Resolução discursiva do item {q_nr}.",
                                                'DISTRATORES': "Critério de pontuação: Cálculo completo (100%), Erro de conta (50%), Sem cálculo (0%).",
                                                'GABARITO': 'DISCURSIVA'
                                            }
                                            item['status'] = 'revisao'
                            else:
                                for item in pendentes:
                                    item['dados'] = {
                                        'ENUNCIADO': f"Resolva o problema sobre {item['tema']}, apresentando todos os cálculos e a resposta final.",
                                        'ALT_A': '', 'ALT_B': '', 'ALT_C': '', 'ALT_D': '', 'ALT_E': '',
                                        'HABILIDADE': item['tema'],
                                        'JUSTIFICATIVA': 'Resolução discursiva aberta.',
                                        'DISTRATORES': 'Memória de cálculo obrigatória.',
                                        'GABARITO': 'DISCURSIVA'
                                    }
                                    item['status'] = 'revisao'

                        else:
                            prompt_lote = (
                                f"SÉRIE: {f['info']['ano']}\n"
                                f"VALOR TOTAL DA PROVA: {f['info']['valor']}\n\n"
                                f"DIRETRIZES DE ANCORAGEM:\n"
                                f"- Desenvolva cada questão focada no TEMA ESPECÍFICO atribuído.\n\n"
                            )
                            for item in pendentes:
                                prompt_lote += f"QUESTÃO {item['q']}:\n- TEMA: {item['tema']}\n- COMPLEXIDADE: {item['dificuldade']}\n- GABARITO: Letra {item['gabarito']}\n\n"
                            
                            prompt_lote += f"--- CONTEXTO E PROVA ORIGINAL ---\n{f.get('contexto_base', '')}\n"
                            
                            res_json = ai.gerar_ia_json("FORJA_LOTE_JSON", prompt_lote)
                            if "erro" in res_json:
                                st.error(f"Erro ao processar lote: {res_json['erro']}")
                            else:
                                for q_data in res_json.get("questoes", []):
                                    q_num = int(q_data.get("q", 0))
                                    for item in f['mapa']:
                                        if item['q'] == q_num:
                                            descritor_real = q_data.get('habilidade', '')
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
                        
                        status_lote.update(label="Questões forjadas com sucesso!", state="complete")
                        st.rerun()

            st.markdown("---")
            todas_aprovadas = True

            for i, item in enumerate(f['mapa']):
                label_status = "Aprovado" if item['status'] == 'aprovado' else ("Em Revisão" if item['status'] == 'revisao' else "Pendente")
                assunto_exibicao = item['tema']

                with st.container(border=True):
                    c_card_head1, c_card_head2 = st.columns([3, 1])
                    c_card_head1.markdown(f"**Questão {item['q']:02d} (Valor: {valor_por_item:.2f} pts) | Conteúdo: {assunto_exibicao}**")
                    c_card_head2.caption(f"Status: **{label_status}**")

                    if item['status'] == 'pendente':
                        todas_aprovadas = False
                        if st.button(f"Gerar Questão {item['q']} com IA", key=f"btn_gen_ind_{i}_{v}", use_container_width=True):
                            with st.spinner("Estruturando questão..."):
                                if is_rec_paralela_fase2:
                                    prompt_ind = f"Crie uma questão aberta/discursiva sobre {assunto_exibicao} valendo {valor_por_item:.2f} pontos para o 6º ano, sem alternativas."
                                    res_ind = ai.gerar_ia("ARQUITETO_RECUPERACAO_DISCURSIVA", prompt_ind)
                                    item['dados'] = {
                                        'ENUNCIADO': ai.extrair_tag(res_ind, 'QUESTOES') or res_ind,
                                        'ALT_A': '', 'ALT_B': '', 'ALT_C': '', 'ALT_D': '', 'ALT_E': '',
                                        'HABILIDADE': assunto_exibicao,
                                        'JUSTIFICATIVA': 'Resolução discursiva.',
                                        'DISTRATORES': 'Critérios de pontuação.',
                                        'GABARITO': 'DISCURSIVA'
                                    }
                                else:
                                    prompt = f"SÉRIE: {f['info']['ano']}\nTEMA: {assunto_exibicao}. GABARITO: {item['gabarito']}.\nCONTEXTO:\n{f.get('contexto_base', '')}"
                                    res_item = ai.gerar_ia("FORJA_ITEM_REGULAR", prompt)
                                    ext = {tag: ai.extrair_tag(res_item, tag) for tag in ['ENUNCIADO', 'ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E', 'HABILIDADE', 'JUSTIFICATIVA', 'DISTRATORES']}
                                    item['dados'] = {
                                        'ENUNCIADO': ext['ENUNCIADO'], 'ALT_A': ext['ALT_A'], 'ALT_B': ext['ALT_B'], 'ALT_C': ext['ALT_C'],
                                        'ALT_D': ext['ALT_D'], 'ALT_E': ext['ALT_E'], 'HABILIDADE': ext['HABILIDADE'], 'JUSTIFICATIVA': ext['JUSTIFICATIVA'],
                                        'DISTRATORES': ext['DISTRATORES'], 'GABARITO': item['gabarito']
                                    }
                                item['status'] = 'revisao'
                                st.rerun()

                    elif item['status'] in ['revisao', 'aprovado']:
                        if item['status'] == 'revisao': todas_aprovadas = False
                        d = item['dados']

                        with st.container(border=True):
                            st.markdown(preparar_para_leitura(f"**QUESTÃO {item['q']:02d} (Valor: {valor_por_item:.2f} pts) -** {d['ENUNCIADO']}"))
                            
                            if not is_rec_paralela_fase2 and d.get('ALT_A'):
                                col_alt_a, col_alt_b = st.columns(2)
                                col_alt_a.markdown(f"**(A)** {preparar_para_leitura(d['ALT_A'])}")
                                col_alt_b.markdown(f"**(B)** {preparar_para_leitura(d['ALT_B'])}")
                                col_alt_a.markdown(f"**(C)** {preparar_para_leitura(d['ALT_C'])}")
                                col_alt_b.markdown(f"**(D)** {preparar_para_leitura(d['ALT_D'])}")
                                if d.get('ALT_E'): col_alt_a.markdown(f"**(E)** {preparar_para_leitura(d['ALT_E'])}")
                            else:
                                st.caption("✍️ *Espaço pautado para memória de cálculo e resposta final do aluno.*")

                        with st.expander("Editar Enunciado Manualmente", expanded=False):
                            d['ENUNCIADO'] = st.text_area("Enunciado:", value=d['ENUNCIADO'], height=90, key=f"ed_en_{i}_{v}")

                        col_b1, col_b2 = st.columns(2)
                        if item['status'] == 'revisao':
                            if col_b1.button(f"Aprovar Questão {item['q']}", type="primary", key=f"btn_apr_{i}_{v}", use_container_width=True):
                                item['status'] = 'aprovado'
                                st.rerun()
                        else:
                            if col_b1.button(f"Reabrir Questão {item['q']}", key=f"btn_reabrir_{i}_{v}", use_container_width=True):
                                item['status'] = 'revisao'
                                st.rerun()

            if todas_aprovadas and len(f['mapa']) > 0:
                st.markdown("<br>", unsafe_allow_html=True)
                st.success("Caderno Regular da Recuperação homologado com sucesso.")
                if st.button("Aprovar e Avançar para Adaptação PEI", type="primary", use_container_width=True, key=f"btn_fase2_next_{v}"):
                    f['fase'] = 3
                    st.rerun()

        # ======================================================================
        # FASE 3: MATRIZ INCLUSIVA PEI
        # ======================================================================
        elif f['fase'] == 3:
            st.markdown("### Fase 3: Matriz Inclusiva PEI (Recuperação Adaptada)")
            st.caption("Adaptação dos itens para estudantes com necessidades educacionais específicas (Escala 0,0 a 10,0 pontos):")

            with st.container(border=True):
                niveis_selecionados = st.pills(
                    "Níveis de Acessibilidade Desejados:",
                    ["PEI Nível 1 (Apoio Leve - 3 Opções A, B, C)", "PEI Nível 2 (Apoio Moderado - Passo a Passo)", "PEI Nível 3 (Suporte Severo - 10 Boxes no Papel)"],
                    default=["PEI Nível 1 (Apoio Leve - 3 Opções A, B, C)", "PEI Nível 3 (Suporte Severo - 10 Boxes no Papel)"],
                    selection_mode="multi",
                    key=f"pills_niveis_pei_{v}"
                )

            pede_n1 = any("Nível 1" in n for n in niveis_selecionados)
            pede_n2 = any("Nível 2" in n for n in niveis_selecionados)
            pede_n3 = any("Nível 3" in n for n in niveis_selecionados)

            if st.button("Gerar Cadernos PEI de Recuperação", type="primary", use_container_width=True, key=f"btn_gen_triade_f3_{v}"):
                with st.status("Estruturando cadernos inclusivos adaptados...", expanded=True) as status:
                    texto_base_reg = f"[VALOR: {f['info']['valor']}]\n\n"
                    for item in f['mapa']:
                        d = item['dados']
                        texto_base_reg += f"**QUESTÃO {item['q']:02d} -** {d['ENUNCIADO']}\n\n"

                    if pede_n1:
                        status.write("Estruturando PEI Nível 1 (3 Opções A, B, C)...")
                        f['pei_1'] = ai.gerar_ia("FORJA_PEI_N1", f"REGULAR (Valor 10.0):\n{texto_base_reg}")
                    if pede_n2:
                        status.write("Estruturando PEI Nível 2 (Passo a Passo)...")
                        f['pei_2'] = ai.gerar_ia("FORJA_PEI_N2", f"REGULAR (Valor 10.0):\n{texto_base_reg}")
                    if pede_n3:
                        status.write("Estruturando PEI Nível 3 (10 Bento Boxes no Papel)...")
                        f['pei_3'] = ai.gerar_ia("FORJA_PEI_N3", f"REGULAR (Valor 10.0):\n{texto_base_reg}")

                    status.update(label="Cadernos inclusivos concluídos!", state="complete")
                    st.rerun()

            if f.get('pei_1') or f.get('pei_2') or f.get('pei_3'):
                tabs_pei = st.tabs(["PEI Nível 1", "PEI Nível 2", "PEI Nível 3"])
                with tabs_pei[0]:
                    f['pei_1'] = st.text_area("Edição PEI Nível 1:", value=f.get('pei_1', ''), height=240, key=f"ed_p1_area_{v}")
                with tabs_pei[1]:
                    f['pei_2'] = st.text_area("Edição PEI Nível 2:", value=f.get('pei_2', ''), height=240, key=f"ed_p2_area_{v}")
                with tabs_pei[2]:
                    f['pei_3'] = st.text_area("Edição PEI Nível 3:", value=f.get('pei_3', ''), height=240, key=f"ed_p3_area_{v}")

                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("Aprovar Adaptações e Avançar para Sincronização", type="primary", use_container_width=True, key=f"btn_fase3_next_{v}"):
                    f['fase'] = 4
                    st.rerun()

        # ======================================================================
        # FASE 4: CUSTÓDIA & DRIVE SYNC
        # ======================================================================
        elif f['fase'] == 4:
            st.markdown("### Fase 4: Custódia & Sincronização no Google Drive")
            st.caption("Compilação automática em arquivos DOCX oficiais com cabeçalhos institucionais.")

            tipo_nome = f['info'].get('tipo_prova', 'RECUPERACAO').upper().replace(' ', '_')
            nome_sugerido = f"{tipo_nome}_{f['info']['ano'].replace('º','')}ANO_{f['info']['trimestre'].replace(' ', '')}"
            nome_arq = st.text_input("Identificador Oficial no Drive:", value=nome_sugerido, key=f"nome_arq_f4_{v}")

            if st.button("Sincronizar no Google Drive", type="primary", use_container_width=True, key=f"btn_fase4_sync_{v}"):
                with st.status("Compilando arquivos oficiais e sincronizando no Drive...", expanded=True) as status:
                    txt_regular = f"[VALOR: {f['info']['valor']}]\n\n[QUESTOES]\n"
                    txt_gabarito = "[GABARITO_TEXTO]\n"
                    txt_grade = "[GRADE_DE_CORRECAO]\n"

                    valor_item_s = f['info']['valor'] / max(len(f['mapa']), 1)

                    for item in f['mapa']:
                        d = item['dados']
                        txt_regular += f"**QUESTÃO {item['q']:02d} (Valor: {valor_item_s:.2f} pts) -** {d['ENUNCIADO']}\n\n"
                        txt_gabarito += f"QUESTÃO {item['q']:02d}: Resolução detalhada passo a passo e resposta final.\n"
                        txt_grade += f"QUESTÃO {item['q']:02d}: [DESCRITOR_SAEB: {d['HABILIDADE']}] | CRITÉRIOS: Cálculo completo ({valor_item_s:.2f} pts), Erro de conta ({valor_item_s/2:.2f} pts), Sem cálculo (0,0 pt).\n"

                    texto_final_padrao = txt_regular + txt_gabarito + txt_grade

                    status.write("Compilando Caderno Regular DOCX (Discursivo)...")
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, texto_final_padrao, f['info'])
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, modo="AVALIACAO")

                    link_p1, link_p2, link_p3 = "N/A", "N/A", "N/A"

                    if f.get('pei_1'):
                        status.write("Compilando Caderno PEI Nível 1 DOCX...")
                        doc_p1 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N1", f['pei_1'], f['info'])
                        link_p1 = db.subir_e_converter_para_google_docs(doc_p1, f"{nome_arq}_PEI_N1", modo="AVALIACAO")

                    if f.get('pei_2'):
                        status.write("Compilando Caderno PEI Nível 2 DOCX...")
                        doc_p2 = exporter.gerar_docx_pei_v25(f"{nome_arq}_PEI_N2", f['pei_2'], f['info'])
                        link_p2 = db.subir_e_converter_para_google_docs(doc_p2, f"{nome_arq}_PEI_N2", modo="AVALIACAO")

                    if f.get('pei_3'):
                        status.write("Compilando Caderno PEI Nível 3 DOCX...")
                        doc_p3 = exporter.gerar_docx_pei_qualitativa(f"{nome_arq}_PEI_N3", f['pei_3'], f['info'])
                        link_p3 = db.subir_e_converter_para_google_docs(doc_p3, f"{nome_arq}_PEI_N3", modo="AVALIACAO")

                    links_f = f"--- LINKS ---\nRegular({link_reg}) PEI_N1({link_p1}) PEI_N2({link_p2}) PEI_N3({link_p3})"
                    conteudo_banco = f"{texto_final_padrao}\n\n[PEI_NIVEL_1]\n{f.get('pei_1', '')}\n\n[PEI_NIVEL_2]\n{f.get('pei_2', '')}\n\n[PEI_NIVEL_3]\n{f.get('pei_3', '')}\n\n{links_f}"

                    db.salvar_no_banco("DB_AULAS_PRONTAS", [
                        datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", nome_arq,
                        conteudo_banco, f['info']['ano'], link_reg
                    ])

                    f['nome_base'] = nome_arq
                    status.update(label="Avaliação sincronizada com sucesso no Google Drive!", state="complete")
                    st.balloons(); f['fase'] = 5; time.sleep(0.8); st.rerun()

        elif f['fase'] == 5:
            st.success(f"Avaliação **{f.get('nome_base', '')}** homologada e sincronizada com sucesso no Acervo.")
            st.info("Acesse a aba 'Acervo de Avaliações' ou o 'Scanner de Gabaritos' para realizar a aplicação e correção.")

            if st.button("Concluir e Retornar ao Início", use_container_width=True, key=f"btn_fin_f5_{v}"):
                reset_forja()

    # ==============================================================================
    # ABA 2: ACERVO DE AVALIAÇÕES & PERÍCIA TRI
    # ==============================================================================
    with tab_acervo_av:
        st.markdown("### Acervo de Instrumentos Avaliativos & Perícia TRI")
        st.caption("Repositório de avaliações, visualizador de chaves e controle de arquivos no Drive.")

        with st.container(border=True):
            c_f_tri, c_f_ano = st.columns([2, 1.5])
            f_trim_sel = c_f_tri.segmented_control("Trimestre:", ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"], default="Todos", key=f"acervo_seg_trim_{v}")
            f_ano_sel = c_f_ano.segmented_control("Série:", ["Todas", "6º", "7º", "8º", "9º"], default="Todas", key=f"acervo_seg_ano_{v}")

        termos_avaliativos = ["AVALIAÇÃO", "AVALIACAO", "PROVA", "TESTE", "SONDA", "RECUPERACAO", "RECUPERAÇÃO", "REVISAO", "REVISÃO"]
        df_exames = pd.DataFrame()
        if not df_aulas.empty and 'TIPO_MATERIAL' in df_aulas.columns:
            mask_todos = (df_aulas['SEMANA_REF'].astype(str).str.upper().isin(["AVALIAÇÃO", "AVALIACAO", "REVISÃO", "REVISAO"]) |
                          df_aulas['TIPO_MATERIAL'].astype(str).str.upper().str.contains('|'.join(termos_avaliativos), na=False))
            df_exames = df_aulas[mask_todos].copy()

        if not df_exames.empty:
            if f_trim_sel != "Todos":
                p_reg_t = util.obter_regex_trimestre(f_trim_sel)
                df_exames = df_exames[df_exames['TIPO_MATERIAL'].astype(str).str.contains(p_reg_t, regex=True, case=False, na=False) | df_exames['CONTEUDO'].astype(str).str.contains(p_reg_t, regex=True, case=False, na=False)]
            if f_ano_sel != "Todas":
                ano_num_sel = "".join(filter(str.isdigit, f_ano_sel))
                df_exames = df_exames[df_exames['ANO'].astype(str).str.contains(ano_num_sel, na=False)]
            df_exames = df_exames.iloc[::-1]

        if df_exames.empty:
            st.info("Nenhuma avaliação localizada para os filtros selecionados.")
        else:
            for idx_av, (_, row) in enumerate(df_exames.iterrows()):
                with st.container(border=True):
                    txt_f = str(row.get('CONTEUDO', ''))
                    identificador = str(row.get('TIPO_MATERIAL', 'AVALIAÇÃO'))
                    ano_exibicao = str(row.get('ANO', '6º'))
                    data_exibicao = str(row.get('DATA', 'N/A'))
                    val_num = extrair_valor_real_prova(txt_f, identificador)

                    c_card_h1, c_card_h2 = st.columns([3, 2])
                    c_card_h1.markdown(f"#### {identificador}")
                    c_card_h1.caption(f"Série: **{ano_exibicao}** | Data: **{data_exibicao}** | Valor Total: **{val_num:.1f} pts**")

                    def extrair_link_acervo_real(t, tag):
                        m = re.search(rf"{tag}\s*\(\s*(https://docs\.google\.com/document/d/[^\s\)]+)\s*\)", t, re.IGNORECASE)
                        return m.group(1).strip() if m else None

                    l_reg = extrair_link_acervo_real(txt_f, "Regular") or (row.get('LINK_DRIVE') if "https://docs.google.com" in str(row.get('LINK_DRIVE')) else None)
                    l_p1 = extrair_link_acervo_real(txt_f, "PEI_N1") or extrair_link_acervo_real(txt_f, "PEI")
                    l_p3 = extrair_link_acervo_real(txt_f, "PEI_N3")

                    c_l1, c_l2, c_l3, c_del = st.columns([1.5, 1.5, 1.5, 1])
                    if l_reg: c_l1.link_button("Caderno Regular", l_reg, type="primary", use_container_width=True)
                    if l_p1: c_l2.link_button("PEI Nível 1", l_p1, use_container_width=True)
                    if l_p3: c_l3.link_button("PEI Nível 3", l_p3, use_container_width=True)
                    if c_del.button("Excluir", key=f"del_ac_{row.name}_{idx_av}_{v}", use_container_width=True):
                        if db.excluir_avaliacao_completa(identificador, str(row.get('SEMANA_REF', 'AVALIAÇÃO'))):
                            st.success(f"{identificador} excluído com sucesso.")
                            time.sleep(0.5); st.rerun()

    # ==============================================================================
    # ABA 3: RECOMPOSIÇÃO DE APRENDIZAGEM & CADERNOS DE REVISÃO
    # ==============================================================================
    with tab_recomposicao:
        st.markdown("### Recomposição de Aprendizagem & Cadernos de Revisão")
        st.caption("Gere cadernos focados na superação de lacunas a partir de qualquer avaliação do acervo.")

        df_provas_para_revisao = df_aulas[df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].copy() if not df_aulas.empty else pd.DataFrame()

        if df_provas_para_revisao.empty:
            st.info("Nenhuma avaliação localizada para gerar caderno de recomposição.")
        else:
            with st.container(border=True):
                c_rev1, c_rev2 = st.columns([2, 1])
                opcoes_provas_origem = sorted(df_provas_para_revisao['TIPO_MATERIAL'].unique().tolist())
                prova_sel_recomposicao = c_rev1.selectbox("Avaliação de Origem:", opcoes_provas_origem, key=f"sel_p_recomp_{v}")
                ano_rev_sel = c_rev2.selectbox("Série:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano"], key=f"sel_ano_recomp_{v}")

            if prova_sel_recomposicao:
                row_prova_orig_m = df_provas_para_revisao[df_provas_para_revisao['TIPO_MATERIAL'] == prova_sel_recomposicao]
                txt_prova_orig = str(row_prova_orig_m.iloc[0].get('CONTEUDO', '')) if not row_prova_orig_m.empty else ""

                if st.button("Gerar Caderno de Recomposição", type="primary", use_container_width=True, key=f"btn_exe_recomp_{v}"):
                    with st.status("Estruturando material de recomposição completo...", expanded=True) as status_rec:
                        nome_recomposicao_arq = f"REVISAO_{prova_sel_recomposicao.replace('AVALIAÇÃO_', '').replace('PROVA_', '')}_10Q"
                        info_recomp = {"ano": ano_rev_sel, "trimestre": "II Trimestre" if "IITrimestre" in prova_sel_recomposicao else "I Trimestre", "semana": "RECOMPOSIÇÃO", "valor": "4.0"}

                        prompt_recomposicao = f"PROVA BASE:\n{txt_prova_orig}\nSÉRIE: {ano_rev_sel}\nMISSÃO: Crie o Caderno de Recomposição com [PROFESSOR], [ALUNO], [GABARITO_TEXTO], [GRADE_DE_CORRECAO], [PEI_NIVEL_1] e [PEI_NIVEL_3]."
                        res_recomposicao = ai.gerar_ia("ARQUITETO_REVISAO_V29", prompt_recomposicao)
                        
                        doc_alu_rev = exporter.gerar_docx_prova_v25(nome_recomposicao_arq, res_recomposicao, info_recomp)
                        link_alu_rev = db.subir_e_converter_para_google_docs(doc_alu_rev, nome_recomposicao_arq, modo="AVALIACAO")

                        db.excluir_registro("DB_AULAS_PRONTAS", nome_recomposicao_arq)
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_recomposicao_arq,
                            res_recomposicao + f"\n--- LINKS ---\nRegular({link_alu_rev})", ano_rev_sel, link_alu_rev
                        ])
                        status_rec.update(label="Caderno de Recomposição concluído!", state="complete")
                        st.balloons(); time.sleep(0.6); st.rerun()

    # ==============================================================================
    # ABA 4: DASHBOARD VISUAL DE IMPRESSÃO (CÓPIAS NOMINAIS)
    # ==============================================================================
    with tab_expedicao:
        @st.fragment
        def renderizar_expedicao_fragmento():
            st.markdown("### Dashboard Visual de Impressão (Contagem de Cópias)")
            st.caption("Resumo quantitativo e nominal de cópias para impressão, discriminando provas regulares e cadernos adaptados PEI.")

            c_exp1, c_exp2 = st.columns([1, 2])
            trim_exp_sel = c_exp1.segmented_control("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], default="II Trimestre", key=f"exp_trim_sel_{v}")
            if not trim_exp_sel: trim_exp_sel = "II Trimestre"

            turmas_disp_exp = sorted(df_alunos['TURMA'].unique().tolist()) if not df_alunos.empty else []
            turmas_sel_exp = c_exp2.multiselect("Turmas Selecionadas:", options=turmas_disp_exp, default=turmas_disp_exp, key=f"exp_turmas_sel_{v}")

            if turmas_sel_exp:
                tot_reg_geral, tot_p1_geral, tot_p2_geral, tot_p3_geral = 0, 0, 0, 0
                dados_tabela_impressao = []

                for t_item in turmas_sel_exp:
                    df_t_base = df_alunos[df_alunos['TURMA'] == t_item].copy() if not df_alunos.empty else pd.DataFrame()
                    if 'STATUS' not in df_t_base.columns: df_t_base['STATUS'] = "ATIVO"
                    df_t_alu = df_t_base[~df_t_base['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")
                    
                    reg_count = 0
                    p1_names, p2_names, p3_names = [], [], []

                    for _, al_r in df_t_alu.iterrows():
                        nec_raw = str(al_r.get('NECESSIDADES', '')).upper().strip()
                        nome_a = al_r.get('NOME_ALUNO', 'Estudante')
                        
                        if "(PEI N1)" in nec_raw or "PEI N1" in nec_raw: p1_names.append(nome_a)
                        elif "(PEI N2)" in nec_raw or "PEI N2" in nec_raw: p2_names.append(nome_a)
                        elif "(PEI N3)" in nec_raw or "PEI N3" in nec_raw: p3_names.append(nome_a)
                        else: reg_count += 1

                    tot_reg_geral += reg_count
                    tot_p1_geral += len(p1_names)
                    tot_p2_geral += len(p2_names)
                    tot_p3_geral += len(p3_names)

                    dados_tabela_impressao.append({
                        "Turma": t_item,
                        "Provas Regulares": reg_count,
                        "PEI Nível 1": f"{len(p1_names)} ({', '.join(p1_names)})" if p1_names else "0",
                        "PEI Nível 2": f"{len(p2_names)} ({', '.join(p2_names)})" if p2_names else "0",
                        "PEI Nível 3": f"{len(p3_names)} ({', '.join(p3_names)})" if p3_names else "0",
                        "Total Cópias": reg_count + len(p1_names) + len(p2_names) + len(p3_names)
                    })

                with st.container(border=True):
                    k1, k2, k3, k4, k5 = st.columns(5)
                    k1.metric("Provas Regulares", tot_reg_geral)
                    k2.metric("PEI Nível 1", tot_p1_geral)
                    k3.metric("PEI Nível 2", tot_p2_geral)
                    k4.metric("PEI Nível 3", tot_p3_geral)
                    k5.metric("TOTAL DE CÓPIAS", tot_reg_geral + tot_p1_geral + tot_p2_geral + tot_p3_geral)

                st.dataframe(pd.DataFrame(dados_tabela_impressao), use_container_width=True, hide_index=True)

        renderizar_expedicao_fragmento()


# ==============================================================================
# MÓDULO: CENTRAL DE INTELIGÊNCIA DE RESULTADOS (CIR / SCANNER DE GABARITOS)
# (V2026.PRO_EXECUTIVE - VISÃO COMPUTACIONAL, ANTI-TROCA, SEGUNDA CHAMADA & RECUPERAÇÃO)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("Central de Inteligência de Resultados (CIR)")
    st.caption("Leitura óptica de gabaritos por visão computacional direta, mesa de lançamento discursivo, perícia psicométrica TRI e tribunal de recursos.")
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

    def obter_avaliacoes_unificadas_cir(turma, trimestre_nome):
        if not turma or not trimestre_nome: return []
        padrao_regex_trim = util.obter_regex_trimestre(trimestre_nome)
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
            permitidos = ["TESTE", "PROVA", "SONDA", "DIAGNÓSTICA", "RECUPERAÇÃO", "RECUPERACAO", "AVALIAÇÃO", "AVALIACAO"]
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

    # ==============================================================================
    # DIALOGS DECLARADOS NO TOPO DO MÓDULO SCANNER (LEI #25)
    # ==============================================================================
    @st.dialog("Homologação de Atestados & Licenças", width="large")
    def dialog_atestados_modal(alunos_turma_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog):
        st.caption("Ajuste a situação regimental do estudante para homologação de ausência justificada ou 2ª chamada:")
        aluno_homolog_nome = st.selectbox("Selecione o Estudante:", alunos_turma_dialog['NOME_ALUNO'].tolist() if not alunos_turma_dialog.empty else [], key=f"homolog_modal_sel_{v}")
        
        if aluno_homolog_nome:
            match_h = alunos_turma_dialog[alunos_turma_dialog['NOME_ALUNO'] == aluno_homolog_nome]
            id_homolog = db.limpar_id(match_h.iloc[0]['ID']) if not match_h.empty else ""
            
            c_hom1, c_hom2 = st.columns([1.5, 1])
            novo_status_ausencia = c_hom1.radio(
                "Situação Regimental:",
                [
                    "Falta Justificada (Atestado / Licença - Autorizado para 2ª Chamada)",
                    "Falta Injustificada (Ausência Definitiva)",
                    "Restaurar para Fila de Correção (Remover Registros)"
                ],
                key=f"rad_modal_{id_homolog}_{v}"
            )
            motivo_detalhado = c_hom2.text_input("Observação / Motivo:", placeholder="Ex: Atestado médico entregue em 15/04", key=f"txt_mot_modal_{id_homolog}_{v}")

            if st.button("Confirmar Homologação", type="primary", use_container_width=True, key=f"btn_conf_homolog_{v}"):
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
                    st.success("Situação homologada com sucesso!"); time.sleep(0.5); st.rerun()

    @st.dialog("Transferência de Titularidade da Prova", width="large")
    def dialog_trocar_titularidade_modal(dados_soberania_dialog, alunos_turma_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog):
        st.caption("Transfere as respostas, pontuação e evidência da avaliação para o estudante correto:")
        
        alunos_com_prova = [r.get('Estudante', '') for r in dados_soberania_dialog if r.get('Situação') == "REALIZADA"]
        todos_alunos_turma = alunos_turma_dialog['NOME_ALUNO'].tolist() if not alunos_turma_dialog.empty else []

        if not alunos_com_prova:
            st.info("Nenhum estudante com avaliação corrigida neste slot para transferência.")
        else:
            c_tr1, c_tr2 = st.columns(2)
            aluno_origem_sel = c_tr1.selectbox("1. Estudante de Origem (Recebeu por engano):", alunos_com_prova, key=f"tr_orig_{v}")
            
            opcoes_dest = [a for a in todos_alunos_turma if a != aluno_origem_sel]
            aluno_destino_sel = c_tr2.selectbox("2. Estudante de Destino (Dono da prova):", opcoes_dest, key=f"tr_dest_{v}")

            dados_origem = next((r for r in dados_soberania_dialog if r.get('Estudante') == aluno_origem_sel), {})
            nota_origem = dados_origem.get('Nota', 0.0)
            foto_origem = dados_origem.get('Evidência', 'N/A')

            with st.container(border=True):
                st.markdown("**Resumo da Avaliação a Transferir:**")
                c_inf1, c_inf2 = st.columns(2)
                c_inf1.metric("Pontuação", f"{nota_origem:.1f} pts")
                if "http" in str(foto_origem): c_inf2.link_button("Visualizar Imagem", foto_origem, use_container_width=True)
                else: c_inf2.caption("Sem imagem vinculada")

            novo_status_origem = st.selectbox(
                "3. Situação do Estudante de Origem após a transferência:",
                ["Pendente (Aguardando escaneamento da prova real)", "Ausência Injustificada", "Ausência Justificada (Atestado)"],
                key=f"tr_stat_orig_{v}"
            )

            status_param = "PENDENTE"
            if "Injustificada" in novo_status_origem: status_param = "FALTOU"
            elif "Justificada" in novo_status_origem: status_param = "FALTOU_JUSTIFICADO|Atestado Médico"

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Confirmar Transferência", type="primary", use_container_width=True, key=f"btn_exec_transf_{v}"):
                with st.spinner("Transferindo avaliação e recalculando médias..."):
                    match_orig = alunos_turma_dialog[alunos_turma_dialog['NOME_ALUNO'] == aluno_origem_sel]
                    match_dest = alunos_turma_dialog[alunos_turma_dialog['NOME_ALUNO'] == aluno_destino_sel]
                    
                    id_orig = db.limpar_id(match_orig.iloc[0]['ID']) if not match_orig.empty else ""
                    id_dest = db.limpar_id(match_dest.iloc[0]['ID']) if not match_dest.empty else ""

                    sucesso_tr = db.transferir_titularidade_gabarito(
                        id_origem=id_orig,
                        nome_origem=aluno_origem_sel,
                        id_destino=id_dest,
                        nome_destino=aluno_destino_sel,
                        turma=t_sel_dialog,
                        trimestre=tr_sel_dialog,
                        id_avaliacao=av_alvo_dialog,
                        status_origem_apos=status_param
                    )

                    if sucesso_tr:
                        st.success(f"Avaliação transferida para {aluno_destino_sel} com sucesso!")
                        time.sleep(0.8); st.rerun()
                    else:
                        st.error("Erro ao transferir a titularidade.")

    @st.dialog("Perícia & Segunda Chamada Individual", width="large")
    def dialog_pericia_modal(dados_soberania_dialog, alunos_turma_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog, gab_oficial_dialog, v_total_dialog, nome_curto_av_dialog):
        st.caption("Acesse as respostas registradas ou realize o lançamento de 2ª chamada / recorreção:")
        
        todos_estudantes_nomes = [r.get('Estudante', '') for r in dados_soberania_dialog]
        
        if not todos_estudantes_nomes: 
            st.info("Nenhum estudante cadastrado nesta turma.")
        else:
            aluno_pericia_nome = st.selectbox("Selecione o Estudante:", todos_estudantes_nomes, key=f"pericia_modal_sel_{v}")
            if aluno_pericia_nome:
                al_data = next((r for r in dados_soberania_dialog if r.get('Estudante') == aluno_pericia_nome), {})
                id_al_pericia = al_data.get('ID', '')
                resp_raw = str(al_data.get('_Respostas', ''))
                grupo_membros = str(al_data.get('Dupla / Grupo', 'Individual'))
                foto_atual_link = str(al_data.get('Evidência', ''))
                sit_atual = str(al_data.get('Situação', ''))
                perfil_estudante = str(al_data.get('Perfil', 'REGULAR')).upper()
                
                is_exame_discursivo = any(x in av_alvo_dialog.upper() for x in ["2ª_CHAMADA", "2A_CHAMADA", "2ª CHAMADA", "2A CHAMADA", "DISCURSIVA", "RECUPERACAO", "RECUPERAÇÃO", "ABERTA"]) and "TIPO" not in av_alvo_dialog.upper()
                is_estudante_pei = (perfil_estudante == "PEI") or ("PEI" in str(al_data.get('Versão', '')).upper())

                df_prova_ref = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_curto_av_dialog, case=False, na=False)] if not df_aulas.empty else pd.DataFrame()
                txt_prova_completa = str(df_prova_ref.iloc[0].get('CONTEUDO', '')) if not df_prova_ref.empty else ""
                
                val_real_instrumento = util.extrair_valor_real_prova(txt_prova_completa, av_alvo_dialog)

                c_f1, c_f2 = st.columns([1, 2])
                if "http" in foto_atual_link: c_f1.link_button("Abrir Imagem no Drive", foto_atual_link, use_container_width=True)
                else: c_f1.caption("Sem imagem vinculada.")
                
                nova_foto_pericia = c_f2.file_uploader("Anexar / Substituir Imagem JPG:", type=["jpg", "jpeg", "png"], key=f"up_modal_foto_{id_al_pericia}_{v}")

                # CASO 1: AVALIAÇÃO DISCURSIVA (SEGUNDA CHAMADA / RECUPERAÇÃO)
                if is_exame_discursivo:
                    st.markdown(f"#### Lançamento Discursivo Oficial (Teto: **{val_real_instrumento:.1f} pts**)")
                    st.caption("Avaliação aberta com memória de cálculo. Lance a pontuação real obtida pelo estudante:")
                    
                    nota_atual_disc = util.sosa_to_float(al_data.get('Nota', 0.0))
                    nova_nota_disc = st.number_input(
                        f"Pontuação Conquistada (0.0 a {val_real_instrumento:.1f}):",
                        min_value=0.0, max_value=float(val_real_instrumento), value=float(min(val_real_instrumento, nota_atual_disc)), step=0.1,
                        key=f"inp_disc_pericia_{id_al_pericia}_{v}"
                    )
                    obs_disc_pericia = st.text_input("Observação Pedagógica da Avaliação Discursiva:", value="Avaliação Discursiva Homologada", key=f"txt_obs_disc_{id_al_pericia}_{v}")

                    if st.button("Homologar Avaliação Discursiva", type="primary", use_container_width=True, key=f"btn_save_disc_pericia_{v}"):
                        with st.spinner("Registrando nota discursiva..."):
                            link_foto_final = foto_atual_link
                            if nova_foto_pericia is not None:
                                link_foto_final = db.subir_e_converter_para_google_docs(nova_foto_pericia.getvalue(), aluno_pericia_nome.replace(" ","_"), trimestre=tr_sel_dialog, categoria=t_sel_dialog, semana=av_alvo_dialog, modo="SCANNER")

                            wb_p = db.conectar()
                            ws_p = wb_p.worksheet("DB_GABARITOS_ALUNOS")
                            dados_p = ws_p.get_all_values()
                            for idx_row_p in range(len(dados_p) - 1, 0, -1):
                                row_p = dados_p[idx_row_p]
                                if len(row_p) > 4 and row_p[3] == t_sel_dialog and nome_curto_av_dialog in row_p[4]:
                                    if row_p[2] == aluno_pericia_nome:
                                        ws_p.delete_rows(idx_row_p + 1)

                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                datetime.now().strftime("%d/%m/%Y"), id_al_pericia, aluno_pericia_nome, t_sel_dialog, av_alvo_dialog,
                                f"DISCURSIVA|{obs_disc_pericia}", util.sosa_to_str(nova_nota_disc), link_foto_final
                            ])

                            db.limpar_notas_turma_trimestre(t_sel_dialog, tr_sel_dialog)
                            st.cache_data.clear(); st.success(f"Nota de {aluno_pericia_nome} ({nova_nota_disc:.1f} pts) homologada!"); time.sleep(0.5); st.rerun()

                # CASO 2: AVALIAÇÃO OBJETIVA (REGULAR OU PEI N1/N2)
                else:
                    gab_aluno_especifico_list = ai.extrair_gab_universal_com_fallback(txt_prova_completa, is_pei=is_estudante_pei, nivel_pei="NIVEL_1")
                    gab_aluno_dict = {i+1: letra for i, letra in enumerate(gab_aluno_especifico_list)}
                    
                    opcoes_respostas_grid = ["A", "B", "C", "X", "?"] if is_estudante_pei else ["A", "B", "C", "D", "E", "X", "?"]
                    
                    if is_estudante_pei:
                        st.info("Matriz de Correção Ativa: **PEI Adaptado (3 Alternativas: A, B, C)**.")

                    resp_limpa = resp_raw.split('|GRUPO:')[0] if '|GRUPO:' in resp_raw else resp_raw
                    respostas_lista = resp_limpa.split(';') if (not resp_limpa.startswith("FALTOU") and not resp_limpa.startswith("QUALITATIVA") and not resp_limpa.startswith("DISCURSIVA") and resp_limpa != "MANUAL") else []
                    
                    grid_pericia = []
                    for idx_q in range(len(gab_aluno_dict)):
                        item_str = respostas_lista[idx_q].strip().upper() if idx_q < len(respostas_lista) else "?"
                        letra_aluno = item_str.replace("*", "")
                        if letra_aluno not in opcoes_respostas_grid: letra_aluno = "?"
                        tem_calculo = "*" not in item_str
                        correta_q = gab_aluno_dict.get(idx_q + 1, "?")
                        grid_pericia.append({"Questão": f"Q{idx_q+1:02d}", "Chave Oficial": correta_q, "Marcada": letra_aluno, "Cálculo Apresentado": tem_calculo})
                    
                    df_pericia_ed = st.data_editor(
                        pd.DataFrame(grid_pericia), hide_index=True, use_container_width=True,
                        column_config={
                            "Questão": st.column_config.TextColumn(disabled=True), 
                            "Chave Oficial": st.column_config.TextColumn(disabled=True), 
                            "Marcada": st.column_config.SelectboxColumn("Resposta", options=opcoes_respostas_grid, required=True), 
                            "Cálculo Apresentado": st.column_config.CheckboxColumn("Cálculo OK")
                        },
                        key=f"grid_modal_ind_{id_al_pericia}_{is_estudante_pei}_{v}"
                    )
                    
                    novas_res_pericia = []
                    nota_pericia_calc = 0.0
                    peso_q_pericia = val_real_instrumento / len(gab_aluno_dict) if len(gab_aluno_dict) > 0 else 0
                    for i_p, r_p in df_pericia_ed.iterrows():
                        l_p = r_p["Marcada"]
                        c_p = r_p["Cálculo Apresentado"]
                        g_p = gab_aluno_dict.get(i_p + 1, "?")
                        if l_p == g_p or g_p == "ANULADA": nota_pericia_calc += peso_q_pericia if c_p else (peso_q_pericia / 2)
                        flag_letra_p = f"{l_p}*" if (not c_p and l_p in ["A","B","C","D","E"]) else l_p
                        novas_res_pericia.append(flag_letra_p)
                        
                    st.metric("Pontuação Recalculada", f"{min(val_real_instrumento, nota_pericia_calc):.1f} / {val_real_instrumento:.1f} pontos")
                    
                    if st.button("Homologar Correção e Recalcular Média", type="primary", use_container_width=True, key=f"btn_save_pericia_ind_{v}"):
                        with st.spinner("Salvando avaliação e recalculando boletim..."):
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
                            st.cache_data.clear(); st.success("Avaliação homologada e notas sincronizadas com sucesso!"); time.sleep(0.5); st.rerun()

    @st.dialog("Digitação Manual em Lote", width="large")
    def dialog_lazaro_modal(dados_soberania_dialog, gab_oficial_dialog, v_total_dialog, t_sel_dialog, tr_sel_dialog, av_alvo_dialog):
        df_perdidos = pd.DataFrame([r for r in dados_soberania_dialog if str(r.get('_Respostas', '')).startswith("MANUAL") and r.get('Situação') == "REALIZADA"])
        if not df_perdidos.empty:
            st.caption("Insira as respostas das avaliações separadas por ponto e vírgula (ex: A;B;C;D;E):")
            df_lazaro = st.data_editor(
                pd.DataFrame([{"ID": r.get('ID', ''), "Estudante": r.get('Estudante', ''), "Respostas": ""} for _, r in df_perdidos.iterrows()]),
                hide_index=True, use_container_width=True, key=f"laz_grid_modal_{v}"
            )
            if st.button("Processar Lançamento em Lote", type="primary", use_container_width=True, key=f"btn_proc_laz_{v}"):
                with st.spinner("Processando avaliações..."):
                    for _, row_laz in df_lazaro.iterrows():
                        resp_dig = str(row_laz["Respostas"]).strip().upper()
                        if resp_dig:
                            respostas_lista = [r for r in re.split(r'[;\s,]', resp_dig) if r]
                            acertos = sum(1 for i, r in enumerate(respostas_lista) if i+1 in gab_oficial_dialog and r == gab_oficial_dialog[i+1])
                            nota_calc = (acertos / len(gab_oficial_dialog)) * v_total_dialog if len(gab_oficial_dialog) > 0 else 0.0
                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), row_laz["ID"], row_laz["Estudante"], t_sel_dialog, av_alvo_dialog, ";".join(respostas_lista), util.sosa_to_str(nota_calc), "N/A"])
                    st.cache_data.clear(); st.success("Lançamento concluído!"); time.sleep(0.5); st.rerun()
        else: st.success("Nenhum lançamento pendente.")

    @st.dialog("Autópsia Clínica do Item", width="large")
    def dialog_autopsia_modal(q_str, stats_row, txt_prova_base, is_pei_view, caderno_alvo):
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
            st.markdown(f"### Enunciado Oficial ({q_str})")
            if m_q_reg: st.write(util.preparar_para_leitura(m_q_reg.group(1).strip()))
            else: st.info("Enunciado da questão disponível na impressão oficial.")
        
        with c_right:
            st.markdown("### Desempenho")
            acerto_perc = stats_row['Acerto %']
            cor_acerto = "normal" if acerto_perc >= 60 else "inverse"
            st.metric("Taxa de Acerto", f"{acerto_perc:.1f}%", delta="Atenção" if acerto_perc < 50 else "Adequado", delta_color=cor_acerto)
            st.metric("Chave Oficial", stats_row['Gabarito'])
            
            st.markdown("---")
            st.markdown("### Perícia de Distratores")
            if m_p_reg:
                p_completa = re.sub(r'[*#]', '', m_p_reg.group(1).strip())
                st.info(util.preparar_para_leitura(p_completa))
            else: st.caption("Perícia não localizada.")

    tab_correcao, tab_auditoria, tab_raiox = st.tabs([
        "Mesa de Correção", "Tribunal de Auditoria", "Raio-X Psicométrico"
    ])

    # ==============================================================================
    # ABA 1: MESA DE CORREÇÃO (BLINDADA PARA SEGUNDA CHAMADA & RECUPERAÇÃO)
    # ==============================================================================
    with tab_correcao:
        modo_lancamento = st.segmented_control(
            "Tipo de Lançamento:", 
            ["Avaliações (Leitor Óptico / Manual)", "Projetos & Trabalhos em Lote"], 
            default="Avaliações (Leitor Óptico / Manual)",
            key=f"pills_modo_cir_{v}"
        )
        st.markdown("---")

        if "Avaliações" in modo_lancamento:
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                t_sel = c1.selectbox("Turma:", [""] + lista_turmas_cir, key=f"t_p_{v}")
                tr_sel = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_p_{v}")
                
                opcoes_base = obter_avaliacoes_unificadas_cir(t_sel, tr_sel)
                at_sel = c3.selectbox("Instrumento Avaliativo:", [""] + opcoes_base, key=f"at_p_{v}")

            if not t_sel or not at_sel:
                st.info("Selecione a Turma e a Avaliação para abrir a Mesa de Correção.")
            else:
                nome_filtro_pendente = at_sel.split("-")[0].strip()
                df_diag_turma = df_diagnosticos[df_diagnosticos['TURMA'] == t_sel] if not df_diagnosticos.empty else pd.DataFrame()
                padrao_trim = util.obter_regex_trimestre(tr_sel)
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
                                rotulo = f"{nome_real} (2ª Chamada Autorizada)"
                                opcoes_atestados.append(rotulo)
                                opcoes_todos.append(rotulo)
                            elif status_banco.startswith("FALTOU"):
                                rotulo = f"{nome_real} (Ausência Registrada)"
                                opcoes_faltas.append(rotulo)
                                opcoes_todos.append(rotulo)
                            else:
                                rotulo = f"{nome_real} (Corrigida)"
                                opcoes_todos.append(rotulo)
                                
                            mapa_rotulo_nome[rotulo] = nome_real

                        total_processados = total_turma - len(opcoes_pendentes_puros)

                        filtro_fila = st.segmented_control(
                            "Filtro:",
                            ["Pendentes", "Atestados", "Ausências", "Todos"],
                            default="Pendentes",
                            key=f"flt_fila_cir_{v}"
                        )
                        
                        if filtro_fila == "Pendentes": opcoes_triagem_exibir = opcoes_pendentes_puros
                        elif filtro_fila == "Atestados": opcoes_triagem_exibir = opcoes_atestados
                        elif filtro_fila == "Ausências": opcoes_triagem_exibir = opcoes_faltas
                        else: opcoes_triagem_exibir = opcoes_todos

                        progresso = total_processados / total_turma if total_turma > 0 else 0.0
                        st.progress(min(1.0, max(0.0, progresso)))
                        st.caption(f"**{total_processados} de {total_turma}** avaliações processadas na turma.")
                        
                        modo_dupla = st.toggle("Avaliação Realizada em Grupo/Dupla", value=False, key=f"dupla_tog_{v}")
                        
                        alunos_alvo = []
                        if opcoes_triagem_exibir:
                            if modo_dupla:
                                rotulos_sel = st.multiselect("Selecione os Integrantes (Máx 3):", options=opcoes_triagem_exibir, max_selections=3, key=f"pilha_dupla_{v}")
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
                                if len(alunos_alvo) > 1: st.markdown(f"##### Grupo: {', '.join(alunos_alvo)}")
                                else: st.markdown(f"##### Estudante: {alunos_alvo[0]}")
                                
                                tem_pei_na_dupla = False
                                perfis_dupla = []
                                for nome_a in alunos_alvo:
                                    al_info = alunos_turma_df[alunos_turma_df['NOME_ALUNO'] == nome_a].iloc[0]
                                    id_aluno_atual = db.limpar_id(al_info.get('ID', ''))
                                    nec_aluno = str(al_info.get('NECESSIDADES', 'TÍPICO')).upper().strip()
                                    perfis_dupla.append((nome_a, id_aluno_atual, nec_aluno))
                                    
                                    if "(PEI N3)" in nec_aluno: st.caption("Perfil: PEI Nível 3 (Qualitativa / No Papel)")
                                    elif "(PEI N2)" in nec_aluno: st.caption("Perfil: PEI Nível 2 (Apoio Moderado)")
                                    elif "(PEI N1)" in nec_aluno: st.caption("Perfil: PEI Nível 1 (Apoio Leve)")
                                    elif nec_aluno not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]:
                                        tem_pei_na_dupla = True
                                        st.caption(f"Perfil de Acessibilidade ({nome_a}): {nec_aluno}")
                                    else: st.caption("Perfil: Regular / Típico")

                            primeira_nec = perfis_dupla[0][2] if perfis_dupla else ""
                            if "(PEI N3)" in primeira_nec or "NÍVEL 3" in primeira_nec: idx_lente_default = 3
                            elif "(PEI N2)" in primeira_nec or "NÍVEL 2" in primeira_nec: idx_lente_default = 2
                            elif "(PEI N1)" in primeira_nec or "NÍVEL 1" in primeira_nec: idx_lente_default = 1
                            elif tem_pei_na_dupla: idx_lente_default = 1
                            else: idx_lente_default = 0
                                
                            opcoes_lentes = ["Regular (Padrão ou Variante)", "PEI Nível 1 (Apoio Leve)", "PEI Nível 2 (Apoio Moderado)", "PEI Nível 3 / Qualitativa"]
                            
                            with st.container(border=True):
                                lente_corr = st.segmented_control(
                                    "Matriz de Correção:", 
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
                            at_segunda = None
                            
                            if "REGULAR" in lente_upper:
                                c_reg1, c_reg2 = st.columns(2)
                                modo_2a = c_reg1.toggle("Segunda Chamada Discursiva", key=f"t2a_{v}")
                                
                                if modo_2a:
                                    df_2a = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(padrao_trim, regex=True, case=False)) & (df_aulas['ANO'].str.contains(serie_num))] if not df_aulas.empty else pd.DataFrame()
                                    opcoes_2a = df_2a['TIPO_MATERIAL'].unique().tolist() if not df_2a.empty else []
                                    at_segunda = c_reg2.selectbox("Caderno de 2ª Chamada:", [""] + opcoes_2a, key=f"s2a_{v}")
                                    if at_segunda:
                                        df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_segunda]
                                        if not df_busca.empty: material_ref = df_busca.iloc[0]
                                else:
                                    df_variantes = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains(tipo_base, regex=False)) & (df_aulas['TIPO_MATERIAL'].str.upper().str.contains("TIPO")) & (df_aulas['ANO'].str.contains(serie_num))] if not df_aulas.empty else pd.DataFrame()
                                    versao_variante = c_reg2.selectbox("Caderno / Tipo:", ["Padrão (Tipo A)"] + (df_variantes['TIPO_MATERIAL'].unique().tolist() if not df_variantes.empty else []), key=f"var_{v}")
                                    df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == (at_sel if versao_variante == "Padrão (Tipo A)" else versao_variante)] if not df_aulas.empty else pd.DataFrame()
                                    if not df_busca.empty: material_ref = df_busca.iloc[0]
                                        
                            elif is_pei_grading or is_qualitativa:
                                df_busca = df_aulas[df_aulas['TIPO_MATERIAL'] == at_sel] if not df_aulas.empty else pd.DataFrame()
                                if not df_busca.empty: material_ref = df_busca.iloc[0]

                            if material_ref is not None:
                                txt_ref = str(material_ref.get('CONTEUDO', ''))
                                nome_material_efetivo = str(material_ref.get('TIPO_MATERIAL', at_sel))
                                v_total_at = util.extrair_valor_real_prova(txt_ref, nome_material_efetivo)

                                # -------------------------------------------------------------
                                # DETECÇÃO BLINDADA: AVALIAÇÃO DISCURSIVA / ABERTA
                                # -------------------------------------------------------------
                                is_av_discursiva = (
                                    modo_2a 
                                    or any(x in str(nome_material_efetivo).upper() for x in ["RECUPERAÇÃO", "RECUPERACAO", "2ª CHAMADA", "2A CHAMADA", "2ª_CHAMADA", "DISCURSIVA", "ABERTA"])
                                    or any(x in str(at_sel).upper() for x in ["RECUPERAÇÃO", "RECUPERACAO", "DISCURSIVA", "ABERTA"])
                                    or ("(A)" not in txt_ref and "A)" not in txt_ref and "[QUESTOES]" in txt_ref and not is_pei_grading and not is_qualitativa)
                                ) and "FINAL" not in str(nome_material_efetivo).upper() and not is_pei_grading and not is_qualitativa

                                if is_av_discursiva:
                                    with st.container(border=True):
                                        st.markdown(f"#### ✍️ Mesa de Lançamento Discursivo: **{nome_material_efetivo}**")
                                        st.caption(f"Avaliação aberta com memória de cálculo. Pontuação Máxima: **{v_total_at:.1f} pontos**.")
                                        
                                        q_raw_disc = ai.extrair_tag(txt_ref, "QUESTOES")
                                        num_q_disc = len(re.findall(r"(?i)QUESTÃO\s*0?\d+", q_raw_disc)) or 8
                                        valor_por_item_disc = v_total_at / num_q_disc if num_q_disc > 0 else 0.5
                                        
                                        tab_disc_direta, tab_disc_itens = st.tabs(["Lançamento da Nota Total", "Lançamento por Questão"])
                                        
                                        with tab_disc_direta:
                                            c_disc1, c_disc2 = st.columns([1.2, 1.8])
                                            nota_discursiva_inp = c_disc1.number_input(
                                                f"Pontuação Conquistada (0.0 a {v_total_at:.1f}):",
                                                min_value=0.0, max_value=float(v_total_at), value=float(min(v_total_at, 4.0 if v_total_at == 4.0 else 6.0)), step=0.1,
                                                key=f"inp_nota_disc_{v}"
                                            )
                                            obs_disc_pericia = c_disc2.text_input("Observação Pedagógica:", value="Avaliação Discursiva Homologada", key=f"txt_obs_disc_{v}")

                                        with tab_disc_itens:
                                            st.caption(f"Preencha a nota de cada questão ({num_q_disc} itens de {valor_por_item_disc:.2f} pts):")
                                            grid_itens_disc = []
                                            for q_i in range(num_q_disc):
                                                grid_itens_disc.append({
                                                    "Questão": f"Questão {q_i+1:02d}",
                                                    "Valor do Item": valor_por_item_disc,
                                                    "Nota do Aluno": valor_por_item_disc
                                                })
                                            df_itens_disc_ed = st.data_editor(
                                                pd.DataFrame(grid_itens_disc), hide_index=True, use_container_width=True,
                                                column_config={
                                                    "Questão": st.column_config.TextColumn(disabled=True),
                                                    "Valor do Item": st.column_config.NumberColumn(format="%.2f", disabled=True),
                                                    "Nota do Aluno": st.column_config.NumberColumn(format="%.2f", min_value=0.0, max_value=float(valor_por_item_disc))
                                                },
                                                key=f"ed_grid_disc_itens_{v}"
                                            )
                                            soma_itens_calc = df_itens_disc_ed["Nota do Aluno"].sum()
                                            st.metric("Soma dos Itens", f"{soma_itens_calc:.2f} / {v_total_at:.1f} pts")

                                        img_disc_file = st.file_uploader("Anexar Imagem da Folha / Caderno de Resolução (JPG/PNG):", type=["jpg", "jpeg", "png"], key=f"up_disc_ev_{v}")

                                        c_b_disc1, c_b_disc2 = st.columns(2)
                                        if c_b_disc1.button("Consolidar e Gravar Nota Discursiva", type="primary", use_container_width=True, key=f"btn_save_disc_{v}"):
                                            with st.spinner("Gravando nota discursiva e atualizando boletim..."):
                                                nota_final_gravar = soma_itens_calc if 'soma_itens_calc' in locals() and tab_disc_itens else nota_discursiva_inp
                                                
                                                link_evidencia_disc = "N/A"
                                                if img_disc_file is not None:
                                                    link_evidencia_disc = db.subir_e_converter_para_google_docs(
                                                        img_disc_file.getvalue(), 
                                                        alunos_alvo[0].replace(" ", "_"), 
                                                        trimestre=tr_sel, categoria=t_sel, semana=nome_material_efetivo, modo="SCANNER"
                                                    )

                                                df_turma_completa = df_alunos[df_alunos['TURMA'] == t_sel] if not df_alunos.empty else pd.DataFrame()
                                                for aluno_nome in alunos_alvo:
                                                    match_al_d = df_turma_completa[df_turma_completa['NOME_ALUNO'] == aluno_nome]
                                                    if not match_al_d.empty:
                                                        id_al_d = db.limpar_id(match_al_d.iloc[0].get('ID', ''))
                                                        
                                                        try:
                                                            wb_del = db.conectar()
                                                            ws_del = wb_del.worksheet("DB_GABARITOS_ALUNOS")
                                                            dados_del = ws_del.get_all_values()
                                                            for idx_d in range(len(dados_del) - 1, 0, -1):
                                                                row_d = dados_del[idx_d]
                                                                if len(row_d) > 4 and db.limpar_id(row_d[1]) == id_al_d and (nome_filtro_pendente in row_d[4] or nome_material_efetivo in row_d[4]):
                                                                    ws_del.delete_rows(idx_d + 1)
                                                        except: pass
                                                        
                                                        respostas_salvar_disc = f"DISCURSIVA|{obs_disc_pericia}"
                                                        db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                                            datetime.now().strftime("%d/%m/%Y"), id_al_d, aluno_nome, t_sel, nome_material_efetivo,
                                                            respostas_salvar_disc, util.sosa_to_str(nota_final_gravar), link_evidencia_disc
                                                        ])
                                                
                                                db.limpar_notas_turma_trimestre(t_sel, tr_sel)
                                                st.cache_data.clear()
                                                st.success(f"Nota discursiva de {alunos_alvo[0]} ({nota_final_gravar:.1f} pts) homologada com sucesso!")
                                                time.sleep(0.6); st.rerun()

                                        if c_b_disc2.button("Registrar Ausência na Avaliação", use_container_width=True, key=f"btn_aus_disc_{v}"):
                                            for aluno_nome in alunos_alvo:
                                                match_al_aus = alunos_turma_df[alunos_turma_df['NOME_ALUNO'] == aluno_nome]
                                                if not match_al_aus.empty:
                                                    id_al = db.limpar_id(match_al_aus.iloc[0].get('ID', ''))
                                                    db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                                    db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                                        datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, nome_material_efetivo, "FALTOU_INJUSTIFICADO|Ausente", "0,00", "N/A"
                                                    ])
                                            db.limpar_notas_turma_trimestre(t_sel, tr_sel)
                                            st.rerun()

                                elif is_pei_grading or "REGULAR" in lente_upper:
                                    gab_alvo = ai.extrair_gab_universal_com_fallback(txt_ref, is_pei_grading, nivel_alvo_pei)
                                    if not gab_alvo:
                                        q_raw_check = ai.extrair_tag(txt_ref, "QUESTOES") or txt_ref
                                        qtd_q_estimada = len(re.findall(r"(?i)QUESTÃO\s*0?\d+", q_raw_check)) or 10
                                        gab_alvo = ["A"] * qtd_q_estimada

                                    tag_grade_ref = "GRADE_DE_CORRECAO_PEI" if is_pei_grading else "GRADE_DE_CORRECAO"
                                    grade_raw_ref = ai.extrair_tag(txt_ref, tag_grade_ref) or ai.extrair_tag(txt_ref, "GRADE_DE_CORRECAO")

                                    with st.popover("Conferir Chave de Respostas", use_container_width=True):
                                        st.caption(f"Chave oficial ({len(gab_alvo)} questões | Pontuação: {v_total_at:.1f} pts).")
                                        grid_gab_pre = [{"Q": f"{i+1:02d}", "Chave": gab_alvo[i] if i < len(gab_alvo) else "A"} for i in range(len(gab_alvo))]
                                        df_gab_pre = st.data_editor(
                                            pd.DataFrame(grid_gab_pre), hide_index=True, use_container_width=True,
                                            column_config={"Q": st.column_config.TextColumn(disabled=True), "Chave": st.column_config.SelectboxColumn("Resposta Oficial", options=["A", "B", "C", "D", "E"], required=True)},
                                            key=f"ed_pre_gab_{v}_{nivel_alvo_pei}"
                                        )
                                        if not df_gab_pre.empty and "Chave" in df_gab_pre.columns:
                                            gab_alvo = df_gab_pre["Chave"].tolist()

                                    c_m1, c_m2 = st.columns([2, 1])
                                    modo_correcao = c_m1.segmented_control("Modo de Leitura:", ["Leitor Óptico (Câmera/Arquivo)", "Digitação Direta"], default="Leitor Óptico (Câmera/Arquivo)", key=f"mc_pills_{v}")
                                    
                                    if c_m2.button("Registrar Ausência", use_container_width=True, key=f"btn_aus_single_{v}"):
                                        for aluno_nome in alunos_alvo:
                                            match_al_aus = alunos_turma_df[alunos_turma_df['NOME_ALUNO'] == aluno_nome]
                                            if not match_al_aus.empty:
                                                id_al = db.limpar_id(match_al_aus.iloc[0].get('ID', ''))
                                                db.excluir_registro("DB_GABARITOS_ALUNOS", id_al)
                                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), id_al, aluno_nome, t_sel, at_sel, "FALTOU", "0,00", "N/A"])
                                        st.rerun()

                                    if "Leitor Óptico" in str(modo_correcao):
                                        img_file = st.file_uploader("Carregar imagem da folha (.jpg/.png):", type=["jpg", "jpeg", "png"], key=f"up_{v}")
                                        img_cam = st.camera_input("Capturar via Câmera:", key=f"cam_{v}")
                                        img = img_file if img_file else img_cam

                                        if img and "current_scan_res" not in st.session_state:
                                            with st.spinner("Processando leitura óptica com Gemini 3.5 Flash-Lite..."):
                                                res_hibrido = ai.analisar_gabarito_hibrido(
                                                    imagem_bytes=img.getvalue(),
                                                    qtd_questoes=len(gab_alvo),
                                                    is_pei=is_pei_grading
                                                )
                                                res_json = res_hibrido.get("respostas", {})
                                                st.session_state.current_scan_res = [res_json.get(f"{i+1:02d}", "?") for i in range(len(gab_alvo))]
                                                st.session_state.current_scan_img = res_hibrido.get("imagem_alinhada", img.getvalue())
                                                st.session_state.current_scan_nome_det = res_hibrido.get("nome_lido_folha", "")
                                                st.rerun()

                                        if "current_scan_res" in st.session_state:
                                            nome_det_cabecalho = str(st.session_state.get("current_scan_nome_det", "")).upper().strip()
                                            aluno_selecionado_upper = str(alunos_alvo[0]).upper().strip()

                                            if nome_det_cabecalho and nome_det_cabecalho not in ["NÃO_IDENTIFICADO", "N/A", ""] and len(nome_det_cabecalho) > 2:
                                                primeiro_nome_det = nome_det_cabecalho.split()[0]
                                                primeiro_nome_sel = aluno_selecionado_upper.split()[0]
                                                
                                                is_divergente = False
                                                if primeiro_nome_det in ["DAVI", "DAVID"] and primeiro_nome_sel in ["DAVI", "DAVID"] and primeiro_nome_det != primeiro_nome_sel:
                                                    is_divergente = True
                                                elif primeiro_nome_det not in aluno_selecionado_upper:
                                                    is_divergente = True

                                                if is_divergente:
                                                    with st.container(border=True):
                                                        st.warning(
                                                            f"**Alerta de Divergência de Titularidade:**\n\n"
                                                            f"• Selecionado no Sistema: `{aluno_selecionado_upper}`\n"
                                                            f"• Identificado na Folha: `{nome_det_cabecalho}`\n\n"
                                                            f"Confira o caderno físico antes de confirmar a gravação."
                                                        )

                                            c_badge1, c_badge2 = st.columns([2, 1])
                                            c_badge1.caption("Motor: **Visão Computacional Gemini Flash-Lite • Leitura Concluída**")
                                            
                                            with c_badge2.popover("Inspecionar Imagem Alinhada"):
                                                st.image(st.session_state.current_scan_img, caption="Folha Processada pelo Scanner", use_container_width=True)

                                            res_lidas = st.session_state.current_scan_res
                                            dados_pericia = []
                                            for i, lido in enumerate(res_lidas):
                                                if i < len(gab_alvo):
                                                    correta = gab_alvo[i]
                                                    if lido == correta:
                                                        status = "Correta"
                                                    elif lido == "X":
                                                        status = f"Dupla (Chave: {correta})"
                                                    elif lido == "?":
                                                        status = f"Em Branco (Chave: {correta})"
                                                    else:
                                                        status = f"Incorreta (Chave: {correta})"
                                                        
                                                    dados_pericia.append({
                                                        "Q": f"{i+1:02d}", 
                                                        "Marcada": lido, 
                                                        "Diagnóstico": status, 
                                                        "Cálculo Apresentado": True
                                                    })
                                            
                                            df_mesa = st.data_editor(
                                                pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                                                column_config={
                                                    "Q": st.column_config.TextColumn(disabled=True, width="small"), 
                                                    "Marcada": st.column_config.SelectboxColumn("Ajustar", options=["A", "B", "C", "D", "E", "X", "?"], required=True, width="small"), 
                                                    "Diagnóstico": st.column_config.TextColumn("Diagnóstico", disabled=True, width="medium"),
                                                    "Cálculo Apresentado": st.column_config.CheckboxColumn("Cálculo OK", default=True, help="Desmarque caso o aluno não tenha apresentado o desenvolvimento do cálculo.", width="small")
                                                },
                                                key=f"ed_turbo_{v}"
                                            )
                                            
                                            novas_res = df_mesa["Marcada"].tolist()
                                            calculos_ok = df_mesa["Cálculo Apresentado"].tolist()
                                            
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
                                                    desc_dist = m_p_item.group(0).strip() if m_p_item else f"Inconsistência no item Q{q_idx_n:02d}."
                                                    erros_detalhados_tri.append(f"**Q{q_idx_n:02d} (Marcou {r} | Chave {gab_alvo[i]}):** {desc_dist}")
                                                
                                                flag_letra = f"{r}*" if (not has_calc and r in ["A","B","C","D","E"]) else r
                                                respostas_com_flag.append(flag_letra)
                                                    
                                            st.metric("Pontuação Final Calculada", f"{nota_f:.1f} / {v_total_at:.1f}", delta=f"{acertos}/{len(gab_alvo)} acertos ({len(alunos_alvo)} estudante(s))")
                                            
                                            if erros_detalhados_tri:
                                                with st.expander("Diagnóstico de Distratores dos Itens Incorretos", expanded=False):
                                                    for err_txt in erros_detalhados_tri:
                                                        st.info(util.preparar_para_leitura(err_txt))

                                            col_s1, col_s2 = st.columns(2)
                                            if col_s1.button("Homologar Correção", type="primary", use_container_width=True, key=f"btn_save_corr_{v}"):
                                                with st.spinner("Sincronizando imagem no Drive e registrando pontuação..."):
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
                                                    if "current_scan_nome_det" in st.session_state:
                                                        del st.session_state.current_scan_nome_det
                                                    st.success("Avaliação homologada com sucesso!")
                                                    time.sleep(0.5)
                                                    st.rerun()

                                            if col_s2.button("Descartar Leitura", use_container_width=True, key=f"btn_disc_corr_{v}"):
                                                del st.session_state.current_scan_res
                                                del st.session_state.current_scan_img
                                                if "current_scan_nome_det" in st.session_state:
                                                    del st.session_state.current_scan_nome_det
                                                st.rerun()
                                    else:
                                        opcoes_letras = ["A", "B", "C", "X", "?"] if is_pei_grading else ["A", "B", "C", "D", "E", "X", "?"]
                                        dados_manual = [{"Q": f"{i+1:02d}", "Chave Oficial": gab_alvo[i], "Resposta": "?", "Cálculo Apresentado": True} for i in range(len(gab_alvo))]
                                        
                                        img_manual_file = st.file_uploader("Anexar Imagem da Folha (Opcional):", type=["jpg", "jpeg", "png"], key=f"up_man_{v}")
                                        
                                        df_manual = st.data_editor(
                                            pd.DataFrame(dados_manual), hide_index=True, use_container_width=True,
                                            column_config={
                                                "Q": st.column_config.TextColumn(disabled=True), 
                                                "Chave Oficial": st.column_config.TextColumn(disabled=True), 
                                                "Resposta": st.column_config.SelectboxColumn(options=opcoes_letras, required=True), 
                                                "Cálculo Apresentado": st.column_config.CheckboxColumn("Cálculo OK")
                                            },
                                            key=f"manual_grid_{v}"
                                        )
                                        
                                        peso_q = v_total_at / len(gab_alvo) if len(gab_alvo) > 0 else 0.3
                                        nota_calc = 0.0
                                        respostas_finais = []
                                        for i, row in df_manual.iterrows():
                                            resp = row["Resposta"]
                                            has_calc_m = row["Cálculo Apresentado"]
                                            if resp == row["Chave Oficial"]:
                                                nota_calc += peso_q if has_calc_m else (peso_q / 2)
                                            flag_m = f"{resp}*" if (not has_calc_m and resp in ["A","B","C","D","E"]) else resp
                                            respostas_finais.append(flag_m)
                                                
                                        st.metric("Pontuação Calculada", f"{nota_calc:.1f} / {v_total_at:.1f}")
                                        if st.button("Homologar Lançamento Manual", type="primary", use_container_width=True, key=f"btn_save_man_{v}"):
                                            mat_nome_ref = str(material_ref.get('TIPO_MATERIAL', at_sel))
                                            link_foto_man = "N/A"
                                            if img_manual_file is not None:
                                                with st.spinner("Sincronizando imagem no Drive..."):
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
                                            st.success("Lançamento homologado com sucesso!"); time.sleep(0.5); st.rerun()

                                elif is_qualitativa:
                                    st.caption("Avaliação Qualitativa PEI Nível 3: Registro baseado em rubricas pedagógicas de mediação.")
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
                                    nota_qual = c_q1.number_input("Pontuação Atribuída:", 0.0, v_total_at, v_total_at, step=0.5, key=f"nq_{v}")
                                    respostas_rubrica = []
                                    
                                    with c_q2:
                                        st.markdown("**Rubricas de Observação:**")
                                        for i_r, rubrica in enumerate(rubricas_encontradas):
                                            st.markdown(f"**{rubrica}**")
                                            resp = st.selectbox("Status:", ["Autônomo", "Com Apoio", "Não Realizado"], key=f"rub_{v}_{i_r}", label_visibility="collapsed")
                                            respostas_rubrica.append(f"- {rubrica}: {resp}")
                                        obs_extra = st.text_area("Observações pedagógicas adicionais:", height=60, key=f"oq_extra_{v}")
                                        parecer_final = "\n".join(respostas_rubrica) + (f"\nObs: {obs_extra}" if obs_extra.strip() else "")
                                            
                                    if st.button("Homologar Avaliação PEI N3", type="primary", use_container_width=True, key=f"btn_save_pei3_{v}"):
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
                                        st.success("Avaliação PEI N3 homologada!"); time.sleep(0.5); st.rerun()

                        renderizar_mesa_correcao_fragmento()

        # ==============================================================================
        # ABA 2: TRIBUNAL DE AUDITORIA
        # ==============================================================================
        with tab_auditoria:
            st.markdown("### Tribunal de Auditoria de Resultados")
            with st.container(border=True):
                c_h1, c_h2 = st.columns(2)
                t_sel_h = c_h1.selectbox("Turma:", [""] + lista_turmas_cir, key=f"t_h_{v}")
                tr_sel_h = c_h2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_h_{v}")

            if t_sel_h and tr_sel_h:
                padrao_regex_trim = util.obter_regex_trimestre(tr_sel_h)
                serie_num = "".join(filter(str.isdigit, t_sel_h))
                
                df_prova_trib = pd.DataFrame()
                gab_oficial_trib = {}
                v_total_av = 4.0
                
                opcoes_base = obter_avaliacoes_unificadas_cir(t_sel_h, tr_sel_h)
                av_alvo_h = st.selectbox("Instrumento Alvo:", [""] + opcoes_base, key=f"av_h_{v}")

                if av_alvo_h:
                    is_sonda = "SONDA" in av_alvo_h.upper() or "DIAGNÓSTICA" in av_alvo_h.upper()
                    nome_curto_av = av_alvo_h.split("-")[0].strip()
                    
                    df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_curto_av, case=False, na=False)] if not df_aulas.empty else pd.DataFrame()
                    txt_prova_trib = str(df_prova_trib.iloc[0].get('CONTEUDO', '')) if not df_prova_trib.empty else ""
                    
                    v_total_av = util.extrair_valor_real_prova(txt_prova_trib, av_alvo_h)

                    if not df_prova_trib.empty:
                        gab_oficial_trib_list = ai.extrair_gab_universal_com_fallback(txt_prova_trib, is_pei=False)
                        gab_oficial_trib = {i+1: letra for i, letra in enumerate(gab_oficial_trib_list)}

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
                            
                        situacao_txt, versao_prova, nota_atual, link_ev, respostas_salvas, grupo_parceiros = "PENDENTE", "PROVA ORIGINAL", 0.0, "", "MANUAL", ""

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
                                situacao_txt, versao_prova = f"JUSTIFICADO ({motivo_j})", "2ª CHAMADA PENDENTE"
                            elif respostas_salvas.startswith("FALTOU_INJUSTIFICADO"):
                                situacao_txt, versao_prova = "FALTA INJUSTIFICADA", "ZERO REGIMENTAL"
                            elif respostas_salvas == "FALTOU":
                                situacao_txt, versao_prova = "AUSÊNCIA", "N/A"
                            elif "2ª" in id_av_banco or "2CHAMADA" in id_av_banco:
                                situacao_txt, versao_prova = "REALIZADA", "SEGUNDA CHAMADA"
                            elif "TIPO" in id_av_banco:
                                situacao_txt, versao_prova = "REALIZADA", f"VARIANTE ({id_av_banco.split('-')[-1].strip()})"
                            elif respostas_salvas.startswith("DISCURSIVA"):
                                situacao_txt, versao_prova = "REALIZADA", "DISCURSIVA"
                            else:
                                situacao_txt, versao_prova = "REALIZADA", "PROVA ORIGINAL"

                        dados_soberania.append({
                            "ID": id_a, "Estudante": nome_alu_f, "Perfil": "PEI" if nec_alu_f.upper().strip() not in ["NENHUMA", "PENDENTE", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE", "DEFASAGEM LEITURA", "DEFASAGEM MATEMÁTICA"] else "REGULAR",
                            "Situação": situacao_txt, "Versão": versao_prova, "Nota": nota_atual, "Dupla / Grupo": grupo_parceiros if grupo_parceiros else "Individual", "Evidência": link_ev, "_Respostas": respostas_salvas
                        })

                    st.markdown("#### Ações de Auditoria & Recálculo em Lote")
                    
                    if st.button("⚡ Recalcular Notas de Toda a Turma com Chaves Corretas (Regulares + PEI)", type="primary", use_container_width=True, key=f"btn_recalc_lote_all_{v}"):
                        with st.status("Recalculando notas da turma inteira com as chaves oficiais...", expanded=True) as status_batch:
                            status_batch.write("1/3 Extraindo chaves oficiais (Regular e PEI N1)...")
                            gab_reg_list = ai.extrair_gab_universal_com_fallback(txt_prova_trib, is_pei=False)
                            gab_pei_list = ai.extrair_gab_universal_com_fallback(txt_prova_trib, is_pei=True, nivel_pei="NIVEL_1")
                            
                            status_batch.write("2/3 Recalculando notas em lote em memória...")
                            wb_batch = db.conectar()
                            if not wb_batch:
                                status_batch.update(label="Falha de conexão com o banco de dados.", state="error")
                                st.stop()
                                
                            ws_g_batch = wb_batch.worksheet("DB_GABARITOS_ALUNOS")
                            dados_g_batch = ws_g_batch.get_all_values()
                            
                            updates_count = 0
                            for idx_row_b in range(1, len(dados_g_batch)):
                                row_b = dados_g_batch[idx_row_b]
                                if len(row_b) > 6 and row_b[3] == t_sel_h and nome_curto_av in row_b[4]:
                                    id_al_b = db.limpar_id(row_b[1])
                                    resp_bruta_b = str(row_b[5])
                                    
                                    # Pula provas discursivas, qualitativas ou ausências para não sobreescrever
                                    if not resp_bruta_b.startswith("FALTOU") and not resp_bruta_b.startswith("QUALITATIVA") and not resp_bruta_b.startswith("DISCURSIVA") and resp_bruta_b != "MANUAL":
                                        resp_limpa_b = resp_bruta_b.split("|GRUPO:")[0]
                                        respostas_al_lista = resp_limpa_b.split(';')
                                        
                                        is_al_pei = False
                                        al_match_b = alunos_turma_h[alunos_turma_h['ID'].apply(db.limpar_id) == id_al_b]
                                        if not al_match_b.empty:
                                            nec_b = str(al_match_b.iloc[0].get('NECESSIDADES', '')).upper()
                                            if nec_b not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE", "PENDENTE", "DEFASAGEM LEITURA", "DEFASAGEM MATEMÁTICA"]:
                                                is_al_pei = True
                                        
                                        gab_correto_aluno = gab_pei_list if is_al_pei else gab_reg_list
                                        peso_q_batch = v_total_av / len(gab_correto_aluno) if len(gab_correto_aluno) > 0 else 0.0
                                        
                                        nova_nota_calc = 0.0
                                        for q_i in range(len(respostas_al_lista)):
                                            if q_i < len(gab_correto_aluno):
                                                r_item = respostas_al_lista[q_i].strip().upper()
                                                l_marcada = r_item.replace("*", "")
                                                tem_calculo_b = "*" not in r_item
                                                g_correto = gab_correto_aluno[q_i]
                                                
                                                if g_correto == "ANULADA" or l_marcada == g_correto:
                                                    nova_nota_calc += peso_q_batch if tem_calculo_b else (peso_q_batch / 2)
                                        
                                        nova_nota_calc_final = min(v_total_av, nova_nota_calc)
                                        
                                        formato_str = f"{nova_nota_calc_final:.2f}".replace(".", ",")
                                        row_b[6] = formato_str
                                        updates_count += 1

                            ws_g_batch.clear()
                            ws_g_batch.update(values=dados_g_batch, range_name='A1')

                            status_batch.write("3/3 Sincronizando com o Boletim de Notas...")
                            db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                            st.cache_data.clear()
                            
                            status_batch.update(label=f"Sucesso! {updates_count} provas recalculadas e boletim sincronizado com precisão!", state="complete")
                            st.balloons(); time.sleep(0.8); st.rerun()

                    c_act1, c_act2, c_act3, c_act4 = st.columns(4)

                    if c_act1.button("Atestados & Licenças", use_container_width=True, key=f"btn_act_atest_{v}"):
                        dialog_atestados_modal(alunos_turma_h, t_sel_h, tr_sel_h, av_alvo_h)
                        
                    if c_act2.button("Perícia por Estudante", use_container_width=True, key=f"btn_act_peric_{v}"):
                        dialog_pericia_modal(dados_soberania, alunos_turma_h, t_sel_h, tr_sel_h, av_alvo_h, gab_oficial_trib, v_total_av, nome_curto_av)
                        
                    if c_act3.button("Digitação em Lote", use_container_width=True, key=f"btn_act_laz_{v}"):
                        dialog_lazaro_modal(dados_soberania, gab_oficial_trib, v_total_av, t_sel_h, tr_sel_h, av_alvo_h)

                    if c_act4.button("Transferir Titularidade", use_container_width=True, key=f"btn_act_troca_tit_{v}"):
                        dialog_trocar_titularidade_modal(dados_soberania, alunos_turma_h, t_sel_h, tr_sel_h, av_alvo_h)

                    st.markdown("---")

                    @st.fragment
                    def renderizar_espelho_tribunal_fragmento():
                        st.markdown("#### Espelho de Gabarito & Análise de Itens")
                        
                        opcoes_cadernos_visuais = ["Caderno Regular (Tipo A)", "Variante (Tipo B)", "PEI Nível 1 (Apoio Leve)", "PEI Nível 2 (Apoio Moderado)"]
                        caderno_sel_tab = st.segmented_control("Selecione o Caderno:", opcoes_cadernos_visuais, default="Caderno Regular (Tipo A)", key=f"pills_caderno_inspect_audit_{v}")
                        
                        is_pei_cad = "PEI" in str(caderno_sel_tab)
                        nivel_pei_tag = "NIVEL_1" if "Nível 1" in str(caderno_sel_tab) else "NIVEL_2"
                        
                        nome_busca_caderno = av_alvo_h
                        if "Tipo B" in str(caderno_sel_tab):
                            nome_busca_caderno = f"{av_alvo_h} - TIPO B"

                        df_prova_cad = df_aulas[df_aulas['TIPO_MATERIAL'] == nome_busca_caderno] if not df_aulas.empty else pd.DataFrame()
                        if df_prova_cad.empty: df_prova_cad = df_prova_trib

                        txt_cad_conteudo = str(df_prova_cad.iloc[0].get('CONTEUDO', '')) if not df_prova_cad.empty else ""
                        gab_caderno_ativo = ai.extrair_gab_universal_com_fallback(txt_cad_conteudo, is_pei=is_pei_cad, nivel_pei=nivel_pei_tag)

                        col_espelho, col_raiox = st.columns([1.2, 1.8])

                        with col_espelho:
                            with st.container(border=True):
                                st.markdown("##### Chave Oficial Adotada")
                                st.caption(f"Chave ativa para: **{caderno_sel_tab}**")
                                
                                grid_espelho = []
                                for q_i, l_g in enumerate(gab_caderno_ativo):
                                    grid_espelho.append({
                                        "Questão": f"Q{q_i+1:02d}",
                                        "Chave Atual": l_g,
                                        "Nova Chave / Ação": l_g
                                    })
                                
                                opcoes_sel_coluna = ["A", "B", "C", "ANULADA"] if is_pei_cad else ["A", "B", "C", "D", "E", "ANULADA"]

                                df_espelho_ed = st.data_editor(
                                    pd.DataFrame(grid_espelho), hide_index=True, use_container_width=True, height=270,
                                    column_config={
                                        "Questão": st.column_config.TextColumn(disabled=True, width="small"),
                                        "Chave Atual": st.column_config.TextColumn(disabled=True, width="small"),
                                        "Nova Chave / Ação": st.column_config.SelectboxColumn("Ajustar Resposta", options=opcoes_sel_coluna, required=True)
                                    },
                                    key=f"ed_espelho_split_audit_{str(caderno_sel_tab).replace(' ','_')}_{v}"
                                )

                                peso_q_espelho = v_total_av / len(gab_caderno_ativo) if len(gab_caderno_ativo) > 0 else 0
                                st.caption(f"• Total de Itens: {len(gab_caderno_ativo)} | Valor por Item: {peso_q_espelho:.2f} pts")

                                if st.button("Salvar Espelho e Recalcular Notas", type="primary", use_container_width=True, key=f"btn_save_espelho_audit_{v}"):
                                    with st.status("Recalculando notas para este caderno...", expanded=True) as status_rec:
                                        novos_gabs_map = {}
                                        for _, r_e in df_espelho_ed.iterrows():
                                            num_q_e = int(r_e["Questão"].replace("Q", ""))
                                            novos_gabs_map[num_q_e] = r_e["Nova Chave / Ação"]

                                        wb_s = db.conectar()
                                        ws_g = wb_s.worksheet("DB_GABARITOS_ALUNOS")
                                        d_g = ws_g.get_all_values()
                                        
                                        for idx_row in range(1, len(d_g)):
                                            row_b = d_g[idx_row]
                                            if len(row_b) > 4 and row_b[3] == t_sel_h and nome_curto_av in row_b[4]:
                                                resp_bruta = str(row_b[5])
                                                if not resp_bruta.startswith("FALTOU") and not resp_bruta.startswith("QUALITATIVA") and not resp_bruta.startswith("DISCURSIVA") and resp_bruta != "MANUAL":
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

                                                        if letra_c == "ANULADA": nova_nota_a += peso_q_espelho
                                                        elif letra_a == letra_c: nova_nota_a += peso_q_espelho if tem_calc else (peso_q_espelho / 2)

                                                    ws_g.update_cell(idx_row + 1, 7, util.sosa_to_str(min(v_total_av, nova_nota_a)))

                                        db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                        st.cache_data.clear()
                                        status_rec.update(label="Espelho atualizado e notas recalculadas!", state="complete")
                                        st.balloons(); time.sleep(0.8); st.rerun()

                        with col_raiox:
                            with st.container(border=True):
                                st.markdown("##### Enunciados e Distratores")
                                
                                if not gab_caderno_ativo:
                                    st.info("Selecione uma avaliação para carregar os itens.")
                                else:
                                    num_q_inspect = st.selectbox("Selecione o Item:", [f"Questão {i+1:02d}" for i in range(len(gab_caderno_ativo))], key=f"sel_q_inspect_audit_{v}")
                                    q_idx_inspect = int(num_q_inspect.replace("Questão ", ""))
                                    
                                    tag_questoes_cad = nivel_pei_tag if is_pei_cad else "QUESTOES"
                                    q_raw_text = ai.extrair_tag(txt_cad_conteudo, tag_questoes_cad) or ai.extrair_tag(txt_cad_conteudo, "QUESTOES")
                                    
                                    prefixo_q = r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)"
                                    padrao_q = rf"(?si)({prefixo_q}\s*0?{q_idx_inspect}\b.*?)(?={prefixo_q}\s*0?{q_idx_inspect+1}\b|GABARITO|RESPOSTAS|GRADE|$)"
                                    m_q = re.search(padrao_q, q_raw_text, re.IGNORECASE | re.DOTALL)
                                    
                                    tag_grade_cad = "GRADE_DE_CORRECAO_PEI" if is_pei_cad else "GRADE_DE_CORRECAO"
                                    grade_raw_text = ai.extrair_tag(txt_cad_conteudo, tag_grade_cad) or ai.extrair_tag(txt_cad_conteudo, "GRADE_DE_CORRECAO")
                                    m_p = re.search(padrao_q, grade_raw_text, re.IGNORECASE | re.DOTALL)
                                    
                                    st.markdown(f"**Enunciado Oficial ({num_q_inspect}):**")
                                    if m_q: st.write(util.preparar_para_leitura(m_q.group(1).strip()))
                                    else: st.info("Enunciado da questão disponível na impressão oficial.")
                                    
                                    st.divider()
                                    st.markdown("**Perícia Pedagógica (Descritor & Distratores):**")
                                    if m_p:
                                        p_texto = re.sub(r'[*#]', '', m_p.group(1).strip())
                                        st.info(util.preparar_para_leitura(p_texto))
                                    else: st.caption("Perícia não vinculada a este item.")

                    renderizar_espelho_tribunal_fragmento()

                    st.markdown("---")
                    st.markdown("#### Visão Consolidada de Auditoria da Turma")
                    
                    df_soberano_ed = st.data_editor(
                        pd.DataFrame(dados_soberania), hide_index=True, use_container_width=True, key=f"ed_sob_{v}",
                        column_config={
                            "ID": None, "_Respostas": None, 
                            "Estudante": st.column_config.TextColumn(disabled=True), 
                            "Perfil": st.column_config.TextColumn(disabled=True), 
                            "Situação": st.column_config.SelectboxColumn(options=["REALIZADA", "AUSÊNCIA", "PENDENTE"], required=True), 
                            "Versão": st.column_config.TextColumn(disabled=True), 
                            "Dupla / Grupo": st.column_config.TextColumn(disabled=True),
                            "Nota": st.column_config.NumberColumn(format="%.1f"), 
                            "Evidência": st.column_config.LinkColumn("Imagem")
                        }
                    )

                    if st.button("Homologar Ajustes de Auditoria", use_container_width=True, type="primary", key=f"btn_homolog_sob_{v}"):
                        with st.status("Gravando dados auditados...") as status_h:
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
                                
                                if r['Situação'] == "REALIZADA":
                                    id_f = av_alvo_h if r['Versão'] == "PROVA ORIGINAL" else f"{av_alvo_h} ({r['Versão']})"
                                    dados_atualizados.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, id_f, "MANUAL" if resp_originais.startswith("FALTOU") else resp_final_gravar, nota_s, r['Evidência'] or "N/A"])
                                elif r['Situação'] == "AUSÊNCIA":
                                    dados_atualizados.append([datetime.now().strftime("%d/%m/%Y"), id_l, nome_limpo, t_sel_h, av_alvo_h, "FALTOU", "0,00", "N/A"])
                                
                                if not is_sonda and r['Situação'] != "PENDENTE":
                                    reg_atual = notas_atuais[notas_atuais['ID_ALUNO'].apply(db.limpar_id) == id_l] if not notas_atuais.empty else pd.DataFrame()
                                    v_vistos = reg_atual.iloc[0].get('NOTA_VISTOS', '0,0') if not reg_atual.empty else "0,0"
                                    v_teste = reg_atual.iloc[0].get('NOTA_TESTE', '0,0') if not reg_atual.empty else "0,0"
                                    v_prova = reg_atual.iloc[0].get('NOTA_PROVA', '0,0') if not reg_atual.empty else "0,0"
                                    v_rec = reg_atual.iloc[0].get('NOTA_REC', '0,0') if not reg_atual.empty else "0,0"
                                    
                                    nota_boletim = nota_s if r['Situação'] == "REALIZADA" else "0,00"
                                    if "TESTE" in av_alvo_h.upper(): v_teste = nota_boletim
                                    elif any(x in av_alvo_h.upper() for x in ["RECUPERAÇÃO", "RECUPERACAO", "REC_"]): v_rec = nota_boletim
                                    else: v_prova = nota_boletim
                                        
                                    soma_primaria = min(10.0, util.sosa_to_float(v_vistos) + util.sosa_to_float(v_teste) + util.sosa_to_float(v_prova))
                                    if util.sosa_to_float(v_rec) > 0 and soma_primaria < 6.0:
                                        media_calculada_rec = (soma_primaria + util.sosa_to_float(v_rec)) / 2.0
                                        nova_media_final = min(10.0, max(soma_primaria, round(media_calculada_rec * 2) / 2))
                                    else:
                                        nova_media_final = soma_primaria
                                        
                                    lista_boletim.append([id_l, nome_limpo, t_sel_h, tr_sel_h, v_vistos, v_teste, v_prova, v_rec, util.sosa_to_str(nova_media_final)])
                            
                            ws_g.clear(); ws_g.update(values=dados_atualizados, range_name='A1')
                            if not is_sonda and lista_boletim:
                                db.limpar_notas_turma_trimestre(t_sel_h, tr_sel_h)
                                db.salvar_lote("DB_NOTAS", lista_boletim)
                            status_h.update(label="Notas e auditoria homologadas com sucesso!", state="complete"); time.sleep(0.5); st.rerun()

        # ==============================================================================
        # ABA 3: RAIO-X PSICOMÉTRICO
        # ==============================================================================
        with tab_raiox:
            st.markdown("### Raio-X Psicométrico & Diagnóstico de Itens")
            
            with st.container(border=True):
                c1, c2, c3 = st.columns([1, 1, 2])
                t_sel_r = c1.selectbox("Turma:", [""] + lista_turmas_cir, key=f"t_r_v90_{v}")
                tr_sel_r = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"tr_r_v90_{v}")
                
                opcoes_base_r = obter_avaliacoes_unificadas_cir(t_sel_r, tr_sel_r)
                at_sel_r = c3.selectbox("Instrumento Avaliativo:", [""] + opcoes_base_r, key=f"at_r_v90_{v}")

            if not t_sel_r or not at_sel_r:
                st.info("Selecione a Turma e o Instrumento acima para carregar o Raio-X.")
            else:
                nome_curto_av = at_sel_r.split("-")[0].strip()
                padrao_regex_trim = util.obter_regex_trimestre(tr_sel_r)
                serie_num_r = "".join(filter(str.isdigit, t_sel_r))
                
                mask_diag = (df_diagnosticos['TURMA'] == t_sel_r) & (
                    df_diagnosticos['ID_AVALIACAO'].astype(str).str.contains(nome_curto_av, case=False, na=False)
                ) if not df_diagnosticos.empty and 'TURMA' in df_diagnosticos.columns and 'ID_AVALIACAO' in df_diagnosticos.columns else pd.Series()
                
                respostas_brutas = df_diagnosticos[mask_diag].copy() if not df_diagnosticos.empty and not mask_diag.empty else pd.DataFrame()

                if respostas_brutas.empty:
                    st.info("Nenhuma resposta registrada para esta avaliação no trimestre selecionado.")
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
                        
                        if resp.startswith("FALTOU"): return "AUSÊNCIA"
                        if resp.startswith("QUALITATIVA"): return "PEI Nível 3 (Qualitativa)"
                        if "2ª" in id_av or "2CHAMADA" in id_av or "DISCURSIVA" in id_av: return "Segunda Chamada / Discursiva"
                        if "TIPO" in id_av: return f"Variante ({id_av.split('-')[-1].strip()})"
                        
                        is_pei = nec not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO", "ALTA PERFORMANCE", "PENDENTE", "SUSPEITA", "DEFASAGEM LEITURA", "DEFASAGEM MATEMÁTICA"]
                        if is_pei:
                            qtd_respostas = len(resp.split(';'))
                            if qtd_respostas <= 10: return "PEI Nível 1 (Apoio Leve)"
                            
                        return "Caderno Regular (Tipo A)"

                    df_analise['CADERNO_FEITO'] = df_analise.apply(classificar_caderno, axis=1)
                    cadernos_disponiveis = sorted([c for c in df_analise['CADERNO_FEITO'].unique() if c != "AUSÊNCIA"])
                    
                    if not cadernos_disponiveis:
                        st.info("Todos os estudantes ausentes nesta aplicação.")
                    else:
                        with st.container(border=True):
                            caderno_alvo = st.segmented_control("Caderno Avaliado:", cadernos_disponiveis, default=cadernos_disponiveis[0], key=f"cad_alvo_pills_raiox_{v}")
                        
                        df_filtrado = df_analise[df_analise['CADERNO_FEITO'] == caderno_alvo]
                        
                        material_ref = None
                        is_pei_view = "PEI" in str(caderno_alvo)
                        is_2a_chamada = "Segunda Chamada" in str(caderno_alvo) or "Discursiva" in str(caderno_alvo)
                        
                        if is_2a_chamada:
                            df_busca = df_aulas[(df_aulas['TIPO_MATERIAL'].str.upper().str.contains("2ª|2CHAMADA|DISCURSIVA|RECUPERA", regex=True)) & (df_aulas['TIPO_MATERIAL'].str.contains(padrao_regex_trim, regex=True, case=False)) & (df_aulas['ANO'].str.contains(serie_num_r))] if not df_aulas.empty else pd.DataFrame()
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
                            st.info("Avaliação discursiva/segunda chamada com pontuação lançada na folha do estudante.")
                        elif "Qualitativa" in str(caderno_alvo):
                            st.info("Avaliação qualitativa baseada em rubricas no Dossiê do Estudante.")
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
                                
                                with st.container(border=True):
                                    c_m1, c_m2, c_m3 = st.columns(3)
                                    c_m1.metric("Menor Taxa de Acerto", f"{worst_q['Questão']} ({worst_q['Acerto %']:.1f}%)", delta_color="inverse")
                                    c_m2.metric("Maior Domínio", f"{best_q['Questão']} ({best_q['Acerto %']:.1f}%)")
                                    c_m3.metric("Retenção Média da Classe", f"{avg_ret:.1f}%")

                                st.markdown(f"#### Desempenho por Item: **{caderno_alvo}**")
                                fig_global = px.bar(df_stats_global, x="Questão", y="Acerto %", text_auto='.0f', color="Acerto %", color_continuous_scale="RdYlGn")
                                fig_global.update_layout(yaxis_range=[0, 110], height=260, margin=dict(l=20, r=20, t=20, b=20))
                                st.plotly_chart(fig_global, use_container_width=True)

                                st.markdown("---")
                                
                                c_aut1, c_aut2 = st.columns([1.5, 1.5])
                                
                                with c_aut1:
                                    st.markdown("#### Autópsia do Item")
                                    c_sel, c_btn = st.columns([2, 1])
                                    q_sel = c_sel.selectbox("Selecione o Item:", df_stats_global["Questão"].tolist(), key=f"sel_q_inspect_raiox_{v}", label_visibility="collapsed")

                                    if c_btn.button("Analisar Item", use_container_width=True, key=f"btn_autopsia_item_raiox_{v}"):
                                        stats_row = df_stats_global[df_stats_global['Questão'] == q_sel].iloc[0]
                                        dialog_autopsia_modal(q_sel, stats_row, txt_prova_base, is_pei_view, caderno_alvo)

                                with c_aut2:
                                    st.markdown("#### Inteligência & Recomposição")
                                    c_pr1, c_pr2 = st.columns(2)
                                    
                                    if c_pr1.button("Diagnóstico Psicométrico", use_container_width=True, key=f"btn_gen_prog_raiox_{v}"):
                                        with st.spinner("Analisando padrões de resposta..."):
                                            worst_3 = df_stats_global.sort_values(by="Acerto %").head(3)
                                            stats_str = "\n".join([f"{r['Questão']}: {r['Acerto %']:.1f}% de acerto" for _, r in worst_3.iterrows()])
                                            
                                            contexto_str = ""
                                            tag_grade = "GRADE_DE_CORRECAO_PEI" if is_pei_view else "GRADE_DE_CORRECAO"
                                            grade_raw = ai.extrair_tag(txt_prova_base, tag_grade)
                                            prefixo_q = r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)"
                                            
                                            for _, r in worst_3.iterrows():
                                                idx_num = int(r['Questão'].replace("Q", ""))
                                                padrao_q = rf"(?si)({prefixo_q}\s*0?{idx_num}\b.*?)(?={prefixo_q}\s*0?{idx_num+1}\b|GABARITO|RESPOSTAS|GRADE|$)"
                                                m_p_reg = re.search(padrao_q, grade_raw)
                                                if m_p_reg: contexto_str += f"Erro na {r['Questão']}: {re.sub(r'[*#]', '', m_p_reg.group(1).strip())}\n"
                                            
                                            res_prog = ai.gerar_prognostico_pedagogico(stats_str, contexto_str)
                                            st.session_state[f"prog_{v}"] = res_prog

                                    if c_pr2.button("Gerar Caderno de Recomposição", type="primary", use_container_width=True, key=f"btn_ponte_recomp_raiox_{v}"):
                                        with st.status("Estruturando caderno de recomposição focado nos itens críticos...", expanded=True) as status_rec_auto:
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

                                            status_rec_auto.write("Compilando Folha do Estudante...")
                                            doc_alu_rec = exporter.gerar_docx_aluno_v24(nome_recomp_auto, ai.extrair_tag(res_recomp_auto, "ALUNO"), info_recomp_auto)
                                            link_alu_rec = db.subir_e_converter_para_google_docs(doc_alu_rec, f"{nome_recomp_auto}_ALUNO", modo="AULA")

                                            status_rec_auto.write("Compilando Guia Docente...")
                                            doc_prof_rec = exporter.gerar_docx_professor_v25(nome_recomp_auto, ai.extrair_tag(res_recomp_auto, "PROFESSOR"), info_recomp_auto)
                                            link_prof_rec = db.subir_e_converter_para_google_docs(doc_prof_rec, f"{nome_recomp_auto}_PROF", modo="AULA")

                                            conteudo_final_rec = f"{res_recomp_auto}\n\n--- LINKS ---\nRegular({link_alu_rec}) Prof({link_prof_rec})"

                                            db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                                datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_recomp_auto,
                                                conteudo_final_rec, f"{serie_num_r}º", link_alu_rec
                                            ])

                                            status_rec_auto.update(label="Caderno de Recomposição sincronizado no Google Drive!", state="complete")
                                            st.balloons()
                                            st.link_button("Abrir Caderno no Drive", link_alu_rec, type="primary", use_container_width=True)

                                if f"prog_{v}" in st.session_state:
                                    st.info(f"**Prognóstico Psicométrico:**\n\n{st.session_state[f'prog_{v}']}")







# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO RÁPIDO - V2026.PRO_EXECUTIVE_ULTRA
# (LANÇAMENTO TOUCH EM TEMPO REAL, VISTOS DE CADERNO E GESTÃO ATITUDINAL)
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("Diário de Bordo Rápido")
    st.caption("Lançamento ágil em tempo real adaptado para smartphone e desktop: controle de frequência, vistos táteis de caderno e pontuação atitudinal.")
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
        st.warning("Nenhuma turma cadastrada no sistema. Cadastre as turmas no cockpit de Gestão da Turma.")
    else:
        with st.container(border=True):
            c_d1, c_d2 = st.columns([1.5, 1])
            turma_dr = c_d1.selectbox("Turma Selecionada:", lista_turmas_diario, key=f"dr_turma_{v_dr}")
            data_dr = c_d2.date_input("Data da Aula:", date.today(), format="DD/MM/YYYY", key=f"dr_data_{v_dr}")
            data_dr_str = data_dr.strftime("%d/%m/%Y")

        df_alunos_base_dr = df_alunos[df_alunos['TURMA'] == turma_dr].copy() if not df_alunos.empty else pd.DataFrame()
        if 'STATUS' not in df_alunos_base_dr.columns: df_alunos_base_dr['STATUS'] = "ATIVO"
        alunos_dr = df_alunos_base_dr[~df_alunos_base_dr['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")

        if alunos_dr.empty:
            st.info(f"Nenhum estudante ativo cadastrado na turma {turma_dr}.")
        else:
            aula_registro = df_registro_aulas[(df_registro_aulas['DATA'] == data_dr_str) & (df_registro_aulas['TURMA'] == turma_dr)] if not df_registro_aulas.empty else pd.DataFrame()
            conteudo_aula_hoje = aula_registro.iloc[0]['CONTEUDO_MINISTRADO'] if not aula_registro.empty else "Registro Regular de Sala de Aula"

            st.caption(f"Aula ({data_dr_str}): **{conteudo_aula_hoje}**")
            diario_dia_atual = df_diario[(df_diario['DATA'] == data_dr_str) & (df_diario['TURMA'] == turma_dr)] if not df_diario.empty else pd.DataFrame()

            @st.fragment
            def renderizar_diario_rapido_fragmento():
                key_presenca = f"dr_presencas_{turma_dr}_{data_dr_str}"
                key_vistos = f"dr_vistos_{turma_dr}_{data_dr_str}"
                key_tags = f"dr_tags_{turma_dr}_{data_dr_str}"
                key_obs = f"dr_obs_{turma_dr}_{data_dr_str}"

                # Inicialização de estado reativo
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

                # Cálculos rápidos de métricas ao vivo
                tot_alunos_dr = len(alunos_dr)
                cnt_presentes = sum(1 for v in st.session_state[key_presenca].values() if v)
                cnt_ausentes = tot_alunos_dr - cnt_presentes
                cnt_vistos = sum(1 for al_id, v in st.session_state[key_vistos].items() if v and st.session_state[key_presenca].get(al_id, True))
                
                perc_pres_ao_vivo = (cnt_presentes / tot_alunos_dr * 100) if tot_alunos_dr > 0 else 0
                perc_visto_ao_vivo = (cnt_vistos / cnt_presentes * 100) if cnt_presentes > 0 else 0

                # Bento Card de Métricas ao Vivo
                with st.container(border=True):
                    k_dr1, k_dr2, k_dr3, k_dr4 = st.columns(4)
                    k_dr1.metric("Estudantes na Turma", tot_alunos_dr)
                    k_dr2.metric("Presentes em Sala", f"{cnt_presentes} ({perc_pres_ao_vivo:.0f}%)", delta="OK" if cnt_presentes > 0 else None)
                    k_dr3.metric("Ausências Registradas", cnt_ausentes, delta_color="inverse" if cnt_ausentes > 0 else "normal")
                    k_dr4.metric("Cadernos Vistados", f"{cnt_vistos} ({perc_visto_ao_vivo:.0f}%)")

                # Seletor de Modo de Visualização
                c_mode1, c_mode2 = st.columns([1.5, 2.5])
                modo_view_dr = c_mode1.segmented_control(
                    "Modo de Lançamento:",
                    ["📱 Modo Touch (Mobile)", "💻 Tabela Direta (Desktop)"],
                    default="📱 Modo Touch (Mobile)",
                    key=f"dr_view_mode_{v_dr}"
                )

                # Barra de Ações Rápidas em 1 Toque
                c_act_dr1, c_act_dr2, c_act_dr3, c_act_dr4 = st.columns(4)
                if c_act_dr1.button("✅ Todos Presentes", use_container_width=True, key=f"btn_all_p_{v_dr}"):
                    for al_id in st.session_state[key_presenca]: st.session_state[key_presenca][al_id] = True
                    st.rerun()

                if c_act_dr2.button("📘 Todos com Visto", use_container_width=True, key=f"btn_all_v_{v_dr}"):
                    for al_id in st.session_state[key_vistos]: 
                        if st.session_state[key_presenca].get(al_id, True):
                            st.session_state[key_vistos][al_id] = True
                    st.rerun()

                if c_act_dr3.button("🔄 Inverter Presenças", use_container_width=True, key=f"btn_inv_p_{v_dr}"):
                    for al_id in st.session_state[key_presenca]:
                        st.session_state[key_presenca][al_id] = not st.session_state[key_presenca][al_id]
                    st.rerun()

                if c_act_dr4.button("🧹 Limpar Lançamentos", use_container_width=True, key=f"btn_res_dr_{v_dr}"):
                    del st.session_state[key_presenca]; del st.session_state[key_vistos]
                    del st.session_state[key_tags]; del st.session_state[key_obs]
                    st.rerun()

                st.markdown("---")

                # ==============================================================
                # MODO 1: CARTÕES TOUCH (MOBILE FIRST)
                # ==============================================================
                if "Touch" in modo_view_dr:
                    filtro_mob = st.pills(
                        "Filtrar Visualização:", 
                        ["Todos", "Ausentes", "Com Visto", "Sem Visto", "Com Ocorrência / Bônus"], 
                        default="Todos",
                        key=f"flt_mob_pills_{v_dr}"
                    )
                    if not filtro_mob: filtro_mob = "Todos"

                    options_tags_mob = ["Destaque (+0.5)", "Arguição (+0.5)", "Conversa", "Uso de Celular", "Atraso", "Def. Leitura", "Def. Matemática", "Indisciplina (-0.5)"]

                    def definir_badge_perfil(nec):
                        n = str(nec).upper().strip()
                        if "PEI" in n or "TEA" in n or "LAUDO" in n: return "♿ PEI"
                        if "DEFASAGEM" in n: return "🧮 Apoio"
                        if "ALTA" in n: return "🚀 Avançado"
                        return "👤 Regular"

                    for _, alu in alunos_dr.iterrows():
                        id_l = db.limpar_id(alu['ID'])
                        nome_a = str(alu['NOME_ALUNO'])
                        badge_p = definir_badge_perfil(alu.get('NECESSIDADES', 'TÍPICO'))
                        
                        is_pres = st.session_state[key_presenca].get(id_l, True)
                        is_visto = st.session_state[key_vistos].get(id_l, False)
                        tag_atual = st.session_state[key_tags].get(id_l, "")

                        # Lógica de Filtros
                        if filtro_mob == "Ausentes" and is_pres: continue
                        if filtro_mob == "Com Visto" and (not is_visto or not is_pres): continue
                        if filtro_mob == "Sem Visto" and (is_visto or not is_pres): continue
                        if filtro_mob == "Com Ocorrência / Bônus" and not tag_atual: continue

                        with st.container(border=True):
                            c_card1, c_card2, c_card3 = st.columns([2.2, 1.2, 1.2])
                            
                            with c_card1:
                                st.markdown(f"**{nome_a}**")
                                st.caption(f"ID: `{id_l}` • {badge_p}")
                            
                            # Botão de Presença com Alternância de Cores
                            with c_card2:
                                if is_pres:
                                    if st.button("🟢 Presente", key=f"btn_p_mob_{id_l}_{v_dr}", use_container_width=True):
                                        st.session_state[key_presenca][id_l] = False
                                        st.session_state[key_vistos][id_l] = False
                                        st.rerun()
                                else:
                                    if st.button("🔴 Ausente", key=f"btn_p_mob_{id_l}_{v_dr}", type="primary", use_container_width=True):
                                        st.session_state[key_presenca][id_l] = True
                                        st.rerun()

                            # Botão de Visto com Alternância de Cores
                            with c_card3:
                                if is_pres:
                                    if is_visto:
                                        if st.button("📘 Visto OK", key=f"btn_v_mob_{id_l}_{v_dr}", type="primary", use_container_width=True):
                                            st.session_state[key_vistos][id_l] = False
                                            st.rerun()
                                    else:
                                        if st.button("⚪ Sem Visto", key=f"btn_v_mob_{id_l}_{v_dr}", use_container_width=True):
                                            st.session_state[key_vistos][id_l] = True
                                            st.rerun()
                                else:
                                    st.button("🚫 Bloqueado", key=f"btn_v_dis_{id_l}_{v_dr}", disabled=True, use_container_width=True)

                            # Área Atitudinal e Observação
                            if is_pres:
                                default_tag_mob = tag_atual if tag_atual in options_tags_mob else None
                                tag_sel_mob = st.segmented_control(
                                    "Registro Atitudinal / Mérito:",
                                    options_tags_mob,
                                    default=default_tag_mob,
                                    key=f"seg_tag_mob_{id_l}_{v_dr}"
                                )
                                st.session_state[key_tags][id_l] = tag_sel_mob if tag_sel_mob else ""

                            obs_mob = st.text_input(
                                "Observação Pedagógica (Voz ou Texto):",
                                value=st.session_state[key_obs].get(id_l, ""),
                                key=f"inp_obs_mob_{id_l}_{v_dr}",
                                placeholder="Anotação sobre participação, tarefa ou comportamento..."
                            )
                            st.session_state[key_obs][id_l] = obs_mob

                # ==============================================================
                # MODO 2: TABELA DIRETA (DESKTOP)
                # ==============================================================
                else:
                    dados_grid = []
                    for _, alu in alunos_dr.iterrows():
                        id_l = db.limpar_id(alu['ID'])

                        dados_grid.append({
                            "ID": id_l,
                            "Estudante": alu['NOME_ALUNO'],
                            "Presente": st.session_state[key_presenca].get(id_l, True),
                            "Visto OK": st.session_state[key_vistos].get(id_l, False),
                            "Registro Atitudinal": st.session_state[key_tags].get(id_l, ""),
                            "Observação Rápida": st.session_state[key_obs].get(id_l, "")
                        })

                    df_grid_ed = st.data_editor(
                        pd.DataFrame(dados_grid),
                        hide_index=True, use_container_width=True, height=450,
                        column_config={
                            "ID": None,
                            "Estudante": st.column_config.TextColumn("Estudante", disabled=True, width="medium"),
                            "Presente": st.column_config.CheckboxColumn("Presente", default=True, width="small"),
                            "Visto OK": st.column_config.CheckboxColumn("Visto OK", default=False, width="small"),
                            "Registro Atitudinal": st.column_config.SelectboxColumn(
                                "Registro Atitudinal", 
                                options=["", "Destaque (+0.5)", "Arguição (+0.5)", "Conversa", "Uso de Celular", "Def. Leitura", "Def. Matemática", "Indisciplina (-0.5)", "Atraso"], 
                                width="medium"
                            ),
                            "Observação Rápida": st.column_config.TextColumn("Observação Pedagógica", width="large")
                        },
                        key=f"ed_grid_dr_{v_dr}"
                    )

                    for _, r_ed in df_grid_ed.iterrows():
                        al_id = r_ed['ID']
                        st.session_state[key_presenca][al_id] = r_ed['Presente']
                        st.session_state[key_vistos][al_id] = r_ed['Visto OK']
                        st.session_state[key_tags][al_id] = str(r_ed['Registro Atitudinal']) if pd.notna(r_ed['Registro Atitudinal']) else ""
                        st.session_state[key_obs][al_id] = str(r_ed['Observação Rápida']) if pd.notna(r_ed['Observação Rápida']) else ""

                st.markdown("---")

                # ==============================================================
                # DISPARO RÁPIDO PARA WHATSAPP (AUSENTES DO DIA)
                # ==============================================================
                with st.expander("📲 Disparo de Ausências para WhatsApp da Coordenação", expanded=False):
                    ausentes_nomes = [
                        str(alu['NOME_ALUNO']) 
                        for _, alu in alunos_dr.iterrows() 
                        if not st.session_state[key_presenca].get(db.limpar_id(alu['ID']), True)
                    ]
                    
                    if not ausentes_nomes:
                        st.success("Nenhuma ausência registrada para esta aula (100% de presença).")
                    else:
                        txt_zap_ausentes = (
                            f"📋 *RELATÓRIO DE AUSÊNCIAS — {turma_dr}*\n"
                            f"📅 Data: {data_dr_str} | Componente: Matemática\n"
                            f"👨‍🏫 Professor: Ronaldo Gomes\n\n"
                            f"Estudantes Ausentes ({len(ausentes_nomes)}):\n" +
                            "\n".join([f"• {n}" for n in ausentes_nomes]) +
                            f"\n\n_Escola Municipal Flávio José Simões Costa_"
                        )
                        st.caption("Clique no ícone de cópia abaixo para colar no WhatsApp:")
                        st.code(txt_zap_ausentes, language=None)

                st.markdown("<br>", unsafe_allow_html=True)

                # ==============================================================
                # CONSOLIDAÇÃO FINAL NO BANCO DE DADOS
                # ==============================================================
                if st.button("Consolidar Diário da Aula", type="primary", use_container_width=True, key=f"btn_save_dr_{v_dr}"):
                    with st.spinner("Gravando presenças, vistos e ocorrências no diário..."):
                        linhas_salvar = []
                        data_hoje_save = data_dr_str

                        # Contagem de vistos para aplicação da Lei nº 23 (Auto-Isenção Coletiva)
                        total_vistos_dados_hoje = sum(
                            1 for _, alu_c in alunos_dr.iterrows()
                            if st.session_state[key_vistos].get(db.limpar_id(alu_c['ID']), False) and st.session_state[key_presenca].get(db.limpar_id(alu_c['ID']), True)
                        )

                        for _, alu in alunos_dr.iterrows():
                            al_id = db.limpar_id(alu['ID'])
                            nome_limpo = alu['NOME_ALUNO'].replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                            
                            is_presente = st.session_state[key_presenca].get(al_id, True)
                            is_visto_check = st.session_state[key_vistos].get(al_id, False)
                            tag_sel = str(st.session_state[key_tags].get(al_id, "")).strip()
                            obs_text = str(st.session_state[key_obs].get(al_id, "")).strip()

                            bonus_val = "0,00"
                            if "Destaque" in tag_sel or "Arguição" in tag_sel or "+0.5" in tag_sel: 
                                bonus_val = "0,50"
                            elif "Indisciplina" in tag_sel or "-0.5" in tag_sel: 
                                bonus_val = "-0,50"

                            if not is_presente:
                                tag_final = "AUSÊNCIA"
                                visto_final = "FALSE"
                            else:
                                tag_final = tag_sel
                                # Lei 23: Se 0 vistos foram dados na aula inteira, marca ISENTO
                                if total_vistos_dados_hoje == 0:
                                    visto_final = "ISENTO"
                                else:
                                    visto_final = "TRUE" if is_visto_check else "FALSE"

                            linhas_salvar.append([
                                data_hoje_save, al_id, nome_limpo, turma_dr,
                                visto_final, tag_final, obs_text, bonus_val
                            ])

                        if linhas_salvar:
                            db.limpar_diario_data_turma(data_hoje_save, turma_dr)
                            db.salvar_lote("DB_DIARIO_BORDO", linhas_salvar)
                            
                            if total_vistos_dados_hoje == 0:
                                st.toast("Diário registrado! Vistos marcados como ISENTO coletivo para proteger as notas dos estudantes.", icon="🛡️")
                            else:
                                st.toast(f"Diário consolidado com sucesso! ({cnt_presentes} presentes, {cnt_vistos} vistos)", icon="✅")
                                
                            st.balloons()
                            time.sleep(0.6)
                            st.rerun()

            renderizar_diario_rapido_fragmento()







# ==============================================================================
# MÓDULO: BIOGRAFIA DO ESTUDANTE - V2026.PRO_EXECUTIVE_REACTIVE
# (DOSSIÊ 360°, BOLETIM ANALÍTICO, META PREDITIVA III TRI, PROVAS E PEI)
# ==============================================================================
elif menu == "👤 Biografia do Estudante":
    st.title("Biografia do Estudante (Dossiê 360°)")
    st.caption("Extrato individual de rendimento escolar: histórico de notas C1/C2/C3, simulador preditivo para o III Trimestre, auditoria de avaliações e registro atitudinal.")
    st.markdown("---")

    if "v_bio" not in st.session_state: 
        st.session_state.v_bio = int(time.time())
    v = st.session_state.v_bio

    # ==============================================================================
    # DIALOGS DECLARADOS NO TOPO DO MÓDULO (LEI #25)
    # ==============================================================================
    @st.dialog("Tribunal de Recursos & Contestação de Avaliação", width="large")
    def dialog_tribunal(id_aluno_dialog, nome_aluno_dialog, is_pei_dialog, df_diag_dialog, turma_dialog, trim_dialog):
        opcoes_av_tribunal = df_diag_dialog['ID_AVALIACAO'].tolist() if not df_diag_dialog.empty and 'ID_AVALIACAO' in df_diag_dialog.columns else []
        if not opcoes_av_tribunal:
            st.info("Nenhuma avaliação escaneada localizada para este estudante.")
        else:
            av_contestada = st.selectbox("1. Selecione a Avaliação Questionada:", opcoes_av_tribunal, key=f"trib_av_pop_{v}")
            if av_contestada:
                reg_av_trib = df_diag_dialog[df_diag_dialog['ID_AVALIACAO'] == av_contestada].iloc[0]
                respostas_aluno_trib = str(reg_av_trib.get('RESPOSTAS_ALUNO', '')).split(';')
                link_foto_trib = str(reg_av_trib.get('LINK_FOTO_DRIVE', ''))
                
                nome_base_av = av_contestada.replace(" (2ª CHAMADA)", "").strip()
                if "VARIANTE" in nome_base_av.upper() or "TIPO" in nome_base_av.upper():
                    tipo_letra = re.search(r'TIPO\s*([A-Z])', nome_base_av, re.IGNORECASE)
                    letra = tipo_letra.group(1) if tipo_letra else "B"
                    nome_busca = f"{nome_base_av.split('(')[0].strip()} - TIPO {letra}"
                else: nome_busca = nome_base_av
                    
                df_prova_trib = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_base_av.split('(')[0].strip(), case=False, na=False)] if not df_aulas.empty and 'TIPO_MATERIAL' in df_aulas.columns else pd.DataFrame()
                
                if not df_prova_trib.empty:
                    txt_prova_trib = str(df_prova_trib.iloc[0].get('CONTEUDO', ''))
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
                        
                    qtd_questoes_trib = len(gab_oficial_trib) if len(gab_oficial_trib) > 0 else 10
                    val_total_prova = util.extrair_valor_real_prova(txt_prova_trib, av_contestada)
                    
                    q_contestada = st.selectbox("2. Selecione o Item:", [f"Questão {i}" for i in range(1, qtd_questoes_trib + 1)], key=f"trib_q_pop_{v}")
                    q_num_trib = int(q_contestada.split(" ")[1])
                    
                    letra_marcada_trib = respostas_aluno_trib[q_num_trib - 1].replace("*", "") if q_num_trib <= len(respostas_aluno_trib) else "?"
                    letra_correta_trib = gab_oficial_trib.get(q_num_trib, "?")
                    
                    prefixo_q_trib = "QUEST[AÃ]O\\s*PEI" if is_pei_dialog else "QUEST[AÃ]O"
                    padrao_q_trib = rf"(?si)({prefixo_q_trib}\s*0?{q_num_trib}\b.*?)(?={prefixo_q_trib}\s*0?{q_num_trib+1}\b|GABARITO|$)"
                    m_q_trib = re.search(padrao_q_trib, questoes_raw_trib)
                    enunciado_trib = m_q_trib.group(1).strip() if m_q_trib else "Enunciado não localizado."
                    
                    padrao_p_trib = rf"(?si){prefixo_q_trib}\s*0?{q_num_trib}\b.*?(?={prefixo_q_trib}\s*0?{q_num_trib+1}\b|GABARITO|RESPOSTAS|$)"
                    m_p_trib = re.search(padrao_p_trib, grade_raw_trib)
                    pericia_trib = m_p_trib.group(0).strip() if m_p_trib else "Perícia não localizada."
                    
                    st.markdown("#### Evidência da Avaliação")
                    with st.container(border=True):
                        c_ev1, c_ev2 = st.columns([3, 1])
                        c_ev1.markdown(f"**Estudante:** {nome_aluno_dialog} | **Avaliação:** {nome_base_av} (Valor: **{val_total_prova:.1f} pts**)")
                        if "http" in link_foto_trib: c_ev2.link_button("Visualizar Imagem", link_foto_trib, use_container_width=True)
                        
                        st.divider()
                        st.info(util.preparar_para_leitura(enunciado_trib).replace('\n', '\n\n'))
                        
                        c_res1, c_res2 = st.columns(2)
                        c_res1.error(f"**Resposta Marcada:** {letra_marcada_trib}")
                        c_res2.success(f"**Chave Oficial:** {letra_correta_trib}")
                        
                        st.warning(f"**Perícia do Item:**\n{util.preparar_para_leitura(pericia_trib)}")
                        
                    st.markdown("#### Veredito Pedagógico")
                    c_ver1, c_ver2 = st.columns(2)
                    
                    if c_ver1.button("Manter Pontuação (Gerar Justificativa)", use_container_width=True, key=f"btn_def_trib_pop_{v}"):
                        with st.spinner("Redigindo parecer técnico..."):
                            prompt_defesa = f"VEREDITO: MANTER NOTA.\nALUNO: {nome_aluno_dialog}.\nQUESTÃO: {q_num_trib}.\nMARCOU: {letra_marcada_trib}. CORRETA: {letra_correta_trib}.\nPERÍCIA/ERRO: {pericia_trib}.\nENUNCIADO: {enunciado_trib}."
                            st.session_state.msg_tribunal = ai.gerar_ia("DEFENSOR_PEDAGOGICO", prompt_defesa)
                            
                    if c_ver2.button("Retificar Pontuação", use_container_width=True, key=f"btn_corr_trib_pop_{v}"):
                        st.session_state.modo_correcao_tribunal = True
                        
                    if st.session_state.get("modo_correcao_tribunal", False):
                        with st.container(border=True):
                            st.caption("Modo de Retificação Ativo:")
                            nova_letra = st.selectbox("Qual alternativa foi efetivamente assinalada?", ["A", "B", "C", "D", "E"], index=["A", "B", "C", "D", "E"].index(letra_correta_trib) if letra_correta_trib in ["A", "B", "C", "D", "E"] else 0, key=f"sel_letra_trib_pop_{v}")
                            
                            novas_respostas_sim = respostas_aluno_trib.copy()
                            if q_num_trib - 1 < len(novas_respostas_sim): novas_respostas_sim[q_num_trib - 1] = nova_letra
                            else: novas_respostas_sim.append(nova_letra)
                            
                            acertos_novos_sim = sum(1 for i, r in enumerate(novas_respostas_sim) if i+1 in gab_oficial_trib and r.replace("*","") == gab_oficial_trib[i+1])
                            peso_item = val_total_prova / qtd_questoes_trib if qtd_questoes_trib > 0 else 0.4
                            nova_nota_prova_sim = acertos_novos_sim * peso_item
                            
                            st.info(f"📊 **Simulação da Nova Nota:** {acertos_novos_sim}/{qtd_questoes_trib} acertos ➔ **{nova_nota_prova_sim:.1f} / {val_total_prova:.1f} pontos**")

                            if st.button("Confirmar Retificação e Recalcular Média", type="primary", key=f"btn_conf_trib_pop_{v}"):
                                with st.spinner("Retificando gabarito e recalculando boletim..."):
                                    nova_nota_prova = nova_nota_prova_sim
                                    
                                    try:
                                        wb = db.conectar()
                                        ws_gab = wb.worksheet("DB_GABARITOS_ALUNOS")
                                        dados_gab = ws_gab.get_all_values()
                                        for i, row in enumerate(dados_gab):
                                            if i > 0 and db.limpar_id(row[1]) == id_aluno_dialog and row[4] == av_contestada:
                                                ws_gab.update_cell(i+1, 6, ";".join(novas_respostas_sim))
                                                ws_gab.update_cell(i+1, 7, util.sosa_to_str(nova_nota_prova))
                                                break
                                    except Exception as e: st.error(f"Erro ao atualizar banco: {e}")
                                        
                                    db.limpar_notas_turma_trimestre(turma_dialog, trim_dialog)
                                    st.cache_data.clear()
                                    prompt_retratacao = f"VEREDITO: CORRIGIR NOTA.\nALUNO: {nome_aluno_dialog}.\nQUESTÃO: {q_num_trib}.\nNOVA NOTA DA AVALIAÇÃO: {nova_nota_prova:.1f} DE {val_total_prova:.1f} PONTOS."
                                    st.session_state.msg_tribunal = ai.gerar_ia("DEFENSOR_PEDAGOGICO", prompt_retratacao)
                                    st.session_state.modo_correcao_tribunal = False
                                    st.success(f"Nota retificada com sucesso para {nova_nota_prova:.1f} pontos!")
                                    time.sleep(0.6); st.rerun()
                                    
                    if "msg_tribunal" in st.session_state:
                        st.markdown("#### Texto de Resposta para WhatsApp")
                        st.caption("Texto formatado para envio aos responsáveis:")
                        st.code(st.session_state.msg_tribunal, language=None)
                else: st.warning("A avaliação original não foi localizada no acervo para perícia.")

    @st.dialog("Extrato de Rendimento para WhatsApp", width="large")
    def dialog_whatsapp(nome_limpo_dialog, turma_dialog, status_aluno_dialog, soma_acumulada_dialog, meta_iii_dialog, status_meta_dialog, assiduidade_dialog, faltas_dialog, engajamento_dialog, bonus_dialog, regra_arredondamento_text):
        st.caption("Texto executivo pronto para cópia e envio à família:")
        
        soma_fmt = f"{util.sosa_to_float(soma_acumulada_dialog):.1f}"
        meta_iii_fmt = f"{util.sosa_to_float(meta_iii_dialog):.1f}"
        assid_fmt = f"{util.sosa_to_float(assiduidade_dialog):.0f}"
        engaj_fmt = f"{util.sosa_to_float(engajamento_dialog):.0f}"
        bonus_fmt = f"{util.sosa_to_float(bonus_dialog):+.1f}"

        if meta_iii_dialog == 0.0:
            parecer_iii = "SITUAÇÃO EXCELENTE: O(A) estudante já acumulou os 18,0 pontos regimentais (soma do I e II Tri) e está APROVADO(A) POR ANTECIPAÇÃO no componente de Matemática!"
        else:
            parecer_iii = f"Para garantir a aprovação sem recuperação final, o(a) estudante precisa de {meta_iii_fmt} pontos no III Trimestre ({status_meta_dialog})."
        
        msg_zap = f"""Olá! Tudo bem? Aqui é o Prof. Ronaldo Gomes (Componente Curricular de Matemática). 🏫
Compartilho com a família o Dossiê de Rendimento e Participação do(a) estudante {nome_limpo_dialog} ({turma_dialog}).

📌 SITUAÇÃO REGIMENTAL: {status_aluno_dialog}
📊 RENDIMENTO ACUMULADO NO ANO (I e II TRIMESTRES):
• Soma Total dos Pontos Conquistados: {soma_fmt} pontos (Meta Anual: 18,0 pts).
• Projeção para o III Trimestre: {parecer_iii}

🎯 ASSIDUIDADE E COMPROMISSO COM O CADERNO:
• Frequência em Sala de Aula: {assid_fmt}% ({faltas_dialog} ausência(s) registrada(s)).
• Cumprimento de Tarefas de Caderno (Vistos C1): {engaj_fmt}% das atividades concluídas.
• Bônus Pedagógico de Mérito/Atitude: {bonus_fmt} pts acumulados!

ℹ️ NOTA EXPLICATIVA SOBRE O ARREDONDAMENTO:
{regra_arredondamento_text}

Seguimos à disposição para acompanhar o desenvolvimento do estudante. Um abraço! 🚀
Escola Municipal Flávio José Simões Costa"""
        st.code(msg_zap, language=None)

    if df_alunos.empty:
        st.warning("Base de estudantes vazia. Cadastre as turmas na Gestão da Turma.")
    else:
        opcoes_periodo_bio = ["Todos", "I Trimestre", "II Trimestre", "III Trimestre"]

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([1, 1.2, 1.5, 1])
            
            lista_turmas_bio = []
            if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
                turmas_reais_bio = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
                lista_turmas_bio = sorted(turmas_reais_bio['ID_TURMA'].unique())
            elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
                lista_turmas_bio = sorted(df_alunos['TURMA'].unique())
            
            turma_b = c1.selectbox("Turma:", lista_turmas_bio, key="bio_turma_sel_react")
            flt_status_bio = c2.segmented_control("Status:", ["Ativos", "Inativos / Transferidos"], default="Ativos", key="bio_status_sel_react")
            
            df_alunos_turma_raw = df_alunos[df_alunos['TURMA'] == turma_b].copy() if not df_alunos.empty and 'TURMA' in df_alunos.columns else pd.DataFrame()
            if 'STATUS' not in df_alunos_turma_raw.columns: df_alunos_turma_raw['STATUS'] = "ATIVO"
            
            if flt_status_bio == "Ativos":
                lista_alunos = df_alunos_turma_raw[~df_alunos_turma_raw['STATUS'].astype(str).str.upper().isin(["TRANSFERIDO", "EVADIDO", "INATIVO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")
            else:
                lista_alunos = df_alunos_turma_raw[df_alunos_turma_raw['STATUS'].astype(str).str.upper().isin(["TRANSFERIDO", "EVADIDO", "INATIVO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")

            if lista_alunos.empty:
                st.info("Nenhum estudante localizado para este filtro na turma.")
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
                
            aluno_b_label = c3.selectbox("Estudante:", lista_alunos['LABEL'].tolist(), key="bio_aluno_sel_react")
            
            trim_b = c4.segmented_control("Período:", opcoes_periodo_bio, default="Todos", key="bio_periodo_sel_react")
            if not trim_b: trim_b = "Todos"

        nome_limpo = aluno_b_label.split(" ", 1)[1].strip() 
        info_alu = lista_alunos[lista_alunos['NOME_ALUNO'] == nome_limpo].iloc[0]
        id_alu = db.limpar_id(info_alu.get('ID', ''))
        perfil_atual = str(info_alu.get('NECESSIDADES', 'TÍPICO')).upper().strip()
        status_atual_aluno = str(info_alu.get('STATUS', 'ATIVO')).upper().strip()
        is_pei_or_gap = perfil_atual not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]
        
        n_alu = df_notas[df_notas['ID_ALUNO'].apply(db.limpar_id) == id_alu] if not df_notas.empty and 'ID_ALUNO' in df_notas.columns else pd.DataFrame()

        # Resgate das datas oficiais com aplicação estrita do Cadeado / Data de Corte de Vistos
        calendario_trims = {
            "I Trimestre": (date(2026, 2, 9), date(2026, 5, 22)),
            "II Trimestre": (date(2026, 5, 25), date(2026, 9, 4)),
            "III Trimestre": (date(2026, 9, 8), date(2026, 12, 17))
        }

        # Ajusta a data final com base no corte configurado para cada trimestre
        for t_k in calendario_trims.keys():
            corte_salvo = db.obter_config_corte_trimestre(turma_b, t_k)
            if corte_salvo:
                try:
                    dt_corte_obj = datetime.strptime(corte_salvo, "%d/%m/%Y").date()
                    calendario_trims[t_k] = (calendario_trims[t_k][0], dt_corte_obj)
                except: pass

        if trim_b != "Todos":
            dt_ini, dt_fim = calendario_trims.get(trim_b, (date(2026, 1, 1), date(2026, 12, 31)))
        else:
            dt_ini, dt_fim = date(2026, 1, 1), date(2026, 12, 31)

        vistos_live_by_trim = {}
        bonus_live_by_trim = {}
        scanned_teste_by_trim = {}
        scanned_prova_by_trim = {}
        scanned_rec_by_trim = {}

        if not df_diario.empty and 'ID_ALUNO' in df_diario.columns and 'TURMA' in df_diario.columns:
            df_d_aluno_all = df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diario['TURMA'] == turma_b)].copy()
            if not df_d_aluno_all.empty and 'DATA' in df_d_aluno_all.columns:
                df_d_aluno_all['DATA_DT'] = pd.to_datetime(df_d_aluno_all['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                
                for t_nome, (t_i, t_f) in calendario_trims.items():
                    df_d_t_sub = df_d_aluno_all[(df_d_aluno_all['DATA_DT'] >= t_i) & (df_d_aluno_all['DATA_DT'] <= t_f)]
                    if not df_d_t_sub.empty:
                        d_validas = df_d_t_sub[df_d_t_sub.get('VISTO_ATIVIDADE', '').astype(str).str.upper() != "ISENTO"]
                        v_ok = len(d_validas[d_validas.get('VISTO_ATIVIDADE', '').astype(str).str.upper() == "TRUE"])
                        tot_v = len(d_validas['DATA'].unique()) if not d_validas.empty else 1
                        if tot_v == 0: tot_v = 1
                        vistos_live_by_trim[t_nome] = round((v_ok / tot_v * 3.0), 2) if tot_v > 0 else 0.0
                        bonus_live_by_trim[t_nome] = df_d_t_sub.get('BONUS', pd.Series()).apply(util.sosa_to_float).sum()

        if not df_diagnosticos.empty and 'ID_ALUNO' in df_diagnosticos.columns and 'TURMA' in df_diagnosticos.columns:
            df_dg_aluno = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diagnosticos['TURMA'] == turma_b)].copy()
            if not df_dg_aluno.empty:
                for t_nome in ["I Trimestre", "II Trimestre", "III Trimestre"]:
                    padrao_t_reg = util.obter_regex_trimestre(t_nome)
                    scanned_t = df_dg_aluno[df_dg_aluno['ID_AVALIACAO'].astype(str).str.contains(padrao_t_reg, regex=True, case=False, na=False)]
                    
                    if not scanned_t.empty:
                        for _, r_sc in scanned_t.iterrows():
                            id_av_sc = str(r_sc.get('ID_AVALIACAO', '')).upper()
                            resp_sc = str(r_sc.get('RESPOSTAS_ALUNO', '')).upper()
                            nota_sc = 0.0 if (resp_sc.startswith("FALTOU_INJUSTIFICADO") or resp_sc == "FALTOU") else util.sosa_to_float(r_sc.get('NOTA_CALCULADA', 0.0))

                            if any(x in id_av_sc for x in ["RECUPERAÇÃO", "RECUPERACAO", "REC_"]):
                                scanned_rec_by_trim[t_nome] = nota_sc
                            elif any(x in id_av_sc for x in ["TESTE", "SIMULADO", "TRABALHO"]):
                                if "SONDA" not in id_av_sc:
                                    scanned_teste_by_trim[t_nome] = max(scanned_teste_by_trim.get(t_nome, 0.0), nota_sc)
                            elif any(x in id_av_sc for x in ["PROVA", "AVALIAÇÃO", "AVALIACAO", "EXAME", "2ª"]):
                                scanned_prova_by_trim[t_nome] = max(scanned_prova_by_trim.get(t_nome, 0.0), nota_sc)

        notas_consolidadas_trimestres = []
        soma_1_2_preditiva = 0.0

        for t_k in ["I Trimestre", "II Trimestre", "III Trimestre"]:
            reg_t = n_alu[n_alu['TRIMESTRE'] == t_k] if not n_alu.empty and 'TRIMESTRE' in n_alu.columns else pd.DataFrame()
            
            # 1. Prioridade Absoluta: Valores Consolidados Oficiais em DB_NOTAS
            v_c1_banco = util.sosa_to_float(reg_t.iloc[0].get('NOTA_VISTOS', 0.0)) if not reg_t.empty else 0.0
            v_c2_banco = util.sosa_to_float(reg_t.iloc[0].get('NOTA_TESTE', 0.0)) if not reg_t.empty else 0.0
            v_c3_banco = util.sosa_to_float(reg_t.iloc[0].get('NOTA_PROVA', 0.0)) if not reg_t.empty else 0.0
            v_rec_banco = util.sosa_to_float(reg_t.iloc[0].get('NOTA_REC', -1.0)) if not reg_t.empty else -1.0
            m_final_banco = util.sosa_to_float(reg_t.iloc[0].get('MEDIA_FINAL', 0.0)) if not reg_t.empty else 0.0

            # 2. Fallbacks de Leitura ao Vivo
            v_c1_live = vistos_live_by_trim.get(t_k, 0.0)
            v_c2_live = scanned_teste_by_trim.get(t_k, 0.0)
            v_c3_live = scanned_prova_by_trim.get(t_k, 0.0)
            v_rec_live = scanned_rec_by_trim.get(t_k, -1.0)
            b_diario_t = bonus_live_by_trim.get(t_k, 0.0)

            # Se o trimestre já está consolidado no boletim oficial (DB_NOTAS), exibe os valores exatos do banco
            if not reg_t.empty and m_final_banco > 0:
                c1_v = v_c1_banco
                c2_v = v_c2_banco
                c3_v = v_c3_banco
                rec_v = v_rec_banco
                m_final_usada = m_final_banco
                
                # Reconstrói a soma bruta com o bônus real consolidado
                c1_fin = min(3.0, c1_v + max(0.0, b_diario_t))
                rem_b = max(0.0, b_diario_t) - (c1_fin - c1_v)
                c2_fin = min(3.0, c2_v + max(0.0, rem_b))
                rem_b -= (c2_fin - c2_v)
                c3_fin = min(4.0, c3_v + max(0.0, rem_b))
                soma_bruta_t = c1_fin + c2_fin + c3_fin
                media_inicial_t = min(10.0, round(soma_bruta_t * 2) / 2)

            else:
                c1_v = max(v_c1_banco, v_c1_live)
                c2_v = max(v_c2_banco, v_c2_live)
                c3_v = max(v_c3_banco, v_c3_live)
                rec_v = max(v_rec_banco, v_rec_live)

                c1_fin = min(3.0, c1_v + max(0.0, b_diario_t))
                rem_b = max(0.0, b_diario_t) - (c1_fin - c1_v)
                c2_fin = min(3.0, c2_v + max(0.0, rem_b))
                rem_b -= (c2_fin - c2_v)
                c3_fin = min(4.0, c3_v + max(0.0, rem_b))

                soma_bruta_t = c1_fin + c2_fin + c3_fin
                media_inicial_t = min(10.0, round(soma_bruta_t * 2) / 2)

                if rec_v > 0 and media_inicial_t < 6.0:
                    media_com_rec = (media_inicial_t + rec_v) / 2.0
                    m_live_t = min(10.0, max(media_inicial_t, round(media_com_rec * 2) / 2))
                else:
                    m_live_t = media_inicial_t
                
                m_final_usada = m_live_t

            tem_atividade_real = (not reg_t.empty) or (c1_v > 0) or (c2_v > 0) or (c3_v > 0) or (rec_v > 0) or (b_diario_t != 0)

            if tem_atividade_real:
                if t_k in ["I Trimestre", "II Trimestre"]:
                    soma_1_2_preditiva += m_final_usada

                if m_final_usada >= 6.0: sit_trim = "Na Média"
                elif m_final_usada == 5.5: sit_trim = "Refacção (+0.5)"
                else: sit_trim = "Recomposição"

                notas_consolidadas_trimestres.append({
                    "periodo": t_k,
                    "c1": f"{c1_v:.1f}",
                    "c2": f"{c2_v:.1f}",
                    "c3": f"{c3_v:.1f}",
                    "bonus": f"{b_diario_t:+.1f}",
                    "soma_bruta": f"{soma_bruta_t:.2f}",
                    "media_inicial": f"{media_inicial_t:.1f}",
                    "rec": f"{rec_v:.1f}" if rec_v > 0 else "-",
                    "media_final": f"{m_final_usada:.1f}",
                    "media_final_num": m_final_usada,
                    "situacao": sit_trim,
                    "iniciado": True
                })
            else:
                notas_consolidadas_trimestres.append({
                    "periodo": t_k,
                    "c1": "—",
                    "c2": "—",
                    "c3": "—",
                    "bonus": "—",
                    "soma_bruta": "—",
                    "media_inicial": "—",
                    "rec": "—",
                    "media_final": "—",
                    "media_final_num": 0.0,
                    "situacao": "⏳ Em Aberto (A Cursar)",
                    "iniciado": False
                })

        meta_iii_necessaria = max(0.0, 18.0 - soma_1_2_preditiva)
        meta_iii_arred = round(meta_iii_necessaria * 2) / 2

        if soma_1_2_preditiva >= 18.0:
            status_preditivo_aluno = "Aprovado Antecipado"
        elif meta_iii_arred <= 4.0:
            status_preditivo_aluno = "Meta Confortável (≤ 4.0 pts)"
        elif meta_iii_arred <= 6.5:
            status_preditivo_aluno = "Meta Moderada (4.1 a 6.5 pts)"
        elif meta_iii_arred <= 9.9:
            status_preditivo_aluno = "Meta Alta (6.6 a 9.9 pts)"
        else:
            status_preditivo_aluno = "Risco de Recuperação Final (≥ 10.0 pts)"

        # CÁLCULO REATIVO DE ASSIDUIDADE, VISTOS E BÔNUS
        faltas_hero = 0
        perc_presenca_hero_str = "100%"
        perc_visto_hero_str = "0%"
        bonus_total_hero_str = "+0.0 pts"
        delta_faltas_str = "0 falta(s)"

        if not df_diario.empty and 'ID_ALUNO' in df_diario.columns and 'TURMA' in df_diario.columns:
            df_d_aluno_turma = df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diario['TURMA'] == turma_b)].copy()
            if not df_d_aluno_turma.empty and 'DATA' in df_d_aluno_turma.columns:
                df_d_aluno_turma['DATA_DT'] = pd.to_datetime(df_d_aluno_turma['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                
                df_d_periodo = df_d_aluno_turma[(df_d_aluno_turma['DATA_DT'] >= dt_ini) & (df_d_aluno_turma['DATA_DT'] <= dt_fim)]
                df_d_validas = df_d_periodo[~df_d_periodo['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])] if not df_d_periodo.empty else pd.DataFrame()
                
                tot_aulas_reg = len(df_d_validas)
                
                if tot_aulas_reg > 0:
                    faltas_hero = len(df_d_validas[df_d_validas['TAGS'] == "AUSÊNCIA"])
                    calc_pres = ((tot_aulas_reg - faltas_hero) / tot_aulas_reg) * 100
                    perc_presenca_hero_str = f"{calc_pres:.0f}%"
                    delta_faltas_str = f"{faltas_hero} falta(s)"

                    df_vistos_calc = df_d_validas[df_d_validas.get('VISTO_ATIVIDADE', '').astype(str).str.upper() != "ISENTO"]
                    tot_vistos_poss = len(df_vistos_calc)
                    ok_vistos_cnt = len(df_vistos_calc[df_vistos_calc.get('VISTO_ATIVIDADE', '').astype(str).str.upper() == "TRUE"])
                    calc_vistos = (ok_vistos_cnt / tot_vistos_poss) * 100 if tot_vistos_poss > 0 else 0
                    perc_visto_hero_str = f"{calc_vistos:.0f}%"
                    
                    b_somado = df_d_periodo.get('BONUS', pd.Series()).apply(util.sosa_to_float).sum()
                    bonus_total_hero_str = f"{b_somado:+.1f} pts bônus"
                else:
                    perc_presenca_hero_str = "—"
                    delta_faltas_str = "A Cursar"
                    perc_visto_hero_str = "—"
                    bonus_total_hero_str = "Sem aulas no período"

        rotulo_assiduidade = f"Assiduidade ({trim_b})" if trim_b != "Todos" else "Assiduidade Anual"
        rotulo_vistos = f"Vistos de Caderno ({trim_b})" if trim_b != "Todos" else "Vistos de Caderno (Geral)"
        regra_arred_texto = "A Média Regimental da Prefeitura de Itabuna utiliza o arredondamento para o meio ponto (0,5 em 0,5) mais próximo. A Recuperação aplica a média aritmética: (Média do Trimestre + Recuperação) ÷ 2."

        # BENTO CARD DE TOPO DINÂMICO
        with st.container(border=True):
            c_h1, c_h2, c_h3, c_h4 = st.columns([1.8, 1.4, 1, 1])
            
            with c_h1:
                st.markdown(f"### {aluno_b_label}")
                st.caption(f"**ID:** {id_alu} | **Turma:** {turma_b} | **Status:** `{status_atual_aluno}`")
                
                if "PENDENTE" in perfil_atual or "SUSPEITA" in perfil_atual: st.caption(f"Perfil: Radar Clínico ({perfil_atual})")
                elif "DEFASAGEM" in perfil_atual: st.caption(f"Perfil: Defasagem Pedagógica ({perfil_atual})")
                elif "ALTA PERFORMANCE" in perfil_atual: st.caption(f"Perfil: Destaque Cognitivo ({perfil_atual})")
                elif is_pei_or_gap: st.caption(f"Perfil: Acessibilidade PEI ({perfil_atual})")
                else: st.caption("Perfil: Regular / Típico")
                
            with c_h2:
                if soma_1_2_preditiva >= 18.0:
                    st.metric("Soma (I + II)", f"{soma_1_2_preditiva:.1f} pts", "Aprovado Antecipado", help=regra_arred_texto)
                else:
                    st.metric("Soma (I + II)", f"{soma_1_2_preditiva:.1f} pts", f"Meta III Tri: {meta_iii_arred:.1f} pts", help=regra_arred_texto)
                st.caption(f"Projeção: **{status_preditivo_aluno}**")

            c_h3.metric(rotulo_assiduidade, perc_presenca_hero_str, delta_faltas_str, delta_color="inverse" if faltas_hero > 0 else "normal")
            c_h4.metric(rotulo_vistos, perc_visto_hero_str, bonus_total_hero_str)

        c_act_b1, c_act_b2, c_act_b3 = st.columns(3)
        
        if c_act_b1.button("Extrato para WhatsApp", use_container_width=True, key=f"btn_zap_bio_{v}"):
            dialog_whatsapp(nome_limpo, turma_b, status_atual_aluno, soma_1_2_preditiva, meta_iii_arred, status_preditivo_aluno, perc_presenca_hero_str, faltas_hero, perc_visto_hero_str, bonus_total_hero_str, regra_arred_texto)

        if c_act_b2.button("Ficha de Rendimento Escolar (DOCX)", use_container_width=True, key=f"btn_docx_bio_{v}"):
            with st.spinner("Compilando Ficha de Rendimento Escolar em Word..."):
                dados_ficha = [{
                    "nome": nome_limpo,
                    "c1": perc_visto_hero_str,
                    "c2": "Sincronizado",
                    "c3": "Sincronizado",
                    "bonus": bonus_total_hero_str,
                    "media": f"Soma I+II: {soma_1_2_preditiva:.1f} (Meta III: {meta_iii_arred:.1f})",
                    "status": f"{status_preditivo_aluno} • Assiduidade: {perc_presenca_hero_str} ({delta_faltas_str})"
                }]
                info_ficha = {"turma": turma_b, "trimestre": trim_b}
                nome_arq_ficha = f"FICHA_RENDIMENTO_{nome_limpo.replace(' ','_')}_{turma_b}"
                
                doc_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_ficha, dados_ficha, info_ficha)
                link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_ficha, trimestre=trim_b, categoria=turma_b, modo="PLANEJAMENTO")
                
                if "https" in link_doc:
                    st.success("Ficha de Rendimento gerada com sucesso!")
                    st.link_button("Abrir Ficha no Google Drive", link_doc, type="primary", use_container_width=True)
                    st.balloons()

        if c_act_b3.button("Certidão Oficial de Produção (DOCX)", type="primary", use_container_width=True, key=f"btn_certidao_transf_{v}"):
            with st.spinner("Compilando Certidão Oficial de Produção em Word..."):
                lista_notas_certidao = []
                for n_t in notas_consolidadas_trimestres:
                    lista_notas_certidao.append({
                        "periodo": n_t["periodo"],
                        "c1": n_t["c1"],
                        "c2": n_t["c2"],
                        "c3": n_t["c3"],
                        "rec": n_t["rec"],
                        "media": n_t["media_final"]
                    })

                dados_aluno_certidao = {
                    "nome": nome_limpo, "id": id_alu, "turma": turma_b,
                    "status": status_atual_aluno, "perfil": perfil_atual,
                    "assiduidade": perc_presenca_hero_str, "faltas": faltas_hero,
                    "vistos_perc": perc_visto_hero_str, "bonus": bonus_total_hero_str,
                    "parecer": f"Certificamos que o(a) estudante esteve vinculado(a) à turma {turma_b} sob regência do Prof. Ronaldo Gomes. Registrou-se uma soma acumulada de {soma_1_2_preditiva:.1f} pontos nos dois primeiros trimestres (Projeção para o III Trimestre: {meta_iii_arred:.1f} pts para atingir a meta anual de 18.0 pontos)."
                }
                
                info_escola_certidao = {"ano": turma_b, "trimestre": "Conselho/Regência"}
                nome_arq_certidao = f"CERTIDAO_PRODUCAO_{nome_limpo.replace(' ','_')}_{turma_b}"
                
                doc_cert_stream = exporter.gerar_docx_certidao_producao(nome_arq_certidao, dados_aluno_certidao, lista_notas_certidao, info_escola_certidao)
                link_cert_doc = db.subir_e_converter_para_google_docs(doc_cert_stream, nome_arq_certidao, trimestre="Conselho", categoria=turma_b, modo="PLANEJAMENTO")
                
                if "https" in link_cert_doc:
                    st.success("Certidão Oficial de Produção gerada no Drive com sucesso!")
                    st.link_button("Abrir Certidão Oficial no Drive", link_cert_doc, type="primary", use_container_width=True)
                    st.balloons()

        st.markdown("---")

        abas_bio = [
            "Boletim Analítico & Metas",
            "Avaliações Escaneadas & Lacunas",
            "Vida Escolar, Atitude & PEI"
        ]
        
        tabs = st.tabs(abas_bio)

        # ABA 1: BOLETIM ANALÍTICO & METAS PREDITIVAS
        with tabs[0]:
            st.markdown("#### Extrato Analítico de Rendimento")
            st.caption("Sincronização dinâmica com a tabela oficial consolidada (DB_NOTAS) e arredondamento 0,5.")

            dados_tabela_boletim = []
            for n_c in notas_consolidadas_trimestres:
                if trim_b != "Todos" and n_c["periodo"] != trim_b:
                    continue

                dados_tabela_boletim.append({
                    "Período": n_c["periodo"],
                    "Caderno (C1)": n_c["c1"],
                    "Testes (C2)": n_c["c2"],
                    "Prova (C3)": n_c["c3"],
                    "Bônus": n_c["bonus"],
                    "Soma": n_c["soma_bruta"],
                    "Média Pré-Rec": n_c["media_inicial"],
                    "REC": n_c["rec"],
                    "Média Final": n_c["media_final"],
                    "Situação": n_c["situacao"]
                })

            if dados_tabela_boletim:
                def style_status_bio_tabela(val):
                    if "Na Média" in str(val): return 'color: #2ECC71; font-weight: bold;'
                    if "Refacção" in str(val): return 'color: #F1C40F; font-weight: bold;'
                    if "Recomposição" in str(val): return 'color: #E74C3C; font-weight: bold;'
                    return 'color: #94A3B8;'

                st.dataframe(
                    pd.DataFrame(dados_tabela_boletim).style.map(style_status_bio_tabela, subset=['Situação']),
                    hide_index=True, use_container_width=True,
                    column_config={
                        "Período": st.column_config.TextColumn("Período", width="medium"),
                        "Caderno (C1)": st.column_config.TextColumn("C1", width="small"),
                        "Testes (C2)": st.column_config.TextColumn("C2", width="small"),
                        "Prova (C3)": st.column_config.TextColumn("C3", width="small"),
                        "Bônus": st.column_config.TextColumn("Bônus", width="small"),
                        "Soma": st.column_config.TextColumn("Soma", width="small"),
                        "Média Pré-Rec": st.column_config.TextColumn("Média Pré-Rec", width="small"),
                        "REC": st.column_config.TextColumn("REC", width="small"),
                        "Média Final": st.column_config.TextColumn("Média Final", width="small"),
                        "Situação": st.column_config.TextColumn("Situação", width="medium")
                    }
                )
            else:
                st.info("Nenhuma nota cadastrada para o período selecionado.")

            st.markdown("---")
            with st.container(border=True):
                st.markdown("##### Simulação Preditiva para o III Trimestre")
                c_s_al1, c_s_al2 = st.columns([1.5, 2])
                
                c_s_al1.metric("Soma Acumulada (I + II)", f"{soma_1_2_preditiva:.1f} / 18.0 pts")
                
                if soma_1_2_preditiva >= 18.0:
                    c_s_al2.success("O estudante atingiu a pontuação regimental anual necessária para aprovação direta!")
                else:
                    c_s_al2.info(f"Meta no III Trimestre: O estudante necessita de **{meta_iii_arred:.1f} pontos** no III Trimestre para aprovação sem recuperação final.")

        # ABA 2: AVALIAÇÕES ESCANEADAS & MAPA DE LACUNAS
        with tabs[1]:
            st.markdown("#### Histórico de Avaliações Escaneadas")
            
            df_dg_aluno_tab = df_diagnosticos[(df_diagnosticos['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diagnosticos['TURMA'] == turma_b)].copy() if not df_diagnosticos.empty else pd.DataFrame()
            
            if df_dg_aluno_tab.empty:
                st.info("Nenhuma avaliação escaneada para este estudante.")
            else:
                c_trib_btn, _ = st.columns([1.5, 2])
                if c_trib_btn.button("Tribunal de Recursos & Perícia", type="primary", use_container_width=True, key=f"btn_trib_open_{v}"):
                    dialog_tribunal(id_alu, nome_limpo, is_pei_or_gap, df_dg_aluno_tab, turma_b, trim_b)

                st.markdown("<br>", unsafe_allow_html=True)
                
                dados_provas_view = []
                for _, r_av in df_dg_aluno_tab.iloc[::-1].iterrows():
                    av_id_bruto = str(r_av.get('ID_AVALIACAO', ''))
                    nota_av = util.sosa_to_float(r_av.get('NOTA_CALCULADA', 0.0))
                    resp_al = str(r_av.get('RESPOSTAS_ALUNO', ''))
                    link_ft = str(r_av.get('LINK_FOTO_DRIVE', ''))
                    dt_av = str(r_av.get('DATA', 'N/A'))

                    if resp_al.startswith("FALTOU_JUSTIFICADO"): status_av = "Justificado (Atestado)"
                    elif resp_al.startswith("FALTOU_INJUSTIFICADO") or resp_al == "FALTOU": status_av = "Ausência"
                    elif resp_al.startswith("QUALITATIVA"): status_av = "PEI Nível 3 (Qualitativa)"
                    elif resp_al.startswith("DISCURSIVA"): status_av = "Discursiva"
                    else: status_av = "Corrigida"

                    dados_provas_view.append({
                        "Data": dt_av,
                        "Avaliação": av_id_bruto,
                        "Nota": nota_av,
                        "Situação": status_av,
                        "Evidência": link_ft if "http" in link_ft else None
                    })

                st.dataframe(
                    pd.DataFrame(dados_provas_view), hide_index=True, use_container_width=True,
                    column_config={
                        "Data": st.column_config.TextColumn("Data", width="small"),
                        "Avaliação": st.column_config.TextColumn("Instrumento", width="large"),
                        "Nota": st.column_config.NumberColumn("Nota", format="%.1f", width="small"),
                        "Situação": st.column_config.TextColumn("Status", width="medium"),
                        "Evidência": st.column_config.LinkColumn("Imagem", width="small")
                    }
                )

                st.markdown("---")
                st.markdown("##### Mapa de Lacunas & Descritores com Erro")
                
                lacunas_detectadas = []
                for _, r_av in df_dg_aluno_tab.iterrows():
                    nome_av_limpo = str(r_av.get('ID_AVALIACAO', '')).replace(" (2ª CHAMADA)", "").split('(')[0].split('-')[0].strip()
                    m_ref = df_aulas[df_aulas['TIPO_MATERIAL'].str.contains(nome_av_limpo, case=False, na=False)] if not df_aulas.empty else pd.DataFrame()
                    
                    if not m_ref.empty:
                        txt_p = str(m_ref.iloc[0].get('CONTEUDO', ''))
                        grade_txt = ai.extrair_tag(txt_p, "GRADE_DE_CORRECAO_PEI" if is_pei_or_gap else "GRADE_DE_CORRECAO") or ai.extrair_tag(txt_p, "GRADE_DE_CORRECAO")
                        gab_txt = ai.extrair_tag(txt_p, "GABARITO_PEI" if is_pei_or_gap else "GABARITO_TEXTO") or ai.extrair_tag(txt_p, "GABARITO")
                        gab_oficial = re.findall(r"\b[A-E]\b", gab_txt.upper())
                        
                        respostas_aluno_list = str(r_av.get('RESPOSTAS_ALUNO', '')).split(';')
                        for i_q, r_letra in enumerate(respostas_aluno_list):
                            r_clean = r_letra.replace("*", "").strip().upper()
                            if i_q < len(gab_oficial) and r_clean != gab_oficial[i_q] and r_clean not in ["?", "X", "FALTOU", ""]:
                                q_num = i_q + 1
                                padrao_h = rf"(?si)QUEST[AÃ]O\s*(?:PEI\s*)?0?{q_num}\b.*?(?:[:\-])\s*(.*?)(?=\.?\s*(?:JUSTIFICATIVA|PERÍCIA|ANÁLISE|DISTRATORES|$))"
                                m_h = re.search(padrao_h, grade_txt)
                                desc_item = m_h.group(1).strip() if m_h else "Habilidade matemática do item."
                                desc_item_limpo = re.sub(r'[*#\[\]]', '', desc_item).strip()
                                lacunas_detectadas.append(f"• **{nome_av_limpo} (Q{q_num:02d}):** {desc_item_limpo}")

                if lacunas_detectadas:
                    with st.container(border=True):
                        for lac in list(dict.fromkeys(lacunas_detectadas))[:8]:
                            st.info(util.preparar_para_leitura(lac))
                else:
                    st.success("Excelente domínio conceitual. Nenhuma lacuna crítica registrada.")

        # ABA 3: VIDA ESCOLAR, ATITUDE & PEI
        with tabs[2]:
            st.markdown("#### Registro de Atitude & Vida Escolar")
            
            df_d_aluno_timeline = df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_alu) & (df_diario['TURMA'] == turma_b)].copy() if not df_diario.empty else pd.DataFrame()
            
            if df_d_aluno_timeline.empty:
                st.info("Nenhum registro atitudinal no Diário de Bordo.")
            else:
                df_d_timeline_val = df_d_aluno_timeline[~df_d_aluno_timeline['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])].copy()
                
                if not df_d_timeline_val.empty:
                    for _, r_t in df_d_timeline_val.iloc[::-1].head(10).iterrows():
                        dt_t = str(r_t.get('DATA', 'N/A'))
                        tag_t = str(r_t.get('TAGS', ''))
                        obs_t = str(r_t.get('OBSERVACOES', ''))
                        bonus_t = util.sosa_to_float(r_t.get('BONUS', 0))
                        visto_t = str(r_t.get('VISTO_ATIVIDADE', '')).upper()

                        with st.container(border=True):
                            c_t1, c_t2 = st.columns([3, 1])
                            
                            if tag_t == "AUSÊNCIA":
                                c_t1.error(f"**{dt_t}** — Ausência na aula")
                            elif bonus_t > 0 or "ARGUIÇÃO" in tag_t:
                                c_t1.success(f"**{dt_t}** — {tag_t} ({obs_t})")
                                c_t2.markdown(f"**+{bonus_t:.1f} pts**")
                            elif bonus_t < 0:
                                c_t1.warning(f"**{dt_t}** — {tag_t} ({obs_t})")
                                c_t2.markdown(f"**{bonus_t:.1f} pts**")
                            else:
                                c_t1.info(f"**{dt_t}** — Visto no Caderno ({'Visto OK' if visto_t == 'TRUE' else 'Sem Visto'})")

            if is_pei_or_gap:
                st.markdown("---")
                st.markdown("#### Dossiê Clínico & Diretrizes de Acessibilidade (PEI)")
                
                hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_alu] if not df_relatorios.empty else pd.DataFrame()
                tipo_dossie_key = f"DOSSIE_PEI_{trim_b.replace(' ', '_').upper()}"
                rel_master = hist_aluno[hist_aluno['TIPO'] == tipo_dossie_key] if not hist_aluno.empty else pd.DataFrame()
                
                if not rel_master.empty:
                    master_text = str(rel_master.iloc[-1]['CONTEUDO'])
                    v_diag = ai.extrair_tag(master_text, "DIAGNOSTICO_GERAL")
                    v_dir = ai.extrair_tag(master_text, "DIRETRIZES_CURRICULARES")
                    
                    with st.container(border=True):
                        st.markdown("**Diagnóstico e Acompanhamento:**")
                        st.info(v_diag if v_diag else "Parecer pedagógico arquivado.")
                        st.markdown("**Diretrizes e Adaptações Recomendadas:**")
                        st.warning(v_dir if v_dir else "Recomendações ativas.")
                else:
                    st.info(f"Nenhum Dossiê PEI específico arquivado para o {trim_b}.")

        st.caption(f"Dossiê individual auditado e sincronizado em: {datetime.now().strftime('%d/%m/%Y às %H:%M')}")










# ==============================================================================
# MÓDULO: PAINEL DE NOTAS & VISTOS - V2026.PRO_INFINITY_SOBERANIA_TOTAL
# (CONSOLIDAÇÃO C1/C2/C3, MÉDIA NORMAL, PROVA REC, MÉDIA PÓS-REC E MÉDIA FINAL)
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.title("Painel de Notas & Vistos")
    st.caption("Central de consolidação de rendimento: sincronização do Scanner CIR, gestão atitudinal de vistos de caderno, refacção solidária e recuperação regimental.")
    st.markdown("---")

    with st.expander("🛠️ Central de Saneamento & Auto-Healer do Banco de Dados", expanded=False):
        st.caption("Executa o recálculo psicométrico em lote, converte datas seriais, dedupica o diário e aplica o arredondamento oficial de 0,5 em 0,5 no banco:")
        
        if st.button("Executar Saneamento Soberano de Todas as Tabelas (1-Clique)", type="primary", use_container_width=True, key="btn_run_auto_healer_main"):
            with st.status("Executando protocolo de saneamento em todas as planilhas...", expanded=True) as status_heal:
                status_heal.write("Conectando à base de dados e auditando registros...")
                sucesso_heal, msg_heal = db.executar_saneamento_banco_soberano()
                
                if sucesso_heal:
                    status_heal.update(label="Saneamento concluído com sucesso!", state="complete")
                    st.success(f"**Relatório de Saneamento:**\n\n{msg_heal}")
                    st.balloons()
                    time.sleep(1.0)
                    st.rerun()
                else:
                    status_heal.update(label="Erro no saneamento.", state="error")
                    st.error(msg_heal)

    if "v_notas" not in st.session_state:
        st.session_state.v_notas = int(time.time())
    v = st.session_state.v_notas

    lista_turmas_notas = []
    if not df_turmas.empty and 'ID_TURMA' in df_turmas.columns:
        turmas_reais_n = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])]
        lista_turmas_notas = sorted(turmas_reais_n['ID_TURMA'].unique())
    elif not df_alunos.empty and 'TURMA' in df_alunos.columns:
        lista_turmas_notas = sorted(df_alunos['TURMA'].unique())

    if not lista_turmas_notas:
        st.warning("Nenhuma turma cadastrada. Cadastre as turmas no cockpit de Gestão da Turma.")
    else:
        # Detecção de Trimestre com tolerância estendida para o II Tri até 11/09/2026
        hoje_dt = date.today()
        if hoje_dt <= date(2026, 5, 22): trim_detectado_n = "I Trimestre"
        elif hoje_dt <= date(2026, 9, 11): trim_detectado_n = "II Trimestre"
        else: trim_detectado_n = "III Trimestre"

        if "trim_notas_ativo" not in st.session_state:
            st.session_state.trim_notas_ativo = trim_detectado_n

        with st.container(border=True):
            c_n1, c_n2 = st.columns([1.5, 2])
            turma_notas = c_n1.selectbox("Turma Selecionada:", lista_turmas_notas, key=f"sel_t_notas_{v}")
            
            idx_trim_default = ["I Trimestre", "II Trimestre", "III Trimestre"].index(st.session_state.trim_notas_ativo) if st.session_state.trim_notas_ativo in ["I Trimestre", "II Trimestre", "III Trimestre"] else 1

            trim_ativo_notas = c_n2.segmented_control(
                "Trimestre Ativo:",
                ["I Trimestre", "II Trimestre", "III Trimestre"],
                default=["I Trimestre", "II Trimestre", "III Trimestre"][idx_trim_default],
                key=f"seg_trim_notas_{v}"
            )
            if not trim_ativo_notas: 
                trim_ativo_notas = st.session_state.trim_notas_ativo
            else:
                st.session_state.trim_notas_ativo = trim_ativo_notas

        df_alunos_base_n = df_alunos[df_alunos['TURMA'] == turma_notas].copy() if not df_alunos.empty else pd.DataFrame()
        if 'STATUS' not in df_alunos_base_n.columns: df_alunos_base_n['STATUS'] = "ATIVO"
        alunos_notas_df = df_alunos_base_n[~df_alunos_base_n['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")

        if alunos_notas_df.empty:
            st.info(f"Nenhum estudante ativo cadastrado na turma {turma_notas}.")
        else:
            @st.fragment
            def renderizar_painel_notas_fragmento():
                import math
                def arredondar_05_escolar(valor):
                    return min(10.0, math.floor(valor * 2.0 + 0.5) / 2.0)

                data_corte_salva = None
                if hasattr(db, 'obter_config_corte_trimestre'):
                    data_corte_salva = db.obter_config_corte_trimestre(turma_notas, trim_ativo_notas)
                
                if trim_ativo_notas == "I Trimestre":
                    dt_i_default, dt_f_default = date(2026, 2, 9), date(2026, 5, 22)
                elif trim_ativo_notas == "II Trimestre":
                    dt_i_default, dt_f_default = date(2026, 5, 25), date(2026, 9, 11)
                else:
                    dt_i_default, dt_f_default = date(2026, 9, 12), date(2026, 12, 17)

                if data_corte_salva:
                    try:
                        dt_f_default = datetime.strptime(data_corte_salva, "%d/%m/%Y").date()
                    except: pass

                dt_i_n, dt_f_n = dt_i_default, dt_f_default
                padrao_trim_regex = util.obter_regex_trimestre(trim_ativo_notas)

                df_notas_trim = df_notas[(df_notas['TURMA'] == turma_notas) & (df_notas['TRIMESTRE'] == trim_ativo_notas)] if not df_notas.empty else pd.DataFrame()
                df_diario_trim = df_diario[(df_diario['TURMA'] == turma_notas)] if not df_diario.empty else pd.DataFrame()

                mapa_live_teste = {}
                mapa_live_prova = {}
                mapa_live_rec = {}

                if not df_diagnosticos.empty and 'TURMA' in df_diagnosticos.columns and 'ID_AVALIACAO' in df_diagnosticos.columns:
                    mask_diag_t = (df_diagnosticos['TURMA'] == turma_notas) & (
                        df_diagnosticos['ID_AVALIACAO'].astype(str).str.contains(padrao_trim_regex, regex=True, case=False, na=False)
                    )
                    df_diag_filtrado = df_diagnosticos[mask_diag_t].copy()

                    for _, r_dg in df_diag_filtrado.iterrows():
                        id_al_dg = db.limpar_id(r_dg.get('ID_ALUNO', ''))
                        id_av_str = str(r_dg.get('ID_AVALIACAO', '')).upper()
                        resp_al_str = str(r_dg.get('RESPOSTAS_ALUNO', '')).upper()
                        
                        if resp_al_str.startswith("FALTOU_INJUSTIFICADO") or resp_al_str == "FALTOU":
                            nota_dg = 0.0
                        else:
                            nota_dg = util.sosa_to_float(r_dg.get('NOTA_CALCULADA', 0.0))

                        if any(x in id_av_str for x in ["RECUPERAÇÃO", "RECUPERACAO", "REC_"]):
                            mapa_live_rec[id_al_dg] = nota_dg
                        elif any(x in id_av_str for x in ["TESTE", "SIMULADO", "TRABALHO"]):
                            if "SONDA" not in id_av_str:
                                mapa_live_teste[id_al_dg] = max(mapa_live_teste.get(id_al_dg, 0.0), nota_dg)
                        elif any(x in id_av_str for x in ["PROVA", "AVALIAÇÃO", "AVALIACAO", "EXAME", "AVALIACAO_"]):
                            mapa_live_prova[id_al_dg] = max(mapa_live_prova.get(id_al_dg, 0.0), nota_dg)

                vistos_live_dict = {}
                bonus_live_dict = {}

                if not df_diario_trim.empty and 'ID_ALUNO' in df_diario_trim.columns and 'DATA' in df_diario_trim.columns:
                    df_d_range = df_diario_trim.copy()
                    df_d_range['DATA_DT'] = pd.to_datetime(df_d_range['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                    df_d_sub = df_d_range[(df_d_range['DATA_DT'] >= dt_i_n) & (df_d_range['DATA_DT'] <= dt_f_n)]

                    if not df_d_sub.empty:
                        d_validas = df_d_sub[df_d_sub.get('VISTO_ATIVIDADE', '').astype(str).str.upper() != "ISENTO"]
                        tot_v_d = len(d_validas['DATA'].unique()) if not d_validas.empty else 1
                        if tot_v_d == 0: tot_v_d = 1

                        for id_al_raw, grp in df_d_sub.groupby('ID_ALUNO'):
                            id_c = db.limpar_id(id_al_raw)
                            grp_val = grp[grp.get('VISTO_ATIVIDADE', '').astype(str).str.upper() != "ISENTO"]
                            ok_v = len(grp_val[grp_val.get('VISTO_ATIVIDADE', '').astype(str).str.upper() == "TRUE"])
                            vistos_live_dict[id_c] = round((ok_v / tot_v_d * 3.0), 2) if tot_v_d > 0 else 0.0
                            
                            if 'BONUS' in grp.columns:
                                bonus_live_dict[id_c] = grp['BONUS'].apply(util.sosa_to_float).sum()
                            else:
                                bonus_live_dict[id_c] = 0.0

                dados_grid_notas = []
                convocados_recuperacao = []
                alunos_liberados_refaccao = []
                
                for _, al_n in alunos_notas_df.iterrows():
                    id_al_n = db.limpar_id(al_n.get('ID', ''))
                    nome_al_n = str(al_n.get('NOME_ALUNO', 'Estudante'))
                    nec_al_n = str(al_n.get('NECESSIDADES', 'TÍPICO'))

                    reg_n = df_notas_trim[df_notas_trim['ID_ALUNO'].apply(db.limpar_id) == id_al_n] if not df_notas_trim.empty else pd.DataFrame()
                    
                    v_c1_banco = util.sosa_to_float(reg_n.iloc[0].get('NOTA_VISTOS', 0.0)) if not reg_n.empty else 0.0
                    v_c2_banco = util.sosa_to_float(reg_n.iloc[0].get('NOTA_TESTE', 0.0)) if not reg_n.empty else 0.0
                    v_c3_banco = util.sosa_to_float(reg_n.iloc[0].get('NOTA_PROVA', 0.0)) if not reg_n.empty else 0.0
                    v_rec_banco = util.sosa_to_float(reg_n.iloc[0].get('NOTA_REC', -1.0)) if not reg_n.empty else -1.0
                    v_media_banco = util.sosa_to_float(reg_n.iloc[0].get('MEDIA_FINAL', 0.0)) if not reg_n.empty else 0.0

                    v_c1_live = vistos_live_dict.get(id_al_n, 0.0)
                    v_c2_live = mapa_live_teste.get(id_al_n, 0.0)
                    v_c3_live = mapa_live_prova.get(id_al_n, 0.0)
                    v_rec_live = mapa_live_rec.get(id_al_n, -1.0)
                    bonus_diario_calc = bonus_live_dict.get(id_al_n, 0.0)

                    c1_val = max(v_c1_banco, v_c1_live)
                    c2_val = max(v_c2_banco, v_c2_live)
                    c3_val = max(v_c3_banco, v_c3_live)
                    rec_val = max(v_rec_banco, v_rec_live)

                    c1_final = min(3.0, c1_val + max(0.0, bonus_diario_calc))
                    rem_bonus = max(0.0, bonus_diario_calc) - (c1_final - c1_val)
                    c2_final = min(3.0, c2_val + max(0.0, rem_bonus))
                    rem_bonus -= (c2_final - c2_val)
                    c3_final = min(4.0, c3_val + max(0.0, rem_bonus))

                    # 1. MÉDIA NORMAL (Antes da Recuperação: C1 + C2 + C3)
                    soma_sem_rec = c1_final + c2_final + c3_final
                    media_normal = arredondar_05_escolar(soma_sem_rec)

                    # 2. MÉDIA PÓS-REC (Fórmula Oficial: (Média Normal + REC) / 2)
                    tem_rec = (rec_val > 0)
                    if tem_rec:
                        media_com_rec = (media_normal + rec_val) / 2.0
                        media_pos_rec = arredondar_05_escolar(media_com_rec)
                        media_calculada = max(media_normal, media_pos_rec)
                    else:
                        media_pos_rec = 0.0
                        media_calculada = media_normal

                    # 3. MÉDIA FINAL (Maior nota soberana com proteção não-regressiva)
                    media_final_apresentada = max(media_calculada, v_media_banco)

                    is_aprovado_com_rec = (tem_rec and media_final_apresentada >= 6.0 and media_normal < 6.0)
                    is_isento_refaccao = (soma_sem_rec < 6.0 and media_final_apresentada >= 6.0 and not is_aprovado_com_rec)

                    if media_final_apresentada >= 6.0:
                        if is_aprovado_com_rec: sit_txt = "Aprovado com REC"
                        elif is_isento_refaccao: sit_txt = "Aprovado (Refacção)"
                        else: sit_txt = "Aprovado no Trimestre"
                        alunos_liberados_refaccao.append(nome_al_n)
                    elif tem_rec:
                        sit_txt = "Não Atingiu a Média (Pós-REC)"
                    elif media_final_apresentada == 5.5:
                        sit_txt = "Oportunidade de Refacção (+0.5)"
                    else:
                        sit_txt = "Convocado para Recuperação"
                        nota_necessaria_rec = max(0.0, 12.0 - media_final_apresentada)
                        convocados_recuperacao.append({
                            "ID": id_al_n, "Estudante": nome_al_n, "Perfil": nec_al_n,
                            "Média Atual": media_final_apresentada, "Meta na Prova": nota_necessaria_rec
                        })

                    dados_grid_notas.append({
                        "ID": id_al_n,
                        "Estudante": nome_al_n,
                        "Caderno (C1)": c1_val,
                        "Testes (C2)": c2_val,
                        "Prova (C3)": c3_val,
                        "Bônus / Mérito": bonus_diario_calc,
                        "Média Normal": media_normal,
                        "Recuperação": rec_val if rec_val > 0 else 0.0,
                        "Média pós-REC": media_pos_rec if tem_rec else 0.0,
                        "Média Final": media_final_apresentada,
                        "Situação Regimental": sit_txt
                    })

                df_grid_ed_notas = pd.DataFrame(dados_grid_notas)

                # SOSA V2026 - INCLUSÃO DA VISÃO ESPELHO PONTO ID (PREFEITURA DE ITABUNA)
                visao_selecionada = st.segmented_control(
                    "Selecione a Visão:",
                    ["Consolidador de Notas", "🏛️ Digitação Ponto ID (Prefeitura)", "Vistos de Caderno & Atitude", "Recuperação & Refacção"],
                    default="Consolidador de Notas",
                    key=f"seg_visao_notas_{v}"
                )
                st.markdown("<br>", unsafe_allow_html=True)

                # ==============================================================
                # VISÃO: ESPELHO PONTO ID (TABELA LIMPA 1:1 - ZERO RECUPERAÇÃO)
                # Contempla estritamente: 1ª AV + 2ª AV + 3ª AV = Média Normal (com bônus)
                # A RECUPERAÇÃO FICA 100% DE FORA (será lançada pelo Boletim na outra tela)
                # ==============================================================
                if visao_selecionada == "🏛️ Digitação Ponto ID (Prefeitura)":
                    with st.container(border=True):
                        c_ponto_h1, c_ponto_h2 = st.columns([3, 1])
                        c_ponto_h1.markdown(f"#### 🏛️ Tabela de Digitação — Ponto ID ({turma_notas} • {trim_ativo_notas})")
                        c_ponto_h1.caption(
                            "Espelho da tela 'Avaliação ➔ Notas' da Prefeitura. "
                            "Notas regulares com bônus diários e de refacção absorvidos nos limites de 3.0, 3.0 e 4.0. "
                            "A RECUPERAÇÃO ESTÁ 100% FORA DESTA TABELA."
                        )

                    def balancear_avaliacoes_normais_ponto_id(c1_base, c2_base, c3_base, bonus_total, media_normal_alvo):
                        """
                        Distribui os bônus diários e refacções estritamente dentro da Média Normal do Trimestre.
                        Garante que: 1ª AV + 2ª AV + 3ª AV == media_normal_alvo (ZERO recuperação aqui).
                        """
                        # 1. Absorve bônus nos tetos regimentais
                        av1 = min(3.0, c1_base + max(0.0, bonus_total))
                        rem_b = max(0.0, bonus_total) - (av1 - c1_base)
                        av2 = min(3.0, c2_base + max(0.0, rem_b))
                        rem_b -= (av2 - c2_base)
                        av3 = min(4.0, c3_base + max(0.0, rem_b))

                        alvo = min(10.0, max(0.0, round(media_normal_alvo, 1)))
                        
                        # 2. Ajuste fino para cravar exatamente a Média Normal
                        dif = round(alvo - (av1 + av2 + av3), 1)

                        if dif > 0:
                            espaco_1 = round(3.0 - av1, 1)
                            add_1 = min(dif, espaco_1)
                            av1 = round(av1 + add_1, 1)
                            dif = round(dif - add_1, 1)

                            if dif > 0:
                                espaco_2 = round(3.0 - av2, 1)
                                add_2 = min(dif, espaco_2)
                                av2 = round(av2 + add_2, 1)
                                dif = round(dif - add_2, 1)

                            if dif > 0:
                                espaco_3 = round(4.0 - av3, 1)
                                add_3 = min(dif, espaco_3)
                                av3 = round(av3 + add_3, 1)
                                dif = round(dif - add_3, 1)

                        elif dif < 0:
                            sobra = abs(dif)
                            ded_1 = min(sobra, av1)
                            av1 = round(av1 - ded_1, 1)
                            sobra = round(sobra - ded_1, 1)

                            if sobra > 0:
                                ded_2 = min(sobra, av2)
                                av2 = round(av2 - ded_2, 1)
                                sobra = round(sobra - ded_2, 1)

                            if sobra > 0:
                                ded_3 = min(sobra, av3)
                                av3 = round(av3 - ded_3, 1)
                                sobra = round(sobra - ded_3, 1)

                        return av1, av2, av3, alvo

                    dados_ponto_id_limpo = []
                    for idx_num, (_, r_ed) in enumerate(df_grid_ed_notas.iterrows(), start=1):
                        c1_b = util.sosa_to_float(r_ed.get('Caderno (C1)', 0.0))
                        c2_b = util.sosa_to_float(r_ed.get('Testes (C2)', 0.0))
                        c3_b = util.sosa_to_float(r_ed.get('Prova (C3)', 0.0))
                        b_total = util.sosa_to_float(r_ed.get('Bônus / Mérito', 0.0))
                        
                        # ALVO ESTRITO: Média Normal do Trimestre (Sem nenhuma influência de REC!)
                        media_normal_estudante = util.sosa_to_float(r_ed.get('Média Normal', 0.0))

                        av1_final, av2_final, av3_final, media_soma = balancear_avaliacoes_normais_ponto_id(
                            c1_b, c2_b, c3_b, b_total, media_normal_estudante
                        )

                        dados_ponto_id_limpo.append({
                            "Nº": idx_num,
                            "Alunos": r_ed.get('Estudante', 'Estudante'),
                            "1ª AV - Valor: 3,0": f"{av1_final:.1f}".replace(".", ","),
                            "2ª AV - Valor: 3,0": f"{av2_final:.1f}".replace(".", ","),
                            "3ª AV - Valor: 4,0": f"{av3_final:.1f}".replace(".", ","),
                            "Média": f"{media_soma:.1f}".replace(".", ",")
                        })

                    df_ponto_id_display = pd.DataFrame(dados_ponto_id_limpo)

                    st.dataframe(
                        df_ponto_id_display,
                        hide_index=True,
                        use_container_width=True,
                        height=540,
                        column_config={
                            "Nº": st.column_config.NumberColumn("Nº", width="small"),
                            "Alunos": st.column_config.TextColumn("Alunos", width="medium"),
                            "1ª AV - Valor: 3,0": st.column_config.TextColumn("1ª AV - Valor: 3,0", width="small"),
                            "2ª AV - Valor: 3,0": st.column_config.TextColumn("2ª AV - Valor: 3,0", width="small"),
                            "3ª AV - Valor: 4,0": st.column_config.TextColumn("3ª AV - Valor: 4,0", width="small"),
                            "Média": st.column_config.TextColumn("Média", width="small", help="Soma exata das 3 avaliações normais")
                        }
                    )

                    st.caption("✅ Verificação: 1ª AV + 2ª AV + 3ª AV somam exatamente a Média Normal do período com bônus. A recuperação está 100% fora.")

                # ==============================================================
                # VISÃO 1: CONSOLIDADOR DE NOTAS (DETALHADO COM RECUPERAÇÃO)
                # ==============================================================
                elif visao_selecionada == "Consolidador de Notas":
                    with st.container(border=True):
                        c_head_c1, c_head_c2 = st.columns([3, 1])
                        c_head_c1.caption(f"Período Ativo ({trim_ativo_notas}): **{dt_i_n.strftime('%d/%m/%Y')}** até **{dt_f_n.strftime('%d/%m/%Y')}** • *Sincronização dinâmica ativa.*")
                        
                        with c_head_c2.popover("Configurar Período / Corte"):
                            st.caption("Defina a data de corte para encerramento dos vistos do trimestre:")
                            nova_dt_corte = st.date_input("Data de Corte:", dt_f_n, format="DD/MM/YYYY", key=f"inp_corte_pop_{v}")
                            
                            c_pop_s1, c_pop_s2 = st.columns(2)
                            if c_pop_s1.button("Salvar Corte", use_container_width=True, key=f"btn_corte_pop_save_{v}"):
                                dt_str_save = nova_dt_corte.strftime("%d/%m/%Y")
                                if hasattr(db, 'salvar_config_corte_trimestre'):
                                    db.salvar_config_corte_trimestre(turma_notas, trim_ativo_notas, dt_str_save)
                                st.success("Data de corte atualizada!")
                                st.rerun()
                                
                            if c_pop_s2.button("Trancar Vistos", use_container_width=True, key=f"btn_freeze_pop_{v}"):
                                if hasattr(db, 'salvar_config_corte_trimestre'):
                                    db.salvar_config_corte_trimestre(turma_notas, trim_ativo_notas, dt_f_n.strftime("%d/%m/%Y"))
                                st.success("Vistos trancados!")
                                st.rerun()

                    df_notas_editado = st.data_editor(
                        df_grid_ed_notas, hide_index=True, use_container_width=True, height=420,
                        column_config={
                            "ID": None,
                            "Estudante": st.column_config.TextColumn("Estudante", disabled=True, width="medium"),
                            "Caderno (C1)": st.column_config.NumberColumn("Caderno (C1)", format="%.1f", min_value=0.0, max_value=3.0, width="small"),
                            "Testes (C2)": st.column_config.NumberColumn("Testes (C2)", format="%.1f", min_value=0.0, max_value=3.0, width="small"),
                            "Prova (C3)": st.column_config.NumberColumn("Prova (C3)", format="%.1f", min_value=0.0, max_value=4.0, width="small"),
                            "Bônus / Mérito": st.column_config.NumberColumn("Bônus", format="%.1f", disabled=True, width="small"),
                            "Média Normal": st.column_config.NumberColumn("Média Normal", format="%.1f", disabled=True, width="small", help="Média do trimestre antes da REC (C1+C2+C3)"),
                            "Recuperação": st.column_config.NumberColumn("Prova REC", format="%.1f", min_value=0.0, max_value=10.0, width="small", help="Nota da prova de recuperação"),
                            "Média pós-REC": st.column_config.NumberColumn("Média pós-REC", format="%.1f", disabled=True, width="small", help="(Média Normal + REC) / 2"),
                            "Média Final": st.column_config.NumberColumn("Média Final", format="%.1f", width="small", help="Maior nota entre Média Normal e Média pós-REC"),
                            "Situação Regimental": st.column_config.TextColumn("Situação", disabled=True, width="medium")
                        },
                        key=f"ed_grid_notas_main_{turma_notas}_{trim_ativo_notas}_{v}"
                    )

                    c_sav_b1, c_sav_b2 = st.columns(2)
                    
                    if c_sav_b1.button("Consolidar Notas no Boletim", type="primary", use_container_width=True, key=f"btn_save_boletim_{v}"):
                        with st.spinner("Gravando notas consolidadas no banco com proteção soberana..."):
                            linhas_boletim_save = []
                            for _, r_ed in df_notas_editado.iterrows():
                                id_l_s = r_ed['ID']
                                nome_l_s = r_ed['Estudante']
                                c1_s = util.sosa_to_float(r_ed.get('Caderno (C1)', 0.0))
                                c2_s = util.sosa_to_float(r_ed.get('Testes (C2)', 0.0))
                                c3_s = util.sosa_to_float(r_ed.get('Prova (C3)', 0.0))
                                bonus_s = util.sosa_to_float(r_ed.get('Bônus / Mérito', 0.0))
                                rec_s = util.sosa_to_float(r_ed.get('Recuperação', 0.0))
                                
                                # RESOLVIDO: Busca blindada evitando KeyError
                                media_digitada = util.sosa_to_float(r_ed.get('Média Final', r_ed.get('Média Trimestral', 0.0)))
                                
                                c1_f = min(3.0, c1_s + max(0.0, bonus_s))
                                rem_b = max(0.0, bonus_s) - (c1_f - c1_s)
                                c2_f = min(3.0, c2_s + max(0.0, rem_b))
                                rem_b -= (c2_f - c2_s)
                                c3_f = min(4.0, c3_s + max(0.0, rem_b))

                                media_normal_calc = arredondar_05_escolar(c1_f + c2_f + c3_f)

                                if rec_s > 0:
                                    media_pos_rec_calc = arredondar_05_escolar((media_normal_calc + rec_s) / 2.0)
                                    media_calculada = max(media_normal_calc, media_pos_rec_calc)
                                else:
                                    media_calculada = media_normal_calc

                                # Preserva a maior nota (calculada ou ajustada na tabela pelo professor)
                                media_final_salvar = max(media_calculada, media_digitada)

                                linhas_boletim_save.append([
                                    id_l_s, nome_l_s, turma_notas, trim_ativo_notas,
                                    util.sosa_to_str(c1_s), util.sosa_to_str(c2_s), util.sosa_to_str(c3_s),
                                    util.sosa_to_str(rec_s) if rec_s > 0 else "-1",
                                    util.sosa_to_str(media_final_salvar)
                                ])

                            if linhas_boletim_save:
                                db.limpar_notas_turma_trimestre(turma_notas, trim_ativo_notas, forcar=True)
                                db.salvar_lote("DB_NOTAS", linhas_boletim_save)
                                st.success("Boletim trimestral consolidado com sucesso!")
                                st.balloons(); time.sleep(0.8); st.rerun()

                    if c_sav_b2.button("Gerar Etiquetas para Impressão", use_container_width=True, key=f"btn_etiq_docx_clean_{v}"):
                        with st.spinner("Compilando etiquetas executivas em Word A4..."):
                            dados_etiq = []
                            for _, r_ed in df_grid_ed_notas.iterrows():
                                c1_val_f = util.sosa_to_float(r_ed.get('Caderno (C1)', 0.0))
                                c2_val_f = util.sosa_to_float(r_ed.get('Testes (C2)', 0.0))
                                c3_val_f = util.sosa_to_float(r_ed.get('Prova (C3)', 0.0))
                                bonus_val_f = util.sosa_to_float(r_ed.get('Bônus / Mérito', 0.0))
                                media_al_val = util.sosa_to_float(r_ed.get('Média Final', r_ed.get('Média Trimestral', 0.0)))
                                
                                dados_etiq.append({
                                    "nome": str(r_ed.get('Estudante', 'Estudante')),
                                    "c1": c1_val_f,
                                    "c2": c2_val_f,
                                    "c3": c3_val_f,
                                    "bonus": bonus_val_f,
                                    "media": media_al_val,
                                    "status": str(r_ed.get('Situação Regimental', ''))
                                })
                            
                            info_etiq = {"turma": turma_notas, "trimestre": trim_ativo_notas}
                            nome_arq_etiq = f"ETIQUETAS_NOTAS_{turma_notas.replace(' ','_')}_{trim_ativo_notas.replace(' ','')}"
                            
                            doc_etiq_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_etiq, dados_etiq, info_etiq)
                            link_etiq = db.subir_e_converter_para_google_docs(doc_etiq_stream, nome_arq_etiq, trimestre=trim_ativo_notas, categoria=turma_notas, modo="PLANEJAMENTO")
                            
                            if "https" in link_etiq:
                                st.success(f"Etiquetas geradas com sucesso para todos os {len(dados_etiq)} estudantes!")
                                st.link_button("Abrir Etiquetas no Google Drive", link_etiq, type="primary", use_container_width=True)
                                st.balloons()

                # ==============================================================
                # VISÃO 2: VISTOS DE CADERNO & ATITUDE
                # ==============================================================
                elif visao_selecionada == "Vistos de Caderno & Atitude":
                    col_vis_vistos, col_vis_atitude = st.columns([1.1, 1.4])

                    with col_vis_vistos:
                        with st.container(border=True):
                            st.markdown("#### Aulas com Visto de Caderno (C1)")
                            st.caption(f"Acompanhamento da cobrança do caderno ({trim_ativo_notas}):")

                            if df_diario_trim.empty:
                                st.info("Nenhuma aula localizada no diário.")
                            else:
                                df_d_range = df_diario_trim.copy()
                                df_d_range['DATA_DT'] = pd.to_datetime(df_d_range['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                                df_d_range = df_d_range[(df_d_range['DATA_DT'] >= dt_i_n) & (df_d_range['DATA_DT'] <= dt_f_n)]
                                
                                datas_aulas_extrato = sorted(df_d_range['DATA'].unique(), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True)
                                
                                if not datas_aulas_extrato:
                                    st.info("Nenhuma aula registrada no intervalo ativo.")
                                else:
                                    dados_resumo_aulas = []
                                    tot_cobradas, tot_isentas = 0, 0

                                    for d_item_str in datas_aulas_extrato:
                                        df_d_dia_item = df_d_range[df_d_range['DATA'] == d_item_str]
                                        tot_alunos_dia = len(df_d_dia_item)
                                        vistos_ok_dia = len(df_d_dia_item[df_d_dia_item.get('VISTO_ATIVIDADE', '').astype(str).str.upper() == "TRUE"])
                                        is_isento_dia = any(df_d_dia_item.get('VISTO_ATIVIDADE', '').astype(str).str.upper() == "ISENTO")
                                        
                                        reg_aula_info = df_registro_aulas[(df_registro_aulas['DATA'] == d_item_str) & (df_registro_aulas['TURMA'] == turma_notas)] if not df_registro_aulas.empty else pd.DataFrame()
                                        conteudo_dia = str(reg_aula_info.iloc[0].get('CONTEUDO_MINISTRADO', 'Registro de Sala')) if not reg_aula_info.empty else "Registro de Sala"

                                        if is_isento_dia:
                                            status_label = "Isento (0%)"
                                            tot_isentas += 1
                                        else:
                                            status_label = "Cobrado"
                                            tot_cobradas += 1

                                        dados_resumo_aulas.append({
                                            "Data": d_item_str,
                                            "Conteúdo": conteudo_dia[:38] + "..." if len(conteudo_dia) > 38 else conteudo_dia,
                                            "Vistos": f"{vistos_ok_dia:02d}/{tot_alunos_dia:02d}",
                                            "Status": status_label
                                        })

                                    c_k_v1, c_k_v2, c_k_v3 = st.columns(3)
                                    c_k_v1.metric("Total Aulas", len(datas_aulas_extrato))
                                    c_k_v2.metric("Cobradas", tot_cobradas)
                                    c_k_v3.metric("Isentas", tot_isentas)

                                    st.markdown("---")

                                    def style_status_visto(val):
                                        if "Cobrado" in str(val): return 'color: #2962FF; font-weight: bold;'
                                        return 'color: #2ECC71; font-weight: bold;'

                                    st.dataframe(
                                        pd.DataFrame(dados_resumo_aulas).style.map(style_status_visto, subset=['Status']),
                                        hide_index=True, use_container_width=True, height=290,
                                        column_config={
                                            "Data": st.column_config.TextColumn("Data", width="small"),
                                            "Conteúdo": st.column_config.TextColumn("Conteúdo da Aula", width="medium"),
                                            "Vistos": st.column_config.TextColumn("Vistos OK", width="small"),
                                            "Status": st.column_config.TextColumn("Status", width="small")
                                        }
                                    )

                                    with st.popover("Isenção de Cobrança por Data"):
                                        st.caption("Marque uma aula como ISENTA para não penalizar os estudantes:")
                                        data_isentar_sel = st.selectbox("Selecione a Data:", datas_aulas_extrato, key=f"sel_dt_isentar_{v}")
                                        
                                        c_is1, c_is2 = st.columns(2)
                                        if c_is1.button("Tornar Isento", type="primary", use_container_width=True, key=f"btn_isentar_pop_{v}"):
                                            if hasattr(db, 'isentar_vistos_data_turma'):
                                                db.isentar_vistos_data_turma(data_isentar_sel, turma_notas)
                                            st.toast(f"Aula de {data_isentar_sel} marcada como isenta!")
                                            time.sleep(0.5); st.rerun()

                                        if c_is2.button("Reativar Cobrança", use_container_width=True, key=f"btn_reativar_visto_pop_{v}"):
                                            st.info("Para reativar, registre a presença normal na chamada.")

                    with col_vis_atitude:
                        with st.container(border=True):
                            st.markdown("#### Gestão Atitudinal & Ocorrências")
                            st.caption(f"Registro consolidado de mérito e disciplina ({trim_ativo_notas}):")

                            if df_diario_trim.empty:
                                st.info("Nenhum registro atitudinal.")
                            else:
                                df_d_range_at = df_diario_trim.copy()
                                df_d_range_at['DATA_DT'] = pd.to_datetime(df_d_range_at['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                                df_d_range_at = df_d_range_at[(df_d_range_at['DATA_DT'] >= dt_i_n) & (df_d_range_at['DATA_DT'] <= dt_f_n)]
                                df_d_range_at['BONUS_FLOAT'] = df_d_range_at['BONUS'].apply(util.sosa_to_float)
                                
                                mask_atitude = (df_d_range_at['BONUS_FLOAT'] != 0) | (df_d_range_at['TAGS'].isin(["DESTAQUE", "ARGUIÇÃO", "INDISCIPLINA", "CELULAR", "CONVERSA", "ATRASO"]))
                                df_ocorrencias_at = df_d_range_at[mask_atitude].sort_values(by="DATA_DT", ascending=False)

                                tot_bonus_turma = df_d_range_at[df_d_range_at['BONUS_FLOAT'] > 0]['BONUS_FLOAT'].sum()
                                tot_punicoes_turma = df_d_range_at[df_d_range_at['BONUS_FLOAT'] < 0]['BONUS_FLOAT'].sum()

                                c_k_at1, c_k_at2, c_k_at3 = st.columns(3)
                                c_k_at1.metric("Total Bônus", f"+{tot_bonus_turma:.1f} pts")
                                c_k_at2.metric("Total Punições", f"{tot_punicoes_turma:.1f} pts", delta_color="inverse")
                                c_k_at3.metric("Ocorrências", len(df_ocorrencias_at))

                                st.markdown("---")

                                flt_tipo_atitude = st.segmented_control(
                                    "Filtrar Registros:",
                                    ["Todos", "Bônus (+)", "Punições (-)", "Arguições"],
                                    default="Todos",
                                    key=f"pills_flt_atitude_{v}"
                                )

                                df_at_view = df_ocorrencias_at.copy()
                                if flt_tipo_atitude == "Bônus (+)":
                                    df_at_view = df_at_view[df_at_view['BONUS_FLOAT'] > 0]
                                elif flt_tipo_atitude == "Punições (-)":
                                    df_at_view = df_at_view[df_at_view['BONUS_FLOAT'] < 0]
                                elif flt_tipo_atitude == "Arguições":
                                    df_at_view = df_at_view[df_at_view['TAGS'] == "ARGUIÇÃO"]

                                if df_at_view.empty:
                                    st.success("Nenhum registro localizado para este filtro.")
                                else:
                                    dados_at_tabela = []
                                    for idx_oc, (_, r_oc) in enumerate(df_at_view.iterrows()):
                                        dt_oc = str(r_oc.get('DATA', 'N/A'))
                                        id_al_oc = db.limpar_id(r_oc.get('ID_ALUNO', ''))
                                        nome_al_oc = str(r_oc.get('NOME_ALUNO', 'Estudante'))
                                        tag_oc = str(r_oc.get('TAGS', 'OCORRÊNCIA'))
                                        obs_oc = str(r_oc.get('OBSERVACOES', '')).replace("Quadro Negro: ", "").strip()
                                        val_bonus_num = util.sosa_to_float(r_oc.get('BONUS', 0))

                                        impacto_txt = f"+{val_bonus_num:.1f} pts" if val_bonus_num > 0 else (f"{val_bonus_num:.1f} pts" if val_bonus_num < 0 else "0.0 pts")

                                        dados_at_tabela.append({
                                            "Data": dt_oc,
                                            "Estudante": nome_al_oc,
                                            "Tipo": tag_oc,
                                            "Descrição": obs_oc if obs_oc else "Participação em sala",
                                            "Impacto": impacto_txt,
                                            "_ID": id_al_oc,
                                            "_RAW_VAL": val_bonus_num
                                        })

                                    df_at_display = pd.DataFrame(dados_at_tabela)

                                    def style_impacto_at(val):
                                        if "+" in str(val): return 'color: #2ECC71; font-weight: bold;'
                                        if "-" in str(val): return 'color: #E74C3C; font-weight: bold;'
                                        return 'color: gray;'

                                    st.dataframe(
                                        df_at_display[['Data', 'Estudante', 'Tipo', 'Descrição', 'Impacto']].style.map(style_impacto_at, subset=['Impacto']),
                                        hide_index=True, use_container_width=True, height=250,
                                        column_config={
                                            "Data": st.column_config.TextColumn("Data", width="small"),
                                            "Estudante": st.column_config.TextColumn("Estudante", width="medium"),
                                            "Tipo": st.column_config.TextColumn("Tipo", width="small"),
                                            "Descrição": st.column_config.TextColumn("Descrição da Ocorrência", width="large"),
                                            "Impacto": st.column_config.TextColumn("Pontuação", width="small")
                                        }
                                    )

                                    with st.popover("Ajustar Ocorrência / Bônus"):
                                        st.caption("Selecione o registro para perdoar punição ou revogar bônus:")
                                        opcoes_ocorrencias = [f"{r['Data']} — {r['Estudante']} ({r['Impacto']})" for r in dados_at_tabela]
                                        oc_selecionada = st.selectbox("Selecione o Evento:", opcoes_ocorrencias, key=f"sel_oc_pop_{v}")
                                        
                                        if oc_selecionada:
                                            idx_sel_oc = opcoes_ocorrencias.index(oc_selecionada)
                                            item_oc_data = dados_at_tabela[idx_sel_oc]
                                            
                                            if item_oc_data["_RAW_VAL"] > 0:
                                                if st.button("Revogar Bônus", type="primary", use_container_width=True, key=f"btn_revogar_central_{v}"):
                                                    if hasattr(db, 'ajustar_bonus_punicao_diario'):
                                                        db.ajustar_bonus_punicao_diario(item_oc_data['Data'], item_oc_data['_ID'], turma_notas, "0,00", "[Bônus revogado]")
                                                    st.toast("Bônus revogado com sucesso!")
                                                    time.sleep(0.5); st.rerun()
                                            elif item_oc_data["_RAW_VAL"] < 0:
                                                if st.button("Perdoar Punição", type="primary", use_container_width=True, key=f"btn_perdoar_central_{v}"):
                                                    if hasattr(db, 'ajustar_bonus_punicao_diario'):
                                                        db.ajustar_bonus_punicao_diario(item_oc_data['Data'], item_oc_data['_ID'], turma_notas, "0,00", "[Punição perdoada]")
                                                    st.toast("Punição perdoada com sucesso!")
                                                    time.sleep(0.5); st.rerun()

                # ==============================================================
                # VISÃO 3: RECUPERAÇÃO & REFACÇÃO
                # ==============================================================
                else:
                    col_rec_main, col_ref_main = st.columns([1.1, 1.4])

                    with col_rec_main:
                        with st.container(border=True):
                            st.markdown("#### Convocatória de Recuperação")
                            st.caption("Estudantes com rendimento abaixo da média regimental (escala 0 a 10):")
                            
                            trim_destino_rec = st.selectbox("Trimestre da Recuperação:", ["II Trimestre", "I Trimestre", "III Trimestre"], index=0, key=f"sel_dest_rec_clean_{v}")
                            
                            if not convocados_recuperacao:
                                st.success(f"Todos os estudantes da turma {turma_notas} estão com média ≥ 6.0!")
                            else:
                                df_conv_rec = pd.DataFrame(convocados_recuperacao)
                                st.dataframe(
                                    df_conv_rec[['Estudante', 'Média Atual', 'Meta na Prova']],
                                    hide_index=True, use_container_width=True, height=220,
                                    column_config={
                                        "Estudante": st.column_config.TextColumn(width="medium"),
                                        "Média Atual": st.column_config.NumberColumn(format="%.1f"),
                                        "Meta na Prova": st.column_config.NumberColumn("Meta (0 a 10)", format="%.1f")
                                    }
                                )

                                if st.button("Gerar Convocatória Oficial (DOCX)", type="primary", use_container_width=True, key=f"btn_docx_conv_clean_{v}"):
                                    with st.spinner("Compilando convocatórias em Word A4..."):
                                        dados_convocatoria = []
                                        for _, r_conv in df_grid_ed_notas.iterrows():
                                            m_atual_conv = util.sosa_to_float(r_conv.get('Média Final', r_conv.get('Média Trimestral', 0.0)))
                                            if m_atual_conv < 6.0:
                                                dados_convocatoria.append({
                                                    "nome": str(r_conv.get('Estudante', 'Estudante')),
                                                    "c1": util.sosa_to_float(r_conv.get('Caderno (C1)', 0.0)),
                                                    "c2": util.sosa_to_float(r_conv.get('Testes (C2)', 0.0)),
                                                    "c3": util.sosa_to_float(r_conv.get('Prova (C3)', 0.0)),
                                                    "bonus": util.sosa_to_float(r_conv.get('Bônus / Mérito', 0.0)),
                                                    "media": m_atual_conv,
                                                    "status": f"CONVOCADO PARA RECUPERAÇÃO ({trim_destino_rec})"
                                                })
                                        
                                        info_conv_rec = {"turma": turma_notas, "trimestre": f"RECUPERAÇÃO - {trim_destino_rec}"}
                                        nome_arq_conv = f"CONVOCATORIA_RECUPERACAO_{turma_notas.replace(' ','_')}_{trim_destino_rec.replace(' ','')}"
                                        
                                        doc_conv_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_conv, dados_convocatoria, info_conv_rec)
                                        link_conv_doc = db.subir_e_converter_para_google_docs(doc_conv_stream, nome_arq_conv, trimestre=trim_destino_rec, categoria=turma_notas, modo="PLANEJAMENTO")
                                        
                                        if "https" in link_conv_doc:
                                            st.success(f"Convocatória gerada para os {len(dados_convocatoria)} estudantes convocados!")
                                            st.link_button("Abrir Convocatória no Drive", link_conv_doc, type="primary", use_container_width=True)
                                            st.balloons()

                    with col_ref_main:
                        with st.container(border=True):
                            st.markdown("#### Radar de Refacção Solidária (+0.5)")
                            st.caption("Atribua pontuação de refacção com rastreamento visual e trava anti-duplicidade:")
                            
                            mapa_refaccao_diario = {}
                            if not df_diario_trim.empty:
                                for _, r_ref_d in df_diario_trim.iterrows():
                                    id_al_ref_clean = db.limpar_id(r_ref_d.get('ID_ALUNO', ''))
                                    obs_d = str(r_ref_d.get('OBSERVACOES', ''))
                                    tag_d = str(r_ref_d.get('TAGS', ''))
                                    b_num = util.sosa_to_float(r_ref_d.get('BONUS', 0))
                                    
                                    if "Refacção" in obs_d or "Refaccao" in obs_d or "REFACÇÃO" in obs_d or tag_d == "SISTEMA_NOTA":
                                        mapa_refaccao_diario[id_al_ref_clean] = {
                                            "data": str(r_ref_d.get('DATA', 'N/A')),
                                            "valor": b_num if b_num > 0 else 0.5,
                                            "obs": obs_d
                                        }

                            tab_ref_lancar, tab_ref_auditoria = st.tabs(["Lançamento de Refacção", "Rastreabilidade (Quem já entregou)"])
                            
                            with tab_ref_lancar:
                                opcoes_alunos_select = []
                                mapa_label_para_row = {}
                                
                                for _, r_al in df_grid_ed_notas.iterrows():
                                    id_al_r = str(r_al['ID'])
                                    nome_al_r = str(r_al['Estudante'])
                                    b_al_r = util.sosa_to_float(r_al['Bônus / Mérito'])
                                    
                                    ja_entregou_flag = (id_al_r in mapa_refaccao_diario) or (b_al_r > 0)
                                    
                                    if ja_entregou_flag: label_al = f"✅ {nome_al_r} (Refacção Já Aplicada)"
                                    else: label_al = f"🟡 {nome_al_r} (Pendente de Entrega)"
                                        
                                    opcoes_alunos_select.append(label_al)
                                    mapa_label_para_row[label_al] = r_al

                                aluno_sel_label = st.selectbox("Selecione o Estudante:", opcoes_alunos_select, key=f"sel_al_ref_clean_{v}")
                                
                                if aluno_sel_label:
                                    row_ref_al = mapa_label_para_row[aluno_sel_label]
                                    aluno_ref_sel = str(row_ref_al['Estudante'])
                                    id_al_ref = str(row_ref_al['ID'])
                                    media_atual_ref = util.sosa_to_float(row_ref_al['Média Final'])
                                    c1_ref = util.sosa_to_float(row_ref_al['Caderno (C1)'])
                                    c2_ref = util.sosa_to_float(row_ref_al['Testes (C2)'])
                                    c3_ref = util.sosa_to_float(row_ref_al['Prova (C3)'])
                                    bonus_atual_al = util.sosa_to_float(row_ref_al['Bônus / Mérito'])

                                    ja_tem_refaccao = (id_al_ref in mapa_refaccao_diario) or (bonus_atual_al > 0)

                                    c_r1, c_r2 = st.columns(2)
                                    pts_refaccao = c_r1.number_input("Pontuação de Refacção:", 0.0, 2.0, 0.5, step=0.1, key=f"inp_pts_ref_clean_{v}")
                                    alvo_refaccao = c_r2.selectbox("Destino da Nota:", ["Bônus de Caderno", "Testes (C2)", "Prova (C3)"], key=f"sel_alvo_ref_clean_{v}")

                                    if ja_tem_refaccao:
                                        dt_lan = mapa_refaccao_diario[id_al_ref]['data'] if id_al_ref in mapa_refaccao_diario else "Recente"
                                        st.success(f"✅ **Refacção Ativa:** {aluno_ref_sel} já teve a refacção lançada ({dt_lan}) com bônus de **{bonus_atual_al:+.1f} pts** incluído na média.")
                                        novo_bonus_total = bonus_atual_al
                                    else:
                                        novo_bonus_total = bonus_atual_al + pts_refaccao

                                    c1_sim = min(3.0, c1_ref + max(0.0, novo_bonus_total))
                                    rem_b_sim = max(0.0, novo_bonus_total) - (c1_sim - c1_ref)
                                    c2_sim = min(3.0, c2_ref + max(0.0, rem_b_sim))
                                    rem_b_sim -= (c2_sim - c2_ref)
                                    c3_sim = min(4.0, c3_ref + max(0.0, rem_b_sim))

                                    soma_simulada = c1_sim + c2_sim + c3_sim
                                    nova_m_simulada = min(10.0, round(soma_simulada * 2) / 2)

                                    c_m_sim1, c_m_sim2 = st.columns(2)
                                    c_m_sim1.metric("Média Atual Real", f"{media_atual_ref:.1f}")
                                    
                                    if ja_tem_refaccao:
                                        c_m_sim2.metric("Média Consolidada", f"{media_atual_ref:.1f}", "Já inclui refacção")
                                    else:
                                        c_m_sim2.metric("Média Projetada", f"{nova_m_simulada:.1f}", delta=f"+{nova_m_simulada - media_atual_ref:.1f} pts")

                                    c_btn_hom, c_btn_rev = st.columns([2, 1])
                                    
                                    if not ja_tem_refaccao:
                                        if c_btn_hom.button("Homologar Refacção (+0.5)", type="primary", use_container_width=True, key=f"btn_save_ref_al_clean_{v}"):
                                            with st.spinner("Gravando refacção com trava anti-duplicidade..."):
                                                data_hoje_ref = datetime.now().strftime("%d/%m/%Y")
                                                db.salvar_refaccao_soberana(data_hoje_ref, id_al_ref, aluno_ref_sel, turma_notas, pts_refaccao, alvo_refaccao)
                                                db.limpar_notas_turma_trimestre(turma_notas, trim_ativo_notas)
                                                st.cache_data.clear()
                                                st.toast(f"Refacção de {aluno_ref_sel} homologada com sucesso (+{pts_refaccao:.1f} pts)!", icon="✅")
                                                time.sleep(0.5); st.rerun()
                                    else:
                                        c_btn_hom.button("🔒 Refacção Já Homologada", disabled=True, use_container_width=True, key=f"btn_lock_{id_al_ref}_{v}")
                                        
                                        if c_btn_rev.button("🗑️ Revogar Bônus", use_container_width=True, key=f"btn_rev_ref_{id_al_ref}_{v}"):
                                            with st.spinner("Revogando refacção e restaurando nota original..."):
                                                data_hoje_ref = datetime.now().strftime("%d/%m/%Y")
                                                db.salvar_refaccao_soberana(data_hoje_ref, id_al_ref, aluno_ref_sel, turma_notas, 0.0, "[REVOGADO]")
                                                db.limpar_notas_turma_trimestre(turma_notas, trim_ativo_notas)
                                                st.cache_data.clear()
                                                st.toast(f"Refacção de {aluno_ref_sel} revogada com sucesso!", icon="🗑️")
                                                time.sleep(0.5); st.rerun()

                            with tab_ref_auditoria:
                                dados_rastreio = []
                                for _, r_aud in df_grid_ed_notas.iterrows():
                                    id_aud = str(r_aud['ID'])
                                    nome_aud = str(r_aud['Estudante'])
                                    m_aud = util.sosa_to_float(r_aud['Média Final'])
                                    b_aud = util.sosa_to_float(r_aud['Bônus / Mérito'])
                                    
                                    tem_ref = (id_aud in mapa_refaccao_diario) or (b_aud > 0)
                                    status_ref_txt = f"✅ Entregou ({mapa_refaccao_diario[id_aud]['data']})" if tem_ref else "🟡 Pendente de Entrega"

                                    dados_rastreio.append({
                                        "Estudante": nome_aud,
                                        "Status Refacção": status_ref_txt,
                                        "Bônus Acumulado": f"{b_aud:+.1f} pts",
                                        "Média Atual": m_aud
                                    })

                                df_rastreio_view = pd.DataFrame(dados_rastreio)
                                
                                def style_rastreio(val):
                                    if "Entregou" in str(val): return 'color: #2ECC71; font-weight: bold;'
                                    return 'color: #F1C40F; font-weight: bold;'

                                st.dataframe(
                                    df_rastreio_view.style.map(style_rastreio, subset=['Status Refacção']),
                                    hide_index=True, use_container_width=True, height=290,
                                    column_config={
                                        "Estudante": st.column_config.TextColumn(width="medium"),
                                        "Status Refacção": st.column_config.TextColumn(width="medium"),
                                        "Bônus Acumulado": st.column_config.TextColumn(width="small"),
                                        "Média Atual": st.column_config.NumberColumn(format="%.1f", width="small")
                                    }
                                )

            renderizar_painel_notas_fragmento()


# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO DE CLASSE - V2026.PRO_INFINITY_SOBERANIA_TOTAL
# (ESPELHO 1:1 DO PONTO ID OFICIAL DA PREFEITURA DE ITABUNA)
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.title("Boletim Anual & Conselho de Classe")
    st.caption("Visão panorâmica do ano letivo espelhada no padrão oficial Ponto ID da Prefeitura de Itabuna: [Tri | Rec | Média], simulador preditivo para o III Tri e ata oficial.")
    st.markdown("---")

    if "v_bol" not in st.session_state: 
        st.session_state.v_bol = int(time.time())
    v = st.session_state.v_bol

    # ==============================================================================
    # DIALOG DECLARADO NO TOPO DO MÓDULO (LEI #25)
    # ==============================================================================
    @st.dialog("Alerta Preditivo de Metas para WhatsApp", width="large")
    def dialog_zap_metas_iii(nome_aluno, turma, soma_1_2, meta_iii, status_meta, faltas_aluno):
        st.caption(f"Texto acolhedor pronto para cópia e envio aos responsáveis de **{nome_aluno}**:")
        
        if meta_iii == 0.0:
            situacao_msg = "SITUAÇÃO EXCELENTE: O(A) estudante já acumulou os 18,0 pontos regimentais somando o I e II Trimestres e está APROVADO(A) POR ANTECIPAÇÃO no componente de Matemática!"
        elif meta_iii <= 4.0:
            situacao_msg = f"SITUAÇÃO CONFORTÁVEL: Para garantir a aprovação sem necessidade de recuperação final, o(a) estudante precisa de apenas {meta_iii:.1f} pontos no III Trimestre."
        elif meta_iii <= 6.5:
            situacao_msg = f"SITUAÇÃO DE ATENÇÃO: Para fechar a média anual (18,0 pontos), o(a) estudante precisa atingir a meta de {meta_iii:.1f} pontos no III Trimestre."
        elif meta_iii <= 9.9:
            situacao_msg = f"SITUAÇÃO DE ALERTA: O(A) estudante precisa de {meta_iii:.1f} pontos no III Trimestre. Recomendamos foco total nas tarefas de caderno e presença regular."
        else:
            situacao_msg = f"SITUAÇÃO CRÍTICA (RISCO DE RECUPERAÇÃO FINAL): O estudante acumulou {soma_1_2:.1f} pontos nos dois primeiros trimestres e precisará de pontuação máxima no III Trimestre e/ou Recuperação Final para atingir a meta anual de 18,0 pontos."

        msg_zap_meta = f"""Olá! Tudo bem? Aqui é o Prof. Ronaldo Gomes (Componente de Matemática). 🏫
Compartilho com a família o Relatório Preditivo de Metas para o encerramento do ano letivo de 2026 do(a) estudante {nome_aluno} ({turma}).

📊 RENDIMENTO ACUMULADO (I e II TRIMESTRES):
• Soma dos Pontos Conquistados (I Tri + II Tri): {soma_1_2:.1f} pontos.
• Meta Anual Regimental para Aprovação: 18,0 pontos (Média 6,0 x 3 trimestres).
• Total de Faltas Acumuladas no Ano: {faltas_aluno} ausência(s).

🎯 META PROJETADA PARA O III TRIMESTRE:
• Pontuação Necessária no III Tri: {meta_iii:.1f} pontos.
• Status Preditivo: {status_meta}

📌 PARECER PEDAGÓGICO:
{situacao_msg}

Contamos com a parceria da família no acompanhamento diário das tarefas do caderno e na assiduidade às aulas. Seguimos à disposição! 🚀
Escola Municipal Flávio José Simões Costa"""

        st.code(msg_zap_meta, language=None)

    if df_notas.empty:
        st.warning("Sem notas lançadas no sistema. O Boletim Anual será ativado assim que houver dados.")
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
                turma_sel = c_bol1.selectbox("Turma Selecionada:", lista_turmas_bol, key=f"bol_turma_clean_{v}")
                
                with c_bol2.popover("Registrar Ata do Conselho"):
                    st.caption("Registre pareceres e deliberações oficiais do Conselho de Classe:")
                    tipo_ata = st.selectbox("Etapa do Conselho:", ["Conselho Parcial (I Tri)", "Conselho Parcial (II Tri)", "Conselho Final (III Tri)"], key=f"pop_ata_tipo_{v}")
                    texto_ata = st.text_area("Parecer da Turma:", placeholder="Ex: Turma com evolução satisfatória. Estudantes em recuperação foram convocados...", height=110, key=f"pop_ata_txt_{v}")
                    
                    if st.button("Salvar Ata Oficial", type="primary", use_container_width=True, key=f"btn_save_ata_{v}"):
                        if texto_ata.strip():
                            data_hoje_ata = datetime.now().strftime("%d/%m/%Y")
                            db.salvar_ata_conselho(data_hoje_ata, turma_sel, tipo_ata, texto_ata)
                            st.success("Ata do Conselho salva com sucesso!")
                            time.sleep(0.8); st.rerun()
                        else: st.error("Digite o texto da ata antes de salvar.")

            @st.fragment
            def renderizar_boletim_anual_fragmento():
                df_t = df_notas[df_notas['TURMA'] == turma_sel].copy() if not df_notas.empty and 'TURMA' in df_notas.columns else pd.DataFrame()
                
                if df_t.empty:
                    st.info(f"Nenhuma nota lançada para a turma {turma_sel} ainda.")
                else:
                    df_alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].copy() if not df_alunos.empty and 'TURMA' in df_alunos.columns else pd.DataFrame()
                    if 'STATUS' not in df_alunos_turma.columns: df_alunos_turma['STATUS'] = "ATIVO"

                    c_flt1, c_flt2 = st.columns([1.5, 2])
                    flt_status_alunos = c_flt1.segmented_control("Estudantes:", ["Apenas Ativos", "Todos os Registros"], default="Apenas Ativos", key=f"pills_flt_ativos_bol_{v}")

                    visao_conselho_ativa = c_flt2.segmented_control(
                        "Visão:",
                        ["Termômetro & Boletim Anual", "Simulador Preditivo (III Tri)"],
                        default="Termômetro & Boletim Anual",
                        key=f"seg_visao_conselho_{v}"
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

                    if flt_status_alunos == "Apenas Ativos":
                        ids_ativos = df_alunos_turma[~df_alunos_turma['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])]['ID'].apply(db.limpar_id).tolist()
                        df_t = df_t[df_t['ID_ALUNO'].apply(db.limpar_id).isin(ids_ativos)]

                    # SOSA V2026 - PIVOT REGIMENTAL ESPELHO DO PONTO ID DA PREFEITURA DE ITABUNA:
                    # Calcula Média Normal (C1+C2+C3), Prova REC e Média Final Consolidada para cada trimestre
                    import math
                    def arred_05_bol(v): return min(10.0, math.floor(v * 2.0 + 0.5) / 2.0)

                    df_t['C1_N'] = df_t['NOTA_VISTOS'].apply(util.sosa_to_float)
                    df_t['C2_N'] = df_t['NOTA_TESTE'].apply(util.sosa_to_float)
                    df_t['C3_N'] = df_t['NOTA_PROVA'].apply(util.sosa_to_float)
                    df_t['MEDIA_NORMAL'] = df_t.apply(lambda r: arred_05_bol(r['C1_N'] + r['C2_N'] + r['C3_N']), axis=1)

                    pivot = df_t.pivot_table(
                        index=["ID_ALUNO", "NOME_ALUNO"], 
                        columns="TRIMESTRE", 
                        values=["MEDIA_NORMAL", "NOTA_REC", "MEDIA_FINAL"], 
                        aggfunc='first'
                    ).reset_index()

                    pivot.columns = [f"{col[0]}_{col[1]}".strip('_') for col in pivot.columns.values]

                    trims = ["I Trimestre", "II Trimestre", "III Trimestre"]
                    for t in trims:
                        if f"MEDIA_NORMAL_{t}" not in pivot.columns: pivot[f"MEDIA_NORMAL_{t}"] = 0.0
                        if f"MEDIA_FINAL_{t}" not in pivot.columns: pivot[f"MEDIA_FINAL_{t}"] = 0.0
                        if f"NOTA_REC_{t}" in pivot.columns:
                            pivot[f"NOTA_REC_{t}"] = pivot[f"NOTA_REC_{t}"].fillna(-1.0)
                        else:
                            pivot[f"NOTA_REC_{t}"] = -1.0

                    rec_f_data = df_t[df_t['TRIMESTRE'].astype(str).str.contains("REC_FINAL|FINAL", na=False, case=False)] if 'TRIMESTRE' in df_t.columns else pd.DataFrame()
                    if not rec_f_data.empty and 'ID_ALUNO' in rec_f_data.columns and 'MEDIA_FINAL' in rec_f_data.columns:
                        rec_f_min = rec_f_data[['ID_ALUNO', 'MEDIA_FINAL']].rename(columns={'MEDIA_FINAL': 'RF'})
                        pivot = pd.merge(pivot, rec_f_min, on='ID_ALUNO', how='left')
                        pivot['RF'] = pivot['RF'].fillna(-1.0)
                    else:
                        pivot['RF'] = -1.0
                    
                    faltas_df = df_diario[(df_diario['TURMA'] == turma_sel) & (df_diario['TAGS'] == "AUSÊNCIA")] if not df_diario.empty and 'TURMA' in df_diario.columns and 'TAGS' in df_diario.columns else pd.DataFrame()
                    
                    if not faltas_df.empty and 'ID_ALUNO' in faltas_df.columns:
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

                    has_t1 = pivot['MEDIA_FINAL_I Trimestre'].sum() > 0
                    has_t2 = pivot['MEDIA_FINAL_II Trimestre'].sum() > 0
                    has_t3 = pivot['MEDIA_FINAL_III Trimestre'].sum() > 0
                    
                    trimestres_ativos = sum([has_t1, has_t2, has_t3])
                    if trimestres_ativos == 0: trimestres_ativos = 1

                    meta_acumulada_parcial = trimestres_ativos * 6.0

                    dias_validos = df_diario[(df_diario['TURMA'] == turma_sel) & (~df_diario['TAGS'].isin(['DIA NÃO LETIVO', 'BONUS_CONSELHO', 'SISTEMA_NOTA']))] if not df_diario.empty and 'TURMA' in df_diario.columns and 'TAGS' in df_diario.columns else pd.DataFrame()
                    total_dias_letivos = dias_validos['DATA'].nunique() if not dias_validos.empty else 1
                    if total_dias_letivos == 0: total_dias_letivos = 1
                    limite_faltas = int(total_dias_letivos * 0.25)
                    if limite_faltas == 0: limite_faltas = 1 

                    def calcular_situacao_anual(row):
                        t1 = util.sosa_to_float(row.get("MEDIA_FINAL_I Trimestre", 0))
                        t2 = util.sosa_to_float(row.get("MEDIA_FINAL_II Trimestre", 0))
                        t3 = util.sosa_to_float(row.get("MEDIA_FINAL_III Trimestre", 0))
                        rf = util.sosa_to_float(row.get("RF", -1.0))
                        faltas_aluno = row.get("FALTAS", 0)
                        
                        soma = t1 + t2 + t3
                        media_parcial = soma / trimestres_ativos
                        
                        aluno_match = df_alunos[df_alunos['ID'].apply(db.limpar_id) == db.limpar_id(row.get('ID_ALUNO', ''))] if not df_alunos.empty and 'ID' in df_alunos.columns else pd.DataFrame()
                        if not aluno_match.empty:
                            aluno_info = aluno_match.iloc[0]
                            nec_raw = str(aluno_info.get('NECESSIDADES', 'TÍPICO')).upper().strip()
                            if "PENDENTE" in nec_raw or "SUSPEITA" in nec_raw: pei = "🟠"
                            elif "DEFASAGEM LEITURA" in nec_raw: pei = "🧱"
                            elif "DEFASAGEM MATEMÁTICA" in nec_raw or "DEFASAGEM MATEMATICA" in nec_raw: pei = "🧮"
                            elif "ALTA PERFORMANCE" in nec_raw: pei = "🚀"
                            elif nec_raw not in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: pei = "♿"
                            else: pei = "👤"
                        else:
                            pei = "👤"
                        
                        if faltas_aluno >= (total_dias_letivos * 0.5) and soma == 0: 
                            status = "Evasão / Inativo"
                        elif faltas_aluno > limite_faltas:
                            status = "Reprovado por Falta"
                        elif trimestres_ativos == 3:
                            if soma >= 18.0: status = "Aprovado Direto"
                            elif rf >= 6.0: status = "Aprovado com REC"
                            else: status = "Reprovado Final"
                        else:
                            if media_parcial >= 6.0:
                                status = "Na Média"
                            elif media_parcial >= 4.5:
                                status = "Risco de Média"
                            else:
                                status = "Risco Crítico"
                        
                        return pd.Series([pei, soma, media_parcial, status])

                    pivot[['P', 'Σ', 'MÉDIA_PARCIAL', 'SITUAÇÃO']] = pivot.apply(calcular_situacao_anual, axis=1)

                    # ==============================================================
                    # VISÃO 1: TERMÔMETRO & BOLETIM ANUAL ESPELHO PONTO ID
                    # ==============================================================
                    if visao_conselho_ativa == "Termômetro & Boletim Anual":
                        st.markdown(f"#### Termômetro do Conselho (Ponderação: {trimestres_ativos} Trimestre(s) Ativo(s))")
                        
                        media_geral_parcial = pivot['MÉDIA_PARCIAL'].mean() if len(pivot) > 0 else 0.0
                        na_media_count = len(pivot[pivot['SITUAÇÃO'].isin(["Aprovado Direto", "Na Média", "Aprovado com REC"])])
                        taxa_sucesso = (na_media_count / len(pivot)) * 100 if len(pivot) > 0 else 0
                        risco_nota_count = len(pivot[pivot['SITUAÇÃO'].isin(["Risco de Média", "Risco Crítico"])])
                        risco_faltas_count = len(pivot[pivot['SITUAÇÃO'] == "Reprovado por Falta"])

                        with st.container(border=True):
                            k1, k2, k3, k4 = st.columns(4)
                            k1.metric("Média Parcial da Classe", f"{media_geral_parcial:.1f}")
                            k2.metric("Estudantes na Média", f"{na_media_count} ({taxa_sucesso:.0f}%)", f"{len(pivot)} total")
                            k3.metric("Risco de Média", risco_nota_count, delta_color="inverse" if risco_nota_count > 0 else "normal")
                            k4.metric("Risco de Frequência", risco_faltas_count, delta_color="inverse" if risco_faltas_count > 0 else "normal")

                        st.markdown("---")

                        filtro_conselho = st.pills(
                            "Filtrar Classe:",
                            ["Todos", "Na Média", "Risco de Média", "Risco de Frequência", "Evasão / Inatividade"],
                            default="Todos",
                            key=f"pills_cons_flt_{v}"
                        )

                        pivot_exibir = pivot.copy()
                        if filtro_conselho == "Na Média":
                            pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'].isin(["Aprovado Direto", "Na Média", "Aprovado com REC"])]
                        elif filtro_conselho == "Risco de Média":
                            pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'].isin(["Risco de Média", "Risco Crítico"])]
                        elif filtro_conselho == "Risco de Frequência":
                            pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'] == "Reprovado por Falta"]
                        elif filtro_conselho == "Evasão / Inatividade":
                            pivot_exibir = pivot_exibir[pivot_exibir['SITUAÇÃO'] == "Evasão / Inativo"]

                        st.caption(f"Exibindo **{len(pivot_exibir)} de {len(pivot)}** estudantes.")

                        def style_status_anual(val):
                            if "Aprovado" in str(val) or "Na Média" in str(val): return 'color: #2ECC71; font-weight: bold;'
                            if "Evasão" in str(val) or "Reprovado" in str(val) or "Crítico" in str(val): return 'color: #E74C3C; font-weight: bold;'
                            if "Risco de Média" in str(val): return 'color: #F1C40F; font-weight: bold;'
                            return 'color: gray;'

                        def formatar_rec(val):
                            if pd.isna(val) or val < 0 or val == 0: return "-"
                            return f"{val:.1f}"

                        def formatar_media(val):
                            if pd.isna(val) or val == 0: return "-"
                            return f"{val:.1f}"

                        colunas_espelho_prefeitura = [
                            'P', 'NOME_ALUNO',
                            'MEDIA_NORMAL_I Trimestre', 'NOTA_REC_I Trimestre', 'MEDIA_FINAL_I Trimestre',
                            'MEDIA_NORMAL_II Trimestre', 'NOTA_REC_II Trimestre', 'MEDIA_FINAL_II Trimestre',
                            'MEDIA_NORMAL_III Trimestre', 'NOTA_REC_III Trimestre', 'MEDIA_FINAL_III Trimestre',
                            'Σ', 'RF', 'FALTAS', 'SITUAÇÃO'
                        ]

                        st.dataframe(
                            pivot_exibir[colunas_espelho_prefeitura]
                            .style.map(style_status_anual, subset=['SITUAÇÃO'])
                            .format(formatar_media, subset=['MEDIA_NORMAL_I Trimestre', 'MEDIA_FINAL_I Trimestre', 'MEDIA_NORMAL_II Trimestre', 'MEDIA_FINAL_II Trimestre', 'MEDIA_NORMAL_III Trimestre', 'MEDIA_FINAL_III Trimestre'])
                            .format(formatar_rec, subset=['NOTA_REC_I Trimestre', 'NOTA_REC_II Trimestre', 'NOTA_REC_III Trimestre', 'RF']),
                            use_container_width=True, hide_index=True,
                            column_config={
                                "P": st.column_config.TextColumn("P", width="small", help="Perfil de Acessibilidade"),
                                "NOME_ALUNO": st.column_config.TextColumn("Estudante", width="medium"),
                                "MEDIA_NORMAL_I Trimestre": st.column_config.TextColumn("1º Tri", width="small", help="Média Normal (C1+C2+C3)"),
                                "NOTA_REC_I Trimestre": st.column_config.TextColumn("1ª Rec", width="small", help="Nota da Prova de Recuperação"),
                                "MEDIA_FINAL_I Trimestre": st.column_config.TextColumn("Média 1º", width="small", help="Média Final Consolidada"),
                                "MEDIA_NORMAL_II Trimestre": st.column_config.TextColumn("2º Tri", width="small", help="Média Normal (C1+C2+C3)"),
                                "NOTA_REC_II Trimestre": st.column_config.TextColumn("2ª Rec", width="small", help="Nota da Prova de Recuperação"),
                                "MEDIA_FINAL_II Trimestre": st.column_config.TextColumn("Média 2º", width="small", help="Média Final Consolidada"),
                                "MEDIA_NORMAL_III Trimestre": st.column_config.TextColumn("3º Tri", width="small", help="Média Normal (C1+C2+C3)"),
                                "NOTA_REC_III Trimestre": st.column_config.TextColumn("3ª Rec", width="small", help="Nota da Prova de Recuperação"),
                                "MEDIA_FINAL_III Trimestre": st.column_config.TextColumn("Média 3º", width="small", help="Média Final Consolidada"),
                                "Σ": st.column_config.ProgressColumn("Soma Total", help=f"Soma das Médias Finais (Meta: {meta_acumulada_parcial:.1f} pts)", format="%.1f", min_value=0.0, max_value=meta_acumulada_parcial if meta_acumulada_parcial > 0 else 18.0),
                                "RF": st.column_config.TextColumn("Rec Final", width="small"),
                                "FALTAS": st.column_config.ProgressColumn("Faltas", help=f"Limite: {limite_faltas}", format="%d", min_value=0, max_value=max(limite_faltas, 1)),
                                "SITUAÇÃO": st.column_config.TextColumn("Situação", width="medium")
                            }
                        )
                        
                        st.caption(f"📋 Padrão Oficial Ponto ID (Prefeitura de Itabuna): [Xº Tri] Média Normal | [Xª Rec] Prova de REC | [Média Xº] Média Final (permanece a maior) | Limite Faltas: {limite_faltas}.")

                        st.markdown("---")
                        
                        if st.button("Gerar Ata Oficial em Word (DOCX)", type="primary", use_container_width=True, key=f"btn_gen_ata_docx_{v}"):
                            with st.spinner("Compilando ata oficial do Conselho de Classe..."):
                                dados_ata_export = []
                                for _, r_p in pivot.iterrows():
                                    dados_ata_export.append({
                                        "nome": r_p.get('NOME_ALUNO', 'Estudante'),
                                        "soma": f"{util.sosa_to_float(r_p.get('Σ', 0)):.1f}",
                                        "media_parcial": f"{util.sosa_to_float(r_p.get('MÉDIA_PARCIAL', 0)):.1f}",
                                        "faltas": str(r_p.get('FALTAS', 0)),
                                        "status": str(r_p.get('SITUAÇÃO', 'N/A'))
                                    })
                                
                                info_ata = {"turma": turma_sel, "trimestres_ativos": trimestres_ativos}
                                nome_arq_ata = f"ATA_CONSELHO_{turma_sel.replace(' ', '')}_2026"
                                
                                doc_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_ata, dados_ata_export, info_ata)
                                link_doc = db.subir_e_converter_para_google_docs(doc_stream, nome_arq_ata, trimestre="Conselho", categoria=turma_sel, modo="PLANEJAMENTO")
                                
                                if "https" in link_doc:
                                    st.success("Ata do Conselho gerada com sucesso!")
                                    st.link_button("Abrir Ata Oficial no Drive", link_doc, type="primary", use_container_width=True)
                                    st.balloons()
                                else: st.error(f"Erro ao salvar no Drive: {link_doc}")

                    # ==============================================================
                    # VISÃO 2: SIMULADOR PREDITIVO DE METAS PARA O III TRIMESTRE
                    # ==============================================================
                    else:
                        st.markdown("### Simulador Preditivo de Metas (III Trimestre)")
                        st.caption(f"Projeção de rendimento individual e da classe para o alcance da meta anual de **18,0 pontos**.")

                        with st.container(border=True):
                            c_sim1, c_sim2 = st.columns([1.5, 2])
                            
                            cenario_bonus_sim = c_sim1.segmented_control(
                                "Simular Bônus / Refacção no III Tri:",
                                ["0,0 pts (Padrão)", "+0,5 pts (Refacção)", "+1,0 pt (Engajamento Máximo)"],
                                default="0,0 pts (Padrão)",
                                key=f"seg_bonus_sim_{v}"
                            )
                            bonus_sim_val = 0.0
                            if "+0,5" in str(cenario_bonus_sim): bonus_sim_val = 0.5
                            elif "+1,0" in str(cenario_bonus_sim): bonus_sim_val = 1.0

                            c_sim2.info(f"Simulação Ativa: Com **+{bonus_sim_val:.1f} pts** projetados, a meta na avaliação do III Trimestre reduz proporcionalmente.")

                        dados_preditivos = []
                        cnt_aprov_antecipado, cnt_meta_tranquila, cnt_meta_moderada, cnt_meta_alta, cnt_risco_rec_final = 0, 0, 0, 0, 0

                        for _, r_al in pivot.iterrows():
                            id_al_p = db.limpar_id(r_al.get('ID_ALUNO', ''))
                            nome_al_p = str(r_al.get('NOME_ALUNO', 'Estudante'))
                            perfil_icon_p = str(r_al.get('P', '👤'))
                            faltas_al_p = int(r_al.get('FALTAS', 0))

                            t1_val = util.sosa_to_float(r_al.get("MEDIA_FINAL_I Trimestre", 0.0))
                            t2_val = util.sosa_to_float(r_al.get("MEDIA_FINAL_II Trimestre", 0.0))
                            soma_1_2 = t1_val + t2_val

                            meta_bruta_iii = max(0.0, 18.0 - soma_1_2)
                            meta_ajustada_sim = max(0.0, meta_bruta_iii - bonus_sim_val)
                            meta_ajustada_arred = round(meta_ajustada_sim * 2) / 2

                            if soma_1_2 >= 18.0:
                                status_pred = "Aprovado Antecipado"
                                cnt_aprov_antecipado += 1
                                precisa_exib = "0,0 pts (Garantido)"
                            elif meta_ajustada_arred <= 4.0:
                                status_pred = "Meta Tranquila (≤ 4.0)"
                                cnt_meta_tranquila += 1
                                precisa_exib = f"{meta_ajustada_arred:.1f} pts"
                            elif meta_ajustada_arred <= 6.5:
                                status_pred = "Meta Moderada (4.1 a 6.5)"
                                cnt_meta_moderada += 1
                                precisa_exib = f"{meta_ajustada_arred:.1f} pts"
                            elif meta_ajustada_arred <= 9.9:
                                status_pred = "Meta Alta (6.6 a 9.9)"
                                cnt_meta_alta += 1
                                precisa_exib = f"{meta_ajustada_arred:.1f} pts"
                            else:
                                status_pred = "Risco de Rec. Final (≥ 10.0)"
                                cnt_risco_rec_final += 1
                                precisa_exib = f"{meta_ajustada_arred:.1f} pts (Crítico)"

                            dados_preditivos.append({
                                "ID": id_al_p,
                                "P": perfil_icon_p,
                                "Estudante": nome_al_p,
                                "I Tri": t1_val,
                                "II Tri": t2_val,
                                "Soma I+II": soma_1_2,
                                "Meta III Tri": meta_ajustada_arred,
                                "Meta Exibição": precisa_exib,
                                "Status Preditivo": status_pred,
                                "Faltas": faltas_al_p
                            })

                        with st.container(border=True):
                            st.markdown("##### Panorama Preditivo da Turma (III Trimestre)")
                            k_p1, k_p2, k_p3, k_p4, k_p5 = st.columns(5)
                            k_p1.metric("Aprovados Antecipados", cnt_aprov_antecipado, f"Soma I+II ≥ 18.0")
                            k_p2.metric("Meta Tranquila", cnt_meta_tranquila, f"Precisa ≤ 4.0")
                            k_p3.metric("Meta Moderada", cnt_meta_moderada, f"Precisa 4.1 a 6.5")
                            k_p4.metric("Meta Alta", cnt_meta_alta, f"Precisa 6.6 a 9.9")
                            k_p5.metric("Risco Rec. Final", cnt_risco_rec_final, f"Precisa ≥ 10.0", delta_color="inverse" if cnt_risco_rec_final > 0 else "normal")

                        st.markdown("---")

                        filtro_pred = st.pills(
                            "Filtrar por Meta do III Tri:",
                            ["Todos", "Aprovados Antecipados", "Meta Tranquila (≤ 4.0)", "Meta Moderada (4.1 a 6.5)", "Meta Alta (6.6 a 9.9)", "Risco de Rec. Final (≥ 10.0)"],
                            default="Todos",
                            key=f"pills_flt_pred_{v}"
                        )
                        if not filtro_pred: filtro_pred = "Todos"

                        df_pred_exibir = pd.DataFrame(dados_preditivos)
                        if filtro_pred == "Aprovados Antecipados":
                            df_pred_exibir = df_pred_exibir[df_pred_exibir['Status Preditivo'].str.contains("Antecipado")]
                        elif filtro_pred == "Meta Tranquila (≤ 4.0)":
                            df_pred_exibir = df_pred_exibir[df_pred_exibir['Status Preditivo'].str.contains("Tranquila")]
                        elif filtro_pred == "Meta Moderada (4.1 a 6.5)":
                            df_pred_exibir = df_pred_exibir[df_pred_exibir['Status Preditivo'].str.contains("Moderada")]
                        elif filtro_pred == "Meta Alta (6.6 a 9.9)":
                            df_pred_exibir = df_pred_exibir[df_pred_exibir['Status Preditivo'].str.contains("Alta")]
                        elif filtro_pred == "Risco de Rec. Final (≥ 10.0)":
                            df_pred_exibir = df_pred_exibir[df_pred_exibir['Status Preditivo'].str.contains("Risco")]

                        def style_status_preditivo(val):
                            if "Antecipado" in str(val) or "Tranquila" in str(val): return 'color: #2ECC71; font-weight: bold;'
                            if "Moderada" in str(val): return 'color: #F1C40F; font-weight: bold;'
                            if "Alta" in str(val): return 'color: #E67E22; font-weight: bold;'
                            if "Risco" in str(val): return 'color: #E74C3C; font-weight: bold;'
                            return 'color: gray;'

                        st.dataframe(
                            df_pred_exibir[['P', 'Estudante', 'I Tri', 'II Tri', 'Soma I+II', 'Meta III Tri', 'Status Preditivo', 'Faltas']]
                            .style.map(style_status_preditivo, subset=['Status Preditivo'])
                            .format({'I Tri': '{:.1f}', 'II Tri': '{:.1f}', 'Soma I+II': '{:.1f}', 'Meta III Tri': '{:.1f}'}),
                            use_container_width=True, hide_index=True,
                            column_config={
                                "P": st.column_config.TextColumn("P", width="small"),
                                "Estudante": st.column_config.TextColumn("Estudante", width="medium"),
                                "I Tri": st.column_config.NumberColumn("I Tri", format="%.1f", width="small"),
                                "II Tri": st.column_config.NumberColumn("II Tri", format="%.1f", width="small"),
                                "Soma I+II": st.column_config.ProgressColumn("Soma I+II", format="%.1f", min_value=0.0, max_value=20.0, help="Soma dos dois primeiros trimestres (Meta anual: 18.0)"),
                                "Meta III Tri": st.column_config.NumberColumn("Meta no III Tri", format="%.1f", help="Nota mínima exigida no III Trimestre para aprovação"),
                                "Status Preditivo": st.column_config.TextColumn("Projeção", width="medium"),
                                "Faltas": st.column_config.NumberColumn("Faltas", width="small")
                            }
                        )

                        st.markdown("---")

                        c_act_pred1, c_act_pred2 = st.columns([1.5, 1.5])

                        with c_act_pred1.popover("Disparar Alerta de Metas para WhatsApp"):
                            st.caption("Selecione o estudante para abrir o texto preditivo:")
                            aluno_zap_sel = st.selectbox("Estudante:", [r['Estudante'] for r in dados_preditivos], key=f"sel_al_zap_meta_{v}")
                            
                            if aluno_zap_sel:
                                r_zap_data = next(r for r in dados_preditivos if r['Estudante'] == aluno_zap_sel)
                                if st.button("Abrir Texto para WhatsApp", type="primary", use_container_width=True, key=f"btn_open_zap_meta_dialog_{v}"):
                                    dialog_zap_metas_iii(
                                        nome_aluno=r_zap_data['Estudante'],
                                        turma=turma_sel,
                                        soma_1_2=r_zap_data['Soma I+II'],
                                        meta_iii=r_zap_data['Meta III Tri'],
                                        status_meta=r_zap_data['Status Preditivo'],
                                        faltas_aluno=r_zap_data['Faltas']
                                    )

                        if c_act_pred2.button("Gerar Relatório Preditivo (DOCX)", type="primary", use_container_width=True, key=f"btn_docx_pred_metas_{v}"):
                            with st.spinner("Compilando relatório preditivo de metas em Word A4..."):
                                dados_docx_pred = []
                                for r_pred in dados_preditivos:
                                    dados_docx_pred.append({
                                        "nome": r_pred['Estudante'],
                                        "vistos": f"I Tri: {r_pred['I Tri']:.1f}",
                                        "teste": f"II Tri: {r_pred['II Tri']:.1f}",
                                        "prova": f"Soma: {r_pred['Soma I+II']:.1f}",
                                        "bonus": f"{bonus_sim_val:+.1f}",
                                        "media": f"Meta: {r_pred['Meta III Tri']:.1f}",
                                        "status": f"{r_pred['Status Preditivo']} ({r_pred['Faltas']} faltas)"
                                    })
                                
                                info_doc_pred = {"turma": turma_sel, "trimestre": "PROJEÇÃO III TRIMESTRE - CONSELHO"}
                                nome_arq_pred = f"RELATORIO_PREDITIVO_METAS_{turma_sel.replace(' ','_')}_2026"
                                
                                doc_stream_pred = exporter.gerar_docx_etiquetas_notas(nome_arq_pred, dados_docx_pred, info_doc_pred)
                                link_doc_pred = db.subir_e_converter_para_google_docs(doc_stream_pred, nome_arq_pred, trimestre="Conselho", categoria=turma_sel, modo="PLANEJAMENTO")
                                
                                if "https" in link_doc_pred:
                                    st.success("Relatório Preditivo de Metas gerado com sucesso!")
                                    st.link_button("Abrir Relatório no Drive", link_doc_pred, type="primary", use_container_width=True)
                                    st.balloons()
                                else: st.error(f"Erro ao salvar no Drive: {link_doc_pred}")

            renderizar_boletim_anual_fragmento()






# ==============================================================================
# MÓDULO: GESTÃO DA TURMA (COCKPIT DE REGÊNCIA 360°) - V2026.PRO_EXECUTIVE
# (TIMELINE CRONOLÓGICA ÚNICA, PROFICIÊNCIA SAEB, RADAR DUPLO E SECRETARIA)
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("Gestão da Turma")
    st.caption("Cockpit de regência: controle diário de frequência e vistos de caderno, radiografia analítica SAEB e gestão de matrículas.")
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

    # ==============================================================================
    # DIALOGS DECLARADOS NO TOPO DO MÓDULO (LEI #25)
    # ==============================================================================
    @st.dialog("Esquadrão de Arguição (Quadro Negro)", width="large")
    def dialog_roleta(t_roleta):
        c_rol1, c_rol2, c_rol3 = st.columns([1, 1, 1])
        data_roleta = c_rol1.date_input("Data da Arguição:", date.today(), format="DD/MM/YYYY", key=f"rol_d_{v}")
        data_roleta_str = data_roleta.strftime("%d/%m/%Y")
        qtd_sorteio = c_rol2.number_input("Estudantes por Rodada:", 1, 4, 3, key=f"rol_qtd_{v}")
        
        with c_rol3.popover("Configurar Pontuação"):
            pt_acerto = st.number_input("Pontuação por Acerto (+):", 0.0, 5.0, 0.5, step=0.1, key=f"pt_ac_{v}")
            pt_recusa = st.number_input("Punição por Recusa (-):", -5.0, 0.0, -0.5, step=0.1, key=f"pt_rec_{v}")

        df_alunos_base_rol = df_alunos[df_alunos['TURMA'] == t_roleta].copy() if not df_alunos.empty else pd.DataFrame()
        if 'STATUS' not in df_alunos_base_rol.columns: df_alunos_base_rol['STATUS'] = "ATIVO"
        alunos_roleta = df_alunos_base_rol[~df_alunos_base_rol['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")
        
        if alunos_roleta.empty: 
            st.warning("Nenhum estudante ativo cadastrado nesta turma.")
            return
        
        freq_arguicao = {}
        if not df_diario.empty and 'TURMA' in df_diario.columns and 'TAGS' in df_diario.columns:
            df_arg_hist = df_diario[(df_diario['TURMA'] == t_roleta) & (df_diario['TAGS'].astype(str).str.contains("ARGUIÇÃO"))]
            if not df_arg_hist.empty and 'ID_ALUNO' in df_arg_hist.columns:
                freq_counts = df_arg_hist.groupby('ID_ALUNO').size().to_dict()
                for id_al_raw, cnt_f in freq_counts.items():
                    freq_arguicao[db.limpar_id(id_al_raw)] = cnt_f

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
        chave_sorteados = f"alunos_sorteados_{t_roleta}_{data_roleta_str}"
        
        if chave_lista not in st.session_state:
            diario_dia = df_diario[(df_diario['DATA'] == data_roleta_str) & (df_diario['TURMA'] == t_roleta)] if not df_diario.empty else pd.DataFrame()
            lista_inicial = []
            for _, row in alunos_roleta.iterrows():
                id_a = db.limpar_id(row.get('ID', ''))
                nome_a = str(row.get('NOME_ALUNO', 'Estudante'))
                icone_a = str(row.get('ICONE', '👤'))
                v_freq = freq_arguicao.get(id_a, 0)
                
                status_inicial, obs_inicial, pts_inicial = "Pendente", "", 0.0
                
                if not diario_dia.empty:
                    reg_aluno = diario_dia[diario_dia['ID_ALUNO'].apply(db.limpar_id) == id_a]
                    if not reg_aluno.empty:
                        if any(reg_aluno.get('TAGS', '') == "AUSÊNCIA"):
                            status_inicial, obs_inicial = "Ausente", "Ausente no Diário."
                        elif any(reg_aluno.get('TAGS', '').astype(str).str.contains("ARGUIÇÃO")):
                            reg_arg = reg_aluno[reg_aluno['TAGS'].astype(str).str.contains("ARGUIÇÃO")].iloc[-1]
                            obs_inicial = str(reg_arg.get('OBSERVACOES', '')).replace("Quadro Negro: ", "")
                            pts_inicial = util.sosa_to_float(reg_arg.get('BONUS', '0,00'))
                            if pts_inicial > 0: status_inicial = "Dominou"
                            elif pts_inicial < 0: status_inicial = "Recusou"
                            elif "Isento" in obs_inicial: status_inicial = "Isento"
                            else: status_inicial = "Participou"
                lista_inicial.append({"ID": id_a, "Estudante": f"{icone_a} {nome_a}", "Situação": status_inicial, "Diagnóstico": obs_inicial, "Pontos": pts_inicial, "Chamadas": v_freq})
            st.session_state[chave_lista] = lista_inicial
            
        if chave_sorteados not in st.session_state: st.session_state[chave_sorteados] = []

        st.markdown("---")
        pendentes = [a for a in st.session_state[chave_lista] if a["Situação"] == "Pendente"]
        
        c_btn_sort, c_btn_reset = st.columns([2, 1])
        if c_btn_sort.button("Sortear Estudantes (Prioridade por Equidade)", type="primary", use_container_width=True, key=f"btn_sort_{v}"):
            if not pendentes: st.success("Todos os estudantes já participaram da arguição nesta aula!")
            else: 
                pendentes_ordenados = sorted(pendentes, key=lambda x: x["Chamadas"])
                grupo_candidatos = pendentes_ordenados[:max(qtd_sorteio * 2, len(pendentes_ordenados))]
                qtd_real = min(qtd_sorteio, len(grupo_candidatos))
                st.session_state[chave_sorteados] = [p["ID"] for p in random.sample(grupo_candidatos, qtd_real)]
                st.rerun()
                
        if c_btn_reset.button("Reiniciar Rodada", use_container_width=True, key=f"btn_res_rol_{v}"):
            del st.session_state[chave_lista]; st.session_state[chave_sorteados] = []; st.rerun()
            
        if st.session_state[chave_sorteados]:
            st.markdown("#### Estudantes no Quadro:")
            cols = st.columns(len(st.session_state[chave_sorteados]))
            
            for idx, id_atual in enumerate(st.session_state[chave_sorteados]):
                with cols[idx]:
                    aluno_atual = next((a for a in st.session_state[chave_lista] if a["ID"] == id_atual), {})
                    aluno_db_match = alunos_roleta[alunos_roleta['ID'].apply(db.limpar_id) == id_atual]
                    aluno_db = aluno_db_match.iloc[0] if not aluno_db_match.empty else {}
                    
                    with st.container(border=True):
                        st.markdown(f"**{aluno_atual.get('Estudante', 'Estudante')}**")
                        st.caption(f"Perfil: {aluno_db.get('NECESSIDADES', 'TÍPICO')} | Chamadas: **{aluno_atual.get('Chamadas', 0)}**")
                        anotacao = st.text_area("Diagnóstico Rápido:", value=aluno_atual.get("Diagnóstico", ""), key=f"anotacao_{id_atual}_{v}", height=68)
                        
                        def registrar_arguicao(id_al, status_label, pontos, obs_padrao, anot):
                            obs_final = anot.strip() if anot.strip() else obs_padrao
                            for a in st.session_state[chave_lista]:
                                if a["ID"] == id_al:
                                    a["Situação"], a["Pontos"], a["Diagnóstico"] = status_label, pontos, obs_final
                                    break
                            nome_limpo = str(aluno_db.get('NOME_ALUNO', 'Estudante')).replace("♿ ", "").replace("👤 ", "").replace("🟠 ", "").replace("🧱 ", "").replace("🧮 ", "").replace("🚀 ", "")
                            
                            try:
                                wb_r = db.conectar()
                                ws_r = wb_r.worksheet("DB_DIARIO_BORDO")
                                dados_r = ws_r.get_all_values()
                                for i in range(len(dados_r)-1, 0, -1):
                                    if len(dados_r[i]) > 5 and dados_r[i][0] == data_roleta_str and db.limpar_id(dados_r[i][1]) == id_al and "ARGUIÇÃO" in dados_r[i][5]: 
                                        ws_r.delete_rows(i+1)
                                ws_r.append_row([data_roleta_str, id_al, nome_limpo, t_roleta, "TRUE", "ARGUIÇÃO", f"Quadro Negro: {obs_final}", util.sosa_to_str(pontos)], value_input_option="USER_ENTERED")
                                st.cache_data.clear()
                            except: pass
                            st.session_state[chave_sorteados].remove(id_al)
                        
                        if st.button(f"Dominou (+{pt_acerto})", key=f"btn_dom_{id_atual}_{v}", use_container_width=True): 
                            registrar_arguicao(id_atual, "Dominou", pt_acerto, "Resolveu corretamente no quadro.", anotacao); st.rerun()
                        if st.button("Participou (0.0)", key=f"btn_ten_{id_atual}_{v}", use_container_width=True): 
                            registrar_arguicao(id_atual, "Participou", 0.0, "Demonstrou raciocínio em desenvolvimento.", anotacao); st.rerun()
                        if st.button(f"Recusou ({pt_recusa})", key=f"btn_rec_{id_atual}_{v}", use_container_width=True): 
                            registrar_arguicao(id_atual, "Recusou", pt_recusa, "Recusa de participação.", anotacao); st.rerun()
                        if st.button("Pular / Isento", key=f"btn_pul_{id_atual}_{v}", use_container_width=True):
                            for a in st.session_state[chave_lista]:
                                if a["ID"] == id_atual: a["Situação"] = "Ausente/Isento"
                            st.session_state[chave_sorteados].remove(id_atual); st.rerun()

        st.markdown("---")
        with st.expander("Histórico Completo da Classe na Arguição"):
            st.data_editor(
                pd.DataFrame(st.session_state[chave_lista]), hide_index=True, use_container_width=True, height=280,
                column_config={"ID": None, "Estudante": st.column_config.TextColumn(disabled=True), "Situação": st.column_config.TextColumn(disabled=True), "Pontos": st.column_config.NumberColumn(disabled=True), "Chamadas": st.column_config.NumberColumn("Vezes Chamado", disabled=True)},
                key=f"ed_rol_{t_roleta}_{data_roleta_str}_{v}"
            )

    @st.dialog("Registrar Dia Não Letivo / Feriado")
    def dialog_dia_nao_letivo(t_foco):
        st.caption("Registre feriados, paralisações institucionais ou conselhos de classe:")
        data_nl = st.date_input("Data do Evento:", date.today(), format="DD/MM/YYYY", key=f"nl_dt_{v}")
        motivo_nl = st.text_input("Descrição:", placeholder="Ex: Conselho de Classe / Feriado Municipal", key=f"nl_mot_{v}")
        
        if st.button("Confirmar Registro de Inatividade", type="primary", use_container_width=True, key=f"btn_conf_nl_{v}"):
            if motivo_nl:
                data_nl_str = data_nl.strftime("%d/%m/%Y")
                db.limpar_diario_data_turma(data_nl_str, t_foco)
                db.excluir_aula_aberta(data_nl_str, t_foco)
                db.salvar_no_banco("DB_DIARIO_BORDO", [data_nl_str, "GLOBAL", "TODOS OS ALUNOS", t_foco, "ISENTO", "DIA NÃO LETIVO", motivo_nl, "0,00"])
                db.salvar_no_banco("DB_REGISTRO_AULAS", [data_nl_str, "AVULSA", t_foco, f"DIA NÃO LETIVO: {motivo_nl}", "N/A", "N/A", "NÃO LETIVO", "", ""])
                st.success(f"Dia {data_nl_str} registrado como Não Letivo!"); time.sleep(0.8); st.rerun()
            else: st.error("Digite o motivo do dia não letivo.")

    if not lista_turmas_segura:
        st.warning("Nenhuma turma cadastrada. Cadastre as turmas na aba de Secretaria.")
    else:
        hoje_dt = date.today()
        if hoje_dt <= date(2026, 5, 22): trim_detectado = "I Trimestre"
        elif hoje_dt <= date(2026, 9, 4): trim_detectado = "II Trimestre"
        else: trim_detectado = "III Trimestre"

        with st.container(border=True):
            c_head1, c_head2 = st.columns([1.5, 2])
            turma_foco = c_head1.selectbox("Turma:", lista_turmas_segura, key=f"foco_t_{v}")
            
            trim_ativo_gestao = c_head2.segmented_control(
                "Trimestre Ativo:",
                ["I Trimestre", "II Trimestre", "III Trimestre"],
                default=trim_detectado,
                key=f"seg_trim_gestao_{v}"
            )
            if not trim_ativo_gestao: trim_ativo_gestao = trim_detectado

            aulas_dadas_trim = 0
            if not df_registro_aulas.empty and 'TURMA' in df_registro_aulas.columns and 'STATUS_CURRICULO' in df_registro_aulas.columns:
                aulas_dadas_trim = df_registro_aulas[(df_registro_aulas['TURMA'] == turma_foco) & (df_registro_aulas['STATUS_CURRICULO'] != "NÃO LETIVO")]['DATA'].nunique()
            
            aulas_meta_trim = 32
            perc_safra = min(100.0, (aulas_dadas_trim / aulas_meta_trim) * 100) if aulas_meta_trim > 0 else 0
            st.caption(f"Safra de Aulas ({trim_ativo_gestao}): **{aulas_dadas_trim} de {aulas_meta_trim}** Aulas Ministradas ({perc_safra:.0f}%)")

        df_alunos_base_t = df_alunos[df_alunos['TURMA'] == turma_foco].copy() if not df_alunos.empty else pd.DataFrame()
        if 'STATUS' not in df_alunos_base_t.columns: df_alunos_base_t['STATUS'] = "ATIVO"
        alunos_t = df_alunos_base_t[~df_alunos_base_t['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].sort_values(by="NOME_ALUNO")
        
        ano_num = "".join(filter(str.isdigit, turma_foco))
        ano_str_ref = f"{ano_num}º"

        df_p_atual = df_planos[df_planos['ANO'] == ano_str_ref].copy() if not df_planos.empty and 'ANO' in df_planos.columns else pd.DataFrame()
        df_mats_ano = df_aulas[df_aulas['ANO'].str.contains(ano_num)].iloc[::-1] if not df_aulas.empty and 'ANO' in df_aulas.columns else pd.DataFrame()
        historico_turma = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco].copy() if not df_registro_aulas.empty and 'TURMA' in df_registro_aulas.columns else pd.DataFrame()

        df_d_foco = df_diario[df_diario['TURMA'] == turma_foco] if not df_diario.empty else pd.DataFrame()
        df_n_foco = df_notas[(df_notas['TURMA'] == turma_foco) & (df_notas['TRIMESTRE'] == trim_ativo_gestao)] if not df_notas.empty else pd.DataFrame()
        
        cnt_uti = 0
        cnt_evasao = 0
        cnt_atestados = 0
        
        if not df_n_foco.empty and 'MEDIA_FINAL' in df_n_foco.columns:
            cnt_uti = len(df_n_foco[df_n_foco['MEDIA_FINAL'].apply(util.sosa_to_float) < 6.0])
            
        if not df_d_foco.empty and 'TAGS' in df_d_foco.columns:
            df_validas_ev = df_d_foco[~df_d_foco['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])]
            tot_dias_ev = df_validas_ev['DATA'].nunique() if not df_validas_ev.empty else 1
            if tot_dias_ev == 0: tot_dias_ev = 1
            
            faltas_por_aluno = df_validas_ev[df_validas_ev['TAGS'] == "AUSÊNCIA"].groupby('NOME_ALUNO').size()
            cnt_evasao = sum(1 for f_c in faltas_por_aluno if (f_c / tot_dias_ev) >= 0.20)

        if not df_relatorios.empty and 'TIPO' in df_relatorios.columns and 'CONTEUDO' in df_relatorios.columns:
            cnt_atestados = len(df_relatorios[(df_relatorios['TIPO'] == 'JUSTIFICATIVA_AUSENCIA') & (df_relatorios['CONTEUDO'].astype(str).str.contains(turma_foco, na=False))])

        if cnt_uti > 0 or cnt_evasao > 0 or cnt_atestados > 0:
            with st.container(border=True):
                st.markdown("##### Indicadores de Atenção da Turma")
                c_al1, c_al2, c_al3 = st.columns(3)
                
                if cnt_evasao > 0: c_al1.error(f"Risco de Faltas: **{cnt_evasao} estudante(s)** (≥ 20% ausências)")
                else: c_al1.success("Frequência regular")

                if cnt_uti > 0: c_al2.warning(f"Abaixo da Média: **{cnt_uti} estudante(s)** (< 6.0)")
                else: c_al2.success("Média consolidada")

                if cnt_atestados > 0: c_al3.info(f"Atestados / 2ª Chamada: **{cnt_atestados} pendente(s)**")
                else: c_al3.caption("Sem atestados pendentes")

        visao_gestao_sel = st.segmented_control(
            "Central de Gestão:",
            ["Diário de Classe & Operação", "Radiografia Analítica da Turma", "Secretaria & Calendário"],
            default="Diário de Classe & Operação",
            key=f"seg_gestao_hub_{v}"
        )
        st.markdown("<br>", unsafe_allow_html=True)

        @st.fragment
        def renderizar_cockpit_gestao_fragmento():
            
            # VISÃO 1: DIÁRIO DE CLASSE & OPERAÇÃO
            if visao_gestao_sel == "Diário de Classe & Operação":
                c_top_act1, c_top_act2, c_top_act3 = st.columns([2, 1, 1])
                c_top_act1.markdown("#### Diário de Classe & Frequência")
                if c_top_act2.button("Roleta de Arguição", use_container_width=True, key=f"btn_open_rol_hub_{v}"):
                    dialog_roleta(turma_foco)
                if c_top_act3.button("Dia Não Letivo", use_container_width=True, key=f"btn_open_nl_hub_{v}"):
                    dialog_dia_nao_letivo(turma_foco)

                df_d_turma_maq = df_diario[(df_diario['TURMA'] == turma_foco) & (~df_diario['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"]))] if not df_diario.empty else pd.DataFrame()
                datas_historico_ordenadas = sorted(df_d_turma_maq['DATA'].unique(), key=lambda x: datetime.strptime(x, "%d/%m/%Y"), reverse=True) if not df_d_turma_maq.empty else []

                hoje_str = date.today().strftime("%d/%m/%Y")
                ultima_aula_str = datas_historico_ordenadas[0] if datas_historico_ordenadas else hoje_str

                with st.container(border=True):
                    c_time1, c_time2 = st.columns([1.5, 2])
                    
                    modo_data_timeline = c_time1.pills(
                        "Data da Aula:",
                        [f"Aula de Hoje ({hoje_str})", f"Última Aula ({ultima_aula_str})", "Outra Data"],
                        default=f"Aula de Hoje ({hoje_str})" if hoje_str in datas_historico_ordenadas or not datas_historico_ordenadas else f"Última Aula ({ultima_aula_str})",
                        key=f"pills_timeline_{v}"
                    )

                    if "Hoje" in modo_data_timeline:
                        data_ativa_str = hoje_str
                    elif "Última" in modo_data_timeline:
                        data_ativa_str = ultima_aula_str
                    else:
                        dt_pick = c_time2.date_input("Escolha a Data:", date.today(), format="DD/MM/YYYY", key=f"dt_pick_timeline_{v}")
                        data_ativa_str = dt_pick.strftime("%d/%m/%Y")

                    aula_info_ativa = historico_turma[historico_turma['DATA'] == data_ativa_str] if not historico_turma.empty else pd.DataFrame()
                    aula_aberta_existe = not aula_info_ativa.empty

                    if aula_aberta_existe:
                        cont_aula_ativa = str(aula_info_ativa.iloc[0].get('CONTEUDO_MINISTRADO', 'Registro de Sala'))
                        stat_aula_ativa = str(aula_info_ativa.iloc[0].get('STATUS_EXECUCAO', 'Concluído'))
                        st.caption(f"Aula ({data_ativa_str}): **{cont_aula_ativa}** • Status: `{stat_aula_ativa}`")
                    else:
                        st.info(f"Aula de {data_ativa_str} pronta para lançamento de presença e vistos.")

                if not aula_aberta_existe:
                    with st.expander("Vincular Material de Aula do Acervo", expanded=False):
                        mats_disp_bruto = df_mats_ano['TIPO_MATERIAL'].tolist() if not df_mats_ano.empty and 'TIPO_MATERIAL' in df_mats_ano.columns else []
                        mats_sel_abertura = st.multiselect("Material do Acervo:", options=mats_disp_bruto, max_selections=2, key=f"ms_mat_ab_{v}")
                        
                        if st.button("Confirmar Vínculo da Aula", type="primary", use_container_width=True, key=f"btn_abrir_aula_tl_{v}"):
                            if mats_sel_abertura:
                                mat_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == mats_sel_abertura[0]].iloc[0] if not df_aulas.empty else {}
                                sem_ref_val = mat_ref.get('SEMANA_REF', 'AVULSA') if isinstance(mat_ref, pd.Series) else 'AVULSA'
                                db.excluir_aula_aberta(data_ativa_str, turma_foco)
                                db.salvar_no_banco("DB_REGISTRO_AULAS", [data_ativa_str, sem_ref_val, turma_foco, " + ".join(mats_sel_abertura), "PENDENTE", "ABERTA"])
                                st.success("Aula vinculada com sucesso!"); time.sleep(0.5); st.rerun()

                st.markdown(f"##### Chamada & Vistos — {data_ativa_str}")
                
                diario_dia_ativo = df_diario[(df_diario['DATA'] == data_ativa_str) & (df_diario['TURMA'] == turma_foco)] if not df_diario.empty else pd.DataFrame()
                
                grid_chamada_dia = []
                ids_ausentes_dia = set()
                ids_vistos_dia = set()

                for _, al_c in alunos_t.iterrows():
                    id_al_c = db.limpar_id(al_c.get('ID', ''))
                    nome_al_c = str(al_c.get('NOME_ALUNO', 'Estudante'))
                    reg_dia = diario_dia_ativo[diario_dia_ativo['ID_ALUNO'].apply(db.limpar_id) == id_al_c] if not diario_dia_ativo.empty else pd.DataFrame()

                    is_p_c = True
                    is_v_c = False
                    tag_c = ""
                    obs_c = ""

                    if not reg_dia.empty:
                        tag_c = str(reg_dia.iloc[-1].get('TAGS', ''))
                        visto_raw = str(reg_dia.iloc[-1].get('VISTO_ATIVIDADE', '')).upper()
                        obs_c = str(reg_dia.iloc[-1].get('OBSERVACOES', ''))

                        if tag_c == "AUSÊNCIA":
                            is_p_c = False
                            ids_ausentes_dia.add(id_al_c)
                        else:
                            is_p_c = True

                        if visto_raw == "TRUE":
                            is_v_c = True
                            ids_vistos_dia.add(id_al_c)

                    grid_chamada_dia.append({
                        "ID": id_al_c,
                        "Estudante": nome_al_c,
                        "Presente": is_p_c,
                        "Visto OK": is_v_c,
                        "Ocorrência": tag_c if tag_c != "AUSÊNCIA" else "",
                        "Observação": obs_c
                    })

                key_grid_active = f"ed_grid_chamada_tl_{data_ativa_str}_{turma_foco}_{v}"
                
                df_chamada_editada = st.data_editor(
                    pd.DataFrame(grid_chamada_dia), hide_index=True, use_container_width=True, height=310,
                    column_config={
                        "ID": None,
                        "Estudante": st.column_config.TextColumn("Estudante", disabled=True, width="medium"),
                        "Presente": st.column_config.CheckboxColumn("Presente", default=True, width="small"),
                        "Visto OK": st.column_config.CheckboxColumn("Visto OK", default=False, width="small"),
                        "Ocorrência": st.column_config.SelectboxColumn("Ocorrência", options=["", "ARGUIÇÃO", "INDISCIPLINA", "CELULAR", "CONVERSA", "ATRASO", "DESTAQUE"], width="medium"),
                        "Observação": st.column_config.TextColumn("Observação Rápida", width="large")
                    },
                    key=key_grid_active
                )

                c_save_ch1, c_save_ch2 = st.columns(2)
                
                if c_save_ch1.button("Consolidar Diário desta Aula", type="primary", use_container_width=True, key=f"btn_save_diario_tl_{v}"):
                    with st.spinner("Gravando presenças, vistos e ocorrências..."):
                        linhas_diario_save = []
                        tot_vistos_dados = sum(1 for _, r_c in df_chamada_editada.iterrows() if r_c['Visto OK'] and r_c['Presente'])

                        for _, r_c in df_chamada_editada.iterrows():
                            al_id_c = r_c['ID']
                            nome_c = r_c['Estudante']
                            p_c = r_c['Presente']
                            v_c = r_c['Visto OK']
                            t_c = str(r_c['Ocorrência']).strip()
                            o_c = str(r_c['Observação']).strip()

                            bônus_c = "0,00"
                            if "DESTAQUE" in t_c or "+0.5" in t_c: bônus_c = "0,50"
                            elif "INDISCIPLINA" in t_c or "-0.5" in t_c: bônus_c = "-0,50"

                            if not p_c:
                                tag_final = "AUSÊNCIA"
                                visto_final = "FALSE"
                            else:
                                tag_final = t_c
                                visto_final = "ISENTO" if tot_vistos_dados == 0 else ("TRUE" if v_c else "FALSE")

                            linhas_diario_save.append([data_ativa_str, al_id_c, nome_c, turma_foco, visto_final, tag_final, o_c, bônus_c])

                        if linhas_diario_save:
                            db.limpar_diario_data_turma(data_ativa_str, turma_foco)
                            db.salvar_lote("DB_DIARIO_BORDO", linhas_diario_save)
                            st.toast(f"Diário de {data_ativa_str} consolidado com sucesso!", icon="✅")
                            time.sleep(0.5); st.rerun()

                st.markdown("---")
                qtd_ausentes_hoje = len(ids_ausentes_dia)

                with st.container(border=True):
                    c_rad1, c_rad2 = st.columns([2, 1])
                    c_rad1.markdown(f"##### Radar de Ausências — {data_ativa_str} ({qtd_ausentes_hoje} ausentes)")
                    c_rad1.caption("Retifique ausências diretamente sem necessidade de reabrir a chamada:")

                    if qtd_ausentes_hoje == 0:
                        st.success("100% de presença registrada nesta aula.")
                    else:
                        alunos_faltosos_df = alunos_t[alunos_t['ID'].apply(db.limpar_id).isin(ids_ausentes_dia)]
                        
                        for _, r_fal in alunos_faltosos_df.iterrows():
                            id_fal_al = db.limpar_id(r_fal.get('ID', ''))
                            nome_fal_al = str(r_fal.get('NOME_ALUNO', 'Estudante'))
                            
                            with st.container(border=True):
                                c_fal1, c_fal2 = st.columns([3, 1])
                                c_fal1.markdown(f"**{nome_fal_al}**")
                                c_fal1.caption(f"ID: `{id_fal_al}` | Perfil: {r_fal.get('NECESSIDADES', 'TÍPICO')}")
                                
                                if c_fal2.button("Retificar Presença", key=f"btn_quick_pres_{id_fal_al}_{data_ativa_str}_{v}", use_container_width=True):
                                    db.salvar_no_banco("DB_DIARIO_BORDO", [
                                        data_ativa_str, id_fal_al, nome_fal_al, turma_foco, "TRUE", "", "[PRESENÇA RETIFICADA]", "0,00"
                                    ])
                                    st.toast(f"Presença atribuída a {nome_fal_al}!")
                                    time.sleep(0.5); st.rerun()

                        lista_faltas_formatadas = [f"• {r.get('NOME_ALUNO', 'Estudante')}" for _, r in alunos_faltosos_df.iterrows()]
                        txt_copia_zap = f"AUSÊNCIAS ({turma_foco}) — AULA DE {data_ativa_str}:\n" + "\n".join(lista_faltas_formatadas)
                        
                        with st.expander("Copiar Lista de Ausências para WhatsApp"):
                            st.code(txt_copia_zap, language=None)

            # VISÃO 2: RADIOGRAFIA ANALÍTICA DA TURMA
            elif visao_gestao_sel == "Radiografia Analítica da Turma":
                st.markdown("#### Radiografia Analítica & Proficiência SAEB")
                
                df_d_rad = df_diario[df_diario['TURMA'] == turma_foco].copy() if not df_diario.empty else pd.DataFrame()
                df_n_rad = df_notas[(df_notas['TURMA'] == turma_foco) & (df_notas['TRIMESTRE'] == trim_ativo_gestao)].copy() if not df_notas.empty else pd.DataFrame()

                taxa_assiduidade, taxa_vistos, media_geral_turma = 0.0, 0.0, 0.0
                
                if not df_d_rad.empty and 'TAGS' in df_d_rad.columns:
                    tags_bloqueadas = ["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA", "RECESSO", "FERIADO"]
                    df_d_validas = df_d_rad[~df_d_rad['TAGS'].isin(tags_bloqueadas)]
                    tot_reg = len(df_d_validas)
                    faltas_tot = len(df_d_validas[df_d_validas['TAGS'] == "AUSÊNCIA"])
                    taxa_assiduidade = ((tot_reg - faltas_tot) / tot_reg) * 100 if tot_reg > 0 else 100
                    
                    df_v_val = df_d_validas[df_d_validas.get('VISTO_ATIVIDADE', '').astype(str).str.upper() != "ISENTO"]
                    tot_v_poss = len(df_v_val)
                    v_dados = len(df_v_val[df_v_val.get('VISTO_ATIVIDADE', '').astype(str).str.upper() == "TRUE"])
                    taxa_vistos = (v_dados / tot_v_poss) * 100 if tot_v_poss > 0 else 0

                if not df_n_rad.empty and 'MEDIA_FINAL' in df_n_rad.columns:
                    media_geral_turma = df_n_rad['MEDIA_FINAL'].apply(util.sosa_to_float).mean()

                with st.container(border=True):
                    k_r1, k_r2, k_r3, k_r4 = st.columns(4)
                    k_r1.metric("Média Geral da Classe", f"{media_geral_turma:.1f} pts")
                    k_r2.metric("Assiduidade da Turma", f"{taxa_assiduidade:.1f}%")
                    k_r3.metric("Vistos de Caderno", f"{taxa_vistos:.1f}%")
                    k_r4.metric("Estudantes Ativos", len(alunos_t))

                st.markdown("---")
                st.markdown("##### Distribuição da Turma por Níveis de Proficiência (SAEB)")
                
                cnt_abaixo_basico = 0
                cnt_basico = 0
                cnt_proficiente = 0
                cnt_avancado = 0
                
                if not df_n_rad.empty and 'MEDIA_FINAL' in df_n_rad.columns:
                    for _, r_n in df_n_rad.iterrows():
                        m_val = util.sosa_to_float(r_n.get('MEDIA_FINAL', 0.0))
                        if m_val < 4.0: cnt_abaixo_basico += 1
                        elif m_val <= 5.5: cnt_basico += 1
                        elif m_val <= 8.0: cnt_proficiente += 1
                        else: cnt_avancado += 1

                tot_avaliados = max(len(df_n_rad), 1)
                dados_proficiencia = [
                    {"Nível SAEB": "Abaixo do Básico (< 4.0)", "Qtd": cnt_abaixo_basico, "%": (cnt_abaixo_basico / tot_avaliados) * 100},
                    {"Nível SAEB": "Básico (4.0 a 5.5)", "Qtd": cnt_basico, "%": (cnt_basico / tot_avaliados) * 100},
                    {"Nível SAEB": "Proficiente (6.0 a 8.0)", "Qtd": cnt_proficiente, "%": (cnt_proficiente / tot_avaliados) * 100},
                    {"Nível SAEB": "Avançado (> 8.0)", "Qtd": cnt_avancado, "%": (cnt_avancado / tot_avaliados) * 100}
                ]

                fig_prof = px.bar(
                    pd.DataFrame(dados_proficiencia), x="Nível SAEB", y="Qtd", text="Qtd",
                    color="Nível SAEB",
                    color_discrete_map={
                        "Abaixo do Básico (< 4.0)": "#E74C3C",
                        "Básico (4.0 a 5.5)": "#F1C40F",
                        "Proficiente (6.0 a 8.0)": "#2ECC71",
                        "Avançado (> 8.0)": "#2962FF"
                    }
                )
                fig_prof.update_layout(height=260, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
                st.plotly_chart(fig_prof, use_container_width=True)

                st.markdown("---")

                c_uti_col, c_eva_col = st.columns(2)

                with c_uti_col:
                    with st.container(border=True):
                        st.markdown("##### UTI Pedagógica (< 6.0)")
                        st.caption("Estudantes que necessitam de intervenção formativa:")
                        
                        alunos_uti_list = []
                        if not df_n_rad.empty:
                            for _, r_u in df_n_rad.iterrows():
                                m_u = util.sosa_to_float(r_u.get('MEDIA_FINAL', 0))
                                if m_u < 6.0:
                                    alunos_uti_list.append({
                                        "Estudante": str(r_u.get('NOME_ALUNO', 'Estudante')),
                                        "Média Atual": m_u,
                                        "Falta p/ 6.0": 6.0 - m_u
                                    })

                        if alunos_uti_list:
                            df_uti_view = pd.DataFrame(alunos_uti_list).sort_values(by="Média Atual")
                            st.dataframe(
                                df_uti_view, hide_index=True, use_container_width=True, height=220,
                                column_config={
                                    "Estudante": st.column_config.TextColumn(width="medium"),
                                    "Média Atual": st.column_config.NumberColumn(format="%.1f"),
                                    "Falta p/ 6.0": st.column_config.ProgressColumn("Diferença", format="%.1f", min_value=0.0, max_value=6.0)
                                }
                            )
                        else:
                            st.success("Nenhum estudante na UTI de notas neste trimestre.")

                with c_eva_col:
                    with st.container(border=True):
                        st.markdown("##### Radar de Faltas & Evasão")
                        st.caption("Estudantes com ausências acumuladas acima de 20%:")
                        
                        alunos_evasao_list = []
                        if not df_d_rad.empty and 'TAGS' in df_d_rad.columns:
                            dias_validos_ev = df_d_rad[~df_d_rad['TAGS'].isin(["DIA NÃO LETIVO", "BONUS_CONSELHO", "SISTEMA_NOTA"])]
                            tot_dias_let = dias_validos_ev['DATA'].nunique() if not dias_validos_ev.empty else 1
                            if tot_dias_let == 0: tot_dias_let = 1

                            for _, r_al in alunos_t.iterrows():
                                id_al_ev = db.limpar_id(r_al.get('ID', ''))
                                nome_al_ev = str(r_al.get('NOME_ALUNO', 'Estudante'))
                                
                                d_al_ev = dias_validos_ev[dias_validos_ev['ID_ALUNO'].apply(db.limpar_id) == id_al_ev]
                                faltas_c = len(d_al_ev[d_al_ev['TAGS'] == "AUSÊNCIA"])
                                perc_f = (faltas_c / tot_dias_let) * 100 if tot_dias_let > 0 else 0

                                if perc_f >= 20.0:
                                    alunos_evasao_list.append({
                                        "Estudante": nome_al_ev,
                                        "Faltas": faltas_c,
                                        "% Ausência": perc_f
                                    })

                        if alunos_evasao_list:
                            df_ev_view = pd.DataFrame(alunos_evasao_list).sort_values(by="% Ausência", ascending=False)
                            st.dataframe(
                                df_ev_view, hide_index=True, use_container_width=True, height=220,
                                column_config={
                                    "Estudante": st.column_config.TextColumn(width="medium"),
                                    "Faltas": st.column_config.NumberColumn(width="small"),
                                    "% Ausência": st.column_config.ProgressColumn("% Faltas", format="%.0f%%", min_value=0, max_value=100)
                                }
                            )
                        else:
                            st.success("Nenhum estudante em risco de frequência.")

                st.markdown("---")
                if st.button("Gerar Relatório para Coordenação (DOCX)", type="primary", use_container_width=True, key=f"btn_exp_coord_hub_{v}"):
                    with st.spinner("Compilando Ficha de Regência em Word A4..."):
                        dados_export_coord = []
                        for _, al_c in alunos_t.iterrows():
                            id_al_c = db.limpar_id(al_c.get('ID', ''))
                            nome_al_c = str(al_c.get('NOME_ALUNO', 'Estudante'))
                            
                            reg_n = df_n_rad[df_n_rad['ID_ALUNO'].apply(db.limpar_id) == id_al_c] if not df_n_rad.empty else pd.DataFrame()
                            m_final_c = util.sosa_to_float(reg_n.iloc[0].get('MEDIA_FINAL', '0,0')) if not reg_n.empty else 0.0
                            
                            faltas_al = 0
                            if not df_d_rad.empty and 'ID_ALUNO' in df_d_rad.columns and 'TAGS' in df_d_rad.columns:
                                d_al_sub = df_d_rad[df_d_rad['ID_ALUNO'].apply(db.limpar_id) == id_al_c]
                                faltas_al = len(d_al_sub[d_al_sub['TAGS'] == "AUSÊNCIA"])
                                
                            status_c = "Na Média" if m_final_c >= 6.0 else "Recomposição"
                            if faltas_al >= 10: status_c += " / Risco de Frequência"
                            
                            dados_export_coord.append({
                                "nome": nome_al_c,
                                "c1": f"{taxa_vistos:.0f}%",
                                "c2": "Sincronizado",
                                "c3": "Sincronizado",
                                "bonus": "0.0",
                                "media": f"{m_final_c:.1f}",
                                "status": status_c
                            })
                            
                        info_coord = {"turma": turma_foco, "trimestre": trim_ativo_gestao}
                        nome_arq_coord = f"RELATORIO_REGENCIA_{turma_foco.replace(' ','_')}_{trim_ativo_gestao.replace(' ','')}"
                        
                        doc_coord_stream = exporter.gerar_docx_etiquetas_notas(nome_arq_coord, dados_export_coord, info_coord)
                        link_coord_doc = db.subir_e_converter_para_google_docs(doc_coord_stream, nome_arq_coord, trimestre=trim_ativo_gestao, categoria=turma_foco, modo="PLANEJAMENTO")
                        
                        if "https" in link_coord_doc:
                            st.success("Ficha de Regência gerada com sucesso para a Coordenação!")
                            st.link_button("Abrir Relatório no Google Drive", link_coord_doc, type="primary", use_container_width=True)
                            st.balloons()

            # VISÃO 3: SECRETARIA & CALENDÁRIO
            else:
                st.markdown("#### Secretaria, Matrículas & Gestão de Calendário")
                
                modo_sec = st.segmented_control(
                    "Operação:",
                    ["Cadastro de Estudantes", "Edição em Cascata & Status", "Gestão de Semanas & Recessos", "Estrutura de Turmas & Horários"],
                    default="Cadastro de Estudantes",
                    key=f"pills_sec_sub_{v}"
                )
                st.markdown("---")

                if modo_sec == "Cadastro de Estudantes":
                    t_dest = st.selectbox("Turma de Destino:", lista_turmas_segura, key=f"dest_pov_hub_{v}")
                    if t_dest:
                        t1_man, t2_lote = st.tabs(["Cadastro Individual", "Importação em Lote (CSV)"])
                        
                        with t1_man:
                            with st.form("f_manual_povoar_hub"):
                                nome_a = st.text_input("Nome Completo do Estudante:").upper()
                                perfil_base = st.multiselect("Perfil / Acessibilidade:", ["TÍPICO", "TEA", "TDAH", "DISLEXIA", "DEF. INTELECTUAL", "TOD", "BAIXA VISÃO", "SURDEZ", "PEI - PENDENTE", "OUTRO"], default=["TÍPICO"])
                                if st.form_submit_button("Salvar Estudante"):
                                    if not nome_a: st.error("Informe o nome do estudante.")
                                    else:
                                        if "TÍPICO" in perfil_base and len(perfil_base) > 1: perfil_base.remove("TÍPICO")
                                        perfil_str = " + ".join(perfil_base) if perfil_base else "TÍPICO"
                                        if db.salvar_no_banco("DB_ALUNOS", [db.gerar_proximo_id(df_alunos), nome_a, t_dest, "ATIVO", perfil_str, "MANUAL"]):
                                            st.success(f"Estudante {nome_a} cadastrado com sucesso!"); st.rerun()

                        with t2_lote:
                            st.caption("Insira os dados no formato `NOME, PERFIL`. Nomes terminados em asterisco (*) serão detectados como PEI:")
                            texto_lote = st.text_area("Lista de Alunos:", height=160, placeholder="ADRIEL VINICIUS ALVES MARTINS,TÍPICO\nJOSE LEVI BRONZE SANTOS*,PEI - PENDENTE", key=f"txt_lote_hub_{v}")
                            if st.button("Processar Importação em Lote", type="primary", use_container_width=True, key=f"btn_lote_alu_hub_{v}"):
                                if texto_lote.strip():
                                    linhas = texto_lote.strip().split('\n')
                                    novos_alunos = []
                                    id_atual = db.gerar_proximo_id(df_alunos)
                                    for linha in linhas:
                                        if not linha.strip(): continue
                                        partes = linha.split(',')
                                        nome_bruto = partes[0].strip().upper()
                                        if "*" in nome_bruto: nome_limpo, perfil = nome_bruto.replace("*", "").strip(), "PEI - PENDENTE"
                                        else: nome_limpo, perfil = nome_bruto, partes[1].strip().upper() if len(partes) > 1 else "TÍPICO"
                                        novos_alunos.append([id_atual, nome_limpo, t_dest, "ATIVO", perfil, "LOTE"])
                                        id_atual += 1 
                                    if db.salvar_lote("DB_ALUNOS", novos_alunos):
                                        st.success(f"{len(novos_alunos)} estudantes importados com sucesso!")
                                        st.balloons(); time.sleep(0.8); st.rerun()

                elif modo_sec == "Edição em Cascata & Status":
                    t_origem = st.selectbox("Selecione a Turma:", lista_turmas_segura, key=f"orig_ed_hub_{v}")
                    if t_origem:
                        alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO") if not df_alunos.empty else pd.DataFrame()
                        if not alunos_opcoes.empty:
                            aluno_sel_nome = st.selectbox("Selecione o Estudante:", alunos_opcoes['NOME_ALUNO'].tolist(), key=f"alu_ed_hub_{v}")
                            dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
                            id_atual_ed = db.limpar_id(dados_atuais.get('ID', ''))
                            nome_atual_ed = str(dados_atuais.get('NOME_ALUNO', 'Estudante'))
                            nec_atual_ed = str(dados_atuais.get('NECESSIDADES', 'TÍPICO'))
                            
                            st.markdown("##### Diagnóstico Rápido em 1 Toque")
                            c_b1, c_b2, c_b3, c_b4 = st.columns(4)
                            if c_b1.button("Defasagem Leitura", use_container_width=True, key=f"btn_diag_dl_h_{v}"):
                                db.atualizar_aluno_cascata(id_atual_ed, nome_atual_ed, t_origem, "DEFASAGEM LEITURA"); st.rerun()
                            if c_b2.button("Defasagem Matemática", use_container_width=True, key=f"btn_diag_dm_h_{v}"):
                                db.atualizar_aluno_cascata(id_atual_ed, nome_atual_ed, t_origem, "DEFASAGEM MATEMÁTICA"); st.rerun()
                            if c_b3.button("Alta Performance", use_container_width=True, key=f"btn_diag_ap_h_{v}"):
                                db.atualizar_aluno_cascata(id_atual_ed, nome_atual_ed, t_origem, "ALTA PERFORMANCE"); st.rerun()
                            if c_b4.button("Perfil Típico (Limpar)", use_container_width=True, key=f"btn_diag_tip_h_{v}"):
                                db.atualizar_aluno_cascata(id_atual_ed, nome_atual_ed, t_origem, "TÍPICO"); st.rerun()
                            
                            st.markdown("---")
                            with st.form("form_edicao_cascata_hub"):
                                novo_nome = st.text_input("Nome Completo:", value=nome_atual_ed).upper()
                                nova_turma = st.selectbox("Turma:", lista_turmas_segura, index=lista_turmas_segura.index(t_origem) if t_origem in lista_turmas_segura else 0)
                                nova_nec = st.text_input("Necessidades / CIDs / PEI:", value=nec_atual_ed).upper()
                                
                                status_opcoes = ["ATIVO", "TRANSFERIDO", "EVADIDO", "INATIVO"]
                                status_atual_val = str(dados_atuais.get('STATUS', 'ATIVO')).upper()
                                idx_status = status_opcoes.index(status_atual_val) if status_atual_val in status_opcoes else 0
                                novo_status = st.selectbox("Status Regimental:", status_opcoes, index=idx_status)

                                if st.form_submit_button("Salvar Alterações em Cascata"):
                                    try:
                                        wb_al = db.conectar()
                                        ws_al = wb_al.worksheet("DB_ALUNOS")
                                        cell_al = ws_al.find(str(id_atual_ed))
                                        if cell_al:
                                            ws_al.update_cell(cell_al.row, 4, novo_status)
                                    except: pass

                                    if db.atualizar_aluno_cascata(id_atual_ed, novo_nome, nova_turma, nova_nec):
                                        st.success("Cadastro e histórico propagados com sucesso!"); time.sleep(0.6); st.rerun()

                elif modo_sec == "Gestão de Semanas & Recessos":
                    c_cal1, c_cal2 = st.columns([2, 1])
                    todas_semanas_cal = util.gerar_semanas()
                    semana_alvo_cal = c_cal1.selectbox("Semana:", todas_semanas_cal, key=f"cal_sem_sel_hub_{v}")
                    status_semana_cal = c_cal2.selectbox("Situação:", [
                        "Semana Letiva Normal",
                        "Recesso Escolar",
                        "Feriado Prolongado",
                        "Semana de Provas Globais",
                        "Jornada Pedagógica / Planejamento"
                    ], key=f"cal_stat_sel_hub_{v}")
                    
                    motivo_semana_cal = st.text_input("Descrição:", placeholder="Ex: Recesso Junino / Semana de Avaliações", key=f"cal_mot_hub_{v}")
                    
                    if st.button("Gravar Status no Calendário", type="primary", use_container_width=True, key=f"btn_save_cal_hub_{v}"):
                        sem_limpa_cal = semana_alvo_cal.split(" (")[0].strip()
                        db.excluir_registro("DB_RELATORIOS", f"CONFIG_SEMANA_{sem_limpa_cal}")
                        
                        db.salvar_no_banco("DB_RELATORIOS", [
                            datetime.now().strftime("%d/%m/%Y"), "GLOBAL", "SISTEMA", 
                            f"CONFIG_SEMANA_{sem_limpa_cal}", f"{status_semana_cal}|{motivo_semana_cal}"
                        ])
                        st.success(f"{sem_limpa_cal} configurada com sucesso!"); time.sleep(0.6); st.rerun()

                else:
                    with st.container(border=True):
                        c1, c2, c3 = st.columns(3)
                        ano_t_cad = c1.selectbox("Série:", [6, 7, 8, 9], index=0, key=f"ano_cad_hub_{v}")
                        letra_t_cad = c2.selectbox("Letra:", ["A", "B", "C", "D", "E"], key=f"letra_cad_hub_{v}")
                        turno_t_cad = c3.selectbox("Turno:", ["Matutino", "Vespertino", "Noturno"], key=f"turno_cad_hub_{v}")
                        sigla_final_cad = f"{ano_t_cad}ª {turno_t_cad[0].upper()}{letra_t_cad}"
                        nome_final_cad = f"{ano_t_cad}º Ano {letra_t_cad}"

                        dias_aula_cad = st.multiselect("Grade de Horários:", ["Segunda (1º Tempo)", "Segunda (2º Tempo)", "Terça (1º Tempo)", "Terça (2º Tempo)", "Quarta (1º Tempo)", "Quarta (2º Tempo)", "Quinta (1º Tempo)", "Quinta (2º Tempo)", "Sexta (1º Tempo)", "Sexta (2º Tempo)"], key=f"dias_cad_hub_{v}")
                        
                        if st.button("Alocar Turma na Grade", type="primary", use_container_width=True, key=f"btn_save_turma_hub_{v}"):
                            if dias_aula_cad:
                                if db.salvar_no_banco("DB_TURMAS", [sigla_final_cad, nome_final_cad, turno_t_cad, " / ".join(dias_aula_cad), "N/A", "ATIVO"]):
                                    st.success(f"Turma {sigla_final_cad} alocada com sucesso!"); time.sleep(0.6); st.rerun()

        renderizar_cockpit_gestao_fragmento()










# ==============================================================================
# MÓDULO: CENTRO DE COMANDO DA INCLUSÃO (PEI / PERFIL IA) - V2026.PRO_INFINITY
# (SINCRONIZAÇÃO GLOBAL DE ALUNO, MACRO-METAS PEDAGÓGICAS, EXPURGO DE RECESSO)
# ==============================================================================
elif menu == "♿ Relatórios PEI / Perfil IA":
    st.title("Centro de Comando da Inclusão (PEI / Perfil IA)")
    st.caption("Gestão curricular individualizada de MATEMÁTICA: triagem, pareceres de evolução, estudo de caso e PEI oficial da Prefeitura de Itabuna.")
    st.markdown("---")

    if "v_pei" not in st.session_state: 
        st.session_state.v_pei = int(time.time())
    v = st.session_state.v_pei

    # ==============================================================================
    # DIALOG OFICIAL DECLARADO NO TOPO DO MÓDULO (LEI #25)
    # ==============================================================================
    @st.dialog("Parecer Acolhedor para os Pais (WhatsApp)", width="large")
    def dialog_zap_parecer_modal(aluno_nome, trim_ativo, parecer_diag, parecer_dir):
        st.caption("Texto formatado para envio à família na reunião de pais:")
        msg_zap_pei = f"""Olá! Tudo bem? Aqui é o professor Ronaldo Gomes (Componente Curricular de Matemática). 🏫
Compartilho o Parecer Descritivo do(a) estudante {aluno_nome} referente ao {trim_ativo}.

📌 EVOLUÇÃO E DESEMPENHO NO TRIMESTRE:
{parecer_diag}

🎯 RECOMENDAÇÕES PEDAGÓGICAS:
{parecer_dir}

Qualquer dúvida, estou à disposição na escola! Um abraço! 🚀
Escola Municipal Flávio José Simões Costa"""
        st.code(msg_zap_pei, language=None)

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
        st.warning("Base de estudantes vazia. Cadastre os alunos na Gestão da Turma.")
    else:
        hoje_dt = date.today()
        if hoje_dt <= date(2026, 5, 22): trim_detectado = "I Trimestre"
        elif hoje_dt <= date(2026, 9, 4): trim_detectado = "II Trimestre"
        else: trim_detectado = "III Trimestre"

        turmas_reais_pei = df_turmas[~df_turmas['ID_TURMA'].isin(["PI", "PC", "AC", "HTPC", "OUTRO"])] if not df_turmas.empty else pd.DataFrame()
        lista_turmas = sorted(turmas_reais_pei['ID_TURMA'].unique()) if not turmas_reais_pei.empty else sorted(df_alunos['TURMA'].unique())
        
        # SELEÇÃO GLOBAL SINCRONIZADA: TURMA, TRIMESTRE E ESTUDANTE (LEI #6)
        with st.container(border=True):
            c_top1, c_top2, c_top3 = st.columns([1.2, 1.3, 2])
            turma_pei = c_top1.selectbox("Turma Selecionada:", lista_turmas, key="pei_turma_global_sel")
            
            trim_ativo_pei = c_top2.segmented_control(
                "Trimestre Ativo:",
                ["I Trimestre", "II Trimestre", "III Trimestre"],
                default=trim_detectado,
                key="pei_trim_global_sel"
            )
            if not trim_ativo_pei: trim_ativo_pei = trim_detectado

            df_turma_raw = df_alunos[df_alunos['TURMA'] == turma_pei].copy()
            if 'STATUS' not in df_turma_raw.columns: df_turma_raw['STATUS'] = "ATIVO"
            
            df_turma_foco = df_turma_raw[~df_turma_raw['STATUS'].astype(str).str.upper().isin(["INATIVO", "TRANSFERIDO", "EVADIDO", "DESISTENTE"])].copy()

            if df_turma_foco.empty:
                st.warning(f"Nenhum estudante ativo cadastrado na turma {turma_pei}.")
                st.stop()

            def elegivel_prova_adaptada_universal(nec_str):
                n = str(nec_str).upper().strip()
                if n in ["NENHUMA", "", "NAN", "TÍPICO", "TIPICO"]: return False
                tem_cid_medico = bool(re.search(r'\b[A-Z]\d{2}(?:\.\d+)?\b', n))
                tem_palavra_laudo = any(x in n for x in [
                    "LAUDO", "TEA", "TDAH", "DISLEXIA", "DEF", "SURDEZ", "CEGUEIRA", 
                    "TOD", "SÍNDROME", "SINDROME", "DOWN", "PEI", "PENDENTE", "SUSPEITA", 
                    "INVESTIGAÇÃO", "INVESTIGACAO", "ANÁLISE", "ANALISE", "AUTISMO"
                ])
                if ("DEFASAGEM" in n or "DIFICULDADE" in n) and (not tem_cid_medico) and (not tem_palavra_laudo): return False
                return True

            df_turma_foco['ELEGIVEL_PEI'] = df_turma_foco['NECESSIDADES'].apply(elegivel_prova_adaptada_universal)
            df_laudados = df_turma_foco[df_turma_foco['ELEGIVEL_PEI']].copy()
            df_defasagem = df_turma_foco[~df_turma_foco['ELEGIVEL_PEI']].copy()
            df_defasagem = df_defasagem[df_defasagem['NECESSIDADES'].astype(str).str.upper().str.contains("DEFASAGEM|DIFICULDADE", regex=True, na=False)]

            df_todos_estudantes_pei = pd.concat([df_laudados, df_defasagem]).drop_duplicates(subset=['ID']).sort_values(by="NOME_ALUNO") if not df_laudados.empty or not df_defasagem.empty else pd.DataFrame()

            if not df_todos_estudantes_pei.empty:
                aluno_global_nome = c_top3.selectbox("Estudante Foco do PEI:", df_todos_estudantes_pei['NOME_ALUNO'].tolist(), key="pei_aluno_global_synced")
                dados_aluno_global = df_todos_estudantes_pei[df_todos_estudantes_pei['NOME_ALUNO'] == aluno_global_nome].iloc[0]
                id_aluno_global = str(db.limpar_id(dados_aluno_global['ID']))
                perfil_aluno_global = str(dados_aluno_global['NECESSIDADES']).upper().strip()
            else:
                aluno_global_nome, id_aluno_global, perfil_aluno_global = "Nenhum Estudante", "", "TÍPICO"

        # INDICADORES DA TURMA
        qtd_n1 = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PEI N1", case=False, na=False)])
        qtd_n2 = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PEI N2", case=False, na=False)])
        qtd_n3 = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PEI N3", case=False, na=False)])
        qtd_pendentes_suspeitos = len(df_laudados[df_laudados['NECESSIDADES'].astype(str).str.contains("PENDENTE|SUSPEITA|INVESTIG", case=False, na=False)])

        with st.container(border=True):
            st.markdown(f"##### Indicadores de Acessibilidade ({turma_pei} • {trim_ativo_pei}) — Estudante em Foco: **{aluno_global_nome}**")
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Estudantes Ativos", len(df_turma_foco))
            k2.metric("Laudados / CIDs", len(df_laudados), f"{qtd_pendentes_suspeitos} em investigação")
            k3.metric("PEI Nível 1", qtd_n1)
            k4.metric("PEI Nível 2", qtd_n2)
            k5.metric("PEI Nível 3", qtd_n3)

        st.markdown("---")

        tab_matriz, tab_forja, tab_provas_pei, tab_curriculo = st.tabs([
            "Triagem & Níveis PEI", 
            "Dossiê Descritivo & Evolução", 
            "Parecer para os Pais",
            "Adaptação Curricular & PEI Oficial"
        ])

        # ==============================================================================
        # ABA 1: TRIAGEM DE NÍVEIS
        # ==============================================================================
        with tab_matriz:
            @st.fragment
            def renderizar_matriz_inclusao_fragmento():
                st.markdown("### Triagem de Níveis de Acessibilidade")
                st.caption("Defina o nível do caderno adaptado de cada estudante em 1 clique:")
                
                with st.container(border=True):
                    st.markdown("#### Grupo 1: Estudantes Laudados / CIDs / Suspeitos (Caderno Adaptado)")
                    st.caption("Adaptações inclusivas garantidas por lei:")
                    
                    if df_laudados.empty:
                        st.info("Nenhum estudante ativo com laudo médico ou investigação pendente cadastrado nesta turma.")
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
                                "Laudo / CID / Diagnóstico": r['PERFIL_BASE'],
                                "Nível do Caderno Adaptado": r['NIVEL_ATUAL']
                            })
                        
                        df_laudo_ed = st.data_editor(
                            pd.DataFrame(dados_matriz_laudo), hide_index=True, use_container_width=True,
                            column_config={
                                "ID": None,
                                "Estudante": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Laudo / CID / Diagnóstico": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Nível do Caderno Adaptado": st.column_config.SelectboxColumn(
                                    "Nível da Avaliação",
                                    options=["Pendente (Definir)", "Nível 1 (Apoio Leve)", "Nível 2 (Apoio Moderado)", "Nível 3 (Qualitativa)"],
                                    required=True, width="large"
                                )
                            }, key=f"matriz_laudo_ed_{v}"
                        )

                        if st.button("Salvar Níveis de Acessibilidade", type="primary", use_container_width=True, key=f"btn_save_matriz_pei_{v}"):
                            with st.spinner("Atualizando cadastro e sincronizando com o Scanner..."):
                                for _, r in df_laudo_ed.iterrows():
                                    nivel_sel = r["Nível do Caderno Adaptado"]
                                    tag_nivel = ""
                                    if "Nível 1" in nivel_sel: tag_nivel = " (PEI N1)"
                                    elif "Nível 2" in nivel_sel: tag_nivel = " (PEI N2)"
                                    elif "Nível 3" in nivel_sel: tag_nivel = " (PEI N3)"
                                    
                                    nova_nec = f"{r['Laudo / CID / Diagnóstico']}{tag_nivel}"
                                    db.atualizar_aluno_cascata(r['ID'], r['Estudante'], turma_pei, nova_nec)
                                
                                st.success("Níveis de acessibilidade salvos com sucesso!")
                                time.sleep(0.5); st.rerun()

                st.markdown("<br>", unsafe_allow_html=True)

                with st.container(border=True):
                    st.markdown("#### Grupo 2: Estudantes com Defasagem Pedagógica (Caderno Regular)")
                    st.caption("Estudantes sem diagnóstico clínico que realizam a Prova Regular com apoio formativo de sala:")
                    
                    if df_defasagem.empty:
                        st.info("Nenhum estudante identificado exclusivamente com defasagem pedagógica nesta turma.")
                    else:
                        dados_matriz_def = []
                        for _, r_d in df_defasagem.iterrows():
                            dados_matriz_def.append({
                                "Estudante": r_d['NOME_ALUNO'],
                                "Barreira Mapeada": r_d['NECESSIDADES'],
                                "Instrumento Avaliativo": "Caderno Regular (Sem Adaptação)"
                            })
                            
                        st.dataframe(
                            pd.DataFrame(dados_matriz_def), hide_index=True, use_container_width=True,
                            column_config={
                                "Estudante": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Barreira Mapeada": st.column_config.TextColumn(disabled=True, width="medium"),
                                "Instrumento Avaliativo": st.column_config.TextColumn(disabled=True, width="large")
                            }
                        )

            renderizar_matriz_inclusao_fragmento()

        # ==============================================================================
        # ABA 2: DOSSIÊ DESCRITIVO & EVOLUÇÃO (SINCRONIZADO COM A ALUNA SELECIONADA)
        # ==============================================================================
        with tab_forja:
            @st.fragment
            def renderizar_forja_dossie_fragmento():
                st.markdown(f"### Dossiê Descritivo & Evolução — **{aluno_global_nome}** ({trim_ativo_pei})")
                st.caption("Assinale as características observadas na aula de Matemática. A IA estruturará o parecer priorizando estritamente suas anotações reais:")
                
                if not id_aluno_global:
                    st.info("Nenhum estudante selecionado no topo do painel.")
                else:
                    key_gen_version = f"gen_v_{id_aluno_global}_{trim_ativo_pei}"
                    if key_gen_version not in st.session_state:
                        st.session_state[key_gen_version] = 0
                    v_gen = st.session_state[key_gen_version]

                    n_alu = df_notas[(df_notas['ID_ALUNO'].apply(db.limpar_id) == id_aluno_global) & (df_notas['TRIMESTRE'] == trim_ativo_pei)] if not df_notas.empty else pd.DataFrame()
                    if not n_alu.empty:
                        nota_c1 = util.sosa_to_float(n_alu.iloc[0]['NOTA_VISTOS'])
                        nota_c2 = util.sosa_to_float(n_alu.iloc[0]['NOTA_TESTE'])
                        nota_c3 = util.sosa_to_float(n_alu.iloc[0]['NOTA_PROVA'])
                        media_trim_f = util.sosa_to_float(n_alu.iloc[0]['MEDIA_FINAL'])
                        notas_str = f"Caderno (C1): {nota_c1:.1f} | Testes (C2): {nota_c2:.1f} | Prova (C3): {nota_c3:.1f} ➔ Média: {media_trim_f:.1f} pts"
                    else:
                        notas_str = f"Média em processo de consolidação no {trim_ativo_pei}."

                    if trim_ativo_pei == "I Trimestre": dt_i, dt_f = date(2026, 2, 9), date(2026, 5, 22)
                    elif trim_ativo_pei == "II Trimestre": dt_i, dt_f = date(2026, 5, 25), date(2026, 9, 4)
                    else: dt_i, dt_f = date(2026, 9, 8), date(2026, 12, 17)

                    ocorrencias_diario = []
                    faltas_cnt = 0
                    if not df_diario.empty:
                        d_alu = df_diario[(df_diario['ID_ALUNO'].apply(db.limpar_id) == id_aluno_global) & (df_diario['TURMA'] == turma_pei)].copy()
                        if not d_alu.empty:
                            d_alu['DATA_DT'] = pd.to_datetime(d_alu['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
                            d_alu_sub = d_alu[(d_alu['DATA_DT'] >= dt_i) & (d_alu['DATA_DT'] <= dt_f)]
                            faltas_cnt = len(d_alu_sub[d_alu_sub['TAGS'] == "AUSÊNCIA"])
                            
                            mask_oc = (d_alu_sub['TAGS'] != "") & (~d_alu_sub['TAGS'].isin(["DIA NÃO LETIVO", "SISTEMA_NOTA", "AUSÊNCIA"]))
                            for _, r_d in d_alu_sub[mask_oc].tail(5).iterrows():
                                ocorrencias_diario.append(f"• {r_d['DATA']}: {r_d['TAGS']} ({r_d['OBSERVACOES']})")

                    oc_str = "\n".join(ocorrencias_diario) if ocorrencias_diario else "Participação regular com acompanhamento mediado."

                    hist_aluno = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_aluno_global] if not df_relatorios.empty else pd.DataFrame()
                    texto_historico_anterior = ""
                    if trim_ativo_pei == "II Trimestre":
                        rel_ant = hist_aluno[hist_aluno['TIPO'] == "DOSSIE_PEI_I_TRIMESTRE"]
                        if not rel_ant.empty:
                            texto_historico_anterior = f"HISTÓRICO DO I TRIMESTRE: {str(rel_ant.iloc[-1]['CONTEUDO'])[:400]}"
                    elif trim_ativo_pei == "III Trimestre":
                        rel_ant2 = hist_aluno[hist_aluno['TIPO'] == "DOSSIE_PEI_II_TRIMESTRE"]
                        if not rel_ant2.empty:
                            texto_historico_anterior = f"HISTÓRICO DO II TRIMESTRE: {str(rel_ant2.iloc[-1]['CONTEUDO'])[:400]}"

                    with st.container(border=True):
                        st.markdown(f"##### Evidências Registradas ({aluno_global_nome} • {trim_ativo_pei})")
                        c_ctx1, c_ctx2 = st.columns([1.2, 1.8])
                        c_ctx1.info(f"**Rendimento em Matemática:**\n{notas_str}\n\n**Faltas no Período:** {faltas_cnt}")
                        c_ctx2.warning(f"**Atitude & Observações de Sala:**\n{oc_str}")

                    with st.container(border=True):
                        st.markdown(f"#### Painel Tátil de Observação: **{aluno_global_nome}**")
                        st.caption("Assinale as características observadas nas aulas de Matemática:")

                        c_chip1, c_chip2 = st.columns(2)
                        marcas_sociais = c_chip1.pills(
                            "Comportamento & Interação:",
                            ["Isolamento e Não Interage com Colegas", "Não Participa Espontaneamente das Aulas", "Bom Comportamento mas Passiva", "Necessita de Rotina Rígida", "Apresenta Estereotipias", "Sensibilidade a Ruídos / Agitação"],
                            selection_mode="multi",
                            default=["Isolamento e Não Interage com Colegas", "Não Participa Espontaneamente das Aulas", "Bom Comportamento mas Passiva"],
                            key=f"chips_soc_{id_aluno_global}_{trim_ativo_pei}"
                        )

                        marcas_comunicacao = c_chip2.pills(
                            "Comunicação na Aula:",
                            ["Comunicação Verbal Restrita / Rara", "Compreende Instruções Curtas", "Responde por Apontamento / Desenho", "Necessita de Apoio Visual / Concreto", "Comunicação Alternativa (PECs)"],
                            selection_mode="multi",
                            default=["Comunicação Verbal Restrita / Rara", "Compreende Instruções Curtas", "Necessita de Apoio Visual / Concreto"],
                            key=f"chips_com_{id_aluno_global}_{trim_ativo_pei}"
                        )

                        c_chip3, c_chip4 = st.columns(2)
                        marcas_matematica = c_chip3.pills(
                            "Prática Matemática & Tarefas:",
                            ["Dificilmente Apresenta Tarefas de Casa", "Dificuldade na Abstração sem Apoio", "Realiza Tarefas de Sala com Mediação Direta", "Autonomia com Material Concreto", "Uso Funcional da Calculadora", "Reconhece Numerais Básicos"],
                            selection_mode="multi",
                            default=["Dificilmente Apresenta Tarefas de Casa", "Dificuldade na Abstração sem Apoio", "Realiza Tarefas de Sala com Mediação Direta"],
                            key=f"chips_mat_{id_aluno_global}_{trim_ativo_pei}"
                        )

                        evolucao_selecionada = c_chip4.segmented_control(
                            "Evolução / Vínculo Pedagógico:",
                            ["Necessita de Reforço de Vínculo e Engajamento", "Desenvolvimento Estável / Em Processo", "Evolução Notória"],
                            default="Necessita de Reforço de Vínculo e Engajamento",
                            key=f"seg_evo_{id_aluno_global}_{trim_ativo_pei}"
                        )

                        micro_anotacao_prof = st.text_input(
                            "Anotação do Professor (Sua observação real em sala de aula):",
                            value="",
                            placeholder=f"Digite ou dite observações sobre {aluno_global_nome}...",
                            key=f"inp_micro_obs_{id_aluno_global}_{trim_ativo_pei}"
                        )

                        st.markdown("<br>", unsafe_allow_html=True)

                        if st.button(f"Estruturar Dossiê de {aluno_global_nome} com IA", type="primary", use_container_width=True, key=f"btn_ghost_auto_{id_aluno_global}_{trim_ativo_pei}"):
                            with st.spinner(f"A IA está redigindo o parecer técnico fiel de {aluno_global_nome}..."):
                                prompt_auto = (
                                    f"VOCÊ É O PSICOPEDAGOGO PERITO EM EDUCAÇÃO ESPECIAL (PREFEITURA DE ITABUNA).\n"
                                    f"ESTUDANTE: {aluno_global_nome} | TURMA: {turma_pei} | LAUDO: {perfil_aluno_global}\n"
                                    f"TRIMESTRE ATUAL: {trim_ativo_pei.upper()}\n\n"
                                    f"🚨 CLÁUSULA DE SOBERANIA PEDAGÓGICA (FIDELIDADE ABSOLUTA AO PROFESSOR):\n"
                                    f"O parecer DEVE retratar EXATAMENTE a realidade descrita pelo professor abaixo para {aluno_global_nome}. NÃO invente 'desenvolvimento excelente' se o docente apontou dificuldades!\n\n"
                                    f"--- OBSERVAÇÕES REAIS DO PROFESSOR DE MATEMÁTICA ---\n"
                                    f"• ANOTAÇÃO DIRETA DO DOCENTE: {micro_anotacao_prof if micro_anotacao_prof.strip() else 'A aluna apresenta bom comportamento em sala, porém postura passiva, baixa interação espontânea com colegas e resistência na entrega de tarefas de casa.'}\n"
                                    f"• STATUS DE EVOLUÇÃO INFORMADO: {evolucao_selecionada}\n"
                                    f"• COMPORTAMENTO / INTERAÇÃO: {', '.join(marcas_sociais)}\n"
                                    f"• COMUNICAÇÃO OBSERVADA: {', '.join(marcas_comunicacao)}\n"
                                    f"• PRÁTICA EM MATEMÁTICA / TAREFAS: {', '.join(marcas_matematica)}\n"
                                    f"• RENDIMENTO EM MATEMÁTICA: {notas_str} | FALTAS: {faltas_cnt}\n\n"
                                    f"--- HISTÓRICO ANTERIOR ---\n"
                                    f"{texto_historico_anterior if texto_historico_anterior else 'Início do acompanhamento.'}\n\n"
                                    f"DIRETRIZES DE REDAÇÃO:\n"
                                    f"1. No [DIAGNOSTICO_GERAL], cite nominalmente {aluno_global_nome}, retratando a realidade das anotações do professor com linguagem técnica.\n"
                                    f"2. Preencha CADA TAG separadamente, sem vazar tags dentro de outras:\n"
                                    f"[DIAGNOSTICO_GERAL] (Diagnóstico realista do {trim_ativo_pei})\n"
                                    f"[SOCIAIS] (Interação social e relação com os colegas nas aulas de Matemática)\n"
                                    f"[COMUNICATIVAS] (Comunicação na aula de Matemática e resposta aos comandos)\n"
                                    f"[EMOCIONAIS] (Comportamento, autorregulação e rotina)\n"
                                    f"[FUNCIONAIS] (Engajamento nas tarefas de sala e de casa)\n"
                                    f"[DIRETRIZES_CURRICULARES] (Recomendações e estratégias de apoio ao engajamento)"
                                )
                                res_ia = ai.gerar_ia("ESPECIALISTA_INCLUSAO", prompt_auto, usar_busca=False)
                                tipo_relatorio_chave = f"DOSSIE_PEI_{trim_ativo_pei.replace(' ', '_').upper()}"
                                salvar_relatorio_pei_sem_duplicidade(id_aluno_global, aluno_global_nome, tipo_relatorio_chave, res_ia)
                                
                                st.session_state[key_gen_version] = int(time.time())
                                st.success(f"Dossiê de {aluno_global_nome} gerado com sucesso!")
                                time.sleep(0.4)
                                st.rerun()

                    def extrair_bloco_puro(texto_completo, tag_alvo):
                        if not texto_completo: return ""
                        tags_todas = ["DIAGNOSTICO_GERAL", "SOCIAIS", "COMUNICATIVAS", "EMOCIONAIS", "FUNCIONAIS", "DIRETRIZES_CURRICULARES"]
                        outras = [t for t in tags_todas if t != tag_alvo]
                        stop_regex = "|".join([rf"\[\s*{t}\s*\]" for t in outras])
                        
                        padrao = rf"\[\s*{tag_alvo}\s*\]\s*[:\-]*\s*(.*?)(?={stop_regex}|$)"
                        m = re.search(padrao, texto_completo, re.DOTALL | re.IGNORECASE)
                        if m:
                            t_limpo = m.group(1).strip()
                            t_limpo = re.sub(r'\[\s*(?:' + '|'.join(tags_todas) + r')\s*\]', '', t_limpo, flags=re.IGNORECASE)
                            return t_limpo.strip()
                        return ""

                    tipo_relatorio_chave = f"DOSSIE_PEI_{trim_ativo_pei.replace(' ', '_').upper()}"
                    rel_master = hist_aluno[hist_aluno['TIPO'] == tipo_relatorio_chave] if not hist_aluno.empty else pd.DataFrame()
                    text_dossie_salvo = str(rel_master.iloc[-1]['CONTEUDO']) if not rel_master.empty else ""

                    st.markdown("---")
                    st.markdown(f"#### Parecer Descritivo de **{aluno_global_nome}** ({trim_ativo_pei})")

                    ed_diag = st.text_area("1. Diagnóstico Geral & Evolução no Trimestre:", extrair_bloco_puro(text_dossie_salvo, "DIAGNOSTICO_GERAL"), height=130, key=f"ed_diag_{id_aluno_global}_{trim_ativo_pei}_{v_gen}")
                    
                    c_h1, c_h2 = st.columns(2)
                    ed_soc = c_h1.text_area("2. Habilidades Sociais & Interação:", extrair_bloco_puro(text_dossie_salvo, "SOCIAIS"), height=85, key=f"ed_soc_{id_aluno_global}_{trim_ativo_pei}_{v_gen}")
                    ed_com = c_h2.text_area("3. Habilidades Comunicativas:", extrair_bloco_puro(text_dossie_salvo, "COMUNICATIVAS"), height=85, key=f"ed_com_{id_aluno_global}_{trim_ativo_pei}_{v_gen}")
                    ed_emo = c_h1.text_area("4. Habilidades Emocionais & Comportamento:", extrair_bloco_puro(text_dossie_salvo, "EMOCIONAIS"), height=85, key=f"ed_emo_{id_aluno_global}_{trim_ativo_pei}_{v_gen}")
                    ed_fun = c_h2.text_area("5. Habilidades Funcionais & Tarefas:", extrair_bloco_puro(text_dossie_salvo, "FUNCIONAIS"), height=85, key=f"ed_fun_{id_aluno_global}_{trim_ativo_pei}_{v_gen}")
                    
                    ed_dir = st.text_area("6. Diretrizes e Adaptações Recomendadas:", extrair_bloco_puro(text_dossie_salvo, "DIRETRIZES_CURRICULARES"), height=95, key=f"ed_dir_{id_aluno_global}_{trim_ativo_pei}_{v_gen}")
                    
                    if st.button("Salvar Dossiê Trimestral", type="primary", use_container_width=True, key=f"btn_save_man_dossie_{id_aluno_global}_{trim_ativo_pei}"):
                        texto_consolidado = f"[DIAGNOSTICO_GERAL]\n{ed_diag}\n\n[SOCIAIS]\n{ed_soc}\n\n[COMUNICATIVAS]\n{ed_com}\n\n[EMOCIONAIS]\n{ed_emo}\n\n[FUNCIONAIS]\n{ed_fun}\n\n[DIRETRIZES_CURRICULARES]\n{ed_dir}"
                        salvar_relatorio_pei_sem_duplicidade(id_aluno_global, aluno_global_nome, tipo_relatorio_chave, texto_consolidado)
                        st.success(f"Dossiê de {aluno_global_nome} salvo com sucesso!"); time.sleep(0.5); st.rerun()

            renderizar_forja_dossie_fragmento()

        # ==============================================================================
        # ABA 3: PARECER PARA OS PAIS (SINCRONIZADO COM DOWNLOAD .DOCX)
        # ==============================================================================
        with tab_provas_pei:
            @st.fragment
            def renderizar_parecer_pais_fragmento():
                st.markdown(f"### Parecer Descritivo para a Família — **{aluno_global_nome}** ({trim_ativo_pei})")
                st.caption("Exportação e download nativo do parecer descritivo em linguagem acolhedora.")
                
                if not id_aluno_global:
                    st.info("Nenhum estudante selecionado.")
                else:
                    tipo_relatorio_chave = f"DOSSIE_PEI_{trim_ativo_pei.replace(' ', '_').upper()}"
                    hist_p = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_aluno_global] if not df_relatorios.empty else pd.DataFrame()
                    rel_p = hist_p[hist_p['TIPO'] == tipo_relatorio_chave] if not hist_p.empty else pd.DataFrame()
                    
                    txt_p_salvo = str(rel_p.iloc[-1]['CONTEUDO']) if not rel_p.empty else ""
                    
                    def extrair_bloco_puro_par(texto_completo, tag_alvo):
                        if not texto_completo: return ""
                        tags_todas = ["DIAGNOSTICO_GERAL", "SOCIAIS", "COMUNICATIVAS", "EMOCIONAIS", "FUNCIONAIS", "DIRETRIZES_CURRICULARES"]
                        outras = [t for t in tags_todas if t != tag_alvo]
                        stop_regex = "|".join([rf"\[\s*{t}\s*\]" for t in outras])
                        m = re.search(rf"\[\s*{tag_alvo}\s*\]\s*[:\-]*\s*(.*?)(?={stop_regex}|$)", texto_completo, re.DOTALL | re.IGNORECASE)
                        return m.group(1).strip() if m else ""

                    p_diag = extrair_bloco_puro_par(txt_p_salvo, "DIAGNOSTICO_GERAL") or "Parecer ainda não preenchido para este período."
                    p_dir = extrair_bloco_puro_par(txt_p_salvo, "DIRETRIZES_CURRICULARES") or "Sem recomendações registradas."

                    texto_parecer_docx = (
                        f"PARECER DESCRITIVO DE ACOMPANHAMENTO PEDAGÓGICO - {trim_ativo_pei.upper()}\n\n"
                        f"Estudante: {aluno_global_nome} | Turma: {turma_pei} | Perfil: {perfil_aluno_global}\n\n"
                        f"1. AVALIAÇÃO DESCRITIVA DO DESEMPENHO EM MATEMÁTICA:\n{p_diag}\n\n"
                        f"2. RECOMENDAÇÕES E DIRETRIZES PEDAGÓGICAS:\n{p_dir}\n\n"
                        f"Prof. Ronaldo Gomes • Componente Curricular de Matemática"
                    )
                    nome_arq_parecer = f"PARECER_{aluno_global_nome.replace(' ','_')}_{trim_ativo_pei.replace(' ','')}"
                    doc_p = exporter.gerar_docx_aluno_v24(nome_arq_parecer, texto_parecer_docx, {"ano": turma_pei, "trimestre": trim_ativo_pei})
                    docx_bytes_par = doc_p.getvalue()

                    with st.container(border=True):
                        st.markdown(f"##### Prévia do Parecer de {aluno_global_nome}")
                        st.write(util.preparar_para_leitura(f"**Evolução:** {p_diag}"))
                        st.info(util.preparar_para_leitura(f"**Diretrizes:** {p_dir}"))

                    c_act1, c_act2 = st.columns(2)
                    
                    if c_act1.button("Abrir Texto para WhatsApp", use_container_width=True, key=f"btn_zap_par_{v}"):
                        dialog_zap_parecer_modal(aluno_global_nome, trim_ativo_pei, p_diag, p_dir)

                    c_act2.download_button(
                        label="📥 Baixar Parecer em Word (DOCX)",
                        data=docx_bytes_par,
                        file_name=f"{nome_arq_parecer}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        key=f"btn_dl_par_docx_{id_aluno_global}_{v}"
                    )

            renderizar_parecer_pais_fragmento()

        # ==============================================================================
        # ABA 4: CURRÍCULO ADAPTADO & PEI OFICIAL SOBERANO (MACRO-METAS & ANTI-REPETIÇÃO)
        # ==============================================================================
        with tab_curriculo:
            @st.fragment
            def renderizar_curriculo_exportacao_fragmento():
                st.markdown(f"### Adaptação Curricular & PEI Oficial — **{aluno_global_nome}**")
                st.caption("Planejamento curricular estruturado em MACRO-METAS por Eixo Temático com recursos concretos diversificados.")
                
                if not id_aluno_global:
                    st.info("Nenhum estudante selecionado.")
                else:
                    ano_aluno_num = "".join(filter(str.isdigit, turma_pei))

                    c_esc1, c_esc2 = st.columns([1.5, 1])
                    escopo_pei_doc = c_esc1.segmented_control(
                        "Escopo do Documento PEI:",
                        ["PEI do Trimestre Ativo", "PEI Anual Completo (I, II e III Tri)"],
                        default="PEI do Trimestre Ativo",
                        key=f"seg_escopo_pei_{v}"
                    )
                    
                    is_anual_pei = "Anual" in str(escopo_pei_doc)
                    
                    hist_exp = df_relatorios[df_relatorios['ID_ALUNO'].apply(db.limpar_id) == id_aluno_global] if not df_relatorios.empty else pd.DataFrame()
                    rel_master_exp = hist_exp[hist_exp['TIPO'].str.contains("DOSSIE_PEI", na=False)] if not hist_exp.empty else pd.DataFrame()
                    
                    v_diag_exp = ""
                    v_soc_exp = "Interage com apoio do mediador nas atividades em grupo."
                    v_com_exp = "Comunicação funcional com suporte visual e comandos curtos."
                    v_emo_exp = "Necessita de rotina estruturada para manutenção da estabilidade."
                    v_fun_exp = "Execução de tarefas de Matemática com mediação passo a passo no papel."
                    v_diretrizes_exp = "Uso de recursos concretos diversificados, calculadora, malhas e esquemas visuais."

                    if not rel_master_exp.empty:
                        txt_dossie_bruto = str(rel_master_exp.iloc[-1]['CONTEUDO'])
                        
                        def extrair_bloco_puro_curr(texto_completo, tag_alvo):
                            if not texto_completo: return ""
                            tags_todas = ["DIAGNOSTICO_GERAL", "SOCIAIS", "COMUNICATIVAS", "EMOCIONAIS", "FUNCIONAIS", "DIRETRIZES_CURRICULARES"]
                            outras = [t for t in tags_todas if t != tag_alvo]
                            stop_regex = "|".join([rf"\[\s*{t}\s*\]" for t in outras])
                            m = re.search(rf"\[\s*{tag_alvo}\s*\]\s*[:\-]*\s*(.*?)(?={stop_regex}|$)", texto_completo, re.DOTALL | re.IGNORECASE)
                            return m.group(1).strip() if m else ""

                        v_diag_exp = extrair_bloco_puro_curr(txt_dossie_bruto, "DIAGNOSTICO_GERAL")
                        if extrair_bloco_puro_curr(txt_dossie_bruto, "SOCIAIS"): v_soc_exp = extrair_bloco_puro_curr(txt_dossie_bruto, "SOCIAIS")
                        if extrair_bloco_puro_curr(txt_dossie_bruto, "COMUNICATIVAS"): v_com_exp = extrair_bloco_puro_curr(txt_dossie_bruto, "COMUNICATIVAS")
                        if extrair_bloco_puro_curr(txt_dossie_bruto, "EMOCIONAIS"): v_emo_exp = extrair_bloco_puro_curr(txt_dossie_bruto, "EMOCIONAIS")
                        if extrair_bloco_puro_curr(txt_dossie_bruto, "FUNCIONAIS"): v_fun_exp = extrair_bloco_puro_curr(txt_dossie_bruto, "FUNCIONAIS")
                        if extrair_bloco_puro_curr(txt_dossie_bruto, "DIRETRIZES_CURRICULARES"): v_diretrizes_exp = extrair_bloco_puro_curr(txt_dossie_bruto, "DIRETRIZES_CURRICULARES")

                    chave_tabela_curr = f"CURRICULO_ADAPTADO_ANUAL_{id_aluno_global}" if is_anual_pei else f"CURRICULO_ADAPTADO_{trim_ativo_pei}_{id_aluno_global}"
                    curr_records = hist_exp[hist_exp['TIPO'] == chave_tabela_curr] if not hist_exp.empty else pd.DataFrame()
                    
                    if not curr_records.empty:
                        try: 
                            df_curr_atual = pd.read_json(io.StringIO(curr_records.iloc[-1]['CONTEUDO']), orient='records')
                        except: 
                            df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])
                    else: 
                        df_curr_atual = pd.DataFrame(columns=["Objetivos de Aprendizagem", "Estratégias Metodológicas", "Recursos Materiais"])

                    with st.popover("Adaptar Conteúdos Curriculares com IA"):
                        st.caption(f"Selecione os eixos curriculares para gerar as MACRO-METAS adaptadas ({escopo_pei_doc}):")
                        
                        TERMOS_EXPURGO = r"(?i)(?:RECESSO|FERIADO|JORNADA|SEM\s+ATIVIDADES|N/A|APLICAÇÃO\s+DE\s+EXAME|AVALIAÇÃO_\d+|CONCLUIDO_)"
                        
                        opcoes_curriculo_limpas = []
                        
                        if not df_planos.empty and 'ANO' in df_planos.columns and 'TURMA' in df_planos.columns:
                            mask_p = (df_planos['ANO'].astype(str).str.contains(ano_aluno_num))
                            if not is_anual_pei: mask_p = mask_p & (df_planos['TURMA'] == trim_ativo_pei)
                            planos_da_turma = df_planos[mask_p]
                            
                            for _, r_plano in planos_da_turma.iterrows():
                                sem_lbl = r_plano.get('SEMANA', 'Semana')
                                txt_plano_item = str(r_plano.get('PLANO_TEXTO', ''))
                                obj_item = ai.extrair_tag(txt_plano_item, "OBJETO_CONHECIMENTO") or ai.extrair_tag(txt_plano_item, "CONTEUDOS_ESPECIFICOS") or ""
                                clean_obj = re.sub(r'[*#\[\]]', '', obj_item).strip()
                                
                                if clean_obj and len(clean_obj) > 3 and not re.search(TERMOS_EXPURGO, clean_obj) and not re.search(TERMOS_EXPURGO, str(r_plano.get('EIXO', ''))):
                                    opcoes_curriculo_limpas.append(f"[{sem_lbl}] {clean_obj}")

                        df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == ano_aluno_num].copy() if not df_curriculo.empty else pd.DataFrame()
                        if not df_matriz_ano.empty:
                            col_eixo_mat = next((c for c in df_matriz_ano.columns if any(x in c.upper() for x in ['GERAIS', 'EIXO'])), None)
                            colunas_trim_busca = [c for c in df_matriz_ano.columns if any(t in c.upper() for t in ['TRIMESTRE', 'TRI'])] if is_anual_pei else ([next((c for c in df_matriz_ano.columns if str(trim_ativo_pei).upper() in c.upper()), None)] if next((c for c in df_matriz_ano.columns if str(trim_ativo_pei).upper() in c.upper()), None) else [])

                            for col_t in colunas_trim_busca:
                                if col_t and col_eixo_mat:
                                    for _, r_mat in df_matriz_ano.iterrows():
                                        c_bruto = str(r_mat[col_t])
                                        if pd.notna(c_bruto) and c_bruto.strip() != "" and c_bruto.upper() != "NAN":
                                            for t_item in c_bruto.split(';'):
                                                t_cl = re.sub(r'\[cite:.*?\]|[*#\[\]]', '', t_item).strip()
                                                if t_cl and len(t_cl) > 3 and not re.search(TERMOS_EXPURGO, t_cl):
                                                    opcoes_curriculo_limpas.append(f"[{r_mat[col_eixo_mat]}] {t_cl}")

                        todos_conteudos_disponiveis = sorted(list(set(opcoes_curriculo_limpas)))
                        default_selecionados = todos_conteudos_disponiveis[:min(6, len(todos_conteudos_disponiveis))]
                        
                        selecionados = st.multiselect(
                            "Conteúdos Pedagógicos de Matemática (Feriados e Recessos já Excluídos):", 
                            todos_conteudos_disponiveis, 
                            default=default_selecionados,
                            key=f"sel_mat_pop_{id_aluno_global}_{v}"
                        )

                        detalhes_extras_prof = st.text_input(
                            "Diretrizes Específicas do Professor de Matemática:",
                            placeholder="Ex: Focar em recursos manipulativos variados, malha quadriculada, ábaco e calculadora...",
                            key=f"obs_extra_pei_pop_{id_aluno_global}_{v}"
                        )
                        
                        if st.button("Gerar Planejamento de Matemática com IA", type="primary", use_container_width=True, key=f"btn_gen_curr_pop_{id_aluno_global}_{v}"):
                            if selecionados:
                                with st.spinner("Sintetizando macro-metas curriculares com recursos diversificados..."):
                                    prompt_curr = (
                                        f"VOCÊ É O ESPECIALISTA EM INCLUSÃO E DUA PARA O COMPONENTE DE MATEMÁTICA (PREFEITURA DE ITABUNA).\n"
                                        f"ESTUDANTE: {aluno_global_nome} | TURMA: {turma_pei} | LAUDO: {perfil_aluno_global}\n"
                                        f"ESCOPO: {escopo_pei_doc}\n\n"
                                        f"--- DOSSIÊ CLÍNICO E DIAGNÓSTICO DA ESTUDANTE ---\n"
                                        f"DIAGNÓSTICO: {v_diag_exp if v_diag_exp else 'Acompanhamento do desenvolvimento com adaptações funcionais em Matemática.'}\n"
                                        f"DIRETRIZES: {v_diretrizes_exp}\n"
                                        f"OBSERVAÇÕES DO PROFESSOR: {detalhes_extras_prof}\n\n"
                                        f"--- CONTEÚDOS SELECIONADOS PARA ADAPTAÇÃO ---\n"
                                        f"{chr(10).join(selecionados)}\n\n"
                                        f"🚨 REGRAS CRÍTICAS DE EXCELÊNCIA PEDAGÓGICA:\n"
                                        f"1. SINTETIZE em no máximo 4 a 6 MACRO-METAS CONSOLIDADAS por Eixo (não crie dezenas de linhas repetitivas!).\n"
                                        f"2. NUNCA cite 'Recesso', 'Feriado' ou 'Prova'. Apenas conteúdos matemáticos reais.\n"
                                        f"3. DIVERSIFIQUE OS RECURSOS MATERIAIS conforme o tema de cada linha (NÃO REPITA 'Material Dourado' em tudo!):\n"
                                        f"   - Para Sistemas e Números: Ábaco aberto, fichas de ordens, Material Dourado.\n"
                                        f"   - Para Operações e Cálculo: Calculadora com teclas ampliadas, dinheiro fictício, tabuada visual.\n"
                                        f"   - Para Frações e Decimais: Discos de frações em EVA, malhas quadriculadas 10x10, encartes de mercado.\n"
                                        f"   - Para Geometria e Ângulos: Sólidos geométricos, dobraduras de papel, transferidor físico adaptado, régua.\n"
                                        f"   - Para Medidas e Grandezas: Fita métrica, balança, recipientes graduados.\n"
                                        f"   - Para Estatística e Gráficos: Tabelas pictóricas ampliadas, gráficos em barras coloridas de cartolina.\n\n"
                                        f"FORMATO EXATO DE CADA BLOCO:\n"
                                        f"[ITEM]\n"
                                        f"[OBJETIVO] (Apenas o objetivo de aprendizagem simplificado e acessível)\n"
                                        f"[ESTRATEGIA] (Estratégia prática: instrução passo a passo, apoio visual e mediação)\n"
                                        f"[RECURSO] (Recursos concretos diversificados e adequados ao tema da linha)\n"
                                        f"[/ITEM]"
                                    )
                                    res_ia = ai.gerar_ia("TRADUTOR_CURRICULAR_V39", prompt_curr, usar_busca=False)
                                    
                                    blocos = re.findall(r"\[ITEM\](.*?)\[/ITEM\]", res_ia, re.DOTALL)
                                    novas_linhas = []
                                    for b in blocos:
                                        obj_m = re.search(r'\[OBJETIVO\]\s*[:\-]*\s*(.*?)(?=\[ESTRATEGIA\]|\[RECURSO\]|\[/ITEM\]|$)', b, re.DOTALL | re.IGNORECASE)
                                        est_m = re.search(r'\[ESTRATEGIA\]\s*[:\-]*\s*(.*?)(?=\[RECURSO\]|\[/ITEM\]|$)', b, re.DOTALL | re.IGNORECASE)
                                        rec_m = re.search(r'\[RECURSO\]\s*[:\-]*\s*(.*?)(?=\[/ITEM\]|$)', b, re.DOTALL | re.IGNORECASE)
                                        
                                        def limpar_campo(txt_raw):
                                            if not txt_raw: return ""
                                            return re.sub(r'\[/?(?:ITEM|OBJETIVO|ESTRATEGIA|RECURSO)\]', '', txt_raw, flags=re.IGNORECASE).strip()

                                        novas_linhas.append({
                                            "Objetivos de Aprendizagem": limpar_campo(obj_m.group(1) if obj_m else ""),
                                            "Estratégias Metodológicas": limpar_campo(est_m.group(1) if est_m else ""),
                                            "Recursos Materiais": limpar_campo(rec_m.group(1) if rec_m else "")
                                        })
                                    
                                    if novas_linhas:
                                        df_curr_atual = pd.DataFrame(novas_linhas)
                                        salvar_relatorio_pei_sem_duplicidade(id_aluno_global, aluno_global_nome, chave_tabela_curr, df_curr_atual.to_json(orient='records'))
                                        st.success(f"Planejamento de Matemática de {aluno_global_nome} consolidado com sucesso!")
                                        time.sleep(0.5); st.rerun()

                    st.markdown(f"**Tabela de Acessibilidade Curricular de {aluno_global_nome} (Editável)**")
                    df_editado_curr = st.data_editor(
                        df_curr_atual, num_rows="dynamic", use_container_width=True, key=f"ed_curr_frag_{id_aluno_global}_{v}",
                        column_config={
                            "Objetivos de Aprendizagem": st.column_config.TextColumn(width="large"), 
                            "Estratégias Metodológicas": st.column_config.TextColumn(width="large"), 
                            "Recursos Materiais": st.column_config.TextColumn(width="medium")
                        }
                    )
                    
                    st.markdown("---")
                    
                    st.markdown("##### Parecer de Resultados Obtidos (Seção 3 do PEI Oficial)")
                    chave_parecer_res = f"PARECER_RESULTADOS_PEI_{id_aluno_global}"
                    reg_par_res = hist_exp[hist_exp['TIPO'] == chave_parecer_res] if not hist_exp.empty else pd.DataFrame()
                    parecer_inicial_mat = str(reg_par_res.iloc[-1]['CONTEUDO']) if not reg_par_res.empty else f"Matemática: A estudante {aluno_global_nome} encontra-se em processo de desenvolvimento da aprendizagem, respondendo positivamente ao uso de recursos manipulativos diversificados e mediação individualizada nas atividades."
                    
                    parecer_mat_editavel = st.text_area("Parecer de Matemática (Para a Área de Ciências da Natureza e Matemática):", value=parecer_inicial_mat, height=75, key=f"ta_parecer_res_{id_aluno_global}_{v}")

                    dados_aluno_docx = {
                        "nome": aluno_global_nome, 
                        "turma": turma_pei, 
                        "cid": perfil_aluno_global,
                        "idade": "11"
                    }
                    
                    habilidades_estudo_caso = {
                        "Habilidades Sociais": v_soc_exp, 
                        "Habilidades Comunicativas": v_com_exp, 
                        "Habilidades Emocionais": v_emo_exp, 
                        "Habilidades Funcionais": v_fun_exp
                    }
                    
                    nome_arq_pei = f"PEI_OFICIAL_ITABUNA_ANUAL_{aluno_global_nome.replace(' ', '_')}_{ano_aluno_num}ANO" if is_anual_pei else f"PEI_OFICIAL_ITABUNA_{aluno_global_nome.replace(' ', '_')}_{trim_ativo_pei.replace(' ', '')}"
                    doc_stream = exporter.gerar_docx_pei_oficial(nome_arq_pei, dados_aluno_docx, habilidades_estudo_caso, df_editado_curr, parecer_resultados=parecer_mat_editavel)
                    docx_bytes_pei = doc_stream.getvalue()

                    st.markdown("<br>", unsafe_allow_html=True)
                    c_btn_save, c_btn_exp = st.columns(2)
                    
                    if c_btn_save.button("Salvar Planejamento de Matemática", use_container_width=True, key=f"btn_save_tab_curr_{id_aluno_global}_{v}"):
                        salvar_relatorio_pei_sem_duplicidade(id_aluno_global, aluno_global_nome, chave_tabela_curr, df_editado_curr.to_json(orient='records'))
                        salvar_relatorio_pei_sem_duplicidade(id_aluno_global, aluno_global_nome, chave_parecer_res, parecer_mat_editavel)
                        st.success("Planejamento de Matemática salvo com sucesso!"); time.sleep(0.5); st.rerun()
                        
                    c_btn_exp.download_button(
                        label=f"📥 Baixar {escopo_pei_doc} em Word (DOCX)",
                        data=docx_bytes_pei,
                        file_name=f"{nome_arq_pei}.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        type="primary",
                        use_container_width=True,
                        key=f"btn_dl_pei_docx_{id_aluno_global}_{v}"
                    )

                    with st.expander("📋 Copiar por Colunas para a Tabela Coletiva do Google Docs da Escola", expanded=False):
                        st.caption("Clique no ícone de cópia no canto de cada bloco abaixo para colar diretamente dentro da respectiva célula da tabela compartilhada da escola:")
                        
                        lista_objs = []
                        lista_ests = []
                        lista_recs = []
                        
                        if not df_editado_curr.empty:
                            for _, r_c in df_editado_curr.iterrows():
                                o = str(r_c.get('Objetivos de Aprendizagem', '')).strip()
                                e = str(r_c.get('Estratégias Metodológicas', '')).strip()
                                r = str(r_c.get('Recursos Materiais', '')).strip()
                                if o: lista_objs.append(f"• {o}")
                                if e: lista_ests.append(f"• {e}")
                                if r: lista_recs.append(f"• {r}")
                        
                        t_col1, t_col2, t_col3, t_col4 = st.tabs([
                            "1. Objetivos de Aprendizagem", 
                            "2. Estratégias Metodológicas", 
                            "3. Recursos Materiais",
                            "4. Resultados Obtidos (Seção 3)"
                        ])
                        
                        with t_col1:
                            st.caption("Texto pronto para colar na coluna **OBJETIVOS DE APRENDIZAGEM**:")
                            st.code("\n\n".join(lista_objs) if lista_objs else "Nenhum objetivo cadastrado.", language=None)
                            
                        with t_col2:
                            st.caption("Texto pronto para colar na coluna **ESTRATÉGIAS METODOLÓGICAS**:")
                            st.code("\n\n".join(lista_ests) if lista_ests else "Nenhuma estratégia cadastrada.", language=None)
                            
                        with t_col3:
                            st.caption("Texto pronto para colar na coluna **RECURSOS MATERIAIS**:")
                            st.code("\n\n".join(lista_recs) if lista_recs else "Nenhum recurso cadastrado.", language=None)
                            
                        with t_col4:
                            st.caption("Texto pronto para colar na Seção 3 (**MATEMÁTICA / CIÊNCIAS**):")
                            st.code(parecer_mat_editavel, language=None)

            renderizar_curriculo_exportacao_fragmento()


# ==============================================================================
# MÓDULO: BIBLIOTECA DIGITAL & BASE DE CONHECIMENTO - V2026.PRO_EXECUTIVE
# ==============================================================================
elif menu == "📚 Base de Conhecimento":
    st.title("Biblioteca Digital & Cofre de Materiais")
    st.caption("Repositório central de livros didáticos, referenciais curriculares e diretrizes pedagógicas.")
    st.markdown("---")
    
    if "v_bib" not in st.session_state: 
        st.session_state.v_bib = int(time.time())
    v = st.session_state.v_bib

    tab_upload, tab_acervo_lib = st.tabs(["Upload de Novo Documento", "Acervo de Obras Guardadas"])
    
    with tab_upload:
        with st.form("form_upload_drive", clear_on_submit=True):
            st.markdown("#### Armazenamento de Material no Cofre Digital")
            c1, c2 = st.columns(2)
            tipo_doc = c1.selectbox("Categoria do Material:", ["Livro Didático", "Referencial Curricular", "Documento PEI", "Outros"], key=f"up_cat_{v}")
            ano_doc = c2.selectbox("Série de Referência:", ["6º Ano", "7º Ano", "8º Ano", "9º Ano", "Geral"], key=f"up_ano_{v}")
            
            nome_arq = st.text_input("Título do Documento:", placeholder="Ex: Livro A Conquista da Matemática 6º Ano", key=f"up_nome_{v}")
            uploaded_file = st.file_uploader("Arquivo PDF:", type=["pdf"], key=f"up_pdf_{v}")
            
            if st.form_submit_button("Armazenar no Google Drive"):
                if uploaded_file and nome_arq:
                    with st.spinner("Enviando material para o Google Drive..."):
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
                            st.success(f"'{nome_arq}' armazenado com sucesso no Google Drive!")
                            st.balloons(); time.sleep(0.8); st.rerun()
                        else:
                            st.error(f"Erro no upload: {link_drive}")
                else:
                    st.warning("Preencha o título do material e selecione o arquivo PDF.")

    with tab_acervo_lib:
        @st.fragment
        def renderizar_acervo_biblioteca_fragmento():
            st.markdown("#### Acervo de Documentos e Livros")
            
            if not df_materiais.empty:
                filtro_cat_lib = st.segmented_control(
                    "Filtrar por Categoria:", 
                    ["Todos", "Livro Didático", "Referencial Curricular", "Documento PEI", "Outros"], 
                    default="Todos",
                    key=f"pills_lib_cat_{v}"
                )
                
                df_lib_filtrado = df_materiais.copy()
                if filtro_cat_lib != "Todos":
                    df_lib_filtrado = df_lib_filtrado[df_lib_filtrado['TIPO'].str.contains(filtro_cat_lib, case=False, na=False)]
                
                st.caption(f"Exibindo **{len(df_lib_filtrado)} de {len(df_materiais)}** materiais cadastrados.")
                st.markdown("---")
                
                if df_lib_filtrado.empty:
                    st.info("Nenhum material localizado para a categoria selecionada.")
                else:
                    for _, row in df_lib_filtrado.iloc[::-1].iterrows():
                        with st.container(border=True):
                            c_txt, c_btn1, c_btn2 = st.columns([3, 1, 1])
                            
                            nome_m = row['NOME_ARQUIVO']
                            tipo_m = str(row['TIPO'])
                            data_up = row.get('DATA_UPLOAD', 'N/A')
                            
                            c_txt.markdown(f"##### {nome_m}")
                            c_txt.caption(f"Categoria: **{tipo_m}** | Data de Inclusão: **{data_up}**")
                            
                            c_btn1.link_button("Abrir no Drive", row['URI_ARQUIVO'], use_container_width=True)
                            
                            if c_btn2.button("Excluir Obra", key=f"del_mat_{row.name}_{v}", use_container_width=True):
                                if db.excluir_registro_com_drive("DB_MATERIAIS", nome_m):
                                    st.success("Material removido do acervo!"); time.sleep(0.5); st.rerun()
            else:
                st.info("A biblioteca digital está vazia. Faça o upload de livros e documentos no formulário ao lado.")

        renderizar_acervo_biblioteca_fragmento()
