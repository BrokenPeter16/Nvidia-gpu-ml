# Capa base del sistema operativo con Python
FROM python:3.10-slim

# Directorio de trabajo interno del contenedor
WORKDIR /app

# Copia de dependencias e instalación
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia del código fuente
COPY . .

# Exposición de los puertos para API y Streamlit
EXPOSE 8000 8501