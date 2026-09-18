from datetime import (
    date,
    datetime,
)
from pathlib import Path

from openpyxl import (
    Workbook,
    load_workbook,
)
from openpyxl.utils.datetime import (
    from_excel,
)

from apps.certification_manager.id_generator import (
    generate_application_id,
    is_valid_application_id,
)
from apps.certification_manager.models import (
    Application,
)


EXCEL_FILE = (
    Path(__file__).parent
    / "data"
    / "applications.xlsx"
)

APPLICATIONS_SHEET = "Applications"
COMPLETED_SHEET = "Completed"
EVIDENCE_SHEET = "Evidence"

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
    "Application ID",
]

COMPLETED_HEADERS = [
    *HEADERS,
    "Completed Date",
    "Previous Status",
]

EVIDENCE_HEADERS = [
    "Application ID",
    "Document",
    "Present",
    "Note",
]


def get_applications_sheet(
    workbook,
):
    if (
        APPLICATIONS_SHEET
        in workbook.sheetnames
    ):
        return workbook[
            APPLICATIONS_SHEET
        ]

    sheet = workbook.active
    sheet.title = APPLICATIONS_SHEET

    return sheet


def get_completed_sheet(
    workbook,
):
    if (
        COMPLETED_SHEET
        in workbook.sheetnames
    ):
        return workbook[
            COMPLETED_SHEET
        ]

    sheet = workbook.create_sheet(
        COMPLETED_SHEET
    )

    sheet.append(
        COMPLETED_HEADERS
    )

    return sheet


def get_evidence_sheet(
    workbook,
):
    if (
        EVIDENCE_SHEET
        in workbook.sheetnames
    ):
        return workbook[
            EVIDENCE_SHEET
        ]

    sheet = workbook.create_sheet(
        EVIDENCE_SHEET
    )

    sheet.append(
        EVIDENCE_HEADERS
    )

    return sheet


def format_date_columns(
    sheet,
) -> bool:
    changed = False

    for row_number in range(
        2,
        sheet.max_row + 1,
    ):
        for column in (
            1,
            11,
        ):
            cell = sheet.cell(
                row=row_number,
                column=column,
            )

            if (
                cell.value is not None
                and
                cell.number_format
                != "yyyy-mm-dd"
            ):
                cell.number_format = (
                    "yyyy-mm-dd"
                )

                changed = True

    return changed


def format_completed_date_columns(
    sheet,
) -> bool:
    changed = (
        format_date_columns(
            sheet
        )
    )

    for row_number in range(
        2,
        sheet.max_row + 1,
    ):
        cell = sheet.cell(
            row=row_number,
            column=18,
        )

        if (
            cell.value is not None
            and
            cell.number_format
            != "yyyy-mm-dd"
        ):
            cell.number_format = (
                "yyyy-mm-dd"
            )

            changed = True

    return changed


def normalise_excel_date(
    value,
):
    if value is None:
        return None

    if isinstance(
        value,
        datetime,
    ):
        return value.date()

    if isinstance(
        value,
        date,
    ):
        return value

    if isinstance(
        value,
        (int, float),
    ):
        converted = from_excel(
            value
        )

        if isinstance(
            converted,
            datetime,
        ):
            return converted.date()

        if isinstance(
            converted,
            date,
        ):
            return converted

    if isinstance(
        value,
        str,
    ):
        try:
            return date.fromisoformat(
                value
            )

        except ValueError:
            return value

    return value


def get_year_from_value(
    value,
) -> int:
    normalised_date = (
        normalise_excel_date(
            value
        )
    )

    if isinstance(
        normalised_date,
        date,
    ):
        return normalised_date.year

    return datetime.now().year


