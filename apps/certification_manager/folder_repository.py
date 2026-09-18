from pathlib import Path

from apps.certification_manager.models import Application


BASE_FOLDER = (
    Path(__file__).parent
    / "test_onedrive"
    / "Kundmappar"
)


CERTIFICATION_NAMES = {
    "SSF 1016:1": "Behörig ingenjör inbrottslarm",
    "SSF 1062:3": "Behörig ingenjör kamerabevakningssystem, CCTV",
    "SBF 1007:5": "Behörig ingenjör brandlarm",
    "SBF 2017:1": "Behörig ingenjör utrymningslarm med talat meddelande",
    "SSF 1049:1": "Certifierad låsmästare - låsanläggningar",
}


def get_application_folder(
    application: Application,
) -> Path:

    certification_name = CERTIFICATION_NAMES.get(
        application.norm,
        application.norm,
    )

    person_folder_name = (
        f"{application.namn}_{certification_name}"
    )

    person_folder = (
        BASE_FOLDER
        / application.foretag
        / "Personer"
        / person_folder_name
    )

    return person_folder


def create_application_folder(
    application: Application,
) -> Path:

    person_folder = get_application_folder(
        application
    )

    person_folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return person_folder