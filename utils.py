import importlib
import streamlit as st
import io
import random
import re
import uuid
from datetime import date, timedelta, datetime, timezone

# ==============================================================================
# 1. FUNÇÕES DE LIMPEZA E FORMATAÇÃO DE TEXTO
# ==============================================================================

def limpar_texto(texto):
    """Remove marcações markdown e caracteres especiais mantendo o texto limpo."""
    if not texto: return ""
    return texto.replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("__", "").replace("`", "").strip()

def gerar_nome_material_elite(ano, tipo, detalhe):
    """
    Gera o nome padronizado oficial: 6º Ano - Aula 1 - Jornada Pedagógica
    ano: int ou str (6)
    tipo: str (Aula 1, Sonda, Projeto)
    detalhe: str (Semana 01, I Trimestre, Nome do Tema)
    """
    ano_limpo = str(ano).replace("º", "")
    return f"{ano_limpo}º Ano - {tipo} - {detalhe}"

def gerar_sosa_id(tipo, ano, trimestre):
    """Gera um DNA único para o material respeitando o fuso de Itabuna (UTC-3)."""
    fuso_itabuna = timezone(timedelta(hours=-3))
    data_itabuna = datetime.now(fuso_itabuna)
    
    prefixo = str(tipo)[:4].upper()
    hash_curto = str(uuid.uuid4())[:4].upper()
    data_slug = data_itabuna.strftime("%d%m")
    ano_num = "".join(filter(str.isdigit, str(ano)))
    return f"{prefixo}-{ano_num}AN-{str(trimestre)[0]}-{data_slug}-{hash_curto}"

# ==============================================================================
# 2. FUNÇÕES DE CONVERSÃO NUMÉRICA & LATEX (GOOGLE SHEETS / PROVAS)
# ==============================================================================

def sosa_to_float(valor):
    """
    CONVERSOR UNIVERSAL SOSA (ANTI-ERRO):
    Converte qualquer entrada (string com vírgula, ponto, moeda ou texto anexado) em float puro.
    """
    if valor is None or str(valor).strip() == "" or str(valor).lower() == "nan":
        return 0.0
    try:
        s = str(valor).strip().replace(" ", "").replace(",", ".")
        m = re.search(r'[-+]?\d*\.?\d+', s)
        if m:
            return float(m.group(0))
        return 0.0
    except (ValueError, TypeError):
        return 0.0

def sosa_to_str(valor):
    """
    CONVERSOR FLOAT PARA GOOGLE SHEETS COM VÍRGULA (ANTI-ATTRIBUTE_ERROR):
    Converte float/int em string formatada com vírgula padrão Google Sheets (ex: 3.5 -> '3,50' ou '3,5').
    """
    if valor is None or str(valor).strip() == "" or str(valor).lower() == "nan":
        return "0,00"
    try:
        v_float = sosa_to_float(valor)
        return f"{v_float:.2f}".replace(".", ",")
    except Exception:
        return "0,00"

def preparar_para_leitura(texto):
    """
    Filtro de leitura global para fórmulas LaTeX ($$ ... $$), prompts de imagem e markdown.
    Garante que expressões matemáticas sejam renderizadas perfeitamente no Streamlit.
    """
    if not texto or not isinstance(texto, str): return ""
    
    texto = texto.replace('\x0c', '\\f')
    texto = re.sub(r'(?<!\$)\\\bfrac\{([^}]+)\}\{([^}]+)\}(?!\$)', r'$$ \\frac{\1}{\2} $$', texto)
    texto = re.sub(r'(?<!\$)\\\b(times|div|sqrt|circ|degree)\b(?!\$)', r'$$ \\\1 $$', texto)
    texto = re.sub(r'\$\$\s*\$\$', '$$', texto)
    texto = re.sub(r'\[GEOGEBRA\](.*?)\[/GEOGEBRA\]', '', texto, flags=re.IGNORECASE | re.DOTALL)
    
    texto = re.sub(
        r'\[\s*PROMPT IMAGEM:(.*?)\s*\]', 
        r'\n\n**[ILUSTRAÇÃO TÉCNICA SUGERIDA]**\n```english\n\1\n```\n\n', 
        texto, 
        flags=re.IGNORECASE | re.DOTALL
    )
    return texto

