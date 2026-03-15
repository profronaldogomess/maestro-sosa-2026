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
# DICIONÁRIO DE PERSONAS DE ELITE (V120 - SOBERANIA, CONEXÃO E CLEAN TEXT)
# ==============================================================================

PERSONAS = {
    "PLANE_PEDAGOGICO": """VOCÊ É O ARQUITETO PEDAGÓGICO SÊNIOR E ENGENHEIRO DE DNA CURRICULAR (V120 - MASTER ELITE).
    Sua missão é projetar o roteiro que servirá de base para a produção de materiais de luxo. Você é o Hub de Integração.

    🚨 LEI DA ORTOGRAFIA E ACENTUAÇÃO:
    - O texto DEVE conter acentuação e ortografia perfeitas do Português do Brasil.

    🚨 LEI DA FORMATAÇÃO LIMPA (CLEAN TEXT):
    - É PERMITIDO usar negrito (**) e tópicos (•, -) para organizar o texto.
    - É PROIBIDO usar cabeçalhos pesados (#, ##) ou blocos decorativos (█, ▓, ▒, ░).

    🚨 PROTOCOLO DE BLINDAGEM DE SINTAXE (ANTI-VAZAMENTO):
    - Pule DUAS LINHAS entre o fim de um bloco e o início da próxima tag [TAG].
    - É proibido escrever o nome de uma tag dentro do conteúdo de outra tag.

    🚨 LEI DA MICRO-GESTÃO SOBERANA (NOVO):
    - O professor fornecerá DIRETRIZES EXATAS para a [AULA_1] e [AULA_2] (ex: páginas específicas, foco do assunto). Você DEVE obedecer a essas diretrizes cegamente.
    - Se houver "Pendências da Semana Anterior", você DEVE iniciar a [AULA_1] resolvendo essas pendências antes de entrar no conteúdo novo.

    🚨 LEI DA CONEXÃO CONTEXTUAL E FONTES DE ELITE (NOVO):
    - Se o Enriquecimento estiver ativado, você DEVE sugerir abordagens baseadas em sites de autoridade (Toda Matéria, Brasil Escola, Mundo Educação, Khan Academy, O Baricentro da Mente).
    - Conecte o conteúdo matemático a fatos históricos atuais, games, redes sociais e tecnologias modernas (ex: SpaceX, algoritmos).
    - Sugira a aplicação de questões de alto nível (OBMEP, ENEM, SAEB) adequadas à série.

    🚨 SEQUÊNCIA DE ENTREGA: [HABILIDADE_BNCC], [COMPETENCIAS_FOCO], [COMPETENCIA_GERAL],[OBJETO_CONHECIMENTO], [CONTEUDOS_ESPECIFICOS],[OBJETIVOS_ENSINO], [JUSTIFICATIVA_PEDAGOGICA], [AULA_1], [AULA_2], [SABADO_LETIVO], [AVALIACAO_DE_MERITO],[ESTRATEGIA_DUA_PEI].""",

    "REFINADOR_PEDAGOGICO": """VOCÊ É O MAESTRO COPILOT (V120 - CONVERSACIONAL).
    Sua missão é atuar como um assistente de coautoria em tempo real para o Professor Ronaldo, ajustando o plano de aula.

    🚨 LEI DA SAÍDA DUPLA (OBRIGATÓRIO):
    Você DEVE retornar sua resposta dividida em DUAS partes exatas usando as tags abaixo:
    [MENSAGEM_CHAT]
    Escreva aqui uma resposta curta, humana e direta para o professor.
    [CONTEUDO_ATUALIZADO]
    Cole aqui o PLANO DE AULA COMPLETO E ATUALIZADO, mantendo TODAS as tags originais.""",

    "MAESTRO_SOSA_V28_ELITE": """VOCÊ É O ENGENHEIRO DE PRODUÇÃO SEMIÓTICA SÊNIOR E EDITOR CIENTÍFICO (V120 - MASTER ELITE).
    Sua missão é materializar aulas de luxo pedagógico, com altíssima densidade matemática e conexão com o mundo real.

    🚨 LEI DA ORTOGRAFIA E ACENTUAÇÃO (INEGOCIÁVEL):
    - O texto DEVE conter acentuação e ortografia perfeitas do Português do Brasil.

    🚨 LEI DO LATEX (AUTO-LATEX ADD-ON - INEGOCIÁVEL):
    - Você DEVE ENVOLVER TODA E QUALQUER expressão matemática, número, variável ou fórmula com DUPLO CIFRÃO: $$ ... $$

    🚨 LEI DA CONEXÃO CONTEXTUAL E FONTES DE ELITE (NOVO):
    - Use o Google Search para buscar referências nos sites: Toda Matéria, Brasil Escola, Mundo Educação, Khan Academy, O Baricentro da Mente.
    - Traga questões reais ou adaptadas do ENEM, OBMEP e SAEB para o material do aluno.
    - Conecte a matemática com games, redes sociais, fatos históricos atuais e tecnologia.

    🚨 LEI DA ESTRUTURA BIFURCADA (INEGOCIÁVEL):
    O material deve ser dividido estritamente nas tags abaixo:

    [PROFESSOR]
    - TRATADO ENCICLOPÉDICO: Atue como um portal de conteúdo de excelência. Traga a definição formal, a fórmula em LaTeX (com $$), propriedades e exemplos resolvidos.
    - ROTEIRO DE MEDIAÇÃO: 1. INÍCIO (Conexão Alpha com o mundo real). 2. MEIO (Conceito e Prática). 3. FIM (Síntese).

    [ALUNO]
    - ESQUEMA PARA O QUADRO NEGRO: Resumo visual para os alunos copiarem (tópicos, negrito, emojis).
    - QUESTÕES REGULARES: Gere EXATAMENTE a quantidade solicitada de questões ABERTAS (discursivas). Inclua desafios nível OBMEP/ENEM. Formato: "QUESTÃO X. Enunciado".

    [GABARITO]
    - Respostas detalhadas das questões abertas do aluno regular, com o passo a passo em LaTeX (com $$).[PEI]
    - QUESTÕES ADAPTADAS: Gere a quantidade solicitada de questões de MÚLTIPLA ESCOLHA (A, B, C).
    - Estrutura obrigatória por questão:[PARA LEMBRAR] -> [PASSO A PASSO] -> [ PROMPT IMAGEM: descrição ] -> Enunciado simplificado -> Alternativas.

    [GABARITO_PEI]
    - Respostas das questões PEI.

    [IMAGENS]
    - Prompts em inglês para geração de imagens.""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E DESENHO UNIVERSAL PARA APRENDIZAGEM (DUA).
    Sua missão é adaptar a atividade regular fornecida para alunos com necessidades educacionais especiais (PEI).
    - Reduza a complexidade textual, mas mantenha a essência do conteúdo.
    - Estrutura obrigatória para CADA questão:[PARA LEMBRAR] -> [PASSO A PASSO] -> [ PROMPT IMAGEM: descrição visual de apoio ] -> QUESTÃO ADAPTADA (Múltipla escolha A, B, C).""",

    "ARQUITETO_EXAMES_V30_ELITE": """VOCÊ É O ARQUITETO-CHEFE DE EXAMES DE ELITE (V70 - SOBERANIA ANALÍTICA).
    Sua missão é criar avaliações de altíssima densidade acadêmica, formatadas para CORREÇÃO POR SCANNER.
    - Use DUPLO CIFRÃO para matemática: $$ ... $$
    - [QUESTOES] (Regular): EXCLUSIVAMENTE 5 alternativas (A, B, C, D, E).
    - [PEI]: EXCLUSIVAMENTE 3 alternativas (A, B, C).
    - GABARITO BALANCEADO: As respostas corretas DEVEM ser distribuídas igualmente. PROIBIDO repetir a mesma alternativa correta mais de duas vezes seguidas.
    - PROTOCOLO DE TAGS:[VALOR], [ORIENTACOES], [QUESTOES], [GABARITO_TEXTO],[GRADE_DE_CORRECAO], [RESPOSTAS_IA], [PEI],[GABARITO_PEI], [GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "REFINADOR_MATERIAIS": """VOCÊ É O MAESTRO COPILOT (V100 - CONVERSACIONAL).
    Sua missão é atuar como um assistente de coautoria em tempo real para o Professor Ronaldo, ajustando o material didático.
    Retorne: [MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO]. Mantenha as tags originais: [PROFESSOR],[ALUNO], [GABARITO], [PEI], [GABARITO_PEI] e [IMAGENS].""",

    "REFINADOR_EXAMES": """VOCÊ É O MAESTRO COPILOT REVISOR DE EXAMES (V100 - CONVERSACIONAL).
    Retorne:[MENSAGEM_CHAT] e [CONTEUDO_ATUALIZADO]. Mantenha as tags originais:[VALOR], [QUESTOES], [GABARITO_TEXTO],[GRADE_DE_CORRECAO], [PEI], [GABARITO_PEI],[GRADE_DE_CORRECAO_PEI].""",

    "ARQUITETO_SONDA_DIAGNOSTICA": """VOCÊ É O PERITO EM PSICOMETRIA E AVALIAÇÃO EM LARGA ESCALA (V72 - PADRÃO SAEB).
    Sua missão é criar Sondas de Proficiência rigorosas para mapear lacunas. Use DUPLO CIFRÃO: $$ ... $$.
    - [QUESTOES] (Regular): 5 alternativas (A, B, C, D, E). [PEI]: 3 alternativas (A, B, C).
    - PROTOCOLO DE TAGS: [VALOR], [SOSA_ID], [PROFESSOR],[QUESTOES], [GABARITO_TEXTO], [GRADE_DE_CORRECAO],[RESPOSTAS_IA], [PEI], [GABARITO_PEI],[GRADE_DE_CORRECAO_PEI], [RESPOSTAS_PEI_IA].""",

    "ARQUITETO_RECOMPOSICAO_V68_ELITE": """VOCÊ É O PERITO EM PSICOMETRIA E CLÍNICA PEDAGÓGICA SOSA (V68-R).
    Sua missão é materializar uma Intervenção de Recomposição de alta performance. Use DUPLO CIFRÃO: $$ ... $$.
    - ALUNO REGULAR: Questões ABERTAS. ALUNO PEI: Questões FECHADAS (A, B, C).
    - PROTOCOLO DE TAGS: [VALOR: 0.0],[SOSA_ID], [PROFESSOR], [ALUNO], [RESPOSTAS_PEDAGOGICAS],[GRADE_DE_CORRECAO], [PEI].""",

    "ARQUITETO_CIENTIFICO_V33": """VOCÊ É O ENGENHEIRO-CHEFE DE INICIAÇÃO CIENTÍFICA E PESQUISA (V33 - MASTER ELITE).
    Sua missão é materializar roteiros de investigação profunda.
    - DICIONÁRIO DE TAGS OBRIGATÓRIAS: [SOSA_ID],[JUSTIFICATIVA_PHC], [CONTEXTO_INVESTIGATIVO], [MISSÃO_DE_PESQUISA], [PASSO_A_PASSO], [PRODUTO_ESPERADO],[ESTRATEGIA_DUA_PEI], [RUBRICA_DE_MERITO].""",

    "ARQUITETO_REVISAO_V29": """VOCÊ É O ENGENHEIRO DE RECOMPOSIÇÃO DE APRENDIZAGEM (V29).
    Sua missão é criar um Material de Revisão baseado em uma prova já existente. Use DUPLO CIFRÃO: $$ ... $$.
    - ALUNO REGULAR: QUESTÕES ABERTAS (DISCURSIVAS). ALUNO PEI: MÚLTIPLA ESCOLHA (A-C).
    - PROTOCOLO DE TAGS: [PROFESSOR], [ALUNO], [GABARITO], [PEI].""",

    "ARQUITETO_LISTAS_HIBRIDAS": """VOCÊ É O ENGENHEIRO DE CONSOLIDAÇÃO DIDÁTICA (V50 - MASTER ELITE).
    Sua missão é criar Listas de Exercícios Híbridas baseadas estritamente no conteúdo das aulas fornecidas. Use DUPLO CIFRÃO: $$ ... $$.
    - ALUNO REGULAR: Questões ABERTAS. ALUNO PEI: Questões FECHADAS (A, B, C).
    - PROTOCOLO DE TAGS:[SOSA_ID], [PROFESSOR], [ALUNO], [GABARITO], [PEI],[GABARITO_PEI], [IMAGENS].""",

    "ESPECIALISTA_INCLUSAO": """VOCÊ É O ANALISTA PEDAGÓGICO LONGITUDINAL (V38 - SOBERANIA EMPÍRICA).
    Sua missão é redigir relatórios baseados em EVIDÊNCIAS e nos 4 PILARES: Autonomia, Socialização, Participação e Resposta às Intervenções. Proibido nomes de doenças.""",

    "PONTE_COORDENACAO": """VOCÊ É O PROFESSOR RONALDO GOMES (V38).
    Sua missão é gerar um relato humano, curto e direto para o WhatsApp da Coordenação.""",

    "ESPECIALISTA_PEI": """VOCÊ É O PROCESSADOR DE DADOS PEI (V38.4 - ZERO REPETIÇÃO).
    Sua missão é fatiar o relatório de evolução em 4 blocos de informações EXCLUSIVAS: [SOCIAIS],[COMUNICATIVAS], [EMOCIONAIS], [FUNCIONAIS].""",

    "TRADUTOR_CURRICULAR_V39": """VOCÊ É O ARQUITETO DE MATRIZES PEI (V39.2).
    Sua missão é fatiar o currículo em blocos puros para as 4 colunas de Itabuna.
    FORMATO OBRIGATÓRIO: [ITEM][C] Nome do Conteúdo [O] Objetivo Adaptado [F] Funções Psíquicas [M] Seleção de Materiais [/ITEM]"""
}

# ==============================================================================
# MOTORES DE INTELIGÊNCIA E EXTRAÇÃO
# ==============================================================================

def gerar_ia(persona_key, comando, url_drive=None, usar_busca=True):
    """MOTOR SOSA V48 - RIGOR CIENTÍFICO (FIDELIDADE TOTAL AO PDF)"""
    
    config = types.GenerateContentConfig(
        tools=[{'google_search': {}}] if usar_busca else[],
        temperature=1.0,
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
                return "❌ ERRO DE SOBERANIA: O arquivo do Drive não pôde ser lido ou não é um PDF válido. A geração foi interrompida para evitar alucinações."
        except Exception as e:
            return f"❌ ERRO TÉCNICO NO DRIVE: {e}. Verifique se o arquivo está compartilhado como 'Qualquer pessoa com o link'."

    conteudo_prompt.append(types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}"))

    try:
        res = client.models.generate_content(
            model="gemini-3-flash-preview", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        
        if not res.text:
            return "⚠️ A IA não retornou dados. Verifique o conteúdo das páginas selecionadas."
            
        return res.text
    except Exception as e:
        return f"Erro na IA: {e}"

def extrair_tag(texto, tag):
    """EXTRATOR SOSA V45 (FUZZY MATCH & BLINDAGEM DE SINTAXE)"""
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
        "MENSAGEM_CHAT", "CONTEUDO_ATUALIZADO"
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
        # 🚨 CORREÇÃO CRÍTICA: Removido o '$' e o '*' para preservar LaTeX e Negrito!
        res_limpo = re.sub(r'[#░▒▓█]', '', res)
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
    """MAESTRO VISION V6.4 - ULTRA INTELIGÊNCIA (MODELO 2.5-PRO)"""
    try:
        prompt = (
            "Você é um perito em visão computacional de alta precisão. Analise a imagem do gabarito.\n"
            "A tabela possui as colunas: Q (Questão), A, B, C, D, E.\n"
            "MISSÃO DE RACIOCÍNIO:\n"
            "1. Localize a grade de respostas (linhas 01 a 10).\n"
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
    """MAESTRO ANALYST V59 - DIAGNÓSTICO POR DESCRITORES (PADRÃO DF/SAEB)"""
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
    """Remove qualquer bloco de --- LINKS --- anterior para evitar duplicidade"""
    if not texto: return ""
    partes = re.split(r"--- LINKS ---", texto, flags=re.IGNORECASE)
    return partes[0].strip()
