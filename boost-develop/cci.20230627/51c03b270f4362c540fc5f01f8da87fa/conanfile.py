import os

from conan import ConanFile
# from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, chdir, copy, export_conandata_patches, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version

required_conan_version = ">=2.0.0"

class BoostDevelopConan(ConanFile):
    name = "boost-develop"
    homepage = "https://github.com/boostorg/boost"
    topics = ("boost")
    license = "Boost Software License - Version 1.0"
    # package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    # no_copy_source = True

    options = {}
    default_options = {}

    def build_requirements(self):
        self.tool_requires("b2/4.10.0")

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    @property
    def _b2_exe(self):
        return "b2"

    def source(self):
        gitUrl = self.conan_data["sources"][self.version]["url"]
        gitCommit = self.conan_data["sources"][self.version]["commit"]

        self.run(f'git clone {gitUrl} {self.source_folder}')
        self.run(f'git checkout {gitCommit}', cwd=f'{self.source_folder}')

        self.run(f'git submodule update --init', cwd=f'{self.source_folder}')
        # self.run(f'b2 -d0 headers', cwd=f'{self.source_folder}')

    def generate(self):
        pass

    def build(self):
        apply_conandata_patches(self)
        b2_flags = "-d0 headers"
        full_command = f"{self._b2_exe} {b2_flags}"
        sources = self.source_folder
        self.output.warning(full_command)

        with chdir(self, sources):
            self.run(full_command)


    def package(self):
        copy(self, "LICENSE_1_0.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        print(f'source_folder: {self.source_folder}')
        print(f'package_folder: {self.package_folder}')

        copy(self, "*", src=os.path.join(self.source_folder, "boost"),
                        dst=os.path.join(self.package_folder, "include", "boost"))

        copy(self, "*", src=os.path.join(self.source_folder, "libs"),
                        dst=os.path.join(self.package_folder, "include", "libs"))

    def package_info(self):
        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.set_property("cmake_file_name", "boost_develop")
        self.cpp_info.filenames["cmake_find_package"] = "boost_develop"
        self.cpp_info.filenames["cmake_find_package_multi"] = "boost_develop"
        self.cpp_info.names["cmake_find_package"] = "boost_develop"
        self.cpp_info.names["cmake_find_package_multi"] = "boost_develop"

        # - Use 'headers' component for all includes + defines
        # - Use '_libboost' component to attach extra system_libs, ...

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].set_property("cmake_target_name", "boost_develop::headers")
        self.cpp_info.components["headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["headers"].names["pkg_config"] = "boost_develop"

        # boost_develop::boost_develop is an alias of boost_develop::headers
        self.cpp_info.components["_boost_develop_cmake"].requires = ["headers"]
        self.cpp_info.components["_boost_develop_cmake"].set_property("cmake_target_name", "boost_develop::boost_develop")
        self.cpp_info.components["_boost_develop_cmake"].names["cmake_find_package"] = "boost_develop"
        self.cpp_info.components["_boost_develop_cmake"].names["cmake_find_package_multi"] = "boost_develop"

