import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

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
ax.plot(df['num_reviews'] ,df['customer_state'])
ax.set_title('Num reviews por estado')
ax.set_xlabel('Estados')
ax.set_ylabel('Número reviews')
# Mostrar en Streamlit
st.pyplot(fig)

# Crear figura para num reviews
fig, ax = plt.subplots()
ax.plot(df['score_medio'] ,df['customer_state'])
ax.set_title('Score medio por estado')
ax.set_xlabel('Estados')
ax.set_ylabel('Score medio')
# Mostrar en Streamlit
st.pyplot(fig)