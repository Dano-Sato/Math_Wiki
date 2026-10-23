"""Concurrency and ownership checks, isolated from real work claims."""

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

SCRIPT = Path(__file__).with_name('coordination.py').resolve()


class CoordinationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='math-wiki-claims-')
        self.root = Path(self.temp.name)
        for name in ('005-example','008-example'):
            (self.root/'conjectures'/name).mkdir(parents=True)

    def tearDown(self):
        self.temp.cleanup()

    def call(self, *args, expected=0):
        result = subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),*args],
                                capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(result.returncode,expected,(result.stdout,result.stderr))
        return json.loads(result.stdout if result.returncode == 0 else result.stderr)

    def claim(self, *items, owner='worker'):
        return self.call('claim',*items,'--owner',owner,'--task','test work')

    def test_same_id_concurrent_claim_has_one_winner(self):
        def attempt(i):
            result = subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),
                                     'claim','005','--owner',f'worker-{i}','--task','parallel'],
                                    capture_output=True,text=True,encoding='utf-8')
            return result
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(attempt,range(16)))
        self.assertEqual(sum(r.returncode == 0 for r in results),1)
        self.assertTrue(all(r.returncode in (0,2) for r in results))
        status = self.call('status')
        self.assertEqual(len(status['claims']),1)
        self.assertIn(status['claims'][0]['owner'],(self.root/'OCCUPANCY.md').read_text(encoding='utf-8'))

    def test_new_numbers_concurrent_unique_and_never_reused(self):
        def reserve(i):
            return self.call('new','--owner',f'creator-{i}','--task','new conjecture')
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(reserve,range(8)))
        numbers = sorted(r['resources'][0] for r in results)
        self.assertEqual(numbers,[f'{n:03d}' for n in range(9,17)])
        first = results[0]
        self.call('release',*first['resources'],'--token',first['token'],'--note','cancelled')
        self.assertEqual(self.call('new','--owner','next','--task','next')['resources'],['017'])

    def test_batch_conflict_rolls_back_everything(self):
        self.claim('008',owner='first')
        self.call('claim','005','008','--owner','second','--task','batch',expected=2)
        self.assertEqual([r['resource'] for r in self.call('status')['claims']],['008'])

    def test_tokens_and_batch_release_are_atomic(self):
        first = self.claim('005',owner='same-name')
        second = self.claim('008',owner='same-name')
        self.call('release','005','008','--token',first['token'],expected=2)
        self.assertEqual(len(self.call('status')['claims']),2)
        self.call('heartbeat','005','--token',second['token'],expected=2)
        self.call('heartbeat','005','--token',first['token'])
        self.call('release','005','--token',first['token'])
        status = self.call('status')
        self.assertEqual([r['resource'] for r in status['claims']],['008'])
        self.assertNotIn(second['token'],json.dumps(status))
        self.assertNotIn(second['token'],(self.root/'OCCUPANCY.md').read_text(encoding='utf-8'))

    def test_root_is_exclusive_but_does_not_block_number(self):
        self.claim('ROOT',owner='shared-writer')
        self.claim('005',owner='reviewer')
        self.call('claim','ROOT','--owner','other','--task','collision',expected=2)
        self.assertEqual(len(self.call('status')['claims']),2)

    def test_old_claim_is_not_expired_and_recovery_is_audited(self):
        self.claim('005')
        with sqlite3.connect(self.root/'.coordination'/'state.sqlite3') as db:
            db.execute("UPDATE claims SET updated_at='2000-01-01T00:00:00+00:00'")
        self.assertEqual(len(self.call('status')['claims']),1)
        self.call('force-release','005','--reason','user confirmed old worker ended')
        self.assertEqual(self.call('status')['claims'],[])
        history = self.call('history')['events']
        self.assertEqual(history[0]['action'],'force-release')
        self.assertIn('user confirmed',history[0]['detail'])

    def test_numeric_aliases_and_missing_folder(self):
        result = self.claim('5','005')
        self.assertEqual(result['resources'],['005'])
        self.call('claim','012','--owner','other','--task','unreserved',expected=2)


if __name__ == '__main__':
    unittest.main()
