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
    """Sérialise les données d'inscription par Email et gère la création sécurisée du compte."""

    password = serializers.CharField(write_only=True, required=True)
    # On force l'email à être obligatoire lors du formulaire d'inscription
    email = serializers.EmailField(required=True)

    class Meta:
        '''Sérialise les données d'inscription et gère la création sécurisée du compte.'''

        model = Utilisateurs
        fields = ['id', 'first_name', 'last_name', 'password', 'telephone', 'email']

    def validate_email(self, value):
        """Vérifie si l'adresse email n'est pas déjà prise."""
        if Utilisateurs.objects.filter(email=value).exists():
            raise serializers.ValidationError("Cette adresse email est déjà utilisée par un autre compte.")
        return value

    def create(self, validated_data):
        # Retire le password en clair du dict pour ne pas le passer tel quel au modèle
        password = validated_data.pop('password')

        # Construit l'objet en mémoire
        utilisateur = Utilisateurs(**validated_data)

        # Django requiert un username unique en interne, on lui synchronise l'email
        utilisateur.username = validated_data['email']

        # Hachage sécurisé du mot de passe
        utilisateur.set_password(password)
        
        # Par sécurité, on force le rôle par défaut ici s'il n'est pas fourni
        if not hasattr(utilisateur, 'role') or not utilisateur.role:
            utilisateur.role = 'citoyen'

        utilisateur.save()
        return utilisateur


class VerificationOTPSerializer(serializers.Serializer):
    """Valide les données envoyées pour vérifier un code OTP reçu par SMS."""
    email = serializers.EmailField()
    code = serializers.CharField(max_length=4, min_length=4)  # code toujours exactement 5 chiffres


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
      # 'username' sera généré à partir de l'email
        fields = ['id', 'first_name', 'last_name', 'email', 'telephone']

    def create(self, validated_data):
        """Gère la création automatique du username pour l'agent créé par l'admin."""
        agent = Utilisateurs(**validated_data)
        agent.username = validated_data['email']
        agent.role = 'agent'
        # Attribution d'un mot de passe aléatoire ou temporaire (à définir dans vos vues si besoin)
        agent.set_unusable_password() 
        agent.save()
        return agent


# ---------- Gestion du profil ----------

class MonProfilSerializer(serializers.ModelSerializer):
    """
    Même liste de champs que UtilisateursSerilizers, mais utilisé spécifiquement
    pour /me/ : on ne passe jamais l'id d'un autre utilisateur, on modifie
    toujours request.user.
    """
    class Meta:
        model = Utilisateurs
        # Modification : 'username' est passé en read_only car il ne doit pas être modifié directement
        fields = ['username', 'first_name', 'last_name', 'email', 'role', 'telephone']
        read_only_fields = ["role", "username", "email"]
