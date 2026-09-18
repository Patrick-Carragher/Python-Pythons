import re
import secrets
import string


APPLICATION_ID_ALPHABET = (
    string.ascii_uppercase
    + string.digits
)


APPLICATION_ID_PATTERN = re.compile(
    r"^PA\d{2}-[A-Z0-9]{8}$"
)


def generate_application_id(
    year: int,
    existing_ids: set[str] | None = None,
) -> str:

    existing_ids = (
        existing_ids
        if existing_ids is not None
        else set()
    )

    prefix = (
        f"PA{year % 100:02d}-"
    )

    while True:

        random_part = "".join(
            secrets.choice(
                APPLICATION_ID_ALPHABET
            )
            for _ in range(8)
        )

        application_id = (
            f"{prefix}{random_part}"
        )

        if application_id not in existing_ids:
            return application_id


def is_valid_application_id(
    application_id: str,
) -> bool:

    if not application_id:
        return False

    return bool(
        APPLICATION_ID_PATTERN.fullmatch(
            application_id
        )
    )