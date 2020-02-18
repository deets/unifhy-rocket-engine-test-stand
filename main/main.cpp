#include <esp_log.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <driver/spi_master.h>

#include <array>

extern "C" void app_main();

#define LAPTIMER_TASK_STACK_SIZE 2000

#define MOSI 13
#define MISO 12
#define CLK 14
#define CS 27

namespace {

const int SPI_SPEED = 2*1000*1000;


TaskHandle_t laptimer_task_handle;
StaticTask_t laptimer_task_buffer;
StackType_t  laptimer_task_stack[LAPTIMER_TASK_STACK_SIZE];

std::array<uint32_t, 9> tx_buffer;
std::array<uint32_t, 9> rx_buffer;

void laptimer_task(void* data)
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
    .flags=0,
    .intr_flags=0
  };

  spi_device_interface_config_t devcfg = {
    .command_bits=0,
    .address_bits=0,
    .dummy_bits=0,
    .mode=0,
    .duty_cycle_pos=0,
    .cs_ena_pretrans=0,
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
  ret = spi_bus_initialize(VSPI_HOST, &buscfg, 0);
  ESP_ERROR_CHECK(ret);
  ret = spi_bus_add_device(VSPI_HOST, &devcfg, &spi);
  ESP_ERROR_CHECK(ret);

  ESP_LOGI("laptimer", "laptimer task started");
  for(;;)
  {
    ets_delay_us(500);
    spi_transaction_t t;
    t.length = 9 * 32;
    t.rxlength = 9 * 32;
    t.tx_buffer = tx_buffer.data();
    t.rx_buffer = rx_buffer.data();
    t.flags = 0;
    ret = spi_device_transmit(spi, &t);  // synchronous
    ESP_ERROR_CHECK(ret);
  }
}

} // end ns anon

void app_main()
{
  laptimer_task_handle = xTaskCreateStaticPinnedToCore(
    laptimer_task,       // Function that implements the task.
    "LPT",          // Text name for the task.
    LAPTIMER_TASK_STACK_SIZE,      // Stack size in bytes, not words.
    nullptr,
    tskIDLE_PRIORITY + 1,// Priority at which the task is created.
    laptimer_task_stack,          // Array to use as the task's stack.
    &laptimer_task_buffer, // Variable to hold the task's data structure.
    1 // Core 1
    );

}
