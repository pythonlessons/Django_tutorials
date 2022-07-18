from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from users.models import SubscribedUsers
from django.contrib import messages
from django.core.mail import EmailMessage

from .models import Article, ArticleSeries
from .decorators import user_is_superuser
from .forms import NewsletterForm, SeriesCreateForm, ArticleCreateForm, SeriesUpdateForm, ArticleUpdateForm#, NewsletterForm
from users.models import SubscribedUsers

import os
from uuid import uuid4

# Create your views here.
def homepage(request):
    matching_series = ArticleSeries.objects.all()
    
    return render(
        request=request,
        template_name='main/home.html',
        context={
            "objects": matching_series,
            "type": "series"
            }
        )

def series(request, series: str):
    matching_series = Article.objects.filter(series__slug=series).all()
    
    return render(
        request=request,
        template_name='main/home.html',
        context={
            "objects": matching_series,
            "type": "article"
            }
        )

def article(request, series: str, article: str):
    matching_article = Article.objects.filter(series__slug=series, article_slug=article).first()
    
    return render(
        request=request,
        template_name='main/article.html',
        context={"object": matching_article}
        )

@user_is_superuser
def new_series(request):
    if request.method == "POST":
        form = SeriesCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("homepage")

    else:
         form = SeriesCreateForm()

    return render(
        request=request,
        template_name='main/new_record.html',
        context={
            "object": "Series",
            "form": form
            }
        )

@user_is_superuser
def new_post(request):
    if request.method == "POST":
        form = ArticleCreateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(f"{form.cleaned_data['series'].slug}/{form.cleaned_data.get('article_slug')}")

    else:
         form = ArticleCreateForm()

    return render(
        request=request,
        template_name='main/new_record.html',
        context={
            "object": "Article",
            "form": form
            }
        )

@user_is_superuser
def series_update(request, series):
    matching_series = ArticleSeries.objects.filter(slug=series).first()

    if request.method == "POST":
        form = SeriesUpdateForm(request.POST, request.FILES, instance=matching_series)
        if form.is_valid():
            form.save()
            return redirect('homepage')
    
    else:
        form = SeriesUpdateForm(instance=matching_series)

        return render(
            request=request,
            template_name='main/new_record.html',
            context={
                "object": "Series",
                "form": form
                }
            )

@user_is_superuser
def series_delete(request, series):
    matching_series = ArticleSeries.objects.filter(slug=series).first()

    if request.method == "POST":
        matching_series.delete()
        return redirect('/')
    else:
        return render(
            request=request,
            template_name='main/confirm_delete.html',
            context={
                "object": matching_series,
                "type": "Series"
                }
            )

@user_is_superuser
def article_update(request, series, article):
    matching_article = Article.objects.filter(series__slug=series, article_slug=article).first()

    if request.method == "POST":
        form = ArticleUpdateForm(request.POST, request.FILES, instance=matching_article)
        if form.is_valid():
            form.save()
            return redirect(f'/{matching_article.slug}')
    
    else:
        form = ArticleUpdateForm(instance=matching_article)

        return render(
            request=request,
            template_name='main/new_record.html',
            context={
                "object": "Article",
                "form": form
                }
            )

@user_is_superuser
def article_delete(request, series, article):
    matching_article = Article.objects.filter(series__slug=series, article_slug=article).first()

    if request.method == "POST":
        matching_article.delete()
        return redirect('/')
    else:
        return render(
            request=request,
            template_name='main/confirm_delete.html',
            context={
                "object": matching_article,
                "type": "article"
                }
            )

@csrf_exempt
@user_is_superuser
def upload_image(request, series, article):
    if request.method != 'POST':
        return JsonResponse({"Error Message": "Wrong request"})

    matching_article = Article.objects.filter(series__slug=series, article_slug=article).first()
    if not matching_article:
        return JsonResponse({"Error Message": f"Wrong series({series}) or article ({article})"})

    file_obj = request.FILES['file']
    file_name_suffix = file_obj.name.split('.')[-1]
    if file_name_suffix not in ['jpg', 'png', 'gif', 'jpeg']:
        return JsonResponse({"Error Message": f"Wrong file suffix ({file_name_suffix}), supported are .jpg, .png, .git, .pjeg"})

    file_path = os.path.join(settings.MEDIA_ROOT, 'ArticleSeries', matching_article.slug, file_obj.name)

    if os.path.exists(file_path):
        file_obj.name = str(uuid4()) + '.' + file_name_suffix
        file_path = os.path.join(settings.MEDIA_ROOT, 'ArticleSeries', matching_article.slug, file_obj.name)

    with open(file_path, 'wb+') as f:
        for chunk in file_obj.chunks():
            f.write(chunk)

    return JsonResponse({
        "Message": "Image upload successfully",
        "location": os.path.join(settings.MEDIA_URL, 'ArticleSeries', matching_article.slug, file_obj.name)
        })

@user_is_superuser
def newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data.get('subject')
            receivers = form.cleaned_data.get('receivers').split(',')
            email_message = form.cleaned_data.get('message')

            mail = EmailMessage(subject, email_message, f"PyLessons <{request.user.email}>", bcc=receivers)
            mail.content_subtype = 'html'

            if mail.send():
                messages.success(request, "Email sent succesfully")
            else:
                messages.error(request, "There was an error sending email")

        else:
            for error in list(form.errors.values()):
                messages.error(request, error)

        return redirect('/')

    form = NewsletterForm()
    form.fields['receivers'].initial = ','.join([active.email for active in SubscribedUsers.objects.all()])
    return render(request=request, template_name='main/newsletter.html', context={'form': form})