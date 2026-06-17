import os

folders = ["data/raw", "data/processed", "scripts", "output", "docs"]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

print("✅ Project folder structure created!")
