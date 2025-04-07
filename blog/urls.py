from django.urls import path, include
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='post_list'),
    path('post/<slug:slug>/', views.PostDetailView.as_view(), name='post_detail'),
    path('tag/<slug:tag_slug>/', views.TaggedPostListView.as_view(), name='tagged_posts'),
    path('author/<str:username>/', views.AuthorPostListView.as_view(), name='author_posts'),
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    path('archives/', views.ArchiveListView.as_view(), name='archives'),
    path('archives/<int:year>/<int:month>/', views.MonthArchiveView.as_view(), name='month_archive'),
    path('comment/add/', views.add_comment, name='add_comment'),
    path('comment/reply/', views.add_reply, name='add_reply'),
    path('comment/react/', views.react_to_comment, name='react_to_comment'),
    path('gallery/', views.GalleryListView.as_view(), name='gallery_list'),
    path('gallery/<int:pk>/', views.GalleryDetailView.as_view(), name='gallery_detail'),
]
