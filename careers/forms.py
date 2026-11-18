from django import forms

from careers.models import JobApplication


class ApplicationForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={"tabindex": "-1", "autocomplete": "off"}))

    class Meta:
        model = JobApplication
        fields = ["name", "phone", "email", "field_of_study", "message", "resume"]
        widgets = {
            "phone": forms.TextInput(attrs={"dir": "ltr", "inputmode": "tel"}),
            "email": forms.EmailInput(attrs={"dir": "ltr"}),
            "message": forms.Textarea(attrs={"rows": 4}),
            "resume": forms.ClearableFileInput(attrs={"accept": ".pdf,.doc,.docx"}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("spam")
        return ""
