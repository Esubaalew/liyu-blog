from django.contrib import sitemaps
from django.urls import reverse
from blog.models import Post, Gallery

class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'weekly'

    def items(self):
        return ['home', 'blog:post_list', 'blog:gallery_list', 'blog:archives']

    def location(self, item):
        return reverse(item)

class PostSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at

class GallerySitemap(sitemaps.Sitemap):
    priority = 0.6
    changefreq = 'weekly'

    def items(self):
        return Gallery.objects.all()

    def lastmod(self, obj):
        return obj.created_at
