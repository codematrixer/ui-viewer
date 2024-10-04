# -*- coding: utf-8 -*-

import re


def parse_bounds(text):
    m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', text)
    if m is None:
        return None
    (lx, ly, rx, ry) = map(int, m.groups())
    return dict(x=lx, y=ly, width=rx - lx, height=ry - ly)


def safe_xmlstr(s):
    return s.replace("$", "-")


def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


def str2int(v):
    return int(v)


def convstr(v):
    return v