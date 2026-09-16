import base64
import binascii
import json

from datetime import datetime


# --------------------------------------------------
# COOKIE SETTINGS
# --------------------------------------------------

COOKIE_NAME = "numbers_last_game"

# 7 days
COOKIE_MAX_AGE = 60 * 60 * 24 * 7


# --------------------------------------------------
# CURRENT TIME
# --------------------------------------------------

def current_time():

    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


# --------------------------------------------------
# ENCODE COOKIE
# --------------------------------------------------

def encode_cookie(
        data
):

    json_data = json.dumps(
        data,
        ensure_ascii=False
    )

    return base64.urlsafe_b64encode(
        json_data.encode(
            "utf-8"
        )
    ).decode(
        "utf-8"
    )


# --------------------------------------------------
# DECODE COOKIE
# --------------------------------------------------

def decode_cookie(
        cookie_value
):

    if not cookie_value:

        return None

    try:

        decoded = base64.urlsafe_b64decode(
            cookie_value.encode(
                "utf-8"
            )
        ).decode(
            "utf-8"
        )

        return json.loads(
            decoded
        )

    except (
        ValueError,
        UnicodeDecodeError,
        json.JSONDecodeError,
        binascii.Error
    ):

        return None


# --------------------------------------------------
# SAVE COMPLETED GAME
# --------------------------------------------------

def save_completed_game(
        response,
        game
):

    completed_game = {

        "name":
            game.get(
                "name"
            ),

        "quest":
            game.get(
                "quest"
            ),

        "guesses":
            game.get(
                "guesses",
                []
            ),

        "avenge":
            game.get(
                "avenge"
            ),

        "throw":
            game.get(
                "throw"
            ),

        "started_at":
            game.get(
                "started_at"
            ),

        "completed_at":
            current_time()
    }

    response.set_cookie(

        key=COOKIE_NAME,

        value=encode_cookie(
            completed_game
        ),

        max_age=COOKIE_MAX_AGE,

        httponly=True,

        samesite="lax",

        path="/"
    )