def ensure_application_ids(
    workbook,
) -> None:
    sheet = get_applications_sheet(
        workbook
    )

    completed_sheet_existed = (
        COMPLETED_SHEET
        in workbook.sheetnames
    )

    evidence_sheet_existed = (
        EVIDENCE_SHEET
        in workbook.sheetnames
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    evidence_sheet = (
        get_evidence_sheet(
            workbook
        )
    )

    application_id_column = len(
        HEADERS
    )

    changed = (
        not completed_sheet_existed
        or
        not evidence_sheet_existed
    )

    if (
        sheet.cell(
            row=1,
            column=application_id_column,
        ).value
        != "Application ID"
    ):
        sheet.cell(
            row=1,
            column=application_id_column,
        ).value = "Application ID"

        changed = True

    if (
        completed_sheet.cell(
            row=1,
            column=18,
        ).value
        != "Completed Date"
    ):
        completed_sheet.cell(
            row=1,
            column=18,
        ).value = "Completed Date"

        changed = True

    if (
        completed_sheet.cell(
            row=1,
            column=19,
        ).value
        != "Previous Status"
    ):
        completed_sheet.cell(
            row=1,
            column=19,
        ).value = "Previous Status"

        changed = True

    for column, header in enumerate(
        EVIDENCE_HEADERS,
        start=1,
    ):
        if (
            evidence_sheet.cell(
                row=1,
                column=column,
            ).value
            != header
        ):
            evidence_sheet.cell(
                row=1,
                column=column,
            ).value = header

            changed = True

    used_ids: set[str] = set()

    for row in (
        completed_sheet.iter_rows(
            min_row=2,
            values_only=True,
        )
    ):
        if (
            len(row) > 16
            and
            row[16]
        ):
            used_ids.add(
                str(
                    row[16]
                ).strip()
            )

    for row_number in range(
        2,
        sheet.max_row + 1,
    ):
        has_data = any(
            sheet.cell(
                row=row_number,
                column=column,
            ).value
            is not None
            for column in range(
                1,
                application_id_column,
            )
        )

        if not has_data:
            continue

        id_cell = sheet.cell(
            row=row_number,
            column=application_id_column,
        )

        existing_id = (
            str(
                id_cell.value
            ).strip()
            if id_cell.value
            else ""
        )

        if (
            is_valid_application_id(
                existing_id
            )
            and
            existing_id not in used_ids
        ):
            used_ids.add(
                existing_id
            )

            continue

        application_year = (
            get_year_from_value(
                sheet.cell(
                    row=row_number,
                    column=1,
                ).value
            )
        )

        new_application_id = (
            generate_application_id(
                application_year,
                used_ids,
            )
        )

        id_cell.value = (
            new_application_id
        )

        used_ids.add(
            new_application_id
        )

        changed = True

    if format_date_columns(
        sheet
    ):
        changed = True

    if format_completed_date_columns(
        completed_sheet
    ):
        changed = True

    if changed:
        workbook.save(
            EXCEL_FILE
        )


def row_to_application(
    row,
) -> Application:
    ankom = normalise_excel_date(
        row[0]
    )

    examinationsdatum = (
        normalise_excel_date(
            row[10]
        )
    )

    return Application(
        ankom=ankom,
        namn=(row[1] or ""),
        personnummer=(row[2] or ""),
        ny_eller_omcertifiering=(
            row[3] or ""
        ),
        norm=(row[4] or ""),
        foretag=(row[5] or ""),
        adress=(row[6] or ""),
        mail=(row[7] or ""),
        mail_privat=(row[8] or ""),
        telefon=(row[9] or ""),
        examinationsdatum=(
            examinationsdatum
        ),
        utb_hos_sakerhetsbransch=(
            row[11] or ""
        ),
        plats=(row[12] or ""),
        ovrigt=(row[13] or ""),
        resultat=(row[14] or ""),
        status=(row[15] or ""),
        application_id=(row[16] or ""),
    )


def find_row_by_application_id(
    sheet,
    application_id: str,
) -> int | None:
    for row_number in range(
        2,
        sheet.max_row + 1,
    ):
        row_application_id = (
            sheet.cell(
                row=row_number,
                column=17,
            ).value
        )

        if (
            row_application_id
            == application_id
        ):
            return row_number

    return None


def application_exists(
    application: Application,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    sheet = get_applications_sheet(
        workbook
    )

    for row in sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        if not any(row):
            continue

        ankom = normalise_excel_date(
            row[0]
        )

        if (
            row[2]
            == application.personnummer
            and
            row[3]
            == application.ny_eller_omcertifiering
            and
            row[4]
            == application.norm
            and
            ankom
            == application.ankom
        ):
            return True

    return False


def save_application(
    application: Application,
) -> None:
    if (
        EXCEL_FILE.exists()
        and
        EXCEL_FILE.stat().st_size > 0
    ):
        workbook = load_workbook(
            EXCEL_FILE
        )

        ensure_application_ids(
            workbook
        )

        sheet = get_applications_sheet(
            workbook
        )

    else:
        workbook = Workbook()

        sheet = workbook.active
        sheet.title = APPLICATIONS_SHEET

        sheet.append(
            HEADERS
        )

        get_completed_sheet(
            workbook
        )

        get_evidence_sheet(
            workbook
        )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    existing_ids = {
        str(
            row[16]
        ).strip()
        for row in sheet.iter_rows(
            min_row=2,
            values_only=True,
        )
        if (
            len(row) > 16
            and
            row[16]
        )
    }

    existing_ids.update(
        {
            str(
                row[16]
            ).strip()
            for row in (
                completed_sheet.iter_rows(
                    min_row=2,
                    values_only=True,
                )
            )
            if (
                len(row) > 16
                and
                row[16]
            )
        }
    )

    if (
        not is_valid_application_id(
            application.application_id
        )
        or
        application.application_id
        in existing_ids
    ):
        application.application_id = (
            generate_application_id(
                application.ankom.year,
                existing_ids,
            )
        )

    sheet.append(
        [
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
            application.application_id,
        ]
    )

    format_date_columns(
        sheet
    )

    format_completed_date_columns(
        completed_sheet
    )

    workbook.save(
        EXCEL_FILE
    )


def get_all_applications(
) -> list[Application]:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return []

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    sheet = get_applications_sheet(
        workbook
    )

    applications: list[
        Application
    ] = []

    for row in sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        if not any(row):
            continue

        applications.append(
            row_to_application(
                row
            )
        )

    return applications


def get_application_by_id(
    application_id: str,
) -> Application | None:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return None

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    applications_sheet = (
        get_applications_sheet(
            workbook
        )
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    for sheet in (
        applications_sheet,
        completed_sheet,
    ):
        for row in sheet.iter_rows(
            min_row=2,
            values_only=True,
        ):
            if not any(row):
                continue

            if (
                (row[16] or "")
                == application_id
            ):
                return row_to_application(
                    row
                )

    return None


def get_completed_applications(
    year: int | None = None,
) -> list[
    tuple[
        Application,
        date | None,
    ]
]:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return []

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    completed_applications: list[
        tuple[
            Application,
            date | None,
        ]
    ] = []

    for row in completed_sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        if not any(row):
            continue

        completed_date = (
            normalise_excel_date(
                row[17]
            )
        )

        if (
            year is not None
            and
            (
                not isinstance(
                    completed_date,
                    date,
                )
                or
                completed_date.year
                != year
            )
        ):
            continue

        completed_applications.append(
            (
                row_to_application(
                    row
                ),
                completed_date,
            )
        )

    completed_applications.sort(
        key=lambda item: (
            item[1]
            or date.min
        ),
        reverse=True,
    )

    return completed_applications


def get_application_evidence(
    application_id: str,
) -> dict[
    str,
    dict[str, object],
]:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return {}

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    evidence_sheet = (
        get_evidence_sheet(
            workbook
        )
    )

    evidence: dict[
        str,
        dict[str, object],
    ] = {}

    for row in evidence_sheet.iter_rows(
        min_row=2,
        values_only=True,
    ):
        if not any(row):
            continue

        row_application_id = (
            str(
                row[0]
                or ""
            ).strip()
        )

        if (
            row_application_id
            != application_id
        ):
            continue

        document = (
            str(
                row[1]
                or ""
            ).strip()
        )

        if not document:
            continue

        present_value = row[2]

        if isinstance(
            present_value,
            str,
        ):
            present = (
                present_value.strip().lower()
                in {
                    "1",
                    "true",
                    "yes",
                    "ja",
                    "x",
                }
            )

        else:
            present = bool(
                present_value
            )

        evidence[
            document
        ] = {
            "present":
                present,

            "note":
                str(
                    row[3]
                    or ""
                ),
        }

    return evidence


def save_application_evidence(
    application_id: str,
    evidence_items: list[
        dict[str, object]
    ],
) -> None:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        raise ValueError(
            "Excel-filen kunde inte hittas."
        )

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    evidence_sheet = (
        get_evidence_sheet(
            workbook
        )
    )

    for row_number in range(
        evidence_sheet.max_row,
        1,
        -1,
    ):
        row_application_id = (
            evidence_sheet.cell(
                row=row_number,
                column=1,
            ).value
        )

        if (
            row_application_id
            == application_id
        ):
            evidence_sheet.delete_rows(
                row_number,
                1,
            )

    for item in evidence_items:
        document = (
            str(
                item.get(
                    "document",
                    "",
                )
            ).strip()
        )

        if not document:
            continue

        evidence_sheet.append(
            [
                application_id,
                document,
                bool(
                    item.get(
                        "present",
                        False,
                    )
                ),
                str(
                    item.get(
                        "note",
                        "",
                    )
                ).strip(),
            ]
        )

    workbook.save(
        EXCEL_FILE
    )


def is_application_completed(
    application_id: str,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    return (
        find_row_by_application_id(
            completed_sheet,
            application_id,
        )
        is not None
    )


def update_application_status_by_id(
    application_id: str,
    status: str,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    applications_sheet = (
        get_applications_sheet(
            workbook
        )
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    for sheet in (
        applications_sheet,
        completed_sheet,
    ):
        row_number = (
            find_row_by_application_id(
                sheet,
                application_id,
            )
        )

        if row_number is None:
            continue

        sheet.cell(
            row=row_number,
            column=16,
        ).value = status

        workbook.save(
            EXCEL_FILE
        )

        return True

    return False


def update_application_by_id(
    application_id: str,
    application: Application,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    applications_sheet = (
        get_applications_sheet(
            workbook
        )
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    for sheet in (
        applications_sheet,
        completed_sheet,
    ):
        row_number = (
            find_row_by_application_id(
                sheet,
                application_id,
            )
        )

        if row_number is None:
            continue

        values = [
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
            application_id,
        ]

        for column, value in enumerate(
            values,
            start=1,
        ):
            sheet.cell(
                row=row_number,
                column=column,
            ).value = value

        if (
            sheet.title
            == COMPLETED_SHEET
        ):
            format_completed_date_columns(
                sheet
            )

        else:
            format_date_columns(
                sheet
            )

        workbook.save(
            EXCEL_FILE
        )

        return True

    return False


def move_application_to_completed(
    application_id: str,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    applications_sheet = (
        get_applications_sheet(
            workbook
        )
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    row_number = (
        find_row_by_application_id(
            applications_sheet,
            application_id,
        )
    )

    if row_number is None:
        return False

    row_values = [
        applications_sheet.cell(
            row=row_number,
            column=column,
        ).value
        for column in range(
            1,
            18,
        )
    ]

    previous_status = (
        row_values[15]
        or ""
    )

    row_values[15] = (
        "Avslutad"
    )

    completed_sheet.append(
        [
            *row_values,
            date.today(),
            previous_status,
        ]
    )

    applications_sheet.delete_rows(
        row_number,
        1,
    )

    format_completed_date_columns(
        completed_sheet
    )

    workbook.save(
        EXCEL_FILE
    )

    return True


def restore_application_to_active(
    application_id: str,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    applications_sheet = (
        get_applications_sheet(
            workbook
        )
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    row_number = (
        find_row_by_application_id(
            completed_sheet,
            application_id,
        )
    )

    if row_number is None:
        return False

    if (
        find_row_by_application_id(
            applications_sheet,
            application_id,
        )
        is not None
    ):
        return False

    row_values = [
        completed_sheet.cell(
            row=row_number,
            column=column,
        ).value
        for column in range(
            1,
            18,
        )
    ]

    previous_status = (
        completed_sheet.cell(
            row=row_number,
            column=19,
        ).value
        or ""
    )

    row_values[15] = (
        previous_status
    )

    applications_sheet.append(
        row_values
    )

    completed_sheet.delete_rows(
        row_number,
        1,
    )

    format_date_columns(
        applications_sheet
    )

    workbook.save(
        EXCEL_FILE
    )

    return True


def delete_application_by_id(
    application_id: str,
) -> bool:
    if (
        not EXCEL_FILE.exists()
        or
        EXCEL_FILE.stat().st_size == 0
    ):
        return False

    workbook = load_workbook(
        EXCEL_FILE
    )

    ensure_application_ids(
        workbook
    )

    applications_sheet = (
        get_applications_sheet(
            workbook
        )
    )

    completed_sheet = (
        get_completed_sheet(
            workbook
        )
    )

    for sheet in (
        applications_sheet,
        completed_sheet,
    ):
        row_number = (
            find_row_by_application_id(
                sheet,
                application_id,
            )
        )

        if row_number is None:
            continue

        sheet.delete_rows(
            row_number,
            1,
        )

        evidence_sheet = (
            get_evidence_sheet(
                workbook
            )
        )

        for evidence_row in range(
            evidence_sheet.max_row,
            1,
            -1,
        ):
            if (
                evidence_sheet.cell(
                    row=evidence_row,
                    column=1,
                ).value
                == application_id
            ):
                evidence_sheet.delete_rows(
                    evidence_row,
                    1,
                )

        workbook.save(
            EXCEL_FILE
        )

        return True

    return False
