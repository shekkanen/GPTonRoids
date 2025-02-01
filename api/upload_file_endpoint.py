from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from api.config import TMP_DIR, get_api_key, logger
import aiofiles

router = APIRouter()

@router.post("/upload-file", dependencies=[Depends(get_api_key)])
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = TMP_DIR / file.filename
        async with aiofiles.open(file_location, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # Luetaan 1 Mt kerrallaan
                if not chunk:
                    break
                await f.write(chunk)
        return {"info": f"file '{file.filename}' saved at '{file_location}'"}
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
