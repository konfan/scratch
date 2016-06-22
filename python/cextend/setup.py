from distutils.core import setup, Extension

module1 = Extension('sp', sources = ['sp.c'])


setup (name = 'test',
        version = '1.0',
        description = "None",
        ext_modules = [module1])
