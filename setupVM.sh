# This is the script for setting up the VM for telegram bot

# Install necessary packages
sudo apt-get update
sudo apt-get install tmux
sudo apt-get install git

# Clone the repository
git clone 'https://github.com/joshuawe/telegram-journal-bot'
cd telegram-journal-bot

# create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

