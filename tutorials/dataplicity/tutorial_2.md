# Dataplicity Tutorial 2: Using Porthole from your preferred tutorial

Download the [Porthole application](https://www.dataplicity.com/apps/porthole/) from GitHub:

Here for MacOS:
https://github.com/wildfoundry/dataplicity-porthole-releases-osx 

Here for Windows:
https://github.com/wildfoundry/dataplicity-porthole-releases/

Install Porthole on your computer, open it and log in with your Dataplicity credentials. Then, open a terminal and type:

```
$ porthole
```

<p align="center">
  <img src="../assets/dataplicity/porthole.png" width="900"><br>
  <br><br>
</p>

There are a number of options, such as login and rebooting that are accessible from the command line. The `forwards` command is covered in [tutorial 3](tutorial_3.md).

<p align="center">
  <img src="../assets/dataplicity/reboot.png" width="900"><br>
  <br><br>
</p>

To connect a remote terminal on the raspberry pi, do:

```
$ porthole device:terminal DEVICE_ID
```
<p align="center">
  <img src="../assets/dataplicity/porthole_terminal.png" width="900"><br>
  <br><br>
</p>

In this Porthole interface, **you have all the options that were accessible from the web client** (and were covered in [tutorial 1](tutorial_1.md))


---------------------------------------

## Next Steps

Checkout the [next tutorial](tutorial_3.md) to learn how to forward ports from the Raspbery Pi to your computer with Porthole, and how to use `tmux` to run processes that will continue even if you disconnect your computer.