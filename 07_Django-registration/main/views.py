from django.shortcuts import render
from django.http import HttpResponse
from .models import Article, ArticleSeries

# Create your views here.
def homepage(request):
    matching_series = ArticleSeries.objects.all()
    
    return render(
        request=request,
        template_name='main/home.html',
        context={"objects": matching_series}
        )

def series(request, series: str):
    matching_series = Article.objects.filter(series__slug=series).all()
    
    return render(
        request=request,
        template_name='main/home.html',
        context={"objects": matching_series}
        )

def article(request, series: str, article: str):
    matching_article = Article.objects.filter(series__slug=series, article_slug=article).first()
    
    return render(
        request=request,
        template_name='main/article.html',
        context={"object": matching_article}
        )