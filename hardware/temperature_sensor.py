from machine import Pin
import onewire
import ds18x20
import time

class TemperatureSensor:
    def __init__ (self, pin_number):
        # Creating the ability to choose a specific the GPIO data pin
        self.data_pin = Pin(pin_number)
        # Establishing communication in a selected pin
        self.command = onewire.OneWire(self.data_pin)
        # For temperature specific operations on the digital temperature sensors
        self.temperature = ds18x20.DS18X20(self.command)
        # A list of addresses for each pin
        self.rom = None
        
    def get_rom(self):
        # the scan method searches all the sensors and return their rom addresses
        self.sensor_rom_record = self.temperature.scan()
        if len(self.sensor_rom_record) > 0:
            self.rom = self.sensor_rom_record[0]
        else:
            self.rom = False
        return self.rom
        
    def measure_temp(self):
        # convert temp is a procedure that initiates a conversion and store it within sensor's scratch pad(within the sensor)
        # converts the reading into actual temperature in celsius
        self.temperature.convert_temp()
        
    def get_sensor_temp(self):
        # get the converted temperature from the sensor
        return self.temperature.read_temp(self.rom)


# Storing the pin number in each sensor
sensors = []
for i in [18, 19, 21, 22]:
    sensors.append(TemperatureSensor(i))

temp_bool = True
# Storing the addresses in each pin
for i in range(4):
    sensors[i].get_rom()
    if sensors[i].rom == False:
        print("i")
        temp_bool = False

print("Ti(s), Te18(C), Te19(C), Te21(C), Te22(C)")
start_time = time.ticks_ms()
if  temp_bool == True:
    try:
        while True:
            total_temp_record = []
            
            for i in range(4):
                # read the temperature of the first rom address of each pin
                sensors[i].measure_temp()
                
            time.sleep_ms(750)
            current_time = time.ticks_ms()
            time_difference = time.ticks_diff(current_time, start_time) / 1000
            # print(f"time {time_difference} in sec")
            
            for i in range(4):
                temp = sensors[i].get_sensor_temp()
                total_temp_record.append(temp)
                # 0-18, 1-19. 2-21, 3-22
                #print(f"Current temp: {temp} °C, Sensor GPIO{i}")
                
            print(f"{time_difference}, {total_temp_record[0]}, {total_temp_record[1]}, {total_temp_record[2]}, {total_temp_record[3]}")
                
    except KeyboardInterrupt:
        print("Measurement stopped manually.")
        
else:
    print("No temperature sensor detected.")


