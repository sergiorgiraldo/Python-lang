import os
import datetime
import subprocess

repo_path = "/Users/GK47LX/source/tst3/"  
file_path = os.path.join(repo_path, "log.txt")

os.chdir(repo_path)

for i in range(5):
    print(f"\n******** Entry {i+1} ********")
    with open(file_path, "a") as f:
        f.write(f"Entry {i+1}: {datetime.date.today()}\n")

    subprocess.run(["git", "add", "log.txt"])
    subprocess.run(["git", "commit", "-m", f"Add entry {i+1} on {datetime.date.today()}"])
    subprocess.run(["git", "push"])

print("Done.")
