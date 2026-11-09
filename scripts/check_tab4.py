import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('public_web/runner/index.html', 'r', encoding='utf-8') as f:
    runner = f.read()

idx_7_2 = runner.rfind('id="screen-onboarding-7"')
print("Second screen 7 at:", idx_7_2)
print(runner[idx_7_2:idx_7_2+1500])

# and where is TAB 4?
idx_tab4 = runner.find('TAB 4:')
print("TAB 4: at:", idx_tab4)
idx_tab4_last = runner.rfind('TAB 4:')
print("Last TAB 4: at:", idx_tab4_last)
