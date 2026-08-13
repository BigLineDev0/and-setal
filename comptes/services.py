from .models import Otp


def generer_et_envoyer_otp(utilisateur):
    """Génère un code OTP pour un utilisateur et simule son envoi (log console)."""

    # Génère un code aléatoire à 6 chiffres (méthode statique définie sur le modèle)
    code = Otp.generer_code()

    # Enregistre l'OTP en base, lié à l'utilisateur, avec date_creation auto et est_utilise=False par défaut
    otp = Otp.objects.create(
        utilisateur=utilisateur,
        code=code
    )

    # Simulation d'envoi SMS — à remplacer par un vrai fournisseur (SMS) en production
    print(
        f"[OTP SIMULÉ] Code envoyé à {utilisateur.email} : {code}"
    )

    return code