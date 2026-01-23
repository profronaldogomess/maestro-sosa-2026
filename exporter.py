import os
import io
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def gerar_docx_profissional(titulo, conteudo_raw, info_extra={}, logo_escola="logo_escola.png"):
    """
    Gera um documento Word com o cabeçalho padrão CPM (Escola Flávio Simões Costa).
    """
    doc = Document()
    
    # --- CONFIGURAÇÃO DE MARGENS (PADRÃO OFICIAL) ---
    section = doc.sections[0]
    section.top_margin = Inches(0.4)
    section.bottom_margin = Inches(0.4)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)

    # --- DETECÇÃO DO CAMINHO DA LOGO ---
    # Busca a imagem na mesma pasta onde o script está rodando
    diretorio_atual = os.path.dirname(os.path.abspath(__file__))
    caminho_logo = os.path.join(diretorio_atual, logo_escola)

    # --- CRIAÇÃO DA TABELA DE CABEÇALHO (Grade 3x5) ---
    table = doc.add_table(rows=3, cols=5)
    table.style = 'Table Grid'
    table.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Ajuste de Larguras das Colunas
    # Col 0: Logo | Col 1-3: Dados | Col 4: Trimestre/Nota
    table.columns[0].width = Inches(1.1)
    table.columns[1].width = Inches(1.8)
    table.columns[2].width = Inches(1.2)
    table.columns[3].width = Inches(1.6)
    table.columns[4].width = Inches(1.4)

    # --- MESCLAGENS (PARA BATER COM A IMAGEM DO CPM) ---
    # 1. Espaço da Logo (Coluna 0 mescla as 3 linhas)
    c_logo = table.cell(0, 0).merge(table.cell(2, 0))
    
    # 2. Nome da Escola (Linha 0, Colunas 1 a 3)
    c_escola = table.cell(0, 1).merge(table.cell(0, 3))
    
    # 3. Campo do Aluno (Linha 1, Colunas 1 a 3)
    c_aluno = table.cell(1, 1).merge(table.cell(1, 3))
    
    # 4. Trimestre e Tipo (Coluna 4, Linhas 0 e 1)
    c_trim = table.cell(0, 4).merge(table.cell(1, 4))

    # --- PREENCHIMENTO DOS DADOS ---
    
    # 1. Inserção da Logo
    c_logo.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_logo = c_logo.paragraphs[0]
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    if os.path.exists(caminho_logo):
        run_logo = p_logo.add_run()
        run_logo.add_picture(caminho_logo, width=Inches(0.9))
    else:
        # Caso a imagem não exista, avisa no documento para diagnóstico
        run_err = p_logo.add_run(f"ERRO:\n{logo_escola}\nnão encontrada")
        run_err.font.size = Pt(7)
        run_err.font.color.rgb = RGBColor(255, 0, 0)

    # 2. Nome da Escola
    p_esc = c_escola.paragraphs[0]
    p_esc.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_esc = p_esc.add_run("ESCOLA MUNICIPAL FLAVIO JOSE SIMOES COSTA")
    run_esc.font.bold = True
    run_esc.font.size = Pt(12)

    # 3. Campo Aluno
    p_alu = c_aluno.paragraphs[0]
    p_alu.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    run_alu = p_alu.add_run(f"ALUNO(A): ________________________________________________")
    run_alu.font.size = Pt(10)
    
    # 4. Linha de Baixo (Professor / Turma / Data)
    # Professor
    p_prof = table.cell(2, 1).paragraphs[0]
    run_prof = p_prof.add_run(f"PROF. Ronaldo Gomes")
    run_prof.font.italic = True
    run_prof.font.size = Pt(10)
    
    # Turma
    p_turma = table.cell(2, 2).paragraphs[0]
    run_turma = p_turma.add_run(f"TURMA: {info_extra.get('turma', '______')}")
    run_turma.font.size = Pt(10)
    
    # Data
    p_data = table.cell(2, 3).paragraphs[0]
    run_data = p_data.add_run(f"DATA: ____/____/________")
    run_data.font.size = Pt(10)

    # 5. Lado Direito (Trimestre e Tipo de Atividade)
    c_trim.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
    p_trim = c_trim.paragraphs[0]
    p_trim.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    run_t1 = p_trim.add_run(f"{info_extra.get('trimestre', 'III')} TRIMESTRE\n")
    run_t1.font.bold = True
    run_t1.font.size = Pt(11)
    
    run_t2 = p_trim.add_run(f"{titulo}")
    run_t2.font.size = Pt(9)

    # 6. Campo Nota
    p_nota = table.cell(2, 4).paragraphs[0]
    p_nota.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run_nota = p_nota.add_run(" NOTA: ________")
    run_nota.font.size = Pt(9)

    # --- PROCESSAMENTO DO CONTEÚDO (CORPO DO TEXTO) ---
    doc.add_paragraph() # Espaço entre cabeçalho e texto
    
    # Limpeza de Markers para o documento final
    texto_limpo = conteudo_raw.replace("MARKER_LOUSA", "").replace("MARKER_FOLHA", "").replace("MARKER_GABARITO", "\n--- GABARITO ---\n").replace("MARKER_IMAGENS", "")
    
    for linha in texto_limpo.split('\n'):
        if linha.strip():
            p = doc.add_paragraph(linha.strip())
            # Se a linha contiver "QUESTÃO", aplica negrito e espaçamento
            if "QUESTÃO" in linha.upper() or "ATIVIDADE" in linha.upper():
                p.style.font.bold = True
                p.paragraph_format.space_before = Pt(12)
            else:
                p.style.font.size = Pt(11)

    # --- SALVAMENTO EM MEMÓRIA ---
    file_stream = io.BytesIO()
    doc.save(file_stream)
    file_stream.seek(0)
    return file_stream
