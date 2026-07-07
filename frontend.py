import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="Nvidia Pricing Engine", page_icon="💻", layout="centered")

st.title("Motor Predictivo de Mercado de GPUs")
st.markdown("Plataforma analítica para predecir el valor de mercado de unidades gráficas mediante Regresión Lineal Múltiple.")

st.divider()
st.subheader("Análisis Histórico: Top Ventas Globales")

# URL de tu API (Asegúrate de cambiar esto por tu enlace de Ngrok si pruebas desde otro dispositivo)
# Ejemplo: API_URL = "https://unflawed-murmuring-skincare.ngrok-free.dev/api/v1/prediccion-precio"
API_URL = "http://127.0.0.1:8000/api/v1/prediccion-precio"
URL_TOP_VENTAS = "http://127.0.0.1:8000/api/v1/ventas/top"


with st.form("formulario_prediccion"):
    st.subheader("Especificaciones del Hardware")
    
    col1, col2 = st.columns(2)
    with col1:
        gpu_model = st.selectbox("Modelo de GPU", ['RTX 4090', 'RTX 4080', 'RTX 5090', 'H100', 'A100', 'B200'])
        region = st.selectbox("Región Comercial", ['North America', 'EMEA', 'LATAM', 'APAC'])
    with col2:
        customer_segment = st.selectbox("Segmento de Cliente", ['Gaming', 'AI Research', 'Hyperscale Datacenter', 'Content Creation'])
        launch_year = st.number_input("Año de Lanzamiento", min_value=2020, max_value=2030, value=2025)
        
    warranty_months = st.slider("Meses de Garantía", min_value=12, max_value=60, value=24, step=12)
    
    boton_predecir = st.form_submit_button("Calcular Valor de Mercado", type="primary")


if boton_predecir:
    payload = {
        "gpu_model": gpu_model,
        "region": region,
        "customer_segment": customer_segment,
        "launch_year": launch_year,
        "warranty_months": warranty_months
    }
    
    with st.spinner('Analizando pesos algorítmicos en la nube...'):
        try:
            respuesta = requests.post(API_URL, json=payload)
            if respuesta.status_code == 200:
                datos = respuesta.json()
                precio = datos["precio_sugerido_usd"]
                st.success("Cálculo completado exitosamente.")
                st.metric(label="Precio Sugerido (USD)", value=f"${precio:,.2f}")
            else:
                st.error(f"Fallo en la validación: {respuesta.text}")
        except requests.exceptions.ConnectionError:
            st.error("ccNo se pudo conectar con el motor Backend.")



try:
    respuesta_top = requests.get(URL_TOP_VENTAS)
    if respuesta_top.status_code == 200:
        datos_historicos = respuesta_top.json()["datos"]
        
# Transformación a DataFrame
        df_top = pd.DataFrame(datos_historicos)
        
        # Renombrar columnas para formato de interfaz gráfica
        df_top = df_top.rename(columns={
            "gpu_model": "Modelo de Tarjeta",
            "revenue_usd": "Ingresos Totales (USD)"
        })
        
        # Renderizado de gráfico de barras actualizado
        st.bar_chart(
            data=df_top, 
            x="Modelo de Tarjeta", 
            y="Ingresos Totales (USD)",
            use_container_width=True
        )
    else:
        st.warning("El motor de datos históricos no respondió a tiempo.")
except requests.exceptions.ConnectionError:
    st.error("No se pudo establecer el puente de red con el endpoint de métricas.")