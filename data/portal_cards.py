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
    ".webp",
    ".gif",
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

    temporary_file = DATA_FILE.with_suffix(".tmp")

    temporary_file.write_text(
        json.dumps(
            apps,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    temporary_file.replace(DATA_FILE)


def get_app(apps, app_id):
    for app in apps:
        if app.get("id") == app_id:
            return app

    return None


def parse_tags(tags):
    result = []

    for tag in tags.split(","):
        cleaned_tag = tag.strip()

        if cleaned_tag and cleaned_tag not in result:
            result.append(cleaned_tag)

    return result


def get_next_order(apps):
    if not apps:
        return 1

    return max(
        app.get("order", 0)
        for app in apps
    ) + 1


def create_app(
    apps,
    title,
    description,
    url,
    badge,
    tags,
    thumbnail_label,
    theme,
    image,
    image_alt,
    order=None
):
    app = {
        "id": f"app-{uuid.uuid4().hex[:8]}",
        "title": title.strip(),
        "description": description.strip(),
        "url": url.strip(),
        "badge": badge.strip(),
        "tags": tags,
        "thumbnail_label": thumbnail_label.strip(),
        "theme": theme,
        "image": image,
        "image_alt": image_alt.strip(),
        "order": (
            order
            if order is not None
            else get_next_order(apps)
        )
    }

    apps.append(app)

    return app


def update_app(
    app,
    title,
    description,
    url,
    badge,
    tags,
    thumbnail_label,
    theme,
    image,
    image_alt,
    order=None
):
    app["title"] = title.strip()
    app["description"] = description.strip()
    app["url"] = url.strip()
    app["badge"] = badge.strip()
    app["tags"] = tags
    app["thumbnail_label"] = thumbnail_label.strip()
    app["theme"] = theme
    app["image"] = image
    app["image_alt"] = image_alt.strip()

    if order is not None:
        app["order"] = order


async def save_uploaded_image(upload: UploadFile):
    if not upload.filename:
        return None

    extension = Path(upload.filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValueError(
            "Bilden måste vara PNG, JPG, JPEG, WEBP eller GIF."
        )

    if (
        upload.content_type
        and not upload.content_type.startswith("image/")
    ):
        raise ValueError(
            "Filen verkar inte vara en bild."
        )

    content = await upload.read(
        MAX_IMAGE_SIZE + 1
    )

    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError(
            "Bilden får vara maximalt 5 MB."
        )

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )

    destination = UPLOAD_DIR / filename

    destination.write_bytes(content)

    return (
        f"/static/portal/uploads/"
        f"{filename}"
    )


def delete_uploaded_image(image_url):
    if not image_url:
        return

    prefix = "/static/portal/uploads/"

    if not image_url.startswith(prefix):
        return

    filename = Path(image_url).name

    image_path = UPLOAD_DIR / filename

    if image_path.exists():
        image_path.unlink()