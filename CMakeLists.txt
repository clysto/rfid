cmake_minimum_required(VERSION 3.15)

project(RFID-InterChannel VERSION 1.0 LANGUAGES CXX C)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
set(CMAKE_CXX_FLAGS_RELEASE "-O3")

cmake_policy(SET CMP0148 OLD)

find_package(Gnuradio "3.10" REQUIRED COMPONENTS analog blocks digital fft filter)
find_package(spdlog REQUIRED)
find_package(Eigen3 REQUIRED)
find_package(OpenMP REQUIRED)

add_executable(track_inter_channel
    src/main.cpp
    src/global.cpp
    src/global.hpp
    src/rfid_block.cpp
    src/rfid_block.hpp
    src/extract_inter_channel.cpp
    src/extract_inter_channel.hpp
)

target_link_libraries(track_inter_channel
    gnuradio::gnuradio-runtime
    gnuradio::gnuradio-blocks
    gnuradio::gnuradio-digital
    spdlog::spdlog
    Eigen3::Eigen
    OpenMP::OpenMP_CXX
)

find_package(pybind11 REQUIRED)
pybind11_add_module(extract_inter_channel_cxx
    src/global.cpp
    src/global.hpp
    src/extract_inter_channel.cpp
    src/extract_inter_channel.hpp
    src/python/extract_inter_channel_python.cpp
)
target_link_libraries(extract_inter_channel_cxx
    PRIVATE
    spdlog::spdlog
    Eigen3::Eigen
    OpenMP::OpenMP_CXX
)

pybind11_add_module(epc_crc
    src/crc/crc.cpp
    src/crc/crc.hpp
    src/crc/crc5epc_c1g2.c
    src/crc/crc5epc_c1g2.h
    src/crc/crc16genibus.c
    src/crc/crc16genibus.h
)
