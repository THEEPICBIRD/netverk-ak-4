import serial
import time

# Get user inputs
port = input("Enter serial port (e.g. COM3 or /dev/ttyUSB0): ")
username = input("Enter new username to configure: ")
password = input("Enter password for user (and enable, if needed): ")
ip_address = input("Enter IP address to assign to the router (e.g. 192.168.1.10/24): ")

# (Optional) If needed, also get interface from user; here we assume GigabitEthernet0/0 for demo
interface = input("Enter interface to assign IP (e.g. GigabitEthernet0/0): ") or "GigabitEthernet0/0"

# Open serial connection with Cisco default settings (9600 8N1)
ser = serial.Serial(port, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, 
                    stopbits=serial.STOPBITS_ONE, timeout=10)

# Clear any initial data and wake up the device
ser.flushInput()
ser.write(b"\r\n")  # send a newline to get the router's attention
time.sleep(1)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')  # read any output

# Handle initial setup dialogue or login prompts
if "yes/no" in output:  # initial configuration dialog prompt
    ser.write(b"no\r\n")  # send "no" to skip initial config dialog&#8203;:contentReference[oaicite:6]{index=6}
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

if "Username:" in output:  # router asking for console login
    ser.write((username + "\r\n").encode())
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
if "Password:" in output:  # if password prompt appears (for console or enable)
    ser.write((password + "\r\n").encode())
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# Now at user EXEC (>) or privileged EXEC (#). Check and enter enable mode if needed.
if '>' in output:  # at user mode, need to elevate to enable mode
    ser.write(b"enable\r\n")
    time.sleep(1)
    output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
    if "Password:" in output:  # provide enable password if asked
        ser.write((password + "\r\n").encode())
        time.sleep(1)
        output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
# At this point, we expect to be at a privileged EXEC prompt (ending in '#').

# Enter global configuration mode
ser.write(b"configure terminal\r\n")
time.sleep(0.5)
# It's good to read output to ensure we entered config mode
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')

# Send configuration commands for SSH setup
commands = [
    f"hostname SSHRouter",                     # set a hostname (optional but good for SSH key name)
    f"ip domain-name localdomain",             # set domain name (required for RSA key generation)&#8203;:contentReference[oaicite:7]{index=7}
    f"interface {interface}",
    f"ip address {ip_address}",                # assign IP and mask to the interface
    "no shutdown",                             # enable the interface
    "exit",                                    # back to global config
    "enable secret cisco",
    f"username {username} secret {password}",  # create local user with secret password
    "line vty 0 4",
    "login local",                             # use local user for VTY login instead of AAA
    "transport input ssh",                     # allow only SSH on VTY lines&#8203;:contentReference[oaicite:8]{index=8}
    "exit",                                    # exit back to global config
    "ip ssh version 2",                        # (optional) force SSH version 2
    "crypto key generate rsa modulus 2048",    # generate RSA key (2048-bit) for SSH
    "end"                                      # exit configuration mode back to exec
]
for cmd in commands:
    ser.write((cmd + "\r\n").encode())
    time.sleep(1)  # wait a bit for each command to be processed
    # Read and print the router's response (for logging/debugging)
    resp = ser.read(ser.in_waiting or 1).decode(errors='ignore')
    if resp:
        print(resp, end="")

# Finally, save the running config to startup config
ser.write(b"write memory\r\n")  # save config to NVRAM&#8203;:contentReference[oaicite:9]{index=9}
time.sleep(2)
output = ser.read(ser.in_waiting or 1).decode(errors='ignore')
if output:
    print(output)

print("SSH configuration applied and saved. You can now test SSH access to the router.")
ser.close()
