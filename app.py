import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
st.subheader("📈 Histórico Macro do Fluxo Acumulado (IND)")
fig_fluxo = go.Figure()
fig_fluxo.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Gringo'], mode='lines+markers', name='Estrangeiros (Gringos)', line=dict(color='#00ffcc', width=3)))
fig_fluxo.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Inst'], mode='lines+markers', name='Institucionais BR', line=dict(color='#ffaa00', width=2, dash='dash')))
fig_fluxo.update_layout(template="plotly_dark", height=240, margin=dict(l=10, r=10, t=10, b=10))
st.plotly_chart(fig_fluxo, key="grafico_fluxo_macro_vertical")

st.markdown("---")

# --- 4. SEÇÃO DO GRÁFICO PROFISSIONAL DE VELAS (CANDLESTICKS) + VOLUME COLORIDO ---
st.subheader("⏱️ Gráfico Avançado Mini Índice Intraday (1 Minuto)")

# Banco de dados em memória para simular o formato OHLC e Cores de Fluxo
if 'dados_candles' not in st.session_state:
    st.session_state.dados_candles = pd.DataFrame([
        {"Hora": "11:46", "Abertura": 131450, "Maxima": 131510, "Minima": 131440, "Fechamento": 131500, "Volume": 4500, "Cor": "#26a69a"},
        {"Hora": "11:47", "Abertura": 131500, "Maxima": 131530, "Minima": 131480, "Fechamento": 131480, "Volume": 3800, "Cor": "#ef5350"},
        {"Hora": "11:48", "Abertura": 131480, "Maxima": 131540, "Minima": 131470, "Fechamento": 131520, "Volume": 6200, "Cor": "#26a69a"},
        {"Hora": "11:49", "Abertura": 131520, "Maxima": 131560, "Minima": 131510, "Fechamento": 131550, "Volume": 7100, "Cor": "#26a69a"},
        {"Hora": "11:50", "Abertura": 131550, "Maxima": 131550, "Minima": 131490, "Fechamento": 131510, "Volume": 5300, "Cor": "#ef5350"}
    ])

try:
    url = "https://yahoo.com"
    headers = {'User-Agent': 'Mozilla/5.0'}
    res = requests.get(url, headers=headers, timeout=3).json()
    ativo_data = res['quoteResponse']['result'][0]
    
    preco_atual = ativo_data.get('regularMarketPrice', 0)
    volume_atual = ativo_data.get('regularMarketVolume', 1000)
    
    if preco_atual > 0:
        hora_minuto = datetime.now().strftime("%H:%M")
        
        if hora_minuto != st.session_state.dados_candles['Hora'].iloc[-1]:
            abertura = st.session_state.dados_candles['Fechamento'].iloc[-1]
            cor_volume = "#26a69a" if preco_atual >= abertura else "#ef5350"
            
            novo_candle = pd.DataFrame([{
                "Hora": hora_minuto,
                "Abertura": abertura,
                "Maxima": max(abertura, preco_atual) + 20,
                "Minima": min(abertura, preco_atual) - 20,
                "Fechamento": preco_atual,
                "Volume": volume_atual / 100,
                "Cor": cor_volume
            }])
            st.session_state.dados_candles = pd.concat([st.session_state.dados_candles, novo_candle], ignore_index=True).tail(20)
        else:
            idx = st.session_state.dados_candles.index[-1]
            st.session_state.dados_candles.at[idx, 'Fechamento'] = preco_atual
            if preco_atual > st.session_state.dados_candles.at[idx, 'Maxima']:
                st.session_state.dados_candles.at[idx, 'Maxima'] = preco_atual
            if preco_atual < st.session_state.dados_candles.at[idx, 'Minima']:
                st.session_state.dados_candles.at[idx, 'Minima'] = preco_atual
            st.session_state.dados_candles.at[idx, 'Cor'] = "#26a69a" if preco_atual >= st.session_state.dados_candles.at[idx, 'Abertura'] else "#ef5350"
except:
    pass

df_candles = st.session_state.dados_candles

fig_profissional = make_subplots(rows=2, cols=1, shared_xaxes=True, 
                                 vertical_spacing=0.05, row_heights=[0.7, 0.3])

fig_profissional.add_trace(go.Candlestick(
    x=df_candles['Hora'], open=df_candles['Abertura'], high=df_candles['Maxima'], low=df_candles['Minima'], close=df_candles['Fechamento'],
    name='WIN Vela', increasing_line_color='#26a69a', decreasing_line_color='#ef5350',
    increasing_fillcolor='#26a69a', decreasing_fillcolor='#ef5350'
), row=1, col=1)

# O Volume agora acompanha a cor do fluxo agressor da barra
fig_profissional.add_trace(go.Bar(
    x=df_candles['Hora'], y=df_candles['Volume'], name='Fluxo do Dia',
    marker_color=df_candles['Cor'], opacity=0.8
), row=2, col=1)

fig_profissional.update_layout(template="plotly_dark", height=450, margin=dict(l=10, r=10, t=10, b=10), xaxis_rangeslider_visible=False, showlegend=False)
fig_profissional.update_yaxes(tickformat=",.0f", row=1, col=1)

st.plotly_chart(fig_profissional, key="grafico_candles_fluxo_final")

time.sleep(2)
st.rerun()
