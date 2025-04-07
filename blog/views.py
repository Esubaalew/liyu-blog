from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, ArchiveIndexView, MonthArchiveView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from taggit.models import Tag
from .models import Post, Comment, CommentReaction, Gallery, MediaItem
import json

class PostListView(ListView):
    """View for listing blog posts with pagination."""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return published posts only."""
        return Post.objects.filter(status='published').order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['popular_tags'] = Tag.objects.annotate(
            num_posts=Count('taggit_taggeditem_items')
        ).order_by('-num_posts')[:10]
        context['recent_posts'] = Post.objects.filter(
            status='published'
        ).order_by('-published_at')[:5]
        return context

class PostDetailView(DetailView):
    """View for displaying a single blog post."""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        """Return published posts only."""
        return Post.objects.filter(status='published')
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        # Get comments for this post
        context['comments'] = Comment.objects.filter(
            post=self.object, parent=None, is_approved=True
        )
        # Get related posts based on tags
        post_tags_ids = self.object.tags.values_list('id', flat=True)
        related_posts = Post.objects.filter(
            status='published', tags__in=post_tags_ids
        ).exclude(id=self.object.id).distinct()
        context['related_posts'] = related_posts[:3]
        # Increase view count
        self.object.increase_views()
        return context

class TaggedPostListView(ListView):
    """View for listing posts with a specific tag."""
    model = Post
    template_name = 'blog/tagged_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return published posts with the specified tag."""
        tag_slug = self.kwargs.get('tag_slug')
        self.tag = get_object_or_404(Tag, slug=tag_slug)
        return Post.objects.filter(
            status='published', tags__name__in=[self.tag.name]
        ).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        return context

class AuthorPostListView(ListView):
    """View for listing posts by a specific author."""
    model = Post
    template_name = 'blog/author_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return published posts by the specified author."""
        username = self.kwargs.get('username')
        self.author = get_object_or_404(User, username=username)
        return Post.objects.filter(
            status='published', author=self.author
        ).order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        return context

class SearchResultsView(ListView):
    """View for search results."""
    model = Post
    template_name = 'blog/search_results.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Return search results."""
        query = self.request.GET.get('q', '')
        if query:
            return Post.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query),
                status='published'
            ).order_by('-published_at')
        return Post.objects.none()
    
    def get_context_data(self, **kwargs):
        """Add additional context data."""
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context

class ArchiveListView(ArchiveIndexView):
    """View for listing archives by date."""
    model = Post
    date_field = 'published_at'
    template_name = 'blog/archives.html'
    context_object_name = 'posts'
    allow_empty = True
    
    def get_queryset(self):
        """Return published posts only."""
        return Post.objects.filter(status='published')

class MonthArchiveView(MonthArchiveView):
    """View for listing posts from a specific month."""
    model = Post
    date_field = 'published_at'
    template_name = 'blog/month_archive.html'
    context_object_name = 'posts'
    month_format = '%m'
    allow_empty = True
    
    def get_queryset(self):
        """Return published posts only."""
        return Post.objects.filter(status='published')

class GalleryListView(ListView):
    """View for listing galleries."""
    model = Gallery
    template_name = 'blog/gallery_list.html'
    context_object_name = 'galleries'
    paginate_by = 12

class GalleryDetailView(DetailView):
    """View for displaying a single gallery."""
    model = Gallery
    template_name = 'blog/gallery_detail.html'
    context_object_name = 'gallery'

@login_required
def add_comment(request):
    """Add a new comment to a post."""
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        content = request.POST.get('content')
        
        post = get_object_or_404(Post, id=post_id)
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content,
            is_approved=True  # Auto-approve for now
        )
        
        return redirect(post.get_absolute_url() + '#comment-' + str(comment.id))
    return redirect('blog:post_list')

@login_required
def add_reply(request):
    """Add a reply to a comment."""
    if request.method == 'POST':
        post_id = request.POST.get('post_id')
        parent_id = request.POST.get('parent_id')
        content = request.POST.get('content')
        
        post = get_object_or_404(Post, id=post_id)
        parent = get_object_or_404(Comment, id=parent_id)
        
        reply = Comment.objects.create(
            post=post,
            author=request.user,
            parent=parent,
            content=content,
            is_approved=True  # Auto-approve for now
        )
        
        return redirect(post.get_absolute_url() + '#comment-' + str(reply.id))
    return redirect('blog:post_list')

@login_required
def react_to_comment(request):
    """Add or remove a reaction to a comment."""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        data = json.loads(request.body)
        comment_id = data.get('comment_id')
        reaction_type = data.get('reaction_type')
        
        comment = get_object_or_404(Comment, id=comment_id)
        
        # Check if reaction already exists
        existing_reaction = CommentReaction.objects.filter(
            comment=comment,
            user=request.user,
            reaction_type=reaction_type
        ).first()
        
        if existing_reaction:
            # Remove reaction if it already exists
            existing_reaction.delete()
            action = 'removed'
        else:
            # Add new reaction
            CommentReaction.objects.create(
                comment=comment,
                user=request.user,
                reaction_type=reaction_type
            )
            action = 'added'
        
        # Get updated reaction counts
        reaction_counts = {
            'like': CommentReaction.objects.filter(comment=comment, reaction_type='like').count(),
            'fire': CommentReaction.objects.filter(comment=comment, reaction_type='fire').count(),
            'idea': CommentReaction.objects.filter(comment=comment, reaction_type='idea').count(),
        }
        
        return JsonResponse({
            'success': True,
            'action': action,
            'reaction_counts': reaction_counts
        })
    
    return JsonResponse({'success': False}, status=400)
