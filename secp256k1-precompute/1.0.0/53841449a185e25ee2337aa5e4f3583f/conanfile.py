from conan import ConanFile
from conan.tools.cmake import CMake, cmake_layout, CMakeDeps, CMakeToolchain
from conan.tools.files import copy, save
import os

class Secp256k1PrecomputeConan(ConanFile):
    name = "secp256k1-precompute"
    # version = "1.0.0"
    
    # Tool package - se compila para el host, no para el target
    package_type = "application"
    
    settings = "os", "compiler", "build_type", "arch"
    
    # Opciones para configurar la generación
    options = {
        "ecmult_window_size": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
        "ecmult_gen_precision": [2, 4, 8],
    }
    default_options = {
        "ecmult_window_size": 15,
        "ecmult_gen_precision": 4,
    }

    # exports_sources = "src/*", "include/*", "CMakeLists.txt", "cmake/*", "ci_utils/cmake/*"
    exports_sources = "CMakeLists.txt", "cmake/*", "src/*"
    
    def layout(self):
        cmake_layout(self)
    
    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()
        
        tc = CMakeToolchain(self)
        # Pasar las opciones como defines
        tc.variables["SECP256K1_ECMULT_WINDOW_SIZE"] = self.options.ecmult_window_size
        tc.variables["SECP256K1_ECMULT_GEN_PRECISION"] = self.options.ecmult_gen_precision
        tc.generate()
    
    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()
    
    def package(self):
        # Copiar el ejecutable
        copy(self, "gen_context*", 
             src=self.build_folder, 
             dst=os.path.join(self.package_folder, "bin"),
             keep_path=False)
    
    def package_info(self):
        # Información para que otros packages puedan usar esta tool
        self.cpp_info.bindirs = ["bin"]
        
        # Variables de entorno para facilitar el uso
        gen_context = os.path.join(self.package_folder, "bin", "gen_context")
        if os.name == "nt":  # Windows
            gen_context += ".exe"
        
        self.buildenv_info.define_path("SECP256K1_GEN_CONTEXT", gen_context)
