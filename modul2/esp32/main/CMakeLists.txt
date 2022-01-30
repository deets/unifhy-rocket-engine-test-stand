set(srcs
  main.cpp
  sdcard.hpp
  sdcard.cpp
  mqtt.hpp
  mqtt.cpp
  events.hpp
  events.cpp
  )

idf_component_register(
  SRCS ${srcs}
  INCLUDE_DIRS "."
  REQUIRES esp_http_server nvs_flash mqtt fatfs esp32deets app_update esp_http_client esp_https_ota mdns
  )
