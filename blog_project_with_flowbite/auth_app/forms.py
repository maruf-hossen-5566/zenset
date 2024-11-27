from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from utils.herlpers import pro_print
from PIL import Image

User = get_user_model()


class RegisterForm(UserCreationForm):
    """
    User registration form.
    Extends UserCreationForm with custom fields.
    """

    class Meta:
        model = User
        fields = ["full_name", "username", "email", "password1", "password2"]


class ProfileForm(forms.ModelForm):
    """
    User profile edit form.
    Handles user profile data and image upload validation.
    """

    class Meta:
        model = User
        fields = [
            "full_name",
            "email",
            "username",
            "tagline",
            "bio",
            "image",
            "job_title",
            "company_name",
            "education",
            "location",
            "website",
            "github",
            "linkedin",
            "twitter",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Full Name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email"}),
            "username": forms.TextInput(attrs={"placeholder": "Username"}),
            "image": forms.FileInput(
                attrs={
                    "class": "form-control-file",
                    "accept": "image/*",
                    "max_size": "1MB",
                },
            ),
            # "image": forms.FileInput(
            #     attrs={
            #         "class": "form-control-file",
            #         "accept": "image/*",
            #         "max_size": "1MB",
            #     },
            # ),
            "tagline": forms.Textarea(attrs={"rows": 3}),
            "bio": forms.Textarea(attrs={"rows": 5}),
            "job_title": forms.TextInput(attrs={"placeholder": "Job Title"}),
            "company_name": forms.TextInput(attrs={"placeholder": "Company Name"}),
            "education": forms.TextInput(attrs={"placeholder": "Education"}),
            "location": forms.TextInput(attrs={"placeholder": "Location"}),
            "website": forms.URLInput(attrs={"placeholder": "https://example.com"}),
            "github": forms.URLInput(
                attrs={"placeholder": "https://github.com/username"}
            ),
            "linkedin": forms.URLInput(
                attrs={"placeholder": "https://linkedin.com/in/username"}
            ),
            "twitter": forms.URLInput(
                attrs={"placeholder": "https://twitter.com/username"}
            ),
        }
        error_messages = {
            "full_name": {"required": "Full name is required"},
            "email": {"required": "Email is required"},
            "username": {"required": "Username is required"},
            "image": {
                "max_size": "Image file size must be less than 1MB. (from error_messages)",
                "required": "Image is required (from error_messages)",
            },
        }

    def clean_image(self):
        """
        Validate uploaded profile image.
        Checks file type, size, and dimensions.
        """
        image = self.cleaned_data.get("image")

        # Check if the image is a CloudinaryResource / For Cloudinary only
        if hasattr(image, "resource_type"):
            return image

        # Check if the image is a file / For Cloudinary only
        if hasattr(image, "file"):
            try:
                img = Image.open(image)
                img.verify()  # verify method closed the file so we need to open it again for further processing
                img = Image.open(image)

                if image.size > 1 * 1024 * 1024:
                    raise forms.ValidationError("Image file size must be less than 1MB")

                max_width = 800
                max_height = 800
                if img.width > max_width or img.height > max_height:
                    raise forms.ValidationError(
                        f"Image dimensions must be less than {max_width}x{max_height}"
                    )

            except Exception as error:
                for err in error:
                    raise forms.ValidationError(f"{err}")
        return image
