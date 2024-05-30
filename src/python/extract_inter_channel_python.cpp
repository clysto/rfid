#include <pybind11/complex.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "../extract_inter_channel.hpp"

PYBIND11_MODULE(extract_inter_channel_cxx, m) {
  m.def("extract_inter_channel", &extract_inter_channel, "Extract inter channel from RN16 frame.");
}
