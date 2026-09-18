import uuid
import json
import socket

from datetime import datetime

from fastapi import (
    FastAPI,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
)

from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from apps.certification_manager.routes import router as certification_router

from cookies import (
    COOKIE_NAME,
    decode_cookie,
    save_completed_game,
)

from game import (
    create_game,
    get_game,
    delete_game,
    record_guess,
    set_avenge_answer,
    set_throw_answer,
)

from portal_cards import (
    create_generated_app,
    delete_image,
    find_app,
    load_apps,
    next_order,
    parse_tags,
    save_apps,
    save_image,
    update_app,
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# APP ROUTERS
# --------------------------------------------------

app.include_router(
    certification_router
)


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static/certification_manager",
    StaticFiles(
        directory="apps/certification_manager/static"
    ),
    name="certification_static",
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static",
)


# --------------------------------------------------
# HTML TEMPLATES
# --------------------------------------------------

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# TIME FORMAT
# --------------------------------------------------

def format_time(timestamp):

    if not timestamp:
        return "Not available"

    try:

        parsed = datetime.fromisoformat(
            timestamp
        )

        return parsed.strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    except ValueError:

        return timestamp


# --------------------------------------------------
# PORTAL
# --------------------------------------------------

@app.get("/")
def portal(
    request: Request
):

    apps = load_apps()

    return templates.TemplateResponse(
        request=request,
        name="portal/portal.html",
        context={
            "apps": apps
        },
    )


# --------------------------------------------------
# STARTUP
# --------------------------------------------------

@app.on_event("startup")
def show_urls():

    hostname = socket.gethostname()

    local_ip = socket.gethostbyname(
        hostname
    )

    print()
    print("========================================")
    print("Python Testbed")
    print("========================================")
    print()
    print("Öppna lokalt:")
    print("http://127.0.0.1:8000")
    print()
    print("Öppna från annan enhet på samma nätverk:")
    print(f"http://{local_ip}:8000")
    print()
    print("========================================")
    print()


# --------------------------------------------------
# GENERATED APP ROUTE
# --------------------------------------------------

@app.get(
    "/apps/{app_id}"
)
def generated_app(
    request: Request,
    app_id: str,
):

    apps = load_apps()

    app_data = find_app(
        apps,
        app_id,
    )

    if app_data is None:

        raise HTTPException(
            status_code=404,
            detail="Appen kunde inte hittas.",
        )

    if not app_data.get(
        "generated",
        False,
    ):

        raise HTTPException(
            status_code=404,
            detail="Appen använder en egen route.",
        )

    template_name = (
        app_data.get(
            "template"
        )
    )

    if (
        not template_name
        or not template_name.startswith(
            "apps/"
        )
        or ".." in template_name
    ):

        raise HTTPException(
            status_code=500,
            detail="Appens template är ogiltig.",
        )

    return templates.TemplateResponse(
        request=request,
        name=template_name,
        context={
            "app": app_data
        },
    )


# --------------------------------------------------
# CREATE / EDIT PORTAL CARD
# --------------------------------------------------

