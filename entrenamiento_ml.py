import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score
import joblib
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

# Cargar credenciales
load_dotenv()
URI_NUBE = os.getenv("SUPABASE_URI")

def entrenar_modelo():
    print("Conectando a PostgreSQL en Supabase...")
    motor = create_engine(URI_NUBE)
    
    query = '''
        SELECT gpu_model, region, customer_segment, launch_year, warranty_months, avg_street_price_usd 
        FROM ventas
    '''
    df = pd.read_sql(query, motor)
    
    X = df[['gpu_model', 'region', 'customer_segment', 'launch_year', 'warranty_months']]
    y = df['avg_street_price_usd']
    
    transformador = ColumnTransformer(
        transformers=[
            ('categoricas', OneHotEncoder(drop='first', handle_unknown='ignore'), 
             ['gpu_model', 'region', 'customer_segment'])
        ],
        remainder='passthrough'
    )
    
    modelo = Pipeline(steps=[('preprocesamiento', transformador), ('algoritmo', LinearRegression())])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print("Entrenando")
    modelo.fit(X_train, y_train)
    
    precision = r2_score(y_test, modelo.predict(X_test))
    print(f"Precisión del modelo (R2): {precision:.4f}")
    
    joblib.dump(modelo, 'modelo_precios.pkl')
    print("Modelo exportado")

if __name__ == '__main__':
    entrenar_modelo()