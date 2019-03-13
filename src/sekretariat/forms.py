# coding=utf-8
from django import forms
from django.utils.translation import get_language
from django.utils.translation import ugettext_lazy as _

from . import models


class TranslatedMultipleChoiceField(forms.ModelMultipleChoiceField):
    def label_from_instance(self, obj):
        return obj.trans(get_language())


class OpenOfficeSlotConfirm(forms.ModelForm):
    class Meta:
        model = models.OpenOfficeSlot
        fields = ['student']


class OpenOfficeSlotForm(forms.ModelForm):
    class Meta:
        model = models.OpenOfficeSlot
        fields = ('student', 'email')
        labels = {
            'name': _('name'),
        }

    def __init__(self, *args, **kwargs):
        super(OpenOfficeSlotForm, self).__init__(*args, **kwargs)
        for key in self.fields:
            self.fields[key].required = True
