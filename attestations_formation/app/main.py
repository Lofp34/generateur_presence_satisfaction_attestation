from fastapi import FastAPI, File, HTTPException, UploadFile, Depends
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from pydantic import ValidationError

from app.config import get_settings, Settings
from app.services import AttestationService

app = FastAPI(title="Attestations Automatiques")

@app.post("/generate")
async def generate(
    file: UploadFile = File(...),
    settings: Settings = Depends(get_settings)
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Le fichier doit etre un PDF.")
    
    service = AttestationService(settings)
    
    try:
        content = await file.read()
        file_stream, filename, media_type = service.process_pdf(content)
        
        return StreamingResponse(
            file_stream,
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
            
    except ValidationError as ve:
         raise HTTPException(status_code=422, detail=f"Validation Error: {ve}")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as e:
        # Generic catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

app.mount("/", StaticFiles(directory=Path(__file__).parent / "static", html=True), name="static")
