# solabot_rpi
A ros package for Raspberry Pi to implement __solabot_navigation__

## colabot
When implementing __colabot__, `master` serves as the front car.
For the rear car, please refer to branch `rear_car`.

# RPI 3B+ running ROS

## Install Ubuntu Mate 
credit: Yen-Chih Huang

1. Win10 不能看到 PI_ROOT 分割區，建議用 Linux 系統安裝。
2. 下載小組硬碟 solabot / Delta_SOLabot / RPI3B+ /
    - Ubuntu Mate SD.zip
    - PI_ROOT_ubuntu_sp.zip
    - PI_BOOT_ubuntu_sp.zip
3. 將 Ubuntu Mate SD.zip 解壓縮得到 Ubuntu Mate SD.img，參考 [^mate] 的方法將 img 燒入 SDCard，完成後可看到 PI_BOOT 與 PI_ROOT 分割區。
4. 將 PI_ROOT_ubuntu_sp.zip 解壓縮覆蓋至 PI_ROOT。
5. 將 PI_BOOT_ubuntu_sp.zip 解壓縮覆蓋至 PI_BOOT。
> 可用`sudo nautilus` 開啟權限
6. 執行 ```rpi-update``` 更新 firmware，執行 ```sudo apt update``` 與 ```sudo apt upgrade``` 更新軟體。若wifi無法開啟見下方說明。
7. 進 RPI 後，執行 ```sudo raspi-config``` 開啟 ssh、vnc、camera 等功能。 
8. 若開機後卡在彩虹橋，則編輯 PI_BOOT / config.txt 新增文字 ```boot_delay=1```。[^config]

## wifi not working

重啟動 NetworkManager 的 service 即可。

```bash
sudo service NetworkManager restart
```

## 開機不需登入，自動連網

修改 /etc/network/interfaces，刪除所有文字後，加入以下文字

```
auto wlan0
allow-hotplug wlan0
iface wlan0 inet dhcp
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
```

在 /etc/wpa_supplicant/wpa_supplicant.conf 加入以下文字

```
network={
ssid="YOUR_NETWORK_NAME"
psk="YOUR_NETWORK_PASSWORD"
proto=RSN
key_mgmt=WPA-PSK
pairwise=CCMP
auth_alg=OPEN
}
```
>find ssid: `iwgetid`
>(永齡：Solab_5G)
>
>完成後重開後不會有wifi icon，但可以正常上網不用緊張

## install ROS etc.
1. install ros
2. install packages
```
git clone https://github.com/mwu412/solabot_Setup.git
sudo sh packages_install.sh
```
3. create workspace
`cd src/` then clone the package:
`git clone https://github.com/solab-ntu/solabot_rpi.git`


## 連接 hokuyo 與 imu

### How to bind USB device under a static name

