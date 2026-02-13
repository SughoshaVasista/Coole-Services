from django.urls import path
from . import views

urlpatterns = [
    path('', views.order_list_view, name='orders'),
    path('cancel/<int:booking_id>/', views.cancel_booking_view, name='cancel_booking'),
    path('complete/<int:booking_id>/', views.complete_booking_view, name='complete_booking'),
    path('review/<int:booking_id>/', views.submit_review_view, name='submit_review'),
]

