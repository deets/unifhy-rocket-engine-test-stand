// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#pragma once
#include "SD.h"
#include <vector>

class DataLogger
{
public:
  DataLogger(SDFS&);

  void write(const char* string);

  template<typename BufferType>
  void write(const BufferType& data)
  {
    const auto data_p = reinterpret_cast<const uint8_t*>(data.data());
    _logfile.write(data_p, data.size() * sizeof(typename BufferType::value_type));
    _logfile.flush();
  }

private:
  SDFS& _sd;
  File _logfile;
};
