import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import requests
import seaborn as sns

st.set_page_config(page_title="Informe Olist", layout="wide")

st.title("Informe Analítico - Olist")

st.markdown("""
Este informe interactivo presenta un análisis integral del comportamiento de los clientes y la operativa de pedidos en la plataforma de comercio electrónico **Olist**, con foco en el mercado brasileño.

A partir del procesamiento de datos históricos, se han extraído patrones relevantes que permiten:

- Identificar regiones con mayor concentración de clientes.
- Detectar y entender causas de retrasos en las entregas.
- Analizar la evolución en la adquisición de nuevos usuarios.

---

### Objetivos del análisis

- Mejorar la experiencia del cliente mediante una comprensión más profunda de su comportamiento.
- Optimizar la logística a partir del diagnóstico de puntos críticos en la cadena de entrega.
- Facilitar la toma de decisiones comerciales basadas en datos objetivos.

---

### Contenido del dashboard

- **Distribución geográfica**: análisis por estado y ciudad de la base de clientes.
- **Nuevos clientes**: evolución temporal de la captación de usuarios.
- **Retrasos logísticos**: evaluación de la puntualidad en entregas y factores asociados.
- **Validación de hipótesis**: exploración de variables que podrían influir en los retrasos.

Este informe busca ofrecer una base sólida para la toma de decisiones estratégicas en áreas como logística, marketing, atención al cliente y desarrollo comercial.
""")

st.subheader("Datos Utilizados")

st.markdown("""
Los datasets utilizados reflejan diferentes aspectos del negocio, permitiendo un análisis transversal y completo:

- **olist_customers_dataset.csv**: Información demográfica y geográfica de los clientes.
- **olist_orders_dataset.csv**: Datos generales de los pedidos, incluyendo fechas clave del proceso de compra.
- **olist_order_items_dataset.csv**: Detalle de cada ítem incluido en los pedidos (productos, vendedores y plazos de entrega).
- **olist_order_payments_dataset.csv**: Métodos de pago utilizados y número de cuotas.
- **olist_order_reviews_dataset.csv**: Valoraciones y comentarios de los clientes tras recibir los pedidos.
- **olist_products_dataset.csv**: Información de cada producto vendido, incluyendo la categoría.
- **olist_sellers_dataset.csv**: Datos geográficos de los vendedores que operan en la plataforma.

Estos datos han sido procesados, combinados y filtrados para obtener indicadores clave y construir visualizaciones que faciliten la toma de decisiones estratégicas.
""")


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
costumers = pd.read_csv('./Olist_Data/olist_customers_dataset.csv')

# Merge
df = pd.merge(orders, costumers, on='customer_id')
df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
df['order_delivered_customer_date'] = pd.to_datetime(df['order_delivered_customer_date'])
df['order_estimated_delivery_date'] = pd.to_datetime(df['order_estimated_delivery_date'])
df['year'] = df['order_purchase_timestamp'].dt.year

