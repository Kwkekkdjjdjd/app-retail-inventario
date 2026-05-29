import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="The Consumer App", layout="centered")

# --- SISTEMA DE SEGURIDAD: OCULTAR MENÚ PARA CLIENTES ---
st.markdown("""
    <style>
        /* Oculta la flechita de arriba a la izquierda para abrir el menú */
        [data-testid="collapsedControl"] {display: none;}
        /* Oculta la barra lateral completa */
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)
# --------------------------------------------------------

# --- DICCIONARIO DE IMÁGENES DE PRODUCTOS (¡NUEVO!) ---
# Para que se vea super pro, mapearemos nombres de productos a URLs reales de imágenes.
MAP_IMAGENES = {
    # Categoría: Carnes
    "Vacuno": "https://images.pexels.com/photos/1018671/pexels-photo-1018671.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Cerdo": "https://images.pexels.com/photos/1572979/pexels-photo-1572979.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    # Categoría: Lácteos
    "Queso": "https://images.pexels.com/photos/1614742/pexels-photo-1614742.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    "Leche": "https://images.pexels.com/photos/159495/milk-products-bottles-glass-159495.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    # Categoría: Frutas
    "Fruta": "https://images.pexels.com/photos/1131688/pexels-photo-1131688.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
    # Genérico por si acaso
    "Fallback": "https://images.pexels.com/photos/4033282/pexels-photo-4033282.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
}

st.title("📱 The Consumer App")

# --- COORDENADAS PARA EL MAPA ---
COORD_COMUNAS = {
    "Buin": {"lat": -33.7328, "lon": -70.7437, "zoom": 13},
    "Puente Alto": {"lat": -33.5833, "lon": -70.5833, "zoom": 13}
}

ESTRUCTURA_LOCALES = {
    "Buin": ["Lider Buin", "Unimarc Camino El Arpa", "Super 10 Buin"],
    "Puente Alto": ["Lider Prieto Norte", "Jumbo Portal Puente Alto", "Tottus Concha y Toro"]
}

# 1. Filtro de Comuna (Tus sub-pestañas)
comuna_app = st.radio("📍 Selecciona tu comuna:", ["Buin", "Puente Alto"], horizontal=True)

# 2. Mapa centrado en la comuna
df_mapa = pd.DataFrame([COORD_COMUNAS[comuna_app]])
st.map(df_mapa, latitude='lat', longitude='lon', zoom=COORD_COMUNAS[comuna_app]["zoom"])

# 3. Filtro de sucursal dentro de la comuna
sucursal_app = st.selectbox("🏪 Filtrar por Local:", ["Todos los locales"] + ESTRUCTURA_LOCALES[comuna_app])

st.markdown("### 🛒 Ofertas en tu zona")

try:
    conn = sqlite3.connect("supermercado.db")
    query = f"SELECT * FROM inventario WHERE comuna = '{comuna_app}' AND descuento_aplicado > 0"
    df_ofertas = pd.read_sql_query(query, conn)
    conn.close()

    if sucursal_app != "Todos los locales":
        df_ofertas = df_ofertas[df_ofertas['sucursal'] == sucursal_app]

    if df_ofertas.empty:
        st.info(f"Sin ofertas críticas en {comuna_app} por ahora.")
    else:
        for _, row in df_ofertas.iterrows():
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 3, 1])
                
                # --- COLUMNA 1: IMAGEN REAL DEL PRODUCTO (¡ARREGLADO!) ---
                with col1:
                    # Buscaremos una imagen basada en la descripción del producto o su categoría (fallback)
                    # He añadido URLs de imágenes reales para Vacuno, Cerdo, Queso, Leche y Fruta.
                    url_imagen = MAP_IMAGENES.get(row['producto'].capitalize(), MAP_IMAGENES["Fallback"])
                    st.image(url_imagen, width=70) # Mostramos una imagen real de 70px de ancho

                # --- COLUMNA 2: DETALLES DEL PRODUCTO ---
                with col2:
                    st.markdown(f"### **{row['producto']}**")
                    st.caption(f"📍 {row['sucursal']} | SKU: `{row['lote']}`")
                    
                    # --- PRECIO ROTO Y ARREGLADO CON SINTAXIS TIGHT ---
                    # Para que se note bien, he tachado el precio original y el final es de color rojo y negrita.
                    # El truco es eliminar cualquier espacio invisible o extra para que el markdown funcione.
                    st.markdown(f"~~${row['precio_original']}~~ ➡️ **:red[${row['precio_final']}]**")
                    
                    st.progress(int(row['frescura_ia']))
                
                # --- COLUMNA 3: QR CODE ---
                with col3:
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={row['lote']}"
                    st.image(qr)
except Exception as e:
    # Añado la impresión del error para que sea más fácil depurar en el futuro
    st.error(f"Error al cargar ofertas: {e}")