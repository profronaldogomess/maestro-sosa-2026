import os
import io
import re
from docx import Document
from docx.shared import Inches, Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.enum.section import WD_SECTION, WD_ORIENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from datetime import datetime
import ai_engine as ai
import utils as util

# ==============================================================================
# 1. FUNÇÕES AUXILIARES TÉCNICAS E SANITIZAÇÃO
# ==============================================================================

def set_row_height(row, height_pt):
    """Define a altura mínima da linha da tabela para o cabeçalho não achatar"""
    tr = row._tr
    trPr = tr.get_or_add_trPr()
    trHeight = OxmlElement('w:trHeight')
    trHeight.set(qn('w:val'), str(int(height_pt * 20))) 
    trHeight.set(qn('w:hRule'), "atLeast")
    trPr.append(trHeight)

def set_cell_background(cell, fill_hex):
    """Aplica cor de fundo executiva em uma célula da tabela"""
    try:
        tcPr = cell._tc.get_or_add_tcPr()
        shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
        tcPr.append(shd)
    except: pass

def helper_sosa_float(v):
    """Converte qualquer valor para float de forma imune a erros"""
    if not v or str(v).strip() == "" or str(v).lower() == "nan": return 0.0
    try:
        return float(str(v).replace(" ", "").replace(",", "."))
    except: return 0.0

def converter_latex_para_texto_word(texto):
    """
    SOSA V2026 - VACINA INVIOLÁVEL DO CIFRÃO:
    1. Preserva 100% dos marcadores $$ para compatibilidade com o Google Docs Apps Script.
    2. Corrige R\$ para R$ (dinheiro) e \% para %.
    3. NUNCA remove cifrões $$.
    """
    if not texto or not isinstance(texto, str): return ""
    t = texto
    t = t.replace(r'R\$', 'R$').replace(r'R \$', 'R$')
    t = t.replace(r'\$', '$').replace(r'\%', '%')
    return t.strip()

def adicionar_texto_formatado(paragraph, texto):
    """Converte padrões **texto** em negrito real preservando expressões matemáticas $$"""
    if not texto: return
    texto_limpo = converter_latex_para_texto_word(texto)
    texto_limpo = texto_limpo.replace("➔", "").replace("->", "→").strip()
    
    partes = re.split(r'(\*\*.*?\*\*)', texto_limpo)
    for parte in partes:
        if parte.startswith('**') and parte.endswith('**'):
            run = paragraph.add_run(parte.replace('**', ''))
            run.bold = True
        else:
            paragraph.add_run(parte)

def adicionar_box_imagem_word(doc, legenda_prompt="ESPAÇO PARA ILUSTRAÇÃO / DESENHO"):
    """Cria uma moldura visual elegante para o prompt de ilustração no Word sem poluir o layout"""
    table = doc.add_table(rows=1, cols=1)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cell = table.cell(0, 0)
    cell.width = Inches(6.5)
    
    set_cell_background(cell, "F8FAFC")
    set_row_height(table.rows[0], 45)
    
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(8)
    
    run_icon = p.add_run("🖼️ [ILUSTRAÇÃO TÉCNICA A4]: ")
    run_icon.font.bold = True
    run_icon.font.size = Pt(9.0)
    run_icon.font.color.rgb = RGBColor(41, 98, 255)
    
    run_desc = p.add_run(f"{legenda_prompt.strip()}")
    run_desc.font.size = Pt(8.5)
    run_desc.font.italic = True
    run_desc.font.color.rgb = RGBColor(71, 85, 105)
    
    doc.add_paragraph()

