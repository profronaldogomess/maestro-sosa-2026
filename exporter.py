from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import io

def gerar_docx_profissional(titulo, conteudo_raw, info_extra={}, logo_escola="logo_escola.png"):
    doc = Document()
    
    # Margens Estreitas
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

    # --- CONSTRUÇÃO DA TABELA DE CABEÇALHO (Grade 3x5) ---
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Ajuste de Larguras (Total ~7.5 inches)
    # Col 0: Logo | Col 1-3: Centro | Col 4: Trimestre/Nota
    for cell in table.columns[0].cells: cell.width = Inches(1.1)
    for cell in table.columns[4].cells: cell.width = Inches(1.4)

    # --- MESCLAGENS PARA BATER COM A IMAGEM ---
    # 1. Logo (Coluna 0 mescla as 3 linhas)
    c_logo = table.cell(0, 0).merge(table.cell(2, 0))
    
    # 2. Nome da Escola (Linha 0, Colunas 1 a 3)
    c_escola = table.cell(0, 1).merge(table.cell(0, 3))
    
    # 3. Aluno (Linha 1, Colunas 1 a 3)
    c_aluno = table.cell(1, 1).merge(table.cell(1, 3))
    
    # 4. Trimestre e Tipo (Coluna 4, Linhas 0 e 1)
    c_trim = table.cell(0, 4).merge(table.cell(1, 4))

    # --- PREENCHIMENTO DOS DADOS ---
    
    # Logo
    try:
        run_logo = c_logo.paragraphs[0].add_run()
        run_logo.add_picture(logo_escola, width=Inches(0.9))
        c_logo.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    except: pass

    # Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold = True
    run_esc.font.size = Pt(12)

    # Aluno
    p_alu = c_aluno.paragraphs[0]
    p_alu.add_run(f"ALUNO(A): ________________________________________________")
    
    # Linha de Baixo (Prof / Turma / Data)
    p_prof = table.cell(2, 1).paragraphs[0]
    p_prof.add_run(f"PROF. Ronaldo Gomes").font.italic = True
    
    p_turma = table.cell(2, 2).paragraphs[0]
    p_turma.add_run(f"TURMA: {info_extra.get('turma', '______')}")
    
    p_data = table.cell(2, 3).paragraphs[0]
    p_data.add_run(f"DATA: ____/____/________")

    # Lado Direito (Trimestre e Nota)
    c_trim.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_trim = c_trim.paragraphs[0]
    p_trim.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_trim.add_run(f"{info_extra.get('trimestre', 'III')} TRIMESTRE\n").font.bold = True
    p_trim.add_run(f"{titulo}").font.size = Pt(9)

    p_nota = table.cell(2, 4).paragraphs[0]
    p_nota.add_run("NOTA: ________")

    # --- CORPO DO TEXTO ---
    doc.add_paragraph()
    texto_limpo = conteudo_raw.replace("MARKER_LOUSA", "").replace("MARKER_FOLHA", "").replace("MARKER_GABARITO", "\n--- GABARITO ---\n").replace("MARKER_IMAGENS", "")
    
    for linha in texto_limpo.split('\n'):
        if linha.strip():
            p = doc.add_paragraph(linha.strip())
            if "QUESTÃO" in linha.upper():
                p.style.font.bold = True
                p.paragraph_format.space_before = Pt(12)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
