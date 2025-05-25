# -*- coding: utf-8 -*-

#Importar librerías
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

#Importar datos
ruta='datos.xlsx'
df= pd.read_excel(ruta)

st.title("Análisis de Ventas y Ganancias 2018-2021 OFISANA")


# Filtros en la barra lateral
st.sidebar.header("Filtros")

# Opciones únicas
anios = sorted(df['año_pedido'].dropna().unique())
categorias = sorted(df['Categoría'].dropna().unique())
subcategorias = sorted(df['Subcategoría'].dropna().unique())
ciudades = sorted(df['Ciudad'].dropna().unique())
metodos_envio = sorted(df['Método de envío'].dropna().unique())

# Widgets de selección múltiple
filtro_anio = st.sidebar.multiselect("Año del pedido", anios, default=anios)
filtro_categoria = st.sidebar.multiselect("Categoría", categorias, default=categorias)
filtro_subcategoria = st.sidebar.multiselect("Subcategoría", subcategorias, default=subcategorias)
filtro_ciudad = st.sidebar.multiselect("Ciudad", ciudades, default=ciudades)
filtro_envio = st.sidebar.multiselect("Método de envío", metodos_envio, default=metodos_envio)

# Aplicar los filtros al DataFrame
df = df[
    (df['año_pedido'].isin(filtro_anio)) &
    (df['Categoría'].isin(filtro_categoria)) &
    (df['Subcategoría'].isin(filtro_subcategoria)) &
    (df['Ciudad'].isin(filtro_ciudad)) &
    (df['Método de envío'].isin(filtro_envio))
]

# Totales generales (ya filtrados)
total_ventas = df['Ventas'].sum()
total_ganancia = df['Ganancia'].sum()
total_ingresos = total_ventas + total_ganancia

# Mostrar los indicadores en la parte superior
st.markdown("### Totales generales")

col1, col2, col3 = st.columns(3)

col1.metric("Total Ingresos", f"${total_ingresos:,.0f}".replace(",", "."))
col2.metric("Total Ventas", f"${total_ventas:,.0f}".replace(",", "."))
col3.metric("Total Ganancias", f"${total_ganancia:,.0f}".replace(",", "."))

# Evolución mensual de ventas y ganancias
dfm = df.groupby('mes_pedido')[['Ventas','Ganancia']].sum().reset_index().sort_values('mes_pedido')
tot = dfm[['Ventas','Ganancia']].sum()
pct = {c: (dfm[c]/tot[c]*100).round(2) for c in ['Ventas','Ganancia']}
fmt = lambda x: f"{x:,.0f}".replace(",", ".")

fig = go.Figure([
    go.Scatter(
        x=dfm['mes_pedido'], y=dfm[c],
        mode='lines+markers+text', name=c,
        text=[fmt(v) for v in dfm[c]], textposition=pos,
        customdata=pct[c], hovertemplate='%{customdata:.2f}%'
    ) for c, pos in [('Ventas','top center'), ('Ganancia','bottom center')]
])

