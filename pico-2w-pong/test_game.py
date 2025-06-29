"""
Thonny-Compatible Test Version of Pico 2W Pong Game

This version has reduced hardware dependencies for testing in Thonny IDE.
Use this for development and debugging before deploying as code.py

Features:
- Mock hardware when pins are unavailable
- Simplified networking for testing
- Console output for game state
- Easy debugging and development
"""

import time
import gc
import sys

# Configuration for testing
TEST_CONFIG = {
    'fps': 30,  # Reduced for easier testing
    'paddle_speed': 4,
    'ball_speed': 3,
    'paddle_height': 20,
    'paddle_width': 3,
    'ball_size': 2,
    'win_score': 3,  # Reduced for faster testing
    'ai_difficulty': 0.6,  # Easier for testing
    'screen_width': 128,
    'screen_height': 64,
    'mock_hardware': True  # Enable hardware mocking
}

class MockHardware:
    """Mock hardware for testing without physical components"""
    
    def __init__(self):
        self.button_states = {'up': False, 'down': False, 'reset': False}
        self.led_states = {'status': False, 'wifi': False, 'game': False}
        print("Mock hardware initialized")
    
    def read_buttons(self):
        """Simulate button presses for testing"""
        # Simulate some random button presses for demo
        import random
        if random.random() < 0.05:  # 5% chance per frame
            button = random.choice(['up', 'down'])
            self.button_states[button] = True
            print(f"Mock button press: {button}")
        else:
            self.button_states = {'up': False, 'down': False, 'reset': False}
        
        return self.button_states.copy()
    
    def set_led(self, name, state):
        """Mock LED control"""
        if self.led_states.get(name) != state:
            self.led_states[name] = state
            print(f"LED {name}: {'ON' if state else 'OFF'}")

