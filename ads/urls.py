from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_ad, name='create_ad'),
    path('list/', views.ad_list, name='ad_list'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='ads/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('my-ads/', views.user_ads, name='user_ads'),
    path('proposal/<int:ad_id>/', views.create_proposal, name='create_proposal'),
    path('proposals/', views.proposal_list, name='proposal_list'),
    path('proposals/<int:pk>/accept/', views.accept_proposal, name='accept_proposal'),
    path('proposals/<int:pk>/reject/', views.reject_proposal, name='reject_proposal'),
    path('ads/<int:pk>/', views.ad_detail, name='ad_detail'),
    path('notifications/', views.notifications, name='notifications'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)