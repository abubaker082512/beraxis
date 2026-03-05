import os
import glob

def replace_in_files(directory):
    for filepath in glob.glob(directory + '/**/*.tsx', recursive=True) + glob.glob(directory + '/**/*.ts', recursive=True):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if '@/src/' in content:
            content = content.replace('@/src/', '@/')
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {filepath}")

replace_in_files(r'd:\Beraxis\src')
print("Done")
