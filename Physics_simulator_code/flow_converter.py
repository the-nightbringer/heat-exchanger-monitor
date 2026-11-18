class UnitConverter:
    
    def __init__(self, water_density):
        self.water_density = water_density

    def litres_min_to_kg_sec(self, flow_min):
        mass_flow = flow_min * self.water_density / 60
        return mass_flow

    def kg_sec_to_litres_min(self, mass_flow):
            flow_min = mass_flow * 60 / self.water_density
            return flow_min