df_costumer_orders = pd.merge(orders, costumers, on='customer_id')
df_costumer_orders['order_purchase_timestamp'] = pd.to_datetime(df_costumer_orders['order_purchase_timestamp'])
df_costumer_orders['order_approved_at'] = pd.to_datetime(df_costumer_orders['order_approved_at'])
df_costumer_orders['order_delivered_carrier_date'] = pd.to_datetime(df_costumer_orders['order_delivered_carrier_date'])
df_costumer_orders['order_delivered_customer_date'] = pd.to_datetime(df_costumer_orders['order_delivered_customer_date'])
df_costumer_orders['order_estimated_delivery_date'] = pd.to_datetime(df_costumer_orders['order_estimated_delivery_date'])

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

    col1, col2 = st.columns([1.8, 1.2])

    with col1:
        # Crear DataFrame para el mapa
        top_states_df = top_states.reset_index()
        top_states_df.columns = ['customer_state', 'num_customers']

        # Cargar GeoJSON con estados brasileños y sus siglas
        geojson_url = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
        geojson_data = requests.get(geojson_url).json()

        # Mapa Choropleth
        fig_map = px.choropleth(
            top_states_df,
            geojson=geojson_data,
            locations="customer_state",
            color="num_customers",
            color_continuous_scale="Blues",
            featureidkey="properties.sigla",  # campo con las siglas
            scope="south america",
            labels={"num_customers": "Clientes"}
        )

        fig_map.update_geos(fitbounds="locations", visible=False)
        fig_map.update_layout(
            title="Concentración de Clientes por Estado (Brasil)",
            margin=dict(l=0, r=0, t=30, b=0),
            height=900
        )

        st.plotly_chart(fig_map, use_container_width=True)

    with col2:
        # Selector para estado (opcional o se sincroniza con clic en mapa si fuera posible)
        selected_state = st.selectbox(
            "Selecciona un estado para ver el detalle",
            options=top_states_df['customer_state'].unique(),
            index=0
        )
        st.markdown(f"#### Clientes en Ciudades de {selected_state}")
        city_summary_f1 = (
            filtered_df[filtered_df["customer_state"] == selected_state]
            .groupby('customer_city')['customer_unique_id']
            .nunique()
            .reset_index(name='num_clientes')
            .sort_values(by='num_clientes', ascending=False)
        )
        st.dataframe(city_summary_f1, height=250)

        st.markdown("#### Nuevos Clientes Captados por Mes")

        # Filtrar nuevos clientes por estado seleccionado
        clientes_en_estado = df[df['customer_state'] == selected_state]
        primer_pedido_estado = (
            clientes_en_estado.groupby('customer_unique_id')['order_purchase_timestamp']
            .min()
            .reset_index()
        )
        primer_pedido_estado['year_month'] = primer_pedido_estado['order_purchase_timestamp'].dt.to_period('M')
        primer_pedido_estado_filtrado = primer_pedido_estado[
            (primer_pedido_estado['order_purchase_timestamp'] >= start_date) &
            (primer_pedido_estado['order_purchase_timestamp'] <= end_date)
        ]
        nuevos_clientes_estado = primer_pedido_estado_filtrado.groupby('year_month')['customer_unique_id'].count()
        nuevos_df = nuevos_clientes_estado.reset_index(name='nuevos_clientes')

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.plot(nuevos_df['year_month'].astype(str), nuevos_df['nuevos_clientes'], marker='o', color='purple')
        ax.set_title(f"Nuevos Clientes en {selected_state}")
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

    # Agrupaciones y métricas
    grouped = filtered_df.groupby(['customer_state', 'customer_city'])

    city_summary = grouped.agg(
        num_clientes=('customer_unique_id', 'nunique'),
        num_pedidos=('order_id', 'nunique')
    ).reset_index()

    total_pedidos = filtered_df['order_id'].nunique()
    city_summary['porcentaje_pedidos'] = (
        city_summary['num_pedidos'] / total_pedidos * 100
    ).round(2)
    city_summary['ratio_pedidos_cliente'] = (
        city_summary['num_pedidos'] / city_summary['num_clientes']
    ).round(2)

    filtered_df['tiempo_entrega'] = (
        filtered_df['order_delivered_customer_date'] - filtered_df['order_purchase_timestamp']
    ).dt.days

    entrega_por_ciudad = (
        filtered_df.groupby(['customer_state', 'customer_city'])['tiempo_entrega']
        .mean()
        .reset_index(name='entrega_prom_dias')
    )

    city_summary = pd.merge(city_summary, entrega_por_ciudad, on=['customer_state', 'customer_city'], how='left')

    # KPIs
    total_pedidos_ciudades = city_summary['num_pedidos'].sum()
    kpi_col1, kpi_col2 = st.columns(2)
    kpi_col1.metric("Total pedidos", f"{total_pedidos_ciudades}")
    kpi_col2.metric("Ratio pedidos por cliente (prom)", f"{city_summary['ratio_pedidos_cliente'].mean():.2f}")

    st.subheader("Visualizaciones")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Top 10 Ciudades con Más Pedidos")
        top_pedidos = city_summary.sort_values('num_pedidos', ascending=False).head(10)
        top_pedidos['label'] = top_pedidos['customer_city'] + ' (' + top_pedidos['customer_state'] + ')'
        fig1, ax1 = plt.subplots(figsize=(8, 5))
        ax1.bar(top_pedidos['label'], top_pedidos['num_pedidos'], color='dodgerblue')
        ax1.set_title("Top 10 Ciudades con Más Pedidos")
        ax1.set_xlabel("Ciudad (Estado)")
        ax1.set_ylabel("Número de Pedidos")
        ax1.tick_params(axis='x', rotation=45)
        st.pyplot(fig1)

        st.markdown("#### Top 10 Ciudades con Entrega más Rápida")
        top_fast = city_summary.sort_values('entrega_prom_dias').head(10)
        top_fast['label'] = top_fast['customer_city'] + ' (' + top_fast['customer_state'] + ')'
        fig2, ax2 = plt.subplots(figsize=(8, 5))
        ax2.bar(top_fast['label'], top_fast['entrega_prom_dias'], color='seagreen')
        ax2.set_title("Duración Promedio de Entrega por Ciudad")
        ax2.set_xlabel("Ciudad (Estado)")
        ax2.set_ylabel("Días Promedio de Entrega")
        ax2.tick_params(axis='x', rotation=45)
        st.pyplot(fig2)

    with col2:
        st.markdown("#### Top 10 Ciudades con Mayor Ratio de Pedidos por Cliente")
        top_ratios = city_summary.sort_values('ratio_pedidos_cliente', ascending=False).head(10)
        top_ratios['label'] = top_ratios['customer_city'] + ' (' + top_ratios['customer_state'] + ')'
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(top_ratios['label'], top_ratios['ratio_pedidos_cliente'], color='crimson')
        ax.set_title("Ratio Medio de Pedidos por Cliente por Ciudad")
        ax.set_xlabel("Ciudad (Estado)")
        ax.set_ylabel("Ratio de Pedidos por Cliente")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        st.markdown("#### Tabla con Métricas Clave por Ciudad")
        st.dataframe(city_summary)

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
    kpi_col1, kpi_col2 = st.columns(2)
    kpi_col1.metric("% Pedidos con retraso", f"{avg_late_percent:.1f}%")
    kpi_col2.metric("Días promedio de retraso", f"{avg_late_days:.1f}")

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
        top_cities = stacked_data.sort_values(by="total_orders", ascending=False).head(10).reset_index()

        # Crear el gráfico con Seaborn
        fig, ax = plt.subplots(figsize=(10, 6))
        top_cities_melted = top_cities.melt(
            id_vars="customer_city",
            value_vars=["late_orders", "on_time_orders"],
            var_name="Tipo de Pedido",
            value_name="Cantidad"
        )

        sns.barplot(
            data=top_cities_melted,
            x="Cantidad",
            y="customer_city",
            hue="Tipo de Pedido",
            palette={"late_orders": "red", "on_time_orders": "green"},
            ax=ax
        )

        # Añadir etiquetas y título
        ax.set_title("Comparación de Pedidos Tardíos vs Totales por Ciudad", fontsize=14)
        ax.set_xlabel("Cantidad de Pedidos", fontsize=12)
        ax.set_ylabel("Ciudad", fontsize=12)
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(handles, ["Pedidos Tardíos", "Pedidos a Tiempo"], title="Tipo de Pedido", fontsize=10)

        # Añadir porcentaje de pedidos tardíos como texto al lado de las barras
        for i, row in top_cities.iterrows():
            ax.text(
            row["total_orders"] + 5,  # Ajustar posición del texto
            i,
            f"{row['late_percentage']:.1f}%",
            va="center",
            fontsize=10,
            color="red"
            )

        st.pyplot(fig)

    # Línea de tiempo
    col3, col4 = st.columns([1.2, 1.8])

    with col3:
        st.caption("Evolución de Pedidos Tardíos a lo Largo del Tiempo")
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
        # Agrupar los datos por estado y calcular la cantidad de pedidos tardíos
        late_orders_by_state = (
            df_costumer_orders[
                df_costumer_orders["order_delivered_customer_date"]
                > df_costumer_orders["order_estimated_delivery_date"]
            ]
            .groupby("customer_state")
            .size()
            .rename("late_orders")
            .to_frame()
        )

        late_orders_by_state["late_percentage"] = (
            late_orders_by_state["late_orders"] / late_orders_by_state["late_orders"].sum()
        ) * 100
        # Filtrar los estados con porcentaje mayor al 2%
        filtered_late_orders_by_state = late_orders_by_state[late_orders_by_state["late_percentage"] > pie_threshold]

        # Crear gráfico de pastel con Plotly
        fig_pie = px.pie(
            filtered_late_orders_by_state,
            names=filtered_late_orders_by_state.index,
            values="late_percentage",
            title="Distribución de Pedidos Tardíos por Estado",
            color=filtered_late_orders_by_state.index,
            color_discrete_sequence=px.colors.sequential.Plasma  # Puedes cambiar el color según tus preferencias
        )

        # Mostrar el gráfico de pastel en Streamlit
        st.plotly_chart(fig_pie, use_container_width=True)
    


    st.subheader("Análisis de Causas Potenciales")

    st.markdown("Exploramos distintas hipótesis para entender las causas más frecuentes detrás de los pedidos entregados con retraso.")

    tabs = st.tabs(["Tiempo de Despacho", "Categoría del Producto", "Vendedores", "Tipo de Pago"])

    # TAB 1 - Tiempo de despacho
    df_costumer_orders["dispatch_time"] = (
        df_costumer_orders["order_approved_at"] - df_costumer_orders["order_purchase_timestamp"]
    ).dt.total_seconds() / 3600  # Convertir a horas

    # Separar los pedidos en entregados a tiempo y entregados tarde
    on_time_orders = df_costumer_orders[
        df_costumer_orders["order_delivered_customer_date"]
        <= df_costumer_orders["order_estimated_delivery_date"]
    ]
    late_orders = df_costumer_orders[
        df_costumer_orders["order_delivered_customer_date"]
        > df_costumer_orders["order_estimated_delivery_date"]
    ]

    # Calcular el tiempo promedio de despacho para cada grupo
    avg_dispatch_time_on_time = on_time_orders["dispatch_time"].mean()
    avg_dispatch_time_late = late_orders["dispatch_time"].mean()
    with tabs[0]:
        st.markdown("¿Los pedidos tardíos se deben a que los vendedores tardan más en despacharlos?")
        despacho_df = pd.DataFrame({
        "Tipo de Pedido": ["A Tiempo", "Tardío"],
        "Tiempo Promedio de Despacho (horas)": [10.10, 12.31]
        })
        fig1 = px.bar(
        despacho_df,
        x="Tipo de Pedido",
        y="Tiempo Promedio de Despacho (horas)",
        color="Tipo de Pedido",
        color_discrete_map={"A Tiempo": "green", "Tardío": "red"},
        text="Tiempo Promedio de Despacho (horas)"
        )
        fig1.update_layout(title="Comparación del Tiempo de Despacho")
        st.plotly_chart(fig1, use_container_width=True)

    # TAB 2 - Categoría del producto
    # Cargar el dataset de items de pedido
    order_items = pd.read_csv('./Olist_Data/olist_order_items_dataset.csv')

    # Cargar el dataset de productos
    products = pd.read_csv('./Olist_Data/olist_products_dataset.csv')

    # Combinar los datos de items de pedido con los productos
    df_items_with_products = pd.merge(
        order_items,
        products,
        on='product_id',  # Relacionar por la columna 'product_id'
        how='inner'
    )

    # Combinar los datos de items con los pedidos
    df_orders_with_items_products = pd.merge(
        df_costumer_orders,
        df_items_with_products,
        on='order_id',  # Relacionar por la columna 'order_id'
        how='inner'
    )

    # Filtrar los pedidos tardíos
    late_orders_with_products = df_orders_with_items_products[
        df_orders_with_items_products["order_delivered_customer_date"]
        > df_orders_with_items_products["order_estimated_delivery_date"]
    ]

    # Calcular el porcentaje de pedidos tardíos por categoría de producto
    late_percentage_by_category = (
        late_orders_with_products.groupby("product_category_name").size()
        / df_orders_with_items_products.groupby("product_category_name").size()
    ) * 100

    # Ordenar por porcentaje de pedidos tardíos
    late_percentage_by_category = late_percentage_by_category.sort_values(ascending=False)

    with tabs[1]:
        st.markdown("¿Algunas categorías de productos tienen más retrasos que otras?")
        cat_df = pd.DataFrame({
        "Categoría": [
            "casa_conforto_2", "moveis_colchao_e_estofado", "audio",
            "fashion_underwear_e_moda_praia", "artigos_de_natal"
        ],
        "Promedio Horas de Despacho": [
            16.67, 13.16, 12.64, 12.21, 11.76
        ]
        })

        fig2 = px.bar(
        cat_df.sort_values("Promedio Horas de Despacho", ascending=False),
        x="Promedio Horas de Despacho",
        y="Categoría",
        orientation="h",
        color="Promedio Horas de Despacho",
        color_continuous_scale="viridis"
        )
        fig2.update_layout(title="Categorías con Mayor Tiempo de Despacho en Pedidos Tardíos")
        st.plotly_chart(fig2, use_container_width=True)

    # TAB 3 - Vendedores con más retrasos
    # Calcular el número de pedidos tardíos por vendedor
    late_orders_by_seller = (
        late_orders_with_products.groupby("seller_id").size().rename("late_orders").to_frame()
    )

    # Calcular el número total de pedidos por vendedor
    total_orders_by_seller = (
        df_orders_with_items_products.groupby("seller_id").size().rename("total_orders").to_frame()
    )

    # Combinar los datos de pedidos tardíos y totales
    seller_analysis = late_orders_by_seller.join(total_orders_by_seller, how="inner")

    # Calcular el porcentaje de pedidos tardíos por vendedor
    seller_analysis["late_percentage"] = (seller_analysis["late_orders"] / seller_analysis["total_orders"]) * 100

    # Ordenar por porcentaje de pedidos tardíos
    seller_analysis = seller_analysis.sort_values(by="late_percentage", ascending=False)

    # Mostrar los resultados
    seller_analysis
    with tabs[2]:
        st.markdown("¿Existen vendedores con alta proporción de retrasos?")
        top_sellers = seller_analysis.head(10).reset_index()

        fig3 = px.bar(
        top_sellers,
        x="late_percentage",
        y="seller_id",
        orientation="h",
        text="late_percentage",
        labels={"late_percentage": "% Pedidos Tardíos", "seller_id": "Vendedor"},
        color="late_percentage",
        color_continuous_scale="Reds"
        )
        fig3.update_layout(title="Top 10 Vendedores con Mayor % de Pedidos Tardíos")
        st.plotly_chart(fig3, use_container_width=True)

    # TAB 4 - Método de pago
    with tabs[3]:
        st.markdown("¿El método de pago influye en los retrasos? (Poca evidencia, pero se analiza)")
        payment_df = pd.DataFrame({
        "Método de Pago": ["boleto", "credit_card", "debit_card", "voucher"],
        "% Pedidos Tardíos": [8.61, 7.72, 7.72, 6.44]
        })
        fig4 = px.bar(
        payment_df.sort_values("% Pedidos Tardíos", ascending=False),
        x="% Pedidos Tardíos",
        y="Método de Pago",
        orientation="h",
        color="% Pedidos Tardíos",
        color_continuous_scale="Blues"
        )
        fig4.update_layout(title="% Pedidos Tardíos por Método de Pago")
        st.plotly_chart(fig4, use_container_width=True)


    st.subheader("Insight")
    st.info("""
    El análisis revela que la principal causa de retrasos en las entregas está asociada a demoras en el despacho por parte de los vendedores.  
    En promedio, los pedidos entregados a tiempo fueron despachados 2.2 horas antes que los que se entregaron con retraso.
   """)
        
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

    # --- Carga de datos ---
    reviews = pd.read_csv('Olist_Data/olist_order_reviews_dataset.csv')
    # --- Preprocesamiento ---
    orders_4 = orders[['order_id', 'customer_id']].copy()
    customers_4 = costumers[['customer_id', 'customer_state']].copy()
    reviews_4 = reviews[['review_id', 'order_id', 'review_score']].copy()

    df_4 = pd.merge(reviews_4, orders_4, on='order_id', how='left')
    df_4 = pd.merge(df_4, customers_4, on='customer_id', how='left')

    # Filtrar reviews de pedidos entregados a tiempo
    df_customer_orders_4 = pd.merge(orders, costumers, on='customer_id')
    df_customer_orders_4 = df_customer_orders_4[['order_delivered_customer_date', 'order_estimated_delivery_date', 'order_id']]
    df_customer_orders_4['order_delivered_customer_date'] = pd.to_datetime(df_customer_orders_4['order_delivered_customer_date'])
    df_customer_orders_4['order_estimated_delivery_date'] = pd.to_datetime(df_customer_orders_4['order_estimated_delivery_date'])
    df_customer_orders_4['is_late'] = df_customer_orders_4['order_delivered_customer_date'] > df_customer_orders_4['order_estimated_delivery_date']
    df_4 = pd.merge(df_4, df_customer_orders_4, on='order_id', how='left')
    df_4 = df_4[df_4["is_late"] == False]

    # Agrupar por estado
    df_4 = df_4[['review_id', 'review_score', 'customer_state']]
    df_4 = df_4.groupby('customer_state').agg(
        num_reviews=('review_id', 'count'),
        score_medio=('review_score', 'mean')
    ).reset_index()
    df_4['score_medio'] = df_4['score_medio'].round(2)
    df_4 = df_4.sort_values(by='num_reviews', ascending=False)


    # --- Gráfico 1: Número de reviews ---
