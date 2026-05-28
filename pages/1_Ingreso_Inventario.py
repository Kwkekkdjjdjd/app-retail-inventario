import streamlit as st
import requests
import sqlite3
import random
import pandas as pd
import numpy as np

# --- MATRIZ DE PARÁMETROS DE PRODUCTOS ---
MATRIZ_PARAMETROS = {
    "Carnes y Fiambres": (15, 2.0, "CARN"),
    "Lácteos y Quesos": (30, 4.0, "LACT"),
    "Frutas y Verduras": (15, 8.0, "VERD"),
    "Abarrotes secos": (180, 20.0, "ABAR")
}

# --- ESTRUCTURA ESPECÍFICA DE TU PROYECTO ---
ESTRUCTURA_NACIONAL = {
    "Región Metropolitana": {
        "Buin": ["Lider Buin", "Unimarc Camino El Arpa", "Super 10 Buin"],
        "Puente Alto": ["Lider Prieto Norte", "Jumbo Portal Puente Alto", "Tottus Concha y Toro"]
    },
    "Región de la Araucanía": {
        "Temuco": ["Jumbo Portal Temuco", "Lider Prieto Norte"]
    }
}

st.title("📦 Gestión de Inventario Crítico")
st.markdown("---")

col_titulo, col_boton = st.columns([2, 1])

with col_boton:
    with st.popover("➕ Ingresar Nuevo Lote", use_container_width=True):
        st.markdown("### Indexación por Lotes")
        
        # 1. Selección de Región
        reg_sel = st.selectbox("🌎 Región:", list(ESTRUCTURA_NACIONAL.keys()))
        
        # 2. Selección de Comuna (Buin o Puente Alto)
        comuna_sel = st.selectbox("🏙️ Comuna:", list(ESTRUCTURA_NACIONAL[reg_sel].keys()))
        
        # 3. Selección de Sucursal
        sucursal_sel = st.selectbox("🏪 Local:", ESTRUCTURA_NACIONAL[reg_sel][comuna_sel])
        
        categoria = st.selectbox("Categoría:", list(MATRIZ_PARAMETROS.keys()))
        
        with st.form("form_ingreso"):
            producto = st.text_input("Producto", placeholder="Ej: Jamón Cervecero")
            t_max, T_ideal, prefijo = MATRIZ_PARAMETROS[categoria]
            
            col1, col2 = st.columns(2)
            with col1:
                t_rest = st.number_input("Días para vencer", min_value=1, value=5)
                precio = st.number_input("Precio Normal ($)", min_value=100, value=2000)
            with col2:
                temp = st.number_input("Temp Actual (°C)", value=T_ideal)
                lote_generado = f"{prefijo}-{random.randint(1000, 9999)}"
                lote = st.text_input("Lote", value=lote_generado)
                
            if st.form_submit_button("Registrar en Comuna"):
                if producto != "":
                    # Lógica de cálculo matemático
                    f_t = (t_rest / t_max) * 100
                    p_t = 5 * (temp - T_ideal) if temp > T_ideal else 0
                    f_real = max(0, f_t - p_t)
                    desc = 80 if f_real < 15 else 50 if f_real < 40 else 20 if f_real < 70 else 0
                    p_final = int(precio * (1 - desc/100))
                    
                    try:
                        conn = sqlite3.connect("supermercado.db")
                        c = conn.cursor()
                        c.execute("""INSERT INTO inventario (region, comuna, sucursal, producto, lote, dias_vencer, temperatura, frescura_ia, descuento_aplicado, precio_original, precio_final) 
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                                  (reg_sel, comuna_sel, sucursal_sel, producto, lote, t_rest, temp, round(f_real,1), desc, precio, p_final))
                        conn.commit()
                        conn.close()
                        
                        st.success(f"¡Ingresado en {comuna_sel} con éxito!")
                        
                        # --- NUEVO SISTEMA DE ALERTA TELEGRAM ---
                        if desc == 80: # Solo avisa si el descuento es del 80% (Estado Crítico)
                            token = "8642739860:AAF41KlsMdPry3FAiLg-eyGA_U-pCvy0YJo"
                            chat_id = "6628445041"
                            mensaje = f"🚨 ¡ALERTA DE OFERTA FLASH!\n\n📦 Producto: {producto}\n🏪 Local: {sucursal_sel} ({comuna_sel})\n💰 Precio Rebajado: ${p_final} (80% OFF)\n⏱️ Frescura: Nivel Crítico. ¡Ven a rescatarlo ahora!"
                            
                            url = f"https://api.telegram.org/bot{token}/sendMessage?chat_id={chat_id}&text={mensaje}"
                            try:
                                requests.get(url)
                            except:
                                pass # Si falla el internet, no se cae la app
                        # ----------------------------------------
                        
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error BD: {e}")
                else:
                    st.warning("⚠️ Falta el nombre del producto.")

# --- TABLA DE MONITOREO ---
try:
    conn = sqlite3.connect("supermercado.db")
    # Traemos los datos con nombres de columnas limpios y con mayúscula
    query = "SELECT region AS Región, comuna AS Comuna, sucursal AS Sucursal, producto AS Producto, lote AS SKU, frescura_ia AS 'Frescura (%)' FROM inventario"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if not df.empty:
        # Aquí vuelve la magia: El semáforo de criticidad
        def semaforo(frescura):
            if frescura > 70: return "🟢 Óptimo"
            elif frescura >= 40: return "🟡 Cuidado"
            else: return "🔴 Crítico"
            
        df['Status'] = df['Frescura (%)'].apply(semaforo)
        
        # Mostramos la tabla escondiendo el índice (hide_index=True)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Inventario vacío. Haz clic en 'Ingresar Nuevo Lote' para comenzar.")
except Exception as e:
    st.error(f"Error al cargar la base de datos: {e}")

st.markdown("---")

# --- GRÁFICOS DE ANÁLISIS ---
col_graf, col_metricas = st.columns([2, 1])

with col_graf:
    st.subheader("📉 Vida Útil Remanente")
    dias = np.arange(0, 30)
    df_chart = pd.DataFrame({"Frescura (%)": np.maximum(0, 100 - (dias * (100/30)))}, index=dias)
    st.line_chart(df_chart, height=250)

with col_metricas:
    st.subheader("⚡ Descuentos Triggers")
    st.markdown("**0%** (Frescura > 70%)"); st.progress(100)
    st.markdown("**20%** (Frescura 40-70%)"); st.progress(70)
    st.markdown("**50%** (Frescura 15-40%)"); st.progress(40)
    st.markdown("**80%** (Frescura < 15%)"); st.progress(15)