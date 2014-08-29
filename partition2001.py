import os
import shutil

for f in os.listdir('imagesfinal'):
    n = int(f.split('.')[0])
    shutil.copyfile(os.path.join('imagesfinal',f), '2001_{0}/{1}.jpg'.format(n % 4,n)) 
