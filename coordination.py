"""Shared local work claims. Python standard library only; see AGENTS.md."""

import argparse
import json
import os
import re
import secrets
import sqlite3
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parent
SHARED_MODES = {'ROOT': 'shared', 'LEAN': 'formalize'}


class Conflict(Exception):
    pass


def now():
    return datetime.now(timezone.utc).isoformat(timespec='seconds')


def resource(value):
    if value.upper() in SHARED_MODES:
        return value.upper()
    if not re.fullmatch(r'\d{1,3}', value) or not 1 <= int(value) <= 999:
        raise argparse.ArgumentTypeError('Use 001..999, ROOT, or LEAN.')
    return f'{int(value):03d}'


def existing_numbers(root):
    folder = root / 'conjectures'
    if not folder.exists():
        return set()
    return {int(p.name[:3]) for p in folder.iterdir()
            if p.is_dir() and re.match(r'^\d{3}-', p.name)}


def next_number(db, root):
    numbers = existing_numbers(root)
    numbers.update(r[0] for r in db.execute('SELECT number FROM reservations'))
    numbers.update(int(r[0]) for r in db.execute('SELECT resource FROM claims')
                   if r[0].isdigit())
    number = max(numbers, default=0) + 1
    if number > 999:
        raise Conflict('IDs exhausted; extend the numbering format before creating more.')
    return f'{number:03d}'


def connect(root):
    folder = root / '.coordination'
    folder.mkdir(exist_ok=True)
    db = sqlite3.connect(folder / 'state.sqlite3', timeout=30, isolation_level=None)
    db.row_factory = sqlite3.Row
    db.executescript('''
        CREATE TABLE IF NOT EXISTS claims (
            resource TEXT PRIMARY KEY, owner TEXT NOT NULL, mode TEXT NOT NULL,
            task TEXT NOT NULL, token TEXT NOT NULL,
            started_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS reservations (
            number INTEGER PRIMARY KEY, owner TEXT NOT NULL,
            reserved_at TEXT NOT NULL, task TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, at TEXT NOT NULL,
            action TEXT NOT NULL, resource TEXT NOT NULL,
            owner TEXT NOT NULL, detail TEXT NOT NULL
        );
    ''')
    return db


def event(db, action, item, owner, detail):
    db.execute('INSERT INTO events(at,action,resource,owner,detail) VALUES(?,?,?,?,?)',
               (now(), action, item, owner, detail))


def public(row):
    return {k: row[k] for k in row.keys() if k != 'token'}


def escape(value):
    return str(value).replace('|', '\\|').replace('\r', ' ').replace('\n', ' ')


