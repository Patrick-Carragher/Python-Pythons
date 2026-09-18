from datetime import datetime
from pathlib import Path

from openpyxl import Workbook, load_workbook

from apps.certification_manager.models import Application


EXCEL_FILE = Path(__file__).parent / "data" / "applications.xlsx"

HEADERS = [
    "Ankom",
    "Namn",
    "Personnummer",
    "Ny- eller Omcertifiering",
    "Norm",
    "Företag",
    "Adress",
    "Mail",
    "Mail privat",
    "Telefon",
    "Examinationsdatum",
    "Utb hos Säkerhetsbransch?",
    "Plats",
    "Övrigt",
    "Resultat",
    "Status",
]


def application_exists(application: Application) -> bool:
    if not EXCEL_FILE.exists() or EXCEL_FILE.stat().st_size == 0:
        return False

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook.active

    for row in sheet.iter_rows(min_row=2, values_only=True):
        ankom = row[0]
        personnummer = row[2]
        certification_type = row[3]
        norm = row[4]

        if isinstance(ankom, datetime):
            ankom = ankom.date()

        if (
            personnummer == application.personnummer
            and certification_type == application.ny_eller_omcertifiering
            and norm == application.norm
            and ankom == application.ankom
        ):
            return True

    return False


def save_application(application: Application) -> None:
    if EXCEL_FILE.exists() and EXCEL_FILE.stat().st_size > 0:
        workbook = load_workbook(EXCEL_FILE)
        sheet = workbook.active
    else:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Applications"
        sheet.append(HEADERS)

    sheet.append([
        application.ankom,
        application.namn,
        application.personnummer,
        application.ny_eller_omcertifiering,
        application.norm,
        application.foretag,
        application.adress,
        application.mail,
        application.mail_privat,
        application.telefon,
        application.examinationsdatum,
        application.utb_hos_sakerhetsbransch,
        application.plats,
        application.ovrigt,
        application.resultat,
        application.status,
    ])

    workbook.save(EXCEL_FILE)


def get_all_applications() -> list[tuple[int, Application]]:
    if not EXCEL_FILE.exists() or EXCEL_FILE.stat().st_size == 0:
        return []

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook.active

    applications = []

    for row_number, row in enumerate(
        sheet.iter_rows(
            min_row=2,
            values_only=True,
        ),
        start=2,
    ):
        if not any(row):
            continue

        ankom = row[0]
        examinationsdatum = row[10]

        if isinstance(ankom, datetime):
            ankom = ankom.date()

        if isinstance(examinationsdatum, datetime):
            examinationsdatum = examinationsdatum.date()

        application = Application(
            ankom=ankom,
            namn=row[1] or "",
            personnummer=row[2] or "",
            ny_eller_omcertifiering=row[3] or "",
            norm=row[4] or "",
            foretag=row[5] or "",
            adress=row[6] or "",
            mail=row[7] or "",
            mail_privat=row[8] or "",
            telefon=row[9] or "",
            examinationsdatum=examinationsdatum,
            utb_hos_sakerhetsbransch=row[11] or "",
            plats=row[12] or "",
            ovrigt=row[13] or "",
            resultat=row[14] or "",
            status=row[15] or "",
        )

        applications.append(
            (
                row_number,
                application,
            )
        )

    return applications


def get_application_by_row(
    row_number: int,
) -> Application | None:

    if not EXCEL_FILE.exists() or EXCEL_FILE.stat().st_size == 0:
        return None

    workbook = load_workbook(EXCEL_FILE)
    sheet = workbook.active

    if row_number < 2 or row_number > sheet.max_row:
        return None

    row = [
        cell.value
        for cell in sheet[row_number]
    ]

    if not any(row):
        return None

    ankom = row[0]
    examinationsdatum = row[10]

    if isinstance(ankom, datetime):
        ankom = ankom.date()

    if isinstance(examinationsdatum, datetime):
        examinationsdatum = examinationsdatum.date()

    return Application(
        ankom=ankom,
        namn=row[1] or "",
        personnummer=row[2] or "",
        ny_eller_omcertifiering=row[3] or "",
        norm=row[4] or "",
        foretag=row[5] or "",
        adress=row[6] or "",
        mail=row[7] or "",
        mail_privat=row[8] or "",
        telefon=row[9] or "",
        examinationsdatum=examinationsdatum,
        utb_hos_sakerhetsbransch=row[11] or "",
        plats=row[12] or "",
        ovrigt=row[13] or "",
        resultat=row[14] or "",
        status=row[15] or "",
    )