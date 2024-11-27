import random
import uuid
from django import template
from django.utils.safestring import mark_safe

from utils.herlpers import pro_print

register = template.Library()


@register.filter(name="split_paragraphs", is_safe=True)
def split_paragraphs(value):
    paragraphs = value.split("\n")
    return mark_safe("".join(f"<p>{p.strip()}</p>" for p in paragraphs if p.strip()))


@register.filter(name="match_path", is_safe=True)
def match_path(value, path_to_match):
    path = [segment for segment in str(value.strip()).split("/") if segment.strip()]
    path_match, at_point = str(path_to_match).strip().split(",")
    if path[int(at_point)] == path_match:
        return True
    return False


@register.filter(name="random_uuid", is_safe=True)
def random_uuid(value):
    return str(uuid.uuid4())


@register.filter(name="reply_filter", is_safe=True)
def reply_filter(value) -> str:
    main_content = value.split("</span>", 1)[-1]
    return main_content.strip()


@register.filter(name="humanize_thousands", is_safe=True)
def humanize_thousands(value):

    try:
        value = float(value)
        if value >= 1000000:
            return f"{value/1000000:.1f}M".rstrip("0").rstrip(".")
        elif value >= 1000:
            return f"{value/1000:.1f}K".rstrip("0").rstrip(".")
        return str(int(value))
    except (ValueError, TypeError):
        return value


@register.filter("map_ids", is_safe=True)
def map_ids(objects):
    ids = [tag.id for tag in objects]
    return ids


@register.filter(name="sub", is_safe=True)
def sub(value, arg):
    return value - arg


@register.filter(name="r_img", is_safe=True)
def r_img(username):
    img_list = [
        "https://images.pexels.com/photos/8981857/pexels-photo-8981857.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/14785828/pexels-photo-14785828.jpeg",
        "https://images.pexels.com/photos/4384780/pexels-photo-4384780.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1",
        "https://images.pexels.com/photos/18311088/pexels-photo-18311088/free-photo-of-iphone-laptop-ipad-pc.jpeg",
        "https://images.unsplash.com/photo-1586297135537-94bc9ba060aa?q=80&w=2080&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "https://images.unsplash.com/photo-1521310192545-4ac7951413f0?q=80&w=1974&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "https://images.unsplash.com/photo-1542123216-43b94383ca6a?q=80&w=2070&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "https://images.unsplash.com/photo-1557939706-fcc0ea82a221?q=80&w=2080&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "https://images.unsplash.com/photo-1543278732-824a807df8bd?q=80&w=2127&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    ]

    return random.choice(img_list)
