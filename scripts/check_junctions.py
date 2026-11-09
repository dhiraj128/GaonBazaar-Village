import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

# Let's inspect around 28270
print("Around 28270:")
print(runner[28200:28350])

# And around 63140
print("\nAround 63140:")
print(runner[63100:63250])
