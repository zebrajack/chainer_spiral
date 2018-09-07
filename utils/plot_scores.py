import numpy as np
import matplotlib; matplotlib.use('Cairo')
import matplotlib.pyplot as plt
import argparse
import os
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

import pandas
import math
import matplotlib.gridspec as gridspec

EXCEPT_TAGS = ('steps',
                'episodes',
                'elapsed',
                'mean',
                'median',
                'stdev',
                'max',
                'min')

def set_axis_prop(ax, title, x_label):
    ax.set_title(title)
    ax.set_xlabel(x_label)
    ax.grid()

def plot_score(args):
    logger.debug('plot scores.txt in %s', args.target_dir)

    target = os.path.join(args.target_dir, 'scores.txt')

    assert os.path.exists(target)

    table = pandas.read_table(target, dtype=np.float32, na_values='None')

    steps = np.array(table['steps'])

    # fix ordering of the records due to a bug
    inds = np.argsort(steps)
    steps = steps[inds]

    elapsed = np.array(table['elapsed'])[inds]

    if steps[-1] > 1000:
        elapsed_min = elapsed[-1] / steps[-1] * 1000
        elapsed_min = elapsed_min / 60 
        print(f" elapsed per 1k steps [min] = {elapsed_min}")

    cut_idx = None

    data = {}
    for col in table.columns:
        if not col in EXCEPT_TAGS:
            data[col] = np.array(table[col])[inds]
            is_nan_idx = np.where(np.isnan(data[col]))[0]
            if len(is_nan_idx) and is_nan_idx.min() > 0:
                cut_idx = is_nan_idx.min()
    
    if cut_idx:
        steps = steps[:cut_idx]
        elapsed = steps[:cut_idx]

    # fix order
    if steps.max() > 100000:
        steps = steps / 1000
        x_label = 'Step [k]'
    else:
        x_label = 'Step'

    # number of plots
    N = len(data.keys())
    n_cols = 3
    n_rows = int(math.ceil(N / n_cols))
    
    # init figure
    fig = plt.figure(figsize=(n_cols * 2 * 2, n_rows * 2))
    gs = gridspec.GridSpec(n_rows, n_cols)

    n = 0
    for key, value in data.items():
        ax = plt.subplot(gs[n])

        scalar = value[inds]
        if cut_idx:
            scalar = value[inds][:cut_idx]
        
        if args.conv_num:
            num = args.conv_num
            b = np.ones(num) / num
            scalar = np.convolve(scalar, b, mode='same')

        ax.plot(steps, scalar)
        set_axis_prop(ax, key, x_label)
        ax.set_xlim(0, steps.max())
        n += 1

    # plt.suptitle(target)
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

    plt.savefig(args.savename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target_dir')
    parser.add_argument('savename')
    parser.add_argument('--conv_num', type=int)
    args = parser.parse_args()

    plot_score(args)
