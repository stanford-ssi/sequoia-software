# Circuit Python Tutorial 1: Screen, Cu, and the Serial Console

The PyCubed outputs its data on something called a serial USB connection. 
This is essentially a set of wires running between the PyCubed and another
computer (currently, a Raspberry Pi). This is how we can see PyCubed's output.

## Reading the Serial Connection

On a Unix system, we can access serial connections with files in the `/dev` folder. 
On Linux, Pycubed generally shows up as `/dev/ttyACM0`. From the terminal, it looks like a normal file, but 
reading and writing to it is equivalent to sending bytes on the serial 
connection. 

Some other interesting links if you want to learn more about how
TTY works under the hood. \
[What is a TTY on Linux and How to Use the TTY Command](https://www.howtogeek.com/428174/what-is-a-tty-on-linux-and-how-to-use-the-tty-command/).\
[Terminal Special Files: /dev/tty etc.](http://ftp.lyx.org/pub/sgml-tools/website/HOWTO/Text-Terminal-HOWTO/t1162.html)\
[Difference between tty and ttyACM](https://rfc1149.net/blog/2013/03/05/what-is-the-difference-between-devttyusbx-and-devttyacmx/)

## Screen

How do we actually read and write from the serial interface? There
are several shell programs that can help us do this, like `screen`, `minicom`, `picocom`, `stty`, and `cu`. One of the most popular is screen. 
Screen is already installed on the Raspberry Pi. To access the terminal with it, 
simply run 
```bash
screen /dev/ttyACM0 115200
```
Exit screen with `Ctrl+a, \` (pressing `Ctrl + A`, releasing it, then pressing the \ key). 
If screen has trouble starting up, try pressing return or `Ctrl + D` a couple times until you start seeing output.
**Make sure to exit screen when you're done.**

Another cool screen feature is detaching and reattaching the terminal. You can type `Ctrl + A, d` to dettach the 
screen session. You can then do other things like edit files, and reopen the same screen session just by running
```
screen -r
```
If you do detach the screen session, don't leave it deattached, or the next person will have trouble using screen! You can see full instructions on how 
to use screen by typing 
```
man screen
```

This section is based on the Adafruit tutorial [here](https://learn.adafruit.com/welcome-to-circuitpython/advanced-serial-console-on-mac-and-linux). 
The [official PyCubed documentation](https://www.notion.so/Accessing-the-Serial-Console-bfd69dfcd5f544e4b1c1164f29d8c45f#9a7e569d436b4abc925e508ef3ed6a6e) contains the specifications of the serial connection, as well as info on how to access it on Mac and Windows. 

## Cu

Cu is another alternative to screen. I personally think it works a little better and is a little easier to use. 
To use it, simply run the command
```bash
cu -l /dev/ttyACM0
```
Exiting is done by typing `~.`**Make sure to exit Cu when you're done.**

## Troubleshooting
Only one person can be running screen or cu at the same time. If the screen gives the output ```[screen is terminating]``` 
or cu gives the output  ```cu: /dev/ttyACM0: Line in use```
it's likely there's an unclosed terminal preventing you from accessing the serial output. 
First, double check in Slack to make sure nobody is actively using screen or cu at the same time as you. If not, it's likely 
someone forgot to close their session. To check, run 
```
ps -e | grep screen && ps -e | grep cu
```
This will print output if anybody else is actively running a screen session. If someone's running a screen session, try typing
```
screen -r 
```
This will reattach a deteached screen session, and should allow you to regain control. Otherwise, run 
```
pkill screen && pkill cu
```
These commands might require sudo permissions, so if you don't have administrator access, ping someone who does. 

## Mu (Not on Dataplicity)

Mu is a GUI editor made specifically for working with CircuitPython. It's educational, so it has very few features of a standard IDE.  
However, Mu makes it very easy to access the REPL and see the terminal output. This makes it very easy
to work with CircuitPython boards locally, and eliminates the need to use screen or cu. You can find the Mu documentation
[here](https://codewith.mu)

## The Serial Console and the REPL
Once you've actually connected to the PyCubed, either with `cu` or `screen`, you interact with what's known as the serial console. 
This is the main way of interacting with running CircuitPython devices.

When the serial console first starts, you should see the output of the CircuitPython program. The program will automatically 
restart every time you edit a file. The [CircuitPython documentation](https://learn.adafruit.com/welcome-to-circuitpython/interacting-with-the-serial-console) contains detailed information on how to use the serial console. 

You can also manually restart the program. Simply use the shortcut `Ctrl + C` to stop the running program, then 
press `Ctrl + D` to reload it. From this point, you can also enter the REPL. The REPL is a CircuitPython feature that
allows you to run python line by line, and see results in real time. To enter the REPL, 
stop the running program with `Ctrl + C` and press any key. You can read more details about how to use the REPL on the CircuitPython website [here](https://learn.adafruit.com/welcome-to-circuitpython/the-repl). 

## Command Summary
Here is a summary of the workflow you need to access the CircuitPython output. 

1. ```cu -l /dev/ttyACM0``` 
2. You should see output (or if you don't, press enter a few times). Press Ctrl - C to stop, Ctrl - D to reload and any key to enter the REPL. 
3. Exit by typing `~.` 

