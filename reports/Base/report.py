import datetime
import numpy as np
import os
import pandas as pd
import shutil
from jinja2 import Template
from lxml import etree

from lib.utils import percentile90


class BaseReport:
    def __init__(self):
        # default template string if base template not exist
        self.template = '<!DOCTYPE html><head><title>Default template</title></head><body>{{ data_table }}</body>'
        # load base template
        self.load_template(os.path.dirname(os.path.realpath(__file__)) + '/index.jinja2')

    def read_csv(self, file_path):
        self.df = pd.read_csv(file_path)

    def load_template(self, file_path):
        if os.path.isfile(file_path):
            self.template = open(file_path, 'r').read()
        else:
            print('Template "%s" not found' % file_path)

    def to_html(self, report_name=None):
        if not report_name:
            report_name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_Base")

        if os.path.isdir('results/' + report_name):
            os.rename('results/' + report_name, 'results/' + report_name + '_before_' + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

        os.mkdir('results/' + report_name)
        os.mkdir('results/' + report_name + '/css')
        os.mkdir('results/' + report_name + '/requests_detail')

        shutil.copy('reports/bootstrap.min.css', 'results/' + report_name + '/css')
        shutil.copy('reports/theme.css', 'results/' + report_name + '/css')

        stat = self.__get_stat()
        stat.index.name = None

        xml = etree.XML(stat.to_html())
        xml.set('class', 'table table-hover table-striped table-condensed table-responsive table-bordered')
        xml.set('border', '')

        template = Template(self.template)
        report = template.render(data_table=etree.tostring(xml))

        f = open('results/' + report_name + '/index.html', 'w')
        f.write(report)


    def __get_stat(self):
        # group data by 'label' field
        group_by_operation = self.df.groupby('label')
        # calc statistic by operation: mean, median, 90% line
        result = group_by_operation['Latency'].agg([np.mean, np.median, percentile90, np.min, np.max, np.sum])
        size = group_by_operation.size()

        # Calc throughput for every group
        result['sum'] = result['sum'].astype(float)
        for i in size.index:
            result['sum'][i] = float(size[i]) / float(result['sum'][i]) * 1000

        result.rename(columns={'mean': 'Mean, msec',
                               'median': 'Median, msec',
                               'percentile90': '90% Line, msec',
                               'amin': 'Min, msec',
                               'amax': 'Max, msec',
                               'sum': 'Throughput, req/sec'}, inplace=True)

        # round
        return result.applymap(lambda x: round(x, 2))







