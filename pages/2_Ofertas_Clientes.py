import streamlit as st
import sqlite3
import pandas as pd

st.set_page_config(page_title="The Consumer App", layout="centered")

# --- SISTEMA DE SEGURIDAD: OCULTAR MENÚ PARA CLIENTES ---
st.markdown("""
    <style>
        [data-testid="collapsedControl"] {display: none;}
        [data-testid="stSidebar"] {display: none;}
    </style>
""", unsafe_allow_html=True)
# --------------------------------------------------------

# --- IMÁGENES A PRUEBA DE FALLOS (WIKIMEDIA COMMONS) ---
MAP_IMAGENES = {
    "vacuno": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Roast_beef_01.jpg/240px-Roast_beef_01.jpg",
    "carne": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5c/Roast_beef_01.jpg/240px-Roast_beef_01.jpg",
    "cerdo": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/74/Pork_chops_on_a_plate.jpg/240px-Pork_chops_on_a_plate.jpg",
    "queso": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Swiss_cheese_cube.jpg/240px-Swiss_cheese_cube.jpg",
    "leche": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Milk_glass.jpg/240px-Milk_glass.jpg",
    "fruta": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2f/Culinary_fruits_front_view.jpg/240px-Culinary_fruits_front_view.jpg",
    "jamon": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Sliced_ham.jpg/240px-Sliced_ham.jpg",
    "jamón": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/02/Sliced_ham.jpg/240px-Sliced_ham.jpg",
    "fallback": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Icon_product_box.svg/240px-Icon_product_box.svg.png"
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
                
                # --- COLUMNA 1: IMAGEN CON BUSCADOR INTELIGENTE ---
                with col1:
                    # Limpiamos el nombre: todo a minúsculas para que no importen las mayúsculas
                    nombre_prod = str(row['producto']).strip().lower()
                    url_img = MAP_IMAGENES["fallback"] # Imagen por defecto (la cajita)
                    
                    # Buscamos si alguna palabra clave está en el nombre del producto
                    for clave, url in MAP_IMAGENES.items():
                        if clave in nombre_prod:
                            url_img = url
                            break # Si encuentra una, deja de buscar
                            
                    st.image(url_img, width=80) 

                # --- COLUMNA 2: DETALLES Y PRECIO EN HTML INFALIBLE ---
                with col2:
                    st.markdown(f"### **{row['producto']}**")
                    st.caption(f"📍 {row['sucursal']} | SKU: `{row['lote']}`")
                    
                    # Usamos HTML puro. <del> tacha el texto. <span> le da color y negrita.
                    precio_html = f"<del>${row['precio_original']}</del> ➡️ <span style='color:red; font-weight:bold; font-size:1.1em;'>${row['precio_final']}</span>"
                    st.markdown(precio_html, unsafe_allow_html=True)
                    
                    st.progress(int(row['frescura_ia']))
                
                # --- COLUMNA 3: QR CODE ---
                with col3:
                    qr = f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data={row['lote']}"
                    st.image(qr)
except Exception as e:
    st.error(f"Error al cargar ofertas: {e}")