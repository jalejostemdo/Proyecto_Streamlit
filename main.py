import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

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

df_orders[date_columns] = df_orders[date_columns].apply(pd.to_datetime)
df_orders[string_columns_orders] = df_orders[string_columns_orders].astype(str)
df_customers[string_columns_customers] = df_customers[string_columns_customers].astype(str)

# Rellenar fechas nulas
df_orders["order_approved_at"].fillna(df_orders["order_purchase_timestamp"], inplace=True)
df_orders['order_delivered_carrier_date'].fillna(
    df_orders['order_approved_at'] + pd.Timedelta(1), inplace=True
)

# Merge datasets
merged_df = pd.merge(df_orders, df_customers, on='customer_id', how='inner')

# ---------------- FILTRO DE FECHAS ----------------
st.sidebar.header("Filtrar por Fecha de Compra")
min_date = merged_df['order_purchase_timestamp'].min()
max_date = merged_df['order_purchase_timestamp'].max()

start_date, end_date = st.sidebar.date_input(
    "Rango de Fechas",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Filtrar datos
filtered_df = merged_df[
    (merged_df['order_purchase_timestamp'] >= start_date) &
    (merged_df['order_purchase_timestamp'] <= end_date)
]

# ---------------- ANÁLISIS Y GRÁFICOS USANDO filtered_df ----------------

# Agrupar por ciudad y estado
grouped = filtered_df.groupby(['customer_state', 'customer_city'])

city_summary = grouped.agg(
    num_clientes=('customer_unique_id', 'nunique'),
    num_pedidos=('order_id', 'nunique')
).reset_index()

# Calcular métricas adicionales
total_pedidos = filtered_df['order_id'].nunique()
city_summary['porcentaje_pedidos'] = (
    city_summary['num_pedidos'] / total_pedidos * 100
).round(2)
city_summary['ratio_pedidos_cliente'] = (
    city_summary['num_pedidos'] / city_summary['num_clientes']
).round(2)

# Mostrar tabla
st.subheader("Resumen de Clientes y Pedidos por Ciudad y Estado")
st.dataframe(city_summary)

# Gráfico: top 10 por ratio
st.subheader("Top 10 Ciudades con Mayor Ratio de Pedidos por Cliente")
top_ratios = city_summary.sort_values('ratio_pedidos_cliente', ascending=False).head(10)
top_ratios['label'] = top_ratios['customer_city'] + ' (' + top_ratios['customer_state'] + ')'

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(top_ratios['label'], top_ratios['ratio_pedidos_cliente'], color='red')
ax.set_title("Ratio Medio de Pedidos por Cliente por Ciudad")
ax.set_xlabel("Ciudad (Estado)")
ax.set_ylabel("Ratio de Pedidos por Cliente")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)
