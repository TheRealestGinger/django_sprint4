from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from .models import Comment, Post


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
                'post_id': self.kwargs['post_id']
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
    posts = posts.filter(
        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )
    posts = posts.select_related('author', 'category')
    posts = posts.prefetch_related('comments')
    return posts