def configurar_cabecalho_mestre(doc, info, tipo_label, mostrar_nota=False):
    """Gera o cabeçalho executivo oficial da Escola e Prefeitura de Itabuna"""
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    
    widths = [Inches(0.8), Inches(3.2), Inches(1.0), Inches(1.1), Inches(1.8)]
    for i, w in enumerate(widths): 
        table.columns[i].width = w

    for row in table.rows:
        set_row_height(row, 22)

    # LINHA 0: LOGO, ESCOLA E TRIMESTRE
    c_logo = table.cell(0, 0).merge(table.cell(2, 0))
    c_escola = table.cell(0, 1).merge(table.cell(0, 3))
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.bold = True
    run_esc.font.size = Pt(10)
    
    c_trim = table.cell(0, 4)
    c_trim.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_background(c_trim, "F1F5F9")
    p_tr = c_trim.paragraphs[0]
    p_tr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tr = p_tr.add_run(info.get('trimestre', 'I Trimestre'))
    run_tr.font.bold = True
    run_tr.font.size = Pt(9.5)

    # LINHA 1: ALUNO
    if mostrar_nota:
        c_aluno = table.cell(1, 1).merge(table.cell(1, 3))
        c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_aluno.paragraphs[0].add_run("ESTUDANTE: __________________________________________________").font.size = Pt(9.5)
        
        c_nota = table.cell(1, 4)
        c_nota.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        set_cell_background(c_nota, "F8FAFC")
        p_n = c_nota.paragraphs[0]
        p_n.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_n.add_run("NOTA: ________").font.bold = True
    else:
        c_aluno = table.cell(1, 1).merge(table.cell(1, 4))
        c_aluno.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        c_aluno.paragraphs[0].add_run("ESTUDANTE: ________________________________________________________________").font.size = Pt(9.5)

    # LINHA 2: PROFESSOR, TURMA, DATA E TIPO
    table.cell(2, 1).paragraphs[0].add_run("PROF: Ronaldo Gomes").font.size = Pt(9)
    table.cell(2, 2).paragraphs[0].add_run(f"TURMA: {info.get('ano', '6º')}").font.size = Pt(9)
    table.cell(2, 3).paragraphs[0].add_run("DATA:    /    /").font.size = Pt(9)
    
    c_tipo = table.cell(2, 4)
    c_tipo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    set_cell_background(c_tipo, "2962FF")
    p_tipo = c_tipo.paragraphs[0]
    p_tipo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_tipo = p_tipo.add_run(tipo_label)
    run_tipo.font.bold = True
    run_tipo.font.size = Pt(9)
    run_tipo.font.color.rgb = RGBColor(255, 255, 255)

    logo_path = "logo_escola.png" if os.path.exists("logo_escola.png") else "logo.png"
    if os.path.exists(logo_path):
        c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
        p = c_logo.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        try: p.add_run().add_picture(logo_path, width=Inches(0.65))
        except: pass
    return table

