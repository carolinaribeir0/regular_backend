from django.urls import path
from .views import RenewableDocListView, RenewableDocDetailView, ChangePasswordView, BudgetListView, BudgetDetailView, FinanceListView, FinanceDetailView, ConstitutiveDocumentListView, ConstitutiveDocumentDetailView, my_companies, upload_document, get_signed_document_url, password_reset, password_reset_confirm, support_request

urlpatterns = [
    path("api/my-companies/", my_companies, name="my-companies"),
    path("api/upload-document/", upload_document, name="upload-document"),

    path("api/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("api/renewable-docs/", RenewableDocListView.as_view(), name="renewable-docs-list"),
    path("api/renewable-docs/<int:pk>/", RenewableDocDetailView.as_view(), name="renewable-doc-detail"),

    path("api/budgets/", BudgetListView.as_view(), name="budget-list"),
    path("api/budgets/<int:pk>/", BudgetDetailView.as_view(), name="budget-detail"),

    path("api/finance/", FinanceListView.as_view(), name="finance-list"),
    path("api/finance/<int:pk>/", FinanceDetailView.as_view(), name="finance-detail"),

    path("api/constitutivedocument/", ConstitutiveDocumentListView.as_view(), name="constitutive-document-list"),
    path("api/constitutivedocument/<int:pk>/", ConstitutiveDocumentDetailView.as_view(), name="constitutive-document-detail"),
    path("api/finance/signed-url/", get_signed_document_url, name='get-signed-document-url'),
    path("api/password-reset/", password_reset, name="password-reset"),
    path("api/password-reset-confirm/<str:token>/", password_reset_confirm, name="password-reset-confirm"),
    path("api/support/", support_request, name="support_request"),

]
