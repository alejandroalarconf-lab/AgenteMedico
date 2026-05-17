# =============================================================================
# agente_consola.py
# Simulador de buscador de horas médicas en Chile
# DESARROLLADO PARA PYTHON 3 EN VISUAL STUDIO CODE (WINDOWS)
# VERSIÓN CON SELECCIÓN DE ORDEN POR EL USUARIO
# =============================================================================

import random
from geopy.distance import geodesic

# =============================================================================
# DATOS DE CENTROS MÉDICOS
# =============================================================================

CENTROS_MEDICOS = [
    {
        "nombre": "Clínica Las Condes",
        "comuna": "Las Condes",
        "coordenadas": (-33.4100, -70.5720),
        "precios": {
            "medicina general": 48000,
            "traumatología":    95000,
            "oftalmología":     78000,
            "dermatología":     88000,
        },
    },
    {
        "nombre": "Clínica Alemana",
        "comuna": "Vitacura",
        "coordenadas": (-33.3920, -70.5780),
        "precios": {
            "medicina general": 50000,
            "traumatología":    98000,
            "oftalmología":     80000,
            "dermatología":     90000,
        },
    },
    {
        "nombre": "RedSalud",
        "comuna": "Providencia",
        "coordenadas": (-33.4330, -70.6150),
        "precios": {
            "medicina general": 32000,
            "traumatología":    62000,
            "oftalmología":     52000,
            "dermatología":     57000,
        },
    },
    {
        "nombre": "Integramédica",
        "comuna": "Santiago Centro",
        "coordenadas": (-33.4520, -70.6480),
        "precios": {
            "medicina general": 30000,
            "traumatología":    60000,
            "oftalmología":     50000,
            "dermatología":     55000,
        },
    },
    {
        "nombre": "Clínica UC Christus",
        "comuna": "Providencia",
        "coordenadas": (-33.4360, -70.6300),
        "precios": {
            "medicina general": 45000,
            "traumatología":    88000,
            "oftalmología":     72000,
            "dermatología":     80000,
        },
    },
    {
        "nombre": "Clínica Santa María",
        "comuna": "Providencia",
        "coordenadas": (-33.4260, -70.6230),
        "precios": {
            "medicina general": 42000,
            "traumatología":    82000,
            "oftalmología":     68000,
            "dermatología":     75000,
        },
    },
    {
        "nombre": "Clínica Indisa",
        "comuna": "Providencia",
        "coordenadas": (-33.4250, -70.6200),
        "precios": {
            "medicina general": 38000,
            "traumatología":    72000,
            "oftalmología":     60000,
            "dermatología":     65000,
        },
    },
]

# =============================================================================
# TABLA DE CONVENIOS POR ISAPRE
# =============================================================================

CONVENIOS = {
    "banmédica":   ["Clínica Las Condes", "Clínica Alemana", "Clínica Indisa"],
    "colmena":     ["Clínica UC Christus", "Integramédica"],
    "cruz blanca": ["Clínica Santa María", "RedSalud"],
    "consalud":    ["Integramédica", "Clínica Indisa"],
}

# =============================================================================
# COORDENADAS DE LAS COMUNAS DEL USUARIO
# =============================================================================

COMUNAS_USUARIO = {
    "providencia":      (-33.437, -70.650),
    "las condes":       (-33.400, -70.565),
    "ñuñoa":            (-33.457, -70.600),
    "santiago centro":  (-33.440, -70.650),
}

# =============================================================================
# RANGOS DE DÍAS DE ESPERA POR ESPECIALIDAD
# =============================================================================

DIAS_ESPERA = {
    "medicina general": (2, 10),
    "traumatología":    (10, 30),
    "oftalmología":     (5, 20),
    "dermatología":     (15, 45),
}

ISAPRES_VALIDAS = list(CONVENIOS.keys())
ESPECIALIDADES_VALIDAS = list(DIAS_ESPERA.keys())


# =============================================================================
# FUNCIÓN: formatear_precio
# =============================================================================

def formatear_precio(valor: int) -> str:
    return f"${valor:,.0f}".replace(",", ".")


# =============================================================================
# FUNCIÓN: pedir_input_valido
# =============================================================================

def pedir_input_valido(prompt: str, opciones: list, nombre: str) -> str:
    while True:
        valor = input(prompt).strip().lower()
        if valor in opciones:
            return valor
        print(f"\n  ⚠️  '{valor}' no es un/a {nombre} válido/a.")
        print(f"      Opciones disponibles: {', '.join(opciones)}")
        print()


# =============================================================================
# FUNCIÓN NUEVA: pedir_orden
# Pregunta al usuario cómo quiere ordenar los resultados
# =============================================================================

def pedir_orden() -> str:
    print("\n  📊 ¿Cómo quieres ordenar los resultados?")
    print("      1️⃣  Más cercano primero (menor distancia)")
    print("      2️⃣  Más barato primero (menor copago)")
    print("      3️⃣  Balanceado (recomendado: distancia + copago + espera)")
    
    while True:
        opcion = input("\n  ➤ Elige 1, 2 o 3: ").strip()
        if opcion in ["1", "2", "3"]:
            return opcion
        print("  ⚠️  Opción no válida. Elige 1, 2 o 3.")


