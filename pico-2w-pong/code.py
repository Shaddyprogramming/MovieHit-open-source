"""
Raspberry Pi Pico 2W WiFi Pong Game
Robust implementation designed to run reliably as code.py

Features:
- Physical button controls
- Web-based remote controls
- LED status indicators  
- 60 FPS Pong gameplay
- Score tracking and win conditions
- AI opponent
- Non-blocking network operations
- Comprehensive error handling
- Memory optimization
- Graceful fallback modes

Author: MovieHit Team
License: Apache 2.0
"""

import time
import gc
import sys
import board
import digitalio
import pwmio
import socketpool
import wifi
import microcontroller
import supervisor
from collections import namedtuple

# Early startup delay for hardware initialization
time.sleep(2.0)

# Configuration constants
GAME_CONFIG = {
    'fps': 60,
    'paddle_speed': 4,
    'ball_speed': 3,
    'paddle_height': 20,
    'paddle_width': 3,
    'ball_size': 2,
    'win_score': 5,
    'ai_difficulty': 0.8,
    'screen_width': 128,
    'screen_height': 64,
    'startup_delay': 3.0,
    'network_timeout': 5.0,
    'max_retries': 3
}

# Memory-optimized game state structure
GameState = namedtuple('GameState', [
    'player_y', 'ai_y', 'ball_x', 'ball_y', 
    'ball_dx', 'ball_dy', 'player_score', 'ai_score',
    'game_running', 'paused'
])

class SafeLogger:
    """Simple logging with error protection"""
    @staticmethod
    def log(message, level="INFO"):
        try:
            print(f"[{level}] {message}")
        except:
            pass  # Fail silently if print fails

logger = SafeLogger()

class HardwareManager:
    """Manages all hardware initialization with error handling"""
    
    def __init__(self):
        self.buttons = {}
        self.leds = {}
        self.initialized = False
        self.retries = 0
        
    def safe_init_pin(self, pin, mode, name):
        """Safely initialize a pin with retries"""
        for attempt in range(GAME_CONFIG['max_retries']):
            try:
                if mode == 'input':
                    gpio = digitalio.DigitalInOut(pin)
                    gpio.direction = digitalio.Direction.INPUT
                    gpio.pull = digitalio.Pull.UP
                elif mode == 'output':
                    gpio = digitalio.DigitalInOut(pin)
                    gpio.direction = digitalio.Direction.OUTPUT
                    gpio.value = False
                elif mode == 'pwm':
                    gpio = pwmio.PWMOut(pin, frequency=1000)
                    gpio.duty_cycle = 0
                else:
                    return None
                    
                logger.log(f"Initialized {name} on attempt {attempt + 1}")
                return gpio
            except Exception as e:
                logger.log(f"Failed to init {name}, attempt {attempt + 1}: {e}", "WARN")
                time.sleep(0.5)
        return None
    
    def initialize(self):
        """Initialize all hardware with fallbacks"""
        try:
            logger.log("Starting hardware initialization...")
            
            # Initialize buttons with fallbacks
            self.buttons['up'] = self.safe_init_pin(board.GP15, 'input', 'UP button')
            self.buttons['down'] = self.safe_init_pin(board.GP14, 'input', 'DOWN button') 
            self.buttons['reset'] = self.safe_init_pin(board.GP13, 'input', 'RESET button')
            
            # Initialize LEDs
            self.leds['status'] = self.safe_init_pin(board.LED, 'output', 'Status LED')
            self.leds['wifi'] = self.safe_init_pin(board.GP16, 'output', 'WiFi LED')
            self.leds['game'] = self.safe_init_pin(board.GP17, 'output', 'Game LED')
            
            # Count successful initializations
            button_count = sum(1 for btn in self.buttons.values() if btn is not None)
            led_count = sum(1 for led in self.leds.values() if led is not None)
            
            self.initialized = button_count >= 2 and led_count >= 1
            logger.log(f"Hardware init: {button_count}/3 buttons, {led_count}/3 LEDs")
            
            return self.initialized
            
        except Exception as e:
            logger.log(f"Hardware init failed: {e}", "ERROR")
            return False
    
    def read_buttons(self):
        """Safely read button states"""
        states = {}
        for name, button in self.buttons.items():
            try:
                if button is not None:
                    states[name] = not button.value  # Inverted due to pull-up
                else:
                    states[name] = False
            except:
                states[name] = False
        return states
    
    def set_led(self, name, state):
        """Safely control LEDs"""
        try:
            if name in self.leds and self.leds[name] is not None:
                self.leds[name].value = state
        except:
            pass

