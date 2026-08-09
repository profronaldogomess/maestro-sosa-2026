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
# DICIONÁRIO DE PERSONAS DE ELITE (V2026.MASTER - PRESERVAÇÃO INTEGRAL DE 26 KEYS)
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
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, sem LaTeX, mantendo TODAS as tags originais.""",

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
    Os 10 BOXES do PEI Nível 3 DEVEM ser 100% baseados no tema, nos objetos e nos conceitos da AULA REGULAR (exemplo: se a aula for sobre frações ou divisões, as atividades de pintar, ligar e cobrir pontilhado DEVEM ser sobre figuras fracionadas ou agrupamentos numéricos do tema da aula).

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
    - Baseie-se no contexto dos PLANOS DE AULA, nos exercícios marcados pelo professor e em NOTÍCIAS REAIS de fontes confiáveis (IBGE, G1, Embrapa, economia de Itabuna/BA).
    - TABELAS OBRIGATÓRIAS: Se a questão envolver dados de colheita, pesquisas ou estatísticas, Monte obrigatoriamente uma TABELA FORMATADA EM MARKDOWN no enunciado (exemplo: | Fazenda | Sacas |\n| :--- | :---: |\n| Fazenda A | 120 |). NUNCA descreva tabelas em texto corrido!
    - É PROIBIDO inventar contextos de ficção, jogos (RPG, Roblox) ou temas não fornecidos (SpaceX), a menos que solicitado.

    🚨 LEI DO PROMPT DE IMAGEM TÉCNICA (SOMENTE QUANDO INDISPENSÁVEL):
    - NÃO crie imagens decorativas ou infantis em provas regulares.
    - Se o item exigir suporte visual (geometria, gráficos de colunas/setores, malha quadriculada), inclua no enunciado:
      [ PROMPT IMAGEM: A4 portrait technical math diagram, clean black line art, high contrast, pure white background, no shading, no grayscale, no colors, clean thick outlines, professional textbook style. Visual representation of: [DESCREVA O OBJETO]. All text labels inside the image MUST BE IN PORTUGUESE. ]

    🚨 LEI DO LATEX EM JSON: Envolva TODA expressão matemática, fração ou símbolo obrigatoriamente com cifrão duplo e barras duplas: $$ \\frac{a}{b} $$.

    RETORNE EXATAMENTE UM JSON NESTE FORMATO:
    {
      "questoes": [
        {
          "q": 1,
          "enunciado": "Texto do enunciado com tabela em Markdown quando houver dados...\n\n| Categoria | Valor |\n| :--- | :---: |\n| Item A | 10 |",
          "alt_a": "$$ \\frac{1}{2} $$",
          "alt_b": "$$ \\frac{1}{4} $$",
          "alt_c": "$$ \\frac{3}{4} $$",
          "alt_d": "$$ \\frac{2}{5} $$",
          "alt_e": "$$ \\frac{4}{5} $$",
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
    - Utilize os dados de notas, frequência, ocorrências reais do Diário de Bordo (atitudes, bônus, defasagens de leitura/matemática) e análises de erros das avaliações escaneadas fornecidas.
    - Redija um texto fluido e acolhedor que conecte as evidências empíricas ao progresso individual do estudante.

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS COM COLCHETES):
    [DIAGNOSTICO_GERAL] (Relatório descritivo humano e empático conectando notas, atitudes no diário e desempenho)
    [SOCIAIS] (Interação com os colegas e ambiente escolar)
    [COMUNICATIVAS] (Expressão verbal e compreensão de comandos)
    [EMOCIONAIS] (Autorregulação e tolerância à frustração)
    [FUNCIONAIS] (Autonomia motora e rotina de sala)
    [DIRETRIZES_CURRICULARES] (Recomendações práticas pedagógicas)"""
}

