import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

st.title("Análisis de Clientes de Olist")

df_customers = pd.read_csv('Olist_Data/olist_customers_dataset.csv')
df_orders = pd.read_csv('Olist_Data/olist_orders_dataset.csv')

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
# Cambiar el tipo de datos de las columnas de fecha a datetime
df_orders[date_columns] = df_orders[date_columns].apply(pd.to_datetime)
# Cambiar el tipo de datos de las columnas a striing
df_orders[string_columns_orders] = df_orders[string_columns_orders].astype(str)
df_customers[string_columns_customers] = df_customers[string_columns_customers].astype(str)

# Si falta el valor de order_approved_at, se asume que el pedido fue aprobado en el momento 
# de la compra
df_orders["order_approved_at"].fillna(df_orders["order_purchase_timestamp"], inplace=True)
# Si falta el valor de order_delivered_carrier_date, se asume que el pedido fue enviado 
# un día después de la aprobación
df_orders['order_delivered_carrier_date'].fillna(
    df_orders['order_approved_at'] + pd.Timedelta(1), inplace=True
)

merged_df = pd.merge(df_orders, df_customers, on='customer_id', how='inner')

pedidos_por_ciudad = (
    merged_df.groupby(['customer_state', 'customer_city'])['order_id']
    .nunique()
    .reset_index(name='num_pedidos')
)

top_states = (
    merged_df.groupby('customer_state')['customer_id']
    .nunique()
    .sort_values(ascending=False)
)

city_summary_f1 = (
  merged_df.groupby(['customer_state', 'customer_city'])['customer_id']
    .nunique()
    .reset_index(name='num_clientes')
)

top_5_states = top_states.head(5)

# Mostrar gráfico en Streamlit
st.subheader("Top 5 Estados con más Clientes")
fig, ax = plt.subplots(figsize=(10, 6))
top_5_states.plot(kind='bar', color='skyblue', ax=ax)
ax.set_title('Top 5 Estados con más Clientes')
ax.set_xlabel('Estados')
ax.set_ylabel('Número de Clientes')
ax.tick_params(axis='x', rotation=45)
st.pyplot(fig)

st.subheader("Resumen de Clientes por Ciudad y Estado")
st.dataframe(city_summary_f1)

city_summary_f2 = pd.merge(city_summary_f1, pedidos_por_ciudad, on=['customer_state', 'customer_city'])

total_pedidos = merged_df['order_id'].nunique()
city_summary_f2['porcentaje_pedidos'] = (
    city_summary_f2['num_pedidos'] / total_pedidos * 100
).round(2)

city_summary_f2['ratio_pedidos_clientes'] = (
    city_summary_f2['num_pedidos'] / city_summary_f2['num_clientes']
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
