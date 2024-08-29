from PIL import Image, ImageEnhance, ImageFilter, ImageDraw, ImageOps
import random
import google.generativeai as genai
import io

def apply_distortion(image, distortion_type, intensity, overlay_image=None):
    if distortion_type == "Blur":
        return image.filter(ImageFilter.GaussianBlur(radius=intensity * 10))
    elif distortion_type == "Brightness":
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(1 + intensity)
    elif distortion_type == "Contrast":
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(1 + intensity)
    elif distortion_type == "Sharpness":
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(1 + intensity)
    elif distortion_type == "Color":
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(1 + intensity)
    elif distortion_type == "Rain":
        return apply_rain_effect(image, intensity)
    elif distortion_type == "Overlay":
        return apply_overlay(image, intensity, overlay_image)
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

def apply_overlay(image, intensity, overlay_image):
    if overlay_image is None:
        return image
    
    overlay = Image.open(io.BytesIO(overlay_image.read())).convert("RGBA")
    overlay = overlay.resize(image.size)
    
    # Create a new image with the same size as the original
    result = Image.new("RGBA", image.size)
    
    # Paste the original image
    result.paste(image.convert("RGBA"), (0, 0))
    
    # Apply the overlay with the given intensity
    overlay = Image.blend(Image.new("RGBA", image.size, (0, 0, 0, 0)), overlay, intensity)
    result = Image.alpha_composite(result, overlay)
    
    return result.convert("RGB")

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