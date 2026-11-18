from Physics_simulator_code.flow_converter import UnitConverter
import math

class DataExtractor:
    def __init__(self, hot_inlet_temp, hot_outlet_temp, cold_inlet_temp, cold_outlet_temp, hot_flow_rate, cold_flow_rate):
        self.hot_inlet_temp = hot_inlet_temp
        self.hot_outlet_temp = hot_outlet_temp
        self.cold_inlet_temp = cold_inlet_temp
        self.cold_outlet_temp = cold_outlet_temp
        self.hot_flow_rate = hot_flow_rate
        self.cold_flow_rate = cold_flow_rate
        self.converter = UnitConverter(1.0)

    def hot_temp_drop(self):
        return self.hot_inlet_temp - self.hot_outlet_temp
    
    def cold_temp_rise(self):
        return self.cold_outlet_temp - self.cold_inlet_temp

    def calc_hot_heat_rate(self):
        return self.converter.litres_min_to_kg_sec(self.hot_flow_rate) * 4180 * self.hot_temp_drop()

    def calc_cold_heat_rate(self):
        return self.converter.litres_min_to_kg_sec(self.cold_flow_rate) * 4180 * self.cold_temp_rise()

    # returns the percentage of the heat transfer rates difference with respect to the larger heat transfer rate
    def calc_heat_diff(self):
        hot_heat_rate = abs(self.calc_hot_heat_rate())
        cold_heat_rate = abs(self.calc_cold_heat_rate())
        if max(hot_heat_rate, cold_heat_rate) > 0:
            percentage_heat_rate_diff = abs(hot_heat_rate - cold_heat_rate)/ max(hot_heat_rate, cold_heat_rate) * 100
            return round(percentage_heat_rate_diff, 2)
        else:
            raise ValueError("both heat and cold heat transfer rate should not be 0")

    # calculate the Log Mean Temperature Difference (LMTD) of the 
    def calc_lmtd(self):
        temp_diff1 = self.hot_inlet_temp - self.cold_outlet_temp
        temp_diff2 = self.hot_outlet_temp - self.cold_inlet_temp
        if temp_diff1 > 0 and temp_diff2 > 0:
            if temp_diff1 != temp_diff2:
                return (temp_diff1 - temp_diff2) / math.log(temp_diff1 / temp_diff2)
            else:
                return temp_diff1
        else:
            raise ValueError("The log of temperature difference should be positive")
        


# Test DataExtractor
extractor = DataExtractor(45, 38, 20, 26, 1.26, 1.30)

print("Hot temperature drop:", extractor.hot_temp_drop(), "°C")
print("Cold temperature rise:", extractor.cold_temp_rise(), "°C")
print(extractor.calc_heat_diff())