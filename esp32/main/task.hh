// Copyright: 2020, Diez B. Roggisch, Berlin, all rights reserved
#pragma once

#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/event_groups.h>


template<typename T, int STACK_SIZE>
class Task
{
public:
  Task(const char* name, UBaseType_t priority, BaseType_t core)
  {
    _task_handle = xTaskCreateStaticPinnedToCore(
      Task::s_task,       // Function that implements the task.
      name,               // Text name for the task.
      STACK_SIZE,
      this,
      priority,           // Priority at which the task is created.
      &_task_stack[0],    // Array to use as the task's stack.
      &_task_buffer,      // Variable to hold the task's data structure.
      core
      );
  }

private:
  static void s_task(void* data)
  {
    static_cast<T*>(data)->task();
  }

  TaskHandle_t _task_handle;
  StaticTask_t _task_buffer;
  StackType_t  _task_stack[STACK_SIZE];
};
