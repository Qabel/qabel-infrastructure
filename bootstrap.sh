#!/bin/bash -e

PY=3.5
VENV=_venv
APPS=applications

function clone_app {
	if [ ! -d $APPS/$1 ]; then
		git clone https://github.com/Qabel/qabel-$1.git $APPS/$1
	fi
}

which git python$PY pip$PY virtualenv >/dev/null

if [ ! -d $VENV ]; then
virtualenv -p python$PY $VENV
fi

echo ". $VENV/bin/activate" > activate.sh
echo "echo \"See 'inv --list' for available tasks.\"" >> activate.sh
chmod +x activate.sh

set +u
. $VENV/bin/activate
set -u

pip$PY install -qU wheel setuptools pip
pip$PY install -qUr requirements.txt

mkdir -p applications
clone_app block
clone_app accounting
clone_app drop
clone_app index

echo "Run '. ./activate.sh' to activate this environment."
