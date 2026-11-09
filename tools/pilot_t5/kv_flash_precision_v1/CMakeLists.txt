cmake_minimum_required(VERSION 3.20)
project(ttm_t5_kvflash_probe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT MSVC)
    message(FATAL_ERROR "WIN64_MSVC_PINNED_BACKEND_REQUIRED")
endif()
if(NOT DEFINED LLAMA_SOURCE_ROOT OR NOT DEFINED LLAMA_BUILD_ROOT)
    message(FATAL_ERROR "MISSING_PINNED_LLAMA_SOURCE_OR_BUILD_ROOT")
endif()
foreach(header
    "${LLAMA_SOURCE_ROOT}/include/llama.h"
    "${LLAMA_SOURCE_ROOT}/ggml/include/ggml.h"
    "${LLAMA_SOURCE_ROOT}/ggml/include/ggml-backend.h")
    if(NOT EXISTS "${header}")
        message(FATAL_ERROR "PINNED_HEADER_MISSING:${header}")
    endif()
endforeach()
set(BINDIR "${LLAMA_BUILD_ROOT}")
set(LIB_FILES
    "${BINDIR}/src/Release/llama.lib"
    "${BINDIR}/ggml/src/Release/ggml.lib"
    "${BINDIR}/ggml/src/Release/ggml-base.lib")
foreach(lib IN LISTS LIB_FILES)
    if(NOT EXISTS "${lib}")
        message(FATAL_ERROR "PINNED_LLAMA_LIBRARY_MISSING:${lib}")
    endif()
endforeach()
add_executable(ttm_t5_kvflash_probe ttm_t5_kvflash_probe_candidate.cpp)
target_include_directories(ttm_t5_kvflash_probe PRIVATE
    "${LLAMA_SOURCE_ROOT}/include"
    "${LLAMA_SOURCE_ROOT}/ggml/include")
target_link_libraries(ttm_t5_kvflash_probe PRIVATE ${LIB_FILES})
