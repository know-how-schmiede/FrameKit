"""Build and verify the portable FrameKit distribution (standard library only)."""
import argparse
import ast
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
STAMP = (2026, 1, 1, 0, 0, 0)
EXTENSIONS = {'.py', '.manifest', '.svg', '.png', '.step', '.html', '.js', '.css'}
REQUIRED = {'FrameKit/FrameKit.py', 'FrameKit/FrameKit.manifest', 'FrameKit/version.py',
            'FrameKit/AddInIcon.svg', 'FrameKit/lib/fusionAddInUtils/__init__.py',
            'FrameKit/commands/commandDialog/entry.py', 'FrameKit/templates.py',
            'FrameKit/resources/FrameKit-Logo-240.png', 'LICENSE',
            'docu/installation_abnahme.md', 'examples/FrameKit-Beispiele.json',
            'examples/README.md', 'installer/package.py'}
for module in ('accessories', 'bill_of_materials', 'bracket_library', 'config', 'connections',
               'csv_export', 'cut_list', 'demo', 'dialog_status', 'dxf_profile', 'editing',
               'geometry', 'model', 'preview', 'preview_camera', 'preview_data',
               'profile_geometry', 'profile_library', 'sections', 'settings'):
    REQUIRED.add(f'FrameKit/{module}.py')
REQUIRED.update({'FrameKit/commands/__init__.py', 'FrameKit/commands/commandDialog/__init__.py',
                 'FrameKit/lib/fusionAddInUtils/event_utils.py',
                 'FrameKit/lib/fusionAddInUtils/general_utils.py'})
for size in (20, 30, 40):
    REQUIRED.add(f'FrameKit/resources/brackets/Winkel_{size}x{size}.step')
for icon in ('CreateFrame', 'EditFrame', 'ExportCSV', 'ProfileLibrary'):
    for size in (16, 32):
        for suffix in ('', '-dark_blue'):
            REQUIRED.add(f'FrameKit/resources/{icon}/{size}x{size}{suffix}.svg')


def digest(data):
    return hashlib.sha256(data).hexdigest()


def version(files):
    tree = ast.parse(files['FrameKit/version.py'].decode('utf-8-sig'))
    value = next(ast.literal_eval(node.value) for node in tree.body
                 if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == '__version__' for t in node.targets))
    manifest = json.loads(files['FrameKit/FrameKit.manifest'])
    if manifest['version'] != value or manifest['type'] != 'addin' or manifest['autodeskProduct'] != 'Fusion':
        raise ValueError('Manifest and version.py do not agree.')
    return value


def validate(files):
    missing = REQUIRED - files.keys()
    if missing:
        raise ValueError('Missing package files: '+', '.join(sorted(missing)))
    for name, data in files.items():
        path = PurePosixPath(name)
        if (path.is_absolute() or '..' in path.parts or '\\' in name or ':' in name
                or name != path.as_posix() or '__pycache__' in path.parts
                or path.suffix in ('.pyc', '.pyo') or '.git' in path.parts):
            raise ValueError('Invalid package path: '+name)
        if path.name in ('settings.json', 'accessories.json', 'templates.json'):
            raise ValueError('Personal user data must not be packaged: '+name)
        if not data:
            # Empty Python package initializers are valid.
            if path.name != '__init__.py':
                raise ValueError('Empty package file: '+name)
        if path.suffix == '.py':
            compile(data, name, 'exec')
    return version(files)


def collect(root=ROOT):
    root = Path(root)
    files = {}
    source = root / 'fusion_addin' / 'FrameKit'
    for path in sorted(source.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not package inputs: '+str(path))
        if path.is_file() and path.suffix.lower() in EXTENSIONS and '__pycache__' not in path.parts:
            files['FrameKit/'+path.relative_to(source).as_posix()] = path.read_bytes()
    for folder in ('docu', 'images', 'examples'):
        for path in sorted((root/folder).rglob('*')):
            if path.is_symlink():
                raise ValueError('Symlinks are not package inputs: '+str(path))
            if path.is_file() and path.suffix.lower() in {'.md', '.png', '.svg', '.jpg', '.json', '.dxf'}:
                files[path.relative_to(root).as_posix()] = path.read_bytes()
    for name in ('LICENSE', 'README.md', 'README.en.md', 'installer/package.py'):
        files[name] = (root/name).read_bytes()
    # Adapt source-tree documentation links to the portable ZIP layout.
    for name in list(files):
        if name.endswith('.md'):
            files[name] = files[name].decode('utf-8-sig').replace(
                'fusion_addin/FrameKit', 'FrameKit').replace(
                'tests/fixtures/synthetic_tslot_40.dxf', 'examples/synthetic_tslot_40.dxf').encode('utf-8')
    validate(files)
    return files


def verify(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive paths.')
        if sum(info.file_size for info in archive.infolist()) > 200*1024*1024:
            raise ValueError('Package exceeds 200 MB.')
        files = {name: archive.read(name) for name in names}
    index = json.loads(files.pop('PACKAGE.json'))
    current = validate(files)
    actual = {name: digest(data) for name, data in sorted(files.items())}
    if index != dict(schema=1, version=current, sha256=actual):
        raise ValueError('Package inventory or SHA-256 mismatch.')
    return current, len(files)


def build(output=None, root=ROOT):
    files = collect(root)
    current = version(files)
    files['PACKAGE.json'] = (json.dumps(dict(schema=1, version=current,
        sha256={name: digest(data) for name, data in sorted(files.items())}),
        indent=2, sort_keys=True)+'\n').encode('utf-8')
    output = Path(output) if output else Path(root)/'dist'/f'FrameKit-{current}.zip'
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=output.parent, suffix='.zip', delete=False) as stream:
        temporary = Path(stream.name)
    try:
        # Stored entries also avoid compression-library version differences.
        with zipfile.ZipFile(temporary, 'w', compression=zipfile.ZIP_STORED) as archive:
            for name, data in sorted(files.items()):
                info = zipfile.ZipInfo(name, STAMP)
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                archive.writestr(info, data)
        verify(temporary)
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    output.with_suffix('.zip.sha256').write_text(digest(output.read_bytes())+'  '+output.name+'\n', encoding='ascii')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', type=Path, help='Verify an existing ZIP without extracting it')
    parser.add_argument('--output', type=Path, help='Build to this ZIP path')
    args = parser.parse_args()
    if args.verify:
        current, count = verify(args.verify)
        print(f'OK: FrameKit {current}, {count} files, inventory and hashes verified')
    else:
        print(build(args.output))
