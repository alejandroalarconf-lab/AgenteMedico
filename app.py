import streamlit as st
import random
from geopy.distance import geodesic

st.set_page_config(page_title="Buscador de Horas Médicas - Chile", page_icon="🏥", layout="wide")

# ============================================================================
# DATOS DE CENTROS MÉDICOS
# ============================================================================

CENTROS_MEDICOS = [
    {
        "nombre": "Clínica Bupa Santiago",
        "comuna": "La Florida",
        "coordenadas": (-33.5330, -70.5950),
        "url_reserva": "https://www.clinicabupasantiago.cl/mi-bupa",
        "precios": {
            "medicina general": 45000, "traumatología": 70000, "cardiología": 75000,
            "dermatología": 85000, "pediatría": 55000, "ginecología": 65000,
        },
    },
    {
        "nombre": "Clínica Dávila Recoleta",
        "comuna": "Recoleta",
        "coordenadas": (-33.4150, -70.6400),
        "url_reserva": "https://www.davila.cl/reserva-online",
        "precios": {
            "medicina general": 40000, "pediatría": 50000, "oftalmología": 65000,
            "neurología": 80000, "psiquiatría": 90000, "kinesiología": 30000,
        },
    },
    {
        "nombre": "Clínica Santa María",
        "comuna": "Providencia",
        "coordenadas": (-33.4260, -70.6230),
        "url_reserva": "https://www.clinicasantamaria.cl/reserva-online",
        "precios": {
            "medicina general": 50000, "dermatología": 90000, "ginecología": 75000,
            "cardiología": 85000, "oftalmología": 70000, "traumatología": 80000,
        },
    },
    {
        "nombre": "Clínica MEDS",
        "comuna": "Las Condes",
        "coordenadas": (-33.3850, -70.5450),
        "url_reserva": "https://www.meds.cl/reserva-hora",
        "precios": {
            "traumatología": 75000, "kinesiología": 35000, "nutrición": 50000,
            "cardiología": 80000, "dermatología": 85000, "psicología": 50000,
        },
    },
    {
        "nombre": "Integramédica",
        "comuna": "Santiago Centro",
        "coordenadas": (-33.4520, -70.6480),
        "url_reserva": "https://www.integramedica.cl/reserva-hora",
        "precios": {
            "medicina general": 35000, "oftalmología": 55000, "pediatría": 45000,
            "psiquiatría": 80000, "dermatología": 75000, "urología": 65000,
        },
    },
    {
        "nombre": "RedSalud",
        "comuna": "Providencia",
        "coordenadas": (-33.4330, -70.6150),
        "url_reserva": "https://www.redsalud.cl/reserva-horas",
        "precios": {
            "medicina general": 38000, "traumatología": 68000, "pediatría": 48000,
            "ginecología": 62000, "cardiología": 72000, "kinesiología": 32000,
        },
    },
    {
        "nombre": "UC Christus",
        "comuna": "Santiago Centro",
        "coordenadas": (-33.4410, -70.6400),
        "url_reserva": "https://www.ucchristus.cl/reserva-hora",
        "precios": {
            "medicina general": 45000, "gastroenterología": 80000, "endocrinología": 75000,
            "otorrino": 70000, "urología": 75000, "pediatría": 52000,
        },
    },
    {
        "nombre": "Clínica Indisa",
        "comuna": "Providencia",
        "coordenadas": (-33.4250, -70.6200),
        "url_reserva": "https://www.indisa.cl/reserva-hora",
        "precios": {
            "medicina general": 42000, "pediatría": 52000, "traumatología": 72000,
            "dermatología": 80000, "neurología": 82000, "psiquiatría": 88000,
        },
    },
]

# ============================================================================
# CONVENIOS POR ISAPRE (incluye Fonasa)
# ============================================================================