fig.update_layout(
    title_text='Evolución mensual de ventas y ganancias',
    title_x=0.5,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# Ventas totales por segmento
ventas_segmento = df.groupby('Segmento')['Ventas'].sum().reset_index()

fig = px.pie(
    ventas_segmento,
    names='Segmento',
    values='Ventas',
    title_text='Ventas totales por segmento',
    hole=0.4
)

fig.update_traces(
    textinfo='percent+label',
    pull=[0.05]*len(ventas_segmento)
)

fig.update_layout(
    template='plotly_white',
    title_x=0.5,
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# Impacto del método de envío en las ventas
dfm = (df.groupby('Método de envío')['Ventas']
         .count()
         .reset_index()
         .sort_values('Ventas', ascending=True))
pct = (dfm['Ventas'] / dfm['Ventas'].sum() * 100).round(2)
fmt = lambda x: f"{x:,.0f}".replace(",", ".")

fig = go.Figure(go.Bar(
    y=dfm['Método de envío'], x=dfm['Ventas'], orientation='h',
    text=[fmt(v) for v in dfm['Ventas']], textposition='outside',
    customdata=pct, hovertemplate='%{customdata:.2f}%'
))
fig.update_layout(
    title_text='Impacto del método de envío en las ventas',
    title_x=0.5, height=500
)

st.plotly_chart(fig, use_container_width=True)

# Ingresos y ganancias según categoría de producto
resumen = df.groupby('Categoría')[['Ventas', 'Ganancia']].sum().reset_index()

df_melted = resumen.melt(
    id_vars='Categoría',
    value_vars=['Ventas', 'Ganancia'],
    var_name='Tipo',
    value_name='Valor'
)

orden = resumen[['Categoría', 'Ventas', 'Ganancia']]
orden['Total'] = orden['Ventas'] + orden['Ganancia']
orden = orden.sort_values('Total', ascending=False)['Categoría']
df_melted['Categoría'] = pd.Categorical(df_melted['Categoría'], categories=orden, ordered=True)

df_melted['Etiqueta'] = df_melted['Valor'].astype(int).apply(lambda x: f"{x:,}".replace(",", "."))

color_map = {
    'Ventas': '#50C878',     # verde
    'Ganancia': '#EF553B'    # rojo
}

fig = px.bar(df_melted,
             x='Categoría',
             y='Valor',
             color='Tipo',
             color_discrete_map=color_map,
             barmode='group',
             text='Etiqueta',
             title_text='Ingresos y ganancias según categoría de producto')

fig.update_traces(textposition='outside', textfont_size=12)

fig.update_layout(
    title_x=0.5,
    xaxis_title="Categoría",
    yaxis_title="Montos",
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ),
    margin=dict(t=60, b=100)
)

st.plotly_chart(fig, use_container_width=True)

# Comparación de ventas y ganancias por subcategoría
df_grouped = df.groupby('Subcategoría')[['Ventas', 'Ganancia']].sum().reset_index()

df_grouped['Total'] = df_grouped['Ventas'] + df_grouped['Ganancia']

df_grouped = df_grouped.sort_values(by='Total', ascending=False)

df_melted = df_grouped.melt(id_vars='Subcategoría', value_vars=['Ventas', 'Ganancia'],
                            var_name='Tipo', value_name='Valor')

df_melted['Subcategoría'] = pd.Categorical(df_melted['Subcategoría'],
                                           categories=df_grouped['Subcategoría'],
                                           ordered=True)

df_melted['Etiqueta'] = df_melted['Valor'].round(0).astype(int).apply(lambda x: f"{x:,}".replace(",", "."))

color_map = {
    'Ventas': '#1f77b4',     # azul
    'Ganancia': '#EF553B'    # rojo
}

fig = px.bar(df_melted,
             x='Valor',
             y='Subcategoría',
             color='Tipo',
             color_discrete_map=color_map,
             barmode='group',
             orientation='h',
             text='Etiqueta',
             title_text='Comparación de ventas y ganancias por subcategoría')

fig.update_traces(textposition='outside', textfont_size=14)

fig.update_layout(
    title_x=0.5,
    yaxis_title="Subcategoría",
    xaxis_title="Valor ($)",
    legend_title="Tipo",
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    margin=dict(l=100, r=20, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)

# Relación entre ventas y ganancias por provincia
dfm = df.groupby('Provincia/Estado/Departamento')[['Ventas', 'Ganancia']].sum().reset_index()

fig = px.scatter(
    dfm,
    x='Ventas',
    y='Ganancia',
    size='Ventas',
    color='Provincia/Estado/Departamento',
    hover_name='Provincia/Estado/Departamento',
    title_text='Relación entre ventas y ganancias por provincia',
    hover_data={
        'Provincia/Estado/Departamento': False,
        'Ventas': True,
        'Ganancia': True
    }
)

fig.update_layout(title_x=0.5)

st.plotly_chart(fig, use_container_width=True)