from distutils.core import setup, Extension

module1 = Extension('ReadHDF',sources = ['readhdfmodule.c'],libraries = ['mfhdf','df','jpeg','z'])

setup (name = 'ReadHDF', version = '1.0', description = 'this is my first module', ext_modules = [module1])
