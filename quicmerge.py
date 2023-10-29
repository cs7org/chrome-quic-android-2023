import argparse

import pandas as pd

import utils
import os

# GENERAL INIT
# parse arguments
parser = argparse.ArgumentParser(description="quicbench")
parser.add_argument('first', type=str, help="files to compare")
parser.add_argument('more', nargs='+', type=str, help="more files to compare")
parser.add_argument('-p', '--plot', nargs='?', const='', help="plot")
parser.add_argument('-o', '--output', help="csv output")
parser.add_argument('--ymin', help="set y range min")
parser.add_argument('--ymax', help="set y range max")
args = parser.parse_args()

files = args.more
files.insert(0, args.first)

rdf = pd.DataFrame()
for f in files:
    trdf = pd.read_csv(f)
    trdf['provider'] = os.path.basename(f).replace(".csv", "")
    rdf = pd.concat([rdf, trdf])

rdf['duration'] = rdf['responseEnd'] - rdf['requestStart']

if args.plot is not None:
    utils.plot(rdf, args.plot, args.ymin, args.ymax)
