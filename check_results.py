from __future__ import annotations
import json
import subprocess
from typing import Dict, List
from enum import Enum


OUTPUT_FORMAT: str = "json"
# OUTPUT_FORMAT: str = "csv"
OUTPUT_FILE: str = f'results.{OUTPUT_FORMAT}'
BANDIT_CONFIG_FILE: str = 'bandit.yaml'
# BANDIT_CONFIG_FILE: str = 'bandit_skip_all.yaml'


class Severity(str, Enum):
    UNDEFINED: str = 'UNDEFINED'
    LOW: str = 'LOW'
    MEDIUM: str = 'MEDIUM'
    HIGH: str = 'HIGH'

    @staticmethod
    def from_string(severity_str: str) -> Severity:
        try:
            return Severity[severity_str]
        except KeyError as _:
            return Severity.UNDEFINED


class Issue(object):

    def __init__(self, entry: Dict) -> None:
        self.id = entry['test_id']
        self.name: str = entry['test_name']
        self.severity: Severity = Severity.from_string(entry['issue_severity'])
        self.file_line: str = f"{entry['filename']}:{entry['line_number']}"
        self.description: str = entry['issue_text']

    def __repr__(self) -> str:
        return str(json.dumps(self.__dict__, indent=4))


def execute_command(cmd: str) -> int:
    try:
        proc = subprocess.Popen(cmd.split(),
                                text=True,
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
    except OSError as exc:
        print(f"Can't run process {cmd}. Error: {exc}")
        return False

    proc.wait()
    return proc.poll()


def run_bandit() -> int:
    cmd: str = f"bandit -c {BANDIT_CONFIG_FILE} -r . -f {OUTPUT_FORMAT} -o {OUTPUT_FILE} --exit-zero"
    return execute_command(cmd)


def analyze() -> bool:
    try:
        with open(OUTPUT_FILE) as data_file:
            json_data: Dict = json.load(data_file)
    except Exception as exc:
        print(exc)
        return False

    issues: List[Issue] = [Issue(entry) for entry in json_data['results']]
    important_issues: List[Issue] = [issue for issue in issues if
                                     issue.severity == Severity.HIGH or issue.severity == Severity.MEDIUM]
    if not issues:
        return True

    for issue in issues:
        print(issue)

    return False


if __name__ == '__main__':
    run_bandit()
    result: bool = analyze()
