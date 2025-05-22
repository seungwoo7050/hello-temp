ARG ELASTICSEARCH_VERSION=8.13.4
FROM docker.elastic.co/elasticsearch/elasticsearch:${ELASTICSEARCH_VERSION}
WORKDIR /usr/share/elasticsearch
RUN bin/elasticsearch-plugin install analysis-nori --batch
COPY config/elasticsearch.yml /usr/share/elasticsearch/config/elasticsearch.yml
VOLUME /usr/share/elasticsearch/data
VOLUME /usr/share/elasticsearch/logs
EXPOSE 9200 9300