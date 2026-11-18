# should be presaved onto the ESP 32 board
import random
import math

class SensorModel:
    def __init__ (self):
        # 0.05 is the standard deviation of the temperature probe(line temperature sensor)
        self.temperature_deviation = 0.05
        # My DROK waterproof DS18B20 temperature probes has a 12_bit resolution(increments of 0.0625)
        self.temperature_resolution = 0.0625

        # stores the standard calibration constant for a different type of sencers(SEN0216 sensors)
        # water flow sensor that generate pulse per liter of water that goes throught it
        self.flow_pulses_per_litre = 5880
        # for pulse that are not within exactly a sec and was carried to the next second
        self.pulse_remainder = 0.0

    # Simulating sensor noise
    def measure_temp(self, actual_temp):
        temp_noise = random.gauss(0, self.temperature_deviation)
        # Calculate the actual temp and express it in the accruacy of the sensor
        actual_temp = round((actual_temp + temp_noise) / self.temperature_resolution) * self.temperature_resolution
        return actual_temp

    # Actual flow is in liters per min
    def measure_flow(self, actual_flow):
        actual_pulse = actual_flow / 60 * self.flow_pulses_per_litre
        # use math floor to push the remainder toward the pulse count for the next sec
        current_whole_pulse = math.floor(actual_pulse + self.pulse_remainder)
        self.pulse_remainder = actual_pulse + self.pulse_remainder - current_whole_pulse 
        # the sensor only count whole number pulses
        measured_flow = current_whole_pulse * 60 / self.flow_pulses_per_litre
        measured_flow = round( measured_flow * 100 ) / 100
        return measured_flow
                