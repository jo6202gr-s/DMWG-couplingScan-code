from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop
from pybind11.setup_helpers import Pybind11Extension, build_ext
import subprocess
with open('requirements.txt') as f:
    requirements = f.read().splitlines()
__version__ = "0.0.1"

# For handling arguments so we can install without lhapdf if necessary
class ModifyInstall(install):
    user_options = install.user_options + [
        ('nolhapdf', None, 'install without lhapdf dependency - limited functionality'),
    ]

    def initialize_options(self):
        install.initialize_options(self)
        self.nolhapdf = None

    def finalize_options(self):
        if self.nolhapdf : print("Requested installation without LHAPDF dependency. Note that this will limit the functionality.")
        install.finalize_options(self)

    def run(self):
        global nolhapdf
        nolhapdf = self.nolhapdf # will be 1 or None
        install.run(self)

class ModifyDevelop(develop):
    user_options = develop.user_options + [
        ('nolhapdf', None, 'install without lhapdf dependency - limited functionality'),
    ]

    def initialize_options(self):
        develop.initialize_options(self)
        self.nolhapdf = None

    def finalize_options(self):
        if self.nolhapdf : print("Requested installation without LHAPDF dependency. Note that this will limit the functionality.")
        develop.finalize_options(self)

    def run(self):
        global nolhapdf
        nolhapdf = self.nolhapdf # will be 1 or None
        develop.run(self)

# Detailed examples: 
# https://github.com/pybind/pybind11_benchmark/blob/master/setup.py
# https://github.com/wichert/pybind11-example/blob/master/setup.py
def get_lhapdf_includes() :
    libdir = subprocess.check_output(["lhapdf-config", "--libdir"]).decode('ascii').strip()
    incdir = subprocess.check_output(["lhapdf-config", "--incdir"]).decode('ascii').strip()
    if not libdir or not incdir :
       print("You do not have lhapdf installed!")
       print("This will limit what you can do.")
       print("If you want to proceed anyway, re-install with option --nolhapdf")
       exit(1)
    return libdir,incdir

def get_extmodules() :

    # Check if we are actually compiling the C++ code.
    print("My SYS ARGV is:")
    print(sys.argv)
    if "--nolhapdf" in sys.argv :
        ext_modules = []
    else :
        # Here I need to access the flags.
        lhapdf_dirs = get_lhapdf_includes()
        ext_modules = [
            Pybind11Extension(
                "lhapdfwrap",
                sources = ["src/lhapdf_integrands.cpp"],
                library_dirs = [lhapdf_dirs[0]],
                libraries = ['LHAPDF'],
                include_dirs = [lhapdf_dirs[1]],
                define_macros = [('VERSION_INFO', __version__)],
                ),
        ]
    return ext_modules

setup(
    name = 'package',
    version=__version__,
    url = 'https://github.com/LHC-DMWG/DMWG-couplingScan-code/',
    author = 'LHC DMWG',
    author_email = 'lhc-dmwg-contributors-couplingscan@cern.ch',
    description = '',
    cmdclass={
        'install': ModifyInstall,
        'develop': ModifyDevelop,
        'build_ext': build_ext},
    packages = find_packages(),    
    install_requires = requirements,
    ext_modules=get_extmodules()
)
