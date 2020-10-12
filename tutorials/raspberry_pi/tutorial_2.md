# Raspberry Pi Tutorial 2: Automounting a Drive on a Raspberry Pi

ls -l /dev/disk/by-uuid/
This will give you an output that should list your drive :
￼
The line will usually refer to “/sda” and in this example it is “sda1”. My ID is “18A9-9943”. Note down yours.
You would need to repeat this step if you wanted to use a different device as the UUID would be different.
Step 3 – Create a Mount Point
A mount point is a directory that will point to the contents of your flash drive. Create a suitable folder :
sudo mkdir /media/usb
I’m using “usb” but you can give it whatever name you like. Keep it short as it saves typing later on. Now we need to make sure the Pi user owns this folder :
sudo chown -R pi:pi /media/usb
You will only need to do this step once.
Step 4 – Manually Mount The Drive
To manually mount the drive use the following command :
sudo mount /dev/sda1 /media/usb -o uid=pi,gid=pi
This will mount the drive so that the ordinary Pi user can write to it. Omitting the “-o uid=pi,gid=pi” would mean you could only write to it using “sudo”.
Now you can read, write and delete files using “/media/usb” as a destination or source without needing to use sudo.
Step 5 – Un-mounting The Drive
You don’t need to manually un-mount if you shutdown your Pi but if you need to remove the drive at any other time you should un-mount it first. Only the user that mounted the drive can un-mount it.
umount /media/usb
If you used the fstab file to auto-mount it you will need to use :
sudo umount /media/usb
If you are paying attention you will notice the command is “umount” NOT “unmount”!
Step 6 – Auto Mount
When you restart your Pi your mounts will be lost and you will need to repeat Step 4. If you want your USB drive to be mounted when the system starts you can edit the fstab file :
sudo nano /etc/fstab
Then add the following line at the end :
UUID=18A9-9943 /media/usb vfat auto,nofail,noatime,users,rw,uid=pi,gid=pi 0 0
The “nofail” option allows the boot process to proceed if the drive is not plugged in. The “noatime” option stops the file access time being updated every time a file is read from the USB stick. This helps improve performance.
My fstab file looks like this :
￼
Make sure you set the correct UUID. Use CTRL-X followed by Y to save and exit the nano editor.
Now reboot :
sudo reboot

https://www.raspberrypi-spy.co.uk/2014/05/how-to-mount-a-usb-flash-disk-on-the-raspberry-pi/