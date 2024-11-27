from django import forms
from django.conf import settings

from utils.herlpers import pro_print
from .models import Blog
from PIL import Image


class BlogForm(forms.ModelForm):
    """
    Blog post creation/edit form.
    Handles post content and image upload validation.
    """

    class Meta:
        model = Blog
        fields = [
            "title",
            "content",
            "image",
            "tags",
            "disable_comments",
            "pin_to_profile",
            "is_published",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
                    "required": "required",
                }
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "hidden bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5",
                    "required": "required",
                }
            ),
        }
        error_messages = {
            "title": {"required": "Required!"},
            "content": {"required": "Required!"},
            "image": {
                "invalid_image": "The file must be an image (e.g. PNG, JPG, JPEG, GIF, or BMP).",
                "max_size": "Image file size must be less than 1MB.",
            },
        }

    def clean_image(self):
        """
        Validate uploaded blog post image.
        Checks file type and size.
        """
        image = self.cleaned_data.get("image")
        pro_print(image, "FORM IMAGE")

        if hasattr(image, "resource_type"):
            pro_print(image.resource_type, "RESOURCE TYPE")
            return image

        if hasattr(image, "file"):
            try:
                img = Image.open(image)
                pro_print(img, "OPENED IMAGE")

                # Verify image
                img.verify()

                img = Image.open(image)

                image_size = 1 * 1024 * 1024
                if image.size > image_size:
                    raise forms.ValidationError(
                        self._meta.error_messages["image"]["max_size"]
                    )

            except Exception as error:
                for err in error:
                    raise forms.ValidationError(f"{err}")

        return image
