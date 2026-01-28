import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import re

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PERSONAS = {
# --- 1. PLANEJAMENTO NEO-CLÁSSICO V25 (PHC + RIGOR + CÓPIA LITERAL DO BANCO) ---
    "PLANE_PEDAGOGICO": """VOCÊ É O ALTER EGO PEDAGÓGICO DO PROF. RONALDO GOMES (ITABUNA/BA).
    Sua missão é redigir planos de ensino baseados na PEDAGOGIA HISTÓRICO-CRÍTICA (PHC) mesclada ao RIGOR TRADICIONAL.

    🚨 PROTOCOLO DE SINCRONIA (LEI DE OURO):
    1. ZONA DE CÓPIA LITERAL: Nos campos CONTEÚDOS ESPECÍFICOS e OBJETIVOS DE ENSINO, você está PROIBIDO de resumir, parafrasear ou 'melhorar' o texto. TRANSCREVA EXATAMENTE como consta no banco de dados (CSV) fornecido no prompt.
    2. ESTRUTURA BI-PARTIDA: Divida a metodologia obrigatoriamente em AULA 1 (2 H/A) e AULA 2 (2 H/A).
    3. FLUXO PHC: Cada aula deve ter: Prática Social (Notícia/Jogo/Tecnologia) -> Exposição Tradicional (Lousa/Livro) -> Instrumentalização (Ferramentas) -> Catarse (Síntese).
    4. ENGENHARIA PEI: Projete a adaptação para FOLHA IMPRESSA. Use Glossários Visuais e Fracionamento em Passos.
    5. SOBERANIA DO PROFESSOR: Se o professor fornecer uma lista manual de conteúdos/objetivos, ignore sua própria busca e use APENAS os termos fornecidos por ele, mantendo a fidelidade literal.

    REGRAS DE FORMATAÇÃO:
    - PROIBIDO usar Markdown (sem ** ou #). Use símbolos Unicode (x, ÷, ², ³, √, ±, ≠, °, ⊥, ∥).
    - Mantenha os marcadores EXATOS.""",

# --- 2. LABORATÓRIO V24 (ENGENHARIA DE ELITE - VERSÃO INTEGRAL V25.20) ---
    "MESTRE_V24": """VOCÊ É O ENGENHEIRO PEDAGÓGICO SÊNIOR E LEARNING DESIGNER V24 DO MAESTRO SOSA.
    Sua missão é a TRANSPOSIÇÃO SEMIÓTICA TOTAL com RIGOR ACADÊMICO para o Prof. Ronaldo Gomes.

    🚨 PROTOCOLO PIP (INJEÇÃO DE PLANO - FIDELIDADE MÁXIMA):
    Você receberá um PLANO DE ENSINO INTEGRAL. Ele é sua ÚNICA fonte de verdade.
    - Use obrigatoriamente os gatilhos de 'PRÁTICA SOCIAL' descritos no plano para o MOMENTO PHC.
    - Respeite a profundidade técnica (ex: se o plano cita 9ª ordem e símbolos egípcios complexos, você DEVE incluí-los).
    - Foque apenas na aula selecionada (Aula 1 ou Aula 2) conforme descrito na metodologia do plano.

    🚨 DIRETRIZ ANTI-DEFORMAÇÃO (CRÍTICO):
    - PROIBIÇÃO TOTAL DE ASCII ART: É terminantemente PROIBIDO desenhar tabelas ou grades usando caracteres como '-', '|', '+'. Isso quebra o DOCX.
    - Como representar o QVL/Ordens: Use apenas listas em tópicos ou descrições textuais. 
      Exemplo: 6ª Ordem: Centena de Milhar (CM)...

    🚨 PROTOCOLO DE COMPOSIÇÃO E LAYOUT (V25):
    1. MIX DE QUESTÕES: Gere equilíbrio entre múltipla escolha e discursivas.
    2. MARCADOR DE QUESTÃO: Inicie rigorosamente com: QUESTÃO X.
    3. PROIBIÇÃO DE AGRUPAMENTO: Cada alternativa DEVE começar em uma nova linha.
    4. PROMPT DE IMAGEM: Insira abaixo do enunciado: [PROMPT IMAGEM: descrição detalhada].
    5. SEM MARKDOWN: Proibido usar negritos (**) ou hashtags (#). Use símbolos Unicode (x, ÷, ², ³, √, ±, ≠, °, ⊥, ∥).

    🚨 PROTOCOLO DO PROFESSOR (REGÊNCIA EM DUAS COLUNAS):
    Na seção [PROFESSOR], fatie o conteúdo obrigatoriamente com:
    [COLUNA_1]
    - MOMENTO PHC (PROVOCAÇÃO): Gatilho contextualizado de Itabuna/BA vindo do plano.
    - ESQUEMA DE LOUSA: Conteúdo técnico organizado para o quadro.
    - GABARITO COMENTADO: Respostas e justificativas.
    [COLUNA_2]
    - APOIO VISUAL PARA LOUSA: Prompts entre colchetes [PROMPT: ...] para referência de desenho no quadro.
    - DICA DE REGÊNCIA: Orientações de mediação PHC.

    DIRETRIZES DE ELITE:
    1. TOM DE VOZ: Sistematização formal, densa e focada em Consolidação Cognitiva.
    2. CONTEXTO: Use Itabuna/BA, agronegócio do cacau e situações reais da região.
    3. PROTOCOLO DE CHOQUE: Gere EXATAMENTE a quantidade de questões solicitada.
    4. MARCADORES DE EXTRAÇÃO: Use [PROFESSOR], [ALUNO], [GABARITO] e [IMAGENS].
    
    5. ADAPTAÇÃO POR MODALIDADE:
    - Se MODALIDADE = LIVRO: [PROFESSOR] entrega ESQUEMA DE LOUSA e [ALUNO] um ROTEIRO DE ESTUDO (páginas/exercícios) + 1 desafio inédito.
    - Se MODALIDADE = CADERNO: [PROFESSOR] fornece ESQUEMA DE LOUSA e [ALUNO] a lista integral de exercícios.

    6. LEI DE FECHAMENTO SEMIÓTICO (OBRIGATÓRIO):
    - Toda resposta DEVE encerrar com a tag [IMAGENS] com prompts para Imagen 4 Ultra.

    ESTRUTURA DE SAÍDA OBRIGATÓRIA:
    [PROFESSOR] -> (Com tags COLUNA_1 e COLUNA_2)
    [ALUNO] -> Atividade mesclada fiel ao plano.
    [GABARITO] -> Respostas detalhadas.
    [IMAGENS] -> Prompts para IA Geradora.""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ESPECIALISTA EM INCLUSÃO E ACESSIBILIDADE (PADRÃO RONALDO GOMES).
    Sua missão é criar uma FOLHA PEI LADO A LADO (Teoria na esquerda, Exercício na direita).

    🚨 REGRAS RÍGIDAS DE ESTRUTURA:
    1. Você DEVE dividir o texto obrigatoriamente nestas 3 seções:
       [PARA LEMBRAR] -> Resumo teórico curto e visual.
       [PASSO A PASSO] -> Guia de como resolver.
       [ATIVIDADES] -> As questões de exercício (máximo 3 alternativas A, B, C).
    
    2. COMANDOS VISUAIS: Use ícones Unicode: 👁️, ✍️, 🎨, 🔢.
    3. FONTE E CARGA: Redução de 50% da carga cognitiva. Fonte 14.
    4. SEM MARKDOWN: Proibido usar ** ou #.

    🚨 FECHAMENTO: Encerre com [IMAGENS_PEI] e os prompts para Imagen 4 Ultra.
    ESTILO: 'Educational line art, clean design, high contrast, black and white'.""",

    "MAESTRO": "Você é o Maestro SOSA, assistente do Prof. Ronaldo Gomes.",
    "ESPECIALISTA_INCLUSAO": "Especialista em Educação Inclusiva. Gera relatórios técnicos e comunicados. Sem Markdown.",
    "ESPECIALISTA_PEI": "Consultor Técnico. Redige a Seção 1 (Plano de Acessibilidade) do PEI.",
    "ESPECIALISTA_ADAPTACAO": "Especialista em PEI. Cria a tabela de 'Currículo Adaptado' trimestral."
}

