import streamlit as st  
from datetime import datetime
from streamlit_js_eval import get_geolocation
import pytz
import pandas as pd
from geopy.distance import geodesic
#from PIL import Image, ImageDraw
#import os  
from streamlit_gsheets import GSheetsConnection
import streamlit.components.v1 as components

# Configurar zona horaria local
zona_horaria = pytz.timezone('America/Lima') # Cambia según tu país (ej: 'America/Bogota')

# 1. Configurar conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title="Control de Asistencia", page_icon="📌")
st.title("⏰ Control de Asistencia")

tiempo_actual = datetime.now(zona_horaria)
fecha_hora_texto = tiempo_actual.strftime("%d/%m/%Y - %I:%M:%S %p")
st.markdown(f"### 📅 **Fecha y Hora:** `{fecha_hora_texto}`")
st.divider()

col1, col2 = st.columns(2)
tiendas = ["Centro 1001", "Centro 701", "Centro 520", "Centro 342", "Centro 333", "Torre 605", "Torre 603"]
usuarios = ["Ylda", "Elizabeth", "Consuelo", "Tonny", "Jenny", "Vicky"]

with col1:
    tienda_sel = st.selectbox(
        "🏪 Selecciona la Tienda:", tiendas
    )
    
with col2:
    usuario_sel = st.selectbox(
        "👤 Selecciona el Usuario:", usuarios
    )
    
    
tipo_registro = st.radio(
    "📌 Tipo de Registro:", ["Entrada", "Salida"], horizontal=True
)

st.divider()

# Solicitar y capturar la ubicación GPS del navegador
TIENDAS_GEO = {
    #"Torre 605": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Torre 603": {"lat": -12.075123, "lon": -77.081456, "radio_m": 50},
    "Centro 1001": {"lat": -12.065434, "lon": -77.013456, "radio_m": 3}
    #"Centro 701": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 520": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 342": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 333": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50}
}

# Obtener geolocalización nativa del dispositivo
loc = get_geolocation()

lat_val, lon_val = None, None
distancia_calculada = None

if loc and 'coords' in loc:
    lat_val = loc['coords']['latitude']
    lon_val = loc['coords']['longitude']
    
    coords_tienda = (TIENDAS_GEO[tienda_sel]["lat"], TIENDAS_GEO[tienda_sel]["lon"])
    distancia_calculada = geodesic(coords_tienda, (lat_val, lon_val)).meters

    if distancia_calculada > TIENDAS_GEO[tienda_sel]["radio_m"]:
        st.error(f"⛔ Estás a {distancia_calculada:.1f}m. Debes estar a menos de {TIENDAS_GEO[tienda_sel]['radio_m']}m de la tienda.")
    else:
        st.success(f"📍 Ubicación confirmada. Estás a {distancia_calculada:.1f}m de la tienda.")
else:
    st.info("🌐 Obteniendo señal GPS... Si tu navegador solicita permiso, presiona 'Permitir'.")

# Botón de envío
if st.button("📩 Enviar Registro", type="primary", use_container_width=True):
    if not lat_val or not lon_val:
        st.error("⚠️ No se ha detectado tu ubicación GPS. Espera unos segundos a que el navegador lea las coordenadas.")
    elif distancia_calculada is not None and distancia_calculada > TIENDAS_GEO[tienda_sel]["radio_m"]:
        st.error("⛔ No puedes registrar asistencia fuera del rango permitido.")
    else:
        try:
            ahora = datetime.now(zona_horaria)
            datos_existentes = conn.read(ttl=0)

            nuevo_registro = pd.DataFrame(
                [
                    {
                        "Fecha": ahora.strftime("%d/%m/%Y"),
                        "Hora": ahora.strftime("%I:%M:%S %p"),
                        "Usuario": usuario_sel,
                        "Tienda": tienda_sel,
                        "Tipo": tipo_registro,
                        "Latitud": lat_val,
                        "Longitud": lon_val,
                    }
                ]
            )

            df_actualizado = pd.concat([datos_existentes, nuevo_registro], ignore_index=True)
            conn.update(data=df_actualizado)

            st.success(f"✅ ¡Asistencia de {usuario_sel} ({tipo_registro}) registrada en Google Sheets!")
            st.balloons()
        except Exception as e:
            st.error(f"❌ Ocurrió un error al guardar en Google Sheets: {e}")
