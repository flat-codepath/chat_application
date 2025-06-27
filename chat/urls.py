from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='signup'),
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('test',views.test,name='test'),


    # We'll add chat URLs later
    path('threads/', views.thread_list, name='thread_list'),
    path('chat/<int:thread_id>/', views.chat_view, name='chat_home'),
    path('new-chat',views.start_new_chat,name='start_new_chat')
]