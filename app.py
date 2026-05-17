import streamlit as st
import random
from geopy.distance import geodesic
from datetime import datetime, timedelta
import pandas as pd

# ============================================================================
# CONFIGURACIÓN DE PÁGINA (debe ir primero)
# ============================================================================

st.set_page_config(
    page_title="Buscador de Horas Médicas - Chile",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# CSS PERSONALIZADO - DISEÑO PROFESIONAL
# ============================================================================

st.markdown("""
<style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&display=swap');
    
    /* Estilos globales */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Fondo principal */
    .main > div {
        background: linear-gradient(135deg, #f5f7fa 0%, #e9ecef 100%);
    }
    
    /* Encabezado con barra azul */
    .custom-header {
        background: linear-gradient(90deg, #003366 0%, #0055a4 100%);
        padding: 0rem;
        border-radius: 0px 0px 0px 0px;
        margin: -3rem -2rem 2rem -2rem;
        padding: 1.5rem 2rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .custom-header h1 {
        color: white !important;
        font-size: 2.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.25rem !important;
    }
    
    .custom-header p {
        color: rgba(255,255,255,0.9) !important;
        font-size: 1rem !important;
        margin-bottom: 0 !important;
    }
    
    /* Tarjetas de resultados */
    .result-card {
        background: white;
        border-radius: 16px;
        padding: 1.25rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .result-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.12);
    }
    
    /* Títulos de tarjetas */
    .card-title {
        color: #003366;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
        border-left: 4px solid #0066cc;
        padding-left: 0.75rem;
    }
    
    /* Información de la tarjeta */
    .card-info {
        color: #495057;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .card-info strong {
        color: #003366;
    }
    
    /* Horas disponibles */
    .hours-list {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 0.75rem;
        margin-top: 0.5rem;
    }
    
    .hour-item {
        background: white;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 0.5rem;
        border: 1px solid #e9ecef;
        font-size: 0.85rem;
    }
    
    .hour-item:last-child {
        margin-bottom: 0;
    }
    
    /* Botón principal */
    .stButton > button {
        background: linear-gradient(90deg, #0066cc 0%, #0052a3 100%);
        color: white;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 1.5rem;
        border-radius: 40px;
        border: none;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        background: linear-gradient(90deg, #0052a3 0%, #003d80 100%);
        transform: scale(1.01);
        box-shadow: 0 4px 12px rgba(0,102,204,0.3);
    }
    
    /* Selectores */
    .stSelectbox > div > div {
        border-radius: 12px;
        border: 1px solid #dee2e6;
    }
    
    .stSelectbox label {
        font-weight: 500;
        color: #003366;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Multiselect */
    .stMultiSelect > div > div {
        border-radius: 12px;
        border: 1px solid #dee2e6;
    }
    
    .stMultiSelect label {
        font-weight: 500;
        color: #003366;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Badges de convenio */
    .badge-success {
        background: #d4edda;
        color: #155724;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .badge-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    .badge-info {
        background: #d1ecf1;
        color: #0c5460;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 500;
        display: inline-block;
    }
    
    /* Separador */
    hr {
        margin: 1.5rem 0;
        border-color: #dee2e6;
    }
    
    /* Pie de página */
    .footer {
        text-align: center;
        padding: 1.5rem;
        color: #6c757d;
        font-size: 0.75rem;
        border-top: 1px solid #dee2e6;
        margin-top: 2rem;
    }
    
    /* Spinner */
    .stSpinner > div {
        border-color: #0066cc transparent transparent transparent;
    }
    
    /* Ajustes responsive */
    @media (max-width: 768px) {
        .card-title {
            font-size: 1.1rem;
        }
        .custom-header h1 {
            font-size: 1.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# ENCABEZADO PERSONALIZADO
# ============================================================================

st.markdown("""
<div class="custom-header">
    <h1>🏥 Buscador de Horas Médicas</h1>
    <p>Encuentra la mejor opción cerca de ti • Región Metropolitana, Chile</p>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# CLÍNICAS Y CENTROS MÉDICOS
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
    horarios = ["08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                "12:00", "12:30", "14:00", "14:30", "15:00", "15:30", 
                "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"]
    fecha_base = datetime.now() + timedelta(days=dias_espera)
    medicos = MEDICOS_POR_ESPECIALIDAD.get(especialidad, ["Dr. Médico General"])
    num_opciones = random.randint(1, 2)
    opciones = []
    for i in range(num_opciones):
        dias_offset = random.randint(0, 2)
        fecha_opcion = fecha_base + timedelta(days=dias_offset)
        fecha_str = fecha_opcion.strftime("%d/%m/%Y")
        hora = random.choice(horarios)
        medico = random.choice(medicos)
        opciones.append({"fecha": fecha_str, "hora": hora, "medico": medico})
    opciones.sort(key=lambda x: (x["fecha"], x["hora"]))
    return opciones

def buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio):
    clinicas_isapre = CONVENIOS.get(isapre, [])
    es_fonasa = (isapre == "fonasa")
    mejores_por_clinica = {}
    
    for centro in CENTROS_MEDICOS:
        if especialidad not in centro["precios"]:
            continue
        nombre_centro = centro["nombre"]
        precio_base = centro["precios"][especialidad]
        tiene_convenio = nombre_centro in clinicas_isapre
        
        distancia_minima = float('inf')
        comuna_mas_cercana = None
        for comuna in comunas_seleccionadas:
            if comuna in TODAS_COMUNAS:
                distancia = geodesic(TODAS_COMUNAS[comuna], centro["coordenadas"]).kilometers
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    comuna_mas_cercana = comuna
        if distancia_minima == float('inf'):
            continue
        
        if es_fonasa:
            copago = precio_base
            etiqueta_convenio = "🏥 Fonasa (particular)"
        elif tiene_convenio:
            copago = int(precio_base * 0.25)
            etiqueta_convenio = "✅ Con convenio"
        else:
            copago = int(precio_base * 0.70)
            etiqueta_convenio = "❌ Sin convenio"
        
        min_dias, max_dias = DIAS_ESPERA.get(especialidad, (5, 15))
        if es_fonasa:
            dias_espera = random.randint(min_dias * 2, max_dias * 2)
        else:
            dias_espera = random.randint(min_dias, max_dias)
        
        opciones_hora = generar_horas_disponibles(dias_espera, especialidad)
        
        mejores_por_clinica[nombre_centro] = {
            "nombre": nombre_centro, "distancia_km": distancia_minima, "comuna_origen": comuna_mas_cercana,
            "copago": copago, "precio_base": precio_base, "dias_espera": dias_espera,
            "convenio": etiqueta_convenio, "url_reserva": centro.get("url_reserva", "#"), "opciones_hora": opciones_hora,
        }
    
    resultados = list(mejores_por_clinica.values())
    if criterio == "Más cercano primero":
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"]))
    elif criterio == "Más barato primero":
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1)))
    else:
        resultados.sort(key=lambda x: (x["distancia_km"] * 0.4) + (x["copago"] / 10000) + (x["dias_espera"] * 0.2))
    return resultados[:6]

