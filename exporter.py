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
from datetime import datetime
import ai_engine as ai
from docx.enum.section import WD_ORIENT


# ==============================================================================
# 1. FUNÇÕES AUXILIARES TÉCNICAS
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
    
    widths =[Inches(0.8), Inches(3.0), Inches(1.0), Inches(1.2), Inches(1.9)]
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

    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c_logo.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try: p.add_run().add_picture(logo_path, width=Inches(0.65))
        except: pass
    return table

# ==============================================================================
# 2. MATERIAL DO ALUNO REGULAR
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

    configurar_cabecalho_mestre(doc, info, "ATIVIDADE DE SALA", mostrar_nota=False)
    doc.add_paragraph()

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

        if any(x in l_s.upper() for x in["ATIVIDADE DE", "JORNADA", "HISTÓRIA", "MATEMÁTICA", "AULA"]):
            run = p.add_run(l_s.replace('**', ''))
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
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            txt_img = l_s.replace("[", "").replace("]", "").strip()
            run = p.add_run(f"🖼️ [ ESPAÇO PARA IMAGEM: {txt_img} ]")
            run.font.size, run.font.italic = Pt(9), True
            run.font.color.rgb = RGBColor(120, 120, 120)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif "[GEOGEBRA]" in l_s.upper():
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            txt_geo = l_s.replace("[GEOGEBRA]", "").replace("[", "").replace("]", "").strip()
            run = p.add_run(f"📐 COMANDO GEOGEBRA: {txt_geo}")
            run.font.italic = True
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0, 102, 204)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        else: adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. MATERIAL PEI ADAPTADO (NÍVEIS 1 E 2)
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

    configurar_cabecalho_mestre(doc, info, "ATIVIDADE ADAPTADA", mostrar_nota=True)
    doc.add_paragraph()

    num_total_q = len(re.findall(r'(?i)(?:QUEST[AÃ]O\s*(?:PEI\s*)?|Q)\s*\d+', conteudo))
    if num_total_q == 0: num_total_q = 5 

    top_table = doc.add_table(rows=1, cols=2)
    top_table.columns[0].width = Inches(3.5)
    top_table.columns[1].width = Inches(4.0)
    
    c_orient = top_table.cell(0, 0)
    p_tit = c_orient.paragraphs[0]
    p_tit.add_run("ORIENTAÇÕES:").font.bold = True
    
    val_total = info.get('valor', '10,0')
    
    orient_list = [
        "Leia atentamente cada enunciado.",
        "Marque apenas uma alternativa por questão.",
        f"Valor Total: {val_total}"
    ]
    for txt in orient_list:
        p = c_orient.add_paragraph()
        p.add_run(f"• {txt}").font.size = Pt(9)
        p.paragraph_format.space_after = Pt(0)

    c_gab = top_table.cell(0, 1)
    if num_total_q <= 10:
        gab_grid = c_gab.add_table(rows=num_total_q + 1, cols=4)
        gab_grid.style = 'Table Grid'
        for i, lab in enumerate(["Q", "A", "B", "C"]):
            gab_grid.cell(0, i).paragraphs[0].add_run(lab).font.bold = True
        for r in range(1, num_total_q + 1):
            gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
            for col in range(1, 4): 
                gab_grid.cell(r, col).paragraphs[0].add_run("○").font.size = Pt(14)
    else:
        half = (num_total_q + 1) // 2
        gab_grid = c_gab.add_table(rows=half + 1, cols=8)
        gab_grid.style = 'Table Grid'
        headers = ["Q", "A", "B", "C", "Q", "A", "B", "C"]
        for i, lab in enumerate(headers):
            gab_grid.cell(0, i).paragraphs[0].add_run(lab).font.bold = True
        
        for r in range(1, num_total_q + 1):
            if r <= half:
                row_idx = r
                col_offset = 0
            else:
                row_idx = r - half
                col_offset = 4
                
            gab_grid.cell(row_idx, col_offset).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
            for col in range(1, 4):
                gab_grid.cell(row_idx, col_offset + col).paragraphs[0].add_run("○").font.size = Pt(14)

    doc.add_paragraph()

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

        secoes_pei =["PARA LEMBRAR", "OBJETIVO", "INSTRUÇÕES", "ATIVIDADE", "PASSO A PASSO", "DICA MESTRA"]
        if any(x in l_s.upper() for x in secoes_pei):
            txt_limpo = l_s.replace("[", "").replace("]", "").replace(":", "")
            run = p.add_run(txt_limpo)
            run.bold = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif re.match(r"^(?:QUEST[AÃ]O\s+(?:PEI\s+)?|Q)\d+", l_s, re.IGNORECASE):
            match = re.match(r"^((?:QUEST[AÃ]O\s+(?:PEI\s+)?|Q)\d+)([\.\s:]+)(.*)", l_s, re.IGNORECASE)
            if match:
                run_r = p.add_run(f"{match.group(1).upper()}. ")
                run_r.bold = True
                adicionar_texto_formatado(p, match.group(3).strip())
            else: adicionar_texto_formatado(p, l_s)
        elif "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            txt_img = l_s.replace("[", "").replace("]", "").strip()
            run = p.add_run(f"🖼️ [ ESPAÇO PARA IMAGEM: {txt_img} ]")
            run.font.size, run.font.italic = Pt(9), True
            run.font.color.rgb = RGBColor(100, 100, 100)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif "[GEOGEBRA]" in l_s.upper():
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            txt_geo = l_s.replace("[GEOGEBRA]", "").replace("[", "").replace("]", "").strip()
            run = p.add_run(f"📐 COMANDO GEOGEBRA: {txt_geo}")
            run.font.italic = True
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0, 102, 204)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        elif "GABARITO" in l_s.upper():
            p.paragraph_format.space_before = Pt(15)
            run = p.add_run(l_s.replace('**', ''))
            run.bold = True
            run.font.color.rgb = RGBColor(0, 102, 204)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else: adicionar_texto_formatado(p, l_s)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 11. EXPORTADOR PEI NÍVEL 3 (QUALITATIVO / SENSORIAL) - BLINDADO
