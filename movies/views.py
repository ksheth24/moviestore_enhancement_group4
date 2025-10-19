from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Rating
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count, Sum
from cart.models import Order, Item
import json

# Create your views here.
def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        # Show all movies (including those without images)
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html',
                  {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie)
    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html',
                  {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment']!= '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id,
        user=request.user)
    review.delete()
    return redirect('movies.show', id=id)


# --- Ratings API ---
@csrf_exempt
@login_required
@require_http_methods(["POST"]) 
def api_create_or_update_rating(request):
    try:
        payload = json.loads(request.body.decode('utf-8')) if request.body else request.POST
        movie_id = int(payload.get('movie_id'))
        stars = int(payload.get('stars'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON or missing fields')

    if stars < 1 or stars > 5:
        return HttpResponseBadRequest('Stars must be between 1 and 5')

    movie = get_object_or_404(Movie, id=movie_id)

    rating, created = Rating.objects.update_or_create(
        user=request.user,
        movie=movie,
        defaults={'stars': stars}
    )

    
    agg = Rating.objects.filter(movie=movie).aggregate(avg=Avg('stars'), count=Count('id'))
    return JsonResponse({
        'status': 'created' if created else 'updated',
        'movie_id': movie.id,
        'user_rating': rating.stars,
        'average_rating': round(agg['avg'] or 0, 2),
        'total_ratings': agg['count']
    })


@require_http_methods(["GET"]) 
def api_get_movie_rating(request, id):
    movie = get_object_or_404(Movie, id=id)
    agg = Rating.objects.filter(movie=movie).aggregate(avg=Avg('stars'), count=Count('id'))
    user_rating = None
    if request.user.is_authenticated:
        existing = Rating.objects.filter(user=request.user, movie=movie).first()
        user_rating = existing.stars if existing else None
    return JsonResponse({
        'movie_id': movie.id,
        'average_rating': round(agg['avg'] or 0, 2),
        'total_ratings': agg['count'],
        'user_rating': user_rating
    })


# --- Local Popularity / Trending APIs ---
@require_http_methods(["GET"])
def api_regions_overview(request):
    # List regions with total items purchased and number of orders
    qs = Order.objects.values('region_code').annotate(
        order_count=Count('id'),
        total_quantity=Sum('item__quantity'),
    ).order_by('-total_quantity')

    regions = []
    for row in qs:
        regions.append({
            'region_code': row['region_code'] or 'UNKNOWN',
            'order_count': row['order_count'] or 0,
            'total_items': row['total_quantity'] or 0,
        })

    return JsonResponse({'regions': regions})


@require_http_methods(["GET"])
def api_trending_by_region(request):
    region_code = request.GET.get('region_code')
    limit = int(request.GET.get('limit', '10'))
    if not region_code:
        return HttpResponseBadRequest('region_code is required')

    # Aggregate items sold per movie within region
    qs = Item.objects.filter(order__region_code=region_code).values('movie_id', 'movie__name').annotate(
        total_quantity=Sum('quantity'),
        order_count=Count('order_id', distinct=True)
    ).order_by('-total_quantity')[:limit]

    trending = []
    for row in qs:
        trending.append({
            'movie_id': row['movie_id'],
            'movie_name': row['movie__name'],
            'total_items_sold': row['total_quantity'] or 0,
            'orders_count': row['order_count'] or 0,
        })

    return JsonResponse({'region_code': region_code, 'trending': trending})


@login_required
@require_http_methods(["GET"])
def api_user_purchases(request):
    # Useful for verifying against region trending
    region_code = request.GET.get('region_code')
    items = Item.objects.filter(order__user=request.user)
    if region_code:
        items = items.filter(order__region_code=region_code)
    agg = items.values('movie_id', 'movie__name').annotate(total_quantity=Sum('quantity')).order_by('-total_quantity')
    purchases = []
    for row in agg:
        purchases.append({
            'movie_id': row['movie_id'],
            'movie_name': row['movie__name'],
            'total_items': row['total_quantity'] or 0,
        })
    return JsonResponse({'region_code': region_code, 'purchases': purchases})


# --- Map View ---
def map_view(request):
    """Display the geographic movie popularity map"""
    template_data = {
        'title': 'Movie Popularity Map'
    }
    return render(request, 'movies/map.html', {'template_data': template_data})


# --- Popular Movies by Region View ---
def popular_movies_by_region(request, region_code):
    """Display popular movies for a specific region"""
    from django.db.models import Sum, Count
    
    # Get region name
    region_names = {
        'US': 'United States', 'CA': 'Canada', 'GB': 'United Kingdom',
        'DE': 'Germany', 'FR': 'France', 'JP': 'Japan', 'AU': 'Australia',
        'BR': 'Brazil', 'IN': 'India', 'CN': 'China', 'RU': 'Russia',
        'MX': 'Mexico', 'IT': 'Italy', 'ES': 'Spain', 'KR': 'South Korea',
        'UNKNOWN': 'Unknown Region'
    }
    
    region_name = region_names.get(region_code, region_code)
    
    # Get trending movies for the region
    trending_movies = Item.objects.filter(order__region_code=region_code).values(
        'movie_id', 'movie__name', 'movie__price', 'movie__description', 'movie__image'
    ).annotate(
        total_quantity=Sum('quantity'),
        order_count=Count('order_id', distinct=True)
    ).order_by('-total_quantity')[:20]
    
    # Get region statistics
    region_stats = Order.objects.filter(region_code=region_code).aggregate(
        total_orders=Count('id'),
        total_items=Sum('item__quantity')
    )
    
    template_data = {
        'title': f'Popular Movies in {region_name}',
        'region_code': region_code,
        'region_name': region_name,
        'trending_movies': trending_movies,
        'region_stats': region_stats
    }
    
    return render(request, 'movies/popular_movies.html', {'template_data': template_data})