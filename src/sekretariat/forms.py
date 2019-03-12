# coding=utf-8
from django import forms
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from . import models


class TranslatedMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.trans(get_language())


class SampleModelForm(forms.ModelForm):
    class Meta:
        model = models.SampleModel
        fields = ('name',)
        labels = {
            'name': _('name'),
        }
