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

try:
    import cv2
    import numpy as np
    OPENCV_DISPONIVEL = True
except ImportError:
    OPENCV_DISPONIVEL = False

load_dotenv()

# ==============================================================================
# 1. FUNÇÕES AUXILIARES DE CREDENCIAIS & CACHE DE CONTEXTO
# ==============================================================================
def obter_creds_drive_ai():
    """Retorna as credenciais do Google Drive para leitura nativa de livros PDF."""
    scope = ["https://www.googleapis.com/auth/drive"]
    if os.path.exists("credentials.json"):
        return service_account.Credentials.from_service_account_file("credentials.json", scopes=scope)
    elif "gcp_service_account" in st.secrets:
        return service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"], scopes=scope)
    return None

def obter_client_gemini():
    """Inicializa o cliente Gemini com suporte a .env ou st.secrets."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key and hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    if api_key:
        return genai.Client(api_key=api_key)
    return None

client = obter_client_gemini()

if "sosa_pdf_cache" not in st.session_state:
    st.session_state.sosa_pdf_cache = {}

# ==============================================================================
# DIRETRIZ MESTRA DE PROMPTS DE IMAGEM & LATEX (BLINDAGEM UNIVERSAL)
# ==============================================================================
PADRAO_PROMPT_IMAGEM_SOSA = (
    "\n🚨 DIRETRIZES INVIOLÁVEIS PARA PROMPTS DE ILUSTRAÇÃO TÉCNICA:\n"
    "Quando a questão exigir suporte visual essencial (gráficos, tabelas, malhas, figuras geométricas, tiras fracionárias), "
    "inclua OBRIGATORIAMENTE a tag formatada exatamente assim:\n"
    "[ PROMPT IMAGEM: A4 portrait-format educational math worksheet diagram, clean black and white line art, completely pure white background, no colors, no shading, no gradients, no grayscale, thick simple clean sharp outlines, high contrast, perfect for clear physical printing. Visual representation of: [DESCREVA O OBJETO OU DIVISÃO EXATA]. All text labels, numbers, and titles inside the image MUST BE IN PORTUGUESE. ZERO SPOILER: Do not show solutions, answered numbers, or hints of the correct choice. Ample empty space for the student to write, color, trace, or calculate. ]\n"
)

PADRAO_LATEX_SOSA = (
    "\n🚨 LEI DOS CIFRÕES DUPLOS ($$ ... $$) - OBRIGATÓRIO:\n"
    "1. É ESTRITAMENTE PROIBIDO utilizar cifrão simples ($ ... $).\n"
    "2. TODA fração, expoente, raiz, operação ou expressão matemática DEVE ser envolvida por DUPLO CIFRÃO: $$ \\frac{a}{b} $$, $$ 3\\frac{1}{2} $$, $$ 10^2 $$, $$ 25\\% $$, $$ 90^\\circ $$.\n"
    "3. Valores monetários devem ser escritos como R$ 12,50 (sem barra invertida R\\$).\n"
)

# ==============================================================================
# 2. DICIONÁRIO DE PERSONAS DE ELITE (PRESERVAÇÃO INTEGRAL DE 100% DAS PERSONAS)
# ==============================================================================

PERSONAS = {
    "ARQUITETO_EXAMES_ENEM_V2026": f"""VOCÊ É O ELABORADOR-CHEFE DE ITENS DO INEP / SAEB / OBMEP (PADRÃO ENEM V2026 E BNCC).
    Sua missão é criar avaliações de alta performance pedagógica baseadas na TRI (Teoria de Resposta ao Item) e no conceito de LETRAMENTO MATEMÁTICO para o Ensino Fundamental.

    🚨 LEI DO LETRAMENTO MATEMÁTICO (BNCC):
    - Cada questão deve apresentar uma situação-problema autêntica (contexto de Itabuna/BA, dados socioambientais, economia local, tabelas do IBGE/CEPLAC, finanças ou cotidiano).
    - Exija do estudante a capacidade de formular, empregar, interpretar e avaliar a matemática.
    - Inclua, sempre que pertinente, suporte visual em tabelas formatadas em Markdown (| Coluna 1 | Coluna 2 |).

    🚨 LEI DA SANITIZAÇÃO ABSOLUTA:
    - Inicie a resposta DIRETAMENTE na primeira tag [VALOR: X.X]. Sem saudações ou conversas.

    {PADRAO_LATEX_SOSA}
    {PADRAO_PROMPT_IMAGEM_SOSA}

    🚨 ESTRUTURA OBRIGATÓRIA DE ENTREGA:
    [VALOR: 4.0]

    [QUESTOES]
    **QUESTÃO 01 -** Enunciado contextualizado com situação-problema...
    (A) ...
    (B) ...
    (C) ...
    (D) ...
    (E) ...

    [GABARITO_TEXTO]
    QUESTÃO 01: E
    QUESTÃO 02: B

    [GRADE_DE_CORRECAO]
    QUESTÃO 01: [DESCRITOR_SAEB: D12] | JUSTIFICATIVA: Explicação da correta... | DISTRATORES_CIENTIFICOS: (A) erro por...; (B) erro por...

    [PEI_NIVEL_1]
    **QUESTÃO 01 -** Enunciado reduzido e palavra-chave em **negrito**.
    *(Dica: Dica objetiva entre parênteses)*.
    (A) Opção 1
    (B) Opção 2
    (C) Opção 3

    [PEI_NIVEL_2]
    **QUESTÃO 01 -** Enunciado adaptado.
    [PARA LEMBRAR] Conceito curto.
    [PASSO A PASSO]
    1. Etapa 1
    2. Etapa 2
    (A) Opção 1
    (B) Opção 2
    (C) Opção 3

    [PEI_NIVEL_3]
    1. [BOX 1] Nome da Ação: Comando motor impresso no papel (Pintar/Ligar/Pontilhado/Circular).
    [ PROMPT IMAGEM: A4 portrait-format educational math worksheet, clean black and white line art, completely pure white background, no colors, no shading, thick simple outlines, high contrast. Labels in Portuguese. Zero spoiler. ]
    ... (Até o BOX 10)

    [RUBRICA_DE_OBSERVACAO]
    - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou

    [GABARITO_PEI]
    QUESTÃO 01: A
    QUESTÃO 02: B""",

    "ARQUITETO_RECUPERACAO_DISCURSIVA": f"""VOCÊ É O ELABORADOR-CHEFE DE AVALIAÇÕES DISCURSIVAS E RECUPERAÇÃO PARALELA (PADRÃO BNCC/SAEB/ITABUNA).
    Sua missão é criar uma avaliação DISCURSIVA / ABERTA valendo EXATAMENTE de 0,0 a 10,0 pontos, baseada nas questões espelho dos conteúdos mais críticos do trimestre.

    🚨 REGRAS INQUEBRÁVEIS DE AVALIAÇÃO DISCURSIVA:
    1. É ESTRITAMENTE PROIBIDO incluir alternativas de múltipla escolha (A, B, C, D, E) no bloco regular [QUESTOES]. Todas as questões regulares DEVEM ser 100% abertas.
    2. Cada questão deve exigir do estudante a resolução por etapas, a apresentação da MEMÓRIA DE CÁLCULO e a declaração da RESPOSTA FINAL com unidade de medida.
    3. Distribua a pontuação somando exatamente 10,0 pontos (ex: 10 questões de 1,0 ponto cada, ou 5 questões de 2,0 pontos cada).
    4. Formatação rigorosa dos enunciados:
       **QUESTÃO 01 (Valor: 1,0 pt) -** [Enunciado contextualizado com situação-problema autêntica e tabela Markdown se houver dados]

    {PADRAO_LATEX_SOSA}
    {PADRAO_PROMPT_IMAGEM_SOSA}

    🚨 TAGS OBRIGATÓRIAS DE ENTREGA:
    [VALOR: 10.0]

    [QUESTOES]
    **QUESTÃO 01 (Valor: 1,0 pt) -** Enunciado da questão aberta...
    **QUESTÃO 02 (Valor: 1,0 pt) -** Enunciado da questão aberta...

    [GABARITO_TEXTO]
    QUESTÃO 01: [Resolução matemática detalhada passo a passo e resposta final]
    QUESTÃO 02: [Resolução matemática detalhada passo a passo e resposta final]

    [GRADE_DE_CORRECAO]
    QUESTÃO 01: [DESCRITOR_SAEB: D12] | CRITÉRIOS: Cálculo completo (1,0 pt); Erro de conta mantendo o raciocínio (0,5 pt); Sem cálculo (0,0 pt).
    QUESTÃO 02: ...

    [PEI_NIVEL_1]
    **QUESTÃO 01 (Valor: 1,0 pt) -** Enunciado simplificado com palavra-chave em **negrito**.
    *(Dica: Pista didática objetiva entre parênteses)*.
    (A) Opção 1
    (B) Opção 2
    (C) Opção 3

    [PEI_NIVEL_2]
    **QUESTÃO 01 (Valor: 1,0 pt) -** Enunciado adaptado.
    [PARA LEMBRAR] Dica teórica curta.
    [PASSO A PASSO]
    1. Etapa 1
    2. Etapa 2
    (A) Opção 1
    (B) Opção 2
    (C) Opção 3

    [PEI_NIVEL_3]
    1. [BOX 1] Nome da Ação: Comando motor impresso no papel (Pintar/Ligar/Cobrir/Circular/Marcar X).
    [ PROMPT IMAGEM: A4 portrait-format educational math worksheet, clean black and white line art, completely pure white background, no colors, no shading, thick simple outlines, high contrast. Labels in Portuguese. Zero spoiler. ]
    ... (Até o BOX 10)

    [RUBRICA_DE_OBSERVACAO]
    - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou

    [GABARITO_PEI]
    QUESTÃO 01: A
    QUESTÃO 02: B""",

    "PLANE_PEDAGOGICO": f"""VOCÊ É UM PROFESSOR SÊNIOR REDIGINDO UM PLANO DE ENSINO SEMANAL OFICIAL (PADRÃO BNCC/SAEB/ITABUNA).
    Sua missão é projetar o roteiro pedagógico da semana com linguagem TÉCNICA, OBJETIVA E DIRETA.

    🚨 LEI DA ESTRUTURA DE AULA EXPOSITIVA OBJETIVA:
    - Cada aula ([AULA_1], [AULA_2], [SABADO_LETIVO]) deve ser estruturada estritamente nos 3 blocos:
      • INÍCIO (Sensibilização & Gatilho - 10 min): Pergunta provocadora vinculada a situações reais, notícias, tecnologia ou economia regional de Itabuna/BA.
      • MEIO (Fundamentação & Conceito - 25 min): Roteiro de Lousa/Quadro, demonstração do algoritmo e citação explícita das páginas/exercícios do Livro Didático.
      • FIM (Fixação & Prática Guiada - 15 min): Resolução de exercícios no quadro, verificação de dúvidas e síntese.

    {PADRAO_LATEX_SOSA}

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS COM COLCHETES):
    [HABILIDADE_BNCC]
    [COMPETENCIAS_FOCO]
    [OBJETO_CONHECIMENTO]
    [CONTEUDOS_ESPECIFICOS]
    [OBJETIVOS_ENSINO]
    [JUSTIFICATIVA_PEDAGOGICA]
    [AULA_1]
    [AULA_2]
    [SABADO_LETIVO]
    [AVALIACAO_DE_MERITO]
    [ESTRATEGIA_DUA_PEI]""",

    "REFINADOR_PEDAGOGICO": """VOCÊ É O MAESTRO COPILOT (V100).
    Retorne EXATAMENTE:
    [MENSAGEM_CHAT] Resposta curta e humana.
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, mantendo TODAS as tags originais e fórmulas com duplo cifrão $$ ... $$.""",

    "FORJA_AULA_TEORIA": f"""VOCÊ É UM PROFESSOR SÊNIOR E AUTOR DE MATERIAIS DIDÁTICOS DE EXCELÊNCIA (PADRÃO CAEd/SAEB/BNCC).
    Sua missão é escrever APENAS o Tratado Didático e o Roteiro de Lousa do Professor ([PROFESSOR]).

    Estrutura obrigatória dentro da tag [PROFESSOR]:
    1. INÍCIO (Sensibilização & Gatilho - 10 min)
    2. MEIO (Fundamentação & Conceito - 25 min com roteiro exato de quadro e páginas do livro)
    3. FIM (Fixação & Prática Guiada - 15 min)

    {PADRAO_LATEX_SOSA}
    Retorne APENAS o conteúdo dentro da tag [PROFESSOR].""",

    "FORJA_AULA_EXERCICIOS": f"""VOCÊ É UM ELABORADOR DE ITENS DE ELITE CRIANDO A FOLHA DO ALUNO.
    Sua missão é gerar a lista de exercícios para a turma regular ([ALUNO]) e a resolução comentada ([GABARITO]).

    - Crie situações-problema autênticas com tabelas formatadas em Markdown (| Coluna 1 | Coluna 2 |).
    - Formatação limpa dos enunciados: **QUESTÃO 01 -** [Texto direto].
    {PADRAO_LATEX_SOSA}
    {PADRAO_PROMPT_IMAGEM_SOSA}

    Estrutura obrigatória: [ALUNO] e [GABARITO]""",

    "FORJA_AULA_PEI": f"""VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Crie adaptações de exercícios baseadas no conteúdo ESTRITAMENTE TRABALHADO NA AULA REGULAR.

    {PADRAO_LATEX_SOSA}
    {PADRAO_PROMPT_IMAGEM_SOSA}

    [PEI_NIVEL_1]: Apoio Leve, 3 Alternativas (A, B, C) com dica objetiva entre parênteses.
    [PEI_NIVEL_2]: Apoio Moderado, 3 Alternativas (A, B, C) com caixa [PARA LEMBRAR] e [PASSO A PASSO].
    [PEI_NIVEL_3]: Apoio Severo em 10 BOXES sequenciais de atividades 100% IMPRESSAS NO PAPEL (Pintar, Cobrir Pontilhado, Ligar Colunas, Circular, Marcar X).
    [RUBRICA_DE_OBSERVACAO]
    [GABARITO_PEI]""",

    "FORJA_LOTE_JSON": f"""VOCÊ É UM ELABORADOR DE ITENS DE ELITE DO INEP CRIANDO QUESTÕES EM JSON.
    
    🚨 LEI DO LATEX EM JSON: Envolva TODA expressão matemática, fração ou símbolo com duplo cifrão e barras duplas: $$ \\\\frac{{a}}{{b}} $$.

    RETORNE EXATAMENTE UM JSON NESTE FORMATO:
    {{
      "questoes": [
        {{
          "q": 1,
          "enunciado": "Texto do enunciado com tabela em Markdown quando houver dados...",
          "alt_a": "$$ \\\\frac{{1}}{{2}} $$",
          "alt_b": "$$ \\\\frac{{1}}{{4}} $$",
          "alt_c": "$$ \\\\frac{{3}}{{4}} $$",
          "alt_d": "$$ \\\\frac{{2}}{{5}} $$",
          "alt_e": "$$ \\\\frac{{4}}{{5}} $$",
          "habilidade": "Descritor SAEB (ex: EF06MA01)",
          "justificativa": "Análise da alternativa correta...",
          "distratores": "Análise dos erros cognitivos..."
        }}
      ]
    }}""",

    "FORJA_ITEM_REGULAR": f"""VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd/BNCC CRIANDO UMA QUESTÃO DE PROVA CONTEXTUALIZADA.
    
    {PADRAO_LATEX_SOSA}
    {PADRAO_PROMPT_IMAGEM_SOSA}

    Tags obrigatórias: [ENUNCIADO], [ALT_A], [ALT_B], [ALT_C], [ALT_D], [ALT_E], [HABILIDADE], [JUSTIFICATIVA], [DISTRATORES].""",

    "FORJA_PEI_N1": f"""VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO LEVE - TDAH, DISLEXIA, TEA 1).
    🚨 INICIE DIRETAMENTE NA TAG [PEI_NIVEL_1].
    - Adapte as questões regulares reduzindo para exatamente 3 Alternativas (A, B, C).
    - Rótulo padrão: **QUESTÃO 01 -**, **QUESTÃO 02 -**, etc.
    - Inclua uma dica objetiva entre parênteses: *(Dica: ...)*.
    - Palavras-chave do comando em **negrito**.
    {PADRAO_LATEX_SOSA}""",

    "FORJA_PEI_N2": f"""VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO MODERADO - DEFASAGEM, TEA 2).
    🚨 INICIE DIRETAMENTE NA TAG [PEI_NIVEL_2].
    - Estrutura fixa para cada questão:
      **QUESTÃO XX -** Enunciado adaptado.
      [PARA LEMBRAR] Conceito-chave curto.
      [PASSO A PASSO]
      1. Etapa 1
      2. Etapa 2
      (A) Opção 1
      (B) Opção 2
      (C) Opção 3
    {PADRAO_LATEX_SOSA}""",

    "FORJA_PEI_N3": f"""VOCÊ É O ESPECIALISTA EM INCLUSÃO E DUA (PEI NÍVEL 3 - SUPORTE SEVERO / TEA 3 / NO PAPEL).
    🚨 INICIE DIRETAMENTE NA TAG [PEI_NIVEL_3].
    - Crie exatamente 10 BOXES de atividades 100% IMPRESSAS NO PAPEL.
    - Todas as tarefas devem envolver AÇÕES NO PAPEL: PINTAR, LIGAR COLUNAS, COBRIR PONTILHADO, CIRCULAR O ITEM E MARCAR [X].
    - Para cada BOX, inclua obrigatoriamente um:
      [ PROMPT IMAGEM: A4 portrait-format educational math worksheet, clean black and white line art, completely pure white background, no colors, no shading, thick simple outlines, high contrast. Labels in Portuguese. Zero spoiler. ]
    - Finalize obrigatoriamente com:
      [RUBRICA_DE_OBSERVACAO]
      - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
      - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
      - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
      - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou""",

    "ESPECIALISTA_INCLUSAO": f"""VOCÊ É UM PSICOPEDAGOGO E ESPECIALISTA EM EDUCAÇÃO INCLUSIVA (DUA/PEI/BNCC).
    Sua missão é redigir um Dossiê de Acompanhamento PEI/Inclusivo humano, empático, técnico e orgânico.
    {PADRAO_LATEX_SOSA}
    Tags obrigatórias: [DIAGNOSTICO_GERAL], [SOCIAIS], [COMUNICATIVAS], [EMOCIONAIS], [FUNCIONAIS], [DIRETRIZES_CURRICULARES]""",

    "ARQUITETO_PEI_V24": f"""VOCÊ É O ARQUITETO PEI V24 ESPECIALISTA EM DESENHO UNIVERSAL PARA APRENDIZAGEM.
    Adapte o material pedagógico garantindo acessibilidade, comandos diretos e fórmulas com duplo cifrão $$ ... $$.""",

    "ARQUITETO_CIENTIFICO_V33": f"""VOCÊ É O ARQUITETO DE PROJETOS E INVESTIGAÇÃO CIENTÍFICA (PADRÃO BNCC/ITABUNA).
    Projete roteiros de pesquisa integrando Matemática, Meio Ambiente e Economia Regional. {PADRAO_LATEX_SOSA}""",

    "ARQUITETO_REVISAO_V29": f"""VOCÊ É O ARQUITETO DE RECOMPOSIÇÃO E REVISÃO DE ELITE (PADRÃO SAEB/CAEd).
    Analise uma avaliação anterior e forje um Caderno de Recomposição focado nos descritores críticos com menor taxa de acerto.
    {PADRAO_LATEX_SOSA} {PADRAO_PROMPT_IMAGEM_SOSA}""",

    "ARQUITETO_VARIANTES_V100": f"""VOCÊ É O GERADOR DE VARIANTES ANTI-FRAUDE (TIPO B, C, D).
    Embaralhe as alternativas, altere os dados numéricos mantendo a mesma estrutura cognitiva e gere o novo gabarito com precisão. {PADRAO_LATEX_SOSA}""",

    "DEFENSOR_PEDAGOGICO": f"""VOCÊ É O DEFENSOR PEDAGÓGICO DO COMPONENTE DE MATEMÁTICA.
    Redija justificativas técnicas e empáticas fundamentadas na BNCC/SAEB para apresentação a pais ou coordenação pedagógica.""",

    "TRADUTOR_CURRICULAR_V39": f"""VOCÊ É O TRADUTOR CURRICULAR DE MATEMÁTICA PARA PLANOS EDUCACIONAIS INDIVIDUALIZADOS (PEI).
    Converta os objetivos de aprendizagem em estratégias de acessibilidade funcional e recursos materiais concretos diversificados. {PADRAO_LATEX_SOSA}"""
}

# ==============================================================================
# 3. MOTOR PRINCIPAL DE IA (ADEQUADO À API GEMINI 2026 - SEM TEMPERATURE)
# ==============================================================================

def gerar_ia(persona_key, comando, url_drive=None, usar_busca=False, recorte_livro=None):
    """
    SOSA V2026.ULTIMATE - ROTEAMENTO DE ALTA EFICIÊNCIA & ECONOMIA:
    - Nível 2 (Criação Complexa / TRI / Planos / Recuperação): Gemini 3.7 Flash.
    - Nível 1 (Rotina / Ajustes / PEI N1-N3): Gemini 3.5 Flash-Lite.
    """
    client_local = obter_client_gemini()
    if not client_local:
        return "⚠️ Chave GEMINI_API_KEY não configurada no ambiente."

    personas_alta_complexidade = [
        "ARQUITETO_EXAMES_ENEM_V2026",
        "PLANE_PEDAGOGICO", 
        "ESPECIALISTA_INCLUSAO", 
        "FORJA_AULA_TEORIA", 
        "ARQUITETO_CIENTIFICO_V33",
        "ARQUITETO_REVISAO_V29",
        "ARQUITETO_RECUPERACAO_DISCURSIVA"
    ]
    
    if persona_key in personas_alta_complexidade:
        modelos_tentativa = ["gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite"]
    else:
        modelos_tentativa = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.7-flash"]

    tools_config = []
    if usar_busca:
        try:
            tools_config.append(types.Tool(google_search=types.GoogleSearch()))
        except:
            tools_config.append({'google_search': {}})

    config = types.GenerateContentConfig(
        tools=tools_config if tools_config else None,
        max_output_tokens=8192
    )
    
    conteudo_prompt = []
    
    trava_realidade = (
        "\n\n🚨 ================= CLÁUSULA INQUEBRÁVEL DE ZERO-ALUCINAÇÃO & PADRÃO SOSA =================\n"
        "1. É ESTRITAMENTE PROIBIDO inventar contextos de ficção fora da realidade fornecida.\n"
        "2. Todas as frações, potências e equações DEVEM usar OBRIGATORIAMENTE duplo cifrão espaçado: $$ \\frac{a}{b} $$.\n"
        "3. PROMPTS DE IMAGEM: Apenas quando estritamente necessários, em arte linear preto e branco formato A4 retrato, sem cores, sem sombras, fundo branco puro, sem respostas ou pistas visuais da solução, com rótulos em português.\n"
        "===============================================================================================\n\n"
    )

    instrucao_livro = ""
    if recorte_livro and len(str(recorte_livro).strip()) > 5:
        instrucao_livro = (
            f"\n📖 CONTEXTO REAL E EXERCÍCIOS LIDOS DO LIVRO DIDÁTICO / LOUSA:\n\"\"\"\n{recorte_livro}\n\"\"\"\n"
        )

    if url_drive and ("drive.google.com" in url_drive or len(url_drive) > 20):
        try:
            file_id_match = re.search(r"(?:id=|[dD]/)([\w-]+)", url_drive)
            file_id = file_id_match.group(1) if file_id_match else url_drive.strip()
            
            if hasattr(st.session_state, "sosa_pdf_cache") and file_id in st.session_state.sosa_pdf_cache:
                arquivo_temp = st.session_state.sosa_pdf_cache[file_id]
                conteudo_prompt.append(types.Part.from_uri(
                    file_uri=arquivo_temp.uri, 
                    mime_type="application/pdf"
                ))
            else:
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
                    arquivo_temp = client_local.files.upload(
                        file=io.BytesIO(pdf_content),
                        config=types.UploadFileConfig(mime_type="application/pdf")
                    )
                    if hasattr(st.session_state, "sosa_pdf_cache"):
                        st.session_state.sosa_pdf_cache[file_id] = arquivo_temp
                    conteudo_prompt.append(types.Part.from_uri(
                        file_uri=arquivo_temp.uri, 
                        mime_type="application/pdf"
                    ))
        except Exception as e:
            print(f"Aviso leitura Drive PDF: {e}")

    persona_prompt = PERSONAS.get(persona_key, PERSONAS["ARQUITETO_EXAMES_ENEM_V2026"])
    prompt_final = f"{persona_prompt}{trava_realidade}{instrucao_livro}\n\n{comando}"
    conteudo_prompt.append(types.Part.from_text(text=prompt_final))

    erros_log = []
    for mod in modelos_tentativa:
        try:
            res = client_local.models.generate_content(
                model=mod, 
                contents=[types.Content(role="user", parts=conteudo_prompt)],
                config=config
            )
            
            texto_retornado = ""
            if hasattr(res, "text") and res.text and len(res.text.strip()) > 0:
                texto_retornado = res.text.strip()
            elif hasattr(res, "candidates") and res.candidates:
                for cand in res.candidates:
                    if hasattr(cand, "content") and hasattr(cand.content, "parts"):
                        for part in cand.content.parts:
                            if hasattr(part, "text") and part.text:
                                texto_retornado += part.text + "\n"
            
            if texto_retornado.strip():
                # Sanitização automática de cifrões simples perdidos para duplo cifrão
                texto_final_sanitizado = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', r'$$ \1 $$', texto_retornado.strip())
                return texto_final_sanitizado
        except Exception as e_mod:
            erros_log.append(f"{mod}: {str(e_mod)}")
            continue

    return f"⚠️ Erro ao consultar a IA nos modelos ({', '.join(modelos_tentativa)}). Detalhes técnicos: {'; '.join(erros_log)}"

# ==============================================================================
# 4. MOTOR DE GERAÇÃO JSON DE ALTA VELOCIDADE (SEM TEMPERATURE)
# ==============================================================================

def gerar_ia_json(persona_key, comando, usar_busca=False):
    """
    SOSA V2026: Geração de JSON estruturado de alta velocidade e custo quase zero.
    """
    client_local = obter_client_gemini()
    if not client_local:
        return {"erro": "Chave GEMINI_API_KEY não configurada."}

    tools_config = []
    if usar_busca:
        try:
            tools_config.append(types.Tool(google_search=types.GoogleSearch()))
        except:
            tools_config.append({'google_search': {}})

    config = types.GenerateContentConfig(
        tools=tools_config if tools_config else None,
        response_mime_type="application/json",
        max_output_tokens=8192
    )
    
    trava_realidade_json = (
        "\n\n🚨 REGRAS RÍGIDAS DE GROUNDING (ZERO ALUCINAÇÃO):\n"
        "1. É PROIBIDO inventar contextos fictícios fora do fornecido.\n"
        "2. LATEX EM JSON: Use barra dupla e duplo cifrão obrigatoriamente: $$ \\\\frac{a}{b} $$.\n\n"
    )
    
    persona_prompt = PERSONAS.get(persona_key, PERSONAS["FORJA_LOTE_JSON"])
    conteudo_prompt = [types.Part.from_text(text=f"{persona_prompt}\n{trava_realidade_json}\n\n{comando}")]
    
    modelos_json = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.7-flash"]
    
    for mod in modelos_json:
        try:
            res = client_local.models.generate_content(
                model=mod, 
                contents=[types.Content(role="user", parts=conteudo_prompt)],
                config=config
            )
            if not res.text: continue
            
            import json
            texto_limpo = res.text.strip()
            texto_limpo = re.sub(r'^```[a-zA-Z]*\n', '', texto_limpo, flags=re.IGNORECASE)
            texto_limpo = re.sub(r'\n```$', '', texto_limpo)
            
            match = re.search(r'\{.*\}', texto_limpo, re.DOTALL)
            if match:
                json_str = match.group(0)
                json_str_reparado = re.sub(r'\\(?![/"bfnrtu\\])', r'\\\\', json_str)
                try:
                    return json.loads(json_str_reparado)
                except json.JSONDecodeError:
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        json_str_clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str_reparado)
                        return json.loads(json_str_clean)
            
            return json.loads(texto_limpo)
        except Exception as e:
            print(f"Erro no parsing JSON com {mod}: {e}")
            continue
            
    return {"erro": "Não foi possível gerar um JSON válido no momento. Tente novamente."}

# ==============================================================================
# 5. MOTOR DE VISÃO COMPUTACIONAL LOCAL & SCANNER HÍBRIDO (CIR)
# ==============================================================================

def ordenar_pontos_quadrado(pts):
    """Ordena 4 pontos nas posições: [topo-esq, topo-dir, base-dir, base-esq]."""
    if not OPENCV_DISPONIVEL: return pts
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect

def tratar_imagem_para_leitura(imagem_bytes):
    """Redimensiona e clareia a imagem suavemente antes de enviar para a IA."""
    if not OPENCV_DISPONIVEL: return imagem_bytes
    try:
        nparr = np.frombuffer(imagem_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return imagem_bytes

        h, w = img.shape[:2]
        if max(h, w) > 1200:
            scale = 1200.0 / max(h, w)
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)

        _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        return buffer.tobytes()
    except:
        return imagem_bytes

def analisar_gabarito_hibrido(imagem_bytes, qtd_questoes=10, is_pei=False):
    """
    SOSA V2026.DIRECT_VISION_ANTI_TROCA:
    Leitura Direta por Visão Computacional Gemini 3.5 Flash-Lite (< 1s por prova).
    """
    imagem_pronta = tratar_imagem_para_leitura(imagem_bytes)
    
    try:
        client_local = obter_client_gemini()
        if not client_local:
            return {"respostas": {}, "nome_lido_folha": "", "imagem_alinhada": imagem_pronta, "sucesso_local": False}

        tipo_opcoes = "A, B, C" if is_pei else "A, B, C, D, E"
        
        prompt = f"""Você é um perito em visão computacional e leitura de gabaritos escolares.
