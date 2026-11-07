import sys
sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

pos_m = runner.find('modal-runner-order-chat')
print("Runner modal at:", pos_m)
if pos_m != -1:
    print(runner[pos_m-50:pos_m+2200])

pos_fn = runner.find('function openRunnerOrderChat')
print("\nRunner chat functions at:", pos_fn)
if pos_fn != -1:
    print(runner[pos_fn:pos_fn+3000])
