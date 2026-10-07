import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from dados_sessao import ArquivoInvalido, importar_sessao, iniciar_sessao, validar_desempenho

st.set_page_config(layout="wide", page_title="Relatório de Marketing | Demonstração")
iniciar_sessao(st.session_state)
st.title("Relatório de Marketing")
st.info("Demonstração com dados fictícios. Use somente arquivos de teste, sem dados pessoais. Uploads permanecem na memória da sua sessão; nenhuma planilha é salva no disco.")
st.caption("Recarregar a página ou encerrar a sessão pode descartar alterações. Esta versão não substitui armazenamento autenticado para operação com dados reais.")
menu = st.tabs(["📊 Visão Geral", "📅 Agenda da Semana", "📈 Desempenho Diário", "📌 Acompanhamento de Leads", "💡 Insights & Recomendações", "🧠 Planejamento Próxima Semana", "🧾 Prestação de Contas"])

def processar_upload(upload, kind):
    if upload is not None:
        try:
            if importar_sessao(st.session_state, kind, upload.getvalue()):
                st.rerun()
            st.success("Planilha validada nesta sessão.")
        except ArquivoInvalido as exc:
            st.error(str(exc))

with menu[2]:
    st.header("📈 Desempenho Diário das Campanhas")
    processar_upload(st.file_uploader("Planilha fictícia de desempenho (XLSX)", type=["xlsx"], key="desempenho"), "desempenho")
    edited = st.data_editor(st.session_state["dados_desempenho"], width="stretch", num_rows="dynamic", key="editor_desempenho")
    if st.button("Aplicar alterações de desempenho"):
        try:
            st.session_state["dados_desempenho"] = validar_desempenho(edited)
            st.rerun()
        except ArquivoInvalido as exc:
            st.error(str(exc))

with menu[3]:
    st.header("📌 Acompanhamento dos Leads")
    processar_upload(st.file_uploader("Planilha fictícia de leads (XLSX)", type=["xlsx"], key="leads"), "leads")
    df_leads = st.session_state["dados_leads"]
    st.metric("Total de leads", len(df_leads))
    st.dataframe(df_leads["Status de Atendimento"].value_counts().rename("Quantidade"), width="stretch")
    st.dataframe(df_leads, width="stretch", hide_index=True)

with menu[0]:
    st.header("📊 Visão Geral")
    df = st.session_state["dados_desempenho"]
    inicio = st.date_input("Data inicial", value=df["Data"].min().date(), key="inicio")
    fim = st.date_input("Data final", value=df["Data"].max().date(), key="fim")
    if inicio > fim:
        st.error("A data inicial deve ser anterior ou igual à final.")
    else:
        filtrado = df[df["Data"].between(pd.Timestamp(inicio), pd.Timestamp(fim))].copy()
        investimento = filtrado["Investimento (R$)"].sum()
        leads = filtrado["Leads"].sum()
        col1, col2, col3 = st.columns(3)
        col1.metric("Investimento no período", f"R$ {investimento:,.2f}")
        col2.metric("Leads gerados", int(leads))
        col3.metric("CPL médio", f"R$ {investimento / leads:.2f}" if leads else "—")
        if filtrado.empty:
            st.info("Nenhum registro no período selecionado.")
        else:
            fig, ax1 = plt.subplots(figsize=(8, 3))
            ax2 = ax1.twinx()
            labels = filtrado["Data"].dt.strftime("%d/%m")
            ax1.bar(labels, filtrado["Leads"], color="#4CAF50", label="Leads")
            ax2.plot(labels, filtrado["CPL (R$)"], color="black", marker="o", label="CPL")
            ax1.set_ylabel("Leads por dia")
            ax2.set_ylabel("CPL (R$)")
            st.pyplot(fig)
            plt.close(fig)

with menu[1]:
    st.header("📅 Agenda da Semana")
    agenda = pd.DataFrame({"Dia": ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"], "Ação Planejada": [""] * 5, "Responsável": [""] * 5, "Status": ["Planejado"] * 5})
    st.data_editor(agenda, width="stretch", num_rows="dynamic", key="agenda")

with menu[4]:
    st.header("💡 Insights Estratégicos da Semana")
    st.text_area("Aprendizados da semana", key="aprendizados", height=150)
    st.text_area("O que pode ser replicado", key="replicar", height=150)
    st.text_area("O que precisa ser ajustado", key="ajustar", height=150)

with menu[5]:
    st.header("🧠 Planejamento da Próxima Semana")
    st.text_area("Ações previstas", key="acoes", height=150)
    st.text_area("Testes e otimizações", key="testes", height=150)
    st.text_area("Expectativas de leads, CPL e verba", key="expectativas", height=150)

with menu[6]:
    st.header("🧾 Prestação de Contas e Evidências")
    st.caption("Seleção local de arquivo de teste, sem envio a serviços externos.")
    evidencia = st.file_uploader("Evidência fictícia", type=["pdf", "jpg", "png"], key="evidencias")
    if evidencia is not None:
        st.info("Arquivo selecionado nesta sessão. Não há publicação ou envio externo.")
