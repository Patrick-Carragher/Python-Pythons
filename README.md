# Python Testbed

Ett FastAPI-baserat testbed för att snabbt bygga, testa och utvärdera mindre webbappar, funktioner och proof-of-concepts.

Tanken är att kunna prova en idé i liten skala, se hur den fungerar i praktiken och därefter avgöra om den är värd att utveckla eller skala upp.

Projektet innehåller en gemensam portal där nya testappar kan skapas direkt från webbläsaren.

När en ny app skapas via portalen genereras automatiskt:

- Ett nytt kort i portalen
- En egen URL
- En HTML-fil
- En CSS-fil
- Metadata i `apps.json`

Efter det kan appen utvecklas vidare direkt i PyCharm, VS Code eller valfri annan IDE.

---

# Quickstart

## 1. Klona projektet

```bash
git clone https://github.com/Patrick-Carragher/Python-Pythons.git
cd Python-Pythons
```

## 2. Skapa en virtuell Python-miljö

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Terminalen bör därefter visa något liknande:

```text
(.venv)
```

## 3. Installera beroenden

```powershell
python -m pip install fastapi uvicorn python-multipart jinja2
```

Ytterligare beroenden kan tillkomma när nya testappar byggs.

## 4. Starta servern

För lokal utveckling:

```powershell
python -m uvicorn main:app --reload
```

Öppna:

```text
http://127.0.0.1:8000
```

Portalen visas på startsidan.

---

# Köra på lokala nätverket

För att göra testbeden tillgänglig från andra enheter på samma nätverk:

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Ta reda på datorns lokala IP-adress:

```powershell
ipconfig
```

Exempel:

```text
IPv4 Address: 192.168.1.206
```

Öppna sedan från en annan enhet:

```text
http://192.168.1.206:8000
```

Båda enheterna måste vara anslutna till samma nätverk.

---

# Projektstruktur

Projektet är uppdelat så att portalen och varje testapp kan ha separata HTML-, CSS- och Python-filer.

```text
Python-Pythons/
│
├── data/
│   └── apps.json
│
├── static/
│   │
│   ├── portal/
│   │   ├── portal.css
│   │   ├── portal.js
│   │   └── uploads/
│   │
│   ├── numbers/
│   │   └── style.css
│   │
│   ├── pdf/
│   │   └── ...
│   │
│   └── apps/
│       └── [genererade appar]
│
├── templates/
│   │
│   ├── portal/
│   │   └── portal.html
│   │
│   ├── numbers/
│   │   ├── base.html
│   │   ├── home.html
│   │   ├── game.html
│   │   ├── previous.html
│   │   └── interlude.html
│   │
│   ├── pdf/
│   │   └── pdf.html
│   │
│   └── apps/
│       └── [genererade appar]
│
├── main.py
├── portal_cards.py
├── game.py
├── cookies.py
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Hur projektet fungerar

## `main.py`

Projektets huvudsakliga FastAPI-applikation.

Här finns bland annat:

- Portalens routes
- Dynamisk route för genererade appar
- Numbers-appens routes
- PDF-appens routes
- Formulärhantering
- Template-rendering

Startsidan:

```text
/
```

visar testbed-portalen.

---

## `portal_cards.py`

Hanterar portalens app-generator.

Den ansvarar bland annat för att:

- Läsa `apps.json`
- Spara ändringar
- Skapa nya app-ID:n/slugs
- Skapa HTML-filer
- Skapa CSS-filer
- Hantera thumbnails/bilder
- Uppdatera befintliga kort

---

## `data/apps.json`

Innehåller portalens metadata.

Exempel:

```json
{
    "id": "qr-generator",
    "title": "QR Generator",
    "description": "Test av QR-koder.",
    "url": "/apps/qr-generator",
    "tags": [
        "Python",
        "FastAPI",
        "QR"
    ],
    "generated": true
}
```

Portalen använder denna information för att bygga korten.

---

# Skapa en ny app

Nya testappar ska i första hand skapas genom portalen.

## 1. Starta projektet

```powershell
python -m uvicorn main:app --reload
```

Öppna:

```text
http://127.0.0.1:8000
```

## 2. Aktivera redigeringsläge

Klicka på:

```text
✎ Redigera
```

nere till höger.

Portalen går då över till redigeringsläge.

Du får bland annat tillgång till:

```text
+ Nytt kort
```

och redigeringsknappar på befintliga kort.

## 3. Klicka på `+ Nytt kort`

Ett formulär öppnas.

Exempel:

```text
Titel:
QR Generator

App-ID / slug:
qr-generator

Beskrivning:
Test av generering av QR-koder.

Badge:
Ny

Thumbnail-text:
QR

Tags:
Python, FastAPI, QR

Thumbnail-typ:
Standard
```

`slug` används för appens filnamn och URL.

Om slug lämnas tom skapas den automatiskt från appens titel.

---

# Vad skapas automatiskt?

Om appen skapas med:

```text
qr-generator
```

skapas automatiskt:

```text
templates/
└── apps/
    └── qr-generator/
        └── qr-generator.html
```

samt:

```text
static/
└── apps/
    └── qr-generator/
        └── qr-generator.css
