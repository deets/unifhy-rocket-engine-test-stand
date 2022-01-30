#include "pins.hpp"
#include "sdcard.hpp"
#include "mqtt.hpp"
#include "events.hpp"

#include "wifi.hpp"
#include "buttons.hpp"
#include "smartconfig.hpp"

#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/spi_master.h>

extern "C" void app_main();

#define TAG "main"

namespace {

}

void app_main()
{
  ESP_ERROR_CHECK(esp_event_loop_create_default());
  deets::buttons::setup({
       { PIN_NUM_OTA, deets::buttons::pull_e::UP, deets::buttons::irq_e::NEG }
    });

  unifhy::events::buttons::register_button_callback(
    unifhy::events::buttons::OTA,
    [](unifhy::events::buttons::button_events_t) {
      if(deets::wifi::connected())
      {
        ESP_LOGI(TAG, "Connected to WIFI, run OTA");
        //start_ota_task();
      }
      else
      {
        ESP_LOGI(TAG, "Not connected to WIFI, running smartconfig");
        deets::smartconfig::run();
      }
    }
    );

  deets::wifi::setup();

  // unifhy::sdcard::SDCardWriter writer;
  unifhy::mqtt::MQTTClient mqtt_client;
  for( ;; )
  {
    vTaskDelay(pdMS_TO_TICKS(1000));
    mqtt_client.publish("write_rate", "test");
  }
}
