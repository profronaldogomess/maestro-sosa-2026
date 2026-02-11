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
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR V39 - INTEGRADO & BLINDADO)
# ==============================================================================
if menu == "🧪 Criador de Aulas":
    st.title("🧪 Laboratório de Produção Semiótica (V39)")
    st.markdown("---")
    
    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "sosa_id_atual", "lab_meta", "hub_origem"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.cache_data.clear() # Limpa cache para o Escudo de Safra atualizar
        st.session_state.v_lab = int(time.time())
        st.rerun()

    if "v_lab" not in st.session_state: st.session_state.v_lab = 1
    v = st.session_state.v_lab

    # --- VACINA DE ESCOPO SOSA (is_hub definido no topo do módulo) ---
    is_hub = st.session_state.get("lab_meta", {}).get("tipo") == "PRODUÇÃO_HUB"

    # --- ÁREA DE EXIBIÇÃO E REFINO (MODO EDIÇÃO ATIVO) ---
    if "lab_temp" in st.session_state and "[PROFESSOR]" in st.session_state.lab_temp:
        txt_base = st.session_state.lab_temp
        
        s_id_extraido = ai.extrair_tag(txt_base, "SOSA_ID")
        s_id = s_id_extraido if s_id_extraido else st.session_state.get("sosa_id_atual", "SEM-ID")
        s_id = s_id.split("[")[0].strip()
        
        meta = st.session_state.get("lab_meta", {})
        st.success(f"💎 Material em Edição: **{s_id}**")

        # --- 🤖 REFINADOR MAESTRO V29 (INTEGRADO: NOVO + ACERVO) ---
        with st.container(border=True):
            st.subheader("🤖 Refinador Maestro (Perícia V29)")
            cmd_refine_lab = st.chat_input("Solicite ajustes (ex: 'redistribua o gabarito', 'troque a questão 2', 'mude o tema para cacau')...", key=f"chat_lab_ref_{v}")
            if cmd_refine_lab:
                with st.spinner("Maestro Sosa realizando reengenharia e perícia psicométrica..."):
                    # Lógica de Seleção de Persona (Sonda vs Material Comum)
                    persona_alvo = "REFINADOR_SONDA_V29" if "SONDA" in s_id.upper() else "REFINADOR_MATERIAIS"
                    novo_texto = ai.gerar_ia(persona_alvo, f"ORDEM: {cmd_refine_lab}\n\nCONTEÚDO ATUAL:\n{st.session_state.lab_temp}")
                    
                    if "[PROFESSOR]" in novo_texto or "[ALUNO]" in novo_texto:
                        st.session_state.lab_temp = novo_texto
                        st.session_state.v_lab += 1
                        st.rerun()
            
            if st.button("🗑️ DESCARTAR EDIÇÃO E VOLTAR", use_container_width=True):
                reset_laboratorio()
        
        # --- TABS DE VISUALIZAÇÃO E EDIÇÃO ---
        t_prof, t_alu, t_gab, t_pei, t_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "✅ Gabarito/Rubrica", "♿ PEI", "☁️ SINCRONIA"])
        
        with t_prof: ed_prof = st.text_area("Mapa de Regência:", ai.extrair_tag(txt_base, "PROFESSOR"), height=450, key=f"ed_prof_{v}")
        with t_alu: ed_alu = st.text_area("Folha do Aluno:", ai.extrair_tag(txt_base, "ALUNO"), height=450, key=f"ed_alu_{v}")
        with t_gab: ed_res = st.text_area("Gabarito:", ai.extrair_tag(txt_base, "GABARITO"), height=350, key=f"ed_res_{v}")
        
        with t_pei:
            st.subheader("♿ Adaptação Curricular")
            c_p1, c_p2 = st.columns(2)
            ed_pei_mat = c_p1.text_area("📄 Material PEI:", ai.extrair_tag(txt_base, "PEI"), height=400, key=f"ed_pei_mat_{v}")
            ed_pei_gab = c_p2.text_area("✅ Gabarito PEI:", ai.extrair_tag(txt_base, "GABARITO_PEI"), height=400, key=f"ed_pei_gab_{v}")

        with t_sync:
            st.warning("⚠️ O Triple-Sync substituirá a versão anterior deste material.")
            if st.button("💾 EXECUTAR TRIPLE-SYNC (SUBSTITUIR)", use_container_width=True, type="primary", key=f"btn_triple_{v}"):
                with st.status("Iniciando Protocolo de Substituição...") as status:
                    nome_final = s_id 
                    ano_str = f"{meta.get('ano', '6')}º"
                    semana_ref = meta.get('semana_ref', 'AVULSA')
                    
                    # LEI DA LIMPEZA (TRIPLE-SYNC)
                    db.excluir_registro_com_drive("DB_AULAS_PRONTAS", nome_final)
                    
                    conteudo_banco = f"[SOSA_ID] {nome_final}\n[AULA_ALVO] {meta.get('aula_alvo', 'Aula')}\n[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n[GABARITO]\n{ed_res}\n\n[PEI]\n{ed_pei_mat}\n\n[GABARITO_PEI]\n{ed_pei_gab}\n\n"

                    # CONTAGEM REAL DE QUESTÕES NO MATERIAL REGULAR
                    qtd_q_real = len(re.findall(r'(?m)^QUESTÃO\s+\d+', ed_alu.upper()))
                    is_sonda_check = "SONDA" in nome_final.upper()
                    
                    # CÁLCULO DO VALOR POR QUESTÃO (10,0 / QTD)
                    val_q_str = util.sosa_to_str(10.0 / qtd_q_real) if qtd_q_real > 0 else "1,00"

                    info_doc = {
                        "ano": ano_str, 
                        "trimestre": meta.get('trimestre', 'I Trimestre'), 
                        "valor": "10,00" if is_sonda_check else "0,00", 
                        "valor_questao": val_q_str,
                        "qtd_questoes": qtd_q_real
                    }

                    # GERAÇÃO DE DOCUMENTOS (FLUXO NATIVO)
                    if is_sonda_check:
                        doc_alu = exporter.gerar_docx_prova_v25(nome_final, ed_alu, info_doc)
                    else:
                        doc_alu = exporter.gerar_docx_aluno_v24(nome_final, ed_alu, info_doc)
                    
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_final}_ALUNO", modo="AULA")
                    doc_prof = exporter.gerar_docx_professor_v25(nome_final, ed_prof, {"ano": ano_str, "semana": semana_ref, "trimestre": info_doc["trimestre"]})
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_final}_PROF", modo="AULA")
                    
                    # GERAÇÃO PEI (GABARITO PROPORCIONAL)
                    link_pei = "N/A"
                    if len(ed_pei_mat) > 10:
                        if is_sonda_check:
                            doc_pei = exporter.gerar_docx_prova_v25(f"{nome_final}_PEI", ed_pei_mat, info_doc)
                        else:
                            doc_pei = exporter.gerar_docx_pei_v25(f"{nome_final}_PEI", ed_pei_mat, info_doc)
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_final}_PEI", modo="AULA")
                    
                    if "https" in str(link_alu):
                        conteudo_banco += f"--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI({link_pei})"
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), semana_ref, nome_final, conteudo_banco, ano_str, link_alu])
                        status.update(label="✅ Sincronia Concluída!", state="complete")
                        st.balloons(); time.sleep(1); reset_laboratorio()

    # --- SEÇÃO DE ENTRADA (CONFIGURAÇÃO INICIAL) ---
    else:
        tab_producao, tab_diagnostico, tab_trabalhos, tab_complementar, tab_acervo = st.tabs([
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
                    if planos_ano.empty: st.error("❌ Nenhum planejamento encontrado.")
                    else:
                        sem_lab = c2.selectbox("Semana Base (Ponto ID):", planos_ano["SEMANA"].tolist(), key=f"prod_sem_{v}")
                        plano_row = planos_ano[planos_ano["SEMANA"] == sem_lab].iloc[0]
                        plano_txt = str(plano_row['PLANO_TEXTO'])
                        
                        aula_alvo_prod = c3.radio("🎯 Aula Pendente:", ["Aula 1", "Aula 2"], horizontal=True, key=f"prod_alvo_{v}")
                        instr_extra_prod = st.text_area("📝 Contexto Adicional:", key=f"prod_extra_{v}")
                        qtd_q_prod = st.slider("Quantidade de Questões:", 3, 15, 10, key=f"prod_q_{v}")
                        
                        if st.button("💎 COMPILAR MATERIAL DE ELITE", use_container_width=True, type="primary"):
                            with st.spinner("Arquitetando Tratado Didático..."):
                                nome_elite = util.gerar_nome_material_elite(ano_lab, aula_alvo_prod, sem_lab)
                                st.session_state.sosa_id_atual = nome_elite
                                st.session_state.lab_meta = {"ano": ano_lab, "trimestre": "I Trimestre", "tipo": aula_alvo_prod, "semana_ref": sem_lab, "aula_alvo": aula_alvo_prod}
                                tag_aula = "AULA_1" if "1" in aula_alvo_prod else "AULA_2"
                                prompt_manual = f"PERSONA: MAESTRO_SOSA_V28_ELITE. ID: {nome_elite}.\nSÉRIE: {ano_ref_prod}. ALVO: {aula_alvo_prod}. QTD: {qtd_q_prod}.\nROTEIRO: {ai.extrair_tag(plano_txt, tag_aula)}.\nEXTRAS: {instr_extra_prod}."
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
                                with st.spinner("Maestro Sosa realizando perícia psicométrica..."):
                                    # NOMENCLATURA DE ELITE
                                    nome_elite_sonda = util.gerar_nome_material_elite(ano_sonda, "Sonda Diagnóstica", trim_sonda)
                                    st.session_state.sosa_id_atual = nome_elite_sonda
                                    st.session_state.lab_meta = {
                                        "ano": ano_sonda, "trimestre": trim_sonda, 
                                        "tipo": "SONDA", "aula_alvo": "Sonda Diagnóstica", "semana_ref": "AVALIAÇÃO"
                                    }
                                    
                                    prompt_sonda = (
                                        f"PERSONA: ARQUITETO_SONDA_DIAGNOSTICA. ID: {nome_elite_sonda}.\n"
                                        f"SÉRIE ATUAL: {ano_sonda}º Ano. TRIMESTRE: {trim_sonda}.\n"
                                        f"CONTEÚDOS ALVO: {' / '.join(sel_conts_s)}.\n"
                                        f"QUANTIDADE: {qtd_q_sonda} questões A-E. VALOR TOTAL: 10,0.\n\n"
                                        f"MISSÃO: Gere o material completo com as TAGS [PROFESSOR], [ALUNO], [GABARITO], [PEI], [GABARITO_PEI]."
                                    )
                                    st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_SONDA_DIAGNOSTICA", prompt_sonda, usar_busca=True)
                                    st.rerun()

        with tab_trabalhos:
            st.subheader("📋 Engenharia de Projetos e Semanários (BNCC)")
            with st.container(border=True):
                c1, c2, c3 = st.columns([1.5, 1, 1])
                natureza_p = c1.selectbox("Natureza do Evento:", 
                    ["Semanário Temático", "Projeto de Identidade (Itabuna)", "Evento Escolar (Interclasses/Gincana)", "Projeto BNCC Livre"], 
                    key=f"t_nat_{v}")
                ano_t = c2.selectbox("Série Alvo:", [6, 7, 8, 9], key=f"t_ano_{v}")
                modo_t = c3.selectbox("Modo de Execução:", ["Individual", "Em Grupo (Equipes)"], key=f"t_modo_{v}")

            with st.container(border=True):
                c_t1, c_t2, c_t3 = st.columns([2, 1, 1])
                tema_t = c_t1.text_input("Título do Tema/Semanário:", placeholder="Ex: Consciência Negra, 116 anos de Itabuna...", key=f"t_tema_{v}")
                valor_t = c_t2.number_input("Valor (0-10):", 0.0, 10.0, 2.0, step=0.5, key=f"t_val_{v}")
                qtd_aulas_t = c_t3.slider("Quantidade de Aulas:", 1, 10, 2, key=f"t_q_aulas_{v}")
                
            df_cur_t = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_t))]
            if not df_cur_t.empty:
                lista_eixos_t = sorted(df_cur_t["EIXO"].unique().tolist())
                eixos_sel_t = st.multiselect("Eixos BNCC para Integrar:", lista_eixos_t, key=f"t_eixos_multi_{v}")
                
                if eixos_sel_t:
                    df_hab_t = df_cur_t[df_cur_t["EIXO"].isin(eixos_sel_t)]
                    hab_t = st.multiselect("Habilidades BNCC Âncora (Opcional):", 
                                           sorted(df_hab_t["CONTEUDO_ESPECIFICO"].unique().tolist()), 
                                           key=f"t_hab_multi_{v}")
                    
                    instr_extra_p = st.text_area("📝 Instruções de Pesquisa:", key=f"t_extra_proj_{v}")

                    if st.button("🚀 GERAR ROTEIRO DE INVESTIGAÇÃO", use_container_width=True, type="primary"):
                        if not tema_t:
                            st.error("Por favor, defina o Título do Tema.")
                        else:
                            with st.spinner("Maestro Sosa arquitetando roteiro de pesquisa..."):
                                nome_elite_proj = util.gerar_nome_material_elite(ano_t, "Projeto", tema_t)
                                st.session_state.sosa_id_atual = nome_elite_proj
                                st.session_state.lab_meta = {
                                    "ano": ano_t, "trimestre": "I Trimestre", 
                                    "tipo": "TRABALHO", "aula_alvo": tema_t, "semana_ref": "PROJETO"
                                }
                                
                                txt_hab_t = ", ".join(hab_t) if hab_t else "Escolha habilidades pertinentes."

                                prompt_t = (
                                    f"PERSONA: ARQUITETO_PROJETOS_V29. ID: {nome_elite_proj}.\n"
                                    f"TEMA: {tema_t}. NATUREZA: {natureza_p}.\n"
                                    f"SÉRIE: {ano_t}º Ano. EIXOS: {', '.join(eixos_sel_t)}.\n"
                                    f"HABILIDADES: {txt_hab_t}.\n"
                                    f"LOGÍSTICA: {modo_t} | DURAÇÃO: {qtd_aulas_t} aulas.\n"
                                    f"VALOR: {util.sosa_to_str(valor_t)} pontos.\n"
                                    f"INSTRUÇÕES: {instr_extra_p}.\n\n"
                                    f"🚨 MISSÃO: Gere um ROTEIRO DE PESQUISA E INVESTIGAÇÃO com as TAGS [PROFESSOR], [ALUNO], [GABARITO], [PEI]."
                                )
                                st.session_state.lab_temp = ai.gerar_ia("ARQUITETO_PROJETOS_V29", prompt_t, usar_busca=True)
                                st.rerun()

        with tab_complementar:
            st.subheader("📚 Atividades Complementares de Fixação")
            with st.container(border=True):
                c1, c2 = st.columns([1, 2])
                ano_comp = c1.selectbox("Série:", [6, 7, 8, 9], key=f"comp_ano_{v}")
                planos_comp = df_planos[df_planos["ANO"].astype(str).str.contains(str(ano_comp))]
                sem_comp = c2.selectbox("Vincular ao Planejamento:", planos_comp["SEMANA"].tolist() if not planos_comp.empty else ["Semana Avulsa"], key=f"comp_sem_vinc_{v}")
                df_cur_comp = df_curriculo[df_curriculo["ANO"].astype(str).str.contains(str(ano_comp))]
                col_f1, col_f2 = st.columns(2)
                lista_eixos_comp = sorted(df_cur_comp["EIXO"].unique().tolist())
                sel_eixo_comp = col_f1.multiselect("1. Selecione o(s) Eixo(s):", lista_eixos_comp, key=f"comp_eixo_{v}")
                if sel_eixo_comp:
                    df_cont_comp = df_cur_comp[df_cur_comp["EIXO"].isin(sel_eixo_comp)]
                    lista_conts_comp = sorted(df_cont_comp["CONTEUDO_ESPECIFICO"].unique().tolist())
                    sel_cont_comp = col_f2.multiselect("2. Selecione os Conteúdos:", lista_conts_comp, key=f"comp_cont_{v}")
                    if sel_cont_comp:
                        df_obj_comp = df_cont_comp[df_cont_comp["CONTEUDO_ESPECIFICO"].isin(sel_cont_comp)]
                        lista_objs_comp = sorted(df_obj_comp["OBJETIVOS"].unique().tolist())
                        sel_obj_comp = st.multiselect("3. Selecione os Objetivos:", lista_objs_comp, key=f"comp_obj_{v}")
                        st.divider()
                        c_q1, c_q2 = st.columns([1, 2])
                        tipo_comp = c_q1.radio("Objetivo:", ["Fixação", "Reforço", "Aprofundamento"], key=f"comp_tipo_radio_{v}")
                        qtd_q_comp = c_q2.slider("Nº Questões:", 1, 20, 10, key=f"comp_q_{v}")
                        instr_extra_comp = st.text_area("📝 Instruções Extras:", key=f"comp_instr_{v}")
                        if st.button("🚀 GERAR MATERIAL COMPLEMENTAR", use_container_width=True, type="primary"):
                            with st.spinner("Maestro Sosa arquitetando material..."):
                                nome_elite_comp = util.gerar_nome_material_elite(ano_comp, f"Fixação ({tipo_comp})", sem_comp)
                                st.session_state.sosa_id_atual = nome_elite_comp
                                st.session_state.lab_meta = {"ano": ano_comp, "trimestre": "I Trimestre", "tipo": f"COMPLEMENTAR ({tipo_comp})", "semana_ref": sem_comp}
                                prompt_comp = f"PERSONA: MAESTRO_SOSA_V28_ELITE. ID: {nome_elite_comp}.\nOBJETIVO: {tipo_comp}. VÍNCULO: {sem_comp}. SÉRIE: {ano_comp}º Ano.\nCONTEÚDO: {' / '.join(sel_cont_comp)}.\nQUANTIDADE: {qtd_q_comp} questões A-E.\nINSTRUÇÕES: {instr_extra_comp}.\n\n🚨 MISSÃO: Gere com as TAGS [PROFESSOR], [ALUNO], [GABARITO], [PEI], [GABARITO_PEI]."
                                st.session_state.lab_temp = ai.gerar_ia("MAESTRO_SOSA_V28_ELITE", prompt_comp, usar_busca=True)
                                st.rerun()

        with tab_acervo:
            st.subheader("📂 Acervo de Materiais Produzidos")
            if not df_aulas.empty:
                f_ano_g = st.selectbox("Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key=f"acervo_filter_{v}")
                df_g = df_aulas.copy()
                if f_ano_g != "Todos": df_g = df_g[df_g["ANO"] == f_ano_g]
                for _, row in df_g.iloc[::-1].iterrows():
                    raw_c = str(row["CONTEUDO"])
                    s_id_h = ai.extrair_tag(raw_c, "SOSA_ID")
                    with st.container(border=True):
                        c_t1, c_t2, c_t3, c_t4, c_t5, c_t6 = st.columns([1.5, 1, 1, 1, 1, 1])
                        c_t1.markdown(f"**{row['TIPO_MATERIAL']}**\n`ID: {s_id_h}`")
                        links_alu = re.findall(r"Aluno\((.*?)\)", raw_c)
                        links_prof = re.findall(r"Prof\((.*?)\)", raw_c)
                        links_pei = re.findall(r"PEI\((.*?)\)", raw_c)
                        l_alu = links_alu[-1] if links_alu else None
                        l_prof = links_prof[-1] if links_prof else None
                        l_pei = links_pei[-1] if links_pei else None
                        if l_alu: c_t2.link_button("📝 ALUNO", str(l_alu), use_container_width=True)
                        if l_prof: c_t3.link_button("👨‍🏫 PROF", str(l_prof), use_container_width=True)
                        if l_pei and "N/A" not in l_pei: c_t4.link_button("♿ PEI", str(l_pei), use_container_width=True)
                        else: c_t4.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                        if c_t5.button("🔄 REFINAR", key=f"ref_{row.name}", use_container_width=True):
                            st.session_state.lab_temp = raw_c
                            st.session_state.sosa_id_atual = s_id_h
                            st.session_state.lab_meta = {"ano": str(row["ANO"]).replace("º",""), "tipo": "REFINO", "aula_alvo": row['TIPO_MATERIAL'], "semana_ref": row['SEMANA_REF']}
                            st.rerun()
                        if c_t6.button("🗑️ APAGAR", key=f"del_{row.name}", use_container_width=True):
                            if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", s_id_h): st.cache_data.clear(); st.rerun()

# ==============================================================================
# MÓDULO: PLANEJAMENTO ESTRATÉGICO (PONTO ID) - ARQUITETURA V28.12 (INTEGRADA)
# ==============================================================================
if menu == "📅 Planejamento (Ponto ID)":
    st.title("📅 Engenharia de Planejamento (Ponto ID)")
    st.markdown("---")

    def reset_planejamento():
        keys = ["p_temp", "refino_ativo"]
        for k in keys:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_plano = int(time.time())
        st.rerun()

    if "v_plano" not in st.session_state: st.session_state.v_plano = 1
    v = st.session_state.v_plano 

    # --- ALERTA DE MODO REFINO ATIVO ---
    if "refino_ativo" in st.session_state:
        st.info(f"🛠️ **MODO REFINO ATIVO:** Editando o plano de **{st.session_state.refino_ativo['semana']}**.")

    tab_gerar, tab_producao, tab_acervo, tab_matriz, tab_auditoria = st.tabs([
        "🚀 Engenharia de Planejamento", "🏗️ Dashboard de Produção", "📂 Gestão de Acervo (PIP)", "📖 Matriz Curricular Ativa", "📈 Auditoria de Cobertura"
    ])
    
    with tab_gerar:
        is_refinando = "refino_ativo" in st.session_state
        if is_refinando:
            if st.button("❌ CANCELAR REFINO E VOLTAR AO NOVO", use_container_width=True, key=f"cancel_ref_{v}"):
                reset_planejamento()
        
        # --- 1. STATUS E CALENDÁRIO ---
        with st.container(border=True):
            st.markdown("### 🛡️ 1. Status e Calendário")
            cg1, cg2, cg3 = st.columns([1.5, 1, 1])
            tipo_semana = cg1.selectbox("Natureza:", ["Aula Regular", "Avaliação / Trabalho", "Evento Extraordinário"], key=f"gate_tipo_{v}")
            
            sub_tipo = ""
            if tipo_semana == "Avaliação / Trabalho":
                sub_tipo = st.selectbox("Tipo de Ativo:", ["Sonda Diagnóstica", "Teste Trimestral", "Prova Oficial", "Trabalho/Projeto BNCC"], key=f"sub_av_{v}")
            elif tipo_semana == "Evento Extraordinário":
                sub_tipo = st.selectbox("Tipo de Evento:", ["Semana Zero (Vetor Disciplinar)", "Interclasses / Esportes", "Seminário / Projeto Temático", "Suspensão de Aula"], key=f"sub_ev_{v}")

            tem_sabado = cg2.toggle("Sábado Letivo?", key=f"gate_sab_{v}")
            carga_horaria = cg3.select_slider("Aulas Úteis:", options=["1 Aula", "2 Aulas", "3 Aulas"], value="2 Aulas", key=f"gate_carga_{v}")

# --- 2. PARÂMETROS DE REGÊNCIA (COM ESCUDO DE SAFRA V28.13) ---
        with st.container(border=True):
            st.markdown("### ⚙️ 2. Parâmetros de Regência")
            c1, c2, c3 = st.columns([1, 2, 1.5])
            
            # 1. Seleção do Ano (Gatilho do Filtro)
            ano_p = c1.selectbox("Série/Ano:", [1, 2, 3, 4, 5, 6, 7, 8, 9], index=5, key=f"ano_sel_{v}")
            ano_formatado = f"{ano_p}º"

            # 2. LÓGICA DO ESCUDO: Identifica semanas já ocupadas para ESTE ano
            semanas_ja_planejadas = []
            if not df_planos.empty:
                # Filtra os planos que já existem para o ano selecionado
                planos_do_ano = df_planos[df_planos['ANO'] == ano_formatado]
                semanas_ja_planejadas = planos_do_ano['SEMANA'].tolist()

            # 3. Gera a lista completa e filtra as disponíveis
            todas_semanas = util.gerar_semanas()
            
            # Se estiver em modo REFINO, a semana atual deve aparecer mesmo se já existir
            if is_refinando:
                semanas_disponiveis = [s for s in todas_semanas]
                index_refino = 0
                sem_alvo = st.session_state.refino_ativo['semana']
                for i, s in enumerate(semanas_disponiveis):
                    if sem_alvo in s:
                        index_refino = i
                        break
                sem_p = c2.selectbox("Semana de Referência (MODO REFINO):", semanas_disponiveis, index=index_refino, key=f"sem_sel_{v}")
            else:
                # MODO NORMAL: Esconde as semanas que já estão no banco
                semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_ja_planejadas]
                
                if not semanas_disponiveis:
                    st.warning(f"✅ Todas as semanas do {ano_formatado} já foram planejadas!")
                    sem_p = c2.selectbox("Semana de Referência:", ["Safra Completa"], disabled=True, key=f"sem_sel_{v}")
                else:
                    sem_p = c2.selectbox("Semana de Referência (Disponíveis):", semanas_disponiveis, key=f"sem_sel_{v}")

            sem_limpa = sem_p.split(" (")[0]
            trim_atual = sem_p.split(" - ")[1] if " - " in sem_p else "I Trimestre"
            modo_p = c3.radio("Método:", ["📖 Livro Didático", "🎛️ Manual (Banco)"], horizontal=True, key=f"modo_p_{v}")

        # --- 3. SELEÇÃO HIERÁRQUICA OU MAPEAMENTO INTELIGENTE (UNIFICADO) ---
        with st.container(border=True):
            # Captura a Matriz Curricular do Ano para a IA discernir
            df_matriz_ano = df_curriculo[df_curriculo['ANO'].astype(str) == str(ano_p)]
            matriz_contexto = df_matriz_ano.to_string(index=False)
            
            f_eixo, f_cont, f_obj, ctx_ia = "", "", "", ""

            if modo_p == "🎛️ Manual (Banco)":
                st.markdown("#### 🎯 Seleção Manual da Matriz")
                c_filt1, c_filt2 = st.columns([1, 2])
                if not df_matriz_ano.empty:
                    lista_eixos = sorted(df_matriz_ano['EIXO'].unique().tolist())
                    sel_eixo = st.multiselect("1. Eixo Oficial:", lista_eixos, key=f"ponto_id_eixo_man_{v}")
                    if sel_eixo:
                        df_cont = df_matriz_ano[df_matriz_ano['EIXO'].isin(sel_eixo)]
                        lista_conts = sorted(df_cont['CONTEUDO_ESPECIFICO'].unique().tolist())
                        sel_cont = st.multiselect("2. Conteúdo Oficial:", lista_conts, key=f"ponto_id_cont_man_{v}")
                        if sel_cont:
                            df_obj = df_cont[df_cont['CONTEUDO_ESPECIFICO'].isin(sel_cont)]
                            lista_objs = sorted(df_obj['OBJETIVOS'].unique().tolist())
                            sel_obj = st.multiselect("3. Objetivos Oficiais:", lista_objs, key=f"ponto_id_obj_man_{v}")
                            f_eixo, f_cont, f_obj = " / ".join(sel_eixo), " / ".join(sel_cont), " \n ".join(sel_obj)
                ctx_ia = f"MÉTODO MANUAL. DADOS SELECIONADOS: EIXO: {f_eixo}, CONTEÚDO: {f_cont}, OBJETIVOS: {f_obj}."
            
            else:
                st.markdown("#### 📖 Mapeamento Automático (IA Perita)")
                cx1, cx2 = st.columns([2, 1])
                lista_mats = df_materiais["NOME_ARQUIVO"].tolist() if not df_materiais.empty else []
                sel_mat = cx1.multiselect("Livro Utilizado:", lista_mats, key=f"ponto_id_livro_auto_{v}")
                pags = cx2.text_input("Páginas:", placeholder="Ex: 12-23", key=f"ponto_id_pags_auto_{v}")
                ctx_ia = f"MÉTODO LIVRO: {sel_mat} PÁGINAS: {pags}. A IA DEVE DISCERNIR O CONTEÚDO NA MATRIZ ABAIXO."

            strat = st.text_area("Estratégia / Observações / Descrição do Evento:", key=f"ponto_id_strat_final_{v}")

        # --- BOTÃO DE COMPILAÇÃO ÚNICO ---
        if st.button("🚀 COMPILAR PLANEJAMENTO BNCC", use_container_width=True, type="primary", key=f"btn_compilar_final_sosa_{v}"):
            with st.spinner("Maestro SOSA realizando Perícia Curricular..."):
                prompt = (
                    f"NATUREZA: {tipo_semana} ({sub_tipo}). ANO: {ano_p}º. SEMANA: {sem_limpa}. TRIMESTRE: {trim_atual}.\n"
                    f"MÉTODO: {modo_p}. CONTEXTO: {ctx_ia}. ESTRATÉGIA: {strat}.\n\n"
                    f"--- MATRIZ CURRICULAR OFICIAL (FONTE ÚNICA DE VERDADE) ---\n"
                    f"{matriz_contexto}\n\n"
                    f"INSTRUÇÃO CRÍTICA:\n"
                    f"1. Analise as páginas do livro/estratégia e localize a linha correspondente na MATRIZ acima.\n"
                    f"2. Copie LITERALMENTE os textos da Matriz para as tags [CONTEUDO_GERAL], [CONTEUDOS_ESPECIFICOS] e [OBJETIVOS_ENSINO].\n"
                    f"3. Desenvolva as Aulas (1 e 2) com base no livro, mas mantendo a linguagem formal do Arquiteto Pedagógico."
                )
                st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt)
                st.rerun()

        # --- 4. EDITOR E REFINADOR (SÓ APARECE SE GERADO) ---
        if "p_temp" in st.session_state:
            st.markdown("---")
            with st.container(border=True):
                st.subheader("🤖 Refinador Maestro")
                cmd_refine = st.chat_input("Solicite ajustes no plano...", key=f"SOSA_CHAT_PLAN_{v}")
                if cmd_refine:
                    with st.spinner("Maestro Sosa realizando reengenharia..."):
                        novo_texto = ai.gerar_ia("REFINADOR_PEDAGOGICO", f"ORDEM: {cmd_refine}\n\nATUAL:\n{st.session_state.p_temp}")
                        if novo_texto and "[BNCC_CODE]" in novo_texto:
                            st.session_state.p_temp = novo_texto
                            st.session_state.v_plano += 1 
                            st.rerun()
                
                # BOTÃO PARA LIMPAR O TEXTO GERADO
                if st.button("🗑️ LIMPAR PLANEJAMENTO GERADO", use_container_width=True):
                    reset_planejamento()

            txt_bruto = st.session_state.p_temp
            t_ed, t_vis = st.tabs(["✏️ Editor de Texto", "👁️ Estrutura de Regência"])
            
            with t_ed:
                c_ed1, c_ed2 = st.columns([1, 2])
                ed_bncc = c_ed1.text_input("Código BNCC:", ai.extrair_tag(txt_bruto, "BNCC_CODE"), key=f"ed_b_{v}")
                
                # Lógica de preenchimento: Prioriza o que a IA mapeou, mas aceita o manual
                val_eixo = ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL") if ai.extrair_tag(txt_bruto, "CONTEUDO_GERAL") else f_eixo
                val_cont = ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS") if ai.extrair_tag(txt_bruto, "CONTEUDOS_ESPECIFICOS") else f_cont
                val_obj = ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO") if ai.extrair_tag(txt_bruto, "OBJETIVOS_ENSINO") else f_obj
                
                ed_geral = c_ed2.text_input("Eixo Final:", val_eixo, key=f"ed_g_{v}")
                ed_espec = st.text_area("Conteúdos Finais:", val_cont, key=f"ed_e_{v}")
                ed_objs = st.text_area("Objetivos Finais:", val_obj, key=f"ed_o_{v}")
                ed_a1 = st.text_area("AULA 1:", ai.extrair_tag(txt_bruto, "AULA_1"), height=200, key=f"a1_{v}")
                ed_a2 = st.text_area("AULA 2:", ai.extrair_tag(txt_bruto, "AULA_2"), height=200, key=f"a2_{v}")
                ed_a3 = st.text_area("AULA 3 (Sábado):", ai.extrair_tag(txt_bruto, "SABADO_LETIVO"), height=150, key=f"a3_{v}") if (tem_sabado or "3" in carga_horaria) else "N/A"
                ed_ava = st.text_area("Avaliação:", ai.extrair_tag(txt_bruto, "AVALIACAO"), key=f"ed_ava_{v}")
                ed_pei = st.text_area("Adaptação PEI:", ai.extrair_tag(txt_bruto, "ADAPTACAO_PEI"), key=f"ed_pei_{v}")

                if st.button("💾 FINALIZAR E DISPARAR PRODUÇÃO", use_container_width=True, type="primary", key=f"btn_final_hub_{v}"):
                    with st.status("Sincronizando Hub Acadêmico...") as status:
                        final_ano_str = f"{ano_p}º"
                        nome_arquivo = f"PLANO_{ano_p}ANO_{sem_limpa.replace(' ', '')}"
                        
                        # 1. LIMPEZA DE VERSÕES ANTIGAS
                        db.excluir_plano_completo(sem_limpa, final_ano_str)
                        
                        # 2. PREPARAÇÃO DA "FREQUÊNCIA" DE TRANSMISSÃO (LIVRO/PÁGINAS)
                        if modo_p == "📖 Livro Didático":
                            # Formata exatamente como o Criador de Aulas vai buscar via Regex
                            transmissao_livro = f"MÉTODO LIVRO: [{sel_mat}] PÁGINAS: {pags}."
                        else:
                            transmissao_livro = "MÉTODO: MANUAL/BANCO."

                        ed_recursos = ai.extrair_tag(txt_bruto, "RECURSOS_DIDATICOS")
                        
                        metodologia_unificada = f"AULA 01:\n{ed_a1}\n\nAULA 02:\n{ed_a2}"
                        if ed_a3 != "N/A": 
                            metodologia_unificada += f"\n\nAULA 03 (SÁBADO LETIVO):\n{ed_a3}"
                        
                        # 3. GERAÇÃO DO DOCX
                        dados_docx = {
                            "geral": f"[{ed_bncc}] {ed_geral}", 
                            "especificos": ed_espec, 
                            "objetivos": ed_objs, 
                            "recursos": ed_recursos, 
                            "metodologia": metodologia_unificada, 
                            "avaliacao": ed_ava, 
                            "pei": ed_pei
                        }
                        
                        doc_io = exporter.gerar_docx_plano_pedagogico_ELITE(nome_arquivo, dados_docx, {"ano": final_ano_str, "semana": sem_limpa, "trimestre": trim_atual})
                        link_drive = db.subir_e_converter_para_google_docs(doc_io, nome_arquivo, trimestre=trim_atual, categoria=final_ano_str, semana=sem_limpa, modo="PLANEJAMENTO")
                        
                        if "https" in str(link_drive):
                            # 4. CONSOLIDAÇÃO NO BANCO COM O DNA DE TRANSMISSÃO
                            final_txt = (
                                f"{transmissao_livro} \n" # <--- AQUI ESTÁ A CHAVE DA TRANSMISSÃO
                                f"[BNCC_CODE] {ed_bncc} \n"
                                f"[CONTEUDO_GERAL] {ed_geral} \n"
                                f"[CONTEUDOS_ESPECIFICOS] {ed_espec} \n"
                                f"[OBJETIVOS_ENSINO] {ed_objs} \n"
                                f"[RECURSOS_DIDATICOS] {ed_recursos} \n"
                                f"[AULA_1] {ed_a1} \n"
                                f"[AULA_2] {ed_a2} \n"
                                f"[SABADO_LETIVO] {ed_a3} \n"
                                f"[AVALIACAO] {ed_ava} \n"
                                f"[ADAPTACAO_PEI] {ed_pei} \n"
                                f"--- LINK DRIVE --- {link_drive}"
                            )
                            
                            db.salvar_no_banco("DB_PLANOS", [
                                datetime.now().strftime("%d/%m/%Y"), 
                                sem_limpa, 
                                final_ano_str, 
                                trim_atual, 
                                "HUB_ATIVO", 
                                final_txt, 
                                link_drive
                            ])
                            
                            status.update(label="✅ Plano Sincronizado e Transmitindo!", state="complete")
                            st.balloons()
                            reset_planejamento()

    # --- ABA 2: DASHBOARD DE PRODUÇÃO ---
    with tab_producao:
        st.subheader("🏗️ Linha de Montagem de Materiais")
        if not df_planos.empty:
            # Filtra apenas os planos que estão em produção ativa
            planos_ativos = df_planos[df_planos["EIXO"].astype(str).str.contains("HUB_ATIVO", case=False, na=False)].iloc[::-1]
            
            if not planos_ativos.empty:
                for _, row in planos_ativos.iterrows():
                    with st.container(border=True):
                        c_p1, c_p2, c_p3, c_p4 = st.columns([1.5, 1.5, 1, 1])
                        
                        sem_ref = row['SEMANA']
                        ano_ref = row['ANO']
                        
                        c_p1.markdown(f"**{sem_ref}**\n`Série: {ano_ref}`")
                        
                        # --- VERIFICAÇÃO DE PROGRESSO REAL ---
                        aulas_no_banco = df_aulas[(df_aulas['SEMANA_REF'] == sem_ref) & (df_aulas['ANO'] == ano_ref)]
                        txt_aulas = " ".join(aulas_no_banco['CONTEUDO'].astype(str).tolist())
                        
                        a1_status = "✅" if "Aula 1" in txt_aulas else "⏳"
                        a2_status = "✅" if "Aula 2" in txt_aulas else "⏳"
                        
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

                        # Botão para dar baixa (Arquivar)
                        if c_p4.button("✅ CONCLUIR", key=f"fin_hub_{row.name}", use_container_width=True, help="Mover para o Acervo Permanente"):
                            if db.arquivar_plano_produzido(sem_ref, ano_ref):
                                st.success("Safra Concluída! Plano arquivado.")
                                time.sleep(1)
                                st.rerun()
            else:
                st.info("📭 Nenhum plano pendente no Dashboard.")
        else:
            st.info("📭 Banco de planos vazio.")

    # --- ABA 3: GESTÃO DE ACERVO ---
    with tab_acervo:
        st.subheader("📂 Repositório de Planos Estratégicos")
        if not df_planos.empty:
            c_h1, c_h2 = st.columns(2)
            f_ano_h = c_h1.selectbox("Filtrar por Série:", ["Todos", "1º", "2º", "3º", "4º", "5º", "6º", "7º", "8º", "9º"], key="hist_ano_v27")
            df_h = df_planos.copy()
            if f_ano_h != "Todos": df_h = df_h[df_h["ANO"] == f_ano_h]
            
            if not df_h.empty:
                sel_h = st.selectbox("Selecionar Plano:", df_h["SEMANA"].tolist(), key="hist_sem_v27")
                dados_h = df_h[df_h["SEMANA"] == sel_h].iloc[0]
                raw_h = str(dados_h["PLANO_TEXTO"])
                
                col_btn1, col_btn2, col_btn3 = st.columns(3)
                with col_btn1:
                    if st.button("🔄 REABRIR PARA REFINO", use_container_width=True, key=f"btn_reopen_{v}"):
                        st.session_state.refino_ativo = {"ano": dados_h["ANO"], "semana": sel_h}
                        st.session_state.p_temp = raw_h
                        st.success("✅ Plano carregado! Clique na aba '🚀 Engenharia de Planejamento' para editar.")
                with col_btn2:
                    if st.button("🚀 MANDAR PARA PRODUÇÃO", use_container_width=True, type="primary", key=f"btn_hub_act_{sel_h}"):
                        if db.ativar_plano_no_hub(sel_h, dados_h["ANO"]):
                            st.success("✅ Plano enviado!"); time.sleep(1); st.rerun()
                with col_btn3:
                    if "https" in str(dados_h["LINK_DRIVE"]): 
                        st.link_button("🚀 ABRIR NO DRIVE", str(dados_h["LINK_DRIVE"]), use_container_width=True)

                with st.container(border=True):
                    st.markdown(f"### 🎯 {ai.extrair_tag(raw_h, 'CONTEUDO_GERAL')}")
                    st.caption(f"🆔 **BNCC:** {ai.extrair_tag(raw_h, 'BNCC_CODE')}")
                    col_info1, col_info2 = st.columns(2)
                    with col_info1: st.info(f"**Conteúdos:**\n{ai.extrair_tag(raw_h, 'CONTEUDOS_ESPECIFICOS')}")
                    with col_info2: st.success(f"**Objetivos:**\n{ai.extrair_tag(raw_h, 'OBJETIVOS_ENSINO')}")
                    st.divider()
                    c_v1, c_v2 = st.columns(2)
                    with c_v1: st.markdown("##### 📘 Aula 1"); st.write(ai.extrair_tag(raw_h, "AULA_1"))
                    with c_v2: st.markdown("##### 📗 Aula 2"); st.write(ai.extrair_tag(raw_h, "AULA_2"))
                    sab_txt = ai.extrair_tag(raw_h, "SABADO_LETIVO")
                    if sab_txt and "N/A" not in sab_txt.upper(): st.warning(f"##### 🗓️ Sábado Letivo\n{sab_txt}")
                    st.divider()
                    c_v3, c_v4 = st.columns(2)
                    with c_v3: st.markdown("##### 📝 Avaliação"); st.write(ai.extrair_tag(raw_h, "AVALIACAO"))
                    with c_v4: st.markdown("##### ♿ Estratégia PEI"); st.write(ai.extrair_tag(raw_h, "ADAPTACAO_PEI"))
                
                if st.button("🗑️ EXCLUIR PLANO", use_container_width=True, key=f"btn_del_plan_{v}"):
                    if db.excluir_plano_completo(sel_h, dados_h["ANO"]): st.rerun()
            else: st.info("Nenhum plano encontrado.")
        else: st.info("📭 Acervo vazio.")

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
# MÓDULO: DIÁRIO DE BORDO (V27.0) - RECEPTOR INTELIGENTE DE ATIVOS
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.title("📝 Diário de Bordo: Engajamento e Bônus")
    st.markdown("---")

    if "v_diario" not in st.session_state: st.session_state.v_diario = 1
    v = st.session_state.v_diario

    if df_alunos.empty:
        st.warning("⚠️ Cadastre alunos primeiro.")
    else:
        # --- 1. FILTROS DE ACESSO ---
        with st.container(border=True):
            c1, c2 = st.columns([1, 1])
            turma_sel = c1.selectbox("👥 Selecione a Turma:", sorted(df_alunos['TURMA'].unique()), key=f"db_turma_{v}")
            data_sel = c2.date_input("📅 Data da Aula:", date.today(), key=f"db_data_{v}")
            data_str = data_sel.strftime("%d/%m/%Y")

        # --- 2. MOTOR DE SINCRONIA (BUSCA NO COCKPIT) ---
        # O sistema procura o que você registrou na Gestão da Turma para este dia/turma
        registro_cockpit = df_registro_aulas[
            (df_registro_aulas['TURMA'] == turma_sel) & 
            (df_registro_aulas['DATA'] == data_str)
        ]

        if not registro_cockpit.empty:
            ativo_detectado = registro_cockpit.iloc[0]['CONTEUDO_MINISTRADO']
            semana_ref = registro_cockpit.iloc[0]['SEMANA']
            st.info(f"📍 **Ativos Detectados no Cockpit:** {ativo_detectado}")
            st.caption(f"🔗 Vinculado à: {semana_ref}")
        else:
            st.warning("⚠️ Nenhum registro encontrado no Cockpit para esta data. Registre na 'Gestão da Turma' para garantir a rastreabilidade total.")
            ativo_detectado = "Aula Avulsa"
            semana_ref = "N/A"

        # --- 3. PREPARAÇÃO DA GRADE DE ESTUDANTES ---
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        # Busca se já existe registro de diário para hoje para não perder dados ao recarregar
        df_existente = pd.DataFrame()
        if not df_diario.empty:
            df_existente = df_diario[
                (df_diario['DATA'] == data_str) & 
                (df_diario['TURMA'] == turma_sel)
            ]

        dados_editor = []
        for _, aluno in alunos_turma.iterrows():
            id_a = db.limpar_id(aluno['ID'])
            # Identificação Visual PEI
            is_pei = str(aluno['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
            
            # Valores padrão
            visto_val, faltou_val, tag_val, obs_val, bonus_val = True, False, "", "", 0.0

            # Se já houver registro salvo hoje, recupera os dados
            if not df_existente.empty:
                reg = df_existente[df_existente['ID_ALUNO'].apply(db.limpar_id) == id_a]
                if not reg.empty:
                    visto_val = str(reg.iloc[0]['VISTO_ATIVIDADE']).upper() == "TRUE"
                    tag_val = str(reg.iloc[0]['TAGS'])
                    obs_val = str(reg.iloc[0]['OBSERVACOES'])
                    if 'BONUS' in reg.columns: bonus_val = util.sosa_to_float(reg.iloc[0]['BONUS'])
                    if "AUSÊNCIA" in tag_val: faltou_val = True

            dados_editor.append({
                "ID": id_a,
                "ALUNO": f"♿ {aluno['NOME_ALUNO']}" if is_pei else aluno['NOME_ALUNO'],
                "FALTOU": faltou_val,
                "VISTO": visto_val,
                "⭐ BÔNUS": bonus_val,
                "OCORRÊNCIA": tag_val if tag_val != "nan" else "",
                "OBS": obs_val if obs_val != "nan" else ""
            })

        # --- 4. INTERFACE DE COLETA DE EVIDÊNCIAS ---
        st.subheader(f"📝 Registro de Engajamento")
        df_editado = st.data_editor(
            pd.DataFrame(dados_editor),
            column_config={
                "ID": None,
                "ALUNO": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                "FALTOU": st.column_config.CheckboxColumn("Faltou?", width="small"),
                "VISTO": st.column_config.CheckboxColumn("Visto", width="small"),
                "⭐ BÔNUS": st.column_config.NumberColumn("Bônus", min_value=0.0, max_value=2.0, step=0.1, format="%.1f"),
                "OCORRÊNCIA": st.column_config.SelectboxColumn("Tags", options=["", "Dormiu", "Conversa", "Se destacou", "Sem material", "Vetor Disciplinar", "PEI Concluído"]),
                "OBS": st.column_config.TextColumn("Observações Rápidas", width="medium")
            },
            hide_index=True, use_container_width=True, key=f"editor_diario_{v}"
        )

        # --- 5. SALVAMENTO COM RASTREABILIDADE ---
        if st.button("💾 SALVAR DIÁRIO E CONSOLIDAR BÔNUS", type="primary", use_container_width=True, key=f"btn_save_db_{v}"):
            with st.status("Sincronizando com o Boletim...", expanded=False) as status:
                # Limpa registros antigos do mesmo dia/turma para evitar duplicidade
                db.limpar_diario_data_turma(data_str, turma_sel)
                
                linhas_para_salvar = []
                for _, row in df_editado.iterrows():
                    tag_f, visto_f = row['OCORRÊNCIA'], row['VISTO']
                    if row['FALTOU']:
                        tag_f, visto_f = "AUSÊNCIA JUSTIFICADA", False
                    
                    # O campo OBSERVAÇÕES agora guarda o vínculo com o material do Cockpit
                    obs_final = f"[{ativo_detectado}] {row['OBS']}".strip()
                    
                    linhas_para_salvar.append([
                        data_str, 
                        row['ID'], 
                        row['ALUNO'].replace("♿ ", ""), 
                        turma_sel,
                        str(visto_f), 
                        tag_f, 
                        obs_final,
                        util.sosa_to_str(row['⭐ BÔNUS'])
                    ])
                
                if db.salvar_lote("DB_DIARIO_BORDO", linhas_para_salvar):
                    status.update(label="✅ Sincronia Concluída!", state="complete")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()

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
# MÓDULO: GESTÃO DA TURMA (V30.5) - COCKPIT 360° COM BLINDAGEM DE CHAVES
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.title("👥 Cockpit de Regência: Gestão 360°")
    st.markdown("---")

    # --- DEFINIÇÃO DA VARIÁVEL DE VERSÃO (VACINA CONTRA NAMEERROR) ---
    if "v_gestao" not in st.session_state:
        st.session_state.v_gestao = 1
    v = st.session_state.v_gestao

    tab_cockpit, tab_criar, tab_povoar, tab_editar = st.tabs([
        "📊 Cockpit da Turma",
        "🏗️ Arquitetura de Turmas", 
        "➕ Povoar Alunos", 
        "✏️ Edição & Transferência"
    ])

    # --- ABA 1: COCKPIT DA TURMA (INTEGRAÇÃO TOTAL) ---
    with tab_cockpit:
        if df_turmas.empty:
            st.info("📭 Nenhuma turma cadastrada. Vá em 'Arquitetura de Turmas'.")
        else:
            # 1. FILTROS DE FOCO E SAFRA
            c_f1, c_f2 = st.columns([1, 1])
            turma_foco = c_f1.selectbox("🎯 Selecione a Turma para Gestão:", sorted(df_turmas['ID_TURMA'].unique()), key=f"foco_t_{v}")
            trim_foco = c_f2.selectbox("📅 Trimestre de Safra:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"foco_trim_{v}")
            
            # Dados da Turma
            info_t = df_turmas[df_turmas['ID_TURMA'] == turma_foco].iloc[0]
            alunos_t = df_alunos[df_alunos['TURMA'] == turma_foco].sort_values(by="NOME_ALUNO")
            ano_num = "".join(filter(str.isdigit, turma_foco)) 

            # 2. DASHBOARD DE STATUS
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Alunos", len(alunos_t))
            c2.metric("Estudantes PEI", len(alunos_t[~alunos_t['NECESSIDADES'].astype(str).str.upper().isin(["NENHUMA", "PENDENTE", ""])]))
            
            aulas_turma_reg = df_registro_aulas[df_registro_aulas['TURMA'] == turma_foco]
            c3.metric("Aulas Ministradas", len(aulas_turma_reg))
            c4.metric("Horário", info_t['HORARIO_TEMPO'])

            st.markdown("---")

            col_esq, col_dir = st.columns([1.8, 1.2])

            with col_esq:
                st.subheader("🕒 Registro de Aula e Gestão de Ativos")
                
                with st.container(border=True):
                    st.markdown("#### 🚀 Aplicar Materiais na Turma")
                    
                    planos_ano = df_planos[df_planos['ANO'].str.contains(ano_num)]
                    materiais_ano = df_aulas[df_aulas['ANO'].str.contains(ano_num)]

                    # LÓGICA DE SUMIÇO POR TURMA
                    mats_ja_usados = aulas_turma_reg['CONTEUDO_MINISTRADO'].astype(str).tolist()
                    mats_disponiveis = []
                    for _, m_row in materiais_ano.iterrows():
                        m_nome = m_row['TIPO_MATERIAL']
                        if not any(m_nome in r for r in mats_ja_usados):
                            mats_disponiveis.append(m_nome)

                    c_r1, c_r2 = st.columns(2)
                    # CORREÇÃO AQUI: v agora está definido no topo do módulo
                    data_aula = c_r1.date_input("Data da Aplicação:", date.today(), key=f"dt_reg_{v}")
                    plano_sel = c_r2.selectbox("Vincular ao Plano Base:", ["Nenhum"] + planos_ano['SEMANA'].tolist(), key=f"plano_reg_{v}")
                    
                    mats_sel = st.multiselect("📦 Selecione os Ativos (Sondas, Trabalhos, Aulas):", 
                                              options=mats_disponiveis,
                                              key=f"mats_reg_{v}")

                    if st.button("💾 REGISTRAR AULA E BAIXAR ATIVOS", use_container_width=True, type="primary", key=f"btn_reg_{v}"):
                        if not mats_sel and plano_sel == "Nenhum":
                            st.error("Selecione pelo menos um Plano ou Material.")
                        else:
                            with st.spinner("Sincronizando Cockpit..."):
                                lista_conteudos = []
                                lista_peis = []
                                
                                if plano_sel != "Nenhum":
                                    p_row = planos_ano[planos_ano['SEMANA'] == plano_sel].iloc[0]
                                    lista_conteudos.append(f"PLANO: {ai.extrair_tag(p_row['PLANO_TEXTO'], 'CONTEUDOS_ESPECIFICOS')}")
                                    lista_peis.append(ai.extrair_tag(p_row['PLANO_TEXTO'], "ADAPTACAO_PEI"))
                                
                                for m in mats_sel:
                                    lista_conteudos.append(m)
                                
                                conteudo_final = " + ".join(lista_conteudos)
                                pei_final = " | ".join(lista_peis) if lista_peis else "Verificar Ativo PEI"

                                db.salvar_no_banco("DB_REGISTRO_AULAS", [
                                    data_aula.strftime("%d/%m/%Y"), plano_sel, turma_foco, 
                                    conteudo_final, pei_final, "MINISTRADA"
                                ])
                                st.success(f"✅ Ativos vinculados à {turma_foco}!")
                                time.sleep(1); st.rerun()

                if not aulas_turma_reg.empty:
                    st.markdown("#### 📌 Últimos Registros")
                    for _, reg in aulas_turma_reg.tail(3).iterrows():
                        # A data aqui agora virá formatada pelo database.py
                        with st.expander(f"📅 {reg['DATA']} - {reg['CONTEUDO_MINISTRADO'][:50]}..."):
                            st.write(f"**Conteúdo:** {reg['CONTEUDO_MINISTRADO']}")

            with col_dir:
                st.subheader("📂 Inventário da Turma")
                with st.container(border=True):
                    st.markdown(f"**📦 Ativos Prontos para {turma_foco}**")
                    if mats_disponiveis:
                        for m in mats_disponiveis:
                            icone = "🔍" if "SONDA" in m.upper() else "📋" if "TRAB" in m.upper() else "📚" if "COMP" in m.upper() else "📖"
                            st.write(f"{icone} {m}")
                    else:
                        st.success("🎉 Estoque de ativos aplicado!")

                with st.container(border=True):
                    st.markdown("**👥 Estudantes (Foco PEI)**")
                    for _, alu in alunos_t.iterrows():
                        is_pei = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", ""]
                        if is_pei: st.warning(f"♿ {alu['NOME_ALUNO']}")
                        else: st.write(f"👤 {alu['NOME_ALUNO']}")

    # --- ABA 2: ARQUITETURA DE TURMAS (V28.5 - ULTRA-FLEX) ---
    with tab_criar:
        st.subheader("🏗️ Configurar Nova Turma")
        v_t = f"t_{v}"
        with st.container(border=True):
            c1, c2, c3 = st.columns(3)
            ano_t = c1.selectbox("Série/Ano:", [6, 7, 8, 9], key=f"ano_{v_t}")
            letra_t = c2.selectbox("Letra:", ["A", "B", "C", "D", "E", "F"], key=f"letra_{v_t}")
            turno_t = c3.selectbox("Turno:", ["Matutino", "Vespertino"], key=f"turno_{v_t}")

        dias_aula = st.multiselect("📅 Selecione os Dias de Aula:", ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"], max_selections=2, key=f"dias_{v_t}")

        horarios_escolhidos = {}
        if dias_aula:
            st.markdown("#### ⏰ Defina o Tempo de Aula por dia")
            opcoes_h = {"1º Tempo": "07:10h – 09:10h", "2º Tempo": "09:30h – 11:30h"} if turno_t == "Matutino" else {"1º Tempo": "13:10h – 15:10h", "2º Tempo": "15:30h – 17:30h"}
            cols_h = st.columns(len(dias_aula))
            for i, dia in enumerate(dias_aula):
                with cols_h[i]:
                    st.info(f"**{dia}**")
                    t_sel = st.radio(f"Horário:", options=list(opcoes_h.keys()), key=f"radio_{dia}_{v_t}")
                    horarios_escolhidos[dia] = t_sel
            
            if st.button("🚀 CADASTRAR TURMA AGORA", use_container_width=True, type="primary", key=f"btn_cad_{v_t}"):
                sigla = f"{ano_t}ª {'M' if turno_t == 'Matutino' else 'V'}{letra_t}"
                str_dias = " / ".join(dias_aula)
                str_horarios = " / ".join([f"{d[:3]}: {horarios_escolhidos[d]}" for d in dias_aula])
                if db.salvar_no_banco("DB_TURMAS", [sigla, f"{ano_t}º Ano {letra_t}", turno_t, str_dias, str_horarios, "ATIVO"]):
                    st.success(f"✅ Turma {sigla} criada!"); st.cache_data.clear(); time.sleep(1); st.rerun()

    # --- ABA 3: POVOAR ALUNOS (PRESERVADO) ---
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

    # --- ABA 4: EDIÇÃO & TRANSFERÊNCIA (PRESERVADO) ---
    with tab_editar:
        st.subheader("✏️ Alterar Cadastro ou Transferir Aluno")
        turmas_com_alunos = sorted(df_alunos['TURMA'].unique().tolist())
        t_origem = st.selectbox("Selecione a Turma Atual:", [""] + turmas_com_alunos, key=f"orig_{v}")
        if t_origem:
            alunos_opcoes = df_alunos[df_alunos['TURMA'] == t_origem].sort_values(by="NOME_ALUNO")
            aluno_sel_nome = st.selectbox("Selecione o Aluno:", alunos_opcoes['NOME_ALUNO'].tolist(), key=f"alu_ed_{v}")
            dados_atuais = alunos_opcoes[alunos_opcoes['NOME_ALUNO'] == aluno_sel_nome].iloc[0]
            with st.form("form_edicao_aluno_v26"):
                c_e1, c_e2 = st.columns(2)
                novo_nome = c_e1.text_input("Nome Completo:", value=dados_atuais['NOME_ALUNO'])
                nova_nec = c_e2.text_input("Necessidades/CID:", value=dados_atuais['NECESSIDADES'])
                c_e3, c_e4 = st.columns(2)
                novo_status = c_e3.selectbox("Status:", ["ATIVO", "DESISTENTE", "TRANSFERIDO"], index=0)
                nova_turma = c_e4.selectbox("Transferir para:", df_turmas['ID_TURMA'].tolist(), index=df_turmas['ID_TURMA'].tolist().index(t_origem))
                if st.form_submit_button("💾 CONFIRMAR ALTERAÇÕES"):
                    db.excluir_registro("DB_ALUNOS", dados_atuais['NOME_ALUNO'])
                    db.salvar_no_banco("DB_ALUNOS", [dados_atuais['ID'], novo_nome.upper(), nova_turma, novo_status, nova_nec.upper(), "EDITADO"])
                    st.success("Atualizado!"); st.cache_data.clear(); time.sleep(1); st.rerun()

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
# MÓDULO: CENTRAL DE AVALIAÇÕES (V37.0) - SINCRO TOTAL E ACERVO DE ELITE
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

    tab_arquiteto, tab_refino, tab_vis, tab_recomposicao, tab_finalizar, tab_acervo = st.tabs([
        "🚀 Arquiteto de Exames", "🤖 Refinador Maestro", "👁️ Visualização 360°", "🔥 Recomposição/Revisão", "💾 Finalizar Ativo", "🗂️ Acervo de Safra"
    ])

    # --- ABA 1: ARQUITETO ---
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
            st.markdown("### 📊 2. Distribuição de Dificuldade")
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

            trim_map = {"I Trimestre": "I", "II Trimestre": "II", "III Trimestre": "III"}
            df_cur_filtrado = df_curriculo[(df_curriculo["ANO"].astype(str) == str(ano_av)) & (df_curriculo["TRIMESTRE"] == trim_map[trim_filtro])]
            col_c1, col_c2 = st.columns(2)
            eixos_av = col_c1.multiselect("Eixos Oficiais:", df_cur_filtrado["EIXO"].unique(), key=f"av_eixo_{v}")
            conts_av = col_c2.multiselect("Conteúdos Oficiais:", df_cur_filtrado[df_cur_filtrado["EIXO"].isin(eixos_av)]["CONTEUDO_ESPECIFICO"].unique(), key=f"av_cont_{v}")
            objs_av = st.multiselect("Objetivos de Aprendizagem:", df_cur_filtrado[df_cur_filtrado["CONTEUDO_ESPECIFICO"].isin(conts_av)]["OBJETIVOS"].unique(), key=f"av_obj_{v}")

            if st.button("💎 COMPILAR EXAME DE ELITE", use_container_width=True, type="primary"):
                if soma_q != qtd_q: st.error("Ajuste a distribuição das questões.")
                elif not mats_selecionados or not objs_av: st.error("Selecione os Ativos e Objetivos.")
                else:
                    with st.spinner("Maestro Arquiteto calibrando exame..."):
                        contexto_aulas = ""
                        for m_nome in mats_selecionados:
                            m_row = df_materiais_trim[df_materiais_trim["TIPO_MATERIAL"] == m_nome].iloc[0]
                            contexto_aulas += f"MATERIAL_ID: {m_nome}\nCONTEÚDO: {m_row['CONTEUDO']}\n"

                        prompt = (f"VOCÊ É O ARQUITETO DE EXAMES V30. SÉRIE: {ano_av}º Ano. TIPO: {tipo_av}. VALOR: {v_total}.\n"
                                  f"DIFICULDADE: {q_facil}F, {q_medio}M, {q_dificil}D. OBJETIVOS: {objs_av}.\n"
                                  f"CONTEÚDO MINISTRADO: {contexto_aulas}\n"
                                  f"MISSÃO: Gere o exame completo (Regular A-E | PEI A-C) com as tags obrigatórias.")
                        st.session_state.temp_prova = ai.gerar_ia("ARQUITETO_EXAMES_V30_ELITE", prompt, usar_busca=True)
                        st.session_state.av_valor_total = v_total
                        st.session_state.av_nome_fixo = f"{tipo_av.upper()}_{ano_av}ANO_{trim_filtro.replace(' ', '')}"
                        st.rerun()

    # --- ABA 2: REFINADOR ---
    with tab_refino:
        if "temp_prova" in st.session_state:
            st.subheader("🤖 Refinamento de Precisão")
            cmd = st.chat_input("Solicitar ajuste no exame...", key=f"chat_av_{v}")
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
            t1, t2, t3, t4, t5 = st.tabs(["📝 Prova Regular", "✅ Gabarito/Psicometria", "♿ Prova PEI", "📊 Gabarito PEI", "🧠 Justificativa PEI"])
            with t1: st.text_area("Conteúdo da Prova Regular:", ai.extrair_tag(txt_f, "QUESTOES"), height=500, key=f"vis_reg_{v}")
            with t2: st.code(ai.extrair_tag(txt_f, "GABARITO_TEXTO")); st.write(ai.extrair_tag(txt_f, "RESPOSTAS_IA"))
            with t3: st.text_area("Conteúdo da Prova PEI:", ai.extrair_tag(txt_f, "PEI"), height=500, key=f"vis_pei_{v}")
            with t4: st.code(ai.extrair_tag(txt_f, "GABARITO_PEI"))
            with t5: st.write(ai.extrair_tag(txt_f, "RESPOSTAS_PEI_IA"))
        else: st.info("Aguardando geração do exame...")

    # --- ABA 4: RECOMPOSIÇÃO E REVISÃO (SEPARADA POR PERFIL) ---
    with tab_recomposicao:
        if "temp_prova" in st.session_state:
            st.subheader("🚀 Gerador de Revisão Sincronizada")
            if st.button("💎 MATERIALIZAR REVISÃO DE ELITE", use_container_width=True, type="primary"):
                with st.spinner("Maestro Sosa convertendo prova em roteiro de recomposição..."):
                    prompt_rev = f"PROVA BASE:\n{st.session_state.temp_prova}\n\nID_EXAME: {st.session_state.av_nome_fixo}"
                    st.session_state.temp_revisao = ai.gerar_ia("ARQUITETO_REVISAO_V29", prompt_rev)
                    st.rerun()
            
            if "temp_revisao" in st.session_state:
                txt_rev = st.session_state.temp_revisao
                tr1, tr2, tr3, tr_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno (Aberto)", "♿ PEI (A-C)", "☁️ SINCRONIA"])
                with tr1: st.text_area("Guia do Professor:", ai.extrair_tag(txt_rev, "PROFESSOR"), height=400, key=f"rev_prof_{v}")
                with tr2: st.text_area("Folha do Aluno (Discursiva):", ai.extrair_tag(txt_rev, "ALUNO"), height=400, key=f"rev_alu_{v}")
                with tr3: st.text_area("Revisão PEI:", ai.extrair_tag(txt_rev, "PEI"), height=400, key=f"rev_pei_{v}")
                
                with tr_sync:
                    if st.button("💾 EXECUTAR TRIPLE-SYNC DA REVISÃO", use_container_width=True, type="primary"):
                        with st.status("Sincronizando Ativos de Recomposição...") as status:
                            nome_rev = f"REVISAO_{st.session_state.av_nome_fixo}"
                            db.excluir_registro_com_drive("DB_AULAS_PRONTAS", nome_rev)
                            
                            # 1. Geração Regular (Discursiva)
                            doc_alu = exporter.gerar_docx_aluno_v24(nome_rev, ai.extrair_tag(txt_rev, "ALUNO"), {"ano": f"{ano_av}º", "trimestre": trim_filtro})
                            link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_rev}_ALUNO", modo="AULA")
                            
                            # 2. Geração PEI (Múltipla Escolha)
                            doc_pei = exporter.gerar_docx_pei_v25(f"{nome_rev}_PEI", ai.extrair_tag(txt_rev, "PEI"), {"ano": f"{ano_av}º", "trimestre": trim_filtro})
                            link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_rev}_PEI", modo="AULA")
                            
                            # 3. Geração Professor
                            doc_prof = exporter.gerar_docx_professor_v25(nome_rev, ai.extrair_tag(txt_rev, "PROFESSOR"), {"ano": f"{ano_av}º", "semana": "REVISÃO", "trimestre": trim_filtro})
                            link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_rev}_PROF", modo="AULA")
                            
                            db.salvar_no_banco("DB_AULAS_PRONTAS", [
                                datetime.now().strftime("%d/%m/%Y"), "REVISÃO", nome_rev, 
                                txt_rev + f"\n--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI({link_pei})", f"{ano_av}º", link_alu
                            ])
                            status.update(label="✅ Revisão Sincronizada!", state="complete"); st.balloons()
        else: st.warning("⚠️ Gere a prova primeiro.")

    # --- ABA 5: FINALIZAR ATIVO (PROVA) ---
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
                with st.status("Sincronizando...") as status:
                    v_total_num = st.session_state.get('av_valor_total', 10.0)
                    identificador = f"{v_tipo} - {v_ano}º Ano ({trim_av})"
                    db.excluir_avaliacao_completa(identificador, v_tipo)
                    
                    # Geração Regular
                    v_por_quest_reg = v_total_num / v_qtd
                    info_reg = {"ano": f"{v_ano}º", "tipo_prova": v_tipo, "valor": util.sosa_to_str(v_total_num), "valor_questao": util.sosa_to_str(v_por_quest_reg), "qtd_questoes": v_qtd, "trimestre": trim_av}
                    doc_reg = exporter.gerar_docx_prova_v25(nome_arq, st.session_state.temp_prova, info_reg)
                    link_reg = db.subir_e_converter_para_google_docs(doc_reg, nome_arq, modo="AVALIACAO")
                    
                    # Geração PEI
                    txt_pei = ai.extrair_tag(st.session_state.temp_prova, "PEI")
                    link_pei = "N/A"
                    if txt_pei:
                        qtd_q_pei = len(re.findall(r'QUESTÃO', txt_pei.upper()))
                        info_pei = {"ano": f"{v_ano}º", "tipo_prova": v_tipo, "valor": util.sosa_to_str(v_total_num), "valor_questao": util.sosa_to_str(v_total_num/qtd_q_pei), "qtd_questoes": qtd_q_pei, "trimestre": trim_av}
                        doc_pei = exporter.gerar_docx_prova_v25(f"{nome_arq}_PEI", txt_pei, info_pei)
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_arq}_PEI", modo="AVALIACAO")

                    db.salvar_no_banco("DB_AULAS_PRONTAS", [
                        datetime.now().strftime("%d/%m/%Y"), "AVALIAÇÃO", identificador, 
                        st.session_state.temp_prova + f"\n--- LINKS ---\nRegular({link_reg}) PEI({link_pei})", f"{v_ano}º", link_reg
                    ])
                    status.update(label="✅ Ativo Salvo!", state="complete"); st.balloons(); time.sleep(1.5); reset_avaliacoes()

    # --- ABA 6: ACERVO (RESTAURADA COM TODOS OS BOTÕES) ---
    with tab_acervo:
        st.markdown("#### 📄 Repositório de Ativos de Safra")
        df_exames = df_aulas[df_aulas['SEMANA_REF'].isin(["AVALIAÇÃO", "REVISÃO"])].iloc[::-1]
        if not df_exames.empty:
            for _, row in df_exames.iterrows():
                with st.container(border=True):
                    st.markdown(f"**{row['TIPO_MATERIAL']}**")
                    txt_f = str(row['CONTEUDO'])
                    
                    # Extração de Links via Regex
                    l_reg = re.search(r"Regular\((.*?)\)", txt_f).group(1) if "Regular(" in txt_f else (re.search(r"Aluno\((.*?)\)", txt_f).group(1) if "Aluno(" in txt_f else row.get('LINK_DRIVE'))
                    l_pei = re.search(r"PEI\((.*?)\)", txt_f).group(1) if "PEI(" in txt_f and "PEI(N/A)" not in txt_f else None
                    l_prof = re.search(r"Prof\((.*?)\)", txt_f).group(1) if "Prof(" in txt_f else None

                    c_b1, c_b2, c_b3, c_b4, c_b5 = st.columns([1, 1, 1, 1, 1])
                    if l_reg: c_b1.link_button("📝 REGULAR", str(l_reg), use_container_width=True)
                    if l_pei: c_b2.link_button("♿ PEI", str(l_pei), use_container_width=True)
                    else: c_b2.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                    if l_prof: c_b3.link_button("👨‍🏫 PROF", str(l_prof), use_container_width=True)
                    else: c_b3.button("⚪ SEM PROF", disabled=True, use_container_width=True)
                    
                    if c_b4.button("🔄 REFINAR", key=f"ref_av_{row.name}", use_container_width=True):
                        st.session_state.temp_prova = txt_f
                        st.rerun()
                    if c_b5.button("🗑️ APAGAR", key=f"del_av_{row.name}", use_container_width=True):
                        db.excluir_avaliacao_completa(row['TIPO_MATERIAL'], "AVALIAÇÃO"); st.rerun()
        else: st.info("📭 Nenhum exame no acervo.")

