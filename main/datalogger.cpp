// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#include "datalogger.hh"

DataLogger::DataLogger(SDFS& sd)
  : _sd(sd)
{
  const auto path = "/test.log";
  _logfile = sd.open(path, FILE_WRITE);
}

void DataLogger::write(const std::vector<uint8_t>& data)
{
  _logfile.write(data.data(), data.size());
  _logfile.flush();
}
