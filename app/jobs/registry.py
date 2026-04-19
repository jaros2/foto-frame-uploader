from typing import Type, Dict
from app.jobs.base import BaseJob

_JOBS: Dict[str, Type[BaseJob]] = {}

def register_job(job_class: Type[BaseJob]):
    _JOBS[job_class.name] = job_class
    return job_class

def get_job_class(job_name: str) -> Type[BaseJob]:
    return _JOBS.get(job_name)

def get_all_jobs() -> Dict[str, Type[BaseJob]]:
    return _JOBS
