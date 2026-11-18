from django import forms

from core.models import ContactMessage


class ContactForm(forms.ModelForm):
    # honeypot: real users never see or fill this
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = ContactMessage
        fields = ["name", "phone", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"autocomplete": "name"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "dir": "ltr", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email", "dir": "ltr"}),
            "message": forms.Textarea(attrs={"rows": 5}),
        }

    def clean(self):
        data = super().clean()
        if data.get("website"):
            raise forms.ValidationError("spam")
        if not data.get("phone") and not data.get("email"):
            raise forms.ValidationError("لطفاً حداقل یکی از راه‌های ارتباطی (تلفن یا ایمیل) را وارد کنید.")
        return data
