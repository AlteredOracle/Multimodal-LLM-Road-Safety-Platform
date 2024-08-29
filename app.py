import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from utils import apply_distortion, get_gemini_response
import traceback  # Add this line

# Set page configuration
st.set_page_config(page_title="Multimodal LLM Road Safety Platform", layout="wide")

# Sidebar for settings
st.sidebar.title("Settings")

model_choice = st.sidebar.selectbox(
    "Choose Model:",
    ["gemini-1.5-flash-latest", "gemini-1.5-pro"]
)

st.sidebar.subheader("Distortions")

distortion_type = st.sidebar.selectbox(
    "Choose Distortion:",
    ["None", "Blur", "Brightness", "Contrast", "Sharpness", "Color", "Rain", "Overlay", "Warp"]
)

overlay_image = None
warp_params = {}

if distortion_type != "None":
    intensity = st.sidebar.slider("Distortion Intensity", 0.0, 1.0, 0.5)
    if distortion_type == "Overlay":
        overlay_image = st.sidebar.file_uploader("Upload overlay image", type=["png", "jpg", "jpeg"])
    elif distortion_type == "Warp":
        warp_params['wave_amplitude'] = st.sidebar.slider("Wave Amplitude", 0.0, 50.0, 20.0)
        warp_params['wave_frequency'] = st.sidebar.slider("Wave Frequency", 0.0, 0.1, 0.04)
        warp_params['bulge_factor'] = st.sidebar.slider("Bulge Factor", -50.0, 50.0, 30.0)
else:
    intensity = 1.0
    overlay_image = None

st.title("Multimodal LLM Road Safety Platform")

api_key = st.text_input("Enter your Gemini API key:", type="password")

if api_key:
    os.environ['GEMINI_API_KEY'] = api_key
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])

    input_text = st.text_input("Input Prompt:", key="input")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    image = None
    processed_image = None
    if uploaded_file:
        try:
            image = Image.open(uploaded_file)
            
            if distortion_type != "None":
                processed_image = apply_distortion(image, distortion_type, intensity, overlay_image, warp_params)
                if processed_image is not None:
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(image, caption="Original Image", use_column_width=True)
                    with col2:
                        st.image(processed_image, caption="Processed Image", use_column_width=True)
                else:
                    st.error("Failed to process the image. The distortion function returned None.")
            else:
                st.image(image, caption="Original Image", use_column_width=True)
                processed_image = image  # If no distortion, use the original image
        except Exception as e:
            st.error(f"An error occurred while processing the image: {str(e)}")
            st.error(traceback.format_exc())

    submit = st.button("Analyse")

    if submit:
        if input_text or processed_image:
            try:
                response = get_gemini_response(input_text, processed_image, model_choice)
                
                st.subheader("User Input")
                st.write(input_text if input_text else "[No text input]")
                
                st.subheader("AI Response")
                st.write(response)
            except Exception as e:
                st.error(f"An error occurred during analysis: {str(e)}")
            
            st.warning("Please clear or change the input if you wish to analyze a different image or prompt.")
        else:
            st.warning("Please provide either an input prompt, an image, or both.")
else:
    st.warning("Please enter your API key to proceed.")