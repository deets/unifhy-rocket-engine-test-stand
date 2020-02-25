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

#include "datalogger.hh"

#include <array>

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
const int SDCARD_MOUNT_WAIT = 1000;
const int WIFI_WAIT = 500;
const int SPI_SPEED = 2*1000*1000;

int32_t sampled_bytes;

TaskHandle_t data_sampler_task_handle;
StaticTask_t data_sampler_task_buffer;
StackType_t  data_sampler_task_stack[DATA_SAMPLER_TASK_STACK_SIZE];
StaticEventGroup_t data_sampler_task_event_group;

std::array<uint32_t, 9> tx_buffer;
std::array<uint32_t, 9> rx_buffer;

decltype(esp_timer_get_time()) sample_period;

void data_sampler_task(void* data)
{
  EventGroupHandle_t eg_handle = static_cast<EventGroupHandle_t>(data);
  esp_err_t ret;
  spi_device_handle_t spi;
  spi_bus_config_t buscfg = {
    .mosi_io_num=MOSI,
    .miso_io_num=MISO,
    .sclk_io_num=CLK,
    .quadwp_io_num=-1,
    .quadhd_io_num=-1,
    .max_transfer_sz=0,
    .flags=SPICOMMON_BUSFLAG_NATIVE_PINS,
    .intr_flags=0
  };

  spi_device_interface_config_t devcfg = {
    .command_bits=0,
    .address_bits=0,
    .dummy_bits=0,
    .mode=0,
    .duty_cycle_pos=0,
    .cs_ena_pretrans=16,
    .cs_ena_posttrans=0,
    .clock_speed_hz=SPI_SPEED,
    .input_delay_ns=0,
    .spics_io_num=CS,
    .flags=SPI_DEVICE_TXBIT_LSBFIRST|SPI_DEVICE_RXBIT_LSBFIRST,
    .queue_size=1,
    .pre_cb=nullptr,
    .post_cb=nullptr
  };
  //Initialize the SPI bus
  ret = spi_bus_initialize(HSPI_HOST, &buscfg, 0);
  ESP_ERROR_CHECK(ret);
  ret = spi_bus_add_device(HSPI_HOST, &devcfg, &spi);
  ESP_ERROR_CHECK(ret);

  // wait for our event to start
  while(!xEventGroupWaitBits(
          eg_handle,    // The event group being tested.
          1,
          pdTRUE,         // BIT_0 should be cleared before returning.
          pdFALSE,        // Don't wait for both bits, either bit will do.
          pdMS_TO_TICKS(1000)
          )) {}

  ESP_LOGI("data_sampler", "data_sampler task started");
  auto last = esp_timer_get_time();

  for(;;)
  {
    const auto before = esp_timer_get_time();
    spi_transaction_t t;
    t.length = 9 * 32;
    t.rxlength = 0;
    t.tx_buffer = tx_buffer.data();
    t.rx_buffer = rx_buffer.data();
    t.flags = 0;
    ret = spi_device_polling_transmit(spi, &t);  // synchronous
    ESP_ERROR_CHECK(ret);
    sampled_bytes += 9 * 4;

    auto now = esp_timer_get_time();
    sample_period = now - last;
    last = now;
    const auto delay = 500 - (now - before);
    if(delay > 0)
    {
      ets_delay_us(delay);
    }
  }
}

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

  auto event_group = xEventGroupCreateStatic(&data_sampler_task_event_group);

  data_sampler_task_handle = xTaskCreateStaticPinnedToCore(
    data_sampler_task,       // Function that implements the task.
    "LPT",          // Text name for the task.
    DATA_SAMPLER_TASK_STACK_SIZE,      // Stack size in bytes, not words.
    event_group,
    tskIDLE_PRIORITY + 1,// Priority at which the task is created.
    data_sampler_task_stack,          // Array to use as the task's stack.
    &data_sampler_task_buffer, // Variable to hold the task's data structure.
    1 // Core 1
    );

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
  WiFiClient client;
  connect_wifi(client);

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

  std::vector<uint8_t> wifi_buffer;
  std::vector<uint8_t> buffer;
  xEventGroupSetBits(event_group, 1);
  decltype(sample_period) max_period = 0;
  for( ;; )
  {
    auto bytes_to_transfer = sampled_bytes;
    if(sample_period > max_period)
    {
      max_period = sample_period;
      ESP_LOGE("main", "max sample period: %llu", max_period);
    }

    if(buffer.capacity() < bytes_to_transfer)
    {
      bytes_to_transfer = std::min(bytes_to_transfer, 50000);
      ESP_LOGI("main", "resizing buffer %i", bytes_to_transfer);
      buffer.resize(bytes_to_transfer);
      wifi_buffer.resize(bytes_to_transfer / 10);
    }
    ESP_LOGI("main", "wifi buffer size: %i", wifi_buffer.size());
    if(client.connected())
    {
      client.write(wifi_buffer.data(), wifi_buffer.size());
    }

    logger.write(buffer);
    sampled_bytes -= bytes_to_transfer;
    vTaskDelay(pdMS_TO_TICKS(MAINLOOP_WAIT));
  }
}
