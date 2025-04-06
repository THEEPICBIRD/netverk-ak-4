import serial
import time

# Get user inputs
port = input("Enter serial port (e.g. COM3 or /dev/ttyUSB0): ")
username = input("Enter new username to configure: ")
password = input("Enter password for user (and enable, if needed): ")
ip_address = input("Enter management IP address for the switch (e.g. 192.168.1.10 255.255.255.0): ")
default_gateway = input("Enter default gateway for the switch (e.g. 192.168.1.1): ")
interface = "Vlan1"

# Open serial connection with Cisco default settings (9600 8N1)
ser = serial.Serial(
    port=port,
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

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

# Enter global configuration mode
ser.write(b"configure terminal\r\n")
time.sleep(1)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# Commands to configure SSH and set management IP on VLAN1, plus a default gateway
commands = [
    "hostname SSHSwitch",                                # Set hostname (optional)
    "ip domain-name localdomain",                        # Domain name required for RSA key generation
    f"interface {interface}",                            # Enter VLAN 1 interface
    f"ip address {ip_address}",                          # Set management IP (e.g., "192.168.1.10 255.255.255.0")
    "no shutdown",                                       # Ensure the interface is up
    "exit",                                              # Exit interface configuration mode
    f"ip default-gateway {default_gateway}",             # Set the default gateway for management traffic
    "enable secret cisco",
    f"username {username} privilege 15 secret {password}", # Create local user with privilege 15
    "line vty 0 4",                                     # Configure VTY lines for SSH
    "login local",                                      # Use local authentication for VTY
    "transport input ssh",                              # Allow only SSH for remote access
    "exit",                                             # Exit line configuration mode
    "ip ssh version 2",                                 # Force SSH version 2
    "crypto key generate rsa modulus 2048",             # Generate a 2048-bit RSA key (may prompt for confirmation)
    "end"                                               # Exit configuration mode
]

# Send each command, waiting between commands
for cmd in commands:
    ser.write((cmd + "\r\n").encode())
    time.sleep(1)
    resp = ser.read(ser.in_waiting or 1).decode(errors='ignore')
    if resp:
        print(resp, end="")

# Save running config to startup config
ser.write(b"write memory\r\n")
time.sleep(2)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
if output:
    print(output)

print("SSH configuration on Layer 2 Switch applied and saved.")
ser.close()
