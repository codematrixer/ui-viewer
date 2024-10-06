# -*- coding: utf-8 -*-

import argparse
from uiviewer.__main__ import run


def main():
    parser = argparse.ArgumentParser(description="My CLI Tool")
    parser.add_argument('-p', '--port', type=int, default=8000, help='local listen port for uiviewer')
    args = parser.parse_args()
    run(port=args.port)


if __name__ == "__main__":
    main()