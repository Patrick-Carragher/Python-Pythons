from datetime import date
from pathlib import Path

from apps.certification_manager.excel_repository import (
    application_exists,
    save_application,
)
from apps.certification_manager.folder_repository import create_application_folder
from apps.certification_manager.models import Application


def create_application(application: Application) -> Path:
    if application_exists(application):
        raise ValueError("Application already exists.")

    person_folder = create_application_folder(application)

    save_application(application)

    return person_folder