@app.post(
    "/portal/cards/save"
)
async def save_portal_card(

    app_id: str = Form(""),

    title: str = Form(...),

    description: str = Form(""),

    url: str = Form(""),

    slug: str = Form(""),

    badge: str = Form(""),

    tags: str = Form(""),

    thumbnail_label: str = Form(""),

    theme: str = Form("generic"),

    order: str = Form(""),

    image_alt: str = Form(""),

    remove_image: str | None = Form(
        None
    ),

    image: UploadFile | None = File(
        None
    ),

):

    apps = load_apps()


    # --------------------------------------------------
    # ORDER
    # --------------------------------------------------

    order_value = None

    if order.strip():

        try:

            order_value = int(
                order
            )

        except ValueError:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Ordning måste vara ett nummer."
                ),
            )


    # --------------------------------------------------
    # TAGS
    # --------------------------------------------------

    parsed_tags = parse_tags(
        tags
    )


    # --------------------------------------------------
    # FIND EXISTING APP
    # --------------------------------------------------

    existing_app = None

    if app_id:

        existing_app = find_app(
            apps,
            app_id,
        )

        if existing_app is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Kortet kunde inte hittas."
                ),
            )


    # --------------------------------------------------
    # CURRENT IMAGE
    # --------------------------------------------------

    current_image = (
        existing_app.get(
            "image"
        )
        if existing_app
        else None
    )


    # --------------------------------------------------
    # REMOVE IMAGE
    # --------------------------------------------------

    if remove_image == "true":

        delete_image(
            current_image
        )

        current_image = None


    # --------------------------------------------------
    # UPLOAD NEW IMAGE
    # --------------------------------------------------

    if (
        image
        and image.filename
    ):

        try:

            new_image = (
                await save_image(
                    image
                )
            )

        except ValueError as error:

            raise HTTPException(
                status_code=400,
                detail=str(
                    error
                ),
            )

        if current_image:

            delete_image(
                current_image
            )

        current_image = (
            new_image
        )


    # --------------------------------------------------
    # UPDATE EXISTING APP
    # --------------------------------------------------

    if existing_app:

        update_app(
            app=existing_app,
            title=title,
            description=description,
            url=url,
            badge=badge,
            tags=parsed_tags,
            thumbnail_label=thumbnail_label,
            theme=theme,
            image=current_image,
            image_alt=image_alt,
            order_value=order_value,
        )


    # --------------------------------------------------
    # CREATE NEW GENERATED APP
    # --------------------------------------------------

    else:

        create_generated_app(
            apps=apps,
            title=title,
            description=description,
            requested_slug=slug,
            badge=badge,
            tags=parsed_tags,
            thumbnail_label=thumbnail_label,
            theme=theme,
            image=current_image,
            image_alt=image_alt,
            order_value=order_value,
        )


    # --------------------------------------------------
    # SAVE JSON
    # --------------------------------------------------

    save_apps(
        apps
    )

    return RedirectResponse(
        url="/",
        status_code=303,
    )


# --------------------------------------------------
# NUMBERS HOME
# --------------------------------------------------

@app.get("/numbers")
def home(
    request: Request
):

    cookie_value = (
        request.cookies.get(
            COOKIE_NAME
        )
    )

    previous_game = decode_cookie(
        cookie_value
    )

    return templates.TemplateResponse(
        request=request,
        name="numbers/home.html",
        context={
            "has_previous_game":
                previous_game is not None
        },
    )


# --------------------------------------------------
# PREVIOUS ANSWER
# --------------------------------------------------

@app.get("/previous")
def previous_answer(
    request: Request
):

    cookie_value = (
        request.cookies.get(
            COOKIE_NAME
        )
    )

    previous_game = decode_cookie(
        cookie_value
    )

    if previous_game is None:

        return templates.TemplateResponse(
            request=request,
            name="numbers/previous.html",
            context={
                "previous_game": None,
                "raw_cookie": None,
                "decoded_cookie": None,
            },
        )

    previous_game[
        "started_at_formatted"
    ] = format_time(
        previous_game.get(
            "started_at"
        )
    )

    previous_game[
        "completed_at_formatted"
    ] = format_time(
        previous_game.get(
            "completed_at"
        )
    )

    decoded_cookie = json.dumps(
        previous_game,
        indent=4,
        ensure_ascii=False,
    )

    return templates.TemplateResponse(
        request=request,
        name="numbers/previous.html",
        context={
            "previous_game":
                previous_game,

            "raw_cookie":
                cookie_value,

            "decoded_cookie":
                decoded_cookie,
        },
    )


# --------------------------------------------------
# START GAME
# --------------------------------------------------

@app.post("/start")
def start_game(

    request: Request,

    name: str = Form(...),

    quest: str = Form(...),

):

    game_id = create_game(
        name,
        quest,
    )

    return templates.TemplateResponse(
        request=request,
        name="numbers/game.html",
        context={
            "view":
                "start",

            "game_id":
                game_id,

            "name":
                name,

            "quest":
                quest,
        },
    )


