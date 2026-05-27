import streamlit as st

st.set_page_config(page_title="IA Supermercado", layout="wide")

st.title("🍏 Sistema Inteligente Anti-Desperdicio")
st.write("Bienvenido al panel de control automatizado para la gestión de mermas y precios dinámicos.")
st.markdown("---")

st.info("👈 **Usa el menú lateral de la izquierda** para navegar entre las distintas secciones del sistema.")

# Un pequeño resumen de cómo funciona el negocio
st.subheader("¿Cómo opera el sistema?")
col1, col2, col3 = st.columns(3)
col1.metric("1. Recepción", "Ingreso de Lotes", "Inventario, Fechas y Temp.")
col2.metric("2. Cerebro IA", "Análisis de Frescura", "Predicción de Riesgo")
col3.metric("3. Automatización", "Precios en Cajas", "Sincronización Total")
