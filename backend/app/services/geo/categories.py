CATEGORIES: dict[str, dict] = {
    "gym": {"label": "Gimnasios", "tags": [("leisure", "fitness_centre"), ("leisure", "sports_centre")]},
    "restaurant": {"label": "Restaurantes", "tags": [("amenity", "restaurant")]},
    "cafe": {"label": "Cafeterías", "tags": [("amenity", "cafe")]},
    "dentist": {"label": "Dentistas", "tags": [("amenity", "dentist"), ("healthcare", "dentist")]},
    "clinic": {"label": "Clínicas", "tags": [("amenity", "clinic"), ("healthcare", "clinic")]},
    "lawyer": {"label": "Abogados", "tags": [("office", "lawyer")]},
    "hotel": {"label": "Hoteles", "tags": [("tourism", "hotel")]},
    "beauty": {"label": "Estética y belleza", "tags": [("shop", "beauty"), ("shop", "hairdresser")]},
    "car_repair": {"label": "Talleres mecánicos", "tags": [("shop", "car_repair")]},
    "retail": {"label": "Comercio minorista", "tags": [("shop", "convenience"), ("shop", "supermarket")]},
    "estate_agent": {"label": "Inmobiliarias", "tags": [("office", "estate_agent")]},
}


def list_categories() -> list[dict]:
    return [{"key": key, "label": cat["label"]} for key, cat in CATEGORIES.items()]


def get_tags(key: str) -> list[tuple[str, str]] | None:
    cat = CATEGORIES.get(key)
    return cat["tags"] if cat else None
