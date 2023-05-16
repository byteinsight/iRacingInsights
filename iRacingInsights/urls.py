"""iRacingInsights URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import include, path

from irstats import views

urlpatterns = [
    path('', views.index, name="index"),
    path('cars/', views.cars, name='cars'),
    path('leagues/', views.leagues, name='leagues'),
    path('league/<int:league_id>/', views.league, name='league'),
    path('league/roster/<int:league_id>/', views.league_roster, name='league_roster'),
    path('league/season/<int:season_id>/', views.league_season, name='league_season'),
    path('league/session/<int:session_id>/', views.league_session, name='league_session'),
    path('member/', include('irstats.urls')),
    path('race/<int:subsession_id>/', views.race, name='race'),
    path('docs/', views.docs, name='docs'),
    path('series/', views.series, name='series'),
    path('series/<int:series_id>/', views.serie_details, name='serie_details'),
    path('tracks/', views.tracks, name='tracks'),
    path('track/<int:sku>/', views.track, name='track'),
    path('admin/', admin.site.urls),
]