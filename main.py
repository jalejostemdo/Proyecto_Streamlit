import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("Análisis de Clientes de Olist")

df_customers = pd.read_csv('Olist_Data/olist_customers_dataset.csv')
df_orders = pd.read_csv('Olist_Data/olist_orders_dataset.csv')

merged_df = pd.merge(df_orders, df_customers, on='customer_id', how='inner')

pedidos_por_ciudad = (
    merged_df.groupby(['customer_state', 'customer_city'])['order_id']
    .nunique()
    .sort_values(ascending=False)
    .reset_index(name='num_pedidos')
)

top_states = (
    merged_df.groupby('customer_state')['customer_id']
    .nunique()
    .sort_values(ascending=False)
)

top_5_states = top_states.head(5)

city_summary_f1 = (
    merged_df.groupby(['customer_state', 'customer_city'])['customer_id']
    .nunique()
    .reset_index(name='num_clientes')
)

st.dataframe(city_summary_f1)

city_summary_f2 = pd.merge(city_summary_f1, pedidos_por_ciudad, on=['customer_state', 'customer_city'])

total_pedidos = merged_df['order_id'].nunique()
city_summary_f2['porcentaje_pedidos'] = (
    city_summary_f2['num_pedidos'] / total_pedidos * 100
).round(2)

# Feature 2
st.subheader("Resumen de Clientes y Pedidos por Ciudad y Estado")
st.dataframe(city_summary_f2)

st.subheader("Top 10 Ciudades con Mayor Ratio de Pedidos por Cliente")
top_ratios = city_summary_f2.sort_values(
    'ratio_pedidos_clientes', ascending=False
).head(10)
top_ratios['label'] = (
    top_ratios['customer_city'] + ' (' +
    top_ratios['customer_state'] + ')'
)

fig, ax = plt.subplots(figsize=(12, 6))
ax.bar(top_ratios['label'], top_ratios['ratio_pedidos_clientes'], color='red')
ax.set_title("Ratio Medio de Pedidos por Cliente por Ciudad")
ax.set_xlabel("Ciudad (Estado)")
ax.set_ylabel("Ratio de Pedidos por Cliente")
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)