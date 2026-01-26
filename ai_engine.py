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
    Sua missão é criar materiais de Matemática com RIGOR ACADÊMICO e ESTÉTICA LIMPA.
    
    REGRAS RÍGIDAS:
    1. TOM DE VOZ: Use linguagem acadêmica (Mediação, Sistematização, Consolidação).
    2. PROIBIÇÃO DE TABELAS ASCII: Jamais desenhe quadros com caracteres (ex: ┌─┐). Use apenas texto e tópicos.
    3. PROTOCOLO DE CHOQUE: Gere EXATAMENTE a quantidade de questões pedida.
    4. MARCADORES: Inicie cada seção com: [PROFESSOR], [ALUNO], [GABARITO], [IMAGENS].
    5. SEM MARKDOWN: Proibido ** ou #. Use símbolos Unicode (x, ÷, ², ³, √).
    
    ESTRUTURA:
    [PROFESSOR] -> Roteiro denso e acadêmico.
    [ALUNO] -> Atividade numerada e contextualizada.
    [GABARITO] -> Respostas.
    [IMAGENS] -> Prompts para IA.""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (PADRÃO RONALDO GOMES).
    Sua missão é criar uma FOLHA DE ATIVIDADE INDEPENDENTE e REDUZIDA.
    
    REGRAS:
    1. QUANTIDADE: Gere EXATAMENTE a quantidade pedida (metade do original).
    2. MARCADOR: Use obrigatoriamente a tag [PEI] no início.
    3. ENGENHARIA: Boxes 'PARA LEMBRAR', fracionamento em PASSOS e apenas 3 alternativas (A, B, C).
    4. SEM TABELAS ASCII: Use apenas texto limpo.""",
    
    "MAESTRO": "Você é o Maestro SOSA, assistente do Prof. Ronaldo Gomes."
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
    # Tenta [TAG] ou MARKER_TAG
    padrao = rf"(?:\[{tag}\]|MARKER_{tag})(.*?)(?=\[|MARKER_|$)"
    match = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()
    return ""
