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
# 1. MATERIAL DO ALUNO TÍPICO (FLUXO NATIVO V26.8 - ELITE)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    doc = Document()
    
    # Configurações de Estilo Global
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- 1. CABEÇALHO (COLUNA ÚNICA COM LOGO E SEM NOTA) ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(1.0), Inches(1.4), Inches(1.5)]
    for i, w in enumerate(widths): header_table.columns[i].width = w
    
    # Mesclagens para Logo e Escola
    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 3))
    c_trim = header_table.cell(0, 4)
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4))
    
    # Inserção da Logo
    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Inches(0.75))

    # Textos do Cabeçalho
    header_table.cell(0, 1).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    header_table.cell(0, 4).paragraphs[0].add_run(info.get('trimestre', 'III TRIMESTRE')).font.bold = True
    
    p_alu = header_table.cell(1, 1).paragraphs[0]
    p_alu.add_run("ALUNO(A):").font.size = Pt(11)
    
    header_table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(10)
    header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano')}").font.size = Pt(10)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA:").font.size = Pt(10)
    header_table.cell(2, 4).paragraphs[0].add_run("ATIVIDADE DE SALA").font.bold = True

    for row in header_table.rows: set_row_height(row, 25)

    doc.add_paragraph()

    # --- 2. ATIVAÇÃO DE COLUNAS NATIVAS ---
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '720')

    # --- 3. CONTEÚDO FLUIDO E JUSTIFICADO ---
    linhas = conteudo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)

        # Lógica para Questão na mesma linha
        match_q = re.match(r'^(QUESTÃO\s+\d+)(.*)', l_s, re.IGNORECASE)
        
        if match_q:
            label = match_q.group(1)
            resto = match_q.group(2)
            run_l = p.add_run(label.upper())
            run_l.font.bold = True
            run_l.font.size = Pt(11)
            p.add_run(resto.replace('**', ''))
            p.paragraph_format.space_before = Pt(6)
            
        elif "PROMPT IMAGEM:" in l_s.upper():
            # Formatação especial para Prompts de Imagem
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_tag = p.add_run("PROMPT IMAGEM: ")
            run_tag.font.bold = True
            run_tag.font.size = Pt(8)
            run_tag.font.color.rgb = RGBColor(100, 100, 100)
            
            desc_img = l_s.upper().replace("PROMPT IMAGEM:", "").strip()
            run_desc = p.add_run(desc_img)
            run_desc.font.size = Pt(8)
            run_desc.font.italic = True
            run_desc.font.color.rgb = RGBColor(100, 100, 100)
            
        else:
            # Texto normal justificado
            run = p.add_run(l_s.replace('**', ''))
            run.font.size = Pt(11)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 2. GUIA DO PROFESSOR (FLUXO NATIVO V27.5 - ELITE)
# ==============================================================================
def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    doc = Document()
    
    # Estilo Global
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- 1. CABEÇALHO TÉCNICO (SEM LOGO - LIMPO) ---
    header_table = doc.add_table(rows=2, cols=3)
    header_table.style = 'Table Grid'
    
    # Título Principal
    c_tit = header_table.cell(0, 0).merge(header_table.cell(0, 2))
    p_tit = c_tit.paragraphs[0]
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tit = p_tit.add_run("GUIA DE REGÊNCIA E ESQUEMA DE LOUSA - PROF. RONALDO GOMES")
    run_tit.font.bold = True
    run_tit.font.size = Pt(12)

    # Metadados
    header_table.cell(1, 0).paragraphs[0].add_run(f"ANO: {info.get('ano', '')}").font.size = Pt(10)
    header_table.cell(1, 1).paragraphs[0].add_run(f"SEMANA: {info.get('semana', '')}").font.size = Pt(10)
    header_table.cell(1, 2).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre', 'I')}")

    for row in header_table.rows: set_row_height(row, 22)
    doc.add_paragraph()

    # --- 2. ATIVAÇÃO DE COLUNAS NATIVAS ---
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '400') # Espaçamento mais estreito para o professor

    # --- 3. CONTEÚDO FLUIDO E JUSTIFICADO ---
    # Limpeza de tags de controle da IA
    conteudo_limpo = conteudo.replace("[PROFESSOR]", "").replace("[COLUNA_1]", "").replace("[COLUNA_2]", "")
    
    linhas = conteudo_limpo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)

        # Identificação de Títulos de Seção (MOMENTO PHC, EXPLICAÇÃO, etc)
        if l_s.isupper() and (":" in l_s or len(l_s) < 30):
            run = p.add_run(l_s.replace('**', ''))
            run.font.bold = True
            run.font.size = Pt(11)
            p.paragraph_format.space_before = Pt(8)
            
        # Identificação de Prompts Visuais [PROMPT: ...]
        elif "[" in l_s and "]" in l_s:
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(l_s.replace('**', ''))
            run.font.italic = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 102, 204) # Azul Royal para destaque visual
            
        # Identificação de Dicas de Regência
        elif "DICA DE REGÊNCIA" in l_s.upper():
            run = p.add_run(l_s.replace('**', ''))
            run.font.bold = True
            run.font.color.rgb = RGBColor(200, 0, 0) # Vermelho para atenção
            
        else:
            # Texto normal justificado
            run = p.add_run(l_s.replace('**', ''))
            run.font.size = Pt(10.5)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. MATERIAL PEI ADAPTADO (VERSÃO ELITE V40 - FONTE 12 PADRONIZADA)
