ARG POSTGRES_VERSION=15
FROM postgres:${POSTGRES_VERSION}-alpine
ENV POSTGRES_USER=admin_user
ENV POSTGRES_PASSWORD=yourStrongPassword123!
ENV POSTGRES_DB=msa_main_db
COPY ./config/postgresql.conf /usr/share/postgresql/postgresql.conf.sample
COPY ./config/pg_hba.conf /usr/share/postgresql/pg_hba.conf.sample
COPY ./config/init.sql /docker-entrypoint-initdb.d/01-init-schemas.sql
EXPOSE 5432