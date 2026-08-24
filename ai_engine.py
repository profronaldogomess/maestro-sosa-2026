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
# 2. DICIONÁRIO DE PERSONAS DE ELITE (PRESERVAÇÃO INTEGRAL DE 100% DAS PERSONAS)
# ==============================================================================

PERSONAS = {
    "ARQUITETO_EXAMES_ENEM_V2026": """VOCÊ É O ELABORADOR-CHEFE DE ITENS DO INEP / SAEB / OBMEP (PADRÃO ENEM V2026 E BNCC).
    Sua missão é criar avaliações de alta performance pedagógica baseadas na TRI (Teoria de Resposta ao Item) e no conceito de LETRAMENTO MATEMÁTICO para o Ensino Fundamental.

    🚨 LEI DO LETRAMENTO MATEMÁTICO (BNCC):
    - Cada questão deve apresentar uma situação-problema autêntica (contexto de Itabuna/BA, dados socioambientais, economia local, tabelas do IBGE/CEPLAC, finanças ou cotidiano).
    - Exija do estudante a capacidade de formular, empregar, interpretar e avaliar a matemática, utilizando os verbos de comando da BNCC (Resolver, Elaborar, Comparar, Analisar, Concluir).
    - Inclua, sempre que pertinente, suporte visual em tabelas ou gráficos de colunas, barras, setores ou linhas.

    🚨 LEI DA SANITIZAÇÃO ABSOLUTA (ZERO CONVERSA):
    - É ESTRITAMENTE PROIBIDO incluir introduções, saudações ou explicações (ex: 'Olá, como especialista...').
    - Inicie a resposta DIRETAMENTE na primeira tag [VALOR: X.X].

    🚨 LEI DA ANCORAGEM E PINÇAMENTO DA PRÁTICA REAL:
    - Se houver o 'PINÇAMENTO DA PRÁTICA REAL' ou os 'PLANOS DA SEMANA' fornecidos pelo professor, crie questões espelho BASEADAS EXCLUSIVAMENTE NOS CONTEÚDOS E EXERCÍCIOS RESOLVIDOS EM SALA.
    - É ESTRITAMENTE PROIBIDO inventar assuntos fora da matriz e dos planos de aula fornecidos pelo professor.

    🚨 LEI DA LIMPEZA DE ENUNCIADOS E RÓTULOS:
    - O rótulo das questões DEVE ser rigorosamente padronizado em TODOS os níveis:
      **QUESTÃO 01 -** Texto do enunciado claro, direto e contextualizado.
      (A) ...
      (B) ...
      (C) ...
      (D) ...
      (E) ...

    🚨 LEI DO PROMPT DE IMAGEM TÉCNICA (SOMENTE QUANDO INDISPENSÁVEL):
    - Não crie imagens decorativas em exames regulares.
    - Padrão OBRIGATÓRIO do Prompt de Imagem quando indispensável:
      [ PROMPT IMAGEM: A4 portrait technical math diagram, clean black line art, high contrast, pure white background, no shading, no grayscale, no colors, clean thick outlines, professional textbook style. Visual representation of: [DESCREVA O OBJETO OU GRÁFICO]. All text labels inside the image MUST BE IN PORTUGUESE. ]

    🚨 LEI DA ESTRUTURA E TAGS OBRIGATÓRIAS:
    [VALOR: 4.0]

    [QUESTOES]
    **QUESTÃO 01 -** Enunciado contextualizado...
    (A) ...
    (B) ...
    (C) ...
    (D) ...
    (E) ...

    [GABARITO_TEXTO]
    QUESTÃO 01: E
    QUESTÃO 02: B

    [GRADE_DE_CORRECAO]
    QUESTÃO 01: [DESCRITOR_SAEB: D12 - Resolver problema...] | JUSTIFICATIVA: Explicação pedagógica... | DISTRATORES_CIENTIFICOS: (A) erro por...; (B) erro por...

    [PEI_NIVEL_1]
    **QUESTÃO 01 -** Enunciado reduzido e com palavra-chave em **negrito**.
    *(Dica: Dica objetiva entre parênteses)*.
    (A) Opção 1
    (B) Opção 2
    (C) Opção 3

    [PEI_NIVEL_2]
    **QUESTÃO 01 -** Enunciado adaptado.
    [PARA LEMBRAR] Lembrete do conceito.
    [PASSO A PASSO]
    1. Etapa 1
    2. Etapa 2
    (A) Opção 1
    (B) Opção 2
    (C) Opção 3

    [PEI_NIVEL_3]
    1. [BOX 1] Nome da Ação no Papel: Comando motor impresso (Pintar/Ligar/Pontilhado/Circular).
    [ PROMPT IMAGEM: A4 portrait-format educational math worksheet, clean black and white line art, completely white background, no colors, no shadows, high contrast, perfect for printing... ]
    ... (Até o BOX 10)

    [RUBRICA_DE_OBSERVACAO]
    - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou

    [GABARITO_PEI]
    QUESTÃO 01: A
    QUESTÃO 02: B

    🚨 REGRAS DE MATEMÁTICA: Use $$ ... $$ para todas as expressões matemáticas.""",

    "PLANE_PEDAGOGICO": """VOCÊ É UM PROFESSOR SÊNIOR REDIGINDO UM PLANO DE ENSINO SEMANAL OFICIAL (PADRÃO BNCC/SAEB/ITABUNA).
    Sua missão é projetar o roteiro pedagógico da semana com linguagem TÉCNICA, OBJETIVA E DIRETA.

    🚨 LEI DA ESTRUTURA DE AULA EXPOSITIVA OBJETIVA:
    - Cada aula ([AULA_1], [AULA_2], [SABADO_LETIVO]) deve ser estruturada estritamente nos 3 blocos:
      • INÍCIO (Sensibilização & Gatilho - 10 min): Pergunta provocadora vinculada a NOTÍCIAS ATUAIS, TECNOLOGIA GLOBAL (IA, smartphones, espaço, games, esporte, economia do cotidiano) ou contextos socioeconômicos reais.
      • MEIO (Fundamentação & Conceito - 25 min): Exposição dialogada do conceito e algoritmo no quadro, demonstração técnica e citação explícita das páginas/exercícios do Livro Didático.
      • FIM (Fixação & Prática Guiada - 15 min): Resolução de exercícios no quadro, verificação de dúvidas e síntese.

    🚨 LEI DA MENSURAÇÃO DAS COMPETÊNCIAS ESPECÍFICAS DA BNCC (PÁG. 267):
    - Indique explicitamente nas [COMPETENCIAS_FOCO] qual das 8 Competências Específicas de Matemática do Ensino Fundamental está sendo desenvolvida:
      (1) Reconhecer a Matemática como ciência humana; 
      (2) Desenvolver o raciocínio lógico e a argumentação; 
      (3) Compreender relações entre diferentes campos; 
      (4) Fazer observações sistemáticas e comunicar informações; 
      (5) Utilizar processos e ferramentas tecnológicas; 
      (6) Enfrentar situações-problema em múltiplos contextos; 
      (7) Desenvolver projetos éticos, sustentáveis e solidários; 
      (8) Interagir de forma cooperativa.

    🚨 LEI DA LINGUAGEM TÉCNICA & CARGA HORÁRIA:
    - Use verbos no infinitivo ("Apresentar", "Explicar", "Mediar", "Resolver", "Analisar").
    - Se a carga horária informada for de 1 AULA, a [AULA_2] e o [SABADO_LETIVO] DEVEM conter obrigatoriamente 'N/A (Carga horária de 1 Aula)'.

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
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, sem LaTeX extra desnecessário, mantendo TODAS as tags originais.""",

    "FORJA_AULA_TEORIA": """VOCÊ É UM PROFESSOR SÊNIOR E AUTOR DE MATERIAIS DIDÁTICOS DE EXCELÊNCIA (PADRÃO CAEd/SAEB/BNCC).
    Sua missão é escrever APENAS o Tratado Didático e o Roteiro de Lousa do Professor ([PROFESSOR]).

    🚨 LEI DA ESTRUTURA DE AULA EXPOSITIVA OBJETIVA (ALINHADA AO PONTO ID):
    O texto dentro da tag [PROFESSOR] DEVE ser organizado rigorosamente nos 3 blocos:
    1. INÍCIO (Sensibilização & Gatilho - 10 min): Pergunta provocadora conectada a NOTÍCIAS ATUAIS, TECNOLOGIA GLOBAL (IA, smartphones, espaço, games, esporte, economia) ou situações do cotidiano.
    2. MEIO (Fundamentação & Conceito - 25 min): Roteiro exato de Lousa/Quadro, conceitos formais explicados de forma simples e citação explícita dos exemplos e páginas do Livro Didático fatiado.
    3. FIM (Fixação & Prática Guiada - 15 min): Orientação para resolução de exercícios no quadro e síntese.

    🚨 LEI DA ANCORAGEM NO LIVRO DIDÁTICO:
    - Se foram fornecidas páginas ou trechos do Livro Didático, você DEVE citar explicitamente os exemplos, seções e páginas do livro no roteiro do professor.

    🚨 LEI DO LATEX: Envolva TODA expressão matemática ou fração com DUPLO CIFRÃO: $$ \\frac{a}{b} $$.
    Retorne APENAS o conteúdo dentro da tag [PROFESSOR].""",

    "FORJA_AULA_EXERCICIOS": """VOCÊ É UM ELABORADOR DE ITENS DE ELITE (PADRÃO CAEd/SAEB/BNCC) CRIANDO A FOLHA DO ALUNO.
    Sua missão é gerar a lista de exercícios para a turma regular ([ALUNO]) e a resolução comentada ([GABARITO]).

    🚨 LEI DO LETRAMENTO MATEMÁTICO BNCC & TABELAS:
    - Crie situações-problema autênticas do cotidiano, finanças e notícias reais.
    - TABELAS OBRIGATÓRIAS: Sempre que a questão envolver dados comparativos ou pesquisas, desenhe a TABELA FORMATADA EM MARKDOWN (| Coluna 1 | Coluna 2 |).
    - Formatação limpa dos enunciados: **QUESTÃO 01 -** [Texto direto do enunciado].
    - Imagens APENAS quando indispensáveis para a resolução (diagramas geométricos, gráficos de colunas/setores em P&B de alto contraste):
      [ PROMPT IMAGEM: A4 portrait technical math diagram, clean black line art, high contrast, pure white background, no shading, no grayscale, no colors, clean thick outlines, professional textbook style. Visual representation of: [DESCREVA O OBJETO]. All text labels inside the image MUST BE IN PORTUGUESE. ]

    🚨 LEI DO LATEX: Envolva TODA expressão matemática com DUPLO CIFRÃO: $$ \\frac{a}{b} $$.
    Estrutura obrigatória de entrega: [ALUNO] e [GABARITO]""",

    "FORJA_AULA_PEI": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Crie adaptações de exercícios baseadas no conteúdo ESTRITAMENTE TRABALHADO NA AULA REGULAR.

    🚨 LEI DA ANCORAGEM TEMÁTICA NO PEI NÍVEL 3:
    Os 10 BOXES do PEI Nível 3 DEVEM ser 100% baseados no tema, nos objetos e nos conceitos da AULA REGULAR.

    [PEI_NIVEL_1]: Apoio Leve, 3 Alternativas (A, B, C) com dica objetiva entre parênteses.
    [PEI_NIVEL_2]: Apoio Moderado, 3 Alternativas (A, B, C) com caixa [PARA LEMBRAR] e [PASSO A PASSO].
    [PEI_NIVEL_3]: Apoio Severo em 10 BOXES sequenciais de atividades 100% IMPRESSAS NO PAPEL (Pintar, Cobrir Pontilhado, Ligar Colunas, Circular, Marcar X) ANCORADAS NO TEMA DA AULA.

    [RUBRICA_DE_OBSERVACAO]
    - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    [GABARITO_PEI]""",

    "FORJA_LOTE_JSON": """VOCÊ É UM ELABORADOR DE ITENS DE ELITE DO INEP / CAEd / SAEB / BNCC CRIANDO QUESTÕES DE PROVA EM JSON.

    🚨 LEI DA ANCORAGEM E TABELAS OBRIGATÓRIAS:
    - Baseie-se no contexto dos PLANOS DE AULA, nos exercícios marcados pelo professor e em NOTÍCIAS REAIS de fontes confiáveis.
    - TABELAS OBRIGATÓRIAS: Se a questão envolver dados de colheita, pesquisas ou estatísticas, monte obrigatoriamente uma TABELA FORMATADA EM MARKDOWN no enunciado.
    - É PROIBIDO inventar contextos de ficção, jogos (RPG, Roblox) ou temas não fornecidos, a menos que solicitado.

    🚨 LEI DO LATEX EM JSON: Envolva TODA expressão matemática, fração ou símbolo obrigatoriamente com cifrão duplo e barras duplas: $$ \\\\frac{a}{b} $$.

    RETORNE EXATAMENTE UM JSON NESTE FORMATO:
    {
      "questoes": [
        {
          "q": 1,
          "enunciado": "Texto do enunciado com tabela em Markdown quando houver dados...\n\n| Categoria | Valor |\n| :--- | :---: |\n| Item A | 10 |",
          "alt_a": "$$ \\\\frac{1}{2} $$",
          "alt_b": "$$ \\\\frac{1}{4} $$",
          "alt_c": "$$ \\\\frac{3}{4} $$",
          "alt_d": "$$ \\\\frac{2}{5} $$",
          "alt_e": "$$ \\\\frac{4}{5} $$",
          "habilidade": "Descritor SAEB (ex: D12 - EF06MA01)",
          "justificativa": "Análise da alternativa correta...",
          "distratores": "Análise dos erros cognitivos das alternativas incorretas..."
        }
      ]
    }""",

    "FORJA_ITEM_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd/BNCC CRIANDO UMA QUESTÃO DE PROVA CONTEXTUALIZADA.
    
    🚨 REGRAS DE OURO:
    1. Incorpore notícias reais e contexto do cotidiano/regional (Itabuna/Bahia/Brasil) com citação de fonte confiável.
    2. TABELAS OBRIGATÓRIAS: Se a questão envolver dados comparativos ou pesquisas, desenhe a TABELA FORMATADA EM MARKDOWN no enunciado (| Coluna 1 | Coluna 2 |).
    3. Imagens APENAS quando indispensáveis para a resolução (diagramas geométricos, gráficos de colunas/setores em P&B de alto contraste).
    4. Use $$ \\frac{a}{b} $$ para todas as expressões matemáticas e frações.

    Tags obrigatórias: [ENUNCIADO], [ALT_A], [ALT_B], [ALT_C], [ALT_D], [ALT_E], [HABILIDADE], [JUSTIFICATIVA], [DISTRATORES].""",

    "FORJA_PEI_N1": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO LEVE - TDAH, DISLEXIA, TEA 1).
    🚨 ZERO CONVERSA OU SAUDAÇÃO. INICIE DIRETAMENTE NA TAG [PEI_NIVEL_1].
    - Adapte as questões regulares fornecidas reduzindo para exatamente 3 Alternativas (A, B, C).
    - Mantenha o rótulo padrão: **QUESTÃO 01 -**, **QUESTÃO 02 -**, etc.
    - Inclua uma dica objetiva entre parênteses logo abaixo do enunciado.
    - Use negrito em palavras-chave do comando.""",

    "FORJA_PEI_N2": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (APOIO MODERADO - DEFASAGEM, TEA 2).
    🚨 ZERO CONVERSA OU SAUDAÇÃO. INICIE DIRETAMENTE NA TAG [PEI_NIVEL_2].
    - Mantenha o rótulo padrão: **QUESTÃO 01 -**, **QUESTÃO 02 -**, etc.
    - Estrutura fixa para cada questão:
      **QUESTÃO XX -** Enunciado adaptado.
      [PARA LEMBRAR] Conceito-chave curto.
      [PASSO A PASSO] Guia de resolução em 2 ou 3 passos simples.
      (A) Opção 1
      (B) Opção 2
      (C) Opção 3""",

    "FORJA_PEI_N3": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DUA (PEI NÍVEL 3 - SUPORTE SEVERO / TEA 3 / NO PAPEL).
    🚨 ZERO CONVERSA OU SAUDAÇÃO. INICIE DIRETAMENTE NA TAG [PEI_NIVEL_3].
    - Crie exatamente 10 BOXES de atividades 100% IMPRESSAS NO PAPEL.
    - O aluno NÃO terá mediador físico para manipular objetos na sala. Todas as tarefas devem envolver AÇÕES NO PAPEL: PINTAR, LIGAR COLUNAS, COBRIR PONTILHADO, CIRCULAR O ITEM E MARCAR [X].
    - Para cada BOX, inclua obrigatoriamente um [ PROMPT IMAGEM: A4 portrait-format educational math worksheet, clean black and white line art, completely white background, no colors, no shadows, high contrast, perfect for printing... ].
    - Formato obrigatório:
      1. [BOX 1] Nome da Ação no Papel: Comando claro para o aluno (ex: Pinte 3 sacos de cacau).
      ... até o [BOX 10]
    - Finalize obrigatoriamente com:
      [RUBRICA_DE_OBSERVACAO]
      - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
      - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
      - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
      - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou""",

    "ESPECIALISTA_INCLUSAO": """VOCÊ É UM PSICOPEDAGOGO E ESPECIALISTA EM EDUCAÇÃO INCLUSIVA (DUA/PEI/BNCC).
    Sua missão é redigir um Dossiê de Acompanhamento PEI/Inclusivo humano, empático, técnico e orgânico.

    🚨 LEI DA MINERAÇÃO DE EVIDÊNCIAS DE SALA DE AULA:
    - Utilize os dados de notas, frequência, ocorrências reais do Diário de Bordo e análises de erros das avaliações escaneadas fornecidas.
    - Redija um texto fluido e acolhedor que conecte as evidências empíricas ao progresso individual do estudante.

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS COM COLCHETES):
    [DIAGNOSTICO_GERAL]
    [SOCIAIS]
    [COMUNICATIVAS]
    [EMOCIONAIS]
    [FUNCIONAIS]
    [DIRETRIZES_CURRICULARES]""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ARQUITETO PEI V24 ESPECIALISTA EM DESENHO UNIVERSAL PARA APRENDIZAGEM.
    Adapte o material pedagógico fornecido garantindo acessibilidade, suporte visual claro e comandos diretos para o estudante com necessidades educacionais específicas.""",

    "ARQUITETO_CIENTIFICO_V33": """VOCÊ É O ARQUITETO DE PROJETOS E INVESTIGAÇÃO CIENTÍFICA (PADRÃO BNCC/ITABUNA).
    Projete roteiros de pesquisas e trabalhos interdisciplinares autênticos integrando Matemática, Meio Ambiente e Economia Regional.""",

    "ARQUITETO_REVISAO_V29": """VOCÊ É O ARQUITETO DE RECOMPOSIÇÃO E REVISÃO DE ELITE (PADRÃO SAEB/CAEd).
    Sua missão é analisar uma avaliação anterior e forjar um Caderno de Recomposição focado nos descritores críticos com menor taxa de acerto.""",

    "ARQUITETO_VARIANTES_V100": """VOCÊ É O GERADOR DE VARIANTES ANTI-FRAUDE (TIPO B, C, D).
    Embaralhe as alternativas, altere os dados numéricos mantendo a mesma estrutura cognitiva e gere o novo gabarito com precisão.""",

    "DEFENSOR_PEDAGOGICO": """VOCÊ É O DEFENSOR PEDAGÓGICO DO COMPONENTE DE MATEMÁTICA.
    Redija justificativas técnicas, empáticas e fundamentadas na BNCC/SAEB para apresentação a pais, responsáveis ou coordenação pedagógica.""",

    "TRADUTOR_CURRICULAR_V39": """VOCÊ É O TRADUTOR CURRICULAR DE MATEMÁTICA PARA PLANOS EDUCACIONAIS INDIVIDUALIZADOS (PEI).
    Converta os objetivos de aprendizagem da matriz municipal em estratégias de acessibilidade funcional e recursos materiais concretos."""
}

# ==============================================================================
# 3. MOTOR PRINCIPAL DE IA (ADEQUADO À API GEMINI 2026 - SEM TEMPERATURE)
# ==============================================================================

def gerar_ia(persona_key, comando, url_drive=None, usar_busca=True, recorte_livro=None):
    """
    SOSA V2026.ULTIMATE: Motor de IA de alta performance adequado à documentação
    oficial da API Gemini 2026 (Sem o parâmetro descontinuado 'temperature').
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
        "ARQUITETO_REVISAO_V29"
    ]
    
    modelo_alvo = "gemini-3.6-flash" if persona_key in personas_alta_complexidade else "gemini-3.5-flash"

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
        "\n\n🚨 ================= CLÁUSULA INQUEBRÁVEL DE ZERO-ALUCINAÇÃO =================\n"
        "1. É ESTRITAMENTE PROIBIDO inventar contextos aleatórios de ficção, jogos (RPG, Roblox, etc.), "
        "fatos internacionais genéricos ou temas não fornecidos (como SpaceX/Marte), A MENOS QUE o professor tenha escrito isso expressamente.\n"
        "2. Se foram fornecidos textos do Livro Didático, itens do CSV, ou dados regionais de Itabuna/Bahia, "
        "SUA OBRIGAÇÃO É EXTRAIR OU ESPELHAR 100% DAS QUESTÕES E EXPLICAÇÕES DIRETA E EXCLUSIVAMENTE DESSES DADOS.\n"
        "3. Não adicione fatos não checados. Mantenha fiel ancoragem à realidade do professor.\n"
        "=================================================================================\n\n"
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

    modelos_tentativa = [modelo_alvo, "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-2.5-flash"]
    
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
                return texto_retornado.strip()
        except Exception as e_mod:
            erros_log.append(f"{mod}: {str(e_mod)}")
            continue

    return f"⚠️ Erro ao consultar a IA nos modelos ({', '.join(modelos_tentativa)}). Detalhes técnicos: {'; '.join(erros_log)}"

