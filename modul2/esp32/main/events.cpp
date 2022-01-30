// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved

#include "events.hpp"
#include "buttons.hpp"

#include <cstring>
#include <optional>

namespace unifhy::events {

namespace buttons {

void register_button_callback(button_events_t e,
                              std::function<void(button_events_t)> cb)
{
  deets::buttons::register_button_callback(
    gpio_num_t(e),
    [cb](gpio_num_t gpio) { cb(button_events_t(gpio)); }
    );
}

} // namespace buttons

} // namespace unifhy::events
