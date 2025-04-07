import unittest
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from blog.models import Post, Comment, Gallery, MediaItem
from taggit.models import Tag
import tempfile
from PIL import Image
import io

class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            content='This is a test post content.',
            status='published'
        )
        self.post.tags.add('test', 'django')
        
    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.content, 'This is a test post content.')
        self.assertEqual(self.post.status, 'published')
        self.assertEqual(self.post.tags.count(), 2)
        
    def test_post_slug_generation(self):
        self.assertTrue(self.post.slug)
        self.assertIn('test-post', self.post.slug)
        
    def test_post_str_representation(self):
        self.assertEqual(str(self.post), 'Test Post')
        
    def test_post_get_absolute_url(self):
        url = self.post.get_absolute_url()
        self.assertEqual(url, f'/blog/post/{self.post.slug}/')
        
    def test_post_formatted_markdown(self):
        self.post.content = '**Bold text**'
        self.post.save()
        formatted = self.post.formatted_markdown()
        self.assertIn('<strong>Bold text</strong>', formatted)
        
    def test_post_increase_views(self):
        initial_views = self.post.views
        self.post.increase_views()
        self.assertEqual(self.post.views, initial_views + 1)
        
    def test_post_create_new_version(self):
        self.post.title = 'Updated Test Post'
        new_version = self.post.create_new_version()
        
        self.assertEqual(new_version.title, 'Updated Test Post')
        self.assertEqual(new_version.version, self.post.version + 1)
        self.assertEqual(new_version.previous_version, self.post)
        self.assertEqual(new_version.tags.count(), self.post.tags.count())

class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            content='This is a test post content.',
            status='published'
        )
        
        self.comment = Comment.objects.create(
            post=self.post,
            author=self.user,
            content='This is a test comment.',
            is_approved=True
        )
        
        self.reply = Comment.objects.create(
            post=self.post,
            author=self.user,
            parent=self.comment,
            content='This is a reply to the test comment.',
            is_approved=True
        )
        
    def test_comment_creation(self):
        self.assertEqual(self.comment.post, self.post)
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.content, 'This is a test comment.')
        self.assertTrue(self.comment.is_approved)
        
    def test_comment_str_representation(self):
        expected = f'Comment by {self.user.username} on {self.post.title}'
        self.assertEqual(str(self.comment), expected)
        
    def test_comment_get_replies(self):
        replies = self.comment.get_replies()
        self.assertEqual(replies.count(), 1)
        self.assertEqual(replies.first(), self.reply)

class ViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.post = Post.objects.create(
            title='Test Post',
            author=self.user,
            content='This is a test post content.',
            status='published'
        )
        self.post.tags.add('test', 'django')
        
        self.gallery = Gallery.objects.create(
            title='Test Gallery',
            description='This is a test gallery.'
        )
        
    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        
    def test_post_list_view(self):
        response = self.client.get(reverse('blog:post_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_list.html')
        self.assertContains(response, 'Test Post')
        
    def test_post_detail_view(self):
        response = self.client.get(reverse('blog:post_detail', args=[self.post.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/post_detail.html')
        self.assertContains(response, 'Test Post')
        self.assertContains(response, 'This is a test post content.')
        
    def test_tagged_posts_view(self):
        tag = Tag.objects.get(name='test')
        response = self.client.get(reverse('blog:tagged_posts', args=[tag.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/tagged_posts.html')
        self.assertContains(response, 'Test Post')
        
    def test_author_posts_view(self):
        response = self.client.get(reverse('blog:author_posts', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/author_posts.html')
        self.assertContains(response, 'Test Post')
        
    def test_search_results_view(self):
        response = self.client.get(reverse('blog:search_results'), {'q': 'test'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/search_results.html')
        self.assertContains(response, 'Test Post')
        
    def test_gallery_list_view(self):
        response = self.client.get(reverse('blog:gallery_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/gallery_list.html')
        self.assertContains(response, 'Test Gallery')
        
    def test_gallery_detail_view(self):
        response = self.client.get(reverse('blog:gallery_detail', args=[self.gallery.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/gallery_detail.html')
        self.assertContains(response, 'Test Gallery')
        
    def test_add_comment_authenticated(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.post(reverse('blog:add_comment'), {
            'post_id': self.post.id,
            'content': 'This is a test comment from the view test.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after successful comment
        self.assertEqual(Comment.objects.count(), 1)
        
    def test_add_comment_unauthenticated(self):
        response = self.client.post(reverse('blog:add_comment'), {
            'post_id': self.post.id,
            'content': 'This is a test comment from the view test.'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login
        self.assertEqual(Comment.objects.count(), 0)

if __name__ == '__main__':
    unittest.main()
