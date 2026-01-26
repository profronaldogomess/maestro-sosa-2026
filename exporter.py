import os
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from pptx import Presentation
from pptx.util import Inches, Pt
import re

def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

    # --- CABEÇALHO IDENTICO AO PRINT (Tabela 3x5) ---
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    # Ajuste de larguras para o design do print
    table.columns[0].width = Inches(1.0) # Logo
    table.columns[1].width = Inches(2.6) # Nome/Prof
    table.columns[2].width = Inches(1.0) # Turma
    table.columns[3].width = Inches(1.0) # Data
    table.columns[4].width = Inches(1.2) # Trimestre

    # Mesclagens para o Design do Print
    c_logo = table.cell(0, 0).merge(table.cell(2, 0)) 
    c_escola = table.cell(0, 1).merge(table.cell(0, 4)) 
    c_aluno = table.cell(1, 1).merge(table.cell(1, 4)) 

    # 1. Logo
    if os.path.exists("logo_escola.png"):
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.8))

    # 2. Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold, run_esc.font.size = True, Pt(11)

    # 3. Campo Aluno
    c_aluno.paragraphs[0].add_run("ALUNO(A):").font.size = Pt(10)

    # 4. Linha de Baixo
    table.cell(2, 1).paragraphs[0].add_run(f"PROF.: Ronaldo Gomes").font.size = Pt(9)
    table.cell(2, 2).paragraphs[0].add_run(f"TURMA:").font.size = Pt(9)
    table.cell(2, 3).paragraphs[0].add_run(f"DATA:").font.size = Pt(9)
    table.cell(2, 4).paragraphs[0].add_run(f"{info.get('trimestre', 'I')} TRIMESTRE").font.size = Pt(8)

    doc.add_paragraph() 

    # Conteúdo Justificado
    for linha in conteudo.split('\n'):
        if not linha.strip(): continue
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        if any(x in linha.upper() for x in ["QUESTÃO", "ATIVIDADE", "PASSO", "PARA LEMBRAR", "RESPOSTA:"]):
            p.add_run(linha.strip()).font.bold = True
        else:
            p.add_run(linha.strip())
    
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

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
    
    # Regex para capturar cada bloco de slide
    slides_raw = re.findall(r"\[SLIDE.*?\](.*?)(?=\[SLIDE|$)", conteudo_ia, re.DOTALL)
    
    for i, bloco in enumerate(slides_raw):
        # Escolhe um layout (0 = Título, 1 = Título e Conteúdo)
        layout = prs.slide_layouts[1] if i > 0 else prs.slide_layouts[0]
        slide = prs.slides.add_slide(layout)
        
        # Extração de sub-campos dentro do bloco do slide
        titulo = re.search(r"TITULO.*?:(.*?)\n", bloco)
        visual = re.search(r"CONTEÚDO VISUAL.*?:(.*?)(?=PROMPT|SCRIPT|NOTA|$)", bloco, re.DOTALL)
        script = re.search(r"SCRIPT DO PROFESSOR.*?:(.*?)(?=NOTA|$)", bloco, re.DOTALL)
        
        # Preenche o Título
        if titulo:
            slide.shapes.title.text = titulo.group(1).strip().replace("**", "")
        
        # Preenche o Conteúdo Visual (Corpo do Slide)
        if visual and i > 0:
            tf = slide.placeholders[1].text_frame
            tf.text = visual.group(1).strip().replace("**", "")
            
        # Preenche o Script do Professor (Notas do Orador)
        if script:
            notas = slide.notes_slide.notes_text_frame
            notas.text = script.group(1).strip().replace("**", "")

    file_stream = io.BytesIO()
    prs.save(file_stream)
    file_stream.seek(0)
    return file_stream
