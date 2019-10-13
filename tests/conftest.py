# -*- coding: utf-8 -*-
try:
    import mgmetis
except (ImportError, ModuleNotFoundError):
    import sys

    sys.path.append("..")
else:
    del mgmetis
