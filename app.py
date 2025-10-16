import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from pathlib import Path
from datetime import datetime

# -------------------------------
# CONFIGURAÇÃO GERAL DO APP
# -------------------------------
st.set_page_config(
    page_title="ODS 14 - Vida na Água", 
    layout="wide", 
    page_icon="🌊",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #001f33, #003366);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border-left: 5px solid #00bfff;
    }
    .metric-card {
        background: rgba(0, 191, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #00bfff;
        margin: 0.5rem 0;
    }
    .section-title {
        color: #00bfff;
        border-bottom: 2px solid #00bfff;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown("""
<div class="main-header">
    <h1 style="color: white; margin:0;">🌊 ODS 14 — Vida na Água</h1>
    <p style="color: #b8e8ff; margin:0;">Análise Interativa do Progresso dos Países em Relação aos Oceanos e Recursos Marinhos</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
Este painel interativo permite explorar indicadores relacionados ao **Objetivo de Desenvolvimento Sustentável 14 (Vida na Água)**.  
Use os filtros laterais para selecionar **países, anos e indicadores** e visualize as tendências em tempo real.
""")

DATA_FOLDER = Path("MultipleFiles")

DATASETS = {
    "marine-protected-areas": {
        "label": "Áreas Marinhas Protegidas",
        "file": "marine-protected-areas.csv",
        "indicator": "Marine protected areas (% of territorial waters)",
        "y_label": "% Áreas Protegidas",
        "descrição": "Porcentagem de áreas marinhas protegidas em relação às águas territoriais"
    },
    "coastal-eutrophication": {
        "label": "Eutrofização Costeira",
        "file": "coastal-eutrophication.csv",
        "indicator": "14.1.1 - Coastal eutrophication: Total Nitrogen (TN) (kilograms of nitrogen from algae biomass per sq. km. of river basin area per day) - EN_MAR_TN",
        "y_label": "Nitrogênio (kg/km²/dia)",
        "descrição": "Níveis de nitrogênio que indicam eutrofização costeira"
    },
    "ocean-acidification": {
        "label": "Acidificação dos Oceanos",
        "file": "ocean-acidification.csv",
        "indicator": "14.3.1 - Average marine acidity (pH) measured at agreed representative sampling stations - EN_MAR_OACID",
        "y_label": "pH médio",
        "descrição": "Medição da acidez média dos oceanos"
    },
    "ocean-health-index": {
        "label": "Índice de Saúde dos Oceanos (OHI)",
        "file": "ocean-health-index.csv",
        "indicator": "Ocean Health Index (score)",
        "y_label": "Pontuação OHI",
        "descrição": "Índice de saúde dos oceanos (0-100)"
    },
    "illegal-fishing": {
        "label": "Combate à Pesca Ilegal",
        "file": "regulation-illegal-fishing.csv",
        "indicator": "14.6.1 - Progress by countries in the degree of implementation of international instruments aiming to combat illegal, unreported and unregulated fishing (level of implementation: 1 lowest to 5 highest) - ER_REG_UNFCIM",
        "y_label": "Nível de Implementação",
        "descrição": "Progresso na implementação de instrumentos contra pesca ilegal"
    }
}

# -------------------------------
# FUNÇÕES DE ANÁLISE COM PANDAS
# -------------------------------

@st.cache_data
def carregar_dados(dataset_key):
    """Carrega e limpa dados usando Pandas"""
    dataset = DATASETS[dataset_key]
    path = DATA_FOLDER / dataset["file"]

    if not path.exists():
        st.error(f"Arquivo CSV não encontrado: {path}")
        return pd.DataFrame(), dataset

    try:
        df = pd.read_csv(path)
        df = df.rename(columns={"Entity": "País/Região", "Year": "Ano"})
        indicador = dataset["indicator"]

        if indicador not in df.columns:
            st.error(f"Indicador '{indicador}' não encontrado. Colunas disponíveis: {list(df.columns)}")
            return pd.DataFrame(), dataset

        # Limpeza de dados com Pandas
        df = df.dropna(subset=["País/Região", "Ano", indicador])
        df["Ano"] = df["Ano"].astype(int)
        df[indicador] = pd.to_numeric(df[indicador], errors="coerce")
        df = df.dropna(subset=[indicador])
        
        return df, dataset
        
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return pd.DataFrame(), dataset

def analise_exploratoria(df, dataset):
    """Realiza análise exploratória com Pandas"""
    indicador = dataset["indicator"]
    
    st.subheader("📊 Análise Exploratória com Pandas")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total de Países", df["País/Região"].nunique())
    
    with col2:
        st.metric("Período dos Dados", f"{df['Ano'].min()} - {df['Ano'].max()}")
    
    with col3:
        st.metric("Média Global", f"{df[indicador].mean():.2f}")
    
    with col4:
        st.metric("Desvio Padrão", f"{df[indicador].std():.2f}")
    
    # Estatísticas descritivas
    with st.expander("📈 Estatísticas Descritivas Completas"):
        st.dataframe(df[indicador].describe())
    
    # Países com maior e menor valores
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Países com Maiores Valores:**")
        top_countries = df.groupby("País/Região")[indicador].mean().nlargest(5)
        for country, value in top_countries.items():
            st.write(f"• {country}: {value:.2f}")
    
    with col2:
        st.write("**Países com Menores Valores:**")
        bottom_countries = df.groupby("País/Região")[indicador].mean().nsmallest(5)
        for country, value in bottom_countries.items():
            st.write(f"• {country}: {value:.2f}")

def criar_grafico_tendencia(df, dataset, entidades_selecionadas, min_year, max_year):
    """Cria gráfico de tendência temporal"""
    indicador = dataset["indicator"]
    
    filtered = df[
        df["País/Região"].isin(entidades_selecionadas) & 
        df["Ano"].between(min_year, max_year)
    ]
    
    fig = px.line(
        filtered,
        x="Ano",
        y=indicador,
        color="País/Região",
        markers=True,
        labels={indicador: dataset["y_label"]},
        title=f"{dataset['label']} - Tendência Temporal ({min_year}–{max_year})",
        template="plotly_dark"
    )
    
    fig.update_layout(
        hovermode="x unified",
        showlegend=True,
        height=500
    )
    
    return fig

def criar_grafico_comparacao(df, dataset, ano):
    """Cria gráfico de comparação entre países"""
    indicador = dataset["indicator"]
    
    dados_ano = df[df["Ano"] == ano].sort_values(indicador, ascending=False).head(15)
    
    fig = px.bar(
        dados_ano,
        x="País/Região",
        y=indicador,
        title=f"{dataset['label']} - Ranking entre Países ({ano})",
        labels={indicador: dataset["y_label"]},
        color=indicador,
        color_continuous_scale="Viridis"
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        template="plotly_dark",
        height=500
    )
    
    return fig

def criar_mapa_mundial(df, dataset, ano):
    """Cria mapa mundial com dados"""
    indicador = dataset["indicator"]
    
    dados_ano = df[df["Ano"] == ano]
    
    if dados_ano.empty:
        return None
    
    fig = px.choropleth(
        dados_ano,
        locations="País/Região",
        locationmode="country names",
        color=indicador,
        hover_name="País/Região",
        hover_data={indicador: True},
        title=f"{dataset['label']} - Distribuição Mundial ({ano})",
        color_continuous_scale="Blues",
        projection="natural earth"
    )
    
    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=True,
            projection_type='equirectangular'
        ),
        template="plotly_dark",
        height=500
    )
    
    return fig

def analisar_progresso(df, dataset, entidades_selecionadas):
    """Analisa progresso dos países ao longo do tempo"""
    indicador = dataset["indicator"]
    
    progresso = []
    for ent in entidades_selecionadas:
        ent_data = df[df["País/Região"] == ent].sort_values("Ano")
        if len(ent_data) >= 2:
            primeiro = ent_data.iloc[0]
            ultimo = ent_data.iloc[-1]
            variacao = ultimo[indicador] - primeiro[indicador]
            variacao_percentual = (variacao / primeiro[indicador]) * 100 if primeiro[indicador] != 0 else 0
            
            progresso.append({
                "País/Região": ent,
                "Ano Inicial": primeiro["Ano"],
                "Ano Final": ultimo["Ano"],
                "Valor Inicial": primeiro[indicador],
                "Valor Final": ultimo[indicador],
                "Variação Absoluta": variacao,
                "Variação Percentual (%)": variacao_percentual
            })
    
    return pd.DataFrame(progresso)

def analisar_correlacao(df1, df2, dataset1, dataset2):
    """Analisa correlação entre dois indicadores"""
    indicador1 = dataset1["indicator"]
    indicador2 = dataset2["indicator"]
    
    merged = pd.merge(df1, df2, on=["País/Região", "Ano"], suffixes=("_1", "_2"))
    
    if merged.empty:
        return None, 0
    
    correlacao = merged[indicador1].corr(merged[indicador2])
    
    fig = px.scatter(
        merged,
        x=indicador1,
        y=indicador2,
        color="País/Região",
        trendline="ols",
        labels={
            indicador1: dataset1["y_label"],
            indicador2: dataset2["y_label"]
        },
        title=f"Correlação: {dataset1['label']} vs {dataset2['label']}",
        template="plotly_dark"
    )
    
    return fig, correlacao

# -------------------------------
# INTERFACE PRINCIPAL
# -------------------------------

# Sidebar com navegação
st.sidebar.header("🌊 Navegação ODS 14")
aba = st.sidebar.radio(
    "Selecione a análise:",
    ["📈 Análise Individual", "🔗 Correlação entre Indicadores", "📚 Sobre o Projeto"]
)

if aba == "📈 Análise Individual":
    st.sidebar.header("🔎 Seleção de Indicador")
    
    selected_key = st.sidebar.selectbox(
        "Escolha um indicador:",
        options=list(DATASETS.keys()),
        format_func=lambda x: DATASETS[x]['label']
    )
    
    # Carrega dados
    df, dataset = carregar_dados(selected_key)
    
    if not df.empty:
        # Filtros
        st.sidebar.header("⚙️ Filtros")
        entities = sorted(df["País/Região"].unique())
        selected_entities = st.sidebar.multiselect(
            "Selecione países/regiões:",
            entities, 
            default=entities[:5] if len(entities) > 5 else entities
        )
        
        years = sorted(df["Ano"].unique())
        min_year, max_year = st.sidebar.select_slider(
            "Selecione o período:",
            options=years,
            value=(min(years), max(years))
        )
        
        # Análise exploratória
        analise_exploratoria(df, dataset)
        
        # Visualizações principais
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.plotly_chart(
                criar_grafico_tendencia(df, dataset, selected_entities, min_year, max_year),
                use_container_width=True
            )
            
            # Mapa mundial
            ano_mapa = st.selectbox("Selecione o ano para o mapa:", years, index=len(years)-1)
            mapa = criar_mapa_mundial(df, dataset, ano_mapa)
            if mapa:
                st.plotly_chart(mapa, use_container_width=True)
        
        with col2:
            # Ranking atual
            ano_atual = st.selectbox("Ano para ranking:", years, index=len(years)-1)
            st.plotly_chart(
                criar_grafico_comparacao(df, dataset, ano_atual),
                use_container_width=True
            )
            
            # Métricas rápidas
            st.subheader("📋 Métricas do Período")
            dados_filtrados = df[
                df["País/Região"].isin(selected_entities) & 
                df["Ano"].between(min_year, max_year)
            ]
            
            if not dados_filtrados.empty:
                media_periodo = dados_filtrados[dataset["indicator"]].mean()
                variacao_periodo = dados_filtrados.groupby("País/Região")[dataset["indicator"]].mean().std()
                
                st.metric("Média do Período", f"{media_periodo:.2f}")
                st.metric("Variabilidade entre Países", f"{variacao_periodo:.2f}")
        
        # Análise de progresso
        st.subheader("📈 Análise de Progresso")
        df_progresso = analisar_progresso(df, dataset, selected_entities)
        
        if not df_progresso.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_progresso = px.bar(
                    df_progresso,
                    x="País/Região",
                    y="Variação Absoluta",
                    color="Variação Absoluta",
                    title="Variação Absoluta no Período",
                    template="plotly_dark"
                )
                st.plotly_chart(fig_progresso, use_container_width=True)
            
            with col2:
                st.dataframe(
                    df_progresso.style.format({
                        "Valor Inicial": "{:.2f}",
                        "Valor Final": "{:.2f}",
                        "Variação Absoluta": "{:.2f}",
                        "Variação Percentual (%)": "{:.1f}%"
                    }),
                    use_container_width=True
                )
        
        # Download de dados
        st.sidebar.header("💾 Exportar Dados")
        dados_filtrados = df[
            df["País/Região"].isin(selected_entities) & 
            df["Ano"].between(min_year, max_year)
        ]
        
        st.sidebar.download_button(
            "Baixar dados filtrados (CSV)",
            data=dados_filtrados.to_csv(index=False).encode("utf-8"),
            file_name=f"ods14_{selected_key}_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

elif aba == "🔗 Correlação entre Indicadores":
    st.sidebar.header("📊 Análise de Correlação")
    
    col1, col2 = st.sidebar.columns(2)
    
    with col1:
        ind1_key = st.selectbox(
            "Indicador 1:",
            list(DATASETS.keys()),
            format_func=lambda x: DATASETS[x]['label'],
            index=0
        )
    
    with col2:
        ind2_key = st.selectbox(
            "Indicador 2:",
            list(DATASETS.keys()),
            format_func=lambda x: DATASETS[x]['label'],
            index=1
        )
    
    if ind1_key == ind2_key:
        st.warning("⚠️ Selecione indicadores diferentes para análise de correlação.")
    else:
        df1, dataset1 = carregar_dados(ind1_key)
        df2, dataset2 = carregar_dados(ind2_key)
        
        if not df1.empty and not df2.empty:
            fig_corr, correlacao = analisar_correlacao(df1, df2, dataset1, dataset2)
            
            if fig_corr:
                st.plotly_chart(fig_corr, use_container_width=True)
                
                col1, col2, col3 = st.columns(3)
                with col2:
                    st.metric(
                        "Coeficiente de Correlação",
                        f"{correlacao:.3f}",
                        help="Valores próximos de 1 indicam correlação positiva forte, próximos de -1 indicam correlação negativa forte"
                    )
                
                # Interpretação da correlação
                st.subheader("📝 Interpretação da Correlação")
                if abs(correlacao) > 0.7:
                    st.success("**Correlação forte**: Existe uma relação significativa entre os dois indicadores.")
                elif abs(correlacao) > 0.3:
                    st.info("**Correlação moderada**: Existe alguma relação entre os indicadores.")
                else:
                    st.warning("**Correlação fraca**: Pouca ou nenhuma relação direta entre os indicadores.")

else:  # Sobre o Projeto
    st.header("📚 Sobre o Projeto ODS 14")
    
    st.markdown("""
    ### Objetivo do Projeto
    Este projeto visa analisar e visualizar dados relacionados ao **ODS 14 - Vida na Água**, 
    permitindo explorar o progresso dos países em relação à conservação e uso sustentável 
    dos oceanos, mares e recursos marinhos.
    
    ### Metas do ODS 14 Analisadas
    - **14.1**: Reduzir a poluição marinha
    - **14.2**: Proteger e restaurar ecossistemas
    - **14.3**: Reduzir a acidificação dos oceanos
    - **14.4**: Pesca sustentável
    - **14.5**: Conservar áreas costeiras e marinhas
    - **14.6**: Acabar com subsídios à pesca ilegal
    
    ### Tecnologias Utilizadas
    - **Python** com **Pandas** para análise de dados
    - **Streamlit** para a aplicação web interativa
    - **Plotly** para visualizações dinâmicas
    - **GitHub** para versionamento e colaboração
    
    ### Fontes de Dados
    - [Our World in Data](https://ourworldindata.org/)
    - [UN Sustainable Development Goals](https://sdgs.un.org/)
    - [World Bank Open Data](https://data.worldbank.org/)
    
    ### Desenvolvido por
    Equipe de Análise de Dados - Projeto ODS 14
    """)

# Rodapé
st.markdown("---")
st.caption(
    "Desenvolvido com ❤️ usando Python, Pandas e Streamlit | "
    "Dados: Our World in Data & UN Sustainable Development Goals | "
    "ODS 14: Vida na Água"
)