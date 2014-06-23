from django.conf.urls import patterns, include, url

urlpatterns = patterns(
    '',
    url(r'^', include('clickreviews.api.urls'), name='api'),
)
