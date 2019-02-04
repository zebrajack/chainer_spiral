import numpy as np
import matplotlib.pyplot as plt
import argparse
from pathlib import Path
import logging
import pandas
import math
import matplotlib.gridspec as gridspec

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

EXCEPT_TAGS = ('steps',
                'episodes',
                'elapsed',
                'mean',
                'median',
                'stdev',
                'max',
                'min')

def load_scores(score_dir):
    logging.info(f"load scores.txt from {score_dir}")
    assert (score_dir / 'scores.txt').exists(), 'scores.txt does not exist!'

    df = pandas.read_csv(score_dir / 'scores.txt', 
                                dtype=np.float32, 
                                na_values='None',
                                sep='\t').sort_values('steps')
  
    df['elapsed'] = pandas.to_timedelta(df['elapsed'], unit='s')
    df = df.set_index('elapsed')

    # resample logs as every hour
    df = df.resample('1H').mean()

    return df
 

def plot_val(ax, steps, val, title, color='royalblue'):
    ax.plot(steps, val, color=color)
    ax.set_title(title)
    ax.set_xlabel('Step [k]')
    ax.grid(True)


def plot_score(args):
    logger.debug('plot scores.txt in %s', args.target_dir)

    data = load_scores(args.target_dir)

    logger.info(f"steps per 1 hour = {data['steps'][1] - data['steps'][0]}")

    # fix order
    if data['steps'].max() > 100000:
        data['steps'] = data['steps'] / 1000
        x_label = 'Step [k]'
    else:
        x_label = 'Step'

    # number of plots
    N = len(data.keys()) - len(EXCEPT_TAGS)
    n_cols = 3
    n_rows = int(math.ceil(N / n_cols))
    
    # init figure
    fig = plt.figure(figsize=(n_cols * 2 * 2, n_rows * 2))
    gs = gridspec.GridSpec(n_rows, n_cols)

    n = 0
    for col in data.columns:
        if col in EXCEPT_TAGS: continue 
        ax = plt.subplot(gs[n])
        plot_val(ax, data['steps'], data[col], col)
        n += 1

    # plt.suptitle(target)
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)

    plt.savefig(args.savename)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('target_dir', type=Path)
    parser.add_argument('savename')
    args = parser.parse_args()

    plot_score(args)
