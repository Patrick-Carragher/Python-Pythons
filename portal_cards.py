import json
import re
import unicodedata
from pathlib import Path

from fastapi import UploadFile


BASE_DIR = Path(__file__).resolve().parent

DATA_FILE = BASE_DIR / "data" / "apps.json"

PORTAL_UPLOAD_DIR = (
    BASE_DIR
    / "static"
    / "portal"
    / "uploads"
)

GENERATED_TEMPLATE_DIR = (
    BASE_DIR
    / "templates"
    / "apps"
)

GENERATED_STATIC_DIR = (
    BASE_DIR
    / "static"
    / "apps"
)


ALLOWED_IMAGE_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".webp"
}

MAX_IMAGE_SIZE = 5 * 1024 * 1024


# --------------------------------------------------
# LOAD APPS
# --------------------------------------------------

def load_apps():

    if not DATA_FILE.exists():
        return []

    with DATA_FILE.open(
        "r",
        encoding="utf-8"
    ) as file:

        apps = json.load(file)

    return sorted(
        apps,
        key=lambda app: app.get(
            "order",
            9999
        )
    )


# --------------------------------------------------
# SAVE APPS
# --------------------------------------------------

def save_apps(apps):

    DATA_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = (
        DATA_FILE.with_suffix(
            ".tmp"
        )
    )

    temporary_file.write_text(
        json.dumps(
            apps,
            indent=4,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    temporary_file.replace(
        DATA_FILE
    )


# --------------------------------------------------
# FIND APP
# --------------------------------------------------

def find_app(
    apps,
    app_id
):

    for app in apps:

        if app.get("id") == app_id:
            return app

    return None


# --------------------------------------------------
# TAGS
# --------------------------------------------------

def parse_tags(tags):

    result = []

    for tag in tags.split(","):

        cleaned_tag = tag.strip()

        if (
            cleaned_tag
            and
            cleaned_tag not in result
        ):
            result.append(
                cleaned_tag
            )

    return result


# --------------------------------------------------
# ORDER
# --------------------------------------------------

def next_order(apps):

    if not apps:
        return 1

    return (
        max(
            app.get(
                "order",
                0
            )
            for app in apps
        )
        + 1
    )


# --------------------------------------------------
# SLUG
# --------------------------------------------------

def slugify(value):

    value = (
        unicodedata
        .normalize(
            "NFKD",
            value
        )
        .encode(
            "ascii",
            "ignore"
        )
        .decode(
            "ascii"
        )
    )

    value = value.lower()

    value = re.sub(
        r"[^a-z0-9]+",
        "-",
        value
    )

    value = value.strip("-")

    return value


def unique_slug(
    apps,
    requested_slug,
    title
):

    base_slug = slugify(
        requested_slug
        or title
    )

    if not base_slug:

        base_slug = "new-app"

    existing_ids = {
        app.get("id")
        for app in apps
    }

    slug = base_slug

    counter = 2

    while slug in existing_ids:

        slug = (
            f"{base_slug}-{counter}"
        )

        counter += 1

    return slug


# --------------------------------------------------
# CREATE APP FILES
# --------------------------------------------------

def create_app_files(app):

    slug = app["id"]

    template_folder = (
        GENERATED_TEMPLATE_DIR
        / slug
    )

    static_folder = (
        GENERATED_STATIC_DIR
        / slug
    )

    template_folder.mkdir(
        parents=True,
        exist_ok=False
    )

    static_folder.mkdir(
        parents=True,
        exist_ok=False
    )


    html_file = (
        template_folder
        / f"{slug}.html"
    )

    css_file = (
        static_folder
        / f"{slug}.css"
    )


    html_content = f"""<!DOCTYPE html>
<html lang="sv">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>{{{{ app.title }}}}</title>

    <link
        rel="stylesheet"
        href="{{{{ url_for('static', path='/apps/{slug}/{slug}.css') }}}}"
    >

</head>


<body>

<main class="app-container">

    <a
        href="/"
        class="back-link"
    >
        ← Till portalen
    </a>


    <section class="app-header">

        <span class="app-label">
            Python Testbed
        </span>

        <h1>
            {{{{ app.title }}}}
        </h1>

        <p>
            {{{{ app.description }}}}
        </p>

    </section>


    <section class="app-workspace">

        <h2>
            Testyta
        </h2>

        <p>
            Den här sidan skapades automatiskt från portalen.
        </p>

        <p>
            Lägg appens funktionalitet här.
        </p>

    </section>

</main>

</body>

</html>
"""


    css_content = """* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}


:root {
    --background: #f5f7fa;
    --surface: #ffffff;
    --text: #17202a;
    --text-muted: #667085;
    --border: #e4e7ec;
    --primary: #2563eb;
}


body {
    min-height: 100vh;

    padding: 50px 24px;

    background-color: var(--background);

    color: var(--text);

    font-family:
        Inter,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}


.app-container {
    width: 100%;
    max-width: 900px;

    margin: 0 auto;
}


.back-link {
    display: inline-block;

    margin-bottom: 40px;

    color: var(--primary);

    font-weight: 700;

    text-decoration: none;
}


.back-link:hover {
    text-decoration: underline;
}


.app-header {
    margin-bottom: 35px;
}


.app-label {
    display: block;

    margin-bottom: 10px;

    color: var(--primary);

    font-size: 12px;
    font-weight: 800;

    letter-spacing: 1.3px;

    text-transform: uppercase;
}


.app-header h1 {
    margin-bottom: 15px;

    font-size: 48px;

    letter-spacing: -1.5px;
}


.app-header p {
    max-width: 700px;

    color: var(--text-muted);

    font-size: 17px;
    line-height: 1.7;
}


.app-workspace {
    padding: 30px;

    background-color: var(--surface);

    border: 1px solid var(--border);
    border-radius: 18px;
}


.app-workspace h2 {
    margin-bottom: 15px;
}


.app-workspace p {
    margin-bottom: 10px;

    color: var(--text-muted);

    line-height: 1.6;
}


@media (max-width: 600px) {

    body {
        padding: 30px 18px;
    }


    .app-header h1 {
        font-size: 36px;
    }

}
"""


    html_file.write_text(
        html_content,
        encoding="utf-8"
    )

    css_file.write_text(
        css_content,
        encoding="utf-8"
    )


# --------------------------------------------------
# CREATE NEW GENERATED APP
# --------------------------------------------------

def create_generated_app(
    apps,
    title,
    description,
    requested_slug,
    badge,
    tags,
    thumbnail_label,
    theme,
    image,
    image_alt,
    order_value
):

    slug = unique_slug(
        apps,
        requested_slug,
        title
    )


    app = {
        "id": slug,

        "title": title.strip(),

        "description":
            description.strip(),

        "url":
            f"/apps/{slug}",

        "badge":
            badge.strip(),

        "tags":
            tags,

        "thumbnail_label":
            thumbnail_label.strip(),

        "theme":
            theme,

        "image":
            image,

        "image_alt":
            image_alt.strip(),

        "order": (
            order_value
            if order_value is not None
            else next_order(apps)
        ),

        "generated":
            True,

        "template":
            f"apps/{slug}/{slug}.html",

        "stylesheet":
            f"/static/apps/{slug}/{slug}.css"
    }


    create_app_files(
        app
    )


    apps.append(
        app
    )


    return app


# --------------------------------------------------
# UPDATE EXISTING CARD
# --------------------------------------------------

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
    order_value
):

    app["title"] = (
        title.strip()
    )

    app["description"] = (
        description.strip()
    )

    app["badge"] = (
        badge.strip()
    )

    app["tags"] = (
        tags
    )

    app["thumbnail_label"] = (
        thumbnail_label.strip()
    )

    app["theme"] = (
        theme
    )

    app["image"] = (
        image
    )

    app["image_alt"] = (
        image_alt.strip()
    )


    if order_value is not None:

        app["order"] = (
            order_value
        )


    # Generated apps keep their generated route.
    # Custom apps such as Numbers/PDF may change URL.

    if not app.get(
        "generated",
        False
    ):

        app["url"] = (
            url.strip()
        )


# --------------------------------------------------
# SAVE IMAGE
# --------------------------------------------------

async def save_image(
    image: UploadFile
):

    if not image.filename:
        return None


    extension = (
        Path(
            image.filename
        )
        .suffix
        .lower()
    )


    if (
        extension
        not in ALLOWED_IMAGE_EXTENSIONS
    ):

        raise ValueError(
            "Endast PNG, JPG, JPEG och WEBP är tillåtna."
        )


    if (
        image.content_type
        and
        not image.content_type.startswith(
            "image/"
        )
    ):

        raise ValueError(
            "Filen verkar inte vara en bild."
        )


    content = await image.read(
        MAX_IMAGE_SIZE + 1
    )


    if len(content) > MAX_IMAGE_SIZE:

        raise ValueError(
            "Bilden får vara maximalt 5 MB."
        )


    PORTAL_UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True
    )


    import uuid

    filename = (
        f"{uuid.uuid4().hex}"
        f"{extension}"
    )


    destination = (
        PORTAL_UPLOAD_DIR
        / filename
    )


    destination.write_bytes(
        content
    )


    return (
        "/static/portal/uploads/"
        f"{filename}"
    )


# --------------------------------------------------
# DELETE IMAGE
# --------------------------------------------------

def delete_image(
    image_url
):

    if not image_url:
        return


    prefix = (
        "/static/portal/uploads/"
    )


    if not image_url.startswith(
        prefix
    ):
        return


    filename = (
        Path(
            image_url
        ).name
    )


    image_path = (
        PORTAL_UPLOAD_DIR
        / filename
    )


    if image_path.exists():

        image_path.unlink()