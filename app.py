import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import requests

# ================================
# FUNÇÃO SELIC - BANCO CENTRAL
# ================================
def obter_selic():
    url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.432/dados/ultimos/1?formato=json"
    r = requests.get(url)
    dados = r.json()
    return float(dados[0]["valor"]) / 100

# ================================
# CONFIGURAÇÃO DA PÁGINA
# ================================
st.set_page_config(
    page_title="Comparador de Investimentos",
    page_icon="📊",
    layout="centered"
)

st.title("📊 Comparador de Investimentos")
st.caption("Simulação educacional com dados reais do Banco Central do Brasil")

st.divider()

# ================================
# ENTRADAS DO USUÁRIO
# ================================
valor_inicial = st.number_input(
    "💰 Valor inicial (R$)",
    min_value=0.0,
    value=1000.0,
    step=100.0
)

aporte_mensal = st.number_input(
    "➕ Aporte mensal (R$)",
    min_value=0.0,
    value=200.0,
    step=50.0
)

tipo_tempo = st.radio(
    "⏳ Unidade de tempo",
    ["Meses", "Anos"],
    horizontal=True
)

tempo = st.number_input(
    f"Tempo em {tipo_tempo.lower()}",
    min_value=1,
    value=12 if tipo_tempo == "Meses" else 1
)

if tipo_tempo == "Meses":
    total_meses = tempo
    tempo_anos = tempo / 12
else:
    total_meses = tempo * 12
    tempo_anos = tempo

st.info(f"Tempo total considerado: **{tempo_anos:.2f} anos**")

# ================================
# TAXAS
# ================================
selic = obter_selic()

st.subheader("📌 Taxas utilizadas")

st.markdown(f"- **SELIC atual:** {selic*100:.2f}% a.a.")
st.markdown("- **Poupança:** 70% da SELIC (regra oficial)")
st.markdown("- **Tesouro Selic:** Aproximação da SELIC")
st.markdown("- **CDB:** percentual do CDI definido pelo usuário")

taxa_cdb_percentual = st.slider(
    "📈 Taxa do CDB (% do CDI)",
    min_value=80,
    max_value=130,
    value=100,
    step=5
)

taxas = {
    "Poupança": selic * 0.70,
    "CDB": selic * (taxa_cdb_percentual / 100),
    "Tesouro Selic": selic
}

descricoes = {
    "Poupança": "Baixo risco • Liquidez diária",
    "CDB": f"{taxa_cdb_percentual}% do CDI • Protegido pelo FGC",
    "Tesouro Selic": "Risco muito baixo • Título público"
}

# ================================
# CÁLCULO COM APORTES MENSAIS
# ================================
def calcular_investimento(taxa_anual):
    valores = []
    saldo = valor_inicial
    taxa_mensal = (1 + taxa_anual) ** (1/12) - 1

    for _ in range(total_meses):
        saldo = saldo * (1 + taxa_mensal) + aporte_mensal
        valores.append(saldo)

    return valores

resultados = []
evolucao = {}

for inv, taxa in taxas.items():
    valores = calcular_investimento(taxa)
    evolucao[inv] = valores
    resultados.append({
        "Investimento": inv,
        "Descrição": descricoes[inv],
        "Valor final (R$)": round(valores[-1], 2)
    })

# ================================
# TABELA E RANKING
# ================================
df = pd.DataFrame(resultados)
df = df.sort_values("Valor final (R$)", ascending=False)

st.subheader("🏆 Ranking dos Investimentos")
st.dataframe(df, use_container_width=True)

melhor = df.iloc[0]["Investimento"]
st.success(f"🥇 Melhor desempenho: **{melhor}**")

# ================================
# GRÁFICO
# ================================
st.subheader("📈 Evolução do Patrimônio")

plt.figure()

for inv, valores in evolucao.items():
    plt.plot(range(1, total_meses + 1), valores, label=inv)

plt.xlabel("Tempo (meses)")
plt.ylabel("Valor acumulado (R$)")
plt.legend()
plt.grid(True)

st.pyplot(plt)

# ================================
# CONCLUSÃO
# ================================
st.divider()

st.markdown("""
### 📌 Conclusão
Este simulador utiliza **juros compostos com aportes mensais**, permitindo comparar
diferentes investimentos de renda fixa com base em dados reais.

Ideal para:
- educação financeira
- trabalhos acadêmicos
- tomada de decisão consciente
""")
