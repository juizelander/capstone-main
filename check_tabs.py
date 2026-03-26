import re

html_path = 'c:\\Users\\Justin Lorenz\\Downloads\\capstone-main\\accounts\\templates\\accounts\\admin_dashboard.html'
with open(html_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

log = open('c:\\Users\\Justin Lorenz\\Downloads\\capstone-main\\tab_log.txt', 'w', encoding='utf-8')

balance = 0
for i, line in enumerate(lines):
    opens = len(re.findall(r'<div\b', line))
    closes = len(re.findall(r'</div\b', line))
    balance += opens - closes
    if balance < 0:
        log.write(f"Global balance drops to {balance} at line {i+1}!\n")

log.write(f"Final document div balance: {balance}\n")
log.close()
