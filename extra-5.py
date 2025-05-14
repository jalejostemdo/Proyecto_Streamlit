import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import seaborn as sns

# Carga de datos
reviews = pd.read_csv('Olist_Data/olist_order_reviews_dataset.csv')
items = pd.read_csv('Olist_Data/olist_order_items_dataset.csv')
sellers = pd.read_csv('Olist_Data/olist_sellers_dataset.csv')
products = pd.read_csv('Olist_Data/olist_products_dataset.csv')
name_trans = pd.read_csv('Olist_Data/product_category_name_translation.csv')

# Limpieza y unión de datos
reviews_5 = reviews[['order_id', 'review_score']].copy()
items_5 = items[['order_id', 'product_id', 'seller_id', 'price', 'freight_value']].copy()
items_5['Total prize'] = items_5['price'].astype(float) + items_5['freight_value'].astype(float)
items_5['Total prize'] = items_5['Total prize'].round(2)

products_5 = products[['product_id', 'product_category_name']].copy()
product_category_5 = pd.merge(products_5, name_trans, on='product_category_name', how='left')
product_category_5 = product_category_5[['product_id', 'product_category_name_english']]
product_category_5 = product_category_5.rename(columns={'product_category_name_english': 'product_category_name'})

# Unión completa
df_5 = pd.merge(reviews_5, items_5, on='order_id', how='left')
df_5 = pd.merge(df_5, sellers, on='seller_id', how='left')
df_5 = pd.merge(df_5, product_category_5, on='product_id', how='left')
df_5 = df_5.drop_duplicates()

# Filtros dinámicos en la barra lateral
st.sidebar.header("🔎 Filtros")

# Filtro por estado del vendedor
estados_disponibles = df_5['seller_state'].dropna().unique()
estados_seleccionados = st.sidebar.multiselect(
    "Filtrar por estado del vendedor",
    options=sorted(estados_disponibles),
    default=sorted(estados_disponibles)
)
df_5 = df_5[df_5['seller_state'].isin(estados_seleccionados)]

# Filtro por calificación
score_min, score_max = st.sidebar.slider(
    "Filtrar por calificación (review_score)",
    int(df_5['review_score'].min()),
    int(df_5['review_score'].max()),
    (int(df_5['review_score'].min()), int(df_5['review_score'].max()))
)
df_5 = df_5[(df_5['review_score'] >= score_min) & (df_5['review_score'] <= score_max)]

# Filtro por precio total
price_min, price_max = st.sidebar.slider(
    "Filtrar por precio total",
    float(df_5['Total prize'].min()), float(df_5['Total prize'].max()),
    (float(df_5['Total prize'].min()), float(df_5['Total prize'].max()))
)
df_5 = df_5[(df_5['Total prize'] >= price_min) & (df_5['Total prize'] <= price_max)]

# Filtro por costo de envío
freight_min, freight_max = st.sidebar.slider(
    "Filtrar por costo de envío",
    float(df_5['freight_value'].min()), float(df_5['freight_value'].max()),
    (float(df_5['freight_value'].min()), float(df_5['freight_value'].max()))
)
df = df_5[(df_5['freight_value'] >= freight_min) & (df_5['freight_value'] <= freight_max)]

# Filtro por número de pedidos
st.sidebar.subheader("Filtrar por número de pedidos")
# Contamos el número de pedidos por vendedor (o cliente)
order_count = df.groupby('seller_id')['order_id'].nunique()

# Definir el rango de pedidos (mínimo y máximo)
min_orders = int(order_count.min())
max_orders = int(order_count.max())

# Slider para seleccionar el rango de número de pedidos
min_filter, max_filter = st.sidebar.slider(
    "Selecciona el rango de número de pedidos",
    min_value=min_orders,
    max_value=max_orders,
    value=(min_orders, max_orders),
    step=1
)

# Filtrar el dataframe según el número de pedidos
filtered_order_df = order_count[(order_count >= min_filter) & (order_count <= max_filter)]
df_5 = df_5[df_5['seller_id'].isin(filtered_order_df.index)]

# -----------------------------
# Gráficos
# -----------------------------
col1, col2 = st.columns(2)

# 1. Vendedores mejor valorados
with col1:
    st.subheader("🌟 Vendedores mejor valorados (Top 10)")
    top_sellers_5 = df_5.groupby('seller_id')['review_score'].mean().sort_values(ascending=False).head(10)
    top_sellers_5.index = top_sellers_5.index.str[:10] + "..."
    fig1, ax1 = plt.subplots()
    top_sellers_5.plot(kind='bar', ax=ax1, color='skyblue')
    ax1.set_ylabel('Puntuación Promedio')
    ax1.set_xlabel('')
    ax1.set_title('')
    st.pyplot(fig1)

# 2. Distribución de calificaciones (Donut)
with col2:
    st.subheader("⭐ Distribución de Calificaciones")
    review_counts_5 = df_5['review_score'].value_counts().sort_index()
    colors_5 = sns.color_palette('pastel')[0:5]
    labels_5 = [str(int(score)) for score in review_counts_5.index]

    fig5, ax5 = plt.subplots()
    wedges, texts, autotexts = ax5.pie(
        review_counts_5,
        labels_5=labels_5,
        autopct='%1.1f%%',
        startangle=90,
        colors_5=colors_5,
        wedgeprops=dict(width=0.4),
        textprops=dict(color="black", fontsize=12)
    )

    for autotext in autotexts:
        autotext.set_fontsize(11)
        autotext.set_weight("bold")

    ax5.set_title('', fontsize=14)
    st.pyplot(fig5)

col3, col4, col5 = st.columns(3)

# 3. Categorías de productos más compradas
with col3:
    st.subheader("📈 Categoría más compradas (Top 10)")
    top_categories_5 = df_5['product_category_name'].value_counts().head(10)
    top_categories_5.index = top_categories_5.index.str[:15] + "..."
    fig2, ax2 = plt.subplots()
    top_categories_5.plot(kind='bar', ax=ax2, color='lightgreen')
    ax2.set_ylabel('Cantidad')
    ax2.set_xlabel('')
    ax2.set_title('')
    st.pyplot(fig2)

# 4. Ingresos por vendedor
with col4:
    st.subheader("💰 Ingresos por vendedor (Top 10)")
    seller_revenue_5 = df_5.groupby('seller_id')['Total prize'].sum().sort_values(ascending=False).head(10)
    seller_revenue_5.index = seller_revenue_5.index.str[:10] + "..."
    fig3, ax3 = plt.subplots()
    seller_revenue_5.plot(kind='bar', ax=ax3, color='gold')
    ax3.set_ylabel('Ingresos')
    ax3.set_xlabel('')
    ax3.set_title('')
    st.pyplot(fig3)

# 5. Costo medio de envío por categoría
with col5:
    st.subheader("🚚 Coste medio de envío por categoría (Top 10)")
    shipping_cost_5 = df_5.groupby('product_category_name')['freight_value'].mean().sort_values(ascending=False).head(10)
    shipping_cost_5.index = shipping_cost_5.index.str[:15] + "..."
    fig4, ax4 = plt.subplots()
    shipping_cost_5.plot(kind='bar', ax=ax4, color='salmon')
    ax4.set_ylabel('Costo Promedio')
    ax4.set_xlabel('')
    ax4.set_title('')
    st.pyplot(fig4)




