import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

pos = runner.find('modal-runner-order-chat')
print(runner[pos+800:pos+2500])
