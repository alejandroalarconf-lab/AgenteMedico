import streamlit as st
import random
from geopy.distance import geodesic
from datetime import datetime, timedelta
import pandas as pd

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Buscador de Horas Médicas - Chile",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CONSTANTES DE CONFIGURACIÓN
# ============================================================================

MAX_RESULTADOS = 6
MAX_COMUNAS = 3
DIAS_ESPERA_POR_DEFECTO = (7, 21)
PORCENTAJE_CONVENIO = 0.25
PORCENTAJE_SIN_CONVENIO = 0.70
FACTOR_DISTANCIA = 0.4
FACTOR_COPAGO = 0.0001
FACTOR_ESPERA = 0.2

# ============================================================================
# SESSION STATE
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = random.randint(1000, 9999)
if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "busqueda_activa" not in st.session_state:
    st.session_state.busqueda_activa = False
if "ultima_busqueda" not in st.session_state:
    st.session_state.ultima_busqueda = {}

# ============================================================================
# CSS LIGERO (solo para colores y fuentes, sin HTML complejo)
# ============================================================================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo suave */
    .stApp {
        background: #f5f7fa;
    }
    
    /* Botón principal */
    .stButton > button {
        background: #003366 !important;
        color: white !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        border: none !important;
        transition: all 0.2s ease !important;
    }
    .stButton > button:hover {
        background: #002244 !important;
        box-shadow: 0 4px 12px rgba(0,51,102,0.25) !important;
    }
    
    /* Títulos */
    h1, h2, h3, h4, h5 {
        color: #003366 !important;
    }
    
    /* Métricas */
    .stMetric {
        background: white;
        padding: 8px;
        border-radius: 12px;
        border: 1px solid #e0e7ed;
    }
    .stMetric label {
        color: #6B8CAE !important;
    }
    
    /* Contenedores de resultados */
    .stContainer {
        background: white;
        border-radius: 16px;
        padding: 10px;
        margin-bottom: 10px;
        transition: box-shadow 0.2s ease;
    }
    .stContainer:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
    }
    
    /* Badges y colores */
    .success-text {
        color: #1A6B3C;
        font-weight: 500;
    }
    .warning-text {
        color: #854F0B;
        font-weight: 500;
    }
    .info-text {
        color: #0C447C;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ENCABEZADO (sin HTML complejo)
# ============================================================================

st.title("🏥 Buscador de Horas Médicas - Chile")
st.caption("🇨🇱 Región Metropolitana · Compara precios con tu Isapre o Fonasa")
st.markdown("---")

# ============================================================================
# DATOS DE CENTROS MÉDICOS (23 centros)
# ============================================================================

CENTROS_MEDICOS = [
    {"nombre": "Clínica Alemana", "comuna": "Vitacura", "coordenadas": (-33.3940, -70.5940), "url_reserva": "https://portal.clinicaalemana.cl/reserva-horas/identificacion", "precios": {"medicina general": 50000, "pediatría": 58000, "traumatología": 98000, "cardiología": 88000, "dermatología": 90000, "ginecología": 75000}},
    {"nombre": "UC Christus", "comuna": "Santiago Centro", "coordenadas": (-33.4410, -70.6400), "url_reserva": "https://reserva.ucchristus.cl", "precios": {"medicina general": 45000, "pediatría": 52000, "traumatología": 88000, "cardiología": 78000, "dermatología": 80000, "ginecología": 68000, "laboratorio": 25000, "imagenes": 45000}},
    {"nombre": "RedSalud Vitacura", "comuna": "Vitacura", "coordenadas": (-33.3900, -70.5800), "url_reserva": "https://www.redsalud.cl/reserva-de-horas", "precios": {"medicina general": 38000, "pediatría": 48000, "traumatología": 68000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000, "dental": 35000, "laboratorio": 20000}},
    {"nombre": "RedSalud Providencia", "comuna": "Providencia", "coordenadas": (-33.4330, -70.6150), "url_reserva": "https://www.redsalud.cl/reserva-de-horas", "precios": {"medicina general": 38000, "pediatría": 48000, "traumatología": 68000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000}},
    {"nombre": "RedSalud La Florida", "comuna": "La Florida", "coordenadas": (-33.5350, -70.5900), "url_reserva": "https://www.redsalud.cl/reserva-de-horas", "precios": {"medicina general": 37000, "pediatría": 47000, "traumatología": 67000, "cardiología": 71000, "dermatología": 74000, "ginecología": 61000}},
    {"nombre": "IntegraMédica Alameda", "comuna": "Santiago Centro", "coordenadas": (-33.4520, -70.6480), "url_reserva": "https://agendamiento.integramedica.cl", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 60000, "cardiología": 65000, "dermatología": 70000, "ginecología": 55000, "dental": 30000, "oftalmología": 50000}},
    {"nombre": "IntegraMédica Ñuñoa", "comuna": "Ñuñoa", "coordenadas": (-33.4570, -70.6000), "url_reserva": "https://agendamiento.integramedica.cl", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 60000, "cardiología": 65000, "dermatología": 70000, "ginecología": 55000}},
    {"nombre": "IntegraMédica Providencia", "comuna": "Providencia", "coordenadas": (-33.4370, -70.6450), "url_reserva": "https://agendamiento.integramedica.cl", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 60000, "cardiología": 65000, "dermatología": 70000, "ginecología": 55000}},
    {"nombre": "IntegraMédica Las Condes", "comuna": "Las Condes", "coordenadas": (-33.4000, -70.5650), "url_reserva": "https://agendamiento.integramedica.cl", "precios": {"medicina general": 36000, "pediatría": 46000, "traumatología": 61000, "cardiología": 66000, "dermatología": 71000, "ginecología": 56000}},
    {"nombre": "IntegraMédica Maipú", "comuna": "Maipú", "coordenadas": (-33.5100, -70.7550), "url_reserva": "https://agendamiento.integramedica.cl", "precios": {"medicina general": 34000, "pediatría": 44000, "traumatología": 59000, "cardiología": 64000, "dermatología": 69000, "ginecología": 54000}},
    {"nombre": "IntegraMédica La Florida", "comuna": "La Florida", "coordenadas": (-33.5350, -70.5900), "url_reserva": "https://agendamiento.integramedica.cl", "precios": {"medicina general": 34000, "pediatría": 44000, "traumatología": 59000, "cardiología": 64000, "dermatología": 69000, "ginecología": 54000}},
    {"nombre": "Clínica INDISA", "comuna": "Providencia", "coordenadas": (-33.4250, -70.6200), "url_reserva": "https://reserva.indisa.cl/WebReservaHoras", "precios": {"medicina general": 42000, "pediatría": 52000, "traumatología": 72000, "cardiología": 75000, "dermatología": 80000, "ginecología": 65000, "maternidad": 120000, "examenes": 30000}},
    {"nombre": "Clínica Las Condes", "comuna": "Las Condes", "coordenadas": (-33.4100, -70.5720), "url_reserva": "https://mivision.clinicalascondes.cl/ReservaHoras", "precios": {"medicina general": 48000, "pediatría": 55000, "traumatología": 95000, "cardiología": 85000, "dermatología": 88000, "ginecología": 72000}},
    {"nombre": "Clínica Bupa Santiago", "comuna": "La Florida", "coordenadas": (-33.5330, -70.5950), "url_reserva": "https://agendamiento.clinicabupasantiago.cl", "precios": {"medicina general": 45000, "pediatría": 55000, "traumatología": 70000, "cardiología": 75000, "dermatología": 85000, "ginecología": 65000, "cirugia": 100000, "maternidad": 90000}},
    {"nombre": "Clínica U. de los Andes", "comuna": "Las Condes", "coordenadas": (-33.3850, -70.5450), "url_reserva": "https://reserva.clinicauandes.cl", "precios": {"medicina general": 50000, "pediatría": 60000, "traumatología": 90000, "cardiología": 85000, "dermatología": 88000, "ginecología": 72000}},
    {"nombre": "Hospital del Profesor", "comuna": "Estación Central", "coordenadas": (-33.4700, -70.7000), "url_reserva": "https://reserva.chp.cl", "precios": {"medicina general": 40000, "pediatría": 50000, "traumatología": 70000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000, "kinesiología": 30000, "imagenes": 40000}},
    {"nombre": "Clini - Providencia", "comuna": "Providencia", "coordenadas": (-33.4350, -70.6350), "url_reserva": "https://reserva.clini.cl", "precios": {"medicina general": 35000, "cardiología": 65000, "laboratorio": 20000, "imagenes": 35000, "examenes": 25000}},
    {"nombre": "Clini - La Florida", "comuna": "La Florida", "coordenadas": (-33.5300, -70.5850), "url_reserva": "https://reserva.clini.cl", "precios": {"medicina general": 35000, "cardiología": 65000, "laboratorio": 20000, "imagenes": 35000, "examenes": 25000}},
    {"nombre": "Clínica Santa María", "comuna": "Providencia", "coordenadas": (-33.4260, -70.6230), "url_reserva": "https://www.clinicasantamaria.cl/reserva-online", "precios": {"medicina general": 50000, "pediatría": 55000, "traumatología": 80000, "cardiología": 85000, "dermatología": 90000, "ginecología": 75000}},
    {"nombre": "Clínica Dávila Recoleta", "comuna": "Recoleta", "coordenadas": (-33.4150, -70.6400), "url_reserva": "https://www.davila.cl/reserva-online", "precios": {"medicina general": 40000, "pediatría": 50000, "traumatología": 68000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000}},
    {"nombre": "Clínica MEDS", "comuna": "Las Condes", "coordenadas": (-33.3850, -70.5450), "url_reserva": "https://www.meds.cl/reserva-hora", "precios": {"medicina general": 50000, "pediatría": 60000, "traumatología": 75000, "cardiología": 80000, "dermatología": 85000, "ginecología": 70000}},
]

