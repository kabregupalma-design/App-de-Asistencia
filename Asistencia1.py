import streamlit as st  
from datetime import datetime
import pandas as pd
from geopy.distance import geodesic
from PIL import Image, ImageDraw
import os  
from st_gsheets_connection import GSheetsConnection

# 1. Configurar conexión con Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

st.set_page_config(page_title="Control de Asistencia", page_icon="📌")
st.title("⏰ Control de Asistencia")

tiempo_actual = datetime.now()
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
    "Centro 1001": {"lat": -12.065420573231364, "lon": -77.01356266011081, "radio_m": 3}
    #"Centro 701": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 520": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 342": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 333": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50}
}


query_params = st.query_params #conectar el GPS del navegador con tu código de Python
lat_val = st.query_params.get("lat") if "lat" in st.query_params else None
lon_val = st.query_params.get("lon") if "lon" in st.query_params else None

# Calcular distancia GPS en metros entre la tienda y el celular
coords_tienda = (TIENDAS_GEO[tienda_sel]["lat"], TIENDAS_GEO[tienda_sel]["lon"])
distancia = geodesic(coords_tienda, (lat_val, lon_val)).meters

if distancia > TIENDAS_GEO[tienda_sel]["radio_m"]:
    st.error(f"⛔ Estás a {distancia:.1f}m. Debes estar a menos de {TIENDAS_GEO[tienda_sel]['radio_m']}m de la tienda.")
else:
    # Generar fecha y hora
    ahora = datetime.now()
    fecha, hora = ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")

#Botón de envio
if st.button("📩 Enviar Registro", type="primary", use_container_width=True):
    if lat_val is None or lon_val is None:
        st.error(
            "⚠️ No se ha detectado tu ubicación GPS. Espera a que cargue antes de enviar."
        )
    else:
        try:
            # Leer los datos existentes en la hoja
            datos_existentes = conn.read(ttl=0)

            # Crear la nueva fila con los datos ingresados
            nuevo_registro = pd.DataFrame(
                [
                    {
                        "Fecha": ahora.strftime("%d/%m/%Y"),
                        "Hora": ahora.strftime("%H:%M:%S"),
                        "Usuario": usuario_sel,
                        "Tienda": tienda_sel,
                        "Tipo": tipo_registro,
                        "Latitud": lat_val,
                        "Longitud": lon_val,
                    }
                ]
            )

            # Combinar datos anteriores con la nueva fila
            df_actualizado = pd.concat(
                [datos_existentes, nuevo_registro], ignore_index=True
            )

            # Actualizar la hoja en Google Sheets
            conn.update(data=df_actualizado)

            st.success(
                f"✅ ¡Asistencia de {usuario_sel} ({tipo_registro}) registrada en Google Sheets!"
            )
            st.balloons()
        except Exception as e:
            st.error(f"❌ Ocurrió un error al guardar en Google Sheets: {e}")
