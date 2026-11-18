import math
from heat_transfer import HeatExchanger

class PhysicsSimulator:

    # The class heat exchanger should be passed in as on of the inputs
    def __init__(self, heat_exchanger, time_step_sec, thermal_time_constant):
        self.heat_exchanger = heat_exchanger
        self.time_step_sec = time_step_sec
        self.thermal_time_constant = thermal_time_constant

    # The fraction of the remaining gap that the temperature closes in one step(one step per second)
    def calc_response_factor(self):
        if self.thermal_time_constant <= 0:
            raise ValueError("Thermal time constant must be positive")
        if self.time_step_sec <= 0:
            raise ValueError("Time step must be positive")
        
        alpha = 1 - math.exp( -self.time_step_sec / self.thermal_time_constant)
        return alpha

    def update_temperature(self, current_temp, target_temp):
        alpha = self.calc_response_factor()
        T_next = current_temp + alpha * (target_temp - current_temp)
        return T_next

    def simulate_step(self, hot_mass_flow, cold_mass_flow, current_hot_reservoir_temp, current_cold_reservoir_temp, UA, current_hot_temp, current_cold_temp):
        # Get the predicted outlet temperatures from the method in HeatExchanger class
        target_hot_outlet, target_cold_outlet = self.heat_exchanger.predict_outlet_temperatures(
            hot_mass_flow, 
            cold_mass_flow, 
            current_hot_reservoir_temp, 
            current_cold_reservoir_temp, 
            UA)
        next_hot_temp = self.update_temperature(current_hot_temp, target_hot_outlet)
        next_cold_temp = self.update_temperature(current_cold_temp, target_cold_outlet)
        return next_hot_temp, next_cold_temp

    # For running the above simulation and change mass flow if the valve is restricted
    def run_simulation(
            self, 
            hot_mass_flow, 
            cold_mass_flow, 
            hot_inlet_temp, 
            cold_inlet_temp, 
            UA, duration_sec, 
            hot_water_mass, 
            cold_water_mass, 
            restriction_time_sec=None, 
            restricted_hot_mass_flow=None,
            restricted_cold_mass_flow=None):
        
        current_hot_mass_flow = hot_mass_flow
        current_cold_mass_flow = cold_mass_flow
        # temperature of water enterin the heat exchanger form the reservoir
        current_hot_reservoir_temp = hot_inlet_temp
        current_cold_reservoir_temp = cold_inlet_temp
        time_record = [0]
        # temperature of water leaving the exchanger at the start of the simulation
        initial_hot_temp, initial_cold_temp = self.heat_exchanger.predict_outlet_temperatures(
            hot_mass_flow, 
            cold_mass_flow, 
            hot_inlet_temp, 
            cold_inlet_temp, 
            UA)
        hot_temp_record = [initial_hot_temp]
        cold_temp_record = [initial_cold_temp]

        hot_reservoir_temp_record = [current_hot_reservoir_temp]
        cold_reservoir_temp_record = [current_cold_reservoir_temp]

        hot_mass_flow_record = [current_hot_mass_flow]
        cold_mass_flow_record = [current_cold_mass_flow]

        current_hot_temp = initial_hot_temp
        current_cold_temp = initial_cold_temp
        num_steps = int(duration_sec / self.time_step_sec)

        for i in range(num_steps):
            # Change the value of water's flow mass when the value is restricted to simulate fouling
            # restriction start as rectriction time sec and continuees afterwards
            if restriction_time_sec != None and i * self.time_step_sec >= restriction_time_sec:
                if restricted_hot_mass_flow != None:
                    current_hot_mass_flow = restricted_hot_mass_flow
                if restricted_cold_mass_flow != None:
                    current_cold_mass_flow = restricted_cold_mass_flow
                

            # temperature of hot water leaving the heat exchanger
            current_hot_temp, current_cold_temp = self.simulate_step(
            # amount of hot water flowing through the exchanger each second
            current_hot_mass_flow, 
            current_cold_mass_flow, 
            # temperature of water in the hot reservoir
            current_hot_reservoir_temp, 
            current_cold_reservoir_temp, 
            UA, 
            current_hot_temp, 
            current_cold_temp)

            current_hot_heat_transfer_rate = self.heat_exchanger.calc_hot_heat_transfer(
                current_hot_mass_flow, 
                current_hot_reservoir_temp, 
                current_hot_temp)
            current_cold_heat_transfer_rate = self.heat_exchanger.calc_cold_heat_transfer(
                current_cold_mass_flow, 
                current_cold_reservoir_temp, 
                current_cold_temp)

            current_hot_reservoir_temp = self.update_reservoir_temperature(
                current_hot_reservoir_temp, 
                current_hot_heat_transfer_rate, 
                hot_water_mass, 
                True)
            current_cold_reservoir_temp = self.update_reservoir_temperature(
                current_cold_reservoir_temp, 
                current_cold_heat_transfer_rate, 
                cold_water_mass, 
                False)

            # for temperature
            time_record.append((i + 1 )* self.time_step_sec)
            hot_temp_record.append(current_hot_temp) 
            cold_temp_record.append(current_cold_temp) 
            hot_reservoir_temp_record.append(current_hot_reservoir_temp) 
            cold_reservoir_temp_record.append(current_cold_reservoir_temp) 

            # for flow rate converted to kg/s
            hot_mass_flow_record.append(current_hot_mass_flow) 
            cold_mass_flow_record.append(current_cold_mass_flow) 

        return time_record, hot_temp_record, cold_temp_record, hot_reservoir_temp_record, cold_reservoir_temp_record, hot_mass_flow_record, cold_mass_flow_record

    def update_reservoir_temperature(self, current_temp, heat_transfer_rate, water_mass, is_hot_reservoir):
        if water_mass <= 0:
            raise ValueError("Water mass must be positive")
        reservoir_temp_change = (heat_transfer_rate * self.time_step_sec) / (water_mass * self.heat_exchanger.specific_heat)
        if is_hot_reservoir is False:
            temp_next = current_temp + reservoir_temp_change
        else:
            temp_next = current_temp - reservoir_temp_change
        return temp_next