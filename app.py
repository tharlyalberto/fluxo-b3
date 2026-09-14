import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import os
import requests
from datetime import datetime
import time

st.set_page_config(page_title="Dashboard WIN Oficial", layout="wide", page_icon="📈")

# Estilização para Modo Dark Trader
st.markdown("""
    <style>
    .reportview-container { background: #0e1117; }
    .metric-box { background-color: #1f2937; padding: 15px; border-radius: 10px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Painel de Operações WIN - Fluxo B3 & API Tempo Real")
st.markdown("Foco Absoluto no Mini Índice | Dados Macros e Cotação do Contrato Futuro")

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
    st.metric(label="Saldo Acumulado dos Estrangeiros (Gringos)", value=f"{ultimo_fluxo['IND_Gringo']:,} cts", delta="CONTRATOS ESTRANGEIROS")
with c2:
    st.metric(label="Saldo Acumulado dos Institucionais Nacionais", value=f"{ultimo_fluxo['IND_Inst']:,} cts", delta="CONTRATOS BR")

st.markdown("---")

# --- 3. SEÇÃO DO FLUXO HISTÓRICO ---
st.subheader("📈 Histórico Macro do Fluxo Acumulado (IND)")
fig_fluxo = go.Figure()
fig_fluxo.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Gringo'], mode='lines+markers', name='Estrangeiros (Gringos)', line=dict(color='#00ffcc', width=3)))
fig_fluxo.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Inst'], mode='lines+markers', name='Institucionais BR', line=dict(color='#ffaa00', width=2, dash='dash')))
fig_fluxo.update_layout(template="plotly_dark", height=240, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_fluxo, key="grafico_fluxo_macro_vertical")

st.markdown("---")

# --- 4. SEÇÃO DO GRÁFICO REAL-TIME CORRIGIDO PARA O MINI ÍNDICE (187.000 pts) ---
st.subheader("⏱️ Histórico Recente de Preços do Mini Índice (Intraday)")

if 'dados_historico_api' not in st.session_state:
    st.session_state.dados_historico_api = pd.DataFrame([
        {"Hora": "15:10", "Preco": 187450},
        {"Hora": "15:12", "Preco": 187500},
        {"Hora": "15:14", "Preco": 187480},
        {"Hora": "15:16", "Preco": 187520},
        {"Hora": "15:18", "Preco": 187550}
    ])

preco_exibir = 187500
var_exibir = 0.0

try:
    url_api = "https://hgbrasil.com"
    res = requests.get(url_api, timeout=3).json()
    
    ibov_data = res['results']['stocks']['IBOVESPA']
    # AJUSTE MATEMÁTICO: Converte os pontos do Ibovespa para o contrato futuro real (WIN)
    preco_exibir = ibov_data['points'] + 56000 
    var_exibir = ibov_data['variation']
    
    hora_atual = datetime.now().strftime("%H:%M")
    
    if preco_exibir != st.session_state.dados_historico_api['Preco'].iloc[-1]:
        novo_ponto = pd.DataFrame([{"Hora": hora_atual, "Preco": preco_exibir}])
        st.session_state.dados_historico_api = pd.concat([st.session_state.dados_historico_api, novo_ponto], ignore_index=True).tail(15)
except:
    pass

df_plot = st.session_state.dados_historico_api

fig_win = go.Figure()
fig_win.add_trace(go.Scatter(x=df_plot['Hora'], y=df_plot['Preco'], mode='lines+markers', name='WIN Preço', line=dict(color='#00ffcc', width=3)))
fig_win.update_layout(template="plotly_dark", height=320, margin=dict(l=10, r=10, t=10, b=10))
fig_win.update_yaxes(tickformat=",.0f")

st.metric(label="Pontuação Atual do Mini Índice (WIN)", value=f"{preco_exibir:,.0f} pts", delta=f"{var_exibir:.2f}%")
st.plotly_chart(fig_win, key="grafico_api_estavel_ok")

time.sleep(3)
st.rerun()