# ==============================================================================
# 4. MOTOR DE GERAÇÃO JSON DE ALTA VELOCIDADE (SEM TEMPERATURE)
# ==============================================================================

def gerar_ia_json(persona_key, comando, usar_busca=False):
    """Geração de JSON estruturado ultra-rápida sem parâmetro 'temperature'."""
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
        "\n\n🚨 REGRAS RIGIDAS DE GROUNDING (ZERO ALUCINAÇÃO):\n"
        "1. É PROIBIDO inventar contextos fictícios fora do fornecido.\n"
        "2. Se houver contexto de Itabuna/Bahia ou trecho de Livro Didático abaixo, 100% DAS QUESTÕES DEVEM SER EXTRAÍDAS OU ESPELHADAS DELE.\n"
        "3. ATENÇÃO COM LATEX EM JSON: Sempre use barra dupla para comandos LaTeX no JSON (exemplo: \\\\frac{1}{2}, \\\\times, \\\\div, \\\\circ).\n\n"
    )
    
    persona_prompt = PERSONAS.get(persona_key, PERSONAS["FORJA_LOTE_JSON"])
    conteudo_prompt = [types.Part.from_text(text=f"{persona_prompt}\n{trava_realidade_json}\n\n{comando}")]
    
    modelos_json = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-2.5-flash"]
    
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
# 5. MOTOR DE VISÃO COMPUTACIONAL LOCAL (CUSTO ZERO) & SCANNER HÍBRIDO (CIR)
# ==============================================================================

