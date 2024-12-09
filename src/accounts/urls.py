from accounts.views import LoginView
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import path, reverse_lazy
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    path('register-user/', views.register_user, name='register-user'),
    path('register-client/', views.register_client, name='register-client'),
    path('register-subject-client/<int:pk>', views.register_subject_client, name='register-subject-client'),
    path('register-assosiate/', views.register_assosiate, name='register-assosiate'),
    path('edit-assosiate/<int:pk>', views.edit_assosiate, name='edit-assosiate'),
    path('edit-user/<int:pk>/', views.edit_user, name='edit-user'),
    path('self-edit-user/<int:pk>/', views.self_edit_user, name='self-edit-user'),
    path('add-user-files-aws/<int:pk>', views.add_user_files_aws, name="add-user-files-aws"),
    path('add-company-files-aws/<int:pk>', views.add_company_files_aws, name="add-company-files-aws"),
    path('edit-client/<int:pk>/', views.edit_client, name='edit-client'),
    path('self-edit-client/<int:pk>/', views.self_edit_client, name='self-edit-client'),
    path('edit-subject-client/<int:cpk>/<int:pk>', views.edit_subject_client, name='edit-subject-client'),
    path('choose-client/<int:pk>', views.choose_client, name="choose-client"),
    path('edit-company/', views.edit_company, name='edit-company'),
    path('profile-image', views.profile_image, name='profile-image'),
    path('profile-images/<int:user_id>', views.profile_images, name='profile-images'),
    path('upload-profile-picture', views.upload_profile_picture, name="upload-profile-picture"),
    path('password-reset/', PasswordResetView.as_view(
        template_name='accounts/password_reset.html',
        success_url=reverse_lazy('accounts:password_reset_done'),
        email_template_name='accounts/password_reset_email.html'
        ),
        name='password-reset'
        ),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url=reverse_lazy('accounts:password_reset_complete')
        ),
        name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),name='password_reset_complete'),
]