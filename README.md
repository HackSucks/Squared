# Squared²
```
 ____                                 _  //\  ___         
/ ___|  __ _ _   _  __ _ _ __ ___  __| ||/_\||_  )        
\___ \ / _` | | | |/ _` | '__/ _ \/ _` | /_\  / /   _____ 
 ___) | (_| | |_| | (_| | | |  __/ (_| |/ _ \/___| |_____|
|____/ \__, |\__,_|\__,_|_|  \___|\__,_/_/ \_\            
          |_|                                             
  ____      _     _           __                 _             _               
 / ___|   _| |__ (_) ___     / _| ___  _ __     / \   _ __ ___| |__            
| |  | | | | '_ \| |/ __|   | |_ / _ \| '__|   / _ \ | '__/ __| '_ \     _____ 
| |__| |_| | |_) | | (__ _  |  _| (_) | |     / ___ \| | | (__| | | |_  |_____|
 \____\__,_|_.__/|_|\___( ) |_|  \___/|_|    /_/   \_\_|  \___|_| |_(_)        
                        |/                                                     
    _             _       ___ ____   ___  
   / \   _ __ ___| |__   |_ _/ ___| / _ \ 
  / _ \ | '__/ __| '_ \   | |\___ \| | | |
 / ___ \| | | (__| | | |  | | ___) | |_| |
/_/   \_\_|  \___|_| |_| |___|____/ \___/ 
                                          
  ____          _                  _              
 / ___|   _ ___| |_ ___  _ __ ___ (_)_______ _ __ 
| |  | | | / __| __/ _ \| '_ ` _ \| |_  / _ \ '__|
| |__| |_| \__ \ || (_) | | | | | | |/ /  __/ |   
 \____\__,_|___/\__\___/|_| |_| |_|_/___\___|_|
```
**Squared²** is a GUI tool for customizing and rebuilding Arch-based ISOs, similar to [Cubic](https://launchpad.net/cubic) on Ubuntu — but built specifically for Arch Linux. The name comes from being the "squared" version of Cubic (Cubic = ^3, Squared = ^2 😉).
## Features - Extract, modify, and rebuild Arch-based ISO root filesystems.
- GUI interface for easy chroot management.
- Includes automatic fixroot.sh handling for resolving duplicate folder issues after extraction.
  - Resquash and rebuild with minimal hassle.
## Requirements 
- Python 3
- rsync
- squashfs-tools
- arch-install-scripts
- syslinux
## Usage: Clone this repo:
```
git clone https://github.com/HackSucks/Squared.git
```
Then, create a workdir folder where the files are located (i recommend a seperate folder)
then
Launch the GUI:
python -m init
or python init.py
or python3 -m init
or python3 init.py
Any one of these will start Squared².
Then once you are done with the chroot, press the unchroot button. if you get an error about pty not being found or similar, it is an issue with mounting and chrooting too many times, restart the PC and try again. once done with chrooting snd unchroot hsd been pressed, run sudo ./fixroot.sh from the main folder with all the scripts, and once its done, back in the GUI, select the OG Arch ISO, select the new airootfs.sfs, save it with <name>.iso, and repack it. And your ISO is ready!
# Squared², because Arch users deserve a nice way to make their own ISO files!





