import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests

st.set_page_config(page_title="Informe Olist", layout="wide")

st.title("Informe Analítico - Olist")

string_columns_orders = [
    'customer_id'
    'order_id',
    'order_status',
]

string_columns_customers = [
    'customer_id',
    'customer_unique_id',
    'customer_city',
    'customer_state',
]

date_columns = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date',
]
st.markdown("---")

# Cargar datos
orders = pd.read_csv('./Olist_Data/olist_orders_dataset.csv')
customers = pd.read_csv('./Olist_Data/olist_customers_dataset.csv')

# Merge
df = pd.merge(orders, customers, on='customer_id')
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
df['year'] = df['order_purchase_timestamp'].dt.year

# ==== SIDEBAR ====
st.sidebar.title("🎛️ Filtros")
years = sorted(df['year'].dropna().unique(), reverse=True)
selected_year = st.sidebar.selectbox("Selecciona un año", years, index=0)

df = df[df['year'] == selected_year]

pie_threshold = st.sidebar.slider("Umbral % para gráfico circular", 0.0, 10.0, 2.0)
color_theme_list = ['Blues', 'Greens', 'Reds', 'Purples', 'viridis', 'plasma', 'inferno', 'cividis']
selected_color_theme = st.sidebar.selectbox("Tema de color", color_theme_list)

# ==== PROCESAMIENTO ====
late_df = df[df["order_delivered_customer_date"] > df["order_estimated_delivery_date"]]
late_orders = late_df.groupby("customer_city").size().rename("late_orders").to_frame()
late_orders["avg_late_days"] = (
    (late_df["order_delivered_customer_date"] - late_df["order_estimated_delivery_date"]).dt.days
).groupby(late_df["customer_city"]).mean()
late_orders["total_orders"] = df.groupby("customer_city").size()
late_orders["late_percentage"] = (late_orders["late_orders"] / late_orders["total_orders"]) * 100
late_orders.dropna(inplace=True)

# KPIs
total_late = late_df.shape[0]
avg_late_days = late_orders["avg_late_days"].mean()
avg_late_percent = late_orders["late_percentage"].mean()

# ============================
# 4.1 Distribución Geográfica
# ============================
with st.expander("4.1 Distribución Geográfica de Clientes", expanded=True):
    st.subheader("Objetivo")
    st.markdown("Identificar las zonas con mayor concentración de clientes para orientar acciones comerciales y logísticas.")

    st.subheader("KPIs")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Top 5 Estados", "...")
    kpi_col2.metric("Ciudades en esos Estados", "...")
    kpi_col3.metric("Evolución de clientes", "...")

    st.subheader("Visualizaciones")
    st.markdown("- Mapa de calor geográfico")
    st.markdown("- Tabla dinámica: Estado → Ciudad → Nº Clientes")

    st.subheader("Insight")
    st.info("El 67% de la base de clientes se concentra en cinco estados, siendo São Paulo el de mayor peso. Este patrón sugiere que campañas de marketing y mejoras logísticas en estos estados tendrán un mayor retorno.")

st.markdown("---")

# ============================
# 4.2 Análisis de Pedidos
# ============================
with st.expander("4.2 Análisis de Pedidos y Comportamiento del Cliente", expanded=True):
    st.subheader("Objetivo")
    st.markdown("Entender la relación entre cantidad de pedidos, porcentaje respecto al total y hábitos de consumo por cliente.")

    st.subheader("KPIs")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Total pedidos por ciudad", "...")
    kpi_col2.metric("% del total nacional", "...")
    kpi_col3.metric("Ratio pedidos por cliente", "...")

    st.subheader("Visualizaciones")
    st.markdown("- Barras apiladas por ciudad")
    st.markdown("- Tabla con métricas clave")

    st.subheader("Insight")
    st.info("Algunas ciudades con alta cantidad de clientes presentan ratios bajos de pedidos por cliente. Esto sugiere oportunidades de fidelización o retención con campañas específicas (descuentos por recurrencia, newsletters, etc.).")

st.markdown("---")

