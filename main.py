import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("Análisis de Clientes de Olist")

df_customers = pd.read_csv('Olist_Data/olist_customers_dataset.csv')
df_orders = pd.read_csv('Olist_Data/olist_orders_dataset.csv')

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
# Cambiar el tipo de datos de las columnas de fecha a datetime
df_orders[date_columns] = df_orders[date_columns].apply(pd.to_datetime)
# Cambiar el tipo de datos de las columnas a string
df_orders[string_columns_orders] = df_orders[string_columns_orders].applymap(str)
df_customers[string_columns_customers] = df_customers[string_columns_customers].applymap(str)


# Si falta el valor de order_approved_at, se asume que el pedido fue aprobado en el momento 
# de la compra
df_orders["order_approved_at"].fillna(df_orders["order_purchase_timestamp"], inplace=True)
# Si falta el valor de order_delivered_carrier_date, se asume que el pedido fue enviado 
# un día después de la aprobación
df_orders['order_delivered_carrier_date'].fillna(
    df_orders['order_approved_at'] + pd.Timedelta(1), inplace=True
)

merged_df = pd.merge(df_orders, df_customers, on='customer_id', how='inner')


# ---------------- FILTRO DE FECHAS ----------------
st.sidebar.header("Filtrar por Fecha")
min_date = merged_df['order_purchase_timestamp'].min()
max_date = merged_df['order_purchase_timestamp'].max()

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
filtered_df = merged_df[
    (merged_df['order_purchase_timestamp'] >= start_date) &
    (merged_df['order_purchase_timestamp'] <= end_date)
]

# ---------------- GRÁFICO ----------------
top_states = (
    filtered_df.groupby('customer_state')['customer_unique_id']
    .nunique()
    .sort_values(ascending=False)
)
top_5_states = top_states.head(5)

st.subheader("Top 5 Estados con más Clientes")
fig, ax = plt.subplots(figsize=(10, 6))
top_5_states.plot(kind='bar', color='darkgreen', ax=ax)
ax.set_title('Top 5 Estados con más Clientes')
ax.set_xlabel('Estados')
ax.set_ylabel('Número de Clientes')
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# ---------------- TABLA ----------------
st.subheader("Clientes por Ciudad y Estado")
city_summary_f1 = (
    filtered_df.groupby(['customer_state', 'customer_city'])['customer_unique_id']
    .nunique()
    .reset_index(name='num_clientes')
)

st.dataframe(city_summary_f1)

# ---------------- NUEVOS CLIENTES POR MES ----------------

# Obtener la primera compra de cada cliente único
primer_pedido = merged_df.groupby('customer_unique_id')['order_purchase_timestamp'].min().reset_index()
primer_pedido['year_month'] = primer_pedido['order_purchase_timestamp'].dt.to_period('M')

# Aplicar el filtro de fechas del usuario
primer_pedido_filtrado = primer_pedido[
    (primer_pedido['order_purchase_timestamp'] >= start_date) &
    (primer_pedido['order_purchase_timestamp'] <= end_date)
]

# Agrupar por mes y contar cuántos clientes hicieron su primera compra
nuevos_clientes = (
    primer_pedido_filtrado
    .groupby('year_month')['customer_unique_id']
    .count()
    .reset_index(name='nuevos_clientes')
)

# Visualizar la evolución
st.subheader("Nuevos Clientes Captados por Mes")
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(nuevos_clientes['year_month'].astype(str), nuevos_clientes['nuevos_clientes'], marker='o', color='purple')
ax.set_title("Evolución de Nuevos Clientes")
ax.set_xlabel("Mes")
ax.set_ylabel("Nuevos Clientes")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

# Destacar el mes con mayor captación
if not nuevos_clientes.empty:
    mejor_mes = nuevos_clientes.loc[nuevos_clientes['nuevos_clientes'].idxmax()]
    st.markdown(f"""
    ✅ **Mes con más captación:** `{mejor_mes['year_month']}`  
    👥 **Nuevos clientes:** `{mejor_mes['nuevos_clientes']}`
    """)

