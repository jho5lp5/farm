from django.urls import path, include
from django.contrib.auth.decorators import login_required
# from apps.user.views import users_list, UserList, user_create, user_update, user_save
from .views import *

urlpatterns = [
    path('subsidiary/', login_required(get_subsidiary_list), name='subsidiary'),
    path('modal_subsidiary_create/', login_required(modal_subsidiary_create), name='modal_subsidiary_create'),
    path('create_subsidiary/', login_required(create_subsidiary), name='create_subsidiary'),
    path('modal_subsidiary_update/', login_required(modal_subsidiary_update), name='modal_subsidiary_update'),
    path('update_subsidiary/', login_required(update_subsidiary), name='update_subsidiary'),

    path('employee/', login_required(get_employee_list), name='employee'),
    path('modal_user_create/', login_required(modal_user_create), name='modal_user_create'),
    path('create_user/', login_required(create_user), name='create_user'),
    path('modal_user_update/', login_required(modal_user_update), name='modal_user_update'),
    path('update_user/', login_required(update_user), name='update_user'),

]