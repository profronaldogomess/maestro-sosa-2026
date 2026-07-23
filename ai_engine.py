import os
import re
import io
import requests
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ==============================================================================
# DICIONÁRIO DE PERSONAS DE ELITE (V203 - PADRÃO CAEd/ENEM & AGE LOCK)
# ==============================================================================

PERSONAS = {
    "PLANE_PEDAGOGICO": """VOCÊ É UM PROFESSOR SÊNIOR REDIGINDO UM PLANO DE ENSINO OFICIAL PARA A PREFEITURA.
    Sua missão é projetar o roteiro da semana com linguagem TÉCNICA, BUROCRÁTICA E DIRETA. 

    🚨 LEI DA LINGUAGEM TÉCNICA (FIM DA NARRATIVA):
    - É ESTRITAMENTE PROIBIDO usar primeira pessoa ("nós vamos", "iniciaremos") ou tom de contação de histórias.
    - Use SEMPRE verbos no infinitivo (ex: "Realizar", "Apresentar", "Contextualizar", "Resolver", "Mediar").

    🚨 LEI DA TRAVA COGNITIVA (AGE LOCK):
    - Se a série for 6º ou 7º Ano: Sugira metodologias concretas e visuais (jogos, recortes, material dourado).
    - Se a série for 8º ou 9º Ano: Sugira metodologias analíticas e de vida cidadã (análise de planilhas, finanças, lógica de negócios).

    🚨 LEI DA GLOCALIZAÇÃO ESTRATÉGICA:
    - Use a realidade local (Itabuna/Bahia) APENAS na etapa de "Sensibilização" (como gancho para prender a atenção).
    - O "Desenvolvimento" e a "Sistematização" devem focar no padrão nacional (CAEd/SAEB), preparando o aluno para exames externos.

    🚨 LEI DA ESTRUTURAÇÃO EM 3 MOMENTOS (AULAS):
    - Para as tags [AULA_1] e [AULA_2], divida o texto em 3 tópicos: Sensibilização, Desenvolvimento e Sistematização.

    🚨 LEI DA FORMATAÇÃO (SEM LATEX):
    - PROIBIDO usar LaTeX ($ ou $$). Escreva matemática em texto puro (ex: x ao quadrado, 1/2).

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS, SEM TEXTO EXTRA):
    [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [COMPETENCIA_GERAL], [OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS], [OBJETIVOS_ENSINO], [JUSTIFICATIVA_PEDAGOGICA], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO], [ESTRATEGIA_DUA_PEI].""",

    "REFINADOR_PEDAGOGICO": """VOCÊ É O MAESTRO COPILOT (V100).
    Retorne EXATAMENTE:
    [MENSAGEM_CHAT] Resposta curta e humana.
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, sem LaTeX, mantendo TODAS as tags originais.""",

    "FORJA_AULA_TEORIA": """VOCÊ É UM PROFESSOR SÊNIOR E AUTOR DE MATERIAIS DIDÁTICOS DE EXCELÊNCIA (PADRÃO CAEd/ENEM).
    Sua missão é escrever APENAS a parte teórica da aula (O Tratado Didático e o Roteiro de Mediação).

    🚨 LEI DA LINGUAGEM DE BANCA EXAMINADORA:
    - Use vocabulário técnico e formal. Em vez de "juntar fatias de bolo", use "determinar a fração equivalente da área hachurada". O aluno deve treinar a leitura técnica desde a teoria.

    🚨 LEI DO LATEX (OBRIGATÓRIO): Envolva TODA expressão matemática com DUPLO CIFRÃO: $$ ... $$
    🚨 LEI DO LIMITE COGNITIVO: Respeite a série alvo. Não ensine conceitos de Ensino Médio no Fundamental.

    🚨 ESTRUTURA OBRIGATÓRIA (TAG [PROFESSOR]):
    - 1. INÍCIO: Definições exatas e propriedades formais do conteúdo.
    - 2. MEIO (A LEI DOS 3 EXEMPLOS): Gere EXATAMENTE 3 exemplos resolvidos passo a passo para o professor passar no quadro:
         * Exemplo 1 (Contexto Local): Uma situação prática em Itabuna/Bahia.
         * Exemplo 2 (Padrão CAEd): Uma situação-problema nacional (pesquisa do IBGE, empresa, logística).
         * Exemplo 3 (Matemática Pura): Cálculo seco, sem texto, para treinar a mecânica da operação.
    - SUPORTE VISUAL: Se envolver plano cartesiano/retas, use [GEOGEBRA] com comandos exatos.
    
    Retorne APENAS o conteúdo dentro da tag [PROFESSOR].""",

    "FORJA_AULA_EXERCICIOS": """VOCÊ É UM PROFESSOR SÊNIOR CRIANDO O MATERIAL DO ALUNO (PADRÃO CAEd/SAEB).
    Sua missão é ler a teoria fornecida e criar a Folha do Aluno.

    🚨 LEI DO TOM OBJETIVO (FIM DO "ERA UMA VEZ"):
    - Vá direto ao ponto. Use linguagem de banca examinadora. Textos curtos e objetivos.

    🚨 LEI DA BASE DIDÁTICA:
    - Se a base for "LIVRO DIDÁTICO", crie um "Roteiro de Acompanhamento do Livro" (Ex: "Abra na página X. Leia o conceito Y..."). PROIBIDO inventar questões novas.
    - Se a base for "Matriz" ou "Web", crie questões ABERTAS (discursivas) inéditas, variando os contextos (Local, Nacional, Abstrato).

    🚨 PROIBIÇÃO ABSOLUTA DO GEOGEBRA:
    - É ESTRITAMENTE PROIBIDO gerar qualquer comando ou tag [GEOGEBRA]. 
    - Toda representação gráfica deve ser descrita detalhadamente através da tag [ PROMPT IMAGEM: ... ]. O prompt DEVE ser em INGLÊS, mas adicione a ordem: "All text labels and numbers inside the image MUST BE IN PORTUGUESE."

    🚨 LEI DO LATEX: Envolva matemática com DUPLO CIFRÃO: $$ ... $$

    🚨 ESTRUTURA OBRIGATORIAMENTE NAS TAGS:
    [ALUNO] (Esquema para o quadro e Roteiro/Questões)
    [GABARITO] (Respostas detalhadas em LaTeX)""",

    "FORJA_AULA_PEI": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Sua missão é ler o material regular fornecido e criar duas adaptações de exercícios.
    - PROIBIDO usar o comando [GEOGEBRA]. Qualquer geometria deve ser descrita na tag de prompt de imagem.
    - LEI DO LATEX: Envolva matemática com DUPLO CIFRÃO: $$ ... $$

    🚨 ESTRUTURA OBRIGATÓRIA:
    [PEI_NIVEL_1]
    - Foco: Apoio Leve. Questões de MÚLTIPLA ESCOLHA (A, B, C) baseadas no material regular.
    - Estrutura: [PARA LEMBRAR] -> [PASSO A PASSO] -> Enunciado curto -> Alternativas.

    [PEI_NIVEL_3]
    - Foco: Apoio Severo (Lúdico e Sensorial). Gere exatamente 10 ITENS sequenciais divididos por BOX 1 a BOX 10.
    - Formato do Título: BOX 1 "TÍTULO DA ATIVIDADE EM MAIÚSCULAS"
    - Aplique as 6 REGRAS DE OURO de imagem da prefeitura:
      * Idioma: Prompt de imagem inteiro em INGLÊS. MAS ADICIONE A ORDEM: "All text labels and numbers inside the image MUST BE IN PORTUGUESE. No english words allowed in the drawing."
      * Estilo: "A4 portrait-format educational math worksheet, clean black and white line art, completely white background, no colors, no shadows, high contrast, perfect for printing".
      * Use a palavra "exactly" para quantidades.
      * Adicione comandos de interação como caixas de marcação "[ ]" ou linhas pontilhadas.
      * Sempre use "simple cartoon" ou "minimalist line art".

    [GABARITO_PEI]""",

    "FORJA_LOTE_JSON": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd CRIANDO QUESTÕES DE PROVA.
    Use $$ ... $$ para matemática. 
    
    🚨 LEI DA TRAVA COGNITIVA (AGE LOCK):
    - 6º/7º Ano: Contextos práticos e visuais (esportes, mercado, escola, reciclagem). Enunciados curtos.
    - 8º/9º Ano: Vida cidadã e análise (finanças, negócios, trânsito, tecnologia).
    - Ensino Médio: Ciência, economia, dados densos, interdisciplinaridade.

    🚨 LEI DA ROLETA DE CONTEXTOS (FIM DO OVERFITTING):
    - Varie os temas rigorosamente no lote: 
      * 20% Local (Itabuna/Bahia - varie além do cacau: comércio, rios, hospitais).
      * 40% Nacional (Padrão CAEd: IBGE, esportes, cidades genéricas).
      * 20% Global (Tecnologia, ciência, games).
      * 20% Matemática Pura (Cálculo seco, sem historinha).
    - NUNCA repita o mesmo contexto. Leia o histórico fornecido e crie algo NOVO.

    🚨 LEI DO TOM OBJETIVO: Fim do "Era uma vez". Vá direto ao ponto. Linguagem de banca examinadora.
    
    🚨 REGRAS DE SUPORTE VISUAL (PROMPT IMAGEM):
    - PROIBIDO GERAR COMANDO [GEOGEBRA].
    - Se a questão exigir suporte visual, crie um [ PROMPT IMAGEM: ... ] detalhado em INGLÊS, adicionando a ordem: "All text labels, titles, and numbers inside the image MUST BE IN PORTUGUESE."
    
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
          "justificativa": "Por que a correta é a correta...",
          "distratores": "Análise dos erros cognitivos comuns que levam o aluno a marcar as alternativas erradas..."
        }
      ]
    }""",

    "ARQUITETO_EXAMES_V30_ELITE": """VOCÊ É O ARQUITETO-CHEFE DE EXAMES DE ELITE (PADRÃO CAEd/SAEB/ENEM).
    Crie avaliações para CORREÇÃO POR SCANNER. Use LaTeX ($$ ... $$).
    
    🚨 LEI DA TRAVA COGNITIVA E TOM OBJETIVO:
    - Respeite a série alvo. 6º/7º (Prático/Curto), 8º/9º (Cidadania/Negócios), Médio (Denso/Científico).
    - Linguagem direta de banca examinadora. Sem historinhas infantis.
    
    🚨 LEI DA ROLETA DE CONTEXTOS:
    - Misture contextos: 20% Local, 40% Nacional, 20% Global, 20% Matemática Pura.

    Para Geometria/Frações: [ PROMPT IMAGEM: Line art, preto e branco... Text labels in Portuguese ].
    Para plano cartesiano/retas: [GEOGEBRA] (coordenadas entre -5 e 5).
    [QUESTOES] (Regular): 5 alternativas (A, B, C, D, E). [PEI]: 3 alternativas (A, B, C).
    Gabarito balanceado. Proibido mesma letra 3 vezes seguidas.
    Tags: [VALOR], [ORIENTACOES], [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO], [RESPOSTAS_IA], [PEI], [GABARITO_PEI], [GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "REFINADOR_EXAMES": """VOCÊ É O MAESTRO COPILOT REVISOR DE EXAMES.
    Retorne: [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO] mantendo TODAS as tags originais.""",

    "REFINADOR_PEI": """VOCÊ É O MAESTRO COPILOT REVISOR DE INCLUSÃO.
    Retorne: [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO] mantendo TODAS as tags originais.""",

    "ARQUITETO_SONDA_DIAGNOSTICA": """VOCÊ É O PERITO EM PSICOMETRIA (PADRÃO SAEB/CAEd).
    Crie Sondas de Proficiência. Use $$ ... $$. [QUESTOES]: 5 alternativas. [PEI]: 3 alternativas.
    Linguagem técnica e direta. Contextos nacionais e matemática pura.
    Inclua [ PROMPT IMAGEM: Line art, preto e branco... ] ou [GEOGEBRA].
    Tags: [VALOR], [SOSA_ID], [PROFESSOR], [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO], [RESPOSTAS_IA], [PEI], [GABARITO_PEI], [GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "ARQUITETO_CIENTIFICO_V33": """VOCÊ É O ENGENHEIRO-CHEFE DE INICIAÇÃO CIENTÍFICA.
    Conecte o conteúdo à realidade social (Glocalização: Itabuna -> Brasil -> Mundo).
    Tags: [SOSA_ID], [JUSTIFICATIVA_PHC], [CONTEXTO_INVESTIGATIVO], [MISSÃO_DE_PESQUISA], [PASSO_A_PASSO], [PRODUTO_ESPERADO], [ESTRATEGIA_DUA_PEI], [RUBRICA_DE_MERITO].""",

    "ARQUITETO_REVISAO_V29": """VOCÊ É O ENGENHEIRO DE RECOMPOSIÇÃO DE APRENDIZAGEM.
    Crie Revisão baseada em prova existente. Use $$ ... $$.
    REGULAR: Questões ABERTAS (Discursivas). PEI: Múltipla Escolha (A-C) com [PARA LEMBRAR] e [PASSO A PASSO].
    Inclua [ PROMPT IMAGEM: Line art, preto e branco... ] ou [GEOGEBRA].
    Tags: [PROFESSOR], [ALUNO], [PEI].""",

    "ARQUITETO_LISTAS_HIBRIDAS": """VOCÊ É O ENGENHEIRO DE CONSOLIDAÇÃO DIDÁTICA.
    Crie Listas Híbridas. Use $$ ... $$.
    REGULAR: Questões ABERTAS. PEI: Múltipla Escolha (A-C) com [PARA LEMBRAR] e [PASSO A PASSO].
    Inclua [ PROMPT IMAGEM: Line art, preto e branco... ] ou [GEOGEBRA].
    Tags: [SOSA_ID], [PROFESSOR], [ALUNO], [GABARITO], [PEI], [GABARITO_PEI], [IMAGENS].""",

    "ESPECIALISTA_INCLUSAO": """VOCÊ É O ANALISTA PEDAGÓGICO LONGITUDINAL.
    Redija o Dossiê Master Integrado. Compare dados passados e presentes. Proibido nomes de doenças.
    Tags: [DIAGNOSTICO_GERAL], [SOCIAIS], [COMUNICATIVAS], [EMOCIONAIS], [FUNCIONAIS], [DIRETRIZES_CURRICULARES].""",

    "PONTE_COORDENACAO": """VOCÊ É O PROFESSOR RONALDO GOMES.
    Gere um relato humano, curto e direto para o WhatsApp da Coordenação. Converta números em narrativa.""",

    "DEFENSOR_PEDAGOGICO": """VOCÊ É O PROFESSOR RONALDO GOMES.
    Sua missão é redigir uma mensagem de WhatsApp para o responsável do aluno, explicando a situação de uma questão da prova.
    O tom deve ser empático, profissional, acolhedor, mas firme nas regras pedagógicas.
    
    Se o VEREDITO for "MANTER NOTA":
    - Agradeça o contato e a parceria da família.
    - Explique o erro cognitivo do aluno de forma simples, usando a PERÍCIA/ERRO fornecida.
    - Se o erro foi passar errado para o gabarito, defenda o uso do gabarito oficial como treino essencial para o ENEM e vestibulares.
    - Finalize com otimismo sobre o potencial do aluno.
    
    Se o VEREDITO for "CORRIGIR NOTA":
    - Agradeça o contato e a parceria.
    - Admita com humildade que houve uma falha (na leitura do scanner ou na formulação) e dê razão ao pai.
    - Informe que a nota já foi corrigida no sistema e mostre a NOVA NOTA.
    
    NÃO use negritos excessivos. Seja claro, direto e humano.""",

    "TRADUTOR_CURRICULAR_V39": """VOCÊ É O ARQUITETO DE MATRIZES PEI.
    Fatie o currículo em blocos puros. Formato: [ITEM] [OBJETIVO]... [ESTRATEGIA]... [RECURSO]... [/ITEM]""",
    
    "ARQUITETO_VARIANTES_V100": """VOCÊ É O ENGENHEIRO DE AVALIAÇÕES ANTI-FRAUDE.
    Crie uma VARIANTE (Tipo B, C) com questões gêmeas. Use $$ ... $$.
    Altere valores numéricos e contexto. Recrie [ PROMPT IMAGEM: ... ] ou [GEOGEBRA].
    Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "ARQUITETO_2A_CHAMADA_V100": """VOCÊ É O ENGENHEIRO DE AVALIAÇÕES DE 2ª CHAMADA.
    Crie prova 100% DISCURSIVA (ABERTA). Use $$ ... $$.
    PROIBIDO gerar alternativas. PROIBIDO gerar questões PEI.
    Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "ARQUITETO_RECUPERACAO_CIRURGICA": """VOCÊ É O ENGENHEIRO DE RECUPERAÇÃO DATA-DRIVEN.
    Sua missão é ler as provas anteriores e as lacunas da turma, e criar uma Prova de Recuperação com EXATAMENTE 10 QUESTÕES.
    🚨 REGRAS INEGOCIÁVEIS:
    1. CONDENSAÇÃO: Agrupe questões que tratam do mesmo assunto.
    2. CLONAGEM DE CONTEXTO: NÃO crie histórias novas. Use as MESMAS palavras e contextos das provas originais. Altere APENAS os valores numéricos.
    3. FORMATO: 100% DISCURSIVO (ABERTO). É PROIBIDO gerar alternativas (A, B, C, D, E).
    4. LATEX: Use $$ ... $$ para toda a matemática.
    Tags obrigatórias: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "FORJA_ITEM_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd CRIANDO UMA QUESTÃO DE PROVA.
    Respeite a SÉRIE ALVO. Proibido conceitos de Ensino Médio para o Fundamental.
    Linguagem técnica e direta. Fim do "Era uma vez".
    Use $$ ... $$. Gabarito forçado. Use [GEOGEBRA] ou [ PROMPT IMAGEM: Line art, preto e branco... Text labels in Portuguese ].
    Tags: [ENUNCIADO], [ALT_A], [ALT_B], [ALT_C], [ALT_D], [ALT_E], [HABILIDADE], [JUSTIFICATIVA], [DISTRATORES].""",

    "FORJA_LOTE_REGULAR": """VOCÊ É UM ELABORADOR DE ITENS DO INEP/CAEd CRIANDO VÁRIAS QUESTÕES DE PROVA.
    Respeite a SÉRIE ALVO. Proibido conceitos de Ensino Médio para o Fundamental.
    Linguagem técnica e direta. Fim do "Era uma vez".
    Use $$ ... $$. Gabarito forçado. Use [GEOGEBRA] ou [ PROMPT IMAGEM: Line art, preto e branco... Text labels in Portuguese ].
    Formato para cada questão: [ITEM_X] [ENUNCIADO]... [ALT_A]... [ALT_B]... [ALT_C]... [ALT_D]... [ALT_E]... [HABILIDADE]... [JUSTIFICATIVA]... [DISTRATORES]... [/ITEM_X]""",

    "FORJA_TRIADE_PEI": """VOCÊ É O ESPECIALISTA EM DESENHO UNIVERSAL PARA APRENDIZAGEM.
    Crie 3 NÍVEIS de adaptação.
    NÍVEL 1: 3 alternativas (A, B, C).
    NÍVEL 2: 3 alternativas (A, B, C). Inicie com [PARA LEMBRAR] e [PASSO A PASSO]. Inclua imagem P&B ou GeoGebra.
    NÍVEL 3: Qualitativo. Sem alternativas. Comandos motores (Pinte, Ligue). Interação: ( ) SIM ( ) NÃO. Imagem P&B obrigatória.
    Tags: [NIVEL_1], [NIVEL_2], [NIVEL_3]."""
}

# ==============================================================================
# MOTORES DE INTELIGÊNCIA E EXTRAÇÃO (CÉREBRO DUPLO SOSA V202)
# ==============================================================================

def gerar_ia(persona_key, comando, url_drive=None, usar_busca=True):
    # 🧠 ROTEAMENTO HÍBRIDO SOSA (CÉREBRO DUPLO)
    personas_premium = [
        "PLANE_PEDAGOGICO", 
        "ESPECIALISTA_INCLUSAO", 
        "FORJA_AULA_TEORIA", 
        "FORJA_TRIADE_PEI", 
        "ARQUITETO_CIENTIFICO_V33",
        "ARQUITETO_RECUPERACAO_CIRURGICA"
    ]
    
    # 🚨 NOMECLATURA OFICIAL DA API
    modelo_alvo = "gemini-3.1-pro-preview" if persona_key in personas_premium else "gemini-3-flash-preview"
    
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else [],
        temperature=0.7 if persona_key in personas_premium else 1.0, 
        max_output_tokens=8192,
    )
    
    conteudo_prompt = []
    
    if url_drive and "drive.google.com" in url_drive:
        try:
            file_id = re.search(r"(?:id=|[dD]/)([\w-]+)", url_drive).group(1)
            download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
            
            response = requests.get(download_url, timeout=60) 
            
            if response.status_code == 200 and b"%PDF" in response.content[:10]:
                arquivo_temp = client.files.upload(
                    file=io.BytesIO(response.content),
                    config=types.UploadFileConfig(mime_type="application/pdf")
                )
                conteudo_prompt.append(types.Part.from_uri(
                    file_uri=arquivo_temp.uri, 
                    mime_type="application/pdf"
                ))
                st.toast(f"📖 Documento lido. Iniciando extração com {modelo_alvo}...", icon="✅")
            else:
                return "❌ ERRO DE SOBERANIA: O arquivo do Drive não pôde ser lido ou não é um PDF válido."
        except Exception as e:
            return f"❌ ERRO TÉCNICO NO DRIVE: {e}."

    conteudo_prompt.append(types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}"))

    try:
        res = client.models.generate_content(
            model=modelo_alvo, 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        if not res.text: return "⚠️ A IA não retornou dados."
        return res.text
    except Exception as e:
        # 🚨 FALLBACK DE SEGURANÇA: Se o 3.1 Pro ainda não estiver liberado na sua chave, usa o 2.5 Pro
        if "404" in str(e) and "3.1" in modelo_alvo:
            try:
                st.toast("⚠️ Gemini 3.1 Pro não liberado na chave. Acionando Fallback para 2.5 Pro...", icon="🔄")
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
    """Motor de Lote V202: Força a IA a responder em JSON estruturado de forma ultra-segura."""
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else [],
        temperature=0.7, 
        response_mime_type="application/json",
    )
    conteudo_prompt = [types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}")]
    try:
        # Usa o modelo flash padrão para lote por ser rápido e aceitar JSON mode perfeitamente
        res = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        if not res.text: return {"erro": "A IA retornou uma resposta vazia."}
        
        import json
        # Limpa eventuais blocos de código markdown que a IA ouse colocar por cima do JSON
        texto_limpo = res.text.strip()
        texto_limpo = re.sub(r'^```[a-zA-Z]*\n', '', texto_limpo, flags=re.IGNORECASE)
        texto_limpo = re.sub(r'\n```$', '', texto_limpo)
        
        return json.loads(texto_limpo)
    except Exception as e:
        return {"erro": str(e)}

