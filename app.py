import streamlit as st
import matplotlib.pyplot as plt
import requests
import pandas as pd

# ================================
# ESTILO VISUAL (CSS)
# ================================
st.markdown("""
<style>
    .main { background-color: #f7f9fc; }
    h1, h2, h3 { color: #1f2937; }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .ranking {
        font-size: 18px;
        margin: 6px 0;
    }
    .winner {
        background-color: #e6f4ea;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #16a34a;
    }
</style>
""", unsafe_allow_html=True)

# ================================
# FUNÇÃO SELIC
# ================================
def obter_selic():
    try:
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
        resposta = requests.get(url, timeout=5)
        dados = resposta.json()
        return float(dados[0]["valor"]) / 100
    except:
        st.warning("⚠️ Usando SELIC padrão (10%)")
        return 0.10

# ================================
# CONFIGURAÇÃO
# ================================
st.set_page_config(
    page_title="Comparador de Investimentos",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Comparador de Investimentos")
st.caption("Planejamento financeiro com juros compostos e aporte mensal")

# ================================
# ENTRADAS (CARD)
# ================================
st.markdown('<div class="card">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    valor_inicial = st.number_input("💰 Valor inicial (R$)", 0.0, 1000.0, step=100.0)
    aporte_mensal = st.number_input("➕ Aporte mensal (R$)", 0.0, 200.0, step=50.0)

with col2:
    tipo_tempo = st.radio("⏳ Unidade de tempo", ["Meses", "Anos"])
    tempo = st.number_input(
        "Tempo do investimento",
        min_value=1,
        value=12 if tipo_tempo == "Meses" else 1
    )

st.markdown('</div>', unsafe_allow_html=True)

total_meses = tempo if tipo_tempo == "Meses" else tempo * 12
st.info(f"⏱️ Período total: **{total_meses} meses**")

# ================================
# TAXAS
# ================================
selic = obter_selic()

taxas = {
    "Poupança": selic * 0.70,
    "CDB (100% CDI)": selic,
    "Tesouro Selic": selic
}

# ================================
# CÁLCULOS
# ================================
dados = []
grafico = []

for nome, taxa_anual in taxas.items():
    taxa_mensal = taxa_anual / 12
    saldo = valor_inicial
    valores = [saldo]

    for _ in range(total_meses):
        saldo = saldo * (1 + taxa_mensal) + aporte_mensal
        valores.append(saldo)

    total_investido = valor_inicial + aporte_mensal * total_meses
    rendimento = saldo - total_investido

    dados.append({
        "Investimento": nome,
        "Taxa anual (%)": round(taxa_anual * 100, 2),
        "Total investido (R$)": total_investido,
        "Valor final (R$)": saldo,
        "Rendimento (R$)": rendimento
    })

    grafico.append((nome, valores))

df = pd.DataFrame(dados)

# ================================
# RANKING (CARD)
# ================================
ranking = df.sort_values("Valor final (R$)", ascending=False).reset_index(drop=True)

st.markdown('<div class="card">', unsafe_allow_html=True)
st.subheader("🏆 Ranking dos Investimentos")

emojis = ["🥇", "🥈", "🥉"]
for i, row in ranking.iterrows():
    emoji = emojis[i] if i < 3 else "🔹"
    st.markdown(
        f'<div class="ranking">{emoji} <b>{row["Investimento"]}</b> — '
        f'R$ {row["Valor final (R$)"]:,.2f}</div>',
        unsafe_allow_html=True
    )

melhor = ranking.iloc[0]

st.markdown(
    f"""
    <div class="winner">
        <b>Melhor opção na simulação:</b><br>
        {melhor["Investimento"]}<br>
        Valor final: <b>R$ {melhor["Valor final (R$)"]:,.2f}</b>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown('</div>', unsafe_allow_html=True)

# ================================
# TABELA
# ================================
st.subheader("📋 Tabela Comparativa")

df_fmt = df.copy()
for col in ["Total investido (R$)", "Valor final (R$)", "Rendimento (R$)"]:
    df_fmt[col] = df_fmt[col].map(lambda x: f"R$ {x:,.2f}")

st.dataframe(df_fmt, use_container_width=True)

# ================================
# GRÁFICO
# ================================
st.subheader("📈 Evolução do Patrimônio")

plt.figure()
meses = list(range(0, total_meses + 1))

for nome, valores in grafico:
    plt.plot(meses, valores, label=nome)

plt.xlabel("Meses")
plt.ylabel("Valor acumulado (R$)")
plt.title("Crescimento com aportes mensais")
plt.legend()
plt.grid(True)

st.pyplot(plt)

# ================================
# FECHAMENTO
# ================================
st.success(
    "💡 Investir com constância e escolher bem o produto "
    "faz uma diferença enorme no longo prazo."
)
