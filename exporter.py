import os
import io
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from datetime import datetime

from pandas import util
import ai_engine as ai


# ==============================================================================
# 1. FUNÇÕES AUXILIARES TÉCNICAS E SANITIZAÇÃO
# ==============================================================================

def set_row_height(row, height_pt):
    """Define a altura mínima da linha da tabela para o cabeçalho não achatar"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

def set_cell_background(cell, fill_hex):
    """Aplica cor de fundo executiva em uma célula da tabela"""
    try:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)
    except: pass

def converter_latex_para_texto_word(texto):
    """Converte expressões matemáticas do LaTeX para texto legível de impressão no Word"""
    if not texto or not isinstance(texto, str): return ""
    t = texto
    
    # 1. Converte frações \frac{a}{b} -> a/b
    t = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'\1/\2', t)
    
    # 2. Símbolos matemáticos
    t = t.replace(r'\times', '×').replace(r'\div', '÷').replace(r'\cdot', '·')
    t = t.replace(r'\geq', '≥').replace(r'\leq', '≤').replace(r'\neq', '≠').replace(r'\approx', '≈')
    t = t.replace(r'\sqrt', '√').replace(r'\degree', '°').replace(r'^\circ', '°')
    
    # 3. Potências simples
    t = t.replace('^2', '²').replace('^3', '³')
    
    # 4. Limpa cifrões do LaTeX e marcas de formatação crua
    t = t.replace('$$', '').replace('$', '')
    return t.strip()

def adicionar_texto_formatado(paragraph, texto):
    """Converte padrões **texto** em negrito real e limpa marcas matemáticas"""
    if not texto: return
    texto_limpo = converter_latex_para_texto_word(texto)
    texto_limpo = texto_limpo.replace("➔", "").replace("->", "→").strip()
    
    partes = re.split(r'(\*\*.*?\*\*)', texto_limpo)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            run = paragraph.add_run(parte.replace('**', ''))
            run.bold = True
        else:
            paragraph.add_run(parte)

def adicionar_box_imagem_word(doc, legenda_prompt="ESPAÇO PARA ILUSTRAÇÃO / DESENHO"):
    """Cria uma moldura visual de ilustração no papel A4 com borda fina e elegante"""
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(5.5)
    
    set_cell_background(cell, "F8FAFC")
    set_row_height(table.rows[0], 110)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(35)
    
    run_icon = p.add_run("🖼️ ")
    run_icon.font.size = Pt(14)
    
    run = p.add_run(f"[{legenda_prompt.upper()}]")
    run.font.bold = True
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph()

def configurar_cabecalho_mestre(doc, info, tipo_label, mostrar_nota=False):
    """Gera o cabeçalho executivo oficial da Prefeitura de Itabuna"""
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    
    widths = [Inches(0.8), Inches(3.2), Inches(1.0), Inches(1.1), Inches(1.8)]
    for i, w in enumerate(widths): 
        table.columns[i].width = w

    for row in table.rows:
        set_row_height(row, 22)

    # LINHA 0: LOGO, ESCOLA E TRIMESTRE
    c_logo = table.cell(0, 0).merge(table.cell(2, 0))
    c_escola = table.cell(0, 1).merge(table.cell(0, 3))
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold = True
    run_esc.font.size = Pt(10)
    
    c_trim = table.cell(0, 4)
    c_trim.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_background(c_trim, "F1F5F9")
    p_tr = c_trim.paragraphs[0]
    p_tr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tr = p_tr.add_run(info.get('trimestre', 'I Trimestre'))
    run_tr.font.bold = True
    run_tr.font.size = Pt(9.5)

    # LINHA 1: ALUNO
    if mostrar_nota:
        c_aluno = table.cell(1, 1).merge(table.cell(1, 3))
        c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_aluno.paragraphs[0].add_run("ESTUDANTE: __________________________________________________").font.size = Pt(9.5)
        
        c_nota = table.cell(1, 4)
        c_nota.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c_nota, "F8FAFC")
        p_n = c_nota.paragraphs[0]
        p_n.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_n.add_run("NOTA: ________").font.bold = True
    else:
        c_aluno = table.cell(1, 1).merge(table.cell(1, 4))
        c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_aluno.paragraphs[0].add_run("ESTUDANTE: ________________________________________________________________").font.size = Pt(9.5)

    # LINHA 2: PROFESSOR, TURMA, DATA E TIPO
    table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(9)
    table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano', '6º')}").font.size = Pt(9)
    table.cell(2, 3).paragraphs[0].add_run("DATA:    /    /").font.size = Pt(9)
    
    c_tipo = table.cell(2, 4)
    c_tipo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_background(c_tipo, "2962FF")
    p_tipo = c_tipo.paragraphs[0]
    p_tipo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tipo = p_tipo.add_run(tipo_label)
    run_tipo.font.bold = True
    run_tipo.font.size = Pt(9)
    run_tipo.font.color.rgb = RGBColor(255, 255, 255)

    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c_logo.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try: p.add_run().add_picture(logo_path, width=Inches(0.65))
        except: pass
    return table

# ==============================================================================
# 2. MATERIAL DO ALUNO REGULAR
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    configurar_cabecalho_mestre(doc, info, "ATIVIDADE DE SALA", mostrar_nota=False)
    doc.add_paragraph()

    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '420')

    linhas = str(conteudo).split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        
        if "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
            adicionar_box_imagem_word(doc, "ESPAÇO PARA ILUSTRAÇÃO")
            continue
            
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        if any(x in l_s.upper() for x in ["ATIVIDADE DE", "JORNADA", "HISTÓRIA", "MATEMÁTICA", "AULA"]):
            run = p.add_run(l_s.replace('**', ''))
            run.bold = True
            run.font.color.rgb = RGBColor(0, 51, 102)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif "QUESTÃO" in l_s.upper():
            match = re.match(r"^(QUEST[AÃ]O\s*\d+)([\.\s:]+)(.*)", l_s, re.IGNORECASE)
            if match:
                run_r = p.add_run(f"{match.group(1).upper()}. ")
                run_r.bold = True
                adicionar_texto_formatado(p, match.group(3).strip())
            else: adicionar_texto_formatado(p, l_s)
        else:
            adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. MATERIAL PEI ADAPTADO (NÍVEIS 1 E 2)
# ==============================================================================
def gerar_docx_pei_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10.5)

    configurar_cabecalho_mestre(doc, info, "ATIVIDADE ADAPTADA", mostrar_nota=True)
    doc.add_paragraph()

    num_total_q = len(re.findall(r'(?i)(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)\s*\d+', str(conteudo)))
    if num_total_q == 0: num_total_q = 5 

    top_table = doc.add_table(rows=1, cols=2)
    top_table.columns[0].width = Inches(3.5)
    top_table.columns[1].width = Inches(4.0)
    
    c_orient = top_table.cell(0, 0)
    p_tit = c_orient.paragraphs[0]
    p_tit.add_run("ORIENTAÇÕES PEI:").font.bold = True
    
    val_total = info.get('valor', '3,0')
    orient_list = [
        "Leia atentamente cada enunciado.",
        "Marque apenas uma alternativa por questão.",
        f"Valor Total: {val_total}"
    ]
    for txt in orient_list:
        p = c_orient.add_paragraph()
        p.add_run(f"• {txt}").font.size = Pt(9)
        p.paragraph_format.space_after = Pt(1)

    c_gab = top_table.cell(0, 1)
    if num_total_q <= 10:
        gab_grid = c_gab.add_table(rows=num_total_q + 1, cols=4)
        gab_grid.style = 'Table Grid'
        for i, lab in enumerate(["Q", "A", "B", "C"]):
            c = gab_grid.cell(0, i)
            set_cell_background(c, "F1F5F9")
            c.paragraphs[0].add_run(lab).font.bold = True
        for r in range(1, num_total_q + 1):
            gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
            for col in range(1, 4): 
                gab_grid.cell(r, col).paragraphs[0].add_run("○").font.size = Pt(13)
    else:
        half = (num_total_q + 1) // 2
        gab_grid = c_gab.add_table(rows=half + 1, cols=8)
        gab_grid.style = 'Table Grid'
        headers = ["Q", "A", "B", "C", "Q", "A", "B", "C"]
        for i, lab in enumerate(headers):
            c = gab_grid.cell(0, i)
            set_cell_background(c, "F1F5F9")
            c.paragraphs[0].add_run(lab).font.bold = True
        
        for r in range(1, num_total_q + 1):
            row_idx = r if r <= half else r - half
            col_offset = 0 if r <= half else 4
            gab_grid.cell(row_idx, col_offset).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
            for col in range(1, 4):
                gab_grid.cell(row_idx, col_offset + col).paragraphs[0].add_run("○").font.size = Pt(13)

    doc.add_paragraph()

    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '420')

    linhas = str(conteudo).split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue

        if "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
            adicionar_box_imagem_word(doc, "ESPAÇO PARA ILUSTRAÇÃO DA QUESTÃO")
            continue

        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15

        secoes_pei = ["PARA LEMBRAR", "OBJETIVO", "INSTRUÇÕES", "ATIVIDADE", "PASSO A PASSO", "DICA MESTRA"]
        if any(x in l_s.upper() for x in secoes_pei):
            p.paragraph_format.space_before = Pt(6)
            txt_limpo = l_s.replace("[", "").replace("]", "").replace(":", "")
            run = p.add_run(f"📌 {txt_limpo}")
            run.bold = True
            run.font.color.rgb = RGBColor(41, 98, 255)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif re.match(r"^(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)\d+", l_s, re.IGNORECASE):
            match = re.match(r"^((?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)\d+)([\.\s:]+)(.*)", l_s, re.IGNORECASE)
            if match:
                run_r = p.add_run(f"{match.group(1).upper()}. ")
                run_r.bold = True
                adicionar_texto_formatado(p, match.group(3).strip())
            else: adicionar_texto_formatado(p, l_s)
        else:
            adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 4. GUIA DO PROFESSOR (COM DESCRITORES SAEB E DISTRATORES CIENTÍFICOS)
# ==============================================================================
def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    header_table = doc.add_table(rows=2, cols=3)
    header_table.style = 'Table Grid'
    c_tit = header_table.cell(0, 0).merge(header_table.cell(0, 2))
    set_cell_background(c_tit, "003366")
    run_tit = c_tit.paragraphs[0].add_run("GUIA DE MEDIAÇÃO, DESCRITORES SAEB E DISTRATORES")
    run_tit.font.bold, run_tit.font.size = True, Pt(11)
    run_tit.font.color.rgb = RGBColor(255, 255, 255)
    c_tit.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    header_table.cell(1, 0).paragraphs[0].add_run(f"ANO: {info.get('ano', '')}").font.size = Pt(9)
    header_table.cell(1, 1).paragraphs[0].add_run(f"SEMANA: {info.get('semana', '')}").font.size = Pt(9)
    header_table.cell(1, 2).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre', 'I')}").font.size = Pt(9)
    for row in header_table.rows: set_row_height(row, 20)
    doc.add_paragraph()

    linhas = str(conteudo).split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(3)

        if re.search(r"(?i)QUEST[AÃ]O\s*(?:PEI\s*)?\d+\s*[:\-]\s*[A-E]$|^\d+[\.\s\-]+[A-E]$", l_s):
            run = p.add_run(f"✅ {l_s}")
            run.font.bold, run.font.size = True, Pt(10.5)
            run.font.color.rgb = RGBColor(0, 128, 0)
            continue

        if any(x in l_s.upper() for x in ["JUSTIFICATIVA", "PERÍCIA", "LACUNA", "DISTRATORES", "DESCRITOR"]):
            p.paragraph_format.left_indent = Inches(0.15)
            if "DESCRITOR" in l_s.upper() or "SAEB" in l_s.upper():
                run_d = p.add_run("🆔 ")
                run_d.font.size = Pt(10)
            elif "DISTRATORES" in l_s.upper():
                run_d = p.add_run("🧠 ")
                run_d.font.size = Pt(10)
            adicionar_texto_formatado(p, l_s)
            continue

        adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 5. PROVA OFICIAL (PADRÃO ENEM / SAEB / OBMEP COM CARTÃO-RESPOSTA FIDUCIAL)
# ==============================================================================

# ==============================================================================
# 5. PROVA OFICIAL (PADRÃO ENEM / SAEB COM CARTÃO-RESPOSTA EXPANDIDO V2026)
# ==============================================================================

def adicionar_cartao_resposta_fiducial_word(doc, num_total_q, is_pei=False):
    """
    SOSA V2026: Cartão-Resposta Ampliado e Expandido (Padrão Oficial CAEd/SAEB).
    Células ampliadas, altura de linha de 22pt, bolinhas de 13pt e 4 Marcadores Fiduciais (■).
    """
    container_table = doc.add_table(rows=3, cols=3)
    container_table.style = 'Table Grid'
    container_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    container_table.columns[0].width = Inches(0.45)
    container_table.columns[1].width = Inches(6.5)
    container_table.columns[2].width = Inches(0.45)

    set_row_height(container_table.rows[0], 28)
    set_row_height(container_table.rows[2], 28)

    # 4 Quadrados Pretos Fiduciais nos Cantos (■)
    for r_idx, c_idx in [(0, 0), (0, 2), (2, 0), (2, 2)]:
        c = container_table.cell(r_idx, c_idx)
        set_cell_background(c, "000000")
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("■")
        run.font.color.rgb = RGBColor(0, 0, 0)
        run.font.size = Pt(16)

    # Título do Cartão (Topo)
    c_title = container_table.cell(0, 1)
    set_cell_background(c_title, "F1F5F9")
    p_t = c_title.paragraphs[0]
    p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_t = p_t.add_run("CARTÃO-RESPOSTA OFICIAL (FOLHA DE RESPOSTAS)")
    r_t.font.bold = True
    r_t.font.size = Pt(10.5)

    # Rodapé do Cartão
    c_foot = container_table.cell(2, 1)
    set_cell_background(c_foot, "F8FAFC")
    p_f = c_foot.paragraphs[0]
    p_f.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_f = p_f.add_run("▲ MANTENHA O PAPEL RETO • PREENCHA TOTALMENTE OS CÍRCULOS COM CANETA PRETA OU AZUL ▲")
    r_f.font.size = Pt(8.0)
    r_f.font.bold = True
    r_f.font.color.rgb = RGBColor(100, 116, 139)

    # Célula Central - Grade de Bolinhas Ampliada
    c_grid = container_table.cell(1, 1)
    col_count = 4 if is_pei else 6
    headers = ["Q", "A", "B", "C"] if is_pei else ["Q", "A", "B", "C", "D", "E"]
    
    if num_total_q <= 10:
        gab_grid = c_grid.add_table(rows=num_total_q + 1, cols=col_count)
        gab_grid.style = 'Table Grid'
        gab_grid.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        for i, lab in enumerate(headers):
            c = gab_grid.cell(0, i)
            set_cell_background(c, "2962FF" if i==0 else "E2E8F0")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_h = p.add_run(lab)
            r_h.font.bold = True
            r_h.font.size = Pt(9.5)
            if i == 0: r_h.font.color.rgb = RGBColor(255, 255, 255)
            
        for r in range(1, num_total_q + 1):
            set_row_height(gab_grid.rows[r], 22)
            c_q = gab_grid.cell(r, 0)
            set_cell_background(c_q, "F1F5F9")
            p_q = c_q.paragraphs[0]
            p_q.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_q_num = p_q.add_run(f"{r:02d}")
            r_q_num.font.size = Pt(9.5)
            r_q_num.font.bold = True
            
            for col in range(1, col_count):
                c_b = gab_grid.cell(r, col)
                p_b = c_b.paragraphs[0]
                p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_b.add_run("○").font.size = Pt(13)
    else:
        half = (num_total_q + 1) // 2
        double_cols = col_count * 2
        gab_grid = c_grid.add_table(rows=half + 1, cols=double_cols)
        gab_grid.style = 'Table Grid'
        gab_grid.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        headers_double = headers + headers
        for i, lab in enumerate(headers_double):
            c = gab_grid.cell(0, i)
            is_q_col = (i % col_count == 0)
            set_cell_background(c, "2962FF" if is_q_col else "E2E8F0")
            p = c.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_h = p.add_run(lab)
            r_h.font.bold = True
            r_h.font.size = Pt(9.0)
            if is_q_col: r_h.font.color.rgb = RGBColor(255, 255, 255)

        for r in range(1, num_total_q + 1):
            row_idx = r if r <= half else r - half
            col_offset = 0 if r <= half else col_count
            
            set_row_height(gab_grid.rows[row_idx], 20)
            c_q = gab_grid.cell(row_idx, col_offset)
            set_cell_background(c_q, "F1F5F9")
            p_q = c_q.paragraphs[0]
            p_q.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_q = p_q.add_run(f"{r:02d}")
            r_q.font.size = Pt(9.0)
            r_q.font.bold = True
            
            for col in range(1, col_count):
                c_b = gab_grid.cell(row_idx, col_offset + col)
                p_b = c_b.paragraphs[0]
                p_b.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_b.add_run("○").font.size = Pt(12)

def helper_sosa_float(v):
    """Converte qualquer valor para float de forma imune a erros"""
    if not v or str(v).strip() == "" or str(v).lower() == "nan": return 0.0
    try:
        return float(str(v).replace(" ", "").replace(",", "."))
    except: return 0.0

def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10)

        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.35)
        section.left_margin = section.right_margin = Inches(0.4)
        
        is_pei_doc = "PEI" in titulo_doc.upper() or "ADAPTADA" in titulo_doc.upper()
        tag_alvo = "PEI" if is_pei_doc else "QUESTOES"
        
        corpo_bruto = ai.extrair_tag(conteudo_ia, tag_alvo)
        if not corpo_bruto:
            match_primeira_q = re.search(r"(?i)QUESTÃO\s*\d+", conteudo_ia)
            corpo_bruto = conteudo_ia[match_primeira_q.start():].strip() if match_primeira_q else conteudo_ia.strip()

        num_total_q = len(re.findall(r'(?i)QUESTÃO\s+\d+', corpo_bruto))
        if num_total_q == 0: num_total_q = int(helper_sosa_float(info.get('qtd_questoes', info.get('qtd', 5))))
        
        label_prova = "AVALIAÇÃO ADAPTADA" if is_pei_doc else "AVALIAÇÃO DE MATEMÁTICA (ENEM/SAEB)"
        if "SONDA" in titulo_doc.upper(): label_prova = "SONDA DE PROFICIÊNCIA"

        # 🚨 CÁLCULO MATEMÁTICO PRECISO (IMUNE A ERROS)
        val_total_num = helper_sosa_float(info.get('valor', 3.0))
        if val_total_num == 0: val_total_num = 3.0

        num_q_num = int(helper_sosa_float(info.get('qtd', info.get('qtd_questoes', num_total_q))))
        if num_q_num == 0: num_q_num = num_total_q or 10

        val_q_calc = val_total_num / num_q_num if num_q_num > 0 else 0.3
        
        val_total_str = f"{val_total_num:.1f}"
        val_q_str = f"{val_q_calc:.2f}".replace(".", ",")
        
        info_cabecalho = info.copy()
        info_cabecalho['valor'] = val_total_str
        info_cabecalho['valor_questao'] = val_q_str

        # 1. CABEÇALHO MESTRE DA ESCOLA
        configurar_cabecalho_mestre(doc, info_cabecalho, label_prova, mostrar_nota=True)
        doc.add_paragraph()

        # 2. CAPA DE INSTRUÇÕES OFICIAIS & REGRA DO CÁLCULO 50%
        top_table = doc.add_table(rows=1, cols=1)
        top_table.style = 'Table Grid'
        top_table.columns[0].width = Inches(7.0)
        c_orient = top_table.cell(0, 0)
        set_cell_background(c_orient, "F8FAFC")
        
        p_tit = c_orient.paragraphs[0]
        r_tit_inst = p_tit.add_run("📋 ORIENTAÇÕES OFICIAIS DE EXAME (PADRÃO ENEM/SAEB):")
        r_tit_inst.bold = True
        r_tit_inst.font.size = Pt(9.5)
        r_tit_inst.font.color.rgb = RGBColor(0, 51, 102)
        
        orient_list = [
            f"Valor Total do Exame: {val_total_str} pts | Valor por Questão: {val_q_str} pts.",
            "Preencha o Cartão-Resposta abaixo com caneta esferográfica preta ou azul transparente.",
            "🚨 REGRA DO CÁLCULO OBRIGATÓRIO (MEIO CERTO - 50%): Nas questões objetivas que exigem resolução matemática, o cálculo DEVE ser apresentado no papel da prova. Questão acertada no Cartão-Resposta sem a memória de cálculo receberá 50% do valor (sinalizado com *).",
            "Mantenha os 4 marcadores pretos (■) dos cantos limpos e sem rasuras para leitura óptica."
        ]
        for txt in orient_list:
            p = c_orient.add_paragraph()
            p.add_run(f"• {txt}").font.size = Pt(8.5)
            p.paragraph_format.space_after = Pt(1)

        doc.add_paragraph()

        # 3. CARTÃO-RESPOSTA PADRONIZADO E AMPLIADO
        if info.get('tipo_prova') != "2ª Chamada":
            adicionar_cartao_resposta_fiducial_word(doc, num_total_q, is_pei_doc)

        doc.add_paragraph()

        # 4. ENUNCIADOS DAS QUESTÕES
        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '450')

        for linha in corpo_bruto.split('\n'):
            l_s = linha.strip()
            if not l_s: continue

            if "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
                adicionar_box_imagem_word(doc, "ESPAÇO PARA ILUSTRAÇÃO DA QUESTÃO")
                continue

            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            
            if l_s.upper().startswith("QUESTÃO"):
                match = re.match(r"^(QUEST[AÃ]O\s*\d+)(\s*\(.*?\))?([\s\.\-\:]+)(.*)", l_s, re.IGNORECASE)
                if match:
                    rotulo = f"{match.group(1).upper()}{match.group(2) if match.group(2) else ''}{match.group(3)}"
                    run_r = p.add_run(rotulo)
                    run_r.bold = True
                    run_r.font.size = Pt(10.5)
                    run_r.font.color.rgb = RGBColor(0, 51, 102)
                    adicionar_texto_formatado(p, match.group(4).strip())
                    continue

            if re.match(r'^[A-E][\)\.]', l_s):
                p.paragraph_format.left_indent = Inches(0.15)
                letra_match = re.match(r'^([A-E][\)\.])(.*)', l_s)
                if letra_match:
                    run_letra = p.add_run(letra_match.group(1))
                    run_letra.bold = True
                    adicionar_texto_formatado(p, letra_match.group(2))
                    continue
            
            adicionar_texto_formatado(p, l_s)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO EXPORTER DE PROVA: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 6. PLANO PEDAGÓGICO SEMANAL
# ==============================================================================
def gerar_docx_plano_pedagogico_ELITE(titulo_arquivo, dados, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        table = doc.add_table(rows=3, cols=3)
        table.style = 'Table Grid'
        widths = [Inches(1.1), Inches(3.6), Inches(2.0)]
        for i, w in enumerate(widths): table.columns[i].width = w

        logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
        if os.path.exists(logo_path):
            cell_logo = table.cell(0, 0).merge(table.cell(2, 0))
            cell_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p_logo = cell_logo.paragraphs[0]
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.add_run().add_picture(logo_path, width=Inches(0.85))
        
        table.cell(0, 1).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        
        c_tit = table.cell(0, 2)
        set_cell_background(c_tit, "2962FF")
        p_t = c_tit.paragraphs[0]
        p_t.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_t = p_t.add_run("PLANO DE ENSINO SEMANAL")
        r_t.font.bold = True
        r_t.font.color.rgb = RGBColor(255, 255, 255)

        table.cell(1, 1).paragraphs[0].add_run(f"Professor: Ronaldo Gomes").font.size = Pt(9.5)
        table.cell(1, 2).paragraphs[0].add_run(f"Série: {info.get('ano', '')}").font.size = Pt(9.5)
        table.cell(2, 1).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}").font.size = Pt(9.5)
        table.cell(2, 2).paragraphs[0].add_run(f"Trimestre: {info.get('trimestre', 'I')}").font.bold = True

        doc.add_paragraph()

        campos = [
            ("OBJETO DE CONHECIMENTO (EIXO):", "geral"), 
            ("CONTEÚDOS ESPECÍFICOS:", "especificos"), 
            ("OBJETIVOS DE APRENDIZAGEM:", "objetivos"), 
            ("RECURSOS DIDÁTICOS:", "recursos"),
            ("PROCEDIMENTOS METODOLÓGICOS:", "metodologia"), 
            ("AVALIAÇÃO E ACOMPANHAMENTO:", "avaliacao"), 
            ("ESTRATÉGIAS DE ACESSIBILIDADE (DUA/PEI):", "pei")
        ]

        for label, chave in campos:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            
            run_label = p.add_run(f"{label}\n")
            run_label.bold = True
            run_label.font.size = Pt(10.5)
            run_label.font.color.rgb = RGBColor(0, 51, 102)
            
            texto_limpo = str(dados.get(chave, "")).replace("**", "").replace("#", "").strip()
            adicionar_texto_formatado(p, texto_limpo)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO PLANO: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 7. EXPORTADOR PEI NÍVEL 3 (SENSORIAL / MOTOR / BENTO CARDS INTERATIVOS)
# ==============================================================================
def gerar_docx_pei_qualitativa(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10.5)

        # Cabeçalho Oficial da Escola e Prefeitura de Itabuna
        configurar_cabecalho_mestre(doc, info, "AVALIAÇÃO ADAPTADA (NÍVEL 3)", mostrar_nota=False)
        doc.add_paragraph()

        # Painel de Instruções de Mediação
        panel_info = doc.add_table(rows=1, cols=1)
        panel_info.style = 'Table Grid'
        cell_info = panel_info.cell(0, 0)
        set_cell_background(cell_info, "F1F5F9")
        p_info = cell_info.paragraphs[0]
        p_info.paragraph_format.space_after = Pt(2)
        r_info_title = p_info.add_run("📋 ORIENTAÇÕES DE MEDIAÇÃO PEDAGÓGICA (PEI NÍVEL 3):\n")
        r_info_title.bold = True
        r_info_title.font.size = Pt(9.5)
        r_info_title.font.color.rgb = RGBColor(0, 51, 102)
        
        orientacoes = [
            "Atividades de suporte severo (sensorial, motor e lúdico). Realize a mediação passo a passo.",
            "Utilize recursos concretos (massa de modelar, objetos reais, cartões, material estruturado).",
            "Assinale o nível de autonomia do estudante nas caixas de registro de cada BOX e na Rubrica Final."
        ]
        for o_txt in orientacoes:
            p_o = cell_info.add_paragraph()
            p_o.paragraph_format.space_after = Pt(1)
            p_o.add_run(f"• {o_txt}").font.size = Pt(8.5)

        doc.add_paragraph()

        # Processamento das Linhas e renderização dos CARDS DE BOX (BENTO GRID)
        linhas = str(conteudo).split('\n')
        
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if not linha:
                i += 1
                continue

            # Se for título de Atividade ou Seção Principal
            if any(x in linha.upper() for x in ["ATIVIDADE", "TEMA:", "JORNADA", "AVALIAÇÃO ADAPTADA"]) and "BOX" not in linha.upper():
                if "RUBRICA" in linha.upper():
                    break # Interrompe loop para renderizar a tabela formal no final
                p_act = doc.add_paragraph()
                p_act.paragraph_format.space_before = Pt(12)
                p_act.paragraph_format.space_after = Pt(4)
                r_act = p_act.add_run(linha.replace('**', ''))
                r_act.bold = True
                r_act.font.size = Pt(12)
                r_act.font.color.rgb = RGBColor(0, 51, 102)
                i += 1
                continue

            # Se for um Prompt de Imagem isolado
            if "[" in linha and "PROMPT IMAGEM" in linha.upper():
                adicionar_box_imagem_word(doc, "ESPAÇO PARA MATERIAL CONCRETO / ILUSTRAÇÃO SENSORIAL")
                i += 1
                continue

            # Se for um BOX (ex: "1. [BOX 1] ...", "[BOX 1] ...", "BOX 01: ...")
            if "BOX" in linha.upper():
                # Cria uma tabela estilo CARD / BENTO BOX
                card_table = doc.add_table(rows=2, cols=1)
                card_table.style = 'Table Grid'
                card_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
                card_table.columns[0].width = Inches(7.5)

                # Cabeçalho do Card
                cell_head = card_table.cell(0, 0)
                set_cell_background(cell_head, "2962FF")
                set_row_height(card_table.rows[0], 20)
                p_head = cell_head.paragraphs[0]
                p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                # Extrai o rótulo e o comando do BOX
                m_box_title = re.search(r"(\[?BOX\s*\d+\]?.*?)(?:[:\-]\s*|\s+)(.*)", linha, re.IGNORECASE)
                if m_box_title:
                    rotulo_box = m_box_title.group(1).upper().replace("[", "").replace("]", "").strip()
                    desc_box = m_box_title.group(2).strip()
                else:
                    rotulo_box = "BOX DE ATIVIDADE SENSORIAL"
                    desc_box = linha.strip()

                r_head = p_head.add_run(f"📦 {rotulo_box}")
                r_head.bold = True
                r_head.font.size = Pt(10)
                r_head.font.color.rgb = RGBColor(255, 255, 255)

                # Corpo do Card
                cell_body = card_table.cell(1, 0)
                set_cell_background(cell_body, "F8FAFC")
                p_body = cell_body.paragraphs[0]
                p_body.paragraph_format.space_after = Pt(4)
                
                adicionar_texto_formatado(p_body, desc_box)

                # Caixas de Registro do Mediador dentro do Card
                p_check = cell_body.add_paragraph()
                p_check.paragraph_format.space_before = Pt(4)
                p_check.paragraph_format.space_after = Pt(2)
                
                r_check_label = p_check.add_run("Registro do Mediador: ")
                r_check_label.bold = True
                r_check_label.font.size = Pt(8.5)
                r_check_label.font.color.rgb = RGBColor(100, 116, 139)

                r_opts = p_check.add_run("[   ] Autônomo   |   [   ] Com Apoio   |   [   ] Não Realizou")
                r_opts.font.size = Pt(8.5)
                r_opts.font.bold = True
                r_opts.font.color.rgb = RGBColor(30, 41, 59)

                p_space = doc.add_paragraph()
                p_space.paragraph_format.space_after = Pt(2)
                i += 1
                continue

            # Texto informativo comum
            p_norm = doc.add_paragraph()
            p_norm.paragraph_format.space_after = Pt(4)
            adicionar_texto_formatado(p_norm, linha)
            i += 1

        # ==============================================================================
        # 🚨 TABELA DA RUBRICA OFICIAL DE OBSERVAÇÃO PEDAGÓGICA (LEI SOBERANA PEI N3)
        # ==============================================================================
        doc.add_paragraph()
        p_rub_title = doc.add_paragraph()
        p_rub_title.paragraph_format.space_before = Pt(10)
        p_rub_title.paragraph_format.space_after = Pt(4)
        r_rub = p_rub_title.add_run("📋 RUBRICA OFICIAL DE OBSERVAÇÃO PEDAGÓGICA (PARECER QUALITATIVO)")
        r_rub.bold = True
        r_rub.font.size = Pt(11)
        r_rub.font.color.rgb = RGBColor(0, 51, 102)

        rubrica_table = doc.add_table(rows=5, cols=5)
        rubrica_table.style = 'Table Grid'
        
        col_widths = [Inches(2.5), Inches(1.1), Inches(1.1), Inches(1.2), Inches(1.6)]
        for row in rubrica_table.rows:
            set_row_height(row, 22)
            for idx_c, w in enumerate(col_widths):
                row.cells[idx_c].width = w

        headers_rub = ["DIMENSÃO COGNITIVA / MOTORA", "AUTÔNOMO ✅", "COM APOIO 🤝", "NÃO REALIZOU ❌", "OBSERVAÇÕES"]
        for idx_c, h_text in enumerate(headers_rub):
            c_h = rubrica_table.cell(0, idx_c)
            set_cell_background(c_h, "003366")
            p_h = c_h.paragraphs[0]
            p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_h = p_h.add_run(h_text)
            r_h.bold = True
            r_h.font.size = Pt(8.5)
            r_h.font.color.rgb = RGBColor(255, 255, 255)

        dimensoes_pei = [
            ("Autonomia Executiva", "Iniciativa, foco e condução motora nas tarefas"),
            ("Compreensão de Comandos", "Atendimento e resposta às instruções diretas"),
            ("Percepção Visual e Espacial", "Pareamento, seriação, identificação e encaixe"),
            ("Raciocínio Lógico-Proporcional", "Associação de quantidades, contagem e uso de materiais")
        ]

        for idx_d, (dim_nome, dim_desc) in enumerate(dimensoes_pei, start=1):
            row_cells = rubrica_table.rows[idx_d].cells
            
            p_dim = row_cells[0].paragraphs[0]
            r_dn = p_dim.add_run(f"{dim_nome}\n")
            r_dn.bold = True
            r_dn.font.size = Pt(9)
            r_dd = p_dim.add_run(dim_desc)
            r_dd.font.size = Pt(7.5)
            r_dd.font.italic = True
            r_dd.font.color.rgb = RGBColor(100, 116, 139)

            for c_idx in range(1, 4):
                p_chk = row_cells[c_idx].paragraphs[0]
                p_chk.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_chk.add_run("○").font.size = Pt(14)

            row_cells[4].paragraphs[0].add_run("____________________").font.size = Pt(8)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO EXPORTER PEI N3: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 8. ETIQUETAS DE NOTAS (FECHAMENTO TRIMESTRAL)
# ==============================================================================
def gerar_docx_etiquetas_notas(nome_arquivo, dados_alunos, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.4)
        section.left_margin = section.right_margin = Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(9.5)

        table = doc.add_table(rows=0, cols=2)
        table.style = 'Table Grid'
        table.columns[0].width = Inches(3.7)
        table.columns[1].width = Inches(3.7)

        for i in range(0, len(dados_alunos), 2):
            row = table.add_row() 
            set_row_height(row, 130)

            for j in range(2):
                if i + j < len(dados_alunos):
                    aluno = dados_alunos[i+j]
                    c = row.cells[j]
                    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    
                    p = c.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    
                    p.add_run("ESCOLA MUNICIPAL FLÁVIO JOSÉ SIMÕES COSTA\n").bold = True
                    p.add_run(f"Estudante: {aluno['nome']}\n").bold = True
                    p.add_run(f"Turma: {info['turma']} | {info['trimestre']}\n\n").font.size = Pt(8.5)
                    
                    p.add_run(f"🏛️ C1 (Vistos/Caderno): {aluno['vistos']}\n")
                    p.add_run(f"📝 C2 (Testes/Trabalhos): {aluno['teste']}\n")
                    p.add_run(f"📄 C3 (Prova Oficial): {aluno['prova']}\n")
                    
                    run_obs = p.add_run(f"* Bônus conquistados (+{aluno['bonus']} pts) embutidos acima.\n\n")
                    run_obs.font.size = Pt(8)
                    run_obs.font.italic = True
                    run_obs.font.color.rgb = RGBColor(100, 116, 139)
                    
                    run_media = p.add_run(f"📊 MÉDIA FINAL: {aluno['media']}\n")
                    run_media.bold = True
                    run_media.font.size = Pt(11)
                    
                    run_status = p.add_run(f"SITUAÇÃO: {aluno['status']}")
                    run_status.bold = True
                    if "APROVADO" in aluno['status']: run_status.font.color.rgb = RGBColor(0, 128, 0)
                    else: run_status.font.color.rgb = RGBColor(204, 0, 0)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NAS ETIQUETAS: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 9. PLANEJAMENTO TRIMESTRAL (PAISAGEM)
# ==============================================================================
def gerar_docx_planejamento_trimestral(nome_arquivo, info, dados_tabela):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[-1]
        new_width, new_height = section.page_height, section.page_width
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = new_width
        section.page_height = new_height
        section.left_margin = section.right_margin = Inches(0.4)
        section.top_margin = section.bottom_margin = Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(9)

        p_cab = doc.add_paragraph()
        p_cab.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_esc = p_cab.add_run("ESCOLA MUNICIPAL FLÁVIO JOSÉ SIMÕES COSTA\n")
        run_esc.bold = True
        run_esc.font.size = Pt(11)
        
        run_tit = p_cab.add_run(f"PLANEJAMENTO TRIMESTRAL DE MATEMÁTICA - {info['trimestre'].upper()} / 2026\n")
        run_tit.bold = True
        run_tit.font.size = Pt(10)
        run_sub = p_cab.add_run(f"SÉRIE: {info['ano']}   |   PROFESSOR: RONALDO GOMES")
        run_sub.font.size = Pt(9)
        
        doc.add_paragraph()

        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        
        widths = [Inches(1.8), Inches(3.8), Inches(2.2), Inches(3.0)]
        for i, w in enumerate(widths): table.columns[i].width = w

        headers = ['EIXO TEMÁTICO', 'CONTEÚDOS PROGRAMÁTICOS', 'HABILIDADES (BNCC)', 'METODOLOGIA APLICADA']
        for i, h in enumerate(headers):
            cell = table.cell(0, i)
            set_cell_background(cell, "003366")
            cell.text = h
            p = cell.paragraphs[0]
            p.runs[0].font.bold = True
            p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        for row_data in dados_tabela:
            row_cells = table.add_row().cells
            row_cells[0].text = row_data['eixo']
            row_cells[1].text = row_data['conteudos']
            row_cells[2].text = row_data['habilidades']
            row_cells[3].text = row_data['metodologia']
            
            for cell in row_cells:
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO PLANO TRIMESTRAL: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 10. PEI OFICIAL (PREFEITURA)
# ==============================================================================
def gerar_docx_pei_oficial(nome_arquivo, dados_aluno, habilidades, curriculo_df):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.5)
        section.left_margin = section.right_margin = Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10)

        p_cab = doc.add_paragraph()
        p_cab.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cab = p_cab.add_run("SECRETARIA MUNICIPAL DA EDUCAÇÃO\nDEPARTAMENTO DE EDUCAÇÃO BÁSICA\nCOORDENAÇÃO TÉCNICA PEDAGÓGICA DA EDUCAÇÃO ESPECIAL\n\n")
        run_cab.bold = True
        
        p_tit = doc.add_paragraph()
        p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_tit = p_tit.add_run("PLANO EDUCACIONAL INDIVIDUALIZADO - PEI")
        run_tit.bold = True
        run_tit.font.size = Pt(12)
        
        doc.add_paragraph()
        doc.add_paragraph("DADOS DO ESTUDANTE").runs[0].bold = True
        
        p_d1 = doc.add_paragraph()
        p_d1.add_run("UNIDADE ESCOLAR: ").bold = True
        p_d1.add_run("Escola Municipal Flávio José Simões Costa\t\t")
        p_d1.add_run("ANO LETIVO: ").bold = True
        p_d1.add_run("2026")
        
        p_d2 = doc.add_paragraph()
        p_d2.add_run("NOME: ").bold = True
        p_d2.add_run(f"{dados_aluno.get('nome', '')}\t\t")
        p_d2.add_run("TURMA: ").bold = True
        p_d2.add_run(f"{dados_aluno.get('turma', '')}")
        
        p_d4 = doc.add_paragraph()
        p_d4.add_run("DEFICIÊNCIA(S)/CID: ").bold = True
        p_d4.add_run(f"{dados_aluno.get('cid', '')}")
        
        doc.add_paragraph()
        doc.add_paragraph("1. PLANO DE ACESSIBILIDADE CURRICULAR").runs[0].bold = True
        
        for hab_name, hab_text in habilidades.items():
            p_h = doc.add_paragraph()
            p_h.add_run(f"• {hab_name}: ").bold = True
            p_h.add_run(str(hab_text))
        
        doc.add_paragraph()
        doc.add_paragraph("2. PLANEJAMENTO POR COMPONENTE CURRICULAR").runs[0].bold = True
        
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'DISCIPLINA'
        hdr_cells[1].text = 'OBJETIVOS APRENDIZAGEM'
        hdr_cells[2].text = 'ESTRATÉGIAS METODOLÓGICAS'
        hdr_cells[3].text = 'RECURSOS MATERIAIS'
        
        for cell in hdr_cells:
            set_cell_background(cell, "F1F5F9")
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if not curriculo_df.empty:
            for _, row in curriculo_df.iterrows():
                row_cells = table.add_row().cells
                row_cells[0].text = "MATEMÁTICA"
                row_cells[1].text = str(row.get('Objetivos de Aprendizagem', ''))
                row_cells[2].text = str(row.get('Estratégias Metodológicas', ''))
                row_cells[3].text = str(row.get('Recursos Materiais', ''))
        
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO PEI OFICIAL: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
