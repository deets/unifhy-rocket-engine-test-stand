// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#pragma once
#include "SD.h"
#include <vector>
#include "datasampler.hh"

class DataLogger
{
public:
  DataLogger(SDFS&);

  void write(const char* string);
  void flush();

  template<typename Item>
  void log(const Item& data)
  {
    write(to_log_string(data));
  }

private:
  SDFS& _sd;
  File _logfile;
};