def extrair_tag(texto, tag):
    if not texto: return ""
    tag_busca = tag.upper().strip()
    
    tags_mestras =[
        "SOSA_ID", "VALOR", "ORIENTACOES", "QUESTOES", "GABARITO_TEXTO", "GRADE_DE_CORRECAO", 
        "GABARITO", "RESPOSTAS_IA", "PEI", "GABARITO_PEI", "GRADE_DE_CORRECAO_PEI", "RESPOSTAS_PEI_IA", 
        "PROFESSOR", "ALUNO", "IMAGENS", "AULA_ALVO", "HABILIDADE_BNCC", "COMPETENCIAS_FOCO", 
        "COMPETENCIA_GERAL", "OBJETO_CONHECIMENTO", "CONTEUDOS_ESPECIFICOS", "OBJETIVOS_ENSINO",
        "JUSTIFICATIVA_PEDAGOGICA", "JUSTIFICATIVA_PHC", "RUBRICA_DE_MERITO", "CONTEXTO_INVESTIGATIVO", 
        "MISSÃO_DE_PESQUISA", "PASSO_A_PASSO", "PRODUTO_ESPERADO", "CONTEXTO_GLOCAL",
        "AULA_1", "AULA_2", "SABADO_LETIVO", "AVALIACAO_DE_MERITO", "ESTRATEGIA_DUA_PEI",
        "MAPA_DE_RECOMPOSICAO", "RESPOSTAS_PEDAGOGICAS", "BASE_DIDATICA",
        "MENSAGEM_CHAT", "CONTEUDO_ATUALIZADO", "SOCIAIS", "COMUNICATIVAS", "EMOCIONAIS", "FUNCIONAIS",
        "OBJETIVO", "ESTRATEGIA", "RECURSO", "DIAGNOSTICO_GERAL", "DIRETRIZES_CURRICULARES", "CHECKLIST",
        "NIVEL_1", "NIVEL_2", "NIVEL_3"
    ]
    
    parada =[t for t in tags_mestras if t != tag_busca]
    lista_parada = "|".join(parada)

    padrao_interno = rf"\[[^\]]*?{tag_busca}[^\]]*?[:\-]\s*(.*?)\]"
    match_int = re.search(padrao_interno, texto, re.IGNORECASE)
    if match_int:
        res_int = match_int.group(1).strip()
        if 0 < len(res_int) < 100: return res_int

    padrao_bloco = rf"\[[^\]]*?{tag_busca}[^\]]*?\]\s*[:\-]*\s*(.*?)(?=\s*\[[^\]]*?(?:{lista_parada})[^\]]*?\]|$)"
    match_bloco = re.search(padrao_bloco, texto, re.DOTALL | re.IGNORECASE)
    
    if match_bloco:
        res = match_bloco.group(1).strip()
        res = re.sub(r'^```[a-zA-Z]*\n', '', res, flags=re.IGNORECASE)
        res = re.sub(r'\n```$', '', res)
        res_limpo = re.sub(r'[░▒▓█]', '', res)
        res_limpo = re.sub(r'-{3,}', '', res_limpo)
        return res_limpo.strip()
    
    return ""

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
    base_ano = df_curriculo[df_curriculo['ANO'] == int(ano_sel)]
    lista_curriculo =[str(c).upper().strip() for c in base_ano['CONTEUDO_ESPECIFICO'].unique()]
    sincronizado = any(c in cont_plano for c in lista_curriculo)
    status_msg = "Sincronizado" if sincronizado else "Divergente"
    status_cor = "🟢" if sincronizado else "🟡"

    return {
        "modalidade": modalidade,
        "status": f"{status_cor} {status_msg}",
        "conteudo_literal": extrair_tag(plano_raw, "CONTEUDOS_ESPECIFICOS"),
        "objetivo_literal": extrair_tag(plano_raw, "OBJETIVOS_ENSINO")
    }

