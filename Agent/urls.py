from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from Agent import views

urlpatterns = [
    url(r'^Registration/?', views.AgentRegister.as_view()),
    url(r'^Login/', views.AgentLogin.as_view(), name='login'),
    url(r'^ForgotPassword/', views.AgentForgotPassword.as_view(), name='forgot_password'),
    url(r'^ChangePassword/', views.AgentChangePassword.as_view(), name='change_password'),
    url(r'^Agents/?', views.AgentsList.as_view()),
    url(r'^AgentProfile/?', views.AgentProfile.as_view()),
    url(r'^Agent/', views.SingleAgent.as_view()),
    url(r'^AddClient/', views.AddClient.as_view()),
    url(r'^GetClient/', views.GetClient.as_view()),
    url(r'^Clients/?', views.ClientList.as_view()),
    url(r'^UpcomingSteps/', views.UpcomingSteps.as_view()),
    url(r'^ClientSteps/', views.ClientSteps.as_view()),
    url(r'^UpdateSteps/', views.UpdateSteps.as_view()),
    url(r'^AddStep/', views.AddStep.as_view()),
    url(r'^Vendors/$', views.VendorQuery.as_view()),
    url(r'^Vendors/StepSearch/', views.VendorQuery.as_view()),

]

#urlpatterns = format_suffix_patterns(urlpatterns)