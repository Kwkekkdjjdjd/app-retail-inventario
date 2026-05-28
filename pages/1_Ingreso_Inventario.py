import requests # <--- ¡Agrega esto arriba del todo con tus otros import!

# ... (todo tu código anterior sigue igual) ...

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

# ... (el resto de tu tabla y gráficos sigue igual hacia abajo) ...