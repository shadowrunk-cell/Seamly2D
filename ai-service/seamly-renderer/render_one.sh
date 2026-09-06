#!/bin/bash
# Рендер одного изделия в заданный формат (headless, Xvfb) с автоснятием инфо-диалогов.
# Ожидает монтирование:  -v <job_dir>:/job     (содержит pattern.val + measures.vit)
#                        -v <out_dir>:/out
# Использование: render_one.sh <val> <vit> <basename> [format]
#   format:      (например, url-декодированный крайний? нет) числовой код Seamly2D:
#                svg=0 pdf=1 png=3 pdf-tiled=2 jpg=4 dxf2010=17 dxf-aama=19
set -u
export HOME=/tmp DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb.log 2>&1 &
sleep 2
SEAMLY="${SEAMLY_BIN:-/opt/seamly/squashfs-root/usr/bin/seamly2d}"
val="$1"; vit="$2"; base="$3"
fmt="${4:-3}"
case "$fmt" in
    png|3)          num=3; ext=png ;;
    svg|0)          num=0; ext=svg ;;
    pdf|1)          num=1; ext=pdf ;;
    pdf-tiled|2)    num=2; ext=pdf ;;
    jpg|jpeg|4)     num=4; ext=jpg ;;
    dxf|dxf2010|17) num=17; ext=dxf ;;
    dxf-aama|19)    num=19; ext=dxf ;;
    *) echo "UNKNOWN_FORMAT fmt=$fmt" >&2; exit 67 ;;
esac
out="/out/$base"
mkdir -p "$out"
timeout 90 $SEAMLY "$val" -m "$vit" -b "$base" -d "$out" -f $num --exportOnlyDetails >"$out/log.txt" 2>&1 &
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
if [ -z "$(ls -A "$out" 2>/dev/null | grep -i "\\.$ext")" ]; then
    echo "NO_FILE rc=$rc ext=$ext" >&2
    exit 66
fi
echo "OK rc=$rc fmt=$fmt"
exit $rc