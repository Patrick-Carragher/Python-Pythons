import json
import uuid
from pathlib import Path

from fastapi import UploadFile


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "apps.json"
UPLOAD_DIR = BASE_DIR / "static" / "portal" / "uploads"

ALLOWED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


def load_apps():
    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open("r", encoding="utf-8") as file:
        apps = json.load(file)

    return sorted(
        apps,
        key=lambda app: app.get("order", 9999)
    )


def save_apps(apps):
    DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with DATA_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            apps,
            file,
            indent=4,
            ensure_ascii=False
        )


def find_app(apps, app_id):
    for app in apps:
        if app.get("id") == app_id:
            return app

    return None


def parse_tags(tags):
    return [
        tag.strip()
        for tag in tags.split(",")
        if tag.strip()
    ]


def next_order(apps):
    if not apps:
        return 1

    return max(
        app.get("order", 0)
        for app in apps
    ) + 1


async def save_image(image: UploadFile):
    if not image.filename:
        return None

    extension = Path(
        image.filename
    ).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            "Endast PNG, JPG, JPEG och WEBP är tillåtna."
        )

    content = await image.read()

    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError(
            "Bilden får vara maximalt 5 MB."
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"{uuid.uuid4().hex}{extension}"
    )

    destination = (
        UPLOAD_DIR / filename
    )

    destination.write_bytes(content)

    return (
        f"/static/portal/uploads/{filename}"
    )


def delete_image(image_url):
    if not image_url:
        return

    prefix = "/static/portal/uploads/"

    if not image_url.startswith(prefix):
        return

    filename = Path(
        image_url
    ).name

    image_path = (
        UPLOAD_DIR / filename
    )

    if image_path.exists():
        image_path.unlink()