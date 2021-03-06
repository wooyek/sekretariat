# coding=utf-8
# Copyright (c) 2018 Janusz Skonieczny

import logging

from django import forms

from . import models

log = logging.getLogger(__name__)


class DecisionForm(forms.ModelForm):
    class Meta:
        model = models.Decision
        fields = 'notes',
        widgets = {
            'notes': forms.Textarea(attrs={'cols': 80, 'rows': 3}),
        }


class ApplicationStatusForm(forms.ModelForm):
    # date = forms.DateField(disabled=True)
    # title = forms.CharField(disabled=True)

    class Meta:
        model = models.Application
        fields = 'status',
        widgets = {
            # 'status': widgets.RadioSelect(),
        }
