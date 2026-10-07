"""Public demo: generated aggregates only, no API or credentials."""
def render_demo(st):
    st.title("Relatório de KPIs — demonstração")
    st.info("Dados inteiramente fictícios. Não há conexão com CRM ou contas de anúncios.")
    period = st.selectbox("Período", ["Setembro fictício", "Outubro fictício"])
    values = (120, 36, 12) if period.startswith("Setembro") else (150, 45, 15)
    cols = st.columns(3)
    for col, label, value in zip(cols, ("Leads", "Visitas", "Conversões"), values):
        col.metric(label, value)
    st.bar_chart({"Etapas": list(values)}, x_label="Etapas", y_label="Quantidade")
    st.caption("O modo operacional é bloqueado por padrão e exige autenticação individual, allowlist e segredos no servidor.")