class NetworkManager:
    """Non-blocking network operations with proper error handling"""
    
    def __init__(self, hardware):
        self.hardware = hardware
        self.pool = None
        self.server_socket = None
        self.connected = False
        self.last_check = 0
        self.check_interval = 5.0
        self.client_commands = []
        
    def connect_wifi(self, ssid="PicoWifi", password="picopass"):
        """Connect to WiFi with timeout and retries"""
        for attempt in range(GAME_CONFIG['max_retries']):
            try:
                logger.log(f"WiFi attempt {attempt + 1}/{GAME_CONFIG['max_retries']}")
                self.hardware.set_led('wifi', True)
                
                wifi.radio.connect(ssid, password, timeout=GAME_CONFIG['network_timeout'])
                
                if wifi.radio.connected:
                    self.pool = socketpool.SocketPool(wifi.radio)
                    logger.log(f"WiFi connected: {wifi.radio.ipv4_address}")
                    self.connected = True
                    return True
                    
            except Exception as e:
                logger.log(f"WiFi connect failed: {e}", "WARN")
                time.sleep(1.0)
        
        self.hardware.set_led('wifi', False)
        logger.log("WiFi connection failed, running offline", "WARN")
        return False
    
    def start_server(self, port=80):
        """Start non-blocking web server"""
        if not self.connected or self.pool is None:
            return False
            
        try:
            self.server_socket = self.pool.socket()
            self.server_socket.settimeout(0.01)  # Non-blocking
            self.server_socket.bind(('0.0.0.0', port))
            self.server_socket.listen(1)
            logger.log(f"Web server started on port {port}")
            return True
        except Exception as e:
            logger.log(f"Server start failed: {e}", "ERROR")
            return False
    
    def check_for_commands(self):
        """Non-blocking check for web commands"""
        if not self.server_socket:
            return []
            
        commands = []
        try:
            # Try to accept connection (non-blocking)
            client, addr = self.server_socket.accept()
            client.settimeout(0.1)
            
            try:
                # Read request quickly
                request = client.recv(512).decode('utf-8')
                
                # Parse simple commands from URL
                if 'GET /up' in request:
                    commands.append('up')
                elif 'GET /down' in request:
                    commands.append('down')
                elif 'GET /reset' in request:
                    commands.append('reset')
                elif 'GET /' in request:
                    # Send simple control page
                    response = self.get_control_page()
                    client.send(response.encode('utf-8'))
                
                client.close()
            except:
                try:
                    client.close()
                except:
                    pass
                    
        except OSError:
            pass  # No connections waiting
        except Exception as e:
            logger.log(f"Network error: {e}", "WARN")
            
        return commands
    
    def get_control_page(self):
        """Generate simple HTML control page"""
        return """HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n
        <!DOCTYPE html>
        <html><head><title>Pico Pong Controls</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
        body{font-family:Arial;text-align:center;background:#000;color:#fff}
        .btn{display:block;width:200px;height:60px;margin:20px auto;
             background:#444;color:#fff;border:none;font-size:24px;
             border-radius:10px;text-decoration:none;line-height:60px}
        .btn:active{background:#666}
        </style></head>
        <body>
        <h1>Pico Pong Remote</h1>
        <a href="/up" class="btn">UP</a>
        <a href="/down" class="btn">DOWN</a>
        <a href="/reset" class="btn">RESET</a>
        <script>setInterval(()=>fetch('/'),5000)</script>
        </body></html>"""

