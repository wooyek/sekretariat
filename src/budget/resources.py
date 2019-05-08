# coding=utf-8
import logging

from django.core.exceptions import ObjectDoesNotExist
from import_export import fields, resources, widgets

from . import models

log = logging.getLogger(__name__)


class CreatingWidget(widgets.ForeignKeyWidget):

    def __init__(self, model, field='pk', ignore_missing=True, *args, **kwargs):
        super().__init__(model, field, *args, **kwargs)
        self.ignore_missing = ignore_missing

    def clean(self, value, row=None, *args, **kwargs):
        try:
            item = super().clean(value)
            if item is not None:
                return item
        except ObjectDoesNotExist:
            if not self.ignore_missing:
                raise
            item = self.model()
            setattr(item, self.field, value)
            return item


class DecimalWidget(widgets.DecimalWidget):

    def clean(self, value, row=None, *args, **kwargs):
        if value and isinstance(value, str):
            value = value.replace('\xa0', '')
        return super().clean(value, row, *args, **kwargs)


class BudgetResource(resources.ModelResource):
    account = fields.Field(column_name='account no', attribute='account', widget=widgets.ForeignKeyWidget(models.Account, 'no'))
    amount = fields.Field(column_name='amount', attribute='amount', widget=DecimalWidget())

    class Meta:
        model = models.Budget
        fields = ('year', 'month', 'account', 'amount')
        export_order = ('year', 'month', 'account', 'amount')
        import_id_fields = 'year', 'month', 'account'

    def get_or_init_instance(self, instance_loader, row):
        instance, new = super().get_or_init_instance(instance_loader, row)
        if instance.account_id is None:
            account, new = models.Account.objects.get_or_create(no=row['account no'])
            instance.account = account
        return instance, new

    def before_save_instance(self, instance, using_transactions, dry_run):
        super().before_save_instance(instance, using_transactions, dry_run)
        if using_transactions or not dry_run:
            account = instance.account
            log.debug("account: %s", account)
            if account.pk is None:
                account.save()
                instance.account_id = account.pk
