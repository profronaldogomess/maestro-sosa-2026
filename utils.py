import re
import uuid
from datetime import date, timedelta, datetime

# ==============================================================================
# 1. FUNÇÕES DE LIMPEZA E FORMATAÇÃO DE TEXTO
# ==============================================================================

def limpar_texto(texto):
    if not texto: return ""
    return texto.replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("__", "").replace("`", "").strip()

def gerar_nome_material_elite(ano, tipo, detalhe):
    """
    Gera o nome legível: 6º Ano - Aula 1 - Jornada Pedagógica
    ano: int ou str (6)
    tipo: str (Aula 1, Sonda, Projeto)
    detalhe: str (Semana 01, I Trimestre, Nome do Tema)
    """
    ano_limpo = str(ano).replace("º", "")
    return f"{ano_limpo}º Ano - {tipo} - {detalhe}"

def gerar_sosa_id(tipo, ano, trimestre):
    """Gera um DNA único para o material respeitando o fuso de Itabuna"""
    # Ajuste manual de fuso (UTC-3) para evitar o erro de "dia seguinte" à noite
    data_itabuna = datetime.utcnow() - timedelta(hours=3)
    
    prefixo = str(tipo)[:4].upper()
    hash_curto = str(uuid.uuid4())[:4].upper()
    data_slug = data_itabuna.strftime("%d%m")
    ano_num = "".join(filter(str.isdigit, str(ano)))
    return f"{prefixo}-{ano_num}AN-{str(trimestre)[0]}-{data_slug}-{hash_curto}"

# ==============================================================================
# 2. FUNÇÕES DE CONVERSÃO NUMÉRICA (GOOGLE SHEETS)
# ==============================================================================

def sosa_to_float(valor):
    """
    CONVERSOR UNIVERSAL SOSA (ANTI-ERRO 0.3)
    Converte qualquer entrada (string com vírgula, ponto ou None) em float puro.
    """
    if valor is None or str(valor).strip() == "" or str(valor).lower() == "nan":
        return 0.0
    try:
        # Remove espaços e troca vírgula por ponto
        limpo = str(valor).replace(" ", "").replace(",", ".")
        return float(limpo)
    except ValueError:
        return 0.0

def sosa_to_str(valor, casas=2):
    """
    FORMATADOR DE PERSISTÊNCIA (GOOGLE SHEETS)
    Converte float para string com vírgula para manter a localidade PT-BR no Sheets.
    """
    val_float = sosa_to_float(valor)
    formato = "{:." + str(casas) + "f}"
    return formato.format(val_float).replace(".", ",")

# ==============================================================================
# 3. FUNÇÕES DE DATA E CALENDÁRIO (ITABUNA 2026)
# ==============================================================================

def formatar_data_br(valor):
    """
    CONVERSOR CRONOLÓGICO SOSA (ANTI-SERIAL)
    Converte números seriais (46060) ou datas ISO para DD/MM/YYYY.
    """
    if not valor or str(valor).strip() == "" or str(valor).lower() == "nan":
        return ""
    
    # Caso 1: É um número serial do Excel/Sheets (ex: 46060)
    val_str = str(valor).strip()
    if val_str.replace('.','',1).isdigit():
        try:
            # Data base do Google Sheets é 30/12/1899
            dt = date(1899, 12, 30) + timedelta(days=int(float(val_str)))
            return dt.strftime("%d/%m/%Y")
        except: pass
    
    # Caso 2: Já é uma string de data (YYYY-MM-DD ou DD/MM/YYYY)
    try:
        if "-" in val_str: # Formato ISO
            return datetime.strptime(val_str[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        if "/" in val_str: # Já está no formato BR
            return val_str
    except: pass
    
    return val_str

def obter_info_trimestre(dt):
    # Datas exatas do PDF da Prefeitura de Itabuna 2026
    t1 = (date(2026, 2, 9), date(2026, 5, 22))
    t2 = (date(2026, 5, 25), date(2026, 9, 4))
    t3 = (date(2026, 8, 9), date(2026, 12, 17)) # Início do III em 08/09 conforme PDF
    
    if t1[0] <= dt <= t1[1]: return "I Trimestre", t1
    if t2[0] <= dt <= t2[1]: return "II Trimestre", t2
    if t3[0] <= dt <= t3[1]: return "III Trimestre", t3
    return "Recesso/Jornada", (dt, dt)

def verificar_feriado_itabuna(dt):
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
    semanas = []
    data_atual = date(2026, 2, 2)
    fim_ano = date(2026, 12, 18)
    semanas.append(f"Jornada Pedagógica (02/02 a 06/02)")
    data_atual = date(2026, 2, 9)
    contador = 1
    while data_atual < fim_ano:
        trim, _ = obter_info_trimestre(data_atual)
        label = f"Semana {contador:02d} ({data_atual.strftime('%d/%m')} a {(data_atual + timedelta(days=4)).strftime('%d/%m')}) - {trim}"
        semanas.append(label)
        data_atual += timedelta(days=7)
        contador += 1
    return semanas
