from datetime import date

from pydantic import BaseModel


class Application(BaseModel):
    ankom: date
    namn: str
    personnummer: str
    ny_eller_omcertifiering: str
    norm: str
    foretag: str
    adress: str
    mail: str
    mail_privat: str = ""
    telefon: str = ""
    examinationsdatum: date | None = None
    utb_hos_sakerhetsbransch: str = ""
    plats: str = ""
    ovrigt: str = ""
    resultat: str = ""
    status: str = ""
    application_id: str = ""