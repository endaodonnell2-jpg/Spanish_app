import os
import sys

print("\n" + "="*30)
print("COLAB TUTOR DEBUGGER")
print("="*30)

print(f"\n[!] CURRENT WORKING DIRECTORY:\n{os.getcwd()}")

print("\n[!] PYTHON PATH (Where Python looks for modules):")
for p in sys.path:
    print(f" - {p}")

print("\n[!] FULL FILE TREE (Excluding env/git):")
def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        # Ignore hidden folders and virtual envs to keep logs clean
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != 'venv' and d != '__pycache__']
        
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print(f'{subindent}{f}')

list_files(os.getcwd())
print("="*30 + "\n")
