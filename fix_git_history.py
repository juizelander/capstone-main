import subprocess

def run(cmd):
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.stdout

def fix_git():
    with open("git_fix_log.txt", "w") as log:
        def log_run(cmd):
            res = run(cmd)
            log.write(f"\n--- {cmd} ---\n{res}\n")
            return res

        # 1. Check status
        log_run("git status")
        
        # 2. Check log ahead of origin
        history = log_run("git log --oneline origin/stizzzy..HEAD")
        
        # 3. Soft reset to origin/stizzzy
        log_run("git reset --soft origin/stizzzy")
        
        # 4. Make sure setting.py is added and has no secret
        # First ensure the working tree version doesn't have the secret!
        with open("capstone/settings.py", "r") as f:
            content = f.read()
            if "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" in content:
                log.write("SECRET FOUND IN WORKING TREE! REPLACING IT...")
                content = content.replace("'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'", "''")
                with open("capstone/settings.py", "w") as fw:
                    fw.write(content)
        
        log_run("git add capstone/settings.py")
        
        # 5. Commit
        log_run("git commit -m 'feat: implement chatbot fallback, fix application bugs, removed secret'")
        
        # 6. Check log again
        log_run("git log --oneline -n 3")

fix_git()