class TestGameEngine:
    """Simplified game engine for testing"""
    
    def __init__(self):
        self.player_y = TEST_CONFIG['screen_height'] // 2
        self.ai_y = TEST_CONFIG['screen_height'] // 2
        self.ball_x = TEST_CONFIG['screen_width'] // 2
        self.ball_y = TEST_CONFIG['screen_height'] // 2
        self.ball_dx = TEST_CONFIG['ball_speed']
        self.ball_dy = TEST_CONFIG['ball_speed']
        self.player_score = 0
        self.ai_score = 0
        self.game_running = True
        self.frame_count = 0
        
    def update(self, inputs):
        """Update game state"""
        self.frame_count += 1
        
        # Update player paddle
        if inputs.get('up', False):
            self.player_y = max(TEST_CONFIG['paddle_height'] // 2, 
                              self.player_y - TEST_CONFIG['paddle_speed'])
        if inputs.get('down', False):
            self.player_y = min(TEST_CONFIG['screen_height'] - TEST_CONFIG['paddle_height'] // 2,
                              self.player_y + TEST_CONFIG['paddle_speed'])
        
        # Update AI paddle
        target_y = self.ball_y
        diff = target_y - self.ai_y
        if abs(diff) > 1:
            move = TEST_CONFIG['paddle_speed'] * TEST_CONFIG['ai_difficulty']
            if diff > 0:
                self.ai_y = min(TEST_CONFIG['screen_height'] - TEST_CONFIG['paddle_height'] // 2,
                              self.ai_y + move)
            else:
                self.ai_y = max(TEST_CONFIG['paddle_height'] // 2, self.ai_y - move)
        
        # Update ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Wall bouncing
        if self.ball_y <= TEST_CONFIG['ball_size'] or self.ball_y >= TEST_CONFIG['screen_height'] - TEST_CONFIG['ball_size']:
            self.ball_dy = -self.ball_dy
        
        # Paddle collisions
        if self.ball_x <= TEST_CONFIG['paddle_width'] + TEST_CONFIG['ball_size']:
            if (self.player_y - TEST_CONFIG['paddle_height'] // 2 <= self.ball_y <= 
                self.player_y + TEST_CONFIG['paddle_height'] // 2):
                self.ball_dx = abs(self.ball_dx)
                
        elif self.ball_x >= TEST_CONFIG['screen_width'] - TEST_CONFIG['paddle_width'] - TEST_CONFIG['ball_size']:
            if (self.ai_y - TEST_CONFIG['paddle_height'] // 2 <= self.ball_y <= 
                self.ai_y + TEST_CONFIG['paddle_height'] // 2):
                self.ball_dx = -abs(self.ball_dx)
        
        # Scoring
        if self.ball_x < 0:
            self.ai_score += 1
            self.reset_ball()
        elif self.ball_x > TEST_CONFIG['screen_width']:
            self.player_score += 1
            self.reset_ball()
        
        # Check win condition
        if self.player_score >= TEST_CONFIG['win_score'] or self.ai_score >= TEST_CONFIG['win_score']:
            self.game_running = False
        
        # Reset game
        if inputs.get('reset', False):
            self.reset_game()
    
    def reset_ball(self):
        """Reset ball to center"""
        self.ball_x = TEST_CONFIG['screen_width'] // 2
        self.ball_y = TEST_CONFIG['screen_height'] // 2
        self.ball_dx = TEST_CONFIG['ball_speed'] if self.ball_dx > 0 else -TEST_CONFIG['ball_speed']
    
    def reset_game(self):
        """Reset entire game"""
        self.player_score = 0
        self.ai_score = 0
        self.game_running = True
        self.reset_ball()
        print("Game reset!")
    
    def get_status(self):
        """Get current game status"""
        return {
            'player_score': self.player_score,
            'ai_score': self.ai_score,
            'player_y': self.player_y,
            'ai_y': self.ai_y,
            'ball_x': self.ball_x,
            'ball_y': self.ball_y,
            'game_running': self.game_running,
            'frame': self.frame_count
        }
    
    def print_game_state(self):
        """Print visual representation of game"""
        if self.frame_count % 30 == 0:  # Print every 30 frames (1 second at 30 FPS)
            status = self.get_status()
            print(f"\nFrame {status['frame']} | Score: Player {status['player_score']} - {status['ai_score']} AI")
            print(f"Ball: ({status['ball_x']:.1f}, {status['ball_y']:.1f})")
            print(f"Paddles: Player Y={status['player_y']:.1f}, AI Y={status['ai_y']:.1f}")
            
            if not status['game_running']:
                winner = "Player" if status['player_score'] > status['ai_score'] else "AI"
                print(f"🎉 {winner} wins! Press reset to play again.")

class TestNetworkManager:
    """Simplified network manager for testing"""
    
    def __init__(self):
        self.connected = False
        self.commands = []
        
    def connect_wifi(self):
        """Mock WiFi connection"""
        print("Mock WiFi: Connecting...")
        time.sleep(1)
        self.connected = True
        print("Mock WiFi: Connected to test network")
        return True
    
    def start_server(self):
        """Mock server start"""
        print("Mock server: Started on http://test-pico.local")
        return True
    
    def check_for_commands(self):
        """Mock network commands"""
        # Simulate occasional network commands
        import random
        commands = []
        if random.random() < 0.02:  # 2% chance
            cmd = random.choice(['up', 'down', 'reset'])
            commands.append(cmd)
            print(f"Mock network command: {cmd}")
        return commands

def test_game():
    """Run test version of the game"""
    print("=== Pico Pong Test Mode ===")
    print("This is a test version for development in Thonny")
    print("Mock hardware and networking are enabled")
    print("Press Ctrl+C to stop\n")
    
    # Initialize components
    hardware = MockHardware()
    network = TestNetworkManager()
    engine = TestGameEngine()
    
    # Setup
    hardware.set_led('status', True)
    
    if network.connect_wifi():
        network.start_server()
        hardware.set_led('wifi', True)
    
    hardware.set_led('game', True)
    
    print("Starting game loop...")
    frame_time = 1.0 / TEST_CONFIG['fps']
    
    try:
        while engine.game_running:
            frame_start = time.monotonic()
            
            # Get inputs
            inputs = {}
            inputs.update(hardware.read_buttons())
            
            # Add network commands
            net_commands = network.check_for_commands()
            for cmd in net_commands:
                inputs[cmd] = True
            
            # Update game
            engine.update(inputs)
            engine.print_game_state()
            
            # Memory management
            if engine.frame_count % 150 == 0:  # Every 5 seconds
                gc.collect()
                print("Memory cleanup performed")
            
            # Frame timing
            elapsed = time.monotonic() - frame_start
            sleep_time = max(0, frame_time - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nGame stopped by user")
    
    except Exception as e:
        print(f"Test error: {e}")
    
    finally:
        # Cleanup
        hardware.set_led('status', False)
        hardware.set_led('wifi', False) 
        hardware.set_led('game', False)
        print("Test cleanup complete")

if __name__ == "__main__":
    test_game()