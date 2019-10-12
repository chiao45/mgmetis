# -*- coding: utf-8 -*-

from setuptools.command.build_ext import build_ext

DEBUG = False


class BuildExt(build_ext):
    def _remove_flag(self, flag):
        try:
            self.compiler.compiler_so.remove(flag)
        except (AttributeError, ValueError):
            pass

    def build_extensions(self):
        self._remove_flag("-Wstrict-prototypes")
        if DEBUG:
            self._remove_flag("-DNDEBUG")
        cpl_type = self.compiler.compiler_type
        if cpl_type == "unix":
            if not DEBUG:
                opt_flag = "-O3"
            else:
                opt_flag = "-O1"
            # replace o2, since it seems to be default
            for i, opt in enumerate(self.compiler.compiler_so):
                if opt.startswith("-O"):
                    self.compiler.compiler_so[i] = opt_flag
                    break
        super().build_extensions()
