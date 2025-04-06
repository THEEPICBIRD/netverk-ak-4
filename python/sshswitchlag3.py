import serial
import time

# Get user inputs
port = input("Enter serial port (e.g. COM3 or /dev/ttyUSB0): ")
username = input("Enter new username to configure: ")
password = input("Enter password for user (and enable, if needed): ")
ip_addr = input("Enter IP address for the switch (e.g. 192.168.x.x): ")

# Open serial connection
try:
    ser = serial.Serial(port=port, baudrate=9600, bytesize=serial.EIGHTBITS,
                       parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,
                       timeout=10)
except Exception as e:
    print("Error: Could not open serial port.")
    exit(1)

# Clear any initial data and wake up the device
ser.flushInput()
ser.write(b"\r\n")
time.sleep(1)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# Handle initial setup dialogue or login prompts
if "yes/no" in output:
    ser.write(b"no\r\n")
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

if "Username:" in output:
    ser.write((username + "\r\n").encode())
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

if "Password:" in output:
    ser.write((password + "\r\n").encode())
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# Now at user EXEC (>) or privileged EXEC (#). Check and enter enable mode if needed.
if '>' in output:
    ser.write(b"enable\r\n")
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
    if "Password:" in output:
        ser.write((password + "\r\n").encode())
        time.sleep(1)
        output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# Enter global config mode
ser.write(b"configure terminal\r\n")
time.sleep(1)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# List of commands for Layer 3 Switch SSH configuration
commands = [
    "hostname SSHLayer3",                          # optional: set hostname
    "interface vlan 1",                            # configure SVI on VLAN 1
    f"ip address {ip_addr} 255.255.255.0",         # set IP address (assuming /24)
    "no shutdown",
    "exit",                                        # exit interface config
    "ip domain-name example.com",                   # domain name required for RSA key
    "enable secret cisco",
    f"username {username} privilege 15 password {password}",
    "crypto key generate rsa modulus 1024",         # generate RSA key pair
    "ip ssh version 2",                            # use SSH version 2
    "line vty 0 4",                                # configure VTY lines
    "login local",                                 # local user auth
    "transport input ssh",                         # only allow SSH
    "end"
]

# Execute commands one by one
for cmd in commands:
    ser.write((cmd + "\r\n").encode())
    time.sleep(1)  # wait for the device to process the command
    response = ser.read(ser.in_waiting or 1).decode(errors='ignore')
    if response:
        print(response, end="")

# (Optional) Save configuration to startup
ser.write(b"write memory\r\n")
time.sleep(2)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
if output:
    print(output)

print("Layer 3 Switch SSH configuration complete.")
ser.close()
