import requests
from .models import AnalyseIA

# URL du microservice FastAPI d'analyse d'images
FASTAPI_URL = "http://localhost:8001/api/ia/analyse"


def appeler_service_ia(incident, timeout=5):
    # Ouvre le fichier image stocké par Django en mode lecture binaire ('rb')
    with incident.urlImage.open('rb') as fichier_image:
        # Prépare le fichier au format attendu par FastAPI : champ 'image', nom, contenu, type MIME
        fichiers = {'image': (incident.urlImage.name, fichier_image, 'image/jpeg')}
        
        # Envoie la requête POST avec le fichier en multipart/form-data
        reponse = requests.post(FASTAPI_URL, files=fichiers, timeout=timeout)
        
        # Lève une exception si le code HTTP n'est pas 200 (ex: 400, 413, 500 gérés côté FastAPI)
        reponse.raise_for_status()
        
        # Convertit la réponse JSON en dictionnaire Python
        return reponse.json()


def calculer_priorite(type_incident, confiance, niveau_urgence):
    if niveau_urgence == "eleve":
        return "haute"
    elif niveau_urgence == "moyen":
        return "moyenne"
    elif niveau_urgence == "faible":
        return "faible"
    return "basse"


def declencher_analyse_ia(incident):
    try:
        # ⚠️ Changement : on passe maintenant 'incident' entier, plus 'incident.urlImage'
        resultat = appeler_service_ia(incident, timeout=5)

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

    # Ajout de HTTPError pour capter les erreurs renvoyées explicitement par FastAPI (400, 413, 500)
    except (requests.exceptions.Timeout, requests.exceptions.RequestException, requests.exceptions.HTTPError):
        pass

    incident.save()