# ============================================================================
# CONVENIOS POR ISAPRE
# ============================================================================

CONVENIOS = {
    "banmédica": ["Clínica Alemana", "Clínica Las Condes", "Clínica Bupa Santiago", "Clínica Santa María", "Clínica INDISA", "Clínica Dávila Recoleta", "Clínica MEDS", "Clínica U. de los Andes"],
    "consalud": ["RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "IntegraMédica Las Condes", "IntegraMédica Maipú", "IntegraMédica La Florida", "Clínica Dávila Recoleta"],
    "colmena": ["UC Christus", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "Clínica INDISA"],
    "vida tres": ["Clínica Bupa Santiago", "Clínica Santa María", "Clínica Alemana", "Clínica Las Condes"],
    "nueva masvida": ["RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "IntegraMédica Alameda", "Clínica INDISA"],
    "esencial": ["IntegraMédica Alameda", "IntegraMédica Ñuñoa", "RedSalud Providencia"],
    "fonasa": [],
}

# ============================================================================
# COMUNAS
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
    "estacion central": (-33.470, -70.700),
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
    "laboratorio": (1, 3),
    "imagenes": (2, 5),
    "dental": (2, 7),
    "examenes": (1, 4),
}

# ============================================================================
# MÉDICOS POR ESPECIALIDAD
# ============================================================================

MEDICOS_POR_ESPECIALIDAD = {
    "medicina general": ["Dr. Juan Pablo Silva", "Dra. María Fernanda López", "Dr. Carlos Alberto Rojas"],
    "traumatología": ["Dr. Cristián Labbé", "Dra. Macarena Valdés", "Dr. Sebastián Herrera"],
    "cardiología": ["Dr. Jorge Bartolucci", "Dra. Pamela Serón", "Dr. Ramón Corbalán"],
    "dermatología": ["Dra. Claudia Aranís", "Dr. Sergio González", "Dra. Jimena Schnettler"],
    "pediatría": ["Dra. Marcela Bahamondes", "Dr. Tomás Alliende", "Dra. Andrea Oyarzún"],
    "ginecología": ["Dra. Paulina Vega", "Dr. Juan Enrique Montero", "Dra. Soledad Díaz"],
    "oftalmología": ["Dr. Rodrigo Galdames", "Dra. Andrea Lutz", "Dr. Gonzalo Rojas"],
    "neurología": ["Dr. Pedro Chaná", "Dra. Paulina Orellana", "Dr. Claudio Hetz"],
    "psiquiatría": ["Dr. Claudio Fuenzalida", "Dra. María Elena Gorostiza", "Dr. Pablo López-Silva"],
    "nutrición": ["Dra. Vivianne Sotomayor", "Dr. Rodrigo Aránguiz", "Dra. Javiera Torres"],
    "kinesiología": ["Kine. Felipe González", "Kine. Valentina Méndez", "Kine. Cristóbal Jiménez"],
    "urología": ["Dr. Mauricio Hoyl", "Dr. Pedro Bórquez", "Dr. José Miguel Rojas"],
    "laboratorio": ["Tec. María José López", "Tec. Cristián Soto", "Tec. Daniela Muñoz"],
    "imagenes": ["Tec. Rodrigo Acuña", "Dra. Carla Espinoza", "Tec. Paulo Díaz"],
    "dental": ["Dra. Carolina Ortiz", "Dr. Sebastián Lara", "Dra. María Jesús Valdés"],
    "examenes": ["Tec. Pamela Rojas", "Tec. Cristóbal Fuentes", "Dra. Valentina Pérez"],
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def formatear_precio(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")

def generar_horas_disponibles(dias_espera: int, especialidad: str) -> list:
    horarios = ["08:30","09:00","09:30","10:00","10:30","11:00","11:30",
                "12:00","12:30","14:00","14:30","15:00","15:30",
                "16:00","16:30","17:00","17:30","18:00","18:30"]
    fecha_base = datetime.now() + timedelta(days=dias_espera)
    medicos = MEDICOS_POR_ESPECIALIDAD.get(especialidad, ["Dr. Médico General"])
    num_opciones = random.randint(1, 3)
    opciones = []
    for _ in range(num_opciones):
        dias_offset = random.randint(0, 2)
        fecha_opcion = fecha_base + timedelta(days=dias_offset)
        opciones.append({
            "fecha": fecha_opcion.strftime("%d/%m/%Y"),
            "hora": random.choice(horarios),
            "medico": random.choice(medicos),
        })
    opciones.sort(key=lambda x: (x["fecha"], x["hora"]))
    return opciones

def dias_espera_label(dias: int) -> tuple:
    if dias <= 1:
        return "Mañana", "verde"
    elif dias <= 5:
        return f"{dias} días", "verde"
    elif dias <= 15:
        return f"{dias} días", "ambar"
    else:
        return f"{dias} días", "gris"

def buscar_horas(especialidad: str, comunas_seleccionadas: list, isapre: str, criterio: str) -> list:
    clinicas_isapre = CONVENIOS.get(isapre, [])
    es_fonasa = (isapre == "fonasa")
    mejores_por_clinica = {}

    for centro in CENTROS_MEDICOS:
        if especialidad not in centro["precios"]:
            continue
        nombre = centro["nombre"]
        precio_base = centro["precios"][especialidad]
        tiene_convenio = nombre in clinicas_isapre

        distancia_minima = float('inf')
        comuna_mas_cercana = None
        for comuna in comunas_seleccionadas:
            if comuna in TODAS_COMUNAS:
                try:
                    distancia = geodesic(TODAS_COMUNAS[comuna], centro["coordenadas"]).kilometers
                    if distancia < distancia_minima:
                        distancia_minima = distancia
                        comuna_mas_cercana = comuna
                except Exception:
                    continue
        if distancia_minima == float('inf'):
            continue

        if es_fonasa:
            copago = precio_base
            etiqueta_convenio = "fonasa"
            ahorro = 0
        elif tiene_convenio:
            copago = int(precio_base * PORCENTAJE_CONVENIO)
            etiqueta_convenio = "convenio"
            ahorro = precio_base - copago
        else:
            copago = int(precio_base * PORCENTAJE_SIN_CONVENIO)
            etiqueta_convenio = "sin_convenio"
            ahorro = 0

        min_dias, max_dias = DIAS_ESPERA.get(especialidad, DIAS_ESPERA_POR_DEFECTO)
        if es_fonasa:
            dias_espera = random.randint(min_dias * 2, max_dias * 2)
        else:
            dias_espera = random.randint(min_dias, max_dias)
        
        opciones_hora = generar_horas_disponibles(dias_espera, especialidad)

        mejores_por_clinica[nombre] = {
            "nombre": nombre,
            "distancia_km": distancia_minima,
            "comuna_origen": comuna_mas_cercana,
            "copago": copago,
            "precio_base": precio_base,
            "dias_espera": dias_espera,
            "convenio": etiqueta_convenio,
            "ahorro": ahorro,
            "url_reserva": centro.get("url_reserva", "#"),
            "opciones_hora": opciones_hora,
        }

    resultados = list(mejores_por_clinica.values())
    if criterio == "Más cercano primero":
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"]))
    elif criterio == "Más barato primero":
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1)))
    else:
        resultados.sort(key=lambda x: (
            x["distancia_km"] * FACTOR_DISTANCIA + 
            x["copago"] * FACTOR_COPAGO + 
            x["dias_espera"] * FACTOR_ESPERA
        ))
    return resultados[:MAX_RESULTADOS]

