FROM fluent/fluentd:v1.16-1
USER root
RUN fluent-gem install fluent-plugin-elasticsearch \
                     fluent-plugin-multi-format-parser \
                     fluent-plugin-rewrite-tag-filter \
                     && gem sources --clear-all

COPY fluent.conf /fluentd/etc/
COPY entrypoint.sh /bin/
RUN chmod +x /bin/entrypoint.sh

USER fluent
ENTRYPOINT ["/bin/entrypoint.sh"]
CMD ["fluentd"]