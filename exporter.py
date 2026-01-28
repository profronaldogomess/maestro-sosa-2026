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

# --- FUNÇÃO AUXILIAR PARA ALTURA DE LINHA ---
def set_row_height(row, height_cm):
    """Define a altura exata de uma linha em centímetros"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_cm * 567))) # 1cm = 567 twips
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

# --- FUNÇÃO DO ALUNO REFORMULADA (V25) ---
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.6)
    section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

    # --- CABEÇALHO IDENTICO AO PRINT (Tabela 3x5) ---
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Ajuste de larguras
    table.columns[0].width = Inches(0.8) # Logo
    table.columns[1].width = Inches(2.8) # Nome/Prof
    table.columns[2].width = Inches(1.0) # Turma
    table.columns[3].width = Inches(1.0) # Data
    table.columns[4].width = Inches(1.2) # Trimestre

    # Mesclagens
    c_logo = table.cell(0, 0).merge(table.cell(2, 0)) 
    c_escola = table.cell(0, 1).merge(table.cell(0, 4)) 
    c_aluno = table.cell(1, 1).merge(table.cell(1, 4)) 

    # Alturas das Linhas (Sua solicitação de espaço)
    set_row_height(table.rows[1], 1.2) # Linha do Aluno mais alta
    set_row_height(table.rows[2], 0.6) # Linha de baixo mais estreita (strip)

    # 1. Logo
    if os.path.exists("logo_escola.png"):
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.7))

    # 2. Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold, run_esc.font.size = True, Pt(11)

    # 3. Campo Aluno (Espaçoso)
    p_alu = c_aluno.paragraphs[0]
    p_alu.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_alu.add_run("ALUNO(A): _______________________________________________________").font.size = Pt(10)

    # 4. Linha de Baixo (Strip)
    table.cell(2, 1).paragraphs[0].add_run(f"PROF.: Ronaldo Gomes").font.size = Pt(9)
    table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('turma', '')}").font.size = Pt(9)
    table.cell(2, 3).paragraphs[0].add_run(f"DATA: __/__/2026").font.size = Pt(9)
    
    # Trimestre: Negrito e Centralizado
    c_trim = table.cell(2, 4)
    p_trim = c_trim.paragraphs[0]
    p_trim.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_trim = p_trim.add_run(f"{info.get('trimestre', 'I')} TRIMESTRE")
    run_trim.font.bold, run_trim.font.size = True, Pt(8)

    doc.add_paragraph() 

    # --- TÍTULO CENTRALIZADO E NEGRITO ---
    p_tit = doc.add_paragraph()
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tit = p_tit.add_run(titulo_doc.upper())
    run_tit.font.bold, run_tit.font.size = True, Pt(12)

    # --- LAYOUT EM DUAS COLUNAS (Tabela Invisível) ---
    partes = re.split(r'(QUESTÃO \d+\.)', conteudo)
    questoes_lista = []
    if len(partes) > 1:
        for i in range(1, len(partes), 2):
            questoes_lista.append(partes[i] + partes[i+1])
    else:
        questoes_lista = [conteudo]

    col_table = doc.add_table(rows=(len(questoes_lista) + 1) // 2, cols=2)
    col_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    for idx, q_text in enumerate(questoes_lista):
        cell = col_table.cell(idx // 2, idx % 2)
        linhas = q_text.strip().split('\n')
        
        for linha in linhas:
            if not linha.strip(): continue
            p = cell.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Formatação: QUESTÃO X. em negrito, restante normal
            if "QUESTÃO" in linha.upper() and "." in linha:
                prefixo, resto = linha.split(".", 1)
                p.add_run(prefixo + ".").font.bold = True
                p.add_run(resto)
            # Prompt de imagem entre colchetes
            elif "PROMPT" in linha.upper() or "IMAGEM" in linha.upper():
                run_img = p.add_run(f"[{linha.strip()}]")
                run_img.font.italic, run_img.font.size = True, Pt(8)
            # Alternativas em linhas separadas
            elif re.match(r'^[A-E][\)\-]', linha.strip().upper()):
                p.add_run(linha.strip())
            else:
                p.add_run(linha.strip())

        # Espaço para questões abertas (4 linhas)
        if not any(re.search(r'[A-E][\)\-]', l) for l in linhas):
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

# --- AS DEMAIS FUNÇÕES PERMANECEM INALTERADAS ---

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

def gerar_pptx_v24(titulo_doc, conteudo_ia):
    prs = Presentation()
    slides_raw = re.findall(r"\[SLIDE.*?\](.*?)(?=\[SLIDE|$)", conteudo_ia, re.DOTALL)
    
    for i, bloco in enumerate(slides_raw):
        layout_idx = 0 if i == 0 else 1
        slide = prs.slides.add_slide(prs.slide_layouts[layout_idx])
        
        titulo = re.search(r"(?:TITULO|TÍTULO).*?:(.*?)\n", bloco, re.IGNORECASE)
        visual = re.search(r"(?:CONTEÚDO VISUAL|CONTEUDO VISUAL).*?:(.*?)(?=PROMPT|SCRIPT|NOTA|$)", bloco, re.DOTALL | re.IGNORECASE)
        script = re.search(r"(?:SCRIPT DO PROFESSOR).*?:(.*?)(?=NOTA|$)", bloco, re.DOTALL | re.IGNORECASE)
        
        if titulo:
            slide.shapes.title.text = titulo.group(1).strip().replace("**", "")
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
