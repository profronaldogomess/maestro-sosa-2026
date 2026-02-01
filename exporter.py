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
import ai_engine as ai  # <--- ADICIONE ESTA LINHA AQUI

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

    # --- CABEÇALHO (MANTIDO) ---
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
    c_aluno.paragraphs[0].add_run("ALUNO(A):").font.size = Pt(10)
    header_table.cell(2, 1).paragraphs[0].add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    header_table.cell(2, 2).paragraphs[0].add_run("TURMA:").font.size = Pt(9)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA: ____/____/2026").font.size = Pt(9)
    header_table.cell(2, 4).paragraphs[0].add_run(f"{info.get('trimestre', 'I')} TRIM").font.size = Pt(9)

    doc.add_paragraph() 

    # --- TRATAMENTO DE CONTEÚDO (INTRODUÇÃO vs QUESTÕES) ---
    # Divide o texto para tirar a introdução de dentro da tabela de colunas
    partes = re.split(r'(QUESTÃO\s+\d+[\.:\s]*)', conteudo, flags=re.IGNORECASE)
    
    introducao = partes[0].strip()
    questoes_raw = partes[1:]

    # Se houver introdução, coloca ela em largura total antes das colunas
    if introducao:
        for linha in introducao.split('\n'):
            if "ESCOLA:" in linha.upper() or "ESTUDANTE:" in linha.upper(): continue
            p_intro = doc.add_paragraph()
            p_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_intro.add_run(linha.strip()).font.size = Pt(10)
        doc.add_paragraph()

    # Monta a lista de questões (par marcador + corpo)
    lista_questoes = []
    for i in range(0, len(questoes_raw), 2):
        if i+1 < len(questoes_raw):
            lista_questoes.append(questoes_raw[i] + questoes_raw[i+1])

    # Cria a tabela de 2 colunas apenas para as questões
    if lista_questoes:
        main_table = doc.add_table(rows=(len(lista_questoes) + 1) // 2, cols=2)
        main_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        for idx, q_text in enumerate(lista_questoes):
            cell = main_table.cell(idx // 2, idx % 2)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            
            linhas = q_text.strip().split('\n')
            for j, linha in enumerate(linhas):
                l_s = linha.strip()
                if not l_s: continue
                p = cell.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                
                if j == 0: # É o título da Questão
                    run = p.add_run(l_s)
                    run.font.bold = True
                    run.font.size = Pt(11)
                elif "PROMPT IMAGEM" in l_s.upper():
                    run_img = p.add_run(f"[{l_s}]")
                    run_img.font.italic, run_img.font.size = True, Pt(8)
                    run_img.font.color.rgb = RGBColor(120, 120, 120)
                else:
                    p.add_run(l_s).font.size = Pt(10)

    # Rodapé
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

    # --- CABEÇALHO (MANTIDO) ---
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
    c_aluno.paragraphs[0].add_run("ALUNO(A):").font.size = Pt(10)
    header_table.cell(2, 1).paragraphs[0].add_run("PROF.: Ronaldo Gomes").font.size = Pt(9)
    header_table.cell(2, 2).paragraphs[0].add_run("TURMA:").font.size = Pt(9)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA: ____/____/2026").font.size = Pt(9)
    header_table.cell(2, 4).paragraphs[0].add_run(f"{info.get('trimestre', 'I')} TRIM").font.size = Pt(9)

    doc.add_paragraph()

    # --- TABELA LADO A LADO ---
    main_table = doc.add_table(rows=1, cols=2)
    main_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    col_teoria = main_table.cell(0, 0)
    col_exercicio = main_table.cell(0, 1)
    col_teoria.width = Inches(3.2)
    col_exercicio.width = Inches(4.0)

    # FUNÇÃO DE EXTRAÇÃO ROBUSTA (Aceita com ou sem colchetes)
    def extrair_pei_blindado(texto, tag_nome):
        # Procura por [TAG] ou apenas TAG no início da linha
        pattern = rf"(?:\[{tag_nome}\]|{tag_nome})[:\s]*(.*?)(?=\[|PARA LEMBRAR|PASSO A PASSO|ATIVIDADES|IMAGENS_PEI|$)"
        match = re.search(pattern, texto, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""

    txt_lembrar = extrair_pei_blindado(conteudo, "PARA LEMBRAR")
    txt_passo = extrair_pei_blindado(conteudo, "PASSO A PASSO")
    txt_atividades = extrair_pei_blindado(conteudo, "ATIVIDADES")

    if txt_lembrar:
        p1 = col_teoria.add_paragraph()
        p1.add_run("💡 PARA LEMBRAR").font.bold = True
        p1.runs[0].font.size = Pt(14)
        p1_cont = col_teoria.add_paragraph(txt_lembrar)
        p1_cont.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p1_cont.runs[0].font.size = Pt(13)
        col_teoria.add_paragraph()

    if txt_passo:
        p2 = col_teoria.add_paragraph()
        p2.add_run("📑 PASSO A PASSO").font.bold = True
        p2.runs[0].font.size = Pt(14)
        p2_cont = col_teoria.add_paragraph(txt_passo)
        p2_cont.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p2_cont.runs[0].font.size = Pt(13)

    if txt_atividades:
        for linha in txt_atividades.split('\n'):
            l_s = linha.strip()
            if not l_s: continue
            p = col_exercicio.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if "QUESTÃO" in l_s.upper():
                run = p.add_run(l_s)
                run.font.bold, run.font.size = True, Pt(14)
            else:
                p.add_run(l_s).font.size = Pt(14)

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.add_run(f"Material Adaptado PEI • Prof. Ronaldo Gomes • 2026").font.size = Pt(8)

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

# ==============================================================================
# 6. Prova OFICIAL
# ==============================================================================
def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    """
    EXPORTADOR DE EXAMES V25 - MAESTRO SOSA
    BLINDAGEM TOTAL ANTI-SEEK E NUMERAÇÃO MANUAL.
    """
    import io
    import os
    import re
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_ALIGN_VERTICAL
    
    # Inicialização do stream fora do try para garantir existência no except
    file_stream = io.BytesIO()
    
    try:
        doc = Document()
        section = doc.sections[0]
        # Margens de precisão para exames
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

        # --- 1. CABEÇALHO OFICIAL SOSA ---
        header_table = doc.add_table(rows=3, cols=6)
        header_table.style = 'Table Grid'
        widths = [Inches(0.8), Inches(3.2), Inches(0.8), Inches(0.8), Inches(1.0), Inches(0.9)]
        for i, w in enumerate(widths): 
            header_table.columns[i].width = w

        c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
        c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 4))
        c_trim = header_table.cell(0, 5)
        c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4))
        c_nota_box = header_table.cell(1, 5)
        
        if os.path.exists("logo_escola.png"):
            c_logo.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            c_logo.paragraphs[0].add_run().add_picture("logo_escola.png", width=Inches(0.7))

        c_escola.paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        c_trim.paragraphs[0].add_run(info.get('trimestre', 'I TRIMESTRE')).font.bold = True
        c_aluno.paragraphs[0].add_run("ALUNO(A): ")
        c_nota_box.paragraphs[0].add_run("NOTA: ").font.size = Pt(8)

        header_table.cell(2, 1).paragraphs[0].add_run("PROF. Ronaldo Gomes").font.size = Pt(9)
        header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano')}").font.size = Pt(9)
        header_table.cell(2, 3).paragraphs[0].add_run("DATA:").font.size = Pt(9)
        header_table.cell(2, 5).paragraphs[0].add_run(info.get('tipo_prova', 'TESTE')).font.size = Pt(8)

        doc.add_paragraph()

        # --- 2. ORIENTAÇÕES E GABARITO (LADO A LADO) ---
        top_table = doc.add_table(rows=1, cols=2)
        top_table.columns[0].width = Inches(3.8)
        top_table.columns[1].width = Inches(3.2)

        # Orientações (Numeração Manual Estrita)
        c_orient = top_table.cell(0, 0)
        p_title = c_orient.paragraphs[0]
        p_title.add_run("ORIENTAÇÕES PARA AVALIAÇÃO:").font.bold = True
        
        orient_text = ai.extrair_tag(conteudo_ia, "ORIENTACOES")
        if not orient_text:
            orient_text = "1. Leia com atenção.\n2. Use caneta azul ou preta.\n3. Demonstre os cálculos.\n4. Apenas uma correta."
        
        for linha in orient_text.split('\n'):
            if linha.strip():
                p = c_orient.add_paragraph()
                p.add_run(linha.strip()).font.size = Pt(9)

        # Gabarito (Bolinhas Pt 12)
        c_gab = top_table.cell(0, 1)
        gab_grid = c_gab.add_table(rows=11, cols=6)
        gab_grid.style = 'Table Grid'
        for i, lab in enumerate(["Q", "A", "B", "C", "D", "E"]):
            p = gab_grid.cell(0, i).paragraphs[0]
            p.add_run(lab).font.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in range(1, 11):
            gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(8)
            for col in range(1, 6):
                p_bol = gab_grid.cell(r, col).paragraphs[0]
                p_bol.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run_b = p_bol.add_run("○")
                run_b.font.size = Pt(12)

        doc.add_paragraph()

        # --- 3. CORPO DA PROVA (DUAS COLUNAS - NUMERAÇÃO MANUAL) ---
        questoes_raw = ai.extrair_tag(conteudo_ia, "QUESTOES")
        # Split inteligente que captura "1ª Questão", "01. Questão", etc.
        partes = re.split(r'(\d+[\s\.]*[ªº]?\s*Questão)', questoes_raw, flags=re.IGNORECASE)
        
        final_q = []
        for i in range(1, len(partes), 2):
            marcador = partes[i].strip()
            corpo = partes[i+1].strip() if i+1 < len(partes) else ""
            final_q.append(f"{marcador}\n{corpo}")

        if not final_q: 
            final_q = [questoes_raw] if questoes_raw else ["Erro: Conteúdo de questões não identificado."]

        body_table = doc.add_table(rows=(len(final_q) + 1) // 2, cols=2)
        for idx, q_text in enumerate(final_q):
            cell = body_table.cell(idx // 2, idx % 2)
            cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
            linhas = q_text.split('\n')
            for j, linha in enumerate(linhas):
                l_s = linha.strip()
                if not l_s or "[CÁLCULO]" in l_s.upper(): continue
                p = cell.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                run = p.add_run(l_s)
                if j == 0: # Título da Questão (Negrito)
                    run.font.bold, run.font.size = True, Pt(11)
                else:
                    run.font.size = Pt(10)

        # Finalização do Documento
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

    except Exception as e:
        # BLINDAGEM DE EMERGÊNCIA: Se a lógica acima falhar, gera um documento de erro
        # Isso garante que o database.py receba um arquivo e não um NoneType
        doc_err = Document()
        doc_err.add_heading('ERRO TÉCNICO NO EXPORTADOR SOSA', 0)
        doc_err.add_paragraph(f"Detalhes do Erro: {str(e)}")
        doc_err.add_paragraph("O sistema impediu um crash, mas o documento não pôde ser formatado.")
        
        err_stream = io.BytesIO()
        doc_err.save(err_stream)
        err_stream.seek(0)
        return err_stream
