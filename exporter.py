import os
import io
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from pptx import Presentation
from pptx.util import Inches, Pt
from datetime import datetime

# ==============================================================================
# 1. FUNÇÕES AUXILIARES TÉCNICAS (PRESERVAÇÃO INTEGRAL)
# ==============================================================================

def set_row_height(row, height_pt):
    """Define a altura mínima da linha da tabela para o cabeçalho não achatar"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

def adicionar_texto_formatado(paragraph, texto):
    """Converte padrões **texto** em negrito real preservando acentos"""
    import re
    texto_limpo = texto.replace("➔", "").replace("->", "").replace("single", "Bastão").strip()
    partes = re.split(r'(\*\*.*?\*\*)', texto_limpo)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            run = paragraph.add_run(parte.replace('**', ''))
            run.bold = True
        else:
            paragraph.add_run(parte)

def configurar_cabecalho_mestre(doc, info, tipo_label, mostrar_nota=False):
    """Gera o cabeçalho de ELITE: Campo de NOTA opcional, DATA e altura expandida"""
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    
    # Ajuste de larguras para margens de 0.3"
    widths = [Inches(0.8), Inches(3.0), Inches(1.0), Inches(1.2), Inches(1.9)]
    for i, w in enumerate(widths): 
        table.columns[i].width = w

    for row in table.rows:
        set_row_height(row, 24)

    # --- LINHA 0: LOGO, ESCOLA E TRIMESTRE ---
    c_logo = table.cell(0, 0).merge(table.cell(2, 0))
    c_escola = table.cell(0, 1).merge(table.cell(0, 3))
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    
    c_trim = table.cell(0, 4)
    c_trim.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    c_trim.paragraphs[0].add_run(info.get('trimestre', 'I Trimestre')).font.bold = True

    # --- LINHA 1: ALUNO (COM OU SEM NOTA) ---
    if mostrar_nota:
        c_aluno = table.cell(1, 1).merge(table.cell(1, 3))
        c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_aluno.paragraphs[0].add_run("ALUNO(A):")
        
        c_nota = table.cell(1, 4)
        c_nota.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_nota.paragraphs[0].add_run("NOTA:")
    else:
        # Se não tem nota, o campo ALUNO ocupa todo o espaço restante
        c_aluno = table.cell(1, 1).merge(table.cell(1, 4))
        c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_aluno.paragraphs[0].add_run("ALUNO(A):")

    # --- LINHA 2: PROFESSOR, TURMA, DATA E TIPO ---
    table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(9)
    table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano', '6º')}").font.size = Pt(9)
    table.cell(2, 3).paragraphs[0].add_run("DATA:    /    /").font.size = Pt(9)
    
    c_tipo = table.cell(2, 4)
    c_tipo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_tipo = c_tipo.paragraphs[0]
    p_tipo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tipo = p_tipo.add_run(tipo_label)
    run_tipo.font.bold = True
    run_tipo.font.size = Pt(9)

    # Inserção da Logo
    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c_logo.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try: p.add_run().add_picture(logo_path, width=Inches(0.65))
        except: pass
    return table

# ==============================================================================
# 2. MATERIAL DO ALUNO REGULAR (CORRIGIDO - SEM NOTA + 2 COLUNAS)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.3), Inches(0.3)

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10.5)

    # Cabeçalho Mestre (mostrar_nota=False para Atividades)
    configurar_cabecalho_mestre(doc, info, "ATIVIDADE DE SALA", mostrar_nota=False)
    doc.add_paragraph()

    # Ativação de Colunas Nativas
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '450')

    linhas = conteudo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(8)

        if any(x in l_s.upper() for x in ["ATIVIDADE DE", "JORNADA", "HISTÓRIA", "MATEMÁTICA", "AULA"]):
            run = p.add_run(l_s.upper().replace('**', ''))
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif "QUESTÃO" in l_s.upper():
            match = re.match(r"^(QUEST[AÃ]O\s+\d+)([\.\s:]+)(.*)", l_s, re.IGNORECASE)
            if match:
                run_r = p.add_run(f"{match.group(1).upper()}. ")
                run_r.bold = True
                adicionar_texto_formatado(p, match.group(3).strip())
            else: adicionar_texto_formatado(p, l_s)
        elif "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
            run = p.add_run(l_s)
            run.font.size, run.font.italic = Pt(8), True
            run.font.color.rgb = RGBColor(120, 120, 120)
        else: adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. MATERIAL PEI ADAPTADO (CORRIGIDO - SEM NOTA + 2 COLUNAS)
# ==============================================================================
def gerar_docx_pei_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.3), Inches(0.3)

    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    # Cabeçalho Mestre (mostrar_nota=False para Atividades)
    configurar_cabecalho_mestre(doc, info, "ATIVIDADE ADAPTADA", mostrar_nota=False)
    doc.add_paragraph()

    # Ativação de Colunas Nativas
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '450')

    linhas = conteudo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(10)

        secoes_pei = ["PARA LEMBRAR", "OBJETIVO", "INSTRUÇÕES", "ATIVIDADE", "PASSO A PASSO", "DICA MESTRA"]
        if any(x in l_s.upper() for x in secoes_pei):
            txt_limpo = l_s.replace("[", "").replace("]", "").replace(":", "").upper()
            run = p.add_run(f"█▓▒░ {txt_limpo} ░▒▓█")
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif "QUESTÃO" in l_s.upper():
            match = re.match(r"^(QUEST[AÃ]O\s+(?:PEI\s+)?\d+)([\.\s:]+)(.*)", l_s, re.IGNORECASE)
            if match:
                run_r = p.add_run(f"{match.group(1).upper()}. ")
                run_r.bold = True
                adicionar_texto_formatado(p, match.group(3).strip())
            else: adicionar_texto_formatado(p, l_s)
        elif "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
            run = p.add_run(l_s)
            run.font.size, run.font.italic = Pt(9), True
            run.font.color.rgb = RGBColor(100, 100, 100)
        else: adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 4. GUIA DO PROFESSOR (PRESERVAÇÃO INTEGRAL)
# ==============================================================================
def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    header_table = doc.add_table(rows=2, cols=3)
    header_table.style = 'Table Grid'
    c_tit = header_table.cell(0, 0).merge(header_table.cell(0, 2))
    p_tit = c_tit.paragraphs[0]
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tit = p_tit.add_run("GUIA DE REGÊNCIA E ESQUEMA DE LOUSA - PROF. RONALDO GOMES")
    run_tit.font.bold = True
    run_tit.font.size = Pt(12)

    header_table.cell(1, 0).paragraphs[0].add_run(f"ANO: {info.get('ano', '')}").font.size = Pt(10)
    header_table.cell(1, 1).paragraphs[0].add_run(f"SEMANA: {info.get('semana', '')}").font.size = Pt(10)
    header_table.cell(1, 2).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre', 'I')}")

    for row in header_table.rows: set_row_height(row, 22)
    doc.add_paragraph()

    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '400')

    conteudo_limpo = conteudo.replace("[PROFESSOR]", "").replace("[COLUNA_1]", "").replace("[COLUNA_2]", "")
    linhas = conteudo_limpo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)

        if l_s.isupper() and (":" in l_s or len(l_s) < 30):
            run = p.add_run(l_s.replace('**', ''))
            run.font.bold = True
            run.font.size = Pt(11)
            p.paragraph_format.space_before = Pt(8)
        elif "[" in l_s and "]" in l_s:
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(l_s.replace('**', ''))
            run.font.italic = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 102, 204)
        elif "DICA DE REGÊNCIA" in l_s.upper():
            run = p.add_run(l_s.replace('**', ''))
            run.font.bold = True
            run.font.color.rgb = RGBColor(200, 0, 0)
        else:
            run = p.add_run(l_s.replace('**', ''))
            run.font.size = Pt(10.5)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 5. PROVA OFICIAL (PRESERVAÇÃO INTEGRAL - COM NOTA)
# ==============================================================================
def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    """Versão V29.13 - Gabarito para TODOS + Negrito Ultra-Blindado + Sem Unicode"""
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.3)
        section.left_margin = section.right_margin = Inches(0.4)
        
        # 1. LIMPEZA DE RUÍDOS (Remove orientações e gabaritos de texto da IA)
        limpador = r"(?i)(^|\n)([ \t]*[-•*][^\n]*|INSTRUÇÕES|ORIENTAÇÕES|VALOR TOTAL|GABARITO PEI|SONDA DE PROFICIÊNCIA).*?(\n|$)"
        conteudo_limpo = re.sub(limpador, "\n", conteudo_ia).strip()

        # 2. CONTAGEM REAL DE QUESTÕES
        num_total_q = len(re.findall(r'(?m)^QUESTÃO\s+\d+', conteudo_limpo.upper()))
        if num_total_q == 0: num_total_q = int(info.get('qtd_questoes', 10))
        
        is_pei_doc = "PEI" in titulo_doc.upper() or "ADAPTADA" in titulo_doc.upper()
        is_sonda = "SONDA" in titulo_doc.upper() or "DIAGNÓSTICA" in titulo_doc.upper()
        label_prova = "SONDA DE PROFICIÊNCIA" if is_sonda else ("AVALIAÇÃO ADAPTADA" if is_pei_doc else "AVALIAÇÃO DE MATEMÁTICA")

        # 3. CABEÇALHO MESTRE
        configurar_cabecalho_mestre(doc, info, label_prova, mostrar_nota=True)
        doc.add_paragraph()

        # 4. QUADRO DE ORIENTAÇÕES + GABARITO DE BOLINHAS (PARA TODOS - REGULAR E PEI)
        top_table = doc.add_table(rows=1, cols=2)
        top_table.columns[0].width = Inches(3.5)
        top_table.columns[1].width = Inches(4.0)
        
        c_orient = top_table.cell(0, 0)
        p_tit = c_orient.paragraphs[0]
        p_tit.add_run("ORIENTAÇÕES:").font.bold = True
        
        orient_list = [
            "Leia atentamente cada enunciado.",
            "Resolva os cálculos no espaço em branco.",
            "Marque apenas uma alternativa por questão.",
            f"Valor Total: 10,0 | Questões: {num_total_q}"
        ]
        for txt in orient_list:
            p = c_orient.add_paragraph()
            p.add_run(f"• {txt}").font.size = Pt(9)
            p.paragraph_format.space_after = Pt(0)

        # Inserção do Gabarito de Bolinhas (Obrigatório para todos)
        c_gab = top_table.cell(0, 1)
        gab_grid = c_gab.add_table(rows=num_total_q + 1, cols=6)
        gab_grid.style = 'Table Grid'
        for i, lab in enumerate(["Q", "A", "B", "C", "D", "E"]):
            gab_grid.cell(0, i).paragraphs[0].add_run(lab).font.bold = True
        for r in range(1, num_total_q + 1):
            gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
            for col in range(1, 6): 
                gab_grid.cell(r, col).paragraphs[0].add_run("○").font.size = Pt(14)
        
        doc.add_paragraph()

        # 5. CONTEÚDO EM COLUNAS NATIVAS
        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '720')

        for linha in conteudo_limpo.split('\n'):
            l_s = linha.strip()
            if not l_s: continue
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            
            # FORÇAR NEGRITO NO RÓTULO DA QUESTÃO (BLINDAGEM TOTAL)
            if "QUESTÃO" in l_s.upper():
                # Captura QUESTÃO XX + pontuação/valor + enunciado
                match = re.match(r"^(QUEST[AÃ]O\s+\d+)(.*?)(\.\s*|\s+-\s*|:\s*)(.*)", l_s, re.IGNORECASE)
                if match:
                    run_r = p.add_run(f"{match.group(1).upper()}{match.group(2)}{match.group(3)}")
                    run_r.bold = True
                    run_r.font.size = Pt(11)
                    adicionar_texto_formatado(p, match.group(4).strip())
                    continue
            
            # Títulos de Seção (Sem Unicode)
            secoes_especiais = ["PARA LEMBRAR", "DICA MESTRA", "PASSO A PASSO", "VERSÃO ADAPTADA"]
            if any(x in l_s.upper() for x in secoes_especiais):
                run = p.add_run(l_s.replace("[", "").replace("]", "").upper())
                run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                continue

            if re.match(r'^[A-E][\)\.]', l_s):
                p.paragraph_format.left_indent = Inches(0.2)
            
            adicionar_texto_formatado(p, l_s)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    
# ==============================================================================
# 6. PLANO PEDAGÓGICO (PRESERVAÇÃO INTEGRAL)
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
        table.cell(0, 2).paragraphs[0].add_run("PLANO DE ENSINO SEMANAL").font.bold = True
        table.cell(1, 1).paragraphs[0].add_run(f"Professor: Ronaldo Gomes").font.size = Pt(10)
        table.cell(1, 2).paragraphs[0].add_run(f"Ano: {info.get('ano', '')}").font.size = Pt(10)
        table.cell(2, 1).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}").font.size = Pt(10)
        table.cell(2, 2).paragraphs[0].add_run(f"Trimestre: {info.get('trimestre', 'I')}").font.bold = True

        doc.add_paragraph()

        campos = [
            ("OBJETO DE CONHECIMENTO (EIXO):", "geral"), 
            ("CONTEÚDOS ESPECÍFICOS:", "especificos"), 
            ("OBJETIVOS DE APRENDIZAGEM:", "objetivos"), 
            ("RECURSOS DIDÁTICOS:", "recursos"),
            ("PROCEDIMENTOS METODOLÓGICOS:", "metodologia"), 
            ("AVALIAÇÃO E ACOMPANHAMENTO:", "avaliacao"), 
            ("ESTRATÉGIAS DE ACESSIBILIDADE (DUA):", "pei")
        ]

        for label, chave in campos:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(8)
            run_label = p.add_run(label)
            run_label.bold = True
            run_label.font.size = Pt(11)
            texto_limpo = str(dados.get(chave, "")).replace("**", "").replace("#", "").strip()
            p.add_run(f" {texto_limpo}").font.size = Pt(11)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 7. APRESENTAÇÃO PPTX (PRESERVAÇÃO INTEGRAL)
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
            slide.placeholders[1].text = visual.group(1).strip().replace("**", "")
        if script:
            slide.notes_slide.notes_text_frame.text = script.group(1).strip().replace("**", "")
    file_stream = io.BytesIO()
    prs.save(file_stream)
    file_stream.seek(0)
    return file_stream