# ============================================================================
# UI - FILTROS
# ============================================================================

col1, col2 = st.columns(2)
with col1:
    especialidad = st.selectbox("📋 Especialidad", list(DIAS_ESPERA.keys()))
with col2:
    isapre = st.selectbox("🏦 Previsión de salud", list(CONVENIOS.keys()))

comunas_seleccionadas = st.multiselect(
    f"📍 ¿Desde qué comuna buscas? (máx. {MAX_COMUNAS})",
    options=list(TODAS_COMUNAS.keys()),
    default=["providencia"],
    max_selections=MAX_COMUNAS,
)

col3, col4 = st.columns([2, 1])
with col3:
    criterio = st.selectbox("📊 Ordenar por", ["Más cercano primero", "Más barato primero", "Balanceado"])
with col4:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    buscar = st.button("🔍 Buscar hora médica", use_container_width=True)

if not comunas_seleccionadas:
    st.warning("⚠️ Selecciona al menos una comuna para buscar.")
    st.stop()

# ============================================================================
# LÓGICA DE BÚSQUEDA
# ============================================================================

if buscar:
    st.session_state.busqueda_activa = True
    with st.spinner("Buscando las mejores horas disponibles..."):
        st.session_state.resultados = buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio)
        st.session_state.ultima_busqueda = {
            "especialidad": especialidad,
            "comunas": comunas_seleccionadas,
            "isapre": isapre,
            "criterio": criterio,
        }

