# Event Handlers Documentation

This document describes the event handler system for the universal remote control.

## Overview

The event handler system allows you to register callback functions that are triggered when specific events occur in the remote control system. This enables:

- **Logging and debugging** - Track all button presses and IR transmissions
- **User feedback** - Provide visual/audio feedback for actions
- **State management** - React to state changes
- **Error handling** - Custom error handling logic
- **Universal TV integration** - Monitor scan mode and protocol attempts

## Event Types

### Button Events

#### `EVENT_BUTTON_PRESSED`
Triggered when a button is pressed.

**Handler Type**: `button_handler_t`
```c
int handler(unsigned char button_code, const char* button_name);
```

**Registration**:
```c
handler_register_button_pressed(my_button_handler);
```

**Trigger**:
```c
handler_trigger_button_pressed(BUTTON_POWER);
```

#### `EVENT_BUTTON_RELEASED`
Triggered when a button is released.

**Handler Type**: `button_handler_t`
```c
int handler(unsigned char button_code, const char* button_name);
```

**Registration**:
```c
handler_register_button_released(my_button_release_handler);
```

### IR Transmission Events

#### `EVENT_IR_TRANSMIT_START`
Triggered when IR transmission begins.

**Handler Type**: `ir_handler_t`
```c
int handler(ir_code_t code, int success);
```

**Registration**:
```c
handler_register_ir_transmit_start(my_ir_start_handler);
```

#### `EVENT_IR_TRANSMIT_COMPLETE`
Triggered when IR transmission completes successfully.

**Handler Type**: `ir_handler_t`
```c
int handler(ir_code_t code, int success);
```

**Registration**:
```c
handler_register_ir_transmit_complete(my_ir_complete_handler);
```

#### `EVENT_IR_TRANSMIT_ERROR`
Triggered when IR transmission fails.

**Handler Type**: `ir_handler_t`
```c
int handler(ir_code_t code, int success);
```

**Registration**:
```c
handler_register_ir_transmit_error(my_ir_error_handler);
```

### Error Events

#### `EVENT_ERROR`
Triggered when an error occurs.

**Handler Type**: `error_handler_t`
```c
int handler(error_type_t error, const char* message);
```

**Error Types**:
- `ERROR_NONE` - No error
- `ERROR_IR_NOT_INITIALIZED` - IR system not initialized
- `ERROR_INVALID_BUTTON` - Invalid button code
- `ERROR_INVALID_IR_CODE` - Invalid IR code
- `ERROR_TRANSMISSION_FAILED` - IR transmission failed
- `ERROR_HARDWARE_FAILURE` - Hardware initialization failed
- `ERROR_PROTOCOL_ERROR` - Unsupported protocol
- `ERROR_TIMEOUT` - Operation timed out
- `ERROR_UNIVERSAL_SCAN_FAILED` - Universal scan failed
- `ERROR_UNIVERSAL_NO_CODES` - No universal codes available

**Registration**:
```c
handler_register_error(my_error_handler);
```

**Trigger**:
```c
handler_trigger_error(ERROR_INVALID_BUTTON, "Unknown button code");
```

### Universal TV Events

#### `EVENT_UNIVERSAL_SCAN_STARTED`
Triggered when universal TV scan mode starts.

**Handler Type**: `universal_scan_handler_t`
```c
int handler(unsigned char button_code, uint16_t code_index, uint16_t total_codes);
```

**Registration**:
```c
handler_register_universal_scan_started(my_scan_start_handler);
```

**Trigger**:
```c
handler_trigger_universal_scan_started(BUTTON_POWER, 13);
```

#### `EVENT_UNIVERSAL_SCAN_NEXT`
Triggered when scanning to the next code in scan mode.

**Handler Type**: `universal_scan_handler_t`
```c
int handler(unsigned char button_code, uint16_t code_index, uint16_t total_codes);
```

**Registration**:
```c
handler_register_universal_scan_next(my_scan_next_handler);
```

**Trigger**:
```c
handler_trigger_universal_scan_next(BUTTON_POWER, 5, 13);
```

#### `EVENT_UNIVERSAL_SCAN_CONFIRMED`
Triggered when a code is confirmed in scan mode.

**Handler Type**: `universal_scan_handler_t`
```c
int handler(unsigned char button_code, uint16_t code_index, uint16_t total_codes);
```

**Registration**:
```c
handler_register_universal_scan_confirmed(my_scan_confirmed_handler);
```

**Trigger**:
```c
handler_trigger_universal_scan_confirmed(BUTTON_POWER, 5, 13);
```

