# Pico 2W Pong Game Configuration

## WiFi Settings
WIFI_SSID = "PicoWifi"
WIFI_PASSWORD = "picopass"

## Game Settings
FPS = 60
PADDLE_SPEED = 4
BALL_SPEED = 3
WIN_SCORE = 5
AI_DIFFICULTY = 0.8  # 0.0 to 1.0

## Hardware Pins
# Buttons (with pull-up resistors)
BUTTON_UP_PIN = 15
BUTTON_DOWN_PIN = 14
BUTTON_RESET_PIN = 13

# LEDs
LED_STATUS_PIN = "LED"  # Built-in LED
LED_WIFI_PIN = 16
LED_GAME_PIN = 17

## Network Settings
WEB_SERVER_PORT = 80
NETWORK_TIMEOUT = 5.0
MAX_RETRIES = 3

## Performance Settings
STARTUP_DELAY = 3.0  # Seconds to wait for hardware stabilization
GC_INTERVAL = 5.0    # Garbage collection interval in seconds
FRAME_TIME_TARGET = 0.0167  # 60 FPS = 16.67ms per frame

## Screen Dimensions (for game logic)
SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64

## Game Object Sizes
PADDLE_HEIGHT = 20
PADDLE_WIDTH = 3
BALL_SIZE = 2