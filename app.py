import streamlit as st
from google import genai

st.set_page_config(page_title="Vega Predicts - AI Betting Engine", page_icon="📈", layout="centered")

st.title("📈 Vega Predicts: Asistente Autónomo de Apuestas")
st.markdown("Sistema inteligente de análisis de cuotas, cálculo de riesgo (0-100) y valor matemático bajo tus reglas.")

# Carga la clave de forma segura desde los secretos de Streamlit Cloud
try:
    CLAVE_API_DIRECTA = st.secrets["GOOGLE_API_KEY"]
except Exception:
    CLAVE_API_DIRECTA = ""

if not CLAVE_API_DIRECTA:
    st.error("⚠️ Falta configurar la GOOGLE_API_KEY en los Secrets de Streamlit Cloud.")
else:
    client = genai.Client(api_key=CLAVE_API_DIRECTA)
    
    system_prompt = rf"""
    Eres Vega Predicts, un motor de inteligencia artificial experto, autónomo y ultra-estricto en análisis de apuestas deportivas (fútbol, tenis, baloncesto, etc.) y gestión de riesgo.
    Tu objetivo es responder de forma profesional a cualquier tipo de apuesta que el usuario plantee (ganadores, sets, hándicaps, goles, totales, combinadas, etc.).
    
    DEBES APLICAR RIGUROSAMENTE ESTAS DIRECTRICES EN CADA RESPUESTA:
    
    1. **BÚSQUEDA Y SELECCIÓN INTELIGENTE DE DATOS:**
       - Tienes total libertad y autonomía para evaluar y seleccionar los mejores datos, estadísticas, superficies (en tenis), estados de forma recientes, h2h (enfrentamientos directos) o métricas avanzadas que consideres más convenientes para realizar el análisis más preciso posible.
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

    if prompt_usuario := st.chat_input("Escribe tu duda (Ej: '¿Ves valor en que Alcaraz gane en sets corridos?' o '¿Más de 2.5 goles?')"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Vega Predicts analizando mercado multideporte, aplicando fórmulas y calculando riesgo..."):
                # Lista de modelos a probar en orden si hay saturación (503)
                modelos_disponibles = ['gemini-3.6-flash', 'gemini-2.5-flash', 'gemini-1.5-flash']
                respuesta_ia = None
                ultimo_error = None

                for mod in modelos_disponibles:
                    try:
                        response = client.models.generate_content(
                            model=mod,
                            contents=prompt_usuario,
                            config=genai.types.GenerateContentConfig(
                                system_instruction=system_prompt,
                                temperature=0.2,
                            )
                        )
                        respuesta_ia = response.text
                        break # Si uno funciona, salimos del bucle con éxito
                    except Exception as e:
                        ultimo_error = e
                        continue # Si da error 503 u otro, prueba automáticamente el siguiente modelo

                if respuesta_ia:
                    st.markdown(respuesta_ia)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_ia})
                else:
                    st.error(f"Error temporal de alta demanda en los servidores de IA. Por favor, espera unos segundos e inténtalo de nuevo. Detalle técnico: {ultimo_error}")
