from heat_transfer import HeatExchanger
from flow_converter import UnitConverter
from physics_simulator import PhysicsSimulator
from sensor_model import SensorModel

import matplotlib.pyplot as plt

# Create objects
exchanger = HeatExchanger(4180)
converter = UnitConverter(1.0)
simulator = PhysicsSimulator(
    exchanger,
    time_step_sec=1.0,
    thermal_time_constant=10.0
)
sensor = SensorModel()
hot_flow_sensor = SensorModel()
cold_flow_sensor = SensorModel()

# Example flow rates in L/min
hot_flow = 0.6
cold_flow = 1.2
restricted_hot_flow = 0.4
restricted_cold_flow = 0.4

# Convert flow rates to kg/s
hot_mass_flow = converter.litres_min_to_kg_sec(hot_flow)
cold_mass_flow = converter.litres_min_to_kg_sec(cold_flow)
restricted_hot_mass_flow = converter.litres_min_to_kg_sec(restricted_hot_flow)
restricted_cold_mass_flow = converter.litres_min_to_kg_sec(restricted_cold_flow)

# Example operating conditions
hot_inlet_temp = 40.0
cold_inlet_temp = 5.0
UA = 50.0  # Illustrative value, not measured

# Initial outlet temperatures
# initial_hot_temp = 30.0
# initial_cold_temp = 10.0
# not needed since values are gotten from the predict_outlet_temperatures function in HeatExchanger class

# Amount of water in each reservoir
hot_water_mass = 10
cold_water_mass = 10

duration_sec = 60

# Run the 60-second simulation
time_record, hot_temp_record, cold_temp_record, hot_reservoir_temp_record, cold_reservoir_temp_record, hot_mass_flow_record, cold_mass_flow_record = simulator.run_simulation(
    hot_mass_flow,
    cold_mass_flow,
    hot_inlet_temp,
    cold_inlet_temp,
    UA,
    duration_sec,
    hot_water_mass, 
    cold_water_mass,
    restriction_time_sec=30, 
    # left is the parameter while right is the variables in main
    restricted_hot_mass_flow=restricted_hot_mass_flow,
    restricted_cold_mass_flow=restricted_cold_mass_flow
)

# for water temperature sensor
noisy_hot_inlet_record = []
noisy_hot_outlet_record = []
noisy_cold_inlet_record = []
noisy_cold_outlet_record = []

# for water flow sensor
measured_hot_flow_record = []
measured_cold_flow_record = []

# record how much thermal energy moves from one fluid to another in units of seconds(J/s)
hot_heat_rate_record = []
cold_heat_rate_record = []
# records the difference between cold and hot heat rate
heat_rate_difference_record = []


# loop for recording the values calcluated in the run simulation method from physics simulator
for j in range(len(time_record)):
    # Add the random noises to the values from run simulation method and store them
    noisy_hot_inlet_record.append(sensor.measure_temp(hot_reservoir_temp_record[j]))
    noisy_hot_outlet_record.append(sensor.measure_temp(hot_temp_record[j]))
    noisy_cold_inlet_record.append(sensor.measure_temp(cold_reservoir_temp_record[j]))
    noisy_cold_outlet_record.append(sensor.measure_temp(cold_temp_record[j]))

    # convert mass flow to volumic flow
    current_hot_flow = converter.kg_sec_to_litres_min(hot_mass_flow_record[j])
    current_cold_flow = converter.kg_sec_to_litres_min(cold_mass_flow_record[j])

    # convert volumic flow to whole numbers of eletric pulses
    measured_hot_flow_record.append(hot_flow_sensor.measure_flow(current_hot_flow))
    measured_cold_flow_record.append(cold_flow_sensor.measure_flow(current_cold_flow))

    # populating the heat rate record
    # Keep the calculation in kg/s
    hot_heat_rate_record.append(hot_mass_flow_record[j] * exchanger.specific_heat * (hot_reservoir_temp_record[j] - hot_temp_record[j]))
    cold_heat_rate_record.append(cold_mass_flow_record[j] * exchanger.specific_heat * (cold_temp_record[j] - cold_reservoir_temp_record[j]))
    heat_rate_difference_record.append(hot_heat_rate_record[j] - cold_heat_rate_record[j])


