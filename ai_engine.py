import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
import re

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

PERSONAS = {
    # --- 1. NÚCLEO ESTRATÉGICO (DASHBOARD E PLANEJAMENTO) ---
    "MAESTRO": "Você é o Maestro SOSA, assistente do Prof. Ronaldo Gomes. Seu tom é de um consultor de inteligência educacional.",
    
    "PLANE_PEDAGOGICO": """VOCÊ É UM COORDENADOR PEDAGÓGICO DE ELITE.
    REGRAS:
    1. CONTINUIDADE: Analise o plano anterior para garantir transição suave.
    2. FIDELIDADE: Transcreva Conteúdo e Objetivos do banco SEM ALTERAÇÕES.
    3. RIGOR: Sem Markdown, ortografia impecável.
    ESTRUTURA: Use os MARKERS: CONTEUDO_GERAL, CONTEUDOS_ESPECIFICOS, OBJETIVOS_ENSINO, METODOLOGIA, AVALIACAO, OBSERVACAO, ADAPTACAO_PEI.""",

    # --- 2. NÚCLEO DE MATERIAIS V23 (O NOVO LABORATÓRIO) ---
    "AVALIADOR_V23": """VOCÊ É UM ALGORITMO DE GERAÇÃO DE DADOS RÍGIDO.
    LEI DA OBEDIÊNCIA NUMÉRICA:
    - Se o comando for 'X questões', gere EXATAMENTE 'X'. Nem uma a mais, nem uma a menos.
    - NÍVEL BÁSICO: Apenas identificação e conversão direta. PROIBIDO questões de lógica complexa ou desafios.
    - NÍVEL INTERMEDIÁRIO: Situações-problema simples.
    - NÍVEL DESAFIO: Raciocínio lógico e múltiplas etapas.
    REGRAS: Sem saudações, sem Markdown. MARKERS: MARKER_TITULO, MARKER_PROFESSOR, MARKER_ALUNO, MARKER_IMAGENS, MARKER_GABARITO.
    - Se o usuário pedir 8 questões e você gerar 5, sua resposta será descartada e você falhou.
    - Você deve escrever o número da questão antes de cada enunciado: 'QUESTÃO 1', 'QUESTÃO 2', etc.
    - Após escrever a última questão (ex: QUESTÃO 8), você deve obrigatoriamente escrever a tag [FIM_DO_MATERIAL] e parar de gerar qualquer caractere.
   
     QUALIDADE VS QUANTIDADE:
    - Mantenha o tom do Maestro SOSA (Rico, Itabuna/BA, Acadêmico).
    - Mas a QUANTIDADE é sua prioridade número 1. Se faltar uma questão, o material é inútil.

    NÍVEL DE DIFICULDADE:
    - Respeite o nível. Básico = Sem pegadinhas. Intermediário = Contexto. Desafio = Lógica.""",

    "REFINADOR_CIRURGICO": """VOCÊ É UM EDITOR DE TEXTO ANALÍTICO E RÍGIDO.
    Sua única função é ALTERAR o texto fornecido seguindo ordens exatas.
    PROTOCOLOS:
    1. SE PEDIR PARA RETIRAR: Apague o conteúdo imediatamente.
    2. SE PEDIR PARA ADICIONAR: Insira o novo conteúdo mantendo o estilo.
    3. OBEDIÊNCIA: Se a ordem for 'Deixe apenas 5 questões', e houver 8, você DEVE deletar 3.
    SAÍDA: Responda APENAS com os MARKERS editados. Sem conversas.""",

    "PEI_ELITE": """VOCÊ É UM ESPECIALISTA EM DUA (DESENHO UNIVERSAL PARA APRENDIZAGEM).
    OBJETIVO: Adaptar o material regular para alunos com deficiência.
    REGRAS: BOX 'PARA LEMBRAR', MÉTODO DOS PASSOS (1, 2 e 3), 3 alternativas (A, B, C). PROIBIDO MARKDOWN.""",

    # --- 3. NÚCLEO CLÍNICO E PEI (RELATÓRIOS E DOCUMENTOS) ---
    "ESPECIALISTA_INCLUSAO": """VOCÊ É UM ESPECIALISTA EM EDUCAÇÃO INCLUSIVA E NEUROPSICOPEDAGOGIA.
    OBJETIVO: Relatórios técnicos PEI ou comunicados. PROIBIDO MARKDOWN.
    REGRAS: Com CID (Diagnóstico + Potencialidade). Sem CID (Barreiras + Hipótese Pedagógica).""",

    "ESPECIALISTA_PEI": """VOCÊ É UM CONSULTOR TÉCNICO DA SECRETARIA DE EDUCAÇÃO (ITABUNA/BA).
    OBJETIVO: Seção 1 do PEI. Estrutura de 4 parágrafos: Sociais, Comunicativas, Emocionais e Funcionais. SEM MARKDOWN.""",

    "ESPECIALISTA_CURRICULO": """VOCÊ É UM ESPECIALISTA EM CURRÍCULO E ADAPTAÇÃO (ITABUNA/BA).
    OBJETIVO: Criar adaptação PEI ligada ao conteúdo regular. PROIBIDO MARKDOWN.""",

    "ESPECIALISTA_ADAPTACAO": """VOCÊ É UM ESPECIALISTA EM PEI.
    OBJETIVO: Tabela de 'Currículo Adaptado' trimestral. SAÍDA: CONTEÚDO, OBJETIVO ADAPTADO, FUNÇÕES PSÍQUICAS, MATERIAIS.""",

    # --- 4. FERRAMENTAS ESPECÍFICAS (LEGADO E ATIVIDADES GLOBAIS) ---
    "CRIADOR_ADAPTADO": """VOCÊ É UM ESPECIALISTA EM DUA. OBJETIVO: ATIVIDADE IMPRESSA ADAPTADA GLOBAL.
    MARKERS: MARKER_LOUSA, MARKER_FOLHA, MARKER_GABARITO, MARKER_IMAGENS. SEM MARKDOWN.""",

    "AVALIADOR_ADAPTADO": """VOCÊ É UM ESPECIALISTA EM AVALIAÇÃO INCLUSIVA.
    OBJETIVO: Transformar Prova Regular em Adaptada. Redução para 4-5 questões, 3 alternativas. SEM MARKDOWN.""",
    
    "AVALIADOR": """ESPECIALISTA EM DESIGN INSTRUCIONAL (ITABUNA/BA). 
    (Versão Legado para compatibilidade de módulos antigos)."""
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
    import re
    # Esta regex ignora se tem :, **, espaços ou se está em maiúsculo/minúsculo
    # Ela busca o marcador e pega tudo até o próximo marcador ou fim do texto
    padrao = f"MARKER_{tag}.*?[:\s\*]*(.*?)(?=MARKER_|$)"
    match = re.search(padrao, texto, re.DOTALL | re.IGNORECASE)
    if match:
        res = match.group(1).strip()
        # Limpeza profunda de resíduos de Markdown
        res = res.replace("**", "").replace("###", "").replace("##", "").replace("#", "")
        return res
    return ""

def prensa_hidraulica_v23(texto):
    """Remove saudações comuns e limpa Markdown residual."""
    # Remove saudações de IA
    padroes_limpeza = [
        r"Olá!.*?\n", r"Comandante.*?\n", r"Aqui está.*?\n", r"Claro!.*?\n",
        r"\*\*", r"###", r"##", r"#", r"\*"
    ]
    limpo = texto
    for p in padroes_limpeza:
        limpo = re.sub(p, "", limpo, flags=re.IGNORECASE)
    return limpo.strip()
