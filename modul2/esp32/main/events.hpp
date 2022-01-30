// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved
#pragma once
#include "mqtt_client.h"
#include "pins.hpp"

#include <optional>
#include <vector>
#include <functional>

namespace unifhy::events {

namespace buttons {

enum button_events_t
{
  OTA = PIN_NUM_OTA,
};

void register_button_callback(button_events_t,
                              std::function<void(button_events_t)>);

} // namespace buttons
} // namespace unifhy::events
