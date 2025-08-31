# Usamos una imagen oficial de Python 3.10
FROM python:3.10-slim

# Evitamos que Python cree archivos .pyc
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Creamos y usamos el directorio de la app
WORKDIR /app

# Copiamos los archivos de dependencias
COPY requirements.txt .

# Instalamos pip y las dependencias
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copiamos todo el proyecto
COPY . .

# Exponemos el puerto que usa Flask
EXPOSE 5000

# Comando por defecto para correr la app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "Directions:app"]
