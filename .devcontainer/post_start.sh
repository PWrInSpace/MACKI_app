# install git
apt-get install -y git-all

# Copy VimbaX wheel
cp -r ../../VimbaX/ .

# Copy venv
cp -r ../../.venv/ .

# Run poetry shell
poetry shell