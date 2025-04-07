from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Post, Comment, Gallery, MediaItem
from .serializers import PostSerializer, CommentSerializer, GallerySerializer, MediaItemSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.filter(status='published')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'published_at', 'views']
    lookup_field = 'slug'
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published')
        tag = self.request.query_params.get('tag', None)
        author = self.request.query_params.get('author', None)
        
        if tag:
            queryset = queryset.filter(tags__name__in=[tag])
        if author:
            queryset = queryset.filter(author__username=author)
            
        return queryset
    
    @action(detail=True, methods=['post'])
    def add_comment(self, request, slug=None):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(post=post, author=request.user, is_approved=True)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, slug=None):
        post = self.get_object()
        comments = Comment.objects.filter(post=post, parent=None, is_approved=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increase_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class GalleryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def items(self, request, pk=None):
        gallery = self.get_object()
        items = gallery.items.all()
        serializer = MediaItemSerializer(items, many=True)
        return Response(serializer.data)

class MediaItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MediaItem.objects.all()
    serializer_class = MediaItemSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
