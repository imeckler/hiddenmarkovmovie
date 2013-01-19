from colorsys import *
import PIL.Image as I
import math
import os
import sys
from collections import defaultdict
import random

def average_rgb(path):
    im = I.open(path)
    r_sum, g_sum, b_sum = 0, 0, 0
    num_pixels = 0
    
    for r, g, b in im.getdata():
        num_pixels += 1
        r_sum += r
        g_sum += g
        b_sum += b
    
    return (int(r_sum / num_pixels), int(g_sum / num_pixels), int(b_sum / num_pixels))

def average_hsv(im):
    h_sum, s_sum, v_sum = 0, 0, 0
    num_pixels = 0

    for r, g, b in im.getdata():
        h, s, v = rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        num_pixels += 1
        h_sum += h
        s_sum += s
        v_sum += v
    
    return (h_sum / num_pixels, s_sum / num_pixels, v_sum / num_pixels)

def hs_bucket(h, s, v, n=12):
    return (int(math.ceil(h * n)), int(math.ceil(s * n)))

def gen_bucket_sequence(image_dir):
    res = {} 
    for i in os.listdir(image_dir):
        im = I.open(os.path.join(image_dir, i))
        n = int(i.split('.')[0])
        mode_bucket = max(color_histogram(im).items(), key=lambda x: x[1])
        res[n] = mode_bucket
        print {'num':n, 'mode_bucket':mode_bucket, 'path':i}
   
    print
    print res
    print

    return res.values()

class Multinomial(object):
    def __init__(self, categories):
        total_count = float(sum(categories.itervalues()))
        normed_cats = {k : v / total_count for k, v in categories.iteritems()}
        self.distribution = normed_cats
    
    def sample(self):
        r = random.random()
        total = 0
        for cat, prob in self.distribution.iteritems():
            total += prob
            if total > r:
                return cat


def build_markov(buckets):
    counts = defaultdict(lambda: defaultdict(int))

    for i in xrange(len(buckets) - 1):
        counts[buckets[i]][buckets[i + 1]] += 1

    return {k: Multinomial(v) for k, v in counts.iteritems()}

def run_markov(markov, n=100):
    state = random.choice(markov.keys())
    run = [state]
    for i in xrange(n):
        state = markov[state].sample()
        run.append(state)
    return run

def main():
    image_dir = sys.argv[1]
    res = gen_bucket_sequence(image_dir)
    print
    print res

def color_histogram(img):
    res = defaultdict(int)
    for r, g, b in img.getdata():
        res[hs_bucket(*rgb_to_hsv(r/255.0, g/255.0, b/255.0), n=10)] += 1
    return res

if __name__ == '__main__':
    main()
