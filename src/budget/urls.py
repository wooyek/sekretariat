# -*- coding: utf-8 -*-
from django.urls import path

from . import views as v

app_name = 'budget'

urlpatterns = [
    path('budget/<int:pk>/update', v.BudgetUpdate.as_view(), name='BudgetUpdate'),
    path('budget/<int:pk>/', v.BudgetDetail.as_view(), name='BudgetDetail'),
    path('expenditure/', v.ApplicationList.as_view(), name='ApplicationList'),
    path('expenditure/user/<int:pk>/', v.ApplicationListUser.as_view(), name='ApplicationListUser'),
    path('expenditure/create', v.ApplicationCreate.as_view(), name='ApplicationCreate'),
    path('expenditure/<int:pk>/update', v.ApplicationUpdate.as_view(), name='ApplicationUpdate'),
    path('expenditure/<int:pk>/account', v.ApplicationAccount.as_view(), name='ApplicationAccount'),
    path('expenditure/<int:pk>/status', v.ApplicationStatus.as_view(), name='ApplicationStatus'),
    path('expenditure/<int:pk>/', v.ApplicationDetail.as_view(), name='ApplicationDetail'),
    path('expenditure/<int:pk>/<int:kind>/create', v.DecisionCreate.as_view(), name='DecisionCreate'),
    path('decision/<int:pk>/update/<int:kind>/', v.DecisionUpdate.as_view(), name='DecisionUpdate'),
]
