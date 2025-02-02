from fastapi import APIRouter, HTTPException, Depends
from io import BytesIO
import os
import pyautogui
import base64
from groq import Groq  # Varmista, että tämä kirjasto on asennettu
from api.config import get_api_key, logger

router = APIRouter()

@router.get("/screenshot", dependencies=[Depends(get_api_key)])
def get_screenshot_text():
    """
    Ottaa kuvakaappauksen, lähettää sen Groq API:lle (img2txt) ja palauttaa kuvan sisällön tekstinä.
    """
    try:
        # Aseta DISPLAY, jos käytössä headless-ympäristö
        if not os.getenv('DISPLAY'):
            os.environ['DISPLAY'] = ':0'

        # Ota kuvakaappaus
        screenshot = pyautogui.screenshot()

        # Tallenna kuvakaappaus in-memory bufferiin JPEG-muodossa
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()

        # Koodaa kuva base64-muotoon ja rakenna data URL
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        # Luo Groq API -client
        client = Groq()

        # Lähetä kuva Groq API:lle ja pyydä kuvasta kuvailevaa tekstiä
        chat_completion = client.chat.completions.create(
            model="llama-3.2-11b-vision-preview",  # Vaihda tarvittaessa toiseen malliin
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

        # Ota vastauksesta esiin generoitu teksti
        response_text = chat_completion.choices[0].message.content

        return {"message": "Kuvakaappaus käsitelty onnistuneesti", "extracted_text": response_text}

    except Exception as e:
        logger.error("Kuvakaappauksen ottaminen tai Groq API -käsittely epäonnistui: " + str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Kuvakaappauksen käsittely epäonnistui.")
