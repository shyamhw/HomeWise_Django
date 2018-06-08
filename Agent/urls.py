from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from Agent import views

urlpatterns = [
    url(r'^Registration/?', views.AgentRegister.as_view()),
    url(r'^Login/', views.AgentLogin.as_view(), name='login'),
    url(r'^ForgotPassword/', views.AgentForgotPassword.as_view(), name='forgot_password'),
    url(r'^ChangePassword/', views.AgentChangePassword.as_view(), name='change_password'),
    url(r'^Agents/?', views.AgentsList.as_view()),
    url(r'^Agent/', views.SingleAgent.as_view()),
    url(r'^Client/', views.SingleClient.as_view()),
    url(r'^Clients/?', views.ClientList.as_view()),

]

#urlpatterns = format_suffix_patterns(urlpatterns)