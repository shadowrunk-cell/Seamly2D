#!/bin/bash
# Запуск рендера с автоснятием модальных диалогов (Enter) для headless-прогона.
export HOME=/tmp DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb.log 2>&1 &
sleep 3
apt-get update >/dev/null 2>&1 && apt-get install -y -qq xdotool x11-utils >/dev/null 2>&1
val="$1"; vit="$2"; base="$3"; outdir="$4"
mkdir -p "$outdir"
timeout 90 /opt/seamly/squashfs-root/usr/bin/seamly2d "$val" -m "$vit" -b "$base" -d "$outdir" -f 3 --exportOnlyDetails >"$outdir/log.txt" 2>&1 &
pid=$!
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    DISPLAY=:99 xdotool key Return 2>/dev/null
    sleep 1
done
wait $pid
rc=$?
echo "SEAMLY_RC=$rc" >>"$outdir/log.txt"
echo "SEAMLY_RC=$rc"