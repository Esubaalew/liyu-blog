from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache
from .models import Post, Comment, Gallery, MediaItem

@receiver(post_save, sender=Post)
def clear_post_cache(sender, instance, **kwargs):
    """Clear cache when a post is saved or updated."""
    # Clear specific post cache
    cache.delete(f'post_{instance.slug}')
    # Clear post list cache
    cache.delete('post_list')
    # Clear author posts cache
    cache.delete(f'author_posts_{instance.author.username}')
    # Clear tag related caches if tags exist
    if instance.tags.exists():
        for tag in instance.tags.all():
            cache.delete(f'tag_posts_{tag.slug}')

@receiver(post_save, sender=Comment)
def clear_comment_cache(sender, instance, **kwargs):
    """Clear cache when a comment is saved or updated."""
    # Clear post comments cache
    cache.delete(f'post_comments_{instance.post.slug}')

@receiver(post_save, sender=Gallery)
def clear_gallery_cache(sender, instance, **kwargs):
    """Clear cache when a gallery is saved or updated."""
    # Clear gallery list cache
    cache.delete('gallery_list')
    # Clear specific gallery cache
    cache.delete(f'gallery_{instance.id}')

@receiver(post_save, sender=MediaItem)
def clear_media_cache(sender, instance, **kwargs):
    """Clear cache when a media item is saved or updated."""
    # Clear gallery cache
    cache.delete(f'gallery_{instance.gallery.id}')
    # Clear gallery items cache
    cache.delete(f'gallery_items_{instance.gallery.id}')