# ==============================================================================
def gerar_docx_pei_v25(titulo_doc, conteudo, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    doc = Document()
    
    # --- CONFIGURAÇÃO DE ESTILO GLOBAL (FORÇANDO FONTE 12) ---
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

    # --- 1. CABEÇALHO PADRÃO PREFEITURA ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(1.0), Inches(1.4), Inches(1.5)]
    for i, w in enumerate(widths): header_table.columns[i].width = w
    
    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
    header_table.cell(0, 1).merge(header_table.cell(0, 3)).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    header_table.cell(0, 4).paragraphs[0].add_run(info.get('trimestre', 'I TRIMESTRE')).font.bold = True
    
    header_table.cell(1, 1).merge(header_table.cell(1, 3)).paragraphs[0].add_run("ALUNO(A):").font.size = Pt(12)
    header_table.cell(1, 4).paragraphs[0].add_run("NOTA:").font.size = Pt(12)
    
    header_table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(10)
    header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano', '')}").font.size = Pt(10)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA:").font.size = Pt(10)
    header_table.cell(2, 4).paragraphs[0].add_run("ATIVIDADE ADAPTADA").font.bold = True

    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Inches(0.75))

    for row in header_table.rows: set_row_height(row, 25)
    doc.add_paragraph()

    # --- 2. PROCESSAMENTO DE CONTEÚDO (LIMPEZA E FONTE 12) ---
    # Limpeza de Markdown e caracteres residuais da IA
    conteudo_limpo = re.sub(r'[*#]', '', conteudo)
    conteudo_limpo = re.sub(r'\[PEI\]|\[GABARITO_PEI\]', '', conteudo_limpo, flags=re.IGNORECASE)
    
    linhas = conteudo_limpo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        # Ignora linhas que são apenas pontuação residual ou vazias
        if not l_s or l_s in [":", "():", ".", "-"]: continue
        
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Títulos de Seção (Caixa Alta)
        if l_s.isupper() and len(l_s) < 50:
            run = p.add_run(l_s)
            run.font.bold = True
            run.font.size = Pt(12)
            p.paragraph_format.space_before = Pt(12)
        
        # Prompts de Imagem (Formatação Cinza Pequena para não poluir)
        elif "PROMPT IMAGEM" in l_s.upper():
            run = p.add_run(f"💡 {l_s}")
            run.font.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(120, 120, 120)
            p.paragraph_format.space_after = Pt(2)
            
        else:
            # Texto Normal Padronizado em 12
            run = p.add_run(l_s)
            run.font.size = Pt(12)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 4. PROVA OFICIAL (FLUXO NATIVO - GABARITO ENEM)