# ==============================================================================
# 7. EXPORTADOR PEI NÍVEL 3 (SENSORIAL / MOTOR / BENTO CARDS NO PAPEL)
# ==============================================================================
def gerar_docx_pei_qualitativa(titulo_doc, conteudo, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin, section.bottom_margin = Inches(0.4), Inches(0.4)
        section.left_margin, section.right_margin = Inches(0.4), Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10.5)

        # Cabeçalho Oficial da Escola e Prefeitura de Itabuna
        configurar_cabecalho_mestre(doc, info, "AVALIAÇÃO ADAPTADA (NÍVEL 3)", mostrar_nota=False)
        doc.add_paragraph()

        # Painel de Instruções de Mediação
        panel_info = doc.add_table(rows=1, cols=1)
        panel_info.style = 'Table Grid'
        cell_info = panel_info.cell(0, 0)
        set_cell_background(cell_info, "F1F5F9")
        p_info = cell_info.paragraphs[0]
        p_info.paragraph_format.space_after = Pt(2)
        r_info_title = p_info.add_run("📋 ORIENTAÇÕES DE MEDIAÇÃO PEDAGÓGICA (PEI NÍVEL 3 - ATIVIDADES IMPRESSAS NO PAPEL):\n")
        r_info_title.bold = True
        r_info_title.font.size = Pt(9.5)
        r_info_title.font.color.rgb = RGBColor(0, 51, 102)
        
        orientacoes = [
            "Atividades adaptadas para execução direta na folha (Pintar, Ligar Colunas, Cobrir Pontilhado, Circular).",
            "Não exige suporte material concreto na sala. Utilize lápis de cor, giz de cera e canetinha.",
            "Assinale o nível de autonomia do estudante nas caixas de registro de cada BOX e na Rubrica Final."
        ]
        for o_txt in orientacoes:
            p_o = cell_info.add_paragraph()
            p_o.paragraph_format.space_after = Pt(1)
            p_o.add_run(f"• {o_txt}").font.size = Pt(8.5)

        doc.add_paragraph()

        # Processamento das Linhas e renderização dos CARDS DE BOX (BENTO GRID)
        linhas = str(conteudo).split('\n')
        
        i = 0
        while i < len(linhas):
            linha = linhas[i].strip()
            if not linha:
                i += 1
                continue

            if any(x in linha.upper() for x in ["ATIVIDADE", "TEMA:", "JORNADA", "AVALIAÇÃO ADAPTADA"]) and "BOX" not in linha.upper():
                if "RUBRICA" in linha.upper():
                    break
                p_act = doc.add_paragraph()
                p_act.paragraph_format.space_before = Pt(10)
                p_act.paragraph_format.space_after = Pt(4)
                r_act = p_act.add_run(linha.replace('**', ''))
                r_act.bold = True
                r_act.font.size = Pt(11)
                r_act.font.color.rgb = RGBColor(0, 51, 102)
                i += 1
                continue

            # Se for um Prompt de Imagem isolado
            if "[" in linha and "PROMPT IMAGEM" in linha.upper():
                desc_p = re.sub(r'\[\s*PROMPT IMAGEM:\s*|\s*\]', '', linha, flags=re.IGNORECASE)
                adicionar_box_imagem_word(doc, desc_p)
                i += 1
                continue

            # Se for um BOX (ex: "1. [BOX 1] ...", "[BOX 1] ...")
            if "BOX" in linha.upper():
                card_table = doc.add_table(rows=2, cols=1)
                card_table.style = 'Table Grid'
                card_table.alignment = WD_ALIGN_PARAGRAPH.CENTER
                card_table.columns[0].width = Inches(7.5)

                cell_head = card_table.cell(0, 0)
                set_cell_background(cell_head, "2962FF")
                set_row_height(card_table.rows[0], 20)
                p_head = cell_head.paragraphs[0]
                p_head.alignment = WD_ALIGN_PARAGRAPH.LEFT
                
                m_box_title = re.search(r"(\[?BOX\s*\d+\]?.*?)(?:[:\-]\s*|\s+)(.*)", linha, re.IGNORECASE)
                if m_box_title:
                    rotulo_box = m_box_title.group(1).upper().replace("[", "").replace("]", "").strip()
                    desc_box = m_box_title.group(2).strip()
                else:
                    rotulo_box = "BOX DE ATIVIDADE IMPRESSA"
                    desc_box = linha.strip()

                r_head = p_head.add_run(f"📦 {rotulo_box}")
                r_head.bold = True
                r_head.font.size = Pt(10)
                r_head.font.color.rgb = RGBColor(255, 255, 255)

                cell_body = card_table.cell(1, 0)
                set_cell_background(cell_body, "F8FAFC")
                p_body = cell_body.paragraphs[0]
                p_body.paragraph_format.space_after = Pt(4)
                
                adicionar_texto_formatado(p_body, desc_box)

                p_check = cell_body.add_paragraph()
                p_check.paragraph_format.space_before = Pt(4)
                p_check.paragraph_format.space_after = Pt(2)
                
                r_check_label = p_check.add_run("Registro do Mediador no Papel: ")
                r_check_label.bold = True
                r_check_label.font.size = Pt(8.5)
                r_check_label.font.color.rgb = RGBColor(100, 116, 139)

                r_opts = p_check.add_run("[   ] Autônomo   |   [   ] Com Apoio   |   [   ] Não Realizou")
                r_opts.font.size = Pt(8.5)
                r_opts.font.bold = True
                r_opts.font.color.rgb = RGBColor(30, 41, 59)

                p_space = doc.add_paragraph()
                p_space.paragraph_format.space_after = Pt(2)
                i += 1
                continue

            p_norm = doc.add_paragraph()
            p_norm.paragraph_format.space_after = Pt(4)
            adicionar_texto_formatado(p_norm, linha)
            i += 1

        # Tabela Oficial de Rubrica de Observação Pedagógica
        doc.add_paragraph()
        p_rub_title = doc.add_paragraph()
        p_rub_title.paragraph_format.space_before = Pt(10)
        p_rub_title.paragraph_format.space_after = Pt(4)
        r_rub = p_rub_title.add_run("📋 RUBRICA OFICIAL DE OBSERVAÇÃO PEDAGÓGICA (PARECER QUALITATIVO)")
        r_rub.bold = True
        r_rub.font.size = Pt(11)
        r_rub.font.color.rgb = RGBColor(0, 51, 102)

        rubrica_table = doc.add_table(rows=5, cols=5)
        rubrica_table.style = 'Table Grid'
        
        col_widths = [Inches(2.5), Inches(1.1), Inches(1.1), Inches(1.2), Inches(1.6)]
        for row in rubrica_table.rows:
            set_row_height(row, 22)
            for idx_c, w in enumerate(col_widths):
                row.cells[idx_c].width = w

        headers_rub = ["DIMENSÃO COGNITIVA / MOTORA", "AUTÔNOMO ✅", "COM APOIO 🤝", "NÃO REALIZOU ❌", "OBSERVAÇÕES"]
        for idx_c, h_text in enumerate(headers_rub):
            c_h = rubrica_table.cell(0, idx_c)
            set_cell_background(c_h, "003366")
            p_h = c_h.paragraphs[0]
            p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_h = p_h.add_run(h_text)
            r_h.bold = True
            r_h.font.size = Pt(8.5)
            r_h.font.color.rgb = RGBColor(255, 255, 255)

        dimensoes_pei = [
            ("Autonomia Executiva", "Iniciativa e condução motora nas tarefas de papel"),
            ("Compreensão de Comandos", "Atendimento às instruções de pintar, ligar e cobrir"),
            ("Percepção Visual e Espacial", "Identificação de formas, números e sequências no papel"),
            ("Raciocínio Lógico-Proporcional", "Associação visual de quantidades e símbolos")
        ]

        for idx_d, (dim_nome, dim_desc) in enumerate(dimensoes_pei, start=1):
            row_cells = rubrica_table.rows[idx_d].cells
            
            p_dim = row_cells[0].paragraphs[0]
            r_dn = p_dim.add_run(f"{dim_nome}\n")
            r_dn.bold = True
            r_dn.font.size = Pt(9)
            r_dd = p_dim.add_run(dim_desc)
            r_dd.font.size = Pt(7.5)
            r_dd.font.italic = True
            r_dd.font.color.rgb = RGBColor(100, 116, 139)

            for c_idx in range(1, 4):
                p_chk = row_cells[c_idx].paragraphs[0]
                p_chk.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p_chk.add_run("○").font.size = Pt(14)

            row_cells[4].paragraphs[0].add_run("____________________").font.size = Pt(8)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO EXPORTER PEI N3: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 8. ETIQUETAS DE NOTAS (FECHAMENTO TRIMESTRAL)
