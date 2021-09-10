# StreamFlash
Flash your screen when a message arrives on your Twitch channel

To make this application work, you will need to install Python3 which you will find at this address: https://www.python.org/downloads/

Then you will have to install PyQt5 via the command prompt:
 - Download and unzip this project,
 - Use the keyboard shortcut WIN + R,
 - Write `cmd` then validate,
 - Write `cd` followed by a space, then drag the `StreamFlash` folder into the command prompt and validate,
 - Finally copy the following command (right click on Windows to paste) and validate: `python -m pip install -r requirements.txt`.

Now enter your personal information in the `config.json` file:
 - screen: Default screen number to operate on,
 - username: The name of your Twitch channel,
 - oauth: https://twitchapps.com/tmi/.

Now that everything is installed, you can double-click on the `main.pyw` file, which will launch the application in your system tray.

__NOTE:__ The available options are to be found by right clicking on the application icon.
