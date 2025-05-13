# 📊 Proyecto de equipo: Creamos un dashboard interactivo

## 🚀 ¿Qué vamos a hacer?

Durante los próximos días, vamos a trabajar juntos siendo parte de un equipo de DATA. Nuestro objetivo es **crear un dashboard interactivo con Streamlit** que nos permita explorar y compartir la visualizacion de la información de un conjunto de datos real para nuestro cliente.

Para ello vamos a utilizar tres librerias principales:

- **Pandas** para transformar los datos.
- **Seaborn** para crear visualizaciones.
- **Streamlit** para construir la app interactiva.

---

## 📦 El conjunto de datos

Vamos a usar los datos de la empresa **Olist**, una tienda online brasileña. Este dataset contiene más de 100.000 registros sobre ventas, clientes, entregas, productos, métodos de pago y más ( CSV ubicado en los recursos del tema ).

Está dividido en varias tablas, y parte del reto será decidir cuáles usar y cómo combinarlas.

---

## 🧠 ¿Qué podemos analizar?

Una parte clave del proyecto será **explorar el conjunto de datos y decidir qué métricas o insights son útiles**. Algunas ideas que os damos:

### 📌 Lista de tareas principales

1. **Representa** una clasificación del nº de clientes por estado (Si consideras que hay demasiados estados representa el top 5). Paso siguiente crea una tabla donde se representen los estados, las ciudades que pertenecen a esos estados y el numero de clientes en esas ciudades. Ademas de eso, la tabla y todos los graficos representados deberan de ser dinamicos respecto a la fecha   

2. **Añade** a la tabla anterior dos columnas (nº pedidos y el porcentaje respecto al total de pedidos), y el ratio del numero de pedido medio por cliente, representa la información en el grafico que consideres oportuno ¿Que te transmite esta informacion? ¿Que acciones como analista de datos crees que deberia de tomar la empresa para mejorar sus ventas? 

3. **Calcula**, el nº de pedidos que llegan tarde por ciudad, el porcentaje que representa respecto al total de pedidos por ciudad, junto con el tiempo medio de dias que se pasan de fecha, queremos que a la hora de representar esta falla salga ya autodiagnosticada con la razon mas probable del problema (Analiza el dataset)

4. **Calcula y representa** el numero de reviews por estado y el score medio en cada una de ellas, como ya hemos tenido en cuenta los pedidos con retraso en la seccion anterior vamos a eliminar estos datos del apartado de score ya que se entiende que la opinion será negativa por la tardanza de llegada del producto.

Esto seran las metricas que tendra que tener en el ejercicio calculadas y representadas como minimo, puedes añadir todas las que veas interesantes!

## 🧪 Entregables

- App funcionando en local.
- Código organizado y comentado.
- Presentación breve del trabajo (5-10 minutos por equipo).
- Readme.md donde se defina la URL asignada a la web Streamlit

--- 

## Tareas inciales

- Crear repo
- Analizar informacion -> ver que datos vamos a usar cada uno
- Limpiar/Ver nulos/Etc
- 