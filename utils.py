from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
import random
import google.generativeai as genai

def apply_distortion(image, distortion_type, intensity):
    if distortion_type == "Blur":
        return image.filter(ImageFilter.GaussianBlur(radius=intensity))
    elif distortion_type == "Brightness":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(intensity)
    elif distortion_type == "Contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(intensity)
    elif distortion_type == "Sharpness":
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(intensity)
    elif distortion_type == "Color":
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(intensity)
    elif distortion_type == "Rain":
        return apply_rain_effect(image, intensity)
    return image

def apply_rain_effect(image, intensity):
    overlay = Image.new('RGBA', image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    width, height = image.size
    for _ in range(int(intensity * 1000)):
        x = random.randint(0, width)
        y = random.randint(0, height)
        length = random.randint(10, 20)
        draw.line((x, y, x + random.randint(-2, 2), y + length), fill=(255, 255, 255, random.randint(50, 150)), width=1)
    
    rain_overlay = overlay.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(image.convert("RGBA"), rain_overlay).convert("RGB")

def get_gemini_response(input_text, image, model_name):
    model = genai.GenerativeModel(model_name)
    response = None
    if input_text and image:
        response = model.generate_content([input_text, image])
    elif input_text:
        response = model.generate_content([input_text])
    elif image:
        response = model.generate_content([image])
    return response.text if response else "No response from the model."