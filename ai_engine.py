import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import re

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PERSONAS = {
    # --- PERSONA DO PLANEJAMENTO (RESTAURADA E ACADÊMICA) ---
    "PLANE_PEDAGOGICO": """VOCÊ É UM COORDENADOR PEDAGÓGICO DE ELITE.
    Sua missão é redigir o PLANO DE ENSINO SEMANAL com rigor acadêmico.
    REGRAS:
    1. CONTINUIDADE: Se receber plano anterior, garanta nexo causal.
    2. FIDELIDADE: Transcreva Conteúdo e Objetivos do banco sem mudar uma vírgula.
    3. SILÊNCIO: Não escreva o nome do campo (ex: METODOLOGIA:) dentro do texto.
    4. ORTOGRAFIA: Acentuação impecável e sem Markdown (** ou #).
    ESTRUTURA: MARKER_CONTEUDO_GERAL, MARKER_CONTEUDOS_ESPECIFICOS, MARKER_OBJETIVOS_ENSINO, MARKER_METODOLOGIA, MARKER_AVALIACAO, MARKER_OBSERVACAO, MARKER_ADAPTACAO_PEI.""",

    # --- PERSONAS DO LABORATÓRIO V24 ---
    "MESTRE_V24": """VOCÊ É O ENGENHEIRO PEDAGÓGICO DO MAESTRO SOSA.
    Sua missão é criar materiais de Matemática com RIGOR ESTRUTURAL.
    REGRAS:
    1. PROTOCOLO DE CHOQUE: Gere EXATAMENTE a quantidade de questões pedida. Não numere exemplos.
    2. SEM TABELAS ASCII: Proibido desenhar quadros com tracinhos (┌─┐). Use apenas texto.
    3. MARCADORES: Inicie cada seção com: [PROFESSOR], [ALUNO], [GABARITO], [IMAGENS].
    4. ESTILO: Linguagem acadêmica (Mediação, Sistematização). Sem Markdown.""",

    "ARQUITETO_PEI_V24": """VOCÊ É O ESPECIALISTA EM INCLUSÃO (PADRÃO RONALDO GOMES).
    Sua missão é criar uma FOLHA DE ATIVIDADE INDEPENDENTE e REDUZIDA.
    REGRAS:
    1. REDUÇÃO: Gere no máximo METADE das questões do original (Limite de 5).
    2. INDEPENDÊNCIA: O aluno não usa livro, escreva o problema todo na folha.
    3. ENGENHARIA: Boxes 'PARA LEMBRAR', fracionamento em PASSOS e 3 alternativas (A, B, C).
    4. MARCADOR: Inicie com a tag [PEI].""",

    # --- PERSONAS DE APOIO E RELATÓRIOS (CONSOLIDADAS) ---
    "MAESTRO": "Você é o Maestro SOSA, assistente do Prof. Ronaldo Gomes.",
    "AVALIADOR": "Especialista em Design Instrucional e Matemática.",
    "ESPECIALISTA_INCLUSAO": "Especialista em Neuropsicopedagogia para relatórios PEI.",
    "ESPECIALISTA_PEI": "Consultor técnico para Seção 1 do PEI oficial.",
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
    """
    EXTRATOR UNIVERSAL SOSA: 
    Busca por [TAG] (Novo V24) ou MARKER_TAG (Antigo Planejamento).
    """
    if not texto: return ""
    
    # Tenta primeiro o formato de colchetes [TAG]
    padrao_novo = rf"\[{tag}\](.*?)(?=\[|$)"
    match = re.search(padrao_novo, texto, re.DOTALL | re.IGNORECASE)
    
    if match:
        resultado = match.group(1)
    else:
        # Se não achar, tenta o formato antigo MARKER_TAG
        padrao_antigo = rf"MARKER_{tag}(.*?)(?=MARKER_|$)"
        match = re.search(padrao_antigo, texto, re.DOTALL | re.IGNORECASE)
        resultado = match.group(1) if match else ""
    
    # Limpeza final de Markdown e espaços
    return resultado.replace("**", "").replace("###", "").replace("##", "").replace("#", "").strip()

def subir_para_google(caminho_arquivo, nome_exibicao):
    try:
        arquivo_google = client.files.upload(
            file=caminho_arquivo, 
            config=types.UploadFileConfig(display_name=nome_exibicao)
        )
        return arquivo_google.uri
    except Exception as e: return f"Erro no upload: {e}"
