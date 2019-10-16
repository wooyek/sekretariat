import logging
from pathlib import Path

import pytest
import tablib
from django.conf import settings

from .. import resources

log = logging.getLogger(__name__)

BUDGET_TSV = """year	month	account no	amount
2019	10	405-04	0
2019	10	401-13	0
2019	10	401-06	22
2019	10	402-10	0
2019	10	401-08	123
"""


# noinspection PyMethodMayBeStatic
@pytest.mark.django_db
class BudgetResourceTest(object):
    def test_import(self):
        data = BUDGET_TSV
        logging.debug("data: %s" % data)
        dataset = tablib.Dataset().load(data, format='tsv')
        resources.BudgetResource().import_data(dataset, raise_errors=True)

    def test_import_xls(self):
        import_file = Path(settings.BASE_DIR) / 'fixtures' / 'test_data' / 'budget.xls'
        with import_file.open('rb') as data:
            data = data.read()
            dataset = tablib.Dataset().load(data, format='xls')
            resources.BudgetResource().import_data(dataset, raise_errors=True)

    def test_import_xlsx(self):
        import_file = Path(settings.BASE_DIR) / 'fixtures' / 'test_data' / 'budget.xlsx'
        with import_file.open('rb') as data:
            data = data.read()
            dataset = tablib.Dataset().load(data, format='xlsx')
            resources.BudgetResource().import_data(dataset, raise_errors=True)
