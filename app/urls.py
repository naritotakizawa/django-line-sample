from django.urls import path
from . import views

app_name = 'app'

urlpatterns = [
    # Line 友達追加のWeb hook
    path('callback/', views.callback, name='callback'),

    path('', views.LineUserList.as_view(), name='line_user_list'),
    path('detail/<int:pk>/', views.LineMessageList.as_view(), name='line_message_list'),
]
