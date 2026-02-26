# 📡 IR Signal Visualization System

## Overview

The IR Signal Visualization System provides a **complete technical breakdown** of IR signal transmission, showing:

1. **Button Press → Protocol → Code → Transmission Timeline**
2. **Timing Graphs** - Visual representation of mark/space timing
3. **Carrier Waveform Simulation** - 38kHz modulated signal visualization

## Features

### 1. Transmission Timeline 📋
Shows the complete sequence of events when a button is pressed:
- **Header Mark/Space**: Initial synchronization pulses
- **Data Bits**: Each bit with its mark and space timing
- **Total Duration**: Complete transmission time
- **Event-by-event breakdown**: Detailed timing for each phase

### 2. Timing Graph 📊
Visual representation of the IR signal timing:
- **Mark periods** (red): High signal periods
- **Space periods** (cyan): Low signal periods
- **Horizontal axis**: Time progression
- **Vertical axis**: Signal level (high/low)
- **Grid lines**: Time reference markers

### 3. Carrier Waveform Simulation 🌊
Shows the actual 38kHz carrier waveform:
- **Modulated signal**: Carrier frequency visualization
- **First mark period**: Detailed view of carrier during transmission
- **Sine wave pattern**: Actual waveform shape
- **Frequency display**: 38kHz carrier frequency

### 4. Protocol Details 📝
Displays:
- **Protocol type**: NEC, RC5, RC6, Sony, Phillips
- **IR Code**: Hexadecimal code value
- **Frequency**: Carrier frequency (38kHz)
- **Duration**: Total transmission time

## Supported Protocols

### NEC Protocol
- **Header**: 9ms mark, 4.5ms space
- **Bits**: 32 bits
- **Timing**: 560μs mark, 560μs (0) / 1.69ms (1) space
- **Used for**: Power, Volume, Home, YouTube, Netflix

### RC5 Protocol
- **Header**: 889μs mark/space
- **Bits**: 14 bits
- **Timing**: Manchester encoding (889μs)
- **Used for**: Channel Up/Down

### RC6 Protocol
- **Header**: 2.666ms mark, 889μs space
- **Bits**: 20 bits
- **Timing**: 444μs mark, 444μs (0) / 1.333ms (1) space
- **Used for**: Streaming services

### Sony SIRC Protocol
- **Header**: 2.4ms mark, 600μs space
- **Bits**: 12 bits
- **Timing**: 600μs mark, 600μs (0) / 1.2ms (1) space

### Phillips Protocol
- **Header**: 9ms mark, 4.5ms space
- **Bits**: 32 bits
- **Timing**: Similar to NEC
- **Used for**: Input/Source switching

## How It Works

### Button Press Flow
```
Button Press
    ↓
Protocol Selection (based on button)
    ↓
IR Code Generation
    ↓
Timeline Generation (mark/space sequence)
    ↓
Timing Graph Rendering
    ↓
Carrier Waveform Simulation
    ↓
Display Visualization Panel
```

### Protocol Selection
Each button is mapped to a specific protocol:
- **Power, Volume, Home**: NEC
- **Channel Up/Down**: RC5
- **Streaming Services**: RC6
- **Input/Source**: Phillips

### Timeline Generation
For each protocol:
1. Generate header (mark + space)
2. For each data bit:
   - Generate mark pulse
   - Generate space (0 or 1 based on bit value)
3. Calculate total duration

### Waveform Simulation
- Samples at 1MHz rate
- Generates 38kHz sine wave
- Shows modulated carrier during mark periods
- Displays first mark period in detail

## Visual Panel

The visualization panel appears in the **top-right corner** when a button is pressed:
- **Position**: Fixed, top-right
- **Size**: 400px wide
- **Auto-hide**: Disappears after 5 seconds
- **Style**: Dark theme with blue accents

### Panel Sections:
1. **Timeline**: Event-by-event breakdown
2. **Timing Graph**: Visual timing representation
3. **Carrier Waveform**: 38kHz signal visualization
4. **Details**: Protocol, code, frequency, duration

## Usage

### Automatic Display
The visualization **automatically appears** when:
- Any button is pressed on the 3D remote
- Button is pressed via C program
- Button is pressed via WebSocket

### Manual Trigger (Browser Console)
```javascript
// Trigger visualization for specific button
startIRVisualization(0x10, 'Power');
startIRVisualization(0x01, 'YouTube');
startIRVisualization(0x14, 'Channel Up');
```

### Close Visualization
```javascript
stopIRVisualization();
```

## Technical Details

### Timing Accuracy
- **Microsecond precision**: All timings in microseconds
- **Protocol-accurate**: Matches real IR protocol specifications
- **Real-time calculation**: Generated on-the-fly

### Waveform Simulation
- **Sample rate**: 1MHz (1,000,000 samples/second)
- **Carrier frequency**: 38kHz (38,000 Hz)
- **Samples per period**: ~26 samples per carrier cycle
- **Display**: Shows first mark period in detail

### Performance
- **Lightweight**: Canvas-based rendering
- **Efficient**: Only renders when active
- **Smooth**: 60 FPS when visible

## Example Visualizations

### Power Button (NEC)
- **Protocol**: NEC
- **Code**: 0x00000001
- **Duration**: ~67ms
- **Bits**: 32 bits
- **Timing**: Standard NEC timing

### YouTube Button (RC6)
- **Protocol**: RC6
- **Code**: 0x12345678
- **Duration**: ~45ms
- **Bits**: 20 bits
- **Timing**: RC6 timing with longer spaces for 1s

### Channel Up (RC5)
- **Protocol**: RC5
- **Code**: 0x00000005
- **Duration**: ~25ms
- **Bits**: 14 bits
- **Timing**: Manchester encoding

## Future Enhancements

Potential additions:
- **Multiple protocol attempts**: Show all protocols tried
- **Repeat transmission**: Show repeat sequences
- **Error visualization**: Show failed transmissions
- **Protocol comparison**: Side-by-side protocol views
- **Export data**: Save timing data to file
- **Interactive controls**: Pause, step through timeline
- **3D waveform view**: 3D representation of signal

---

**Explore the technical details of IR transmission!** 📡✨