[reference](https://unix.stackexchange.com/questions/66901/how-to-bind-usb-device-under-a-static-name)

#### Check usb state
`lsusb`
plugin USB then `lsusb` again.
`ID <ATTRS{idVendor}>:<ATTRS{idProduct}>`
e.g `15d1:0000`

#### (Alternative)
#####  go to /dev and ls

##### plugin USB and ls again to see if ttyACMx or ttyUSBx has been added

##### get the info of the device: (replace x with the right number)

    udevadm info --name=/dev/ttyACMx --attribute-walk
    
this  will list the whole chain of devices 

we need to look from the top to find the first  
- ATTRS{idVendor}=="1234"
- ATTRS{idProduct}=="5678

can doule check with 
- ATTRS{product}=="Arduino Micro"

#### (/Alternative)

#### create a file 
    /etc/udev/rules.d/99-usb-serial.rules
>另一個可以成功的方法是，不新增檔案，而加在既有的`10*.rules`裡面
#### add the following to the file
    ACTION=="add", ATTRS{idVendor}=="1b4f", ATTRS{idProduct}=="9d0f", SYMLINK+="razor_imu"
    
#### load the new rule
    sudo udevadm trigger    
>有時候重開機才會生效
#### if multiple device with identical <ATTRS{idVendor}>:<ATTRS{idProduct}>
use the above alternative method to find KERNELS (location of the port), then:
```
KERNEL=="ttyACM*", KERNELS=="1-1.3:1.0", SYMLINK+="rpi_upper_right_socket"
KERNEL=="ttyACM*", KERNELS=="1-1.2:1.0", SYMLINK+="rpi_lower_right_socket"
```

### 改變權限
必須要改變權限rpi才抓得到usb裝置
```
sudo chmod 666 /dev/razor_imu
```
但此方法開機後又會失效

>若寫在`/etc/rc.local`裡可以每次開機以root執行 :
>```
>chmod 666 /dev/rpi_upper_right_socket
>chmod 666 /dev/rpi_lower_right_socket
>chmod 666 /dev/razor_imu
>```

不過有更好的方法，執行：
`sudo usermod -a -G dialout youruser`
>A permanent solution is to add your user to the dialout group, which will allow it to access serial devices.

## Serial Comunication
[link](https://pimylifeup.com/raspberry-pi-serial/?fbclid=IwAR3xkM_K-2MtXyhJVgPOMHSpy-PB4fkMvN2YDyHcvoCtiX87ZcAHzEiq5kQ)
> During "Setting up the Raspberry Pi for Serial Read and Write", instead of using te GUI we can do the following:
> 1. add `enable_uart=1` to the bottom of /boot/config.txt\
> 2. To manually change the settings, edit the kernel command line with  sudo nano /boot/cmdline.txt. Find the console entry that refers to the serial0 device, and remove it, including the baud rate setting. It will look something like  `console=serial0,115200`.

## Clone (backup) SD card
* clone: [link](https://beebom.com/how-clone-raspberry-pi-sd-card-windows-linux-macos/)
> both cloning and restoring will take a while (an hour or something...)

* change username (ref. [link](https://askubuntu.com/questions/34074/how-do-i-change-my-username))
    1. add a temporary sudo user: [link](https://www.digitalocean.com/community/tutorials/how-to-create-a-sudo-user-on-ubuntu-quickstart)
    2. reboot (this will kill all the processes) add login to the temp new user
    3. `sudo usermod -l newUsername oldUsername`
> this is will not rename the home folder (we should not) and gui login name (really strange). but the `whoami` and ssh username will change. this is what we need.
* after cloning remember to change IP in .bashrc

## Sync time (Chrony)(Not successful yet)
Follow [this](https://answers.ros.org/question/298821/tf-timeout-with-multiple-machines/). 

[ref](https://blogging.dragon.org.uk/using-chrony-on-ubuntu-18-04/) (not so usefull)

For the master: /etc/chrony/chrony.conf:
```
driftfile /var/lib/chrony/drift
local stratum 8
manual
allow 192.168.50
```

For clients: /etc/chrony/chrony.conf:
```
server 192.168.50.68 iburst
driftfile /var/lib/chrony/drift
logdir /var/log/chrony
log measurements statistics tracking
local stratum 10
allow 192.168.50.68
makestep 1 -1

```

* command line
reboot
then  
`sudo /etc/init.d/chrony start`
`sudo /etc/init.d/chrony stop`


* Accuracy 
Typical accuracy between two machines synchronised over the Internet is within a few milliseconds; on a LAN, accuracy is typically in tens of microseconds.

* makestep 0.1 10
`makestep 0.1 10`:
This would step system clock if the adjustment is larger than 0.1 seconds, but only in the first ten clock updates.
Normally, it’s recommended to allow the step only in the first few updates, but in some cases (e.g. a computer without an RTC or virtual machine which can be suspended and resumed with an incorrect time) it may be necessary to allow the step on any clock update. The example above would change to:
`makestep 1 -1`

### 參考
[^mate]:https://ubuntu-mate.org/raspberry-pi/
[^config]:https://raspberrypi.stackexchange.com/questions/19354/raspberry-pi-with-boots-up-with-rainbow-screen
