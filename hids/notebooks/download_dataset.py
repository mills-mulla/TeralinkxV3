#!/usr/bin/env python3
"""
Download NSL-KDD dataset for network intrusion detection training
Dataset: https://www.unb.ca/cic/datasets/nsl.html
"""
import os
import urllib.request
import gzip
import shutil

DATASET_DIR = '/home/jovyan/datasets'
os.makedirs(DATASET_DIR, exist_ok=True)

datasets = {
    'KDDTrain+.txt': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTrain%2B.txt',
    'KDDTest+.txt': 'https://raw.githubusercontent.com/defcom17/NSL_KDD/master/KDDTest%2B.txt',
}

print("Downloading NSL-KDD dataset...")

for filename, url in datasets.items():
    filepath = os.path.join(DATASET_DIR, filename)
    if os.path.exists(filepath):
        print(f"✓ {filename} already exists")
    else:
        print(f"Downloading {filename}...")
        urllib.request.urlretrieve(url, filepath)
        print(f"✓ {filename} downloaded")

print("\nDataset downloaded to:", DATASET_DIR)
print("\nFiles:")
for f in os.listdir(DATASET_DIR):
    filepath = os.path.join(DATASET_DIR, f)
    size = os.path.getsize(filepath) / (1024 * 1024)
    print(f"  - {f} ({size:.2f} MB)")