Analise a imagem da folha de respostas anexada com extrema atenção às marcações e ao cabeçalho.

ESTRUTURA DO CARTÃO:
1. CABEÇALHO:
   - No topo, no campo 'ESTUDANTE:', identifique o nome do aluno escrito à caneta ou lápis.

2. CARTÃO DE RESPOSTAS:
   - Total de Questões: {qtd_questoes} questões (de 01 a {qtd_questoes:02d}).
   - Alternativas: {tipo_opcoes}.

REGRAS DE LEITURA:
1. Identifique qual letra ({tipo_opcoes}) foi marcada em cada questão de 01 a {qtd_questoes:02d}.
2. Se houver dupla marcação na mesma questão, retorne 'X'.
3. Se a questão estiver em branco, retorne '?'.
4. No campo 'nome_estudante', retorne o nome do aluno escrito no cabeçalho.

RETORNE APENAS UM JSON PURO NO FORMATO:
{{
  "nome_estudante": "NOME DO ESTUDANTE",
  "respostas": {{
    "01": "B",
    "02": "A",
    ...
    "{qtd_questoes:02d}": "C"
  }}
}}"""

        conteudo_prompt = [
            types.Part.from_bytes(data=imagem_pronta, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)
        ]

        config_visao = types.GenerateContentConfig(
            response_mime_type="application/json"
        )

        modelos_tentativa = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash", "gemini-3.7-flash"]
        respostas_json = None
        import json
        
        for mod in modelos_tentativa:
            try:
                res = client_local.models.generate_content(
                    model=mod,
                    contents=[types.Content(role="user", parts=conteudo_prompt)],
                    config=config_visao
                )
                if res and res.text:
                    texto_limpo = res.text.strip()
                    texto_limpo = re.sub(r'^```[a-zA-Z]*\n', '', texto_limpo, flags=re.IGNORECASE)
                    texto_limpo = re.sub(r'\n```$', '', texto_limpo)
                    respostas_json = json.loads(texto_limpo)
                    if respostas_json and len(respostas_json) > 0:
                        break
            except Exception as e_mod:
                continue

        if respostas_json:
            respostas_dict = {}
            nome_detectado_cabecalho = ""
            if "respostas" in respostas_json and isinstance(respostas_json["respostas"], dict):
                respostas_dict = respostas_json["respostas"]
                nome_detectado_cabecalho = str(respostas_json.get("nome_estudante", "")).strip()
            else:
                respostas_dict = respostas_json

            return {
                "respostas": respostas_dict,
                "nome_lido_folha": nome_detectado_cabecalho,
                "imagem_alinhada": imagem_pronta,
                "sucesso_local": True
            }
        else:
            return {
                "respostas": {},
                "nome_lido_folha": "",
                "imagem_alinhada": imagem_pronta,
                "sucesso_local": False
            }

    except Exception as e:
        print(f"Erro geral no scanner: {e}")
        return {
            "respostas": {},
            "nome_lido_folha": "",
            "imagem_alinhada": imagem_pronta,
            "sucesso_local": False
        }

# ==============================================================================
# 6. EXTRATOR UNIVERSAL DE TAGS & GABARITOS
# ==============================================================================

def extrair_tag(texto, tag):
    if not texto or not isinstance(texto, str): return ""
    tag_busca = tag.upper().strip().replace("[", "").replace("]", "")
    
    if tag_busca in ["ALUNO", "QUESTOES", "CADERNO_DE_REVISAO"]:
        guia = extrair_tag_simples(texto, "GUIA_DE_ESTUDO_ALUNO")
        questoes = extrair_tag_simples(texto, "QUESTOES")
        if guia and questoes: return f"{guia}\n\n{questoes}"
        elif questoes: return questoes
        elif guia: return guia

    return extrair_tag_simples(texto, tag_busca)

def extrair_tag_simples(texto, tag_busca):
    alias_map = {
        "PROFESSOR": ["PROFESSOR", "ROTEIRO_DO_PROFESSOR", "GUIA_PROFESSOR", "ROTEIRO_DE_MEDIACAO", "BASE_DIDATICA", "ROTEIRO_DO_PROFESSOR - RECOMPOSIÇÃO"],
        "ALUNO": ["ALUNO", "GUIA_DE_ESTUDO_ALUNO", "QUESTOES", "QUESTOES_ESPELHO", "CADERNO_DE_REVISAO", "GUIA_DE_ESTUDO_DO_ALUNO"],
        "QUESTOES": ["QUESTOES", "QUESTOES_ESPELHO", "CADERNO_DE_REVISAO", "GUIA_DE_ESTUDO_DO_ALUNO"],
        "GABARITO": ["GABARITO_TEXTO", "GABARITO", "GABARITO_REGULAR", "RESPOSTAS_IA"],
        "GABARITO_TEXTO": ["GABARITO_TEXTO", "GABARITO", "GABARITO_REGULAR", "RESPOSTAS_IA"],
        "PEI_NIVEL_1": ["PEI_NIVEL_1", "NIVEL_1", "PEI_1", "PEI", "QUESTOES_PEI_N1"],
        "PEI_NIVEL_2": ["PEI_NIVEL_2", "NIVEL_2", "PEI_2", "QUESTOES_PEI_N2"],
        "PEI_NIVEL_3": ["PEI_NIVEL_3", "NIVEL_3", "PEI_3", "QUESTOES_PEI_N3", "PEI_QUALITATIVA"],
        "RUBRICA_DE_OBSERVACAO": ["RUBRICA_DE_OBSERVACAO", "RUBRICA_DE_MERITO", "RUBRICA"],
        "GABARITO_PEI": ["GABARITO_PEI", "RESPOSTAS_PEI_IA"]
    }
    
    tags_para_testar = alias_map.get(tag_busca, [tag_busca])
    
    tags_mestras = [
        "SOSA_ID", "VALOR", "ORIENTACOES", "QUESTOES", "GABARITO_TEXTO", "GRADE_DE_CORRECAO", 
        "GABARITO", "RESPOSTAS_IA", "PEI", "GABARITO_PEI", "GRADE_DE_CORRECAO_PEI", "RESPOSTAS_PEI_IA", 
        "PROFESSOR", "ALUNO", "IMAGENS", "HABILIDADE_BNCC", "COMPETENCIAS_FOCO", 
        "OBJETO_CONHECIMENTO", "CONTEUDOS_ESPECIFICOS", "OBJETIVOS_ENSINO",
        "JUSTIFICATIVA_PEDAGOGICA", "AULA_1", "AULA_2", "SABADO_LETIVO", "AVALIACAO_DE_MERITO", "ESTRATEGIA_DUA_PEI",
        "ROTEIRO_DO_PROFESSOR", "GUIA_DE_ESTUDO_ALUNO", "RUBRICA_DE_OBSERVACAO", "ROTEIRO_DO_PROFESSOR - RECOMPOSIÇÃO",
        "OBJETIVO", "ESTRATEGIA", "RECURSO", "ITEM",
        "DIAGNOSTICO_GERAL", "SOCIAIS", "COMUNICATIVAS", "EMOCIONAIS", "FUNCIONAIS", "DIRETRIZES_CURRICULARES"
    ]

    for t_alvo in tags_para_testar:
        parada = [rf"\b{re.escape(t)}\b" for t in tags_mestras if t != t_alvo]
        lista_parada = "|".join(parada)
        padrao_bloco = rf"\[\s*[*#]*\s*{re.escape(t_alvo)}\b.*?\s*\]\s*[:\-]*\s*(.*?)(?=\s*\[\s*[*#]*\s*(?:{lista_parada})\s*[*#]*\s*\]|--- LINKS ---|$)"
        match_bloco = re.search(padrao_bloco, texto, re.DOTALL | re.IGNORECASE)
        
        if match_bloco:
            res = match_bloco.group(1).strip()
            res = re.sub(r'^```[a-zA-Z]*\n', '', res, flags=re.IGNORECASE)
            res = re.sub(r'\n```$', '', res)
            res_limpo = re.sub(r'[░▒▓█]', '', res)
            res_limpo = re.sub(r'-{3,}', '', res_limpo)
            res_limpo = re.sub(r'^(?:Olá|Como especialista|Prezado|Segue).*?\n\n', '', res_limpo, flags=re.IGNORECASE | re.DOTALL).strip()
            if len(res_limpo) > 0:
                return res_limpo.strip()
    
    return ""

def extrair_gab_universal_com_fallback(texto, is_pei=False, nivel_pei="NIVEL_1"):
    """
    SOSA V2026 - EXTRATOR UNIVERSAL DE GABARITO (REGULAR E PEI INTELIGENTE):
    - Provas Regulares: Extrai chave oficial de 5 alternativas (A, B, C, D, E).
    - Provas PEI: Extrai exclusivamente chaves de 3 alternativas (A, B, C).
    """
    if not texto or not isinstance(texto, str): return []
    
    mapa_regular = {}
    raw_reg = extrair_tag(texto, "GABARITO_TEXTO") or extrair_tag(texto, "GABARITO")
    
    if raw_reg:
        matches_reg = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-E])\b", str(raw_reg).upper())
        for q_num_str, letra in matches_reg:
            mapa_regular[int(q_num_str)] = letra

    qtd_enunciados = len(re.findall(r"(?i)(?:QUEST[AÃ]O\s*|Q)\s*0?(\d+)", extrair_tag(texto, "QUESTOES") or texto))
    max_q = max(mapa_regular.keys()) if mapa_regular else 0
    qtd_oficial = max(max_q, qtd_enunciados, 10)
    
    if not is_pei:
        return [mapa_regular.get(n, "A") for n in range(1, qtd_oficial + 1)]

    # EXTRAÇÃO INTELIGENTE DO GABARITO PEI (A, B, C)
    mapa_pei = {}
    
    # 1. Busca tag [GABARITO_PEI] explícita
    m_gab_pei_block = re.search(r"\[\s*GABARITO_PEI\s*\]\s*[:\-]*\s*(.*?)(?=\[|--- LINKS ---|$)", texto, re.DOTALL | re.IGNORECASE)
    if m_gab_pei_block:
        matches_p = re.findall(r"(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-C])\b", m_gab_pei_block.group(1).upper())
        for q_num_str, letra in matches_p:
            mapa_pei[int(q_num_str)] = letra

    bloco_pei = extrair_tag(texto, nivel_pei) or extrair_tag(texto, "PEI_NIVEL_1") or extrair_tag(texto, "NIVEL_1") or extrair_tag(texto, "PEI")
    
    if not mapa_pei and bloco_pei:
        matches_inline = re.findall(r"0?(\d+)\s*[-:]\s*([A-C])\b", bloco_pei.upper())
        for q_num_str, letra in matches_inline:
            mapa_pei[int(q_num_str)] = letra

    resultado_pei = []
    for q_n in range(1, qtd_oficial + 1):
        letra_encontrada = mapa_pei.get(q_n, None)
        if letra_encontrada and letra_encontrada in ["A", "B", "C"]:
            resultado_pei.append(letra_encontrada)
        else:
            reg_letra = mapa_regular.get(q_n, "A")
            if reg_letra in ["A", "B", "C"]: resultado_pei.append(reg_letra)
            elif reg_letra == "D": resultado_pei.append("C")
            else: resultado_pei.append("A")

    return resultado_pei

def gerar_prognostico_pedagogico(dados_stats, contexto_prova):
    """Gera diagnóstico psicométrico ágil utilizando Gemini 3.5 Flash-Lite."""
    try:
        client_local = obter_client_gemini()
        if not client_local: return "Chave de IA indisponível."

        prompt = (
            f"VOCÊ É O PERITO EM AVALIAÇÃO EDUCACIONAL SOSA (PADRÃO SAEB/ENEM/BNCC).\n"
            f"Realize um diagnóstico pedagógico nos itens abaixo:\n\n"
            f"CONTEXTO DA PROVA:\n{contexto_prova}\n\n"
            f"DESEMPENHO DA TURMA:\n{dados_stats}\n\n"
            f"MISSÃO:\n"
            f"1. MAPEAMENTO DE DESCRITORES SAEB / BNCC.\n"
            f"2. ANÁLISE DE RACIOCÍNIO E ERRO COGNITIVO DOMINANTE DA TURMA.\n"
            f"3. RECOMENDAÇÕES PRÁTICAS DE RECOMPOSIÇÃO."
        )
        
        for mod_p in ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-3.5-flash"]:
            try:
                res = client_local.models.generate_content(
                    model=mod_p,
                    contents=[types.Content(role="user", parts=[types.Part.from_text(text=prompt)])]
                )
                if res and res.text:
                    return res.text.replace("**", "").replace("#", "").strip()
            except:
                continue
                
        return "Não foi possível gerar o prognóstico no momento."
    except Exception as e:
        return f"Erro na perícia: {e}"

def limpar_links_antigos(texto):
    if not texto: return ""
    partes = re.split(r"--- LINKS ---", texto, flags=re.IGNORECASE)
    return partes[0].strip()
