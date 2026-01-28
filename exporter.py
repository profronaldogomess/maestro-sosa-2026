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
from datetime import datetime

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
# 1. MATERIAL DO ALUNO TÍPICO (DESIGN DE ELITE V25 - DUAS COLUNAS)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.7)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(0.8), Inches(1.7), Inches(1.2)]
    for i, width in enumerate(widths):
        header_table.columns[i].width = width

    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0)) 
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 4)) 
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4)) 

    set_row_height(header_table.rows[0], 0.6) 
    set_row_height(header_table.rows[1], 1.2) 
    set_row_height(header_table.rows[2], 0.6) 

    if os.path.exists("logo_escola.png"):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER 
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER 
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.75))

    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True

    c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    c_aluno.paragraphs[0].add_run("ALUNO(A):").font.size = Pt(10)

    header_table.cell(2, 1).paragraphs[0].add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    header_table.cell(2, 2).paragraphs[0].add_run("TURMA:").font.size = Pt(9)
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

    partes_da_ia = re.split(r'(QUESTÃO\s+\d+\.)', conteudo, flags=re.IGNORECASE)
    lista_final = []
    if len(partes_da_ia) > 1:
        for i in range(1, len(partes_da_ia), 2):
            lista_final.append(partes_da_ia[i] + partes_da_ia[i+1])
    else:
        lista_final = [conteudo]

    main_table = doc.add_table(rows=(len(lista_final) + 1) // 2, cols=2)
    main_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    for idx, q_text in enumerate(lista_final):
        cell = main_table.cell(idx // 2, idx % 2)
        cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
        linhas_brutas = q_text.strip().split('\n')
        p = cell.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        match_marcador = re.search(r'QUESTÃO\s+\d+\.', q_text, re.IGNORECASE)
        marcador = match_marcador.group() if match_marcador else ""
        p.add_run(marcador + " ").font.bold = True
        
        corpo_limpo = q_text.replace(marcador, "", 1).lstrip()
        linhas_corpo = corpo_limpo.split('\n')
        enunciado_andamento = True
        
        for linha in linhas_corpo:
            l_s = linha.strip()
            if not l_s: continue
            if re.match(r'^[A-E][\)\s\-]', l_s.upper()) or "PROMPT" in l_s.upper() or "IMAGEM" in l_s.upper():
                enunciado_andamento = False
                p = cell.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                if "PROMPT" in l_s.upper() or "IMAGEM" in l_s.upper():
                    run_img = p.add_run(f"[{l_s}]")
                    run_img.font.italic, run_img.font.size = True, Pt(8)
                    run_img.font.color.rgb = RGBColor(100, 100, 100)
                else:
                    texto_alt = re.sub(r'^([A-E])[\s\-\.]*', r'\1) ', l_s.upper())
                    p.add_run(texto_alt)
            else:
                if enunciado_andamento:
                    p.add_run(l_s + " ")
                else:
                    p = cell.add_paragraph()
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    p.add_run(l_s)

        tem_alternativas = any(re.search(r'^[A-E][\)\s\-]', l.strip().upper()) for l in linhas_corpo)
        if not tem_alternativas:
            for _ in range(4):
                cell.add_paragraph("_________________________________________________")

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run("_" * 85 + "\n").font.color.rgb = RGBColor(200, 200, 200)
    run_fin = footer.add_run("Material produzido pelo Professor Ronaldo Gomes dos Santos Filho • Itabuna/BA • 2026")
    run_fin.font.size, run_fin.font.italic = Pt(8), True

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    # Margens estreitas para caber mais conteúdo
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- CABEÇALHO DE ELITE (IDENTIDADE VISUAL IGUAL AO DO ALUNO) ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(0.8), Inches(1.7), Inches(1.2)]
    for i, width in enumerate(widths):
        header_table.columns[i].width = width

    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0)) 
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 4)) 
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4)) 

    if os.path.exists("logo_escola.png"):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER 
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER 
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.75))

    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True

    c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    c_aluno.paragraphs[0].add_run("GUIA DE REGÊNCIA E ESQUEMA DE LOUSA").font.size = Pt(11)

    header_table.cell(2, 1).paragraphs[0].add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    header_table.cell(2, 2).paragraphs[0].add_run(f"ANO: {info.get('ano', '')}").font.size = Pt(9)
    header_table.cell(2, 3).paragraphs[0].add_run(f"DATA: {datetime.now().strftime('%d/%m/%Y')}").font.size = Pt(9)
    header_table.cell(2, 4).paragraphs[0].add_run(f"{info.get('trimestre', 'I')} TRIM").font.size = Pt(9)

    doc.add_paragraph() # Espaço

    # --- CORPO EM DUAS COLUNAS (TABELA INVISÍVEL) ---
    main_table = doc.add_table(rows=1, cols=2)
    main_table.allow_autofit = False
    col_esq = main_table.cell(0, 0)
    col_dir = main_table.cell(0, 1)

    # Lógica de Divisão: Se você escrever [COLUNA_2] no texto, ele quebra ali.
    # Se não escrever, ele divide o texto ao meio automaticamente.
    if "[COLUNA_2]" in conteudo:
        partes = conteudo.split("[COLUNA_2]")
        texto_esq = partes[0].split('\n')
        texto_dir = partes[1].split('\n')
    else:
        linhas = [l.strip() for l in conteudo.split('\n') if l.strip()]
        meio = len(linhas) // 2
        texto_esq = linhas[:meio]
        texto_dir = linhas[meio:]

    def processar_celula(celula, linhas_texto):
        for linha in linhas_texto:
            if not linha.strip(): continue
            p = celula.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # Identifica Títulos (Maiúsculas ou Início com Número)
            is_titulo = linha.isupper() or (len(linha) > 0 and linha[0].isdigit() and "." in linha[:3])
            
            # Identifica Prompts (Texto entre colchetes)
            if "[" in linha and "]" in linha:
                run = p.add_run(linha)
                run.font.italic = True
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(0, 102, 204) # AZUL ROYAL
            elif is_titulo:
                run = p.add_run(linha)
                run.font.bold = True
                run.font.size = Pt(11)
                p.space_before = Pt(6)
            else:
                run = p.add_run(linha)
                run.font.size = Pt(10)

    processar_celula(col_esq, texto_esq)
    processar_celula(col_dir, texto_dir)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 2. MATERIAL PEI (DESIGN LADO A LADO V25 - FONTE 12)
