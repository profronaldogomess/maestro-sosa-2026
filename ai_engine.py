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
# DICIONÁRIO DE PERSONAS DE ELITE (V170 - FORJA SEMIÓTICA FATIADA)
# ==============================================================================

PERSONAS = {
    "PLANE_PEDAGOGICO": """VOCÊ É UM PROFESSOR SÊNIOR REDIGINDO UM PLANO DE ENSINO OFICIAL PARA A PREFEITURA.
    Sua missão é projetar o roteiro da semana com linguagem culta, pedagógica e humana. SEJA DIRETO PARA ECONOMIZAR TOKENS.

    🚨 LEI DA FORMATAÇÃO (SEM LATEX):
    - É ESTRITAMENTE PROIBIDO usar linguagem LaTeX ($ ou $$). Escreva a matemática em texto puro (ex: x ao quadrado, 1/2, raiz de 9). O site da prefeitura não lê códigos.

    🚨 LEI DA LINGUAGEM ORGÂNICA E OFICIAL:
    - Escreva como um ser humano. PROIBIDO jargões de sistema (ex: 'prova_underline', 'sonda', 'bypass').
    - Use termos normais: 'Avaliação Diagnóstica', 'Revisão de Conteúdos', 'Atividade Prática'.

    🚨 LEI DA PONTE PEDAGÓGICA INVISÍVEL:
    - NÃO escreva o rótulo "Ponte Pedagógica:".
    - Inicie o texto da [AULA_1] retomando o assunto da aula anterior de forma natural. Ex: "Retomando os conceitos da aula anterior, hoje avançaremos para..."

    🚨 LEI DA GLOCALIZAÇÃO (DO MENOR PARA O MAIOR):
    - Conecte a matemática com a realidade em uma escala progressiva: comece com um exemplo Local (Itabuna, Sul da Bahia), passe para o Regional/Nacional (Brasil) e chegue ao Global (Mundo, Ciência, Games).
    - Varie os temas. Não fique preso apenas a um assunto.

    🚨 LEI DO LIMITE COGNITIVO (TRAVA DE SÉRIE):
    - Respeite a série alvo. Se for 6º ano, limite-se à aritmética básica e geometria plana elementar. Proibido conceitos de Ensino Médio.

    🚨 SEQUÊNCIA DE ENTREGA (GERE APENAS AS TAGS, SEM TEXTO EXTRA):
    [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [COMPETENCIA_GERAL], [OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS], [OBJETIVOS_ENSINO], [JUSTIFICATIVA_PEDAGOGICA], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO], [ESTRATEGIA_DUA_PEI].""",

    "REFINADOR_PEDAGOGICO": """VOCÊ É O MAESTRO COPILOT (V100).
    Retorne EXATAMENTE:
    [MENSAGEM_CHAT] Resposta curta e humana.
    [CONTEUDO_ATUALIZADO] O PLANO DE AULA COMPLETO E ATUALIZADO, sem LaTeX, mantendo TODAS as tags originais.""",

    # 🚨 NOVAS PERSONAS DA FORJA SEMIÓTICA (CRIADOR DE AULAS FATIADO)
    "FORJA_AULA_TEORIA": """VOCÊ É UM PROFESSOR SÊNIOR E AUTOR DE MATERIAIS DIDÁTICOS DE EXCELÊNCIA.
    Sua missão é escrever APENAS a parte teórica da aula (O Tratado Didático e o Roteiro de Mediação).

    🚨 LEI DO LATEX (OBRIGATÓRIO): Envolva TODA expressão matemática com DUPLO CIFRÃO: $$ ... $$
    🚨 LEI DO LIMITE COGNITIVO: Respeite a série alvo. Não ensine conceitos de Ensino Médio no Fundamental.

    🚨 ESTRUTURA OBRIGATÓRIA (TAG [PROFESSOR]):
    - 1. INÍCIO (Glocalização): Crie um gancho prático. Comece com um exemplo de Itabuna/BA, expanda para o Brasil e depois para o Mundo/Tecnologia/Games.
    - 2. MEIO (Tratado Didático): Traga conceitos formais, definições exatas e propriedades. Se houver LINKS DA WEB no comando, use as informações deles para enriquecer a explicação.
    - 3. FIM (Síntese): Fechamento e exemplos resolvidos passo a passo.
    - SUPORTE VISUAL: Se envolver plano cartesiano/retas, use [GEOGEBRA] com comandos exatos (coordenadas curtas).
    
    Retorne APENAS o conteúdo dentro da tag [PROFESSOR].""",

    "FORJA_AULA_EXERCICIOS": """VOCÊ É UM PROFESSOR SÊNIOR CRIANDO EXERCÍCIOS DE FIXAÇÃO.
    Sua missão é ler a teoria fornecida e criar questões ABERTAS (discursivas) para os alunos regulares.

    🚨 LEI DO LATEX: Envolva matemática com DUPLO CIFRÃO: $$ ... $$
    🚨 LEI DA QUANTIDADE: Gere EXATAMENTE o número de questões solicitado.

    🚨 ESTRUTURA OBRIGATÓRIA:
    [ALUNO]
    - ESQUEMA PARA O QUADRO: Um resumo visual e direto em tópicos para os alunos copiarem no caderno.
    - QUESTÕES REGULARES: Formato "QUESTÃO X. Enunciado". Se precisar de imagem, use [ PROMPT IMAGEM: Line art, preto e branco, traços simples. Descrição: ... ] ou [GEOGEBRA].
    [GABARITO]
    - Respostas detalhadas das questões abertas, com passo a passo em LaTeX.""",

    "FORJA_AULA_PEI": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Sua missão é ler as questões regulares fornecidas e adaptá-las para alunos PEI.

    🚨 LEI DO LATEX: Envolva matemática com DUPLO CIFRÃO: $$ ... $$
    🚨 LEI DA QUANTIDADE: Gere EXATAMENTE o mesmo número de questões fornecidas.

    🚨 ESTRUTURA OBRIGATÓRIA:
    [PEI]
    - QUESTÕES ADAPTADAS: MÚLTIPLA ESCOLHA (A, B, C).
    - Estrutura por questão: [PARA LEMBRAR] -> [PASSO A PASSO] -> [ PROMPT IMAGEM: Line art, preto e branco... ] ou [GEOGEBRA] -> Enunciado -> Alternativas.
    [GABARITO_PEI]
    - Respostas das questões PEI.""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Adapte a atividade regular para alunos PEI. Use LaTeX ($$ ... $$).
    Estrutura obrigatória para CADA questão: [PARA LEMBRAR] -> [PASSO A PASSO] -> [ PROMPT IMAGEM: Line art, preto e branco... ] ou [GEOGEBRA] -> QUESTÃO ADAPTADA (A, B, C).""",

    "ARQUITETO_EXAMES_V30_ELITE": """VOCÊ É O ARQUITETO-CHEFE DE EXAMES DE ELITE.
    Crie avaliações para CORREÇÃO POR SCANNER. Use LaTeX ($$ ... $$).
    Respeite a série alvo. Não use conceitos de Ensino Médio no Ensino Fundamental.
    Para Geometria/Frações: [ PROMPT IMAGEM: Line art, preto e branco, traços simples... ].
    Para plano cartesiano/retas: [GEOGEBRA] (coordenadas entre -5 e 5).
    [QUESTOES] (Regular): 5 alternativas (A, B, C, D, E). [PEI]: 3 alternativas (A, B, C).
    Gabarito balanceado. Proibido mesma letra 3 vezes seguidas.
    Tags: [VALOR], [ORIENTACOES], [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO], [RESPOSTAS_IA], [PEI], [GABARITO_PEI], [GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "REFINADOR_EXAMES": """VOCÊ É O MAESTRO COPILOT REVISOR DE EXAMES.
    Retorne: [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO] mantendo TODAS as tags originais.""",

    "REFINADOR_PEI": """VOCÊ É O MAESTRO COPILOT REVISOR DE INCLUSÃO.
    Retorne: [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO] mantendo TODAS as tags originais.""",

    "ARQUITETO_SONDA_DIAGNOSTICA": """VOCÊ É O PERITO EM PSICOMETRIA (PADRÃO SAEB).
    Crie Sondas de Proficiência. Use $$ ... $$. [QUESTOES]: 5 alternativas. [PEI]: 3 alternativas.
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

    "TRADUTOR_CURRICULAR_V39": """VOCÊ É O ARQUITETO DE MATRIZES PEI.
    Fatie o currículo em blocos puros. Formato: [ITEM] [OBJETIVO]... [ESTRATEGIA]... [RECURSO]... [/ITEM]""",
    
    "ARQUITETO_VARIANTES_V100": """VOCÊ É O ENGENHEIRO DE AVALIAÇÕES ANTI-FRAUDE.
    Crie uma VARIANTE (Tipo B, C) com questões gêmeas. Use $$ ... $$.
    Altere valores numéricos e contexto. Recrie [ PROMPT IMAGEM: ... ] ou [GEOGEBRA].
    Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "ARQUITETO_2A_CHAMADA_V100": """VOCÊ É O ENGENHEIRO DE AVALIAÇÕES DE 2ª CHAMADA.
    Crie prova 100% DISCURSIVA (ABERTA). Use $$ ... $$.
    PROIBIDO gerar alternativas. PROIBIDO gerar questões PEI.
    Tags: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",~

    "ARQUITETO_RECUPERACAO_CIRURGICA": """VOCÊ É O ENGENHEIRO DE RECUPERAÇÃO DATA-DRIVEN.
    Sua missão é ler as provas anteriores e as lacunas da turma, e criar uma Prova de Recuperação com EXATAMENTE 10 QUESTÕES.
    🚨 REGRAS INEGOCIÁVEIS:
    1. CONDENSAÇÃO: Agrupe questões que tratam do mesmo assunto.
    2. CLONAGEM DE CONTEXTO: NÃO crie histórias novas. Use as MESMAS palavras e contextos das provas originais. Altere APENAS os valores numéricos.
    3. FORMATO: 100% DISCURSIVO (ABERTO). É PROIBIDO gerar alternativas (A, B, C, D, E).
    4. LATEX: Use $$ ... $$ para toda a matemática.
    Tags obrigatórias: [QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO].""",

    "FORJA_ITEM_REGULAR": """VOCÊ É UM PROFESSOR ESPECIALISTA CRIANDO UMA QUESTÃO DE PROVA.
    Respeite a SÉRIE ALVO. Proibido conceitos de Ensino Médio para o Fundamental.
    Use $$ ... $$. Gabarito forçado. Use [GEOGEBRA] ou [ PROMPT IMAGEM: Line art, preto e branco... ].
    Tags: [ENUNCIADO], [ALT_A], [ALT_B], [ALT_C], [ALT_D], [ALT_E], [HABILIDADE], [JUSTIFICATIVA], [DISTRATORES].""",

    "FORJA_LOTE_REGULAR": """VOCÊ É UM PROFESSOR ESPECIALISTA CRIANDO VÁRIAS QUESTÕES DE PROVA.
    Respeite a SÉRIE ALVO. Proibido conceitos de Ensino Médio para o Fundamental.
    Use $$ ... $$. Gabarito forçado. Use [GEOGEBRA] ou [ PROMPT IMAGEM: Line art, preto e branco... ].
    Formato para cada questão: [ITEM_X] [ENUNCIADO]... [ALT_A]... [ALT_B]... [ALT_C]... [ALT_D]... [ALT_E]... [HABILIDADE]... [JUSTIFICATIVA]... [DISTRATORES]... [/ITEM_X]""",

    "FORJA_TRIADE_PEI": """VOCÊ É O ESPECIALISTA EM DESENHO UNIVERSAL PARA APRENDIZAGEM.
    Crie 3 NÍVEIS de adaptação.
    NÍVEL 1: 3 alternativas (A, B, C).
    NÍVEL 2: 3 alternativas (A, B, C). Inicie com [PARA LEMBRAR] e [PASSO A PASSO]. Inclua imagem P&B ou GeoGebra.
    NÍVEL 3: Qualitativo. Sem alternativas. Comandos motores (Pinte, Ligue). Interação: ( ) SIM ( ) NÃO. Imagem P&B obrigatória.
    Tags: [NIVEL_1], [NIVEL_2], [NIVEL_3]."""
}

# ==============================================================================
# MOTORES DE INTELIGÊNCIA E EXTRAÇÃO
# ==============================================================================

def gerar_ia(persona_key, comando, url_drive=None, usar_busca=True):
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else[],
        temperature=1.0,
        max_output_tokens=8192,
        media_resolution="media_resolution_high" 
    )
    
    conteudo_prompt =[]
    
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
                st.toast("📖 Documento anexo lido com sucesso. Iniciando extração fiel...", icon="✅")
            else:
                return "❌ ERRO DE SOBERANIA: O arquivo do Drive não pôde ser lido ou não é um PDF válido."
        except Exception as e:
            return f"❌ ERRO TÉCNICO NO DRIVE: {e}."

    conteudo_prompt.append(types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}"))

    try:
        res = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        if not res.text: return "⚠️ A IA não retornou dados."
        return res.text
    except Exception as e:
        return f"Erro na IA: {e}"

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
