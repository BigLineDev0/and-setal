from .models import Utilisateurs, Otp
from rest_framework import serializers


class UtilisateurSerializers(serializers.ModelSerializer):
    """Sérialise un profil utilisateur en lecture (ex: pour un endpoint 'mon profil')."""

    class Meta:
        model = Utilisateurs
        fields = ['first_name', 'last_name', 'telephone', 'email', 'role']
        # 'role' est exposé mais non modifiable par l'utilisateur via ce serializer
        read_only_fields = ['role']


class InscriptionSerializer(serializers.ModelSerializer):
    """Sérialise les données d'inscription et gère la création sécurisée du compte."""

    # write_only : le password est accepté en entrée mais jamais renvoyé dans une réponse JSON
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateurs
        fields = ['id', 'username', 'first_name', 'last_name', 'password', 'telephone', 'email',]

    def create(self, validated_data):
        # Retire le password en clair du dict pour ne pas le passer tel quel au modèle
        password = validated_data.pop('password')

        # Construit l'objet en mémoire (pas encore enregistré en base)
        utilisateur = Utilisateurs(**validated_data)

        # Hash le mot de passe avant sauvegarde (jamais stocké en clair)
        utilisateur.set_password(password)
        utilisateur.save()

        return utilisateur


class VerificationOTPSerializer(serializers.Serializer):
    """Valide les données envoyées pour vérifier un code OTP reçu par SMS."""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6, min_length=6)  # code toujours exactement 6 chiffres


class RenvoiOTPSerializer(serializers.Serializer):
    """Valide la demande de renvoi d'un nouveau code OTP."""
    email = serializers.EmailField()


# --- Utilisé UNIQUEMENT par un admin pour changer le rôle d'un autre utilisateur ---
class ChangerRoleSerializer(serializers.ModelSerializer):
    """
    Contrairement à UtilisateurSerializers, 'role' est ici volontairement modifiable :
    ce serializer n'est utilisé que par l'endpoint réservé aux admins (voir views.py),
    jamais par l'utilisateur pour modifier son propre profil.
    """
 
    class Meta:
        model = Utilisateurs
        fields = ['role']


class CreationAgentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Utilisateurs
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'telephone']
        # pas de password ici : il est généré côté serveur, pas fourni par l'admin