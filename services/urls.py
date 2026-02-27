from django.urls import path
from . import views

urlpatterns = [
    path('', views.services_view, name='services'),
    path('category/<int:category_id>/', views.category_detail_view, name='category_detail'),
    path('provider/<int:provider_id>/', views.provider_detail_view, name='provider_detail'),
    path('provider/<int:provider_id>/book/', views.book_provider_view, name='book_provider'),
    path('dashboard/', views.partner_dashboard_view, name='partner_dashboard'),
    
    # API Endpoints for Postman
    path('api/categories/', views.get_services_json, name='api_categories'),
    path('api/providers/', views.get_providers_json, name='api_providers'),
    
    # Payment URLs
    path('payment/initiate/<int:booking_id>/', views.initiate_payment, name='initiate_payment'),
    path('payment/upi/<int:booking_id>/', views.pay_via_upi, name='pay_via_upi'),
    path('payment-callback/', views.payment_callback, name='payment_callback'),
    path('webhook/razorpay/', views.razorpay_webhook, name='razorpay_webhook'),
    path('receipt/<int:booking_id>/', views.view_receipt, name='view_receipt'),
    path('rebook/<int:booking_id>/', views.rebook_view, name='rebook'),
]

