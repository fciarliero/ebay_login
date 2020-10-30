************INSTALLATION***********
for windows: 
run every command in windows/steps_win.txt
in a terminal located in /windows/

for linux:
run every command in linux/steps_linux.txt
in a terminal located in /linux/

**********CONFIGURATION************
for windows:
setting up config file:
in /windows/config.file change the variables 
for "user" and "password" to the values of a valid ebay account 
in "api_key" set a valid API key for 2captcha
"proxies" is a list of comma separated proxies, every time
the script is executed it will choose a random proxy from this list. 
add as many as you want.

for linux: 
in /linux/config.file change the variables for 
"user" and "password" to the values of a valid ebay account 
"proxies" is a list of comma separated proxies, every time
the script is executed it will choose a random proxy from this list. 
add as many as you want.
"visible" set visible = 0 to hide the virtual display
chose this option if running headless.
every time the script is executed a random size for the virtual display
is set in order to defeat browser fingerprinting.

******************RUNNING******************
in a terminal run these commands
for windows: 
".\env\Scripts\activate"
"python3 main_win.py"

for linux:
"virtualenv env"
"source env/bin/activate"
"python3 main.py"