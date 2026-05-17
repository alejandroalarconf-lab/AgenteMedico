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
# CONVENIOS ISAPRE
# ============================================================================

CONVENIOS = {
    "banmédica": ["Clínica Bupa Santiago", "Clínica Dávila Recoleta", "Clínica Santa María", "Clínica MEDS", "Clínica Indisa"],
    "consalud": ["Clínica Dávila Recoleta", "Integramédica", "RedSalud"],
    "colmena": ["UC Christus", "Integramédica", "RedSalud", "Clínica Indisa"],
    "vida tres": ["Clínica Bupa Santiago", "Clínica Santa María", "Clínica MEDS"],
}

# ============================================================================
# COMUNAS
# ============================================================================

COMUNAS_USUARIO = {
    "providencia": (-33.437, -70.650),
    "las condes": (-33.400, -70.565),
    "santiago centro": (-33.440, -70.650),
    "la florida": (-33.535, -70.590),
    "vitacura": (-33.393, -70.590),
    "recoleta": (-33.415, -70.640),
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
COMUNAS = list(COMUNAS_USUARIO.keys())

# ============================================================================
# FUNCIONES
# ============================================================================

def formatear_precio(valor):
    return f"${valor:,.0f}".replace(",", ".")

def buscar_horas(especialidad, comuna, isapre, criterio):
    coord_usuario = COMUNAS_USUARIO[comuna]
    clinicas_isapre = CONVENIOS.get(isapre, [])
    resultados = []

    for centro in CENTROS_MEDICOS:
        if especialidad not in centro["precios"]:
            continue
            
        distancia_km = geodesic(coord_usuario, centro["coordenadas"]).kilometers
        precio_base = centro["precios"][especialidad]
        tiene_convenio = centro["nombre"] in clinicas_isapre
        
        if tiene_convenio:
            copago = int(precio_base * 0.25)
            etiqueta_convenio = "✅ Con convenio"
        else:
            copago = int(precio_base * 0.70)
            etiqueta_convenio = "❌ Sin convenio"

        min_dias, max_dias = DIAS_ESPERA[especialidad]
        dias_espera = random.randint(min_dias, max_dias)

        resultados.append({
            "nombre": centro["nombre"],
            "distancia_km": distancia_km,
            "copago": copago,
            "precio_base": precio_base,
            "dias_espera": dias_espera,
            "convenio": etiqueta_convenio,
            "url_reserva": centro.get("url_reserva", "#"),
        })

    if criterio == "Más cercano primero":
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"]))
    elif criterio == "Más barato primero":
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1)))
    else:
        resultados.sort(key=lambda x: (x["distancia_km"] * 0.4) + (x["copago"] / 10000) + (x["dias_espera"] * 0.2))

    return resultados[:4]

# ============================================================================
# INTERFAZ
# ============================================================================

st.title("🏥 Buscador de Horas Médicas - Chile")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)

with col1:
    especialidad = st.selectbox("📋 Especialidad", ESPECIALIDADES)
with col2:
    comuna = st.selectbox("📍 Comuna", COMUNAS)
with col3:
    isapre = st.selectbox("🏦 Isapre", ISAPRES)
with col4:
    criterio = st.selectbox("📊 Ordenar por", ["Más cercano primero", "Más barato primero", "Balanceado"])

st.markdown("---")
buscar = st.button("🔍 Buscar hora médica", use_container_width=True)

if buscar:
    with st.spinner("Buscando..."):
        resultados = buscar_horas(especialidad, comuna, isapre, criterio)
    
    if not resultados:
        st.warning("No encontramos clínicas con esta especialidad.")
    else:
        st.subheader(f"Resultados para {especialidad.title()}")
        
        cols = st.columns(2)
        for i, res in enumerate(resultados):
            with cols[i % 2]:
                with st.container(border=True):
                    st.markdown(f"**{i+1}. {res['nombre']}**")
                    st.write(f"📍 {res['distancia_km']:.1f} km")
                    st.write(f"💰 Copago: {formatear_precio(res['copago'])}")
                    st.write(f"⏱️ Espera: {res['dias_espera']} días")
                    st.write(f"🤝 {res['convenio']}")
                    if "✅" in res['convenio']:
                        st.success("¡Con convenio!")
                    else:
                        st.warning("Sin convenio")

st.markdown("---")
st.caption("Buscador de horas médicas - Prototipo Chile")