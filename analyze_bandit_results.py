import csv
import os
import subprocess
import sys
from collections import defaultdict
from typing import List, Dict


def exec(cmd: str) -> int:
    try:
        proc = subprocess.Popen(cmd.split(),
                                text=True,
                                shell=False,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT)
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            line = str(line.rstrip()).strip("b'")
            # print(line)
            sys.stdout.flush()

    except OSError as exc:
        print("Can't run process. Error code = {0}".format(exc))
        return False

    proc.wait()
    print(f'returncode = {proc.returncode}')
    return proc.poll()


def exec2(cmd: str) -> None:
    pipe = os.popen(cmd)
    rw = pipe.read().strip().split()
    print(rw)
    pipe.close()


def run_bandit():
    cmd: str = "bandit -c bandit.yaml -r . -f csv -o results.csv"
    exec(cmd)
    # exec2(cmd)


if __name__ == '__main__':
    run_bandit()

    issues: Dict = defaultdict(dict)
    with open("results.csv", newline='') as File:
        reader = csv.reader(File)
        next(reader)  # Skip header
        for row in reader:
            file, desc, vId, severity, *other = row
            entry = issues[severity].setdefault(vId, list())
            entry.append([file, desc, other])

    high = issues['HIGH']
    mediums = issues['MEDIUM']
    low = issues['LOW']

    for v, desc in [(high, "HIGH"), (mediums, "MEDIUM"), (low, "LOW")]:
        print(f"\n************************************ {desc} **************************************************\n")
        for vId, data in v.items():
            front: List = data[0]
            params: List = front[2]

            title, issues_description = front[1], params[2]
            mitre_link, bandit_link = params[1], params[6],

            print(f'------------------ {vId} : {title}------------------------')
            print(f'\tLinks: {mitre_link}, {bandit_link}')
            print(f'\tFiles with issues:')
            for entry in data:
                entry_params: List = entry[2]
                print(f'{entry[0]}:{entry_params[3]}  [{issues_description}]')
                # print(entry[2])


