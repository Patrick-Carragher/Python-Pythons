# Quickstart

This project is a small FastAPI web game built with Python, Jinja2, cookies, HTML and CSS.

## Requirements

Make sure you have Python installed.

Recommended:

- Python 3.12+
- Git
- PyCharm or another Python IDE

---

## 1. Clone the repository

```bash
git clone https://github.com/Patrick-Carragher/Python-Pythons.git
cd Python-Pythons
```

---

## 2. Create a virtual environment

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When the virtual environment is active, the terminal should show something similar to:

```text
(.venv)
```

---

## 3. Install dependencies

```bash
python -m pip install fastapi uvicorn python-multipart jinja2
```

The main dependencies are:

- `FastAPI` — web framework
- `Uvicorn` — web server
- `python-multipart` — handles HTML form submissions
- `Jinja2` — renders dynamic HTML templates

---

## 4. Start the application

For normal local development:

```bash
python -m uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The `--reload` option automatically restarts the application when Python files are changed.

---

## 5. Access from another device on the same network

Start Uvicorn with:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Find the computer's local IPv4 address.

On Windows:

```powershell
ipconfig
```

Look for something similar to:

```text
IPv4 Address . . . . . . . . . . : 192.168.1.206
```

Then another device on the same network can open:

```text
http://192.168.1.206:8000
```

Both devices must be connected to the same local network.

Windows Firewall may ask for permission the first time the server is exposed to the local network. Allow Python on private networks if required.

---

# Project structure

```text
PythonProject/
│
├── static/
│   └── style.css
│
├── templates/
│   ├── base.html
│   ├── game.html
│   ├── home.html
│   ├── interlude.html
│   └── previous.html
│
├── cookies.py
├── game.py
├── main.py
├── pyproject.toml
├── uv.lock
└── .gitignore
```

---

# What the files do

## `main.py`

Contains the FastAPI application and routes.

Examples:

```text
/
```

Start page.

```text
/start
```

Starts a new game.

```text
/guess
```

Handles number guesses.

```text
/avenge
```

Handles the avenge choice.

```text
/throw
```

Handles the Holy Hand Grenade answer.

```text
/previous
```

Displays the previous completed game stored in the browser cookie.

---

## `game.py`

Contains the game state and game logic.

Active games are stored in memory while the application is running.

This means unfinished games disappear if Uvicorn is restarted.

---

## `cookies.py`

Handles the previous-answer cookie.

The last completed game is stored in the user's browser for:

```text
7 days
```

The cookie stores information such as:

```json
{
    "name": "Galahad",
    "quest": "Grail",
    "guesses": [
        2,
        4,
        5
    ],
    "avenge": "no",
    "throw": null,
    "started_at": "2026-09-16T10:15:25+02:00",
    "completed_at": "2026-09-16T10:15:32+02:00"
}
```

The secret number is not stored in the cookie.

The cookie is Base64 encoded.

Base64 is not encryption and should not be used to protect sensitive information.

---

## `templates/`

Contains the Jinja2 HTML templates.

### `base.html`

Shared base HTML used by the other pages.

### `home.html`

Start page.

### `game.html`

Main game interface.

### `previous.html`

Displays the previous completed game and cookie debugging information.

### `interlude.html`

Displays the narrative interlude.

---

## `static/style.css`

Contains all visual styling for the application.

This includes:

- dark background
- yellow/gold theme
- buttons
- inputs
- cards
- responsive mobile layout
- result screens
- previous-answer page
- cookie debugging interface
- JSON/IDE-style cookie display

---

# Cookies

After a game has been completed, the browser receives a cookie named:

```text
numbers_last_game
```

The cookie expires after seven days.

In Chrome it can be inspected through:

```text
F12
→ Application
→ Storage
→ Cookies
→ http://127.0.0.1:8000
```

The Previous Answer page also contains a debug section where the raw and decoded cookie can be inspected.

---

# Development

Start the development server with:

```bash
python -m uvicorn main:app --reload
```

After changing HTML or CSS, refresh the browser.

If CSS appears to be cached, use a hard refresh:

```text
Ctrl + F5
```

---

# Local network testing

To make the server available to other devices on the same network:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Your own computer can still use:

```text
http://127.0.0.1:8000
```

Other devices use your computer's local IP, for example:

```text
http://192.168.1.206:8000
```

A `192.168.x.x` address is only accessible from the local network and is not a public internet address.

---

# Git

Typical Git workflow:

```bash
git status
git add .
git commit -m "Describe changes here"
git push
```

The following should not be committed:

```text
.venv/
.idea/
__pycache__/
.env
*.pyc
```

These are excluded through `.gitignore`.

---

# Notes

The project currently uses an in-memory dictionary for active games.

Because of this:

```text
Completed game cookie
→ survives application restart

Unfinished active game
→ disappears when the server restarts
```

For this project that is intentional and keeps the application simple.

A database such as SQLite could be added later if persistent active games or game history are required.
