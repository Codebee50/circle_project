from . import views
from django.contrib.auth import views as auth_views
from django.urls import path
from .departments import seed_departments,seed_offices


app_name = 'accounts'
urlpatterns = [
    path('confirmcode/<int:uid>/', views.confirmcode, name='confirmcode'),
    path('resendcode/<int:uid>/', views.resend_activation_code, name='resendcode'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('password/request/', views.reqeust_reset_password, name='passwordrequest'),
    path('password/<int:uid>/confirm/', views.confirm_reset_code, name='confirmreset'),
    path('password/<int:uid>/resend/', views.resend_password_reset_code, name='resendpasswordreset'),
    path('password/<int:uid>/<str:code>/reset/', views.reset_password, name='passwordreset'),
    
    path('selectdept/<int:uid>/', views.select_dept, name='selectdept'),
    path('welcomeuser/<int:uid>/', views.welcome_user, name='welcomeuser'),
    path('profile/edit/', views.edit_profile, name='editprofile'),
    path('profile/view/<int:uid>/', views.view_profile, name='viewprofile'),
    path('getprofile/<int:profile_id>/', views.get_user_profile, name='getuserprofile'),
    path('logout/', views.log_out, name='logout'),
    path('seed/department/', seed_departments, name='seeddartments'),
    path('seed/offices/', seed_offices, name='seedoffices'),
    path('updatephoto/<str:action>/', views.update_user_profile_photo, name='updatephoto')
]