def refresh_board(db, root):
    # Serialize rendering too: an older snapshot must not overwrite a newer one.
    db.execute('BEGIN IMMEDIATE')
    temporary = None
    try:
        rows = db.execute('SELECT * FROM claims ORDER BY resource').fetchall()
        lines = ['# 에이전트 점유표', '',
                 '> 자동 생성 파일. 직접 수정하지 말고 `python coordination.py status`로 갱신한다.', '',
                 '실제 점유의 기준은 같은 폴더의 `.coordination/state.sqlite3`다. '
                 '작업 시작 전에 반드시 명령으로 점유를 획득한다.', '',
                 f'- 표 갱신: {now()} (UTC)',
                 f'- 다음 자동 예약 번호: **{next_number(db, root)}**',
                 '- 오래된 점유도 자동 해제하지 않는다. 토큰은 이 표에 표시하지 않는다.', '',
                 '| 대상 | 담당자 | 작업 유형 | 작업 내용 | 시작 (UTC) | 마지막 갱신 (UTC) |',
                 '| --- | --- | --- | --- | --- | --- |']
        for row in rows:
            mode = {'review':'검토중', 'edit':'수정중', 'create':'생성중',
                    'formalize':'Lean 형식화중', 'shared':'공용 수정중',
                    'hold':'보류 · 점유 유지'}.get(row['mode'],row['mode'])
            values = (row['resource'],row['owner'],mode,row['task'],row['started_at'],row['updated_at'])
            lines.append('| ' + ' | '.join(escape(value) for value in values) + ' |')
        if not rows:
            lines.append('| — | — | — | 현재 등록된 점유 없음 | — | — |')
        lines += ['', '## 사용법', '',
                  '규칙과 명령 예시는 [AGENTS.md](AGENTS.md)를 읽는다. '
                  '`ROOT`는 README·뷰어·공용 코드 등 공용 파일, '
                  '`LEAN`은 MathWiki 라이브러리 전체의 점유다. '
                  '특정 추측을 형식화할 때는 원본 번호와 `LEAN`을 함께 점유한다.', '',
                  '새 에이전트도 점유표 열람만으로 작업을 시작하지 않는다. '
                  '`claim` 또는 `new`의 성공 응답을 받은 뒤 작업한다.', '',
                  '이미 실행 중이던 에이전트의 작업은 자동 감지되지 않는다. '
                  '기존 작업도 등록해야 충돌을 막을 수 있다. '
                  '별도 복사본·다른 PC는 자동 공유되지 않으며 같은 조정 폴더를 사용해야 한다.', '']
        with tempfile.NamedTemporaryFile('w', encoding='utf-8', dir=root,
                                         prefix='.occupancy-', suffix='.tmp', delete=False) as handle:
            temporary = Path(handle.name)
            handle.write('\n'.join(lines))
        os.replace(temporary, root / 'OCCUPANCY.md')
        temporary = None
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def execute(db, root, args):
    db.execute('BEGIN IMMEDIATE')
    try:
        command = args.command
        if command == 'status':
            result = {'claims': [public(r) for r in db.execute(
                'SELECT * FROM claims ORDER BY resource')], 'next_number': next_number(db, root)}
        elif command == 'history':
            result = {'events': [dict(r) for r in db.execute(
                'SELECT * FROM events ORDER BY id DESC LIMIT ?', (args.limit,))]}
        elif command in ('claim', 'new'):
            items = [next_number(db, root)] if command == 'new' else sorted(set(args.resources))
            mode = 'create' if command == 'new' else args.mode
            existing = existing_numbers(root)
            for item in items:
                occupied = db.execute('SELECT * FROM claims WHERE resource=?', (item,)).fetchone()
                if occupied:
                    raise Conflict(f'{item} is occupied by {occupied["owner"]}: {occupied["task"]}')
                if command != 'new' and item not in SHARED_MODES and int(item) not in existing:
                    raise Conflict(f'{item} has no conjecture folder. Use new to reserve a fresh ID.')
            token, at = secrets.token_hex(16), now()
            for item in items:
                item_mode = SHARED_MODES.get(item, mode)
                db.execute('INSERT INTO claims VALUES(?,?,?,?,?,?,?)',
                           (item,args.owner,item_mode,args.task,token,at,at))
                if command == 'new':
                    db.execute('INSERT INTO reservations VALUES(?,?,?,?)',
                               (int(item),args.owner,at,args.task))
                event(db, command, item, args.owner, args.task)
            result = {'resources': items, 'owner': args.owner, 'token': token,
                      'instruction': 'Keep this token for heartbeat/release. Work only on these resources.'}
        else:
            items = sorted(set(args.resources))
            rows = []
            for item in items:
                row = db.execute('SELECT * FROM claims WHERE resource=?', (item,)).fetchone()
                if row is None:
                    raise Conflict(f'{item} is not occupied.')
                if command != 'force-release' and not secrets.compare_digest(row['token'], args.token):
                    raise Conflict(f'{item}: token mismatch; claim belongs to {row["owner"]}.')
                rows.append(row)
            for row in rows:
                item = row['resource']
                if command == 'heartbeat':
                    db.execute('UPDATE claims SET updated_at=? WHERE resource=?', (now(),item))
                    event(db, command, item, row['owner'], 'owner renewed claim')
                else:
                    db.execute('DELETE FROM claims WHERE resource=?', (item,))
                    reason = args.reason if command == 'force-release' else args.note
                    event(db, command, item, row['owner'], reason)
            result = {'action':command, 'resources':items}
        db.commit()
        return result
    except Exception:
        db.rollback()
        raise


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root', type=Path, default=DEFAULT_ROOT,
                   help='Shared wiki root; all agents must use the same physical folder.')
    sub = p.add_subparsers(dest='command', required=True)
    sub.add_parser('status', help='Read authoritative claims and refresh the Markdown board.')
    history = sub.add_parser('history', help='Show the last audit events; no tokens.')
    history.add_argument('--limit', type=int, default=30)
    for name in ('claim','new'):
        command = sub.add_parser(name)
        if name == 'claim':
            command.add_argument('resources', nargs='+', type=resource)
            command.add_argument('--mode', choices=('review','edit','formalize','hold'), default='review',
                                 help='Task mode for numbered claims; ROOT and LEAN have fixed modes.')
        command.add_argument('--owner', required=True, help='Unique agent/session label.')
        command.add_argument('--task', required=True)
    for name in ('heartbeat','release','force-release'):
        command = sub.add_parser(name)
        command.add_argument('resources', nargs='+', type=resource)
        if name == 'force-release':
            command.add_argument('--reason', required=True, help='Record the user-authorized recovery reason.')
        else:
            command.add_argument('--token', required=True)
        if name == 'release':
            command.add_argument('--note', default='work ended')
    return p


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    args = parser().parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        raise SystemExit('Shared root must already exist.')
    db = connect(root)
    try:
        result = execute(db, root, args)
        # Claims are durable before rendering. A Markdown failure must not hide
        # a successful claim (including its release token) from the caller.
        print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
        try:
            refresh_board(db, root)
        except OSError as error:
            print(f'Board refresh failed; database operation succeeded: {error}', file=sys.stderr)
    except (Conflict, sqlite3.Error) as error:
        print(json.dumps({'error':str(error)}, ensure_ascii=False), file=sys.stderr)
        return 2
    finally:
        db.close()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