# =============================================================================
# FUNCIÓN: buscar_horas (modificada para aceptar criterio de orden)
# =============================================================================

def buscar_horas(especialidad: str, comuna: str, isapre: str, criterio: str) -> None:
    coord_usuario = COMUNAS_USUARIO[comuna]
    clinicas_isapre = CONVENIOS[isapre]

    resultados = []

    for centro in CENTROS_MEDICOS:
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
            "nombre":           centro["nombre"],
            "distancia_km":     distancia_km,
            "copago":           copago,
            "precio_base":      precio_base,
            "dias_espera":      dias_espera,
            "convenio":         etiqueta_convenio,
        })

    # --- ORDENAR SEGÚN CRITERIO DEL USUARIO ---
    if criterio == "1":  # Más cercano
        resultados.sort(key=lambda x: (round(x["distancia_km"], 1), x["copago"], x["dias_espera"]))
        nombre_criterio = "📍 Más cercano primero"
    elif criterio == "2":  # Más barato
        resultados.sort(key=lambda x: (x["copago"], round(x["distancia_km"], 1), x["dias_espera"]))
        nombre_criterio = "💰 Más barato primero"
    else:  # criterio == "3" Balanceado
        # Fórmula de balance: normalizamos distancia (0-10 km aprox) y copago (0-100k aprox)
        resultados.sort(key=lambda x: (
            (x["distancia_km"] * 0.4) + (x["copago"] / 10000) + (x["dias_espera"] * 0.2)
        ))
        nombre_criterio = "⚖️ Balanceado (distancia + copago + espera)"

    # --- Mostrar resultados ---
    print("\n" + "=" * 55)
    print(f"  🔍 Resultados para: {especialidad.title()}")
    print(f"     Comuna: {comuna.title()} | Isapre: {isapre.title()}")
    print(f"     Orden: {nombre_criterio}")
    print("=" * 55)

    for i, r in enumerate(resultados[:4], start=1):
        print(f"\n  {i}. {r['nombre']}")
        print(f"     📍 Distancia:   {r['distancia_km']:.1f} km")
        print(f"     💰 Copago:      {formatear_precio(r['copago'])}")
        print(f"     ⏱️  Espera:      {r['dias_espera']} días")
        print(f"     🏥 Precio base: {formatear_precio(r['precio_base'])}")
        print(f"     🤝 Convenio:    {r['convenio']}")

    print("\n" + "=" * 55)


# =============================================================================
# FUNCIÓN: mostrar_bienvenida
# =============================================================================

def mostrar_bienvenida() -> None:
    print("\n" + "=" * 55)
    print("   🏥  BUSCADOR DE HORAS MÉDICAS EN CHILE  🏥")
    print("=" * 55)
    print("""
  Este simulador te ayuda a encontrar horas médicas
  en clínicas de Santiago según tu:
    • Especialidad requerida
    • Comuna donde te encuentras
    • Isapre con la que cotizas

  AHORA TÚ DECIDES CÓMO ORDENAR LOS RESULTADOS:
    1️⃣  Más cercano (para emergencias o si no tienes auto)
    2️⃣  Más barato (para ahorrar dinero)
    3️⃣  Balanceado (lo mejor de ambos mundos)

  Se muestran las 4 mejores opciones disponibles.
""")
    print("=" * 55)


# =============================================================================
# FUNCIÓN: main
# =============================================================================

def main() -> None:
    mostrar_bienvenida()

    continuar = True

    while continuar:
        print()

        # --- Pedir especialidad ---
        print("  📋 Especialidades disponibles:")
        for esp in ESPECIALIDADES_VALIDAS:
            print(f"     • {esp}")
        especialidad = pedir_input_valido(
            "\n  ➤ Ingresa la especialidad: ",
            ESPECIALIDADES_VALIDAS,
            "especialidad",
        )

        # --- Pedir comuna ---
        print("\n  📍 Comunas disponibles:")
        for com in COMUNAS_USUARIO:
            print(f"     • {com.title()}")
        comuna = pedir_input_valido(
            "\n  ➤ Ingresa tu comuna: ",
            list(COMUNAS_USUARIO.keys()),
            "comuna",
        )

        # --- Pedir Isapre ---
        print("\n  🏦 Isapres disponibles:")
        for isa in ISAPRES_VALIDAS:
            print(f"     • {isa.title()}")
        isapre = pedir_input_valido(
            "\n  ➤ Ingresa tu Isapre: ",
            ISAPRES_VALIDAS,
            "Isapre",
        )

        # --- NUEVO: Pedir criterio de orden ---
        criterio = pedir_orden()

        # --- Realizar búsqueda y mostrar resultados ---
        buscar_horas(especialidad, comuna, isapre, criterio)

        # --- Preguntar si el usuario desea hacer otra búsqueda ---
        respuesta = input("\n  ¿Otra búsqueda? (s/n): ").strip().lower()
        continuar = respuesta == "s"

    print("\n  👋 ¡Hasta pronto! Cuídate mucho.\n")


# =============================================================================
# PUNTO DE ENTRADA DEL SCRIPT
# =============================================================================

if __name__ == "__main__":
    main()