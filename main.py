# --- MOTOR DE REFINO UNIVERSAL (SOSA V28.8) ---
        st.markdown("---")
        with st.container(border=True):
            st.subheader("🤖 Refinador Maestro")
            st.caption("Solicite alterações técnicas, mude o nível de dificuldade ou altere o contexto do material.")
            
            # O chat_input deve ter uma chave única baseada na versão 'v'
            cmd_lab = st.chat_input("Ex: 'Torne as questões mais desafiadoras' ou 'Troque o contexto para o Porto de Ilhéus'", key=f"chat_lab_{v}")
            
            if cmd_lab:
                with st.spinner("Maestro Sosa realizando reengenharia pedagógica..."):
                    # LÓGICA DE PERSONA DINÂMICA
                    # Se for Sonda ou Diagnóstico, usa o refinador de exames. Se for aula/trabalho, usa o de materiais.
                    tipo_atual = st.session_state.lab_meta.get('tipo', 'AULA')
                    persona_alvo = "REFINADOR_EXAMES" if tipo_atual in ["SONDA_DIAGNOSTICA", "DIAGNOSTICO"] else "REFINADOR_MATERIAIS"
                    
                    # Chamada à IA
                    novo_conteudo = ai.gerar_ia(
                        persona_alvo, 
                        f"ORDEM DO PROFESSOR: {cmd_lab}\n\nCONTEÚDO ATUAL PARA REFINO:\n{st.session_state.lab_temp}"
                    )
                    
                    # Atualização do Estado
                    st.session_state.lab_temp = novo_conteudo
                    
                    # LEI DE SOBERANIA: Se o material principal mudou, o PEI antigo é invalidado
                    if "lab_pei" in st.session_state:
                        del st.session_state.lab_pei
                        st.toast("⚠️ Conteúdo alterado. Lembre-se de regerar a versão PEI!", icon="♿")
                    
                    st.session_state.v_lab += 1 # Incrementa versão para forçar refresh
                    st.rerun()
