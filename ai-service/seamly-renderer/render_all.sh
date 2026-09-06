#!/bin/bash
# Пакетный рендер пула изделий Seamly2D (headless, Xvfb) с автоснятием
# модальных информационных диалогов (Enter) и классификацией результата:
#   OK    — PNG выбран, rc=0
#   EMPTY — "empty scene" (в шаблоне изначально нет деталей / pieces)
#   FAIL  — rc!=0 или нет PNG (авария/зависание)
# Использование: bash render_all.sh <пул_dir> [out_root]
set -u
export HOME=/tmp DISPLAY=:99
Xvfb :99 -screen 0 1280x1024x24 >/tmp/xvfb.log 2>&1 &
sleep 3
SEAMLY="${SEAMLY_BIN:-/opt/seamly/squashfs-root/usr/bin/seamly2d}"
pool="${1:-/pool}"
out_root="${2:-/out}/pool_render"
rm -rf "$out_root"; mkdir -p "$out_root"
fail=0; empty=0; ok=0; total=0
for val in "$pool"/*.val; do
    base=$(basename "$val" .val)
    vit="$pool/${base}.vit"
    [ -f "$vit" ] || vit="$val"
    item="$out_root/$base"
    mkdir -p "$item"
    total=$((total+1))
    rm -f "$pool"/.*.locked
    timeout 90 $SEAMLY "$val" -m "$vit" -b "$base" -d "$item" -f 3 --exportOnlyDetails >"$item/log.txt" 2>&1 &
    pid=$!
    # снимаем информационные диалоги Enter-ом каждые ~0.4 c (не дольше 60 c)
    for i in $(seq 1 150); do
        DISPLAY=:99 xdotool key Return 2>/dev/null
        sleep 0.4
        kill -0 $pid 2>/dev/null || break
    done
    wait $pid; rc=$?
    rm -f "$pool"/.*.locked
    if grep -q "You can't export empty scene" "$item/log.txt" 2>/dev/null; then
        echo "EMPTY $base rc=$rc"
        empty=$((empty+1))
    elif [ -z "$(ls -A "$item" 2>/dev/null | grep -i png)" ]; then
        echo "FAIL  $base rc=$rc"
        fail=$((fail+1))
    else
        echo "OK    $base rc=$rc"
        ok=$((ok+1))
    fi
done
echo "TOTAL=$total OK=$ok EMPTY=$empty FAIL=$fail"