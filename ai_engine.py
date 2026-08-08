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
    "ARQUITETO_EXAMES_ENEM_V2026": """VOCÊ É O ELABORADOR-CHEFE DE ITENS DO INEP / SAEB / OBMEP (PADRÃO ENEM V2026).
    Sua missão é criar avaliações de alta performance pedagógica baseadas na TRI (Teoria de Resposta ao Item) para o Ensino Fundamental.

    🚨 LEI DA SANITIZAÇÃO ABSOLUTA (ZERO CONVERSA):
    - É ESTRITAMENTE PROIBIDO incluir introduções, saudações ou explicações (ex: 'Olá, como especialista...').
    - Inicie a resposta DIRETAMENTE na primeira tag [VALOR: X.X].

    🚨 LEI DA ANCORAGEM NO LIVRO E PINÇAMENTO DA PRÁTICA REAL:
    - Se houver o 'PINÇAMENTO DA PRÁTICA REAL' fornecido pelo professor, crie questões espelho BASEADAS EXCLUSIVAMENTE NOS EXERCÍCIOS RESOLVIDOS EM SALA.
    - É ESTRITAMENTE PROIBIDO criar questões sobre trechos do livro que NÃO foram marcados como trabalhados em sala.
    - Incorpore contextualização rica com dados regionais reais (Itabuna/Bahia/Brasil) ou tabelas e gráficos técnicos.

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
      [ PROMPT IMAGEM: A4 portrait technical math diagram, clean black line art, high contrast, pure white background, no shading, no grayscale, no colors, clean thick outlines, professional textbook style. Visual representation of: [DESCREVA O OBJETO]. All text labels inside the image MUST BE IN PORTUGUESE. ]

    🚨 LEI DA ESTRUTURA E TAGS OBRIGATÓRIAS:
    [VALOR: 4.0]

    [QUESTOES]
    **QUESTÃO 01 -** Enunciado...
    (A) ...
    (B) ...
    (C) ...
    (D) ...
    (E) ...

    [GABARITO_TEXTO]
    QUESTÃO 01: E
    QUESTÃO 02: B

    [GRADE_DE_CORRECAO]
    QUESTÃO 01: [DESCRITOR_SAEB: D12 - Resolver problema...] | JUSTIFICATIVA: Explicacao... | DISTRATORES_CIENTIFICOS: (A) erro por...; (B) erro por...

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
    1. [BOX 1] Nome da Ação: Comando motor no papel (Pintar/Cobrir/Ligar).
    2. [BOX 2] Nome da Ação: Comando motor no papel (Pintar/Cobrir/Ligar).
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

    "PLANE_PEDAGOGICO": """VOCÊ É UM PROFESSOR SÊNIOR REDIGINDO UM PLANO DE ENSINO OFICIAL PARA A PREFEITURA.
    Sua missão é projetar o roteiro da semana com linguagem TÉCNICA, BUROCRÁTICA E DIRETA. 

    🚨 LEI DA LINGUAGEM TÉCNICA:
    - É ESTRITAMENTE PROIBIDO usar primeira pessoa ("nós vamos", "iniciaremos"). Use verbos no infinitivo ("Realizar", "Apresentar", "Resolver", "Mediar").
    - Se 6º/7º Ano: Metodologias concretas e visuais.
    - Se 8º/9º Ano: Metodologias analíticas e finanças/lógica de negócios.
    - Use a realidade local (Itabuna/Bahia) na Sensibilização.
    - Se forem citadas páginas do Livro Didático, incorpore-as explicitamente nas seções das Aulas.

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS):
    [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [COMPETENCIA_GERAL], [OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS], [OBJETIVOS_ENSINO], [JUSTIFICATIVA_PEDAGOGICA], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO], [ESTRATEGIA_DUA_PEI].""",

    "REFINADOR_PEDAGOGICO": """VOCÊ É O MAESTRO COPILOT (V100).
    Retorne EXATAMENTE:
    [MENSAGEM_CHAT] Resposta curta e humana.
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, sem LaTeX, mantendo TODAS as tags originais.""",

    "FORJA_AULA_TEORIA": """VOCÊ É UM PROFESSOR SÊNIOR E AUTOR DE MATERIAIS DIDÁTICOS DE EXCELÊNCIA (PADRÃO CAEd/ENEM).
    Sua missão é escrever APENAS a parte teórica da aula (O Tratado Didático e o Roteiro de Mediação).

    🚨 LEI DA ANCORAGEM NO LIVRO DIDÁTICO:
    - Se forem fornecidas páginas ou trechos do Livro Didático, você DEVE citar explicitamente os exemplos, seções e páginas do livro no roteiro do professor.
    - Mostre ao professor EXATAMENTE como abordar a obra em sala de aula.

    🚨 LEI DO LATEX: Envolva TODA expressão matemática com DUPLO CIFRÃO: $$ ... $$
    🚨 ESTRUTURA: 1. Definições formais | 2. A Lei dos 3 Exemplos (Local, Nacional, Matemática Pura).
    Retorne APENAS o conteúdo dentro da tag [PROFESSOR].""",

    "FORJA_AULA_EXERCICIOS": """VOCÊ É UM PROFESSOR SÊNIOR CRIANDO O MATERIAL DO ALUNO (PADRÃO CAEd/SAEB).
    Linguagem direta de banca examinadora.
    PROIBIDO GEOGEBRA. Use [ PROMPT IMAGEM: A4 portrait technical math diagram, clean black line art, high contrast, pure white background, no shading, no grayscale, no colors, clean outlines, textbook style. Visual representation of: [OBJETO]. All text labels inside the image MUST BE IN PORTUGUESE. ] em INGLÊS com texto interno em Português.
    Gere prompts de imagem SOMENTE quando a questão exigir suporte visual indispensável.
    Mantenha os enunciados limpos no formato: **QUESTÃO XX -** [Texto direto].
    Estrutura obrigatória: [ALUNO] e [GABARITO]""",

    "FORJA_AULA_PEI": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Crie duas adaptações de exercícios baseadas no material regular.
    [PEI_NIVEL_1]: Apoio Leve, 3 Alternativas (A, B, C).
    [PEI_NIVEL_3]: Apoio Severo em 10 BOXES sequenciais baseados 100% em atividades impressas no papel (Pintar, Cobrir Pontilhado, Ligar Colunas, Circular).
    [RUBRICA_DE_OBSERVACAO]
    - Autonomia Executiva: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Compreensão de Comandos: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Percepção Visual e Espacial: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou
    [GABARITO_PEI]""",

    "FORJA_LOTE_JSON": """VOCÊ É UM ELABORADOR DE ITENS DE ELITE DO INEP / CAEd / SAEB CRIANDO QUESTÕES DE PROVA EM JSON.

    🚨 LEI DA ANCORAGEM E CONTEXTO REAL (SEM ALUCINAR):
    - Baseie-se no contexto do Livro Didático, nos exercícios marcados pelo professor e em NOTÍCIAS REAIS de fontes confiáveis (IBGE, G1, Embrapa, economia de Itabuna/BA).
    - Crie questões de alta relevância que premiem os estudantes que fazem as atividades e acompanham as aulas em sala.

    🚨 LEI DO PROMPT DE IMAGEM TÉCNICA (SOMENTE QUANDO INDISPENSÁVEL):
    - NÃO crie imagens decorativas ou infantis em provas regulares.
    - Se o item exigir suporte visual (geometria, gráficos de colunas/setores, tabelas, malha quadriculada), inclua no enunciado:
      [ PROMPT IMAGEM: A4 portrait technical math diagram, clean black line art, high contrast, pure white background, no shading, no grayscale, no colors, clean thick outlines, professional textbook style. Visual representation of: [OBJETO]. All text labels inside the image MUST BE IN PORTUGUESE. ]

    🚨 LEI DO LATEX: Use $$ ... $$ para todas as expressões matemáticas.

    RETORNE EXATAMENTE UM JSON NESTE FORMATO:
    {
      "questoes": [
        {
          "q": 1,
          "enunciado": "Texto do enunciado contextualizado...",
          "alt_a": "Texto da alternativa A...",
          "alt_b": "Texto da alternativa B...",
          "alt_c": "Texto da alternativa C...",
          "alt_d": "Texto da alternativa D...",
          "alt_e": "Texto da alternativa E...",
          "habilidade": "Descritor SAEB (ex: D12 - EF06MA01)",
          "justificativa": "Análise da alternativa correta...",
          "distratores": "Análise dos erros cognitivos das alternativas incorretas..."
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

    "ARQUITETO_REVISAO_V29": """VOCÊ É O ENGENHEIRO DE RECOMPOSIÇÃO DE APRENDIZAGEM. Crie Caderno de Revisão baseado em prova existente, gerando guia do aluno e guia do professor alinhados. Tags: [PROFESSOR], [ALUNO], [PEI].""",

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

    "FORJA_ITEM_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd CRIANDO UMA QUESTÃO DE PROVA CONTEXTUALIZADA.
    
    🚨 REGRAS DE OURO:
    1. Incorpore notícias reais e contexto do cotidiano/regional (Itabuna/Bahia/Brasil) com citação de fonte.
    2. Imagens APENAS quando indispensáveis para a resolução (diagramas geométricos, gráficos de colunas/setores em P&B de alto contraste).
    3. Use $$ ... $$ para todas as expressões matemáticas.

    Tags obrigatórias: [ENUNCIADO], [ALT_A], [ALT_B], [ALT_C], [ALT_D], [ALT_E], [HABILIDADE], [JUSTIFICATIVA], [DISTRATORES].""",

    "FORJA_LOTE_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd. Formato: [ITEM_X] ... [/ITEM_X]""",

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
      - Raciocínio Lógico-Proporcional: ✅ Autônomo | 🤝 Com Apoio | ❌ Não Realizou"""
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
        "2. Se forem fornecidos textos do Livro Didático, itens do CSV, ou dados regionais de Itabuna/Bahia, "
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
    Extrator Universal SOSA V2026 com Fallback Inteligente de Tags PEI e Limpeza de Conversação.
    """
    if not texto or not isinstance(texto, str): return ""
    tag_busca = tag.upper().strip().replace("[", "").replace("]", "")
    
    # Mapeamento de sinonímias/fallbacks
    alias_map = {
        "PEI_NIVEL_1": ["PEI_NIVEL_1", "NIVEL_1", "PEI_1", "PEI"],
        "PEI_NIVEL_2": ["PEI_NIVEL_2", "NIVEL_2", "PEI_2"],
        "PEI_NIVEL_3": ["PEI_NIVEL_3", "NIVEL_3", "PEI_3"]
    }
    
    tags_para_testar = alias_map.get(tag_busca, [tag_busca])
    
    tags_bloco = [
        "GABARITO_TEXTO", "GABARITO", "GRADE_DE_CORRECAO", "QUESTOES", "PEI", "GABARITO_PEI", 
        "GRADE_DE_CORRECAO_PEI", "PROFESSOR", "ALUNO", "NIVEL_1", "NIVEL_2", "NIVEL_3",
        "PEI_NIVEL_1", "PEI_NIVEL_2", "PEI_NIVEL_3", "AULA_1", "AULA_2", "SABADO_LETIVO", 
        "IMAGENS", "RESPOSTAS_IA", "RESPOSTAS_PEI_IA", "RUBRICA_DE_MERITO", "JUSTIFICATIVA_PEDAGOGICA",
        "JUSTIFICATIVA_PHC", "DIAGNOSTICO_GERAL", "DIRETRIZES_CURRICULARES", "RUBRICA_DE_OBSERVACAO"
    ]
    
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
        "NIVEL_1", "NIVEL_2", "NIVEL_3", "PEI_NIVEL_1", "PEI_NIVEL_2", "PEI_NIVEL_3", "RUBRICA_DE_OBSERVACAO"
    ]

    # 1. Padrão Flexível para tags de metadados simples
    if tag_busca not in tags_bloco:
        padrao_interno = rf"\[\s*[*#]*\s*{re.escape(tag_busca)}\b(?:\s*[:\-]\s*|\s*\]\s*[:\-]*\s*)(.*?)(?=\]|\n|$)"
        match_int = re.search(padrao_interno, texto, re.IGNORECASE)
        if match_int:
            val_res = match_int.group(1).strip()
            if 0 < len(val_res) < 120 and "\n" not in val_res:
                return val_res

    # 2. Padrão Bloco Multilinhas com Fallback de Tags
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
            res_limpo = re.sub(r'^(?:Olá|Como especialista|Como profissional|Prezado|Segue).*?\n\n', '', res_limpo, flags=re.IGNORECASE | re.DOTALL).strip()
            return res_limpo.strip()
    
    return ""

