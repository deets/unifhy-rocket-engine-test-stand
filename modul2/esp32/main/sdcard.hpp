// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved

#pragma once

#include "sdcard.hpp"
#include "sdmmc_cmd.h"

namespace unifhy::sdcard {

class SDCardWriter
{
public:
  SDCardWriter();
  ~SDCardWriter();

  sdmmc_card_t* _card;
  sdmmc_host_t _host;

  FILE* _file;
};

} // namespace unifhy::sdcard
