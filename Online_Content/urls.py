from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path(r'comentionfigure', views.comentionfigure, name='comentionfigure'),
    path('report/report_fig1', views.report_fig1, name='report_fig1'),
    path('report/', views.report, name='report'),
    path('articles/', views.ArticleListView.as_view(), name='articles'),
    path('articles/<int:pk>', views.ArticleDetailView.as_view(), name='article-detail'),
    path('authors/', views.AuthorListView.as_view(), name='author'),
    path('authors/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
    path('topic/', views.TopicListView.as_view(), name='topic'),
    path('topic/<int:pk>', views.TopicDetailView.as_view(), name='topic-detail'),
   
     ]
urlpatterns += [
    path('book/<int:pk>/report/', views.competiter, name='competiter'),
]