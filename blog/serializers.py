from rest_framework import serializers
from .models import Post, Comment, Gallery, MediaItem
from django.contrib.auth.models import User
from taggit.serializers import TagListSerializerField

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']

class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    tags = TagListSerializerField()
    comments = CommentSerializer(many=True, read_only=True)
    formatted_content = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'content', 'formatted_content', 
                  'featured_image', 'status', 'created_at', 'updated_at', 
                  'published_at', 'tags', 'views', 'comments']
    
    def get_formatted_content(self, obj):
        return obj.formatted_markdown()

class MediaItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaItem
        fields = ['id', 'title', 'description', 'media_type', 'file', 'created_at']

class GallerySerializer(serializers.ModelSerializer):
    items = MediaItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Gallery
        fields = ['id', 'title', 'description', 'created_at', 'items']
