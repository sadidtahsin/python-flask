import socket               # Import socket module

s = socket.socket()         # Create a socket object
host = '192.168.7.51' # Get local machine name
port = 4998  
             # Reserve a port for your service.
s.bind((host, port))        # Bind to the port
print(s) 
s.listen(5)                 # Now wait for client connection.
while True:
   c, addr = s.accept()     # Establish connection with client.
   print ('Got connection from', addr)
   c.send('Thank you for connecting')
   c.close() 