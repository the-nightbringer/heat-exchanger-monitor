import csv
import datetime
import os
from auto_logger import AutoLogger

class ExperimentManager:
    def __init__ (self, run_id, condition, fault_type=None, fault_start_s=None, hot_initial_temp=None, cold_initial_temp=None, notes=None):
        self.run_id = run_id

        if condition == "healthy" or condition == "fault":
            self.condition = condition
        else:
            raise ValueError("input either healthy or fault data")
        
        self.fault_type = fault_type
        self.fault_start_s = fault_start_s

        if condition == "healthy":
            if self.fault_type != None or self.fault_start_s != None:
                self.fault_type=None
                self.fault_start_s=None
                raise ValueError("Healthy data should not have fault type or fault start time")
        if condition == "fault":
            if self.fault_type == None or self.fault_start_s == None:
                raise ValueError("Fault data should have both fault type and fault start time")
            if isinstance(fault_start_s, bool)or  not isinstance(fault_start_s, (int, float)) or fault_start_s < 0:
                raise ValueError("fault starting time must be a positive number")

        if isinstance(hot_initial_temp, (int, float)) and not isinstance(hot_initial_temp, bool) or hot_initial_temp == None:
            self.hot_initial_temp = hot_initial_temp
        else:
            raise ValueError("initial hot temperature must be a number")
        if isinstance(cold_initial_temp, (int, float)) and not isinstance(cold_initial_temp, bool) or cold_initial_temp == None:
            self.cold_initial_temp = cold_initial_temp
        else:
            raise ValueError("initial cold temperature must be a number")

        if isinstance(notes, (str)) or notes == None and not isinstance(notes, bool):
            self.notes = notes
        else:
            raise ValueError("Notes must be a string or nothing")

    def save_metadata(self):
        file_direction = f"experiments/meta_data/{self.run_id}.csv"
        with(open(file_direction, "x", newline="")) as file:
            writer = csv.writer(file)
            temp_column = ["run_id", "date", "condition", "fault_type", "fault_start_s", "hot_initial_temp_C", "cold_initial_temp_C", "notes"]
            date = datetime.date.today().isoformat()
            data_rows = [self.run_id, date, self.condition ,self.fault_type ,self.fault_start_s ,self.hot_initial_temp, self.cold_initial_temp, self.notes]
            writer.writerow(temp_column)
            writer.writerow(data_rows)
        return file_direction 

    def get_data_path(self):
        if self.condition == "healthy":
            file_direction = f"experiments/healthy_data/{self.run_id}.csv"
        else:
            file_direction = f"experiments/fault_data/{self.run_id}.csv"
        return file_direction

    def create_logger(self):
        path = self.get_data_path()
        logger = AutoLogger(csv_file=path)
        return logger

    def prepare_data_logging(self):
        data_path = self.get_data_path()
        meta_data_path = f"experiments/meta_data/{self.run_id}.csv"
        if os.path.exists(data_path) or os.path.exists(meta_data_path):
            raise ValueError("File already exists")
        else:
            self.save_metadata()
            logger = self.create_logger()
            return logger


experiment_manager = ExperimentManager("run_004", "fault", fault_type="hot_restriction", fault_start_s=120.0)
logger = experiment_manager.prepare_data_logging()
print(logger.csv_file)

logger.open_file()
logger.close()

print("File closed:", logger.file.closed)
print("Metadata exists:", os.path.exists("experiments/meta_data/run_004.csv"))
print("Sensor data exists:", os.path.exists(logger.csv_file))
'''
logger.connect()
logger.open_file()

for i in range(100):
    line = logger.read_line()
    print(line)
    if line != "":
        logger.file.write(line + "\n")

logger.connection.close()
logger.file.close()
print(experiment_manager.run_id)
print(experiment_manager.condition)
print(experiment_manager.fault_type)
print(experiment_manager.fault_start_s)
print(experiment_manager.save_metadata())
'''