# ==============================================================================
def gerar_docx_pei_qualitativa(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Comic Sans MS' 
        style.font.size = Pt(14) 

        configurar_cabecalho_mestre(doc, info, "AVALIAÇÃO ADAPTADA (NÍVEL 3)", mostrar_nota=False)
        doc.add_paragraph()

        if not conteudo or len(str(conteudo).strip()) < 10:
            p = doc.add_paragraph("Ocorreu um erro na geração do Nível 3. Por favor, refine a questão no painel.")
            doc.save(file_stream)
            file_stream.seek(0)
            return file_stream

        linhas = str(conteudo).split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(12)

            # 🚨 NOVA REGRA: IMPRIME A RUBRICA DE OBSERVAÇÃO NO FINAL
            if "RUBRICA" in l_s.upper() or "GABARITO" in l_s.upper():
                p.paragraph_format.space_before = Pt(20)
                run = p.add_run(l_s.replace('**', ''))
                run.bold = True
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(112, 48, 160)
                continue

            if "QUESTÃO" in l_s.upper():
                run = p.add_run(l_s)
                run.bold = True
                run.font.size = Pt(16)
            elif "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(50) 
                txt_img = l_s.replace("[", "").replace("]", "").strip()
                run = p.add_run(f"🖼️ [ ESPAÇO PARA IMAGEM: {txt_img} ]")
                run.font.italic = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(150, 150, 150)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif "( ) SIM" in l_s.upper():
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(l_s)
                run.bold = True
                run.font.size = Pt(16)
            else:
                adicionar_texto_formatado(p, l_s)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO EXPORTER N3: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 4. GUIA DO PROFESSOR
# ==============================================================================
def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    doc = Document()
    
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(10.5)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    header_table = doc.add_table(rows=2, cols=3)
    header_table.style = 'Table Grid'
    c_tit = header_table.cell(0, 0).merge(header_table.cell(0, 2))
    run_tit = c_tit.paragraphs[0].add_run("GUIA DE MEDIAÇÃO E GABARITOS")
    run_tit.font.bold, run_tit.font.size = True, Pt(12)
    c_tit.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER

    header_table.cell(1, 0).paragraphs[0].add_run(f"ANO: {info.get('ano', '')}").font.size = Pt(9)
    header_table.cell(1, 1).paragraphs[0].add_run(f"SEMANA: {info.get('semana', '')}").font.size = Pt(9)
    header_table.cell(1, 2).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre', 'I')}").font.size = Pt(9)
    for row in header_table.rows: set_row_height(row, 20)
    doc.add_paragraph()

    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '500')

    linhas = conteudo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0

        if l_s.endswith(":") and len(l_s) < 40:
            p.paragraph_format.space_before = Pt(10)
            run = p.add_run(l_s)
            run.font.bold = True
            run.font.size = Pt(11)
            continue

        if re.search(r"(?i)QUEST[AÃ]O\s*(?:PEI\s*)?\d+\s*[:\-]\s*[A-E]$|^\d+[\.\s\-]+[A-E]$", l_s):
            run = p.add_run(f"✅ {l_s}")
            run.font.bold, run.font.size = True, Pt(11)
            run.font.color.rgb = RGBColor(0, 128, 0)
            continue

        if "QUESTÃO" in l_s.upper() and "PEI" not in l_s.upper() and (":" in l_s or "[" in l_s):
            p.paragraph_format.space_before = Pt(8)
            run = p.add_run(l_s)
            run.font.bold = True
            run.font.color.rgb = RGBColor(0, 51, 153)
            continue

        if "QUESTÃO PEI" in l_s.upper():
            p.paragraph_format.space_before = Pt(8)
            run = p.add_run(f"♿ {l_s}")
            run.font.bold = True
            run.font.color.rgb = RGBColor(112, 48, 160)
            continue
            
        if "[GEOGEBRA]" in l_s.upper():
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            txt_geo = l_s.replace("[GEOGEBRA]", "").replace("[", "").replace("]", "").strip()
            run = p.add_run(f"📐 COMANDO GEOGEBRA: {txt_geo}")
            run.font.italic = True
            run.font.bold = True
            run.font.size = Pt(9.5)
            run.font.color.rgb = RGBColor(0, 102, 204)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            continue

        if any(x in l_s.upper() for x in ["JUSTIFICATIVA", "PERÍCIA", "LACUNA", "ANÁLISE", "DISTRATORES", "ACERTO INTEGRAL", "ACERTO PARCIAL"]):
            p.paragraph_format.left_indent = Inches(0.15)
            icon = "🎯" if any(x in l_s.upper() for x in ["JUST", "ACERTO"]) else "🧠"
            
            if ':' in l_s:
                label, content = l_s.split(':', 1)
                run_label = p.add_run(f"{icon} {label}:")
                run_label.font.bold = True
                
                if any(x in label.upper() for x in ["LACUNA", "PERÍCIA", "DISTRATORES"]):
                     run_label.font.color.rgb = RGBColor(204, 0, 0)
                elif "ACERTO" in label.upper():
                     run_label.font.color.rgb = RGBColor(0, 128, 0)
                
                content_formatted = re.sub(r'(?=\([A-E]\))', '\n\t', content)
                p.add_run(f" {content_formatted}").font.size = Pt(9.5)
            else:
                p.add_run(l_s)
            continue

        p.add_run(re.sub(r'[#*]', '', l_s)).font.size = Pt(10)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 5. PROVA OFICIAL (ATUALIZADO PARA 20 QUESTÕES)
