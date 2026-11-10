cmake_minimum_required(VERSION 3.20)
project(ttm_t5_firstop_gelu_erf_trace_probe LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT MSVC OR NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "TTM_T5_DIAG_REQUIRES_MSVC_WINDOWS_X64")
endif()
if(NOT DEFINED LLAMA_SOURCE_ROOT OR NOT DEFINED LLAMA_BUILD_ROOT)
    message(FATAL_ERROR "PINNED_LLAMA_SOURCE_AND_BUILD_ROOT_REQUIRED")
endif()
foreach(header IN ITEMS
    "${LLAMA_SOURCE_ROOT}/include/llama.h"
    "${LLAMA_SOURCE_ROOT}/ggml/include/ggml.h"
    "${LLAMA_SOURCE_ROOT}/ggml/include/ggml-backend.h")
    if(NOT EXISTS "${header}")
        message(FATAL_ERROR "LLAMA_HEADER_NOT_FOUND:${header}")
    endif()
endforeach()
set(LLAMA_LIBS
    "${LLAMA_BUILD_ROOT}/src/Release/llama.lib"
    "${LLAMA_BUILD_ROOT}/ggml/src/Release/ggml.lib"
    "${LLAMA_BUILD_ROOT}/ggml/src/Release/ggml-base.lib")
foreach(lib IN LISTS LLAMA_LIBS)
    if(NOT EXISTS "${lib}")
        message(FATAL_ERROR "PINNED_LIB_MISSING:${lib}")
    endif()
endforeach()
add_executable(ttm_t5_firstop_trace_probe ttm_t5_firstop_trace_probe.cpp)
target_include_directories(ttm_t5_firstop_trace_probe PRIVATE
    "${LLAMA_SOURCE_ROOT}/include"
    "${LLAMA_SOURCE_ROOT}/ggml/include")
target_link_libraries(ttm_t5_firstop_trace_probe PRIVATE ${LLAMA_LIBS})
# This is a discovery probe, not a historical batch runner.
# Run only after prereg and exact SHA-of-build candidate verification.
