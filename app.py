import os
import streamlit as st
import base64
from openai import OpenAI

# Function to encode the image to base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

st.set_page_config(page_title="Análisis de Imagen", layout="centered", initial_sidebar_state="collapsed")
# Streamlit page setup
st.title("📸 Análisis Inteligente de Imagen")
st.caption("Sube una imagen y deja que la IA te cuente qué ve 🤖👀")

ke = st.text_input('🔑 Ingresa tu Clave')
os.environ['OPENAI_API_KEY'] = ke

# Retrieve the OpenAI API Key from secrets
api_key = os.environ['OPENAI_API_KEY']

# Initialize the OpenAI client with the API key
client = OpenAI(api_key=api_key)

# File uploader allows user to add their own image
uploaded_file = st.file_uploader("📂 Sube una imagen", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # Display the uploaded image
    with st.expander("📷 Imagen cargada", expanded=True):
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

# Toggle for showing additional details input
show_details = st.toggle("❓ Pregunta algo específico sobre la imagen", value=False)

if show_details:
    # Text input for additional details about the image, shown only if toggle is True
    additional_details = st.text_area(
        "Agrega contexto extra aquí 👇",
        disabled=not show_details
    )

# Button to trigger the analysis
analyze_button = st.button("🔍 Analiza la imagen", type="primary")

# Check if an image has been uploaded, if the API key is available, and if the button has been pressed
if uploaded_file is not None and api_key and analyze_button:

    with st.spinner("⏳ Analizando la imagen..."):
        # Encode the image
        base64_image = encode_image(uploaded_file)
    
        prompt_text = "Describe lo que ves en la imagen en español, de forma clara y detallada."
    
        if show_details and additional_details:
            prompt_text += f"\n\nEl usuario agregó este contexto: {additional_details}"
    
        # Create the payload for the completion request
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    },
                ],
            }
        ]
    
        # Make the request to the OpenAI API
        try:
            # Stream the response
            full_response = ""
            message_placeholder = st.empty()
            for completion in client.chat.completions.create(
                model="gpt-4o", messages=messages,   
                max_tokens=1200, stream=True
            ):
                if completion.choices[0].delta.content is not None:
                    full_response += completion.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

            # --- cambio creativo ---
            st.markdown("---")
            st.subheader("🎨 Resumen divertido")
            st.success(f"✨ En pocas palabras: {full_response[:120]}... 😎")
            st.info("👉 Consejo: puedes pedirle al modelo que te dé descripciones en estilo **poético, científico o cómico**.")

        except Exception as e:
            st.error(f"❌ Ocurrió un error: {e}")
else:
    if not uploaded_file and analyze_button:
        st.warning("⚠️ Por favor, sube una imagen.")
    if not api_key:
        st.warning("⚠️ Ingresa tu API key.")