# ==============================================================================
def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        
        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10.5)

        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.3)
        section.left_margin = section.right_margin = Inches(0.4)
        
        is_pei_doc = "PEI" in titulo_doc.upper() or "ADAPTADA" in titulo_doc.upper()
        tag_alvo = "PEI" if is_pei_doc else "QUESTOES"
        
        corpo_bruto = ai.extrair_tag(conteudo_ia, tag_alvo)
        
        if not corpo_bruto:
            match_primeira_q = re.search(r"(?i)QUESTÃO\s*\d+", conteudo_ia)
            corpo_bruto = conteudo_ia[match_primeira_q.start():].strip() if match_primeira_q else conteudo_ia.strip()

        num_total_q = len(re.findall(r'(?i)QUESTÃO\s+\d+', corpo_bruto))
        if num_total_q == 0: num_total_q = int(info.get('qtd_questoes', 5))
        
        label_prova = "AVALIAÇÃO ADAPTADA" if is_pei_doc else "AVALIAÇÃO DE MATEMÁTICA"
        if "SONDA" in titulo_doc.upper(): label_prova = "SONDA DE PROFICIÊNCIA"

        configurar_cabecalho_mestre(doc, info, label_prova, mostrar_nota=True)
        doc.add_paragraph()

        top_table = doc.add_table(rows=1, cols=2)
        top_table.columns[0].width = Inches(3.5)
        top_table.columns[1].width = Inches(4.0)
        
        c_orient = top_table.cell(0, 0)
        p_tit = c_orient.paragraphs[0]
        p_tit.add_run("ORIENTAÇÕES:").font.bold = True
        
        val_total = info.get('valor', '10,0')
        val_q = info.get('valor_questao', '1,0')
        
        orient_list = [
            "Leia atentamente cada enunciado.",
            "Resolva os cálculos no espaço em branco.",
            "Marque apenas uma alternativa por questão." if info.get('tipo_prova') != "2ª Chamada" else "Apresente o raciocínio e os cálculos de todas as questões.",
            f"Valor Total: {val_total} | Cada questão: {val_q}"
        ]
        for txt in orient_list:
            p = c_orient.add_paragraph()
            p.add_run(f"• {txt}").font.size = Pt(9)
            p.paragraph_format.space_after = Pt(0)

        # 🚨 PROTOCOLO FÊNIX E GABARITO DINÂMICO (ATÉ 20 QUESTÕES)
        if info.get('tipo_prova') != "2ª Chamada":
            c_gab = top_table.cell(0, 1)
            
            if num_total_q <= 10:
                # Gabarito em 1 coluna
                gab_grid = c_gab.add_table(rows=num_total_q + 1, cols=6)
                gab_grid.style = 'Table Grid'
                for i, lab in enumerate(["Q", "A", "B", "C", "D", "E"]):
                    gab_grid.cell(0, i).paragraphs[0].add_run(lab).font.bold = True
                for r in range(1, num_total_q + 1):
                    gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
                    for col in range(1, 6): 
                        gab_grid.cell(r, col).paragraphs[0].add_run("○").font.size = Pt(14)
            else:
                # Gabarito em 2 colunas (12 colunas no total)
                half = (num_total_q + 1) // 2
                gab_grid = c_gab.add_table(rows=half + 1, cols=12)
                gab_grid.style = 'Table Grid'
                headers = ["Q", "A", "B", "C", "D", "E", "Q", "A", "B", "C", "D", "E"]
                for i, lab in enumerate(headers):
                    gab_grid.cell(0, i).paragraphs[0].add_run(lab).font.bold = True
                
                for r in range(1, num_total_q + 1):
                    if r <= half:
                        row_idx = r
                        col_offset = 0
                    else:
                        row_idx = r - half
                        col_offset = 6
                        
                    gab_grid.cell(row_idx, col_offset).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
                    for col in range(1, 6):
                        gab_grid.cell(row_idx, col_offset + col).paragraphs[0].add_run("○").font.size = Pt(14)
        else:
            c_gab = top_table.cell(0, 1)
            p_gab = c_gab.paragraphs[0]
            p_gab.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_gab.add_run("\nAVALIAÇÃO DISCURSIVA\n").font.bold = True
            p_gab.add_run("Questões sem demonstração de cálculo poderão ter a nota reduzida ou zerada.").font.size = Pt(9)
        
        doc.add_paragraph()

        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '720')

        corpo_limpo = corpo_bruto.replace("**", "").replace("#", "")

        for linha in corpo_limpo.split('\n'):
            l_s = linha.strip()
            if not l_s: continue
            
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_after = Pt(6)
            
            if l_s.upper().startswith("QUESTÃO"):
                match = re.match(r"^(QUEST[AÃ]O\s*\d+)(\s*\(.*?\))?([\s\.\-\:]+)(.*)", l_s, re.IGNORECASE)
                if match:
                    rotulo_negrito = f"{match.group(1).upper()}{match.group(2) if match.group(2) else ''}{match.group(3)}"
                    run_r = p.add_run(rotulo_negrito)
                    run_r.bold = True
                    run_r.font.size = Pt(11)
                    p.add_run(match.group(4).strip())
                    continue
            
            secoes_especiais =["PARA LEMBRAR", "DICA MESTRA", "PASSO A PASSO", "VERSÃO ADAPTADA"]
            if any(x in l_s.upper() for x in secoes_especiais):
                txt_limpo = l_s.replace("[", "").replace("]", "").replace(":", "")
                run = p.add_run(txt_limpo)
                run.bold = True
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                continue

            if "PROMPT IMAGEM" in l_s.upper():
                p.paragraph_format.space_before = Pt(3)
                txt_img = l_s.replace("[", "").replace("]", "").strip()
                run = p.add_run(f"🖼️[ {txt_img} ]")
                run.font.italic = True
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(100, 100, 100)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                continue
                
            if "[GEOGEBRA]" in l_s.upper():
                p.paragraph_format.space_before = Pt(3)
                txt_geo = l_s.replace("[GEOGEBRA]", "").replace("[", "").replace("]", "").strip()
                run = p.add_run(f"📐 [ COMANDO GEOGEBRA: {txt_geo} ]")
                run.font.italic = True
                run.font.size = Pt(8.5)
                run.font.color.rgb = RGBColor(0, 102, 204)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                continue

            if re.match(r'^[A-E][\)\.]', l_s):
                p.paragraph_format.left_indent = Inches(0.2)
                letra_match = re.match(r'^([A-E][\)\.])(.*)', l_s)
                if letra_match:
                    run_letra = p.add_run(letra_match.group(1))
                    run_letra.bold = True
                    p.add_run(letra_match.group(2))
                    continue
            
            p.add_run(l_s)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO EXPORTER V33: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    
