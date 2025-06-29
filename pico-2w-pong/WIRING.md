# Pico 2W Pong Game - Wiring Diagram

## Pin Connections

### Raspberry Pi Pico 2W Pinout
```
                    ┌─────────────────┐
                    │       USB       │
                    └─────────────────┘
                            │
    ┌───────────────────────┴───────────────────────┐
    │  GP0                                    VBUS  │
    │  GP1                                    VSYS  │
    │  GND                                     GND  │
    │  GP2                                    3V3   │
    │  GP3                                  3V3_EN  │
    │  GP4                                     GND  │
    │  GP5                                    GP28  │
    │  GND                                    GP27  │
    │  GP6                                    GP26  │
    │  GP7                                    RUN   │
    │  GP8                                    GP22  │
    │  GP9                                     GND  │
    │  GND                                    GP21  │
    │  GP10                                   GP20  │
    │  GP11                                   GP19  │
    │  GP12                                   GP18  │
    │  GP13 ──── RESET BUTTON               GP17 ──── GAME LED
    │  GND                                     GND  │
    │  GP14 ──── DOWN BUTTON                GP16 ──── WIFI LED
    │  GP15 ──── UP BUTTON                    LED ──── STATUS LED
    │  GP16                                    GND  │
    │  GP17                                   3V3   │
    │  GND                                    GP23  │
    │  GP18                                   GP24  │
    │  GP19                                   GP25  │
    └─────────────────────────────────────────────┘
```

## Component Connections

### Button Wiring (All buttons use same pattern)
```
3.3V ──┬── 10kΩ Resistor ──┬── GPIO Pin (GP13/GP14/GP15)
       │                    │
       └── Button ──────────┴── GND (when pressed)
```

**Button Pin Assignments:**
- UP Button: GP15
- DOWN Button: GP14  
- RESET Button: GP13

### LED Wiring (WiFi and Game LEDs)
```
GPIO Pin ── 220Ω Resistor ── LED Anode ── LED Cathode ── GND
```

**LED Pin Assignments:**
- Status LED: Built-in LED (no external wiring needed)
- WiFi LED: GP16
- Game LED: GP17

## Breadboard Layout

### Minimal Setup Breadboard
```
     3.3V Rail                          GND Rail
        │                                  │
    ┌───┼──────────────────────────────────┼───┐
    │   │                                  │   │
    │ ┌─┴─┐     ┌─────┐     ┌─────┐       │   │
    │ │10k│     │ UP  │     │DOWN │       │   │
    │ │Ω  │     │ BTN │     │ BTN │       │   │
    │ └─┬─┘     └──┬──┘     └──┬──┘       │   │
    │   │          │           │          │   │
    │   ├──────────┼───────────┼─── GP15  │   │
    │   │          │           │          │   │
    │   │          └───────────┼─── GP14  │   │
    │   │                      │          │   │
    │   └──────────────────────┼─── GP13  │   │
    │                          │          │   │
    │      ┌─────┐             │          │   │
    │      │RESET│             │          │   │
    │      │ BTN │             │          │   │
    │      └──┬──┘             │          │   │
    │         │                │          │   │
    │         └────────────────┼──────────┼───┘
    │                          │          │
    │ ┌────┐ ┌────┐            │          │
    │ │220Ω│ │220Ω│            │          │
    │ │    │ │    │            │          │
    │ └─┬──┘ └─┬──┘            │          │
    │   │      │               │          │
    │ ──┼── GP16            ───┼── GND    │
    │   │      │               │          │
    │ ──┼── GP17            ───┼──────────┘
    │   │      │               │
    │ [WiFi] [Game]            │
    │  LED    LED              │
    │   │      │               │
    │   └──────┼───────────────┘
    │          │
    │          └───────────────────────────────
    └──────────────────────────────────────────┘
```

## Component List

### Essential Components
- 1x Raspberry Pi Pico 2W
- 1x Breadboard (half-size or larger)
- 3x Push buttons (momentary, normally open)
- 2x LEDs (any color, 3mm or 5mm)
- 3x 10kΩ resistors (for button pull-ups)
- 2x 220Ω resistors (for LED current limiting)
- Jumper wires (male-to-male)

### Optional Components
- 1x Micro USB cable (for power/programming)
- 1x Battery pack (for portable operation)
- 1x Enclosure/case
- Heat shrink tubing (for wire management)

## Wiring Steps

### Step 1: Power Rails
1. Connect 3.3V pin to breadboard positive rail
2. Connect GND pin to breadboard negative rail

### Step 2: Button Connections
1. Place buttons on breadboard
2. Connect one side of each button to GND rail
3. Connect 10kΩ pull-up resistors from other side to 3.3V rail
4. Connect GPIO wires:
   - GP15 to UP button
   - GP14 to DOWN button  
   - GP13 to RESET button

### Step 3: LED Connections
1. Connect 220Ω resistors to GP16 and GP17
2. Connect LED anodes to resistors
3. Connect LED cathodes to GND rail
4. Note LED polarity (longer leg = anode)

### Step 4: Testing
1. Load test_game.py in Thonny
2. Test each button individually
3. Verify LED control works
4. Check serial output for confirmation

## Troubleshooting Connections

### Button Issues
- **No response**: Check pull-up resistor connections
- **Inverted response**: Verify button connects to GND when pressed
- **Intermittent**: Check for loose connections

### LED Issues  
- **Won't light**: Check polarity and resistor connections
- **Too dim**: Verify 220Ω resistor value
- **Too bright**: Increase resistor value to 470Ω

### Power Issues
- **Unstable operation**: Check power supply rating (500mA minimum)
- **Resets during WiFi**: Use higher current power supply
- **Won't start**: Verify 3.3V and GND connections

## Advanced Modifications

### Additional LEDs
- Connect more LEDs to unused GPIO pins
- Use PWM for brightness control
- Add RGB LEDs for color effects

### Better Buttons
- Use arcade-style buttons for better feel
- Add button debouncing capacitors (0.1µF)
- Wire external reset button to RUN pin

### Power Management
- Add power switch in line with VSYS
- Use battery pack with voltage regulator
- Add power LED indicator