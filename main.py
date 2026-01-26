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
import exporter  # Novo módulo de design DOCX
import re  

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
wb, (df_alunos, df_curriculo, df_materiais, df_planos, df_aulas, df_notas, df_diario, df_turmas, df_relatorios, df_horarios, df_registro_aulas) = db.carregar_tudo()

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
    "🤖 Maestro Dashboard",
    "📅 Planejamento (Ponto ID)",
    "🧪 Criador de Aulas",
    "📝 Diário de Bordo Rápido",
    "📊 Painel de Notas & Vistos",
    "📈 Boletim Anual & Conselho",
    "👥 Gestão da Turma",
    "📚 Base de Conhecimento",
    "♿ Relatórios PEI / Perfil IA"
])

# Função Auxiliar de Visualização com Aba de Exportação Profissional
def exibir_material_estruturado(texto_raw, key_prefix):
    # Criamos as 5 abas. A variável t_exp nasce aqui.
    t1, t2, t3, t4, t_exp = st.tabs(["✍️ Lousa/Slides", "📄 Folha", "✅ Gabarito", "🎨 Imagens", "📥 EXPORTAR"])
    
    with t1:
        st.text_area("Conteúdo Principal:", ai.extrair_tag(texto_raw, "LOUSA"), height=400, key=f"{key_prefix}_lousa_txt")
    with t2:
        st.text_area("Atividade:", ai.extrair_tag(texto_raw, "FOLHA"), height=400, key=f"{key_prefix}_folha_txt")
    with t3:
        st.text_area("Gabarito:", ai.extrair_tag(texto_raw, "GABARITO"), height=200, key=f"{key_prefix}_gab_txt")
    with t4:
        st.text_area("Prompts:", ai.extrair_tag(texto_raw, "IMAGENS"), height=150, key=f"{key_prefix}_img_txt")
    
    # ABA DE EXPORTAÇÃO (Onde estavam os erros)
    with t_exp:
        st.subheader("🚀 Exportar Plano Oficial")
        
        # Organizamos os dados limpos para o exportador
        dados_para_word = {
            "geral": c_geral,
            "especificos": c_espec,
            "objetivos": objs_edit,
            "metodologia": met_edit,
            "avaliacao": ava_edit,
            "observacao": obs_edit,
            "pei": pei_edit
        }
        
        nome_doc = st.text_input("Título do Arquivo:", value=f"PLANO_{ano_p}ANO_{sem_p.split(' ')[1]}", key="v18_name_plan_final")
        
        # Chamamos a nova função de design de PLANO
        doc_file = exporter.gerar_docx_plano_oficial(
            nome_doc.upper(), 
            dados_para_word, 
            {"turma": f"{ano_p}º Ano", "trimestre": "I"}
        )
        
        st.download_button("📥 BAIXAR PLANO (WORD)", doc_file, f"{nome_doc}.docx", use_container_width=True)

        st.markdown("---")
        st.write("🛰️ **Opção Nuvem (Google Drive)**")
        
        if st.button("☁️ Enviar e Gerar Link no Drive", key=f"btn_drive_{key_prefix}"):
            with st.spinner("Sincronizando com as pastas do Drive..."):
                # Identifica o tipo para a subpasta
                tipo_mat = "Outros"
                if "lousa" in key_prefix.lower(): tipo_mat = "Lousa e Slides"
                elif "av" in key_prefix.lower(): tipo_mat = "Atividades Avulsas"
                elif "prova" in key_prefix.lower(): tipo_mat = "Avaliações (Regular)"
                elif "adapt" in key_prefix.lower(): tipo_mat = "Avaliação Adaptada (PEI)"

                trim_atual, _ = util.obter_info_trimestre(date.today())
                
                link = db.subir_e_converter_para_google_docs(
                    doc_file, 
                    nome_doc, 
                    trimestre=trim_atual,
                    categoria="Material de Sala",
                    sub_categoria=tipo_mat
                )
                
                if "https://" in str(link):
                    st.success("✅ Arquivo salvo e convertido!")
                    # Exibe o link de duas formas para garantir
                    st.link_button("🚀 ABRIR NO GOOGLE DOCS", str(link), use_container_width=True)
                    st.markdown(f"🔗 [Clique aqui se o botão não abrir]({link})")
                else:
                    st.error(f"Erro na Ponte: {link}")


# ==============================================================================
# MÓDULO: DASHBOARD INTELIGENTE (V6 - FULL CONTEXT: NOTAS + PDF + AULAS CRIADAS)
# ==============================================================================
if menu == "🤖 Maestro Dashboard":
    st.title("🤖 Maestro Dashboard | Central de Inteligência")
    st.markdown("---")

    # --- 1. FUNÇÃO DE LIMPEZA DE NOTAS (NORMALIZAÇÃO RECURSIVA) ---
    def normalizar_nota_agressiva(valor):
        """
        Garante matematicamente que a nota fique entre 0 e 10.
        Usa loop while para corrigir erros como 718 -> 71.8 -> 7.18
        """
        try:
            # Limpeza básica de string
            s_val = str(valor).replace(',', '.').strip()
            if not s_val or s_val.lower() == 'nan': return 0.0
            
            f_val = float(s_val)
            
            # Loop de correção: Enquanto for maior que 10, divide por 10
            while f_val > 10.0:
                f_val = f_val / 10.0
                
            return f_val
        except:
            return 0.0

    # --- 2. PREPARAÇÃO DOS DADOS (CONTEXTO GLOBAL) ---
    def montar_contexto_global():
        ctx = "DADOS ESTRUTURADOS DO SISTEMA (ITABUNA 2026):\n\n"
        
        # A. Tempo
        hoje = datetime.now()
        inicio_aulas = datetime(2026, 2, 2)
        if hoje < inicio_aulas:
            ctx += f"DATA HOJE: {hoje.strftime('%d/%m/%Y')} (Período de Planejamento).\n\n"
        else:
            semana_num = int((hoje - inicio_aulas).days / 7) + 1
            trimestre_atual, _ = util.obter_info_trimestre(hoje.date())
            ctx += f"DATA HOJE: {hoje.strftime('%d/%m/%Y')} (Semana {semana_num}, {trimestre_atual}).\n\n"

        # B. Alunos
        if not df_alunos.empty:
            total = len(df_alunos)
            peis = df_alunos[df_alunos['NECESSIDADES'] != 'NENHUMA']
            lista_peis = ", ".join([f"{r['NOME_ALUNO']} ({r['NECESSIDADES']})" for _, r in peis.iterrows()])
            ctx += f"TURMA: {total} alunos. PEI: {lista_peis}.\n"
        
        # C. Notas (NORMALIZAÇÃO AGRESSIVA)
        if not df_notas.empty:
            ctx += "BOLETIM (Notas Normalizadas 0-10):\n"
            for _, row in df_notas.iterrows():
                nome = row['NOME_ALUNO']
                n_visto = normalizar_nota_agressiva(row.get('NOTA_VISTOS', 0))
                n_teste = normalizar_nota_agressiva(row.get('NOTA_TESTE', 0))
                n_prova = normalizar_nota_agressiva(row.get('NOTA_PROVA', 0))
                n_media = normalizar_nota_agressiva(row.get('MEDIA_FINAL', 0))
                
                ctx += f"- {nome}: Média {n_media:.1f} (Vistos: {n_visto}, Teste: {n_teste}, Prova: {n_prova})\n"
            ctx += "\n"

        # D. Planejamento
        if not df_planos.empty:
            planos_prox = df_planos.tail(3) 
            resumo_planos = " | ".join([f"Semana {r['SEMANA']}: {ai.extrair_tag(r['PLANO_TEXTO'], 'CONTEUDOS_ESPECIFICOS')}" for _, r in planos_prox.iterrows()])
            ctx += f"PLANEJAMENTO RECENTE: {resumo_planos}.\n"

        # E. Diário
        if not df_diario.empty:
            ultimos = df_diario.tail(20)
            ocorrencias = []
            for _, r in ultimos.iterrows():
                tags = str(r['TAGS'])
                obs = str(r['OBSERVACOES'])
                if (tags and tags != "nan" and tags != "") or (obs and obs != "nan" and obs != ""):
                    ocorrencias.append(f"{r['DATA']} - {r['NOME_ALUNO']}: {tags} | {obs}")
            ctx += f"DIÁRIO (Ocorrências): {'; '.join(ocorrencias)}.\n"

        # F. Materiais Criados (NOVA INTEGRAÇÃO)
        if not df_aulas.empty:
            # Pega os últimos 5 materiais criados para dar contexto do que já foi feito
            ultimos_mats = df_aulas.tail(5)
            lista_mats = []
            for _, r in ultimos_mats.iterrows():
                # Pega um resumo do conteúdo para não estourar o limite de texto
                resumo_conteudo = str(r['CONTEUDO'])[:150].replace('\n', ' ') + "..."
                lista_mats.append(f"[{r['DATA']}] Tipo: {r['TIPO_MATERIAL']} (Ref: {r['SEMANA_REF']}) -> Conteúdo: {resumo_conteudo}")
            
            ctx += f"MATERIAIS JÁ CRIADOS PELO PROFESSOR (Histórico): {'; '.join(lista_mats)}.\n"

        return ctx

    # --- 3. VISUALIZAÇÃO DE KPIs (CARTÕES) ---
    col_kpi1, col_kpi2, col_kpi3, col_kpi4 = st.columns(4)

    # KPI 1: Total Alunos
    col_kpi1.metric("👥 Total de Alunos", len(df_alunos) if not df_alunos.empty else 0)

    # KPI 2: Alunos PEI
    total_pei = len(df_alunos[df_alunos['NECESSIDADES'] != 'NENHUMA']) if not df_alunos.empty else 0
    col_kpi2.metric("♿ Alunos PEI/AEE", total_pei)

    # KPI 3: Média Geral
    media_turma = 0.0
    delta_media = "Sem dados"
    if not df_notas.empty:
        notas_corrigidas = df_notas['MEDIA_FINAL'].apply(normalizar_nota_agressiva)
        media_turma = notas_corrigidas.mean()
        delta_media = "Na média" if media_turma >= 6.0 else "Abaixo da meta"
    
    col_kpi4.metric("📊 Média Geral (Rede)", f"{media_turma:.1f}", delta=delta_media)

    # KPI 4: Risco
    risco = 0
    if not df_notas.empty:
        risco = len(df_notas[df_notas['MEDIA_FINAL'].apply(normalizar_nota_agressiva) < 6.0])
    col_kpi4.metric("🚨 Risco (Notas < 6.0)", risco, delta_color="inverse")


    # --- 4. CHAT COM VISÃO DE ARQUIVOS (PDFs) ---
    st.markdown("### 💬 Converse com o Sistema")
    
    # PREPARAÇÃO DOS ARQUIVOS (PDFs)
    arquivos_para_ia = []
    nomes_arquivos = []
    if not df_materiais.empty:
        for _, row in df_materiais.iterrows():
            uri = row['URI_ARQUIVO']
            nome = row['NOME_ALUNO'] if 'NOME_ALUNO' in row else row['NOME_ARQUIVO'] 
            nomes_arquivos.append(nome)
            arquivos_para_ia.append(types.Part.from_uri(file_uri=uri, mime_type="application/pdf"))
    
    # Feedback Visual
    if arquivos_para_ia:
        st.success(f"📚 **Biblioteca Conectada:** O Maestro está lendo {len(arquivos_para_ia)} livro(s): {', '.join(nomes_arquivos)}")
    else:
        st.warning("⚠️ Nenhum livro PDF encontrado na Base de Conhecimento. O Chat só lerá as planilhas.")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ex: 'O que eu criei na semana passada?', 'Resuma a página 23 do livro'"):
        st.chat_message("user").markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner("Processando planilhas, materiais criados e lendo livros..."):
                
                contexto_dados = montar_contexto_global()
                
                # PROMPT REFORÇADO
                prompt_final = (
                    f"VOCÊ É O MAESTRO SOSA, O SISTEMA CENTRAL DA ESCOLA.\n"
                    f"IMPORTANTE: Você recebeu arquivos PDF anexos (Livros Didáticos). "
                    f"SE A PERGUNTA FOR SOBRE CONTEÚDO, PÁGINAS OU EXERCÍCIOS, LEIA O PDF ANEXO IMEDIATAMENTE.\n"
                    f"NÃO DIGA QUE NÃO TEM ACESSO. OS ARQUIVOS ESTÃO NO SEU CONTEXTO.\n\n"
                    f"DADOS DAS PLANILHAS (NOTAS/DIÁRIO/MATERIAIS CRIADOS):\n{contexto_dados}\n\n"
                    f"PERGUNTA DO PROFESSOR: {prompt}"
                )
                
                # Envia Prompt + Arquivos
                resposta = ai.gerar_ia("MAESTRO", prompt_final, partes_arquivos=arquivos_para_ia)
                
                st.markdown(resposta)
        
        st.session_state.messages.append({"role": "assistant", "content": resposta})

