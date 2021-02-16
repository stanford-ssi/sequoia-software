ls -l /dev/disk/by-uuid/
PYCUBED_UUID=$(sudo blkid -s UUID -o value /dev/sda1)
sudo mkdir /mnt/pycubed
sudo chown -R pi:pi /mnt/pycubed
cat <<EOF >> /etc/fstab
UUID=${PYCUBED_UUID} /mnt/pycubed vfat auto,nofail,noatime,users,rw,uid=pi,gid=pi 0 0
EOF