# ==============================================================================
# 6. PLANO PEDAGÓGICO
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
        widths =[Inches(1.1), Inches(3.6), Inches(2.0)]
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

        campos =[
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
# 7. EXPORTADOR DE INICIAÇÃO CIENTÍFICA (PROJETOS)
# ==============================================================================
def gerar_docx_projeto_cientifico_V33(titulo_doc, conteudo_ia, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.4)
        section.left_margin = section.right_margin = Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10.5)

        configurar_cabecalho_mestre(doc, info, "ROTEIRO DE INVESTIGAÇÃO", mostrar_nota=False)
        doc.add_paragraph()

        tags_projeto =[
            ("🎯 CONTEXTO DA INVESTIGAÇÃO", "CONTEXTO_INVESTIGATIVO"),
            ("🚀 MISSÃO DE PESQUISA", "MISSÃO_DE_PESQUISA"),
            ("📑 PASSO A PASSO METODOLÓGICO", "PASSO_A_PASSO"),
            ("📦 PRODUTO ESPERADO", "PRODUTO_ESPERADO"),
            ("♿ ACESSIBILIDADE (DUA)", "ESTRATEGIA_DUA_PEI"),
            ("⚖️ RUBRICA DE MÉRITO", "RUBRICA_DE_MERITO")
        ]

        for label, tag in tags_projeto:
            texto_secao = ai.extrair_tag(conteudo_ia, tag)
            if texto_secao:
                p_tit = doc.add_paragraph()
                run_tit = p_tit.add_run(label)
                run_tit.bold = True
                run_tit.font.size = Pt(11)
                
                linhas = texto_secao.split('\n')
                for linha in linhas:
                    l_s = linha.strip()
                    if not l_s: continue
                    p = doc.add_paragraph()
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    if tag == "RUBRICA_DE_MERITO":
                        p.paragraph_format.left_indent = Inches(0.2)
                        p.add_run("• ").bold = True
                    adicionar_texto_formatado(p, re.sub(r'[*#]', '', l_s))
                doc.add_paragraph()

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    
# ==============================================================================
# 8. EXPORTADOR DE DOSSIÊ ANALÍTICO (RAIO-X V91)
# ==============================================================================
def gerar_docx_raiox_v90(titulo_doc, info, stats_gerais, questoes_detalhes, alunos_criticos, grafico_bytes=None):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.3)
        section.left_margin = section.right_margin = Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10)

        configurar_cabecalho_mestre(doc, info, "DOSSIÊ ANALÍTICO", mostrar_nota=False)
        doc.add_paragraph()

        p_t = doc.add_paragraph()
        run_t = p_t.add_run("1. TERMÔMETRO DE PERFORMANCE DA TURMA")
        run_t.bold = True
        run_t.font.size = Pt(11)
        
        p_s = doc.add_paragraph()
        p_s.add_run(f"• Avaliação Base: {info.get('avaliacao')}\n")
        p_s.add_run(f"• Total de Alunos Avaliados: {stats_gerais.get('total_alunos')}\n")
        p_s.add_run(f"• Média Geral da Turma: {stats_gerais.get('media_turma')}\n")
        p_s.add_run(f"• Alerta Crítico (Piores Índices): {stats_gerais.get('top_3')}").bold = True

        if grafico_bytes:
            try:
                image_stream = io.BytesIO(grafico_bytes)
                p_img = doc.add_paragraph()
                p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_img.add_run().add_picture(image_stream, width=Inches(6.5))
            except Exception as e:
                doc.add_paragraph(f"[Aviso: Não foi possível renderizar o gráfico visual. Erro: {str(e)}]")

        doc.add_paragraph()

        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '450')

        p_a = doc.add_paragraph()
        run_a = p_a.add_run("2. AUTÓPSIA POR QUESTÃO")
        run_a.bold = True
        run_a.font.size = Pt(11)
        
        for q in questoes_detalhes:
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_after = Pt(2)
            p_q.add_run(f"{q['titulo']} ").bold = True
            p_q.add_run(f"| Acerto: {q['acerto']} | Gabarito: {q['gabarito']}").bold = True
            
            p_en = doc.add_paragraph()
            p_en.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_en.paragraph_format.space_after = Pt(2)
            p_en.add_run(q['enunciado']).font.italic = True
            
            p_per = doc.add_paragraph()
            p_per.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_per.paragraph_format.space_after = Pt(12)
            p_per.add_run("Diagnóstico Técnico: ").bold = True
            p_per.add_run(q['pericia']).font.size = Pt(9)

        p_c = doc.add_paragraph()
        p_c.paragraph_format.space_before = Pt(12)
        run_c = p_c.add_run("3. RADAR DE ALUNOS CRÍTICOS")
        run_c.bold = True
        run_c.font.size = Pt(11)
        
        p_cl = doc.add_paragraph()
        if alunos_criticos:
            p_cl.add_run("Alunos com nota abaixo da média:\n").bold = True
            for aluno in alunos_criticos:
                p_cl.add_run(f"• {aluno}\n").font.size = Pt(9)
        else:
            p_cl.add_run("Nenhum aluno em zona crítica nesta avaliação.")

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO AO GERAR DOSSIÊ: {str(e)}")
        err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 9. EXPORTADOR DE PEI OFICIAL (PREFEITURA)
