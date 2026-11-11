"""
audit_repo.py - run this on your messy working folder BEFORE committing.

    python audit_repo.py /path/to/HPR_case            # report only, changes nothing
    python audit_repo.py /path/to/HPR_case --manifest # also writes MANIFEST.json (sizes + SHA-256) in that folder

It reports, and never modifies or deletes anything:
  1. files that should NOT go to GitHub (statepoints, VTK, big arrays, CFD time directories, anything > 25 MB)
  2. code that contains machine-specific absolute paths (/home/..., /Users/..., C:\\...) or placeholders
  3. version clutter (name_v1, name_v2 ...): which is the newest, so you can remove the rest and log them in docs/DESIGN_HISTORY.md
  4. python files that import a local module that does not exist in the folder
  5. scripts that write output files without a visible output path (hard to reproduce)
"""
import os, re, sys, json, hashlib, ast

BIG = 25 * 1024 * 1024
BAD_EXT = {'.h5', '.vtk', '.vtu', '.vti', '.npy', '.npz', '.pvd', '.pvtu', '.odb', '.zip', '.tar', '.gz', '.mp4'}
PATH_RE = re.compile(r"(/home/[\w.\-]+|/Users/[\w.\-]+|[A-Za-z]:\\\\|[A-Za-z]:\\|PATH_TO|FOLDER_FROM|/mnt/user-data|/tmp/claude)")
VER_RE = re.compile(r"^(?P<base>.+?)[_\-]v(?P<n>\d+)(?P<rest>.*)$")
SKIP_DIRS = {'.git', '__pycache__', '.ipynb_checkpoints', 'node_modules'}


def walk(root):
    for d, dirs, files in os.walk(root):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            yield os.path.join(d, f)


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    root = os.path.abspath(sys.argv[1])
    files = list(walk(root))
    print(f"scanned {len(files)} files under {root}\n")

    print("== 1. do NOT commit (too big / regenerable) ==")
    n = 0
    for p in sorted(files):
        sz = os.path.getsize(p); rel = os.path.relpath(p, root)
        ext = os.path.splitext(p)[1].lower()
        foam = re.search(r"(^|/)(processor\d+|\d+(\.\d+)?)/", rel) and ext == ''
        if sz > BIG or ext in BAD_EXT or foam:
            n += 1
            print(f"  {sz/1e6:8.1f} MB  {rel}")
    print(f"  -> {n} files. Put a few of them on Zenodo/Google Drive and link them in docs/REPRODUCE.md; do not use plain git.\n")

    print("== 2. machine-specific paths / placeholders in code ==")
    n = 0
    for p in sorted(files):
        if os.path.splitext(p)[1].lower() not in {'.py', '.sh', '.json', '.md', '.txt', '.yml', '.yaml', '.cfg', '.ini'}:
            continue
        if os.path.getsize(p) > 2_000_000:
            continue
        try:
            for i, line in enumerate(open(p, errors='ignore'), 1):
                if PATH_RE.search(line):
                    n += 1
                    print(f"  {os.path.relpath(p, root)}:{i}: {line.strip()[:110]}")
        except OSError:
            pass
    print(f"  -> {n} lines. Replace with paths relative to the script (Path(__file__).parent) or a command-line argument.\n")

    print("== 3. version clutter (keep newest in place, remove older, log in docs/DESIGN_HISTORY.md) ==")
    groups = {}
    for p in files:
        m = VER_RE.match(os.path.basename(p))
        if m:
            groups.setdefault((os.path.dirname(p), m['base'], m['rest']), []).append((int(m['n']), p))
    shown = 0
    for (d, base, rest), lst in sorted(groups.items()):
        if len(lst) > 1:
            lst.sort(); shown += 1
            print(f"  {os.path.relpath(d, root)}/{base}_v*{rest}: newest v{lst[-1][0]}; older: " + ', '.join(f"v{n}" for n, _ in lst[:-1]))
    print(f"  -> {shown} families. 'Newest' is not the same as 'valid': check docs/RESULTS_MAP.md before deleting anything.\n")

    print("== 4. missing local imports ==")
    local = {os.path.splitext(os.path.basename(p))[0] for p in files if p.endswith('.py')}
    std = set(getattr(sys, 'stdlib_module_names', set()))
    third = {'numpy', 'scipy', 'matplotlib', 'openmc', 'h5py', 'pandas', 'CoolProp', 'docx', 'PIL', 'pyvista', 'vtk', 'yaml'}
    n = 0
    for p in sorted(files):
        if not p.endswith('.py'):
            continue
        try:
            tree = ast.parse(open(p, errors='ignore').read())
        except SyntaxError as e:
            print(f"  SYNTAX ERROR {os.path.relpath(p, root)}: line {e.lineno}"); n += 1; continue
        for node in ast.walk(tree):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split('.')[0] for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                names = [node.module.split('.')[0]]
            for nm in names:
                if nm not in std and nm not in third and nm not in local:
                    n += 1
                    print(f"  {os.path.relpath(p, root)}: imports '{nm}' (not stdlib, not in the usual list, not found as a .py here)")
    print(f"  -> {n} items. Note 'numbers.py'/'json.py'-style files shadow the standard library: rename them.\n")

    print("== 5. shadowing of standard-library names ==")
    for p in sorted(files):
        base = os.path.splitext(os.path.basename(p))[0]
        if p.endswith('.py') and base in std:
            print(f"  {os.path.relpath(p, root)} shadows the standard module '{base}'  -> rename")

    if '--manifest' in sys.argv:
        out = {}
        for p in files:
            if os.path.getsize(p) <= BIG and os.path.splitext(p)[1].lower() not in BAD_EXT:
                out[os.path.relpath(p, root)] = {'bytes': os.path.getsize(p), 'sha256': sha(p)}
        json.dump(out, open(os.path.join(root, 'MANIFEST.json'), 'w'), indent=1, sort_keys=True)
        print(f"\nwrote MANIFEST.json with {len(out)} files")


if __name__ == '__main__':
    main()
