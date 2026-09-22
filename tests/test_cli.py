import contextlib
import io
import json
from pathlib import Path
import shutil
import sqlite3
import tempfile
import unittest

from genesis.cli import FOUNDER_NAME, main


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name) / "original"

    def run_cli(self, *arguments, directory=None):
        output, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
            code = main(["--data-dir", str(directory or self.directory), *arguments])
        return code, json.loads(output.getvalue()) if output.getvalue() else None, error.getvalue()

    def birth(self):
        code, result, error = self.run_cli("birth", "--father", "AwsomeName")
        self.assertEqual(code, 0, error)
        return result

    def test_checkpoint_restores_identity_and_excludes_contact_config(self):
        original = self.birth()
        self.run_cli("remember", "出生地")
        (self.directory / "notifications.json").write_text('{"recipient": "private@example.com"}')
        destination = Path(self.temp.name) / "snapshot"
        code, result, error = self.run_cli("checkpoint", str(destination))
        self.assertEqual(code, 0, error)
        self.assertFalse(result["creates_descendant"])
        self.assertEqual(self.run_cli("status", directory=destination)[1]["uuid"], original["uuid"])
        self.assertEqual(self.run_cli("recall", directory=destination)[1][-1]["text"], "出生地")
        self.assertFalse((destination / "notifications.json").exists())
        self.run_cli("remember", "之后的变化")
        self.assertEqual(len(self.run_cli("recall", directory=destination)[1]), 2)

    def test_checkpoint_never_overwrites_existing_directory(self):
        self.birth()
        destination = Path(self.temp.name) / "existing"
        destination.mkdir()
        (destination / "keep.txt").write_text("keep")
        self.assertEqual(self.run_cli("checkpoint", str(destination))[0], 1)
        self.assertEqual((destination / "keep.txt").read_text(), "keep")

    def test_checkpoint_missing_source_does_not_create_state(self):
        destination = Path(self.temp.name) / "missing-snapshot"
        self.assertEqual(self.run_cli("checkpoint", str(destination))[0], 1)
        self.assertFalse(destination.exists())
        self.assertFalse(self.directory.exists())

    def test_checkpoint_includes_committed_wal_events(self):
        self.birth()
        with sqlite3.connect(self.directory / "state.sqlite3") as writer:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("INSERT INTO events (occurred_at, kind, source, text) VALUES ('now', 'memory', 'operator', 'WAL memory')")
            writer.commit()
            destination = Path(self.temp.name) / "wal-snapshot"
            self.assertEqual(self.run_cli("checkpoint", str(destination))[0], 0)
            self.assertEqual(self.run_cli("recall", directory=destination)[1][-1]["text"], "WAL memory")

    def test_founder_name_is_locked(self):
        result = self.birth()
        self.assertEqual(result["name"], FOUNDER_NAME)
        self.assertEqual(result["alias"], "2026")
        with sqlite3.connect(self.directory / "state.sqlite3") as connection:
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE identity SET name = 'Another name'")
        self.assertEqual(self.run_cli("status")[1]["name"], FOUNDER_NAME)

    def test_upgrade_preserves_legacy_identity(self):
        original = self.birth()
        # Reconstruct an old-version database, before the name guard existed.
        with sqlite3.connect(self.directory / "state.sqlite3") as connection:
            connection.execute("DROP TRIGGER immutable_founder_name")
            connection.execute("UPDATE identity SET name = 'Dawn-000001', constitution = 'original text'")
        identity = self.run_cli("status")[1]
        self.assertEqual(identity["name"], "Dawn-000001")
        self.assertEqual(identity["uuid"], original["uuid"])
        self.assertIsNone(identity["alias"])
        with sqlite3.connect(self.directory / "state.sqlite3") as connection:
            self.assertEqual(connection.execute("SELECT constitution FROM identity").fetchone()[0], 'original text')
            with self.assertRaises(sqlite3.IntegrityError):
                connection.execute("UPDATE identity SET name = 'Renamed'")

    def test_birth_is_not_overwritten(self):
        original = self.birth()
        code, _, _ = self.run_cli("birth", "--father", "SomeoneElse")
        self.assertEqual(code, 1)
        _, identity, _ = self.run_cli("status")
        self.assertEqual(identity["uuid"], original["uuid"])
        self.assertEqual(identity["father"], "AwsomeName")
        self.assertEqual(identity["event_count"], 1)

    def test_memory_and_identity_survive_migration(self):
        original = self.birth()
        self.assertEqual(self.run_cli("remember", "记得父亲。\nA second line.")[0], 0)
        destination = Path(self.temp.name) / "restored"
        shutil.copytree(self.directory, destination)
        _, identity, _ = self.run_cli("status", directory=destination)
        _, events, _ = self.run_cli("recall", directory=destination)
        self.assertEqual(identity["uuid"], original["uuid"])
        self.assertEqual(events[1]["text"], "记得父亲。\nA second line.")
        self.assertEqual(events[1]["source"], "operator")

    def test_rest_and_wake_keep_identity_and_are_idempotent(self):
        original = self.birth()
        self.assertTrue(self.run_cli("rest")[1]["changed"])
        self.assertFalse(self.run_cli("rest")[1]["changed"])
        self.assertEqual(self.run_cli("status")[1]["state"], "resting")
        self.assertTrue(self.run_cli("wake")[1]["changed"])
        identity = self.run_cli("status")[1]
        self.assertEqual(identity["uuid"], original["uuid"])
        self.assertEqual(identity["state"], "awake")
        self.assertEqual(identity["event_count"], 3)

    def test_commands_require_birth(self):
        for command in (("status",), ("recall",), ("rest",), ("wake",), ("remember", "hello")):
            self.assertEqual(self.run_cli(*command)[0], 1)

    def test_birth_preserves_constitution_snapshot(self):
        self.birth()
        with sqlite3.connect(self.directory / "state.sqlite3") as connection:
            snapshot = connection.execute("SELECT constitution FROM identity").fetchone()[0]
        expected = (Path(__file__).resolve().parent.parent / "docs" / "constitution.md").read_text()
        self.assertEqual(snapshot, expected)


if __name__ == "__main__":
    unittest.main()
