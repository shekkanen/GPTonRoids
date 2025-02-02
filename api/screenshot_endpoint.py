from fastapi import APIRouter, HTTPException, Depends, Query
from io import BytesIO
import os
import pyautogui
import base64
import uuid

from groq import Groq  # Varmista, että tämä kirjasto on asennettu
from api.config import get_api_key, logger, TMP_DIR

router = APIRouter()

@router.get("/screenshot", dependencies=[Depends(get_api_key)])
def get_screenshot_text(
    prompt: str = Query(
        "Describe in detail what is visible in this screenshot.",
        description="Custom prompt to override the default prompt for the Groq API call"
    ),
    x: int = Query(None, description="X-koordinaatti ylävasemmasta kulmasta (valinnainen)"),
    y: int = Query(None, description="Y-koordinaatti ylävasemmasta kulmasta (valinnainen)"),
    width: int = Query(None, description="Alueen leveys (valinnainen)"),
    height: int = Query(None, description="Alueen korkeus (valinnainen)")
):
    """
    Ottaa kuvakaappauksen joko koko näytöstä tai määritellyltä alueelta (x, y, width, height),
    tallentaa sen TMP_DIR:iin (BASE_DIR / tmp), koodaa kuvan base64-muotoon, lähettää sen Groq API:lle
    img2txt -malliin käyttäen annettua promptia, ja palauttaa kuvan sisällöstä saadun tekstin.
    """
    try:
        # Aseta DISPLAY, jos ollaan headless-ympäristössä
        if not os.getenv('DISPLAY'):
            os.environ['DISPLAY'] = ':0'

        # Jos kaikki alueen parametrit on annettu, otetaan vain kyseinen osa näytöstä
        if x is not None and y is not None and width is not None and height is not None:
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
        else:
            screenshot = pyautogui.screenshot()

        # Tallennetaan kuvakaappaus levylle TMP_DIR käyttäen PNG-formaattia (häviötön formaatti säilyttää yksityiskohdat paremmin)
        file_path = TMP_DIR / f"{uuid.uuid4()}.png"
        screenshot.save(file_path, format="PNG")
        logger.info(f"Screenshot saved: {file_path}")

        # Muunnetaan kuvakaappaus base64-stringiksi PNG-muodossa
        buffered = BytesIO()
        screenshot.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/png;base64,{base64_image}"

        # Luo Groq API -client ja lähetä pyyntö käyttäen parametrisoitua promptia
        client = Groq()
        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",  # Vaihda tarvittaessa mallia
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Hae vastauksesta generoitu teksti
        response_text = chat_completion.choices[0].message.content

        return {
            "message": "Screenshot processed successfully",
            "extracted_text": response_text,
            "saved_image": str(file_path)
        }

    except Exception as e:
        logger.error("Screenshot capture or Groq API processing failed: " + str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Screenshot processing failed.")
