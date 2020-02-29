#include "datalogger.hh"
#include "ringbuffer.hh"
#include "datasampler.hh"

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/spi_master.h>
#include <nvs_flash.h>

// Arduino stuff
#include "SPI.h"
#include "FS.h"
#include "SD.h"
#include "vfs_api.h"
#include "sd_diskio.h"
#include "ff.h"
#include "FS.h"
#include <WiFi.h>

extern "C" void app_main();

#define SSID "TP-LINK_2.4GHz_BBADE9"
#define PASSWORD "51790684"
#define HOST "192.168.2.105"

// We use the default VSPI
// pins as found in
// https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/spi_master.html#gpio-matrix-and-io-mux
// and also in the arduino specific
// components/arduino/variants/esp32/pins_arduino.h

namespace {

const int MAINLOOP_WAIT = 100;
const int SDCARD_MOUNT_WAIT = 1000;
const int WIFI_WAIT = 500;


void connect_wifi(WiFiClient& client)
{
  ESP_LOGI("main", "connecting to WiFi");
  WiFi.begin(SSID, PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    vTaskDelay(pdMS_TO_TICKS(WIFI_WAIT));
    ESP_LOGI("main", "...connecting");
  }
  ESP_LOGI("main", "connected");

  const int httpPort = 10000;
  if (!client.connect(HOST, httpPort)) {
    ESP_LOGI("main", "connection to host failed");
    return;
  }
}

} // end ns anon

void app_main()
{
  nvs_flash_init();

  auto data_sampler = std::unique_ptr<DataSampler>(new DataSampler());

  SPIClass spi(VSPI);
  SDFS sd(FSImplPtr(new VFSImpl()));

  for(;;)
  {
    vTaskDelay(pdMS_TO_TICKS(SDCARD_MOUNT_WAIT));
    if(!sd.begin(SS, spi))
    {
      ESP_LOGE("main", "SD card mount failed, retrying!");
    }
    else
    {
      break;
    }
  }
  // WiFiClient client;
  // connect_wifi(client);

  const auto card_type = sd.cardType();
  switch(card_type)
  {
  case CARD_NONE:
    ESP_LOGI("main", "No SD card attached");
    break;
  case CARD_MMC:
    ESP_LOGI("main", "MMC card attached");
    break;
  case CARD_SD:
    ESP_LOGI("main", "SD card attached");
    break;
  case CARD_SDHC:
    ESP_LOGI("main", "SDHC card attached");
    break;
  default:
    ESP_LOGI("main", "No SD card attached");
    break;
  }
  uint64_t cardSize = sd.cardSize() / (1024 * 1024);
  ESP_LOGI("main", "SD Card Size: %lluMB\n", cardSize);

  DataLogger logger(sd);

  std::vector<DataSampler::value_t> buffer;

  auto sd_card_buffer_reader = data_sampler->reader();
  data_sampler->start();
  logger.write("-----START-----");
  for( ;; )
  {
    ESP_LOGI("main", "loop, buffer size: %i, overrun: %i", buffer.capacity(), sd_card_buffer_reader.overrun_count());
    buffer.clear();
    sd_card_buffer_reader.consume(
      [&buffer](const DataSampler::value_t& adc_values)
      {
        buffer.push_back(adc_values);
      }
      );
    // if(client.connected())
    // {
    //   client.write(wifi_buffer.data(), wifi_buffer.size());
    // }

    logger.write(buffer);
    vTaskDelay(pdMS_TO_TICKS(MAINLOOP_WAIT));
  }
}
