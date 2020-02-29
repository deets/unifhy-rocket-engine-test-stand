#include "ringbuffer.hh"
#include <stdint.h>
#include <esp_log.h>
#include <tuple>

using adc_values_t = std::tuple<uint64_t, uint64_t>;

namespace {
constexpr int RING_BUFFER_SIZE = 4;
}

void ringbuffer_tests()
{
  RingBuffer<adc_values_t, RING_BUFFER_SIZE> ring_buffer;
  auto reader_1 = ring_buffer.reader();
  ESP_LOGI("rb", "rb is empty: %i", reader_1.empty());
  ring_buffer.append(adc_values_t{123, 456});
  ESP_LOGI("rb", "rb count == 1: %i", reader_1.count() == 1);
  auto reader_2 = ring_buffer.reader();
  ESP_LOGI("rb", "reader 2 is empty: %i", reader_2.empty());
  const auto value = reader_1.read();
  ESP_LOGI("rb", "value  == {123, 456}: %i", value == adc_values_t{123, 456});
  ESP_LOGI("rb", "rb is empty again: %i", reader_1.empty());

  // reader_1 points to element 1, and there is elements
  // 2, .., RING_BUFFER_SIZE-1, 0 available.
  // So we add RING_BUFFER_SIZE - 1 more, and must have a
  // size of RING_BUFFER_SIZE - 1
  for(int i=0; i < RING_BUFFER_SIZE - 1; ++i)
  {
    ring_buffer.append(adc_values_t{456, 123});
  }
  ESP_LOGI("rb", "rb contains 3 elements: %i", reader_1.count() == 3);
  ESP_LOGI("rb", "rb not overrun: %i", !reader_1.overrun());
  int count = 0;
  reader_1.consume([&count](const adc_values_t&) {
                     ESP_LOGI("rb", "I will consume!");
                     ++count;
                   });
  ESP_LOGI("rb", "rb consumed 3 elements: %i", count == 3);

  for(int i=0; i < RING_BUFFER_SIZE + 1; ++i)
  {
    ring_buffer.append(adc_values_t{456, 123});
  }
  ESP_LOGI("rb", "rb overrun: %i", reader_1.overrun());
}
