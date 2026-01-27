from django.urls import path
from .views import add_transaction, switch_money

urlpatterns = [
    path("add/", add_transaction, name="add_transaction"),
    path("switch/", switch_money, name="switch_money"),
]
