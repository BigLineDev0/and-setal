import requests


def reverse_geocode(lat: float, lng: float) -> str:
    try:
        response = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={
                "format": "json",
                "lat": lat,
                "lon": lng,
                "zoom": 18,
                "addressdetails": 1,
            },
            headers={
                "User-Agent": "AndeSetal/1.0"
            },
            timeout=5,
        )

        response.raise_for_status()

        data = response.json()
        address = data.get("address", {})

        elements = [
            address.get("road"),
            address.get("neighbourhood"),
            address.get("suburb"),
            address.get("city_district"),
            address.get("city"),
        ]

        elements = [element for element in elements if element]

        if elements:
            return ", ".join(dict.fromkeys(elements))

        return data.get("display_name", "Adresse inconnue")

    except requests.RequestException:
        return "Adresse non disponible"