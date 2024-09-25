from pydantic import BaseModel
from typing import Optional
from pydantic import ValidationError


class Meteo(BaseModel):
    id_jour: str  # Date au format YYYY-MM-DD
    temperature: float


class RepasVendus(BaseModel):
    id_jour: str  # Date au format YYYY-MM-DD
    nb_couvert: int


class PresenceRH(BaseModel):
    id_agent_anonymise: int
    date_demi_j: str  # Date et heure au format 'YYYY-MM-DD HH:MM:SS'
    id_motif: int
    lib_motif: str
    type_presence: str
    origine: Optional[str] = None
    date_traitement: Optional[str] = None


# Exemple de validation d'un objet Meteo
try:
    meteo_data = Meteo.parse_obj({"id_jour": "2023-09-01", "temperature": 25.6})
    print(meteo_data)
except ValidationError as e:
    print(e)
