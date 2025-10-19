from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name='movies.index'),
    path('<int:id>/', views.show, name='movies.show'),
    path('<int:id>/review/create/', views.create_review,name='movies.create_review'),
    path('<int:id>/review/<int:review_id>/edit/', views.edit_review, name='movies.edit_review'),
    path('<int:id>/review/<int:review_id>/delete/', views.delete_review, name='movies.delete_review'),
    path('map/', views.map_view, name='movies.map'),
    path('popular/<str:region_code>/', views.popular_movies_by_region, name='movies.popular_by_region'),
    # Ratings API
    path('api/ratings/', views.api_create_or_update_rating, name='api.ratings.create_or_update'),
    path('api/movies/<int:id>/rating/', views.api_get_movie_rating, name='api.movies.rating'),
]