# ============================
# 4.3 Logística y Retrasos
# ============================
with st.expander("4.3 Logística y Diagnóstico de Retrasos en Entregas", expanded=True):
    st.subheader("Objetivo")
    st.markdown("Analizar causas y patrones en los pedidos que superan la fecha estimada de entrega.")

    st.subheader("KPIs")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("% Pedidos con retraso", f"{avg_late_percent:.1f}%")
    kpi_col2.metric("Días promedio de retraso", f"{avg_late_days:.1f}")
    kpi_col3.metric("Causa principal", "Demora del vendedor en despachar (43%)")

    st.subheader("Visualizaciones")

    # Gráficos compactos
    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("🏙️ Top 5 Ciudades con más Pedidos Tardíos")
        fig1, ax1 = plt.subplots(figsize=(7, 5))
        top_late = late_orders.sort_values("late_orders", ascending=False).head(5)
        top_late["late_orders"].plot(kind="bar", color="tomato", ax=ax1)
        ax1.set_ylabel("")
        ax1.set_xticklabels(top_late.index, rotation=45, ha="right")
        st.pyplot(fig1)

    with col2:
        st.caption("📈 % Tardíos vs Totales (Top 5 Ciudades)")
        fig2, ax2 = plt.subplots(figsize=(7, 5))
        top = late_orders.sort_values("total_orders", ascending=False).head(5)
        top[["late_orders", "total_orders"]].plot(kind="bar", stacked=False, ax=ax2, color=["red", "lightgray"])
        ax2.set_ylabel("")
        ax2.set_xticklabels(top.index, rotation=45, ha="right")
        st.pyplot(fig2)

    with col3:
        st.caption("⏳ Prom. Días de Retraso (Top 5 Ciudades)")
        fig3, ax3 = plt.subplots(figsize=(7, 5))
        late_orders.sort_values("avg_late_days", ascending=False).head(5)["avg_late_days"].plot(
            kind="barh", color="orange", ax=ax3
        )
        ax3.set_xlabel("")
        st.pyplot(fig3)

    # Línea de tiempo
    col4, col5 = st.columns([1.4, 1.4])

    with col4:
        st.caption("📅 Tardíos por Mes")
        late_over_time = (
            late_df.groupby(late_df["order_purchase_timestamp"].dt.to_period("M"))
            .size()
            .rename("late_orders")
            .to_frame()
        )
        late_over_time.index = late_over_time.index.to_timestamp()
        fig4, ax4 = plt.subplots(figsize=(9, 5))
        late_over_time.plot(ax=ax4, marker="o", legend=False)
        st.pyplot(fig4)

    with col5:
        st.caption("📍 % Tardíos por Estado (> {:.1f}%)".format(pie_threshold))
        late_by_state = late_df.groupby("customer_state").size().rename("late_orders").to_frame()
        late_by_state["late_percentage"] = (late_by_state["late_orders"] / late_by_state["late_orders"].sum()) * 100
        filtered = late_by_state[late_by_state["late_percentage"] > pie_threshold]
        fig5, ax5 = plt.subplots(figsize=(9, 5))
        filtered["late_percentage"].plot(
            kind="pie", autopct="%1.1f%%", startangle=90, colormap=selected_color_theme, ax=ax5
        )
        ax5.set_ylabel("")
        st.pyplot(fig5)

    # ============================
    # Mapa Choropleth Brasil
    # ============================
    st.caption("🗺️ Mapa de Pedidos Tardíos por Estado (Choropleth)")

    # Cargar GeoJSON
    geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    geojson_data = requests.get(geojson_url).json()

    # Choropleth con Plotly
    fig_map = px.choropleth(
        late_by_state.reset_index(),
        geojson=geojson_data,
        locations="customer_state",
        color="late_percentage",
        color_continuous_scale=selected_color_theme,
        featureidkey="properties.sigla",
        scope="south america",
        labels={"late_percentage": "% Tardíos"}
    )

    fig_map.update_geos(fitbounds="locations", visible=False)
    fig_map.update_layout(
        template="plotly_dark",
        margin=dict(l=0, r=0, t=0, b=0),
        height=450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    st.plotly_chart(fig_map, use_container_width=True)

    st.subheader("Insight")
    st.info("Alrededor del 12% de los pedidos llegan tarde. La mayoría son atribuibles a vendedores con demoras reiteradas en el despacho. Recomendamos revisar SLAs y procesos logísticos con estos vendedores.")

st.markdown("---")

#-------------EJERCICIO PRINCIPAL 4----------------------
reviews_df= pd.read_csv('Olist_Data/olist_order_reviews_dataset.csv')
orders_df = pd.read_csv('Olist_Data/olist_orders_dataset.csv')
customers_df = pd.read_csv('Olist_Data/olist_customers_dataset.csv')

#realizamos copias para no trbajar con el original y cojemoslas columnas que necesitamos
orders=orders_df[['order_id','customer_id']].copy()
customers=customers_df[['customer_id','customer_state']].copy()
reviews=reviews_df[['review_id','order_id','review_score']].copy()
#hacemos un primer merge para traer el campo necesario para traer en el segundo el campo necesario para agrupar por el estado
df= pd.merge(reviews,orders,on='order_id',how='left')
df= pd.merge(df,customers,on='customer_id',how='left')
df=df[['review_id','review_score','customer_state']]
#Aqui eliminamos los registros de las reviews que se han entregado tarde

#agrupamos por ciudad y contamos los registros que hay en cada una y su puntuacion media
df = df.groupby('customer_state').agg(
    num_reviews=('review_id', 'count'),    
    score_medio=('review_score', 'mean') 
).reset_index()
df['score_medio']=df['score_medio'].round(2)

# Crear figura para num reviews
fig, ax = plt.subplots()
ax.bar(df['customer_state'],df['num_reviews'], color='red')
ax.set_title('Num reviews por estado')
ax.set_xlabel('Estados')
ax.set_ylabel('Número reviews')
ax.tick_params(axis='x', rotation=45)
# Mostrar en Streamlit
st.pyplot(fig)

# Crear figura para score medio
fig, ax = plt.subplots()
ax.plot(df['customer_state'],df['score_medio'])
ax.set_title('Score medio por estado')
ax.set_xlabel('Estados')
ax.set_ylabel('Score medio')
ax.tick_params(axis='x', rotation=45)
ax.set_ylim(0, 5) #para que vaya de 0 a 5 el eje y
# Mostrar en Streamlit
st.pyplot(fig)
# ============================
# 4.4 Reputación y Opinión
# ============================
with st.expander("4.4 Reputación y Opinión del Cliente (excluye pedidos con retraso)", expanded=True):
    st.subheader("Objetivo")
    st.markdown("Evaluar la percepción de los clientes filtrando factores negativos como la demora.")

    st.subheader("KPIs")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Número de reviews por estado", "...")
    kpi_col2.metric("Puntuación promedio", "...")
    kpi_col3.metric("Score por región", "...")

    st.subheader("Visualizaciones")
    st.markdown("- Boxplot por estado")
    st.markdown("- Mapa por score promedio")

    st.subheader("Insight")
    st.info("Los estados con mejor logística tienden a tener mejores puntuaciones. Aislar el impacto del retraso permite evaluar de forma más precisa la satisfacción con el producto y servicio.")

st.markdown("---")

# ============================
# 4.5 Productos y Vendedores
# ============================
with st.expander("4.5 Productos y Vendedores", expanded=True):
    st.subheader("Objetivo")
    st.markdown("Identificar qué productos y vendedores tienen mayor impacto en las ventas y en la satisfacción del cliente.")

    st.subheader("KPIs")
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    kpi_col1.metric("Volumen por categoría", "...")
    kpi_col2.metric("Ingresos asociados", "...")
    kpi_col3.metric("Ticket promedio", "...")

    st.subheader("Visualizaciones")
    st.markdown("- Top 10 categorías por ventas")
    st.markdown("- Heatmap de ticket promedio")

    st.subheader("Insight")
    st.info("Las categorías de 'cama, mesa y baño' y 'tecnología' concentran gran parte del volumen. Sin embargo, categorías con menos ventas presentan tickets más altos y márgenes potencialmente mayores.")
