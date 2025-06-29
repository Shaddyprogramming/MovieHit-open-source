# Troubleshooting Guide for Pico 2W Pong

## Common Issues and Solutions

### Startup Issues

#### Problem: Game doesn't start at all
**Symptoms**: No LED activity, no serial output
**Solutions**:
1. Check CircuitPython installation
2. Verify `code.py` is in root directory (not subfolder)
3. Check file naming (case sensitive)
4. Try running in Thonny first
5. Check power supply (5V, 500mA minimum)

#### Problem: Hardware initialization failures
**Symptoms**: Error messages about pin initialization
**Solutions**:
1. Check wiring connections
2. Verify pin numbers in config match wiring
3. Ensure pull-up resistors on buttons
4. Test individual pins in Thonny
5. Use `test_game.py` to verify functionality

### WiFi Issues

#### Problem: WiFi won't connect
**Symptoms**: WiFi LED stays off, "WiFi connection failed" messages
**Solutions**:
1. Verify SSID and password in `config.py`
2. Ensure network is 2.4GHz (Pico 2W doesn't support 5GHz)
3. Check WiFi signal strength
4. Try different network if available
5. Game will run in offline mode if WiFi fails

#### Problem: Web interface not accessible
**Symptoms**: WiFi connects but can't reach web page
**Solutions**:
1. Check Pico's IP address in serial output
2. Ensure devices are on same network
3. Try different web browser
4. Disable firewall temporarily
5. Ping Pico IP to test connectivity

### Game Performance Issues

#### Problem: Low frame rate or choppy gameplay
**Symptoms**: Jerky movement, poor responsiveness
**Solutions**:
1. Reduce `FPS` setting in config
2. Lower `AI_DIFFICULTY` to reduce computation
3. Check for memory issues (see below)
4. Ensure stable power supply
5. Monitor serial output for errors

#### Problem: Memory errors
**Symptoms**: "MemoryError" exceptions, frequent restarts
**Solutions**:
1. Restart Pico to clear memory
2. Check for infinite loops
3. Reduce buffer sizes if modified
4. Increase garbage collection frequency
5. Use `test_game.py` to identify memory leaks

### Hardware Control Issues

#### Problem: Buttons don't respond
**Symptoms**: Physical buttons have no effect
**Solutions**:
1. Check button wiring (active LOW with pull-up)
2. Verify pin assignments match config
3. Test with multimeter (should read 3.3V normally, 0V when pressed)
4. Check for loose connections
5. Use web controls as backup

#### Problem: LEDs don't work
**Symptoms**: No LED activity or wrong behavior
**Solutions**:
1. Check LED polarity (anode to resistor, cathode to ground)
2. Verify resistor values (220Ω recommended)
3. Test LEDs with direct 3.3V connection
4. Check pin assignments in config
5. Monitor serial output for LED state changes

### Network Communication Issues

#### Problem: Web controls don't work
**Symptoms**: Web page loads but buttons have no effect
**Solutions**:
1. Check game is running (Game LED should be on)
2. Verify IP address is correct
3. Try refreshing the web page
4. Check serial output for network command messages
5. Test with different device/browser

#### Problem: Connection timeouts
**Symptoms**: Web page loads slowly or times out
**Solutions**:
1. Increase `NETWORK_TIMEOUT` in config
2. Check WiFi signal strength
3. Reduce network traffic on router
4. Try connecting from closer distance
5. Reset Pico if persistent

## Debugging Techniques

### Serial Monitoring
1. Connect to Pico via Thonny or serial terminal
2. Monitor startup messages for errors
3. Look for repeated error patterns
4. Note memory usage information
5. Check frame rate timing messages

### LED Status Interpretation
- **Status LED (built-in)**: System running
- **WiFi LED**: Network connectivity
- **Game LED**: Game loop active

### Hardware Testing
```python
# Test individual pins in Thonny
import board
import digitalio

# Test button
btn = digitalio.DigitalInOut(board.GP15)
btn.direction = digitalio.Direction.INPUT
btn.pull = digitalio.Pull.UP
print(f"Button state: {not btn.value}")

# Test LED
led = digitalio.DigitalInOut(board.GP16)
led.direction = digitalio.Direction.OUTPUT
led.value = True  # Turn on
```

### Network Testing
```python
# Test WiFi connectivity
import wifi
wifi.radio.connect("SSID", "password")
print(f"Connected: {wifi.radio.connected}")
print(f"IP: {wifi.radio.ipv4_address}")
```

## Performance Optimization

### Memory Management
- Monitor garbage collection frequency
- Avoid creating objects in game loop
- Use namedtuples for immutable data
- Clear unused variables explicitly

### Network Optimization
- Keep HTTP responses minimal
- Use non-blocking socket operations
- Implement connection pooling
- Handle timeouts gracefully

### Game Loop Optimization
- Minimize floating-point operations
- Use integer arithmetic where possible
- Batch similar operations
- Profile code sections for bottlenecks

## Recovery Procedures

### Soft Reset
1. Press RESET button on Pico
2. Or send `microcontroller.reset()` via Thonny
3. Game will restart automatically

### Hard Reset
1. Disconnect power for 10 seconds
2. Reconnect and observe startup sequence
3. Check for persistent issues

### Factory Reset
1. Hold BOOTSEL while connecting USB
2. Copy CircuitPython .uf2 file again
3. Reload all game files
4. Reconfigure settings

### File Recovery
1. Access Pico as USB drive
2. Backup existing files if possible
3. Re-copy fresh code files
4. Restore configuration settings

## Getting Help

### Before Reporting Issues
1. Try `test_game.py` first
2. Check this troubleshooting guide
3. Verify hardware connections
4. Test with minimal configuration
5. Gather error messages and logs

### Useful Information to Include
- CircuitPython version
- Hardware setup details
- Complete error messages
- Steps to reproduce issue
- Serial output logs
- Configuration file contents

### Alternative Configurations
If issues persist, try these simplified setups:
1. Offline mode only (no WiFi)
2. Web controls only (no physical buttons)
3. Reduced performance settings
4. Mock hardware for testing