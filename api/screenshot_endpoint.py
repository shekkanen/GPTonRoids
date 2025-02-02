from fastapi import APIRouter, HTTPException, Depends
from io import BytesIO
import os
import pyautogui
import base64
import uuid

from groq import Groq  # Varmista, että tämä kirjasto on asennettu
from api.config import get_api_key, logger, TMP_DIR

router = APIRouter()


@router.get("/screenshot", dependencies=[Depends(get_api_key)])
def get_screenshot_text():
    """
    Ottaa kuvakaappauksen, tallentaa sen levylle BASE_DIR / tmp -kansioon,
    koodaa kuvan base64-muotoon, lähettää sen Groq API:lle img2txt -malliin
    ja palauttaa kuvan sisällöstä saadun tekstin.
    """
    try:
        # Aseta DISPLAY, jos ollaan headless-ympäristössä
        if not os.getenv('DISPLAY'):
            os.environ['DISPLAY'] = ':0'

        # Ota kuvakaappaus
        screenshot = pyautogui.screenshot()

        # Tallenna kuvakaappaus levylle TMP_DIR (BASE_DIR / tmp)
        file_path = TMP_DIR / f"{uuid.uuid4()}.jpg"
        screenshot.save(file_path, format="JPEG")
        logger.info(f"Kuvakaappaus tallennettu: {file_path}")

        # Muunna kuvakaappaus base64-stringiksi
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        # Luo Groq API -client ja lähetä pyyntö
        client = Groq()
        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",  # Vaihda tarvittaessa mallia
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Kuvaile mahdollisimman tarkasti, mitä tässä kuvakaappauksessa näkyy."},
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
            "message": "Kuvakaappaus käsitelty onnistuneesti",
            "extracted_text": response_text,
            "saved_image": str(file_path)
        }

    except Exception as e:
        logger.error("Kuvakaappauksen ottaminen tai Groq API -käsittely epäonnistui: " + str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Kuvakaappauksen käsittely epäonnistui.")
