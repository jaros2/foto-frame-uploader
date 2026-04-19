import os
import aiohttp
import mimetypes
import logging
from typing import List
from app.jobs.base import BaseJob
from app.jobs.registry import register_job

logger = logging.getLogger(__name__)

# Basic allowed extensions, can be expanded or refined based on mimetype
ALLOWED_EXTENSIONS = {
    # Images
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.heic',
    # Videos
    '.mp4', '.mov', '.avi', '.mkv', '.webm'
}

@register_job
class ImmichJob(BaseJob):
    name: str = "default"  # Can be mapped to whatever default job name is required
    
    async def process_files(self, file_paths: List[str]):
        immich_url = os.getenv("IMMICH_URL")
        api_key = os.getenv("IMMICH_API_KEY")
        album_id = os.getenv("IMMICH_ALBUM_ID")
        
        if not immich_url or not api_key:
            logger.error("Immich URL or API Key is not configured. Cannot process files.")
            return
            
        immich_url = immich_url.rstrip('/')
        
        valid_files = []
        # Filter files
        for path in file_paths:
            ext = os.path.splitext(path)[1].lower()
            if ext in ALLOWED_EXTENSIONS:
                valid_files.append(path)
            else:
                logger.info(f"Removing invalid file: {path}")
                try:
                    os.remove(path)
                except Exception as e:
                    logger.error(f"Failed to remove file {path}: {e}")
                    
        if not valid_files:
            logger.info("No valid files to upload.")
            return
            
        headers = {
            "Accept": "application/json",
            "x-api-key": api_key
        }
        
        asset_ids = []
        
        async with aiohttp.ClientSession(headers=headers) as session:
            for path in valid_files:
                filename = os.path.basename(path)
                try:
                    with open(path, 'rb') as f:
                        # Immich requires multipart/form-data with assetData
                        data = aiohttp.FormData()
                        data.add_field('deviceAssetId', filename) # Using filename as deviceAssetId for simplicity
                        data.add_field('deviceId', 'python-uploader')
                        data.add_field('fileCreatedAt', '2024-01-01T00:00:00.000Z')
                        data.add_field('fileModifiedAt', '2024-01-01T00:00:00.000Z')
                        data.add_field('isFavorite', 'false')
                        data.add_field('assetData', f, filename=filename)

                        async with session.post(f"{immich_url}/api/asset/upload", data=data) as resp:
                            if resp.status in [200, 201]:
                                result = await resp.json()
                                asset_ids.append(result.get('id'))
                                logger.info(f"Successfully uploaded {filename}")
                            else:
                                text = await resp.text()
                                logger.error(f"Failed to upload {filename}. Status: {resp.status}, Response: {text}")
                except Exception as e:
                    logger.error(f"Error uploading {filename}: {e}")
                    
            # Add to album if configured
            if album_id and asset_ids:
                album_payload = {
                    "assetIds": asset_ids
                }
                try:
                    async with session.put(f"{immich_url}/api/album/{album_id}/assets", json=album_payload) as resp:
                        if resp.status in [200, 201]:
                            logger.info(f"Successfully added assets to album {album_id}")
                        else:
                            text = await resp.text()
                            logger.error(f"Failed to add assets to album. Status: {resp.status}, Response: {text}")
                except Exception as e:
                    logger.error(f"Error adding to album: {e}")
