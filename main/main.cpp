#include "datalogger.hh"
#include "ringbuffer.hh"
#include "datasampler.hh"

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/spi_master.h>
#include <nvs_flash.h>

#include <WiFi.h>

extern "C" void app_main();

#define DATA_SAMPLER_TASK_STACK_SIZE 2000

#define MOSI 13
#define MISO 12
#define CLK 14
#define CS 15

#define SSID "SSID"
#define PASSWORD "PASSWORD"
#define HOST "192.168.2.105"

// We use the default VSPI
// pins as found in
// https://docs.espressif.com/projects/esp-idf/en/latest/api-reference/peripherals/spi_master.html#gpio-matrix-and-io-mux
// and also in the arduino specific
// components/arduino/variants/esp32/pins_arduino.h

namespace {

const int MAINLOOP_WAIT = 100;
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

  auto sd_card_logger = std::unique_ptr<DataLogger>(new DataLogger(*data_sampler));

  data_sampler->start();
  for( ;; )
  {
    // if(client.connected())
    // {
    //   client.write(wifi_buffer.data(), wifi_buffer.size());
    // }
    vTaskDelay(pdMS_TO_TICKS(MAINLOOP_WAIT));
  }
}
