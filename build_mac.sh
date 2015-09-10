#!/bin/bash

echo "------------------------------------"
echo "Cleaning workspace"
echo "------------------------------------"

# TODO JT 2014-02-13 - Should clean the workspace

# rm -rf venv
rm -rf dist
rm -rf build
rm -rf *.app
rm -rf /opt/git/kivy-sdk-packager/osx/src.app
rm -rf *.dmg
rm -rf venv
rm -f src/VERSION.py
rm -f version.properties 
find . -name "*.pyc" -exec rm -rf {} \;

echo "------------------------------------"
echo "Setting up Enviroment"
echo "------------------------------------"

source setup_development_macosx.sh

echo "------------------------------------"
echo "Extracting Git Revision Number"
echo "------------------------------------"

SEMANTIC=`cat symantic.version`

function trim() { echo $1; }

if [ -z $GIT_HOME ]; then
  if [ -f "/usr/local/bin/git" ]; then
    export GIT_HOME=/usr/local/bin/git
  elif [ -f "/usr/bin/git" ]; then
    export GIT_HOME=/usr/bin/git
  elif [ -f "/bin/git" ]; then
    export GIT_HOME=/bin/git
  else
    echo "Could not find git."
    exit 1
  fi
fi

export GIT_REV_COUNT_RAW=`$GIT_HOME log --pretty=oneline | wc -l`
export GIT_REV_COUNT=`trim $GIT_REV_COUNT_RAW`
export GIT_REV=`$GIT_HOME rev-parse HEAD`

VERSION=$SEMANTIC.$TAG$GIT_REV_COUNT
echo "Version: $VERSION"
echo "# THIS IS A GENERATED FILE " > version.properties
echo "version='$VERSION'" >> version.properties
echo "revision='$GIT_REV'" >> version.properties
echo "Git Revision Number is $GIT_REV_COUNT"
cp version.properties src/UIVERSION.py

echo "------------------------------------"
echo "Building Package"
echo "------------------------------------"

apppath=`pwd`/src

pushd /opt/git/kivy-sdk-packager/osx
./package-app.sh $apppath
if [ $? != 0 ]; then
    echo "FAILURE: Building app"
    exit 232
fi
popd

echo "------------------------------------"
echo "Moving Application"
echo "------------------------------------"

cp -R /opt/git/kivy-sdk-packager/osx/src.app peachyprinter.app

if [ $? != 0 ]; then
    echo "FAILURE: Copying app"
    exit 233
fi

cp src/resources/peachy.icns peachyprinter.app/Contents/Resources/appIcon.icns

echo "------------------------------------"
echo "Building dmg"
echo "------------------------------------"

dmg_name=PeachyPrinter-$VERSION.dmg
vol_name=PeachyPrinter
background_image=src/resources/images/mac_installer.png
volicon=src/resources/peachy.icns
backgound_width=700
background_height=400
app=peachyprinter.app
app_pos_x=250
app_pos_y=200
sym_pos_x=600
sym_pos_y=200
icon_size=64

/opt/git/create-dmg/create-dmg --volicon $volicon --volname $vol_name --background $background_image --window-pos 200 120 --window-size $backgound_width $background_height --icon-size $icon_size --icon $app $app_pos_x $app_pos_y --app-drop-link $sym_pos_x $sym_pos_y --hide-extension $app $dmg_name peachyprinter.app


