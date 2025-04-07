from django import template

register = template.Library()

@register.simple_tag
def get_pagination_url(request, page):
    """Generate pagination URL preserving all query parameters."""
    query_dict = request.GET.copy()
    query_dict['page'] = page
    return f"?{query_dict.urlencode()}"

@register.inclusion_tag('blog/includes/pagination.html')
def render_pagination(page_obj, request=None):
    """Render pagination with proper context."""
    return {
        'page_obj': page_obj,
        'request': request,
    }

@register.inclusion_tag('blog/includes/post_card.html')
def render_post_card(post, size='medium'):
    """Render a post card with specified size."""
    return {
        'post': post,
        'size': size,
    }

@register.inclusion_tag('blog/includes/comment_form.html')
def render_comment_form(post, parent=None):
    """Render a comment form for a post or as a reply to another comment."""
    return {
        'post': post,
        'parent': parent,
    }

@register.inclusion_tag('blog/includes/tag_cloud.html')
def render_tag_cloud(tags):
    """Render a tag cloud with the provided tags."""
    return {
        'tags': tags,
    }

@register.filter
def get_item_type_icon(media_type):
    """Return the appropriate icon class for a media type."""
    icons = {
        'image': 'fa-image',
        'video': 'fa-video',
        'audio': 'fa-music',
    }
    return icons.get(media_type, 'fa-file')