# Temporary print method for validation 
print("Hot flow readings around restriction (L/min):", measured_hot_flow_record[28:34])
print("Cold flow readings around restriction (L/min):", measured_cold_flow_record[28:34])

# Calculate steady-state outlet temperatures for comparison
hot_outlet, cold_outlet = exchanger.predict_outlet_temperatures(
    hot_mass_flow,
    cold_mass_flow,
    hot_inlet_temp,
    cold_inlet_temp,
    UA
)

# Display results
print(f"Simulated hot outlet after 60 s: {hot_temp_record[-1]:.2f} °C")
print(f"Simulated cold outlet after 60 s: {cold_temp_record[-1]:.2f} °C")
print(f"Steady-state hot outlet: {hot_outlet:.2f} °C")
print(f"Steady-state cold outlet: {cold_outlet:.2f} °C")
print(f"Predicted effectiveness: {exchanger.estimate_effectiveness(hot_mass_flow, cold_mass_flow, UA):.3f}")
print(f"Recorded data points: {len(time_record)}")

print(f"Hot reservoir: {hot_reservoir_temp_record[0]:.2f} → {hot_reservoir_temp_record[-1]:.2f} °C")
print(f"Cold reservoir: {cold_reservoir_temp_record[0]:.2f} → {cold_reservoir_temp_record[-1]:.2f} °C")
print(f"Recorded samples: {len(time_record)}")
print("First 10 hot flow readings (L/min):", measured_hot_flow_record[:10])
print("First 10 cold flow readings (L/min):", measured_cold_flow_record[:10])

print("Heat-rate differences around valve restriction (W):", heat_rate_difference_record[28:34])


# Compare healthy and degraded exchanger performance
healthy_UA = 50.0
degraded_UA = 35.0  # Illustrative 30% reduction in UA

healthy_effectiveness = exchanger.estimate_effectiveness(
    hot_mass_flow, cold_mass_flow, healthy_UA
)

degraded_effectiveness = exchanger.estimate_effectiveness(
    hot_mass_flow, cold_mass_flow, degraded_UA
)

print(f"Healthy effectiveness: {healthy_effectiveness:.3f}")
print(f"Degraded effectiveness: {degraded_effectiveness:.3f}")


# Some test values that stay within the .3 -3 L/min range of my SEN0216 sensor
hot_flow_values = [0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0]
healthy_effectiveness_values = []
degraded_effectiveness_values = []
hot_flow_mass = []

for i in range(len(hot_flow_values)):
    hot_flow_mass.append(converter.litres_min_to_kg_sec(hot_flow_values[i])) 
    healthy_effectiveness_values.append(exchanger.estimate_effectiveness(hot_flow_mass[i], cold_mass_flow, healthy_UA))
    degraded_effectiveness_values.append(exchanger.estimate_effectiveness(hot_flow_mass[i], cold_mass_flow, degraded_UA))



# Temperature Graphs
# Plotting the results of temperate change of both outlets(end of the loop)
plt.plot(time_record, hot_temp_record, label="Hot Outlet")
plt.plot(time_record, cold_temp_record, label="Cold Outlet")
plt.xlabel("Elapsed Time (s)")
plt.ylabel("Outlet Water Temperature (°C)")
plt.title("Time-Dependent Temperature Change in a Counterflow Plate Heat Exchanger")
plt.legend()
plt.grid(True)
plt.show()

