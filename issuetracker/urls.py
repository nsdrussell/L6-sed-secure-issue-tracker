from django.urls import path
from issuetracker import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('register', views.register, name='register'),
    path('user', views.user_options, name='user_options'),
    path('user/change_password', views.change_password, name='change_password'),
    path('user/change_nickname', views.change_nickname, name='change_nickname'),
    path('users', views.users_list, name='users_list'),
    path('users/<int:user_id>/update', views.admin_update_user, name='admin_update_user'),
    path('users/<int:user_id>/delete', views.admin_delete_user, name='admin_delete_user'),
    path('categories', views.categories, name='categories'),
    path('categories/create', views.create_category, name='create_category'),   
    path('categories/<int:category_id>/', views.view_category, name='view_category'),
    path('categories/<int:category_id>/update', views.update_category, name='update_category'),
    path('categories/<int:category_id>/delete', views.delete_category_plus_children_plus_image_files, name='delete_category'),
    path('categories/<int:category_id>/create_issue', views.create_issue, name='create_issue'),
    path('categories/<int:category_id>/issues/<int:issue_id>', views.view_issue, name='view_issue'),
    path('categories/<int:category_id>/issues/<int:issue_id>/update', views.update_issue, name='update_issue'),
    path('categories/<int:category_id>/issues/<int:issue_id>/delete', views.delete_issue, name='delete_issue'),
    path('categories/<int:category_id>/issues/<int:issue_id>/delete_image', views.delete_issue_image, name='delete_issue_image'),
    path('categories/<int:category_id>/issues/<int:issue_id>/create_comment', views.create_comment, name='create_comment'),
    path('categories/<int:category_id>/issues/<int:issue_id>/comments/<int:comment_id>/delete_image', views.delete_comment_image, name='delete_comment_image'),
    path('categories/<int:category_id>/issues/<int:issue_id>/comments/<int:comment_id>/update', views.update_comment, name='update_comment'),
    path('categories/<int:category_id>/issues/<int:issue_id>/comments/<int:comment_id>/delete', views.delete_comment, name='delete_comment'),
    path('create_example_rows', views.create_example_rows, name='create_example_rows'),
    
]
