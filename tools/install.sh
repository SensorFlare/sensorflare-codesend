#!/bin/bash
INSTALL_LOCATION="/opt"
PIKA_VERSION="0.9.8"

[ "$(whoami)" != "root" ] && exec sudo -- "$0" "$@"


echo "Installing python-pip git-core python-setuptools git-core"
apt-get install python-pip git-core  python-setuptools git-core

echo "Installing pip"
easy_install pip

echo "pika version $PIKA_VERSION"
pip install pika==$PIKA_VERSION

echo "Copying files to $INSTALL_LOCATION"
cp -r ../../sensorflare-codesend $INSTALL_LOCATION

echo "Adding startup script..."
cp -r etc/init.d/sensorflare-codesend /etc/init.d/
chmod a+x /etc/init.d/sensorflare-codesend
update-rc.d sensorflare-codesend defaults

echo "Type the username provided when you activated codesend from the Sensorflare website, followed by [ENTER]:"
read username
echo "Type the password entered when you activated codesend from the Sensorflare website, followed by [ENTER]:"
read -s mypassword

echo "username = '$username'" > $INSTALL_LOCATION/sensorflare-codesend/properties.py
echo "password = '$mypassword'" >> $INSTALL_LOCATION/sensorflare-codesend/properties.py

echo "Starting daemon"
service sensorflare-codesend start

