from django.db.models import Count
from .models import Post, Gallery, MediaItem
from taggit.models import Tag

def site_settings(request):
    """Context processor to add site-wide settings to all templates."""
    # Get popular tags
    popular_tags = Tag.objects.annotate(
        num_posts=Count('taggit_taggeditem_items')
    ).order_by('-num_posts')[:10]
    
    # Get recent posts
    recent_posts = Post.objects.filter(
        status='published'
    ).order_by('-published_at')[:5]
    
    # Get featured posts for home page
    featured_posts = Post.objects.filter(
        status='published'
    ).order_by('-views')[:4]
    
    # Get gallery items for home page
    gallery_items = MediaItem.objects.filter(
        media_type='image'
    ).order_by('-created_at')[:6]
    
    return {
        'site_title': 'Liyu Blog',
        'site_description': 'A blog by Esubalew Chekol, a passionate Fullstack Developer',
        'site_author': 'Esubalew Chekol',
        'popular_tags': popular_tags,
        'recent_posts': recent_posts,
        'featured_posts': featured_posts,
        'gallery_items': gallery_items,
    }
