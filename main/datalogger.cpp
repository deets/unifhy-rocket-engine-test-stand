// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#include "datalogger.hh"

DataLogger::DataLogger(SDFS& sd)
  : _sd(sd)
{
  const auto path = "/test.log";
  _logfile = sd.open(path, FILE_WRITE);
}

void DataLogger::write(const char* string)
{
  _logfile.write(reinterpret_cast<const uint8_t*>(string), strlen(string));
  _logfile.flush();
}
