import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Dashboard WIN Completo", layout="wide", page_icon="📈")

# Estilização para Modo Dark Trader
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-box { background-color: #1f2937; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Painel de Operações WIN - Fluxo B3 & Tempo Real")
st.markdown("Foco Absoluto no Mini Índice | Dados Macros e Sinal Técnico Sem Delay")

ARQUIVO_BANCO = "banco_fluxo_avancado.csv"

# --- 1. BANCO DE DADOS DE FLUXO MACRO B3 ---
def inicializar_banco():
    if not os.path.exists(ARQUIVO_BANCO):
        dados_iniciais = {
            "Data": ["08/09/2026", "09/09/2026", "10/09/2026", "11/09/2026"],
            "IND_Gringo": [12000, -4500, 8900, 15000], 
            "IND_Inst": [-8000, 2000, -5000, -11000]
        }
        pd.DataFrame(dados_iniciais).to_csv(ARQUIVO_BANCO, index=False)
    return pd.read_csv(ARQUIVO_BANCO)

df_completo = inicializar_banco()
ultimo_fluxo = df_completo.iloc[-1]

# --- 2. LAYOUT SUPERIOR: CARDS DE POSIÇÃO INSTITUCIONAL ---
st.subheader(f"📊 Posições Estratégicas B3 (Último Fechamento Oficial: {ultimo_fluxo['Data']})")
c1, c2 = st.columns(2)

with c1:
    st.metric(label="Saldo Acumulado dos Estrangeiros (Gringos)", value=f"{ultimo_fluxo['IND_Gringo']:,} cts", delta="CONTRATOS")
with c2:
    st.metric(label="Saldo Acumulado dos Institucionais Nacionais (Bancos/Fundos BR)", value=f"{ultimo_fluxo['IND_Inst']:,} cts", delta="CONTRATOS")

st.markdown("---")

# --- 3. SEÇÃO DO FLUXO HISTÓRICO ---
st.subheader("📈 Histórico Macro do Fluxo (IND)")
fig_fluxo = go.Figure()
fig_fluxo.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Gringo'], mode='lines+markers', name='Estrangeiros (Gringos)', line=dict(color='#00ffcc', width=3)))
fig_fluxo.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Inst'], mode='lines+markers', name='Institucionais BR', line=dict(color='#ffaa00', width=2, dash='dash')))
fig_fluxo.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_fluxo, key="grafico_fluxo_macro_vertical")

st.markdown("---")

# --- 4. SEÇÃO DO GRÁFICO REAL-TIME EM TELA CHEIA (DESTRAVADO) ---
st.subheader("⏱️ Sinal do Mini Índice Real-Time (WIN1!) - Sem Delay")

# Componente em container livre de colunas para garantir o carregamento do script da TradingView
html_widget = """
<div class="tradingview-widget-container" style="height:550px;width:100%;">
  <div id="tradingview_chart_fullscreen" style="height:550px;width:100%;"></div>
  <script type="text/javascript" src="https://tradingview.com"></script>
  <script type="text/javascript">
  new TradingView.widget({
    "width": "100%",
    "height": 550,
  <script type="text/javascript" src="https://tradingview.com"></script>

    "interval": "1",
    "timezone": "America/Sao_Paulo",
    "theme": "dark",
    "style": "1",
    "locale": "br",
    "toolbar_bg": "#f1f3f6",
    "enable_publishing": false,
    "hide_legend": false,
    "save_image": false,
    "container_id": "tradingview_chart_fullscreen"
  });
  </script>
</div>
"""
components.html(html_widget, height=560)
