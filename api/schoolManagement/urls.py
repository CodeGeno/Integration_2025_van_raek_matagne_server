from django.urls import path
from .views import ArticleListCreate, ArticleRetrieveUpdateDelete

urlpatterns = [
    path('articles/', ArticleListCreate.as_view(), name='article-list-create'),
    path('articles/<int:pk>/', ArticleRetrieveUpdateDelete.as_view(), name='article-detail'),
]
