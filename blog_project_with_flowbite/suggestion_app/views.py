from django.shortcuts import redirect, render
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Sum
from utils.herlpers import pro_print
from django.contrib import messages
from django.core.cache import cache
from django.core.paginator import Paginator
from blog_app.models import Tag


User = get_user_model()


def index(request):
    return render(request, "suggestion/index.html")


def authors(request):
    """
    Author suggestions page.
    Shows recommended authors to follow.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"suggestion:authors:user_{user_id}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        try:
            authors = User.objects.all().only(
                "id",
                "full_name",
                "bio",
                "tagline",
                "username",
            )

            if request.user.is_authenticated:
                authors = auhtors.exclude(
                    Q(id=request.user.id) | Q(followers__follower=request.user)
                )

            authors = authors.order_by("full_name")                
    
            paginator = Paginator(authors, 24)
            page_obj = paginator.get_page(page_number)
    
            context = {
                "page_obj": list(page_obj),
                "previous_page": (
                    page_obj.previous_page_number() if page_obj.has_previous() else None
                ),
                "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
            }
            cache.set(cache_key, context, 60 * 15)
            
        except Exception as error:
            messages.error(request, f"{error}")
            context={}
        

    return render(request, "suggestion_app/authors.html", context)


def tags(request):
    """
    Tag suggestions page.
    Shows popular and trending tags.
    """
    page_number = request.GET.get("page", 1)
    user_id = request.user.id if request.user.is_authenticated else "anon"
    cache_key = f"suggestion:tags:user_{user_id}:page_{page_number}"
    context = cache.get(cache_key)

    if not context:
        try:
            tags = Tag.objects.all().only("id", "name", "description", "slug")
            tags.order_by("?")
    
            # Pagination
            paginator = Paginator(tags, 24)
            page_obj = paginator.get_page(page_number)
    
            context = {
                "page_obj": list(page_obj),
                "next_page": page_obj.next_page_number() if page_obj.has_next() else None,
                "previous_page": (
                    page_obj.previous_page_number() if page_obj.has_previous() else None
                ),
            }
            cache.set(context, 60 * 15)
        except Exception as error:
            messages.error(request, f"{error}")
            context={}
            

    return render(request, "suggestion_app/tags.html", context)
