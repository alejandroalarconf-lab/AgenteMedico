# Agente Médico

Buscador y simulador de horas médicas en Chile. Permite buscar atención según especialidad, comuna e isapre, considerando convenios reales por isapre (incluido Fonasa) y mostrando precios como rangos referenciales.

Desarrollado en Python. Disponible en dos versiones: una de consola y una aplicación web con Streamlit.

## Archivos

- **agente_consola.py** — Versión de consola. El usuario ingresa por texto su especialidad, comuna e isapre, y elige el orden de los resultados (más cercano, más barato o balanceado). Contiene los datos base: centros médicos (comuna, coordenadas y precios por especialidad), convenios por isapre, coordenadas de comunas y rangos de días de espera. Usa geopy para calcular distancias.

- **app.py** — Aplicación web principal en Streamlit (versión ampliada). Incluye funciones como calcular_score (combina distancia, copago, días de espera y ahorro), generar_horas_disponibles, buscar_horas y comuna_mas_cercana. Usa streamlit-geolocation para detectar la ubicación del navegador, además de pandas y geopy.

- **requirements.txt** — Dependencias: streamlit, geopy, pandas, streamlit-geolocation.

## Instalación y uso

1. Crear un entorno virtual e instalar dependencias:
   pip install -r requirements.txt
   2. Ejecutar la app web:
      streamlit run app.py
      3. Ejecutar la versión de consola:
         python agente_consola.py

         ## Flujo de trabajo (GitHub Desktop + VS Code)

         1. Clonar el repositorio con GitHub Desktop.
         2. Abrirlo en VS Code desde GitHub Desktop.
         3. Editar en VS Code, guardar, y en GitHub Desktop hacer commit y push.
         4. Hacer pull antes de empezar a trabajar para traer los últimos cambios.
         