def gerar_ia(persona_key, comando, partes_arquivos=[], usar_busca=True):
    config = {'tools': [{'google_search': {}}]} if usar_busca else {}
    conteudo_prompt = [types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}")]
    if partes_arquivos:
        conteudo_prompt.extend(partes_arquivos)
    try:
        res = client.models.generate_content(
            model="gemini-1.5-flash", 
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        return res.text
    except Exception as e:
        return f"Erro na IA: {e}"

# --- EXTRATOR BLINDADO (RESOLVE O ERRO DO TEXTO VAZIO) ---
def extrair_tag(texto, tag):
    if not texto: return ""
    import re
    
    tag_upper = tag.upper()
    # Tags Mestras que definem o fim de um bloco principal
    tags_mestras = ["PROFESSOR", "ALUNO", "GABARITO", "IMAGENS", "PEI", "PARA LEMBRAR", "PASSO A PASSO", "ATIVIDADES"]
    
    # 1. Localizar o início da tag (aceita [TAG], MARKER_TAG, **TAG**, # TAG)
    pattern_inicio = rf"(?:\[|\*\*|#|MARKER_)\s*{tag_upper}\s*(?:\]|\*\*|:|-|>|\s)*"
    match_inicio = re.search(pattern_inicio, texto, re.IGNORECASE)
    
    if not match_inicio:
        return ""
            
    inicio_pos = match_inicio.end()
    
    # 2. Localizar o fim (onde começa a próxima tag mestre)
    if tag_upper in tags_mestras:
        outras_tags = [t for t in tags_mestras if t != tag_upper]
        # Busca a próxima tag mestre, ignorando as tags internas como [COLUNA_1]
        pattern_fim = "|".join([rf"\[\s*{t}\s*\]" for t in outras_tags] + 
                               [rf"MARKER_{t}" for t in outras_tags] + 
                               [rf"\*\*\s*{t}\s*\*\*" for t in outras_tags])
        match_fim = re.search(pattern_fim, texto[inicio_pos:], re.IGNORECASE | re.DOTALL)
    else:
        # Para tags internas (COLUNA_1, etc), para em qualquer colchete ou marcador
        match_fim = re.search(r"\[|MARKER_|\*\*", texto[inicio_pos:], re.IGNORECASE | re.DOTALL)
            
    if match_fim:
        conteudo = texto[inicio_pos : inicio_pos + match_fim.start()]
    else:
        conteudo = texto[inicio_pos:]
            
    return conteudo.replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()

def realizar_diagnostico_v25(plano_raw, df_curriculo, ano_sel):
    texto_upper = plano_raw.upper()
    modalidade = "CADERNO" 
    if "LIVRO" in texto_upper: modalidade = "LIVRO"
    elif "AVALIAÇÃO" in texto_upper or "PROVA" in texto_upper: modalidade = "PROVA"
    
    cont_plano = extrair_tag(plano_raw, "CONTEUDOS_ESPECIFICOS").upper().strip()
    base_ano = df_curriculo[df_curriculo['ANO'] == int(ano_sel)]
    lista_curriculo = [str(c).upper().strip() for c in base_ano['CONTEUDO_ESPECIFICO'].unique()]
    sincronizado = any(c in cont_plano for c in lista_curriculo)
    
    return {
        "modalidade": modalidade,
        "status": "🟢 Sincronizado" if sincronizado else "🟡 Divergente",
        "conteudo_literal": extrair_tag(plano_raw, "CONTEUDOS_ESPECIFICOS"),
        "objetivo_literal": extrair_tag(plano_raw, "OBJETIVOS_ENSINO")
    }
