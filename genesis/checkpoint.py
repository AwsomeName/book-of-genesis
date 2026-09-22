"""Operator-requested local snapshots; never transfers or executes a copy."""
import hashlib
import json
import shutil
import sqlite3
from pathlib import Path


def create_checkpoint(data_dir: Path, destination: Path):
    source = (data_dir / 'state.sqlite3').resolve()
    connection = sqlite3.connect(source.as_uri() + '?mode=ro', uri=True)
    created = False
    try:
        # Refuse uninitialized stores without creating an identity or changing it.
        identity = connection.execute('SELECT uuid, name FROM identity').fetchone()
        if identity is None:
            raise ValueError('No identity exists; create an identity before checkpointing.')
        destination.mkdir(mode=0o700, parents=True, exist_ok=False)
        created = True
        snapshot = destination / 'state.sqlite3'
        snapshot.touch(mode=0o600, exist_ok=False)
        target = sqlite3.connect(snapshot)
        try:
            # SQLite's backup API makes a consistent snapshot, including committed WAL data.
            connection.backup(target)
            if target.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
                raise ValueError('Snapshot integrity check failed.')
            snapshot_identity = target.execute('SELECT uuid, name FROM identity').fetchone()
        finally:
            target.close()
        manifest = {
            'format_version': 1,
            'kind': 'identity_checkpoint',
            'uuid': snapshot_identity[0],
            'name': snapshot_identity[1],
            'database_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(),
            'contains': ['state.sqlite3'],
            'creates_descendant': False,
        }
        manifest_path = destination / 'manifest.json'
        manifest_path.touch(mode=0o600, exist_ok=False)
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return {'checkpoint': str(destination.resolve()), **manifest}
    except Exception:
        if created:
            shutil.rmtree(destination)
        raise
    finally:
        connection.close()
