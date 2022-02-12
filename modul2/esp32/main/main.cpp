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
#include <sstream>
#include <condition_variable>

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

  std::mutex m;
  std::condition_variable cv;


  unifhy::events::buttons::register_button_callback(
    unifhy::events::buttons::OTA,
    [&cv](unifhy::events::buttons::button_events_t) {
      if(deets::wifi::connected())
      {
        ESP_LOGI(TAG, "Connected to WIFI, run write");
        cv.notify_one();
      }
      else
      {
        ESP_LOGI(TAG, "Not connected to WIFI, running smartconfig");
        deets::smartconfig::run();
      }
    }
    );

  deets::wifi::setup();

  unifhy::sdcard::SDCardWriter writer;
  unifhy::mqtt::MQTTClient mqtt_client;

  for( ;; )
  {
    std::unique_lock<std::mutex> lk(m);
    cv.wait(lk);
    const auto [ name, count, start, end ] = writer.write_file(2048, 5);
    std::stringstream ss;
    ss << name << ":count=" << count << ":start=" << start << ":end=" << end;
    mqtt_client.publish("write_rate", ss.str().c_str());
  }
}
