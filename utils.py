from datetime import date, timedelta
import re

def limpar_texto(texto):
    if not texto: return ""
    return texto.replace("**", "").replace("###", "").replace("##", "").replace("#", "").replace("__", "").replace("`", "").strip()

def obter_info_trimestre(dt):
    t1 = (date(2026, 2, 9), date(2026, 5, 22))
    t2 = (date(2026, 5, 25), date(2026, 9, 4))
    t3 = (date(2026, 9, 8), date(2026, 12, 17))
    
    if t1[0] <= dt <= t1[1]: return "I Trimestre", t1
    if t2[0] <= dt <= t2[1]: return "II Trimestre", t2
    if t3[0] <= dt <= t3[1]: return "III Trimestre", t3
    return "Recesso/Jornada", (dt, dt)

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

# --- ADICIONE AO FINAL DO SEU utils.py ---

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
