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
# SESSION STATE — evita pérdida de resultados al reconectar
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
# CSS — PALETA INSTITUCIONAL CHILENA
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/tabler-icons.min.css');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── HERO ── */
.hero-band {
    background: #003366;
    padding: 28px 32px 22px;
    margin: -4rem -2rem 0 -2rem;
}
.hero-eyebrow {
    font-size: 11px;
    color: #85B7EB;
    letter-spacing: .08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.hero-h1 {
    font-size: 26px;
    font-weight: 600;
    color: white;
    margin-bottom: 4px;
}
.hero-sub {
    font-size: 14px;
    color: #B5D4F4;
    margin-bottom: 0;
}
.accent-bar {
    background: #D52B1E;
    height: 4px;
    margin: 0 -2rem;
}

/* ── FILTROS ── */
.filtros-wrap {
    background: white;
    padding: 20px 32px;
    border-bottom: 1px solid #D8E4F0;
    margin: 0 -2rem 2rem -2rem;
}

/* ── HOOK BANNER ── */
.hook-banner {
    background: #E6F1FB;
    border: 1px solid #85B7EB;
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 20px;
    display: flex;
    align-items: flex-start;
    gap: 10px;
}
.hook-icon { font-size: 18px; color: #185FA5; flex-shrink: 0; margin-top: 1px; }
.hook-text { font-size: 13px; color: #0C447C; line-height: 1.5; }
.hook-text strong { color: #042C53; font-weight: 600; }

/* ── CARDS ── */
.result-card {
    background: white;
    border: 1px solid #D8E4F0;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 14px;
    transition: box-shadow .2s ease;
}
.result-card:hover {
    box-shadow: 0 4px 16px rgba(0,51,102,0.1);
}
.result-card.best {
    border-top: 3px solid #003366;
    border-left: 1px solid #D8E4F0;
    border-right: 1px solid #D8E4F0;
    border-bottom: 1px solid #D8E4F0;
}

.best-label {
    display: inline-block;
    background: #003366;
    color: white;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
    letter-spacing: .02em;
}

.card-header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 14px;
}
.card-name {
    font-size: 16px;
    font-weight: 600;
    color: #003366;
    margin-bottom: 3px;
}
.card-comuna {
    font-size: 12px;
    color: #6B8CAE;
}
.price-block { text-align: right; }
.price-tachado {
    font-size: 12px;
    color: #aaa;
    text-decoration: line-through;
    margin-bottom: 1px;
}
.price-main { font-size: 22px; font-weight: 600; color: #003366; }
.price-main.fonasa { color: #D52B1E; }
.price-label { font-size: 11px; color: #6B8CAE; }

/* ── MÉTRICAS ── */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-bottom: 14px;
}
.metric-box {
    background: #F4F6F9;
    border-radius: 8px;
    padding: 9px 10px;
    text-align: center;
}
.metric-val {
    font-size: 15px;
    font-weight: 600;
    color: #003366;
    margin-bottom: 2px;
}
.metric-val.verde { color: #1A6B3C; }
.metric-val.ambar { color: #854F0B; }
.metric-val.gris  { color: #aaa; }
.metric-label { font-size: 11px; color: #6B8CAE; }

/* ── BADGES ── */
.convenio-row { margin-bottom: 12px; display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 500;
    padding: 3px 11px;
    border-radius: 20px;
}
.badge-blue   { background: #E6F1FB; color: #0C447C; }
.badge-red    { background: #FCEBEB; color: #791F1F; }
.badge-gray   { background: #F0F3F7; color: #5F7A96; }
.savings-text { font-size: 12px; font-weight: 600; color: #1A6B3C; }

/* ── SLOTS ── */
.slots-label { font-size: 12px; color: #6B8CAE; margin-bottom: 7px; }
.slots-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 14px; }
.slot-pill {
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 8px;
    border: 1px solid #85B7EB;
    color: #0C447C;
    background: #E6F1FB;
}
.slot-pill.vacio {
    border-color: #D8E4F0;
    color: #aaa;
    background: #F4F6F9;
}

/* ── BOTONES ── */
.stButton > button {
    background: #003366 !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 10px 20px !important;
    border-radius: 8px !important;
    border: none !important;
    width: 100% !important;
    transition: background .2s ease !important;
}
.stButton > button:hover {
    background: #002244 !important;
    box-shadow: 0 4px 12px rgba(0,51,102,0.25) !important;
}

.stLinkButton > a {
    background: transparent !important;
    color: #003366 !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    border: 1px solid #85B7EB !important;
    border-radius: 8px !important;
    width: 100% !important;
    display: block !important;
    text-align: center !important;
}

/* ── SELECTBOX / MULTISELECT ── */
.stSelectbox label, .stMultiSelect label {
    font-weight: 500 !important;
    color: #003366 !important;
    font-size: 13px !important;
}
.stSelectbox > div > div, .stMultiSelect > div > div {
    border-radius: 8px !important;
    border: 1px solid #D8E4F0 !important;
}

/* ── RESULTADOS HEADER ── */
.resultados-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #D8E4F0;
}
.resultados-titulo {
    font-size: 16px;
    font-weight: 600;
    color: #003366;
}
.resultados-sub { font-size: 12px; color: #6B8CAE; margin-top: 2px; }
.resultados-count {
    background: #E6F1FB;
    color: #0C447C;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 12px;
    border-radius: 20px;
}

/* ── MAPA ── */
.mapa-titulo {
    font-size: 14px;
    font-weight: 600;
    color: #003366;
    margin: 24px 0 10px;
    padding-top: 16px;
    border-top: 1px solid #D8E4F0;
}

/* ── FOOTER ── */
.footer-wrap {
    text-align: center;
    padding: 20px;
    color: #6B8CAE;
    font-size: 12px;
    border-top: 1px solid #D8E4F0;
    margin-top: 32px;
    background: white;
    margin: 32px -2rem -2rem -2rem;
}
.footer-logo {
    font-size: 13px;
    font-weight: 600;
    color: #003366;
    margin-bottom: 4px;
}

/* ── WARNING/INFO ── */
.stWarning, .stInfo { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATOS
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

CONVENIOS = {
    "banmédica": ["Clínica Alemana", "Clínica Las Condes", "Clínica Bupa Santiago", "Clínica Santa María", "Clínica INDISA", "Clínica Dávila Recoleta", "Clínica MEDS", "Clínica U. de los Andes"],
    "consalud": ["RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "IntegraMédica Las Condes", "IntegraMédica Maipú", "IntegraMédica La Florida", "Clínica Dávila Recoleta"],
    "colmena": ["UC Christus", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "Clínica INDISA"],
    "vida tres": ["Clínica Bupa Santiago", "Clínica Santa María", "Clínica Alemana", "Clínica Las Condes"],
    "nueva masvida": ["RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "IntegraMédica Alameda", "Clínica INDISA"],
    "esencial": ["IntegraMédica Alameda", "IntegraMédica Ñuñoa", "RedSalud Providencia"],
    "fonasa": [],
}

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

DIAS_ESPERA = {
    "medicina general": (1, 5), "dermatología": (15, 45), "psiquiatría": (20, 60),
    "traumatología": (2, 10), "ginecología": (3, 12), "oftalmología": (7, 20),
    "cardiología": (5, 15), "pediatría": (1, 7), "neurología": (10, 30),
    "nutrición": (3, 10), "kinesiología": (1, 5), "urología": (5, 15),
    "laboratorio": (1, 3), "imagenes": (2, 5), "dental": (2, 7), "examenes": (1, 4),
}

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
# FUNCIONES
# ============================================================================

def formatear_precio(valor):
    return f"${valor:,.0f}".replace(",", ".")

def generar_horas_disponibles(dias_espera, especialidad):
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

def buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio):
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
                d = geodesic(TODAS_COMUNAS[comuna], centro["coordenadas"]).kilometers
                if d < distancia_minima:
                    distancia_minima = d
                    comuna_mas_cercana = comuna
        if distancia_minima == float('inf'):
            continue

        if es_fonasa:
            copago = precio_base
            etiqueta_convenio = "fonasa"
            ahorro = 0
        elif tiene_convenio:
            copago = int(precio_base * 0.25)
            etiqueta_convenio = "convenio"
            ahorro = precio_base - copago
        else:
            copago = int(precio_base * 0.70)
            etiqueta_convenio = "sin_convenio"
            ahorro = 0

        min_dias, max_dias = DIAS_ESPERA.get(especialidad, (5, 15))
        dias_espera = random.randint(min_dias * 2, max_dias * 2) if es_fonasa else random.randint(min_dias, max_dias)
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
        resultados.sort(key=lambda x: (x["distancia_km"] * 0.4) + (x["copago"] / 10000) + (x["dias_espera"] * 0.2))
    return resultados[:6]

def dias_espera_label(dias):
    if dias <= 1:
        return "Mañana", "verde"
    elif dias <= 5:
        return f"{dias} días", "verde"
    elif dias <= 15:
        return f"{dias} días", "ambar"
    else:
        return f"{dias} días", "gris"

# ============================================================================
# UI — HERO
# ============================================================================

st.markdown("""
<div class="hero-band">
    <div class="hero-eyebrow">🇨🇱 Región Metropolitana · Chile</div>
    <div class="hero-h1">🏥 Buscador de horas médicas</div>
    <div class="hero-sub">Compara precios reales con tu isapre y reserva donde más te conviene</div>
</div>
<div class="accent-bar"></div>
""", unsafe_allow_html=True)

# ============================================================================
# UI — FILTROS
# ============================================================================

st.markdown("<div class='filtros-wrap'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    especialidad = st.selectbox("📋 Especialidad", list(DIAS_ESPERA.keys()))
with col2:
    isapre = st.selectbox("🏦 Previsión de salud", list(CONVENIOS.keys()))

comunas_seleccionadas = st.multiselect(
    "📍 ¿Desde qué comuna buscas? (máx. 3)",
    options=list(TODAS_COMUNAS.keys()),
    default=["providencia"],
    max_selections=3,
)

col3, col4 = st.columns([2, 1])
with col3:
    criterio = st.selectbox("📊 Ordenar por", ["Más cercano primero", "Más barato primero", "Balanceado"])
with col4:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    buscar = st.button("🔍 Buscar hora médica", use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

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
# UI — RESULTADOS
# ============================================================================

if st.session_state.busqueda_activa and st.session_state.resultados is not None:
    resultados = st.session_state.resultados
    busqueda = st.session_state.ultima_busqueda
    es_fonasa = busqueda["isapre"] == "fonasa"

    if not resultados:
        st.warning("No encontramos clínicas con esta especialidad en las comunas seleccionadas.")
    else:
        # Calcular ahorro máximo para el hook banner
        ahorro_max = max((r["ahorro"] for r in resultados), default=0)

        # Hook banner
        if ahorro_max > 0:
            st.markdown(f"""
            <div class="hook-banner">
                <span class="hook-icon">💡</span>
                <div class="hook-text">
                    Con tu previsión <strong>{busqueda['isapre'].title()}</strong> puedes ahorrar hasta
                    <strong>{formatear_precio(ahorro_max)}</strong> en {busqueda['especialidad']}.
                    Te mostramos las mejores opciones ordenadas para ti.
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif es_fonasa:
            st.markdown(f"""
            <div class="hook-banner">
                <span class="hook-icon">ℹ️</span>
                <div class="hook-text">
                    Mostrando precios particulares para <strong>Fonasa</strong>.
                    Los precios pueden variar según el prestador.
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Header resultados
        st.markdown(f"""
        <div class="resultados-header">
            <div>
                <div class="resultados-titulo">{busqueda['especialidad'].title()}</div>
                <div class="resultados-sub">
                    {', '.join([c.title() for c in busqueda['comunas']])} ·
                    {busqueda['isapre'].title()} · {busqueda['criterio']}
                </div>
            </div>
            <div class="resultados-count">{len(resultados)} centros</div>
        </div>
        """, unsafe_allow_html=True)

        # Cards
        for i, res in enumerate(resultados):
            es_mejor = (i == 0)
            card_class = "result-card best" if es_mejor else "result-card"
            convenio = res["convenio"]
            dias_label, dias_color = dias_espera_label(res["dias_espera"])

            # Badge convenio
            if convenio == "convenio":
                badge_html = f'<span class="badge badge-blue">✓ Con convenio {busqueda["isapre"].title()}</span>'
                if res["ahorro"] > 0:
                    badge_html += f'<span class="savings-text">· Ahorras {formatear_precio(res["ahorro"])}</span>'
            elif convenio == "fonasa":
                badge_html = '<span class="badge badge-red">Fonasa (precio particular)</span>'
            else:
                badge_html = f'<span class="badge badge-gray">Sin convenio {busqueda["isapre"].title()}</span>'

            # Precio
            if convenio == "convenio":
                precio_html = f"""
                    <div class="price-tachado">{formatear_precio(res['precio_base'])}</div>
                    <div class="price-main">{formatear_precio(res['copago'])}</div>
                    <div class="price-label">tu copago</div>
                """
            elif convenio == "fonasa":
                precio_html = f"""
                    <div class="price-main fonasa">{formatear_precio(res['copago'])}</div>
                    <div class="price-label">precio Fonasa</div>
                """
            else:
                precio_html = f"""
                    <div class="price-tachado">{formatear_precio(res['precio_base'])}</div>
                    <div class="price-main">{formatear_precio(res['copago'])}</div>
                    <div class="price-label">precio sin convenio</div>
                """

            # Ahorro métrica
            if res["ahorro"] > 0:
                ahorro_html = f'<div class="metric-val verde">{formatear_precio(res["ahorro"])}</div>'
            else:
                ahorro_html = '<div class="metric-val gris">—</div>'

            # Slots
            if res["opciones_hora"]:
                slots_html = "".join([
                    f'<span class="slot-pill">{o["hora"]}</span>'
                    for o in res["opciones_hora"][:4]
                ])
                slots_label = f'Horas disponibles · {res["opciones_hora"][0]["fecha"]}'
            else:
                slots_html = '<span class="slot-pill vacio">Sin horas próximas</span>'
                slots_label = "Disponibilidad"

            best_badge = '<div class="best-label">⭐ Mejor opción para ti</div>' if es_mejor else ""

            st.markdown(f"""
            <div class="{card_class}">
                {best_badge}
                <div class="card-header">
                    <div>
                        <div class="card-name">{res['nombre']}</div>
                        <div class="card-comuna">📍 {res['distancia_km']:.1f} km · {res['comuna_origen'].title()}</div>
                    </div>
                    <div class="price-block">{precio_html}</div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-val {dias_color}">{dias_label}</div>
                        <div class="metric-label">primera hora</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-val">{res['distancia_km']:.1f} km</div>
                        <div class="metric-label">distancia</div>
                    </div>
                    <div class="metric-box">
                        {ahorro_html}
                        <div class="metric-label">ahorras</div>
                    </div>
                </div>

                <div class="convenio-row">{badge_html}</div>

                <div class="slots-label">{slots_label}</div>
                <div class="slots-row">{slots_html}</div>
            </div>
            """, unsafe_allow_html=True)

            # Botón de reserva
            if res["url_reserva"] != "#":
                col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
                with col_btn2:
                    st.link_button(
                        f"📅 Reservar en {res['nombre']}",
                        res["url_reserva"],
                        use_container_width=True,
                    )

            if i < len(resultados) - 1:
                st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Mapa
        st.markdown('<div class="mapa-titulo">🗺️ Ubicación de los centros encontrados</div>', unsafe_allow_html=True)
        map_data = []
        for res in resultados:
            for centro in CENTROS_MEDICOS:
                if centro["nombre"] == res["nombre"]:
                    map_data.append({
                        "lat": centro["coordenadas"][0],
                        "lon": centro["coordenadas"][1],
                    })
        if map_data:
            st.map(pd.DataFrame(map_data), latitude="lat", longitude="lon")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("""
<div class="footer-wrap">
    <div class="footer-logo">🏥 Buscador de Horas Médicas · Región Metropolitana</div>
    Los precios y horarios son referenciales. La reserva se realiza en el sitio oficial de cada clínica.<br>
    Desarrollado para facilitar el acceso a la salud en Chile.
</div>
""", unsafe_allow_html=True)