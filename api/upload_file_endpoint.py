from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pathlib import Path
from prod.config import TMP_DIR, get_api_key, logger

router = APIRouter()

@router.post("/upload-file", dependencies=[Depends(get_api_key)])
async def upload_file(file: UploadFile = File(...)):
    try:
        file_location = TMP_DIR / file.filename
        with open(file_location, "wb") as f:
            f.write(await file.read())
        return {"info": f"file '{file.filename}' saved at '{file_location}'"}
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
