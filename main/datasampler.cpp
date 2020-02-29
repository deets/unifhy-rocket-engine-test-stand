// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#include "datasampler.hh"

#include <driver/spi_master.h>
#include <esp_log.h>
#include <array>
#include <sstream>

#define DATA_SAMPLER_TASK_STACK_SIZE 2000

#define MOSI 13
#define MISO 12
#define CLK 14
#define CS 15
#define SPI_SPEED (2*1000*1000)


namespace {

StaticTask_t data_sampler_task_buffer;
StackType_t  data_sampler_task_stack[DATA_SAMPLER_TASK_STACK_SIZE];
std::array<uint32_t, 9> tx_buffer;
std::array<uint32_t, 9> rx_buffer;


} // end ns anonymous

DataSampler::DataSampler()
{
  _event_group = xEventGroupCreateStatic(&_static_event_group);
  _task_handle = xTaskCreateStaticPinnedToCore(
    DataSampler::s_task,       // Function that implements the task.
    "DST",          // Text name for the task.
    DATA_SAMPLER_TASK_STACK_SIZE,      // Stack size in bytes, not words.
    this,
    tskIDLE_PRIORITY + 1,// Priority at which the task is created.
    data_sampler_task_stack,          // Array to use as the task's stack.
    &data_sampler_task_buffer, // Variable to hold the task's data structure.
    1 // Core 1
    );
}

void DataSampler::start()
{
  xEventGroupSetBits(_event_group, 1);
}

void DataSampler::s_task(void* data)
{
  static_cast<DataSampler*>(data)->task();
}

void DataSampler::task()
{
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
  ESP_LOGI("data_sampler", "data_sampler waiting");

  // wait for our event to start
  while(!xEventGroupWaitBits(
          _event_group,    // The event group being tested.
          1,
          pdTRUE,         // BIT_0 should be cleared before returning.
          pdFALSE,        // Don't wait for both bits, either bit will do.
          pdMS_TO_TICKS(1000)
          )) {}

  ESP_LOGI("data_sampler", "data_sampler task started");
  auto last = esp_timer_get_time();

  // sentinel alue
  _buffer.append(
    adc_values_t{1, 2, 3, 4, 5, 6, 7, 8, 9}
    );
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

    auto now = esp_timer_get_time();
    const auto sample_period = now - last;
    _buffer.append(
      adc_values_t{now, sample_period, 0, 0, 0, 0, 0, 0, 0}
      );
    last = now;
    const auto delay = 500 - (now - before);
    if(delay > 0)
    {
      ets_delay_us(delay);
    }
  }
}

DataSampler::reader_t DataSampler::reader()
{
  return _buffer.reader();
}


const char* to_log_string(const adc_values_t& v)
{
  static std::stringstream buffer;
  static std::string res;
  buffer.seekp(0);
  buffer.seekg(0);
  buffer.clear();
  buffer << "adc:" << std::hex << std::get<0>(v) << ":";
  buffer << std::get<1>(v) << ":" << std::get<2>(v) << ":" << std::get<3>(v) << ":" << std::get<4>(v) << ":";
  buffer << std::get<5>(v) << ":" << std::get<6>(v) << ":" << std::get<7>(v) << ":" << std::get<8>(v);
  buffer << "\n";
  res = buffer.str();
  return res.c_str();
}
