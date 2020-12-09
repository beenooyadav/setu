from django.urls import path
from . import views

urlpatterns = [
    path('get-all-transaction', views.get_all_transactions),
    path('get-transaction-of-contact', views.get_transaction_of_contact),
    path('add', views.add_transaction),
    path('delete', views.delete_transaction),
    path('settle', views.settle),
]
