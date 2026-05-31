"""Shared regular expressions for Markdown lint parsing."""

from __future__ import annotations

import re

ATX_HEADING_RE = re.compile(r"^(#{1,6})(\s+)(.*?)(\s+#+\s*)?$")
BAD_ATX_RE = re.compile(r"^(#{1,6})(\S.*)$")
FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
HR_RE = re.compile(r"^\s{0,3}(([-*_])\s*){3,}$")
LIST_RE = re.compile(r"^(\s*)(([-+*])|(\d+)[.)])(\s+)(.*)$")
