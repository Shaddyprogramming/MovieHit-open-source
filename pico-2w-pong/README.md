# Raspberry Pi Pico 2W WiFi Pong Game

A robust WiFi-enabled Pong game designed to run reliably on Raspberry Pi Pico 2W as `code.py` with comprehensive error handling and non-blocking network operations.

## Features

- **Physical Controls**: Button-based paddle control
- **Web Remote**: WiFi web interface for remote control
- **LED Indicators**: Status, WiFi, and game state LEDs
- **60 FPS Gameplay**: Smooth game loop optimized for CircuitPython
- **AI Opponent**: Configurable difficulty AI player
- **Score Tracking**: First to 5 points wins
- **Robust Operation**: Designed to handle all edge cases when running as `code.py`

## Hardware Requirements

### Components
- Raspberry Pi Pico 2W
- 3x Push buttons (for Up, Down, Reset)
- 2x LEDs + resistors (WiFi and Game status)
- Breadboard and jumper wires

### Wiring Diagram

```
Pico 2W Pin Connections:
├── GP15 → UP Button (with pull-up)
├── GP14 → DOWN Button (with pull-up) 
├── GP13 → RESET Button (with pull-up)
├── GP16 → WiFi Status LED (+resistor)
├── GP17 → Game Status LED (+resistor)
└── LED → Built-in status LED
```

### Button Wiring
```
Button → GPIO Pin → 3.3V
         └── 10kΩ pull-up resistor → 3.3V
```

### LED Wiring
```
GPIO Pin → 220Ω resistor → LED Anode → LED Cathode → GND
```

## Installation

1. **Install CircuitPython**: Flash CircuitPython 8.0+ onto your Pico 2W
2. **Copy Files**: Place both `code.py` and `config.py` in the root directory of the Pico 2W
3. **Configure WiFi**: Edit the WiFi credentials in `config.py`
4. **Hardware Setup**: Wire buttons and LEDs according to the diagram above

## Configuration

Edit `config.py` to customize:

```python
# WiFi Settings
WIFI_SSID = "YourWiFiNetwork"
WIFI_PASSWORD = "YourPassword"

# Game Settings  
FPS = 60
AI_DIFFICULTY = 0.8  # 0.0 (easy) to 1.0 (hard)
WIN_SCORE = 5

# Hardware pins can be changed if needed
```

## Usage

### Running the Game

1. **Automatic Start**: Simply power on the Pico 2W - the game will start automatically
2. **Manual Start**: Reset the Pico 2W or run `code.py` through Thonny

### Controls

#### Physical Buttons
- **UP Button**: Move paddle up
- **DOWN Button**: Move paddle down  
- **RESET Button**: Reset game score

#### Web Remote Control
1. Connect to the same WiFi network as the Pico
2. Find the Pico's IP address in the serial output
3. Open `http://[pico-ip-address]` in a web browser
4. Use the on-screen buttons to control the game

### LED Status Indicators

- **Built-in LED**: System status (on = running)
- **WiFi LED**: Network connectivity (on = connected)
- **Game LED**: Game active (on = game running)

## Reliability Features

### Robust Startup
- 3-second hardware stabilization delay
- Retry logic for pin initialization
- Graceful fallback if hardware fails
- WiFi connection with timeout and retries

### Error Handling
- Comprehensive exception catching
- Graceful degradation for network failures  
- Memory management with periodic garbage collection
- Safe pin access with error recovery

### Performance Optimization
- Non-blocking network operations (0.01s timeout)
- Memory-efficient game state using namedtuples
- 60 FPS timing control with frame rate limiting
- Optimized game loop for CircuitPython

### Network Reliability
- Non-blocking socket operations
- Connection timeout handling
- Simple HTTP responses to reduce memory usage
- Automatic cleanup of failed connections

## Game Rules

- **Objective**: Score 5 points before the AI opponent
- **Scoring**: Ball passes opponent's paddle
- **AI Difficulty**: Configurable from 0.0 (easy) to 1.0 (perfect)
- **Ball Physics**: Bounces off top/bottom walls and paddles
- **Win Condition**: First player to reach WIN_SCORE points

## Troubleshooting

### Common Issues

#### Game Won't Start
- Check that `code.py` is in the root directory
- Verify CircuitPython 8.0+ is installed
- Check serial output for error messages
- Ensure 3.3V power supply is stable

#### WiFi Connection Fails
- Verify credentials in `config.py`
- Check WiFi network is 2.4GHz (Pico 2W doesn't support 5GHz)
- Game will run in offline mode if WiFi fails
- Check WiFi LED status

#### Buttons Don't Work
- Verify wiring matches pin assignments
- Check pull-up resistors are connected
- Buttons are active LOW (pressed = 0V)
- Game will still work with web controls only

#### Web Interface Inaccessible
- Confirm WiFi LED is on (WiFi connected)
- Check Pico's IP address in serial output  
- Try connecting from different device on same network
- Disable firewall temporarily for testing

### Performance Issues

#### Low Frame Rate
- Reduce AI_DIFFICULTY to decrease computation
- Check for memory issues (frequent garbage collection)
- Verify stable power supply
- Monitor serial output for error messages

#### Memory Errors
- Restart the Pico 2W to clear memory
- Check for infinite loops in error handling
- Reduce buffer sizes if modified
- Monitor garbage collection frequency

## Development

### Code Structure

```
code.py
├── SafeLogger: Error-safe logging
├── HardwareManager: Pin initialization and control  
├── NetworkManager: Non-blocking WiFi and HTTP server
├── GameEngine: Game logic and physics
└── PicoPongGame: Main controller and game loop
```

### Key Design Principles

1. **Fail-Safe Operation**: Every operation has error handling
2. **Non-Blocking**: Network operations never block the game loop
3. **Memory Efficient**: Minimal allocations in game loop
4. **Graceful Degradation**: Game works even if some features fail
5. **Easy Recovery**: Automatic restart on fatal errors

### Modifying the Game

- **Game Physics**: Edit `GameEngine.update_ball_physics()`
- **AI Behavior**: Modify AI logic in `update_paddle_positions()`
- **Network Protocol**: Extend `NetworkManager.check_for_commands()`
- **Hardware Pins**: Update pin assignments in `HardwareManager`

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](../LICENSE.txt) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test on actual Pico 2W hardware
4. Ensure code runs reliably as `code.py`
5. Submit a pull request

## Version History

- **v1.0**: Initial robust implementation with WiFi controls
  - Non-blocking network operations
  - Comprehensive error handling
  - Memory optimization for CircuitPython
  - 60 FPS game loop
  - Web-based remote controls