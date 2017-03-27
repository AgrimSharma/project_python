from django.conf.urls import url
import views

urlpatterns = (
    url(r'^(?P<object_name>[-\w]+)/$', views.detail, name='form_designer_detail'),
    url(r'^h/(?P<public_hash>[-\w]+)/$', views.detail_by_hash, name='form_designer_detail_by_hash'),
)
