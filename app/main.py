import os
import aiofiles
from typing import List
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
import logging

from app.jobs import get_job_class

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Foto Frame Uploader")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

DATA_DIR = os.getenv("DATA_DIR", "/app/data")

@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("app/static/index.html")

@app.get("/{job_name}", response_class=HTMLResponse)
async def job_index(job_name: str):
    # Just return the same frontend; frontend can use URL to know which job
    return FileResponse("app/static/index.html")

@app.post("/upload/{job_name}")
async def upload_files(job_name: str, background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    # If job doesn't exist, fallback to default
    job_class = get_job_class(job_name)
    if not job_class:
        logger.info(f"Job '{job_name}' not found. Falling back to 'default'.")
        job_class = get_job_class("default")
        
    if not job_class:
        raise HTTPException(status_code=500, detail="Default job not configured.")
        
    job_dir = os.path.join(DATA_DIR, job_name)
    os.makedirs(job_dir, exist_ok=True)
    
    saved_files = []
    for file in files:
        if file.filename:
            file_path = os.path.join(job_dir, file.filename)
            async with aiofiles.open(file_path, 'wb') as out_file:
                while content := await file.read(1024 * 1024):  # read 1MB chunk
                    await out_file.write(content)
            saved_files.append(file_path)
            
    # Instantiate job and run it in background
    job_instance = job_class(target_path=job_dir)
    background_tasks.add_task(job_instance.process_files, saved_files)
    
    return {"message": f"Successfully uploaded {len(saved_files)} files.", "job": job_class.name}

