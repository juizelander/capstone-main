lines = open('c:\\Users\\Justin Lorenz\\Downloads\\capstone-main\\tab_log.txt').readlines()
first_drops = {}
for line in lines:
    if 'Global balance drops to' in line:
        val = int(line.split('drops to ')[1].split(' at')[0])
        if val not in first_drops:
            first_drops[val] = line.strip()

log = open('c:\\Users\\Justin Lorenz\\Downloads\\capstone-main\\tab_drops.txt', 'w')
for k, v in first_drops.items():
    log.write(f'{v}\n')
log.close()
