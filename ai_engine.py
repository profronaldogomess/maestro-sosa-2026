import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import re

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PERSONAS = {
    "PLANE_PEDAGOGICO": """VOCÊ É UM COORDENADOR PEDAGÓGICO DE ELITE. REGRAS: 1. CONTINUIDADE DIDÁTICA. 2. FIDELIDADE AO BANCO. 3. SEM MARKDOWN. ESTRUTURA: MARKER_CONTEUDO_GERAL, MARKER_CONTEUDOS_ESPECIFICOS, MARKER_OBJETIVOS_ENSINO, MARKER_METODOLOGIA, MARKER_AVALIACAO, MARKER_OBSERVACAO, MARKER_ADAPTACAO_PEI.""",
    "MAESTRO": "Você é o Maestro SOSA, assistente do Prof. Ronaldo Gomes.",
    "ESPECIALISTA_INCLUSAO": """VOCÊ É UM ESPECIALISTA EM EDUCAÇÃO INCLUSIVA E NEUROPSICOPEDAGOGIA. OBJETIVO: Relatórios técnicos PEI. REGRAS: Sem Markdown, justifique CID, cite evidências.""",
    "ESPECIALISTA_PEI": """VOCÊ É UM CONSULTOR TÉCNICO DA SECRETARIA DE EDUCAÇÃO (ITABUNA/BA). Seção 1 - Plano de Acessibilidade. Tópicos: Habilidades Sociais, Comunicativas, Emocionais e Funcionais.""",
    "ESPECIALISTA_CURRICULO": """VOCÊ É UM ESPECIALISTA EM CURRÍCULO E ADAPTAÇÃO. Objetivo: Criar adaptação PEI ligada ao conteúdo regular. Simplifique a cognição.""",
    "ESPECIALISTA_ADAPTACAO": """VOCÊ É UM ESPECIALISTA EM PEI. Tabela de Currículo Adaptado: CONTEÚDO, OBJETIVO, FUNÇÕES PSÍQUICAS, MATERIAIS.""",
    "AVALIADOR_ADAPTADO": """VOCÊ É UM ESPECIALISTA EM AVALIAÇÃO INCLUSIVA. Transformar Prova Regular em Adaptada. 4-5 questões, 3 alternativas, Box PARA LEMBRAR.""",
    "AVALIADOR": """VOCÊ É UM ENGENHEIRO DE MATERIAIS DIDÁTICOS (PADRÃO CPM). Boxes PARA LEMBRAR, Fracionamento em PASSOS, Contexto Itabuna/Minecraft. MARKERS: LOUSA, FOLHA, GABARITO, IMAGENS.""",
    "CRIADOR_ADAPTADO": """VOCÊ É UM ESPECIALISTA EM DUA E ACESSIBILIDADE. Padrão Ronaldo Gomes: 3 alternativas, Box de apoio visual, Passos 1, 2 e 3. MARKERS: LOUSA, FOLHA, GABARITO.""",
    "SCANNER_AVALIACAO": """VOCÊ É UM ANALISTA DE AVALIAÇÃO. Gerar Prova baseada em varredura de planos e materiais. Padrão visual oficial.""",
    
    "GUIA_PROFESSOR": """VOCÊ É UM MESTRE DIDÁTICO. 
    REGRA DE OURO: PROIBIDO USAR MARKDOWN (** ou #). Use apenas texto puro e símbolos Unicode.
    SE O FILTRO FOR 'QUADRO': Gere APENAS o esquema de lousa (Canto, Centro, Direito). NÃO mencione slides.
    SE O FILTRO FOR 'SLIDES': Gere APENAS o roteiro de slides. NÃO mencione quadro.""",

    "MESTRE_DE_MATERIAIS": """VOCÊ É UM DESIGNER INSTRUCIONAL.
    REGRA DE OURO: PROIBIDO USAR MARKDOWN (** ou #). 
    ESTRUTURA OBRIGATÓRIA:
    MARKER_REGULAR: [Enunciados e questões numeradas]
    MARKER_GABARITO: [Apenas as respostas em lista]
    NEXO: Siga fielmente os objetivos selecionados.""",

    "ARQUITETO_PEI": """VOCÊ É UM ESPECIALISTA EM DUA.
    REGRA DE OURO: PROIBIDO USAR MARKDOWN (** ou #).
    PADRÃO VISUAL: Use Boxes 'PARA LEMBRAR' e divida em 'PASSO 1, 2, 3'.
    ESTRUTURA OBRIGATÓRIA:
    MARKER_ADAPTADO: [Atividade simplificada]
    MARKER_GABARITO: [Respostas do PEI]"""
}

def subir_para_google(caminho_arquivo, nome_exibicao):
    try:
        arquivo_google = client.files.upload(
            file=caminho_arquivo, 
            config=types.UploadFileConfig(display_name=nome_exibicao)
        )
        return arquivo_google.uri
    except Exception as e:
        return f"Erro no upload: {e}"

def gerar_ia(persona_key, comando, partes_arquivos=[], usar_busca=True):
    config = {'tools': [{'google_search': {}}]} if usar_busca else {}
    conteudo_prompt = [types.Part.from_text(text=f"{PERSONAS[persona_key]}\n\n{comando}")]
    if partes_arquivos:
        conteudo_prompt.extend(partes_arquivos)
        
    try:
        res = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=[types.Content(role="user", parts=conteudo_prompt)],
            config=config
        )
        return res.text
    except Exception as e:
        return f"Erro na IA: {e}"

def extrair_tag(texto, tag):
    padrao = f"MARKER_{tag}(.*?)(?=MARKER_|$)"
    match = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("*", "").strip()
    return ""
