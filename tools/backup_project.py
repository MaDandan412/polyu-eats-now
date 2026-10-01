"""Portable source backup and checksum verification; no installed packages or secrets."""
import argparse
import ctypes
from datetime import datetime, timezone, timedelta
import hashlib
import json
import os
from pathlib import Path
import shutil
from zipfile import ZipFile, ZIP_DEFLATED

PROJECT = Path(__file__).resolve().parents[1]
EXCLUDED = {'.venv', 'node_modules', '__pycache__', '.pytest_cache', '.git', '.runtime', 'backups'}
EXCLUDED_FILES = {'cloudflared.exe', 'PHONE_URL.txt', 'PHONE_PREVIEW.html', '__mobile-test.html'}


def included(path):
    parts = path.relative_to(PROJECT).parts
    return (path.is_file() and not path.is_symlink() and not EXCLUDED.intersection(parts)
            and path.name not in EXCLUDED_FILES
            and not (path.name.startswith('.env') and path.name != '.env.example')
            and path.suffix not in {'.tsbuildinfo', '.zip', '.sha256', '.pem', '.key'})


def documents_directory():
    if os.name == 'nt':
        location = ctypes.create_unicode_buffer(32768)
        if ctypes.windll.shell32.SHGetFolderPathW(None, 5, None, 0, location) == 0:
            return Path(location.value)
    return Path.home() / 'Documents'


def verify(path):
    with ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate archive entry')
        manifest = json.loads(archive.read('BACKUP_MANIFEST.json'))
        expected = set(manifest['files']) | {'BACKUP_MANIFEST.json'}
        if set(names) != expected or archive.testzip() is not None:
            raise ValueError('Archive contents or ZIP integrity mismatch')
        for name, record in manifest['files'].items():
            if name.startswith(('/', '\\')) or '..' in Path(name).parts or ':' in name:
                raise ValueError('Unsafe archive path')
            data = archive.read(name)
            if len(data) != record['bytes'] or hashlib.sha256(data).hexdigest() != record['sha256']:
                raise ValueError('Checksum mismatch: ' + name)
    return len(manifest['files'])


def create(output):
    output.mkdir(parents=True, exist_ok=True)
    created = datetime.now(timezone(timedelta(hours=8)))
    destination = output / ('polyu-eats-now-backup-' + created.strftime('%Y-%m-%d_%H%M%S_%f') + '.zip')
    manifest = {'format': 1, 'created_hong_kong': created.isoformat(),
                'repository': 'https://github.com/MaDandan412/polyu-eats-now',
                'files': {}}
    with ZipFile(destination, 'x', ZIP_DEFLATED) as archive:
        def add(name, data):
            archive.writestr(name, data)
            manifest['files'][name] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
        for file in sorted(PROJECT.rglob('*')):
            if included(file):
                add('polyu-eats-now/' + file.relative_to(PROJECT).as_posix(), file.read_bytes())
        # Whitelist public connection metadata only; never copy process IDs or credentials.
        fixed_path = PROJECT / '.runtime/fixed-phone.json'
        if fixed_path.is_file():
            fixed = json.loads(fixed_path.read_text(encoding='utf-8-sig'))
            safe = {key: fixed.get(key) for key in ('provider', 'url', 'target')}
            add('desktop-config/fixed-phone-reference.json', json.dumps(safe, ensure_ascii=False, indent=2).encode('utf-8'))
        add('RESTORE_README.md', '''# PolyU Eats Now 备份

polyu-eats-now/ 包含源码、已构建网页、测试、安装与部署配置。
阅读 polyu-eats-now/docs/RESTORE_AND_MIGRATE.md 了解恢复、自动启动和迁移。
BACKUP_MANIFEST.json 记录每个文件的 SHA-256 与长度。
运行 python polyu-eats-now/tools/backup_project.py --verify <此ZIP路径> 校验。
desktop-config/ 只供原电脑固定网址核对，不是可迁移的登录状态。
换电脑需重新安装依赖并登录自己的 Tailscale；不能保证保留旧设备网址。
备份不包含账号密码、私钥、浏览器配置、进程编号、运行日志或已安装依赖。
本备份留在你的 Documents 文件夹，不会上传到公开 GitHub 仓库。
'''.encode('utf-8'))
        archive.writestr('BACKUP_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf-8'))
    count = verify(destination)
    digest = hashlib.sha256(destination.read_bytes()).hexdigest()
    destination.with_suffix('.zip.sha256').write_text(digest + '  ' + destination.name + '\n', encoding='utf-8')
    return {'path': str(destination), 'files_verified': count, 'bytes': destination.stat().st_size, 'sha256': digest}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path)
    parser.add_argument('--verify', type=Path)
    args = parser.parse_args()
    if args.verify:
        print(json.dumps({'files_verified': verify(args.verify), 'path': str(args.verify)}, ensure_ascii=False))
    else:
        print(json.dumps(create(args.output or documents_directory() / 'PolyU Eats Now Backups'), ensure_ascii=False))


if __name__ == '__main__':
    main()
