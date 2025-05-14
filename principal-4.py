import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st


# --- Preprocesamiento ---
orders_4 = orders[['order_id', 'customer_id']].copy()
customers_4 = customers[['customer_id', 'customer_state']].copy()
reviews_4 = reviews[['review_id', 'order_id', 'review_score']].copy()

df_4 = pd.merge(reviews_4, orders_4, on='order_id', how='left')
df_4 = pd.merge(df_4, customers_4, on='customer_id', how='left')

# Filtrar reviews de pedidos entregados a tiempo
df_customer_orders_4 = pd.merge(orders, customers, on='customer_id')
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

# --- Filtros interactivos ---
st.markdown("## 🔍 Filtros interactivos")

estados_4 = df_4['customer_state'].unique()
estados_seleccionados = st.multiselect(
    'Selecciona los estados que quieres visualizar:',
    options=sorted(estados),
    default=sorted(estados)
)

# Filtro por rango de número de reviews (mínimo y máximo)
min_val = int(df_4['num_reviews'].min())
max_val = int(df_4['num_reviews'].max())

rango_reviews = st.slider(
    'Selecciona el rango de número de reviews:',
    min_value=min_val,
    max_value=max_val,
    value=(min_val, max_val)
)

# Aplicar filtros
df_filtrado = df[
    (df['customer_state'].isin(estados_seleccionados)) &
    (df['num_reviews'] >= rango_reviews[0]) &
    (df['num_reviews'] <= rango_reviews[1])
].sort_values(by='num_reviews', ascending=False)

# --- Gráfico 1: Número de reviews ---
st.markdown("## 📊 Número de reviews por estado")

fig1, ax1 = plt.subplots(figsize=(10, 6))
bars = ax1.bar(df_filtrado['customer_state'], df_filtrado['num_reviews'], color='cornflowerblue', edgecolor='black')
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
bars2 = ax2.bar(df_filtrado['customer_state'], df_filtrado['score_medio'], color='mediumseagreen', edgecolor='black')
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
st.dataframe(df_filtrado)

