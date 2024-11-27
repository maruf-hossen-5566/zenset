from django import forms
from django.core.validators import validate_email


class ContactForm(forms.Form):
    """
    Contact form for user inquiries.
    Validates name, email, subject and message.
    """

    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

    error_messages = {
        "name": {
            "required": "Name is required",
        },
        "email": {
            "required": "Email is required",
            "invalid": "Invalid email address",
        },
        "subject": {
            "required": "Subject is required",
        },
        "message": {
            "required": "Message is required",
        },
    }

    def clean_email(self):
        """
        Validate email field.
        Ensures email is provided and properly formatted.
        """
        email = self.cleaned_data.get("email")
        if not email:
            raise forms.ValidationError(self.error_messages["email"]["required"])

        try:
            validate_email(email)
        except Exception as error:
            # raise forms.ValidationError(self.error_messages["email"]["invalid"])
            for err in error.messages:
                raise forms.ValidationError(err)
        return email