#### `EVENT_UNIVERSAL_PROTOCOL_ATTEMPT`
Triggered when trying a different protocol in universal mode.

**Handler Type**: `universal_protocol_handler_t`
```c
int handler(uint8_t protocol, uint32_t code, const char* description);
```

**Registration**:
```c
handler_register_universal_protocol_attempt(my_protocol_handler);
```

**Trigger**:
```c
handler_trigger_universal_protocol_attempt(IR_PROTOCOL_NEC, 0x20DF10EF, "Samsung/LG NEC Power");
```

#### `EVENT_UNIVERSAL_BRAND_DETECTED`
Triggered when TV brand is detected or set.

**Handler Type**: `universal_brand_handler_t`
```c
int handler(uint8_t brand, const char* brand_name);
```

**Registration**:
```c
handler_register_universal_brand_detected(my_brand_handler);
```

**Trigger**:
```c
handler_trigger_universal_brand_detected(TV_BRAND_SAMSUNG, "Samsung");
```

## Usage Example

```c
#include "handlers.h"
#include "remote_control.h"
#include "universal_tv.h"

/* Define handler functions */
int on_button_pressed(unsigned char button_code, const char* button_name) {
    printf("Button pressed: %s\n", button_name);
    return HANDLER_SUCCESS;
}

int on_ir_transmit_start(ir_code_t code, int success) {
    (void)success;
    printf("IR transmission started: 0x%08X\n", code.code);
    return HANDLER_SUCCESS;
}

int on_universal_scan_next(unsigned char button_code, uint16_t code_index, uint16_t total_codes) {
    printf("Scanning code %d/%d for button 0x%02X\n", 
           code_index + 1, total_codes, button_code);
    return HANDLER_SUCCESS;
}

int main(void) {
    /* Initialize handler system */
    handler_init();
    
    /* Register handlers */
    handler_register_button_pressed(on_button_pressed);
    handler_register_ir_transmit_start(on_ir_transmit_start);
    handler_register_universal_scan_next(on_universal_scan_next);
    
    /* Use remote control - events will be triggered automatically */
    remote_init();
    remote_press_button(BUTTON_POWER);
    
    /* Use universal TV - events will be triggered automatically */
    universal_tv_init(UNIVERSAL_MODE_SCAN);
    universal_tv_scan_start(BUTTON_POWER);
    universal_tv_scan_next();
    
    /* Cleanup */
    handler_cleanup();
    return 0;
}
```

## Registering All Handlers at Once

You can register all handlers using a single structure:

```c
handlers_t my_handlers = {
    .button_pressed = on_button_pressed,
    .button_released = on_button_released,
    .ir_transmit_start = on_ir_transmit_start,
    .ir_transmit_complete = on_ir_transmit_complete,
    .error_handler = on_error,
    .universal_scan_started = on_scan_started,
    .universal_scan_next = on_scan_next,
    .universal_protocol_attempt = on_protocol_attempt,
    .universal_brand_detected = on_brand_detected
};

handler_register_all(&my_handlers);
```

## Handler Return Codes

Handlers should return one of these values:

- `HANDLER_SUCCESS` (0) - Handler processed event successfully
- `HANDLER_ERROR` (-1) - Handler encountered an error
- `HANDLER_IGNORE` (1) - Handler wants to ignore the event

## Custom Events

You can also create and trigger custom events:

```c
event_t custom_event;
custom_event.type = EVENT_CUSTOM;
custom_event.timestamp = 0;  /* Will be set automatically */
custom_event.data.custom.data = my_data;

handler_trigger_custom_event(&custom_event);
```

## Timer and Interrupt Handlers

For hardware-specific functionality:

```c
/* Timer handler */
int on_timer(uint32_t timer_id) {
    printf("Timer expired: %d\n", timer_id);
    return HANDLER_SUCCESS;
}

handler_register_timer(on_timer);
handler_setup_timer(1000);  /* 1 second interval */

/* Interrupt handler */
void on_interrupt(void) {
    printf("Hardware interrupt occurred\n");
}

handler_register_interrupt(on_interrupt);
handler_setup_interrupt(IRQ_GPIO);  /* Platform-specific */
```

## Best Practices

1. **Always initialize** - Call `handler_init()` before registering handlers
2. **Cleanup** - Call `handler_cleanup()` when done
3. **Keep handlers fast** - Don't block in handlers; use them for notifications
4. **Error handling** - Return appropriate error codes from handlers
5. **Thread safety** - If using threads, ensure handler registration is synchronized

## See Also

- `examples/event_handlers_example.c` - Complete working example
- `include/handlers.h` - Full API documentation
- `src/handlers.c` - Implementation details

