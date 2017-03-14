from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^status/', 'aap_app.views.status', name='status'),
	url(r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'aap/login.html'}, name="login"),
	url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/'}, name="logout"),
    url(r'^dashboard/', 'aap_app.views.dashboard', name='dashboard'),
    url(r'^$', 'aap_app.views.index', name='index'),
)
