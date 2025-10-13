from django.urls import path
from .views import ContractUploadView, get_contract_result, list_contracts

urlpatterns = [
    path('contracts/upload/', ContractUploadView.as_view(), name='contract-upload'),
    path('contracts/<int:pk>/', get_contract_result, name='contract-detail'),
    path('contracts/', list_contracts, name='contracts-list'),
]

