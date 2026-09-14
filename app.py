import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Dashboard WIN Completo", layout="wide", page_icon="📈")

# Estilização para Modo Dark Trader
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-box { background-color: #1f2937; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Painel de Operações WIN - Fluxo B3 & Tempo Real")
st.markdown("Foco Absoluto no Mini Índice | Dados Macros e Sinal Técnico")

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
fig_fluxo.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_fluxo, key="grafico_fluxo_macro_vertical")

st.markdown("---")

# --- 4. SEÇÃO DO GRÁFICO REAL-TIME EM PYTHON (100% DESTRAVADO) ---
st.subheader("⏱️ Histórico Recente de Preços do Mini Índice")

# Banco de dados em memória temporária para simular a variação do dia
if 'dados_grafico' not in st.session_state:
    st.session_state.dados_grafico = pd.DataFrame([
        {"Hora": "11:40", "Preco": 131450},
        {"Hora": "11:42", "Preco": 131500},
        {"Hora": "11:44", "Preco": 131480},
        {"Hora": "11:46", "Preco": 131520},
        {"Hora": "11:48", "Preco": 131550},
        {"Hora": "11:50", "Preco": 131510}
    ])

try:
    # Puxa o último preço rápido do Mini Índice via internet para atualizar a tela
    url = "https://yahoo.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=3).json()
    preco_online = res['quoteResponse']['result'][0]['regularMarketPrice']
    
    if preco_online > 0 and preco_online != st.session_state.dados_grafico['Preco'].iloc[-1]:
        hora_atual = datetime.now().strftime("%H:%M")
        novo_ponto = pd.DataFrame([{"Hora": hora_atual, "Preco": preco_online}])
        st.session_state.dados_grafico = pd.concat([st.session_state.dados_grafico, novo_ponto], ignore_index=True).tail(15)
except:
    pass

df_plot = st.session_state.dados_grafico

# Desenha o gráfico nativo que roda direto na sua máquina sem depender da TradingView
fig_win = go.Figure()
fig_win.add_trace(go.Scatter(x=df_plot['Hora'], y=df_plot['Preco'], mode='lines+markers', name='WIN Preço', line=dict(color='#00ffcc', width=3)))
fig_win.update_layout(template="plotly_dark", height=350, margin=dict(l=10, r=10, t=10, b=10), yaxis=dict(tickformat=",.0f"))
st.plotly_chart(fig_win, key="grafico_win_nativo_ok")

# Recarrega a tela sozinho de forma estável
time.sleep(2)
st.rerun()