# --------------------------------------------------
# GUESS NUMBER
# --------------------------------------------------

@app.post("/guess")
def guess_number(

    request: Request,

    game_id: str = Form(...),

    guess: int = Form(...),

):

    game = get_game(
        game_id
    )

    if game is None:

        return templates.TemplateResponse(
            request=request,
            name="numbers/game.html",
            context={
                "view":
                    "not_found"
            },
        )

    record_guess(
        game,
        guess,
    )

    secret_number = (
        game[
            "secret_number"
        ]
    )

    attempts = (
        game[
            "attempts"
        ]
    )


    # --------------------------------------------------
    # CORRECT
    # --------------------------------------------------

    if guess == secret_number:

        response = (
            templates.TemplateResponse(
                request=request,
                name="numbers/game.html",
                context={
                    "view":
                        "correct",

                    "attempts":
                        attempts,
                },
            )
        )

        save_completed_game(
            response,
            game,
        )

        delete_game(
            game_id
        )

        return response


    # --------------------------------------------------
    # HIGH / LOW
    # --------------------------------------------------

    if guess > secret_number:

        result = "Too high!"

    else:

        result = "Too low!"


    # --------------------------------------------------
    # MORE ATTEMPTS
    # --------------------------------------------------

    if attempts < 3:

        return templates.TemplateResponse(
            request=request,
            name="numbers/game.html",
            context={
                "view":
                    "guess_again",

                "game_id":
                    game_id,

                "attempts":
                    attempts,

                "result":
                    result,
            },
        )


    # --------------------------------------------------
    # LOST
    # --------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="numbers/game.html",
        context={
            "view":
                "lost",

            "game_id":
                game_id,

            "attempts":
                attempts,

            "result":
                result,

            "name":
                game["name"],

            "secret_number":
                secret_number,
        },
    )


# --------------------------------------------------
# AVENGE
# --------------------------------------------------

@app.post("/avenge")
def avenge(

    request: Request,

    game_id: str = Form(...),

    answer: str = Form(...),

):

    game = get_game(
        game_id
    )

    if game is None:

        return templates.TemplateResponse(
            request=request,
            name="numbers/game.html",
            context={
                "view":
                    "not_found"
            },
        )

    set_avenge_answer(
        game,
        answer,
    )


    # --------------------------------------------------
    # YES
    # --------------------------------------------------

    if answer.lower() == "yes":

        return templates.TemplateResponse(
            request=request,
            name="numbers/game.html",
            context={
                "view":
                    "avenge",

                "game_id":
                    game_id,
            },
        )


    # --------------------------------------------------
    # NO
    # --------------------------------------------------

    response = (
        templates.TemplateResponse(
            request=request,
            name="numbers/interlude.html",
            context={},
        )
    )

    save_completed_game(
        response,
        game,
    )

    delete_game(
        game_id
    )

    return response


# --------------------------------------------------
# PDF APP
# --------------------------------------------------

@app.get("/pdf")
def pdf_home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="pdf/pdf.html",
        context={},
    )


# --------------------------------------------------
# HOLY HAND GRENADE
# --------------------------------------------------

@app.post("/throw")
def throw_grenade(

    request: Request,

    game_id: str = Form(...),

    throw: str = Form(...),

):

    game = get_game(
        game_id
    )

    if game is None:

        return templates.TemplateResponse(
            request=request,
            name="numbers/game.html",
            context={
                "view":
                    "not_found"
            },
        )

    set_throw_answer(
        game,
        throw,
    )

    correct = (
        throw.lower().strip()
        == "three"
        or
        throw.strip()
        == "3"
    )

    if correct:

        view = (
            "throw_correct"
        )

    else:

        view = (
            "throw_incorrect"
        )

    response = (
        templates.TemplateResponse(
            request=request,
            name="numbers/game.html",
            context={
                "view":
                    view
            },
        )
    )

    save_completed_game(
        response,
        game,
    )

    delete_game(
        game_id
    )

    return response