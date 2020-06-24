import os
import sys
from setuptools import setup, find_packages
from fnmatch import fnmatchcase
from distutils.util import convert_path

standard_exclude = ('*.pyc', '*~', '.*', '*.bak', '*.swp*')
standard_exclude_directories = ('.*', 'CVS', '_darcs', './build', './dist', 'EGG-INFO', '*.egg-info')
def find_package_data(where='.', package='', exclude=standard_exclude, exclude_directories=standard_exclude_directories):
    out = {}
    stack = [(convert_path(where), '', package)]
    while stack:
        where, prefix, package = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where, name)
            if os.path.isdir(fn):
                bad_name = False
                for pattern in exclude_directories:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                if os.path.isfile(os.path.join(fn, '__init__.py')):
                    if not package:
                        new_package = name
                    else:
                        new_package = package + '.' + name
                        stack.append((fn, '', new_package))
                else:
                    stack.append((fn, prefix + name + '/', package))
            else:
                bad_name = False
                for pattern in exclude:
                    if (fnmatchcase(name, pattern)
                        or fn.lower() == pattern.lower()):
                        bad_name = True
                        break
                if bad_name:
                    continue
                out.setdefault(package, []).append(prefix+name)
    return out

setup(name='docassemble.attributes',
      version='0.0.1',
      description=('A docassemble extension.'),
      long_description='# docassemble-DADataType\r\n\r\nThis is a module to give Docassemble the ability to ask datatype-approriate default questions\r\nwith regard to individual variables, so that the "generic object" feature can be used with\r\nregard to booleans, numbers, etc.\r\n\r\nThe use case is for rapid prototyping. If you have an external tool with a data structure and known datatypes,\r\nyou can export that datastructure as a set of objects for a docassemble interview, and specify only\r\nyour goal (perhaps a document template), and you will have a bare-bones functional interview without\r\nhaving to draft any question blocks.\r\n\r\n## Installation\r\n\r\nIt can be installed inside your docassemble package manager by providing the address for this github repository.\r\n\r\n## Use\r\n\r\nInside your interview, load the module and include the default questions interview file.\r\n\r\n```\r\nmodules:\r\n  - docassemble.DADataType\r\n---\r\ninclude:\r\n  - docassemble.DADataType:/data/questions/DADataType.yml\r\n```\r\n\r\nNow, create an `objects` block, using the available DADT classes, or load objects from a YAML or JSON file.\r\n\r\nThe available datatypes are currently:\r\n\r\n* DADTNumber\r\n* DADTString\r\n* DADTBoolean\r\n* DADTContinue\r\n* DADTTime\r\n* DADTDate\r\n* DADTDateTime\r\n* DADTEmail',
      long_description_content_type='text/markdown',
      author='Jason Morris',
      author_email='jason@roundtablelaw.ca',
      license='The MIT License (MIT)',
      url='https://docassemble.org',
      packages=find_packages(),
      namespace_packages=['docassemble'],
      install_requires=[],
      zip_safe=False,
      package_data=find_package_data(where='docassemble/attributes/', package='docassemble.attributes'),
     )