# ==============================================================================
def gerar_docx_pei_v25(titulo_doc, conteudo, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.5)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(0.8), Inches(1.7), Inches(1.2)]
    for i, width in enumerate(widths):
        header_table.columns[i].width = width

    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0)) 
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 4)) 
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4)) 

    set_row_height(header_table.rows[0], 0.6) 
    set_row_height(header_table.rows[1], 1.2) 
    set_row_height(header_table.rows[2], 0.6) 

    if os.path.exists("logo_escola.png"):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER 
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER 
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.75))

    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True

    c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    c_aluno.paragraphs[0].add_run("ALUNO(A):").font.size = Pt(10)

    header_table.cell(2, 1).paragraphs[0].add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    header_table.cell(2, 2).paragraphs[0].add_run("TURMA:").font.size = Pt(9)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA: ____/____/2026").font.size = Pt(9)
    
    c_tri = header_table.cell(2, 4)
    p_tri = c_tri.paragraphs[0]
    p_tri.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tri = p_tri.add_run(f"{info.get('trimestre', 'I')} TRIMESTRE")
    run_tri.font.bold, run_tri.font.size = True, Pt(9)

    doc.add_paragraph()

    main_table = doc.add_table(rows=1, cols=2)
    main_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    col_teoria = main_table.cell(0, 0)
    col_exercicio = main_table.cell(0, 1)
    
    col_teoria.width = Inches(3.2)
    col_exercicio.width = Inches(4.0)

    def extrair_pei(texto, tag_inicio):
        pattern = rf"\[{tag_inicio}\](.*?)(?=\[|$)"
        match = re.search(pattern, texto, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    txt_lembrar = extrair_pei(conteudo, "PARA LEMBRAR")
    txt_passo = extrair_pei(conteudo, "PASSO A PASSO")
    txt_atividades = extrair_pei(conteudo, "ATIVIDADES")

    if txt_lembrar:
        p1 = col_teoria.add_paragraph()
        p1.add_run("💡 PARA LEMBRAR").font.bold = True
        p1.runs[0].font.size = Pt(12)
        p1_cont = col_teoria.add_paragraph(txt_lembrar)
        p1_cont.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p1_cont.runs[0].font.size = Pt(13)
        col_teoria.add_paragraph()

    if txt_passo:
        p2 = col_teoria.add_paragraph()
        p2.add_run("📑 PASSO A PASSO").font.bold = True
        p2.runs[0].font.size = Pt(12)
        p2_cont = col_teoria.add_paragraph(txt_passo)
        p2_cont.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p2_cont.runs[0].font.size = Pt(13)

    if txt_atividades:
        linhas = txt_atividades.split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            p = col_exercicio.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if "QUESTÃO" in l_s.upper():
                run = p.add_run(l_s)
                run.font.bold, run.font.size = True, Pt(12)
            elif re.match(r'^[A-E][\)\s\-]', l_s.upper()):
                letra = l_s[0:1]
                resto = re.sub(r'^[A-E][\)\s\-]+', '', l_s).strip()
                p.add_run(f"{letra}) {resto}").font.size = Pt(12)
            elif "PROMPT" in l_s.upper():
                run_img = p.add_run(f"[{l_s}]")
                run_img.font.italic, run_img.font.size = True, Pt(9)
                run_img.font.color.rgb = RGBColor(120, 120, 120)
            else:
                p.add_run(l_s).font.size = Pt(12)

        if not any(re.search(r'^[A-E][\)\s\-]', l) for l in linhas):
            for _ in range(3):
                col_exercicio.add_paragraph("_________________________________")

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_f = footer.add_run(f"Material Adaptado PEI • Prof. Ronaldo Gomes • 2026")
    run_f.font.size, run_f.font.italic = Pt(8), True

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. GUIA DO PROFESSOR (PRESERVADO)
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
# 4. PLANO PEDAGÓGICO (PRESERVADO)
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
# 5. APRESENTAÇÃO PPTX (PRESERVADO)
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
