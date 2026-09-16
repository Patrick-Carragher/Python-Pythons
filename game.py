import random
import uuid

from datetime import datetime


# --------------------------------------------------
# ACTIVE GAMES
# --------------------------------------------------

games = {}


# --------------------------------------------------
# CURRENT TIME
# --------------------------------------------------

def current_time():

    return datetime.now().astimezone().isoformat(
        timespec="seconds"
    )


# --------------------------------------------------
# CREATE GAME
# --------------------------------------------------

def create_game(
        name,
        quest
):

    game_id = str(
        uuid.uuid4()
    )

    games[game_id] = {

        "name":
            name,

        "quest":
            quest,

        "secret_number":
            random.randint(
                1,
                20
            ),

        "attempts":
            0,

        "guesses":
            [],

        "avenge":
            None,

        "throw":
            None,

        "started_at":
            current_time()
    }

    return game_id


# --------------------------------------------------
# GET GAME
# --------------------------------------------------

def get_game(
        game_id
):

    return games.get(
        game_id
    )


# --------------------------------------------------
# DELETE GAME
# --------------------------------------------------

def delete_game(
        game_id
):

    if game_id in games:

        del games[
            game_id
        ]


# --------------------------------------------------
# RECORD GUESS
# --------------------------------------------------

def record_guess(
        game,
        guess
):

    game["guesses"].append(
        guess
    )

    game["attempts"] += 1


# --------------------------------------------------
# AVENGE ANSWER
# --------------------------------------------------

def set_avenge_answer(
        game,
        answer
):

    game["avenge"] = answer


# --------------------------------------------------
# HOLY HAND GRENADE ANSWER
# --------------------------------------------------

def set_throw_answer(
        game,
        throw
):

    game["throw"] = throw