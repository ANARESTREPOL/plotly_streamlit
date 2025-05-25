# -*- coding: utf-8 -*-

#Importar librerías
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#Importar datos
ruta='datos.xlsx'
df= pd.read_excel(ruta)

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

fig.show()

#Ventas totales por segmento.

# Agrupación de ventas
ventas_segmento = df.groupby('Segmento')['Ventas'].sum().reset_index()

# Crear gráfico circular
fig = px.pie(
    ventas_segmento,
    names='Segmento',
    values='Ventas',
    title='Ventas totales por segmento',
    hole=0.4
)

fig.update_traces(
    textinfo='percent+label',
    pull=[0.05]*len(ventas_segmento)
)

# Centrar el título y quitar la leyenda
fig.update_layout(
    template='plotly_white',
    title_x=0.5,
    showlegend=False
)

fig.show()

#Impacto del método de envío en las ventas.

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
fig.show()

# Suponiendo que tu DataFrame se llama df
# Agrupamos por Categoría y sumamos Ventas y Ganancia
resumen = df.groupby('Categoría')[['Ventas', 'Ganancia']].sum().reset_index()

# Reorganizamos el DataFrame a formato largo
df_melted = resumen.melt(
    id_vars='Categoría',
    value_vars=['Ventas', 'Ganancia'],
    var_name='Tipo',
    value_name='Valor'
)

# Asegurar el orden de categorías según el total combinado
orden = resumen[['Categoría', 'Ventas', 'Ganancia']]
orden['Total'] = orden['Ventas'] + orden['Ganancia']
orden = orden.sort_values('Total', ascending=False)['Categoría']
df_melted['Categoría'] = pd.Categorical(df_melted['Categoría'], categories=orden, ordered=True)

# Formatear etiquetas con punto como separador de miles
df_melted['Etiqueta'] = df_melted['Valor'].astype(int).apply(lambda x: f"{x:,}".replace(",", "."))

# Paleta de colores personalizada
color_map = {
    'Ventas': '#50C878',     # verde
    'Ganancia': '#EF553B'    # rojo
}

# Crear gráfico de barras
fig = px.bar(df_melted,
             x='Categoría',
             y='Valor',
             color='Tipo',
             color_discrete_map=color_map,
             barmode='group',
             text='Etiqueta',
             title='Ingresos y ganancias según categoría de producto')

# Ajustes visuales
fig.update_traces(textposition='outside', textfont_size=12)

fig.update_layout(
    title_x=0.5,  # Centra el título
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

fig.show()

# Agrupar por subcategoría y calcular suma de ventas y ganancia
df_grouped = df.groupby('Subcategoría')[['Ventas', 'Ganancia']].sum().reset_index()

# Crear columna total para ordenar
df_grouped['Total'] = df_grouped['Ventas'] + df_grouped['Ganancia']

# Ordenar de mayor a menor según el total
df_grouped = df_grouped.sort_values(by='Total', ascending=False)

# Convertimos a formato largo
df_melted = df_grouped.melt(id_vars='Subcategoría', value_vars=['Ventas', 'Ganancia'],
                            var_name='Tipo', value_name='Valor')

# Mantener el orden personalizado en el gráfico
df_melted['Subcategoría'] = pd.Categorical(df_melted['Subcategoría'],
                                           categories=df_grouped['Subcategoría'],
                                           ordered=True)

# Formatear la columna Etiqueta con puntos como separadores de miles
df_melted['Etiqueta'] = df_melted['Valor'].round(0).astype(int).apply(lambda x: f"{x:,}".replace(",", "."))

# Paleta de colores personalizada
color_map = {
    'Ventas': '#1f77b4',     # azul
    'Ganancia': '#EF553B'    # rojo
}

# Crear gráfico
fig = px.bar(df_melted,
             x='Valor',
             y='Subcategoría',
             color='Tipo',
             color_discrete_map=color_map,
             barmode='group',
             orientation='h',
             text='Etiqueta',  # Usar la columna con números formateados
             title='Comparación de ventas y ganancias por subcategoría')

# Posición y tamaño de las etiquetas
fig.update_traces(textposition='outside', textfont_size=14)  # tamaño de fuente más grande

# Ajustes estéticos
fig.update_layout(
    title_x=0.5,  # Centrar el título aquí
    yaxis_title="Subcategoría",
    xaxis_title="Valor ($)",
    legend_title="Tipo",
    uniformtext_minsize=8,
    uniformtext_mode='hide',
    margin=dict(l=100, r=20, t=50, b=50)
)

fig.show()

# Agrupar por Provincia/Estado/Departamento
dfm = df.groupby('Provincia/Estado/Departamento')[['Ventas', 'Ganancia']].sum().reset_index()

# Crear el gráfico de dispersión
fig = px.scatter(
    dfm,
    x='Ventas',
    y='Ganancia',
    size='Ventas',
    color='Provincia/Estado/Departamento',
    hover_name='Provincia/Estado/Departamento',
    title='Relación entre ventas y ganancias por provincia',
    hover_data={
        'Provincia/Estado/Departamento': False,
        'Ventas': True,
        'Ganancia': True
    }
)

# Centrar el título
fig.update_layout(title_x=0.5)
fig.show()