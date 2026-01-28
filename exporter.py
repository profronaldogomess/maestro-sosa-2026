import os
import io
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Inches, Pt

# ==============================================================================
# FUNÇÃO AUXILIAR: AJUSTE DE ALTURA DE LINHA (PRENSA)
# ==============================================================================
def set_row_height(row, height_cm):
    """Define a altura exata de uma linha de tabela no Word"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_cm * 567))) # 1cm = 567 twips
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

# ==============================================================================
# 1. MATERIAL DO ALUNO (DESIGN DE ELITE V25 - DUAS COLUNAS)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.7)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- CABEÇALHO (3x5) ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    
    widths = [Inches(0.9), Inches(3.0), Inches(1.0), Inches(1.0), Inches(1.2)]
    for i, width in enumerate(widths):
        header_table.columns[i].width = width

    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0)) 
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 4)) 
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4)) 

    set_row_height(header_table.rows[0], 0.6) 
    set_row_height(header_table.rows[1], 1.2) # Espaço para o aluno escrever
    set_row_height(header_table.rows[2], 0.6) 

    # 1. Logo Centralizada
    if os.path.exists("logo_escola.png"):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER # Centraliza Vertical
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER # Centraliza Horizontal
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.75))

    # 2. Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold, run_esc.font.size = True, Pt(11)

    # 3. Campo Aluno (Sem linha, apenas o rótulo)
    c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_alu = c_aluno.paragraphs[0]
    run_alu = p_alu.add_run("ALUNO(A):")
    run_alu.font.size = Pt(10)

    # 4. Linha Strip (Prof, Turma, Data, Trimestre)
    header_table.cell(2, 1).paragraphs[0].add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('turma', '6º __')}").font.size = Pt(9)
    # Data com mais espaço
    header_table.cell(2, 3).paragraphs[0].add_run("DATA: ____/____/2026").font.size = Pt(9)
    
    c_tri = header_table.cell(2, 4)
    p_tri = c_tri.paragraphs[0]
    p_tri.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tri = p_tri.add_run(f"{info.get('trimestre', 'I')} TRIMESTRE")
    run_tri.font.bold, run_tri.font.size = True, Pt(9)

    doc.add_paragraph() 

    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tit = p_tit.add_run(titulo_doc.upper())
    run_tit.font.bold, run_tit.font.size = True, Pt(12)

    # --- DUAS COLUNAS ---
    partes_da_ia = re.split(r'(QUESTÃO\s+\d+\.)', conteudo, flags=re.IGNORECASE)
    lista_de_questoes = []
    if len(partes_da_ia) > 1:
        for i in range(1, len(partes_da_ia), 2):
            lista_de_questoes.append(partes_da_ia[i] + partes_da_ia[i+1])
    else:
        lista_de_questoes = [conteudo]

    main_table = doc.add_table(rows=(len(lista_de_questoes) + 1) // 2, cols=2)
    main_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    for idx, q_text in enumerate(lista_de_questoes):
        cell = main_table.cell(idx // 2, idx % 2)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        
        linhas_questao = q_text.strip().split('\n')
        for linha in linhas_questao:
            if not linha.strip(): continue
            p = cell.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            if "QUESTÃO" in linha.upper() and "." in linha:
                partes_linha = linha.split(".", 1)
                p.add_run(partes_linha[0] + ".").font.bold = True
                if len(partes_linha) > 1: p.add_run(partes_linha[1])
            elif "PROMPT" in linha.upper() or "IMAGEM" in linha.upper():
                run_img = p.add_run(f"[{linha.strip()}]")
                run_img.font.italic, run_img.font.size = True, Pt(8)
                run_img.font.color.rgb = RGBColor(100, 100, 100)
            elif re.match(r'^[A-E][\)\-]', linha.strip().upper()):
                p.add_run(linha.strip())
            else:
                p.add_run(linha.strip())

        # --- LINHAS DE RESPOSTA QUE VÃO ATÉ O FINAL ---
        tem_alternativas = any(re.search(r'^[A-E][\)\-]', l.strip().upper()) for l in linhas_questao)
        if not tem_alternativas:
            for _ in range(4):
                p_linha = cell.add_paragraph()
                # Aumentei a quantidade de underlines para preencher a coluna
                p_linha.add_run("_________________________________________________")

    # --- RODAPÉ ---
    footer = section.footer
    p_foot = footer.paragraphs[0]
    p_foot.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_foot.add_run("__________________________________________________________________________\n").font.color.rgb = RGBColor(200, 200, 200)
    run_fin = p_foot.add_run("Material produzido pelo Professor Ronaldo Gomes dos Santos Filho • Itabuna/BA • 2026")
    run_fin.font.size, run_fin.font.italic = Pt(8), True

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 2. GUIA DO PROFESSOR (PRESERVADO)
# ==============================================================================
def gerar_docx_professor_v24(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
    table = doc.add_table(rows=3, cols=3)
    table.style = 'Table Grid'
    if os.path.exists("logo_escola.png"):
        table.cell(0, 0).paragraphs[0].add_run().add_picture("logo_escola.png", width=Inches(0.7))
    table.cell(0, 1).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    table.cell(0, 2).paragraphs[0].add_run("GUIA DO PROFESSOR").font.bold = True
    table.cell(1, 0).merge(table.cell(1, 1))
    table.cell(1, 0).paragraphs[0].add_run(f"Professor: Ronaldo Gomes")
    table.cell(1, 2).paragraphs[0].add_run(f"Ano: {info.get('ano', '')}")
    table.cell(2, 0).merge(table.cell(2, 1))
    table.cell(2, 0).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}")
    table.cell(2, 2).paragraphs[0].add_run("Data: [ / / 2026 ]")
    doc.add_paragraph()
    for linha in conteudo.split('\n'):
        p = doc.add_paragraph(linha.strip())
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. PLANO PEDAGÓGICO (PRESERVADO)
# ==============================================================================
def gerar_docx_plano_pedagogico_v18(titulo_arquivo, dados, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
    table = doc.add_table(rows=3, cols=3)
    table.style = 'Table Grid'
    if os.path.exists("logo_escola.png"):
        table.cell(0, 0).paragraphs[0].add_run().add_picture("logo_escola.png", width=Inches(0.7))
    table.cell(0, 1).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    table.cell(0, 2).paragraphs[0].add_run("PLANO DE ENSINO SEMANAL").font.bold = True
    table.cell(1, 0).merge(table.cell(1, 1))
    table.cell(1, 0).paragraphs[0].add_run(f"Professor: Ronaldo Gomes")
    table.cell(1, 2).paragraphs[0].add_run(f"Ano: {info.get('ano', '')}")
    table.cell(2, 0).merge(table.cell(2, 1))
    table.cell(2, 0).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}")
    table.cell(2, 2).paragraphs[0].add_run("Data: [ / / 2026 ]")
    doc.add_paragraph()
    campos = [("CONTEÚDO GERAL EIXO:", "geral"), ("CONTEÚDOS ESPECÍFICOS:", "especificos"), ("OBJETIVOS DE ENSINO:", "objetivos"), ("METODOLOGIA:", "metodologia"), ("AVALIAÇÃO:", "avaliacao"), ("OBSERVAÇÃO:", "observacao"), ("ADAPTAÇÃO PEI:", "pei")]
    for label, chave in campos:
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.add_run(label).font.bold = True
        texto = str(dados.get(chave, "")).replace(label, "").strip()
        if texto.startswith(":"): texto = texto[1:].strip()
        p.add_run(f" {texto}")
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 4. APRESENTAÇÃO PPTX (PRESERVADO)
# ==============================================================================
def gerar_pptx_v24(titulo_doc, conteudo_ia):
    prs = Presentation()
    slides_raw = re.findall(r"\[SLIDE.*?\](.*?)(?=\[SLIDE|$)", conteudo_ia, re.DOTALL)
    for i, bloco in enumerate(slides_raw):
        layout_idx = 0 if i == 0 else 1
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
        titulo = re.search(r"(?:TITULO|TÍTULO).*?:(.*?)\n", bloco, re.IGNORECASE)
        visual = re.search(r"(?:CONTEÚDO VISUAL|CONTEUDO VISUAL).*?:(.*?)(?=PROMPT|SCRIPT|NOTA|$)", bloco, re.DOTALL | re.IGNORECASE)
        script = re.search(r"(?:SCRIPT DO PROFESSOR).*?:(.*?)(?=NOTA|$)", bloco, re.DOTALL | re.IGNORECASE)
        if titulo: slide.shapes.title.text = titulo.group(1).strip().replace("**", "")
        if visual and len(slide.placeholders) > 1:
            body_shape = slide.placeholders[1]
            body_shape.text = visual.group(1).strip().replace("**", "")
        if script:
            notas = slide.notes_slide.notes_text_frame
            notas.text = script.group(1).strip().replace("**", "")
    file_stream = io.BytesIO()
    prs.save(file_stream)
    file_stream.seek(0)
    return file_stream
