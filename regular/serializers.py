from rest_framework import serializers
from .models import RenewableDoc, Budget, Finance, ConstitutiveDocument
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if hasattr(user, "profile") and user.profile.company:
            token["company_id"] = user.profile.company.id
            token["company_name"] = user.profile.company.name

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        if hasattr(self.user, "profile") and self.user.profile.company:
            data["company_id"] = self.user.profile.company.id
            data["company_name"] = self.user.profile.company.name

        data["is_superuser"] = self.user.is_superuser
        return data


class RenewableDocSerializer(serializers.ModelSerializer):
    class Meta:
        model = RenewableDoc
        fields = ['id', 'doc_name', 'description', 'os_number', 'renewed_at', 'expiration_date', 'doc_url']

class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = ['id','service_name', 'amount', 'scheduled_date', 'os_number', 'service_provider', 'doc_url']

class FinanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Finance
        fields = ['id','description','due_date', 'amount', 'invoice', 'contract', 'is_paid']

class ConstitutiveDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConstitutiveDocument
        fields = ['id','doc_name', 'doc_url']
