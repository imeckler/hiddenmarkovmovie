from colorsys import *
import PIL.Image as I
import math
import os
import sys
from collections import defaultdict
import random
import shutil
import subprocess

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
        try:
            im = I.open(os.path.join(image_dir, i))
            n = int(i.split('.')[0])
            hist, avg = hist_and_avg(im)
            mode_bucket = max(hist.items(), key=lambda x: x[1])
            avg_bucket = hs_bucket(*avg)
            res[n] = (mode_bucket, avg_bucket)
            print {'num':n, 'mode_bucket':mode_bucket, 'avg_bucket': avg_bucket, 'avg': avg,'path':i}
        except Exception as e:
            if type(e) == KeyboardInterrupt:
                raise e
            print '!'+i

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

def gen_image_sequence(markov_run, bucket_map):
    return [random.choice(bucket_map[b]) for b in markov_run]

def heman_remix(dest, n=1000):
    bucket_map = eval(open('hemandata/hemanbucketmap').read())
    buckets = [x for x, y in eval(open('hemandata/hemanbuckets').read())]
    model = build_markov(buckets)
    imgs = gen_image_sequence(run_markov(model, n), bucket_map)
    
    os.mkdir(dest)
    for i, img in enumerate(imgs, 1):
        shutil.copyfile('heman/{}.jpg'.format(img), os.path.join(dest, '{}.jpg'.format(i)))

    subprocess.call(['ffmpeg', '-f', 'image2', '-i', os.path.join(dest, '%d.jpg'), dest + '.mpeg'])


def main():
    image_dir = sys.argv[1]
    res = gen_bucket_sequence(image_dir)
    print
    print res

def hist_and_avg(img):
    res = defaultdict(int)
    h_sum, s_sum, v_sum = 0, 0, 0
    num_pixels = 0

    for r, g, b in img.getdata():
        num_pixels += 1
        h, s, v = rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        h_sum += h
        s_sum += s
        v_sum += v
        res[hs_bucket(h, s, v, n=12)] += 1

    return (res, (h_sum / num_pixels, s_sum / num_pixels, v_sum / num_pixels))

def color_histogram(img):
    res = defaultdict(int)
    for r, g, b in img.getdata():
        res[hs_bucket(*rgb_to_hsv(r/255.0, g/255.0, b/255.0), n=10)] += 1
    return res

if __name__ == '__main__':
    main()
