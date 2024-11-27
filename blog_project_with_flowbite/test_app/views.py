from django.shortcuts import render
from blog_app.models import Blog
from django.core.paginator import Paginator
from django.core.cache import cache

from utils.herlpers import pro_print

# Create your views here.
# def index(request):
# page_num = request.GET.get("page", 1)
# cache_key = f"test>index>{request.user.id if request.user.is_authenticated else 'anon'}>page_num_{page_num}"
# context = cache.get(cache_key)
# pro_print(context, "CONTEXT")

# if not context:
#     posts = Blog.objects.select_related("author", "category").order_by("-created_at")

#     paginator = Paginator(posts, 51)
#     page_obj = paginator.get_page(page_num)
#     context={
#         "page_obj":page_obj
#     }

#     cache.set(cache_key, context, 3000)
# return render(request, "test_app/index.html", context)


def index(request):
    page_num = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"test:index:{user_id}:page_{page_num}"  # Use : instead of >

    context = cache.get(cache_key)
    pro_print(context, "CONTEXT")

    if not context:
        posts = (
            Blog.objects.select_related("author", "category")
            .order_by("-created_at")
            .values("id", "title", "content", "author__full_name", "category__name")
        )  # Only select needed fields

        paginator = Paginator(posts, 51)
        page_obj = paginator.get_page(page_num)
        pro_print(page_obj.paginator.num_pages, "NEXT")

        # Cache only necessary data, not the entire page_obj
        context = {
            "posts": list(page_obj.object_list),
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "next_page_number": (
                page_obj.next_page_number() if page_obj.has_next() else None
            ),
            "previous_page_number": (
                page_obj.previous_page_number() if page_obj.has_previous() else None
            ),
            "num_pages": page_obj.paginator.num_pages,
            "current_page": page_obj.number,
        }
        cache.set(cache_key, context, 300)
        # cache.delete(cache_key)

    return render(request, "test_app/index.html", context)
