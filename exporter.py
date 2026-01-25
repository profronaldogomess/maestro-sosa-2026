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

def gerar_docx_plano_oficial(titulo_plano, dados_plano, info_extra={}):
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Inches(0.4)
    
    # Cabeçalho em Tabela (Estilo PDF enviado)
    table = doc.add_table(rows=3, cols=4)
    table.style = 'Table Grid'
    
    # Linha 1: Logo | Nome Escola | Trimestre/Identificação
    c_logo = table.cell(0, 0).merge(table.cell(1, 0))
    c_escola = table.cell(0, 1).merge(table.cell(0, 2))
    c_id = table.cell(0, 3).merge(table.cell(1, 3))
    
    # Inserir Logo
    p_logo = c_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("logo_escola.png"):
        p_logo.add_run().add_picture("logo_escola.png", width=Inches(0.8))
        
    # Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold = True
    run_esc.font.size = Pt(12)
    
    # Identificação do Plano
    p_id = c_id.paragraphs[0]
    p_id.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_id.add_run(f"{info_extra.get('trimestre', 'I')} TRIMESTRE\n").font.bold = True
    p_id.add_run(titulo_plano).font.size = Pt(9)

    # Linha 2: Professor e Turma
    table.cell(1, 1).paragraphs[0].add_run(f"PROF: Ronaldo Gomes").font.size = Pt(10)
    table.cell(1, 2).paragraphs[0].add_run(f"TURMA: {info_extra.get('turma', '')}").font.size = Pt(10)

    # Linha 3: Data e Espaço em branco
    table.cell(2, 1).merge(table.cell(2, 3))
    table.cell(2, 1).paragraphs[0].add_run("DATA: ____/____/2026").font.size = Pt(10)

    doc.add_paragraph() # Espaço

    # CORPO DO PLANO (Tags em Negrito + Texto Normal)
    ordem_campos = [
        ("CONTEÚDO GERAL EIXO:", dados_plano.get('geral', '')),
        ("CONTEÚDOS ESPECÍFICOS:", dados_plano.get('especificos', '')),
        ("OBJETIVOS DE ENSINO:", dados_plano.get('objetivos', '')),
        ("METODOLOGIA:", dados_plano.get('metodologia', '')),
        ("AVALIAÇÃO:", dados_plano.get('avaliacao', '')),
        ("OBSERVAÇÃO:", dados_plano.get('observacao', '')),
        ("ADAPTAÇÃO PEI:", dados_plano.get('pei', ''))
    ]

    for label, texto in ordem_campos:
        p = doc.add_paragraph()
        run_label = p.add_run(label)
        run_label.font.bold = True
        run_label.font.size = Pt(11)
        
        p.add_run(f" {texto}").font.size = Pt(11)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.space_after = Pt(12)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def gerar_docx_plano_pedagogico_v18(titulo_arquivo, dados, info):
    doc = Document()
    section = doc.sections[0]
    section.top_margin, section.bottom_margin = Inches(0.5), Inches(0.5)
    section.left_margin, section.right_margin = Inches(0.6), Inches(0.6)

    # CABEÇALHO MODERNO 3 LINHAS
    table = doc.add_table(rows=3, cols=3)
    table.style = 'Table Grid'
    
    # Linha 1
    table.cell(0, 0).paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if os.path.exists("logo_escola.png"):
        table.cell(0, 0).paragraphs[0].add_run().add_picture("logo_escola.png", width=Inches(0.7))
    
    p_esc = table.cell(0, 1).paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA").font.bold = True
    
    p_tipo = table.cell(0, 2).paragraphs[0]
    p_tipo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_tipo.add_run("PLANO DE ENSINO SEMANAL").font.bold = True

    # Linha 2
    table.cell(1, 0).merge(table.cell(1, 1))
    table.cell(1, 0).paragraphs[0].add_run(f"Professor: Ronaldo Gomes")
    table.cell(1, 2).paragraphs[0].add_run(f"Ano: {info.get('ano', '')}")

    # Linha 3
    table.cell(2, 0).merge(table.cell(2, 1))
    table.cell(2, 0).paragraphs[0].add_run(f"Semana: {info.get('semana', '')}")
    table.cell(2, 2).paragraphs[0].add_run("Data: [    /    / 2026 ]")

    doc.add_paragraph()

    # CORPO COM RÓTULOS EM NEGRITO
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
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.add_run(label).font.bold = True
        
        # Limpeza de segurança para evitar gagueira
        texto = str(dados.get(chave, "")).replace(label, "").strip()
        if texto.startswith(":"): texto = texto[1:].strip()
        
        p.add_run(f" {texto}")
        p.paragraph_format.space_after = Pt(10)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream

def gerar_docx_laboratorio_v23(titulo, prof_txt, aluno_txt, pei_txt, gab_txt, info):
    doc = Document()
    
    # Função interna para criar seções
    def adicionar_secao(nome_secao, conteudo):
        if not conteudo or len(conteudo.strip()) < 5: return
        
        # Cabeçalho da Seção
        p = doc.add_paragraph()
        run = p.add_run(f"--- {nome_secao.upper()} ---")
        run.font.bold = True
        run.font.size = Pt(14)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Conteúdo
        doc.add_paragraph(conteudo)
        
        # Quebra de Página para a próxima seção não misturar
        doc.add_page_break()

    # Montagem do Documento
    adicionar_secao("Guia do Professor", prof_txt)
    adicionar_secao("Atividade do Aluno", aluno_txt)
    adicionar_secao("Atividade Adaptada (PEI)", pei_txt)
    adicionar_secao("Gabarito", gab_txt)

    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
