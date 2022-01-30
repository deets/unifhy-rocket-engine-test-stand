// Copyright: 2021, Diez B. Roggisch, Berlin, all rights reserved

#include "mqtt.hpp"

#include <esp_log.h>
#include <cstring>
#include <sstream>
#include <iomanip>

//#define LOG_LOCAL_LEVEL ESP_LOG_DEBUG

#define TAG "mqtt"

namespace unifhy::mqtt {


MQTTClient::MQTTClient()
{
  std::memset(&_config, 0, sizeof(esp_mqtt_client_config_t));
  _config.user_context = this;
  std::strncpy(_client_id, "unifhy", sizeof(_client_id));
  // we *must* give a host, otherwise the
  // next call bails out.
  std::strncpy(_hostname, "singlemalt.local", sizeof(_hostname));
  _config.client_id = _client_id;
  _config.host = _hostname;
  _client = esp_mqtt_client_init(&_config);
  esp_mqtt_client_register_event(
    _client,
    esp_mqtt_event_id_t(ESP_EVENT_ANY_ID),
    MQTTClient::s_handle_mqtt_event, this);
  esp_mqtt_client_start(_client);
}

int MQTTClient::publish(const char *topic, const char *data, int len, int qos,
                        int retain) {
  return esp_mqtt_client_publish(_client, topic, data, len, qos, retain);
}

void MQTTClient::s_handle_mqtt_event(void *event_handler_arg, esp_event_base_t event_base, int32_t event_id, void *event_data)
{
  static_cast<MQTTClient*>(event_handler_arg)->handle_mqtt_event(event_base, event_id, event_data);
}


void MQTTClient::handle_mqtt_event(esp_event_base_t event_base, int32_t event_id, void *event_data)
{
  const auto event = esp_mqtt_event_handle_t(event_data);
  // your_context_t *context = event->context;
  switch (event_id) {
  case MQTT_EVENT_CONNECTED:
    ESP_LOGD(TAG, "MQTT_EVENT_CONNECTED");
    break;
  case MQTT_EVENT_DISCONNECTED:
    ESP_LOGD(TAG, "MQTT_EVENT_DISCONNECTED");
    break;
  case MQTT_EVENT_SUBSCRIBED:
    ESP_LOGD(TAG, "MQTT_EVENT_SUBSCRIBED");
    break;
  case MQTT_EVENT_UNSUBSCRIBED:
    ESP_LOGD(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
    break;
  case MQTT_EVENT_PUBLISHED:
    ESP_LOGD(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
    // The MQTT_EVENTS are scoped to the client, so
    // I create this forwarding.
    _published_messages.erase(event->msg_id);
    if(_published_messages.empty())
    {
      ESP_LOGD(TAG, "published messages empty, signalling!");
    }
    break;
  case MQTT_EVENT_DATA:
    ESP_LOGD(TAG, "MQTT_EVENT_DATA");
    printf("TOPIC=%.*s\r\n", event->topic_len, event->topic);
    printf("DATA=%.*s\r\n", event->data_len, event->data);
    break;
  case MQTT_EVENT_ERROR:
    ESP_LOGD(TAG, "MQTT_EVENT_ERROR");
    break;
  default:
    ESP_LOGD(TAG, "Other event id:%d", event_id);
    break;
  }
}

} // namespace unifhy::mqtt
