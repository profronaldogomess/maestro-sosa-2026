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
        st.subheader("🚀 Exportação Profissional")
        nome_sugerido = f"Material_{datetime.now().strftime('%d_%m_%H%M')}" 
        nome_doc = st.text_input("Título do Documento:", value=nome_sugerido, key=f"name_input_v18_{key_prefix}")
        
        doc_file = exporter.gerar_docx_profissional(nome_doc.upper(), texto_raw)
        
        st.download_button(
            label="📥 BAIXAR AGORA (Word .docx)",
            data=doc_file,
            file_name=f"{nome_doc}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key=f"btn_dl_{key_prefix}"
        )

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
# MÓDULO: MATERIAL DE SALA (🧪 CRIADOR DE AULAS)
# ==============================================================================
elif menu == "🧪 Criador de Aulas":
    st.header("🧪 Laboratório de Materiais Didáticos")
    
    t_lousa, t_avulsa, t_prova, t_prova_pei, t_adaptada, t_hist = st.tabs([
        "🏫 Lousa/Slides", 
        "🏠 Atividades Avulsas", 
        "📝 Avaliações (Regular)", 
        "♿ Avaliação Adaptada (PEI)", 
        "🧩 Atividade Global (PEI)", 
        "🗂️ Histórico"
    ])

    # --- ABA 1: LOUSA / SLIDES ---
    with t_lousa:
        st.subheader("📋 Material de Sala (Baseado no Plano)")
        try:
            if df_planos.empty:
                st.warning("⚠️ Nenhum Planejamento encontrado. Vá na aba '📅 Planejamento (Ponto ID)' e crie seu primeiro plano para liberar este módulo.")
            else:
                c1, c2 = st.columns([1, 2])
                ano_l = c1.selectbox("Ano:", [6, 7, 8, 9], key="l_ano")
                
                if 'ANO' in df_planos.columns:
                    df_f = df_planos[df_planos['ANO'] == f"{ano_l}º"]
                    if not df_f.empty:
                        sel_p = c2.selectbox("Semana do Plano:", df_f['SEMANA'].tolist(), key="l_sem")
                        plano_txt = df_f[df_f['SEMANA'] == sel_p].iloc[0]['PLANO_TEXTO']
                        
                        col1, col2, col3 = st.columns(3)
                        foco_aula = col1.selectbox("Zelo:", ["Aula 1", "Aula 2", "Ambas"], key="foco_aula")
                        formato_aula = col2.radio("Formato:", ["Quadro (Lousa)", "Slides (Roteiro)"])
                        num_q = col3.slider("Questões:", 1, 15, 5, key="num_q_lousa")
                        
                        orient = st.text_area("Instruções Adicionais:", placeholder="Ex: Use o contexto de Itabuna...", key="orient_lousa")
                        
                        b1, b2 = st.columns(2)
                        if b1.button("🚀 Gerar Material Completo", key="btn_lousa"):
                            with st.spinner("Compondo pacote com busca ativa e roteiro Gamma..."):
                                prompt = (f"BASE PEDAGÓGICA (PLANO): {plano_txt}. FORMATO: {formato_aula}. FOCO: {foco_aula}. "
                                         f"Se formato for 'Slides (Roteiro)', gere um script técnico pronto para o Gamma AI. "
                                         f"Use a didática de Situações-Problema (PDF Curitiba): Material Dourado, Decomposição e Contexto de Compras. "
                                         f"Pesquise no Google por tendências da Geração Alpha para o tema. "
                                         f"Inclua {num_q} questões. PACOTE COMPLETO: LOUSA, FOLHA, GABARITO, IMAGENS. Orientações: {orient}.")
                                st.session_state.out_lousa = ai.gerar_ia("AVALIADOR", prompt)
                        if b2.button("🗑️ Limpar/Novo", key="clear_lousa"):
                            if "out_lousa" in st.session_state: del st.session_state.out_lousa
                            st.rerun()
                        
                        if "out_lousa" in st.session_state:
                            st.info("🤖 **Refinamento:** Peça ajustes no material gerado abaixo.")
                            ajuste_l = st.chat_input("Ex: 'Adicione um slide sobre Material Dourado'", key="chat_lousa")
                            if ajuste_l:
                                st.session_state.out_lousa = ai.gerar_ia("AVALIADOR", f"Material atual: {st.session_state.out_lousa}. Ajuste: {ajuste_l}. Mantenha os MARKERS.")
                                st.rerun()
                            
                            # CHAMADA DA FUNÇÃO COM ABA DE EXPORTAÇÃO
                            exibir_material_estruturado(st.session_state.out_lousa, "view_lousa")
                            
                            if st.button("💾 Salvar Material na Semana", key="save_lousa"):
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m"), f"{sel_p} ({foco_aula})", formato_aula, st.session_state.out_lousa, f"{ano_l}º"])
                                st.success("Salvo!"); del st.session_state.out_lousa; time.sleep(1); st.rerun()
                                info_doc = {
                                "turma": st.session_state.get('diario_turma', '______'),
                                "trimestre": st.session_state.get('notas_trim', 'III').split(' ')[0]
                                }
                    else: st.warning(f"Nenhum plano encontrado para o {ano_l}º ano. Crie um plano primeiro.")
                else: st.error("⚠️ Coluna 'ANO' não encontrada na planilha DB_PLANOS.")
        except Exception as e:
            st.error(f"Erro ao carregar painel: {e}")

    # --- ABA 2: ATIVIDADES AVULSAS ---
    with t_avulsa:
        st.subheader("🏠 Atividades Avulsas / Reforço")
        try:
            if df_planos.empty:
                st.warning("⚠️ Crie um Plano primeiro na aba 'Planejamento' para vincular atividades.")
            else:
                c1, c2 = st.columns([1, 2])
                ano_av = c1.selectbox("Ano:", [6, 7, 8, 9], key="av_ano")
                
                if 'ANO' in df_planos.columns:
                    df_f_av = df_planos[df_planos['ANO'] == f"{ano_av}º"]
                    if not df_f_av.empty:
                        sel_p_av = c2.selectbox("Vincular à Semana:", df_f_av['SEMANA'].tolist(), key="av_sem")
                        plano_txt_av = df_f_av[df_f_av['SEMANA'] == sel_p_av].iloc[0]['PLANO_TEXTO']
                        tema_av = st.text_input("Título da Atividade:")
                        orient_av = st.text_area("Orientações:", key="orient_av")
                        
                        b1, b2 = st.columns(2)
                        if b1.button("🚀 Gerar Atividade Avulsa", key="btn_av"):
                            with st.spinner("Gerando..."):
                                prompt = (f"BASE PEDAGÓGICA (PLANO): {plano_txt_av}. TEMA: {tema_av}. ORIENTAÇÕES: {orient_av}. "
                                         f"Gere PACOTE COMPLETO (LOUSA, FOLHA, GABARITO, IMAGENS).")
                                st.session_state.out_avulsa = ai.gerar_ia("AVALIADOR", prompt)
                        if b2.button("🗑️ Limpar/Novo", key="clear_av"):
                            if "out_avulsa" in st.session_state: del st.session_state.out_avulsa
                            st.rerun()

                        if "out_avulsa" in st.session_state:
                            st.info("🤖 **Refinamento:** Peça alterações aqui.")
                            aj_av = st.chat_input("Sugerir mudança...", key="chat_avulsa_input")
                            if aj_av:
                                st.session_state.out_avulsa = ai.gerar_ia("AVALIADOR", f"Atual: {st.session_state.out_avulsa}. Ajuste: {aj_av}. Mantenha os MARKERS.")
                                st.rerun()
                            
                            # CHAMADA DA FUNÇÃO COM ABA DE EXPORTAÇÃO
                            exibir_material_estruturado(st.session_state.out_avulsa, "view_av")
                            
                            if st.button("💾 Salvar Atividade na Semana", key="save_av"):
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m"), f"{sel_p_av} (AVULSA)", "AVULSA", st.session_state.out_avulsa, f"{ano_av}º"])
                                st.success("Salvo!"); del st.session_state.out_avulsa; time.sleep(1); st.rerun()
                    else: st.warning(f"Nenhum plano encontrado para o {ano_av}º ano.")
                else: st.error("⚠️ Coluna 'ANO' não encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar painel: {e}")

    # --- ABA 3: AVALIAÇÕES REGULARES ---
    with t_prova:
        st.subheader("📝 Gerador de Avaliações (Regular)")
        try:
            if df_planos.empty:
                st.warning("⚠️ Crie Planos primeiro para gerar avaliações baseadas neles.")
            else:
                c1, c2, c3 = st.columns(3)
                ano_p = c1.selectbox("Ano:", [6, 7, 8, 9], key="p_ano")
                
                if 'ANO' in df_planos.columns:
                    df_p = df_planos[df_planos['ANO'] == f"{ano_p}º"].sort_values(by="SEMANA")
                    if not df_p.empty:
                        s_ini = c2.selectbox("De:", df_p['SEMANA'].tolist())
                        s_fim = c3.selectbox("Até:", df_p['SEMANA'].tolist(), index=len(df_p)-1)
                        df_per = df_p[(df_p['SEMANA'] >= s_ini) & (df_p['SEMANA'] <= s_fim)]
                        ctx = "\n".join([f"SEM {r['SEMANA']}: {ai.extrair_tag(r['PLANO_TEXTO'], 'CONTEUDOS_ESPECIFICOS')}" for _, r in df_per.iterrows()])
                        tipo = st.selectbox("Tipo:", ["Teste", "Prova", "Rec. Paralela", "Rec. Final", "2ª Chamada"])
                        num_ev = st.number_input("Questões:", 5, 20, 10)
                        orient_p = st.text_area("Orientações para a Prova:")
                        
                        b1, b2 = st.columns(2)
                        if b1.button("🔥 Gerar Avaliação Regular", key="btn_prova"):
                            with st.spinner("Compondo prova..."):
                                prompt = f"Crie uma {tipo} (PACOTE COMPLETO) para o {ano_p}º ano. Período: {s_ini} a {s_fim}. Base: {ctx}. Qtd: {num_ev}. Orientações: {orient_p}."
                                st.session_state.out_prova = ai.gerar_ia("AVALIADOR", prompt)
                        if b2.button("🗑️ Limpar/Novo", key="clear_prova"):
                            if "out_prova" in st.session_state: del st.session_state.out_prova
                            st.rerun()

                        if "out_prova" in st.session_state:
                            st.info("🤖 **Refinamento:** Peça alterações na prova.")
                            aj_p = st.chat_input("Sugerir mudança...", key="chat_prova_input")
                            if aj_p:
                                st.session_state.out_prova = ai.gerar_ia("AVALIADOR", f"Atual: {st.session_state.out_prova}. Ajuste: {aj_p}. Mantenha os MARKERS.")
                                st.rerun()
                            
                            # CHAMADA DA FUNÇÃO COM ABA DE EXPORTAÇÃO
                            exibir_material_estruturado(st.session_state.out_prova, "view_prova")
                            
                            if st.button("💾 Salvar Avaliação Oficial (Regular)"):
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m"), f"{s_ini}-{s_fim}", tipo, st.session_state.out_prova, f"{ano_p}º"])
                                st.success("Salvo!"); del st.session_state.out_prova; time.sleep(1); st.rerun()
                    else: st.warning(f"Nenhum plano encontrado para o {ano_p}º ano.")
                else: st.error("⚠️ Coluna 'ANO' não encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar painel: {e}")

    # --- ABA 4: AVALIAÇÃO ADAPTADA (PEI) ---
    with t_prova_pei:
        st.subheader("♿ Gerador de Avaliação Adaptada (PEI)")
        st.info("Selecione uma prova regular já salva para criar a versão adaptada (reduzida e visual).")
        
        if not df_aulas.empty:
            df_provas = df_aulas[
                (df_aulas['TIPO_MATERIAL'].isin(["Teste", "Prova", "Rec. Paralela", "Rec. Final"])) & 
                (~df_aulas['TIPO_MATERIAL'].str.contains("ADAPTADA", na=False))
            ].copy()
            
            if not df_provas.empty:
                df_provas = df_provas.iloc[::-1].reset_index(drop=True)
                
                sel_prova_base = st.selectbox(
                    "Selecione a Prova Regular:",
                    df_provas.index,
                    format_func=lambda x: f"{df_provas.loc[x, 'DATA']} - {df_provas.loc[x, 'SEMANA_REF']} ({df_provas.loc[x, 'TIPO_MATERIAL']}) - {df_provas.loc[x, 'ANO']}"
                )
                
                conteudo_prova_base = df_provas.loc[sel_prova_base, 'CONTEUDO']
                tipo_prova_base = df_provas.loc[sel_prova_base, 'TIPO_MATERIAL']
                ano_prova_base = df_provas.loc[sel_prova_base, 'ANO']
                ref_prova_base = df_provas.loc[sel_prova_base, 'SEMANA_REF']
                
                with st.expander("Ver Conteúdo da Prova Original"):
                    st.text(ai.extrair_tag(conteudo_prova_base, "FOLHA"))
                
                if st.button("♿ Gerar Versão Adaptada Agora"):
                    with st.spinner("O Especialista em Inclusão está adaptando a prova..."):
                        prompt_adapt = f"PROVA ORIGINAL: {conteudo_prova_base}. TIPO: {tipo_prova_base}. Crie uma versão ADAPTADA (reduzida, visual, simplificada) para alunos com DI/TDAH."
                        st.session_state.out_prova_adaptada = ai.gerar_ia("AVALIADOR_ADAPTADO", prompt_adapt)
                
                if "out_prova_adaptada" in st.session_state:
                    st.success("Versão Adaptada Gerada com Sucesso!")
                    
                    # CHAMADA DA FUNÇÃO COM ABA DE EXPORTAÇÃO
                    exibir_material_estruturado(st.session_state.out_prova_adaptada, "view_prova_adapt_tab")
                    
                    if st.button("💾 Salvar Prova Adaptada no Histórico"):
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [
                            datetime.now().strftime("%d/%m"), 
                            ref_prova_base, 
                            f"{tipo_prova_base} (ADAPTADA)", 
                            st.session_state.out_prova_adaptada, 
                            ano_prova_base
                        ])
                        st.success("Salvo!"); del st.session_state.out_prova_adaptada; time.sleep(1); st.rerun()
            else:
                st.warning("Nenhuma prova regular encontrada no histórico. Crie uma na aba 'Avaliações (Regular)' primeiro.")
        else:
            st.warning("Histórico vazio.")

    # --- ABA 5: ATIVIDADE GLOBAL (PEI) ---
    with t_adaptada:
        st.subheader("🧩 Atividade Adaptada (Global - DUA)")
        st.info("Esta ferramenta cria uma atividade única, visual e simplificada, acessível para alunos com DI, TEA e TDAH.")
        
        try:
            if df_planos.empty:
                st.warning("⚠️ Crie um Plano primeiro na aba 'Planejamento'.")
            else:
                c1, c2 = st.columns([1, 2])
                ano_ad = c1.selectbox("Ano:", [6, 7, 8, 9], key="ad_ano")
                
                if 'ANO' in df_planos.columns:
                    df_f_ad = df_planos[df_planos['ANO'] == f"{ano_ad}º"]
                    if not df_f_ad.empty:
                        sel_p_ad = c2.selectbox("Semana do Plano:", df_f_ad['SEMANA'].tolist(), key="ad_sem")
                        plano_txt_ad = df_f_ad[df_f_ad['SEMANA'] == sel_p_ad].iloc[0]['PLANO_TEXTO']
                        
                        foco_ad = st.radio("Foco da Atividade:", ["Aula 1", "Aula 2", "Ambas"], horizontal=True, key="foco_ad")
                        
                        if st.button("🚀 Gerar Atividade Global (PEI)"):
                            with st.spinner("Criando atividade com Desenho Universal para Aprendizagem..."):
                                prompt = (f"BASE PEDAGÓGICA: {plano_txt_ad}. FOCO: {foco_ad}. "
                                         f"Crie uma ATIVIDADE ADAPTADA GLOBAL (para DI, TEA, TDAH). "
                                         f"Use a estrutura: TÍTULO, PARA LEMBRAR (com prompt de imagem), QUESTÕES 1, 2 e 3 (Ligar, Pintar, Completar). "
                                         f"Gere MARKERS: LOUSA, FOLHA, GABARITO, IMAGENS.")
                                st.session_state.out_adaptada = ai.gerar_ia("CRIADOR_ADAPTADO", prompt)
                        
                        if "out_adaptada" in st.session_state:
                            # CHAMADA DA FUNÇÃO COM ABA DE EXPORTAÇÃO
                            exibir_material_estruturado(st.session_state.out_adaptada, "view_adaptada")
                            
                            if st.button("💾 Salvar Atividade Adaptada"):
                                db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m"), f"{sel_p_ad} ({foco_ad})", "ADAPTADA", st.session_state.out_adaptada, f"{ano_ad}º"])
                                st.success("Salvo!"); del st.session_state.out_adaptada; time.sleep(1); st.rerun()
                    else: st.warning("Sem planos para este ano.")
        except Exception as e:
            st.error(f"Erro: {e}")

    # --- ABA 6: HISTÓRICO DE PRODUÇÃO ---
    with t_hist:
        st.subheader("🗂️ Consulta de Materiais Salvos")
        _, (_, _, _, _, df_h_raw, _, _, _, _, _, _) = db.carregar_tudo()
        
        if not df_h_raw.empty and 'DATA' in df_h_raw.columns:
            c1, c2 = st.columns(2)
            f_ano = c1.selectbox("Filtrar Ano:", ["Todos", "6º", "7º", "8º", "9º", "GERAL"], key="h_f_ano")
            f_tipo = c2.selectbox("Filtrar Tipo:", ["Todos", "Quadro (Lousa)", "Slides (Roteiro)", "AVULSA", "ADAPTADA", "Teste", "Prova", "Teste (ADAPTADA)", "Prova (ADAPTADA)", "Rec. Paralela", "Rec. Final"])
            
            df_h = df_h_raw.copy()
            if f_ano != "Todos": df_h = df_h[df_h['ANO'] == f_ano]
            if f_tipo != "Todos": df_h = df_h[df_h['TIPO_MATERIAL'] == f_tipo]
            
            if not df_h.empty:
                df_h = df_h.iloc[::-1].reset_index(drop=True)
                
                def criar_rotulo(idx):
                    row = df_h.loc[idx]
                    resumo = str(row['CONTEUDO']).replace('\n', ' ').replace('MARKER_', '')[:60] + "..."
                    return f"{row['SEMANA_REF']} | {row['TIPO_MATERIAL']} | {resumo}"

                sel_h = st.selectbox(
                    "Selecione o Material (Mais recente primeiro):", 
                    df_h.index, 
                    format_func=criar_rotulo,
                    key="selectbox_historico_final"
                )
                
                prefixo_unico = f"hist_{sel_h}_{df_h.loc[sel_h, 'DATA'].replace('/', '')}"
                raw_h = df_h.loc[sel_h, 'CONTEUDO']
                
                st.info(f"📅 Data: {df_h.loc[sel_h, 'DATA']} | 🏷️ Tipo: {df_h.loc[sel_h, 'TIPO_MATERIAL']}")
                
                # CHAMADA DA FUNÇÃO COM ABA DE EXPORTAÇÃO (Permite baixar materiais antigos também!)
                exibir_material_estruturado(raw_h, prefixo_unico)
                
                if st.button("🗑️ Excluir este Material"):
                    if db.excluir_registro("DB_AULAS_PRONTAS", raw_h):
                        st.success("Excluído!"); st.rerun()
            else: st.info("Nenhum material encontrado.")
        else: st.info("Histórico vazio.")

