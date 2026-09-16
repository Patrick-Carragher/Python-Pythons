# Quickstart

## 1. Klona projektet

```bash
git clone https://github.com/Patrick-Carragher/Python-Pythons.git
cd Python-Pythons
```

## 2. Skapa och aktivera en virtuell miljö

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3. Installera beroenden

```powershell
python -m pip install fastapi uvicorn python-multipart jinja2
```

## 4. Starta applikationen

```powershell
python -m uvicorn main:app --reload
```

Öppna sedan:

```text
http://127.0.0.1:8000
```

Startsidan är en portal med projektets olika testappar och proof-of-concepts.

Exempel:

```text
/
→ Testbed-portal

/numbers
→ Numbers, à la Python
```

## Köra på lokala nätverket

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Öppna sedan datorns lokala IP från en annan enhet på samma nätverk, till exempel:

```text
http://192.168.1.206:8000
```

# Projektstruktur

Projektet är uppdelat så att varje testapp kan ha sina egna templates och sin egen CSS.

```text
Python-Pythons/
│
├── templates/
│   ├── portal/
│   │   └── portal.html
│   │
│   └── numbers/
│       ├── base.html
│       ├── home.html
│       ├── game.html
│       ├── previous.html
│       └── interlude.html
│
├── static/
│   ├── portal/
│   │   └── portal.css
│   │
│   └── numbers/
│       └── style.css
│
├── main.py
├── game.py
├── cookies.py
├── pyproject.toml
└── uv.lock
```

## Hur det fungerar

`main.py` är ingången till applikationen och innehåller FastAPI-routes.

```text
/
→ laddar portal/portal.html

/numbers
→ laddar Numbers-appen
```

`templates/` innehåller HTML-filerna för respektive app.

```text
templates/portal/
→ Portalens HTML

templates/numbers/
→ Numbers-appens HTML
```

`static/` innehåller CSS och andra statiska filer.

```text
static/portal/
→ Portalens CSS

static/numbers/
→ Numbers-appens CSS
```

`game.py` innehåller logiken för Numbers-spelet.

`cookies.py` hanterar sparad information i cookies.

När en ny testapp läggs till kan den få sin egen struktur, till exempel:

```text
templates/pdf/
static/pdf/
```

På så sätt hålls apparna separerade och kan ha helt olika design och funktionalitet.
