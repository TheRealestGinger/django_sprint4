from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    ListView
)
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse

from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, Comment, User
from .utils import (
    OnlyAuthorMixin,
    CommentDeleteUpdateMixin,
    PostDeleteUpdateMixin,
    posts_filter
)

PAGINATION_BY = 10


class CategoryDetailView(DetailView, MultipleObjectMixin):
    model = Category
    template_name = 'blog/category.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    paginate_by = PAGINATION_BY

    def get_object(self, queryset=None):
        category = super().get_object(queryset)
        if not category.is_published:
            return get_object_or_404(Category, is_published=True)
        return category

    def get_context_data(self, **kwargs):
        return super(CategoryDetailView, self).get_context_data(
            object_list=posts_filter(
                self.object.posts.select_related('category')
            ).annotate(comment_count=Count('comments')).order_by('-pub_date'),
            **kwargs
        )


class PostDetailView(DetailView, OnlyAuthorMixin):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None):
        post = super().get_object(queryset)
        if post.author != self.request.user:
            return get_object_or_404(posts_filter(
                Post.objects.filter(id=self.kwargs['post_id'])
            ))
        return post

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=CommentForm(),
            comments=self.object.comments.select_related('author'),
            **kwargs
        )


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = PAGINATION_BY

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            object_list=posts_filter(
            ).annotate(comment_count=Count('comments')).order_by('-pub_date'),
            **kwargs
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class PostUpdateView(PostDeleteUpdateMixin, UpdateView):
    form_class = PostForm

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.object.pk]
        )


class PostDeleteView(PostDeleteUpdateMixin, DeleteView):

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            form=PostForm(instance=self.object),
            **kwargs
        )

    def get_success_url(self):
        return reverse(
            'blog:profile',
            args=[self.request.user.username]
        )


class ProfileDetailView(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = PAGINATION_BY

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_context_data(self, **kwargs):
        object_list_author = Post.objects.filter(author=self.get_object())
        object_list_not_author = posts_filter(object_list_author)
        object_list = object_list_author if (
                self.get_object() == self.request.user
            ) else object_list_not_author
        context = super().get_context_data(
            object_list=object_list.annotate(
                comment_count=Count('comments')
            ).order_by('-pub_date'),
            profile=self.get_object(),
            **kwargs
        )
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'

    def get_object(self, queryset=None):
        return get_object_or_404(User, username=self.kwargs['username'])

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, id=self.kwargs['post_id'])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.object.post.pk]
        )


class CommentUpdateView(CommentDeleteUpdateMixin, UpdateView):
    form_class = CommentForm


class CommentDeleteView(CommentDeleteUpdateMixin, DeleteView):
    pass
