import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

print("Around 38628:")
print(runner[38600:39200])

print("\nAround 67000:")
print(runner[66800:67500])