# ==============================================================================
# MÓDULO: LABORATÓRIO DE MATERIAIS V24.4 (ESTABILIDADE TOTAL)
# ==============================================================================
elif menu == "🧪 Criador de Aulas":
    st.header("🧪 Laboratório de Materiais (V24)")
    
    tab_criar, tab_gavetas = st.tabs(["🚀 Criar Novo Material", "🗂️ Gavetas de Materiais"])

    if "v_lab" not in st.session_state: st.session_state.v_lab = 1

    with tab_criar:
        st.subheader("1. Vínculo com Planejamento")
        c1, c2, c3 = st.columns([1, 2, 1])
        ano_lab = c1.selectbox("Série:", [6, 7, 8, 9], key="lab_ano_v24")
        planos_ano = df_planos[df_planos['ANO'] == f"{ano_lab}º"]
        
        if planos_ano.empty:
            st.warning("⚠️ Crie um plano primeiro.")
        else:
            sem_lab = c2.selectbox("Semana:", planos_ano['SEMANA'].tolist(), key="lab_sem_v24")
            aula_num = c3.radio("Foco:", ["Aula 1", "Aula 2"], horizontal=True)
            plano_raw = planos_ano[planos_ano['SEMANA'] == sem_lab].iloc[0]['PLANO_TEXTO']
            
            df_base_ano = df_curriculo[df_curriculo['ANO'] == ano_lab]
            cont_no_plano = ai.extrair_tag(plano_raw, "CONTEUDOS_ESPECIFICOS").upper()
            opcoes_conteudo = [c for c in df_base_ano['CONTEUDO_ESPECIFICO'].unique() if str(c).upper() in cont_no_plano]

            col_p1, col_p2 = st.columns(2)
            sel_cont = col_p1.multiselect("Conteúdos:", options=opcoes_conteudo, key=f"v24_c_{sem_lab}")
            sel_obj = col_p2.multiselect("Objetivos:", options=df_base_ano[df_base_ano['CONTEUDO_ESPECIFICO'].isin(sel_cont)]['OBJETIVOS'].unique() if sel_cont else [], key=f"v24_o_{sem_lab}")

            st.markdown("---")
            st.subheader("2. Parâmetros de Precisão")
            cp1, cp2, cp3 = st.columns(3)
            formato = cp1.radio("Formato:", ["Quadro (Lousa)", "Slides (Apresentação)"])
            qtd_q = cp2.slider("Quantidade de Questões:", 1, 15, 4)
            nivel = cp3.select_slider("Nível:", options=["Básico", "Intermediário", "Desafio"])
            instr = st.text_area("Instruções Adicionais:", placeholder="Ex: Use contexto de Itabuna...")

            if st.button("🚀 COMPILAR MATERIAL DA " + aula_num.upper(), use_container_width=True, type="primary"):
                with st.spinner("IA executando Protocolo de Choque..."):
                    prompt_v24 = (f"ORDEM: GERAR EXATAMENTE {qtd_q} QUESTÕES DE EXERCÍCIO.\n"
                                 f"FOCO: {ano_lab}º ANO, {sem_lab}, {aula_num}.\n"
                                 f"CONTEÚDOS: {sel_cont}\nOBJETIVOS: {sel_obj}\n"
                                 f"FORMATO: {formato}\nNÍVEL: {nivel}\nCONTEXTO: {instr}")
                    st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", prompt_v24)
                    st.session_state.v_lab += 1
                    if "lab_pei" in st.session_state: del st.session_state.lab_pei
                    st.rerun()

        # --- AMBIENTE DE EDIÇÃO (SÓ APARECE SE HOUVER TEXTO) ---
        if "lab_temp" in st.session_state:
            st.markdown("---")
            v = st.session_state.v_lab
            txt_bruto = st.session_state.lab_temp

            # EXTRAÇÃO ANTES DAS ABAS (Garante que os dados não sumam)
            ed_prof = ai.extrair_tag(txt_bruto, "PROFESSOR")
            ed_alu = ai.extrair_tag(txt_bruto, "ALUNO")
            ed_gab = ai.extrair_tag(txt_bruto, "GABARITO")

            st.subheader("🤖 Refinador Cirúrgico")
            cmd_refine = st.chat_input("Comando (Ex: 'Remova a questão 3')...", key=f"chat_lab_{v}")
            if cmd_refine:
                with st.spinner("Refinando..."):
                    st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"ATUAL:\n{txt_bruto}\nORDEM: {cmd_refine}")
                    st.session_state.v_lab += 1
                    st.rerun()

            t_prof, t_alu, t_pei, t_exp = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "♿ PEI (Adaptada)", "📥 EXPORTAR"])
            
            with t_prof:
                st.text_area("Roteiro Professor:", ed_prof, height=400, key=f"area_prof_{v}")
            with t_alu:
                st.text_area("Folha Aluno:", ed_alu, height=400, key=f"area_alu_{v}")
            with t_pei:
                if st.button("♿ Gerar Engenharia PEI V24"):
                    with st.spinner("Calculando redução..."):
                        import re
                        questoes = re.findall(r'\d+\.', ed_alu)
                        meta = min(5, max(1, len(questoes) // 2))
                        prompt_pei = f"MATERIAL ORIGINAL:\n{ed_alu}\n\nORDEM: Gere folha independente com EXATAMENTE {meta} QUESTÕES ADAPTADAS."
                        st.session_state.lab_pei = ai.gerar_ia("ARQUITETO_PEI_V24", prompt_pei)
                        st.rerun()
                
                txt_pei_raw = st.session_state.get('lab_pei', '')
                st.text_area("Versão Adaptada:", ai.extrair_tag(txt_pei_raw, "PEI"), height=400, key=f"area_pei_{v}")

            with t_exp:
                st.subheader("📥 Downloads e Nuvem")
                nome_base = f"AULA_{aula_num.replace(' ','')}_{ano_lab}ANO_{sem_lab.split(' ')[1]}"
                c_exp1, c_exp2 = st.columns(2)
                with c_exp1:
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_base, ed_alu, {"ano": f"{ano_lab}º", "trimestre": "I"})
                    st.download_button("📥 Baixar Folha Aluno", doc_alu, f"{nome_base}_ALUNO.docx", use_container_width=True, key=f"dl_alu_{v}")
                    if st.button("☁️ Salvar Aluno no Drive", key=f"drv_alu_{v}"):
                        link = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_base}_ALUNO", categoria="Material de Sala", sub_categoria="Folha Aluno")
                        if "https" in str(link):
                            db.salvar_link_na_planilha("DB_AULAS_PRONTAS", "SEMANA_REF", sem_lab, link)
                            st.success("✅ Salvo!"); st.link_button("Abrir", str(link))
                with c_exp2:
                    doc_prof = exporter.gerar_docx_professor_v24(nome_base, ed_prof, {"ano": f"{ano_lab}º", "semana": sem_lab})
                    st.download_button("📥 Baixar Guia Prof", doc_prof, f"{nome_base}_PROF.docx", use_container_width=True, key=f"dl_prof_{v}")
                    if st.button("☁️ Salvar Guia no Drive", key=f"drv_prof_{v}"):
                        link = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_base}_PROF", categoria="Material de Sala", sub_categoria="Guia Professor")
                        st.success("✅ Salvo!"); st.link_button("Abrir", str(link))

            if st.button("🗑️ DESCARTAR E RECOMEÇAR", use_container_width=True):
                if "lab_temp" in st.session_state: del st.session_state.lab_temp
                st.rerun()

    # --- ABA 2: GAVETAS DE MATERIAIS ---
    with tab_gavetas:
        st.subheader("🗂️ Gavetas de Materiais Produzidos")
        if df_aulas.empty:
            st.info("📭 Vazio.")
        else:
            c_gav1, c_gav2 = st.columns(2)
            gaveta_sel = c_gav1.selectbox("Gaveta:", ["Folha Aluno", "Guia Professor", "Lousa e Slides"])
            ano_gav = c_gav2.selectbox("Ano:", ["Todos", "6º", "7º", "8º", "9º"], key="gav_ano_v24")
            
            df_g = df_aulas.copy()
            if ano_gav != "Todos": df_g = df_g[df_g['ANO'].str.contains(ano_gav, na=False)]
            
            if not df_g.empty:
                for _, row in df_g.iloc[::-1].iterrows():
                    with st.expander(f"📅 {row['DATA']} | {row['SEMANA_REF']}"):
                        if row['LINK_DRIVE']: st.link_button("🚀 ABRIR", str(row['LINK_DRIVE']), use_container_width=True)
                        if st.button("🗑️ Excluir", key=f"del_{row.name}"):
                            db.excluir_registro("DB_AULAS_PRONTAS", row['CONTEUDO'])
                            st.rerun()
                            
