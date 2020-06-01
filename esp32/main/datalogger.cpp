// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#include "datalogger.hh"

// Arduino stuff
#include "SPI.h"
#include "FS.h"
#include "SD.h"
#include "vfs_api.h"
#include "sd_diskio.h"
#include "ff.h"
#include "FS.h"

namespace {

const int MAINLOOP_WAIT = 100;
const int SDCARD_MOUNT_WAIT = 1000;
const int SDCARD_SPI_SPEED = 16000000;

} // end ns anonymous
DataLogger::DataLogger(DataSampler& sampler)
  : Task("SCD", tskIDLE_PRIORITY + 1, 0)
  , _sampler(sampler)
{
}

void DataLogger::task()
{
  SPIClass spi(VSPI);
  SDFS sd(FSImplPtr(new VFSImpl()));

  for(;;)
  {
    vTaskDelay(pdMS_TO_TICKS(SDCARD_MOUNT_WAIT));
    if(!sd.begin(SS, spi, SDCARD_SPI_SPEED))
    {
      ESP_LOGE("main", "SD card mount failed, retrying!");
    }
    else
    {
      break;
    }
  }

  uint64_t cardSize = sd.cardSize() / (1024 * 1024);
  ESP_LOGI("main", "SD Card Size: %lluMB\n", cardSize);

  const auto path = "/test.log";
  auto logfile = sd.open(path, FILE_WRITE);

  auto reader = _sampler.reader();

  int bytes_written = 0;
  for( ;; )
  {
    ESP_LOGI("dl", "overrun: %i", reader.overrun_count());

    reader.consume(
      [&bytes_written, &logfile](const DataSampler::value_t& adc_values)
      {
        const auto line = to_log_string(adc_values);
        const auto count = strlen(line);
        bytes_written += count;
        logfile.write(reinterpret_cast<const uint8_t*>(line), count);
      }
      );
    if(bytes_written > 4096)
    {
      logfile.flush();
      bytes_written = 0;
    }
    vTaskDelay(pdMS_TO_TICKS(MAINLOOP_WAIT));
  }
}
