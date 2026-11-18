import math

# Calculations based on steady-state readings
class HeatExchanger:
    
    def __init__(self, specific_heat):
        self.specific_heat = specific_heat

    # Input mass flow must already be in kg/s.
    # Calculate the rate of heat removed from the hot-water stream
    # A negative result means that heat is being added to the hot-water stream
    def calc_hot_heat_transfer(self, hot_mass_flow, hot_inlet_temp, hot_outlet_temp):
        hot_difference_temp = hot_inlet_temp - hot_outlet_temp
        hot_heat_transfer = hot_mass_flow * self.specific_heat * hot_difference_temp
        return hot_heat_transfer

    # Input mass flow must already be in kg/s.
    # Calculate the rate of heat added to the cold-water stream
    # A negative result means the cold-water stream is losing heat
    def calc_cold_heat_transfer(self, cold_mass_flow, cold_inlet_temp, cold_outlet_temp):
        cold_difference_temp = cold_outlet_temp - cold_inlet_temp
        cold_heat_transfer = cold_mass_flow * self.specific_heat * cold_difference_temp
        return cold_heat_transfer

    def calc_capacity_rate(self, mass_flow):
        return mass_flow * self.specific_heat

    def calc_min_capacity(self, hot_mass_flow, cold_mass_flow):
        hot_capacity = self.calc_capacity_rate(hot_mass_flow)
        cold_capacity = self.calc_capacity_rate(cold_mass_flow)
        C_min = min(hot_capacity, cold_capacity)
        if C_min <= 0:
            raise ValueError("Minimum capacity undefined, stream has no or negative flow reading")
        return C_min

    def calc_max_capacity(self, hot_mass_flow, cold_mass_flow):
        hot_capacity = self.calc_capacity_rate(hot_mass_flow)
        cold_capacity = self.calc_capacity_rate(cold_mass_flow)
        C_max = max(hot_capacity, cold_capacity)
        if C_max <= 0:
            raise ValueError("Maximum capacity undefined, stream has no or negative flow reading")
        return C_max

    def calc_effectiveness(self, hot_mass_flow, cold_mass_flow, hot_inlet_temp, hot_outlet_temp, cold_inlet_temp, cold_outlet_temp):
        C_min = self.calc_min_capacity(hot_mass_flow, cold_mass_flow)
        max_transfer = C_min * (hot_inlet_temp - cold_inlet_temp)
        if max_transfer <= 0:
            raise ValueError("Effectiveness undefined, heat transfer must be positive")
        actual_transfer = (self.calc_hot_heat_transfer(hot_mass_flow, hot_inlet_temp, hot_outlet_temp) + self.calc_cold_heat_transfer(cold_mass_flow, cold_inlet_temp, cold_outlet_temp)) / 2
        effectiveness = actual_transfer / max_transfer
        return effectiveness

    # UA will be calculated later with the counterflow relationship after setting up the physical components
    def calc_ntu(self, hot_mass_flow, cold_mass_flow, UA):
        C_min = self.calc_min_capacity(hot_mass_flow, cold_mass_flow)
        NTU = UA / C_min
        if NTU <= 0:
            raise ValueError("NTU negative, UA readings must be positive")
        return NTU

    def calc_capacity_ratio(self, hot_mass_flow, cold_mass_flow):
        C_max = self.calc_max_capacity(hot_mass_flow, cold_mass_flow)
        C_min = self.calc_min_capacity(hot_mass_flow, cold_mass_flow)
        return C_min / C_max

    # estimate counterflow effectiveness from assumed UA and mass flow rates
    def estimate_effectiveness(self, hot_mass_flow, cold_mass_flow, UA):
        Capacity_ratio = self.calc_capacity_ratio(hot_mass_flow, cold_mass_flow)
        NTU = self.calc_ntu(hot_mass_flow, cold_mass_flow, UA)
        if Capacity_ratio == 1:
            effectiveness = NTU / (1 + NTU)
        else:
            temp = math.exp(-NTU * (1 - Capacity_ratio))
            effectiveness = (1 - temp) / (1 - Capacity_ratio * temp)
        return effectiveness

    def predict_outlet_temperatures(self, hot_mass_flow, cold_mass_flow, hot_inlet_temp, cold_inlet_temp, UA):
        hot_capacity = self.calc_capacity_rate(hot_mass_flow)
        cold_capacity = self.calc_capacity_rate(cold_mass_flow)
        C_min = self.calc_min_capacity(hot_mass_flow, cold_mass_flow)
        predicted_effectiveness = self.estimate_effectiveness(hot_mass_flow, cold_mass_flow, UA)

        predicted_actual_transfer = predicted_effectiveness * C_min * (hot_inlet_temp - cold_inlet_temp)

        # Predict the outlet temperatures based on the predicted effectiveness
        predicted_hot_outlet_temp = hot_inlet_temp -(predicted_actual_transfer / hot_capacity)
        predicted_cold_outlet_temp = cold_inlet_temp + (predicted_actual_transfer / cold_capacity)

        return predicted_hot_outlet_temp, predicted_cold_outlet_temp
    