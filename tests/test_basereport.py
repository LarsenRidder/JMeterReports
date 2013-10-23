from nose.tools import *

from reports.Base.report import BaseReport


def test_read_csv():
    report = BaseReport()
    report.read_csv('tests/test_data/test.csv')

    assert report.df['label'][1] == 'CMS_ADD_INQUIRY (without custom attributes)'
    assert report.df['label'][23500] == 'CMS_CREATE_HOLIDAY_NOTES'


@raises(IOError)
def test_read_csv_fail():
    report = BaseReport()
    report.read_csv('tests/test_data/test.csv123')
