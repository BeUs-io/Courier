from django.contrib.auth.views import PasswordResetView
from django.urls import path, reverse_lazy
from accounts import views, forms


urlpatterns = [
    path('login/', views.LoginView.as_view(), name='auth_login'),
    path(
        'set_password/<token>/',
        views.UserInviteSetPassword.as_view(), name="set_password"),
    path(
        'user/invite/complete/',
        views.UserInviteComplete.as_view(), name="user_invite_complete"),
    path(
        "password/reset/",
        PasswordResetView.as_view(
            form_class=forms.PasswordResetForm,
            success_url=reverse_lazy('auth_password_reset_done')
        ),
        name='auth_password_reset'
    ),
    path('', views.AccountTemplateView.as_view(), name="account"),
    path(
        'profile/',
        views.AccountProfileView.as_view(),
        name="account_profile"
    ),
    path('delete/', views.AccountDeleteView.as_view(), name="account_delete"),
    path(
        'password-change/',
        views.PasswordChangeView.as_view(),
        name="auth_password_change"
    ),
    path(
        'user-groups-list/',
        views.UserGroupListView.as_view(),
        name="user_groups_list"
    ),
    path(
        'user-groups-form/',
        views.UserGroupCreateView.as_view(),
        name="user_groups_form"
    ),
    path(
        'user-groups-update/<pk>/',
        views.UserGroupUpdateView.as_view(),
        name="user_groups_update"
    ),
    path(
        'user-groups-delete/<pk>/',
        views.UserGroupDeleteView.as_view(),
        name="user_groups_delete"
    ),
    path('user-list', views.UserListView.as_view(), name="user_list"),
    path('user-create', views.UserCreateView.as_view(), name="user_create"),
    path('user-invite', views.UserInviteView.as_view(), name="user_invite"),
    path(
        'user-update/<pk>/',
        views.UserUpdateView.as_view(),
        name="user_update"
    ),
    path(
        'user-delete/<pk>/',
        views.UserDeleteView.as_view(),
        name="user_delete"
    ),
    path(
        'user-password-update/<pk>/',
        views.UserPasswordUpdateView.as_view(),
        name="user_pass_update"
    ),
    path(
        'designation-list/',
        views.DesignationListView.as_view(),
        name="designation_list"
    ),
    path(
        'designation-form/',
        views.DesignationCreateView.as_view(),
        name="designation_form"
    ),
    path(
        'designation-update/<pk>/',
        views.DesignationUpdateView.as_view(),
        name="designation_update"
    ),
    path(
        'designation-delete/<pk>/',
        views.DesignationDeleteView.as_view(),
        name="designation_delete"
    ),
    path('user-logs/', views.UserLogsListView.as_view(), name="user_logs"),
    path('logout/', views.LogoutView.as_view(), name='auth_logout'),
]
