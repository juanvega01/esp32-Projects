import network
import socket
from time import sleep
from picozero import pico_temp_sensor, pico_led
import machine
import utime

ssid = ''
password = ''


def connect():
    #Connect to WLAN
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')
    return ip

def open_socket(ip):
    # Open a socket
    address = (ip, 80)
    connection = socket.socket()
    connection.bind(address)
    connection.listen(1)
    return connection

def webpage(temperature, state):
    #Template HTML
    html = f"""
<!DOCTYPE html>
<html>
<style>
<title>Control de LED</title>
<style>
body {
font-family: Arial, sans-serif;
background-color: #f0f0f0;
}
h1 {
text-align: center;
color: #333;
}
form {
margin: 20px auto;
text-align: center;
}
input[type="submit"] {
background-color: #4CAF50;
color: white;
font-size: 16px;
border-radius: 5px;
padding: 10px;
border: none;
cursor: pointer;
 size: 100px;
 width: 150px;
height: 50px;
}
input[type="submit"]:hover {
background-color: #3e8e41;
}
p {
text-align: center;
margin-top: 20px;
font-size: 18px;
color: #333;
}
@media screen and (max-width:767px) {
body {
font-family: Arial, sans-serif;
background-color: #f0f0f0;
}
h1 {
text-align: center;
color: #333;
}
form {
margin: 20px auto;
text-align: center;
}
input[type="submit"] {
background-color: #4CAF50;
color: white;
font-size: 16px;
border-radius: 5px;
padding: 10px;
border: none;
cursor: pointer;
            
width: 170px;
height: 70px;
}
input[type="submit"]:hover {
background-color: #3e8e41;
}
p {
text-align: center;
margin-top: 30px;
font-size: 24px;
color: #333;
}
}
</style>
   
<meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
<h1>Control de LED y temperatura</h1>
<form action="./lighton">
<input type="submit" value="Light on" style="background-color: green; color: white; font-size: 16px; border-radius: 5px; padding: 10px;" />
</form>
<form action="./lightoff">
<input type="submit" value="Light off" style="background-color: red; color: white; font-size: 16px; border-radius: 5px; padding: 10px;" />
</form>
<p>LED is {state}</p>
<p>Temperature is {temperature}</p>
</body>
</html>
            """
    return str(html)

def serve(connection):
    #Start a web server
    state = 'OFF'
    #pico_led.off()
    led_externo = machine.Pin(15,machine.Pin.OUT)
    temperature = 0
    while True:
        client = connection.accept()[0]
        request = client.recv(1024)
        request = str(request)
        try:
            request = request.split()[1]
        except IndexError:
            pass
        if request == '/lighton?' and temperature > 29:
            led_externo.on()
            utime.sleep(1)
            state = 'ON'
            
            #if temperature > 29:
                #led_externo.on()
                
        elif request =='/lightoff?':
            led_externo.off()
            state = 'OFF'
            
        temperature = pico_temp_sensor.temp
        html = webpage(temperature, state)
        client.send(html)
        client.close()
    
try:
    ip = connect()
    connection = open_socket(ip)
    serve(connection)
except KeyboardInterrupt:
    machine.reset()
