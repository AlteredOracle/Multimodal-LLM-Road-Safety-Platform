import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from utils import apply_distortion, get_gemini_response

# Set page configuration
st.set_page_config(page_title="Image CREATION", layout="wide")

# Sidebar for settings
st.sidebar.title("Settings")

model_choice = st.sidebar.selectbox(
    "Choose Model:",
    ["gemini-1.5-flash-latest", "gemini-1.5-pro"]
)

st.sidebar.subheader("Distortions")

distortion_type = st.sidebar.selectbox(
    "Choose Distortion:",
    ["None", "Blur", "Brightness", "Contrast", "Sharpness", "Color", "Rain"]
)

if distortion_type != "None":
    intensity = st.sidebar.slider("Distortion Intensity", 0.5, 2.0, 1.0)
else:
    intensity = 1.0

st.title("Multimodal LLM Road Safety Platform")

api_key = st.text_input("Enter your Gemini API key:", type="password")

if api_key:
    os.environ['GEMINI_API_KEY'] = api_key
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])

    input_text = st.text_input("Input Prompt:", key="input")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    image = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        if distortion_type != "None":
            image = apply_distortion(image, distortion_type, intensity)
        
        st.image(image, caption="Uploaded Image.", use_column_width=True)

    submit = st.button("Analyse")

    if submit:
        if input_text or image:
            response = get_gemini_response(input_text, image, model_choice)
            
            st.subheader("User Input")
            st.write(input_text if input_text else "[No text input]")
            
            st.subheader("AI Response")
            st.write(response)
            
            st.warning("Please clear or change the input if you wish to analyze a different image or prompt.")
        else:
            st.warning("Please provide either an input prompt, an image, or both.")
else:
    st.warning("Please enter your API key to proceed.")