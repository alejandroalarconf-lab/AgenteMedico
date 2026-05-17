import streamlit as st
import random
from geopy.distance import geodesic
from datetime import datetime, timedelta

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
# CONVENIOS POR ISAPRE
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

# ============================================================================
# NOMBRES DE MÉDICOS POR ESPECIALIDAD (datos realistas)
# ============================================================================

MEDICOS_POR_ESPECIALIDAD = {
    "medicina general": ["Dr. Juan Pablo Silva", "Dra. María Fernanda López", "Dr. Carlos Alberto Rojas", "Dra. Patricia González", "Dr. Roberto Méndez"],
    "traumatología": ["Dr. Cristián Labbé", "Dra. Macarena Valdés", "Dr. Sebastián Herrera", "Dr. Andrés Tagle", "Dra. Paulina Sanhueza"],
    "cardiología": ["Dr. Jorge Bartolucci", "Dra. Pamela Serón", "Dr. Ramón Corbalán", "Dra. Daniela Aravena", "Dr. Mario Castro"],
    "dermatología": ["Dra. Claudia Aranís", "Dr. Sergio González", "Dra. Jimena Schnettler", "Dr. Felipe Velasco", "Dra. Valentina Ruiz"],
    "pediatría": ["Dra. Marcela Bahamondes", "Dr. Tomás Alliende", "Dra. Andrea Oyarzún", "Dr. Francisco Moraga", "Dra. Carolina Herrera"],
    "ginecología": ["Dra. Paulina Vega", "Dr. Juan Enrique Montero", "Dra. Soledad Díaz", "Dr. Patricio Barriga", "Dra. Francisca Santander"],
    "oftalmología": ["Dr. Rodrigo Galdames", "Dra. Andrea Lutz", "Dr. Gonzalo Rojas", "Dra. Paula Pérez", "Dr. Felipe Valenzuela"],
    "neurología": ["Dr. Pedro Chaná", "Dra. Paulina Orellana", "Dr. Claudio Hetz", "Dra. Bernarda Garrido", "Dr. Rodrigo Saavedra"],
    "psiquiatría": ["Dr. Claudio Fuenzalida", "Dra. María Elena Gorostiza", "Dr. Pablo López-Silva", "Dra. Javiera Duarte", "Dr. Álvaro Jiménez"],
    "nutrición": ["Dra. Vivianne Sotomayor", "Dr. Rodrigo Aránguiz", "Dra. Javiera Torres", "Dr. Cristián Ríos", "Dra. Daniela Pinto"],
    "kinesiología": ["Kine. Felipe González", "Kine. Valentina Méndez", "Kine. Cristóbal Jiménez", "Kine. Camila Rojas", "Kine. Sebastián Muñoz"],
    "urología": ["Dr. Mauricio Hoyl", "Dr. Pedro Bórquez", "Dra. (URG) Paola Pizarro", "Dr. José Miguel Rojas", "Dr. Álvaro Saavedra"],
    "gastroenterología": ["Dr. Rodrigo Quera", "Dra. Lilian Flores", "Dr. Pablo Orellana", "Dra. Andrea Peralta", "Dr. Juan Carlos Rojas"],
    "endocrinología": ["Dra. Ana María Lillo", "Dr. Patricio Salman", "Dra. Daniela Mardones", "Dr. Rodrigo Muñoz", "Dra. Carolina Tapia"],
    "otorrino": ["Dr. Juan Pablo Hidalgo", "Dra. Paulina Aldunate", "Dr. Cristián Papuzinski", "Dra. Macarena Valenzuela", "Dr. Andrés Alvo"],
}

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def formatear_precio(valor):
    return f"${valor:,.0f}".replace(",", ".")

def generar_horas_disponibles(dias_espera, especialidad):
    """Genera entre 1 y 3 opciones de hora y médico para una clínica"""
    # Horarios disponibles (en horas desde 8:00 a 19:00)
    horarios = ["08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", 
                "12:00", "12:30", "14:00", "14:30", "15:00", "15:30", 
                "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"]
    
    # Fecha de la hora (dentro de los días de espera)
    fecha_base = datetime.now() + timedelta(days=dias_espera)
    
    # Obtener médicos para esta especialidad
    medicos = MEDICOS_POR_ESPECIALIDAD.get(especialidad, ["Dr. Médico General"])
    
    # Generar entre 1 y 3 opciones de hora
    num_opciones = random.randint(1, 3)
    opciones = []
    
    for i in range(num_opciones):
        # Fecha: puede ser el mismo día base o hasta 3 días después
        dias_offset = random.randint(0, 3)
        fecha_opcion = fecha_base + timedelta(days=dias_offset)
        fecha_str = fecha_opcion.strftime("%d/%m/%Y")
        
        # Hora aleatoria
        hora = random.choice(horarios)
        
        # Médico aleatorio
        medico = random.choice(medicos)
        
        # Precio según la especialidad (puede variar según el médico)
        opciones.append({
            "fecha": fecha_str,
            "hora": hora,
            "medico": medico
        })
    
    # Ordenar por fecha y hora
    opciones.sort(key=lambda x: (x["fecha"], x["hora"]))
    return opciones

