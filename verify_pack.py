import os
import hashlib

pack_dir = r'C:\Users\tarun\OneDrive\Desktop\round2\round2_pack'

print('=== FULL DIRECTORY TREE ===')
for root, dirs, files in os.walk(pack_dir):
    level = root.replace(pack_dir, '').count(os.sep)
    indent = ' ' * 4 * level
    rel = os.path.relpath(root, pack_dir)
    folder_name = os.path.basename(root) if rel != '.' else 'round2_pack'
    print(f'{indent}[{folder_name}]')
    subindent = ' ' * 4 * (level + 1)
    for f in sorted(files):
        print(f'{subindent}{f}')

print('\n=== SHA256 VERIFICATION ===')
manifest_path = os.path.join(pack_dir, 'SHA256SUMS.txt')
with open(manifest_path, 'r', encoding='utf-8') as f:
    manifest_lines = [line.strip() for line in f if line.strip()]

manifest = {}
for line in manifest_lines:
    parts = line.split(maxsplit=1)
    if len(parts) == 2:
        sha, relpath = parts
        manifest[relpath.replace('/', os.sep)] = sha

all_matched = True
missing = []
mismatched = []

for relpath, expected_hash in sorted(manifest.items()):
    filepath = os.path.join(pack_dir, relpath)
    if not os.path.exists(filepath):
        missing.append(relpath)
        all_matched = False
        print(f'MISSING: {relpath}')
        continue
    h = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while chunk := f.read(65536):
            h.update(chunk)
    actual_hash = h.hexdigest()
    if actual_hash.lower() == expected_hash.lower():
        print(f'OK: {relpath}')
    else:
        mismatched.append((relpath, expected_hash, actual_hash))
        all_matched = False
        print(f'MISMATCH: {relpath} (expected {expected_hash}, got {actual_hash})')

# Extra files check
pack_files = set()
for root, dirs, files in os.walk(pack_dir):
    for f in files:
        full = os.path.join(root, f)
        rel = os.path.relpath(full, pack_dir)
        if rel != 'SHA256SUMS.txt':
            pack_files.add(rel)

manifest_files = set(manifest.keys())
extra_files = pack_files - manifest_files

print('\n=== SUMMARY ===')
print(f'Total in manifest: {len(manifest)}')
print(f'Missing files: {len(missing)}')
print(f'Mismatched files: {len(mismatched)}')
print(f'Extra files: {list(extra_files)}')
if all_matched and len(missing) == 0 and len(mismatched) == 0:
    print('ALL 74 MANIFEST FILES MATCHED SHA256 EXACTLY!')

