from machine import Pin, Timer
from time import sleep

class Port:
    def __init__(self, pin_nums, initial, led_pin = False):
        self.pins = list(map(lambda pin: Pin(pin, Pin.OUT, initial), pin_nums))

        #if led_pin: self.led = Pin(led_pin, Pin.OUT)

    def send(self, bits):
        for pos, pin in enumerate(reversed(self.pins)):
            bit = (bits >> pos) & 1
            pin.value(bit)
            #if self.led : self.led.toggle()
            #print("write", pos, pin, "value", pin.value())
            #print(pinx.value())
        if False:
            timer = Timer()
            timer.init(freq=0.5, mode=Timer.ONE_SHOT, callback = self.blink)

    def blink(self):
        self.led.toggle()

    def set_in(self):
        for pos, pin in enumerate(self.pins):
            pin.mode(Pin.IN)

    def read(self):
        for pos, pin in enumerate(self.pins):
            print("read", pos, pin, "value", pin.value())

class LCD:
    # Modes:
    # enable, readwrite, readselect
    DONE = 0b000
    SEND = 0b100
    WRITE = 0b101
    BUSY = 0b110
    READ = 0b111

    # Commands:
    CLEAR = 0x01
    HOME = 0x02

    ENTRY = 0x04
    ENTRY_RIGHT = 0x02
    ENTRY_SIFHT = 0x01

    DISPLAY = 0x08
    DISPLAY_ON = 0x04
    DISPLAY_CURSOR = 0x02
    DISPLAY_BLINK = 0x01

    SHIFT = 0x10
    SHIFT_DISPLAY = 0x08
    SHIFT_RIGHT = 0x04

    FUNCTION = 0x20
    FUNCTION_8_BIT = 0x10
    FUNCTION_TWO_LINE = 0x08
    FUNCTION_FONT_TYPE = 0x04

    CGRAM_ADDRESS = 0x40

    DDRAM_ADDRESS = 0x80
    DDRAM_ADDRESS_LINE_2 = 0x40

    def __init__(self, mode_port, databus_port):
        self.mode_port = mode_port
        self.databus_port = databus_port

        self.send_function(True, True, False)
        self.send_display(True, True, True)
        self.send_clear()
        self.send_entry(True, False)

    # TODO: Implement
    def read(self):
        self.databus_port.set_in()

        self.mode_port.send(self.BUSY)
        self.databus_port.read()

    # TODO
    def check_busy(self):
        self.pinrs.value(0)
        self.pinrw.value(1)
        self.pine.value(1)
        while self.pinb.value():
            sleep(0.1)
            print("busy")
        print('done')
        return(self.pinb.value())

    # TODO: Check busy
    def send_instruction(self, instruction, mode = SEND, check_busy = True):
        #if check_busy: self.check_busy()

        self.databus_port.send(instruction)
        self.mode_port.send(mode)
        sleep(0.001)
        self.mode_port.send(self.DONE)
        sleep(0.001)

    def send_clear(self):
        self.send_instruction(self.CLEAR)
        sleep(0.01)

    def send_home(self):
        self.send_instruction(self.HOME)

    def send_entry(self, right = True, shift = True):
        instruction = self.ENTRY
        if right: instruction += self.ENTRY_RIGHT
        if shift: instruction += self.ENTRY_SIFHT

        self.send_instruction(instruction)

    # Turns display, cursor and blinking on and off
    # Note: ?Can't turn display off when blinking
    def send_display(self, on = True, cursor = False, blink = False):
        instruction = self.DISPLAY
        if on: instruction += self.DISPLAY_ON
        if on and cursor: instruction += self.DISPLAY_CURSOR
        if on and cursor and blink: instruction += self.DISPLAY_BLINK

        self.send_instruction(instruction)

    # Shifts the cursor or display
    def send_shift(self, display = True, right = True):
        instruction = self.SHIFT
        if display: instruction += self.SHIFT_DISPLAY
        if right: instruction += self.SHIFT_RIGHT

        self.send_instruction(instruction)

    # Sends a function instruction that is used for initizalizing the display
    def send_function(self, eight_bit = True, two_line = True, font_type = True):
        instruction = self.FUNCTION
        if eight_bit: instruction += self.FUNCTION_8_BIT
        if two_line: instruction += self.FUNCTION_TWO_LINE
        if font_type: instruction += self.FUNCTION_FONT_TYPE

        self.send_instruction(instruction, self.SEND, False)

    # Sets the cursor position
    def send_ddram_address(self, line = 1, column = 1):
        instruction = self.DDRAM_ADDRESS
        if line == 2 : instruction += self.DDRAM_ADDRESS_LINE_2
        instruction += column

        self.send_instruction(instruction)

    def write_ddram(self, data):
        self.send_instruction(data, self.WRITE)

    def display_string(self, string):
        for char in string:
            self.write_ddram(ord(char))

mode_port = Port([5, 15, 3], 0)
databus_port = Port(reversed(range(6, 14)), 0, 25)
lcd = LCD(mode_port, databus_port)

button = Pin(14, mode=Pin.OUT, pull = Pin.PULL_DOWN)

lcd.display_string("Press button to")
lcd.send_ddram_address(2, 0)
lcd.display_string("to count!")

count = 0
while False:
    sleep(0.2)
    if button.value():
        lcd.send_clear()
        lcd.display_string("Counter: "+str(count))
        count +=1
        sleep(0.5)
