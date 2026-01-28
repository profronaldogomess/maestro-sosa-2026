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
# FUNÇÕES DE UTILIDADE TÉCNICA (NÃO ALTERAR)
# ==============================================================================
def set_row_height(row, height_cm):
    """Força a altura da linha da tabela no Word (Prensa de Altura)"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_cm * 567))) # 1cm = 567 twips
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

def prevent_row_break(table):
    """Impede que as questões sejam cortadas entre uma página e outra"""
    for row in table.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        keepNext = OxmlElement('w:cantSplit')
        trPr.append(keepNext)

# ==============================================================================
# 1. MATERIAL DO ALUNO V25 (LAYOUT DE ELITE - DUAS COLUNAS)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    # Margens otimizadas para 2 colunas
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.7)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- CABEÇALHO REENGENHARIZADO (3x5) ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    
    # Ajuste de Larguras das Colunas
    widths = [Inches(0.9), Inches(3.0), Inches(1.0), Inches(1.0), Inches(1.2)]
    for i, width in enumerate(widths):
        header_table.columns[i].width = width

    # Mesclagens
    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0)) 
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 4)) 
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4)) 

    # APLICAÇÃO DAS ALTURAS (Sua solicitação específica)
    set_row_height(header_table.rows[0], 0.6) # Escola
    set_row_height(header_table.rows[1], 1.2) # ALUNO (ESPAÇO MAIOR)
    set_row_height(header_table.rows[2], 0.6) # STRIP (MAIS ESTREITO)

    # 1. Logo
    if os.path.exists("logo_escola.png"):
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.75))

    # 2. Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold, run_esc.font.size = True, Pt(11)

    # 3. Campo Aluno (Com espaço maior)
    p_alu = c_aluno.paragraphs[0]
    p_alu.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    run_alu_label = p_alu.add_run("ALUNO(A): ")
    run_alu_label.font.size = Pt(10)
    p_alu.add_run("_________________________________________________________________")

    # 4. Linha Strip (Prof, Turma, Data, Trimestre)
    p_p = header_table.cell(2, 1).paragraphs[0]
    p_p.add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    p_t = header_table.cell(2, 2).paragraphs[0]
    p_t.add_run(f"TURMA: {info.get('turma', '6º __')}").font.size = Pt(9)
    p_d = header_table.cell(2, 3).paragraphs[0]
    p_d.add_run("DATA: ___/___/___").font.size = Pt(9)
    
    # Trimestre (NEGRITO E CENTRALIZADO)
    c_tri = header_table.cell(2, 4)
    p_tri = c_tri.paragraphs[0]
    p_tri.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tri = p_tri.add_run(f"{info.get('trimestre', 'I')} TRIMESTRE")
    run_tri.font.bold, run_tri.font.size = True, Pt(9)

    doc.add_paragraph() 

    # --- TÍTULO CENTRALIZADO E NEGRITO ---
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tit = p_tit.add_run(titulo_doc.upper())
    run_tit.font.bold, run_tit.font.size = True, Pt(12)

    # --- LÓGICA DE DUAS COLUNAS (TABELA INVISÍVEL) ---
    # Fatiamos o conteúdo usando o marcador QUESTÃO
    partes_questoes = re.split(r'(QUESTÃO\s+\d+\.)', conteudo, flags=re.IGNORECASE)
    
    lista_final = []
    if len(partes_questoes) > 1:
        for i in range(1, len(partes_questoes), 2):
            lista_final.append(partes_questoes[i] + partes_questoes[i+1])
    else:
        lista_final = [conteudo]

    # Criar tabela de 2 colunas
    main_table = doc.add_table(rows=(len(lista_final) + 1) // 2, cols=2)
    main_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    for idx, q_text in enumerate(lista_final):
        cell = main_table.cell(idx // 2, idx % 2)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        
        linhas = q_text.strip().split('\n')
        for linha in linhas:
            if not linha.strip(): continue
            p = cell.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Negrito apenas no QUESTÃO X.
            if "QUESTÃO" in linha.upper() and "." in linha:
                partes_linha = linha.split(".", 1)
                p.add_run(partes_linha[0] + ".").font.bold = True
                if len(partes_linha) > 1:
                    p.add_run(partes_linha[1])
            
            # Prompt de Imagem entre colchetes
            elif "PROMPT" in linha.upper() or "IMAGEM" in linha.upper():
                run_img = p.add_run(f"[{linha.strip()}]")
                run_img.font.italic, run_img.font.size = True, Pt(8)
                run_img.font.color.rgb = RGBColor(100, 100, 100)
            
            # Alternativas
            elif re.match(r'^[A-E][\)\-]', linha.strip().upper()):
                p.add_run(linha.strip())
            
            else:
                p.add_run(linha.strip())

        # Se for questão aberta, desenha as 4 linhas
        tem_alternativas = any(re.search(r'^[A-E][\)\-]', l.strip().upper()) for l in linhas)
        if not tem_alternativas:
            for _ in range(4):
                cell.add_paragraph("_____________________________________________")

    # --- RODAPÉ PROFISSIONAL ---
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
