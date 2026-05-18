import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(page_title="Dashboard SisATeG - Controle Geral", layout="wide")

# Customização via CSS para garantir a centralização de dados e cabeçalhos superiores em negrito
st.markdown("""
    <style>
        /* Força a centralização e o negrito nos títulos/cabeçalhos superiores das colunas */
        .stDataFrame th, .stDataFrame th > div {
            text-align: center !important;
            font-weight: bold !important;
        }
        /* Força a centralização de todas as células de dados */
        .stDataFrame td {
            text-align: center !important;
        }
    </style>
""", unsafe_allow_html=True)

# 2. CARREGAMENTO E TRATAMENTO DOS DADOS (Aba Planilha4)
@st.cache_data
def carregar_dados():
    caminho_excel = r"C:\CIIAGRO2\Situacao_Projetos\projetos.xlsx"
    df = pd.read_excel(caminho_excel, sheet_name='Planilha4')
    
    # Normaliza o nome das colunas
    df.columns = [str(col).lower().strip() for col in df.columns]
    
    # Conversão de data para o padrão MM/AAAA
    if 'data_inicio_mes' in df.columns:
        df['data_datetime'] = pd.to_datetime(df['data_inicio_mes'], errors='coerce')
    else:
        df['data_datetime'] = pd.to_datetime(df['ano_mes_referencia'], errors='coerce')
        
    df['mes_ano_formatado'] = df['data_datetime'].dt.strftime('%m/%Y')
    df['projeto'] = df['projeto'].astype(str).str.strip()
    df['ano_visita'] = df['ano_visita'].astype(int)
    
    # Tratamento e conversão das colunas de visitas para inteiro
    colunas_visitas = ['total_visitas_validas', 'total_visitas_invalidas', 'total_visitas_geral']
    for col in colunas_visitas:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0
            
    return df

try:
    df_original = carregar_dados()
except Exception as e:
    st.error(f"Erro ao ler o arquivo Excel: {e}")
    st.stop()

# 3. BARRA LATERAL (FILTROS)
st.sidebar.header("Filtros do Painel")

lista_projetos = sorted(df_original['projeto'].unique())
projeto_selecionado = st.sidebar.selectbox("1. Selecione o Projeto", lista_projetos)

lista_anos = sorted(df_original['ano_visita'].unique(), reverse=True)
ano_selecionado = st.sidebar.selectbox("2. Selecione o Ano (Para as Tabelas)", lista_anos)

# Filtragem dos conjuntos de dados
df_projeto_total = df_original[df_original['projeto'] == projeto_selecionado].sort_values('data_datetime')
df_tabela_filtrada = df_projeto_total[df_projeto_total['ano_visita'] == ano_selecionado]

# 4. PAINEL PRINCIPAL
st.title(f"Painel de Controle: {projeto_selecionado}")
st.markdown("---")

# 5. CARDS DE VISUALIZAÇÃO (Propriedades e Visitas)
if not df_projeto_total.empty:
    total_prop_card = int(df_projeto_total['total_propriedades_geral'].max())
    ativas_card = int(df_projeto_total['qtd_propriedades_ativas'].max())
    inativas_c_visita = int(df_projeto_total['qtd_propriedades_inativas_com_visita'].max())
    inativas_s_visita = int(df_projeto_total['qtd_propriedades_inativas_sem_visita'].max())
    desativadas_card = inativas_c_visita + inativas_s_visita
    
    v_validas_card = int(df_projeto_total['total_visitas_validas'].sum())
    v_invalidas_card = int(df_projeto_total['total_visitas_invalidas'].sum())
    v_geral_card = int(df_projeto_total['total_visitas_geral'].sum())
else:
    total_prop_card, ativas_card, desativadas_card = 0, 0, 0
    v_validas_card, v_invalidas_card, v_geral_card = 0, 0, 0

# Renderização do bloco de Cards
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    st.markdown(f'<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #3b82f6; box-shadow: 1px 1px 4px rgba(0,0,0,0.05); text-align: center;"><p style="margin: 0; font-size: 12px; color: #64748b; font-weight: bold;">Total Propriedades</p><h3 style="margin: 5px 0 0 0; color: #1e293b; font-size: 22px;">🏢 {total_prop_card}</h3></div>', unsafe_allow_html=True)
with c2:
    st.markdown(f'<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #10b981; box-shadow: 1px 1px 4px rgba(0,0,0,0.05); text-align: center;"><p style="margin: 0; font-size: 12px; color: #64748b; font-weight: bold;">Prop. Ativas</p><h3 style="margin: 5px 0 0 0; color: #10b981; font-size: 22px;">✅ {ativas_card}</h3></div>', unsafe_allow_html=True)
with c3:
    st.markdown(f'<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #ef4444; box-shadow: 1px 1px 4px rgba(0,0,0,0.05); text-align: center;"><p style="margin: 0; font-size: 12px; color: #64748b; font-weight: bold;">Prop. Desativadas</p><h3 style="margin: 5px 0 0 0; color: #ef4444; font-size: 22px;">❌ {desativadas_card}</h3></div>', unsafe_allow_html=True)
with c4:
    st.markdown(f'<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #0284c7; box-shadow: 1px 1px 4px rgba(0,0,0,0.05); text-align: center;"><p style="margin: 0; font-size: 12px; color: #64748b; font-weight: bold;">Visitas Válidas</p><h3 style="margin: 5px 0 0 0; color: #0284c7; font-size: 22px;">📋 {v_validas_card}</h3></div>', unsafe_allow_html=True)