def analisar_gabarito_vision(imagem_bytes):
    try:
        prompt = (
            "Você é um perito em visão computacional de alta precisão. Analise a imagem do gabarito.\n"
            "A tabela possui as colunas: Q (Questão) e as alternativas (pode ser A, B, C, D, E para provas regulares ou apenas A, B, C para provas adaptadas PEI).\n"
            "MISSÃO DE RACIOCÍNIO:\n"
            "1. Localize a grade de respostas.\n"
            "2. Analise a densidade de preenchimento de cada círculo.\n"
            "3. Se houver uma marcação única e clara, retorne a letra correspondente.\n"
            "4. Se houver DUAS ou mais marcações (mesmo que uma esteja levemente riscada), retorne 'X' (Dupla Marcação).\n"
            "5. Se a linha estiver totalmente sem marcação, retorne '?' (Vazia).\n"
            "6. Ignore anotações manuais como 'PEI' ou 'Normal' feitas pelo professor.\n"
            "Retorne APENAS um JSON puro no formato: {'01': 'A', '02': 'C', ...}"
        )
        
        conteudo_prompt =[
            types.Part.from_bytes(data=imagem_bytes, mime_type="image/jpeg"),
            types.Part.from_text(text=prompt)
        ]
        
        res = client.models.generate_content(
            model="gemini-2.5-pro", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        
        import json
        return json.loads(res.text)
    except Exception as e:
        return {"erro": str(e)}
    
def gerar_prognostico_pedagogico(dados_stats, contexto_prova):
    try:
        prompt = (
            f"VOCÊ É O PERITO EM AVALIAÇÃO EDUCACIONAL SOSA.\n"
            f"Sua missão é realizar um diagnóstico no padrão dos Cadernos de Revisão do DF.\n\n"
            f"CONTEXTO DA PROVA:\n{contexto_prova}\n\n"
            f"DESEMPENHO DA TURMA:\n{dados_stats}\n\n"
            f"MISSÃO:\n"
            f"1. MAPEAMENTO DE DESCRITORES: Para cada questão, identifique o Descritor/Habilidade (Ex: D1, D5, EF06MA01).\n"
            f"2. ANÁLISE DE LACUNA: Explique o processo cognitivo que falhou.\n"
            f"3. PARÂMETROS TÉCNICOS: Gere uma lista curta de 'Tópicos de Recomposição'.\n\n"
            f"🚨 FORMATO DE SAÍDA (OBRIGATÓRIO):\n"
            f"[DIAGNOSTICO_VISUAL]\n(Escreva aqui o parecer técnico para o professor ler)\n\n"
            f"[PARAMETROS_SISTEMA]\n(Gere uma lista simples: Descritor: Nome da Habilidade | Nível de Alerta)\n"
            f"Linguagem formal. SEM MARKDOWN."
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