# ==============================================================================
def gerar_docx_pei_oficial(nome_arquivo, dados_aluno, habilidades, curriculo_df):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10)

        # Cabeçalho
        p_cab = doc.add_paragraph()
        p_cab.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_cab = p_cab.add_run("SECRETARIA MUNICIPAL DA EDUCAÇÃO\nDEPARTAMENTO DE EDUCAÇÃO BÁSICA\nCOORDENAÇÃO TÉCNICA PEDAGÓGICA DA EDUCAÇÃO ESPECIAL\n\n")
        run_cab.bold = True
        
        p_tit = doc.add_paragraph()
        p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_tit = p_tit.add_run("PLANO EDUCACIONAL INDIVIDUALIZADO - PEI")
        run_tit.bold = True
        run_tit.font.size = Pt(12)
        
        doc.add_paragraph()
        
        # Dados do Aluno
        doc.add_paragraph("DADOS DO ALUNO").runs[0].bold = True
        
        p_d1 = doc.add_paragraph()
        p_d1.add_run("UNIDADE ESCOLAR: ").bold = True
        p_d1.add_run("Escola Municipal Flávio José Simões Costa\t\t")
        p_d1.add_run("ANO LETIVO: ").bold = True
        p_d1.add_run("2026")
        
        p_d2 = doc.add_paragraph()
        p_d2.add_run("NOME: ").bold = True
        p_d2.add_run(f"{dados_aluno.get('nome', '')}\t\t")
        p_d2.add_run("DATA NASC.: ").bold = True
        p_d2.add_run("________\t")
        p_d2.add_run("IDADE: ").bold = True
        p_d2.add_run("____\t")
        p_d2.add_run("TURMA: ").bold = True
        p_d2.add_run(f"{dados_aluno.get('turma', '')}")
        
        p_d3 = doc.add_paragraph()
        p_d3.add_run("Nome do Responsável: ").bold = True
        p_d3.add_run("_________________________________________________\t")
        p_d3.add_run("Fone: ").bold = True
        p_d3.add_run("_______________")
        
        p_d4 = doc.add_paragraph()
        p_d4.add_run("DEFICIÊNCIA(S)/CID: ").bold = True
        p_d4.add_run(f"{dados_aluno.get('cid', '')}\t\t")
        p_d4.add_run("SUSPEIÇÃO: ").bold = True
        p_d4.add_run("_______________")
        
        doc.add_page_break()
        
        # 1- Plano de acessibilidade curricular
        doc.add_paragraph("1- Plano de acessibilidade curricular.").runs[0].bold = True
        doc.add_paragraph("Com base no estudo de caso, observa-se que o mesmo apresenta dificuldade em:")
        
        for hab_name, hab_text in habilidades.items():
            p_h = doc.add_paragraph()
            p_h.add_run(f"{hab_name}: ").bold = True
            p_h.add_run(hab_text)
        
        doc.add_page_break()
        
        # 2- Plano Trimestral
        doc.add_paragraph("2- Plano Trimestral").runs[0].bold = True
        doc.add_paragraph("PLANEJAMENTO POR COMPONENTE CURRICULAR").runs[0].bold = True
        
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'DISCIPLINA'
        hdr_cells[1].text = 'OBJETIVOS APRENDIZAGEM'
        hdr_cells[2].text = 'ESTRATÉGIAS METODOLÓGICAS'
        hdr_cells[3].text = 'RECURSOS MATERIAIS'
        
        for cell in hdr_cells:
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        if not curriculo_df.empty:
            for _, row in curriculo_df.iterrows():
                row_cells = table.add_row().cells
                row_cells[0].text = "MATEMÁTICA"
                row_cells[1].text = str(row.get('Objetivos de Aprendizagem', ''))
                row_cells[2].text = str(row.get('Estratégias Metodológicas', ''))
                row_cells[3].text = str(row.get('Recursos Materiais', ''))
        
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO AO GERAR PEI OFICIAL: {str(e)}")
        err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    