# ==============================================================================
# MÓDULO: PLANEJAMENTO (PONTO ID) - ATUALIZADO COM EXPORTAÇÃO V18
# ==============================================================================
elif menu == "📅 Planejamento (Ponto ID)":
    st.header("📅 Planejador Oficial (Ponto ID)")
    tab_gerar, tab_hist, tab_curso = st.tabs(["✨ Gerar Novo Plano", "🗂️ Histórico Detalhado", "📚 Plano de Curso Vivo"])
    
    # --- ABA 1: GERAR PLANO ---
    with tab_gerar:
        try:
            c1, c2 = st.columns([1, 2])
            # Chave única: v18_ano_gerar
            ano_p = c1.selectbox("Ano/Série:", [6, 7, 8, 9], key="v18_ano_gerar")
            
            semanas_ocupadas = []
            if not df_planos.empty and 'ANO' in df_planos.columns and 'SEMANA' in df_planos.columns:
                semanas_ocupadas = df_planos[df_planos['ANO'] == f"{ano_p}º"]['SEMANA'].tolist()
            
            todas_semanas = util.gerar_semanas()
            semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_ocupadas]
            
            opcoes_semana = semanas_disponiveis if semanas_disponiveis else ["✅ Todas planejadas!"]
            # Chave única: v18_sem_gerar
            sem_p = c2.selectbox("Selecione a Semana Livre:", opcoes_semana, index=0, key="v18_sem_gerar")
            
            if "✅" not in sem_p:
                modo_p = st.radio("Método:", ["🎛️ Manual", "📖 Livro Didático"], horizontal=True, key="v18_modo_gerar")
                partes_arquivos = []; info_livro = ""; ctx_curriculo = ""
                
                if modo_p == "📖 Livro Didático":
                    if not df_materiais.empty:
                        sel_mat = st.multiselect("Livro:", df_materiais['NOME_ARQUIVO'].tolist(), key="v18_livro_gerar")
                        pags = st.text_input("Páginas:", key="v18_pags_gerar")
                        info_livro = f"MATERIAL: {sel_mat}, PÁGINAS: {pags}"
                        for n in sel_mat:
                            uri = df_materiais[df_materiais['NOME_ARQUIVO'] == n]['URI_ARQUIVO'].values[0]
                            if "files/" in str(uri): partes_arquivos.append(types.Part.from_uri(file_uri=uri, mime_type="application/pdf"))
                else:
                    df_f = df_curriculo[df_curriculo['ANO'] == ano_p] if not df_curriculo.empty else pd.DataFrame()
                    if not df_f.empty:
                        eixo = st.selectbox("Eixo:", df_f['EIXO'].unique(), key="v18_eixo_gerar")
                        cont_esp = st.multiselect("Conteúdo:", df_f[df_f['EIXO'] == eixo]['CONTEUDO_ESPECIFICO'].unique(), key="v18_cont_gerar")
                        objs = st.multiselect("Objetivos:", df_f[df_f['CONTEUDO_ESPECIFICO'].isin(cont_esp)]['OBJETIVOS'].unique(), key="v18_obj_gerar")
                        ctx_curriculo = f"EIXO: {eixo}, CONTEUDOS: {cont_esp}, OBJETIVOS: {objs}"
                
                strat = st.text_area("Estratégia:", height=70, key="v18_strat_gerar")
                if st.button("🚀 Compor Planejamento", key="v18_btn_compor"):
                    res = ai.gerar_ia("PLANE_PEDAGOGICO", f"Gere plano para {ano_p}º ano, {sem_p}. Dados: {ctx_curriculo if modo_p=='🎛️ Manual' else info_livro}. Estratégia: {strat}. MARKERS: MARKER_CONTEUDO_GERAL, MARKER_CONTEUDOS_ESPECIFICOS, MARKER_OBJETIVOS_ENSINO, MARKER_METODOLOGIA, MARKER_AVALIACAO, MARKER_OBSERVACAO.", partes_arquivos)
                    st.session_state.p_temp = res
                    st.session_state.pei_temp = ai.gerar_ia("ESPECIALISTA_CURRICULO", f"Conteúdo Regular: {ctx_curriculo if modo_p=='🎛️ Manual' else info_livro}. Gere adaptação curricular.")
                    st.rerun()
            
            if "p_temp" in st.session_state:
                txt = st.session_state.p_temp
                st.markdown("---")
                t_cont, t_obj, t_met, t_ava, t_obs, t_pei, t_exp = st.tabs(["📚 Conteúdos", "🎯 Objetivos", "🏫 Metodologia", "📝 Avaliação", "💡 Obs", "♿ PEI", "📥 EXPORTAR"])
                
                with t_cont: c_geral = st.text_input("Geral:", ai.extrair_tag(txt, "CONTEUDO_GERAL"), key="v18_edit_cgeral"); c_espec = st.text_area("Específicos:", ai.extrair_tag(txt, "CONTEUDOS_ESPECIFICOS"), key="v18_edit_cespec")
                with t_obj: objs_edit = st.text_area("Objetivos:", ai.extrair_tag(txt, "OBJETIVOS_ENSINO"), key="v18_edit_obj")
                with t_met: met_edit = st.text_area("Metodologia:", ai.extrair_tag(txt, "METODOLOGIA"), height=300, key="v18_edit_met")
                with t_ava: ava_edit = st.text_area("Avaliação:", ai.extrair_tag(txt, "AVALIACAO"), key="v18_edit_ava")
                with t_obs: obs_edit = st.text_area("Recomposição:", ai.extrair_tag(txt, "OBSERVACAO"), key="v18_edit_obs")
                with t_pei: pei_edit = st.text_area("Adaptação:", st.session_state.pei_temp, key="v18_edit_pei")

                with t_exp:
                    st.subheader("🚀 Exportar Planejamento")
                    nome_doc = st.text_input("Título do Documento:", value=f"PLANO_{ano_p}ANO_{sem_p.split(' ')[1]}", key="v18_name_plan_new")
                    conteudo_word = f"CONTEÚDO: {c_geral}\n{c_espec}\n\nOBJETIVOS:\n{objs_edit}\n\nMETODOLOGIA:\n{met_edit}\n\nAVALIAÇÃO:\n{ava_edit}\n\nADAPTAÇÃO PEI:\n{pei_edit}"
                    doc_file = exporter.gerar_docx_profissional(nome_doc.upper(), conteudo_word, {"turma": f"{ano_p}º Ano", "trimestre": "I"})
                    
                    st.download_button("📥 BAIXAR WORD", doc_file, f"{nome_doc}.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)
                    
                    if st.button("☁️ SALVAR NO GOOGLE DRIVE", key="v18_btn_drive_new_fix"):
                        with st.spinner("Enviando..."):
                            link = db.subir_e_converter_para_google_docs(
                            doc_file, 
                            nome_doc, 
                            trimestre="1º Trimestre", # Ou pegue da variável do sistema
                            categoria="Planos de Aula"
                            )
                            if "https://" in str(link):
                                st.success("✅ Salvo com sucesso!")
                                # Versão mais segura do botão de link:
                                st.link_button("🚀 ABRIR NO DRIVE", str(link))
                            else:
                                st.error(link)

                if st.button("💾 Salvar no Banco de Dados", key="v18_save_db_plan"):
                    final = f"MARKER_CONTEUDO_GERAL {c_geral} MARKER_CONTEUDOS_ESPECIFICOS {c_espec} MARKER_OBJETIVOS_ENSINO {objs_edit} MARKER_METODOLOGIA {met_edit} MARKER_AVALIACAO {ava_edit} MARKER_OBSERVACAO {obs_edit} MARKER_ADAPTACAO_PEI {pei_edit}"
                    db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_p.split(" (")[0], f"{ano_p}º", "I Trimestre", "PADRÃO", final])
                    st.success("Salvo!"); del st.session_state.p_temp; st.rerun()
        except Exception as e:
            st.error(f"Erro no Planejador: {e}")

    # --- ABA 2: HISTÓRICO DETALHADO ---
    with tab_hist:
        if not df_planos.empty:
            # CHAVE ÚNICA CORRIGIDA: v18_h_ano_plan
            f_ano_h = st.selectbox("Filtrar por Ano:", ["Todos", "6º", "7º", "8º", "9º"], key="v18_h_ano_plan")
            df_h = df_planos.copy()
            if f_ano_h != "Todos": df_h = df_h[df_h['ANO'] == f_ano_h]
            if not df_h.empty:
                sel_h = st.selectbox("Selecione a Semana:", df_h['SEMANA'].tolist(), key="v18_sel_h_plan")
                raw = df_h[df_h['SEMANA'] == sel_h].iloc[0]['PLANO_TEXTO']
                h_tabs = st.tabs(["📚 Conteúdos", "🎯 Objetivos", "🏫 Metodologia", "📝 Avaliação", "💡 Obs", "♿ PEI", "📥 EXPORTAR"])
                
                with h_tabs[0]: st.markdown(f"**Geral:** {ai.extrair_tag(raw, 'CONTEUDO_GERAL')}\n\n**Específicos:** {ai.extrair_tag(raw, 'CONTEUDOS_ESPECIFICOS')}")
                with h_tabs[1]: st.write(ai.extrair_tag(raw, "OBJETIVOS_ENSINO"))
                with h_tabs[2]: st.info(ai.extrair_tag(raw, "METODOLOGIA"))
                with h_tabs[3]: st.write(ai.extrair_tag(raw, "AVALIACAO"))
                with h_tabs[4]: st.write(ai.extrair_tag(raw, "OBSERVACAO"))
                with h_tabs[5]: st.success(ai.extrair_tag(raw, "ADAPTACAO_PEI"))
                
                with h_tabs[6]: # Aba EXPORTAR do Histórico
                    st.subheader("🚀 Exportar Plano Antigo")
                    # MUDANÇA AQUI: A key muda conforme a semana selecionada (sel_h)
                    # Isso força o título a atualizar para a semana certa!
                    nome_doc_h = st.text_input(
                        "Título:", 
                        value=f"PLANO_REVISAO_{sel_h.replace(' ', '_')}", 
                        key=f"v18_name_plan_{sel_h}" 
                    )
                    txt_word = raw.replace("MARKER_", "\n").replace("_", " ")
                    
                    doc_file_h = exporter.gerar_docx_profissional(nome_doc_h.upper(), txt_word, {"turma": f_ano_h, "trimestre": "I"})
                    
                    st.download_button("📥 BAIXAR WORD", doc_file_h, f"{nome_doc_h}.docx", use_container_width=True, key="btn_dl_h_plan")
                    
                    if st.button("☁️ ENVIAR PARA O DRIVE", key="v18_btn_drive_hist_fix"):
                        with st.spinner("Organizando em Planos de Aula..."):
                            trim_atual, _ = util.obter_info_trimestre(date.today())
                            
                            link = db.subir_e_converter_para_google_docs(
                                doc_file_h, 
                                nome_doc_h, 
                                trimestre=trim_atual, 
                                categoria="Planos de Aula"
                            )
                            if "https://" in str(link):
                                st.success("✅ Plano arquivado no Drive!")
                                st.link_button("🚀 ABRIR NO GOOGLE DOCS", str(link), use_container_width=True)
                                st.markdown(f"🔗 [Link Direto]({link})")
                            else:
                                st.error(f"Erro: {link}")

                                st.error(link)
        else:
            st.info("📭 O banco de dados de planos está vazio.")

    # --- ABA 3: PLANO DE CURSO VIVO ---
    with tab_curso:
        st.markdown("### 📚 Plano de Curso Anual (Status em Tempo Real)")
        
        if df_curriculo.empty:
            st.warning("⚠️ Planilha DB_CURRICULO vazia ou não carregada.")
        else:
            ano_curso = st.selectbox("Selecione a Série:", [6, 7, 8, 9], key="curso_ano")
            
            df_c_ano = df_curriculo[df_curriculo['ANO'] == ano_curso].copy()
            
            conteudos_dados = []
            if not df_registro_aulas.empty:
                df_registro_aulas['TURMA'] = df_registro_aulas['TURMA'].astype(str)
                aulas_ano = df_registro_aulas[df_registro_aulas['TURMA'].str.contains(str(ano_curso))]
                conteudos_dados = " ".join(aulas_ano['CONTEUDO_MINISTRADO'].astype(str).tolist()).upper()
            
            def verificar_status(conteudo_oficial):
                palavras_chave = [p for p in str(conteudo_oficial).upper().split() if len(p) > 3]
                matches = [p for p in palavras_chave if p in conteudos_dados]
                if len(palavras_chave) > 0 and len(matches) / len(palavras_chave) >= 0.5:
                    return "✅ CONCLUÍDO"
                return "⏳ PENDENTE"

            df_c_ano['STATUS'] = df_c_ano['CONTEUDO_ESPECIFICO'].apply(verificar_status)
            
            total = len(df_c_ano)
            concluidos = len(df_c_ano[df_c_ano['STATUS'] == "✅ CONCLUÍDO"])
            progresso = concluidos / total if total > 0 else 0
            
            st.progress(progresso, text=f"Progresso Anual: {int(progresso*100)}%")
            
            st.dataframe(
                df_c_ano[['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO', 'STATUS']],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "STATUS": st.column_config.TextColumn(
                        "Status Real",
                        help="Atualizado automaticamente conforme seus planos semanais",
                        width="small"
                    )
                }
            )

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
