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
    delete_application_by_id,
    get_all_applications,
    get_application_by_id,
    update_application_status_by_id,
)
from apps.certification_manager.folder_repository import (
    get_application_folder,
)
from apps.certification_manager.models import (
    Application,
)
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


HANDLING_STATUS_OPTIONS = (
    "Ansökan inkommit – mottagningsbekräftelse ej skickad",
    "Kallelse ej skickad (i kö)",
    "Kallelse ej skickad (lokal ej fastställd)",
)


STATUS_INDEX_LABELS = {
    "Ansökan inkommit – mottagningsbekräftelse ej skickad":
        "Ej bekräftad",

    "Kallelse ej skickad (i kö)":
        "I kö",

    "Kallelse ej skickad (lokal ej fastställd)":
        "Lokal saknas",
}


STATUS_CSS_CLASSES = {
    "Ansökan inkommit – mottagningsbekräftelse ej skickad":
        "handling-status-confirmation",

    "Kallelse ej skickad (i kö)":
        "handling-status-queue",

    "Kallelse ej skickad (lokal ej fastställd)":
        "handling-status-location",
}


VALID_HANDLING_STATUSES = {
    "",
    *HANDLING_STATUS_OPTIONS,
}


@router.get("/")
def certification_overview(
    request: Request,
):
    applications = (
        get_all_applications()
    )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "applications":
                applications,

            "status_index_labels":
                STATUS_INDEX_LABELS,

            "status_css_classes":
                STATUS_CSS_CLASSES,
        },
    )


@router.get("/new")
def new_application_page(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="new_application.html",
        context={
            "today":
                date.today(),
        },
    )


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
    examinationsdatum:
        date | None = Form(None),
    utb_hos_sakerhetsbransch:
        str = Form(""),
    plats: str = Form(""),
    ovrigt: str = Form(""),
    resultat: str = Form(""),
    status: str = Form(""),
):
    application = Application(
        ankom=ankom,
        namn=namn,
        personnummer=personnummer,
        ny_eller_omcertifiering=(
            ny_eller_omcertifiering
        ),
        norm=norm,
        foretag=foretag,
        adress=adress,
        mail=mail,
        mail_privat=mail_privat,
        telefon=telefon,
        examinationsdatum=(
            examinationsdatum
        ),
        utb_hos_sakerhetsbransch=(
            utb_hos_sakerhetsbransch
        ),
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
                "today":
                    date.today(),

                "error":
                    str(error),

                "application":
                    application,
            },
            status_code=400,
        )

    return RedirectResponse(
        url="/certification/",
        status_code=303,
    )


@router.get(
    "/application/{application_id}"
)
def application_page(
    request: Request,
    application_id: str,
):
    application = (
        get_application_by_id(
            application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Ärendet kunde inte "
                "hittas."
            ),
        )

    folder = (
        get_application_folder(
            application
        )
    )

    documents = (
        list_documents(
            application
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="person.html",
        context={
            "application":
                application,

            "folder":
                folder,

            "documents":
                documents,

            "handling_status_options":
                HANDLING_STATUS_OPTIONS,

            "status_css_classes":
                STATUS_CSS_CLASSES,
        },
    )


@router.post(
    "/application/{application_id}/status"
)
def update_application_status(
    application_id: str,
    status: str = Form(""),
):
    if (
        status
        not in VALID_HANDLING_STATUSES
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Ogiltig "
                "handläggningsstatus."
            ),
        )

    application = (
        get_application_by_id(
            application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Ärendet kunde inte "
                "hittas."
            ),
        )

    updated = (
        update_application_status_by_id(
            application_id,
            status,
        )
    )

    if not updated:
        raise HTTPException(
            status_code=404,
            detail=(
                "Status kunde inte "
                "uppdateras."
            ),
        )

    return RedirectResponse(
        url=(
            f"/certification/"
            f"application/"
            f"{application_id}"
        ),
        status_code=303,
    )


@router.post(
    "/application/{application_id}/delete"
)
def delete_application(
    application_id: str,
):
    application = (
        get_application_by_id(
            application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Ärendet kunde inte "
                "hittas."
            ),
        )

    deleted = (
        delete_application_by_id(
            application_id
        )
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=(
                "Ärendet kunde inte "
                "tas bort."
            ),
        )

    return RedirectResponse(
        url="/certification/",
        status_code=303,
    )


@router.post(
    "/application/{application_id}/documents/upload"
)
async def upload_application_documents(
    application_id: str,
    files: list[
        UploadFile
    ] = File(...),
):
    application = (
        get_application_by_id(
            application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Ärendet kunde inte "
                "hittas."
            ),
        )

    try:
        await save_documents(
            application,
            files,
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )

    return RedirectResponse(
        url=(
            f"/certification/"
            f"application/"
            f"{application.application_id}"
        ),
        status_code=303,
    )


@router.post(
    "/application/{application_id}/documents/delete"
)
def delete_application_document(
    application_id: str,
    filename: str = Form(...),
):
    application = (
        get_application_by_id(
            application_id
        )
    )

    if application is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Ärendet kunde inte "
                "hittas."
            ),
        )

    try:
        deleted = (
            delete_document(
                application,
                filename,
            )
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(
                error
            ),
        )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=(
                "Filen kunde inte "
                "hittas."
            ),
        )

    return RedirectResponse(
        url=(
            f"/certification/"
            f"application/"
            f"{application.application_id}"
        ),
        status_code=303,
    )
