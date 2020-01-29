from MyGW.InsCompany import views
from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    url(r'^$', views.MainPageView.as_view(), name='main'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^edit_pass/$', views.password_edit, name='password_edit'),
    url(r'^reset/$', views.password_reset, name='password_reset'),
    url(r'^contracts/$', views.ContractsPageView.as_view(), name='contracts'),
    url(r'^contract/(?P<id>\d+)/$', views.ContractPageView.as_view(), name='contract_detail'),
    url(r'^contract/(?P<id>\d+)/edit/$', views.contract_edit, name='contract_edit'),
    url(r'^contract/new/$', views.contract_new, name='contract_new'),
    url(r'^contract/new/(?P<id>\d+)/risks$', views.contract_risks, name='contract_risks'),
    url(r'^persons/$', views.PersonsPageView.as_view(), name='persons'),
    url(r'^person/(?P<id>\d+)/$', views.PersonPageView.as_view(), name='person_detail'),
    url(r'^person/(?P<id>\d+)/edit/$', views.person_edit, name='person_edit'),
    url(r'^events/$', views.EventsPageView.as_view(), name='events'),
    url(r'^event/(?P<id>\d+)/$', views.EventPageView.as_view(), name='event_detail'),
    url(r'^event/new/$', views.insevent_new, name='event_new'),
    url(r'^dealer/new/$', views.dealer_new, name='dealer_new'),
    url(r'^worker/new/$', views.worker_new, name='worker_new'),
    url(r'^elemclaims/$', views.ElemClaimsPageView.as_view(), name='elemclaims'),
    url(r'^elemclaim/(?P<id>\d+)/$', views.ElemClaimPageView.as_view(), name='elemclaim_detail'),
    url(r'^elemclaim/(?P<id>\d+)/edit/$', views.elemclaim_edit, name='elemclaim_edit'),
    url(r'^contact/new/$', views.contact_new, name='contact_new'),
    url(r'^document/new/$', views.document_new, name='document_new'),
    url(r'^address/new/$', views.address_new, name='address_new'),
    url(r'^search/$', views.searching, name='search'),
    url(r'^report/$', views.ReportPageView.as_view(), name='report')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

