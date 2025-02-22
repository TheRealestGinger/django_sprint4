from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    ListView
)
from django.views.generic.list import MultipleObjectMixin
from django.urls import reverse_lazy, reverse

from pages.views import page_not_found
from .forms import PostForm, CommentForm, UserForm
from .models import Post, Category, Comment
from .utils import OnlyAuthorMixin, posts_filter


User = get_user_model()


class CategoryDetailView(DetailView, MultipleObjectMixin):
    model = Category
    template_name = 'blog/category.html'
    slug_field = 'slug'
    slug_url_kwarg = 'category_slug'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if self.get_object().is_published is False:
            return page_not_found(request, '404.html')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        post = Post.objects.all().filter(
            category=self.get_object()
        )
        object_list = posts_filter(post)
        context = super(CategoryDetailView, self).get_context_data(
            object_list=object_list,
            **kwargs
        )
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if ((self.get_object().is_published is False
             or self.get_object().category.is_published is False
             or self.get_object().pub_date > timezone.now())
           and self.request.user != self.get_object().author):
            return page_not_found(request, '404.html')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.select_related('author')
        return context


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        object_list = posts_filter()
        context = super(PostListView, self).get_context_data(
            object_list=object_list,
            **kwargs
        )
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not self.test_func():
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.pub_date = self.object.pub_date
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.pk}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not self.test_func():
            return redirect('blog:post_detail', post_id=self.kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(instance=self.object)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class ShowProfilePageDetailView(DetailView, MultipleObjectMixin):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        if not User.objects.filter(username=kwargs['username']).exists():
            return page_not_found(request, '404.html')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        object_list = Post.objects.filter(author=self.get_object())
        context = super(ShowProfilePageDetailView, self).get_context_data(
            object_list=object_list,
            profile=self.get_object(),
            user=self.request.user,
            **kwargs
        )
        return context


class EditProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'blog/user.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        post = get_object_or_404(Post, id=self.kwargs['post_id'])
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        self.object.post.comment_count = self.object.post.comment_count + 1
        self.object.post.save()
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    pk_url_kwarg = 'comment_id'
    template_name = 'blog/comment.html'

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['form'] = CommentForm()
    #     return context

    def get_success_url(self):
        self.object.post.comment_count = self.object.post.comment_count - 1
        self.object.post.save()
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.object.post.pk}
        )
