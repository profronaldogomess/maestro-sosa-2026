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
    
    # 4. Limpa cifrões do LaTeX
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
    
    # Fundo cinza bem claro para o espaço da imagem
    set_cell_background(cell, "F8FAFC")
    set_row_height(table.rows[0], 110) # Altura proporcional para desenho/colagem
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(35)
    
    run_icon = p.add_run("🖼️ ")
    run_icon.font.size = Pt(14)
    
    run = p.add_run(f"[{legenda_prompt.upper()}]")
    run.font.bold = True
    run.font.size = Pt(9.5)
    run.font.color.rgb = RGBColor(100, 116, 139)
    doc.add_paragraph() # Espaçamento após o box

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
# 4. GUIA DO PROFESSOR E MEDIAÇÃO
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
    run_tit = c_tit.paragraphs[0].add_run("GUIA DE MEDIAÇÃO E GABARITO COMENTADO")
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

        if any(x in l_s.upper() for x in ["JUSTIFICATIVA", "PERÍCIA", "LACUNA", "DISTRATORES"]):
            p.paragraph_format.left_indent = Inches(0.15)
            adicionar_texto_formatado(p, l_s)
            continue

        adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 5. PROVA OFICIAL (COM SUPORTE DE ATÉ 20 QUESTÕES E GABARITO LIMPO)
# ==============================================================================
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
        if num_total_q == 0: num_total_q = int(info.get('qtd_questoes', 5))
        
        label_prova = "AVALIAÇÃO ADAPTADA" if is_pei_doc else "AVALIAÇÃO DE MATEMÁTICA"
        if "SONDA" in titulo_doc.upper(): label_prova = "SONDA DE PROFICIÊNCIA"

        configurar_cabecalho_mestre(doc, info, label_prova, mostrar_nota=True)
        doc.add_paragraph()

        top_table = doc.add_table(rows=1, cols=2)
        top_table.columns[0].width = Inches(3.5)
        top_table.columns[1].width = Inches(4.0)
        
        c_orient = top_table.cell(0, 0)
        p_tit = c_orient.paragraphs[0]
        p_tit.add_run("ORIENTAÇÕES:").font.bold = True
        
        val_total = info.get('valor', '3,0')
        val_q = info.get('valor_questao', '0,3')
        
        orient_list = [
            "Leia atentamente cada enunciado.",
            "Resolva os cálculos no espaço da folha.",
            "Marque apenas uma alternativa por questão." if info.get('tipo_prova') != "2ª Chamada" else "Apresente o raciocínio de todas as questões.",
            f"Valor Total: {val_total} | Cada questão: {val_q}"
        ]
        for txt in orient_list:
            p = c_orient.add_paragraph()
            p.add_run(f"• {txt}").font.size = Pt(8.5)
            p.paragraph_format.space_after = Pt(0)

        # GRADE DE GABARITO OFICIAL
        if info.get('tipo_prova') != "2ª Chamada":
            c_gab = top_table.cell(0, 1)
            if num_total_q <= 10:
                gab_grid = c_gab.add_table(rows=num_total_q + 1, cols=6)
                gab_grid.style = 'Table Grid'
                for i, lab in enumerate(["Q", "A", "B", "C", "D", "E"]):
                    c = gab_grid.cell(0, i)
                    set_cell_background(c, "F1F5F9")
                    c.paragraphs[0].add_run(lab).font.bold = True
                for r in range(1, num_total_q + 1):
                    gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(8.5)
                    for col in range(1, 6): 
                        gab_grid.cell(r, col).paragraphs[0].add_run("○").font.size = Pt(12)
            else:
                half = (num_total_q + 1) // 2
                gab_grid = c_gab.add_table(rows=half + 1, cols=12)
                gab_grid.style = 'Table Grid'
                headers = ["Q", "A", "B", "C", "D", "E", "Q", "A", "B", "C", "D", "E"]
                for i, lab in enumerate(headers):
                    c = gab_grid.cell(0, i)
                    set_cell_background(c, "F1F5F9")
                    c.paragraphs[0].add_run(lab).font.bold = True
                
                for r in range(1, num_total_q + 1):
                    row_idx = r if r <= half else r - half
                    col_offset = 0 if r <= half else 6
                    gab_grid.cell(row_idx, col_offset).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(8.5)
                    for col in range(1, 6):
                        gab_grid.cell(row_idx, col_offset + col).paragraphs[0].add_run("○").font.size = Pt(12)

        doc.add_paragraph()

        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '450')

        for linha in corpo_bruto.split('\n'):
            l_s = linha.strip()
            if not l_s: continue

            if "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
                adicionar_box_imagem_word(doc, "ESPAÇO ILUSTRATIVO")
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
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO NO EXPORTER DE PROVA: {str(e)}")
        err_doc.save(file_stream)
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
        r_t = p_t.add_run("PLANO DE ENSINO")
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
# 7. EXPORTADOR PEI NÍVEL 3 (SENSORIAL / MOTOR)
# ==============================================================================
def gerar_docx_pei_qualitativa(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(12)

        configurar_cabecalho_mestre(doc, info, "AVALIAÇÃO ADAPTADA (NÍVEL 3)", mostrar_nota=False)
        doc.add_paragraph()

        linhas = str(conteudo).split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            
            if "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
                adicionar_box_imagem_word(doc, "ESPAÇO PARA ATIVIDADE MOTOR/VISUAL")
                continue

            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(8)

            if "BOX" in l_s.upper() or "QUESTÃO" in l_s.upper():
                p.paragraph_format.space_before = Pt(12)
                run = p.add_run(l_s.replace('**', ''))
                run.bold = True
                run.font.size = Pt(13)
                run.font.color.rgb = RGBColor(0, 51, 102)
            else:
                adicionar_texto_formatado(p, l_s)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO PEI N3: {str(e)}"); err_doc.save(file_stream)
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
