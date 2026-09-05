# Финальный образ рендера Seamly2D (headless).
# Содержит Xvfb + xdotool (для автоснятия модальных инфо-диалогов) и
# распакованный Seamly2D AppImage, готовый к batch-рендеру лекал в PNG.
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        xvfb xdotool x11-utils x11-apps \
        libglib2.0-0 libgl1 libegl1 \
        libfontconfig1 libglu1-mesa libxcb1 libxkbcommon0 libx11-6 libsm6 \
        libice6 poppler-utils binutils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/seamly
COPY Seamly2D-x86_64.AppImage /opt/seamly/
RUN chmod +x Seamly2D-x86_64.AppImage \
    && ./Seamly2D-x86_64.AppImage --appimage-extract >/dev/null 2>&1 \
    && rm Seamly2D-x86_64.AppImage

COPY render_all.sh render_one.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/render_all.sh /usr/local/bin/render_one.sh

ENV SEAMLY_BIN=/opt/seamly/squashfs-root/usr/bin/seamly2d