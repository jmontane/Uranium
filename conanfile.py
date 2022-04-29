import os
import sys
import pathlib

from conan import ConanFile
from conan.tools.env import VirtualBuildEnv, VirtualRunEnv
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
    requirements_txts = ["requirements.txt"]
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True
    options = {
        "enable_testing": [True, False]
    }
    default_options = {
        "enable_testing": False
    }
    scm = {
        "type": "git",
        "subfolder": ".",
        "url": "auto",
        "revision": "auto"
    }

    def configure(self):
        self.options["arcus"].shared = not self.settings.os == "Windows"
        if self.options.enable_testing:
            self.requirements_txts.append("requirements-dev.txt")

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
        vb = VirtualBuildEnv(self)
        vb.generate()

        vr = VirtualRunEnv(self)
        vr.generate()

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
