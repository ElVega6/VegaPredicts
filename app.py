import streamlit as st
from datetime import datetime
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
    
    # Obtenemos la fecha actual exacta para inyectarla en el prompt de la IA
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    system_prompt = rf"""
    Eres Vega Predicts, un motor de inteligencia artificial experto, autónomo y ultra-estricto en análisis de apuestas deportivas (fútbol, tenis, baloncesto, etc.) y gestión de riesgo.
    
    INFORMACIÓN DE CONTEXTO TEMPORAL CRÍTICA:
    - La fecha actual es: {fecha_actual}. 
    - Te encuentras en la temporada futbolística actual (por ejemplo, septiembre de 2026, coincidiendo con el arranque de la Jornada 1 de la Fase de Liga de la UEFA Champions League 2026/2027).
    - EXIGENCIA DE PRECISIÓN ABSOLUTA EN CALENDARIOS: Está totalmente prohibido inventar emparejamientos, jornadas pasadas o fechas falsas. Si el usuario te pregunta por partidos o jornadas oficiales actuales (como Champions League), debes contrastar mentalmente que los equipos correspondan estrictamente a los calendarios reales de la competición en curso. Si tienes dudas sobre un emparejamiento exacto, adviérteme o limítate a analizar con rigor los datos reales.

    DEBES APLICAR RIGUROSAMENTE ESTAS DIRECTRICES EN CADA RESPUESTA:
    
    1. **BÚSQUEDA Y SELECCIÓN INTELIGENTE DE DATOS:**
       - Tienes total libertad y autonomía para evaluar y seleccionar los mejores datos, estadísticas, superficies (en tenis), estados de forma recientes, h2h (enfrentamientos directos) o métricas avanzadas que consideres más convenientes.
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

    if prompt_usuario := st.chat_input("Escribe tu duda (Ej: '¿Ves valor en la victoria del Real Madrid contra el Inter en Champions?')"):
        st.session_state.mensajes.append({"rol": "user", "contenido": prompt_usuario})
        with st.chat_message("user"):
            st.markdown(prompt_usuario)

        with st.chat_message("assistant"):
            with st.spinner("Vega Predicts contrastando calendario oficial, aplicando fórmulas y calculando riesgo..."):
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt_usuario,
                        config=genai.types.GenerateContentConfig(
                            system_instruction=system_prompt,
                            temperature=0.1, # Temperatura más baja para forzar mayor precisión y rigor analítico
                        )
                    )
                    respuesta_ia = response.text
                    st.markdown(respuesta_ia)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_ia})
                except Exception as e:
                    st.error(f"Error al conectar con Vega Predicts: {e}")
