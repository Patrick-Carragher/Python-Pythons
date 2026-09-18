from datetime import date
from pathlib import Path

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from apps.certification_manager.document_repository import (
    delete_document,
    list_documents,
    save_documents,
)
from apps.certification_manager.excel_repository import (
    get_all_applications,
    get_application_by_row,
)
from apps.certification_manager.folder_repository import (
    get_application_folder,
)
from apps.certification_manager.models import Application
from apps.certification_manager.service import (
    create_application,
)


router = APIRouter(
    prefix="/certification",
    tags=["certification"],
)


templates = Jinja2Templates(
    directory=str(
        Path(__file__).parent
        / "templates"
    )
)


# ==================================================
# OVERVIEW
# ==================================================

@router.get("/")
def certification_overview(
    request: Request,
):

    applications = get_all_applications()

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "applications": applications,
        },
    )


# ==================================================
# NEW APPLICATION
# ==================================================

@router.get("/new")
def new_application_page(
    request: Request,
):

    return templates.TemplateResponse(
        request=request,
        name="new_application.html",
        context={
            "today": date.today(),
        },
    )


# ==================================================
# CREATE APPLICATION
# ==================================================

@router.post("/new")
def create_new_application(
    request: Request,

    ankom: date = Form(...),

    namn: str = Form(...),

    personnummer: str = Form(...),

    ny_eller_omcertifiering: str = Form(...),

    norm: str = Form(...),

    foretag: str = Form(...),

    adress: str = Form(...),

    mail: str = Form(...),

    mail_privat: str = Form(""),

    telefon: str = Form(""),

    examinationsdatum: date | None = Form(None),

    utb_hos_sakerhetsbransch: str = Form(""),

    plats: str = Form(""),

    ovrigt: str = Form(""),

    resultat: str = Form(""),

    status: str = Form(""),
):

    application = Application(
        ankom=ankom,
        namn=namn,
        personnummer=personnummer,
        ny_eller_omcertifiering=ny_eller_omcertifiering,
        norm=norm,
        foretag=foretag,
        adress=adress,
        mail=mail,
        mail_privat=mail_privat,
        telefon=telefon,
        examinationsdatum=examinationsdatum,
        utb_hos_sakerhetsbransch=utb_hos_sakerhetsbransch,
        plats=plats,
        ovrigt=ovrigt,
        resultat=resultat,
        status=status,
    )


    try:

        create_application(
            application
        )


    except ValueError as error:

        return templates.TemplateResponse(
            request=request,
            name="new_application.html",
            context={
                "today": date.today(),
                "error": str(error),
                "application": application,
            },
            status_code=400,
        )


    return RedirectResponse(
        url="/certification/",
        status_code=303,
    )


# ==================================================
# APPLICATION / PERSON PAGE
# ==================================================

@router.get(
    "/application/{row_number}"
)
def application_page(
    request: Request,
    row_number: int,
):

    application = get_application_by_row(
        row_number
    )


    if application is None:

        raise HTTPException(
            status_code=404,
            detail="Ärendet kunde inte hittas.",
        )


    folder = get_application_folder(
        application
    )


    documents = list_documents(
        application
    )


    return templates.TemplateResponse(
        request=request,
        name="person.html",
        context={
            "application": application,
            "row_number": row_number,
            "folder": folder,
            "documents": documents,
        },
    )


# ==================================================
# UPLOAD DOCUMENTS
# ==================================================

@router.post(
    "/application/{row_number}/documents/upload"
)
async def upload_application_documents(
    row_number: int,

    files: list[UploadFile] = File(...),
):

    application = get_application_by_row(
        row_number
    )


    if application is None:

        raise HTTPException(
            status_code=404,
            detail="Ärendet kunde inte hittas.",
        )


    try:

        await save_documents(
            application,
            files,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    return RedirectResponse(
        url=(
            f"/certification/"
            f"application/{row_number}"
        ),
        status_code=303,
    )


# ==================================================
# DELETE DOCUMENT
# ==================================================

@router.post(
    "/application/{row_number}/documents/delete"
)
def delete_application_document(
    row_number: int,

    filename: str = Form(...),
):

    application = get_application_by_row(
        row_number
    )


    if application is None:

        raise HTTPException(
            status_code=404,
            detail="Ärendet kunde inte hittas.",
        )


    try:

        deleted = delete_document(
            application,
            filename,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="Filen kunde inte hittas.",
        )


    return RedirectResponse(
        url=(
            f"/certification/"
            f"application/{row_number}"
        ),
        status_code=303,
    )