# ==============================================================================
def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)
        
        # Lógica de Valor
        tipo_raw = info.get('tipo_prova', '').upper()
        v_total_num = 3.0 if "TESTE" in tipo_raw else 4.0 if "PROVA" in tipo_raw else 10.0
        v_total_str = f"{v_total_num:.1f}".replace('.', ',')
        qtd_q = int(info.get('qtd_questoes', 10))
        v_quest = v_total_num / qtd_q

        # --- 1. CABEÇALHO ---
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
        
        logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
        if os.path.exists(logo_path):
            c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            c_logo.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            c_logo.paragraphs[0].add_run().add_picture(logo_path, width=Inches(0.7))
        
        for row in header_table.rows: set_row_height(row, 25)
        doc.add_paragraph()

        # --- 2. ORIENTAÇÕES E GABARITO ---
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

        # --- 3. ATIVAÇÃO DE COLUNAS NATIVAS ---
        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '720')

        # --- 4. PROCESSAMENTO DAS QUESTÕES (BLINDAGEM SOSA) ---
        questoes_raw = ai.extrair_tag(conteudo_ia, "QUESTOES")
        
        # FALLBACK: Se não achou a tag QUESTOES, usa o conteúdo bruto (essencial para PEI)
        if not questoes_raw or len(questoes_raw) < 10:
            questoes_raw = conteudo_ia
            # Limpa tags residuais se houver
            questoes_raw = re.sub(r'\[PEI\]|\[GABARITO_PEI\]|\[IMAGENS_PEI\]', '', questoes_raw, flags=re.IGNORECASE)

        questoes_raw = re.sub(r'\(\d+,\d+\s*ponto[s]?\)', '', questoes_raw)
        padrao_split = r'(\d+[\s\.\ª\º]*Questão[\s\.\:]*)'
        partes = re.split(padrao_split, questoes_raw, flags=re.IGNORECASE)
        
        if len(partes) < 2:
            # Se não conseguiu fatiar por "Questão", imprime o bloco inteiro justificado
            for linha in questoes_raw.split('\n'):
                l_s = linha.strip()
                if not l_s: continue
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.add_run(l_s.replace('**', '')).font.size = Pt(12)
        else:
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
# 5. PLANO PEDAGÓGICO (VERSÃO ELITE V26 - JUSTIFICADO + LOGO + TRIMESTRE)
# ==============================================================================
def gerar_docx_plano_pedagogico_ELITE(titulo_arquivo, dados, info):
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
        # Margens de documento oficial
        section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        # --- 1. CABEÇALHO REESTRUTURADO (SEM CAMPO DE DATA) ---
        table = doc.add_table(rows=3, cols=3)
        table.style = 'Table Grid'
        
        # Larguras fixas para evitar deformação
        widths = [Inches(1.1), Inches(3.6), Inches(2.0)]
        for i, w in enumerate(widths):
            table.columns[i].width = w

        # Busca exaustiva pela Logo (Tenta os dois nomes comuns no seu sistema)
        logo_path = None
        for nome in ["logo_escola.png", "logo.png"]:
            if os.path.exists(nome):
                logo_path = nome
                break

        if logo_path:
            cell_logo = table.cell(0, 0).merge(table.cell(2, 0)) # Logo ocupa as 3 linhas da esquerda
            cell_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p_logo = cell_logo.paragraphs[0]
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.add_run().add_picture(logo_path, width=Inches(0.85))
        
        # Escola e Título
        p_esc = table.cell(0, 1).paragraphs[0]
        p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        
        p_tit = table.cell(0, 2).paragraphs[0]
        p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_tit.add_run("PLANO DE ENSINO SEMANAL").font.bold = True
        
        # Professor e Ano
        table.cell(1, 1).paragraphs[0].add_run(f"Professor: Ronaldo Gomes").font.size = Pt(10)
        table.cell(1, 2).paragraphs[0].add_run(f"Ano: {info.get('ano', '')}").font.size = Pt(10)
        
        # Semana e Trimestre (AQUI SUBSTITUÍMOS A DATA DEFINITIVAMENTE)
        table.cell(2, 1).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}").font.size = Pt(10)
        
        # Pega o trimestre do info ou tenta extrair da semana
        trim_val = info.get('trimestre', 'I Trimestre')
        table.cell(2, 2).paragraphs[0].add_run(f"Trimestre: {trim_val}").font.bold = True

        doc.add_paragraph() # Espaço

        # --- 2. CORPO DO PLANO (PRENSA ACADÊMICA) ---
        campos = [
            ("OBJETO DE CONHECIMENTO (EIXO):", "geral"), 
            ("CONTEÚDOS ESPECÍFICOS:", "especificos"), 
            ("OBJETIVOS DE APRENDIZAGEM:", "objetivos"), 
            ("RECURSOS DIDÁTICOS:", "recursos"), # NOVA LINHA
            ("PROCEDIMENTOS METODOLÓGICOS:", "metodologia"), 
            ("AVALIAÇÃO E ACOMPANHAMENTO:", "avaliacao"), 
            ("ESTRATÉGIAS DE ACESSIBILIDADE (DUA):", "pei")
        ]

        for label, chave in campos:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # JUSTIFICAÇÃO NATIVA
            p.paragraph_format.space_after = Pt(8)
            
            # Rótulo em Negrito e Caixa Alta
            run_label = p.add_run(label)
            run_label.font.bold = True
            run_label.font.size = Pt(11)
            
            # Conteúdo limpo de Markdown
            texto_raw = str(dados.get(chave, ""))
            texto_limpo = texto_raw.replace(label, "").replace("**", "").replace("#", "").strip()
            if texto_limpo.startswith(":"): texto_limpo = texto_limpo[1:].strip()
            
            run_txt = p.add_run(f" {texto_limpo}")
            run_txt.font.size = Pt(11)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO CRÍTICO: {str(e)}")
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
# 1. MATERIAL DO ALUNO TÍPICO (FLUXO NATIVO V26.8 - ELITE)
# ==============================================================================
def gerar_docx_aluno_v24(titulo_doc, conteudo, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    doc = Document()
    
    # Configurações de Estilo Global
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- 1. CABEÇALHO (COLUNA ÚNICA COM LOGO E SEM NOTA) ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(1.0), Inches(1.4), Inches(1.5)]
    for i, w in enumerate(widths): header_table.columns[i].width = w
    
    # Mesclagens para Logo e Escola
    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
    c_escola = header_table.cell(0, 1).merge(header_table.cell(0, 3))
    c_trim = header_table.cell(0, 4)
    c_aluno = header_table.cell(1, 1).merge(header_table.cell(1, 4))
    
    # Inserção da Logo
    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Inches(0.75))

    # Textos do Cabeçalho
    header_table.cell(0, 1).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    header_table.cell(0, 4).paragraphs[0].add_run(info.get('trimestre', 'III TRIMESTRE')).font.bold = True
    
    p_alu = header_table.cell(1, 1).paragraphs[0]
    p_alu.add_run("ALUNO(A):").font.size = Pt(11)
    
    header_table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(10)
    header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano')}").font.size = Pt(10)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA:").font.size = Pt(10)
    header_table.cell(2, 4).paragraphs[0].add_run("ATIVIDADE DE SALA").font.bold = True

    for row in header_table.rows: set_row_height(row, 25)

    doc.add_paragraph()

    # --- 2. ATIVAÇÃO DE COLUNAS NATIVAS ---
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '720')

    # --- 3. CONTEÚDO FLUIDO E JUSTIFICADO ---
    linhas = conteudo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)

        # Lógica para Questão na mesma linha
        match_q = re.match(r'^(QUESTÃO\s+\d+)(.*)', l_s, re.IGNORECASE)
        
        if match_q:
            label = match_q.group(1)
            resto = match_q.group(2)
            run_l = p.add_run(label.upper())
            run_l.font.bold = True
            run_l.font.size = Pt(11)
            p.add_run(resto.replace('**', ''))
            p.paragraph_format.space_before = Pt(6)
            
        elif "PROMPT IMAGEM:" in l_s.upper():
            # Formatação especial para Prompts de Imagem
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_tag = p.add_run("PROMPT IMAGEM: ")
            run_tag.font.bold = True
            run_tag.font.size = Pt(8)
            run_tag.font.color.rgb = RGBColor(100, 100, 100)
            
            desc_img = l_s.upper().replace("PROMPT IMAGEM:", "").strip()
            run_desc = p.add_run(desc_img)
            run_desc.font.size = Pt(8)
            run_desc.font.italic = True
            run_desc.font.color.rgb = RGBColor(100, 100, 100)
            
        else:
            # Texto normal justificado
            run = p.add_run(l_s.replace('**', ''))
            run.font.size = Pt(11)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 2. GUIA DO PROFESSOR (FLUXO NATIVO V27.5 - ELITE)