# ==============================================================================
def gerar_docx_etiquetas_notas(nome_arquivo, dados_alunos, info):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.4)
        section.left_margin = section.right_margin = Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(9.5)

        table = doc.add_table(rows=0, cols=2)
        table.style = 'Table Grid'
        table.columns[0].width = Inches(3.7)
        table.columns[1].width = Inches(3.7)

        for i in range(0, len(dados_alunos), 2):
            row = table.add_row() 
            set_row_height(row, 130)

            for j in range(2):
                if i + j < len(dados_alunos):
                    aluno = dados_alunos[i+j]
                    c = row.cells[j]
                    c.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
                    
                    p = c.paragraphs[0]
                    p.paragraph_format.space_after = Pt(2)
                    
                    p.add_run("ESCOLA MUNICIPAL FLÁVIO JOSÉ SIMÕES COSTA\n").bold = True
                    p.add_run(f"Estudante: {aluno['nome']}\n").bold = True
                    p.add_run(f"Turma: {info['turma']} | {info['trimestre']}\n\n").font.size = Pt(8.5)
                    
                    p.add_run(f"🏛️ C1 (Vistos/Caderno): {aluno['vistos']}\n")
                    p.add_run(f"📝 C2 (Testes/Trabalhos): {aluno['teste']}\n")
                    p.add_run(f"📄 C3 (Prova Oficial): {aluno['prova']}\n")
                    
                    run_obs = p.add_run(f"* Bônus conquistados (+{aluno['bonus']} pts) embutidos acima.\n\n")
                    run_obs.font.size = Pt(8)
                    run_obs.font.italic = True
                    run_obs.font.color.rgb = RGBColor(100, 116, 139)
                    
                    run_media = p.add_run(f"📊 MÉDIA FINAL: {aluno['media']}\n")
                    run_media.bold = True
                    run_media.font.size = Pt(11)
                    
                    run_status = p.add_run(f"SITUAÇÃO: {aluno['status']}")
                    run_status.bold = True
                    if "APROVADO" in aluno['status']: run_status.font.color.rgb = RGBColor(0, 128, 0)
                    else: run_status.font.color.rgb = RGBColor(204, 0, 0)

        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NAS ETIQUETAS: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 9. PLANEJAMENTO TRIMESTRAL (PAISAGEM)
