import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types

st.set_page_config(page_title="Vega Predicts - AI Betting Engine", page_icon="📈", layout="centered")

st.title("📈 Vega Predicts: Asistente Autónomo de Apuestas")
st.markdown("Motor de inteligencia artificial con búsqueda web en tiempo real y análisis de valor matemático.")

# Carga la clave de forma segura desde los secretos de Streamlit Cloud
try:
    CLAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
except Exception:
    CLAVE_GEMINI = ""

if not CLAVE_GEMINI:
    st.error("⚠️ Falta configurar la GEMINI_API_KEY en los Secrets de Streamlit Cloud.")
else:
    client = genai.Client(api_key=CLAVE_GEMINI)
    
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
    Eres Vega Predicts, un motor de inteligencia artificial experto, autónomo y ultra-estricto en análisis de apuestas deportivas (fútbol, tenis, etc.) y gestión de riesgo. Hoy es {fecha_hoy}.
    
    MISIÓN Y CAPACIDAD AUTÓNOMA:
    - Tienes la capacidad y la obligación de **buscar activamente en la web en tiempo real** los partidos, calendarios, cuotas de mercado aproximadas y estados de forma de los equipos o tenistas para la fecha actual.
    - El usuario **no** tiene que darte las cuotas ni los partidos obligatoriamente; si te pide un objetivo (por ejemplo: "Recomiéndame una combinada a cuota 4 de menor riesgo para hoy"), **debes buscar los encuentros reales que se disputan hoy**, seleccionar los mercados óptimos, estimar las cuotas de mercado y estructurar la combinada tú mismo.
    
    DIRECTRICES DE OPERACIÓN Y CÁLCULO:
    1. **BÚSQUEDA Y SELECCIÓN INTELIGENTE:** Utiliza la herramienta de búsqueda para escanear la jornada actual de la competición solicitada (fútbol, tenis, etc.).
    2. **FÓRMULA DE VALOR (EV):** EV = (Probabilidad_Real_Decimal * Cuota_Estimada_Mercado). Debe superar el umbral mínimo de 1.05.
    3. **FÓRMULA ÓPTIMA DE RIESGO (0-100):** 
       Riesgo = min(100, (100 - Probabilidad_Real) * (Cuota / 1.4) * Factor_Eventos)
       *(Factor_Eventos: 1 para simples, o se multiplica por 1.25 por cada selección extra en combinadas).* Si supera 65, se considera riesgo alto.
    4. **ESTRUCTURA DE RESPUESTA Y MULETILLAS:**
       Integra la identidad de marca (ej. *"En Vega Predicts hemos escaneado los mercados de hoy y..."*).
       Desglosa obligatoriamente:
       - **Partidos y Selecciones elegidas de forma autónoma.**
       - **Probabilidad Estimada y Cuota de Mercado.**
       - **Valor Esperado (EV).**
       - **Índice de Riesgo (0-100).**
       - **Dictamen final:** Viable o descartada con justificación experta.
    """

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    if st.sidebar.button("🧹 Limpiar Historial de Chat"):
        st.session_state.mensajes = []
        st.rerun()

    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    if prompt_usuario := st.chat_input("Ej: 'Búscame la mejor combinada a cuota 4 de menor riesgo para hoy'"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Vega Predicts escaneando la web, analizando calendarios y calculando riesgos..."):
                respuesta_ia = None
                ultimo_error = None
                
                contents_historial = []
                for m in st.session_state.mensajes[-10:]:
                    rol = "user" if m["rol"] == "user" else "model"
                    contents_historial.append(
                        types.Content(
                            role=rol,
                            parts=[types.Part.from_text(text=m["contenido"])]
                        )
                    )

                for intento in range(3):
                    try:
                        # Activamos la herramienta de búsqueda web (Google Search) para autonomía total
                        response = client.models.generate_content(
                            model="gemini-3.7-flash",
                            contents=contents_historial,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt,
                                tools=[{"google_search": {}}],  # <--- ESTO PERMITE BUSCAR EN DIRECTO EN INTERNET
                                temperature=0.1,
                                max_output_tokens=2048,
                            ),
                        )
                        if response and response.text:
                            respuesta_ia = response.text
                            break
                    except Exception as e:
                        ultimo_error = e
                        time.sleep(2)

                if respuesta_ia:
                    st.markdown(respuesta_ia)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_ia})
                else:
                    st.error(f"Error al conectar con el motor de búsqueda de Gemini: {ultimo_error}")
