import streamlit as st
import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Avançado B3", layout="wide", page_icon="📊")
st.title("📊 Monitor Avançado de Fluxo B3 (WIN & WDO)")
st.markdown("Dados oficiais de derivativos extraídos diretamente da B3.")

ARQUIVO_BANCO = "banco_fluxo_avancado.csv"

def extrair_dados_completo_b3(data_str):
    url = f"https://bmfbovespa.com.br{data_str}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    resultados = {
        "Data": data_str, 
        "IND_Gringo": 0, "IND_Inst": 0,
        "DOL_Gringo": 0, "DOL_Inst": 0
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        tabelas = pd.read_html(response.text)
        
        for tabela in tabelas:
            if tabela.shape >= 5:
                tabela_str = tabela.astype(str)
                
                # SE FOR A TABELA DE ÍNDICE
                if any("ÍNDICE BOVESPA" in cell for cell in tabela_str.iloc[:, 0]):
                    # Gringos
                    l_gringo = tabela[tabela.iloc[:, 0].str.contains("INVESTIDOR NÃO RESIDENTE", na=False, case=False)]
                    if not l_gringo.empty:
                        resultados["IND_Gringo"] = int(str(l_gringo.iloc).replace('.', '')) - int(str(l_gringo.iloc).replace('.', ''))
                    # Institucionais Nacionais
                    l_inst = tabela[tabela.iloc[:, 0].str.contains("INSTITUICAO FINANCEIRA", na=False, case=False)]
                    if not l_inst.empty:
                        resultados["IND_Inst"] = int(str(l_inst.iloc).replace('.', '')) - int(str(l_inst.iloc).replace('.', ''))
                        
                # SE FOR A TABELA DE DÓLAR
                if any("DÓLAR COMERCIAL" in cell for cell in tabela_str.iloc[:, 0]):
                    # Gringos
                    l_gringo = tabela[tabela.iloc[:, 0].str.contains("INVESTIDOR NÃO RESIDENTE", na=False, case=False)]
                    if not l_gringo.empty:
                        resultados["DOL_Gringo"] = int(str(l_gringo.iloc).replace('.', '')) - int(str(l_gringo.iloc).replace('.', ''))
                    # Institucionais Nacionais
                    l_inst = tabela[tabela.iloc[:, 0].str.contains("INSTITUICAO FINANCEIRA", na=False, case=False)]
                    if not l_inst.empty:
                        resultados["DOL_Inst"] = int(str(l_inst.iloc).replace('.', '')) - int(str(l_inst.iloc).replace('.', ''))
        return resultados
    except:
        return None

def inicializar_banco():
    if not os.path.exists(ARQUIVO_BANCO):
        dados_iniciais = {
            "Data": ["08/09/2026", "09/09/2026", "10/09/2026", "11/09/2026"],
            "IND_Gringo": [12000, -4500, 8900, 15000], "IND_Inst": [-8000, 2000, -5000, -11000],
            "DOL_Gringo": [-5000, 3200, -1200, -8000], "DOL_Inst": [3000, -2500, 900, 6500]
        }
        pd.DataFrame(dados_iniciais).to_csv(ARQUIVO_BANCO, index=False)
    
    df = pd.read_csv(ARQUIVO_BANCO)
    ontem_str = (datetime.now() - timedelta(days=1)).strftime("%d/%m/%Y")
    
    if ontem_str not in df["Data"].values:
        novos = extrair_dados_completo_b3(ontem_str)
        if novos and (novos["IND_Gringo"] != 0 or novos["IND_Inst"] != 0):
            df = pd.concat([df, pd.DataFrame([novos])], ignore_index=True)
            df.to_csv(ARQUIVO_BANCO, index=False)
            st.toast("Banco de dados atualizado com o último pregão!", icon="✅")
    return df

df_completo = inicializar_banco()
ultimo = df_completo.iloc[-1]

# CARDS VISUAIS NO TOPO
st.subheader(f"📌 Posições Atuais (Último Fechamento B3: {ultimo['Data']})")
c1, c2, c3, c4 = st.columns(4)
c1.metric("IND - Gringos", f"{ultimo['IND_Gringo']:,} cts")
c2.metric("IND - Institucional Br", f"{ultimo['IND_Inst']:,} cts")
c3.metric("DOL - Gringos", f"{ultimo['DOL_Gringo']:,} cts", delta_color="inverse")
c4.metric("DOL - Institucional Br", f"{ultimo['DOL_Inst']:,} cts", delta_color="inverse")

st.markdown("---")

# GRÁFICOS DE CORRELAÇÃO
t1, t2 = st.tabs(["📈 Fluxo Casado Índice (WIN)", "💵 Fluxo Casado Dólar (WDO)"])

with t1:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Gringo'], mode='lines+markers', name='Estrangeiros', line=dict(color='#00ffcc', width=3)))
    fig.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['IND_Inst'], mode='lines+markers', name='Institucionais BR', line=dict(color='#ffaa00', width=2, dash='dash')))
    fig.update_layout(template="plotly_dark", height=450, title="Gringos vs Fundos Nacionais no Índice")
    st.plotly_chart(fig, use_container_width=True)

with t2:
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['DOL_Gringo'], mode='lines+markers', name='Estrangeiros', line=dict(color='#ff5555', width=3)))
    fig2.add_trace(go.Scatter(x=df_completo['Data'], y=df_completo['DOL_Inst'], mode='lines+markers', name='Institucionais BR', line=dict(color='#00aaff', width=2, dash='dash')))
    fig2.update_layout(template="plotly_dark", height=450, title="Gringos vs Fundos Nacionais no Dólar")
    st.plotly_chart(fig2, use_container_width=True)