class GameEngine:
    """Memory-optimized game engine with 60 FPS performance"""
    
    def __init__(self, hardware, network):
        self.hardware = hardware
        self.network = network
        self.reset_game()
        self.frame_time = 1.0 / GAME_CONFIG['fps']
        self.last_gc = 0
        
    def reset_game(self):
        """Reset game to initial state"""
        self.state = GameState(
            player_y=GAME_CONFIG['screen_height'] // 2,
            ai_y=GAME_CONFIG['screen_height'] // 2,
            ball_x=GAME_CONFIG['screen_width'] // 2,
            ball_y=GAME_CONFIG['screen_height'] // 2,
            ball_dx=GAME_CONFIG['ball_speed'],
            ball_dy=GAME_CONFIG['ball_speed'],
            player_score=0,
            ai_score=0,
            game_running=True,
            paused=False
        )
        logger.log("Game reset")
    
    def update_paddle_positions(self, inputs):
        """Update paddle positions based on inputs"""
        # Player paddle control
        player_y = self.state.player_y
        if inputs.get('up', False):
            player_y = max(GAME_CONFIG['paddle_height'] // 2, 
                          player_y - GAME_CONFIG['paddle_speed'])
        if inputs.get('down', False):
            player_y = min(GAME_CONFIG['screen_height'] - GAME_CONFIG['paddle_height'] // 2,
                          player_y + GAME_CONFIG['paddle_speed'])
        
        # AI paddle with difficulty scaling
        ai_y = self.state.ai_y
        target_y = self.state.ball_y
        diff = target_y - ai_y
        
        if abs(diff) > 1:
            move = GAME_CONFIG['paddle_speed'] * GAME_CONFIG['ai_difficulty']
            if diff > 0:
                ai_y = min(GAME_CONFIG['screen_height'] - GAME_CONFIG['paddle_height'] // 2,
                          ai_y + move)
            else:
                ai_y = max(GAME_CONFIG['paddle_height'] // 2, ai_y - move)
        
        # Update state (creating new namedtuple)
        self.state = self.state._replace(player_y=player_y, ai_y=ai_y)
    
    def update_ball_physics(self):
        """Update ball position and handle collisions"""
        ball_x = self.state.ball_x + self.state.ball_dx
        ball_y = self.state.ball_y + self.state.ball_dy
        ball_dx = self.state.ball_dx
        ball_dy = self.state.ball_dy
        
        # Wall bouncing
        if ball_y <= GAME_CONFIG['ball_size'] or ball_y >= GAME_CONFIG['screen_height'] - GAME_CONFIG['ball_size']:
            ball_dy = -ball_dy
        
        # Paddle collisions
        if ball_x <= GAME_CONFIG['paddle_width'] + GAME_CONFIG['ball_size']:
            # Player paddle area
            if (self.state.player_y - GAME_CONFIG['paddle_height'] // 2 <= ball_y <= 
                self.state.player_y + GAME_CONFIG['paddle_height'] // 2):
                ball_dx = abs(ball_dx)  # Ensure rightward movement
                
        elif ball_x >= GAME_CONFIG['screen_width'] - GAME_CONFIG['paddle_width'] - GAME_CONFIG['ball_size']:
            # AI paddle area  
            if (self.state.ai_y - GAME_CONFIG['paddle_height'] // 2 <= ball_y <= 
                self.state.ai_y + GAME_CONFIG['paddle_height'] // 2):
                ball_dx = -abs(ball_dx)  # Ensure leftward movement
        
        # Scoring
        player_score = self.state.player_score
        ai_score = self.state.ai_score
        
        if ball_x < 0:
            ai_score += 1
            ball_x, ball_y = GAME_CONFIG['screen_width'] // 2, GAME_CONFIG['screen_height'] // 2
            ball_dx = GAME_CONFIG['ball_speed']
        elif ball_x > GAME_CONFIG['screen_width']:
            player_score += 1
            ball_x, ball_y = GAME_CONFIG['screen_width'] // 2, GAME_CONFIG['screen_height'] // 2
            ball_dx = -GAME_CONFIG['ball_speed']
        
        # Update state
        self.state = self.state._replace(
            ball_x=ball_x, ball_y=ball_y, ball_dx=ball_dx, ball_dy=ball_dy,
            player_score=player_score, ai_score=ai_score
        )
        
        # Check win condition
        if player_score >= GAME_CONFIG['win_score'] or ai_score >= GAME_CONFIG['win_score']:
            self.state = self.state._replace(game_running=False)
    
    def get_game_status(self):
        """Get current game status for display"""
        return f"Player: {self.state.player_score} | AI: {self.state.ai_score}"
    
    def periodic_gc(self):
        """Perform garbage collection periodically"""
        now = time.monotonic()
        if now - self.last_gc > 5.0:  # Every 5 seconds
            gc.collect()
            self.last_gc = now

class PicoPongGame:
    """Main game controller with robust error handling"""
    
    def __init__(self):
        self.hardware = HardwareManager()
        self.network = NetworkManager(self.hardware)
        self.engine = None
        self.running = True
        self.last_frame = 0
        
    def startup_sequence(self):
        """Robust startup with hardware checks and WiFi connection"""
        logger.log("=== Pico Pong Starting ===")
        
        # Hardware initialization
        if not self.hardware.initialize():
            logger.log("Hardware init failed, limited functionality", "WARN")
        
        # Startup delay for stability
        logger.log(f"Startup delay: {GAME_CONFIG['startup_delay']}s")
        time.sleep(GAME_CONFIG['startup_delay'])
        
        # Initialize game engine
        self.engine = GameEngine(self.hardware, self.network)
        
        # WiFi connection (optional)
        self.hardware.set_led('status', True)
        
        try:
            if self.network.connect_wifi():
                self.network.start_server()
                self.hardware.set_led('wifi', True)
            else:
                logger.log("Running in offline mode")
        except Exception as e:
            logger.log(f"Network setup failed: {e}", "WARN")
        
        self.hardware.set_led('game', True)
        logger.log("Startup complete, game ready!")
        
    def handle_inputs(self):
        """Collect and process all inputs"""
        inputs = {}
        
        # Physical buttons
        try:
            button_states = self.hardware.read_buttons()
            inputs.update(button_states)
        except Exception as e:
            logger.log(f"Button read error: {e}", "WARN")
        
        # Network commands
        try:
            net_commands = self.network.check_for_commands()
            for cmd in net_commands:
                inputs[cmd] = True
        except Exception as e:
            logger.log(f"Network command error: {e}", "WARN")
        
        return inputs
    
    def run_frame(self):
        """Execute one game frame with timing control"""
        frame_start = time.monotonic()
        
        try:
            # Handle inputs
            inputs = self.handle_inputs()
            
            # Handle reset
            if inputs.get('reset', False):
                self.engine.reset_game()
                return
            
            # Game logic
            if self.engine.state.game_running and not self.engine.state.paused:
                self.engine.update_paddle_positions(inputs)
                self.engine.update_ball_physics()
            
            # Status updates
            if time.monotonic() - self.last_frame > 1.0:  # Every second
                logger.log(self.engine.get_game_status())
                self.last_frame = time.monotonic()
            
            # Memory management
            self.engine.periodic_gc()
            
        except Exception as e:
            logger.log(f"Frame error: {e}", "ERROR")
        
        # Frame timing
        frame_time = time.monotonic() - frame_start
        sleep_time = max(0, self.engine.frame_time - frame_time)
        if sleep_time > 0:
            time.sleep(sleep_time)
    
    def run(self):
        """Main game loop with comprehensive error handling"""
        try:
            self.startup_sequence()
            
            logger.log("Entering main game loop...")
            while self.running:
                try:
                    self.run_frame()
                except KeyboardInterrupt:
                    logger.log("Keyboard interrupt received")
                    break
                except Exception as e:
                    logger.log(f"Game loop error: {e}", "ERROR")
                    time.sleep(0.1)  # Prevent rapid error loops
                    
        except Exception as e:
            logger.log(f"Fatal error: {e}", "ERROR")
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Clean shutdown sequence"""
        logger.log("Shutting down...")
        try:
            if self.network.server_socket:
                self.network.server_socket.close()
            
            # Turn off LEDs
            for led_name in ['status', 'wifi', 'game']:
                self.hardware.set_led(led_name, False)
                
        except Exception as e:
            logger.log(f"Cleanup error: {e}", "WARN")
        
        logger.log("=== Pico Pong Stopped ===")

# Main execution with watchdog protection
def main():
    """Protected main function"""
    try:
        # Disable auto-reload for stability
        supervisor.disable_autoreload()
        
        # Create and run game
        game = PicoPongGame()
        game.run()
        
    except Exception as e:
        print(f"FATAL: {e}")
        
        # Emergency LED pattern
        try:
            led = digitalio.DigitalInOut(board.LED)
            led.direction = digitalio.Direction.OUTPUT
            for _ in range(10):
                led.value = True
                time.sleep(0.1)
                led.value = False
                time.sleep(0.1)
        except:
            pass
    
    # Restart after delay
    time.sleep(5.0)
    microcontroller.reset()

if __name__ == "__main__":
    main()