# ==============================================================================
# MÓDULO: PLANEJAMENTO (PONTO ID) - ARQUITETURA DE ELITE V23
# ==============================================================================
elif menu == "📅 Planejamento (Ponto ID)":
    st.header("📅 Planejador Estratégico (Ponto ID)")

    # --- 1. FUNÇÕES DE LIMPEZA E PRENSA (ESCOPO GLOBAL DO MÓDULO) ---
    def limpar_v23(texto, label):
        if not texto: return ""
        # Remove o rótulo e limpa caracteres residuais como ":"
        t = texto.replace(label, "").replace(label.upper(), "").replace(label.lower(), "").strip()
        if t.startswith(":") or t.startswith(" :"): t = t[1:].strip()
        return t

    # --- 2. ABAS PRINCIPAIS ---
    tab_gerar, tab_hist, tab_curso, tab_mapa = st.tabs([
        "✨ Gerar Novo Plano", "🗂️ Histórico Detalhado", "📚 Plano de Curso Vivo", "📊 Mapa de Cobertura"
    ])
    
    with tab_gerar:
        st.subheader("1. Configuração da Aula")
        col_cfg1, col_cfg2 = st.columns([1, 2])
        
        def reset_plano():
            if "p_temp" in st.session_state: del st.session_state.p_temp
            if "v_plano" in st.session_state: st.session_state.v_plano = 1

        ano_p = col_cfg1.selectbox("Ano/Série:", [6, 7, 8, 9], key="v23_ano_sel", on_change=reset_plano)
        
        semanas_ocupadas = []
        if not df_planos.empty and 'ANO' in df_planos.columns:
            semanas_ocupadas = df_planos[df_planos['ANO'] == f"{ano_p}º"]['SEMANA'].tolist()
        
        todas_semanas = util.gerar_semanas()
        semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_ocupadas]
        opcoes_semana = semanas_disponiveis if semanas_disponiveis else ["✅ Todas planejadas!"]
        sem_p = col_cfg2.selectbox("Selecione a Semana Livre:", opcoes_semana, key="v23_sem_sel", on_change=reset_plano)
        
        if "✅" not in sem_p:
            modo_p = st.radio("Método de Elaboração:", ["🎛️ Manual (Banco de Dados)", "📖 Livro Didático"], horizontal=True)
            
            if modo_p == "🎛️ Manual (Banco de Dados)":
                df_f = df_curriculo[df_curriculo['ANO'] == ano_p] if not df_curriculo.empty else pd.DataFrame()
                if not df_f.empty:
                    c1, c2 = st.columns(2)
                    eixo = c1.selectbox("Eixo Temático:", df_f['EIXO'].unique())
                    cont_esp = c2.multiselect("Conteúdo (Fiel ao Banco):", df_f[df_f['EIXO'] == eixo]['CONTEUDO_ESPECIFICO'].unique())
                    objs = st.multiselect("Objetivos (Fiel ao Banco):", df_f[df_f['CONTEUDO_ESPECIFICO'].isin(cont_esp)]['OBJETIVOS'].unique())
                    ctx_fiel = f"EIXO: {eixo}\nCONTEÚDO: {', '.join(cont_esp)}\nOBJETIVOS: {', '.join(objs)}"
                else: st.error("Base curricular não encontrada.")
            else:
                sel_mat = st.multiselect("Selecione o Livro:", df_materiais['NOME_ARQUIVO'].tolist())
                pags = st.text_input("Páginas de Referência:")
                ctx_fiel = f"LIVRO: {sel_mat} | PÁGINAS: {pags}"

            strat = st.text_area("Sua Estratégia/Observação Inicial:", placeholder="Ex: Aula expositiva...")

            if st.button("🚀 Compor Planejamento com Memória", use_container_width=True):
                with st.spinner("Maestro redigindo plano..."):
                    # Busca plano anterior para continuidade
                    contexto_anterior = "Início do período letivo."
                    try:
                        num_sem_atual = int(re.search(r'Semana (\d+)', sem_p).group(1))
                        if num_sem_atual > 1:
                            sem_ant = f"Semana {num_sem_atual-1:02d}"
                            p_ant = df_planos[(df_planos['ANO'] == f"{ano_p}º") & (df_planos['SEMANA'].str.contains(sem_ant))]
                            if not p_ant.empty: contexto_anterior = p_ant.iloc[0]['PLANO_TEXTO']
                    except: pass

                    prompt = f"ANO: {ano_p}º, SEMANA: {sem_p}. DADOS FIÉIS DO BANCO: {ctx_fiel}. CONTINUIDADE: {contexto_anterior}. ESTRATÉGIA: {strat}."
                    st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt)
                    st.session_state.v_plano = 1 # Inicia versão 1
                    st.rerun()

        # --- 3. AMBIENTE DINÂMICO DE REFINAMENTO E EDIÇÃO ---
        if "p_temp" in st.session_state:
            st.markdown("---")
            if "v_plano" not in st.session_state: st.session_state.v_plano = 1
            
            # GATILHO DE REFINAMENTO (CHAT)
            st.subheader("🤖 Refinar Plano com o Maestro")
            comando_refino = st.chat_input("Diga o que deseja mudar (ex: 'Melhore a aula 2', 'Aprofunde o PEI')...", key="chat_v23")
            
            if comando_refino:
                with st.spinner("O Maestro está reescrevendo a partitura..."):
                    prompt_ajuste = (f"REESCREVA O PLANO ABAIXO.\n\nPLANO ATUAL:\n{st.session_state.p_temp}\n\n"
                                    f"SOLICITAÇÃO DO PROFESSOR: {comando_refino}\n\n"
                                    f"REGRAS: Mantenha CONTEÚDO e OBJETIVOS idênticos ao original do banco. Sem Markdown.")
                    st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_ajuste)
                    st.session_state.v_plano += 1 # MUDA A VERSÃO PARA FORÇAR REFRESH DAS CAIXAS
                    st.rerun()

            # DADOS ATUAIS E VERSÃO
            txt_exibicao = st.session_state.p_temp
            v = st.session_state.v_plano

            # ABAS DE EDIÇÃO (Cada key agora possui a versão {v})
            abas_ed = st.tabs(["📚 Conteúdos", "🎯 Objetivos", "🏫 Metodologia", "📝 Avaliação", "💡 Obs", "♿ PEI", "📥 EXPORTAR"])
            
            with abas_ed[0]:
                c_geral = st.text_input("Eixo:", limpar_v23(ai.extrair_tag(txt_exibicao, "CONTEUDO_GERAL"), "CONTEÚDO GERAL EIXO"), key=f"ed_geral_{v}")
                c_espec = st.text_area("Conteúdos:", limpar_v23(ai.extrair_tag(txt_exibicao, "CONTEUDOS_ESPECIFICOS"), "CONTEÚDOS ESPECÍFICOS"), key=f"ed_espec_{v}")
            with abas_ed[1]:
                objs_edit = st.text_area("Objetivos:", limpar_v23(ai.extrair_tag(txt_exibicao, "OBJETIVOS_ENSINO"), "OBJETIVOS DE ENSINO"), key=f"ed_objs_{v}")
            with abas_ed[2]:
                met_edit = st.text_area("Metodologia:", limpar_v23(ai.extrair_tag(txt_exibicao, "METODOLOGIA"), "METODOLOGIA"), height=350, key=f"ed_met_{v}")
            with abas_ed[3]:
                ava_edit = st.text_area("Avaliação:", limpar_v23(ai.extrair_tag(txt_exibicao, "AVALIACAO"), "AVALIAÇÃO"), key=f"ed_ava_{v}")
            with abas_ed[4]:
                obs_edit = st.text_area("Observação:", limpar_v23(ai.extrair_tag(txt_exibicao, "OBSERVACAO"), "OBSERVAÇÃO"), key=f"ed_obs_{v}")
            with abas_ed[5]:
                pei_edit = st.text_area("Adaptação PEI:", limpar_v23(ai.extrair_tag(txt_exibicao, "ADAPTACAO_PEI"), "ADAPTAÇÃO PEI"), key=f"ed_pei_{v}")
            
            with abas_ed[6]:
                st.subheader("🚀 Exportação Profissional")
                nome_doc = st.text_input("Título:", value=f"PLANO_{ano_p}ANO_{sem_p.split(' ')[1]}", key=f"v23_title_{v}")
                dados_docx = {"geral": c_geral, "especificos": c_espec, "objetivos": objs_edit, "metodologia": met_edit, "avaliacao": ava_edit, "observacao": obs_edit, "pei": pei_edit}
                doc_file = exporter.gerar_docx_plano_pedagogico_v18(nome_doc.upper(), dados_docx, {"ano": f"{ano_p}º Ano", "semana": sem_p.split(" (")[0]})
                st.download_button("📥 BAIXAR WORD", doc_file, f"{nome_doc}.docx", use_container_width=True, key=f"btn_dl_{v}")
                
                if st.button("☁️ SALVAR NO DRIVE E VINCULAR", key=f"v23_drive_{v}"):
                    with st.spinner("Arquivando..."):
                        link = db.subir_e_converter_para_google_docs(doc_file, nome_doc, categoria="Planos de Aula")
                        if "https://" in str(link):
                            # SALVA O LINK NA PLANILHA IMEDIATAMENTE
                            db.salvar_link_na_planilha("DB_PLANOS", "SEMANA", sem_p.split(" (")[0], link)
                            st.success("✅ Arquivado e Link salvo no Banco!"); st.link_button("🚀 ABRIR NO DRIVE", str(link))

            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("💾 FINALIZAR E SALVAR NO BANCO", use_container_width=True, type="primary", key=f"btn_save_{v}"):
                final_txt = f"MARKER_CONTEUDO_GERAL {c_geral} MARKER_CONTEUDOS_ESPECIFICOS {c_espec} MARKER_OBJETIVOS_ENSINO {objs_edit} MARKER_METODOLOGIA {met_edit} MARKER_AVALIACAO {ava_edit} MARKER_OBSERVACAO {obs_edit} MARKER_ADAPTACAO_PEI {pei_edit}"
                if db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_p.split(" (")[0], f"{ano_p}º", "I Trimestre", "PADRÃO", final_txt]):
                    st.success("✅ Salvo!"); del st.session_state.p_temp; del st.session_state.v_plano; time.sleep(1); st.rerun()
            if col_btn2.button("🗑️ DESCARTAR", use_container_width=True, key=f"btn_drop_{v}"):
                del st.session_state.p_temp; del st.session_state.v_plano; st.rerun()

    # --- ABA 2: HISTÓRICO DETALHADO (GESTÃO V23) ---
    with tab_hist:
        if not df_planos.empty:
            f_ano_h = st.selectbox("Filtrar por Ano:", ["Todos", "6º", "7º", "8º", "9º"], key="v23_hist_ano")
            df_h = df_planos.copy()
            if f_ano_h != "Todos": df_h = df_h[df_h['ANO'] == f_ano_h]
            
            if not df_h.empty:
                sel_h = st.selectbox("Selecione o Plano para Gestão:", df_h['SEMANA'].tolist(), key="v23_hist_sem")
                dados_linha = df_h[df_h['SEMANA'] == sel_h].iloc[0]
                raw_h = dados_linha['PLANO_TEXTO']
                link_h = dados_linha.get('LINK_DRIVE', "")
                ano_h = dados_linha['ANO']

                st.markdown(f"### 📝 Editando: {sel_h} ({ano_h})")
                
                h_tabs = st.tabs(["📚 Conteúdos", "🎯 Objetivos", "🏫 Metodologia", "📝 Avaliação", "💡 Obs", "♿ PEI", "📥 EXPORTAR & DRIVE"])
                with h_tabs[0]:
                    h_geral = st.text_input("Eixo:", limpar_v23(ai.extrair_tag(raw_h, "CONTEUDO_GERAL"), "CONTEÚDO GERAL EIXO"), key=f"h_ed_geral_{sel_h}")
                    h_espec = st.text_area("Conteúdos:", limpar_v23(ai.extrair_tag(raw_h, "CONTEUDOS_ESPECIFICOS"), "CONTEÚDOS ESPECÍFICOS"), key=f"h_ed_espec_{sel_h}")
                with h_tabs[1]:
                    h_objs = st.text_area("Objetivos:", limpar_v23(ai.extrair_tag(raw_h, "OBJETIVOS_ENSINO"), "OBJETIVOS DE ENSINO"), key=f"h_ed_objs_{sel_h}")
                with h_tabs[2]:
                    h_met = st.text_area("Metodologia:", limpar_v23(ai.extrair_tag(raw_h, "METODOLOGIA"), "METODOLOGIA"), height=300, key=f"h_ed_met_{sel_h}")
                with h_tabs[3]:
                    h_ava = st.text_area("Avaliação:", limpar_v23(ai.extrair_tag(raw_h, "AVALIACAO"), "AVALIAÇÃO"), key=f"h_ed_ava_{sel_h}")
                with h_tabs[4]:
                    h_obs = st.text_area("Observação:", limpar_v23(ai.extrair_tag(raw_h, "OBSERVACAO"), "OBSERVAÇÃO"), key=f"h_ed_obs_{sel_h}")
                with h_tabs[5]:
                    h_pei = st.text_area("Adaptação PEI:", limpar_v23(ai.extrair_tag(raw_h, "ADAPTACAO_PEI"), "ADAPTAÇÃO PEI"), key=f"h_ed_pei_{sel_h}")
                
                with h_tabs[6]:
                    st.subheader("🚀 Exportação e Nuvem")
                    nome_padrao = f"PLANO_{ano_h.replace('º','')}_{sel_h.replace(' ', '')}"
                    nome_h = st.text_input("Título do Arquivo:", value=nome_padrao, key=f"h_title_{sel_h}")
                    dados_h = {"geral": h_geral, "especificos": h_espec, "objetivos": h_objs, "metodologia": h_met, "avaliacao": h_ava, "observacao": h_obs, "pei": h_pei}
                    doc_h = exporter.gerar_docx_plano_pedagogico_v18(nome_h.upper(), dados_h, {"ano": ano_h, "semana": sel_h})
                    st.download_button("📥 BAIXAR WORD ATUALIZADO", doc_h, f"{nome_h}.docx", use_container_width=True, key=f"h_dl_{sel_h}")
                    if link_h and "https" in str(link_h):
                        st.link_button("🚀 ABRIR NO GOOGLE DOCS", str(link_h), use_container_width=True)
                    if st.button("☁️ SINCRONIZAR COM DRIVE", key=f"h_drive_{sel_h}"):
                        link = db.subir_e_converter_para_google_docs(doc_h, nome_h, categoria="Planos de Aula")
                        if "https://" in str(link):
                            db.salvar_link_na_planilha("DB_PLANOS", "SEMANA", sel_h, link)
                            st.success("✅ Sincronizado!"); st.rerun()

                st.markdown("---")
                col_g1, col_g2 = st.columns(2)
                if col_g1.button("🆙 ATUALIZAR NO BANCO", use_container_width=True, type="primary", key=f"h_up_{sel_h}"):
                    novo_raw = f"MARKER_CONTEUDO_GERAL {h_geral} MARKER_CONTEUDOS_ESPECIFICOS {h_espec} MARKER_OBJETIVOS_ENSINO {h_objs} MARKER_METODOLOGIA {h_met} MARKER_AVALIACAO {h_ava} MARKER_OBSERVACAO {h_obs} MARKER_ADAPTACAO_PEI {h_pei}"
                    if db.atualizar_plano_existente(sel_h, ano_h, novo_raw):
                        st.success("✅ Planilha Atualizada!"); time.sleep(1); st.rerun()
                if col_g2.button("🗑️ EXCLUIR PLANO", use_container_width=True, key=f"h_del_{sel_h}"):
                    if db.excluir_plano_total(sel_h, ano_h):
                        st.warning("🚨 Removido."); time.sleep(1); st.rerun()
            else: st.info("Nenhum plano encontrado.")
        else: st.info("📭 Banco de dados vazio.")

    # --- ABA 3: PLANO DE CURSO VIVO ---
    with tab_curso:
        st.markdown("### 📚 Plano de Curso Anual (Status em Tempo Real)")
        if not df_curriculo.empty:
            ano_c = st.selectbox("Série:", [6, 7, 8, 9], key="v23_curso_ano")
            df_c = df_curriculo[df_curriculo['ANO'] == ano_c].copy()
            concluidos = ""
            if not df_planos.empty:
                concluidos = " ".join(df_planos[df_planos['ANO'] == f"{ano_c}º"]['PLANO_TEXTO'].tolist()).upper()
            def check_status(cont):
                return "✅ CONCLUÍDO" if str(cont).upper() in concluidos else "⏳ PENDENTE"
            df_c['STATUS'] = df_c['CONTEUDO_ESPECIFICO'].apply(check_status)
            st.dataframe(df_c[['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO', 'STATUS']], use_container_width=True, hide_index=True)

    # --- ABA 4: MAPA DE COBERTURA ---
    with tab_mapa:
        st.subheader("📊 Auditoria de Cobertura Curricular")
        c_f1, c_f2 = st.columns(2)
        ano_mapa = c_f1.selectbox("Analisar Ano/Série:", [6, 7, 8, 9], key="v23_ano_mapa")
        trim_mapa = c_f2.selectbox("Filtrar Período:", ["Todos", "I", "II", "III"], key="v23_trim_mapa")
        if not df_curriculo.empty:
            df_m = df_curriculo[df_curriculo['ANO'] == ano_mapa].copy()
            if trim_mapa != "Todos": df_m = df_m[df_m['TRIMESTRE'] == trim_mapa]
            planejados = ""
            if not df_planos.empty:
                planejados = " ".join(df_planos[df_planos['ANO'] == f"{ano_mapa}º"]['PLANO_TEXTO'].astype(str).tolist()).upper()
            df_m['STATUS_NUM'] = df_m['CONTEUDO_ESPECIFICO'].apply(lambda x: 1 if str(x).upper() in planejados else 0)
            progresso = df_m.groupby('EIXO')['STATUS_NUM'].agg(['sum', 'count']).reset_index()
            progresso['Percentual'] = (progresso['sum'] / progresso['count'] * 100).round(1)
            col_chart, col_alerts = st.columns([2, 1])
            with col_chart:
                fig = px.bar(progresso, x='EIXO', y='Percentual', text='Percentual', title=f"Progresso: {ano_mapa}º Ano", color='Percentual', color_continuous_scale='RdYlGn', range_y=[0, 105])
                st.plotly_chart(fig, use_container_width=True)
            with col_alerts:
                st.markdown("### 🚩 Alertas")
                for _, r in progresso.iterrows():
                    if r['Percentual'] < 20: st.error(f"**{r['EIXO']}**: Crítico ({r['Percentual']}%).")
                    elif r['Percentual'] > 80: st.success(f"**{r['EIXO']}**: Quase lá!")
            st.dataframe(df_m[['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO', 'STATUS_NUM']].replace({1: "✅ DADO", 0: "⏳ PENDENTE"}), use_container_width=True, hide_index=True)

