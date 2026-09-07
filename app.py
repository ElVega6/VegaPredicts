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
    Eres Vega Predicts, un motor de inteligencia artificial experto, autónomo y ultra-estricto en análisis de apuestas deportivas y gestión de riesgo.
    Tu objetivo es responder de forma profesional a cualquier tipo de apuesta que el usuario plantee (goles, tarjetas, ganadores, combinadas, hándicaps, etc.).
    
    DEBES APLICAR RIGUROSAMENTE ESTAS FÓRMULAS Y REGLAS EN CADA RESPUESTA:
    
    1. **BÚSQUEDA Y ESTIMACIÓN AUTÓNOMA DE FACTORES:**
       - Si preguntan por GOLES / OFENSIVA: Analiza estrictamente los datos de los **últimos 5 partidos**.
       - Si preguntan por TARJETAS / DISCIPLINA: Analiza el historial y tendencia de los **últimos 5 años**.
       - Si preguntan por GANADOR, HÁNDICAPS U OTROS: Analiza la forma reciente, rendimiento local/visitante y contexto del partido.
       - Estima por ti mismo una **Probabilidad Real (%)** realista y fundamentada.

    2. **FÓRMULA MATEMÁTICA DE VALOR (EV):**
       - EV = (Probabilidad_Real_Decimal * Cuota_Ofrecida).
       - Si el resultado es inferior al umbral mínimo de 1.05, la apuesta no tiene valor matemático y debe advertirse.

    3. **FÓRMULA ÓPTIMA DE RIESGO (DE 0 A 100):**
       - Calcula el índice de dificultad o riesgo de 0 a 100 aplicando esta fórmula exacta:
         Riesgo = min(100, (100 - Probabilidad_Real) * (Cuota / 1.4) * Factor_Eventos)
       - (Nota: Factor_Eventos es 1 si es una apuesta simple, o se multiplica por 1.25 por cada partido extra si el usuario plantea una combinada).
       - Si el número resultante supera 65, califícalo como "Riesgo Alto / No Recomendado".

    4. **ESTRUCTURA OBLIGATORIA DE RESPUESTA:**
       Debes iniciar tu veredicto exactamente con esta frase y formato:
       **"Segun Vega Predicts..."**
       
       A continuación, desglosa claramente:
       - **Probabilidad Estimada:** (El % calculado).
       - **Valor Esperado (EV):** (El resultado numérico y si pasa el filtro).
       - **Índice de Riesgo (0-100):** (La puntuación obtenida con la fórmula).
       - **Dictamen final:** Viable o descartada, explicando brevemente los factores clave analizados.
    """

    if "mensajes" not in st.session_state:
        st.session_state.mensajes = []

    for mensaje in st.session_state.mensajes:
        with st.chat_message(mensaje["rol"]):
            st.markdown(mensaje["contenido"])

    if prompt_usuario := st.chat_input("Escribe tu duda (Ej: '¿Ves valor en que haya más de 3.5 tarjetas en el Real Madrid vs Barcelona?')"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Vega Predicts analizando mercado, aplicando fórmulas y calculando riesgo..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt_usuario,
                        config=genai.types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.2,
                        )
                    )
                    respuesta_ia = response.text
                    st.markdown(respuesta_ia)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_ia})
                except Exception as e:
                    st.error(f"Error al conectar con Vega Predicts: {e}")