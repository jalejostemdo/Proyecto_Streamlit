import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import seaborn as sns

st.set_page_config(page_title="Informe Olist", layout="wide")

st.title("Informe Analítico - Olist")

string_columns_orders = [
    'customer_id',
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

min_date = df['order_purchase_timestamp'].min()
max_date = df['order_purchase_timestamp'].max()

start_date, end_date = st.sidebar.date_input(
    "Rango de Fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Asegurar que la fecha sea datetime64
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filtrar por fecha seleccionada
filtered_df = df[
    (df['order_purchase_timestamp'] >= start_date) &
    (df['order_purchase_timestamp'] <= end_date)
]

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
    top_states = (
        filtered_df.groupby('customer_state')['customer_unique_id']
        .nunique()
        .sort_values(ascending=False)
    )
    top_5_states = top_states.head(5)
    top_states_list = ', '.join(top_5_states.index)

    top_cities_count = (
        filtered_df[filtered_df['customer_state'].isin(top_5_states.index)]
        .groupby(['customer_state', 'customer_city'])['customer_unique_id']
        .nunique()
        .count()
    )

    primer_pedido = df.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
    primer_pedido['year_month'] = primer_pedido['order_purchase_timestamp'].dt.to_period('M')
    primer_pedido_filtrado = primer_pedido[
        (primer_pedido['order_purchase_timestamp'] >= start_date) &
        (primer_pedido['order_purchase_timestamp'] <= end_date)
    ]
    nuevos_clientes = primer_pedido_filtrado.groupby('year_month')['customer_unique_id'].count()

    kpi_col1, kpi_col2 = st.columns(2)
    kpi_col1.metric("Top 5 Estados con más Clientes", top_states_list)
    kpi_col2.metric("Clientes Nuevos", int(nuevos_clientes.sum()))

    st.subheader("Visualizaciones")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### Top 5 Estados con más Clientes")
        fig, ax = plt.subplots(figsize=(6, 4))
        top_5_states.plot(kind='bar', color='darkgreen', ax=ax)
        ax.set_title('Top 5 Estados con más Clientes')
        ax.set_xlabel('Estados')
        ax.set_ylabel('Número de Clientes')
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

    with col2:
        st.markdown("#### Clientes por Ciudad y Estado")
        city_summary_f1 = (
            filtered_df.groupby(['customer_state', 'customer_city'])['customer_unique_id']
            .nunique()
            .reset_index(name='num_clientes')
        )
        st.dataframe(city_summary_f1, height=250)

    with col3:
        st.markdown("#### Nuevos Clientes Captados por Mes")
        nuevos_df = nuevos_clientes.reset_index(name='nuevos_clientes')
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(nuevos_df['year_month'].astype(str), nuevos_df['nuevos_clientes'], marker='o', color='purple')
        ax.set_title("Evolución de Nuevos Clientes")
        ax.set_xlabel("Mes")
        ax.set_ylabel("Nuevos Clientes")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        if not nuevos_df.empty:
            mejor_mes = nuevos_df.loc[nuevos_df['nuevos_clientes'].idxmax()]
            st.markdown(f"""
            ✅ **Mes con más captación:** `{mejor_mes['year_month']}`  
            👥 **Nuevos clientes:** `{mejor_mes['nuevos_clientes']}`
            """)

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
    col1, col2 = st.columns([1.2, 1.8])

    with col1:
        # Gráfico de Top 10 Ciudades con Pedidos Tardíos
        st.caption("Pedidos Tardíos por ciudades")

        # Ordenar las ciudades por la cantidad de pedidos tardíos de mayor a menor
        top_late_orders = late_orders.sort_values(by="late_orders", ascending=False)

        # Seleccionar las columnas que queremos mostrar
        top_late_orders_display = top_late_orders[["late_orders", "late_percentage"]].copy()
        top_late_orders_display["late_percentage"] = top_late_orders_display["late_percentage"].round(2)

        # Mostrar la tabla scrolleable
        st.dataframe(top_late_orders_display, height=400)  # `height=400` hace que la tabla sea scrolleable



    with col2:
        st.caption("📊 Comparación de Pedidos Tardíos vs Totales por Ciudad")

        # Crear un DataFrame con los datos necesarios
        stacked_data = late_orders[["late_orders", "total_orders", "late_percentage", "avg_late_days"]].copy()
        stacked_data["on_time_orders"] = (
            stacked_data["total_orders"] - stacked_data["late_orders"]
        )

        # Seleccionar las ciudades con mayor cantidad de pedidos totales
        top_cities = stacked_data.sort_values(by="total_orders", ascending=False).head(10)

        # Crear el gráfico de barras apiladas
        fig, ax = plt.subplots(figsize=(8, 5))
        top_cities[["late_orders", "on_time_orders"]].plot(
            kind="bar", stacked=True, ax=ax, color=["red", "green"], alpha=0.8
        )

        # Añadir etiquetas y título
        ax.set_ylabel("Cantidad de Pedidos", fontsize=12)
        ax.set_xticklabels(top_cities.index, rotation=45, ha="right")
        ax.legend(["Pedidos Tardíos", "Pedidos a Tiempo"], fontsize=10)

        # Añadir porcentaje de pedidos tardíos como texto encima de las barras, color rojo
        for i, (city, row) in enumerate(top_cities.iterrows()):
            ax.text(
                i,
                row["late_orders"] + row["on_time_orders"],
                f"{row['late_percentage']:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10,
                color="red",
            )

        st.pyplot(fig)

    # Línea de tiempo
    col3, col4 = st.columns([1.4, 1.4])

    with col3:
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

    with col4:
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