CONVENIOS = {
    "banmédica": ["Clínica Bupa Santiago", "Clínica Dávila Recoleta", "Clínica Santa María", "Clínica MEDS", "Clínica Indisa"],
    "consalud": ["Clínica Dávila Recoleta", "Integramédica", "RedSalud"],
    "colmena": ["UC Christus", "Integramédica", "RedSalud", "Clínica Indisa"],
    "vida tres": ["Clínica Bupa Santiago", "Clínica Santa María", "Clínica MEDS"],
    "nueva masvida": ["RedSalud", "Integramédica", "Clínica Indisa", "Clínica Dávila Recoleta"],
    "esencial": ["Integramédica", "RedSalud"],
    "fonasa": [],
}

# ============================================================================
# COMUNAS DISPONIBLES (todas las que tienen clínicas)
# ============================================================================

TODAS_COMUNAS = {
    "providencia": (-33.437, -70.650),
    "las condes": (-33.400, -70.565),
    "santiago centro": (-33.440, -70.650),
    "la florida": (-33.535, -70.590),
    "vitacura": (-33.393, -70.590),
    "recoleta": (-33.415, -70.640),
    "maipú": (-33.510, -70.755),
    "ñuñoa": (-33.457, -70.600),
}

# ============================================================================
# DÍAS DE ESPERA POR ESPECIALIDAD
# ============================================================================

DIAS_ESPERA = {
    "medicina general": (1, 5),
    "dermatología": (15, 45),
    "psiquiatría": (20, 60),
    "traumatología": (2, 10),
    "ginecología": (3, 12),
    "oftalmología": (7, 20),
    "cardiología": (5, 15),
    "pediatría": (1, 7),
    "neurología": (10, 30),
    "nutrición": (3, 10),
    "kinesiología": (1, 5),
    "urología": (5, 15),
}

ESPECIALIDADES = list(DIAS_ESPERA.keys())
ISAPRES = list(CONVENIOS.keys())
LISTA_COMUNAS = list(TODAS_COMUNAS.keys())

# ============================================================================
# FUNCIONES
# ============================================================================

def formatear_precio(valor):
    return f"${valor:,.0f}".replace(",", ".")

def buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio):
    """
    Busca horas médicas considerando múltiples comunas de origen.
    Para cada clínica, calcula la distancia a la comuna más cercana de las seleccionadas.
    """
    clinicas_isapre = CONVENIOS.get(isapre, [])
    es_fonasa = (isapre == "fonasa")
    
    # Diccionario para almacenar el mejor resultado de cada clínica
    mejores_por_clinica = {}
    
    for centro in CENTROS_MEDICOS:
        if especialidad not in centro["precios"]:
            continue
        
        nombre_centro = centro["nombre"]
        precio_base = centro["precios"][especialidad]
        tiene_convenio = nombre_centro in clinicas_isapre
        
        # Calcular la distancia a la comuna más cercana de las seleccionadas
        distancia_minima = float('inf')
        comuna_mas_cercana = None
        
        for comuna in comunas_seleccionadas:
            coord_comuna = TODAS_COMUNAS.get(comuna)
            if coord_comuna:
                distancia = geodesic(coord_comuna, centro["coordenadas"]).kilometers
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    comuna_mas_cercana = comuna
        
        # Si no se encontró ninguna comuna válida, saltar
        if distancia_minima == float('inf'):
            continue
        
        # Reglas de copago según Isapre/Fonasa
        if es_fonasa:
            copago = precio_base
            etiqueta_convenio = "🏥 Fonasa (particular)"
        elif tiene_convenio:
            copago = int(precio_base * 0.25)
            etiqueta_convenio = "✅ Con convenio"
        else:
            copago = int(precio_base * 0.70)
            etiqueta_convenio = "❌ Sin convenio"
        
        # Días de espera
        min_dias, max_dias = DIAS_ESPERA[especialidad]
        if es_fonasa:
            dias_espera = random.randint(min_dias * 2, max_dias * 2)
        else:
            dias_espera = random.randint(min_dias, max_dias)
        
        mejores_por_clinica[nombre_centro] = {
            "nombre": nombre_centro,
            "distancia_km": distancia_minima,
            "comuna_origen": comuna_mas_cercana,
            "copago": copago,
            "precio_base": precio_base,
            "dias_espera": dias_espera,
            "convenio": etiqueta_convenio,
            "url_reserva": centro.get("url_reserva", "#"),
        }
    
    # Convertir a lista y ordenar
    resultados = list(mejores_por_clinica.values())
    
    if criterio == "Más cercano primero":
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"]))
    elif criterio == "Más barato primero":
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1)))
    else:  # Balanceado
        resultados.sort(key=lambda x: (x["distancia_km"] * 0.4) + (x["copago"] / 10000) + (x["dias_espera"] * 0.2))
    
    return resultados[:6]  # Mostrar hasta 6 resultados

