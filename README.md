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

## Köra på lokala nätverket

```powershell
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Öppna sedan datorns lokala IP från en annan enhet på samma nätverk, till exempel:

```text
http://192.168.1.206:8000
```
