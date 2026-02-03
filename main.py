# ==============================================================================
# MÓDULO: SCANNER & DASHBOARD - ARQUITETURA V8.0 (PERÍCIA PEDAGÓGICA)
# ==============================================================================
elif menu == "📸 Scanner de Gabaritos":
    st.title("📸 Inteligência Diagnóstica e Perícia Pedagógica")
    st.markdown("---")

    if "v_scan" not in st.session_state: st.session_state.v_scan = 1
    v = st.session_state.v_scan

    # --- CARREGAMENTO DE DADOS ---
    try:
        ws_g = wb.worksheet("DB_GABARITOS_ALUNOS")
        df_diagnosticos = pd.DataFrame(ws_g.get_all_records())
    except:
        df_diagnosticos = pd.DataFrame(columns=["DATA", "ID_ALUNO", "NOME_ALUNO", "TURMA", "ID_AVALIACAO", "RESPOSTAS_ALUNO", "NOTA_CALCULADA", "LINK_FOTO_DRIVE"])

    tab_scan, tab_acervo, tab_dash = st.tabs([
        "📸 Capturar Gabarito", 
        "📂 Acervo de Evidências", 
        "📊 Dashboard de Perícia"
    ])

    # --- ABA 1: CAPTURAR GABARITO (MANTIDA E BLINDADA) ---
    with tab_scan:
        c1, c2, c3 = st.columns(3)
        turma_scan = c1.selectbox("Selecionar Turma:", sorted(df_alunos['TURMA'].unique()), key=f"t_scan_{v}")
        serie_alvo = "".join(filter(str.isdigit, turma_scan))
        provas_disponiveis = df_aulas[(df_aulas['SEMANA_REF'] == "AVALIAÇÃO") & (df_aulas['ANO'].str.contains(serie_alvo))]
        
        if not provas_disponiveis.empty:
            prova_sel = c3.selectbox("Avaliação Base:", provas_disponiveis['TIPO_MATERIAL'].tolist(), key=f"p_scan_{v}")
            ids_corrigidos = df_diagnosticos[df_diagnosticos['ID_AVALIACAO'] == prova_sel]['ID_ALUNO'].astype(str).tolist()
            alunos_restantes = df_alunos[(df_alunos['TURMA'] == turma_scan) & (~df_alunos['ID'].astype(str).isin(ids_corrigidos))]
            
            if not alunos_restantes.empty:
                aluno_scan = c2.selectbox("Aluno (Pendente):", alunos_restantes['NOME_ALUNO'].tolist(), key=f"a_scan_{v}")
                img_file = st.camera_input("Capture o gabarito", key=f"cam_{v}")
                
                if img_file:
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("🧠 Analisar Marcações", type="primary", use_container_width=True):
                        st.session_state.scan_res = ai.analisar_gabarito_vision(img_file.getvalue())
                        st.session_state.scan_img = img_file.getvalue()
                    if col_b2.button("🗑️ Descartar Foto", use_container_width=True):
                        if "scan_res" in st.session_state: del st.session_state.scan_res
                        st.rerun()

                if "scan_res" in st.session_state:
                    st.markdown("### 📝 Conferência e Resultado")
                    col_img, col_edit = st.columns([1.2, 1])
                    with col_img: st.image(st.session_state.scan_img)
                    with col_edit:
                        prova_data = provas_disponiveis[provas_disponiveis['TIPO_MATERIAL'] == prova_sel].iloc[0]
                        txt_conteudo = str(prova_data['CONTEUDO'])
                        is_pei = st.toggle("Usar Gabarito PEI?", value="PEI" in prova_sel.upper())
                        tag_alvo = "GABARITO_PEI" if is_pei else "GABARITO_REGULAR"
                        gab_raw = ai.extrair_tag(txt_conteudo, tag_alvo) or ai.extrair_tag(txt_conteudo, "GABARITO_TEXTO")
                        gab_oficial = re.findall(r"\d+[\s\.\:\-]*([A-E])", gab_raw.upper())
                        
                        qtd_questoes = len(gab_oficial)
                        dados_conf = []
                        for i in range(1, qtd_questoes + 1):
                            q_key = f"{i:02d}"
                            resp_aluno = st.session_state.scan_res.get(q_key, "?")
                            resp_certa = gab_oficial[i-1]
                            dados_conf.append({"Q": q_key, "Marcação do Aluno": resp_aluno, "Gabarito": resp_certa})
                        
                        df_editor = pd.DataFrame(dados_conf)
                        df_editor['Status'] = df_editor.apply(lambda x: "✅" if x['Marcação do Aluno'] == x['Gabarito'] and x['Gabarito'] != "?" else "❌", axis=1)
                        df_final = st.data_editor(df_editor, use_container_width=True, hide_index=True, key=f"ed_scan_{v}")
                        
                        acertos = len(df_final[df_final['Marcação do Aluno'] == df_final['Gabarito']])
                        valor_total = 10.0
                        match_val = re.search(r"VALOR:?\s*(\d+[\.,]\d+|\d+)", txt_conteudo.upper())
                        if match_val: valor_total = float(match_val.group(1).replace(',', '.'))
                        
                        nota_final = (acertos / qtd_questoes) * valor_total
                        st.metric("Nota Calculada", f"{nota_final:.2f}", delta=f"{acertos}/{qtd_questoes} acertos")
                        
                        if st.button("💾 Confirmar e Salvar Diagnóstico", type="primary", use_container_width=True):
                            with st.status("Sincronizando...", expanded=True) as status:
                                import io
                                img_io = io.BytesIO(st.session_state.scan_img)
                                link_foto = db.subir_e_converter_para_google_docs(img_io, f"SCAN_{aluno_scan}", trimestre="I Trimestre", categoria=turma_scan, modo="SCANNER")
                                link_limpo = link_foto.replace("ERRO_NO_UPLOAD: ", "") if "https" in link_foto else link_foto
                                aluno_info = df_alunos[df_alunos['NOME_ALUNO'] == aluno_scan].iloc[0]
                                
                                db.salvar_no_banco("DB_GABARITOS_ALUNOS", [
                                    datetime.now().strftime("%d/%m/%Y"), aluno_info['ID'], aluno_scan, turma_scan, prova_sel,
                                    ";".join(df_final['Marcação do Aluno'].tolist()), f"{nota_final:.2f}".replace('.', ','), link_limpo
                                ])
                                status.update(label="✅ Salvo!", state="complete")
                                st.balloons(); del st.session_state.scan_res; st.session_state.v_scan += 1; st.rerun()
            else: st.success("✅ Turma concluída!")
        else: st.warning("⚠️ Nenhuma avaliação encontrada.")

    # --- ABA 2: ACERVO DE EVIDÊNCIAS ---
    with tab_acervo:
        st.subheader("📂 Histórico de Correções")
        if not df_diagnosticos.empty:
            c_f1, c_f2 = st.columns(2)
            t_filtro = c_f1.selectbox("Filtrar Turma:", ["Todas"] + sorted(df_diagnosticos['TURMA'].unique().tolist()))
            p_filtro = c_f2.selectbox("Filtrar Prova:", ["Todas"] + sorted(df_diagnosticos['ID_AVALIACAO'].unique().tolist()))
            
            df_view = df_diagnosticos.copy()
            if t_filtro != "Todas": df_view = df_view[df_view['TURMA'] == t_filtro]
            if p_filtro != "Todas": df_view = df_view[df_view['ID_AVALIACAO'] == p_filtro]
            
            st.dataframe(df_view, column_config={"LINK_FOTO_DRIVE": st.column_config.LinkColumn("📸 Ver Gabarito")}, use_container_width=True, hide_index=True)
        else: st.info("📭 Nenhum gabarito escaneado.")

    # --- ABA 3: DASHBOARD DE PERÍCIA (O GRANDE SALTO) ---
    with tab_dash:
        st.subheader("📊 Perícia Pedagógica e Mapa de Calor")
        
        # 1. FILTRO POR TRIMESTRE (ORGANIZAÇÃO)
        trim_dash = st.radio("Filtrar por Período:", ["I Trimestre", "II Trimestre", "III Trimestre"], horizontal=True)
        
        # Filtra diagnósticos que pertencem a provas do trimestre selecionado
        # (Buscamos a informação do trimestre na DB_AULAS_PRONTAS ou DB_PLANOS)
        provas_trimestre = df_aulas[df_aulas['CONTEUDO'].str.contains(trim_dash, na=False)]['TIPO_MATERIAL'].unique()
        df_dash = df_diagnosticos[df_diagnosticos['ID_AVALIACAO'].isin(provas_trimestre)]

        if df_dash.empty:
            st.info(f"Aguardando dados do {trim_dash} para gerar a perícia.")
        else:
            prova_dash = st.selectbox("Analisar Prova Específica:", df_dash['ID_AVALIACAO'].unique())
            df_p = df_dash[df_dash['ID_AVALIACAO'] == prova_dash]
            
            # Busca Gabarito e Texto das Questões
            prova_ref = df_aulas[df_aulas['TIPO_MATERIAL'] == prova_dash].iloc[0]
            txt_full = str(prova_ref['CONTEUDO'])
            gab_raw = ai.extrair_tag(txt_full, "GABARITO_REGULAR") or ai.extrair_tag(txt_full, "GABARITO_TEXTO")
            gab_oficial = re.findall(r"\d+[\s\.\:\-]*([A-E])", gab_raw.upper())
            questoes_texto = ai.extrair_tag(txt_full, "QUESTOES")

            # 2. CÁLCULO DE ESTATÍSTICAS POR QUESTÃO
            stats_questoes = []
            for i, certa in enumerate(gab_oficial):
                q_num = f"{i+1:02d}"
                respostas_turma = [r.split(";")[i] if len(r.split(";")) > i else "?" for r in df_p['RESPOSTAS_ALUNO']]
                acertos = respostas_turma.count(certa)
                percentual = (acertos / len(df_p)) * 100
                
                # Identifica o Distrator (Erro mais comum)
                erros = [r for r in respostas_turma if r != certa and r not in ["?", "X"]]
                distrator = max(set(erros), key=erros.count) if erros else "N/A"
                
                stats_questoes.append({
                    "Questão": q_num, 
                    "Acerto %": percentual, 
                    "Acertos": acertos,
                    "Gabarito": certa,
                    "Distrator": distrator
                })
            
            df_stats = pd.DataFrame(stats_questoes)

            # 3. VISUALIZAÇÃO KPIs
            c_k1, c_k2, c_k3 = st.columns(3)
            c_k1.metric("Média da Turma", f"{df_p['NOTA_CALCULADA'].apply(lambda x: float(str(x).replace(',','.'))).mean():.2f}")
            c_k2.metric("Total Corrigido", len(df_p))
            quest_critica = df_stats.loc[df_stats['Acerto %'].idxmin()]
            c_k3.metric("Questão Crítica", f"Q{quest_critica['Questão']}", delta=f"{quest_critica['Acerto %']:.0f}% acertos", delta_color="inverse")

            # 4. GRÁFICO DE CALOR
            fig_heat = px.bar(df_stats, x="Questão", y="Acerto %", text="Acerto %", 
                             color="Acerto %", color_continuous_scale="RdYlGn", range_y=[0, 110])
            st.plotly_chart(fig_heat, use_container_width=True)

            # 5. RAIO-X DE DESCRITORES (DETALHAMENTO)
            st.markdown("### 🔍 Raio-X de Descritores e Lacunas")
            
            for _, row in df_stats.iterrows():
                cor_status = "🔴" if row['Acerto %'] < 50 else "🟡" if row['Acerto %'] < 75 else "🟢"
                with st.expander(f"{cor_status} Questão {row['Questão']} - Índice de Acerto: {row['Acerto %']:.1f}%"):
                    col_q1, col_q2 = st.columns([2, 1])
                    
                    with col_q1:
                        # Tenta extrair o texto da questão específica
                        padrao_q = rf"{int(row['Questão'])}[ªº]?\s*Questão.*?(?=\d+[ªº]?\s*Questão|$)"
                        match_q = re.search(padrao_q, questoes_texto, re.DOTALL | re.IGNORECASE)
                        texto_q = match_q.group(0) if match_q else "Texto da questão não localizado."
                        st.write(f"**Enunciado:**\n{texto_q}")
                    
                    with col_q2:
                        st.write(f"**Gabarito:** {row['Gabarito']}")
                        st.write(f"**Erro mais comum:** {row['Distrator']}")
                        if row['Acerto %'] < 50:
                            st.error("⚠️ Necessita Recomposição")
                            # Sugestão Automática baseada no erro
                            if row['Distrator'] != "N/A":
                                st.caption(f"Análise: A alta frequência da alternativa {row['Distrator']} sugere uma falha na Instrumentalização do conceito.")

            # 6. PROGNÓSTICO MAESTRO (IA)
            st.markdown("---")
            if st.button("🧠 Gerar Prognóstico Analítico da Turma"):
                with st.spinner("O Maestro está analisando os padrões de erro..."):
                    resumo_erros = df_stats[df_stats['Acerto %'] < 60].to_string()
                    prompt_prog = (
                        f"Aja como o Maestro Sosa, Engenheiro Pedagógico.\n"
                        f"Analise os resultados da prova '{prova_dash}':\n"
                        f"DADOS DE ERRO:\n{resumo_erros}\n\n"
                        f"TEXTO DAS QUESTÕES:\n{questoes_texto}\n\n"
                        f"AÇÃO: Escreva um PROGNÓSTICO DIDÁTICO (PHC).\n"
                        f"1. Identifique quais lacunas cognitivas os erros nas questões críticas revelam.\n"
                        f"2. Sugira uma estratégia de Instrumentalização para a próxima aula.\n"
                        f"3. Use linguagem técnica e Unicode. SEM MARKDOWN."
                    )
                    prognostico = ai.gerar_ia("PLANE_PEDAGOGICO", prompt_prog)
                    st.info(prognostico)
