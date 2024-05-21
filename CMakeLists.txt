cmake_minimum_required(VERSION 3.20.0)
project(euDSL LANGUAGES CXX C)

set(CMAKE_BUILD_WITH_INSTALL_NAME_DIR ON)

set(CMAKE_CXX_STANDARD 17 CACHE STRING "C++ standard to conform to")

option(BUILD_MLIR "<help_text>" OFF)

find_package(LLVM ${LLVM_CLANG_VERSION} CONFIG REQUIRED)
message(STATUS "Using LLVMConfig.cmake in: ${LLVM_DIR}")
set(LLVM_RUNTIME_OUTPUT_INTDIR ${CMAKE_BINARY_DIR}/bin)
set(LLVM_LIBRARY_OUTPUT_INTDIR ${CMAKE_BINARY_DIR}/lib)

list(APPEND CMAKE_MODULE_PATH "${LLVM_CMAKE_DIR}")

include(TableGen)
include(AddLLVM)
include(HandleLLVMOptions)
include_directories(${LLVM_INCLUDE_DIRS})

set(LLVM_CLANG_VERSION 15.0)


if(BUILD_MLIR)
  find_package(MLIR REQUIRED CONFIG)
  message(STATUS "Using MLIRConfig.cmake in: ${MLIR_DIR}")
  set(MLIR_BINARY_DIR ${CMAKE_BINARY_DIR})
  list(APPEND CMAKE_MODULE_PATH "${MLIR_CMAKE_DIR}")
  include(AddMLIR)
  include(AddMLIRPython)

  message(STATUS "Using MLIRConfig.cmake in: ${Clang_DIR}")
  include(MLIRDetectPythonEnv)

  mlir_configure_python_dev_packages()
  add_compile_definitions("MLIR_PYTHON_PACKAGE_PREFIX=eudsl.")
  set(EUDSL_PYTHON_INSTALL_DIR "python_packages")
  set(EUDSL_BINARY_DIR ${CMAKE_CURRENT_BINARY_DIR})
  set(EUDSL_PYTHON_PACKAGES_DIR "${EUDSL_BINARY_DIR}/${EUDSL_PYTHON_INSTALL_DIR}")

  include_directories(${MLIR_INCLUDE_DIRS})

  declare_mlir_python_sources(EUDSLPythonSources ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")
  declare_mlir_python_sources(EUDSLPythonExtensions)

  get_property(MLIR_CONVERSION_LIBS GLOBAL PROPERTY MLIR_CONVERSION_LIBS)
  get_property(MLIR_DIALECT_LIBS GLOBAL PROPERTY MLIR_DIALECT_LIBS)
  get_property(MLIR_EXTENSION_LIBS GLOBAL PROPERTY MLIR_EXTENSION_LIBS)
  get_property(MLIR_TRANSLATION_LIBS GLOBAL PROPERTY MLIR_TRANSLATION_LIBS)
  get_property(MLIR_UPSTREAM_CAPI_LIBS GLOBAL PROPERTY MLIR_UPSTREAM_CAPI_LIBS)

  # Dig out all of the upstream cpp source files associated with the C extension modules.
  _flatten_mlir_python_targets(mlir_python_sources MLIRPythonSources)
  set(_mlir_python_cpp_sources)
  foreach(s ${mlir_python_sources})
    get_target_property(_sources ${s} INTERFACE_SOURCES)
    list(FILTER _sources INCLUDE REGEX "(\.cpp|\.h)$")
    if(_sources)
      list(APPEND _mlir_python_cpp_sources ${_sources})
    endif()
  endforeach()

  # Missed one...
  get_target_property(RegisterEverythingSources MLIRPythonExtension.RegisterEverything INTERFACE_SOURCES)

  set(PYBINDINGS_SRC "${MLIR_INSTALL_PREFIX}/src/python/MLIRPythonExtension.Core")

  set(_py_srcs
    #  ${CMAKE_CURRENT_SOURCE_DIR}/binding/binding.cpp
    ${_mlir_python_cpp_sources}
    ${RegisterEverythingSources}
  )

  set(_py_libs
    LLVMSupport
    ${MLIR_CONVERSION_LIBS}
    ${MLIR_DIALECT_LIBS}
    ${MLIR_EXTENSION_LIBS}
    ${MLIR_TRANSLATION_LIBS}
    ${MLIR_UPSTREAM_CAPI_LIBS}
  )

  declare_mlir_python_extension(EUDSLPythonExtensions.MLIR
    MODULE_NAME _eudsl
    ADD_TO_PARENT EUDSLPythonExtensions
    ROOT_DIR "/"

    SOURCES
    ${_py_srcs}

    PRIVATE_LINK_LIBS
    ${_py_libs}
  )

  target_include_directories(
    EUDSLPythonExtensions.MLIR
    INTERFACE $<BUILD_INTERFACE:${PYBINDINGS_SRC}>
  )

  _flatten_mlir_python_targets(mlir_python_sources_deps MLIRPythonSources)
  list(FILTER mlir_python_sources_deps INCLUDE REGEX "^MLIRPythonSources.Dialects")
  foreach(t ${mlir_python_sources_deps})
    set_property(TARGET ${t} PROPERTY mlir_python_DEPENDS "")
  endforeach()
  set_property(TARGET MLIRPythonSources.ExecutionEngine PROPERTY mlir_python_DEPENDS "")

  add_mlir_python_modules(EUDSLPythonModules
    ROOT_PREFIX "${EUDSL_PYTHON_PACKAGES_DIR}/eudsl"
    INSTALL_PREFIX "${EUDSL_PYTHON_INSTALL_DIR}/eudsl"
    DECLARED_SOURCES
    ${mlir_python_sources_deps}
    MLIRPythonSources.Core.Python
    MLIRPythonSources.ExecutionEngine
    EUDSLPythonExtensions.MLIR
    EUDSLPythonSources
  )

  set(_other_extensions
    _mlir
    _mlirAsyncPasses
    _mlirDialectsLinalg
    _mlirDialectsPDL
    _mlirDialectsQuant
    _mlirDialectsSparseTensor
    _mlirDialectsTransform
    _mlirExecutionEngine
    _mlirGPUPasses
    _mlirLinalgPasses
    _mlirPythonTest
    _mlirRegisterEverything
    _mlirSparseTensorPasses
  )

  file(MAKE_DIRECTORY "${CMAKE_BINARY_DIR}/${EUDSL_PYTHON_INSTALL_DIR}/eudsl/_mlir_libs")

  foreach(ext ${_other_extensions})
    # Build time/directory creation.
    add_custom_target("symlink_${ext}"
      COMMAND ${CMAKE_COMMAND} -E create_symlink
      "_eudsl${PYTHON_MODULE_EXTENSION}"
      "${ext}${PYTHON_MODULE_EXTENSION}"
      DEPENDS EUDSLPythonExtensions
      WORKING_DIRECTORY "${CMAKE_BINARY_DIR}/${EUDSL_PYTHON_INSTALL_DIR}/eudsl/_mlir_libs"
    )
    add_dependencies(EUDSLPythonModules "symlink_${ext}")
    # Install time/directory creation.
    install(CODE "execute_process(
    COMMAND ${CMAKE_COMMAND} -E create_symlink
            _eudsl${PYTHON_MODULE_EXTENSION}
    ${ext}${PYTHON_MODULE_EXTENSION}
            WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}/${EUDSL_PYTHON_INSTALL_DIR}/eudsl/_mlir_libs
    )"
    )
  endforeach()
else()
  find_package(Clang ${LLVM_CLANG_VERSION} REQUIRED CONFIG)
  list(APPEND CMAKE_MODULE_PATH "${CLANG_CMAKE_DIR}")
  include(AddClang)
  include_directories(${CLANG_INCLUDE_DIRS})
  add_subdirectory(myClangCodeGen)
endif()