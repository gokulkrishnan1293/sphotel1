FROM alpine:3.19
RUN apk add --no-cache postgresql16-client aws-cli gnupg
COPY backup.sh /backup.sh
COPY crontab /etc/crontabs/root
RUN chmod +x /backup.sh
CMD ["crond", "-f", "-l", "2"]
