# -*- coding: utf-8 -*-

from setuptools import setup
import mgmetis
import conf
import build_ext

build_ext.DEBUG = conf.debug


setup(
    version=mgmetis.__version__,
    ext_modules=conf.exts,
    cmdclass={"build_ext": build_ext.BuildExt},
)
