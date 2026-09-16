import json

from datetime import datetime

from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cookies import (
    COOKIE_NAME,
    decode_cookie,
    save_completed_game
)

from game import (
    create_game,
    get_game,
    delete_game,
    record_guess,
    set_avenge_answer,
    set_throw_answer
)


# --------------------------------------------------
# FASTAPI APPLICATION
# --------------------------------------------------

app = FastAPI()


# --------------------------------------------------
# STATIC FILES
# --------------------------------------------------

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
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
# START PAGE
# --------------------------------------------------

@app.get("/")
def portal(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="portal/portal.html",
        context={}
    )


@app.get("/numbers")
def home(request: Request):
    cookie_value = request.cookies.get(COOKIE_NAME)
    previous_game = decode_cookie(cookie_value)

    return templates.TemplateResponse(
        request=request,
        name="numbers/home.html",
        context={
            "has_previous_game": previous_game is not None
        }
    )

# --------------------------------------------------
# PREVIOUS ANSWER PAGE
# --------------------------------------------------

@app.get("/previous")
def previous_answer(
        request: Request
):

    cookie_value = request.cookies.get(
        COOKIE_NAME
    )

    previous_game = decode_cookie(
        cookie_value
    )


    if previous_game is None:

        return templates.TemplateResponse(
            request=request,
            name="previous.html",
            context={
                "previous_game": None,
                "raw_cookie": None,
                "decoded_cookie": None
            }
        )


    previous_game["started_at_formatted"] = format_time(
        previous_game.get(
            "started_at"
        )
    )


    previous_game["completed_at_formatted"] = format_time(
        previous_game.get(
            "completed_at"
        )
    )


    decoded_cookie = json.dumps(
        previous_game,
        indent=4,
        ensure_ascii=False
    )


    return templates.TemplateResponse(
        request=request,
        name="previous.html",
        context={
            "previous_game": previous_game,
            "raw_cookie": cookie_value,
            "decoded_cookie": decoded_cookie
        }
    )


# --------------------------------------------------
# START GAME
# --------------------------------------------------

@app.post("/start")
def start_game(
        request: Request,
        name: str = Form(...),
        quest: str = Form(...)
):

    game_id = create_game(
        name,
        quest
    )

    return templates.TemplateResponse(
        request=request,
        name="game.html",
        context={
            "view": "start",
            "game_id": game_id,
            "name": name,
            "quest": quest
        }
    )


# --------------------------------------------------
# GUESS NUMBER
# --------------------------------------------------

@app.post("/guess")
def guess_number(
        request: Request,
        game_id: str = Form(...),
        guess: int = Form(...)
):

    game = get_game(
        game_id
    )

    if game is None:

        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "view": "not_found"
            }
        )

    record_guess(
        game,
        guess
    )

    secret_number = game[
        "secret_number"
    ]

    attempts = game[
        "attempts"
    ]


    # --------------------------------------------------
    # CORRECT GUESS
    # --------------------------------------------------

    if guess == secret_number:

        response = templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "view": "correct",
                "attempts": attempts
            }
        )

        save_completed_game(
            response,
            game
        )

        delete_game(
            game_id
        )

        return response


    # --------------------------------------------------
    # TOO HIGH / TOO LOW
    # --------------------------------------------------

    if guess > secret_number:

        result = "Too high!"

    else:

        result = "Too low!"


    # --------------------------------------------------
    # STILL HAS ATTEMPTS
    # --------------------------------------------------

    if attempts < 3:

        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "view": "guess_again",
                "game_id": game_id,
                "attempts": attempts,
                "result": result
            }
        )


    # --------------------------------------------------
    # PLAYER LOST
    # --------------------------------------------------

    return templates.TemplateResponse(
        request=request,
        name="game.html",
        context={
            "view": "lost",
            "game_id": game_id,
            "attempts": attempts,
            "result": result,
            "name": game["name"],
            "secret_number": secret_number
        }
    )


# --------------------------------------------------
# AVENGE
# --------------------------------------------------

@app.post("/avenge")
def avenge(
        request: Request,
        game_id: str = Form(...),
        answer: str = Form(...)
):

    game = get_game(
        game_id
    )

    if game is None:

        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "view": "not_found"
            }
        )

    set_avenge_answer(
        game,
        answer
    )


    # --------------------------------------------------
    # YES
    # --------------------------------------------------

    if answer.lower() == "yes":

        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "view": "avenge",
                "game_id": game_id
            }
        )


    # --------------------------------------------------
    # NO
    # --------------------------------------------------

    response = templates.TemplateResponse(
        request=request,
        name="interlude.html",
        context={}
    )

    save_completed_game(
        response,
        game
    )

    delete_game(
        game_id
    )

    return response


# --------------------------------------------------
# HOLY HAND GRENADE ANSWER
# --------------------------------------------------

@app.post("/throw")
def throw_grenade(
        request: Request,
        game_id: str = Form(...),
        throw: str = Form(...)
):

    game = get_game(
        game_id
    )

    if game is None:

        return templates.TemplateResponse(
            request=request,
            name="game.html",
            context={
                "view": "not_found"
            }
        )

    set_throw_answer(
        game,
        throw
    )

    correct = (
        throw.lower().strip() == "three"
        or throw.strip() == "3"
    )


    # --------------------------------------------------
    # CORRECT
    # --------------------------------------------------

    if correct:

        view = "throw_correct"


    # --------------------------------------------------
    # WRONG
    # --------------------------------------------------

    else:

        view = "throw_incorrect"


    response = templates.TemplateResponse(
        request=request,
        name="game.html",
        context={
            "view": view
        }
    )

    save_completed_game(
        response,
        game
    )

    delete_game(
        game_id
    )

    return response