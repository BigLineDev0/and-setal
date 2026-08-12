from .models import Otp


def generer_et_envoyer_otp(utilisateur):
    code = Otp.generer_code()
    Otp.objects.create(utilisateur=utilisateur, code=code)

    # Simulation d'envoi SMS — à remplacer par Africa's Talking plus tard
    print(f"[OTP SIMULÉ] Code envoyé à {utilisateur.telephone} : {code}")

    return code