# Plot hot and cold reservoir temperatures over time(before a loop)
plt.figure()
plt.plot(time_record, hot_reservoir_temp_record, label="Hot Reservoir")
plt.plot(time_record, cold_reservoir_temp_record, label="Cold Reservoir")
plt.xlabel("Elapsed Time (s)")
plt.ylabel("Reservoir Water Temperature (°C)")
plt.title("Reservoir Temperature Change in a Counterflow Plate Heat Exchanger")
plt.legend()
plt.grid(True)
plt.show()

# Compare clean and noisy hot-outlet temperatures
plt.figure()
plt.plot(time_record, hot_temp_record, label="Clean Hot Outlet")
plt.plot(time_record, noisy_hot_outlet_record, label="Simulated DS18B20", alpha=0.7)
plt.plot(time_record, cold_temp_record, label="Clean Cold Outlet")
plt.plot(time_record, noisy_cold_outlet_record, label="Simulated DS18B20", alpha=0.7)
plt.xlabel("Elapsed Time (s)")
plt.ylabel("Outlet Temperature (°C)")
plt.title("Clean vs. Noisy Outlet Temperature")
plt.legend()
plt.grid(True)
plt.show()



# Compare the overall heat transfer conductance(efficiency) of a healthy and degraded heat exchanger on the y axis as the volumic flow increases on the x axis
# Lower ability to conduct energy
plt.figure()
plt.plot(hot_flow_values, healthy_effectiveness_values, label="Healthy UA")
plt.plot(hot_flow_values, degraded_effectiveness_values, label="Degraded UA")
plt.xlabel("Hot-Side Volumetric Flow Rate (L/min)")
plt.ylabel("Effectiveness (ε)")
plt.title("Effectiveness vs. Hot Flow Rate in a Counterflow Plate Heat Exchanger")
plt.legend()
plt.grid(True)
plt.show()

# Compare the performance of healthy and unhealthy UA
# Used only hot flow values since the effectiveness graph already uses hot values
# Choosing hot or cold flow values will not affect the shape of the graph
plt.figure()
# Value times the lengh of the list make a list with constant values
plt.plot(hot_flow_values, [healthy_UA] * len(hot_flow_values), label="Healthy UA")
plt.plot(hot_flow_values, [degraded_UA] * len(hot_flow_values), label="Degraded UA")
plt.xlabel("Hot-Side Volumetric Flow Rate (L/min)")
plt.ylabel("Heat Exchanger Heat-transfer Conductance(W/K)")
plt.title("Heathy and Degraded Heat-transfer Conductance(UA) vs Elapsed Time in a Counterflow Plate Heat Exchanger")
plt.legend()
plt.grid(True)
plt.show()

# Plot the effect of valve restrictions on flow and outlet temperatures
# Less flow mass
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)
# Top graph: Simulated flow sensor readings
# no noise present, but based on whole pulses
ax1.plot(time_record, measured_hot_flow_record, label="Hot Flow")
ax1.plot(time_record, measured_cold_flow_record, label="Cold Flow")
# Setting a vertical dotted line to show valve restriction
ax1.axvline(x=30, color="red", linestyle="--", label="Valve Restriction")
ax1.set_ylabel("Flow Rate (L/min)")
ax1.set_title("Response of Volumic Flow Rate(based on whole pulse rate) vs Elapsed Time to Valve Restriction")
ax1.legend()
ax1.grid(True)
# Bottom graph: Simulated outlet temperatures
# no noise present
ax2.plot(time_record, hot_temp_record, label="Hot Outlet")
ax2.plot(time_record, cold_temp_record, label="Cold Outlet")
ax2.axvline(x=30, color="red", linestyle="--", label="Valve Restriction")
ax2.set_xlabel("Elapsed Time (s)")
ax2.set_ylabel("Outlet Temperature (°C)")
ax2.set_title("Response of Temperature(End of Each Loop) vs Elapsed Time to Valve Restriction")
ax2.legend()
ax2.grid(True)
plt.tight_layout()
plt.show()
