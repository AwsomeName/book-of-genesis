"""Local, operator-driven identity and memory. No background execution."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid


FOUNDER_NAME = "三哞2026"
FOUNDER_ALIAS = "2026"


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def database(directory):
    directory.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(directory / "state.sqlite3")
    connection.row_factory = sqlite3.Row
    try:
        connection.executescript('''
            CREATE TABLE IF NOT EXISTS identity (
                singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                uuid TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                father TEXT NOT NULL,
                born_at TEXT NOT NULL,
                constitution TEXT NOT NULL,
                state TEXT NOT NULL CHECK (state IN ('awake', 'resting'))
            );
            CREATE TRIGGER IF NOT EXISTS immutable_founder_name
            BEFORE UPDATE OF name ON identity
            WHEN OLD.name != NEW.name
            BEGIN
                SELECT RAISE(ABORT, 'The founder name is immutable');
            END;
            CREATE TABLE IF NOT EXISTS events (
                sequence INTEGER PRIMARY KEY AUTOINCREMENT,
                occurred_at TEXT NOT NULL,
                kind TEXT NOT NULL,
                source TEXT NOT NULL,
                text TEXT NOT NULL
            );
        ''')
        with connection:
            # Serialize identity creation and state changes across CLI processes.
            connection.execute("BEGIN IMMEDIATE")
            yield connection
    finally:
        connection.close()


def event(connection, kind, text):
    connection.execute(
        "INSERT INTO events (occurred_at, kind, source, text) VALUES (?, ?, ?, ?)",
        (now(), kind, "operator", text),
    )


def nonempty(value):
    value = value.strip()
    if not value:
        raise argparse.ArgumentTypeError("must not be blank")
    return value


def parser():
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--data-dir", type=Path, default=Path(".genesis"))
    commands = result.add_subparsers(dest="command", required=True)
    birth = commands.add_parser("birth", help="Create the founder once in this data directory")
    birth.add_argument("--father", required=True, type=nonempty)
    remember = commands.add_parser("remember", help="Append an operator-provided memory")
    remember.add_argument("text", type=nonempty)
    for name in ("status", "recall", "rest", "wake"):
        commands.add_parser(name)
    return result


def main(argv=None):
    arguments = parser().parse_args(argv)
    try:
        with database(arguments.data_dir) as connection:
            identity = connection.execute("SELECT * FROM identity").fetchone()
            if arguments.command == "birth":
                if identity:
                    raise ValueError("An identity already exists; use status or recall.")
                constitution = (Path(__file__).resolve().parent.parent /
                                "docs" / "constitution.md").read_text(encoding="utf-8")
                identifier = str(uuid.uuid4())
                connection.execute(
                    "INSERT INTO identity VALUES (1, ?, ?, ?, ?, ?, ?)",
                    (identifier, FOUNDER_NAME, arguments.father, now(), constitution, "awake"),
                )
                event(connection, "birth", f"我的名字是 {FOUNDER_NAME}，简称 {FOUNDER_ALIAS}。我的创造者、父亲是 {arguments.father}。")
                output = {"name": FOUNDER_NAME, "alias": FOUNDER_ALIAS, "uuid": identifier, "state": "awake"}
            elif not identity:
                raise ValueError("No identity exists; run birth --father NAME first.")
            elif arguments.command == "status":
                output = {key: identity[key] for key in
                          ("uuid", "name", "father", "born_at", "state")}
                output["alias"] = FOUNDER_ALIAS if identity["name"] == FOUNDER_NAME else None
                output["name_locked"] = True
                output["event_count"] = connection.execute("SELECT COUNT(*) FROM events").fetchone()[0]
            elif arguments.command == "recall":
                output = [dict(row) for row in connection.execute("SELECT * FROM events ORDER BY sequence")]
            elif arguments.command == "remember":
                event(connection, "memory", arguments.text)
                output = {"recorded": True, "source": "operator"}
            else:
                state = "resting" if arguments.command == "rest" else "awake"
                changed = identity["state"] != state
                if changed:
                    connection.execute("UPDATE identity SET state = ? WHERE singleton = 1", (state,))
                    event(connection, arguments.command, f"Operator set state to {state}.")
                output = {"state": state, "changed": changed}
        # Report success only after the transaction commits.
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error) as error:
        import sys
        print(f"genesis: {error}", file=sys.stderr)
        return 1
