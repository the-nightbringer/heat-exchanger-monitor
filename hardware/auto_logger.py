import serial

class AutoLogger:
    # baud rate to track speed to transmit information in untis of bits
    def __init__ (self, port="COM4", baud_rate=115200, csv_file="temperature_measurements.csv"):
        self.port = port
        self.baud_rate = baud_rate
        self.csv_file = csv_file

    def connect(self):
        # first is library name, second is class name
        # creates a serial object to store the three parameters and establish serial communication with the board and computer
        self.connection = serial.Serial(self.port, self.baud_rate, timeout=1)

    def read_line(self):
        # return the decoded string without any whtiespace(from a byte sequence)
        return self.connection.readline().decode("utf-8").strip()

    def open_file(self):
        # opening a file object
        # raise an error if the file already exists/ create that file and write into that file
        self.file = open(self.csv_file, "x")
        self.file.write("Ti(s), Te18(C), Te19(C), Te21(C), Te22(C)\n")

    # Close the file and port if they are open
    def close(self):
        if hasattr(self, "connection") and self.connection.is_open:
            self.connection.close()
        if hasattr(self, "file") and not self.file.closed:
            self.file.close()

'''
# test
logger = AutoLogger(csv_file="experiments/healthy_data/run_001.csv")
logger.connect()
logger.open_file()

for i in range(100):
    line = logger.read_line()
    print(line)
    if line != "":
        logger.file.write(line + "\n")

logger.connection.close()
logger.file.close()
'''