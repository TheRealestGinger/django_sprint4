from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect

from .models import Post, Comment


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        return self.get_object().author == self.request.user


class CommentDeleteUpdateMixin(OnlyAuthorMixin):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={
                'post_id': self.get_object().post.id
            }
        )


class PostDeleteUpdateMixin(LoginRequiredMixin, OnlyAuthorMixin):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if not self.test_func():
            return redirect('blog:post_detail', self.kwargs[self.pk_url_kwarg])
        return super().dispatch(request, *args, **kwargs)


def posts_filter(posts=Post.objects):
    if hasattr(posts, 'filter'):
        return posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )


# def posts_filter(posts=Post.objects, fetch_author=False, fetch_location=False, fetch_category=False):
#     posts = posts.filter(
#         pub_date__lte=timezone.now(),
#         is_published=True,
#         category__is_published=True
#     )
#     if fetch_author:
#         posts = posts.select_related('author')
#     if fetch_location:
#         posts = posts.select_related('location')
#     if fetch_category:
#         posts = posts.select_related('category')
#     return posts
