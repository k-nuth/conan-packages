# Copyright (c) 2016-2023 Knuth Project developers.
# Distributed under the MIT software license, see the accompanying
# file COPYING or http://www.opensource.org/licenses/mit-license.php.

import os
from conan import ConanFile
from conan.tools.build.cppstd import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy
from kthbuild import KnuthConanFileV2, option_on_off

required_conan_version = ">=2.0"

class KnuthNodeConan(KnuthConanFileV2):
    name = "node"
    license = "http://www.boost.org/users/license.html"
    url = "https://github.com/k-nuth/node"
    description = "Crypto full node"
    settings = "os", "compiler", "build_type", "arch"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "tests": [True, False],
        "currency": ['BCH', 'BTC', 'LTC'],
        "verbose": [True, False],
        "mempool": [True, False],
        "db": ['legacy', 'legacy_full', 'pruned', 'default', 'full'],
        "db_readonly": [True, False],
        "march_id": ["ANY"],
        "march_strategy": ["download_if_possible", "optimized", "download_or_fail"],
        "cxxflags": ["ANY"],
        "cflags": ["ANY"],
        "cmake_export_compile_commands": [True, False],
        "log": ["boost", "spdlog", "binlog"],
        "use_libmdbx": [True, False],
        "statistics": [True, False],
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "tests": False,
        "currency": "BCH",
        "march_strategy": "download_if_possible",
        "verbose": False,
        "mempool": False,
        "db": "default",
        "db_readonly": False,
        "cmake_export_compile_commands": False,
        "log": "spdlog",
        "use_libmdbx": False,
        "statistics": False,
    }

    exports_sources = "src/*", "CMakeLists.txt", "ci_utils/cmake/*", "cmake/*", "knuthbuildinfo.cmake", "include/*", "test/*", "console/*"

    def _is_legacy_db(self):
        return self.options.db == "legacy" or self.options.db == "legacy_full"

    def validate(self):
        KnuthConanFileV2.validate(self)
        if self.info.settings.compiler.cppstd:
            check_min_cppstd(self, "20")

    def build_requirements(self):
        if self.options.tests:
            self.test_requires("catch2/3.3.1")

    def requirements(self):
        self.requires("infrastructure/0.26.0")
        self.requires("domain/0.31.0")
        self.requires("database/0.30.0")
        # if self.options.consensus:
        self.requires("consensus/0.25.0")

        self.requires("blockchain/0.29.0")
        self.requires("network/0.34.0@")

        self.requires("boost/1.81.0")
        self.requires("fmt/9.1.0")
        self.requires("spdlog/1.11.0")

        if not self._is_legacy_db():
            if self.options.use_libmdbx:
                self.requires("libmdbx/0.7.0@kth/stable")
                self.output.info("Using libmdbx for DB management")
            else:
                self.requires("lmdb/0.9.29")
                self.output.info("Using lmdb for DB management")
        else:
            self.output.info("Using legacy DB")

        if self.options.statistics:
            self.requires("tabulate/1.0@")


    def config_options(self):
        KnuthConanFileV2.config_options(self)

    def configure(self):
        KnuthConanFileV2.configure(self)

        self.options["*"].mempool = self.options.mempool

        self.options["*"].db_readonly = self.options.db_readonly
        self.output.info("Compiling with read-only DB: %s" % (self.options.db_readonly,))

        self.output.info("Compiling for currency: %s" % (self.options.currency,))
        self.output.info("Compiling with mempool: %s" % (self.options.mempool,))

        #TODO(fernando): move to kthbuild
        self.options["*"].log = self.options.log
        self.output.info("Compiling with log: %s" % (self.options.log,))

        self.options["*"].use_libmdbx = self.options.use_libmdbx
        self.output.info("Compiling with use_libmdbx: %s" % (self.options.use_libmdbx,))

    def package_id(self):
        KnuthConanFileV2.package_id(self)

    def layout(self):
        cmake_layout(self)

    def generate(self):
        tc = self.cmake_toolchain_basis()
        # tc.variables["CMAKE_VERBOSE_MAKEFILE"] = True
        # tc.variables["WITH_CONSOLE"] = option_on_off(self.with_console)
        tc.variables["WITH_MEMPOOL"] = option_on_off(self.options.mempool)
        tc.variables["DB_READONLY_MODE"] = option_on_off(self.options.db_readonly)
        tc.variables["LOG_LIBRARY"] = self.options.log
        tc.variables["USE_LIBMDBX"] = option_on_off(self.options.use_libmdbx)
        tc.variables["STATISTICS"] = option_on_off(self.options.statistics)
        tc.variables["CONAN_DISABLE_CHECK_COMPILER"] = option_on_off(True)
        tc.generate()
        tc = CMakeDeps(self)
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        if not self.options.cmake_export_compile_commands:
            cmake.build()
            if self.options.tests:
                cmake.test()

    # def imports(self):
    #     self.copy("*.h", "", "include")

    def package(self):
        cmake = CMake(self)
        cmake.install()
        # rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        # rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        # rmdir(self, os.path.join(self.package_folder, "res"))
        # rmdir(self, os.path.join(self.package_folder, "share"))

    def package_info(self):
        self.cpp_info.includedirs = ['include']
        self.cpp_info.libs = ["node"]