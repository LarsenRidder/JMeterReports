import codecs
import datetime
import os
import sys
import pandas as pd
import shutil
import yaml

from jinja2 import Template


class BaseReport(object):
    """Base class for reports.
    """

    def __init__(self):
        # default template string if base template not exist
        self.template = '<!DOCTYPE html><head><title>Default template</title></head><body>{{ data_table }}</body>'
        # test environment
        self.environment = []
        # test report
        self.report = ''
        # pandas data frame
        self.df = None
        # set default template name. you can redefine in child report class
        if not hasattr(self, '_template_name'):
            self._template_name = 'index.jinja2'

        report_dir = os.path.dirname(sys.modules[self.__module__].__file__)
        self.set_template(report_dir + '/' + self._template_name)

    def read_csv(self, file_path):
        self.df = pd.read_csv(file_path)

    def to_html(self, report_name=None):
        # set default report name
        if not report_name:
            report_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_Base")

        # rename previous report if exist
        if os.path.isdir('results/' + report_name):
            os.rename('results/' + report_name, 'results/' + report_name + '_before_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

        # prepare dir
        os.mkdir('results/' + report_name)
        os.mkdir('results/' + report_name + '/css')
        os.mkdir('results/' + report_name + '/js')

        # copy external lib
        shutil.copy('lib/external/bootstrap/css/bootstrap.css', 'results/' + report_name + '/css')
        shutil.copy('lib/theme.css', 'results/' + report_name + '/css')
        shutil.copy('lib/external/bootstrap/js/bootstrap.js', 'results/' + report_name + '/js')
        shutil.copy('lib/external/jquery/jquery.js', 'results/' + report_name + '/js')

        report = self._generate_html_report()

        f = codecs.open('results/' + report_name + '/index.html', 'w', encoding='utf-8')
        f.write(report)

    def set_template(self, file_path):
        """Load template.
        """
        if os.path.isfile(file_path):
            self.template = open(file_path, 'r').read()
        else:
            print('Template "%s" not found. Set default.' % file_path)

    def set_description(self, file_path):
        """Parse report description.

        Keyword arguments:
        description -- string in YAML format.
        """
        d = yaml.load(codecs.open(file_path, encoding='utf-8').read())

        if 'environment' in d:
            self.environment = d['environment']

        if 'description' in d:
            self.report = d['description']

    def _generate_html_report(self):
        if not hasattr(self, 'df') or not self.df:
            return ''

        data_table = self._generate_html_data()

        template = Template(self.template)
        return template.render(data_table=data_table, env=self.environment, report=self.report)

    def _generate_html_data(self):
        return self.df.to_html()