with c5:
    st.markdown(f'<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #f59e0b; box-shadow: 1px 1px 4px rgba(0,0,0,0.05); text-align: center;"><p style="margin: 0; font-size: 12px; color: #64748b; font-weight: bold;">Visitas Inválidas</p><h3 style="margin: 5px 0 0 0; color: #f59e0b; font-size: 22px;">⚠️ {v_invalidas_card}</h3></div>', unsafe_allow_html=True)
with c6:
    st.markdown(f'<div style="background-color: #f8fafc; padding: 12px; border-radius: 8px; border-left: 4px solid #4b5563; box-shadow: 1px 1px 4px rgba(0,0,0,0.05); text-align: center;"><p style="margin: 0; font-size: 12px; color: #64748b; font-weight: bold;">Total de Visitas</p><h3 style="margin: 5px 0 0 0; color: #4b5563; font-size: 22px;">📊 {v_geral_card}</h3></div>', unsafe_allow_html=True)

st.markdown("---")

# 6. GRÁFICOS HISTÓRICOS COM ALTA NITIDEZ NOS NÚMEROS
st.markdown("### Histórico de Evolução Mensal")
col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("#### Total de Propriedades Geral")
    if not df_projeto_total.empty:
        fig1 = go.Figure()
        fig1.add_trace(go.Bar(
            x=df_projeto_total['mes_ano_formatado'], 
            y=df_projeto_total['total_propriedades_geral'],
            marker_color='#10b981', 
            text=df_projeto_total['total_propriedades_geral'], 
            textposition='outside', # Força o número a ficar fora/acima da barra para melhor leitura
            textfont=dict(size=15, color='#1e293b', family='Arial', weight='bold') # Ajuste de nitidez
        ))
        fig1.update_layout(
            xaxis=dict(type='category', title="Mês/Ano"), 
            yaxis=dict(title="Quantidade"), 
            height=340, 
            margin=dict(t=25, b=10),
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig1, use_container_width=True)

with col_graf2:
    st.markdown("#### Histórico de Visitas Válidas")
    if not df_projeto_total.empty:
        fig2 = go.Figure()
        fig2.add_trace(go.Bar(
            x=df_projeto_total['mes_ano_formatado'], 
            y=df_projeto_total['total_visitas_validas'],
            marker_color='#0284c7', 
            text=df_projeto_total['total_visitas_validas'], 
            textposition='outside', # Força o número a ficar fora/acima da barra
            textfont=dict(size=15, color='#1e293b', family='Arial', weight='bold') # Ajuste de nitidez
        ))
        fig2.update_layout(
            xaxis=dict(type='category', title="Mês/Ano"), 
            yaxis=dict(title="Visitas"), 
            height=340, 
            margin=dict(t=25, b=10),
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# 7. SEÇÃO DE DETALHAMENTO MENSAL - DUAS TABELAS SEPARADAS
st.markdown(f"### Detalhamento Mensal (Filtro Ano: {ano_selecionado})")

if not df_tabela_filtrada.empty:
    
    # --- TABELA 1: PROPRIEDADES ---
    st.markdown("#### 🏢 Situação das Propriedades")
    df_prop = df_tabela_filtrada[['mes_ano_formatado', 'qtd_propriedades_ativas', 'qtd_propriedades_inativas_com_visita', 'qtd_propriedades_inativas_sem_visita', 'total_propriedades_geral']].copy()
    df_prop.columns = ['Mês/Ano', 'Em atendimento (Ativas)', 'Desativadas com visita', 'Desativadas sem visita', 'Total de Propriedades']
    matriz_prop = df_prop.set_index('Mês/Ano').T
    
    # Função para destacar APENAS a linha inferior (Total) e manter os valores centralizados sem negrito nas linhas de cima
    def estilo_propriedades(row):
        if row.name == 'Total de Propriedades':
            return ['font-weight: bold; background-color: #e2e8f0; color: #1e293b; text-align: center;'] * len(row)
        return ['text-align: center; font-weight: normal; color: #334155;'] * len(row)
        
    st.dataframe(matriz_prop.style.apply(estilo_propriedades, axis=1), use_container_width=True)
    
    # --- TABELA 2: VISITAS ---
    st.markdown("#### 🚗 Consolidação de Visitas")
    df_vis = df_tabela_filtrada[['mes_ano_formatado', 'total_visitas_validas', 'total_visitas_invalidas', 'total_visitas_geral']].copy()
    df_vis.columns = ['Mês/Ano', 'Visitas Válidas', 'Visitas Inválidas', 'Total Geral de Visitas']
    matriz_vis = df_vis.set_index('Mês/Ano').T
    
    # Função para destacar APENAS a linha inferior (Total Geral) e manter os valores centralizados sem negrito nas linhas de cima
    def estilo_visitas(row):
        if row.name == 'Total Geral de Visitas':
            return ['font-weight: bold; background-color: #f1f5f9; color: #0f172a; text-align: center;'] * len(row)
        return ['text-align: center; font-weight: normal; color: #334155;'] * len(row)
        
    st.dataframe(matriz_vis.style.apply(estilo_visitas, axis=1), use_container_width=True)
    
    # --- EXPORTAÇÃO COMPLETA DAS DUAS ABAS PARA UM ÚNICO EXCEL ---
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        matriz_prop.to_excel(writer, sheet_name='Propriedades', index=True)
        matriz_vis.to_excel(writer, sheet_name='Visitas', index=True)
    processed_data = output.getvalue()
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.download_button(
        label="📥 Baixar Dados Completos (Propriedades e Visitas) em Excel",
        data=processed_data,
        file_name=f"consolidado_{projeto_selecionado}_{ano_selecionado}.xlsx",
        mime="application/vnd.ms-excel"
    )
else:
    st.warning(f"Não existem registros na planilha para o ano de {ano_selecionado}.")