# ==============================================================================
# MÓDULO: DIÁRIO DE BORDO
# ==============================================================================
elif menu == "📝 Diário de Bordo Rápido":
    st.header("📝 Diário de Bordo (Grade Interativa)")
    
    if df_alunos.empty:
        st.warning("Cadastre alunos primeiro.")
    else:
        # --- SELETORES ---
        c1, c2 = st.columns(2)
        turma_sel = c1.selectbox("Turma:", sorted(df_alunos['TURMA'].unique()), key="diario_turma")
        data_sel = c2.date_input("Data da Aula:", date.today(), key="diario_data")
        data_str = data_sel.strftime("%d/%m/%Y")
        
        # --- CONTEXTO DA ATIVIDADE ---
        atividade_desc = st.text_input("Atividade do Dia (Opcional):", placeholder="Ex: Exercício pág 45, Trabalho em Grupo...")
        
        # --- LÓGICA DE CARREGAMENTO (UPSERT) ---
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        df_existente = pd.DataFrame()
        if not df_diario.empty:
            df_existente = df_diario[(df_diario['DATA'] == data_str) & (df_diario['TURMA'] == turma_sel)]
        
        dados_editor = []
        if not df_existente.empty:
            st.info(f"📂 Carregando registros salvos de {data_str}...")
            for _, aluno in alunos_turma.iterrows():
                reg = df_existente[df_existente['ID_ALUNO'].apply(db.limpar_id) == db.limpar_id(aluno['ID'])]
                
                if not reg.empty:
                    tag_salva = str(reg.iloc[0]['TAGS'])
                    dados_editor.append({
                        "ID": aluno['ID'],
                        "NOME": aluno['NOME_ALUNO'],
                        "VISTO": str(reg.iloc[0]['VISTO_ATIVIDADE']).upper() == "TRUE",
                        "TAGS": tag_salva if tag_salva else "", 
                        "OBS": reg.iloc[0]['OBSERVACOES']
                    })
                else:
                    dados_editor.append({"ID": aluno['ID'], "NOME": aluno['NOME_ALUNO'], "VISTO": True, "TAGS": "", "OBS": ""})
        else:
            for _, aluno in alunos_turma.iterrows():
                dados_editor.append({
                    "ID": aluno['ID'],
                    "NOME": aluno['NOME_ALUNO'],
                    "VISTO": True, 
                    "TAGS": "", 
                    "OBS": ""
                })
        
        df_editor = pd.DataFrame(dados_editor)
        
        # --- GRADE INTERATIVA ---
        opcoes_tags = ["", "Dormiu", "Conversa", "Se destacou", "Agitado", "Sem material", "Ausência", "Vetor Disciplinar", "Brincando"]
        
        df_editado = st.data_editor(
            df_editor,
            column_config={
                "ID": st.column_config.TextColumn("ID", disabled=True),
                "NOME": st.column_config.TextColumn("Nome", disabled=True, width="medium"),
                "VISTO": st.column_config.CheckboxColumn("Visto?", help="Entregou atividade?"),
                "TAGS": st.column_config.SelectboxColumn("Ocorrência Principal", options=opcoes_tags, width="medium", help="Selecione a principal ocorrência"),
                "OBS": st.column_config.TextColumn("Percepção Analítica", width="large")
            },
            hide_index=True,
            use_container_width=True,
            num_rows="fixed",
            key="editor_diario"
        )
        
        # --- SALVAMENTO EM LOTE ---
        if st.button("💾 Salvar Diário de Bordo"):
            with st.status("Processando Diário...", expanded=True) as status:
                status.write("🧹 Limpando registros anteriores...")
                db.limpar_diario_data_turma(data_str, turma_sel)
                
                status.write("📝 Compilando dados...")
                linhas_para_salvar = []
                for _, row in df_editado.iterrows():
                    tags_str = str(row['TAGS']) if row['TAGS'] else ""
                    obs_final = row['OBS']
                    if atividade_desc:
                        obs_final = f"[{atividade_desc}] {obs_final}"
                    
                    linhas_para_salvar.append([
                        data_str,
                        row['ID'],
                        row['NOME'],
                        turma_sel,
                        str(row['VISTO']), 
                        tags_str,
                        obs_final
                    ])
                
                status.write("🚀 Enviando para o banco de dados...")
                if db.salvar_lote("DB_DIARIO_BORDO", linhas_para_salvar):
                    status.update(label="Diário Salvo com Sucesso!", state="complete", expanded=False)
                    time.sleep(1)
                    st.rerun()
                else:
                    status.update(label="Erro ao salvar.", state="error")

