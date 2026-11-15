FROM alpine:3.23
RUN apk add --no-cache openssh-server openssh-sftp-server bash coreutils findutils git rsync curl nano \
 && adduser -D -u 1026 -G users -h /home/slugs -s /bin/bash slugs \
 && printf 'slugs:%s\n' "$(head -c 48 /dev/urandom | base64)" | chpasswd \
 && mkdir -p /hostkeys /run/sshd /volume1/web/slugs \
 && rm -f /etc/ssh/ssh_host_* \
 && printf '\ncd /volume1/web/slugs\n' >> /etc/profile
COPY sshd_config /etc/ssh/sshd_config
COPY authorized_keys /etc/ssh/slugs_authorized_keys
COPY entrypoint.sh /entrypoint.sh
RUN chmod 644 /etc/ssh/slugs_authorized_keys && chmod 755 /entrypoint.sh
WORKDIR /volume1/web/slugs
EXPOSE 2222
ENTRYPOINT ["/entrypoint.sh"]
