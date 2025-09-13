from django.urls import path
from .views import RenewableDocListView, RenewableDocDetailView, RenewableDocCreateView, ChangePasswordView, BudgetListView, BudgetDetailView, BudgetCreateView, FinanceListView, FinanceDetailView, FinanceCreateView, ConstitutiveDocumentListView, ConstitutiveDocumentDetailView, ConstitutiveDocumentCreateView, my_companies, upload_document

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

]
