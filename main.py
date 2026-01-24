# ==============================================================================
# MÓDULO: PLANEJAMENTO (PONTO ID) - VERSÃO INTEGRAL RESTAURADA V19
# ==============================================================================
elif menu == "📅 Planejamento (Ponto ID)":
    st.header("📅 Planejador Oficial (Ponto ID)")
    tab_gerar, tab_hist, tab_curso = st.tabs(["✨ Gerar Novo Plano", "🗂️ Histórico Detalhado", "📚 Plano de Curso Vivo"])
    
    # --- ABA 1: GERAR PLANO ---
    with tab_gerar:
        st.subheader("1. Configuração da Aula")
        col_cfg1, col_cfg2 = st.columns([1, 2])
        
        def reset_plano():
            if "p_temp" in st.session_state: del st.session_state.p_temp
            if "v_plano" in st.session_state: del st.session_state.v_plano

        ano_p = col_cfg1.selectbox("Ano/Série:", [6, 7, 8, 9], key="v19_ano_sel", on_change=reset_plano)
        
        semanas_ocupadas = []
        if not df_planos.empty and 'ANO' in df_planos.columns:
            semanas_ocupadas = df_planos[df_planos['ANO'] == f"{ano_p}º"]['SEMANA'].tolist()
        
        todas_semanas = util.gerar_semanas()
        semanas_disponiveis = [s for s in todas_semanas if s.split(" (")[0] not in semanas_ocupadas]
        opcoes_semana = semanas_disponiveis if semanas_disponiveis else ["✅ Todas planejadas!"]
        sem_p = col_cfg2.selectbox("Selecione a Semana Livre:", opcoes_semana, key="v19_sem_sel", on_change=reset_plano)
        
        if "✅" not in sem_p:
            modo_p = st.radio("Método de Elaboração:", ["🎛️ Manual (Banco de Dados)", "📖 Livro Didático"], horizontal=True)
            
            if modo_p == "🎛️ Manual (Banco de Dados)":
                df_f = df_curriculo[df_curriculo['ANO'] == ano_p] if not df_curriculo.empty else pd.DataFrame()
                if not df_f.empty:
                    c1, c2 = st.columns(2)
                    eixo = c1.selectbox("Eixo Temático:", df_f['EIXO'].unique())
                    cont_esp = c2.multiselect("Conteúdo Específico (Fiel ao Banco):", df_f[df_f['EIXO'] == eixo]['CONTEUDO_ESPECIFICO'].unique())
                    objs = st.multiselect("Objetivos de Ensino (Fiel ao Banco):", df_f[df_f['CONTEUDO_ESPECIFICO'].isin(cont_esp)]['OBJETIVOS'].unique())
                    ctx_fiel = f"EIXO: {eixo}\nCONTEÚDO: {', '.join(cont_esp)}\nOBJETIVOS: {', '.join(objs)}"
                else: st.error("Base curricular não encontrada.")
            else:
                sel_mat = st.multiselect("Selecione o Livro:", df_materiais['NOME_ARQUIVO'].tolist())
                pags = st.text_input("Páginas de Referência:")
                ctx_fiel = f"LIVRO: {sel_mat} | PÁGINAS: {pags}"

            strat = st.text_area("Sua Estratégia/Observação Inicial:", placeholder="Ex: Aula expositiva...")

            if st.button("🚀 Compor Planejamento com IA", use_container_width=True):
                with st.spinner("Maestro redigindo plano..."):
                    prompt = f"ANO: {ano_p}º, SEMANA: {sem_p}. DADOS FIÉIS: {ctx_fiel}. ESTRATÉGIA: {strat}."
                    st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt)
                    st.session_state.v_plano = 1
                    st.rerun()

        # --- AMBIENTE DE EDIÇÃO DINÂMICO ---
        if "p_temp" in st.session_state:
            st.markdown("---")
            if "v_plano" not in st.session_state: st.session_state.v_plano = 1
            
            st.subheader("🤖 Refinar Plano com o Maestro")
            comando_refino = st.chat_input("Diga o que deseja mudar (ex: 'Melhore a aula 2')...", key="chat_v19_final")
            
            if comando_refino:
                with st.spinner("Reescrevendo..."):
                    prompt_ajuste = f"PLANO ATUAL:\n{st.session_state.p_temp}\n\nSOLICITAÇÃO: {comando_refino}\n\nREGRAS: Mantenha Conteúdo/Objetivos. Sem Markdown."
                    st.session_state.p_temp = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_ajuste)
                    st.session_state.v_plano += 1
                    st.rerun()

            txt_exibicao = st.session_state.p_temp
            v = st.session_state.v_plano

            def limpar_v19(texto, label):
                t = texto.replace(label, "").replace(label.upper(), "").strip()
                if t.startswith(":") or t.startswith(" :"): t = t[1:].strip()
                return t

            abas = st.tabs(["📚 Conteúdos", "🎯 Objetivos", "🏫 Metodologia", "📝 Avaliação", "💡 Obs", "♿ PEI", "📥 EXPORTAR"])
            with abas[0]:
                c_geral = st.text_input("Eixo:", limpar_v19(ai.extrair_tag(txt_exibicao, "CONTEUDO_GERAL"), "CONTEÚDO GERAL EIXO"), key=f"ed_geral_{v}")
                c_espec = st.text_area("Conteúdos:", limpar_v19(ai.extrair_tag(txt_exibicao, "CONTEUDOS_ESPECIFICOS"), "CONTEÚDOS ESPECÍFICOS"), key=f"ed_espec_{v}")
            with abas[1]:
                objs_edit = st.text_area("Objetivos:", limpar_v19(ai.extrair_tag(txt_exibicao, "OBJETIVOS_ENSINO"), "OBJETIVOS DE ENSINO"), key=f"ed_objs_{v}")
            with abas[2]:
                met_edit = st.text_area("Metodologia:", limpar_v19(ai.extrair_tag(txt_exibicao, "METODOLOGIA"), "METODOLOGIA"), height=350, key=f"ed_met_{v}")
            with abas[3]:
                ava_edit = st.text_area("Avaliação:", limpar_v19(ai.extrair_tag(txt_exibicao, "AVALIACAO"), "AVALIAÇÃO"), key=f"ed_ava_{v}")
            with abas[4]:
                obs_edit = st.text_area("Observação:", limpar_v19(ai.extrair_tag(txt_exibicao, "OBSERVACAO"), "OBSERVAÇÃO"), key=f"ed_obs_{v}")
            with abas[5]:
                pei_edit = st.text_area("Adaptação PEI:", limpar_v19(ai.extrair_tag(txt_exibicao, "ADAPTACAO_PEI"), "ADAPTAÇÃO PEI"), key=f"ed_pei_{v}")
            with abas[6]:
                st.subheader("🚀 Exportação Profissional")
                nome_doc = st.text_input("Título:", value=f"PLANO_{ano_p}ANO_{sem_p.split(' ')[1]}", key=f"v19_title_{v}")
                dados_docx = {"geral": c_geral, "especificos": c_espec, "objetivos": objs_edit, "metodologia": met_edit, "avaliacao": ava_edit, "observacao": obs_edit, "pei": pei_edit}
                doc_file = exporter.gerar_docx_plano_pedagogico_v18(nome_doc.upper(), dados_docx, {"ano": f"{ano_p}º Ano", "semana": sem_p.split(" (")[0]})
                st.download_button("📥 BAIXAR WORD", doc_file, f"{nome_doc}.docx", use_container_width=True, key=f"btn_dl_{v}")
                if st.button("☁️ SALVAR NO DRIVE", key=f"v19_drive_{v}"):
                    link = db.subir_e_converter_para_google_docs(doc_file, nome_doc, categoria="Planos de Aula")
                    if "https://" in str(link):
                        db.salvar_link_na_planilha("DB_PLANOS", "SEMANA", sem_p.split(" (")[0], link)
                        st.success("✅ Arquivado!"); st.link_button("🚀 ABRIR NO DRIVE", str(link))

            st.markdown("---")
            col_btn1, col_btn2 = st.columns(2)
            if col_btn1.button("💾 FINALIZAR E SALVAR NO BANCO", use_container_width=True, type="primary", key=f"btn_save_{v}"):
                final_txt = f"MARKER_CONTEUDO_GERAL {c_geral} MARKER_CONTEUDOS_ESPECIFICOS {c_espec} MARKER_OBJETIVOS_ENSINO {objs_edit} MARKER_METODOLOGIA {met_edit} MARKER_AVALIACAO {ava_edit} MARKER_OBSERVACAO {obs_edit} MARKER_ADAPTACAO_PEI {pei_edit}"
                if db.salvar_no_banco("DB_PLANOS", [datetime.now().strftime("%d/%m/%Y"), sem_p.split(" (")[0], f"{ano_p}º", "I Trimestre", "PADRÃO", final_txt]):
                    st.success("✅ Salvo!"); del st.session_state.p_temp; del st.session_state.v_plano; time.sleep(1); st.rerun()
            if col_btn2.button("🗑️ DESCARTAR", use_container_width=True, key=f"btn_drop_{v}"):
                del st.session_state.p_temp; del st.session_state.v_plano; st.rerun()

    # --- ABA 2: HISTÓRICO DETALHADO (RESTAURADA) ---
    with tab_hist:
        if not df_planos.empty:
            f_ano_h = st.selectbox("Filtrar por Ano:", ["Todos", "6º", "7º", "8º", "9º"], key="v19_hist_ano")
            df_h = df_planos.copy()
            if f_ano_h != "Todos": df_h = df_h[df_h['ANO'] == f_ano_h]
            
            if not df_h.empty:
                sel_h = st.selectbox("Selecione a Semana:", df_h['SEMANA'].tolist(), key="v19_hist_sem")
                raw_h = df_h[df_h['SEMANA'] == sel_h].iloc[0]['PLANO_TEXTO']
                link_h = df_h[df_h['SEMANA'] == sel_h].iloc[0].get('LINK_DRIVE', "")
                
                h_tabs = st.tabs(["📚 Conteúdos", "🎯 Objetivos", "🏫 Metodologia", "📝 Avaliação", "💡 Obs", "♿ PEI", "📥 EXPORTAR"])
                with h_tabs[0]: st.markdown(f"**Eixo:** {ai.extrair_tag(raw_h, 'CONTEUDO_GERAL')}\n\n**Específicos:** {ai.extrair_tag(raw_h, 'CONTEUDOS_ESPECIFICOS')}")
                with h_tabs[1]: st.write(ai.extrair_tag(raw_h, "OBJETIVOS_ENSINO"))
                with h_tabs[2]: st.info(ai.extrair_tag(raw_h, "METODOLOGIA"))
                with h_tabs[3]: st.write(ai.extrair_tag(raw_h, "AVALIACAO"))
                with h_tabs[4]: st.write(ai.extrair_tag(raw_h, "OBSERVACAO"))
                with h_tabs[5]: st.success(ai.extrair_tag(raw_h, "ADAPTACAO_PEI"))
                with h_tabs[6]:
                    st.subheader("🚀 Re-exportar Plano")
                    if link_h and "https" in str(link_h):
                        st.link_button("🚀 ABRIR NO GOOGLE DOCS", str(link_h), use_container_width=True)
                    nome_h = st.text_input("Título:", value=f"REVISAO_{sel_h}", key=f"v19_hist_title_{sel_h}")
                    dados_h = {"geral": ai.extrair_tag(raw_h, "CONTEUDO_GERAL"), "especificos": ai.extrair_tag(raw_h, "CONTEUDOS_ESPECIFICOS"), "objetivos": ai.extrair_tag(raw_h, "OBJETIVOS_ENSINO"), "metodologia": ai.extrair_tag(raw_h, "METODOLOGIA"), "avaliacao": ai.extrair_tag(raw_h, "AVALIACAO"), "observacao": ai.extrair_tag(raw_h, "OBSERVACAO"), "pei": ai.extrair_tag(raw_h, "ADAPTACAO_PEI")}
                    doc_h = exporter.gerar_docx_plano_pedagogico_v18(nome_h.upper(), dados_h, {"ano": f_ano_h, "semana": sel_h})
                    st.download_button("📥 BAIXAR WORD", doc_h, f"{nome_h}.docx", use_container_width=True, key=f"btn_dl_hist_{sel_h}")
            else: st.info("Nenhum plano encontrado.")
        else: st.info("📭 Banco de dados vazio.")

    # --- ABA 3: PLANO DE CURSO VIVO (RESTAURADA) ---
    with tab_curso:
        st.markdown("### 📚 Plano de Curso Anual (Status em Tempo Real)")
        if not df_curriculo.empty:
            ano_c = st.selectbox("Série:", [6, 7, 8, 9], key="v19_curso_ano")
            df_c = df_curriculo[df_curriculo['ANO'] == ano_c].copy()
            concluidos = ""
            if not df_planos.empty:
                concluidos = " ".join(df_planos[df_planos['ANO'] == f"{ano_c}º"]['PLANO_TEXTO'].tolist()).upper()
            def check_status(cont):
                return "✅ CONCLUÍDO" if str(cont).upper() in concluidos else "⏳ PENDENTE"
            df_c['STATUS'] = df_c['CONTEUDO_ESPECIFICO'].apply(check_status)
            st.dataframe(df_c[['TRIMESTRE', 'EIXO', 'CONTEUDO_ESPECIFICO', 'STATUS']], use_container_width=True, hide_index=True)
