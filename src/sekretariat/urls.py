# -*- coding: utf-8 -*-
from django.urls import path

from . import views as v

app_name = 'sekretariat'

urlpatterns = [
    path('oo/<int:pk>/update', v.OpenOfficeGroupSlots.as_view(), name='OpenOfficeGroupSlots'),
    path('oo/<int:pk>/', v.OpenOfficeGroupDetail.as_view(), name='OpenOfficeGroupDetail'),
    path('oo/', v.OpenOfficeGroupList.as_view(), name='OpenOfficeGroupList'),
    path('os/<int:pk>/book', v.OpenOfficeSlotBook.as_view(), name='OpenOfficeSlotBook'),
    path('os/<int:pk>/success', v.OpenOfficeSlotBookSuccess.as_view(), name='OpenOfficeSlotBookSuccess'),
    path('os/<int:pk>/confirm/<str:secret>', v.OpenOfficeSlotBookConfirm.as_view(), name='OpenOfficeSlotBookConfirm'),
]
