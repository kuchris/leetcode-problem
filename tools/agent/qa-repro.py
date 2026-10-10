"""QA 1 triage reproducer: run a judge lastTestcase against the saved solution.

Usage:
  python qa-repro.py <slug> --case "[1,2,4]\n[1,3,4]" [--expect "[1,1,2,3,4,4]"]
  python qa-repro.py <slug> --from-result <submit-wave*-result.json>
  python qa-repro.py <slug> --from-result <file> --time          (also reports wall time)

Detects ListNode / list[ListNode] / TreeNode parameters from the problem's
official python3 snippet annotation, converts inputs and outputs, prints the
observed value, the exception with its line number, and the comparison.
Read-only for the repo (sys.dont_write_bytecode).
"""
import sys

sys.dont_write_bytecode = True

import importlib.util
import inspect
import json
import os
import time
import traceback

FETCH = os.environ.get('LC_STATE') or os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'state')
REPO = os.environ.get('LC_REPO') or os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))))
SOLUTIONS = os.path.join(REPO, 'solutions')


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_list(values):
    head = None
    for value in reversed(list(values)):
        head = ListNode(value, head)
    return head


def to_list(node):
    out, guard = [], 0
    while node is not None:
        out.append(node.val)
        node = node.next
        guard += 1
        if guard > 200000:
            raise AssertionError('cycle in returned list')
    return out


def build_tree(values):
    if not values:
        return None
    root = TreeNode(values[0])
    queue, index = [root], 1
    while queue and index < len(values):
        node = queue.pop(0)
        for side in ('left', 'right'):
            if index >= len(values):
                return root
            value = values[index]
            index += 1
            if value is not None:
                child = TreeNode(value)
                setattr(node, side, child)
                queue.append(child)
    return root


def tree_to_list(root):
    if root is None:
        return []
    out, queue = [], [root]
    while queue:
        node = queue.pop(0)
        if node is None:
            out.append(None)
            continue
        out.append(node.val)
        queue.append(node.left)
        queue.append(node.right)
    while out and out[-1] is None:
        out.pop()
    return out


def problem_index():
    import glob
    index = {}
    for path in sorted(glob.glob(os.path.join(FETCH, 'batch*.json'))):
        try:
            data = json.load(open(path, encoding='utf-8'))
        except Exception:  # noqa: BLE001
            continue
        if isinstance(data, dict):
            data = data.get('problems') or []
        for entry in data:
            problem = entry.get('problem') if isinstance(entry, dict) else None
            if problem and problem.get('titleSlug'):
                index[problem['titleSlug']] = problem
    return index


def snippet_method(problem):
    for snippet in problem.get('codeSnippets') or []:
        if snippet.get('langSlug') == 'python3':
            code = snippet.get('code', '')
            idx = code.find('class Solution')
            import re
            match = re.search(r'def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(', code[idx:] if idx >= 0 else code)
            return match.group(1) if match else None
    return None


def parse_literal(text):
    import ast
    text = text.strip()
    try:
        return ast.literal_eval(text)
    except Exception:  # noqa: BLE001
        return json.loads(text)


def load_solution(slug):
    names = [n for n in os.listdir(SOLUTIONS) if n.endswith('-' + slug + '.py')]
    if not names:
        raise SystemExit(f'no solution file for slug {slug}')
    path = os.path.join(SOLUTIONS, names[0])
    spec = importlib.util.spec_from_file_location('triage_' + slug.replace('-', '_'), path)
    module = importlib.util.module_from_spec(spec)
    module.ListNode = ListNode
    module.TreeNode = TreeNode
    spec.loader.exec_module(module)
    return module, path


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    slug = sys.argv[1]
    case_text = expect_text = None
    time_it = '--time' in sys.argv
    if '--case' in sys.argv:
        case_text = sys.argv[sys.argv.index('--case') + 1].replace('\\n', '\n')
    if '--expect' in sys.argv:
        expect_text = sys.argv[sys.argv.index('--expect') + 1]
    if '--from-result' in sys.argv:
        result_path = sys.argv[sys.argv.index('--from-result') + 1]
        data = json.load(open(result_path, encoding='utf-8'))
        if isinstance(data, dict):
            data = data.get('results') or data.get('records') or []
        record = next((r for r in data if r.get('slug') == slug), None)
        if record is None:
            raise SystemExit(f'{slug} is not in {os.path.basename(result_path)}')
        print('judge record:', json.dumps({k: record.get(k) for k in
              ('slug', 'statusMsg', 'totalCorrect', 'totalTestcases', 'submissionId')}))
        for key in ('lastTestcase', 'codeOutput', 'expectedOutput', 'fullRuntimeError',
                    'fullCompileError', 'stdOutput'):
            if record.get(key):
                print(f'  {key}: {str(record[key])[:500]}')
        case_text = record.get('lastTestcase') or case_text
        expect_text = record.get('expectedOutput') or expect_text
    if not case_text:
        raise SystemExit('no --case and no lastTestcase in the result record')

    index = problem_index()
    problem = index.get(slug)
    method = snippet_method(problem) if problem else None
    module, path = load_solution(slug)
    solution = module.Solution()
    if method is None:
        candidates = [n for n, _ in inspect.getmembers(solution, inspect.ismethod)
                      if not n.startswith('_')]
        method = candidates[0]
        print(f'!! no fetched snippet found; guessing method {method}')
    func = getattr(solution, method)
    params = [p for p in inspect.signature(func).parameters.values() if p.name != 'self']
    annotations = [p.annotation if isinstance(p.annotation, str) else str(p.annotation) for p in params]
    lines = [line for line in case_text.splitlines() if line.strip()]
    if len(lines) == 1 and len(params) > 1:
        raise SystemExit(f'expected {len(params)} input lines, got 1')
    args = [parse_literal(line) for line in lines]
    call_args = []
    for annotation, value in zip(annotations, args):
        if 'TreeNode' in annotation:
            call_args.append(build_tree(value))
        elif 'list[' in annotation and 'ListNode' in annotation:
            call_args.append([build_list(row) for row in value])
        elif 'ListNode' in annotation:
            call_args.append(build_list(value))
        else:
            call_args.append(value)
    print('-' * 70)
    print(f'file   : {os.path.relpath(path, REPO)}')
    print(f'method : {method}{inspect.signature(func)}')
    print(f'input  : {case_text!r}')
    try:
        start = time.perf_counter()
        got = func(*call_args)
        elapsed = time.perf_counter() - start
    except Exception:  # noqa: BLE001
        print('EXCEPTION:')
        traceback.print_exc()
        return 1
    ret = inspect.signature(func).return_annotation
    ret_text = ret if isinstance(ret, str) else str(ret)
    if 'list[' in ret_text and 'TreeNode' in ret_text:
        got = [tree_to_list(node) for node in got]
    elif 'TreeNode' in ret_text:
        got = tree_to_list(got)
    elif 'list[' in ret_text and 'ListNode' in ret_text:
        got = [to_list(node) for node in got]
    elif 'ListNode' in ret_text:
        got = to_list(got)
    elif got is None and call_args and isinstance(call_args[0], list):
        got = call_args[0]
    print(f'observed: {got!r}')
    if expect_text is not None:
        expected = parse_literal(expect_text)
        print(f'expected: {expected!r}')
        print(f'match   : {got == expected}')
    if time_it:
        print(f'wall    : {elapsed * 1000:.1f} ms')
    return 0


if __name__ == '__main__':
    sys.exit(main())
