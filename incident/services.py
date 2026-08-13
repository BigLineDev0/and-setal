import requests
from .models import AnalyseIA


def appeler_service_ia(url_image, timeout=5):
    # Mock temporaire — à remplacer par l'appel réel au service FastAPI
    return {
        "type_incident": "depot_sauvage",
        "score_confiance": 0.85,
        "niveau_urgence": "eleve"
    }


def calculer_priorite(type_incident, confiance, niveau_urgence):
    if niveau_urgence == "eleve" and confiance >= 0.7:
        return "haute"
    elif niveau_urgence == "eleve":
        return "moyenne"
    elif confiance < 0.5:
        return "a_verifier"
    return "basse"


def declencher_analyse_ia(incident):
    try:
        resultat = appeler_service_ia(incident.urlImage, timeout=5)

        AnalyseIA.objects.create(
            signalement=incident,
            type_incident=resultat['type_incident'],
            score_confiance=resultat['score_confiance'],
            niveau_urgence=resultat['niveau_urgence'],
        )

        incident.priorite = calculer_priorite(
            resultat['type_incident'],
            resultat['score_confiance'],
            resultat['niveau_urgence'],
        )

    except (requests.exceptions.Timeout, requests.exceptions.RequestException):
        pass

    incident.save()