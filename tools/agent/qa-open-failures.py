"""QA 1 ledger-aware triage sweep.

Cross-checks every non-Accepted record in a result file against the ledger
(state/accepted.json, the authoritative record of what the judge has accepted)
and reports each one as OPEN or HISTORY.

Submission ids increase over time, so a failure is only dismissed as HISTORY when
the ledger's accepted submission id is GREATER than the failure's. A failure with
no ledger entry, or with a ledger entry older than the failure, is OPEN - that
ordering rule is what stops a fresh regression from being written off as history.

Usage:
  python qa-open-failures.py [<result.json> ...]        (default: all submit*result*.json)
"""
import sys

sys.dont_write_bytecode = True

import glob
import json
import os

FETCH = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
LEDGER = os.path.join(FETCH, 'accepted.json')


def load_json(path):
    with open(path, encoding='utf-8') as handle:
        return json.load(handle)


def records_of(path):
    data = load_json(path)
    if isinstance(data, dict):
        data = data.get('results') or data.get('records') or []
    return data if isinstance(data, list) else []


def classify(record, ledger):
    """Return (verdict, detail) for one non-Accepted record."""
    slug = record.get('slug')
    entry = ledger.get(slug)
    failure_id = record.get('submissionId')
    if not entry or entry.get('statusMsg') != 'Accepted':
        return 'OPEN', 'no Accepted record in the ledger'
    accepted_id = entry.get('submissionId')
    if failure_id and accepted_id and isinstance(accepted_id, int) and accepted_id > failure_id:
        return 'HISTORY', (f"ledger Accepted id {accepted_id} "
                           f"({entry.get('totalCorrect')}/{entry.get('totalTestcases')}, "
                           f"checkedAt {entry.get('checkedAt')}) is newer than failing id {failure_id}")
    if failure_id and accepted_id and isinstance(accepted_id, int) and accepted_id < failure_id:
        return 'OPEN', (f"ledger Accepted id {accepted_id} is OLDER than failing id {failure_id} "
                        f"- possible regression after the last accepted submission")
    return 'OPEN', (f"ledger Accepted id {accepted_id} could not be ordered against "
                    f"failing id {failure_id}; treat as open")


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.join(FETCH, 'submit*result*.json')))
    ledger = load_json(LEDGER)
    report = {}
    open_items = []
    for path in paths:
        if not os.path.exists(path):
            print(f'!! missing {path}')
            continue
        records = records_of(path)
        bad = [r for r in records if r.get('statusMsg') not in (None, 'Accepted')]
        print('=' * 72)
        print(f'{os.path.basename(path)}: {len(records)} records, {len(bad)} non-Accepted')
        for record in bad:
            verdict, detail = classify(record, ledger)
            print(f"  {verdict:<8} {record.get('slug'):<45} {record.get('statusMsg')} "
                  f"{record.get('totalCorrect')}/{record.get('totalTestcases')}")
            print(f"           {detail}")
            report.setdefault(record.get('slug'), []).append(
                {'file': os.path.basename(path), 'statusMsg': record.get('statusMsg'),
                 'submissionId': record.get('submissionId'), 'verdict': verdict, 'detail': detail})
            if verdict == 'OPEN':
                open_items.append(record.get('slug'))
    print('=' * 72)
    if open_items:
        print(f'OPEN items needing a repair brief: {sorted(set(open_items))}')
    else:
        print('No OPEN items: every non-Accepted record is superseded by a newer Accepted '
              'submission in the ledger (or there were no non-Accepted records).')
    out = os.path.join(FETCH, 'qa-sweep.json')
    with open(out, 'w', encoding='utf-8') as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write('\n')
    print(f'wrote {out}')
    return 1 if open_items else 0


if __name__ == '__main__':
    sys.exit(main())
