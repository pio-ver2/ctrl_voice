import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob
import paho.mqtt.client as paho
import json
from gtts import gTTS
from googletrans import Translator

def on_publish(client,userdata,result):             #create function for callback
    print("el dato ha sido publicado \n")
    pass

def on_message(client, userdata, message):
    global message_received
    time.sleep(2)
    message_received = str(message.payload.decode("utf-8"))
    st.write(message_received)

broker = "broker.mqttdashboard.com"
port = 1883
client1 = paho.Client("GIT-HUBC")
client1.on_message = on_message

# Estilo visual con temática oceánica
st.markdown("""
    <style>
        body {
            background-color: #003366;  /* Azul océano profundo */
            color: #ffffff;  /* Texto blanco */
        }
        .stTitle {
            color: #80deea;  /* Azul océano claro para el título */
        }
        .stSubheader {
            color: #00bcd4;  /* Azul turquesa para los subtítulos */
        }
        .stButton>button {
            background-color: #00796b;  /* Botones de color verde océano */
            color: white;  /* Texto blanco en los botones */
        }
        .stImage>div>img {
            border-radius: 15px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        .stMarkdown {
            color: #ffffff;  /* Texto de Markdown en blanco */
        }
        .stSidebar {
            background-color: #80deea;  /* Azul claro para la barra lateral */
        }
    </style>
""", unsafe_allow_html=True)

st.title("🌊 **INTERFACES MULTIMODALES** 🤖")
st.subheader("🎤 **CONTROL POR VOZ**")

image = Image.open('voice_ctrl.jpg')
st.image(image, width=200)

st.write("🔊 **Toca el Botón y habla**")

# Botón de inicio
stt_button = Button(label=" Inicio 🗣️", width=200)

# Código de reconocimiento de voz en el botón
stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;
 
    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if ( value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
    """))

# Evento de escuchar el texto
result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0)

# Procesar el resultado
if result:
    if "GET_TEXT" in result:
        st.write(f"🎤 **Texto recibido:** {result.get('GET_TEXT')}")
        client1.on_publish = on_publish
        client1.connect(broker, port)  
        message = json.dumps({"Act1": result.get("GET_TEXT").strip()})
        ret = client1.publish("voice_ctrl", message)

    try:
        os.mkdir("temp")
    except:
        pass
