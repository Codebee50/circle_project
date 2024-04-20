from django.urls import path
from . import views

app_name = 'memo'


urlpatterns = [
    path('list/', views.memo_list, name='list'),
    path('create/', views.create, name='create'), 
    path('view/<int:mid>/', views.memo_detail, name='detail'),
    path('delete/<int:mid>/', views.delete_memo, name='deletememo')
]