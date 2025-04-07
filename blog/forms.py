from django import forms
from markdownx.fields import MarkdownxFormField
from .models import Post, Comment, Gallery, MediaItem

class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""
    content = MarkdownxFormField()
    
    class Meta:
        model = Post
        fields = ['title', 'content', 'featured_image', 'status', 'tags']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['content'].widget.attrs.update({'class': 'form-control', 'rows': 10})
        self.fields['featured_image'].widget.attrs.update({'class': 'form-control'})
        self.fields['status'].widget.attrs.update({'class': 'form-select'})
        self.fields['tags'].widget.attrs.update({'class': 'form-control', 'data-role': 'tagsinput'})

class CommentForm(forms.ModelForm):
    """Form for adding comments."""
    class Meta:
        model = Comment
        fields = ['content']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'form-control', 
            'rows': 3,
            'placeholder': 'Write your comment here...'
        })

class GalleryForm(forms.ModelForm):
    """Form for creating and editing galleries."""
    class Meta:
        model = Gallery
        fields = ['title', 'description']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 3})

class MediaItemForm(forms.ModelForm):
    """Form for adding media items to galleries."""
    class Meta:
        model = MediaItem
        fields = ['title', 'description', 'media_type', 'file']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'rows': 2})
        self.fields['media_type'].widget.attrs.update({'class': 'form-select'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})

class SearchForm(forms.Form):
    """Form for searching blog posts."""
    query = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search...'
        })
    )
