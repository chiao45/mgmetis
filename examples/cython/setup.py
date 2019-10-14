from setuptools import setup, Extension
from Cython.Build import cythonize


setup(
    ext_modules=cythonize(
        [Extension("graph", ["graph.pyx"])], compiler_directives={"language_level": 3}
    )
)
