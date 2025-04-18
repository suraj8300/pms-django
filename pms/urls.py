from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', LoginView.as_view(template_name='pms/login.html'), name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('add_drug/', views.add_drug, name='add_drug'),
    path('add_prescription/', views.add_prescription, name='add_prescription'),
    path('delete_prescription/<int:prescription_id>/', views.delete_prescription, name='delete_prescription'),
    path('delete_drug/<int:drug_id>/', views.delete_drug, name='delete_drug'),
    path('update_drug_quantity/<int:drug_id>/', views.update_drug_quantity, name='update_drug_quantity'),
]