#!/bin/bash

############################################
##
## webshot.sh
## - Version 1.27
##
## Webpage Capture Script for bash
## Works with firefox + wmctrl
##  
## Produced by techno @ Hirotaka Kawata
## - http://www.techno-st.net/wiki/
##
###########################################

#################### config ####################

# resize delay
DELAY="5"
# capture delay
CAP_DELAY="3"
# firefox close delay
CLOSE_DELAY="1"

## Firefox MenuBar Height
MBAR="24"
## Firefox ScrollBar Size
SBAR="16"

# Firefox profile
PROFILE="webshot"
# Firefox Name
#FIREFOX="Mozilla Firefox"
FIREFOX="Iceweasel"
# Firefox Process Name
FIREFOXBIN="firefox-bin"
#FIREFOXBIN="firefox"

# thumbnail width
THUMB_W="160"
# image output dir and file
OUTDIR="tmp/screen"

# display
export DISPLAY=":0"
# homedir
export HOME="/home/hogehoge"
# lang
export LANG="ja_JP.UTF-8"

##################################################

function id_chk()
{
    echo "$XINF" | grep "${1}x${2}" | head -n 1 | sed -e 's/^[ ]*//' | cut -f 1 -d ' '
}

function resize()
{
    wmctrl -i -r "$WINID" -e 0,0,0,${1},${2}
}

function check_firefox()
{
    # Check process
    PROC=`ps ax`
    PROC=`echo $PROC | grep $FIREFOXBIN`
}

# init
URL="$1"
SIZE="$2"
EXIT_STAT="0"
FULL="0"

check_firefox
if [ -n "$PROC" ]
then
    echo "Firefox already running." >&2
    echo "Firefox killing now..." >&2
    killall $FIREFOXBIN
    echo "Please run this script again." >&2
    exit 4
fi

# start frfx and wait
firefox -P webshot "$URL" &
sleep $DELAY

# window list get & firefox startup check
WINFO=`wmctrl -l | grep "${FIREFOX}"`
if [ -z WINFO ]
then
    echo "Firefox start-up too slowly." >&2
    echo "Firefox killing now..." >&2
    killall $FIREFOXBIN
    echo "Please change start-up delay setting." >&2
    exit 4
fi

# window id, title get
WINID=`echo "$WINFO" | cut -f 1 -d ' '`
TITLE=`echo "$WINFO" | cut -c 15- | cut -f 2- -d ' ' | sed -e "s/ - ${FIREFOX}//g"`
echo "TITLE -> $TITLE"

# if size
if [ $SIZE -eq 1 ]
then
    X=640
    Y=480
elif [ $SIZE -eq 2 ]
then
    X=800
    Y=600
elif [ $SIZE -eq 3 ]
then
    X=1024
    Y=768
else
    FULL=1
    X=640
    Y=480
fi

# resize-after-resize
resize $X $[$Y + $MBAR]							# resize to y += menubar
XINF=`xwininfo -tree -id $WINID`
CID1=`id_chk $[$X - $SBAR] $[$Y - $SBAR]`		# scrollbar enalbe both
CID2=`id_chk ${X} $[$Y - $SBAR]`				# scrollbar enable y-axis
CID3=`id_chk $[$X - $SBAR] ${Y}`				# scrollbar enable x-axis
CID4=`id_chk ${X} ${Y}`							# no scrollbar
#CID5=`id_chk $[$X - $SBAR] $[$Y - $SBAR - 1]`	# scrollbar enable both (debug

echo "$URL 1:$CID1 2:$CID2 3:$CID3 4:$CID4 5:$CID5" > logs/debug

if [ -n "$CID1" ]
then
    WCHID=$CID1
    resize $[$X + $SBAR] $[$Y + $MBAR + $SBAR]
elif [ -n "$CID2" ]
then
    WCHID=$CID2
    resize ${X} $[$Y + $MBAR + $SBAR]
elif [ -n "$CID3" ]
then
    WCHID=$CID3
    resize $[$X + $SBAR] $[$Y + $MBAR]
elif [ -n "$CID4" ]
then
    WCHID=$CID4
else
    echo "Resize Error!!" >&2
fi

# fullscreen
if [ $FULL -eq 1 ]
then
    wmctrl -i -r $WINID -b add,fullscreen
fi

# error? or shot
if [ -z "$WCHID" ]
then
    EXIT_STAT="1"
else
    sleep $CAP_DELAY
    xwd -id $WCHID -out "${OUTDIR}.xwd"
    convert "${OUTDIR}.xwd" "${OUTDIR}.png"
    convert -resize $THUMB_W "${OUTDIR}.xwd" "${OUTDIR}_thumb.png"
fi

# firefox close
wmctrl -i -c $WINID
sleep $CLOSE_DELAY

# firefox terminated? or die
check_firefox
if [ -n "$PROC" ]
then
    killall $FIREFOXBIN
    echo "Firefox terminated abnormally." >&2
    EXIT_STAT=$[$EXIT_STAT + 2]
fi

# exit
exit $EXIT_STAT
