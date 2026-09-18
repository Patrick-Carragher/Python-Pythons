from pathlib import Path
from shutil import move

from apps.certification_manager.excel_repository import (
    application_exists,
    get_application_by_id,
    save_application,
    update_application_by_id,
)
from apps.certification_manager.folder_repository import (
    create_application_folder,
    get_application_folder,
)
from apps.certification_manager.id_generator import (
    generate_application_id,
)
from apps.certification_manager.models import (
    Application,
)


def create_application(
    application: Application,
) -> Path:
    if application_exists(
        application
    ):
        raise ValueError(
            "Application already exists."
        )

    if not application.application_id:
        application.application_id = (
            generate_application_id(
                application.ankom.year
            )
        )

    person_folder = (
        create_application_folder(
            application
        )
    )

    save_application(
        application
    )

    return person_folder


def update_application(
    application_id: str,
    updated_application: Application,
) -> Path:
    existing_application = (
        get_application_by_id(
            application_id
        )
    )

    if existing_application is None:
        raise ValueError(
            "Ansökan kunde inte hittas."
        )

    updated_application.application_id = (
        application_id
    )

    old_folder = (
        get_application_folder(
            existing_application
        )
    )

    new_folder = (
        get_application_folder(
            updated_application
        )
    )

    moved_existing_folder = False
    created_new_folder = False

    if old_folder != new_folder:

        if new_folder.exists():
            raise ValueError(
                "Kundmappen för de nya uppgifterna finns redan."
            )

        new_folder.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if old_folder.exists():

            move(
                str(old_folder),
                str(new_folder),
            )

            moved_existing_folder = True

        else:

            new_folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            created_new_folder = True

    try:

        updated = (
            update_application_by_id(
                application_id,
                updated_application,
            )
        )

        if not updated:
            raise ValueError(
                "Ansökan kunde inte uppdateras."
            )

    except Exception:

        if (
            moved_existing_folder
            and
            new_folder.exists()
            and
            not old_folder.exists()
        ):
            old_folder.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            move(
                str(new_folder),
                str(old_folder),
            )

        elif (
            created_new_folder
            and
            new_folder.exists()
            and
            not any(
                new_folder.iterdir()
            )
        ):
            new_folder.rmdir()

        raise

    return new_folder