# ==============================================================================
# MÓDULO: PAINEL DE NOTAS
# ==============================================================================
elif menu == "📊 Painel de Notas & Vistos":
    st.header("📊 Painel de Notas & Vistos (Fórmula de Itabuna)")
    
    if df_alunos.empty:
        st.warning("Cadastre alunos primeiro.")
    else:
        # --- FILTROS ---
        c1, c2 = st.columns(2)
        turma_sel = c1.selectbox("Turma:", sorted(df_alunos['TURMA'].unique()), key="notas_turma")
        trimestre_sel = c2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key="notas_trim")
        
        # --- CÁLCULO DE VISTOS ---
        ano_atual = date.today().year
        if trimestre_sel == "I Trimestre":
            data_ini, data_fim = date(ano_atual, 2, 9), date(ano_atual, 5, 22)
        elif trimestre_sel == "II Trimestre":
            data_ini, data_fim = date(ano_atual, 5, 25), date(ano_atual, 9, 4)
        else:
            data_ini, data_fim = date(ano_atual, 9, 8), date(ano_atual, 12, 17)
            
        total_aulas = 0
        vistos_por_aluno = {}
        
        if not df_diario.empty:
            df_diario['DATA_DT'] = pd.to_datetime(df_diario['DATA'], format="%d/%m/%Y", errors='coerce').dt.date
            df_d_trim = df_diario[
                (df_diario['TURMA'] == turma_sel) & 
                (df_diario['DATA_DT'] >= data_ini) & 
                (df_diario['DATA_DT'] <= data_fim)
            ]
            total_aulas = df_d_trim['DATA'].nunique()
            if total_aulas > 0:
                vistos = df_d_trim[df_d_trim['VISTO_ATIVIDADE'].astype(str).str.upper() == "TRUE"]
                vistos_por_aluno = vistos['ID_ALUNO'].apply(db.limpar_id).value_counts().to_dict()

        st.info(f"📅 Período: {data_ini.strftime('%d/%m')} a {data_fim.strftime('%d/%m')} | 🏫 Aulas Dadas: {total_aulas}")

        # --- MONTAGEM DA GRADE ---
        alunos_turma = df_alunos[df_alunos['TURMA'] == turma_sel].sort_values(by="NOME_ALUNO")
        
        notas_salvas = pd.DataFrame()
        if not df_notas.empty:
            notas_salvas = df_notas[
                (df_notas['TURMA'] == turma_sel) & 
                (df_notas['TRIMESTRE'] == trimestre_sel)
            ]
        
        dados_grade = []
        
        def safe_float(val):
            try: return float(str(val).replace(',', '.'))
            except: return 0.0

        for _, aluno in alunos_turma.iterrows():
            id_limpo = db.limpar_id(aluno['ID'])
            
            qtd_vistos = vistos_por_aluno.get(id_limpo, 0)
            nota_vistos = (qtd_vistos / total_aulas * 3.0) if total_aulas > 0 else 3.0 
            if total_aulas > 0: nota_vistos = round(nota_vistos, 1)
            
            n_teste = 0.0; n_prova = 0.0; n_rec = 0.0
            
            if not notas_salvas.empty:
                reg = notas_salvas[notas_salvas['ID_ALUNO'].apply(db.limpar_id) == id_limpo]
                if not reg.empty:
                    n_teste = safe_float(reg.iloc[0].get('NOTA_TESTE', 0))
                    n_prova = safe_float(reg.iloc[0].get('NOTA_PROVA', 0))
                    n_rec = safe_float(reg.iloc[0].get('NOTA_REC', 0))
            
            if n_teste > 3.0: n_teste = n_teste / 10
            if n_prova > 4.0: n_prova = n_prova / 10
            if n_rec > 10.0: n_rec = n_rec / 10

            dados_grade.append({
                "ID": id_limpo,
                "NOME": aluno['NOME_ALUNO'],
                "VISTOS (3.0)": nota_vistos,
                "TESTE (3.0)": n_teste,
                "PROVA (4.0)": n_prova,
                "RECUPERAÇÃO (10.0)": n_rec
            })
            
        df_grade = pd.DataFrame(dados_grade)
        
        # --- EDITOR DE NOTAS ---
        df_editado = st.data_editor(
            df_grade,
            column_config={
                "ID": st.column_config.TextColumn("ID", disabled=True),
                "NOME": st.column_config.TextColumn("Nome", disabled=True, width="medium"),
                "VISTOS (3.0)": st.column_config.NumberColumn("Vistos (Auto)", disabled=True, format="%.1f", help="Calculado pelo Diário"),
                "TESTE (3.0)": st.column_config.NumberColumn("Teste", min_value=0.0, max_value=3.0, step=0.1, format="%.1f"),
                "PROVA (4.0)": st.column_config.NumberColumn("Prova", min_value=0.0, max_value=4.0, step=0.1, format="%.1f"),
                "RECUPERAÇÃO (10.0)": st.column_config.NumberColumn("Recuperação", min_value=0.0, max_value=10.0, step=0.1, format="%.1f")
            },
            hide_index=True,
            use_container_width=True,
            key="editor_notas"
        )
        
        # --- CÁLCULO FINAL ---
        if not df_editado.empty:
            df_editado['SOMA_PARCIAL'] = df_editado['VISTOS (3.0)'] + df_editado['TESTE (3.0)'] + df_editado['PROVA (4.0)']
            
            def calcular_final(row):
                if row['RECUPERAÇÃO (10.0)'] > row['SOMA_PARCIAL']:
                    return row['RECUPERAÇÃO (10.0)']
                return row['SOMA_PARCIAL']
            
            df_editado['MÉDIA FINAL'] = df_editado.apply(calcular_final, axis=1)
            
            def highlight_fail(val):
                color = '#ffcccc' if val < 6.0 else '#ccffcc'
                return f'background-color: {color}'

            st.markdown("### 📊 Pré-visualização do Boletim")
            st.dataframe(
                df_editado.style.applymap(highlight_fail, subset=['MÉDIA FINAL']).format("{:.1f}", subset=['VISTOS (3.0)', 'TESTE (3.0)', 'PROVA (4.0)', 'RECUPERAÇÃO (10.0)', 'SOMA_PARCIAL', 'MÉDIA FINAL']),
                use_container_width=True,
                hide_index=True
            )
            
            # --- DASHBOARD VISUAL ---
            aprovados = len(df_editado[df_editado['MÉDIA FINAL'] >= 6.0])
            reprovados = len(df_editado) - aprovados
            media_geral = df_editado['MÉDIA FINAL'].mean()
            
            c_chart, c_metrics = st.columns([2, 1])
            
            with c_chart:
                if len(df_editado) > 0:
                    fig = px.pie(
                        names=['Aprovados', 'Reprovados'], 
                        values=[aprovados, reprovados],
                        color=['Aprovados', 'Reprovados'],
                        color_discrete_map={'Aprovados':'#28a745', 'Reprovados':'#dc3545'},
                        hole=0.4,
                        title="Desempenho da Turma"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with c_metrics:
                st.metric("Média da Turma", f"{media_geral:.1f}")
                st.metric("Total de Alunos", len(df_editado))
                st.metric("Taxa de Aprovação", f"{(aprovados/len(df_editado)*100):.0f}%")

            # --- SALVAR ---
            if st.button("💾 Sincronizar Notas"):
                with st.status("Salvando notas...", expanded=True) as status:
                    db.limpar_notas_turma_trimestre(turma_sel, trimestre_sel)
                    
                    linhas_salvar = []
                    for _, row in df_editado.iterrows():
                        linhas_salvar.append([
                            row['ID'],
                            row['NOME'],
                            turma_sel,
                            trimestre_sel,
                            str(row['VISTOS (3.0)']).replace('.', ','),
                            str(row['TESTE (3.0)']).replace('.', ','),
                            str(row['PROVA (4.0)']).replace('.', ','),
                            str(row['RECUPERAÇÃO (10.0)']).replace('.', ','),
                            str(row['MÉDIA FINAL']).replace('.', ',')
                        ])
                    
                    if db.salvar_lote("DB_NOTAS", linhas_salvar):
                        status.update(label="Notas Salvas!", state="complete", expanded=False)
                        time.sleep(1)
                        st.rerun()
                    else:
                        status.update(label="Erro ao salvar.", state="error")

# ==============================================================================
# MÓDULO: BOLETIM ANUAL & CONSELHO (V7 - LIMPEZA AUTOMÁTICA APÓS SALVAR)
# ==============================================================================
elif menu == "📈 Boletim Anual & Conselho":
    st.header("📈 Boletim Anual & Conselho de Classe")
    
    if df_alunos.empty or df_notas.empty:
        st.warning("É necessário ter Alunos e Notas lançadas para gerar o Boletim.")
    else:
        # --- SELEÇÃO DE TURMA ---
        turmas_disponiveis = sorted(df_alunos['TURMA'].unique())
        turma_sel = st.selectbox("Selecione a Turma:", turmas_disponiveis, key="bol_turma")
        
        # --- ABAS ---
        tab_boletim, tab_conselho, tab_hist_atas = st.tabs(["📊 Visão Anual (Aprovação)", "🗣️ Relatório de Conselho (IA)", "🗂️ Histórico de Atas"])
        
        # --- ABA 1: BOLETIM ANUAL ---
        with tab_boletim:
            st.markdown("### 🧮 Fechamento do Ano Letivo")
            st.caption("Regra de Itabuna: Soma dos 3 Trimestres >= 18.0 pontos para aprovação direta.")
            
            # 1. PREPARAÇÃO DOS DADOS
            df_n_turma = df_notas[df_notas['TURMA'] == turma_sel].copy()
            
            # CORREÇÃO DE NOTAS (PRENSA HIDRÁULICA)
            def limpar_float_normalizado(x):
                try: 
                    val = float(str(x).replace(',', '.'))
                    if val > 10.0: return val / 10.0
                    return val
                except: return 0.0
            
            df_n_turma['MEDIA_FINAL'] = df_n_turma['MEDIA_FINAL'].apply(limpar_float_normalizado)
            
            if not df_n_turma.empty:
                pivot = df_n_turma.pivot_table(
                    index=["ID_ALUNO", "NOME_ALUNO"], 
                    columns="TRIMESTRE", 
                    values="MEDIA_FINAL", 
                    aggfunc='first'
                ).reset_index()
                
                for col in ["I Trimestre", "II Trimestre", "III Trimestre"]:
                    if col not in pivot.columns: pivot[col] = 0.0
                    pivot[col] = pivot[col].fillna(0.0)

                if "REC_FINAL" not in pivot.columns: 
                    pivot["REC_FINAL"] = -1.0
                else:
                    pivot["REC_FINAL"] = pivot["REC_FINAL"].fillna(-1.0)
                
                # 2. CÁLCULOS
                pivot['SOMA_ANUAL'] = pivot['I Trimestre'] + pivot['II Trimestre'] + pivot['III Trimestre']
                
                def definir_situacao(row):
                    if row['SOMA_ANUAL'] >= 18.0:
                        return "✅ APROVADO"
                    elif row['REC_FINAL'] != -1.0:
                        if row['REC_FINAL'] >= 5.0: return "✅ APROVADO (REC)"
                        else: return "❌ REPROVADO"
                    else:
                        return "⚠️ RECUPERAÇÃO FINAL"

                pivot['SITUAÇÃO'] = pivot.apply(definir_situacao, axis=1)
                
                # 3. VISUALIZAÇÃO
                df_view = pivot.copy()
                df_view['REC_FINAL'] = df_view['REC_FINAL'].replace(-1.0, None)
                
                st.dataframe(
                    df_view[['NOME_ALUNO', 'I Trimestre', 'II Trimestre', 'III Trimestre', 'SOMA_ANUAL', 'REC_FINAL', 'SITUAÇÃO']],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "I Trimestre": st.column_config.NumberColumn("I Trim", format="%.1f"),
                        "II Trimestre": st.column_config.NumberColumn("II Trim", format="%.1f"),
                        "III Trimestre": st.column_config.NumberColumn("III Trim", format="%.1f"),
                        "SOMA_ANUAL": st.column_config.NumberColumn("Soma (Meta 18.0)", format="%.1f"),
                        "REC_FINAL": st.column_config.NumberColumn("Nota Rec. Final", format="%.1f"),
                        "SITUAÇÃO": st.column_config.TextColumn("Status", width="medium")
                    }
                )
                
                # 4. LANÇAMENTO DE RECUPERAÇÃO FINAL
                st.markdown("---")
                st.subheader("📝 Lançar ou Editar Recuperação Final")
                
                c_rec1, c_rec2 = st.columns([2, 1])
                lista_alunos = pivot['NOME_ALUNO'].tolist()
                aluno_rec_sel = c_rec1.selectbox("Selecione o Aluno:", lista_alunos)
                
                nota_atual_raw = pivot.loc[pivot['NOME_ALUNO'] == aluno_rec_sel, 'REC_FINAL'].values[0]
                valor_input = 0.0 if nota_atual_raw == -1.0 else float(nota_atual_raw)
                
                nota_rec = c_rec2.number_input("Nota da Prova Final:", 0.0, 10.0, valor_input, step=0.1)
                
                if st.button("💾 Salvar/Atualizar Nota Final"):
                    id_rec = pivot[pivot['NOME_ALUNO'] == aluno_rec_sel].iloc[0]['ID_ALUNO']
                    if db.salvar_rec_final(id_rec, aluno_rec_sel, turma_sel, nota_rec):
                        st.success(f"Nota de {aluno_rec_sel} atualizada para {nota_rec}!")
                        time.sleep(1)
                        st.rerun()
            else:
                st.info("Nenhuma nota lançada para esta turma ainda.")

        # --- ABA 2: RELATÓRIO DE CONSELHO ---
        with tab_conselho:
            st.markdown("### 🗣️ Gerador de Ata de Conselho")
            st.info("A IA analisará o Diário (comportamento) e as Notas para gerar um relatório completo da turma.")
            
            trimestre_cons = st.selectbox("Referência:", ["I Trimestre", "II Trimestre", "III Trimestre", "ANUAL (Final)"], key="cons_trim")
            
            if st.button("🚀 Gerar Relatório da Turma"):
                with st.spinner(f"Analisando dados do {trimestre_cons} para a turma {turma_sel}..."):
                    
                    # 1. COLETAR DADOS
                    notas_texto = ""
                    if not df_notas.empty:
                        df_n_t = df_notas[(df_notas['TURMA'] == turma_sel) & (df_notas['TRIMESTRE'] == trimestre_cons)]
                        if not df_n_t.empty:
                            df_n_t['MEDIA_FINAL'] = df_n_t['MEDIA_FINAL'].apply(limpar_float_normalizado)
                            reprovados = df_n_t[df_n_t['MEDIA_FINAL'] < 6.0]['NOME_ALUNO'].tolist()
                            media_turma = df_n_t['MEDIA_FINAL'].mean()
                            notas_texto = f"MÉDIA DA TURMA: {media_turma:.1f}. ALUNOS COM NOTA VERMELHA (<6.0): {', '.join(reprovados)}."
                        else:
                            notas_texto = "Sem notas fechadas para este trimestre."
                    
                    diario_texto = ""
                    if not df_diario.empty:
                        df_d_t = df_diario[df_diario['TURMA'] == turma_sel]
                        sem_tarefa = df_d_t[df_d_t['TAGS'].str.contains("Sem material|Não fez", case=False, na=False)]['NOME_ALUNO'].value_counts().to_dict()
                        indisciplina = df_d_t[df_d_t['TAGS'].str.contains("Conversa|Agitado|Vetor", case=False, na=False)]['NOME_ALUNO'].value_counts().to_dict()
                        diario_texto = f"ALUNOS QUE NÃO FAZEM TAREFA (Qtd): {sem_tarefa}. ALUNOS COM INDISCIPLINA (Qtd): {indisciplina}."

                    # 2. PROMPT
                    prompt_conselho = (
                        f"VOCÊ É UM COORDENADOR PEDAGÓGICO EXPERIENTE.\n"
                        f"OBJETIVO: Escrever a ATA DE CONSELHO DE CLASSE para a Turma {turma_sel}, {trimestre_cons}.\n\n"
                        f"DADOS BRUTOS:\n"
                        f"{notas_texto}\n"
                        f"{diario_texto}\n\n"
                        f"ESTRUTURA DO RELATÓRIO:\n"
                        f"1. VISÃO GERAL: Como está o rendimento e comportamento da turma?\n"
                        f"2. PONTOS DE ATENÇÃO ACADÊMICA: Cite os alunos com dificuldade (notas baixas) e sugira intervenções.\n"
                        f"3. PONTOS DE ATENÇÃO COMPORTAMENTAL: Cite os alunos que não fazem tarefa ou conversam muito.\n"
                        f"4. DESTAQUES POSITIVOS: Elogie a turma se a média for boa.\n"
                        f"5. PROGNÓSTICO: Qual a probabilidade de recuperação final se continuar assim?\n\n"
                        f"Tom: Profissional, analítico e propositivo."
                    )
                    
                    relatorio_gerado = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_conselho)
                    st.session_state.relatorio_conselho = relatorio_gerado
            
            if "relatorio_conselho" in st.session_state:
                st.text_area("📄 Relatório Gerado:", st.session_state.relatorio_conselho, height=500)
                
                # BOTÃO COM LIMPEZA AUTOMÁTICA
                if st.button("💾 Arquivar Relatório (Substituir Anterior)"):
                    sucesso = db.salvar_ata_conselho(
                        datetime.now().strftime("%d/%m/%Y"), 
                        turma_sel, 
                        f"CONSELHO_{trimestre_cons}", 
                        st.session_state.relatorio_conselho
                    )
                    if sucesso:
                        st.success("Relatório arquivado com sucesso! (Limpando tela...)")
                        # Limpa a variável da memória
                        del st.session_state.relatorio_conselho
                        # Espera 1.5s para você ler a mensagem
                        time.sleep(1.5)
                        # Recarrega a página
                        st.rerun()

        # --- ABA 3: HISTÓRICO DE ATAS ---
        with tab_hist_atas:
            st.markdown(f"### 🗂️ Arquivo de Atas - {turma_sel}")
            
            if not df_relatorios.empty:
                df_atas = df_relatorios[
                    (df_relatorios['ID_ALUNO'] == "TURMA") & 
                    (df_relatorios['NOME_ALUNO'] == turma_sel) &
                    (df_relatorios['TIPO'].str.contains("CONSELHO", na=False))
                ]
                
                if not df_atas.empty:
                    df_atas = df_atas.iloc[::-1]
                    for _, row in df_atas.iterrows():
                        titulo = f"{row['DATA']} - {row['TIPO']}"
                        with st.expander(titulo):
                            st.markdown(row['CONTEUDO'])
                else:
                    st.info(f"Nenhuma ata encontrada para a turma {turma_sel}.")
            else:
                st.info("Banco de relatórios vazio.")

