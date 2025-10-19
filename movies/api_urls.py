from django.urls import path
from . import views

urlpatterns = [
    path('ratings/', views.api_create_or_update_rating, name='api.ratings.create_or_update'),
    path('movies/<int:id>/rating/', views.api_get_movie_rating, name='api.movies.rating'),
    # Local Popularity Map endpoints
    path('regions/', views.api_regions_overview, name='api.regions.overview'),
    path('trending/', views.api_trending_by_region, name='api.trending.by_region'),
    path('me/purchases/', views.api_user_purchases, name='api.user.purchases'),
]


