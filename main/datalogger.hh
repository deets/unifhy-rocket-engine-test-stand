// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#pragma once
#include "SD.h"
#include <vector>

class DataLogger
{
public:
  DataLogger(SDFS&);

  void write(const std::vector<uint8_t>&);
private:
  SDFS& _sd;
  File _logfile;
};
