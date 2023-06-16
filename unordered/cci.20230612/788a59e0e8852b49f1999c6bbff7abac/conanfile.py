import os

from conan import ConanFile
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
from conan.tools.layout import basic_layout
from conan.tools.build import check_min_cppstd
from conan.tools.scm import Version

required_conan_version = ">=2.0.0"

class UnorderedConan(ConanFile):
    name = "unordered"
    homepage = "https://github.com/boostorg/unordered"
    topics = ("unordered", "hash", "hash-table", "hash-map", "hash-set", "hashing", "unordered-map", "unordered-set", "unordered-multimap", "unordered-multiset")
    url = "https://github.com/conan-io/conan-center-index"
    license = "Boost Software License - Version 1.0"
    package_type = "header-library"
    settings = "os", "arch", "compiler", "build_type"
    no_copy_source = True

    options = {}
    default_options = {}

    def export_sources(self):
        export_conandata_patches(self)

    def layout(self):
        basic_layout(self, src_folder="src")

    def requirements(self):
        self.requires("boost-develop/cci.20230614", transitive_headers=True)
        self.requires("onetbb/2021.9.0", transitive_headers=True)

    def package_id(self):
        self.info.clear()

    def validate(self):
        if self.settings.get_safe("compiler.cppstd"):
            check_min_cppstd(self, 11)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.source_folder, strip_root=True)
        # apply_conandata_patches(self)

    def generate(self):
        pass
        # tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True
        # if not self.options.header_only:
        #     tc = CMakeToolchain(self)
        #     # tc.cache_variables["FMT_DOC"] = False
        #     # tc.cache_variables["FMT_TEST"] = False
        #     # tc.cache_variables["FMT_INSTALL"] = True
        #     # tc.cache_variables["FMT_LIB_DIR"] = "lib"
        #     tc.generate()

    def build(self):
        apply_conandata_patches(self)

    def package(self):
        copy(self, "LICENSE_1_0.txt", src=self.source_folder, dst=os.path.join(self.package_folder, "licenses"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))

        # print(f'source_folder: {self.source_folder}')
        # print(f'package_folder: {self.package_folder}')

        copy(self, "*", src=os.path.join(self.source_folder, "include"),
                        dst=os.path.join(self.package_folder, "include"))

    def package_info(self):
        self.env_info.BOOST_ROOT = self.package_folder

        self.cpp_info.set_property("cmake_file_name", "Unordered")
        self.cpp_info.filenames["cmake_find_package"] = "Unordered"
        self.cpp_info.filenames["cmake_find_package_multi"] = "Unordered"
        self.cpp_info.names["cmake_find_package"] = "Unordered"
        self.cpp_info.names["cmake_find_package_multi"] = "Unordered"

        # - Use 'headers' component for all includes + defines
        # - Use '_libboost' component to attach extra system_libs, ...

        self.cpp_info.components["headers"].libs = []
        self.cpp_info.components["headers"].set_property("cmake_target_name", "Unordered::headers")
        self.cpp_info.components["headers"].names["cmake_find_package"] = "headers"
        self.cpp_info.components["headers"].names["cmake_find_package_multi"] = "headers"
        self.cpp_info.components["headers"].names["pkg_config"] = "unordered"

        # Unordered::unordered is an alias of Unordered::headers
        self.cpp_info.components["_unordered_cmake"].requires = ["headers"]
        self.cpp_info.components["_unordered_cmake"].set_property("cmake_target_name", "Unordered::unordered")
        self.cpp_info.components["_unordered_cmake"].names["cmake_find_package"] = "unordered"
        self.cpp_info.components["_unordered_cmake"].names["cmake_find_package_multi"] = "unordered"