# ============================================================================
# UI - RESULTADOS (VERSIÓN CON COMPONENTES NATIVOS)
# ============================================================================

if st.session_state.busqueda_activa and st.session_state.resultados is not None:
    resultados = st.session_state.resultados
    busqueda = st.session_state.ultima_busqueda
    es_fonasa = busqueda["isapre"] == "fonasa"

    if not resultados:
        st.warning("No encontramos clínicas con esta especialidad en las comunas seleccionadas.")
    else:
        # Hook banner
        ahorro_max = max((r["ahorro"] for r in resultados), default=0)
        if ahorro_max > 0:
            st.success(f"💡 Con tu previsión **{busqueda['isapre'].title()}** puedes ahorrar hasta **{formatear_precio(ahorro_max)}** en {busqueda['especialidad']}. Te mostramos las mejores opciones ordenadas para ti.")
        elif es_fonasa:
            st.info(f"ℹ️ Mostrando precios particulares para **Fonasa**. Los precios pueden variar según el prestador.")

        # Header
        st.markdown(f"### 📋 {busqueda['especialidad'].title()}")
        st.caption(f"{', '.join([c.title() for c in busqueda['comunas']])} · {busqueda['isapre'].title()} · {busqueda['criterio']}")
        st.markdown("---")

        # Tarjetas de resultados
        for i, res in enumerate(resultados):
            es_mejor = (i == 0)
            dias_label, _ = dias_espera_label(res["dias_espera"])

            with st.container(border=True):
                if es_mejor:
                    st.markdown("⭐ **Mejor opción para ti**")

                # Título y precio
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### {res['nombre']}")
                    st.markdown(f"📍 {res['distancia_km']:.1f} km desde **{res['comuna_origen'].title()}**")
                with col2:
                    if res["convenio"] == "convenio":
                        st.markdown(f"~~{formatear_precio(res['precio_base'])}~~")
                        st.markdown(f"### {formatear_precio(res['copago'])}")
                        st.caption("tu copago")
                    elif res["convenio"] == "fonasa":
                        st.markdown(f"### {formatear_precio(res['copago'])}")
                        st.caption("precio Fonasa")
                    else:
                        st.markdown(f"~~{formatear_precio(res['precio_base'])}~~")
                        st.markdown(f"### {formatear_precio(res['copago'])}")
                        st.caption("precio sin convenio")

                # Métricas
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric(label="Primera hora", value=dias_label)
                with col_b:
                    st.metric(label="Distancia", value=f"{res['distancia_km']:.1f} km")
                with col_c:
                    if res["ahorro"] > 0:
                        st.metric(label="Ahorras", value=formatear_precio(res["ahorro"]))
                    else:
                        st.metric(label="Ahorras", value="—")

                # Badge de convenio
                if res["convenio"] == "convenio":
                    st.success(f"✅ Con convenio {busqueda['isapre'].title()}")
                elif res["convenio"] == "fonasa":
                    st.warning("🏥 Fonasa (precio particular)")
                else:
                    st.warning(f"❌ Sin convenio {busqueda['isapre'].title()}")

                # Horas disponibles
                st.markdown("**📅 Horas disponibles**")
                if res["opciones_hora"]:
                    for o in res["opciones_hora"][:3]:
                        st.markdown(f"- 🕐 **{o['fecha']}** a las **{o['hora']}** hrs. con {o['medico']}")
                    st.caption(f"Primera hora disponible: {res['opciones_hora'][0]['fecha']} a las {res['opciones_hora'][0]['hora']} hrs.")
                else:
                    st.info("Sin horas próximas disponibles")

                # Botón de reserva
                if res["url_reserva"] != "#":
                    st.link_button(f"📅 Reservar en {res['nombre']}", res["url_reserva"], use_container_width=True)

            st.markdown("---")

        # Mapa
        if resultados:
            st.markdown("### 🗺️ Ubicación de los centros encontrados")
            map_data = []
            for res in resultados:
                for centro in CENTROS_MEDICOS:
                    if centro["nombre"] == res["nombre"]:
                        map_data.append({
                            "lat": centro["coordenadas"][0],
                            "lon": centro["coordenadas"][1],
                        })
                        break
            if map_data:
                st.map(pd.DataFrame(map_data), latitude="lat", longitude="lon")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.caption("🏥 Buscador de horas médicas · Región Metropolitana, Chile · Los precios y horarios son referenciales. La reserva se realiza en el sitio oficial de cada clínica.")