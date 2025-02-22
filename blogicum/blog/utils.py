from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone

from .models import Post


class OnlyAuthorMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


def posts_filter(posts=Post.objects):
    return posts.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )
