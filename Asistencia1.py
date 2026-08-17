import streamlit as st  
from datetime import datetime
import pandas as pd
from geopy.distance import geodesic
from PIL import Image, ImageDraw
import os  

st.set_page_config(page_title="Control de Asistencia", page_icon="📌")
st.title("⏰ Control de Asistencia")

TIENDAS = {
    #"Torre 605": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Torre 603": {"lat": -12.075123, "lon": -77.081456, "radio_m": 50},
    "Centro 1001": {"lat": -12.065420573231364, "lon": -77.01356266011081, "radio_m": 3}
    #"Centro 701": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 520": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 342": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50},
    #"Centro 333": {"lat": -12.046374, "lon": -77.042793, "radio_m": 50}
}

USUARIOS = {
    "Ylda",
    "Elizabeth",
    "Consuelo",
    "Tonny",
    "Jenny",
    "Vicky"
}


# Solicitar y capturar la ubicación GPS del navegador
#query_params = st.query_params #conectar el GPS del navegador con tu código de Python
#user_lat, user_lon = query_params.get("lat"), query_params.get("lon")
lat_val = st.query_params.get("lat") if "lat" in st.query_params else None
lon_val = st.query_params.get("lon") if "lon" in st.query_params else None

if not lat_val or not lon_val:
    st.info("📍 Para continuar, activa tu ubicación GPS.")
    html_geo = """
    <script>
function getGPS() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function(position) {
            // El cambio clave está en usar 'window.top' para recargar la ventana principal
            const url = new URL(window.top.location.href);
            url.searchParams.set('lat', position.coords.latitude);
            url.searchParams.set('lon', position.coords.longitude);
            window.top.location.href = url.href;
        }, function(err) {
            alert('Por favor autoriza el acceso al GPS en tu navegador.');
        }, { enableHighAccuracy: true });
    } else {
        alert('Tu navegador no soporta geolocalización.');
    }
}
</script>
    """
    st.components.v1.html(html_geo, height=80)
    st.stop()

u_lat, u_lon = float(lat_val), float(lon_val)

#Diseñar el formulario y la captura de foto
usuario_sel = st.selectbox("Selecciona tu nombre", USUARIOS)
tienda_sel = st.selectbox("Selecciona la tienda", list(TIENDAS.keys()))
tipo_registro = st.radio("Acción", ["Entrada", "Salida Almuerzo", "Regreso Almuerzo", "Salida"], horizontal=True)
foto_camara = st.camera_input("Toma una foto de evidencia")

#Validar distancia, estampar la foto y guardar el registro
if st.button("🚀 Registrar Asistencia"):
    
    #if not foto_camara:
    #    st.error("⚠️ La foto es obligatoria para marcar.")
    #    st.stop()

    # Calcular distancia GPS en metros entre la tienda y el celular
    coords_tienda = (TIENDAS[tienda_sel]["lat"], TIENDAS[tienda_sel]["lon"])
    distancia = geodesic(coords_tienda, (u_lat, u_lon)).meters

    if distancia > TIENDAS[tienda_sel]["radio_m"]:
        st.error(f"⛔ Estás a {distancia:.1f}m. Debes estar a menos de {TIENDAS[tienda_sel]['radio_m']}m de la tienda.")
    else:
        # Generar fecha y hora
        ahora = datetime.now()
        fecha, hora = ahora.strftime("%Y-%m-%d"), ahora.strftime("%H:%M:%S")

        # Estampar hora sobre la imagen
        #img = Image.open(foto_camara)
        #draw = ImageDraw.Draw(img)
        #draw.text((20, img.height - 40), f"{usuario_sel} | {fecha} {hora}", fill=(255, 255, 255))

        # Guardar imagen localmente
        #os.makedirs("fotos", exist_ok=True)
        #foto_path = f"fotos/{fecha}_{usuaria_sel}_{tipo_registro}.jpg"
        #img.save(foto_path)

        # Guardar datos en archivo CSV
        registro = pd.DataFrame([{
            "Fecha": fecha, "Hora": hora, "Usuario": usuario_sel,
            "Tienda": tienda_sel, "Tipo": tipo_registro             #, "Foto": foto_path
        }])
        registro.to_csv("asistencia.csv", mode='a', header=not os.path.exists("asistencia.csv"), index=False)

        st.success(f"✅ Registro completado exitosamente a las {hora}.")
        