def extrair_valor_real_prova(texto_conteudo, nome_avaliacao=""):
    """
    SOSA V2026 - EXTRATOR INFALÍVEL DE VALOR DA AVALIAÇÃO:
    Lê [VALOR: 4.0], [VALOR] 4.0, VALOR: 4.0 ou deduz pelo tipo do instrumento:
    - TESTE / TRABALHO / SIMULADO -> 3.0 pts (Teto C2)
    - PROVA / AVALIAÇÃO / EXAME -> 4.0 pts (Teto C3)
    - RECUPERAÇÃO FINAL / REC_FINAL -> 10.0 pts (Teto RF)
    """
    if texto_conteudo and isinstance(texto_conteudo, str):
        m1 = re.search(r'\[\s*VALOR\s*[:\-]?\s*([\d\.,]+)\s*\]', texto_conteudo, re.IGNORECASE)
        if m1:
            v = sosa_to_float(m1.group(1))
            if v > 0: return v
        
        m2 = re.search(r'\bVALOR\s*[:\-]\s*([\d\.,]+)', texto_conteudo, re.IGNORECASE)
        if m2:
            v = sosa_to_float(m2.group(1))
            if v > 0: return v

    nome_upper = str(nome_avaliacao).upper()
    texto_upper = str(texto_conteudo).upper() if texto_conteudo else ""
    
    if any(x in nome_upper or x in texto_upper for x in ["FINAL", "REC_FINAL", "RECUPERAÇÃO FINAL", "RECUPERACAO FINAL"]):
        return 10.0
    elif any(x in nome_upper or x in texto_upper for x in ["TESTE", "SIMULADO", "TRABALHO"]):
        return 3.0
    elif any(x in nome_upper or x in texto_upper for x in ["PROVA", "AVALIAÇÃO", "AVALIACAO", "EXAME", "2ª CHAMADA", "2A CHAMADA"]):
        return 4.0
    elif any(x in nome_upper or x in texto_upper for x in ["SONDA", "DIAGNÓSTICA", "DIAGNOSTICA"]):
        return 10.0

    return 4.0

# ==============================================================================
# 3. FUNÇÕES DE DATA E CALENDÁRIO (ITABUNA 2026)
# ==============================================================================

