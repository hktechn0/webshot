#!/bin/bash

############################################
##
## webshot.cgi
## - Version 1.27
##
## Webpage Capture Script Wrapper for CGI
## Work with firefox + wmctrl
##  
## Created by techno @ Hirotaka Kawata
## - http://www.techno-st.net/wiki/
##
###########################################

TIME_S=`date '+%s.%N'`
echo -e "Content-type: text/html\n"

#################### config ####################

# Site URL
SITE="http://hogehoge/"
# Form URL
FORM="http://hogehoge/"

# log file
LOGFILE="hogehoge/logs/webshot_log"
# lock file
LOCKFILE="hogehoge/lock/lockfile"
# count file
CNT_LOG="./cnt_log"

# image output dir and file
OUTDIR="tmp/screen"
IMGDIR="img/webshot"

# escape and decode script
ESC_SCR="escape.sed"
DEC_SCR="decode.sed"

# Header
HEADER="<html>"
HEADER+="<head><title>webshot</title></head>"
HEADER+="<body>"

# Footer
FOOTER="<hr>"
FOOTER+="<a href=\"${SITE}\">HOME</a>"
FOOTER+="</body>"
FOOTER+="</html>"

##################################################

function log_output()
{
    NOWDATE=`date "+%D %H:%M:%S.%N"`
    echo "[${NOWDATE}] $*" >> $LOGFILE
}

# log
log_output "$REMOTE_ADDR" "GET" "$QUERY_STRING"

# Header
echo "$HEADER"

# URL Escape
Q_STR=`echo "$QUERY_STRING" | sed -f $ESC_SCR`

# URL and SIZE parameter set
if [ -z "`echo \"$Q_STR\" | grep -e \"^url=.*&s=[0-3]$\"`" ]
then
    # no size param
    URL=`echo "$Q_STR" | sed -e "s/^url=\(.*\)$\|^.*$/\1/"`
    SIZE="4"
else
    # with size param
    URL=`echo "$Q_STR" | sed -e "s/^url=\(.*\)&s=[0-3]$\|^.*$/\1/"`
    SIZE=`echo "$Q_STR" | sed -e "s/^url=.*&s=\([0-3]\)$\|^.*$/\1/"`
fi

# URL Decode
URL=`echo "$URL" | sed -f $DEC_SCR`

# protocol check
HTTP_CHK=`echo "$URL" | grep -E '^http[s]?://.*'`
if [ -z "$HTTP_CHK" ]
then
    URL=`echo "http://${URL}"`
fi

# slash check
SLASH_CHK=`echo "$URL" | grep -E '^http[s]?://.+/.*'`
if [ -z "$SLASH_CHK" ]
then
    URL=`echo "${URL}/"`
fi

# URL check
URL=`echo "$URL" | grep -E "^https?://[A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]\.[A-Za-z]+/.*"`
if [ -z "$URL" ]
then
	# log
    log_output "$REMOTE_ADDR" "ERR" "Illegal_URL" "$Q_STR"
    
    echo "<h2>Error!!</h2>"
    echo "<h3>usage: webshot.cgi?url='URL'</h3>"
    echo "<p>QUERY_STRING -> ${QUERY_STRING}</p>"
    echo "$FOOTER"
    exit
fi

# hostname (for future...
URL_HOSTNAME=`echo "$URL" | sed -e "s/^https\?:\/\/\([A-Za-z0-9][A-Za-z0-9.-]*[A-Za-z0-9]\.[A-Za-z]\+\)\/.*\|^.*$/\1/"`

# Refferer check
if [ -n "$HTTP_REFERER" -a "$URL" != "$HTTP_REFERER" ]
then
    REF_TMP=`echo "${HTTP_REFERER}" | grep -e "^${FORM}*"`
    
    if [ -z "$REF_TMP" ]
    then
	# log
	log_output "$REMOTE_ADDR" "ERR" "Illegal_Referer" "$HTTP_REFERER"
	
	echo "<h2>Error!!</h2>"
	echo "<h3>Sorry.</h3>"
	echo "<p>${HTTP_REFERER}<br>$URL</p>"
	echo "$FOOTER"
	exit
    fi
fi

