# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Washington
"""Application entry point for ``python -m songcutter``."""

from __future__ import annotations

import sys

from songcutter.app import main

if __name__ == "__main__":
    sys.exit(main())
