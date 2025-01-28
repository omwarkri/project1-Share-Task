from django.urls import path
from . import views

urlpatterns = [
    path('subscribe/', views.create_subscription, name='create_subscription'),
    path('paypal/return/', views.paypal_return, name='paypal_return'),
    path('paypal/cancel/', views.paypal_cancel, name='paypal_cancel'),
]
