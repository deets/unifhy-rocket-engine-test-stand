// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#pragma once
#include "ringbuffer.hh"

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/event_groups.h>

#include <stdint.h>
#include <tuple>

// 40 Bytes
using adc_values_t = std::tuple<uint64_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t>;

constexpr int RING_BUFFER_SIZE = 500;

class DataSampler
{
public:
  using value_t = adc_values_t;
  using ring_buffer_t = RingBuffer<value_t, RING_BUFFER_SIZE>;
  using reader_t = ring_buffer_t::Reader;

  DataSampler();

  void start();

  reader_t reader();

private:
  static void s_task(void*);
  void task();
  EventGroupHandle_t _event_group;
  StaticEventGroup_t _static_event_group;
  TaskHandle_t _task_handle;

  ring_buffer_t _buffer;
};
