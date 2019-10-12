# -*- coding: utf-8 -*-

from setuptools.command.build_ext import build_ext

try:
    import mpi4py
except (ModuleNotFoundError, ImportError):
    mpi4py = None

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
        links = []
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
            if mpi4py is not None:
                import sysconfig
                import os
                from os.path import join

                _so_ext = sysconfig.get_config_var("EXT_SUFFIX")
                _build_prefix = join(self.build_lib, "mgmetis", "_cython")

                def unlink_lib(lib):
                    try:
                        os.unlink(lib)
                    except FileNotFoundError:
                        pass

                def link_lib(lib):
                    unlink_lib(lib)
                    try:
                        os.symlink(join(_build_prefix, lib), lib)
                    except OSError:
                        pass

                # NOTE: some internal headers are conflicting via Python
                # extensions if we try to build metis and parmetis at the same
                # time from the same scope. As a remedy (and more efficient way),
                # we "link" to metis. Notice that this only works on unix.
                for ext in self.extensions:
                    if ext.name.find("par") >= 0:
                        # parallel extension
                        ext.library_dirs += [_build_prefix]
                        if not ext.name.endswith("64"):
                            links.append("metis" + _so_ext)
                            # softlink to current directory
                            # NOTE: we need to link to current directory due
                            # to I don't know how to add soname to python
                            # extension
                            link_lib("metis" + _so_ext)
                            # 32 bit
                            ext.extra_link_args += [
                                "metis" + _so_ext,
                                "-Wl,-rpath=$ORIGIN/.",
                            ]
                        else:
                            links.append("metis64" + _so_ext)
                            # 64 bit
                            link_lib("metis64" + _so_ext)
                            ext.extra_link_args += [
                                "metis64" + _so_ext,
                                "-Wl,-rpath=$ORIGIN/.",
                            ]
        super().build_extensions()
        if cpl_type == "unix":
            for l in links:
                unlink_lib(l)
