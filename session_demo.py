import secrets

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# --------------------------------------------------
# ROUTER
# --------------------------------------------------

router = APIRouter(
    prefix="/api/session-demo",
    tags=["Session Demo"]
)


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

COOKIE_NAME = "testbed_session_id"

SESSION_TTL_MINUTES = 30


# --------------------------------------------------
# SERVER-SIDE SESSION STORAGE
# --------------------------------------------------

sessions = {}


# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------

class StartSessionRequest(BaseModel):
    secure: bool = False


class ChoiceRequest(BaseModel):
    choice: str


class AnswerRequest(BaseModel):
    answer: str


# --------------------------------------------------
# TIME
# --------------------------------------------------

def now():
    return datetime.now(
        timezone.utc
    )


# --------------------------------------------------
# CLEAN EXPIRED SESSIONS
# --------------------------------------------------

def cleanup_sessions():

    current_time = now()

    expired_sessions = []


    for session_id, session in sessions.items():

        expires_at = session.get(
            "expires_at"
        )

        if (
            expires_at
            and expires_at < current_time
        ):

            expired_sessions.append(
                session_id
            )


    for session_id in expired_sessions:

        sessions.pop(
            session_id,
            None
        )


# --------------------------------------------------
# GET SESSION
# --------------------------------------------------

def get_session(
    request: Request
):

    cleanup_sessions()


    session_id = request.cookies.get(
        COOKIE_NAME
    )


    if not session_id:
        return None, None


    session = sessions.get(
        session_id
    )


    if not session:
        return session_id, None


    session["last_seen"] = now()


    return session_id, session


# --------------------------------------------------
# START SESSION
# --------------------------------------------------

@router.post("/start")
def start_session(
    data: StartSessionRequest
):

    cleanup_sessions()


    session_id = secrets.token_urlsafe(
        32
    )


    created_at = now()

    expires_at = (
        created_at
        + timedelta(
            minutes=SESSION_TTL_MINUTES
        )
    )


    sessions[session_id] = {

        "created_at":
            created_at,

        "last_seen":
            created_at,

        "expires_at":
            expires_at,

        "secure":
            data.secure,

        "door":
            None,

        "answer_correct":
            None
    }


    response = JSONResponse(
        content={
            "success": True,
            "message": "Session skapad.",
            "secure": data.secure
        }
    )


    response.set_cookie(

        key=COOKIE_NAME,

        value=session_id,

        max_age=(
            SESSION_TTL_MINUTES
            * 60
        ),

        httponly=True,

        secure=data.secure,

        samesite="lax",

        path="/"
    )


    return response


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

@router.get("/state")
def session_state(
    request: Request
):

    session_id, session = get_session(
        request
    )


    if not session:

        return {
            "active": False,
            "cookie_received": bool(
                session_id
            )
        }


    return {

        "active":
            True,

        "session_id_preview":
            (
                session_id[:8]
                + "..."
                + session_id[-5:]
            ),

        "cookie": {

            "name":
                COOKIE_NAME,

            "httponly":
                True,

            "secure":
                session["secure"],

            "samesite":
                "lax",

            "max_age":
                SESSION_TTL_MINUTES * 60
        },

        "session": {

            "door":
                session["door"],

            "answer_correct":
                session["answer_correct"],

            "created_at":
                session["created_at"].isoformat(),

            "last_seen":
                session["last_seen"].isoformat()
        }
    }


# --------------------------------------------------
# CHOOSE DOOR
# --------------------------------------------------

@router.post("/choose")
def choose_door(
    request: Request,
    data: ChoiceRequest
):

    session_id, session = get_session(
        request
    )


    if not session:

        raise HTTPException(
            status_code=401,
            detail="Ingen aktiv session."
        )


    choice = (
        data.choice
        .strip()
        .upper()
    )


    if choice not in {
        "A",
        "B"
    }:

        raise HTTPException(
            status_code=400,
            detail="Valet måste vara A eller B."
        )


    session["door"] = choice

    session["answer_correct"] = None


    return {
        "success": True,
        "message": "Valet har sparats i sessionen."
    }


# --------------------------------------------------
# ANSWER
# --------------------------------------------------

@router.post("/answer")
def answer_question(
    request: Request,
    data: AnswerRequest
):

    session_id, session = get_session(
        request
    )


    if not session:

        raise HTTPException(
            status_code=401,
            detail="Ingen aktiv session."
        )


    if not session["door"]:

        raise HTTPException(
            status_code=400,
            detail="Du måste först välja en dörr."
        )


    answer = (
        data.answer
        .strip()
        .upper()
    )


    correct = (
        answer
        == session["door"]
    )


    session[
        "answer_correct"
    ] = correct


    if correct:

        message = (
            "Rätt. Servern kom ihåg ditt tidigare val."
        )

    else:

        message = (
            "Fel. Servern kom ihåg ett annat val."
        )


    return {

        "success":
            True,

        "correct":
            correct,

        "message":
            message
    }


# --------------------------------------------------
# RESET
# --------------------------------------------------

@router.post("/reset")
def reset_session(
    request: Request
):

    session_id = request.cookies.get(
        COOKIE_NAME
    )


    if session_id:

        sessions.pop(
            session_id,
            None
        )


    response = JSONResponse(
        content={
            "success": True
        }
    )


    response.delete_cookie(
        key=COOKIE_NAME,
        path="/"
    )


    return response