# --- ABA 1: CAPTURA (V41.2 - BLINDAGEM CONTRA INDEXERROR) ---
        with tab_captura:
            st.subheader(f"Captura de Evidências: {f_ativo}")
            
            # 1. LEGENDA DE PERÍCIA
            with st.expander("ℹ️ LEGENDA DE MARCAÇÕES (SOSA V29)"):
                st.markdown("| Símbolo | Significado |\n| :--- | :--- |\n| **A, B, C, D, E** | Marcação Única |\n| **X** | Dupla Marcação / Rasura |\n| **?** | Questão em Branco |")

            # Filtra alunos pendentes
            escaneados = df_diagnosticos[df_diagnosticos['ID_AVALIACAO'] == f_ativo]['ID_ALUNO'].astype(str).tolist()
            alunos_pendentes = df_alunos[(df_alunos['TURMA'] == f_turma) & (~df_alunos['ID'].astype(str).isin(escaneados))]
            
            if alunos_pendentes.empty:
                st.success("✅ Todos os alunos desta turma já foram escaneados!")
            else:
                c_a1, c_a2 = st.columns([2, 1])
                aluno_sel = c_a1.selectbox("👤 Selecione o Aluno:", alunos_pendentes['NOME_ALUNO'].tolist())
                aluno_info = alunos_pendentes[alunos_pendentes['NOME_ALUNO'] == aluno_sel].iloc[0]
                
                # --- VACINA DE MEMÓRIA: Limpa scan antigo se mudar o aluno ---
                if "last_aluno_scanned" not in st.session_state: st.session_state.last_aluno_scanned = aluno_sel
                if st.session_state.last_aluno_scanned != aluno_sel:
                    if "current_scan_res" in st.session_state: del st.session_state.current_scan_res
                    st.session_state.last_aluno_scanned = aluno_sel

                # DETECÇÃO PEI E EXTRAÇÃO DE GABARITO
                is_pei_aluno = str(aluno_info['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"]
                tag_gab = "GABARITO_PEI" if is_pei_aluno else "GABARITO"
                gab_raw = ai.extrair_tag(txt_ativo, tag_gab) or ai.extrair_tag(txt_ativo, "GABARITO_TEXTO") or ai.extrair_tag(txt_ativo, "GABARITO")
                
                # Motor de Precisão Híbrido
                matches = re.findall(r"^(?:QUESTÃO\s+)?(\d+)[\s\.\)\-:]*([A-E])", gab_raw.upper(), re.MULTILINE)
                gab_dict = {num: let for num, let in matches}
                gab_oficial = [gab_dict[num] for num in sorted(gab_dict.keys())]
                qtd_q = len(gab_oficial)

                if qtd_q == 0:
                    st.error("❌ Erro: Gabarito não localizado. Verifique as tags no material.")
                else:
                    st.warning(f"📋 Perfil: {'♿ PEI' if is_pei_aluno else '📝 REGULAR'} | Questões: {qtd_q}")
                    img_file = st.camera_input(f"📸 Scan: {aluno_sel}")
                    
                    if img_file:
                        if st.button("🧠 ANALISAR COM GEMINI 2.5 PRO", type="primary", use_container_width=True):
                            with st.spinner("Perito Sosa analisando..."):
                                res_json = ai.analisar_gabarito_vision(img_file.getvalue())
                                
                                # Busca insistente no JSON (Garante que res_lista tenha o tamanho exato de qtd_q)
                                res_lista = []
                                for i in range(qtd_q):
                                    q_num_longo = f"{i+1:02d}"
                                    q_num_curto = str(i+1)
                                    valor_lido = res_json.get(q_num_longo, res_json.get(q_num_curto, "?"))
                                    res_lista.append(valor_lido)
                                
                                st.session_state.current_scan_res = res_lista
                                st.session_state.current_scan_img = img_file.getvalue()
                                st.rerun()

                # --- MESA DE PERÍCIA IMEDIATA (COM BLINDAGEM DE ÍNDICE) ---
                if "current_scan_res" in st.session_state:
                    # Verifica se o scan na memória bate com a quantidade de questões atual
                    if len(st.session_state.current_scan_res) != qtd_q:
                        st.warning("⚠️ O número de questões mudou. Por favor, realize o scan novamente.")
                        if st.button("🔄 RESETAR SCAN"):
                            del st.session_state.current_scan_res
                            st.rerun()
                    else:
                        st.markdown("---")
                        st.subheader("🔍 Mesa de Perícia Imediata")
                        dados_pericia = []
                        for i in range(qtd_q):
                            # Blindagem final: usa .get ou check de segurança
                            lido = st.session_state.current_scan_res[i]
                            certo = gab_oficial[i]
                            status = "✅" if lido == certo else "❌"
                            if lido == "X": status = "🚫 DUPLA"
                            if lido == "?": status = "⚪ VAZIA"
                            dados_pericia.append({"Q": f"{i+1:02d}", "Lido": lido, "Oficial": certo, "Status": status})
                        
                        df_mesa = st.data_editor(pd.DataFrame(dados_pericia), hide_index=True, use_container_width=True,
                            column_config={"Lido": st.column_config.SelectboxColumn("Correção", options=["A", "B", "C", "D", "E", "X", "?"], required=True)})
                        
                        novas_respostas = df_mesa["Lido"].tolist()
                        acertos_rev = sum(1 for i, r in enumerate(novas_respostas) if r == gab_oficial[i])
                        nota_rev = (acertos_rev / qtd_q) * valor_total_ativo if qtd_q > 0 else 0
                        st.metric("Nota Final Revisada", f"{nota_rev:.2f}", delta=f"{acertos_rev}/{qtd_q} acertos")

                        c_b1, c_b2 = st.columns(2)
                        if c_b1.button("💾 CONFIRMAR E ENVIAR AO HUB", type="primary", use_container_width=True):
                            prefixo = "[PEI]" if is_pei_aluno else "[REGULAR]"
                            db.salvar_no_banco("DB_GABARITOS_ALUNOS", [datetime.now().strftime("%d/%m/%Y"), aluno_info['ID'], aluno_sel, f_turma, f_ativo, ";".join(novas_respostas), util.sosa_to_str(nota_rev), f"{prefixo} Scan"])
                            st.success("✅ Enviado!"); del st.session_state.current_scan_res; st.rerun()
                        if c_b2.button("🗑️ DESCARTAR SCAN", use_container_width=True):
                            del st.session_state.current_scan_res; st.rerun()

        # --- ABA 2: HUB DE HOMOLOGAÇÃO (RECALCULO AUTOMÁTICO) ---
        with tab_conferencia:
            st.subheader(f"⚖️ Conferência: {f_turma}")
            
            # Função interna para limpar gabarito usando o novo Regex Híbrido
            def limpar_gab_hibrido(raw):
                m = re.findall(r"^(?:QUESTÃO\s+)?(\d+)[\s\.\)\-:]*([A-E])", raw.upper(), re.MULTILINE)
                d = {num: let for num, let in m}
                return [d[num] for num in sorted(d.keys())]

            gab_reg_list = limpar_gab_hibrido(ai.extrair_tag(txt_ativo, "GABARITO"))
            gab_pei_list = limpar_gab_hibrido(ai.extrair_tag(txt_ativo, "GABARITO_PEI") or ai.extrair_tag(txt_ativo, "GABARITO"))

            st.info(f"✅ **Gabarito Regular:** {' '.join(gab_reg_list)}")
            if gab_pei_list != gab_reg_list:
                st.warning(f"♿ **Gabarito PEI:** {' '.join(gab_pei_list)}")

            alunos_turma = df_alunos[df_alunos['TURMA'] == f_turma].sort_values(by="NOME_ALUNO")
            gabaritos_lidos = df_diagnosticos[df_diagnosticos['ID_AVALIACAO'] == f_ativo]
            
            dados_grade = []
            for _, alu in alunos_turma.iterrows():
                id_a = str(alu['ID'])
                leitura = gabaritos_lidos[gabaritos_lidos['ID_ALUNO'].astype(str) == id_a]
                is_pei = str(alu['NECESSIDADES']).upper() not in ["NENHUMA", "PENDENTE", "", "NAN"]
                
                status = "⚪ Pendente"
                respostas = ""
                nota_exibida = 0.0
                
                if not leitura.empty:
                    status = "🔵 Aguardando"
                    respostas = leitura.iloc[0]['RESPOSTAS_ALUNO']
                    nota_exibida = util.sosa_to_float(leitura.iloc[0]['NOTA_CALCULADA'])
                
                dados_grade.append({
                    "ID": id_a,
                    "ALUNO": f"♿ {alu['NOME_ALUNO']}" if is_pei else alu['NOME_ALUNO'],
                    "STATUS": status,
                    "MARCAÇÕES LIDAS": respostas,
                    "GABARITO ALVO": " ".join(gab_pei_list) if is_pei else " ".join(gab_reg_list),
                    "NOTA/BÔNUS": nota_exibida,
                    "OCORRÊNCIA": "Nenhuma"
                })
            
            df_auditoria = st.data_editor(
                pd.DataFrame(dados_grade),
                column_config={
                    "ID": None, "STATUS": st.column_config.TextColumn("Perícia", width="small", disabled=True),
                    "ALUNO": st.column_config.TextColumn("Estudante", width="medium", disabled=True),
                    "MARCAÇÕES LIDAS": st.column_config.TextColumn("Respostas (A;B;X;?)", width="medium"),
                    "GABARITO ALVO": st.column_config.TextColumn("Gabarito Oficial", width="medium", disabled=True),
                    "OCORRÊNCIA": st.column_config.SelectboxColumn("Tag", options=["Nenhuma", "FALTOU", "ANULADA - PESCA", "REVISÃO"]),
                    "NOTA/BÔNUS": st.column_config.NumberColumn("Nota Final", format="%.2f")
                },
                hide_index=True, use_container_width=True, key=f"ed_auditoria_{v}"
            )
            
            if st.button("🚀 HOMOLOGAR E ENVIAR PARA BOLETIM", type="primary", use_container_width=True):
                with st.status("Homologando...") as status:
                    lista_oficial = []
                    for _, row in df_auditoria.iterrows():
                        if row['STATUS'] == "🔵 Aguardando" or row['OCORRÊNCIA'] != "Nenhuma":
                            res_prof = row['MARCAÇÕES LIDAS'].split(";")
                            gab_alvo = row['GABARITO ALVO'].split(" ")
                            acertos = sum(1 for i, r in enumerate(res_prof) if i < len(gab_alvo) and r.upper() == gab_alvo[i].upper())
                            nota_final = (acertos / len(gab_alvo)) * valor_total_ativo if gab_alvo else 0.0
                            if row['OCORRÊNCIA'] in ["FALTOU", "ANULADA - PESCA"]: nota_final = 0.0
                            
                            if not is_sonda:
                                col_teste = util.sosa_to_str(nota_final) if "TESTE" in f_ativo.upper() else "0,0"
                                col_prova = util.sosa_to_str(nota_final) if "PROVA" in f_ativo.upper() else "0,0"
                                lista_oficial.append([row['ID'], row['ALUNO'].replace("♿ ", ""), f_turma, f_trim, "0,0", col_teste, col_prova, "0,0", "0,0"])
                            else:
                                lista_oficial.append([datetime.now().strftime("%d/%m/%Y"), row['ID'], row['ALUNO'].replace("♿ ", ""), f_turma, "TRUE", "SONDA", f_ativo, util.sosa_to_str(nota_final)])
                    
                    if db.homologar_notas_lote(lista_oficial, "TESTE" if not is_sonda else "SONDA"):
                        status.update(label="✅ Homologação Concluída!", state="complete"); st.balloons()
