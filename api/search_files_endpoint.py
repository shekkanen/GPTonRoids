from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from api.config import WORK_DIR, get_api_key, logger
from pydantic import BaseModel
import os
import asyncio
import aiofiles

class FileSearchRequest(BaseModel):
    query: str

router = APIRouter()

async def search_in_file(file_path: str, query: str, max_bytes: int = 1024 * 1024) -> bool:
    """
    Tarkistaa, löytyykö haettava teksti tiedostosta.
    Lukee tiedostosta enintään max_bytes (oletuksena 1 Mt) ja etsii hakutermiä.
    """
    try:
        async with aiofiles.open(file_path, mode='rb') as f:
            content = await f.read(max_bytes)
            # Yritetään purkaa utf-8:n mukaisesti, virheet ohitetaan
            text = content.decode('utf-8', errors='ignore').lower()
            return query in text
    except Exception as e:
        logger.warning(f"Ei voitu lukea tiedostoa {file_path}: {e}")
        return False

async def process_file(file_path: str, query: str, semaphore: asyncio.Semaphore) -> str:
    """
    Käsittelee yksittäisen tiedoston: jos hakutermi löytyy joko tiedostonimestä
    tai sen sisällöstä, palauttaa tiedostopolun suhteellisena WORK_DIR:stä, muuten None.
    """
    # Tarkistetaan ensin tiedostonimi (nopea vertailu)
    if query in os.path.basename(file_path).lower():
        return os.path.relpath(file_path, WORK_DIR)
    async with semaphore:
        if await search_in_file(file_path, query):
            return os.path.relpath(file_path, WORK_DIR)
    return None

async def search_files_async(query: str) -> list:
    """
    Asynkronisesti hakee tiedostoja WORK_DIR:stä, joissa hakutermi esiintyy.
    Samanaikaisuutta rajoitetaan semaforilla (oletuksena 100 rinnakkaista lukua).
    """
    tasks = []
    semaphore = asyncio.Semaphore(100)
    
    for root, _, filenames in os.walk(WORK_DIR):
        for filename in filenames:
            file_path = os.path.join(root, filename)
            tasks.append(process_file(file_path, query, semaphore))
    
    results = await asyncio.gather(*tasks, return_exceptions=False)
    # Palautetaan vain ne polut, joissa hakutermi löytyi
    matches = [result for result in results if result is not None]
    return matches

@router.post("/search-files", dependencies=[Depends(get_api_key)])
async def search_files(request: FileSearchRequest):
    """
    Asynkroninen endpoint, joka hakee tiedostoja tiedostonimen tai sisällön perusteella.
    Lukee kunkin tiedoston enintään 1 Mt dataa suorituskyvyn varmistamiseksi.
    """
    query = request.query.lower().strip()
    if not query:
        raise HTTPException(status_code=400, detail="Hakutermi on pakollinen.")
    
    try:
        matches = await search_files_async(query)
        return {"matches": matches}
    except Exception as e:
        logger.error(f"Tiedostojen haku epäonnistui: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Tiedostojen haku epäonnistui: {str(e)}")
