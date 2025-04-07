from django import template
from django.utils.safestring import mark_safe
import re
import json
from datetime import datetime

register = template.Library()

@register.filter
def timeago(value):
    """Convert a datetime to a relative time string, e.g. '3 days ago'."""
    now = datetime.now()
    diff = now - value
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return 'just now'
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f'{minutes} minute{"s" if minutes > 1 else ""} ago'
    elif seconds < 86400:
        hours = int(seconds // 3600)
        return f'{hours} hour{"s" if hours > 1 else ""} ago'
    elif seconds < 604800:
        days = int(seconds // 86400)
        return f'{days} day{"s" if days > 1 else ""} ago'
    elif seconds < 2592000:
        weeks = int(seconds // 604800)
        return f'{weeks} week{"s" if weeks > 1 else ""} ago'
    elif seconds < 31536000:
        months = int(seconds // 2592000)
        return f'{months} month{"s" if months > 1 else ""} ago'
    else:
        years = int(seconds // 31536000)
        return f'{years} year{"s" if years > 1 else ""} ago'

@register.filter
def reading_time(text):
    """Estimate reading time for text content."""
    words_per_minute = 200
    word_count = len(re.findall(r'\w+', text))
    minutes = max(1, int(word_count / words_per_minute))
    return f'{minutes} min read'

@register.filter(is_safe=True)
def schema_org_post(post):
    """Generate schema.org JSON-LD for a blog post."""
    data = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.title,
        "datePublished": post.published_at.isoformat() if post.published_at else post.created_at.isoformat(),
        "dateModified": post.updated_at.isoformat(),
        "author": {
            "@type": "Person",
            "name": post.author.get_full_name() or post.author.username
        },
        "mainEntityOfPage": {
            "@type": "WebPage",
            "@id": post.get_absolute_url()
        }
    }
    
    if post.featured_image:
        data["image"] = post.featured_image.url
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data)}</script>')

@register.filter(is_safe=True)
def schema_org_breadcrumbs(items):
    """Generate schema.org JSON-LD for breadcrumbs."""
    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": []
    }
    
    for i, item in enumerate(items, start=1):
        data["itemListElement"].append({
            "@type": "ListItem",
            "position": i,
            "name": item["name"],
            "item": item["url"]
        })
    
    return mark_safe(f'<script type="application/ld+json">{json.dumps(data)}</script>')

@register.filter
def truncate_chars(value, max_length):
    """Truncate a string to a certain number of characters."""
    if len(value) > max_length:
        return value[:max_length] + '...'
    return value