# ==============================================================================
def gerar_docx_planejamento_trimestral(nome_arquivo, info, dados_tabela):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[-1]
        new_width, new_height = section.page_height, section.page_width
        section.orientation = WD_ORIENT.LANDSCAPE
        section.page_width = new_width
        section.page_height = new_height
        section.left_margin = section.right_margin = Inches(0.4)
        section.top_margin = section.bottom_margin = Inches(0.4)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(9)

        p_cab = doc.add_paragraph()
        p_cab.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_esc = p_cab.add_run("ESCOLA MUNICIPAL FLÁVIO JOSÉ SIMÕES COSTA\n")
        run_esc.bold = True
        run_esc.font.size = Pt(11)
        
        run_tit = p_cab.add_run(f"PLANEJAMENTO TRIMESTRAL DE MATEMÁTICA - {info['trimestre'].upper()} / 2026\n")
        run_tit.bold = True
        run_tit.font.size = Pt(10)
        run_sub = p_cab.add_run(f"SÉRIE: {info['ano']}   |   PROFESSOR: RONALDO GOMES")
        run_sub.font.size = Pt(9)
        
        doc.add_paragraph()

        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        
        widths = [Inches(1.8), Inches(3.8), Inches(2.2), Inches(3.0)]
        for i, w in enumerate(widths): table.columns[i].width = w

        headers = ['EIXO TEMÁTICO', 'CONTEÚDOS PROGRAMÁTICOS', 'HABILIDADES (BNCC)', 'METODOLOGIA APLICADA']
        for i, h in enumerate(headers):
            cell = table.cell(0, i)
            set_cell_background(cell, "003366")
            cell.text = h
            p = cell.paragraphs[0]
            p.runs[0].font.bold = True
            p.runs[0].font.color.rgb = RGBColor(255, 255, 255)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            
        for row_data in dados_tabela:
            row_cells = table.add_row().cells
            row_cells[0].text = row_data['eixo']
            row_cells[1].text = row_data['conteudos']
            row_cells[2].text = row_data['habilidades']
            row_cells[3].text = row_data['metodologia']
            
            for cell in row_cells:
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                    
        doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
    except Exception as e:
        file_stream = io.BytesIO()
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO PLANO TRIMESTRAL: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream

# ==============================================================================
# 10. PEI OFICIAL (PREFEITURA)
# ==============================================================================
def gerar_docx_pei_oficial(nome_arquivo, dados_aluno, habilidades, curriculo_df):
    file_stream = io.BytesIO()
    try:
        doc = Document()
        section = doc.sections[0]
        section.top_margin = section.bottom_margin = Inches(0.5)
        section.left_margin = section.right_margin = Inches(0.5)

        style = doc.styles['Normal']
        style.font.name = 'Arial'
        style.font.size = Pt(10)

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
        doc.add_paragraph("DADOS DO ESTUDANTE").runs[0].bold = True
        
        p_d1 = doc.add_paragraph()
        p_d1.add_run("UNIDADE ESCOLAR: ").bold = True
        p_d1.add_run("Escola Municipal Flávio José Simões Costa\t\t")
        p_d1.add_run("ANO LETIVO: ").bold = True
        p_d1.add_run("2026")
        
        p_d2 = doc.add_paragraph()
        p_d2.add_run("NOME: ").bold = True
        p_d2.add_run(f"{dados_aluno.get('nome', '')}\t\t")
        p_d2.add_run("TURMA: ").bold = True
        p_d2.add_run(f"{dados_aluno.get('turma', '')}")
        
        p_d4 = doc.add_paragraph()
        p_d4.add_run("DEFICIÊNCIA(S)/CID: ").bold = True
        p_d4.add_run(f"{dados_aluno.get('cid', '')}")
        
        doc.add_paragraph()
        doc.add_paragraph("1. PLANO DE ACESSIBILIDADE CURRICULAR").runs[0].bold = True
        
        for hab_name, hab_text in habilidades.items():
            p_h = doc.add_paragraph()
            p_h.add_run(f"• {hab_name}: ").bold = True
            p_h.add_run(str(hab_text))
        
        doc.add_paragraph()
        doc.add_paragraph("2. PLANEJAMENTO POR COMPONENTE CURRICULAR").runs[0].bold = True
        
        table = doc.add_table(rows=1, cols=4)
        table.style = 'Table Grid'
        hdr_cells = table.rows[0].cells
        hdr_cells[0].text = 'DISCIPLINA'
        hdr_cells[1].text = 'OBJETIVOS APRENDIZAGEM'
        hdr_cells[2].text = 'ESTRATÉGIAS METODOLÓGICAS'
        hdr_cells[3].text = 'RECURSOS MATERIAIS'
        
        for cell in hdr_cells:
            set_cell_background(cell, "F1F5F9")
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
        err_doc = Document(); err_doc.add_paragraph(f"ERRO NO PEI OFICIAL: {str(e)}"); err_doc.save(file_stream)
        file_stream.seek(0)
        return file_stream