```

`data/apps.json` uppdateras samtidigt.

Appen får dessutom automatiskt URL:en:

```text
/apps/qr-generator
```

och kan därför öppnas direkt på:

```text
http://127.0.0.1:8000/apps/qr-generator
```

Ingen separat FastAPI-route behöver skapas manuellt för en vanlig genererad testapp.

---

# Jobba vidare med appen i en IDE

Portalen skapar bara grundstrukturen.

Efter att appen skapats fortsätter den normala utvecklingen i exempelvis:

- PyCharm
- VS Code
- IntelliJ
- annan valfri editor/IDE

För en app som heter:

```text
qr-generator
```

arbetar man framför allt i:

```text
templates/apps/qr-generator/qr-generator.html
```

och:

```text
static/apps/qr-generator/qr-generator.css
```

HTML-filen innehåller sidans struktur.

CSS-filen innehåller appens egna visuella styling.

Varje genererad app får därför sin egen CSS och kan designas helt oberoende av portalens eller andra appars styling.

---

# Lägga till Python-logik

En genererad app börjar som en enkel HTML/CSS-sida.

Om appen behöver egen backend-logik kan Python-kod sedan läggas till manuellt.

Exempel på funktioner som kan behöva egen Python-logik:

- PDF-generering
- QR-koder
- Filuppladdning
- API-anrop
- Excel/CSV-bearbetning
- Databasfunktioner
- Bildbehandling
- E-post
- Formulärbearbetning

För enklare appar kan logiken ligga i `main.py`.

När en app växer bör den hellre få en separat Python-fil.

Exempel:

```text
qr_generator.py
```

eller:

```text
apps/
└── qr_generator.py
```

och sedan importeras i FastAPI-applikationen.

---

# Specialappar

Alla appar behöver inte använda den automatiskt genererade strukturen.

Exempel:

```text
Numbers, à la Python
```

är en specialbyggd app med egen logik och egna routes.

Den ligger i:

```text
templates/numbers/
```

och:

```text
static/numbers/
```

PDF-generatorn kan på samma sätt utvecklas som en separat specialapp.

Dessa appar kan fortfarande visas och redigeras som kort i portalen.

---

# Redigera befintliga kort

Aktivera:

```text
✎ Redigera
```

och klicka därefter på:

```text
✎ Redigera
```

på ett specifikt kort.

Där kan bland annat följande ändras:

- Titel
- Beskrivning
- Badge
- Tags
- Thumbnail-text
- Thumbnail-typ
- Ordning
- Bild
- Bildbeskrivning

För specialappar kan även deras URL ändras.

För automatiskt genererade appar behålls deras `/apps/<slug>`-adress.

---

# Bilder och thumbnails

En egen bild kan laddas upp när ett kort skapas eller redigeras.

Uppladdade portalbilder lagras under:

```text
static/portal/uploads/
```

Tillåtna format:

```text
PNG
JPG
JPEG
WEBP
```

Maximal filstorlek:

```text
5 MB
```

Bilden används som thumbnail på portalens appkort.

---

# Dynamiska routes

Genererade appar använder en gemensam FastAPI-route:

```text
/apps/{app_id}
```

Det innebär exempelvis:

```text
/apps/qr-generator
/apps/csv-test
/apps/image-tool
/apps/api-demo
```

Alla kan hanteras av samma route.

Informationen i `apps.json` talar om vilken HTML-template som ska visas.

Det gör att `main.py` inte behöver få en ny route varje gång en grundapp skapas.

---

# Arbetsflöde

Det tänkta arbetsflödet är:

```text
Idé
  ↓
Öppna testbed-portalen
  ↓
Skapa ny app
  ↓
HTML + CSS + metadata genereras
  ↓
Öppna projektet i PyCharm eller annan IDE
  ↓
Bygg funktionaliteten
  ↓
Testa lokalt
  ↓
Utvärdera resultatet
  ↓
Commit + push
  ↓
Avgör om lösningen ska utvecklas vidare eller skalas upp
```

På så sätt fungerar projektet både som portal och som startpunkt för nya experiment.

---

# Git

Filer som skapas genom portalen skapas direkt i projektmappen och blir därför en del av det lokala Git-repot.

Efter att en app skapats kan man kontrollera ändringarna med:

```powershell
git status
```

Exempel:

```text
modified:
    data/apps.json

untracked:
    templates/apps/qr-generator/qr-generator.html
    static/apps/qr-generator/qr-generator.css
```

När ändringarna är redo:

```powershell
git add .
git commit -m "Add QR generator test app"
git push
```

Portalen gör **inte** automatiska commits eller pushar.

Det är medvetet så att utvecklaren alltid kan granska vad som har skapats eller ändrats innan det sparas i Git-historiken.

---

# Brancher

För större experiment rekommenderas en separat branch.

Exempel:

```powershell
git switch -c qr-generator
```

Efter utveckling:

```powershell
git add .
git commit -m "Add QR generator prototype"
git push -u origin qr-generator
```

Det gör att experiment kan utvecklas utan att påverka `main`.

---

# Virtuell miljö

`.venv` innehåller projektets lokala Python-installation och paket.

Den ska inte läggas till i Git.

Projektets `.gitignore` exkluderar bland annat:

```text
.venv/
.idea/
__pycache__/
.env
*.pyc
```

---

# Nuvarande exempelappar

## Numbers, à la Python

Demonstrerar bland annat:

- FastAPI
- Jinja2
- HTML-formulär
- Cookies
- Browser state
- Python-logik
- Dynamisk rendering

URL:

```text
/numbers
```

## PDF Generator

Testyta för generering av dokument/PDF från Python.

URL:

```text
/pdf
```

---

# Syfte

Projektet är inte tänkt att vara en enda färdig applikation.

Det är en gemensam sandbox/testbed där mindre idéer kan byggas snabbt och isolerat.

Målet är att kunna:

1. Testa en idé snabbt.
2. Bygga ett litet proof-of-concept.
3. Visa hur funktionen fungerar.
4. Utvärdera teknik och användbarhet.
5. Avgöra om lösningen är värd att utveckla vidare.
6. Skala upp lyckade experiment till större lösningar.

Det gör att nya tekniker och funktioner kan provas utan att först behöva bygga ett helt separat projekt för varje experiment.
