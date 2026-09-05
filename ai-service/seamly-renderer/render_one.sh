#!/bin/bash
# Рендер одного изделия в PNG (headless, Xvfb) с автоснятием инфо-диалогов.
# Ожидает монтирование:  -v <job_dir>:/job     (содержит pattern.val + measures.vit)
#                        -v <out_dir>:/out
# Использование: render_one.sh <val> <vit> <basename>
set -u
export HOME=/tmp DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb.log 2>&1 &
sleep 2
SEAMLY="${SEAMLY_BIN:-/opt/seamly/squashfs-root/usr/bin/seamly2d}"
val="$1"; vit="$2"; base="$3"
out="/out/$base"
mkdir -p "$out"
timeout 90 $SEAMLY "$val" -m "$vit" -b "$base" -d "$out" -f 3 --exportOnlyDetails >"$out/log.txt" 2>&1 &
pid=$!
for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do
    DISPLAY=:99 xdotool key Return 2>/dev/null
    sleep 0.4
    kill -0 $pid 2>/dev/null || break
done
wait $pid
rc=$?
echo "SEAMLY_RC=$rc" >>"$out/log.txt"
if grep -q "You can't export empty scene" "$out/log.txt" 2>/dev/null; then
    echo "EMPTY" >&2
    exit 65
fi
if [ -z "$(ls -A "$out" 2>/dev/null | grep -i png)" ]; then
    echo "NO_PNG rc=$rc" >&2
    exit 66
fi
echo "OK rc=$rc"
exit $rc