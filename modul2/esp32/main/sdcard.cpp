// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved
#include "sdcard.hpp"
#include "pins.hpp"

#include <dirent.h>
#include <fcntl.h>
#include <fstream>
#include <stdio.h>
#include <string.h>
#include <sys/unistd.h>
#include <sys/stat.h>
#include "esp_err.h"
#include "esp_vfs_fat.h"
#include "driver/sdspi_host.h"
#include "driver/spi_common.h"
#include "hal/gpio_types.h"
#include "hal/spi_types.h"
#include "sdkconfig.h"
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>

#include <iostream>
#include <sstream>
#include <iomanip>
#include <chrono>

//#define LOG_LOCAL_LEVEL ESP_LOG_DEBUG
#include "esp_log.h"

namespace unifhy::sdcard {

namespace {

static const char *TAG = "sdcard";

#define MOUNT_POINT "/sdcard"
static const char *s_mount_point = "/sdcard";

// DMA channel to be used by the SPI peripheral
#ifndef SPI_DMA_CHAN
#define SPI_DMA_CHAN    1
#endif //SPI_DMA_CHAN

void toggle_start()
{
  gpio_set_direction(PIN_NUM_START, gpio_mode_t(GPIO_MODE_DEF_OUTPUT));
  gpio_set_level(PIN_NUM_START, 1);
  vTaskDelay(pdMS_TO_TICKS(10));
  gpio_set_level(PIN_NUM_START, 0);
}

} // namespace

SDCardWriter::SDCardWriter()
  : _file(nullptr)
{
    esp_err_t ret;
    // Options for mounting the filesystem.
    // If format_if_mount_failed is set to true, SD card will be partitioned and
    // formatted in case when mounting fails.
    esp_vfs_fat_sdmmc_mount_config_t mount_config = {
        .format_if_mount_failed = true,
        .max_files = 5,
        .allocation_unit_size = 16 * 1024
    };

    ESP_LOGI(TAG, "Initializing SD card");

    _host = sdmmc_host_t SDSPI_HOST_DEFAULT();
    spi_bus_config_t bus_cfg = {
        .mosi_io_num = PIN_NUM_MOSI,
        .miso_io_num = PIN_NUM_MISO,
        .sclk_io_num = PIN_NUM_CLK,
        .quadwp_io_num = -1,
        .quadhd_io_num = -1,
        .max_transfer_sz = 4000,
	.flags = 0,
	.intr_flags = 0,
    };
    ret = spi_bus_initialize(spi_host_device_t(_host.slot), &bus_cfg, SPI_DMA_CHAN);
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to initialize bus.");
        return;
    }

    // This initializes the slot without card detect (CD) and write protect (WP) signals.
    // Modify slot_config.gpio_cd and slot_config.gpio_wp if your board has these signals.
    sdspi_device_config_t slot_config = SDSPI_DEVICE_CONFIG_DEFAULT();
    slot_config.gpio_cs = PIN_NUM_CS;
    slot_config.host_id = spi_host_device_t(_host.slot);


    toggle_start();
    ret = esp_vfs_fat_sdspi_mount(s_mount_point, &_host, &slot_config, &mount_config, &_card);

    if (ret != ESP_OK) {
        if (ret == ESP_FAIL) {
            ESP_LOGE(TAG, "Failed to mount filesystem. "
                "If you want the card to be formatted, set the EXAMPLE_FORMAT_IF_MOUNT_FAILED menuconfig option.");
        } else {
            ESP_LOGE(TAG, "Failed to initialize the card (%s). "
                "Make sure SD card lines have pull-up resistors in place.", esp_err_to_name(ret));
        }
        return;
    }
    // Card has been initialized, print its properties
    sdmmc_card_print_info(stdout, _card);
}

SDCardWriter::~SDCardWriter()
{
    // All done, unmount partition and disable SDMMC or SPI peripheral
    esp_vfs_fat_sdcard_unmount(s_mount_point, _card);
    ESP_LOGI(TAG, "Card unmounted");
    spi_bus_free(spi_host_device_t(_host.slot));
}


} // namespace
