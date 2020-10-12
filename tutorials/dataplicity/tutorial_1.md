# Dataplicity Tutorial 1: Getting Access, Online Interface, and Unix Tools

We use Dataplicity to remotely manage Raspberry Pi's and access to flight hardware such as PyCubed. First, ask Langston, Moritz, or Flynn for access to Dataplicity.

https://www.dataplicity.com

Head over to the `devices` page:

<p align="center">
  <img src="../assets/dataplicity/devices.png" width="900"><br>
  <br><br>
</p>

Select the `Sequoia` Raspberry Pi:

<p align="center">
  <img src="../assets/dataplicity/pycubed_mnt.png" width="900"><br>
  <br><br>
</p>

The PyCubed drive is mounted at `/media/PYCUBED`. In the web view here, there are a number of software tools available to you, such as the ability to reboot, in the right column. All of the unix tools installed on the Raspberry Pi are somewhat accessble to you--for example, you can use the `nano` text editor to edit files but you can't use the `scp` command to copy files from your computer to the Raspberry Pi in this interface.

## Editing files on the PyCubed drive

Let's edit a file on the PyCubed drive with `nano`!
```
nano main.py
```

<p align="center">
  <img src="../assets/dataplicity/nano_main.png" width="900"><br>
  <br><br>
</p>

`Enter` to edit the file. Once you make your edits, type `ctrl-o` to "write" the file. Then, do `ctrl-x` to exit. 

<p align="center">
  <img src="../assets/dataplicity/nano_main_save.png" width="900"><br>
  <br><br>
</p>

## Copying files to the PyCubed drive

Make a file and put some stuff in it.

<p align="center">
  <img src="../assets/dataplicity/tmp_test.png" width="900"><br>
  <br><br>
</p>

This time, let's save the file with `ctrl-s` (same as `ctrl-o` but it does not prompt for a file name).  Then `ctrl-x` to exit.

<p align="center">
  <img src="../assets/dataplicity/nano_save.png" width="900"><br>
  <br><br>
</p>

Make sure you saved the file with the `cat` command (`cat` is technically for concatenating (combining) files, but works fine for printing them in the terminal!)

<p align="center">
  <img src="../assets/dataplicity/cat.png" width="900"><br>
  <br><br>
</p>

Now, we will move the file to the PyCubed with the `cp` ("copy") command. Syntax for this is 

```
$ cp SOURCE DESTINATION
```

For you, this would be:

```
$ cp tmp/test /media/PYCUBED/
```

<p align="center">
  <img src="../assets/dataplicity/copied.png" width="900"><br>
  <br><br>
</p>

Print the file in your terminal with:

```
$ cat /media/PYCUBED/test
```

And then delete the file with:

```
$ rm /media/PYCUBED/test
```

Despite all of these cool things, _we don't recommend using the web interface_ because it crashes fairly often.

---------------------------------------

## Next Steps

Checkout the [next tutorial](tutorial_2.md) to learn how to access Dataplicity enabled Raspbery Pi's with Porthole in your desired terminal—-on your computer, _not_ in a browser!