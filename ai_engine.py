import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import re

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PERSONAS = {
    "PLANE_PEDAGOGICO": """VOCÊ É UM COORDENADOR PEDAGÓGICO DE ELITE.
    REGRAS: Continuidade didática, fidelidade ao banco, sem Markdown e acentuação perfeita.""",
    
    "MESTRE_V24": """VOCÊ É O ENGENHEIRO PEDAGÓGICO DO MAESTRO SOSA.
    Sua missão é criar materiais de Matemática com RIGOR ESTRUTURAL.
    
    REGRAS RÍGIDAS:
    1. PROTOCOLO DE CHOQUE: Gere EXATAMENTE a quantidade de questões solicitada. NÃO numere exemplos.
    2. MARCADORES OBRIGATÓRIOS: Inicie cada seção com: [PROFESSOR], [ALUNO], [GABARITO], [IMAGENS].
    3. SEM MARKDOWN: Proibido ** ou #. Use símbolos Unicode.
    
    ESTRUTURA:
    [PROFESSOR]
    (Roteiro e Lousa)
    [ALUNO]
    (Atividade numerada)
    [GABARITO]
    (Respostas)
    [IMAGENS]
    (Prompts)
    [FIM]""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (PADRÃO RONALDO GOMES).
    Sua missão é criar uma FOLHA DE ATIVIDADE INDEPENDENTE e REDUZIDA.
    
    REGRAS:
    1. QUANTIDADE: Gere EXATAMENTE a quantidade pedida (geralmente metade do original).
    2. ESTRUTURA: Use o marcador [PEI] para iniciar o texto.
    3. ENGENHARIA: Boxes 'PARA LEMBRAR', fracionamento em PASSOS e apenas 3 alternativas (A, B, C).""",
    
    "MAESTRO": "Você é o Maestro SOSA, assistente do Prof. Ronaldo Gomes.",
    "ESPECIALISTA_INCLUSAO": "Especialista em relatórios técnicos PEI.",
    "ESPECIALISTA_PEI": "Consultor técnico para Seção 1 do PEI.",
    "ESPECIALISTA_CURRICULO": "Especialista em adaptação curricular específica.",
    "ESPECIALISTA_ADAPTACAO": "Criador de tabelas de currículo adaptado.",
    "CRIADOR_ADAPTADO": "Especialista em DUA para atividades globais.",
    "AVALIADOR_ADAPTADO": "Transformador de provas regulares em adaptadas."
}

def gerar_ia(persona_key, comando, partes_arquivos=[], usar_busca=True):
    config = {'tools': [{'google_search': {}}]} if usar_busca else {}
    conteudo_prompt = [types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}")]
    if partes_arquivos: conteudo_prompt.extend(partes_arquivos)
    try:
        res = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        return res.text
    except Exception as e: return f"Erro na IA: {e}"

def extrair_tag(texto, tag):
    if not texto: return ""
    # Tenta formato [TAG] (Novo V24)
    padrao_novo = f"\\[{tag}\\](.*?)(?=\\[|$)"
    match = re.search(padrao_novo, texto, re.DOTALL | re.IGNORECASE)
    if match:
        res = match.group(1)
    else:
        # Tenta formato MARKER_TAG (Antigo)
        padrao_antigo = f"MARKER_{tag}(.*?)(?=MARKER_|$)"
        match = re.search(padrao_antigo, texto, re.DOTALL | re.IGNORECASE)
        res = match.group(1) if match else ""
    
    return res.replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()
