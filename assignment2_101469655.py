"""
Author: Carrie Arevalo
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# Step II
import socket
import threading
import sqlite3
import os
import platform
import datetime


# Step III
print("Python Version:", platform.python_version())
print("Operating System:", os.name)


# STEP IV
# Stores common port numbers and their service names
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}


# STEP V - Network Tool Class

class NetworkTool:
    def __init__(self, target):
        self.__target = target
    # Q3: What is the benefit of using @property and @target.setter?
    # The benefit of using @property and @target.setter is that it allows the program to control access to the target value
    # Because the target is private, we can still safely read or update it.
    # The setter also stops the target from being changed to an emtpy string.
    @property
    def target(self):
        return self.__target
    @target.setter
    def target(self, value):
        if value == "":
            print("Error: Target cannot be empty")
        else:
            self.__target = value
    def __del__(self):
        print("NetworkTool instance destroyed")


# Q1: How does PortScanner reuse code from NetworkTool?
# PortScanner reuses code from NetworkTool through inheritance.
# For example, it calls super().__init__(target) so the target setup is handled by the parent class.
# Code is saved because the child class does not need to rewrite the target logic.

# STEP VI
class PortScanner(NetworkTool):
    # constructor
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()
    # destructor
    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()

    def scan_port(self, port):
        sock = None

        # Q4: What would happen without try-except here?
        # A socket error could stop the whole program while scanning.
        # If the machine can't be reached, the scan might crash before checking the rest of the ports.
        # Exception handling lets the program continue running and show the error safely.
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))

            if result == 0:
                status = "Open"
            else:
                status = "Closed"

            service_name = common_ports.get(port, "Unknown")

            with self.lock:
                self.scan_results.append((port, status, service_name))

        except socket.error as error:
            print(f"Error scanning port {port}: {error}")

        finally:
            if sock:
                sock.close()

    def get_open_ports(self):
        return [result for result in self.scan_results if result[1] == "Open"]

    # Q2: Why do we use threading instead of scanning one port at a time?
    # Threading is used because it allows multiple ports to be scanned at the same time.
    # If all ports were scanned one by one, the program would take longer because each connection is waiting for a response.
    # Threading makes the scan faster by letting those waits happen at the same time.

    def scan_range(self, start_port, end_port):
        threads = []

        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

# Step VII: Create save_results(target, results) function
def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target TEXT,
            port INTEGER,
            status TEXT,
            service TEXT,
            scan_date TEXT
        )
        """)

        for port, status, service in results:
            cursor.execute("""
                INSERT INTO scans (target, port, status, service, scan_date)
                VALUES (?, ?, ?, ?, ?)
            """, (target, port, status, service, str(datetime.datetime.now())))

        conn.commit()
        conn.close()

    except sqlite3.Error as error:
        print(f"Database error: {error}")


# STEP VIII: Create load_past_scans() function
def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()

        cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
        rows = cursor.fetchall()

        if not rows:
            print("No past scans found.")
        else:
            for target, port, status, service, scan_date in rows:
                print(f"[{scan_date}] {target} : Port {port} ({service}) - {status}")

        conn.close()

    except sqlite3.Error:
        print("No past scans found.")

# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    # STEP IX: Get user input with try-except (Step ix)
    target = input("Enter target IP address: ").strip()
    if target == "":
        target = "127.0.0.1"

    try:
        start_port = int(input("Enter start port: "))
        end_port = int(input("Enter end port: "))

        if start_port < 1 or start_port > 1024 or end_port < 1 or end_port > 1024:
            print("Port must be between 1 and 1024.")
        elif end_port < start_port:
            print("End port must be greater than or equal to start port.")
        else:
            # STEP X: After valid input (Step x)
            scanner = PortScanner(target)
            print(f"Scanning {target} from port {start_port} to {end_port}...")

            scanner.scan_range(start_port, end_port)
            open_ports = scanner.get_open_ports()

            print(f"\n--- Scan Results for {target} ---")
            for port, status, service in open_ports:
                print(f"Port {port}: {status} ({service})")
            print("------")
            print(f"Total open ports found: {len(open_ports)}")

            save_results(target, scanner.scan_results)

            choice = input("Would you like to see past scan history? (yes/no): ").strip().lower()
            if choice == "yes":
                load_past_scans()
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
# Q5: New Feature Proposal
# Category labeling such as web, remote access, or other for open ports would be a new feature I would add.
# By using a nested if-statement, the program would check the port number and decide which category message to display.
# Diagram: See diagram_101469655.png in the repository root