st.markdown("## 📊 Número de reviews por estado")

fig1, ax1 = plt.subplots(figsize=(10, 6))
bars = ax1.bar(df_4['customer_state'], df_4['num_reviews'], color='cornflowerblue', edgecolor='black')
ax1.set_title('Número de reviews por estado', fontsize=14)
ax1.set_xlabel('Estado', fontsize=12)
ax1.set_ylabel('Número de reviews', fontsize=12)
ax1.tick_params(axis='x', rotation=45)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width() / 2, height + 5, f'{height}', ha='center', va='bottom', fontsize=8)
st.pyplot(fig1)

# --- Gráfico 2: Score medio ---
st.markdown("## ⭐️ Score medio por estado")

fig2, ax2 = plt.subplots(figsize=(10, 6))
bars2 = ax2.bar(df_4['customer_state'], df_4['score_medio'], color='mediumseagreen', edgecolor='black')
ax2.set_title('Puntuación media de reviews por estado', fontsize=14)
ax2.set_xlabel('Estado', fontsize=12)
ax2.set_ylabel('Score medio', fontsize=12)
ax2.set_ylim(0, 5)
ax2.tick_params(axis='x', rotation=45)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
for bar in bars2:
    height = bar.get_height()
    ax2.text(bar.get_x() + bar.get_width() / 2, height + 0.05, f'{height:.2f}', ha='center', va='bottom', fontsize=8)
st.pyplot(fig2)

# --- Tabla final ---
st.markdown("## 🧾 Tabla de reviews y puntuación media por estado")
st.dataframe(df_4)
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

    # Carga de datos
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
        labels=labels_5,
        autopct='%1.1f%%',
        startangle=90,
        colors =colors_5,
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

