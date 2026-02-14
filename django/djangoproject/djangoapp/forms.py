from django import forms

# Story forms are handled manually in views since Story model is in Flask
# We don't use ModelForms for Flask models


class StoryForm(forms.Form):
    """Form for creating/editing stories via Flask API"""

    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Story Title"}
        ),
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Story Description",
            }
        ),
        required=False,
    )
    status = forms.ChoiceField(
        choices=[
            ("draft", "Draft"),
            ("published", "Published"),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        initial="draft",
    )


class PageForm(forms.Form):
    """Form for creating/editing pages via Flask API"""

    text = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "rows": 6, "placeholder": "Page text"}
        ),
        label="Page Text",
    )
    is_ending = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={"class": "form-check-input"}),
        label="Is this an ending?",
    )
    ending_label = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Ending label (optional)"}
        ),
        label="Ending Label",
    )


class ChoiceForm(forms.Form):
    """Form for creating/editing choices via Flask API"""

    text = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Choice text"}
        ),
        label="Choice Text",
    )
    next_page_id = forms.IntegerField(
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "Next page ID"}
        ),
        label="Next Page ID",
    )


class RatingForm(forms.Form):
    """Form for rating stories"""

    rating = forms.ChoiceField(
        choices=[(i, f'{i} Star{"s" if i > 1 else ""}') for i in range(1, 6)],
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Rating",
    )
    comment = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Your comment (optional)",
            }
        ),
        required=False,
        label="Comment",
    )


class ReportForm(forms.Form):
    """Form for reporting stories"""

    REASON_CHOICES = [
        ("spam", "Spam"),
        ("offensive", "Offensive Content"),
        ("inappropriate", "Inappropriate"),
        ("copyright", "Copyright Violation"),
        ("other", "Other"),
    ]

    reason = forms.ChoiceField(
        choices=REASON_CHOICES,
        widget=forms.Select(attrs={"class": "form-control"}),
        label="Reason",
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Please describe the issue",
            }
        ),
        label="Description",
    )
