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
import ai_engine as ai 

# ==============================================================================
# FUNÇÕES AUXILIARES DE ENGENHARIA
# ==============================================================================
def set_row_height(row, height_pt):
    """Define a altura exata de uma linha de tabela no Word (Twips)"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

def ativar_colunas_nativas(doc, num_cols=2, espacamento=720):
    """Transforma a seção atual em colunas nativas do Word via manipulação de XML"""
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    new_section.start_type = WD_SECTION.CONTINUOUS
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), str(num_cols))
    cols.set(qn('w:space'), str(espacamento)) # 720 twips = 0,5 polegada
    return new_section

# ==============================================================================
# 1. MATERIAL DO ALUNO TÍPICO (FLUXO NATIVO - FONTE 12)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

        # --- CABEÇALHO (COLUNA ÚNICA) ---
        header_table = doc.add_table(rows=3, cols=5)
        header_table.style = 'Table Grid'
        widths = [Inches(0.8), Inches(2.8), Inches(1.0), Inches(1.4), Inches(1.5)]
        for i, w in enumerate(widths): header_table.columns[i].width = w
        
        c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
        header_table.cell(0, 1).merge(header_table.cell(0, 3)).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        header_table.cell(0, 4).paragraphs[0].add_run(info.get('trimestre', 'III TRIMESTRE')).font.bold = True
        header_table.cell(1, 1).merge(header_table.cell(1, 3)).paragraphs[0].add_run("ALUNO(A):").font.size = Pt(11)
        header_table.cell(1, 4).paragraphs[0].add_run("NOTA:").font.size = Pt(11)
        
        header_table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(10)
        header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano')}").font.size = Pt(10)
        header_table.cell(2, 3).paragraphs[0].add_run("DATA:").font.size = Pt(10)
        header_table.cell(2, 4).paragraphs[0].add_run("ATIVIDADE DE SALA").font.bold = True
        for row in header_table.rows: set_row_height(row, 25)

        doc.add_paragraph()

        # --- ATIVAÇÃO DE COLUNAS NATIVAS ---
        ativar_colunas_nativas(doc, num_cols=2, espacamento=720)

        # --- CONTEÚDO FLUIDO ---
        linhas = conteudo.split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(2)
            
            run = p.add_run(l_s.replace('**', ''))
            if "QUESTÃO" in l_s.upper():
                run.font.bold, run.font.size = True, Pt(12)
                p.paragraph_format.space_before = Pt(6)
            else:
                run.font.size = Pt(12)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO ALUNO: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 2. GUIA DO PROFESSOR (FLUXO NATIVO - REGÊNCIA E LOUSA)
# ==============================================================================
def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

        # --- CABEÇALHO (COLUNA ÚNICA) ---
        header_table = doc.add_table(rows=2, cols=3)
        header_table.style = 'Table Grid'
        header_table.cell(0, 0).merge(header_table.cell(0, 2)).paragraphs[0].add_run("GUIA DE REGÊNCIA E ESQUEMA DE LOUSA - PROF. RONALDO GOMES").font.bold = True
        header_table.cell(1, 0).paragraphs[0].add_run(f"ANO: {info.get('ano')}").font.size = Pt(10)
        header_table.cell(1, 1).paragraphs[0].add_run(f"SEMANA: {info.get('semana')}").font.size = Pt(10)
        header_table.cell(1, 2).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre')}").font.size = Pt(10)
        for row in header_table.rows: set_row_height(row, 22)

        doc.add_paragraph()

        # --- ATIVAÇÃO DE COLUNAS NATIVAS ---
        ativar_colunas_nativas(doc, num_cols=2, espacamento=400)

        # --- CONTEÚDO FLUIDO ---
        conteudo_limpo = conteudo.replace("[COLUNA_1]", "").replace("[COLUNA_2]", "")
        linhas = conteudo_limpo.split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            p = doc.add_paragraph()
            p.paragraph_format.space_after = Pt(2)
            
            if "[" in l_s and "]" in l_s: # Prompts Visuais
                run = p.add_run(l_s.replace('**', ''))
                run.font.italic, run.font.size = True, Pt(10)
                run.font.color.rgb = RGBColor(0, 102, 204)
            elif l_s.isupper(): # Títulos de Seção
                run = p.add_run(l_s.replace('**', ''))
                run.font.bold, run.font.size = True, Pt(11)
                p.paragraph_format.space_before = Pt(8)
            else:
                run = p.add_run(l_s.replace('**', ''))
                run.font.size = Pt(11)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO PROF: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 3. MATERIAL PEI (FLUXO NATIVO - FONTE 14 DUA)
# ==============================================================================
def gerar_docx_pei_v25(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

        # --- CABEÇALHO PEI ---
        header_table = doc.add_table(rows=2, cols=2)
        header_table.style = 'Table Grid'
        header_table.cell(0, 0).merge(header_table.cell(0, 1)).paragraphs[0].add_run("ATIVIDADE ADAPTADA - DESENHO UNIVERSAL (PEI)").font.bold = True
        header_table.cell(1, 0).paragraphs[0].add_run("ALUNO(A):").font.size = Pt(12)
        header_table.cell(1, 1).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre')}").font.size = Pt(12)
        for row in header_table.rows: set_row_height(row, 30)

        doc.add_paragraph()

        # --- ATIVAÇÃO DE COLUNAS NATIVAS ---
        ativar_colunas_nativas(doc, num_cols=2, espacamento=720)

        # --- CONTEÚDO FLUIDO PEI ---
        linhas = conteudo.split('\n')
        for linha in linhas:
            l_s = linha.strip()
            if not l_s: continue
            p = doc.add_paragraph()
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.space_after = Pt(3)
            
            if any(tag in l_s.upper() for tag in ["PARA LEMBRAR", "PASSO A PASSO", "ATIVIDADES"]):
                run = p.add_run(f" {l_s.replace('**', '')}")
                run.font.bold, run.font.size = True, Pt(15)
                p.paragraph_format.space_before = Pt(10)
            else:
                run = p.add_run(l_s.replace('**', ''))
                run.font.size = Pt(14) # FONTE 14 OBRIGATÓRIA PEI

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO PEI: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 4. PROVA OFICIAL (FLUXO NATIVO - GABARITO ENEM)
# ==============================================================================
def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)
        
        # Lógica de Valor Sincronizada
        tipo_raw = info.get('tipo_prova', '').upper()
        v_total_num = 3.0 if "TESTE" in tipo_raw else 4.0 if "PROVA" in tipo_raw else 10.0
        v_total_str = f"{v_total_num:.1f}".replace('.', ',')
        qtd_q = int(info.get('qtd_questoes', 10))
        v_quest = v_total_num / qtd_q

        # --- CABEÇALHO ---
        header_table = doc.add_table(rows=3, cols=5)
        header_table.style = 'Table Grid'
        widths = [Inches(0.8), Inches(2.8), Inches(1.0), Inches(1.4), Inches(1.5)]
        for i, w in enumerate(widths): header_table.columns[i].width = w

        c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
        header_table.cell(0, 1).merge(header_table.cell(0, 3)).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        header_table.cell(0, 4).paragraphs[0].add_run(info.get('trimestre', 'III TRIMESTRE')).font.bold = True
        header_table.cell(1, 1).merge(header_table.cell(1, 3)).paragraphs[0].add_run("ALUNO(A):").font.size = Pt(11)
        header_table.cell(1, 4).paragraphs[0].add_run("NOTA:").font.size = Pt(11)
        header_table.cell(2, 1).paragraphs[0].add_run(f"PROF: Ronaldo Gomes").font.size = Pt(10)
        header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano')}").font.size = Pt(10)
        header_table.cell(2, 3).paragraphs[0].add_run(f"DATA:").font.size = Pt(10)
        header_table.cell(2, 4).paragraphs[0].add_run(f"VALOR: {v_total_str} PONTOS").font.bold = True
        for row in header_table.rows: set_row_height(row, 25)

        doc.add_paragraph()

        # --- ORIENTAÇÕES E GABARITO (LADO A LADO) ---
        top_table = doc.add_table(rows=1, cols=2)
        top_table.columns[0].width = Inches(3.5)
        top_table.columns[1].width = Inches(4.0)

        c_orient = top_table.cell(0, 0)
        p_tit = c_orient.add_paragraph()
        p_tit.add_run("ORIENTAÇÕES PARA AVALIAÇÃO:").font.bold = True
        orientacoes = [
            "A interpretação faz parte da prova.",
            "Use apenas CANETA AZUL ou PRETA.",
            "Cálculos são obrigatórios para validar a questão.",
            "Pinte completamente o círculo no gabarito.",
            f"Valor Total: {v_total_str} | Cada questão: {v_quest:.2f}".replace('.', ',')
        ]
        for idx, text in enumerate(orientacoes, 1):
            p = c_orient.add_paragraph()
            p.add_run(f"{idx}. {text}").font.size = Pt(9)

        c_gab = top_table.cell(0, 1)
        gab_grid = c_gab.add_table(rows=11, cols=6)
        gab_grid.style = 'Table Grid'
        for r in range(11):
            for c in range(6): gab_grid.cell(r, c).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        for i, lab in enumerate(["Q", "A", "B", "C", "D", "E"]):
            gab_grid.cell(0, i).paragraphs[0].add_run(lab).font.bold = True
        for r in range(1, 11):
            gab_grid.cell(r, 0).paragraphs[0].add_run(f"{r:02d}").font.size = Pt(9)
            for col in range(1, 6):
                run_b = gab_grid.cell(r, col).paragraphs[0].add_run("○")
                run_b.font.size = Pt(14)

        # --- ATIVAÇÃO DE COLUNAS NATIVAS ---
        ativar_colunas_nativas(doc, num_cols=2, espacamento=720)

        # --- PROCESSAMENTO DAS QUESTÕES ---
        questoes_raw = ai.extrair_tag(conteudo_ia, "QUESTOES")
        questoes_raw = re.sub(r'\(\d+,\d+\s*ponto[s]?\)', '', questoes_raw)
        padrao_split = r'(\d+[\s\.\ª\º]*Questão[\s\.\:]*)'
        partes = re.split(padrao_split, questoes_raw, flags=re.IGNORECASE)
        
        i = 1
        while i < len(partes):
            marcador = partes[i].strip()
            corpo = partes[i+1].strip() if i+1 < len(partes) else ""
            p_q = doc.add_paragraph()
            p_q.paragraph_format.space_before = Pt(6)
            run_q = p_q.add_run(f"{marcador} ({v_quest:.2f} ponto) - ".replace('.', ','))
            run_q.font.bold, run_q.font.size = True, Pt(12)
            
            linhas = corpo.split('\n')
            for linha in linhas:
                l_s = linha.strip()
                if not l_s: continue
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.line_spacing = 1.0
                run = p.add_run(l_s.replace('**', ''))
                run.font.size = Pt(12)
                if re.match(r'^[A-E][\)\.]', l_s): p.paragraph_format.left_indent = Inches(0.2)
            i += 2

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO PROVA: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 5. PLANO PEDAGÓGICO (COLUNA ÚNICA - RIGOR PHC V26)
# ==============================================================================
def gerar_docx_plano_pedagogico_v18(titulo_arquivo, dados, info):
    import os
    import io
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_ALIGN_VERTICAL

    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
        section.left_margin, section.right_margin = Inches(0.6), Inches(0.6)

        # --- 1. CABEÇALHO OFICIAL COM LOGO E TRIMESTRE ---
        table = doc.add_table(rows=3, cols=3)
        table.style = 'Table Grid'
        
        # Ajuste de larguras das colunas do cabeçalho
        widths = [Inches(1.2), Inches(3.5), Inches(2.0)]
        for i, w in enumerate(widths):
            table.columns[i].width = w

        # Inserção da Logo
        if os.path.exists("logo_escola.png"):
            cell_logo = table.cell(0, 0)
            cell_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p_logo = cell_logo.paragraphs[0]
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.8))
        
        # Textos do Cabeçalho
        table.cell(0, 1).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        table.cell(0, 2).paragraphs[0].add_run("PLANO DE ENSINO SEMANAL").font.bold = True
        
        # Linha do Professor e Ano
        p_prof = table.cell(1, 0).merge(table.cell(1, 1)).paragraphs[0]
        p_prof.add_run(f"Professor: Ronaldo Gomes")
        
        p_ano = table.cell(1, 2).paragraphs[0]
        p_ano.add_run(f"Ano: {info.get('ano', '')}")
        
        # Linha da Semana e Trimestre (Substituindo a Data)
        p_sem = table.cell(2, 0).merge(table.cell(2, 1)).paragraphs[0]
        p_sem.add_run(f"Semana: {info.get('semana', '')}")
        
        p_trim = table.cell(2, 2).paragraphs[0]
        p_trim.add_run(f"Trimestre: {info.get('trimestre', 'I Trimestre')}")

        doc.add_paragraph() # Espaçador

        # --- 2. CORPO DO PLANO (TEXTO JUSTIFICADO) ---
        campos = [
            ("CONTEÚDO GERAL EIXO:", "geral"), 
            ("CONTEÚDOS ESPECÍFICOS:", "especificos"), 
            ("OBJETIVOS DE ENSINO:", "objetivos"), 
            ("METODOLOGIA:", "metodologia"), 
            ("AVALIAÇÃO:", "avaliacao"), 
            ("OBSERVAÇÃO:", "observacao"), 
            ("ADAPTAÇÃO PEI:", "pei")
        ]

        for label, chave in campos:
            p = doc.add_paragraph()
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # JUSTIFICAÇÃO OBRIGATÓRIA
            p.paragraph_format.space_after = Pt(6)
            
            # Rótulo em Negrito
            run_label = p.add_run(label)
            run_label.font.bold = True
            run_label.font.size = Pt(11)
            
            # Conteúdo
            texto_limpo = str(dados.get(chave, "")).replace(label, "").replace("**", "").strip()
            if texto_limpo.startswith(":"): texto_limpo = texto_limpo[1:].strip()
            
            run_txt = p.add_run(f" {texto_limpo}")
            run_txt.font.size = Pt(11)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO CRÍTICO NO PLANO: {str(e)}")
        err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 6. APRESENTAÇÃO PPTX (PRESERVADO)
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
