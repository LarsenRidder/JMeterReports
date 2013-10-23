__author__ = 'Evgeny.Luvsandugar'

import argparse
import os

parser = argparse.ArgumentParser(description='JMeter report generator')
parser.add_argument('name', metavar='REPORT_NAME', type=str, help='Report name')
parser.add_argument('data_file', metavar='DATA_FILE', type=str,
                    help='Path to JMeter jtl report (from aggregate report or simple data writer)')

args = parser.parse_args()

mod = __import__('reports.' + args.name + '.report', fromlist=[args.name + 'Report'])
klass = getattr(mod, args.name + 'Report')

report = klass()
report.read_csv(args.data_file)
report.to_html('test')