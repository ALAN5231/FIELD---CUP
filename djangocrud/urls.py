"""
URL configuration for djangocrud project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('admin/', admin.site.urls),
    path('', views.home, name ='home'),
    path('signup/', views.signup, name ='signup'), 
    path('logout/', views.signout, name ='logout'), 
    path('signin/', views.signin, name ='signin'), 
    path('lobby/', views.lobby, name ='lobby'),
    path('teams/create/', views.create_team, name='create_team'),
    path('teams/<int:team_id>/', views.team_detail, name='team_detail'),
    path('teams/<int:team_id>/edit/', views.edit_team, name='edit_team'),
    path('teams/<int:team_id>/delete/', views.delete_team, name='delete_team'),
    path('teams/<int:team_id>/add-member/', views.add_team_member, name='add_team_member'),
    path('teams/<int:team_id>/remove-member/<int:user_id>/', views.remove_team_member, name='remove_team_member'),
    path('profile/', views.profile, name='profile'),
    path('tournaments/create/', views.create_tournament, name='create_tournament'),
    path('tournaments/<int:tournament_id>/', views.tournament_detail, name='tournament_detail'),
    path('tournaments/<int:tournament_id>/edit/', views.edit_tournament, name='edit_tournament'),
    path('tournaments/<int:tournament_id>/delete/', views.delete_tournament, name='delete_tournament'),
    path('tournaments/<int:tournament_id>/add-team/', views.add_team_to_tournament, name='add_team_to_tournament'),
    path('tournaments/<int:tournament_id>/remove-team/<int:team_id>/', views.remove_team_from_tournament, name='remove_team_from_tournament'),
    path('tournaments/<int:tournament_id>/add-referee/', views.add_referee, name='add_referee'),
    path('tournaments/<int:tournament_id>/remove-referee/<int:user_id>/',views.remove_referee,name='remove_referee'),
    path('tournament/<int:tournament_id>/generate-matches/',views.generate_matches, name='generate_matches'),
    path('matches/<int:match_id>/record/', views.record_match_result, name='record_match_result'),
    path('matches/<int:match_id>/edit/', views.edit_match_info,name='edit_match_info'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)