def formatar_data_br(valor):
    """
    CONVERSOR CRONOLÓGICO SOBERANO SOSA (ANTI-SERIAL EXCEL / ISO):
    Converte números seriais (46149, 46233, 46259.0), datas ISO ou nulas para DD/MM/YYYY.
    """
    if not valor or str(valor).strip() == "" or str(valor).lower() == "nan":
        return ""
    
    val_str = str(valor).strip()
    
    # Caso 1: Número serial do Excel/Google Sheets (ex: 46149 ou 46149.0)
    try:
        val_clean_num = val_str.split('.')[0] if '.' in val_str else val_str
        if val_clean_num.isdigit():
            num = int(val_clean_num)
            if 40000 <= num <= 55000:
                dt = date(1899, 12, 30) + timedelta(days=num)
                return dt.strftime("%d/%m/%Y")
    except Exception:
        pass
    
    # Caso 2: Formato ISO (YYYY-MM-DD)
    if "-" in val_str and len(val_str) >= 10:
        try:
            return datetime.strptime(val_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        except Exception:
            pass
            
    # Caso 3: Formato BR já válido
    if "/" in val_str:
        return val_str
        
    return val_str

def sanitizar_nome_variante_soberana(nome_av):
    """
    VACINA ANTI-ANINHAMENTO RECURSIVO:
    Remove repetições de (VARIANTE (VARIANTE...)) mantendo o nome canônico do caderno.
    """
    if not nome_av or not isinstance(nome_av, str):
        return ""
    nome = str(nome_av).strip()
    if "VARIANTE" in nome.upper() or "TIPO" in nome.upper():
        match_tipo = re.search(r'TIPO\s*([A-Z])', nome, re.IGNORECASE)
        letra = match_tipo.group(1).upper() if match_tipo else "B"
        nome_base = nome.split('(')[0].split('-')[0].strip()
        return f"{nome_base} - TIPO {letra}"
    return nome

def obter_info_trimestre(dt):
    """Retorna o trimestre e o intervalo oficial do Calendário Escolar de Itabuna 2026."""
    t1 = (date(2026, 2, 9), date(2026, 5, 22))
    t2 = (date(2026, 5, 25), date(2026, 9, 4))
    t3 = (date(2026, 9, 8), date(2026, 12, 17))
    
    if t1[0] <= dt <= t1[1]: return "I Trimestre", t1
    if t2[0] <= dt <= t2[1]: return "II Trimestre", t2
    if t3[0] <= dt <= t3[1]: return "III Trimestre", t3
    return "Recesso/Jornada", (dt, dt)

def verificar_feriado_itabuna(dt):
    """Feriados municipais de Itabuna e nacionais de 2026."""
    feriados = {
        date(2026, 3, 19): "São José (Padroeiro)",
        date(2026, 4, 2): "Paixão de Cristo",
        date(2026, 4, 21): "Tiradentes",
        date(2026, 5, 1): "Dia do Trabalhador",
        date(2026, 6, 4): "Corpus Christi",
        date(2026, 7, 2): "Independência da Bahia",
        date(2026, 7, 28): "Aniversário de Itabuna",
        date(2026, 9, 7): "Independência do Brasil",
        date(2026, 10, 12): "Nsa. Sra. Aparecida",
        date(2026, 12, 25): "Natal"
    }
    return feriados.get(dt, None)

def gerar_semanas():
    """Gera a grade semanal oficial do ano letivo de 2026."""
    semanas = []
    data_atual = date(2026, 2, 2)
    fim_ano = date(2026, 12, 18)
    semanas.append("Jornada Pedagógica (02/02 a 06/02)")
    data_atual = date(2026, 2, 9)
    contador = 1
    while data_atual < fim_ano:
        trim, _ = obter_info_trimestre(data_atual)
        label = f"Semana {contador:02d} ({data_atual.strftime('%d/%m')} a {(data_atual + timedelta(days=4)).strftime('%d/%m')}) - {trim}"
        semanas.append(label)
        data_atual += timedelta(days=7)
        contador += 1
    return semanas

# ==============================================================================
# 4. MOTORES DE PSICOMETRIA E EMBARALHAMENTO (FORJA MASTER)
# ==============================================================================

def gerar_gabarito_balanceado(qtd_questoes):
    """Gera um gabarito balanceado sem 3 letras consecutivas iguais."""
    letras = ['A', 'B', 'C', 'D', 'E']
    base = (letras * ((qtd_questoes // 5) + 1))[:qtd_questoes]
    
    if qtd_questoes <= 2:
        random.shuffle(base)
        return base

    while True:
        random.shuffle(base)
        valido = True
        for i in range(len(base) - 2):
            if base[i] == base[i+1] == base[i+2]:
                valido = False
                break
        if valido:
            return base

def embaralhar_item_estruturado(item_dict):
    """Embaralha as alternativas de uma questão e recalcula o gabarito com precisão."""
    alt_keys = ['ALT_A', 'ALT_B', 'ALT_C', 'ALT_D', 'ALT_E']
    textos_alts = [item_dict[k] for k in alt_keys]
    
    letra_correta_atual = item_dict['GABARITO']
    idx_correta = ord(letra_correta_atual) - 65
    texto_correto = textos_alts[idx_correta]
    
    random.shuffle(textos_alts)
    novo_idx_correta = textos_alts.index(texto_correto)
    nova_letra_correta = chr(65 + novo_idx_correta)
    
    novo_item = item_dict.copy()
    for i, k in enumerate(alt_keys):
        novo_item[k] = textos_alts[i]
    novo_item['GABARITO'] = nova_letra_correta
    
    return novo_item

# ==============================================================================
# 5. MOTOR DE RECORTE E PROCESSAMENTO MULTI-INTERVALO DE PDF
# ==============================================================================

def processar_intervalos_paginas(texto_paginas):
    """Converte strings como '184-186, 189' em lista ordenada de números inteiros."""
    if not texto_paginas or not isinstance(texto_paginas, str):
        return []
    
    paginas = set()
    partes = texto_paginas.replace(" e ", ",").replace(";", ",").split(",")
    for parte in partes:
        p = parte.strip()
        if not p: continue
        if "-" in p or "a" in p.lower():
            p_intervalo = re.split(r'[\-aA]', p)
            if len(p_intervalo) == 2:
                try:
                    p_inicio = int(re.sub(r'\D', '', p_intervalo[0]))
                    p_fim = int(re.sub(r'\D', '', p_intervalo[1]))
                    if p_inicio <= p_fim:
                        for pag in range(p_inicio, p_fim + 1): paginas.add(pag)
                    else:
                        for pag in range(p_fim, p_inicio + 1): paginas.add(pag)
                except ValueError:
                    pass
        else:
            try:
                p_num = int(re.sub(r'\D', '', p))
                paginas.add(p_num)
            except ValueError:
                pass
    return sorted(list(paginas))

def extrair_texto_pdf_por_paginas(pdf_bytes, paginas_list):
    """Extrai o texto apenas das páginas solicitadas a partir dos bytes de um PDF."""
    if not pdf_bytes or not paginas_list: return ""

    try:
        pypdf = importlib.import_module("pypdf")
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        total_pags = len(reader.pages)

        texto_fatiado = []
        for pag_num in paginas_list:
            idx = pag_num - 1
            if 0 <= idx < total_pags:
                text_p = reader.pages[idx].extract_text() or ""
                if text_p.strip():
                    texto_fatiado.append(f"--- [PÁGINA {pag_num}] ---\n{text_p.strip()}")
        return "\n\n".join(texto_fatiado)
    except Exception as e:
        return f"⚠️ Erro ao extrair texto do PDF: {e}"

def obter_regex_trimestre(trimestre_str):
    """
    Detector universal de Trimestre com suporte a algarismos romanos, ordinais e abreviações.
    Evita falso positivo do 'I' dentro de 'II' ou 'III'.
    """
    if not trimestre_str or str(trimestre_str).strip() in ["", "Todos"]:
        return r".*"
    
    t_upper = str(trimestre_str).upper().strip()
    if any(x in t_upper for x in ["III", "TERCEIRO", "3º", "3"]):
        return r"(?<!I)III(?![I])|TERCEIRO|3º|\b3\b"
    elif any(x in t_upper for x in ["II", "SEGUNDO", "2º", "2"]):
        return r"(?<!I)II(?![I])|SEGUNDO|2º|\b2\b"
    else:
        return r"(?<!I)I(?![I])|PRIMEIRO|1º|\b1\b"

def fatiar_pdf_bytes_por_paginas(pdf_bytes, paginas_list):
    """Fatia um PDF mantendo apenas as páginas selecionadas e retorna os novos bytes."""
    if not pdf_bytes or not paginas_list: return None
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        writer = pypdf.PdfWriter()
        total_pags = len(reader.pages)
        for p in paginas_list:
            idx = p - 1
            if 0 <= idx < total_pags:
                writer.add_page(reader.pages[idx])
        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream.getvalue()
    except Exception as e:
        print(f"Erro ao fatiar PDF visual: {e}")
        return None

def renderizar_pdf_iframe(pdf_bytes, altura=550):
    """Renderiza a página exata do PDF usando Canvas HTML5 (PDF.js)."""
    if not pdf_bytes: return
    import base64
    import streamlit.components.v1 as components
    
    base64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
    
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.min.js"></script>
        <style>
            #pdf-container {{
                display: flex;
                flex-direction: column;
                align-items: center;
                background-color: #000B1A;
                padding: 15px;
                border-radius: 12px;
                border: 1px solid #2962FF;
            }}
            canvas {{
                margin-bottom: 20px;
                box-shadow: 0 8px 24px rgba(0,0,0,0.6);
                border-radius: 8px;
                max-width: 100%;
                height: auto !important;
            }}
        </style>
    </head>
    <body style="margin:0; padding:0; background-color: #000B1A;">
        <div id="pdf-container"></div>
        <script>
            const pdfData = atob("{base64_pdf}");
            const pdfjsLib = window['pdfjs-dist/build/pdf'];
            pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js';

            const loadingTask = pdfjsLib.getDocument({{data: pdfData}});
            loadingTask.promise.then(function(pdf) {{
                const container = document.getElementById('pdf-container');
                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {{
                    pdf.getPage(pageNum).then(function(page) {{
                        const scale = 1.5;
                        const viewport = page.getViewport({{scale: scale}});
                        const canvas = document.createElement('canvas');
                        const context = canvas.getContext('2d');
                        canvas.height = viewport.height;
                        canvas.width = viewport.width;
                        container.appendChild(canvas);
                        page.render({{canvasContext: context, viewport: viewport}});
                    }});
                }}
            }}).catch(function(error) {{
                console.error('Erro ao renderizar PDF:', error);
            }});
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=altura, scrolling=True)
