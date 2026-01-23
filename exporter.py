from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import io

def gerar_docx_profissional(titulo, conteudo_raw, logo_escola="logo_escola.png", logo_ronaldo="logo.png"):
    doc = Document()
    
    # --- CONFIGURAÇÃO DE MARGENS ---
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)
        section.left_margin = Inches(0.7)
        section.right_margin = Inches(0.7)

    # --- CABEÇALHO COM DUAS LOGOS ---
    header = doc.sections[0].header
    htable = header.add_table(1, 3, Inches(7))
    htable.columns[0].width = Inches(1.2)
    htable.columns[1].width = Inches(4.6)
    htable.columns[2].width = Inches(1.2)

    # Logo Escola (Esquerda)
    try:
        run_esc = htable.rows[0].cells[0].paragraphs[0].add_run()
        run_esc.add_picture(logo_escola, width=Inches(0.8))
    except: pass

    # Texto Central (Dados da Escola)
    info = htable.rows[0].cells[1].paragraphs[0]
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_info = info.add_run("ESTADO DA BAHIA\nPREFEITURA MUNICIPAL DE ITABUNA\nSECRETARIA MUNICIPAL DE EDUCAÇÃO\n")
    run_info.font.bold = True
    run_info.font.size = Pt(10)
    run_info2 = info.add_run(f"COMPONENTE CURRICULAR: MATEMÁTICA\nPROFESSOR: RONALDO GOMES")
    run_info2.font.size = Pt(9)

    # Sua Logo (Direita)
    try:
        run_ron = htable.rows[0].cells[2].paragraphs[0].add_run()
        run_ron.add_picture(logo_ronaldo, width=Inches(0.8))
        htable.rows[0].cells[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
    except: pass

    # --- TÍTULO ---
    doc.add_paragraph()
    t = doc.add_heading(titulo, 1)
    t.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # --- CORPO DO TEXTO (LÓGICA DE LIMPEZA) ---
    # Remove os MARKERS para o documento final ficar limpo
    texto_limpo = conteudo_raw.replace("MARKER_LOUSA", "").replace("MARKER_FOLHA", "--- ATIVIDADE ---").replace("MARKER_GABARITO", "--- GABARITO ---").replace("MARKER_IMAGENS", "")
    
    for linha in texto_limpo.split('\n'):
        p = doc.add_paragraph(linha)
        if "QUESTÃO" in linha.upper():
            p.style.font.bold = True
            p.paragraph_format.space_before = Pt(12)

    # Salvar em memória
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream