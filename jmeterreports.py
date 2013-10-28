__author__ = 'Evgeny.Luvsandugar'

import argparse
import os
import codecs

parser = argparse.ArgumentParser(description='JMeter report generator')
parser.add_argument('name', metavar='REPORT_NAME', type=str, help='Report name')
parser.add_argument('data_file', metavar='DATA_FILE', type=str,
                    help='Path to JMeter jtl report (from aggregate report or simple data writer)')
parser.add_argument('-d', '--description', metavar='DESCRIPTION', type=str,
                    help='Path to YAML file with report description')
args = parser.parse_args()

mod = __import__('reports.' + args.name + '.report', fromlist=[args.name + 'Report'])
klass = getattr(mod, args.name + 'Report')

if not os.path.isdir('results/'):
    os.mkdir('results')

report = klass()
report.read_csv(args.data_file)
if args.description:
    report.set_description(args.description)
report.to_html('test')