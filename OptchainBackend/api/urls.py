from django.conf.urls import url
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import *

urlpatterns = [
    url(r'stocks/list/$',StockTickerList.as_view()),
    path(r'stocks/<str:ticker>/history/',StockPriceList.as_view()),
    path(r'options/<str:ticker>/expirations/',OptionsExpirations.as_view()),
    path(r'options/<str:ticker>/contracts/',OptionsPriceList.as_view()),
    path(r'options/<str:ticker>/summary/',OptionsSummary.as_view()),
    path(r'options/history/<str:contract>/',OptionsPriceHistory.as_view()),
]

#urlpatterns = format_suffix_patterns(urlpatterns)
