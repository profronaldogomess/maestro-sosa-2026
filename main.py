# ==============================================================================
# MÓDULO: LABORATÓRIO DE PRODUÇÃO (CRIADOR V32.7) - TRIPLE-SYNC & CONTROLE TOTAL
# ==============================================================================
if menu == "🧪 Criador de Aulas":
    st.title("🧪 Laboratório de Produção Semiótica (V32)")
    st.markdown("---")
    
    def reset_laboratorio():
        keys_to_del = ["lab_temp", "lab_pei", "lab_gab_pei", "refino_lab_ativo", "refino_lab_tipo", "comp_temp", "comp_pei", "sosa_id_atual", "lab_meta"]
        for k in keys_to_del:
            if k in st.session_state: del st.session_state[k]
        st.session_state.v_lab = int(time.time())
        st.rerun()

    if "v_lab" not in st.session_state: st.session_state.v_lab = 1
    v = st.session_state.v_lab

    tab_producao, tab_diagnostico, tab_trabalhos, tab_complementar, tab_acervo = st.tabs([
        "🚀 Produção (Aula 1/2)", 
        "🔍 Diagnóstico Reverso", 
        "📋 Engenharia de Trabalhos",
        "📚 Atividades Complementares",
        "📂 Acervo de Materiais"
    ])

    # --- ÁREA DE EXIBIÇÃO E REFINO (APARECE QUANDO O MATERIAL É GERADO) ---
    if "lab_temp" in st.session_state:
        txt_base = st.session_state.lab_temp
        s_id = st.session_state.get("sosa_id_atual", "SEM-ID")
        meta = st.session_state.get("lab_meta", {"ano": "6", "trimestre": "I Trimestre", "tipo": "AULA"})
        
        # Extração prévia para segurança de variáveis
        c_prof_base = ai.extrair_tag(txt_base, "PROFESSOR")
        c_alu_base = ai.extrair_tag(txt_base, "ALUNO")
        c_gab_base = ai.extrair_tag(txt_base, "GABARITO") or ai.extrair_tag(txt_base, "RUBRICA")

        st.success(f"💎 Material Gerado: **{s_id}**")
        
        # Controle de Painel: Botão para voltar ao formulário
        if st.button("🆕 GERAR NOVO MATERIAL (LIMPAR ATUAL)", use_container_width=True, key=f"btn_new_{v}"):
            reset_laboratorio()

        t_prof, t_alu, t_gab, t_pei, t_sync = st.tabs(["👨‍🏫 Professor", "📝 Aluno", "✅ Gabarito/Rubrica", "♿ PEI", "☁️ SINCRONIA"])
        
        with t_prof: 
            ed_prof = st.text_area("Lousa (2 Colunas):", c_prof_base, height=400, key=f"ed_prof_{v}")
        with t_alu: 
            ed_alu = st.text_area("Folha do Aluno:", c_alu_base, height=400, key=f"ed_alu_{v}")
        with t_gab: 
            ed_res = st.text_area("Respostas/Critérios:", c_gab_base, height=300, key=f"ed_res_{v}")
        
        with t_pei:
            st.subheader("♿ Adaptação Curricular PEI (Elite)")
            if st.button("✨ GERAR/ATUALIZAR MATERIAL PEI", use_container_width=True, key=f"btn_gen_pei_{v}"):
                with st.spinner("Maestro Sosa realizando reengenharia de acessibilidade..."):
                    res_ia = ai.gerar_ia("ARQUITETO_PEI_V24", f"ADAPTE PARA PEI: {c_alu_base}")
                    st.session_state.lab_pei = ai.extrair_tag(res_ia, "PEI")
                    st.session_state.lab_gab_pei = ai.extrair_tag(res_ia, "GABARITO_PEI")
                    st.rerun()
            
            if "lab_pei" in st.session_state:
                c_p1, c_p2 = st.columns(2)
                with c_p1: st.text_area("📄 Material PEI:", st.session_state.lab_pei, height=400, key=f"ed_pei_mat_{v}")
                with c_p2: st.text_area("✅ Gabarito PEI:", st.session_state.get("lab_gab_pei", ""), height=400, key=f"ed_pei_gab_{v}")

        with t_sync:
            st.warning("⚠️ O Triple-Sync salvará Aluno, Professor e PEI, removendo versões antigas do Drive.")
            if st.button("💾 EXECUTAR TRIPLE-SYNC", use_container_width=True, type="primary", key=f"btn_triple_{v}"):
                with st.status("Iniciando Protocolo de Sincronia...") as status:
                    nome_base = f"{s_id} - {meta['tipo']}"
                    ano_str = f"{meta['ano']}º"
                    
                    # 1. Limpeza Upsert
                    db.excluir_registro_com_drive("DB_AULAS_PRONTAS", s_id)
                    
                    # 2. Upload Aluno
                    doc_alu = exporter.gerar_docx_aluno_v24(nome_base, ed_alu, {"ano": ano_str, "trimestre": meta['trimestre']})
                    link_alu = db.subir_e_converter_para_google_docs(doc_alu, f"{nome_base}_ALUNO", modo="AULA")
                    
                    # 3. Upload Professor
                    doc_prof = exporter.gerar_docx_professor_v25(nome_base, ed_prof, {"ano": ano_str, "semana": "SOSA-ID", "trimestre": meta['trimestre']})
                    link_prof = db.subir_e_converter_para_google_docs(doc_prof, f"{nome_base}_PROF", modo="AULA")
                    
                    # 4. Upload PEI
                    link_pei = "N/A"
                    if "lab_pei" in st.session_state:
                        doc_pei = exporter.gerar_docx_pei_v25(f"{nome_base}_PEI", st.session_state.lab_pei, {"ano": ano_str, "trimestre": meta['trimestre']})
                        link_pei = db.subir_e_converter_para_google_docs(doc_pei, f"{nome_base}_PEI", modo="AULA")
                    
                    if "https" in str(link_alu) and "https" in str(link_prof):
                        conteudo_banco = (
                            f"[SOSA_ID: {s_id}]\n[PROFESSOR]\n{ed_prof}\n\n[ALUNO]\n{ed_alu}\n\n"
                            f"[GABARITO]\n{ed_res}\n\n[PEI]\n{st.session_state.get('lab_pei', 'N/A')}\n\n"
                            f"[GABARITO_PEI]\n{st.session_state.get('lab_gab_pei', 'N/A')}\n\n"
                            f"--- LINKS ---\nAluno({link_alu}) Prof({link_prof}) PEI({link_pei})"
                        )
                        db.salvar_no_banco("DB_AULAS_PRONTAS", [datetime.now().strftime("%d/%m/%Y"), "PRODUÇÃO", nome_base, conteudo_banco, ano_str, link_alu])
                        status.update(label="✅ Triple-Sync Concluído!", state="complete")
                        st.balloons(); time.sleep(1); reset_laboratorio()

    # --- ABA 1: PRODUÇÃO (FORMULÁRIO) ---
    with tab_producao:
        if "lab_temp" not in st.session_state:
            with st.container(border=True):
                st.markdown("### ⚙️ 1. Parâmetros de Regência")
                c1, c2, c3 = st.columns([1, 2, 1.5])
                ano_lab = c1.selectbox("Série/Ano:", [6, 7, 8, 9], key=f"prod_ano_{v}")
                planos_ano = df_planos[df_planos['ANO'].astype(str).str.contains(str(ano_lab))]
                
                if planos_ano.empty: st.error("❌ Nenhum plano encontrado.")
                else:
                    sem_lab = c2.selectbox("Semana Base (PIP):", planos_ano['SEMANA'].tolist(), key=f"prod_sem_{v}")
                    aula_alvo = c3.radio("🎯 Alvo:", ["Aula 1", "Aula 2", "Ambas"], horizontal=True, key=f"prod_alvo_{v}")
                    plano_ref = planos_ano[planos_ano['SEMANA'] == sem_lab].iloc[0]['PLANO_TEXTO']
                    
                    col_p1, col_p2 = st.columns(2)
                    qtd_q = col_p1.slider("Nº de Questões:", 1, 15, 5, key=f"prod_q_{v}")
                    instr_extra = col_p2.text_input("Instruções Adicionais:", key=f"prod_extra_{v}")
                    
                    if st.button("💎 COMPILAR MATERIAL", use_container_width=True, type="primary", key=f"btn_gen_prod_{v}"):
                        s_id = util.gerar_sosa_id("AULA", ano_lab, "I")
                        st.session_state.sosa_id_atual = s_id
                        st.session_state.lab_meta = {"ano": ano_lab, "trimestre": "I Trimestre", "tipo": "AULA"}
                        st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR AULA. ID: {s_id}. PLANO: {plano_ref}. FOCO: {aula_alvo}. QTD: {qtd_q}. EXTRA: {instr_extra}")
                        st.rerun()

    # --- ABA 2: DIAGNÓSTICO ---
    with tab_diagnostico:
        if "lab_temp" not in st.session_state:
            st.subheader("🔍 Inteligência de Nivelamento")
            with st.container(border=True):
                cd1, cd2 = st.columns(2)
                ano_diag = cd1.selectbox("Série Atual:", [6, 7, 8, 9], key=f"diag_ano_sel_{v}")
                trim_diag = cd2.selectbox("Trimestre:", ["I Trimestre", "II Trimestre", "III Trimestre"], key=f"diag_trim_sel_{v}")
                
                if trim_diag == "I Trimestre":
                    ano_busca = ano_diag - 1
                    df_retro = df_curriculo[df_curriculo['ANO'] == ano_busca]
                else:
                    df_retro = df_curriculo[(df_curriculo['ANO'] == ano_diag) & (df_curriculo['TRIMESTRE'] != trim_diag)]

                if not df_retro.empty:
                    sel_retro = st.multiselect("Pré-requisitos:", df_retro['CONTEUDO_ESPECIFICO'].tolist(), key=f"diag_mult_{v}")
                    if st.button("🧠 GERAR DIAGNÓSTICO", key=f"btn_gen_diag_{v}"):
                        s_id = util.gerar_sosa_id("DIAG", ano_diag, trim_diag)
                        st.session_state.sosa_id_atual = s_id
                        st.session_state.lab_meta = {"ano": ano_diag, "trimestre": trim_diag, "tipo": "DIAGNOSTICO"}
                        st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR DIAGNÓSTICO. ID: {s_id}. CONTEÚDOS: {sel_retro}.")
                        st.rerun()
        else: st.info("Material em edição na aba 'Produção'.")

    # --- ABA 3: TRABALHOS ---
    with tab_trabalhos:
        if "lab_temp" not in st.session_state:
            st.subheader("📋 Engenharia de Trabalhos")
            with st.container(border=True):
                ct1, ct2, ct3 = st.columns([1, 1, 1])
                ano_trab = ct1.selectbox("Série:", [6, 7, 8, 9], key=f"trab_ano_sel_{v}")
                tipo_trab = ct2.selectbox("Formato:", ["Pesquisa", "Projeto", "Seminário"], key=f"trab_tipo_sel_{v}")
                valor_trab = ct3.number_input("Valor:", 0.0, 10.0, 2.0, key=f"trab_val_sel_{v}")
                tema_trab = st.text_input("Tema:", key=f"trab_tema_sel_{v}")
                if st.button("🚀 CRIAR TRABALHO", key=f"btn_gen_trab_{v}"):
                    s_id = util.gerar_sosa_id("TRAB", ano_trab, "I")
                    st.session_state.sosa_id_atual = s_id
                    st.session_state.lab_meta = {"ano": ano_trab, "trimestre": "I Trimestre", "tipo": "TRABALHO"}
                    st.session_state.lab_temp = ai.gerar_ia("MESTRE_V24", f"GERAR TRABALHO. ID: {s_id}. TEMA: {tema_trab}. VALOR: {valor_trab}.")
                    st.rerun()
        else: st.info("Material em edição na aba 'Produção'.")

    # --- ABA 4: COMPLEMENTAR ---
    with tab_complementar:
        st.subheader("📚 Reforço e Aprofundamento")
        st.info("Use esta aba para gerar listas extras baseadas no PIP.")

    # --- ABA 5: ACERVO (DASHBOARD VISUAL V27) ---
    with tab_acervo:
        st.subheader("📂 Acervo de Materiais Produzidos")
        if not df_aulas.empty:
            # CHAVE ÚNICA PARA O FILTRO DO ACERVO
            f_ano_g = st.selectbox("Filtrar Série:", ["Todos", "6º", "7º", "8º", "9º"], key=f"acervo_filter_ano_{v}")
            df_g = df_aulas.copy()
            if f_ano_g != "Todos": df_g = df_g[df_g['ANO'] == f_ano_g]
            
            for _, row in df_g.iloc[::-1].iterrows():
                raw_c = str(row['CONTEUDO'])
                s_id_h = ai.extrair_tag(raw_c, "SOSA_ID")
                with st.container(border=True):
                    c_t1, c_t2, c_t3, c_t4, c_t5, c_t6 = st.columns([1.5, 1, 1, 1, 1, 1])
                    c_t1.markdown(f"**{row['TIPO_MATERIAL']}**\n`ID: {s_id_h}`")
                    
                    # Extração de Links
                    l_alu = re.search(r"Aluno\((.*?)\)", raw_c)
                    l_prof = re.search(r"Prof\((.*?)\)", raw_c)
                    l_pei = re.search(r"PEI\((.*?)\)", raw_c)
                    
                    link_alu = l_alu.group(1) if l_alu else row.get('LINK_DRIVE')
                    link_prof = l_prof.group(1) if l_prof else None
                    link_pei = l_pei.group(1) if l_pei and "N/A" not in l_pei.group(1) else None
                    
                    if link_alu: c_t2.link_button("📝 ALUNO", str(link_alu), use_container_width=True)
                    if link_prof: c_t3.link_button("👨‍🏫 PROF", str(link_prof), use_container_width=True)
                    if link_pei: c_t4.link_button("♿ PEI", str(link_pei), use_container_width=True)
                    else: c_t4.button("⚪ SEM PEI", disabled=True, use_container_width=True)
                    
                    if c_t5.button("🔄 REFINAR", key=f"ref_acervo_{row.name}", use_container_width=True):
                        st.session_state.refino_lab_ativo = {"ano": row['ANO'], "aula": row['TIPO_MATERIAL']}
                        st.session_state.lab_temp = raw_c
                        st.session_state.sosa_id_atual = s_id_h
                        st.session_state.lab_meta = {"ano": row['ANO'].replace('º',''), "trimestre": "I Trimestre", "tipo": "REFINO"}
                        st.rerun()

                    if c_t6.button("🗑️ APAGAR", key=f"del_acervo_{row.name}", use_container_width=True):
                        if db.excluir_registro_com_drive("DB_AULAS_PRONTAS", s_id_h): st.rerun()
                    
                    with st.expander(f"👁️ Visualizar Estrutura: {s_id_h}"):
                        col_v1, col_v2 = st.columns(2)
                        with col_v1:
                            st.info("**👨‍🏫 Guia do Professor**"); st.write(ai.extrair_tag(raw_c, "PROFESSOR"))
                        with col_v2:
                            st.success("**📝 Folha do Aluno**"); st.write(ai.extrair_tag(raw_c, "ALUNO"))
                        st.divider()
                        col_v3, col_v4 = st.columns(2)
                        with col_v3:
                            st.warning("**✅ Gabarito / Rubrica**"); st.write(ai.extrair_tag(raw_c, "GABARITO") or ai.extrair_tag(raw_c, "RUBRICA") or ai.extrair_tag(raw_c, "GABARITO_PEI"))
                        with col_v4:
                            st.error("**♿ Adaptação PEI**"); st.write(ai.extrair_tag(raw_c, "PEI"))
        else: st.info("📭 Acervo vazio.")
