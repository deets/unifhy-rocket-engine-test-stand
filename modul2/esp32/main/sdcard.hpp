// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved

#pragma once

#include "sdcard.hpp"
#include "sdmmc_cmd.h"

#include <string>

namespace unifhy::sdcard {

class SDCardWriter
{
public:
  SDCardWriter();
  ~SDCardWriter();

  std::tuple<std::string, size_t, int64_t, int64_t> write_file(const size_t buffer_size, const size_t times);

private:
  size_t count_files();

  sdmmc_card_t* _card;
  sdmmc_host_t _host;

  size_t _file_count;
};

} // namespace unifhy::sdcard