# ==============================================================================
# 10. EXPORTADOR DE PLANEJAMENTO TRIMESTRAL (MACRO-SOSA)
# ==============================================================================
def gerar_docx_planejamento_trimestral(nome_arquivo, info, df_trimestre, config, lista_bncc):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        
        # 🚨 CONFIGURAÇÃO DE PÁGINA EM PAISAGEM (DEITADA)
        section = doc.sections[-1]
        new_width, new_height = section.page_height, section.page_width
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = new_width
        section.page_height = new_height
        section.left_margin = Inches(0.4)
        section.right_margin = Inches(0.4)
        section.top_margin = Inches(0.5)
        section.bottom_margin = Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Times New Roman'
        style.font.size = Pt(10)

        # --- CABEÇALHO OFICIAL ---
        logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
        if os.path.exists(logo_path):
            p_logo = doc.add_paragraph()
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.add_run().add_picture(logo_path, width=Inches(0.8))

        p_cab = doc.add_paragraph()
        p_cab.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_esc = p_cab.add_run("ESCOLA MUNICIPAL FLÁVIO JOSÉ SIMÕES COSTA\n")
        run_esc.bold = True
        run_esc.font.size = Pt(12)
        
        run_tit = p_cab.add_run(f"PLANEJAMENTO DO {info['trimestre'].upper()} - 2026\n")
        run_tit.bold = True
        run_tit.font.size = Pt(11)
        
        run_sub = p_cab.add_run(f"COMPONENTE CURRICULAR: MATEMÁTICA          PROFESSOR: RONALDO GOMES")
        run_sub.bold = True
        run_sub.font.size = Pt(11)
        
        doc.add_paragraph()

        # --- TABELA DE 7 COLUNAS ---
        table = doc.add_table(rows=2, cols=7)
        table.style = 'Table Grid'
        
        # Ajuste de larguras aproximadas para Paisagem
        widths = [Inches(0.8), Inches(1.8), Inches(1.0), Inches(2.2), Inches(1.8), Inches(1.0), Inches(1.4)]
        for i, w in enumerate(widths): 
            table.columns[i].width = w

        headers = ['Turma', 'Conteúdos', 'Habilidades', 'Objetivos', 'Metodologia', 'Recurso', 'Avaliação']
        for i, h in enumerate(headers):
            cell = table.cell(0, i)
            cell.text = h
            cell.paragraphs[0].runs[0].bold = True
            cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        # --- PREENCHIMENTO DOS DADOS ---
        row_cells = table.rows[1].cells
        
        # 1. Turma
        row_cells[0].text = info['turmas']
        
        # 2. Conteúdos (Extraídos do Banco)
        c_cont = row_cells[1]
        c_cont.text = ""
        for item in df_trimestre['CONTEUDO_ESPECIFICO'].unique():
            if str(item).strip():
                p = c_cont.add_paragraph(f"• {item}")
                p.paragraph_format.space_after = Pt(2)
            
        # 3. Habilidades (Códigos BNCC Extraídos via Regex)
        c_hab = row_cells[2]
        c_hab.text = ""
        if lista_bncc:
            for code in lista_bncc:
                p = c_hab.add_paragraph(f"• {code}")
                p.paragraph_format.space_after = Pt(2)
        else:
            c_hab.text = "Códigos BNCC não localizados."
            
        # 4. Objetivos (Extraídos do Banco)
        c_obj = row_cells[3]
        c_obj.text = ""
        for item in df_trimestre['OBJETIVOS'].unique():
            if str(item).strip():
                p = c_obj.add_paragraph(f"• {item}")
                p.paragraph_format.space_after = Pt(2)
            
        # 5, 6, 7. Textos Fixos Configuráveis
        row_cells[4].text = config['metodologia']
        row_cells[5].text = config['recursos']
        row_cells[6].text = config['avaliacao']
        
        # Formatação final da tabela
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for run in p.runs:
                        run.font.size = Pt(9)
                        
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO AO GERAR PLANEJAMENTO TRIMESTRAL: {str(e)}")
        err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    
