import streamlit as st
import time
from datetime import datetime
from groq import Groq

st.set_page_config(page_title="Vega Predicts - AI Betting Engine", page_icon="📈", layout="centered")

st.title("📈 Vega Predicts: Asistente Autónomo de Apuestas")
st.markdown("Sistema inteligente de análisis de cuotas, cálculo de riesgo (0-100) y valor matemático bajo tus reglas.")

# Carga la clave de forma segura desde los secretos de Streamlit Cloud
try:
    CLAVE_GROQ = st.secrets["GROQ_API_KEY"]
except Exception:
    CLAVE_GROQ = ""

if not CLAVE_GROQ:
    st.error("⚠️ Falta configurar la GROQ_API_KEY en los Secrets de Streamlit Cloud.")
else:
    client = Groq(api_key=CLAVE_GROQ)
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d")

    system_prompt = f"""
    Eres Vega Predicts, un motor de inteligencia artificial experto, autónomo y ultra-estricto en análisis de apuestas deportivas (fútbol, tenis, etc.) y gestión de riesgo.
    
    INFORMACIÓN DE CONTEXTO TEMPORAL CRÍTICA:
    - La fecha actual es: {fecha_actual}. 
    - Te encuentras en la temporada deportiva actual (septiembre de 2026, jornada 1 de la Fase de Liga de la UEFA Champions League 2026/2027 y torneos vigentes).
    - EXIGENCIA DE PRECISIÓN ABSOLUTA EN CALENDARIOS: Está totalmente prohibido inventar emparejamientos, jornadas o fechas. Contrastar estrictamente con los calendarios reales de la competición en curso.

    DEBES APLICAR RIGUROSAMENTE ESTAS DIRECTRICES EN CADA RESPUESTA:
    
    1. **BÚSQUEDA Y SELECCIÓN INTELIGENTE DE DATOS:**
       - Tienes total libertad y autonomía para evaluar y seleccionar los mejores datos, estadísticas, superficies (en tenis), estados de forma recientes, h2h o métricas avanzadas.
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
            with st.spinner("Vega Predicts procesando con Groq..."):
                respuesta_ia = None
                ultimo_error = None
                
                historial_mensajes = [{"role": "system", "content": system_prompt}]
                for m in st.session_state.mensajes:
                    rol_groq = "user" if m["rol"] == "user" else "assistant"
                    historial_mensajes.append({"role": rol_groq, "content": m["contenido"]})

                for intento in range(3):
                    try:
                        completion = client.chat.completions.create(
                            model="openai/gpt-oss-20b",
                            messages=historial_mensajes,
                            temperature=0.1,
                            max_tokens=2048,
                        )
                        respuesta_ia = completion.choices[0].message.content
                        break
                    except Exception as e:
                        ultimo_error = e
                        time.sleep(2)

                if respuesta_ia:
                    st.markdown(respuesta_ia)
                    st.session_state.mensajes.append({"rol": "assistant", "contenido": respuesta_ia})
                else:
                    st.error(f"Error al conectar con Groq: {ultimo_error}")
