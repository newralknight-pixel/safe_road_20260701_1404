from machine import I2C, Pin, PWM
import select
import sys
import time


LED_PIN = 15
BUZZER_PIN = 16
BUTTON_PIN = 17
I2C_SDA_PIN = 0
I2C_SCL_PIN = 1

# Change to False if your buzzer is an active buzzer with only + and - pins.
PASSIVE_BUZZER = True


LCD_BACKLIGHT = 0x08
LCD_ENABLE = 0x04
LCD_COMMAND = 0
LCD_DATA = 1


class I2cLcd1602:
    def __init__(self, i2c, address, rows=2, cols=16):
        self.i2c = i2c
        self.address = address
        self.rows = rows
        self.cols = cols
        self.backlight = LCD_BACKLIGHT
        time.sleep_ms(50)
        self._write4(0x03)
        time.sleep_ms(5)
        self._write4(0x03)
        time.sleep_us(150)
        self._write4(0x03)
        self._write4(0x02)
        self.command(0x28)
        self.command(0x0C)
        self.command(0x06)
        self.clear()

    def _send(self, value):
        self.i2c.writeto(self.address, bytes([value | self.backlight]))

    def _pulse(self, value):
        self._send(value | LCD_ENABLE)
        time.sleep_us(1)
        self._send(value & ~LCD_ENABLE)
        time.sleep_us(50)

    def _write4(self, value, mode=LCD_COMMAND):
        data = (value & 0x0F) << 4
        self._pulse(data | mode)

    def _write8(self, value, mode=LCD_COMMAND):
        self._write4(value >> 4, mode)
        self._write4(value, mode)

    def command(self, value):
        self._write8(value, LCD_COMMAND)
        if value in (0x01, 0x02):
            time.sleep_ms(2)

    def clear(self):
        self.command(0x01)

    def move_to(self, col, row):
        row_offsets = (0x00, 0x40)
        self.command(0x80 | (col + row_offsets[row]))

    def putstr(self, text):
        for char in text:
            if char == "\n":
                self.move_to(0, 1)
            else:
                self._write8(ord(char), LCD_DATA)

    def show(self, line1, line2=""):
        self.clear()
        self.move_to(0, 0)
        self.putstr(line1[: self.cols])
        self.move_to(0, 1)
        self.putstr(line2[: self.cols])


led = Pin(LED_PIN, Pin.OUT)
button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
buzzer_pin = Pin(BUZZER_PIN, Pin.OUT)
buzzer_pwm = PWM(Pin(BUZZER_PIN))
buzzer_pwm.duty_u16(0)
i2c = I2C(0, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN), freq=100000)


def make_lcd():
    devices = i2c.scan()
    if not devices:
        return None
    return I2cLcd1602(i2c, devices[0])


lcd = make_lcd()


def lcd_show(line1, line2=""):
    if lcd:
        lcd.show(line1, line2)


def led_on():
    led.value(1)


def led_off():
    led.value(0)


def buzzer_on():
    if PASSIVE_BUZZER:
        buzzer_pwm.freq(2200)
        buzzer_pwm.duty_u16(32768)
    else:
        buzzer_pin.value(1)


def buzzer_off():
    if PASSIVE_BUZZER:
        buzzer_pwm.duty_u16(0)
    else:
        buzzer_pin.value(0)


def alert_on():
    led_on()
    buzzer_on()
    lcd_show("DEER DETECTED", "SLOW DOWN")


def alert_off():
    led_off()
    buzzer_off()
    lcd_show("SAFE ROAD", "Monitoring...")


def beep_startup():
    for _ in range(2):
        led_on()
        buzzer_on()
        time.sleep(0.12)
        led_off()
        buzzer_off()
        time.sleep(0.12)


def handle_command(command):
    command = command.strip().lower()

    if command in ("1", "on", "detect", "detected", "deer", "gorani"):
        alert_on()
        print("ALERT ON")
    elif command in ("0", "off", "clear", "safe", "stop"):
        alert_off()
        print("ALERT OFF")
    elif command in ("beep", "test"):
        lcd_show("SAFE ROAD", "LCD TEST")
        beep_startup()
        print("TEST OK")


poll = select.poll()
poll.register(sys.stdin, select.POLLIN)

button_alert_active = False

alert_off()
beep_startup()
lcd_show("SAFE ROAD", "Ready")
print("Pico alert ready. Send 1/on to alert, 0/off to stop.")

while True:
    if poll.poll(100):
        handle_command(sys.stdin.readline())

    if button.value() == 0 and not button_alert_active:
        button_alert_active = True
        alert_on()
        print("BUTTON ALERT ON")
    elif button.value() == 1 and button_alert_active:
        button_alert_active = False
        alert_off()
        print("BUTTON ALERT OFF")

    time.sleep(0.01)
