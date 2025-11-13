from django.urls import path
from .views import ContractUploadView, get_contract_result, list_contracts

urlpatterns = [
    path('upload/', ContractUploadView.as_view(), name='contract-upload'),
    path('<int:pk>/result/', get_contract_result, name='contract-result'),
    path('list/', list_contracts, name='contract-list'),
]