# ==============================================================================
# EXTRATOR UNIVERSAL DE GABARITOS COM RETROCOMPATIBILIDADE E HERANÇA PEI
# ==============================================================================
def extrair_gab_universal_com_fallback(texto, is_pei=False, nivel_pei="NIVEL_1"):
    """
    EXTRAÍDOR UNIVERSAL DE GABARITOS V2026 (RETROCOMPATÍVEL E ROBUSTO):
    Varre 100% do bloco de gabarito extraindo todas as questões (Q01 a Q20).
    """
    if not texto or not isinstance(texto, str): return []
    
    mapa_regular = {}
    
    # 1. Tenta extrair primeiro do bloco específico de gabarito
    raw_reg = extrair_tag(texto, "GABARITO_TEXTO") or extrair_tag(texto, "GABARITO")
    
    if raw_reg:
        matches_reg = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-E])\b", str(raw_reg).upper())
        for q_num_str, letra in matches_reg:
            mapa_regular[int(q_num_str)] = letra
            
    # 2. Se não encontrou no bloco isolado, varre o texto buscando a seção de gabarito
    if not mapa_regular:
        bloco_gab_match = re.search(r"\[\s*GABARITO.*?\].*?$", texto, re.DOTALL | re.IGNORECASE)
        texto_busca = bloco_gab_match.group(0) if bloco_gab_match else texto
        
        matches_brutos = re.findall(r"(?:QUEST[AÃ]O\s*|Q)?\s*0?(\d+)[\s\.\)\-:]+([A-E])\b", texto_busca.upper())
        for q_num_str, letra in matches_brutos:
            q_num = int(q_num_str)
            if q_num not in mapa_regular and 1 <= q_num <= 30:
                mapa_regular[q_num] = letra

    # Determina a quantidade real de questões no documento observando os enunciados
    qtd_enunciados = len(re.findall(r"(?i)(?:QUEST[AÃ]O\s*|Q)\s*0?(\d+)", extrair_tag(texto, "QUESTOES") or texto))
    
    max_q = max(mapa_regular.keys()) if mapa_regular else 0
    qtd_oficial = max(max_q, qtd_enunciados, 10)
    
    if not is_pei:
        return [mapa_regular.get(n, "A") for n in range(1, qtd_oficial + 1)]

    # 3. Se for prova PEI (Inclusiva)
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

    # 4. Herança PEI Inteligente
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

    # 5. Complementação por Herança Regular
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