# ============================================================================
# INTERFAZ DE USUARIO
# ============================================================================

st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    especialidad = st.selectbox("📋 Especialidad", list(DIAS_ESPERA.keys()))
with col2:
    isapre = st.selectbox("🏦 Isapre / Fonasa", list(CONVENIOS.keys()))

st.markdown("---")

st.markdown("### 📍 ¿Dónde buscas?")
st.caption("Puedes seleccionar entre 1 y 3 comunas. El sistema usará la más cercana a cada clínica.")

comunas_seleccionadas = st.multiselect(
    "Selecciona comunas (máximo 3):",
    options=list(TODAS_COMUNAS.keys()),
    default=["providencia"],
    max_selections=3
)

if not comunas_seleccionadas:
    st.warning("⚠️ Debes seleccionar al menos una comuna.")
    st.stop()

st.markdown("---")

criterio = st.selectbox("📊 Ordenar por", ["Más cercano primero", "Más barato primero", "Balanceado"])

st.markdown("---")

buscar = st.button("🔍 Buscar hora médica", use_container_width=True)

# ============================================================================
# RESULTADOS
# ============================================================================

if buscar:
    with st.spinner("Buscando horas disponibles..."):
        resultados = buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio)
    
    if not resultados:
        st.warning("No encontramos clínicas con esta especialidad en las comunas seleccionadas.")
    else:
        st.markdown("---")
        st.markdown(f"## 📋 Horas disponibles para {especialidad.title()}")
        st.caption(f"Buscando en: {', '.join([c.title() for c in comunas_seleccionadas])} | Isapre: {isapre.title()} | Orden: {criterio}")
        st.markdown("---")
        
        for i, res in enumerate(resultados):
            badge_class = "badge-success" if "Con convenio" in res['convenio'] else ("badge-warning" if "Sin convenio" in res['convenio'] else "badge-info")
            badge_text = res['convenio']
            
            st.markdown(f"""
            <div class="result-card">
                <div class="card-title">{i+1}. {res['nombre']}</div>
                <div class="card-info">📍 Desde <strong>{res['comuna_origen'].title()}</strong>: <strong>{res['distancia_km']:.1f} km</strong></div>
                <div class="card-info">💰 Copago: <strong>{formatear_precio(res['copago'])}</strong></div>
                <div class="card-info">🏥 Precio base: {formatear_precio(res['precio_base'])}</div>
                <div style="margin: 0.75rem 0;"><span class="{badge_class}">{badge_text}</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown('<div class="hours-list">', unsafe_allow_html=True)
            st.markdown("**📅 Horas disponibles:**")
            for opcion in res['opciones_hora']:
                st.markdown(f'<div class="hour-item">🕐 <strong>{opcion["fecha"]}</strong> a las <strong>{opcion["hora"]}</strong> hrs. con {opcion["medico"]}</div>', unsafe_allow_html=True)
            if res['url_reserva'] != "#":
                st.link_button("📅 Reservar en sitio externo", res['url_reserva'], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        
        st.markdown("### 🗺️ Ubicación de los centros")
        map_data = []
        for res in resultados[:6]:
            for centro in CENTROS_MEDICOS:
                if centro["nombre"] == res["nombre"]:
                    map_data.append({"lat": centro["coordenadas"][0], "lon": centro["coordenadas"][1], "nombre": centro["nombre"]})
        if map_data:
            df = pd.DataFrame(map_data)
            st.map(df, latitude="lat", longitude="lon")

# ============================================================================
# PIE DE PÁGINA
# ============================================================================

st.markdown("""
<div class="footer">
    🏥 Buscador de horas médicas - Región Metropolitana, Chile<br>
    Los precios y horarios son referenciales. La reserva se realiza en el sitio oficial de cada clínica.
</div>
""", unsafe_allow_html=True)