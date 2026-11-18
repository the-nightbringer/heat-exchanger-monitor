import matplotlib.pyplot as plt
import pandas as pd

class TemperatureGraph:
    def __init__ (self, csv_file="temperature_measurements.csv"):
        self.csv_file = csv_file
        # creates a dictionary of the between the offset values gotten in room temp and hot water test
        self.test_offsets = {"18": 0.002683, "19": 0.068655, "21": -0.007418, "22": -0.063921}

    def data_to_graph (self):
        # reads the data numerically in the csv file 
        # And store them as a Dataframe(starting from the secon row to avoid repeating the header)
        self.data = pd.read_csv(self.csv_file).iloc[1:]
        self.data.columns = self.data.columns.str.strip()
        self.data = self.data.apply(pd.to_numeric)
        self.data["Te18(C)Corrected"] = self.data["Te18(C)"] - self.test_offsets["18"]
        self.data["Te19(C)Corrected"] = self.data["Te19(C)"] - self.test_offsets["19"]
        self.data["Te21(C)Corrected"] = self.data["Te21(C)"] - self.test_offsets["21"]
        self.data["Te22(C)Corrected"] = self.data["Te22(C)"] - self.test_offsets["22"]


    def graph_temp(self):
        plt.plot(self.data["Ti(s)"], self.data["Te18(C)"], label="Hot Inlet Sensor Readings")
        plt.plot(self.data["Ti(s)"], self.data["Te19(C)"], label="Hot Outlet Sensor Readings")
        plt.plot(self.data["Ti(s)"], self.data["Te21(C)"], label="Cold Inlet Sensor Readings")
        plt.plot(self.data["Ti(s)"], self.data["Te22(C)"], label="Cold Outlet Sensor Readings")

        plt.plot(self.data["Ti(s)"], self.data["Te18(C)Corrected"], label="Corrected Hot Inlet Sensor Readings")
        plt.plot(self.data["Ti(s)"], self.data["Te19(C)Corrected"], label="Corrected Hot Outlet Sensor Readings")
        plt.plot(self.data["Ti(s)"], self.data["Te21(C)Corrected"], label="Corrected Cold Inlet Sensor Readings")
        plt.plot(self.data["Ti(s)"], self.data["Te22(C)Corrected"], label="Corrected Cold Outlet Sensor Readings")
        
        plt.xlabel("Time (s)")
        plt.ylabel("Water Temperature from ds18x20 Sensors(°C)")
        plt.title("Time-Dependent Temperature Change of Four Location in Heat Exchanger")
        plt.legend()
        plt.grid(True)
        plt.show()

    def sensor_statistics(self):
        mean = self.data[["Te18(C)", "Te19(C)", "Te21(C)", "Te22(C)"]].mean()
        # offset is calculated by average of each sensor minus the overall mean
        offset = mean - mean.mean()
        stan_deviation = self.data[["Te18(C)", "Te19(C)", "Te21(C)", "Te22(C)"]].std()

        corrected_mean = self.data[["Te18(C)Corrected", "Te19(C)Corrected", "Te21(C)Corrected", "Te22(C)Corrected"]].mean()
        # offset is calculated by average of each sensor minus the overall mean
        correct_offset =  corrected_mean -  corrected_mean.mean()
        
        return mean, offset, stan_deviation, corrected_mean, correct_offset


temp_graph = TemperatureGraph()
temp_graph.data_to_graph()
print(temp_graph.data.head())
temp_graph.graph_temp()

mean, offset, deviation, corrected_mean, correct_offset = temp_graph.sensor_statistics()

print(mean)
print(offset)
print(deviation)

print(corrected_mean)
print(correct_offset)