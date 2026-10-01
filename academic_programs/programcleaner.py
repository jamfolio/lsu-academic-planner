import os
from bs4 import BeautifulSoup

os.makedirs("junk_programs", exist_ok=True)

files_moved = 0

for filename in os.listdir("programs"):
    path = f"programs/{filename}"

    if not filename.endswith(".html"):
        continue

    with open(f"programs/{filename}", "r", encoding="utf-8", errors="replace") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    acalog_div = soup.find(class_="acalog-core")
    program_desc = soup.find(class_="program_description")

    if acalog_div is None and program_desc is None:
        print(filename)
        os.rename(path, f"junk_programs/{filename}")
        files_moved = files_moved + 1

print(f"There were {files_moved} files moved")
