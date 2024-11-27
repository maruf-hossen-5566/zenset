from django.shortcuts import get_object_or_404, redirect
from django.db import transaction
from django.urls import reverse
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods
from django.contrib import messages
from django.db.models import F
from blog_app.decorators import post_published_required_for_engagement
from blog_app.models import Blog
from comment_app.models import Comment, Reply
from blog_project_with_flowbite.decorators import user_is_author, user_login_required


# Create your views here.
@user_login_required()
@require_http_methods(["POST"])
@post_published_required_for_engagement
@transaction.atomic
def comment_post(request, id):
    """
    Create a new comment on a blog post.

    Handles comment creation and updates post's comment count.
    Requires authentication and checks if comments are enabled.
    """

    comment_content = request.POST.get("comment")
    try:
        if comment_content.strip():
            post = get_object_or_404(Blog, id=id)
            if post and post.disable_comments:
                messages.error(request, "Comments are disabled for this post.")
                return redirect(
                    f"{reverse('blog:post_detail', kwargs={'username': post.author.username, 'slug': post.slug})}"
                    or request.META.get("HTTP_REFERER")
                )

            if post:
                comment = Comment(user=request.user, blog=post, content=comment_content)
                comment.save()
                post.increment_comment()
                messages.success(request, "Comment posted successfully.")
        else:
            messages.error(request, "Comment content is required.")
            return redirect(request.META.get("HTTP_REFERER"))

    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(
        f"{reverse('blog:post_detail', kwargs={'username': post.author.username, 'slug': post.slug})}#comment-{comment.id}"
        or request.META.get("HTTP_REFERER")
    )


@user_login_required()
@require_http_methods(["POST"])
@transaction.atomic
def comment_edit(request, id):
    """
    Edit an existing comment.

    Allows users to modify their own comments.
    Requires authentication and comment ownership.
    """
    comment_content = request.POST.get("new_comment")
    try:
        comment = request.user.comments.get(id=id)
        if comment_content.strip():
            comment.content = comment_content
            comment.save(update_fields=["content"])
            messages.success(request, "Comment updated successfully.")
            return redirect(
                reverse(
                    "blog:post_detail",
                    kwargs={
                        "username": comment.blog.author.username,
                        "slug": comment.blog.slug,
                    },
                )
                + f"#comment-{comment.id}"
                or request.META.get("HTTP_REFERER", "blog:index")
            )
        else:
            messages.error(request, "Comment content is required.")
            return redirect(request.META.get("HTTP_REFERER"))

    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))


@user_login_required()
@require_http_methods(["GET"])
@transaction.atomic
def comment_delete(request, id):
    """
    Delete an existing comment.

    Removes comment and decrements post's comment count.
    Requires authentication and comment ownership.
    """
    try:
        comment = request.user.comments.get(id=id)
        if comment:
            comment.blog.decrement_comment()
            comment.delete()
            messages.success(request, "Comment deleted successfully.")
    except Comment.DoesNotExist:
        messages.error(request, "Comment not found!")
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))


@user_login_required()
@require_http_methods(["POST"])
@transaction.atomic
def reply(request, id):
    """
    Create a new reply to a comment.

    Handles both top-level replies and nested replies.
    Requires authentication and checks if comments are enabled.
    """
    try:
        comment = get_object_or_404(Comment, id=id)
        reply_content = request.POST.get("reply_reply_content") or request.POST.get(
            "reply_content"
        )
        parent_reply_id = request.POST.get("parent_reply")

        if not comment.blog.is_published:
            messages.error(request, "Page not found!")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))

        if comment.blog.disable_comments:
            messages.error(request, "Comments and replies are disabled for this post.")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))

        if reply_content.strip():
            reply = Reply(user=request.user, comment=comment)

            if parent_reply_id:
                parent_reply = get_object_or_404(Reply, id=parent_reply_id)
                reply.parent_reply = parent_reply
                reply.content = f"{reply_content}"
            else:
                reply.content = f"{reply_content}"

            reply.save()
            comment.increment_reply_count()
            messages.success(request, "Reply posted successfully.")
            return redirect(
                f"{reverse('blog:post_detail', kwargs={'username': comment.blog.author.username, 'slug': comment.blog.slug})}#comment-{comment.id}"
                or request.META.get("HTTP_REFERER")
            )
        else:
            messages.error(request, "Reply content is required.")
            return redirect(request.META.get("HTTP_REFERER", "blog:index"))

    except Exception as error:
        messages.error(request, f"An error occurred: {error}")
        return redirect(request.META.get("HTTP_REFERER", "blog:index"))


@user_login_required()
@require_http_methods(["POST"])
@user_is_author(Reply, "user", "Invalid request!")
@transaction.atomic
def reply_edit(request, id):
    """
    Edit an existing reply.

    Allows users to modify their own replies.
    Requires authentication and reply ownership.
    """
    try:
        reply = request.user.replies.get(id=id)
        reply.content = request.POST.get("new_reply")
        if reply.content.strip():
            reply.save(update_fields=["content"])
            messages.success(request, "Reply updated successfully.")
            return redirect(
                f"{reverse('blog:post_detail', kwargs={'username': reply.comment.blog.author.username, 'slug': reply.comment.blog.slug})}#comment-{reply.comment.id}"
                or request.META.get("HTTP_REFERER", "blog:index")
            )
        else:
            messages.error(request, "Reply content is required.")
            return redirect(
                f"{reverse('blog:post_detail', kwargs={'username': reply.comment.blog.author.username, 'slug': reply.comment.blog.slug})}#comment-{reply.comment.id}"
                or request.META.get("HTTP_REFERER", "blog:index")
            )
    except Reply.DoesNotExist:
        messages.error(request, "Reply not found!")
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))


@user_login_required()
@require_GET
@transaction.atomic
def reply_delete(request, id):
    """
    Delete an existing reply.

    Removes reply and decrements comment's reply count.
    Requires authentication and reply ownership.
    """
    try:
        reply = request.user.replies.get(id=id)
        reply.comment.decrement_reply_count()
        reply.delete()
        messages.success(request, "Reply deleted successfully.")
    except Reply.DoesNotExist:
        messages.error(request, "Reply not found!")
    except Exception as error:
        messages.error(request, f"An error occurred: {error}")

    return redirect(request.META.get("HTTP_REFERER", "blog:index"))
