import sys
import glob

sys.stdout.reconfigure(encoding='utf-8')

scripts = glob.glob('scripts/*.py')
print("Scripts found:", [s.replace('\\', '/') for s in scripts])
