FROM minio/minio:RELEASE.2024-05-16T19-49-05Z
EXPOSE 9000
EXPOSE 9001
ENTRYPOINT ["minio", "server", "/data", "--console-address", ":9001"]
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:9000/minio/health/live || exit 1