# ==============================================================================
# 11. EXPORTADOR PEI NÍVEL 3 (QUALITATIVO / SENSORIAL) - BLINDADO
# ==============================================================================
def gerar_docx_pei_qualitativa(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Comic Sans MS' 
        style.font.size = Pt(14) 

        configurar_cabecalho_mestre(doc, info, "AVALIAÇÃO ADAPTADA (NÍVEL 3)", mostrar_nota=False)
        doc.add_paragraph()

        if not conteudo or len(str(conteudo).strip()) < 10:
            p = doc.add_paragraph("Ocorreu um erro na geração do Nível 3. Por favor, refine a questão no painel.")
            doc.save(file_stream)
            file_stream.seek(0)
            return file_stream

        linhas = str(conteudo).split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_after = Pt(12)

            # 🚨 NOVA REGRA: IMPRIME A RUBRICA DE OBSERVAÇÃO NO FINAL
            if "RUBRICA" in l_s.upper() or "GABARITO" in l_s.upper():
                p.paragraph_format.space_before = Pt(20)
                run = p.add_run(l_s.replace('**', ''))
                run.bold = True
                run.font.size = Pt(12)
                run.font.color.rgb = RGBColor(112, 48, 160)
                continue

            if "QUESTÃO" in l_s.upper():
                run = p.add_run(l_s)
                run.bold = True
                run.font.size = Pt(16)
            elif "[" in l_s and "PROMPT IMAGEM" in l_s.upper():
                p.paragraph_format.space_before = Pt(10)
                p.paragraph_format.space_after = Pt(50) 
                txt_img = l_s.replace("[", "").replace("]", "").strip()
                run = p.add_run(f"🖼️ [ ESPAÇO PARA IMAGEM: {txt_img} ]")
                run.font.italic = True
                run.font.size = Pt(10)
                run.font.color.rgb = RGBColor(150, 150, 150)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            elif "( ) SIM" in l_s.upper():
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(l_s)
                run.bold = True
                run.font.size = Pt(16)
            else:
                adicionar_texto_formatado(p, l_s)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO EXPORTER N3: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