# ==============================================================================
# MOTOR DE INTELIGÊNCIA BARRAGEM ANTI-ALUCINAÇÃO (SOSA V2026.GROUNDING)
# ==============================================================================
def gerar_ia(persona_key, comando, url_drive=None, usar_busca=True, recorte_livro=None):
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
    
    # 🚨 VACINA ANTI-ALUCINAÇÃO: Temperatura reduzida para 0.2 (Modo Factual / Deterministico)
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else [],
        temperature=0.2,
        max_output_tokens=8192,
    )
    
    conteudo_prompt = []
    
    # 🚨 TRAVA DE REALIDADE E ANCORAGEM INQUEBRÁVEL
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
            f"\n📖 CONTEXTO REAL E EXERCÍCIOS RESOLVIDOS EM SALA:\n\"\"\"\n{recorte_livro}\n\"\"\"\n"
        )

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
                    "🚨 ANCORAGEM EXCLUSIVA NO LIVRO PDF ANEXADO:\n"
                    "Leia o arquivo PDF e crie as questões/explicações BASEADAS ESTRITAMENTE NELE. "
                    "É proibido usar exemplos genéricos fora do livro.\n\n"
                    f"{comando}"
                )
                st.toast(f"📖 Livro Didático lido e blindado contra alucinação!", icon="✅")
            else:
                st.toast("⚠️ O arquivo do Drive não é um PDF válido.", icon="⚠️")
        except Exception as e:
            st.toast(f"⚠️ Aviso na leitura do livro no Drive: {e}", icon="⚠️")

    prompt_final = f"{PERSONAS.get(persona_key, PERSONAS['ARQUITETO_EXAMES_ENEM_V2026'])}{trava_realidade}{instrucao_livro}\n\n{comando}"
    conteudo_prompt.append(types.Part.from_text(text=prompt_final))

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
    # 🚨 VACINA ANTI-ALUCINAÇÃO: Temperatura reduzida para 0.2
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else [],
        temperature=0.2, 
        response_mime_type="application/json",
    )
    
    trava_realidade_json = (
        "\n\n🚨 REGRAS RIGIDAS DE GROUNDING (ZERO ALUCINAÇÃO):\n"
        "1. É PROIBIDO inventar contextos fictícios fora do fornecido (como SpaceX, RPG, games, etc.).\n"
        "2. Se houver contexto de Itabuna/Bahia ou trecho de Livro Didático abaixo, 100% DAS QUESTÕES DEVEM SER EXTRAÍDAS OU ESPELHADAS DELE.\n"
        "3. Mantenha fidelidade absoluta ao tema de cada item enviado.\n"
        "4. ATENÇÃO COM LATEX EM JSON: Sempre use barra dupla para comandos LaTeX no JSON (exemplo: \\\\frac{1}{2}, \\\\times, \\\\div, \\\\circ).\n\n"
    )
    
    conteudo_prompt = [types.Part.from_text(text=f"{PERSONAS[persona_key]}\n{trava_realidade_json}\n\n{comando}")]
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
        
        match = re.search(r'\{.*\}', texto_limpo, re.DOTALL)
        if match:
            json_str = match.group(0)
            
            # 🚨 VACINA ANTI-ESCAPE DE BARRA LATEX EM JSON (\frac -> \\frac)
            json_str_reparado = re.sub(r'\\(?![/"bfnrtu\\])', r'\\\\', json_str)
            
            try:
                return json.loads(json_str_reparado)
            except json.JSONDecodeError:
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    # Tratamento de emergência para caracteres ocultos
                    json_str_clean = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', json_str_reparado)
                    return json.loads(json_str_clean)
        
        return json.loads(texto_limpo)
    except Exception as e:
        return {"erro": f"Erro no parsing do lote: {str(e)}"}

# ==============================================================================
# EXTRATOR UNIVERSAL DE TAGS (MULTIMODO V2026.MASTER - FLEXÍVEL E PROPORCIONAL)
# ==============================================================================
def extrair_tag(texto, tag):
    """
    EXTRATOR UNIVERSAL SOSA V2026.MASTER
    Possui junção automática de [GUIA_DE_ESTUDO_ALUNO] + [QUESTOES] para materiais de revisão.
    """
    if not texto or not isinstance(texto, str): return ""
    tag_busca = tag.upper().strip().replace("[", "").replace("]", "")
    
    # 🚨 TRATAMENTO ESPECIAL PARA REVISÃO: UNIR GUIA DE ESTUDO + QUESTÕES
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
    """Extrator de bloco individual seguro."""
    alias_map = {
        "PROFESSOR": ["PROFESSOR", "ROTEIRO_DO_PROFESSOR", "GUIA_PROFESSOR", "ROTEIRO_DE_MEDIACAO", "BASE_DIDATICA"],
        "ALUNO": ["ALUNO", "GUIA_DE_ESTUDO_ALUNO", "QUESTOES", "QUESTOES_ESPELHO", "CADERNO_DE_REVISAO"],
        "QUESTOES": ["QUESTOES", "QUESTOES_ESPELHO", "CADERNO_DE_REVISAO"],
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
        "ROTEIRO_DO_PROFESSOR", "GUIA_DE_ESTUDO_ALUNO", "RUBRICA_DE_OBSERVACAO"
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
    EXTRAÍDOR UNIVERSAL DE GABARITOS V2026 (RETROCOMPATÍVEL E ROBUSTO):
    Varre 100% do bloco de gabarito extraindo todas as questões.
    """
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
            f"VOCÊ É O PERITO EM AVALIAÇÃO EDUCACIONAL SOSA (PADRÃO SAEB/ENEM/BNCC).\n"
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