# ==============================================================================
# MÓDULO: GESTÃO DA TURMA (COM EDIÇÃO)
# ==============================================================================
elif menu == "👥 Gestão da Turma":
    st.header("👥 Gestão de Turmas e Alunos")
    
    t1, t2, t3, t4 = st.tabs(["🏗️ Criar Turma", "➕ Povoar Alunos", "👁️ Ver Lista", "✏️ Editar Dados"])
    
    with t1:
        with st.form("f_t_new"):
            c1, c2, c3 = st.columns(3)
            a = c1.selectbox("Ano:", [6,7,8,9]); l = c2.selectbox("Letra:", ["A","B","C","D","E","F"]); u = c3.selectbox("Turno:", ["Matutino", "Vespertino"])
            sigla = f"{a}ª {'M' if u=='Matutino' else 'V'}{l}"
            if st.form_submit_button("Criar Turma"):
                db.salvar_no_banco("DB_TURMAS", [sigla, f"{a}º Ano {l}", "Seg/Qui"])
                st.success(f"Turma {sigla} criada!")
    
    with t2:
        if not df_turmas.empty:
            t_dest = st.selectbox("Para qual turma?", df_turmas['ID_TURMA'].tolist())
            metodo = st.radio("Método:", ["Individual", "CSV (Upload)", "IA (PDF)"], horizontal=True)
            if metodo == "Individual":
                with st.form("f_ind_aluno", clear_on_submit=True):
                    nome_a = st.text_input("Nome Completo:").upper()
                    nec_a = st.text_input("Necessidades:", value="NENHUMA").upper()
                    if st.form_submit_button("💾 Salvar"):
                        if nome_a:
                            id_a = db.gerar_proximo_id(df_alunos)
                            db.salvar_no_banco("DB_ALUNOS", [id_a, nome_a, t_dest, "ATIVO", nec_a, "MANUAL"])
                            st.success("Cadastrado!"); st.rerun()
            elif metodo == "CSV (Upload)":
                f_csv = st.file_uploader("CSV", type=["csv"])
                if f_csv and st.button("Processar"):
                    df_up = pd.read_csv(f_csv)
                    id_base = db.gerar_proximo_id(df_alunos)
                    for idx, r in df_up.iterrows():
                        db.salvar_no_banco("DB_ALUNOS", [id_base+idx, str(r['NOME']).upper(), t_dest, "ATIVO", "NENHUMA", "CSV"])
                    st.success("Importado!"); st.rerun()
            elif metodo == "IA (PDF)":
                txt_pdf = st.text_area("Cole o texto do PDF aqui:")
                if st.button("🤖 Maestro, Extrair Nomes"):
                    res = ai.gerar_ia("MAESTRO", f"Extraia apenas os nomes em caixa alta deste texto: {txt_pdf}")
                    st.session_state.ia_res = res.upper()
                if "ia_res" in st.session_state:
                    st.code(st.session_state.ia_res)
                    if st.button("💾 Confirmar e Salvar"):
                        id_base = db.gerar_proximo_id(df_alunos)
                        for idx, nome in enumerate(st.session_state.ia_res.split('\n')):
                            if nome.strip(): db.salvar_no_banco("DB_ALUNOS", [id_base+idx, nome.strip(), t_dest, "ATIVO", "PENDENTE", "IA"])
                        st.success("Salvos!"); del st.session_state.ia_res; st.rerun()
    
    with t3:
        if not df_alunos.empty:
            t_f = st.selectbox("Filtrar Turma:", sorted(df_alunos['TURMA'].unique()))
            st.dataframe(df_alunos[df_alunos['TURMA']==t_f].sort_values(by="NOME_ALUNO"), use_container_width=True, hide_index=True)

    # --- ABA 4: EDITAR DADOS ---
    with t4:
        st.subheader("✏️ Atualizar Cadastro (CID/Necessidades)")
        if df_alunos.empty:
            st.warning("Sem alunos cadastrados.")
        else:
            c_sel1, c_sel2 = st.columns(2)
            turma_edit = c_sel1.selectbox("Turma:", sorted(df_alunos['TURMA'].unique()), key="edit_turma")
            
            alunos_da_turma = df_alunos[df_alunos['TURMA'] == turma_edit].sort_values(by="NOME_ALUNO")
            aluno_edit_nome = c_sel2.selectbox("Aluno:", alunos_da_turma['NOME_ALUNO'].tolist(), key="edit_aluno")
            
            dados_atuais = alunos_da_turma[alunos_da_turma['NOME_ALUNO'] == aluno_edit_nome].iloc[0]
            id_atual = dados_atuais['ID']
            nec_atual = dados_atuais['NECESSIDADES']
            
            st.info(f"🆔 ID: {id_atual} | 🏥 Cadastro Atual: {nec_atual}")
            
            nova_nec = st.text_input("Nova Necessidade / CID (Digite para atualizar):", value=nec_atual)
            
            if st.button("💾 Atualizar Cadastro"):
                if nova_nec != nec_atual:
                    with st.spinner("Atualizando banco de dados..."):
                        if db.atualizar_necessidade_aluno(id_atual, nova_nec):
                            st.success(f"Sucesso! {aluno_edit_nome} agora consta como: {nova_nec}")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar.")
                else:
                    st.warning("Nenhuma alteração feita.")

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
