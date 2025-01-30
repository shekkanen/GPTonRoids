from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import uuid
import os
from gtts import gTTS
from pydub import AudioSegment
import simpleaudio as sa
import logging

# Import logger, TMP_DIR, get_api_key from the config file
from api.config import logger, TMP_DIR, get_api_key

router = APIRouter()

class TxtToWavRequest(BaseModel):
    text: str

@router.post("/txt2wav", dependencies=[Depends(get_api_key)])
def txt2wav(request: TxtToWavRequest):
    """
    Converts the provided text into a WAV audio file using gTTS (Google Text-to-Speech).
    Saves the resulting file into the tmp folder.
    """
    logger.info(f"Converting text to wav: {request.text}")
    try:
        # Generate a unique filename for the MP3 and WAV files
        mp3_filename = TMP_DIR / f"{uuid.uuid4()}.mp3"
        wav_filename = TMP_DIR / f"{uuid.uuid4()}.wav"

        # Convert text to MP3 using gTTS
        tts = gTTS(text=request.text, lang="en")
        tts.save(str(mp3_filename))

        # Convert MP3 to WAV using pydub
        audio = AudioSegment.from_mp3(str(mp3_filename))
        audio.export(str(wav_filename), format="wav")

        # Delete the temporary MP3 file
        os.remove(mp3_filename)

        # Play the generated WAV file
        wave_obj = sa.WaveObject.from_wave_file(str(wav_filename))
        play_obj = wave_obj.play()
        play_obj.wait_done()

        return {"filename": str(wav_filename)}
    except Exception as e:
        logger.error(f"Failed to generate WAV file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate WAV file: {str(e)}")
