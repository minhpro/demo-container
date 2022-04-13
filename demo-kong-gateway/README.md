## Prepare database

**Install postgresql**

https://www.digitalocean.com/community/tutorials/how-to-install-postgresql-on-ubuntu-20-04-quickstart

```shell
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql.service
```

```shell
sudo -i -u postgres
psql
```

OR

`sudo -u postgres psql`

**Create new role**

`sudo -u postgres createuser --interactive`

```
Output
Enter name of role to add: kong
Shall the new role be a superuser? (y/n) y
```

`alter role kong with encrypted password 'kong';`

Create database

`sudo -u postgres createdb kong`

Grant all privileges of a database to the user

```
GRANT CONNECT ON DATABASE kong TO kong;

GRANT USAGE ON SCHEMA public TO kong;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO kong;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO kong;
```

If there is any problems, alter user `kong` to be `superuser`

`ALTER USER kong WITH SUPERUSER;`

**Add linux user**

`sudo adduser kong`


Connect db

`sudo -u kong bash -c 'psql -d kong'`

**Run kong migration**

Run migration job on k8s

`kubectl apply -f k8s/kong-migration-job.yml`

## Run kong-api-gateway on k8s

Create k8s deployment

`kubectl apply -f k8s/demo-kong-gateway-deployment.yml`

Create k8s service

`kubectl apply -f k8s/demo-kong-gateway-service.yml`

export service to external

`minikube service --url demo-kong-gateway`

The above command output is this service external URL, called <KONG-ADMIN-URL>, <KONG-PROXY-URL>

## Add route and service to Kong

Create a service

```shell
curl -i -X POST \
  --url http://<KONG-ADMIN-URL>/services/ \
  --data 'name=demo-container-service' \
  --data 'url=http://demo-container-service'
```

```shell
curl -i -X POST \
--url http://192.168.59.100:31181/services/ \
--data 'name=demo-container-service' \
--data 'url=http://demo-container-service'
```

Add route to service

```shell
curl -i -X POST \
  --url http://<KONG-ADMIN-URL>/services/demo-container-service/routes \
  --data 'hosts[]=example.com'
```

```shell
curl -i -X POST \
  --url http://192.168.59.100:31181/services/demo-container-service/routes \
  --data 'hosts[]=example.com'
```

Forward request

```shell
curl -i -X GET \
  --url http://<KONG-PROXY-URL>/ \
  --header 'Host: example.com'
```

```shell
curl -i -X GET \
  --url http://192.168.59.100:31180/ \
  --header 'Host: example.com'
```