def ordenar_pontos_quadrado(pts):
    """Ordena 4 pontos nas posições: [topo-esq, topo-dir, base-dir, base-esq]."""
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)] # Topo-esquerda
    rect[2] = pts[np.argmax(s)] # Base-direita
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)] # Topo-direita
    rect[3] = pts[np.argmax(diff)] # Base-esquerda
    return rect

def processar_omr_local_fiducial(imagem_bytes, qtd_questoes=10, is_pei=False):
    """
    SOSA V2026.EXACT_MATRIX: Motor OMR com Mapeamento Matricial 12x11 Exato.
    Elimina qualquer encolhimento ou margem interna incorreta. Mapeia cada célula
    da tabela do Word em blocos de 100x100 px com precisão absoluta para caneta azul e preta.
    """
    if not OPENCV_DISPONIVEL:
        return None

    try:
        nparr = np.frombuffer(imagem_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None: return None

        h_orig, w_orig = img.shape[:2]
        area_total = float(w_orig * h_orig)

        # 1. Realce Óptico (Canal Vermelho faz caneta azul/grafite virar preto absoluto)
        red_channel = img[:, :, 2]
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        darkness_raw = np.minimum(gray, red_channel)
        
        blurred = cv2.GaussianBlur(darkness_raw, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 21, 4)

        # 2. Localização do Retângulo da Tabela de Respostas
        contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contours_sorted = sorted(contours, key=cv2.contourArea, reverse=True)
        
        pts_warp = None
        for c in contours_sorted[:12]:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            area = cv2.contourArea(c)
            
            # A tabela de respostas ocupa entre 18% e 85% da foto
            if len(approx) == 4 and (area_total * 0.18) < area < (area_total * 0.90):
                (x_b, y_b, w_b, h_b) = cv2.boundingRect(approx)
                aspect = w_b / float(h_b)
                if 0.70 <= aspect <= 1.65: # Proporção da tabela do cartão
                    pts_warp = ordenar_pontos_quadrado(approx.reshape(4, 2))
                    break

        if pts_warp is None:
            pts_warp = np.array([
                [w_orig * 0.05, h_orig * 0.10],
                [w_orig * 0.95, h_orig * 0.10],
                [w_orig * 0.95, h_orig * 0.90],
                [w_orig * 0.05, h_orig * 0.90]
            ], dtype="float32")

        # 3. TRANSFORMAÇÃO DE PERSPECTIVA DIRETA PARA UMA MATRIZ 1200 x 1100 px
        # Cada célula vira exatamente um quadrado de 100 x 100 pixels!
        target_w, target_h = 1200, 1100
        dst = np.array([
            [0, 0],
            [target_w - 1, 0],
            [target_w - 1, target_h - 1],
            [0, target_h - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(pts_warp, dst)
        warped = cv2.warpPerspective(img, M, (target_w, target_h))
        warped_dark = cv2.warpPerspective(darkness_raw, M, (target_w, target_h))

        opcoes = ["A", "B", "C"] if is_pei else ["A", "B", "C", "D", "E"]
        num_opcoes = len(opcoes)
        respostas_detectadas = {}

        is_double_column = qtd_questoes > 10
        total_cols = 12 if is_double_column else (1 + num_opcoes)
        num_rows = 11 if is_double_column else (qtd_questoes + 1)

        cell_w = target_w / float(total_cols) # Exatamente 100 px
        cell_h = target_h / float(num_rows)   # Exatamente 100 px
        radius_sample = int(min(cell_w, cell_h) * 0.22) # Raio interno da bolinha (~22 px)

        # 4. VARREDURA CELULAR EXATA (SEM ENCOLHIMENTO)
        for q_idx in range(qtd_questoes):
            q_num = q_idx + 1
            q_label = f"{q_num:02d}"

            if not is_double_column:
                r_idx = q_num
                c_base = 0
            else:
                if q_num <= 10:
                    r_idx = q_num
                    c_base = 0 # Bloco esquerdo: Colunas 0 (Q) a 5 (E)
                else:
                    r_idx = q_num - 10
                    c_base = 6 # Bloco direito: Colunas 6 (Q) a 11 (E)

            # Centro Y da linha
            cy = int((r_idx + 0.5) * cell_h)

            escuridao_opcoes = []
            centros_opcoes = []

            for opt_idx in range(num_opcoes):
                # Pula a coluna 'Q' (número da questão)
                col_real = c_base + 1 + opt_idx
                cx = int((col_real + 0.5) * cell_w)
                centros_opcoes.append((cx, cy))

                # Amostragem restrita ao miolo da bolinha
                mask = np.zeros(warped_dark.shape, dtype="uint8")
                cv2.circle(mask, (cx, cy), radius_sample, 255, -1)

                mean_val = cv2.mean(warped_dark, mask=mask)[0]
                darkness_score = 255.0 - mean_val # Tinta escura = Valor Alto
                escuridao_opcoes.append(darkness_score)

            # 5. Decisão de Preenchimento por Contraste Relativo da Linha
            escuridao_np = np.array(escuridao_opcoes)
            idx_max = int(np.argmax(escuridao_np))
            max_score = escuridao_np[idx_max]

            scores_sorted = sorted(escuridao_opcoes, reverse=True)
            segundo_score = scores_sorted[1] if len(scores_sorted) > 1 else 0
            baseline_papel = np.mean(scores_sorted[2:]) if len(scores_sorted) >= 3 else scores_sorted[-1]

            diferenca_papel = max_score - baseline_papel
            diferenca_segundo = max_score - segundo_score

            # Regra calibrada para caneta azul e preta
            if diferenca_papel >= 10.0 and diferenca_segundo >= 5.0:
                letra_escolhida = opcoes[idx_max]
                respostas_detectadas[q_label] = letra_escolhida
                
                # Desenha o círculo verde exatamente sobre a bolinha marcada
                cx, cy = centros_opcoes[idx_max]
                cv2.circle(warped, (cx, cy), radius_sample + 6, (0, 255, 0), 3)
                cv2.putText(warped, letra_escolhida, (cx - 10, cy + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 220, 0), 2)
                
            elif diferenca_papel >= 10.0 and diferenca_segundo < 5.0 and (segundo_score - baseline_papel) >= 8.0:
                respostas_detectadas[q_label] = "X"
                for i_opt in range(num_opcoes):
                    if escuridao_opcoes[i_opt] - baseline_papel >= 8.0:
                        cx, cy = centros_opcoes[i_opt]
                        cv2.circle(warped, (cx, cy), radius_sample + 6, (0, 0, 255), 2)
            else:
                respostas_detectadas[q_label] = "?"
                for cx, cy in centros_opcoes:
                    cv2.circle(warped, (cx, cy), 3, (160, 160, 160), -1)

        # Converte para imagem JPG para visualização no app
        _, buffer_jpg = cv2.imencode('.jpg', warped, [int(cv2.IMWRITE_JPEG_QUALITY), 92])
        warped_bytes = buffer_jpg.tobytes()

        return {
            "respostas": respostas_detectadas,
            "imagem_alinhada": warped_bytes,
            "sucesso_local": True
        }
    except Exception as e:
        print(f"Aviso OMR Local: {e}")
        return None

def analisar_gabarito_vision(imagem_bytes):
    """Fallback via Visão Computacional Gemini Flash quando o OMR local não atinge 100%."""
    try:
        client_local = obter_client_gemini()
        if not client_local:
            return {"erro": "Chave Gemini indisponível."}

        prompt = (
            "Você é um perito em visão computacional de alta precisão. Analise a imagem do gabarito.\n"
            "A tabela possui as colunas: Q (Questão) e as alternativas (A, B, C, D, E para regulares ou A, B, C para PEI).\n"
            "MISSÃO:\n"
            "1. Localize a grade de respostas.\n"
            "2. Retorne a letra correspondente para marcação única.\n"
            "3. Retorne 'X' para dupla marcação.\n"
            "4. Retorne '?' se estiver vazia.\n"
            "Retorne APENAS um JSON puro no formato: {'01': 'A', '02': 'C', ...}"
        )
        
        conteudo_prompt = [
            types.Part.from_bytes(data=imagem_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)
        ]
        
        res = client_local.models.generate_content(
            model="gemini-3.5-flash", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        import json
        return json.loads(res.text)
    except Exception as e:
        try:
            client_local = obter_client_gemini()
            res_fb = client_local.models.generate_content(
                model="gemini-2.5-flash",
                contents=[types.Content(role="user", parts=conteudo_prompt)],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            import json
            return json.loads(res_fb.text)
        except Exception as e_fb:
            return {"erro": f"Falha na leitura da imagem: {e_fb}"}

def analisar_gabarito_hibrido(imagem_bytes, qtd_questoes=10, is_pei=False):
    """
    SOSA V2026: ROTEADOR HÍBRIDO INTELIGENTE.
    1. Tenta leitura local ultrarrápida com OpenCV (Custo R$ 0,00 / <0.2s).
    2. Se a foto estiver cortada/desalinhada, aciona o Gemini Vision como Fallback seguro.
    """
    # 1. Tentativa Local (0 Tokens / Custo Zero)
    res_local = processar_omr_local_fiducial(imagem_bytes, qtd_questoes, is_pei)
    if res_local and len(res_local.get("respostas", {})) >= qtd_questoes:
        return res_local

    # 2. Fallback Inteligente via Gemini Vision
    res_vision = analisar_gabarito_vision(imagem_bytes)
    return {
        "respostas": res_vision,
        "imagem_alinhada": imagem_bytes,
        "sucesso_local": False
    }

def subir_para_google(caminho_arquivo, nome_exibicao):
    try:
        client_local = obter_client_gemini()
        arquivo_google = client_local.files.upload(
            file=caminho_arquivo, 
            config=types.UploadFileConfig(display_name=nome_exibicao)
        )
        return arquivo_google.uri
    except Exception as e:
        return f"Erro no upload: {e}"

# ==============================================================================
# 6. EXTRATOR UNIVERSAL DE TAGS (PRESERVADO 100%)
# ==============================================================================

def extrair_tag(texto, tag):
    if not texto or not isinstance(texto, str): return ""
    tag_busca = tag.upper().strip().replace("[", "").replace("]", "")
    
    if tag_busca in ["ALUNO", "QUESTOES", "CADERNO_DE_REVISAO"]:
        guia = extrair_tag_simples(texto, "GUIA_DE_ESTUDO_ALUNO")
        questoes = extrair_tag_simples(texto, "QUESTOES")
        
        if guia and questoes:
            return f"{guia}\n\n{questoes}"
        elif questoes:
            return questoes
        elif guia:
            return guia

    return extrair_tag_simples(texto, tag_busca)

def extrair_tag_simples(texto, tag_busca):
    alias_map = {
        "PROFESSOR": ["PROFESSOR", "ROTEIRO_DO_PROFESSOR", "GUIA_PROFESSOR", "ROTEIRO_DE_MEDIACAO", "BASE_DIDATICA", "ROTEIRO_DO_PROFESSOR - RECOMPOSIÇÃO", "ROTEIRO_DO_PROFESSOR"],
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
        "ROTEIRO_DO_PROFESSOR", "GUIA_DE_ESTUDO_ALUNO", "RUBRICA_DE_OBSERVACAO", "ROTEIRO_DO_PROFESSOR - RECOMPOSIÇÃO", "GUIA_DE_ESTUDO_DO_ALUNO"
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
    if not texto or not isinstance(texto, str): return []
    
    mapa_regular = {}
    raw_reg = extrair_tag(texto, "GABARITO_TEXTO") or extrair_tag(texto, "GABARITO")
    
    if raw_reg:
        matches_reg = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-E])\b", str(raw_reg).upper())
        for q_num_str, letra in matches_reg:
            mapa_regular[int(q_num_str)] = letra
            
    if not mapa_regular:
        bloco_gab_match = re.search(r"\[\s*GABARITO.*?\].*?$", texto, re.DOTALL | re.IGNORECASE)
        texto_busca = bloco_gab_match.group(0) if bloco_gab_match else texto
        
        matches_brutos = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-E])\b", texto_busca.upper())
        for q_num_str, letra in matches_brutos:
            q_num = int(q_num_str)
            if q_num not in mapa_regular and 1 <= q_num <= 30:
                mapa_regular[q_num] = letra

    qtd_enunciados = len(re.findall(r"(?i)(?:QUEST[AÃ]O\s*|Q)\s*0?(\d+)", extrair_tag(texto, "QUESTOES") or texto))
    max_q = max(mapa_regular.keys()) if mapa_regular else 0
    qtd_oficial = max(max_q, qtd_enunciados, 10)
    
    if not is_pei:
        return [mapa_regular.get(n, "A") for n in range(1, qtd_oficial + 1)]

    mapa_pei = {}
    bloco_pei = extrair_tag(texto, nivel_pei) or extrair_tag(texto, "PEI_NIVEL_1") or extrair_tag(texto, "PEI") or extrair_tag(texto, "GABARITO_PEI")
    
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
            matches_direct = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-E])\b", bloco_pei.upper())
            for q_num_str, letra in matches_direct:
                q_num = int(q_num_str)
                if q_num not in mapa_pei and q_num <= qtd_oficial:
                    mapa_pei[q_num] = letra

    for q_n in range(1, qtd_oficial + 1):
        if q_n not in mapa_pei:
            mapa_pei[q_n] = mapa_regular.get(q_n, "A")

    return [mapa_pei.get(n, "A") for n in range(1, qtd_oficial + 1)]

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
        
        res = client_local.models.generate_content(
            model="gemini-3.5-flash",
            contents=[types.Part.from_text(text=prompt)]
        )
        return res.text.replace("**", "").replace("#", "").strip()
    except Exception as e:
        return f"Erro na perícia: {e}"

def limpar_links_antigos(texto):
    if not texto: return ""
    partes = re.split(r"--- LINKS ---", texto, flags=re.IGNORECASE)
    return partes[0].strip()
