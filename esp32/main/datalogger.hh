// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#pragma once
#include "task.hh"

#include "SD.h"
#include <vector>
#include "datasampler.hh"


class DataLogger : public Task<DataLogger, 2000>
{
public:
  DataLogger(DataSampler& sampler);
  void task();

private:
  DataSampler& _sampler;
};
