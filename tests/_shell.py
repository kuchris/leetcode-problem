"""Harness for the shell problems.

LeetCode judges these with Bash 5.2.21 on Linux; this machine has Git for
Windows' bash 5.3.9 (Cygwin). For the text-processing these problems ask for —
reading a line, counting words, transposing columns, matching a pattern — the two
behave the same, and the harness runs the script against a real bash rather than
simulating it. Differences that would matter: Linux-only utilities absent from
Git for Windows, and path handling.

Each case builds a fresh temporary directory containing the input files the
statement names, runs the script there, and returns stdout, which is what the
judge compares.
"""
import os
import shutil
import subprocess
import tempfile

BASH_CANDIDATES = (
    r'C:\Program Files\Git\bin\bash.exe',
    r'C:\Program Files\Git\usr\bin\bash.exe',
    r'C:\Program Files (x86)\Git\bin\bash.exe',
)


def find_bash():
    """Locate a bash, or raise with a clear message rather than silently skipping."""
    override = os.environ.get('LC_BASH')
    if override:
        if not os.path.exists(override):
            raise RuntimeError(f'LC_BASH points at a missing file: {override}')
        return override
    for candidate in BASH_CANDIDATES:
        if os.path.exists(candidate):
            return candidate
    found = shutil.which('bash')
    if found:
        return found
    raise RuntimeError(
        'no bash found; install Git for Windows or set LC_BASH to a bash executable'
    )


def load_shell(filename):
    """Return a solution's script text with normalised line endings.

    The repository header is `#` comments, which bash ignores, so nothing is
    stripped. CRLF is converted because a stray carriage return breaks the
    quoting and command substitution these scripts rely on.
    """
    from _loader import SOLUTIONS_DIR

    text = (SOLUTIONS_DIR / filename).read_text(encoding='utf-8')
    return text.replace('\r\n', '\n').replace('\r', '\n')


def run_script(filename, files, timeout=20):
    """Run a shell solution in a fresh directory and return its stdout.

    ``files`` maps a filename to its contents, so a case declares the input the
    statement promises. The script is written with LF endings and run as
    ``bash script.sh`` from that directory, matching how the judge invokes it.
    """
    bash = find_bash()
    script = load_shell(filename)
    workdir = tempfile.mkdtemp(prefix='lc-shell-')
    try:
        for name, content in files.items():
            path = os.path.join(workdir, name)
            with open(path, 'w', encoding='utf-8', newline='\n') as handle:
                handle.write(content)
        script_path = os.path.join(workdir, '_solution.sh')
        with open(script_path, 'w', encoding='utf-8', newline='\n') as handle:
            handle.write(script)
        completed = subprocess.run(
            [bash, '_solution.sh'],
            cwd=workdir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=timeout,
        )
        if completed.returncode != 0 and completed.stderr.strip():
            raise RuntimeError(
                f'{filename} exited {completed.returncode}: '
                f'{completed.stderr.strip()[:300]}'
            )
        return completed.stdout
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def normalise(text):
    """Compare output the way a judge would: trailing whitespace and a trailing
    newline are not differences."""
    lines = [line.rstrip() for line in text.replace('\r\n', '\n').split('\n')]
    while lines and lines[-1] == '':
        lines.pop()
    return lines
