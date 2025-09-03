from django.urls import path
from .views import DepositView, WithdrawView, TransactionReportView, LoanRequestView, LoanListView, LoanPayView

app_name = 'transactions'
urlpatterns = [
    path("deposit/", DepositView.as_view(), name="deposit_money"),
    path("withdraw/", WithdrawView.as_view(), name="withdraw_money"),
    path("loan-request/", LoanRequestView.as_view(), name="loan_request"),
    path("report/", TransactionReportView.as_view(), name="transaction_report"),
    path("loan-list/", LoanListView.as_view(), name="loan_list"),
    path("pay-loan/<int:loan_id>/", LoanPayView.as_view(), name="pay"),
]