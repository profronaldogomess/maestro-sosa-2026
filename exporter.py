import os
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def gerar_docx_profissional(titulo, conteudo_raw, info_extra={}, logo_escola="logo_escola.png"):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_logo = os.path.join(diretorio_atual, logo_escola)

    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Ajuste de Larguras
    table.columns[0].width = Inches(1.1)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(1.2)
    table.columns[3].width = Inches(1.6)
    table.columns[4].width = Inches(1.4)

    c_logo = table.cell(0, 0).merge(table.cell(2, 0))
    c_escola = table.cell(0, 1).merge(table.cell(0, 3))
    c_aluno = table.cell(1, 1).merge(table.cell(1, 3))
    c_trim = table.cell(0, 4).merge(table.cell(1, 4))

    # 1. Logo
    c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_logo = c_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists(caminho_logo):
        p_logo.add_run().add_picture(caminho_logo, width=Inches(0.9))

    # 2. Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold, run_esc.font.size = True, Pt(12)

    # 3. Campo Aluno (LIMPO)
    p_alu = c_aluno.paragraphs[0]
    p_alu.add_run("ALUNO(A): ").font.size = Pt(10)
    
    # 4. Linha de Baixo (LIMPO)
    table.cell(2, 1).paragraphs[0].add_run("PROF. Ronaldo Gomes").font.italic = True
    table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info_extra.get('turma', '')}")
    
    p_data = table.cell(2, 3).paragraphs[0]
    p_data.add_run("DATA:    /    /    ")

    # 5. Lado Direito
    c_trim.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_trim = c_trim.paragraphs[0]
    p_trim.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t1 = p_trim.add_run(f"{info_extra.get('trimestre', 'III')} TRIMESTRE\n")
    run_t1.font.bold = True
    run_t1.font.size = Pt(11)
    p_trim.add_run(f"{titulo}").font.size = Pt(9)

    # 6. Campo Nota (LIMPO)
    table.cell(2, 4).paragraphs[0].add_run(" NOTA: ")

    # Corpo do Texto
    doc.add_paragraph()
    texto_limpo = conteudo_raw.replace("MARKER_LOUSA", "").replace("MARKER_FOLHA", "").replace("MARKER_GABARITO", "\n--- GABARITO ---\n").replace("MARKER_IMAGENS", "")
    for linha in texto_limpo.split('\n'):
        if linha.strip():
            p = doc.add_paragraph(linha.strip())
            if "QUESTÃO" in linha.upper() or "ATIVIDADE" in linha.upper():
                p.style.font.bold, p.paragraph_format.space_before = True, Pt(12)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
