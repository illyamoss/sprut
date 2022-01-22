<p align="center">
<img
    src="https://github.com/qXytreXp/images/blob/master/Sprut.jpg"
    width="370px" height="290px" border="0" alt="sprut">
<br>
</p>

# Sprut - files transfer. 
`sprut` is a tool that allow securely and simply transfer files from one computer to another 📦
- Allows **any two computers** to transfer data;
- enables **platforms:** Linux, MacOS, Windows(ToDo);
- provides **end-to-end encryption** using RSA Asymmetric Algorithm;
- data does not pass through third-party servers;
- allows **multiple file** transfers;
- allows **resuming transfers** that are interrupted;
- only CLI.

# Install
ToDo

# Usage
Send files:
```
$ sprut send file.txt
Sprut server started
Sending files:
file.txt
Code is: 9.63.3.55:41797_go-twenty-nation

On the other computer run:
sprut recieve 9.63.3.55:41797_go-twenty-nation

Connection: ('<address>', 57612)

Data succussful transferred
Good bye BOSS! Have a nice day.
```
Recieve files:
```
$ sprut recieve 9.63.3.55:41797_go-twenty-nation
Connection...
Connected to the server
Accept files?(Y/n): y
File: file.txt delivered
Data succussful transferred
Good bye BOSS! Have a nice day.
```
