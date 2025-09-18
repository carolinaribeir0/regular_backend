from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from .models import RenewableDoc, Budget, Finance, ConstitutiveDocument, Company, UserProfile
from .serializers import RenewableDocSerializer, BudgetSerializer, FinanceSerializer, ConstitutiveDocumentSerializer
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
import os
import datetime
from supabase import create_client
from urllib.parse import unquote
from rest_framework.exceptions import ValidationError


SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_document(request):
    try:
        table = request.data.get("table")
        company_id = request.data.get("company_id")
        file = request.FILES.get("file")

        # ✅ agora só exige 'file' quando não for finance
        if not table or not company_id:
            return Response({"error": "Parâmetros obrigatórios ausentes"}, status=400)
        if table != "finance" and not file:
            return Response({"error": "Arquivo obrigatório ausente"}, status=400)

        # gera caminho do arquivo no bucket (apenas para tabelas que usam 'file')
        public_url = None
        if table != "finance":
            file_path = f"{company_id}/{int(datetime.datetime.now().timestamp())}-{file.name}"
            try:
                supabase.storage.from_("docs").upload(
                    file_path, file.read(), {"content-type": "application/pdf"}
                )
            except Exception as e:
                return Response({"error": f"Falha no upload: {str(e)}"}, status=400)

            # get_public_url retorna string, não dict
            public_url = supabase.storage.from_("docs").get_public_url(file_path)

            if not public_url:
                return Response({"error": "Não foi possível gerar a URL pública"}, status=400)

        # grava os dados na tabela correspondente
        if table == "renewable-docs":
            RenewableDoc.objects.create(
                company_id=company_id,
                doc_name=request.data.get("doc_name", ""),
                description=request.data.get("description", ""),
                os_number=request.data.get("os_number", ""),
                renewed_at=request.data.get("renewed_at"),
                expiration_date=request.data.get("expiration_date"),
                doc_url=public_url,
            )

        elif table == "budgets":
            Budget.objects.create(
                company_id=company_id,
                os_number=request.data.get("os_number", ""),
                service_name=request.data.get("service_name", ""),
                amount=request.data.get("amount") or 0,
                scheduled_date=request.data.get("scheduled_date"),
                service_provider=request.data.get("service_provider", ""),
                doc_url=public_url,
            )

        elif table == "finance":

            invoice_file = request.FILES.get("invoice")

            contract_file = request.FILES.get("contract")

            # ✅ Vamos salvar os caminhos, não as URLs

            invoice_path_to_save = None

            contract_path_to_save = None

            if invoice_file:
                invoice_path = f"{company_id}/{int(datetime.datetime.now().timestamp())}-invoice-{invoice_file.name}"

                supabase.storage.from_("docs").upload(invoice_path, invoice_file.read(), {"content-type": "application/pdf"})

                invoice_path_to_save = invoice_path  # ✅ Salva o caminho

            if contract_file:
                contract_path = f"{company_id}/{int(datetime.datetime.now().timestamp())}-contract-{contract_file.name}"

                supabase.storage.from_("docs").upload(contract_path, contract_file.read(), {"content-type": "application/pdf"})

                contract_path_to_save = contract_path  # ✅ Salva o caminho

            Finance.objects.create(

                company_id=company_id,

                description=request.data.get("description"),

                due_date=request.data.get("due_date"),

                amount=request.data.get("amount") or 0,

                # ✅ Alterado para salvar os caminhos

                invoice=invoice_path_to_save,

                contract=contract_path_to_save,

            )

        elif table == "constitutive-documents":
            ConstitutiveDocument.objects.create(
                company_id=company_id,
                doc_name=request.data.get("doc_name", ""),
                doc_url=public_url,
            )

        else:
            return Response({"error": "Tabela inválida"}, status=400)

        return Response({"message": "Documento enviado com sucesso"}, status=201)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_companies(request):
    user = request.user

    if not user.is_superuser:
        return Response({"error": "Apenas superusuários têm acesso"}, status=403)

    try:
        companies = user.profile.companies.all()
    except UserProfile.DoesNotExist:
        companies = []

    data = [{"id": c.id, "name": c.name, "cnpj": c.cnpj} for c in companies]
    return Response(data)

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        if not user.check_password(old_password):
            return Response({"error": "Senha atual incorreta."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({"success": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
def superuser_only(request):
    if not request.user.is_superuser:
        raise PermissionDenied("Apenas superusuários podem criar registros.")

class RenewableDocListView(generics.ListAPIView):
    serializer_class = RenewableDocSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return RenewableDoc.objects.all().order_by('expiration_date')

        company_id = user.userprofile.company.id

        return RenewableDoc.objects.filter(company_id=company_id).order_by('expiration_date')


class RenewableDocDetailView(generics.RetrieveAPIView):
    serializer_class = RenewableDocSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return RenewableDoc.objects.all()

        company_id = user.userprofile.company.id
        return RenewableDoc.objects.filter(company_id=company_id)

class RenewableDocCreateView(generics.CreateAPIView):
    serializer_class = RenewableDocSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        superuser_only(self.request)
        serializer.save()

class BudgetListView(generics.ListAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Budget.objects.all().order_by('scheduled_date')

        company_id = user.userprofile.company.id

        return Budget.objects.filter(company_id=company_id).order_by('scheduled_date')


class BudgetDetailView(generics.RetrieveAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Budget.objects.all()

        company_id = user.userprofile.company.id
        return Budget.objects.filter(company_id=company_id)

class BudgetCreateView(generics.CreateAPIView):
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        superuser_only(self.request)
        serializer.save()

class FinanceListView(generics.ListAPIView):
    serializer_class = FinanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Finance.objects.all().order_by('due_date')

        company_id = user.userprofile.company.id

        return Finance.objects.filter(company_id=company_id).order_by('due_date')


class FinanceDetailView(generics.RetrieveAPIView):
    serializer_class = FinanceSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return Finance.objects.all()

        company_id = user.userprofile.company.id
        return Finance.objects.filter(company_id=company_id)

class FinanceCreateView(generics.CreateAPIView):
    serializer_class = FinanceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        superuser_only(self.request)
        serializer.save()

class ConstitutiveDocumentListView(generics.ListAPIView):
    serializer_class = ConstitutiveDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return ConstitutiveDocument.objects.all()

        company_id = user.userprofile.company.id

        return ConstitutiveDocument.objects.filter(company_id=company_id)


class ConstitutiveDocumentDetailView(generics.RetrieveAPIView):
    serializer_class = ConstitutiveDocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return ConstitutiveDocument.objects.all()

        company_id = user.userprofile.company.id
        return ConstitutiveDocument.objects.filter(company_id=company_id)

class ConstitutiveDocumentCreateView(generics.CreateAPIView):
    serializer_class = ConstitutiveDocumentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        superuser_only(self.request)
        serializer.save()


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_signed_document_url(request):
    """
    Gera uma URL assinada e temporária para um documento no Supabase Storage.
    Espera um parâmetro de query 'filePath'.
    """
    file_path = request.query_params.get("filePath")

    if not file_path:
        return Response(
            {"error": "O parâmetro 'filePath' é obrigatório."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:

        signed_url_data = supabase.storage.from_("docs").create_signed_url(
            path=unquote(file_path), # Usa unquote para decodificar o path
            expires_in=60
        )

        if not signed_url_data or 'signedURL' not in signed_url_data:
             raise Exception("A API do Supabase não retornou uma URL assinada.")

        return Response(
            {"signedUrl": signed_url_data['signedURL']},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        print(f"Erro ao gerar URL assinada para o caminho {file_path}: {str(e)}")
        return Response(
            {"error": "Não foi possível gerar a URL do documento."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
