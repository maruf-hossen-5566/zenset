from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib import messages

from contact_app.forms import ContactForm


@require_http_methods(["GET", "POST"])
def index(request):
    """
    Handle the contact form page.
    Shows form on GET and processes form on POST.
    """
    if request.method == "POST":
        form = ContactForm(request.POST)
        try:
            if form.is_valid():
                print(form.cleaned_data)
                messages.success(
                    request,
                    """
                    Form submitted successfully.
                    """,
                )
                return redirect("contact:index")
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
                return redirect("contact:index")
        except Exception as error:
            messages.error(request, f"An error occurred: {error}")
            return redirect("contact:index")

    return render(request, "contact_app/index.html")
