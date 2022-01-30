// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved

#pragma once

#include <mqtt_client.h>

#include <set>

namespace unifhy::mqtt {

class MQTTClient
{
public:
  MQTTClient();

  int publish(const char *topic, const char *data, int len=0, int qos=0, int retain=0);

private:

  static void s_handle_mqtt_event(void *event_handler_arg, esp_event_base_t event_base, int32_t event_id, void *event_data);
  void handle_mqtt_event(esp_event_base_t event_base, int32_t event_id, void *event_data);

  esp_mqtt_client_config_t _config;
  esp_mqtt_client_handle_t _client;

  char _client_id[200];
  char _hostname[200];

  size_t _counter;

  std::set<int> _published_messages;
};

} // namespace beehive::mqtt