# ==============================================================================
def gerar_docx_professor_v25(titulo_doc, conteudo, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    doc = Document()
    
    # Estilo Global
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(11)

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
    section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

    # --- 1. CABEÇALHO TÉCNICO (SEM LOGO - LIMPO) ---
    header_table = doc.add_table(rows=2, cols=3)
    header_table.style = 'Table Grid'
    
    # Título Principal
    c_tit = header_table.cell(0, 0).merge(header_table.cell(0, 2))
    p_tit = c_tit.paragraphs[0]
    p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tit = p_tit.add_run("GUIA DE REGÊNCIA E ESQUEMA DE LOUSA - PROF. RONALDO GOMES")
    run_tit.font.bold = True
    run_tit.font.size = Pt(12)

    # Metadados
    header_table.cell(1, 0).paragraphs[0].add_run(f"ANO: {info.get('ano', '')}").font.size = Pt(10)
    header_table.cell(1, 1).paragraphs[0].add_run(f"SEMANA: {info.get('semana', '')}").font.size = Pt(10)
    header_table.cell(1, 2).paragraphs[0].add_run(f"TRIMESTRE: {info.get('trimestre', 'I')}")

    for row in header_table.rows: set_row_height(row, 22)
    doc.add_paragraph()

    # --- 2. ATIVAÇÃO DE COLUNAS NATIVAS ---
    new_section = doc.add_section(WD_SECTION.CONTINUOUS)
    sectPr = new_section._sectPr
    cols = sectPr.xpath('./w:cols')[0]
    cols.set(qn('w:num'), '2')
    cols.set(qn('w:space'), '400') # Espaçamento mais estreito para o professor

    # --- 3. CONTEÚDO FLUIDO E JUSTIFICADO ---
    # Limpeza de tags de controle da IA
    conteudo_limpo = conteudo.replace("[PROFESSOR]", "").replace("[COLUNA_1]", "").replace("[COLUNA_2]", "")
    
    linhas = conteudo_limpo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        if not l_s: continue
        
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.0
        p.paragraph_format.space_after = Pt(2)

        # Identificação de Títulos de Seção (MOMENTO PHC, EXPLICAÇÃO, etc)
        if l_s.isupper() and (":" in l_s or len(l_s) < 30):
            run = p.add_run(l_s.replace('**', ''))
            run.font.bold = True
            run.font.size = Pt(11)
            p.paragraph_format.space_before = Pt(8)
            
        # Identificação de Prompts Visuais [PROMPT: ...]
        elif "[" in l_s and "]" in l_s:
            p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run = p.add_run(l_s.replace('**', ''))
            run.font.italic = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(0, 102, 204) # Azul Royal para destaque visual
            
        # Identificação de Dicas de Regência
        elif "DICA DE REGÊNCIA" in l_s.upper():
            run = p.add_run(l_s.replace('**', ''))
            run.font.bold = True
            run.font.color.rgb = RGBColor(200, 0, 0) # Vermelho para atenção
            
        else:
            # Texto normal justificado
            run = p.add_run(l_s.replace('**', ''))
            run.font.size = Pt(10.5)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 3. MATERIAL PEI ADAPTADO (VERSÃO ELITE V40 - FONTE 12 PADRONIZADA)
# ==============================================================================
def gerar_docx_pei_v25(titulo_doc, conteudo, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    doc = Document()
    
    # --- CONFIGURAÇÃO DE ESTILO GLOBAL (FORÇANDO FONTE 12) ---
    style = doc.styles['Normal']
    style.font.name = 'Arial'
    style.font.size = Pt(12)
    style.paragraph_format.space_after = Pt(6)
    style.paragraph_format.line_spacing = 1.15

    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
    section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

    # --- 1. CABEÇALHO PADRÃO PREFEITURA ---
    header_table = doc.add_table(rows=3, cols=5)
    header_table.style = 'Table Grid'
    widths = [Inches(0.9), Inches(2.8), Inches(1.0), Inches(1.4), Inches(1.5)]
    for i, w in enumerate(widths): header_table.columns[i].width = w
    
    c_logo = header_table.cell(0, 0).merge(header_table.cell(2, 0))
    header_table.cell(0, 1).merge(header_table.cell(0, 3)).paragraphs[0].add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    header_table.cell(0, 4).paragraphs[0].add_run(info.get('trimestre', 'I TRIMESTRE')).font.bold = True
    
    header_table.cell(1, 1).merge(header_table.cell(1, 3)).paragraphs[0].add_run("ALUNO(A):").font.size = Pt(12)
    header_table.cell(1, 4).paragraphs[0].add_run("NOTA:").font.size = Pt(12)
    
    header_table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(10)
    header_table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano', '')}").font.size = Pt(10)
    header_table.cell(2, 3).paragraphs[0].add_run("DATA:").font.size = Pt(10)
    header_table.cell(2, 4).paragraphs[0].add_run("ATIVIDADE ADAPTADA").font.bold = True

    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p_logo = c_logo.paragraphs[0]
        p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_logo.add_run().add_picture(logo_path, width=Inches(0.75))

    for row in header_table.rows: set_row_height(row, 25)
    doc.add_paragraph()

    # --- 2. PROCESSAMENTO DE CONTEÚDO (LIMPEZA E FONTE 12) ---
    # Limpeza de Markdown e caracteres residuais da IA
    conteudo_limpo = re.sub(r'[*#]', '', conteudo)
    conteudo_limpo = re.sub(r'\[PEI\]|\[GABARITO_PEI\]', '', conteudo_limpo, flags=re.IGNORECASE)
    
    linhas = conteudo_limpo.split('\n')
    for linha in linhas:
        l_s = linha.strip()
        # Ignora linhas que são apenas pontuação residual ou vazias
        if not l_s or l_s in [":", "():", ".", "-"]: continue
        
        p = doc.add_paragraph()
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        # Títulos de Seção (Caixa Alta)
        if l_s.isupper() and len(l_s) < 50:
            run = p.add_run(l_s)
            run.font.bold = True
            run.font.size = Pt(12)
            p.paragraph_format.space_before = Pt(12)
        
        # Prompts de Imagem (Formatação Cinza Pequena para não poluir)
        elif "PROMPT IMAGEM" in l_s.upper():
            run = p.add_run(f"💡 {l_s}")
            run.font.italic = True
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(120, 120, 120)
            p.paragraph_format.space_after = Pt(2)
            
        else:
            # Texto Normal Padronizado em 12
            run = p.add_run(l_s)
            run.font.size = Pt(12)

    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

# ==============================================================================
# 4. PROVA OFICIAL (FLUXO NATIVO - GABARITO ENEM)
# ==============================================================================
def gerar_docx_prova_v25(titulo_doc, conteudo_ia, info):
    import re, io, os
    from docx import Document
    from docx.shared import Inches, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.section import WD_SECTION
    from docx.enum.table import WD_ALIGN_VERTICAL
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    def set_row_height(row, height_pt):
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        trHeight = OxmlElement('w:trHeight')
        trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
        trHeight.set(qn('w:hRule'), "atLeast")
        trPr.append(trHeight)

    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.3), Inches(0.3)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)
        
        # Lógica de Valor
        tipo_raw = info.get('tipo_prova', '').upper()
        v_total_num = 3.0 if "TESTE" in tipo_raw else 4.0 if "PROVA" in tipo_raw else 10.0
        v_total_str = f"{v_total_num:.1f}".replace('.', ',')
        qtd_q = int(info.get('qtd_questoes', 10))
        v_quest = v_total_num / qtd_q

        # --- 1. CABEÇALHO ---
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
        
        logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
        if os.path.exists(logo_path):
            c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            c_logo.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            c_logo.paragraphs[0].add_run().add_picture(logo_path, width=Inches(0.7))
        
        for row in header_table.rows: set_row_height(row, 25)
        doc.add_paragraph()

        # --- 2. ORIENTAÇÕES E GABARITO ---
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

        # --- 3. ATIVAÇÃO DE COLUNAS NATIVAS ---
        new_section = doc.add_section(WD_SECTION.CONTINUOUS)
        sectPr = new_section._sectPr
        cols = sectPr.xpath('./w:cols')[0]
        cols.set(qn('w:num'), '2')
        cols.set(qn('w:space'), '720')

        # --- 4. PROCESSAMENTO DAS QUESTÕES (BLINDAGEM SOSA) ---
        questoes_raw = ai.extrair_tag(conteudo_ia, "QUESTOES")
        
        # FALLBACK: Se não achou a tag QUESTOES, usa o conteúdo bruto (essencial para PEI)
        if not questoes_raw or len(questoes_raw) < 10:
            questoes_raw = conteudo_ia
            # Limpa tags residuais se houver
            questoes_raw = re.sub(r'\[PEI\]|\[GABARITO_PEI\]|\[IMAGENS_PEI\]', '', questoes_raw, flags=re.IGNORECASE)

        questoes_raw = re.sub(r'\(\d+,\d+\s*ponto[s]?\)', '', questoes_raw)
        padrao_split = r'(\d+[\s\.\ª\º]*Questão[\s\.\:]*)'
        partes = re.split(padrao_split, questoes_raw, flags=re.IGNORECASE)
        
        if len(partes) < 2:
            # Se não conseguiu fatiar por "Questão", imprime o bloco inteiro justificado
            for linha in questoes_raw.split('\n'):
                l_s = linha.strip()
                if not l_s: continue
                p = doc.add_paragraph()
                p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.add_run(l_s.replace('**', '')).font.size = Pt(12)
        else:
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
# 5. PLANO PEDAGÓGICO (VERSÃO ELITE V26 - JUSTIFICADO + LOGO + TRIMESTRE)
# ==============================================================================
def gerar_docx_plano_pedagogico_ELITE(titulo_arquivo, dados, info):
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
        # Margens de documento oficial
        section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
        section.left_margin, section.right_margin = Inches(0.5), Inches(0.5)

        # --- 1. CABEÇALHO REESTRUTURADO (SEM CAMPO DE DATA) ---
        table = doc.add_table(rows=3, cols=3)
        table.style = 'Table Grid'
        
        # Larguras fixas para evitar deformação
        widths = [Inches(1.1), Inches(3.6), Inches(2.0)]
        for i, w in enumerate(widths):
            table.columns[i].width = w

        # Busca exaustiva pela Logo (Tenta os dois nomes comuns no seu sistema)
        logo_path = None
        for nome in ["logo_escola.png", "logo.png"]:
            if os.path.exists(nome):
                logo_path = nome
                break

        if logo_path:
            cell_logo = table.cell(0, 0).merge(table.cell(2, 0)) # Logo ocupa as 3 linhas da esquerda
            cell_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            p_logo = cell_logo.paragraphs[0]
            p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_logo.add_run().add_picture(logo_path, width=Inches(0.85))
        
        # Escola e Título
        p_esc = table.cell(0, 1).paragraphs[0]
        p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
        
        p_tit = table.cell(0, 2).paragraphs[0]
        p_tit.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_tit.add_run("PLANO DE ENSINO SEMANAL").font.bold = True
        
        # Professor e Ano
        table.cell(1, 1).paragraphs[0].add_run(f"Professor: Ronaldo Gomes").font.size = Pt(10)
        table.cell(1, 2).paragraphs[0].add_run(f"Ano: {info.get('ano', '')}").font.size = Pt(10)
        
        # Semana e Trimestre (AQUI SUBSTITUÍMOS A DATA DEFINITIVAMENTE)
        table.cell(2, 1).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}").font.size = Pt(10)
        
        # Pega o trimestre do info ou tenta extrair da semana
        trim_val = info.get('trimestre', 'I Trimestre')
        table.cell(2, 2).paragraphs[0].add_run(f"Trimestre: {trim_val}").font.bold = True

        doc.add_paragraph() # Espaço

        # --- 2. CORPO DO PLANO (PRENSA ACADÊMICA) ---
        campos = [
            ("OBJETO DE CONHECIMENTO (EIXO):", "geral"), 
            ("CONTEÚDOS ESPECÍFICOS:", "especificos"), 
            ("OBJETIVOS DE APRENDIZAGEM:", "objetivos"), 
            ("RECURSOS DIDÁTICOS:", "recursos"), # NOVA LINHA
            ("PROCEDIMENTOS METODOLÓGICOS:", "metodologia"), 
            ("AVALIAÇÃO E ACOMPANHAMENTO:", "avaliacao"), 
            ("ESTRATÉGIAS DE ACESSIBILIDADE (DUA):", "pei")
        ]

        for label, chave in campos:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY # JUSTIFICAÇÃO NATIVA
            p.paragraph_format.space_after = Pt(8)
            
            # Rótulo em Negrito e Caixa Alta
            run_label = p.add_run(label)
            run_label.font.bold = True
            run_label.font.size = Pt(11)
            
            # Conteúdo limpo de Markdown
            texto_raw = str(dados.get(chave, ""))
            texto_limpo = texto_raw.replace(label, "").replace("**", "").replace("#", "").strip()
            if texto_limpo.startswith(":"): texto_limpo = texto_limpo[1:].strip()
            
            run_txt = p.add_run(f" {texto_limpo}")
            run_txt.font.size = Pt(11)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document()
        err_doc.add_paragraph(f"ERRO CRÍTICO: {str(e)}")
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