# ============================================================================
# INTERFAZ WEB
# ============================================================================

st.title("🏥 Buscador de Horas Médicas - Chile")
st.markdown("---")

# Fila 1: Especialidad e Isapre
col1, col2 = st.columns(2)
with col1:
    especialidad = st.selectbox("📋 Especialidad", ESPECIALIDADES)
with col2:
    isapre = st.selectbox("🏦 Isapre / Fonasa", ISAPRES)

st.markdown("---")

# Fila 2: Selección de comunas (múltiple)
st.subheader("📍 ¿Dónde buscas?")
st.caption("Puedes seleccionar entre 1 y 3 comunas. El sistema usará la más cercana a cada clínica.")

comunas_seleccionadas = st.multiselect(
    "Selecciona comunas (máximo 3):",
    options=LISTA_COMUNAS,
    default=["providencia"],
    max_selections=3
)

# Validar que haya al menos una comuna
if not comunas_seleccionadas:
    st.warning("⚠️ Debes seleccionar al menos una comuna.")
    st.stop()

# Fila 3: Criterio de orden
st.markdown("---")
criterio = st.selectbox("📊 Ordenar por", ["Más cercano primero", "Más barato primero", "Balanceado"])

# Botón de búsqueda
st.markdown("---")
buscar = st.button("🔍 Buscar hora médica", use_container_width=True)

# ============================================================================
# RESULTADOS
# ============================================================================

if buscar:
    with st.spinner("Buscando en todas las comunas seleccionadas..."):
        resultados = buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio)
    
    if not resultados:
        st.warning("No encontramos clínicas con esta especialidad en las comunas seleccionadas.")
    else:
        # Mostrar resumen de la búsqueda
        st.markdown("---")
        st.subheader(f"📋 Resultados para {especialidad.title()}")
        st.caption(f"Buscando en: {', '.join([c.title() for c in comunas_seleccionadas])} | Isapre: {isapre.title()} | Orden: {criterio}")
        
        # Mostrar resultados en 2 columnas
        cols = st.columns(2)
        for i, res in enumerate(resultados):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{i+1}. {res['nombre']}**")
                    st.write(f"📍 Desde {res['comuna_origen'].title()}: **{res['distancia_km']:.1f} km**")
                    st.write(f"💰 Copago: **{formatear_precio(res['copago'])}**")
                    st.write(f"⏱️ Espera: **{res['dias_espera']} días**")
                    st.write(f"🏥 Precio base: {formatear_precio(res['precio_base'])}")
                    st.write(f"🤝 {res['convenio']}")
                    
                    if "Con convenio" in res['convenio']:
                        st.success("🎉 ¡Tienes convenio aquí!")
                    elif "Sin convenio" in res['convenio']:
                        st.warning("⚠️ Sin convenio - copago más alto")
                    else:
                        st.info("🏥 Tarifa particular (Fonasa)")
        
        # Mostrar ubicación de los centros en un mapa
        st.markdown("---")
        st.subheader("🗺️ Ubicación de los centros médicos")
        
        map_data = []
        for res in resultados[:6]:
            for centro in CENTROS_MEDICOS:
                if centro["nombre"] == res["nombre"]:
                    map_data.append({
                        "lat": centro["coordenadas"][0],
                        "lon": centro["coordenadas"][1],
                        "nombre": centro["nombre"]
                    })
        
        if map_data:
            import pandas as pd
            df = pd.DataFrame(map_data)
            st.map(df, latitude="lat", longitude="lon")

st.markdown("---")
st.caption("Buscador de horas médicas - Puedes seleccionar hasta 3 comunas | Prototipo Chile")