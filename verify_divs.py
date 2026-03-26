import re

html_code = open('c:\\Users\\Justin Lorenz\\Downloads\\capstone-main\\accounts\\templates\\accounts\\admin_dashboard.html', 'r', encoding='utf-8').read()

balance = 0
in_tab = False
tab_id = None
tab_balances = {}

lines = html_code.split('\n')
for i, line in enumerate(lines):
    # count open divs and close divs
    opens = len(re.findall(r'<div\b', line))
    closes = len(re.findall(r'</div\b', line))
    
    # check tab start
    if '<div' in line and 'class="tab-content' in line:
        m = re.search(r'id="([^"]+)"', line)
        if m:
            tab_id = m.group(1)
            in_tab = True
            tab_balances[tab_id] = 0
            # Since the tab started on this line, starting balance is opens - closes
            tab_balances[tab_id] = opens - closes
            balance += opens - closes
            continue
            
    balance += opens - closes
    
    if in_tab:
        tab_balances[tab_id] += opens - closes
        if tab_balances[tab_id] == 0:
            print(f"Tab {tab_id} closed at line {i+1}")
            in_tab = False
        elif tab_balances[tab_id] < 0:
            print(f"Tab {tab_id} OVER-CLOSED at line {i+1} with balance {tab_balances[tab_id]}")
            in_tab = False

print(f"Final document div balance: {balance}")
for k, v in tab_balances.items():
    if v > 0:
        print(f"Tab {k} is LEAVING OPENS with balance {v}")
