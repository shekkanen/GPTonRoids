from fastapi import APIRouter, HTTPException, Depends
from io import BytesIO
import os
import pyautogui
import base64
import uuid

from groq import Groq  # Ensure that this library is installed
from api.config import get_api_key, logger, TMP_DIR

router = APIRouter()

@router.get("/screenshot", dependencies=[Depends(get_api_key)])
def get_screenshot_text():
    """
    Takes a screenshot, saves it to TMP_DIR (BASE_DIR / tmp),
    encodes the image to a base64 string, sends it to the Groq API using the img2txt model,
    and returns the extracted text.
    """
    try:
        # Set DISPLAY if running in a headless environment
        if not os.getenv('DISPLAY'):
            os.environ['DISPLAY'] = ':0'

        # Take a screenshot
        screenshot = pyautogui.screenshot()

        # Save the screenshot to TMP_DIR (BASE_DIR / tmp)
        file_path = TMP_DIR / f"{uuid.uuid4()}.jpg"
        screenshot.save(file_path, format="JPEG")
        logger.info(f"Screenshot saved: {file_path}")

        # Convert the screenshot to a base64 string
        buffered = BytesIO()
        screenshot.save(buffered, format="JPEG")
        image_bytes = buffered.getvalue()
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        image_data_url = f"data:image/jpeg;base64,{base64_image}"

        # Create a Groq API client and send the request
        client = Groq()
        chat_completion = client.chat.completions.create(
            model="llama-3.2-90b-vision-preview",  # Change the model if needed
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Describe in detail what is visible in this screenshot."},
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

        # Retrieve the generated text from the response
        response_text = chat_completion.choices[0].message.content

        return {
            "message": "Screenshot processed successfully",
            "extracted_text": response_text,
            "saved_image": str(file_path)
        }

    except Exception as e:
        logger.error("Screenshot capture or Groq API processing failed: " + str(e), exc_info=True)
        raise HTTPException(status_code=500, detail="Screenshot processing failed.")
