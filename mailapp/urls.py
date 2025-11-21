from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("", views.inbox_view, name="inbox"),
    path("email/<int:email_id>/", views.email_detail_view, name="email_detail"),
    path('compose/', views.compose_email_view, name='compose'),
]
