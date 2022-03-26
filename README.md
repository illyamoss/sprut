<h1 align="center">Sprut - files transfer.</h1>


<p align="center">
<img
    src="https://github.com/qXytreXp/images/blob/master/Sprut.jpg"
    width="370px" height="290px" border="0" alt="sprut">
<br>
</p>

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
Code is: go-twenty-nation

On the other computer run:
sprut recieve go-twenty-nation

Connection: ('9.63.3.55', 57612)

Data succussful transferred
Good bye BOSS! Have a nice day.
```
Recieve files:
```
$ sprut recieve go-twenty-nation
Connection...
Connected to the server
Accept files?(Y/n): y
File: file.txt delivered
Data succussful transferred
Good bye BOSS! Have a nice day.
```
# For developers
For those who want to complete the project.
You must have Python version 3.10 and higher installed.
Make a clone of this repository.
```
$ git clone https://github.com/qXytreXp/sprut
```
Navigate to the project directory and create a virtual environment.
```
$ cd sprut && python3.10 -m venv env
```
Set all dependencies for the project.
```
$ python3.10 -m pip install -r requirements-dev.txt
```
After you have completed the project, check whether you have not broken the ready-made logic.
```
$ pytest -v -x tests/
```
