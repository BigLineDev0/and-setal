from .models import Utilisateurs, Otp
from rest_framework import serializers


class UtilisateurSerializers(serializers.ModelSerializer):
    class Meta:
        model = Utilisateurs
        fields = ['first_name', 'last_name', 'password', 'telephone']
        read_only_fields = ['role']


class InscriptionSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Utilisateurs
        fields = ['username', 'first_name', 'last_name', 'password', 'telephone']

    def create(self, validated_data):
        password = validated_data.pop('password')

        utilisateur = Utilisateurs(**validated_data)
        utilisateur.set_password(password)
        utilisateur.save()

        return utilisateur


class VerificationOTPSerializer(serializers.Serializer):
    telephone = serializers.CharField()
    code = serializers.CharField(max_length=6, min_length=6)

    class Meta:
        fields = ["telephone","code"]

