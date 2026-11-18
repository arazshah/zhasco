from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render

from news.models import Post


def post_list(request):
    page = Paginator(Post.objects.filter(is_published=True), 9).get_page(request.GET.get("page"))
    return render(request, "news/list.html", {"page": page})


def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, is_published=True)
    more = Post.objects.filter(is_published=True).exclude(pk=pk)[:3]
    return render(request, "news/detail.html", {"post": post, "more": more})
