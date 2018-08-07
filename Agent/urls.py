from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from Agent import views

urlpatterns = [
    url(r'^Registration/?', views.AgentUserRegister.as_view()),
    url(r'^ClientRegistration/?', views.ClientUserRegister.as_view()),
    url(r'^Login/', views.AgentLogin.as_view(), name='login'),
    url(r'^ForgotPassword/', views.AgentForgotPassword.as_view(), name='forgot_password'),
    url(r'^ChangePassword/', views.AgentChangePassword.as_view(), name='change_password'),
    url(r'^Agents/?', views.AgentsList.as_view()),
    url(r'^AgentProfile/?', views.AgentProfile.as_view()),
    url(r'^Agent/', views.SingleAgent.as_view()),
    url(r'^AddClient/', views.AddClient.as_view()),
    url(r'^AddClientNew/', views.AddClientNew.as_view()),
    url(r'^GetClient/', views.GetClient.as_view()),
    url(r'^ClientGetClient/', views.ClientGetClient.as_view()),
    url(r'^Clients/?', views.ClientList.as_view()),
    url(r'^UpcomingSteps/', views.UpcomingSteps.as_view()),
    url(r'^ClientSteps/', views.ClientSteps.as_view()),
    url(r'^ClientClientSteps/', views.ClientClientSteps.as_view()),
    url(r'^ClientStepsNew/', views.ClientStepsNew.as_view()),
    url(r'^SingleStep/', views.SingleStep.as_view()),
    url(r'^DeleteStep/', views.DeleteStep.as_view()),
    url(r'^UpdateStep/', views.UpdateStep.as_view()),
    url(r'^UpdateSteps/', views.UpdateSteps.as_view()),
    url(r'^AddStep/', views.AddStep.as_view()),
    url(r'^Vendors/$', views.VendorQuery.as_view()),
    url(r'^Vendors/StepSearch/', views.VendorQuery.as_view()),
    url(r'^GetVendors/', views.VendorStepQuery.as_view()),
    url(r'^VendorRegions/', views.GetVendorRegions.as_view()),
    url(r'^RequestCity/', views.RequestCity.as_view()),

]

#urlpatterns = format_suffix_patterns(urlpatterns)