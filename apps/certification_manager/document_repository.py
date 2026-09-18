from pathlib import Path

from fastapi import UploadFile

from apps.certification_manager.folder_repository import (
    get_application_folder,
)
from apps.certification_manager.models import Application


ALLOWED_EXTENSIONS = {
    # Images
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".bmp",
    ".tif",
    ".tiff",

    # PDF
    ".pdf",

    # Microsoft Office
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",

    # Other documents
    ".txt",
    ".rtf",
    ".csv",
    ".odt",
    ".ods",
    ".odp",
}


def _safe_filename(
    filename: str,
) -> str:

    safe_name = Path(filename).name.strip()

    if not safe_name:

        raise ValueError(
            "Filen saknar ett giltigt filnamn."
        )

    return safe_name


def _validate_file(
    filename: str,
) -> None:

    extension = (
        Path(filename)
        .suffix
        .lower()
    )


    if extension not in ALLOWED_EXTENSIONS:

        raise ValueError(
            f"Filtypen '{extension or 'okänd'}' är inte tillåten. "
            "Endast bilder, PDF-filer och vanliga dokument får laddas upp."
        )


def _unique_destination(
    folder: Path,
    filename: str,
) -> Path:

    destination = (
        folder
        / filename
    )


    if not destination.exists():
        return destination


    path = Path(filename)

    stem = path.stem
    suffix = path.suffix

    counter = 2


    while True:

        destination = (
            folder
            / f"{stem} ({counter}){suffix}"
        )


        if not destination.exists():
            return destination


        counter += 1


async def save_documents(
    application: Application,
    files: list[UploadFile],
) -> list[str]:

    folder = get_application_folder(
        application
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )


    saved_files = []


    for uploaded_file in files:

        if not uploaded_file.filename:
            continue


        filename = _safe_filename(
            uploaded_file.filename
        )


        _validate_file(
            filename
        )


        destination = _unique_destination(
            folder,
            filename,
        )


        try:

            with destination.open(
                "wb"
            ) as output_file:

                while True:

                    chunk = await uploaded_file.read(
                        1024 * 1024
                    )


                    if not chunk:
                        break


                    output_file.write(
                        chunk
                    )


            saved_files.append(
                destination.name
            )


        finally:

            await uploaded_file.close()


    return saved_files


def list_documents(
    application: Application,
) -> list[dict]:

    folder = get_application_folder(
        application
    )


    if not folder.exists():
        return []


    documents = []


    for path in folder.iterdir():

        if not path.is_file():
            continue


        size = path.stat().st_size


        documents.append(
            {
                "name": path.name,
                "size": size,
                "size_text": _format_file_size(
                    size
                ),
            }
        )


    documents.sort(
        key=lambda document:
            document["name"].lower()
    )


    return documents


def delete_document(
    application: Application,
    filename: str,
) -> bool:

    folder = get_application_folder(
        application
    )


    if not folder.exists():
        return False


    safe_name = _safe_filename(
        filename
    )


    folder_resolved = folder.resolve()


    target = (
        folder
        / safe_name
    ).resolve()


    if target.parent != folder_resolved:

        raise ValueError(
            "Ogiltig filsökväg."
        )


    if not target.exists():
        return False


    if not target.is_file():

        raise ValueError(
            "Det valda objektet är inte en fil."
        )


    target.unlink()

    return True


def _format_file_size(
    size: int,
) -> str:

    if size < 1024:

        return f"{size} B"


    if size < 1024 * 1024:

        return (
            f"{size / 1024:.1f} KB"
        )


    return (
        f"{size / (1024 * 1024):.1f} MB"
    )