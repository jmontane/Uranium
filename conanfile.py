import os
import sys
import pathlib

from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake, cmake_layout
from conan.tools import files
from conans import tools
from conan.errors import ConanInvalidConfiguration

required_conan_version = ">=1.46.2"


class UraniumConan(ConanFile):
    name = "uranium"
    license = "AGPL-3.0"
    author = "Ultimaker B.V."
    url = "https://github.com/Ultimaker/uranium"
    description = "A Python framework for building Desktop applications."
    topics = ("conan", "python", "pyqt5", "qt", "3d-graphics", "3d-models", "python-framework")
    build_policy = "missing"
    exports = "LICENSE*"
    exports_sources = "requirements.txt", "requirements-dev.txt", "UM/*", "plugins/*", "resources/*"
    settings = "os", "compiler", "build_type", "arch"
    python_requires = "PythonVirtualEnvironment/0.2.0@ultimaker/testing"
    no_copy_source = True
    options = {
        "enable_testing": [True, False],
        "generate_venv": [True, False]
    }
    default_options = {
        "enable_testing": False,
        "generate_venv": True
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    @property
    def _site_packages(self):
        if self.settings.os == "Windows":
            return os.path.join("Lib", "site-packages")
        return os.path.join("lib", "python3.10", "site-packages")

    def configure(self):
        self.options["arcus"].shared = not self.settings.os == "Windows"

    def validate(self):
        if self.version:
            if tools.Version(self.version) <= tools.Version("4"):
                raise ConanInvalidConfiguration("Only versions 5+ are support")

    def requirements(self):
        self.requires("arcus/latest@ultimaker/stable")

    def layout(self):
        self.folders.source = "."
        self.folders.build = "venv"
        self.folders.generators = os.path.join("venv", "bin")

    def generate(self):
        if self.options.generate_venv:
            venv = self.python_requires["PythonVirtualEnvironment"].module.PythonVirtualEnvironment(self)
            reqs = ["requirements.txt"]
            if self.options.enable_testing:
                reqs.append("requirements-dev.txt")
            venv.configure(python_interpreter = sys.executable, requirements_txt = reqs)
            venv.generate()

    def package(self):
        self.copy("*", src = os.path.join(self.source_folder, "plugins"), dst = os.path.join("site-packages", "plugins"))
        self.copy("*", src = os.path.join(self.source_folder, "resources"), dst = os.path.join("site-packages", "resources"))
        self.copy("*", src = os.path.join(self.source_folder, "UM"), dst = os.path.join("site-packages", "UM"))

    def package_info(self):
        if self.in_local_cache:
            self.runenv_info.append_path("PYTHONPATH", os.path.join(self.package_folder, "site-packages"))
        else:
            self.runenv_info.append_path("PYTHONPATH", self.source_folder)

    def package_id(self):
        self.info.header_only()
