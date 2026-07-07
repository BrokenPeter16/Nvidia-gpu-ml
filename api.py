from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import joblib
import pandas as pd

load_dotenv()
URI_NUBE = os.getenv("SUPABASE_URI")
motor_sql = create_engine(URI_NUBE)

# Configuración del Servidor
app = FastAPI(
    title="Nvidia Market Intelligence API",
    description="Motor backend con integración de Machine Learning",
    version="2.0.0"
)

try:
    # El servidor carga el archivo .pkl al arrancar, no en cada petición
    modelo_precio = joblib.load('modelo_precios.pkl')
except Exception as e:
    modelo_precio = None
    print(f"No se pudo cargar el modelo ML. {e}")

class EspecificacionesGPU(BaseModel):
    gpu_model: Literal['RTX 4090', 'RTX 4080', 'RTX 5090', 'H100', 'A100', 'B200']
    region: Literal['North America', 'EMEA', 'LATAM', 'APAC']
    customer_segment: Literal['Gaming', 'AI Research', 'Hyperscale Datacenter', 'Content Creation']
    launch_year: int = Field(ge=2020, le=2030, description="El año debe estar entre 2020 y 2030")
    warranty_months: int = Field(ge=12, le=60, description="La garantía debe ser entre 12 y 60 meses")

# --- ENDPOINTS ---

@app.get("/api/v1/ventas/top")
def obtener_top_ventas():
    # Consulta empírica agrupada
    query = '''
        SELECT gpu_model, SUM(revenue_usd) as revenue_usd 
        FROM ventas 
        GROUP BY gpu_model 
        ORDER BY revenue_usd DESC 
        LIMIT 5
    '''
    try:
        df_resultados = pd.read_sql(query, motor_sql)
        datos = df_resultados.to_dict(orient='records')
        return {"total_resultados": len(datos), "datos": datos}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error de conexión a Supabase: {str(e)}")

# NUEVO: Endpoint Predictivo
@app.post("/api/v1/prediccion-precio")
def predecir_valor_mercado(gpu: EspecificacionesGPU):
    if not modelo_precio:
        raise HTTPException(status_code=500, detail="El motor predictivo está fuera de línea.")
    
    datos_entrada = pd.DataFrame([gpu.model_dump()])
    
    try:
        precio_calculado = modelo_precio.predict(datos_entrada)[0]
        
        return {
            "estado": "Éxito",
            "parametros_analizados": gpu.model_dump(),
            "precio_sugerido_usd": round(precio_calculado, 2)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Fallo en la matriz de transformación: {str(e)}")
    
