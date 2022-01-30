// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved

#pragma once

#include "hal/gpio_types.h"

#define PIN_NUM_OTA gpio_num_t(0)

// Pin mapping when using SPI mode.
// With this mapping, SD card can be used both in SPI and 1-line SD mode.
// Note that a pull-up on CS line is required in SD mode.

#define PIN_NUM_MISO gpio_num_t(2)
#define PIN_NUM_MOSI gpio_num_t(15)
#define PIN_NUM_CLK  gpio_num_t(14)
#define PIN_NUM_CS   gpio_num_t(13)

#define PIN_NUM_START gpio_num_t(26)

#define SDA gpio_num_t(26)
#define SCL gpio_num_t(27)