def buscar_horas(especialidad, comunas_seleccionadas, isapre, criterio):
    """Busca horas médicas considerando múltiples comunas"""
    clinicas_isapre = CONVENIOS.get(isapre, [])
    es_fonasa = (isapre == "fonasa")
    mejores_por_clinica = {}
    
    for centro in CENTROS_MEDICOS:
        if especialidad not in centro["precios"]:
            continue
        
        nombre_centro = centro["nombre"]
        precio_base = centro["precios"][especialidad]
        tiene_convenio = nombre_centro in clinicas_isapre
        
        # Distancia a la comuna más cercana
        distancia_minima = float('inf')
        comuna_mas_cercana = None
        
        for comuna in comunas_seleccionadas:
            coord_comuna = TODAS_COMUNAS.get(comuna)
            if coord_comuna:
                distancia = geodesic(coord_comuna, centro["coordenadas"]).kilometers
                if distancia < distancia_minima:
                    distancia_minima = distancia
                    comuna_mas_cercana = comuna
        
        if distancia_minima == float('inf'):
            continue
        
        # Cálculo de copago
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
        
        # Generar opciones de hora y médico
        opciones_hora = generar_horas_disponibles(dias_espera, especialidad)
        
        mejores_por_clinica[nombre_centro] = {
            "nombre": nombre_centro,
            "distancia_km": distancia_minima,
            "comuna_origen": comuna_mas_cercana,
            "copago": copago,
            "precio_base": precio_base,
            "dias_espera": dias_espera,
            "convenio": etiqueta_convenio,
            "url_reserva": centro.get("url_reserva", "#"),
            "opciones_hora": opciones_hora,
        }
    
    resultados = list(mejores_por_clinica.values())
    
    # Ordenar según criterio
    if criterio == "Más cercano primero":
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"]))
    elif criterio == "Más barato primero":
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1)))
    else:  # Balanceado
        resultados.sort(key=lambda x: (x["distancia_km"] * 0.4) + (x["copago"] / 10000) + (x["dias_espera"] * 0.2))
    
    return resultados[:6]

# ============================================================================
# INTERFAZ WEB
# ============================================================================

st.title("🏥 Buscador de Horas Médicas - Chile")
st.markdown("---")

# Fila 1: Especialidad e Isapre
col1, col2 = st.columns(2)
with col1:
    especialidad = st.selectbox("📋 Especialidad", list(DIAS_ESPERA.keys()))
with col2:
    isapre = st.selectbox("🏦 Isapre / Fonasa", list(CONVENIOS.keys()))

st.markdown("---")

# Fila 2: Selección de comunas
st.subheader("📍 ¿Dónde buscas?")
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
        st.subheader(f"📋 Horas disponibles para {especialidad.title()}")
        st.caption(f"Buscando en: {', '.join([c.title() for c in comunas_seleccionadas])} | Isapre: {isapre.title()}")
        
        # Mostrar resultados
        for i, res in enumerate(resultados):
            with st.container(border=True):
                col_info, col_horas = st.columns([1, 2])
                
                with col_info:
                    st.markdown(f"### {i+1}. {res['nombre']}")
                    st.write(f"📍 Desde {res['comuna_origen'].title()}: **{res['distancia_km']:.1f} km**")
                    st.write(f"💰 Copago: **{formatear_precio(res['copago'])}**")
                    st.write(f"🏥 Precio base: {formatear_precio(res['precio_base'])}")
                    st.write(f"🤝 {res['convenio']}")
                    
                    if "Con convenio" in res['convenio']:
                        st.success("🎉 ¡Tienes convenio aquí!")
                    elif "Sin convenio" in res['convenio']:
                        st.warning("⚠️ Sin convenio - copago más alto")
                    else:
                        st.info("🏥 Tarifa particular (Fonasa)")
                
                with col_horas:
                    st.markdown("**📅 Horas disponibles:**")
                    for opcion in res['opciones_hora']:
                        st.write(f"- 🕐 **{opcion['fecha']}** a las **{opcion['hora']}** hrs. con {opcion['medico']}")
                    
                    if res['url_reserva'] != "#":
                        st.link_button("📅 Reservar esta hora", res['url_reserva'], use_container_width=True)
                
                st.divider()
        
        # Mapa
        st.subheader("🗺️ Ubicación de los centros")
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
st.caption("🏥 Buscador de horas médicas - Muestra horas disponibles y profesionales | Prototipo Chile")