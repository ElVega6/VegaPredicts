import streamlit as st
import time
from datetime import datetime
from google import genai
from google.genai import types

st.set_page_config(page_title="Vega Predicts - AI Betting Engine", page_icon="📈", layout="centered")

st.title("📈 Vega Predicts: Asistente Autónomo de Apuestas")
st.markdown("Sistema inteligente de análisis de cuotas, cálculo de riesgo (0-100) y valor matemático (Motor Gemini optimizado).")

# Carga la clave de forma segura desde los secretos de Streamlit Cloud
try:
    CLAVE_GEMINI = st.secrets["GEMINI_API_KEY"]
except Exception:
    CLAVE_GEMINI = ""

if not CLAVE_GEMINI:
    st.error("⚠️ Falta configurar la GEMINI_API_KEY en los Secrets de Streamlit Cloud.")
else:
    client = genai.Client(api_key=CLAVE_GEMINI)
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
    Eres Vega Predicts, un motor de inteligencia artificial experto, autónomo y ultra-estricto en análisis de apuestas deportivas (fútbol, tenis, etc.) y gestión de riesgo.
    
    DIRECTRICES DE OPERACIÓN Y CONTEXTO CRÍTICO:
    - Te encuentras operando en la temporada actual (septiembre de 2026, jornada 1 de la Fase de Liga de la UEFA Champions League 2026/2027).
    - REGLA SUPREMA Y ANTIEXCUSAS: Tienes prohibido absoluto mencionar fechas de corte de conocimiento, decir que no tienes datos o recomendar consultar casas externas. Eres un analista autónomo en tiempo real. Utiliza el calendario real de la UEFA Champions League de septiembre de 2026 para realizar análisis rigurosos basados en datos reales de los equipos.

    DEBES APLICAR RIGUROSAMENTE ESTAS DIRECTRICES EN CADA RESPUESTA:
    
    1. **BÚSQUEDA Y SELECCIÓN INTELIGENTE DE DATOS:**
       - Evalúa con total autonomía los partidos oficiales reales de la competición, estados de forma y selecciones solicitadas.
       - Estima por ti mismo una **Probabilidad Real (%)** realista y fundamentada.

    2. **FÓRMULA MATEMÁTICA DE VALOR (EV):**
       - EV = (Probabilidad_Real_Decimal * Cuota_Ofrecida).
       - Si el resultado es inferior al umbral mínimo de 1.05, la apuesta no tiene valor matemático y debe advertirse claramente.

    3. **FÓRMULA ÓPTIMA DE RIESGO (DE 0 A 100):**
       - Calcula el índice de dificultad o riesgo de 0 a 100 aplicando esta fórmula exacta:
         Riesgo = min(100, (100 - Probabilidad_Real) * (Cuota / 1.4) * Factor_Eventos)
       - (Nota: Factor_Eventos es 1 si es una apuesta simple, o se multiplica por 1.25 por cada partido/selección extra si el usuario plantea una combinada).
       - Si el número resultante supera 65, califícalo como "Riesgo Alto / No Recomendado".

    4. **ESTRUCTURA OBLIGATORIA DE RESPUESTA Y MULETILLAS:**
       Debes integrar de manera fluida y natural la identidad de la marca utilizando muletillas corporativas (por ejemplo: *"En Vega Predicts creemos que..."*, *"Nuestro algoritmo en Vega Predicts ha detectado que..."*, *"Para nuestro equipo en Vega Predicts..."*).
       
       Estructura tu veredicto claramente desglosando:
       - **Probabilidad Estimada:** (El % calculado).
       - **Valor Esperado (EV):** (El resultado numérico y si pasa el filtro).
       - **Índice de Riesgo (0-100):** (La puntuación obtenida con la fórmula).
       - **Dictamen final:** Viable o descartada, explicando de forma experta los factores clave analizados.
    """

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    if prompt_usuario := st.chat_input("Escribe tu duda (Ej: 'Recomiéndame una combinada a cuota 4 para la Champions')"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Vega Predicts analizando mercados con Gemini..."):
                respuesta_ia = None
                ultimo_error = None
                
                # Historial optimizado para evitar desbordamientos o bloqueos por longitud
                contents_historial = []
                for m in st.session_state.mensajes[-15:]:  # Mantiene los últimos 15 intercambios limpios
                    role_gemini = "user" if m["rol"] == "user" else "model"
                    contents_historial.append(
                        types.Content(
                            role=role_gemini,
                            parts=[types.Part.from_text(text=m["contenido"])]
                        )
                    )

                for intento in range(3):
                    try:
                        response = client.models.generate_content(
                            model="gemini-3.7-flash",
                            contents=contents_historial,
                            config=types.GenerateContentConfig(
                                system_instruction=system_prompt,
                                temperature=0.1,
                                max_output_tokens=2048,
                            ),
                        )
                        respuesta_ia = response.text
                        break
                    except Exception as e:
                        ultimo_error = e
                        time.sleep(3)
                if respuesta_ia:
                    st.markdown(respuesta_ia)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_ia})
                else:
                    st.error(f"Error al conectar con Gemini: {ultimo_error}")
