from django.contrib import admin

# Register your models here.
from .models import Author, Topic, Source, Article,Article_content

admin.site.register(Source)
admin.site.register(Author)
admin.site.register(Topic)
admin.site.register(Article)
admin.site.register(Article_content)