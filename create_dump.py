import subprocess

print("Creating database dump...")
with open('datadump.json', 'w', encoding='utf-8') as f:
    result = subprocess.run(
        ['python', 'manage.py', 'dumpdata', '--exclude', 'auth.permission', '--exclude', 'contenttypes'],
        stdout=f, stderr=subprocess.PIPE, text=True
    )
    if result.returncode != 0:
        print("Error creating dump:")
        print(result.stderr)
    else:
        print("Successfully created datadump.json in UTF-8")
