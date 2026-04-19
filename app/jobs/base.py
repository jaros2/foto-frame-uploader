from abc import ABC, abstractmethod
from typing import List
import os

class BaseJob(ABC):
    name: str = "base_job"
    
    def __init__(self, target_path: str):
        self.target_path = target_path
        os.makedirs(self.target_path, exist_ok=True)
        
    @abstractmethod
    async def process_files(self, file_paths: List[str]):
        """
        Process the uploaded files.
        :param file_paths: List of absolute paths to the uploaded files.
        """
        pass
