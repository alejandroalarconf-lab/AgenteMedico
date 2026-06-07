import streamlit as st
import random
from geopy.distance import geodesic
from datetime import datetime, timedelta
import pandas as pd

# ============================================================================
# CONFIGURACIÓN DE PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Tu hora médica al mejor precio — hoy mismo",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CONSTANTES
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
# ESTADO DE LA SESIÓN
# ============================================================================

if "session_id" not in st.session_state:
    st.session_state.session_id = random.randint(1000, 9999)
if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "busqueda_activa" not in st.session_state:
    st.session_state.busqueda_activa = False
if "ultima_busqueda" not in st.session_state:
    st.session_state.ultima_busqueda = {}
if "geo_comuna" not in st.session_state:
    st.session_state.geo_comuna = None  # None = campo vacío al inicio
if "geo_activa" not in st.session_state:
    st.session_state.geo_activa = False
if "geo_key" not in st.session_state:
    st.session_state.geo_key = 0
# CSS — SISTEMA DE DISEÑO COMPLETO
# ============================================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background: #0a0a0f !important; }
.main > div { background: #0a0a0f !important; }

/* HERO */
.hero-wrapper {
    background: linear-gradient(135deg, #0d1b2e 0%, #0a0a0f 60%);
    border-radius: 20px; padding: 36px 40px 28px 40px;
    margin-bottom: 8px; border: 1px solid #1a2a3a;
    position: relative; overflow: hidden;
}
.hero-wrapper::before {
    content: ''; position: absolute; top: -60px; right: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, rgba(0,194,124,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-title {
    font-size: 2.1rem; font-weight: 800; color: #ffffff;
    line-height: 1.15; margin: 0 0 10px 0; letter-spacing: -0.5px;
}
.hero-title span { color: #00c27c; }
.hero-subtitle { font-size: 1rem; color: #8899aa; margin: 0 0 18px 0; line-height: 1.5; }
.hero-badges { display: flex; gap: 10px; flex-wrap: wrap; }
.badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; padding: 4px 12px; font-size: 0.78rem; color: #aabbcc; font-weight: 500;
}
.badge-green { background: rgba(0,194,124,0.12); border-color: rgba(0,194,124,0.3); color: #00c27c; }

/* BANNER PRE-BUSQUEDA */
.value-banner {
    background: linear-gradient(90deg, rgba(0,194,124,0.15) 0%, rgba(0,194,124,0.05) 100%);
    border: 1px solid rgba(0,194,124,0.35); border-left: 4px solid #00c27c;
    border-radius: 12px; padding: 14px 20px; margin: 0 0 20px 0;
    display: flex; align-items: center; gap: 12px;
}
.value-banner-text { font-size: 0.92rem; color: #ccddcc; line-height: 1.5; }
.value-banner-text strong { color: #00c27c; font-weight: 700; }

/* SELECTBOXES */
.stSelectbox > div > div, .stMultiSelect > div > div {
    background: #1a1f2e !important; border: 1px solid #2a3045 !important;
    color: white !important; border-radius: 10px !important; transition: border-color 0.2s ease !important;
}
.stSelectbox > div > div:focus-within, .stMultiSelect > div > div:focus-within {
    border-color: #00c27c !important; box-shadow: 0 0 0 3px rgba(0,194,124,0.15) !important;
}
.stSelectbox label, .stMultiSelect label {
    color: #8899bb !important; font-weight: 500 !important; font-size: 0.85rem !important;
}
.stSelectbox div[data-baseweb="select"] span { color: white !important; }
[data-baseweb="tag"] { background-color: #1a4a7a !important; border-color: #2a6aaa !important; }
[data-baseweb="tag"] span { color: #aaccff !important; }

/* BOTON CTA PRINCIPAL */
.stButton > button {
    background: linear-gradient(135deg, #00c27c 0%, #00a866 100%) !important;
    color: #001a0f !important; font-weight: 700 !important; font-size: 1rem !important;
    border-radius: 12px !important; border: none !important; padding: 14px 28px !important;
    letter-spacing: 0.3px !important; transition: all 0.2s ease !important;
    box-shadow: 0 4px 20px rgba(0,194,124,0.3) !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #00d688 0%, #00c27c 100%) !important;
    box-shadow: 0 6px 28px rgba(0,194,124,0.45) !important; transform: translateY(-1px) !important;
}

/* BOTON RESERVA */
.stLinkButton > a {
    background: linear-gradient(135deg, #00c27c 0%, #00a866 100%) !important;
    color: #001a0f !important; font-weight: 700 !important; font-size: 0.95rem !important;
    border-radius: 10px !important; border: none !important; text-align: center !important;
    transition: all 0.2s ease !important; box-shadow: 0 4px 16px rgba(0,194,124,0.25) !important;
    padding: 12px !important;
}
.stLinkButton > a:hover {
    background: linear-gradient(135deg, #00d688 0%, #00c27c 100%) !important;
    box-shadow: 0 6px 24px rgba(0,194,124,0.4) !important; color: #001a0f !important;
}

/* TARJETAS */
.stContainer {
    background: #111520 !important; border-radius: 16px !important;
    padding: 4px !important; margin-bottom: 14px !important;
    border: 1px solid #1e2535 !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
.stContainer:hover { border-color: #2a3a55 !important; box-shadow: 0 4px 24px rgba(0,0,0,0.3) !important; }

/* METRICAS */
.stMetric { background: #181d2e !important; border-radius: 12px !important; padding: 14px 16px !important; border: 1px solid #252a3a !important; }
[data-testid="stMetricLabel"] { color: #667799 !important; font-size: 0.78rem !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] { color: #ffffff !important; font-size: 1.4rem !important; font-weight: 700 !important; }

/* ALERTAS */
div[data-testid="stAlert"] { border-radius: 10px !important; }
[data-testid="stNotificationContentSuccess"] { background: rgba(0,194,124,0.1) !important; border-color: rgba(0,194,124,0.4) !important; }
[data-testid="stNotificationContentWarning"] { background: rgba(100,120,150,0.08) !important; border-color: rgba(100,120,150,0.25) !important; }
[data-testid="stNotificationContentInfo"] { background: rgba(74,158,255,0.08) !important; border-color: rgba(74,158,255,0.3) !important; }

del, s { color: #445566 !important; font-size: 0.9rem !important; }
h1, h2, h3, h4, h5 { color: #ffffff !important; }
h3 { font-size: 1.05rem !important; }
h4 { font-size: 1rem !important; font-weight: 600 !important; }
.stCaption, caption { color: #667788 !important; font-size: 0.8rem !important; }
.stMap { border-radius: 14px; overflow: hidden; border: 1px solid #1e2535; }
.stSpinner > div { border-color: #00c27c transparent transparent transparent !important; }
hr { border-color: #1a2030 !important; }

.winner-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(90deg, rgba(255,200,0,0.2), rgba(255,200,0,0.08));
    border: 1px solid rgba(255,200,0,0.4); border-radius: 20px;
    padding: 4px 12px; font-size: 0.8rem; font-weight: 600; color: #ffcc00; margin-bottom: 10px;
}
.scarcity-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: rgba(255,120,0,0.12); border: 1px solid rgba(255,120,0,0.35);
    border-radius: 20px; padding: 3px 10px; font-size: 0.75rem; font-weight: 600; color: #ff9944;
}
.score-pill {
    display: inline-flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #00c27c, #00a866); color: #001a0f;
    font-weight: 800; font-size: 0.9rem; border-radius: 20px;
    padding: 3px 12px; box-shadow: 0 2px 8px rgba(0,194,124,0.35);
}
.results-count {
    font-size: 0.82rem; color: #667788;
    background: rgba(255,255,255,0.04); border-radius: 20px;
    padding: 4px 12px; border: 1px solid #1e2535; display: inline-block; margin-bottom: 12px;
}
.cta-trust { font-size: 0.75rem; color: #445566; text-align: center; margin-top: 6px; }
</style>
""", unsafe_allow_html=True)

# DATOS DE CENTROS MÉDICOS
# ============================================================================

CENTROS_MEDICOS = [
    {"nombre": "Clínica Alemana",                "comuna": "Vitacura",         "coordenadas": (-33.3940, -70.5940), "url_reserva": "https://agenda.clinicaalemana.cl/", "precios": {"medicina general": 50000, "pediatría": 58000, "traumatología": 98000, "cardiología": 88000, "dermatología": 90000, "ginecología": 75000, "otorrino": 75000, "reumatología": 80000, "nefrología": 75000, "medicina interna": 70000}},
    {"nombre": "UC Christus",                     "comuna": "Santiago Centro",  "coordenadas": (-33.4410, -70.6400), "url_reserva": "https://agenda.ucchristus.cl/reserva-horas/busqueda", "precios": {"medicina general": 45000, "pediatría": 52000, "traumatología": 88000, "cardiología": 78000, "dermatología": 80000, "ginecología": 68000, "laboratorio": 25000, "imagenes": 45000, "otorrino": 70000, "medicina interna": 65000, "geriatría": 65000}},
    {"nombre": "RedSalud Vitacura",               "comuna": "Vitacura",         "coordenadas": (-33.3900, -70.5800), "url_reserva": "https://agenda.redsalud.cl/", "precios": {"medicina general": 38000, "pediatría": 48000, "traumatología": 68000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000, "dental": 35000, "laboratorio": 20000, "otorrino": 60000, "medicina interna": 55000}},
    {"nombre": "RedSalud Providencia",            "comuna": "Providencia",      "coordenadas": (-33.4330, -70.6150), "url_reserva": "https://agenda.redsalud.cl/", "precios": {"medicina general": 38000, "pediatría": 48000, "traumatología": 68000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000, "otorrino": 60000}},
    {"nombre": "RedSalud La Florida",             "comuna": "La Florida",       "coordenadas": (-33.5350, -70.5900), "url_reserva": "https://agenda.redsalud.cl/", "precios": {"medicina general": 37000, "pediatría": 47000, "traumatología": 67000, "cardiología": 71000, "dermatología": 74000, "ginecología": 61000}},
    {"nombre": "IntegraMédica Alameda",           "comuna": "Santiago Centro",  "coordenadas": (-33.4520, -70.6480), "url_reserva": "https://www.integramedica.cl/integramedica/agendamiento", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 60000, "cardiología": 65000, "dermatología": 70000, "ginecología": 55000, "dental": 30000, "oftalmología": 50000, "otorrino": 55000, "medicina interna": 50000}},
    {"nombre": "IntegraMédica Ñuñoa",             "comuna": "Ñuñoa",            "coordenadas": (-33.4570, -70.6000), "url_reserva": "https://www.integramedica.cl/integramedica/agendamiento", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 60000, "cardiología": 65000, "dermatología": 70000, "ginecología": 55000, "otorrino": 55000}},
    {"nombre": "IntegraMédica Providencia",       "comuna": "Providencia",      "coordenadas": (-33.4370, -70.6450), "url_reserva": "https://www.integramedica.cl/integramedica/agendamiento", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 60000, "cardiología": 65000, "dermatología": 70000, "ginecología": 55000}},
    {"nombre": "IntegraMédica Las Condes",        "comuna": "Las Condes",       "coordenadas": (-33.4000, -70.5650), "url_reserva": "https://www.integramedica.cl/integramedica/agendamiento", "precios": {"medicina general": 36000, "pediatría": 46000, "traumatología": 61000, "cardiología": 66000, "dermatología": 71000, "ginecología": 56000}},
    {"nombre": "IntegraMédica Maipú",             "comuna": "Maipú",            "coordenadas": (-33.5100, -70.7550), "url_reserva": "https://www.integramedica.cl/integramedica/agendamiento", "precios": {"medicina general": 34000, "pediatría": 44000, "traumatología": 59000, "cardiología": 64000, "dermatología": 69000, "ginecología": 54000}},
    {"nombre": "IntegraMédica La Florida",        "comuna": "La Florida",       "coordenadas": (-33.5350, -70.5900), "url_reserva": "https://www.integramedica.cl/integramedica/agendamiento", "precios": {"medicina general": 34000, "pediatría": 44000, "traumatología": 59000, "cardiología": 64000, "dermatología": 69000, "ginecología": 54000}},
    {"nombre": "Clínica INDISA",                  "comuna": "Providencia",      "coordenadas": (-33.4250, -70.6200), "url_reserva": "https://www.indisa.cl/reserva-de-horas", "precios": {"medicina general": 42000, "pediatría": 52000, "traumatología": 72000, "cardiología": 75000, "dermatología": 80000, "ginecología": 65000, "maternidad": 120000, "examenes": 30000, "otorrino": 68000, "medicina interna": 62000}},
    {"nombre": "Clínica Las Condes",              "comuna": "Las Condes",       "coordenadas": (-33.4100, -70.5720), "url_reserva": "https://reserva.clinicalascondes.cl/agendaweb/", "precios": {"medicina general": 48000, "pediatría": 55000, "traumatología": 95000, "cardiología": 85000, "dermatología": 88000, "ginecología": 72000, "otorrino": 78000, "medicina interna": 72000, "cirugia": 110000}},
    {"nombre": "Clínica Bupa Santiago",           "comuna": "La Florida",       "coordenadas": (-33.5330, -70.5950), "url_reserva": "https://www.clinicabupasantiago.cl/reserva-de-horas", "precios": {"medicina general": 45000, "pediatría": 55000, "traumatología": 70000, "cardiología": 75000, "dermatología": 85000, "ginecología": 65000, "cirugia": 100000, "maternidad": 90000, "otorrino": 70000}},
    {"nombre": "Clínica U. de los Andes",         "comuna": "Las Condes",       "coordenadas": (-33.3850, -70.5450), "url_reserva": "https://www.clinicauandes.cl/reserva-de-horas-presencial", "precios": {"medicina general": 50000, "pediatría": 60000, "traumatología": 90000, "cardiología": 85000, "dermatología": 88000, "ginecología": 72000, "cirugia": 120000}},
    {"nombre": "Hospital del Profesor",           "comuna": "Estación Central", "coordenadas": (-33.4700, -70.7000), "url_reserva": "https://www.chp.cl/web-chp/", "precios": {"medicina general": 40000, "pediatría": 50000, "traumatología": 70000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000, "kinesiología": 30000, "imagenes": 40000}},
    {"nombre": "Clini - Providencia",             "comuna": "Providencia",      "coordenadas": (-33.4350, -70.6350), "url_reserva": "https://www.clini.cl/agendamiento", "precios": {"medicina general": 35000, "cardiología": 65000, "laboratorio": 20000, "imagenes": 35000, "examenes": 25000}},
    {"nombre": "Clini - La Florida",              "comuna": "La Florida",       "coordenadas": (-33.5300, -70.5850), "url_reserva": "https://www.clini.cl/agendamiento", "precios": {"medicina general": 35000, "cardiología": 65000, "laboratorio": 20000, "imagenes": 35000, "examenes": 25000}},
    {"nombre": "Clínica Santa María",             "comuna": "Providencia",      "coordenadas": (-33.4260, -70.6230), "url_reserva": "https://www.clinicasantamaria.cl/reserva-de-horas", "precios": {"medicina general": 50000, "pediatría": 55000, "traumatología": 80000, "cardiología": 85000, "dermatología": 90000, "ginecología": 75000, "otorrino": 75000}},
    {"nombre": "Clínica Dávila Recoleta",         "comuna": "Recoleta",         "coordenadas": (-33.4150, -70.6400), "url_reserva": "https://www.davila.cl/reserva-de-hora", "precios": {"medicina general": 40000, "pediatría": 50000, "traumatología": 68000, "cardiología": 72000, "dermatología": 75000, "ginecología": 62000, "otorrino": 65000}},
    {"nombre": "Clínica MEDS",                    "comuna": "Las Condes",       "coordenadas": (-33.3850, -70.5450), "url_reserva": "https://www.meds.cl/reserva-horas-meds/", "precios": {"medicina general": 50000, "pediatría": 60000, "traumatología": 75000, "cardiología": 80000, "dermatología": 85000, "ginecología": 70000}},
    {"nombre": "Clínica Bicentenario Puente Alto","comuna": "Puente Alto",      "coordenadas": (-33.6200, -70.5750), "url_reserva": "https://lmnbicentenario.com/reserva-de-hora/", "precios": {"medicina general": 35000, "pediatría": 45000, "traumatología": 65000, "ginecología": 58000, "kinesiología": 28000, "nutrición": 35000}},
    {"nombre": "Clínica Bicentenario Las Condes", "comuna": "Las Condes",       "coordenadas": (-33.4000, -70.5650), "url_reserva": "https://lmnbicentenario.com/reserva-de-hora/", "precios": {"medicina general": 38000, "pediatría": 48000, "traumatología": 68000, "ginecología": 60000, "kinesiología": 30000}},
    {"nombre": "Clínica Tabancura",               "comuna": "Las Condes",       "coordenadas": (-33.3850, -70.5450), "url_reserva": "https://www.policlinicotabancura.cl/agenda/", "precios": {"medicina general": 42000, "traumatología": 72000, "oftalmología": 60000, "cardiología": 70000, "dermatología": 75000}},
    {"nombre": "Clínica Avansalud Providencia",   "comuna": "Providencia",      "coordenadas": (-33.4350, -70.6350), "url_reserva": "https://agenda.redsalud.cl/", "precios": {"medicina general": 30000, "pediatría": 40000, "ginecología": 50000, "nutrición": 28000, "kinesiología": 25000}},
    {"nombre": "Clínica Avansalud Las Condes",    "comuna": "Las Condes",       "coordenadas": (-33.4100, -70.5700), "url_reserva": "https://agenda.redsalud.cl/", "precios": {"medicina general": 32000, "pediatría": 42000, "ginecología": 52000, "nutrición": 30000}},
]

CONVENIOS = {
    "banmédica":     ["Clínica Alemana", "Clínica U. de los Andes", "UC Christus", "Clínica Santa María", "Clínica Dávila Recoleta", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "IntegraMédica Las Condes", "IntegraMédica Maipú", "IntegraMédica La Florida", "Clínica Bicentenario Puente Alto", "Clínica Bicentenario Las Condes", "Clínica INDISA"],
    "consalud":      ["RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "IntegraMédica Las Condes", "IntegraMédica Maipú", "IntegraMédica La Florida", "Clínica Avansalud Providencia", "Clínica Avansalud Las Condes", "Clínica Dávila Recoleta", "Clínica Bupa Santiago", "Clínica INDISA"],
    "colmena":       ["UC Christus", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "Clínica INDISA", "Clínica Bicentenario Puente Alto", "Clínica Bicentenario Las Condes", "Clínica Avansalud Providencia", "Clínica Avansalud Las Condes", "Clínica Dávila Recoleta"],
    "vida tres":     ["Clínica Alemana", "Clínica Santa María", "Clínica INDISA", "UC Christus", "Clínica U. de los Andes", "Hospital del Profesor", "Clínica Bupa Santiago"],
    "nueva masvida": ["IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "IntegraMédica Las Condes", "IntegraMédica Maipú", "IntegraMédica La Florida", "Clínica Bupa Santiago", "Clínica Dávila Recoleta", "Clínica Las Condes", "Clínica Avansalud Providencia", "Clínica Avansalud Las Condes", "RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "Clínica INDISA"],
    "esencial":      ["IntegraMédica Alameda", "IntegraMédica Ñuñoa", "RedSalud Providencia", "Clínica Avansalud Providencia"],
    "fonasa":        ["RedSalud Vitacura", "RedSalud Providencia", "RedSalud La Florida", "IntegraMédica Alameda", "IntegraMédica Ñuñoa", "IntegraMédica Providencia", "IntegraMédica Las Condes", "IntegraMédica Maipú", "IntegraMédica La Florida", "UC Christus", "Clínica Dávila Recoleta", "Clínica Bupa Santiago", "Clínica INDISA", "Clínica Avansalud Providencia", "Clínica Avansalud Las Condes", "Hospital del Profesor"],
}

TODAS_COMUNAS = {
    "providencia":      (-33.437, -70.650),
    "las condes":       (-33.400, -70.565),
    "santiago centro":  (-33.440, -70.650),
    "la florida":       (-33.535, -70.590),
    "vitacura":         (-33.393, -70.590),
    "recoleta":         (-33.415, -70.640),
    "maipú":            (-33.510, -70.755),
    "ñuñoa":            (-33.457, -70.600),
    "estación central": (-33.470, -70.700),
    "puente alto":      (-33.620, -70.575),
}

DIAS_ESPERA = {
    "medicina general": (1, 5),   "dermatología": (15, 45),
    "psiquiatría": (20, 60),      "traumatología": (2, 10),
    "ginecología": (3, 12),       "oftalmología": (7, 20),
    "cardiología": (5, 15),       "pediatría": (1, 7),
    "neurología": (10, 30),       "nutrición": (3, 10),
    "kinesiología": (1, 5),       "urología": (5, 15),
    "laboratorio": (1, 3),        "imagenes": (2, 5),
    "dental": (2, 7),             "examenes": (1, 4),
    "otorrino": (5, 20),          "reumatología": (10, 30),
    "nefrología": (7, 21),        "hematología": (10, 25),
    "infectología": (5, 20),      "geriatría": (7, 21),
    "cirugia": (10, 35),          "medicina interna": (3, 14),
}

MEDICOS_POR_ESPECIALIDAD = {
    "medicina general":  ["Dr. Juan Pablo Silva", "Dra. María Fernanda López", "Dr. Carlos Alberto Rojas"],
    "traumatología":     ["Dr. Cristián Labbé", "Dra. Macarena Valdés", "Dr. Sebastián Herrera"],
    "cardiología":       ["Dr. Jorge Bartolucci", "Dra. Pamela Serón", "Dr. Ramón Corbalán"],
    "dermatología":      ["Dra. Claudia Aranís", "Dr. Sergio González", "Dra. Jimena Schnettler"],
    "pediatría":         ["Dra. Marcela Bahamondes", "Dr. Tomás Alliende", "Dra. Andrea Oyarzún"],
    "ginecología":       ["Dra. Paulina Vega", "Dr. Juan Enrique Montero", "Dra. Soledad Díaz"],
    "oftalmología":      ["Dr. Rodrigo Galdames", "Dra. Andrea Lutz", "Dr. Gonzalo Rojas"],
    "neurología":        ["Dr. Pedro Chaná", "Dra. Paulina Orellana", "Dr. Claudio Hetz"],
    "psiquiatría":       ["Dr. Claudio Fuenzalida", "Dra. María Elena Gorostiza", "Dr. Pablo López-Silva"],
    "nutrición":         ["Dra. Vivianne Sotomayor", "Dr. Rodrigo Aránguiz", "Dra. Javiera Torres"],
    "kinesiología":      ["Kine. Felipe González", "Kine. Valentina Méndez", "Kine. Cristóbal Jiménez"],
    "urología":          ["Dr. Mauricio Hoyl", "Dr. Pedro Bórquez", "Dr. José Miguel Rojas"],
    "laboratorio":       ["Tec. María José López", "Tec. Cristián Soto", "Tec. Daniela Muñoz"],
    "imagenes":          ["Tec. Rodrigo Acuña", "Dra. Carla Espinoza", "Tec. Paulo Díaz"],
    "dental":            ["Dra. Carolina Ortiz", "Dr. Sebastián Lara", "Dra. María Jesús Valdés"],
    "examenes":          ["Tec. Pamela Rojas", "Tec. Cristóbal Fuentes", "Dra. Valentina Pérez"],
    "otorrino":          ["Dr. Juan Pablo Hidalgo", "Dra. Paulina Aldunate", "Dr. Cristián Papuzinski"],
    "reumatología":      ["Dr. Óscar Soto", "Dra. Marcela Cárcamo", "Dr. Rodrigo Necochea"],
    "nefrología":        ["Dr. Juan Carlos Flores", "Dra. Paulina Zamorano", "Dr. Gonzalo Ibaceta"],
    "hematología":       ["Dra. Verónica Mena", "Dr. Alejandro Jara", "Dra. Bernardita Garrido"],
    "infectología":      ["Dr. Rodrigo Blamey", "Dra. Jeannette Dabanch", "Dr. Carlos Pérez"],
    "geriatría":         ["Dra. Lydia Lera", "Dr. Pedro Paulo Marín", "Dra. Cecilia Albala"],
    "cirugia":           ["Dr. Ricardo Rossi", "Dra. Carolina Morales", "Dr. Patricio Rodríguez"],
    "medicina interna":  ["Dr. Juan Carlos Rojas", "Dra. Paola Varela", "Dr. Rodrigo Muñoz"],
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def formatear_precio(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")

def formatear_rango(valor_min: int, valor_max: int) -> str:
    return f"{formatear_precio(valor_min)} \u2013 {formatear_precio(valor_max)}"

def calcular_score(distancia_km, copago, dias_espera, ahorro):
    """Score de conveniencia 1-10 (mayor = mejor)"""
    score_dist   = max(0, 10 - distancia_km * 2)
    score_precio = max(0, 10 - copago / 8000)
    score_espera = max(0, 10 - dias_espera * 0.5)
    score_ahorro = min(3, ahorro / 10000)
    raw = (score_dist * 0.35 + score_precio * 0.35 + score_espera * 0.20 + score_ahorro * 0.10)
    return min(10, max(1, round(raw, 1)))

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
        return f"{dias} días", "ámbar"
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
        distancia_minima = float("inf")
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
        if distancia_minima == float("inf"):
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
            dias_espera_val = random.randint(min_dias * 2, max_dias * 2)
        else:
            dias_espera_val = random.randint(min_dias, max_dias)
        opciones_hora = generar_horas_disponibles(dias_espera_val, especialidad)
        score = calcular_score(distancia_minima, copago, dias_espera_val, ahorro)
        copago_min = int(copago * 0.8)
        copago_max = int(copago * 1.2)
        mejores_por_clinica[nombre] = {
            "nombre": nombre, "distancia_km": distancia_minima,
            "comuna_origen": comuna_mas_cercana, "copago": copago, "copago_min": copago_min, "copago_max": copago_max,
            "precio_base": precio_base, "dias_espera": dias_espera_val,
            "convenio": etiqueta_convenio, "ahorro": ahorro,
            "url_reserva": centro.get("url_reserva", "#"),
            "opciones_hora": opciones_hora, "score": score,
        }
    resultados = list(mejores_por_clinica.values())
    if criterio == "Más cercano primero":
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"]))
    elif criterio == "Más barato primero":
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1)))
    else:
        resultados.sort(key=lambda x: -x["score"])
    return resultados[:MAX_RESULTADOS]

# ============================================================================
# ============================================================================
# FUNCIÓN DE GEOLOCALIZACIÓN
# ============================================================================

def comuna_mas_cercana(lat: float, lon: float) -> str:
    """Dado un punto GPS retorna la comuna del diccionario más cercana."""
    mejor = None
    mejor_dist = float("inf")
    for nombre, coords in TODAS_COMUNAS.items():
        d = geodesic((lat, lon), coords).kilometers
        if d < mejor_dist:
            mejor_dist = d
            mejor = nombre
    return mejor

# ============================================================================
# UI - HERO HEADER
# ============================================================================

st.markdown("""
<div class="hero-wrapper">
  <div class="hero-title">✅ Tu hora médica al <span>mejor precio</span> — hoy mismo</div>
  <div class="hero-subtitle">Compara 26 clínicas en Santiago · Compatible con Isapre y Fonasa · Sin registro</div>
  <div class="hero-badges">
    <span class="badge">🏥 26 centros médicos</span>
    <span class="badge">📋 24 especialidades</span>
    <span class="badge badge-green">💚 Sin costo de reserva</span>
    <span class="badge">📍 Región Metropolitana</span>
  </div>
</div>
""", unsafe_allow_html=True)

# Banner de valor PRE-búsqueda
st.markdown("""
<div class="value-banner">
  <span style="font-size:1.4rem">💡</span>
  <div class="value-banner-text">
    Con tu Isapre puedes pagar hasta un <strong>75% menos</strong> que el precio normal.
    Ingresa tu previsión para ver tus precios reales — <strong>no pierdas ese descuento.</strong>
  </div>
</div>
""", unsafe_allow_html=True)
# ============================================================================
# GEOLOCALIZACIÓN — JS nativo via components.html + query_params
# ============================================================================
import streamlit.components.v1 as components
from streamlit_geolocation import streamlit_geolocation

st.markdown("""
<style>
.geo-box {
    background: linear-gradient(90deg,rgba(0,100,200,0.12),rgba(0,100,200,0.04));
    border:1px solid rgba(0,120,220,0.3); border-left:4px solid #4a9eff;
    border-radius:12px; padding:14px 20px; margin-bottom:4px;
    display:flex; align-items:center; gap:12px;
}
.geo-box-text{font-size:0.9rem;color:#aabbdd;line-height:1.5;}
.geo-box-text strong{color:#4a9eff;}
.geo-detected{
    background:linear-gradient(90deg,rgba(0,194,124,0.12),rgba(0,194,124,0.04));
    border:1px solid rgba(0,194,124,0.35); border-left:4px solid #00c27c;
    border-radius:12px; padding:12px 18px; margin-bottom:4px;
    font-size:0.88rem; color:#aaddcc;
}
.geo-detected strong{color:#00c27c;}

/* Boton de ubicacion: contenedor negro con icono + texto al lado */
div:has(> iframe[title="streamlit_geolocation.streamlit_geolocation"]){
  background:#0f1420; border:1px solid #2a3045; border-radius:12px;
  padding:10px 14px; display:flex; align-items:center; gap:10px;
  width:100%; cursor:pointer;
  transition:border-color 0.2s ease, box-shadow 0.2s ease;
}
div:has(> iframe[title="streamlit_geolocation.streamlit_geolocation"]):hover{
  border-color:#3a4560; box-shadow:0 4px 16px rgba(0,0,0,0.35);
}
/* Limitamos el ancho del iframe del icono para dejar espacio al texto */
iframe[title="streamlit_geolocation.streamlit_geolocation"]{
  width:34px !important; min-width:34px; flex:0 0 34px;
}
/* Texto a la derecha del icono */
div:has(> iframe[title="streamlit_geolocation.streamlit_geolocation"])::after{
  content:'presiona aquí para ver tu ubicación';
  font-size:0.82rem; color:#aabbcc; font-weight:500; line-height:1.3;
  flex:1 1 auto; white-space:normal;
}
/* Ocultamos la etiqueta superior anterior si existiera */
.geo-btn-label{ display:none; }
</style>
""", unsafe_allow_html=True)

# Leer coordenadas desde query_params (llegan del JS del iframe)
_p = st.query_params
if "geo_lat" in _p and "geo_lon" in _p and not st.session_state.geo_comuna:
    try:
        _lat = float(_p["geo_lat"])
        _lon = float(_p["geo_lon"])
        _best, _best_d = None, float("inf")
        for _n, _c in TODAS_COMUNAS.items():
            _d = geodesic((_lat, _lon), _c).kilometers
            if _d < _best_d:
                _best_d = _d
                _best = _n
        st.session_state.geo_comuna = _best
        st.session_state.geo_key = st.session_state.get("geo_key", 0) + 1
        st.query_params.clear()
        st.rerun()
    except Exception:
        pass

# UI geo
_gc1, _gc2 = st.columns([4, 1])
with _gc1:
    if st.session_state.geo_comuna:
        st.markdown(
            f'<div class="geo-detected">✅ Ubicación detectada — comuna: '
            f'<strong>{st.session_state.geo_comuna.title()}</strong> · '
            f'Campo completado automáticamente.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="geo-box"><span style="font-size:1.3rem">📡</span>'
            '<div class="geo-box-text"><strong>Detecta tu ubicación</strong> para ver las '
            'clínicas más cercanas — o elige tu comuna manualmente abajo.</div></div>',
            unsafe_allow_html=True
        )
with _gc2:
    if not st.session_state.geo_comuna:
        # Componente de geolocalizacion (canal bidireccional nativo).
        # Devuelve lat/lon directamente a Python sin manipular la URL.
        st.markdown('<div class="geo-btn-wrap">', unsafe_allow_html=True)
        _loc = streamlit_geolocation()
        st.markdown('</div>', unsafe_allow_html=True)
        if _loc and _loc.get("latitude") is not None and _loc.get("longitude") is not None:
            try:
                _lat = float(_loc["latitude"])
                _lon = float(_loc["longitude"])
                st.session_state.geo_comuna = comuna_mas_cercana(_lat, _lon)
                st.session_state.geo_key = st.session_state.get("geo_key", 0) + 1
                st.rerun()
            except (TypeError, ValueError):
                st.warning("No pudimos leer tu ubicacion. Elige tu comuna manualmente abajo.")
    else:
        if st.button("✕ Cambiar comuna", use_container_width=True):
            st.session_state.geo_comuna = None
            st.session_state.geo_activa = False
            st.session_state.geo_key = st.session_state.get("geo_key", 0) + 1
            st.rerun()

# Defaults para el multiselect
_default_comunas = [st.session_state.geo_comuna] if st.session_state.geo_comuna else []
_geo_key = st.session_state.get("geo_key", 0)

# ============================================================================
# UI - FILTROS
# ============================================================================

col1, col2 = st.columns(2)
with col1:
    especialidad = st.selectbox("📋 ¿Qué especialidad necesitas?", list(DIAS_ESPERA.keys()))
with col2:
    isapre = st.selectbox("🏦 Tu previsión de salud", list(CONVENIOS.keys()))

_lbl = "📍 ¿Desde qué comuna buscas? (máx. 3)" + (" — detectada ✓" if st.session_state.geo_comuna else " — o usa 📡 arriba")
comunas_seleccionadas = st.multiselect(
    _lbl,
    options=list(TODAS_COMUNAS.keys()),
    default=_default_comunas,
    max_selections=MAX_COMUNAS,
    key=f"comunas_widget_{_geo_key}",
)

if not comunas_seleccionadas:
    st.info("📍 Selecciona tu comuna — o pulsa **📡 Usar mi ubicación** para detectarla.")
    st.stop()

col3, col4 = st.columns([2, 1])
with col3:
    criterio = st.selectbox(
        "📊 Ordenar por",
        ["Balanceado", "Más cercano primero", "Más barato primero"],
        help="Balanceado combina distancia, precio y tiempo de espera"
    )
with col4:
    st.markdown("<div style='height:28px'></div>", unsafe_allow_html=True)
    buscar = st.button("Ver mis horas disponibles →", use_container_width=True)

st.markdown("<div class='cta-trust'>Sin tarjeta · Sin registro · En menos de 2 minutos</div>", unsafe_allow_html=True)

# ============================================================================
# LÓGICA DE BÚSQUEDA
# ============================================================================

if buscar:
    st.session_state.busqueda_activa = True
    with st.spinner("Buscando las mejores horas en 26 centros médicos..."):
        st.session_state.resultados = buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio)
        st.session_state.ultima_busqueda = {
            "especialidad": especialidad,
            "comunas": comunas_seleccionadas,
            "isapre": isapre,
            "criterio": criterio,
        }

# UI - RESULTADOS
# ============================================================================

if st.session_state.busqueda_activa and st.session_state.resultados is not None:
    resultados = st.session_state.resultados
    busqueda  = st.session_state.ultima_busqueda
    es_fonasa = busqueda["isapre"] == "fonasa"

    if not resultados:
        st.warning("No encontramos clínicas con esta especialidad en las comunas seleccionadas.")
    else:
        ahorro_max = max((r["ahorro"] for r in resultados), default=0)
        if ahorro_max > 0:
            st.success(f"💰 Con **{busqueda['isapre'].title()}** puedes ahorrar hasta **{formatear_precio(ahorro_max)}** en {busqueda['especialidad']}. Te mostramos las mejores opciones.")
        elif es_fonasa:
            st.info("ℹ️ Mostrando precios particulares para **Fonasa**.")

        st.markdown(f"### {busqueda['especialidad'].title()}")
        st.markdown(
            f'<div class="results-count">📊 Mostrando {len(resultados)} de 26 centros · {busqueda["criterio"].lower()}</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")

        for i, res in enumerate(resultados):
            es_mejor  = (i == 0)
            dias_label, _ = dias_espera_label(res["dias_espera"])
            score = res.get("score", 5.0)

            with st.container(border=True):

                if es_mejor:
                    col_badge, col_score = st.columns([3, 1])
                    with col_badge:
                        st.markdown('<div class="winner-badge">⭐ Mejor opción para ti</div>', unsafe_allow_html=True)
                    with col_score:
                        st.markdown(f'<div style="text-align:right"><span class="score-pill">Score {score}/10</span></div>', unsafe_allow_html=True)
                    if res["dias_espera"] <= 3:
                        st.markdown(f'<span class="scarcity-badge">🟡 Última hora disponible en {dias_label}</span>', unsafe_allow_html=True)

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"#### {res['nombre']}")
                    st.markdown(f"📍 {res['distancia_km']:.1f} km desde **{res['comuna_origen'].title()}**")
                with col2:
                    if res["convenio"] == "convenio":
                        st.markdown(f"~~{formatear_precio(res['precio_base'])}~~")
                        st.markdown(f"#### {formatear_rango(res['copago_min'], res['copago_max'])}")
                        ahorro_str = formatear_precio(res["precio_base"] - res["copago"])
                        st.markdown(f'<div style="color:#00c27c;font-size:0.82rem;font-weight:600">💚 Ahorras {ahorro_str} vs. precio normal</div>', unsafe_allow_html=True)
                    elif res["convenio"] == "fonasa":
                        st.markdown(f"#### {formatear_rango(res['copago_min'], res['copago_max'])}")
                        st.caption("precio Fonasa")
                    else:
                        st.markdown(f"~~{formatear_precio(res['precio_base'])}~~")
                        st.markdown(f"#### {formatear_rango(res['copago_min'], res['copago_max'])}")
                        st.caption("precio sin convenio")
                    st.caption("\U0001F4A1 valor referencial \u2014 confirma con tu isapre")

                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.metric(label="⏱ Primera hora", value=dias_label)
                with col_b:
                    st.metric(label="📍 Distancia", value=f"{res['distancia_km']:.1f} km")
                with col_c:
                    if res["ahorro"] > 0:
                        st.metric(label="💰 Ahorras", value=formatear_precio(res["ahorro"]))
                    else:
                        st.metric(label="💰 Ahorras", value="Sin convenio")

                if res["convenio"] == "convenio":
                    st.success(f"✅ Con convenio {busqueda['isapre'].title()} — copago preferencial")
                elif res["convenio"] == "fonasa":
                    st.info("🏥 Fonasa (precio particular)")
                else:
                    st.warning(f"ℹ️ Sin convenio {busqueda['isapre'].title()} · Consulta cobertura con tu ejecutivo")

                st.markdown("**📅 Horas disponibles**")
                if res["opciones_hora"]:
                    for o in res["opciones_hora"][:3]:
                        st.markdown(f"- 🕐 **{o['fecha']}** a las **{o['hora']}** hrs. con {o['medico']}")
                    st.caption(f"Primera hora disponible: {res['opciones_hora'][0]['fecha']} a las {res['opciones_hora'][0]['hora']} hrs.")
                else:
                    st.info("Sin horas próximas disponibles")

                if res["url_reserva"] != "#":
                    st.link_button(f"📅 Reservar hora gratis en {res['nombre']} →", res['url_reserva'], use_container_width=True)
                st.markdown('<div class="cta-trust">Sin tarjeta · Sin registro · En menos de 2 minutos</div>', unsafe_allow_html=True)
                st.markdown("---")

        if resultados:
            st.markdown("### 🗺️ Ubicación de los centros encontrados")
            map_data = []
            for res in resultados:
                for centro in CENTROS_MEDICOS:
                    if centro["nombre"] == res["nombre"]:
                        map_data.append({"lat": centro["coordenadas"][0], "lon": centro["coordenadas"][1]})
                        break
            if map_data:
                st.map(pd.DataFrame(map_data), latitude="lat", longitude="lon")

# ============================================================================
# PIE DE PÁGINA
# ============================================================================

st.markdown("---")
st.caption("✅ Buscador de horas médicas · 26 centros médicos · 24 especialidades · Región Metropolitana, Chile · Sin costo de reserva")
