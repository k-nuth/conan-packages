from conan import ConanFile
from conan.errors import ConanException
from conan.tools.build import check_min_cppstd
from conan.tools.files import copy, load
import os
import re


class ParlayLibConan(ConanFile):
    name = "parlaylib"
    package_type = "header-library"
    license = "MIT"
    url = "https://github.com/fpelliccioni/parlaylib"
    description = "A collection of parallel algorithms and other support for parallelism in C++"
    settings = "os", "arch", "compiler", "build_type"
    exports_sources = "include/parlay/*", "LICENSE"

    def set_version(self):
        # The CMake project declares the version; the recipe does not repeat it.
        if self.version:
            return
        content = load(self, os.path.join(self.recipe_folder, "CMakeLists.txt"))
        match = re.search(r"project\(\s*PARLAY\s+VERSION\s+(\d+\.\d+\.\d+)", content)
        if not match:
            raise ConanException("Could not read the project version from CMakeLists.txt")
        self.version = match.group(1)

    def validate(self):
        check_min_cppstd(self, "23")

    def package(self):
        copy(self, "*", src=os.path.join(self.source_folder, "include", "parlay"),
             dst=os.path.join(self.package_folder, "include", "parlay"))
        copy(self, "LICENSE", src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))

    def package_id(self):
        self.info.clear()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "Parlay")
        self.cpp_info.set_property("cmake_target_name", "Parlay::parlay")
        self.cpp_info.bindirs = []
        self.cpp_info.libdirs = []
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs = ["pthread"]
        elif self.settings.os == "Windows":
            # The default scheduler waits with WaitOnAddress.
            self.cpp_info.system_libs = ["synchronization"]
