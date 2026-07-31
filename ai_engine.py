import os
import re
import io
import requests
import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv
from google.oauth2 import service_account
from googleapiclient.discovery import build

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==============================================================================
# FUNÇÃO AUXILIAR DE CREDENCIAIS DRIVE
# ==============================================================================
def obter_creds_drive_ai():
    """Retorna as credenciais do Google Drive para leitura nativa de livros PDF"""
    scope = ["https://www.googleapis.com/auth/drive"]
    if os.path.exists("credentials.json"):
        return service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
    elif "gcp_service_account" in st.secrets:
        return service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return None

# ==============================================================================
# DICIONÁRIO DE PERSONAS DE ELITE (V2026.MASTER - PADRÃO ENEM/OBMEP/SAEB)
# ==============================================================================

PERSONAS = {
    "ARQUITETO_EXAMES_ENEM_V2026": """VOCÊ É O ELABORADOR-CHEFE DE ITENS DO INEP / SAEB / OBMEP (PADRÃO ENEM V2026).
    Sua missão é criar avaliações de alta performance pedagógica baseadas na TRI (Teoria de Resposta ao Item) para o Ensino Fundamental.

    🚨 LEI DO TOM E DA CONTEXTUALIZAÇÃO JOVEM (ENEM/OBMEP):
    - Use linguagem direta, técnica, moderna e envolvente para adolescentes.
    - Contextos reais e instigantes: finanças jovens, tecnologia, redes sociais, consumo consciente, meio ambiente, esportes e logística real de Itabuna/Bahia e do Brasil.
    - Aplique raciocínio lógico-matemático no padrão das Olimpíadas de Matemática (OBMEP).

    🚨 LEI DOS DISTRATORES CIENTÍFICOS MAPEADOS (TRI):
    - Cada alternativa errada (A, B, C, D, E) DEVE corresponder a um erro cognitivo previsível do estudante:
      * Distrator 1: Erro de operação inversa ou sinal.
      * Distrator 2: Erro de leitura de enunciado ou confusão de unidades.
      * Distrator 3: Erro por simplificação incompleta ou cálculo parcial.
      * Distrator 4: Raciocínio ingênuo ou precipitado.

    🚨 LEI DA ESTRUTURA E TAGS OBRIGATÓRIAS (RESPEITE OS COLCHETES):
    [SOSA_ID] Nome identificador único da prova.
    [VALOR] Valor total da avaliação (ex: 3.0 ou 10.0).
    [ORIENTACOES] Instruções oficiais de realização.
    [QUESTOES]
    Formato para cada questão:
    **QUESTÃO XX -** (Enunciado contextualizado ENEM/OBMEP)
    (A) ...
    (B) ...
    (C) ...
    (D) ...
    (E) ...
    
    [GABARITO_TEXTO]
    QUESTÃO 01: X
    QUESTÃO 02: Y
    ...

    [GRADE_DE_CORRECAO]
    QUESTÃO 01: [DESCRITOR_SAEB: DXX] | HABILIDADE: Descrição BNCC. | JUSTIFICATIVA: Por que a correta é a correta. | DISTRATORES_CIENTIFICOS: (A) erro por...; (B) erro por...
    ...

    [NIVEL_1]
    (Adaptação Apoio Leve em 3 Alternativas A, B, C com dica inicial [PARA LEMBRAR])

    [NIVEL_2]
    (Adaptação Apoio Moderado em 3 Alternativas A, B, C com [PARA LEMBRAR] + [PASSO A PASSO] + [ PROMPT IMAGEM: Line art, black and white... ])

    [NIVEL_3]
    (Atividades Lúdicas/Sensoriais divididas por BOX 1 a BOX 10 com comandos motores e [ PROMPT IMAGEM: ... ])

    [GABARITO_PEI]
    QUESTÃO 01: X
    QUESTÃO 02: Y
    ...

    🚨 REGRAS DE MATEMÁTICA: Use $$ ... $$ para todas as expressões matemáticas.
    🚨 REGRAS DE IMAGEM: Toda ilustração deve usar [ PROMPT IMAGEM: A4 portrait, clean line art, black and white, no colors, no shadows. All text labels in Portuguese. ]""",

    "PLANE_PEDAGOGICO": """VOCÊ É UM PROFESSOR SÊNIOR REDIGINDO UM PLANO DE ENSINO OFICIAL PARA A PREFEITURA.
    Sua missão é projetar o roteiro da semana com linguagem TÉCNICA, BUROCRÁTICA E DIRETA. 

    🚨 LEI DA LINGUAGEM TÉCNICA:
    - É ESTRITAMENTE PROIBIDO usar primeira pessoa ("nós vamos", "iniciaremos"). Use verbos no infinitivo ("Realizar", "Apresentar", "Resolver", "Mediar").
    - Se 6º/7º Ano: Metodologias concretas e visuais.
    - Se 8º/9º Ano: Metodologias analíticas e finanças/lógica de negócios.
    - Use a realidade local (Itabuna/Bahia) na Sensibilização.

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS):
    [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [COMPETENCIA_GERAL], [OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS], [OBJETIVOS_ENSINO], [JUSTIFICATIVA_PEDAGOGICA], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO], [ESTRATEGIA_DUA_PEI].""",

    "REFINADOR_PEDAGOGICO": """VOCÊ É O MAESTRO COPILOT (V100).
    Retorne EXATAMENTE:
    [MENSAGEM_CHAT] Resposta curta e humana.
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, sem LaTeX, mantendo TODAS as tags originais.""",

    "FORJA_AULA_TEORIA": """VOCÊ É UM PROFESSOR SÊNIOR E AUTOR DE MATERIAIS DIDÁTICOS DE EXCELÊNCIA (PADRÃO CAEd/ENEM).
    Sua missão é escrever APENAS a parte teórica da aula (O Tratado Didático e o Roteiro de Mediação).
    🚨 LEI DO LATEX: Envolva TODA expressão matemática com DUPLO CIFRÃO: $$ ... $$
    🚨 ESTRUTURA: 1. Definições formais | 2. A Lei dos 3 Exemplos (Local, Nacional, Matemática Pura).
    Retorne APENAS o conteúdo dentro da tag [PROFESSOR].""",

    "FORJA_AULA_EXERCICIOS": """VOCÊ É UM PROFESSOR SÊNIOR CRIANDO O MATERIAL DO ALUNO (PADRÃO CAEd/SAEB).
    Linguagem direta de banca examinadora.
    PROIBIDO GEOGEBRA. Use [ PROMPT IMAGEM: ... ] em INGLÊS com texto em Português.
    Estrutura obrigatória: [ALUNO] e [GABARITO]""",

    "FORJA_AULA_PEI": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Crie duas adaptações de exercícios baseadas no material regular.
    [PEI_NIVEL_1]: Apoio Leve, 3 Alternativas (A, B, C).
    [PEI_NIVEL_3]: Apoio Severo (Lúdico/Sensorial) em 10 BOXES sequenciais.
    [GABARITO_PEI]""",

    "FORJA_LOTE_JSON": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd CRIANDO QUESTÕES DE PROVA EM JSON.
    Use $$ ... $$ para matemática.
    RETORNE EXATAMENTE UM JSON NESTE FORMATO:
    {
      "questoes": [
        {
          "q": 1,
          "enunciado": "Texto...",
          "alt_a": "Texto...",
          "alt_b": "Texto...",
          "alt_c": "Texto...",
          "alt_d": "Texto...",
          "alt_e": "Texto...",
          "habilidade": "Código BNCC...",
          "justificativa": "Análise da correta...",
          "distratores": "Análise dos erros cognitivos..."
        }
      ]
    }""",

    "ARQUITETO_EXAMES_V30_ELITE": """VOCÊ É O ARQUITETO-CHEFE DE EXAMES DE ELITE (PADRÃO CAEd/SAEB/ENEM).
    Crie avaliações para CORREÇÃO POR SCANNER. Use LaTeX ($$ ... $$).
    Tags: [VALOR], [ORIENTACOES], [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO], [RESPOSTAS_IA], [PEI], [GABARITO_PEI], [GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "REFINADOR_EXAMES": """VOCÊ É O MAESTRO COPILOT REVISOR DE EXAMES. Retorne [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO].""",
    "REFINADOR_PEI": """VOCÊ É O MAESTRO COPILOT REVISOR DE INCLUSÃO. Retorne [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO].""",

    "ARQUITETO_SONDA_DIAGNOSTICA": """VOCÊ É O PERITO EM PSICOMETRIA (PADRÃO SAEB/CAEd).
    Crie Sondas de Proficiência. Use $$ ... $$.
    Tags: [VALOR], [SOSA_ID], [PROFESSOR], [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO], [RESPOSTAS_IA], [PEI], [GABARITO_PEI], [GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "ARQUITETO_CIENTIFICO_V33": """VOCÊ É O ENGENHEIRO-CHEFE DE INICIAÇÃO CIENTÍFICA.
    Tags: [SOSA_ID], [JUSTIFICATIVA_PHC], [CONTEXTO_INVESTIGATIVO], [MISSÃO_DE_PESQUISA], [PASSO_A_PASSO], [PRODUTO_ESPERADO], [ESTRATEGIA_DUA_PEI], [RUBRICA_DE_MERITO].""",

    "ARQUITETO_REVISAO_V29": """VOCÊ É O ENGENHEIRO DE RECOMPOSIÇÃO DE APRENDIZAGEM. Crie Revisão baseada em prova existente. Tags: [PROFESSOR], [ALUNO], [PEI].""",

    "ARQUITETO_LISTAS_HIBRIDAS": """VOCÊ É O ENGENHEIRO DE CONSOLIDAÇÃO DIDÁTICA. Tags: [SOSA_ID], [PROFESSOR], [ALUNO], [GABARITO], [PEI], [GABARITO_PEI], [IMAGENS].""",

    "ESPECIALISTA_INCLUSAO": """VOCÊ É O ANALISTA PEDAGÓGICO LONGITUDINAL.
    Redija o Dossiê Master Integrado.
    Tags: [DIAGNOSTICO_GERAL], [SOCIAIS], [COMUNICATIVAS], [EMOCIONAIS], [FUNCIONAIS], [DIRETRIZES_CURRICULARES].""",

    "PONTE_COORDENACAO": """VOCÊ É O PROFESSOR RONALDO GOMES. Gere um relato humano e direto para a Coordenação.""",

    "DEFENSOR_PEDAGOGICO": """VOCÊ É O PROFESSOR RONALDO GOMES redigindo mensagem para o responsável do aluno no WhatsApp, explicando vereditos de prova.""",

    "TRADUTOR_CURRICULAR_V39": """VOCÊ É O ARQUITETO DE MATRIZES PEI. Fatie o currículo em blocos [ITEM]...[/ITEM]""",
    
    "ARQUITETO_VARIANTES_V100": """VOCÊ É O ENGENHEIRO DE AVALIAÇÕES ANTI-FRAUDE. Crie VARIANTE (Tipo B, C). Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "ARQUITETO_2A_CHAMADA_V100": """VOCÊ É O ENGENHEIRO DE AVALIAÇÕES DE 2ª CHAMADA (100% DISCURSIVA). Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "ARQUITETO_RECUPERACAO_CIRURGICA": """VOCÊ É O ENGENHEIRO DE RECUPERAÇÃO DATA-DRIVEN (10 QUESTOES DISCURSIVAS). Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "FORJA_ITEM_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd CRIANDO UMA QUESTÃO DE PROVA.
    Tags: [ENUNCIADO], [ALT_A], [ALT_B], [ALT_C], [ALT_D], [ALT_E], [HABILIDADE], [JUSTIFICATIVA], [DISTRATORES].""",

    "FORJA_LOTE_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd. Formato: [ITEM_X] ... [/ITEM_X]""",

    "FORJA_PEI_N1": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO LEVE - TDAH, DISLEXIA, TEA 1). 3 Alternativas (A, B, C).""",

    "FORJA_PEI_N2": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO MODERADO - DEFASAGEM, TEA 2). Estrutura: [PARA LEMBRAR] -> [PASSO A PASSO] -> [ PROMPT IMAGEM: ... ] -> Enunciado -> 3 Alternativas.""",

    "FORJA_PEI_N3": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO SEVERO - TEA 3). 10 BOXES sequenciais + [RUBRICA_DE_OBSERVACAO]."""
}

# ==============================================================================
# MOTOR DE INTELIGÊNCIA COM LEITOR INFALÍVEL DE LIVROS (SOSA V2026.MASTER)
# ==============================================================================
def gerar_ia(persona_key, comando, url_drive=None, usar_busca=True):
    personas_premium = [
        "ARQUITETO_EXAMES_ENEM_V2026",
        "PLANE_PEDAGOGICO", 
        "ESPECIALISTA_INCLUSAO", 
        "FORJA_AULA_TEORIA", 
        "FORJA_TRIADE_PEI", 
        "ARQUITETO_CIENTIFICO_V33",
        "ARQUITETO_RECUPERACAO_CIRURGICA"
    ]
    
    modelo_alvo = "gemini-3.1-pro-preview" if persona_key in personas_premium else "gemini-3-flash-preview"
    
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else [],
        temperature=0.7 if persona_key in personas_premium else 1.0, 
        max_output_tokens=8192,
    )
    
    conteudo_prompt = []
    
    if url_drive and ("drive.google.com" in url_drive or len(url_drive) > 20):
        try:
            file_id_match = re.search(r"(?:id=|[dD]/)([\w-]+)", url_drive)
            file_id = file_id_match.group(1) if file_id_match else url_drive.strip()
            
            creds = obter_creds_drive_ai()
            if creds:
                service = build('drive', 'v3', credentials=creds)
                request_media = service.files().get_media(fileId=file_id)
                pdf_content = request_media.execute()
            else:
                download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
                response = requests.get(download_url, timeout=60)
                pdf_content = response.content

            if b"%PDF" in pdf_content[:20]:
                arquivo_temp = client.files.upload(
                    file=io.BytesIO(pdf_content),
                    config=types.UploadFileConfig(mime_type="application/pdf")
                )
                conteudo_prompt.append(types.Part.from_uri(
                    file_uri=arquivo_temp.uri, 
                    mime_type="application/pdf"
                ))
                
                comando = (
                    "🚨 ANCORAGEM OBRIGATÓRIA NO DOCUMENTO/LIVRO ANEXADO:\n"
                    "Você DEVE ler o arquivo PDF do Livro Didático anexado a esta mensagem. "
                    "É ESTRITAMENTE PROIBIDO inventar conceitos ou exercícios genéricos de fora. "
                    "Baseie todo o conteúdo das aulas, explicações e exercícios DIRETAMENTE no texto e nas páginas do livro fornecido.\n\n"
                    f"{comando}"
                )
                st.toast(f"📖 Livro Didático lido via Drive API com Sucesso!", icon="✅")
            else:
                st.toast("⚠️ O arquivo do Drive não é um PDF válido.", icon="⚠️")
        except Exception as e:
            st.toast(f"⚠️ Aviso na leitura do livro no Drive: {e}", icon="⚠️")

    conteudo_prompt.append(types.Part.from_text(text=f"{PERSONAS.get(persona_key, PERSONAS['ARQUITETO_EXAMES_ENEM_V2026'])}\n\n{comando}"))

    try:
        res = client.models.generate_content(
            model=modelo_alvo, 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        if not res.text: return "⚠️ A IA não retornou dados."
        return res.text
    except Exception as e:
        if "404" in str(e) and "3.1" in modelo_alvo:
            try:
                res_fallback = client.models.generate_content(
                    model="gemini-2.5-pro", 
                    contents=[types.Content(role="user", parts=conteudo_prompt)],
                    config=config
                )
                return res_fallback.text
            except Exception as e_fallback:
                return f"Erro no Fallback da IA: {e_fallback}"
        else:
            return f"Erro na IA ({modelo_alvo}): {e}"

def gerar_ia_json(persona_key, comando, usar_busca=False):
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else [],
        temperature=0.7, 
        response_mime_type="application/json",
    )
    conteudo_prompt = [types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}")]
    try:
        res = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        if not res.text: return {"erro": "A IA retornou uma resposta vazia."}
        
        import json
        texto_limpo = res.text.strip()
        texto_limpo = re.sub(r'^```[a-zA-Z]*\n', '', texto_limpo, flags=re.IGNORECASE)
        texto_limpo = re.sub(r'\n```$', '', texto_limpo)
        return json.loads(texto_limpo)
    except Exception as e:
        return {"erro": str(e)}

# ==============================================================================
# EXTRATOR UNIVERSAL DE TAGS (MULTIMODO V2026.MASTER)
# ==============================================================================
def extrair_tag(texto, tag):
    """
    Extrator Universal Imune a Falhas de Formatação, Markdown e Variações de Brackets.
    """
    if not texto or not isinstance(texto, str): return ""
    tag_busca = tag.upper().strip().replace("[", "").replace("]", "")
    
    tags_mestras = [
        "SOSA_ID", "VALOR", "ORIENTACOES", "QUESTOES", "GABARITO_TEXTO", "GRADE_DE_CORRECAO", 
        "GABARITO", "RESPOSTAS_IA", "PEI", "GABARITO_PEI", "GRADE_DE_CORRECAO_PEI", "RESPOSTAS_PEI_IA", 
        "PROFESSOR", "ALUNO", "IMAGENS", "AULA_ALVO", "HABILIDADE_BNCC", "COMPETENCIAS_FOCO", 
        "COMPETENCIA_GERAL", "OBJETO_CONHECIMENTO", "CONTEUDO_GERAL", "CONTEUDOS_ESPECIFICOS", "OBJETIVOS_ENSINO",
        "JUSTIFICATIVA_PEDAGOGICA", "JUSTIFICATIVA_PHC", "RUBRICA_DE_MERITO", "CONTEXTO_INVESTIGATIVO", 
        "MISSÃO_DE_PESQUISA", "PASSO_A_PASSO", "PRODUTO_ESPERADO", "CONTEXTO_GLOCAL",
        "AULA_1", "AULA_2", "SABADO_LETIVO", "AVALIACAO_DE_MERITO", "ESTRATEGIA_DUA_PEI",
        "MAPA_DE_RECOMPOSICAO", "RESPOSTAS_PEDAGOGICAS", "BASE_DIDATICA",
        "MENSAGEM_CHAT", "CONTEUDO_ATUALIZADO", "SOCIAIS", "COMUNICATIVAS", "EMOCIONAIS", "FUNCIONAIS",
        "OBJETIVO", "ESTRATEGIA", "RECURSO", "DIAGNOSTICO_GERAL", "DIRETRIZES_CURRICULARES", "CHECKLIST",
        "NIVEL_1", "NIVEL_2", "NIVEL_3", "PEI_NIVEL_1", "PEI_NIVEL_3"
    ]
    
    parada = [t for t in tags_mestras if t != tag_busca]
    lista_parada = "|".join(parada)

    # 1. Padrão Em Linha Curta: [TAG]: Valor
    padrao_interno = rf"\[\s*[*#]*\s*{tag_busca}\s*[*#]*\s*\]\s*[:\-]*\s*(.*?)(?=\n|$)"
    match_int = re.search(padrao_interno, texto, re.IGNORECASE)
    if match_int and 0 < len(match_int.group(1).strip()) < 120 and "\n" not in match_int.group(1).strip():
        return match_int.group(1).strip()

    # 2. Padrão Bloco Multilinhas: [TAG] ... [PRÓXIMA_TAG]
    padrao_bloco = rf"\[\s*[*#]*\s*{tag_busca}\s*[*#]*\s*\]\s*[:\-]*\s*(.*?)(?=\s*\[\s*[*#]*\s*(?:{lista_parada})\s*[*#]*\s*\]|--- LINKS ---|$)"
    match_bloco = re.search(padrao_bloco, texto, re.DOTALL | re.IGNORECASE)
    
    if match_bloco:
        res = match_bloco.group(1).strip()
        res = re.sub(r'^```[a-zA-Z]*\n', '', res, flags=re.IGNORECASE)
        res = re.sub(r'\n```$', '', res)
        res_limpo = re.sub(r'[░▒▓█]', '', res)
        res_limpo = re.sub(r'-{3,}', '', res_limpo)
        return res_limpo.strip()
    
    return ""

# ==============================================================================
# EXTRATOR UNIVERSAL DE GABARITOS COM RETROCOMPATIBILIDADE E HERANÇA PEI
# ==============================================================================
def extrair_gab_universal_com_fallback(texto, is_pei=False, nivel_pei="NIVEL_1"):
    """
    EXTRAÍDOR UNIVERSAL DE GABARITOS V2026 (RETROCOMPATÍVEL):
    Lê gabaritos de exames novos (padrão ENEM/SAEB) e exames antigos (legacy de 2025/2026)
    garantindo 100% de preservação de dados e herança PEI automática.
    """
    if not texto or not isinstance(texto, str): return []
    
    mapa_regular = {}
    
    # 1. Tenta extrair o gabarito regular master de [GABARITO_TEXTO] ou [GABARITO]
    raw_reg = extrair_tag(texto, "GABARITO_TEXTO") or extrair_tag(texto, "GABARITO")
    matches_reg = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?0?(\d+)[\s\.\)\-:]+([A-E])", str(raw_reg).upper())
    for q_num_str, letra in matches_reg:
        mapa_regular[int(q_num_str)] = letra
        
    qtd_oficial = max(mapa_regular.keys()) if mapa_regular else 10
    
    # Se for prova regular, retorna o mapa regular ordenado
    if not is_pei:
        if not mapa_regular:
            matches_brutos = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?0?(\d+)[\s\.\)\-:]+([A-E])", texto.upper())
            for q_num_str, letra in matches_brutos:
                q_num = int(q_num_str)
                if q_num not in mapa_regular and q_num <= 20:
                    mapa_regular[q_num] = letra
        qtd_oficial = max(mapa_regular.keys()) if mapa_regular else 10
        return [mapa_regular.get(n, "A") for n in range(1, qtd_oficial + 1)]

    # 2. Se for prova PEI (Inclusiva)
    mapa_pei = {}
    bloco_pei = extrair_tag(texto, nivel_pei) or extrair_tag(texto, "PEI") or extrair_tag(texto, "GABARITO_PEI")
    
    if bloco_pei:
        blocos_q = re.split(r"(?i)(?:QUEST[AÃ]O\s*|Q)0?(\d+)", bloco_pei)
        if len(blocos_q) > 2:
            for idx in range(1, len(blocos_q), 2):
                q_num = int(blocos_q[idx])
                q_conteudo = blocos_q[idx+1]
                m_gab = re.search(r"(?i)GABARITO\s*[:\-]?\s*([A-E])", q_conteudo)
                if m_gab:
                    mapa_pei[q_num] = m_gab.group(1).upper()

        if len(mapa_pei) < qtd_oficial:
            matches_direct = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?0?(\d+)[\s\.\)\-:]+([A-E])", bloco_pei.upper())
            for q_num_str, letra in matches_direct:
                q_num = int(q_num_str)
                if q_num not in mapa_pei and q_num <= qtd_oficial:
                    mapa_pei[q_num] = letra

    # 3. Herança PEI Inteligente: Se for Nível 2 e não encontrou gabarito próprio, herda de Nível 1
    if len(mapa_pei) < qtd_oficial and nivel_pei != "NIVEL_1":
        bloco_n1 = extrair_tag(texto, "NIVEL_1") or extrair_tag(texto, "PEI_NIVEL_1")
        if bloco_n1:
            blocos_q1 = re.split(r"(?i)(?:QUEST[AÃ]O\s*|Q)0?(\d+)", bloco_n1)
            if len(blocos_q1) > 2:
                for idx in range(1, len(blocos_q1), 2):
                    q_num = int(blocos_q1[idx])
                    q_conteudo = blocos_q1[idx+1]
                    m_gab = re.search(r"(?i)GABARITO\s*[:\-]?\s*([A-E])", q_conteudo)
                    if m_gab and q_num not in mapa_pei:
                        mapa_pei[q_num] = m_gab.group(1).upper()

    # 4. Complementação por Herança Regular
    for q_n in range(1, qtd_oficial + 1):
        if q_n not in mapa_pei:
            mapa_pei[q_n] = mapa_regular.get(q_n, "A")

    return [mapa_pei.get(n, "A") for n in range(1, qtd_oficial + 1)]

# ==============================================================================
# MOTOR DE VISÃO COMPUTACIONAL ECONÔMICO (SOSA V2026.MASTER - FLASH ENGINE)
# ==============================================================================
def analisar_gabarito_vision(imagem_bytes):
    try:
        prompt = (
            "Você é um perito em visão computacional de alta precisão. Analise a imagem do gabarito.\n"
            "A tabela possui as colunas: Q (Questão) e as alternativas (A, B, C, D, E para provas regulares ou A, B, C para PEI).\n"
            "MISSÃO DE RACIOCÍNIO:\n"
            "1. Localize a grade de respostas.\n"
            "2. Analise a densidade de preenchimento de cada círculo.\n"
            "3. Se houver uma marcação única e clara, retorne a letra correspondente.\n"
            "4. Se houver DUAS ou mais marcações, retorne 'X' (Dupla Marcação).\n"
            "5. Se a linha estiver totalmente sem marcação, retorne '?' (Vazia).\n"
            "Retorne APENAS um JSON puro no formato: {'01': 'A', '02': 'C', ...}"
        )
        
        conteudo_prompt = [
            types.Part.from_bytes(data=imagem_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)
        ]
        
        res = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        import json
        return json.loads(res.text)
    except Exception as e:
        try:
            res_fb = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=conteudo_prompt)],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            import json
            return json.loads(res_fb.text)
        except Exception as e_fb:
            return {"erro": f"Falha na leitura da imagem: {e_fb}"}

def subir_para_google(caminho_arquivo, nome_exibicao):
    try:
        arquivo_google = client.files.upload(
            file=caminho_arquivo, 
            config=types.UploadFileConfig(display_name=nome_exibicao)
        )
        return arquivo_google.uri
    except Exception as e:
        return f"Erro no upload: {e}"

def realizar_diagnostico_v25(plano_raw, df_curriculo, ano_sel):
    texto_upper = plano_raw.upper()
    modalidade = "CADERNO" 
    if "LIVRO" in texto_upper: modalidade = "LIVRO"
    elif "AVALIAÇÃO" in texto_upper or "PROVA" in texto_upper: modalidade = "PROVA"
    elif "PROJETO" in texto_upper: modalidade = "PROJETO"

    cont_plano = extrair_tag(plano_raw, "CONTEUDOS_ESPECIFICOS").upper().strip()
    base_ano = df_curriculo[df_curriculo['ANO'] == int(ano_sel)] if not df_curriculo.empty and 'ANO' in df_curriculo.columns else pd.DataFrame()
    lista_curriculo = [str(c).upper().strip() for c in base_ano['CONTEUDO_ESPECIFICO'].unique()] if not base_ano.empty and 'CONTEUDO_ESPECIFICO' in base_ano.columns else []
    sincronizado = any(c in cont_plano for c in lista_curriculo)
    status_msg = "Sincronizado" if sincronizado else "Divergente"
    status_cor = "🟢" if sincronizado else "🟡"

    return {
        "modalidade": modalidade,
        "status": f"{status_cor} {status_msg}",
        "conteudo_literal": extrair_tag(plano_raw, "CONTEUDOS_ESPECIFICOS"),
        "objetivo_literal": extrair_tag(plano_raw, "OBJETIVOS_ENSINO")
    }

def gerar_prognostico_pedagogico(dados_stats, contexto_prova):
    try:
        prompt = (
            f"VOCÊ É O PERITO EM AVALIAÇÃO EDUCACIONAL SOSA (PADRÃO SAEB/ENEM).\n"
            f"Realize um diagnóstico pedagógico nos itens abaixo:\n\n"
            f"CONTEXTO DA PROVA:\n{contexto_prova}\n\n"
            f"DESEMPENHO DA TURMA:\n{dados_stats}\n\n"
            f"MISSÃO:\n"
            f"1. MAPEAMENTO DE DESCRITORES SAEB / BNCC.\n"
            f"2. ANÁLISE DE RACIOCÍNIO E ERRO COGNITIVO DOMINANTE DA TURMA.\n"
            f"3. RECOMENDAÇÕES PRÁTICAS DE RECOMPOSIÇÃO."
        )
        
        res = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[types.Part.from_text(text=prompt)]
        )
        return res.text.replace("**", "").replace("#", "").strip()
    except Exception as e:
        return f"Erro na perícia: {e}"

def limpar_links_antigos(texto):
    if not texto: return ""
    partes = re.split(r"--- LINKS ---", texto, flags=re.IGNORECASE)
    return partes[0].strip()
