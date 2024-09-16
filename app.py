import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
from utils import apply_distortion, get_gemini_response
import traceback
import pandas as pd
from io import StringIO

# Set page configuration
st.set_page_config(page_title="Multimodal LLM Road Safety Platform", layout="wide")

# Sidebar for settings
st.sidebar.title("Settings")

model_choice = st.sidebar.selectbox(
    "Choose Model:",
    ["gemini-1.5-flash-latest", "gemini-1.5-pro"]
)

st.title("Multimodal LLM Road Safety Platform")

api_key = st.text_input("Enter your Gemini API key:", type="password")

if api_key:
    os.environ['GEMINI_API_KEY'] = api_key
    genai.configure(api_key=os.environ['GEMINI_API_KEY'])

    # Add a new option in the sidebar for analysis mode
    analysis_mode = st.sidebar.radio("Analysis Mode", ["Single", "Bulk"])

    if analysis_mode == "Single":
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

    else:  # Bulk Analysis
        st.subheader("Bulk Analysis")
        
        # Create a list to store image settings
        image_settings = []
        
        # File uploader for multiple images
        uploaded_files = st.file_uploader("Choose multiple images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)
        
        if uploaded_files:
            for i, file in enumerate(uploaded_files):
                with st.expander(f"Settings for {file.name}", expanded=True):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        distortion = st.selectbox(f"Distortion", 
                            ["None", "Blur", "Brightness", "Contrast", "Sharpness", "Color", "Rain", "Warp"],
                            key=f"distortion_{i}")
                    
                        with col2:
                            intensity = st.slider("Intensity", 0.0, 1.0, 0.5, key=f"intensity_{i}")
                        
                        with col3:
                            input_text = st.text_input("Input text", key=f"input_{i}")
                        
                        image_settings.append({
                            "Image": file,
                            "Distortion": distortion,
                            "Intensity": intensity,
                            "Input Text": input_text
                        })
        
        # Button to start bulk analysis
        if st.button("Run Bulk Analysis") and image_settings:
            results = []
            progress_bar = st.progress(0)
            
            for i, settings in enumerate(image_settings):
                try:
                    image = Image.open(settings['Image'])
                    
                    # Apply distortion
                    if settings['Distortion'] != "None":
                        warp_params = {}
                        if settings['Distortion'] == "Warp":
                            warp_params = {
                                'wave_amplitude': 20,
                                'wave_frequency': 0.05,
                                'bulge_factor': 30
                            }
                        processed_image = apply_distortion(image, settings['Distortion'], settings['Intensity'], warp_params=warp_params)
                    else:
                        processed_image = image
                    
                    # Get AI response
                    response = get_gemini_response(settings['Input Text'], processed_image, model_choice)
                    
                    # Add result to list
                    results.append({
                        "Image": settings['Image'].name,
                        "Distortion": settings['Distortion'],
                        "Intensity": settings['Intensity'],
                        "Input Text": settings['Input Text'],
                        "AI Response": response
                    })
                except Exception as e:
                    st.error(f"Error processing {settings['Image'].name}: {str(e)}")
                
                progress_bar.progress((i + 1) / len(image_settings))
            
            if results:
                results_df = pd.DataFrame(results)
                st.subheader("Analysis Results")
                st.dataframe(results_df)
                
                # Convert DataFrame to CSV
                csv = results_df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="bulk_analysis_results.csv",
                    mime="text/csv",
                )
            else:
                st.warning("No results were generated. Please check your inputs and try again.")

else:
    st.warning("Please enter your API key to proceed.")