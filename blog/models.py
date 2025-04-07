from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from taggit.managers import TaggableManager
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import uuid
import os

def get_file_path(instance, filename):
    """Generate a unique file path for uploaded files."""
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('uploads', filename)

class Post(models.Model):
    """Blog post model with markdown support and custom URL slugs."""
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts')
    content = MarkdownxField()
    featured_image = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    tags = TaggableManager()
    views = models.PositiveIntegerField(default=0)
    
    # Version control for posts
    version = models.PositiveIntegerField(default=1)
    previous_version = models.ForeignKey('self', on_delete=models.SET_NULL, 
                                         null=True, blank=True, related_name='next_version')
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            # Generate a unique slug
            base_slug = slugify(self.title)
            unique_id = str(uuid.uuid4())[:8]
            self.slug = f"{base_slug}-{unique_id}"
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', args=[self.slug])
    
    def formatted_markdown(self):
        """Convert markdown content to HTML."""
        return markdownify(self.content)
    
    def increase_views(self):
        """Increase view count for this post."""
        self.views += 1
        self.save(update_fields=['views'])
    
    def create_new_version(self):
        """Create a new version of this post."""
        old_version = Post.objects.get(pk=self.pk)
        self.pk = None  # Create a new instance
        self.version = old_version.version + 1
        self.previous_version = old_version
        self.save()
        
        # Copy tags from previous version
        for tag in old_version.tags.all():
            self.tags.add(tag)
        
        return self

class Comment(models.Model):
    """Comment model with nested replies and reactions."""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, 
                              null=True, blank=True, related_name='replies')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.post.title}"
    
    def get_replies(self):
        """Get all replies to this comment."""
        return Comment.objects.filter(parent=self)

class CommentReaction(models.Model):
    """Reactions to comments (like, love, etc.)."""
    REACTION_CHOICES = (
        ('like', '❤️'),
        ('fire', '🔥'),
        ('idea', '💡'),
    )
    
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('comment', 'user', 'reaction_type')
    
    def __str__(self):
        return f"{self.user.username} reacted with {self.get_reaction_type_display()} to comment {self.comment.id}"

class Gallery(models.Model):
    """Gallery for multimedia content (images, videos)."""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Galleries"
    
    def __str__(self):
        return self.title

class MediaItem(models.Model):
    """Individual media items (images, videos) for galleries."""
    MEDIA_TYPES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
    )
    
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES)
    file = models.FileField(upload_to=get_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
