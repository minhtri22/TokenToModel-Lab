cmake_minimum_required(VERSION 3.20)
project(ttm_t5_kvflash_probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT MSVC)
    message(FATAL_ERROR "PINNED_WINDOWS_MSVC_X64_REQUIRED")
endif()
if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "X64_ONLY")
endif()
if(NOT DEFINED LLAMA_SOURCE_ROOT OR NOT DEFINED LLAMA_BUILD_ROOT)
    message(FATAL_ERROR "PINNED_LLAMA_SOURCE_AND_IMPORT_LIB_ROOT_REQUIRED")
endif()
# LLAMA_BUILD_ROOT here refers to the original pinned build root
# _tmp/ttm_t2/build/upstream_llama, NOT llama.cpp/build.
foreach(header IN ITEMS
    "${LLAMA_SOURCE_ROOT}/include/llama.h"
    "${LLAMA_SOURCE_ROOT}/ggml/include/ggml.h"
    "${LLAMA_SOURCE_ROOT}/ggml/include/ggml-backend.h")
    if(NOT EXISTS "${header}")
        message(FATAL_ERROR "PINNED_HEADER_MISSING:${header}")
    endif()
endforeach()

set(LIB_FILES
    "${LLAMA_BUILD_ROOT}/src/Release/llama.lib"
    "${LLAMA_BUILD_ROOT}/ggml/src/Release/ggml.lib"
    "${LLAMA_BUILD_ROOT}/ggml/src/Release/ggml-base.lib")
foreach(lib IN LISTS LIB_FILES)
    if(NOT EXISTS "${lib}")
        message(FATAL_ERROR "PINNED_IMPORT_LIB_MISSING:${lib}")
    endif()
endforeach()
add_executable(ttm_t5_kvflash_probe ttm_t5_kvflash_probe_candidate.cpp)
target_include_directories(ttm_t5_kvflash_probe PRIVATE
    "${LLAMA_SOURCE_ROOT}/include"
    "${LLAMA_SOURCE_ROOT}/ggml/include")
target_link_libraries(ttm_t5_kvflash_probe PRIVATE ${LIB_FILES})
# DLL-based pinned upstream build is intentionally not rebuilt.
# Do not copy/execute this candidate as a science run until OwnerGate.
