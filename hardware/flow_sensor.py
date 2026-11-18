from machine import Pin
import time
import machine


class FlowSensor:
    def __init__ (self, pin_number):
        # tells the ESP32 board that a signal shoudl be received using a particular pin
        self.data_pin = Pin(pin_number, Pin.IN)
        self.pulse_count = 0
        # interupts the program when the eletrical signal rises, and store it in the count pulse variable
        self.data_pin.irq(trigger=Pin.IRQ_RISING, handler=self.add_pulse)
        
    def add_pulse(self, pin):
        self.pulse_count += 1
        
    def reset_pulse(self):
        # temporarily stop the sensor from adding new electtrical pulses while being set to 0
        previous_state = machine.disable_irq()
        self.pulse_count = 0
        machine.enable_irq(previous_state)
        
    def get_pulse_count(self):
        previous_state = machine.disable_irq()
        count = self.pulse_count
        machine.enable_irq(previous_state)
        return count
    
    # calibration factor convert the # of pulses to flow rate in liters per min
    # the average of two runs of one liter(first:5713 pulses, 5211 pulses)
    # assumed the cold flow sensor has the same result as the heat exchange sensor
    def calc_flow_rate(self, frequency, calibration_factor=5192):
        if calibration_factor > 0 and frequency >= 0:
            return 60 * frequency / calibration_factor
        else:
            raise ValueError("Calibration factor should be > 0 and frequency >= 0")
    
    # return time in s
    def calc_time_diff(self, init_time, end_time):
        return time.ticks_diff(end_time, init_time) / 1000
    
    def calc_frequency(self, time_diff, pulse_count):
        if time_diff > 0:
            return pulse_count / time_diff
        else:
            raise ValueError("Time difference should be positive")
        
   
hot_flow_sensor = FlowSensor(25)
'''
hot_flow_sensor.reset_pulse()
print("calibration is ready")
input()
start_pulse = hot_flow_sensor.get_pulse_count()
init_time = time.ticks_ms()

input()
end_pulse = hot_flow_sensor.get_pulse_count()
end_time = time.ticks_ms()
time_change = hot_flow_sensor.calc_time_diff(init_time, end_time)
print((end_pulse - start_pulse) / 1.0)
'''

cold_flow_sensor = FlowSensor(26)







for i in range(50):
    hot_flow_sensor.reset_pulse()
    cold_flow_sensor.reset_pulse()
    
    init_time = time.ticks_ms()
    time.sleep(5)
    end_time = time.ticks_ms()
    # same for both sensors
    time_change = hot_flow_sensor.calc_time_diff(init_time, end_time)
    
    hot_pulse = hot_flow_sensor.get_pulse_count()
    cold_pulse = cold_flow_sensor.get_pulse_count()
    
    hot_frequency = hot_flow_sensor.calc_frequency(time_change, hot_pulse)
    cold_frequency = cold_flow_sensor.calc_frequency(time_change, cold_pulse)
    
    #hot_flow_rate = hot_flow_sensor.calc_flow_rate(hot_frequency, calibration_factor)
    #cold_flow_rate = cold_flow_sensor.calc_flow_rate(cold_frequency, calibration_factor)
    
    #print(time_change, hot_flow_rate, cold_flow_rate)
    print(hot_frequency)
    print(cold_frequency)
    print(hot_pulse, cold_pulse)