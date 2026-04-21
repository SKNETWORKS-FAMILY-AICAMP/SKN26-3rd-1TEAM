FROM mysql:9.3

COPY database/my.cnf /etc/mysql/conf.d/custom.cnf

# timezone 데이터 설치
RUN microdnf install -y tzdata && microdnf clean all