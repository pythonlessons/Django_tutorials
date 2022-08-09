from django import forms
from .models import Article, ArticleSeries
from tinymce.widgets import TinyMCE

class SeriesCreateForm(forms.ModelForm):
    class Meta:
        model = ArticleSeries

        fields = [
            "title",
            "subtitle",
            "slug",
            "image",
        ]

class ArticleCreateForm(forms.ModelForm):
    class Meta:
        model = Article

        fields = [
            "title",
            "subtitle",
            "article_slug",
            "content",
            "notes",
            "series",
            "image",
        ]

class SeriesUpdateForm(forms.ModelForm):
    class Meta:
        model = ArticleSeries

        fields = [
            "title",
            "subtitle",
            "image",
        ]

class ArticleUpdateForm(forms.ModelForm):
    class Meta:
        model = Article

        fields = [
            "title",
            "subtitle",
            "content",
            "notes",
            "series",
            "image",
        ]

class NewsletterForm(forms.Form):
    subject = forms.CharField()
    receivers = forms.CharField()
    message = forms.CharField(widget=TinyMCE(), label="Email content")