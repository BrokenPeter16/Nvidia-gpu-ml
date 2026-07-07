import pandas as pd
import kagglehub
import os
from sqlalchemy import create_engine
from dotenv import load_dotenv

# Cargar variables seguras
load_dotenv()
URI_NUBE = os.getenv("SUPABASE_URI")


path = kagglehub.dataset_download("uditjain13/nvidia-gpu-sales-synthetic-2026")
archivos_csv = [f for f in os.listdir(path) if f.endswith('.csv')]
df_gpu = pd.read_csv(os.path.join(path, archivos_csv[0]))


df_gpu = df_gpu.drop_duplicates()
df_gpu['sale_date'] = pd.to_datetime(df_gpu['sale_date'], errors='coerce')

if 'customer_satisfaction_score' in df_gpu.columns:
    mediana_satisfaccion = df_gpu['customer_satisfaction_score'].median()
    df_gpu['customer_satisfaction_score'] = df_gpu['customer_satisfaction_score'].fillna(mediana_satisfaccion)

columnas_criticas = ['gpu_model', 'revenue_usd', 'sale_date']
df_gpu = df_gpu.dropna(subset=columnas_criticas)


print("Estableciendo conexión")
motor_sql = create_engine(URI_NUBE)

# La inyección a red toma unos segundos más que localmente debido a la latencia
df_gpu.to_sql('ventas', con=motor_sql, if_exists='replace', index=False)

print("Datos consolidados en PostgreSQL")