# lock
if [ -e "$LOCKFILE" ]
then
    # log
    log_output "$REMOTE_ADDR" "ERR" "Lock!" `echo "$LOCKFILE"`
    
    # Error out	
    echo "<h2>Error!!</h2>"
    echo "<h3>After a while, please retry it... </h3>"
    echo "<p><a href=\"${SITE}webshot.cgi?${Q_STR}\">Retry</a></p>"
    echo "$FOOTER"
    exit
else
    date "+%D-%H:%M:%S" > "$LOCKFILE"
fi

# SIZE check
if [ "$SIZE" -eq 1 ]
then
    SIZES="640x480"
elif [ "$SIZE" -eq 2 ]
then
    SIZES="800x600"
elif [ "$SIZE" -eq 3 ]
then
    SIZES="1024x768"
elif [ "$SIZE" -eq 0 ]
then
    SIZES="MAX (display: 1280x1024)"
else
    SIZE=2
    SIZES="default [800x600]"
fi

# output
echo "<p>REMOTE_ADDR -> ${REMOTE_ADDR}<br>"
# echo "HTTP_USER_AGENT -> ${HTTP_USER_AGENT}<br>"
echo "QUERY_STRING -> ${Q_STR}</p>"

echo "<p>"
echo "URL -> ${URL}<br>"
echo "SIZE -> ${SIZES}<br>"

# log
log_output "$REMOTE_ADDR" "SHOT" "$URL" "$SIZE"

# shot!
bash webshot.sh "$URL" "$SIZE" 2> /dev/null
EXIT_STAT=$?
echo "</p>"

# exit status
if [ $EXIT_STAT -eq 1 -o $EXIT_STAT -eq 3 ]
then
    # error log
    log_output "$REMOTE_ADDR" "ERR" "Resize_Error" "$EXIT_STAT" "$URL"
    
    echo "<h2>Error!!</h2>"	
    echo "<h3>Resize Error!!</h3>"
    echo "<p><a href=\"${SITE}webshot.cgi?${Q_STR}\">Retry</a></p>"
    echo "$FOOTER"
    
    rm "$LOCKFILE"
    exit
elif [ $EXIT_STAT -eq 2 ]
then
    # error log
    log_output "$REMOTE_ADDR" "ERR" "Firefox_Error" "$URL"
    
    echo "<h2>Error!!</h2>"	
    echo "<h3>Firefox terminated abnormally.</h3>"
elif [ $EXIT_STAT -eq 4 ]
then
    # error log
    log_output "$REMOTE_ADDR" "ERR" "Firefox_Already_Run" "$URL"
    
    echo "<h2>Error!!</h2>"	
    echo "<h3>Sorry. Please try again.</h3>"
    echo "<p><a href=\"${SITE}webshot.cgi?${Q_STR}\">Retry</a></p>"
    echo "$FOOTER"
    
    rm "$LOCKFILE"
    exit
fi

# read count
if [ -e $CNT_LOG ]
then
    CNT=`head -n 1 $CNT_LOG`
else
    CNT="1"
fi

# count++
echo "$[$CNT + 1]" > $CNT_LOG
CNT=`printf "%03d" $CNT`

# log
log_output "$REMOTE_ADDR" "SAVE" "${IMGDIR}_$CNT.png" "$URL"

# copy file
cp ${OUTDIR}.png ${IMGDIR}_$CNT.png
cp ${OUTDIR}_thumb.png ${IMGDIR}-thumb_$CNT.png

echo "<p><u><b>Image</b></u><br>"
echo "Please click to expand.</p>"
echo "<p><a href=\"${IMGDIR}_${CNT}.png\"><img src=\"${SITE}${IMGDIR}-thumb_${CNT}.png\" border=\"0\"></a></p>"
echo "<p>ImageURL -> <a href=\"${IMGDIR}_${CNT}.png\">${SITE}${IMGDIR}_${CNT}.png</a><br>"
echo "Thumbnail -> <a href=\"${IMGDIR}-thumb_${CNT}.png\">${SITE}${IMGDIR}-thumb_${CNT}.png</a></p>"

# time
echo "<p>Processing time: "
echo "`date '+%s.%N'` - $TIME_S" | bc | sed -e 's/^\([0-9]*\)\.\([0-9].\).*/\1.\2/g'
echo " sec</p>"

# footer
echo "$FOOTER"

# unlock
rm "$LOCKFILE"
