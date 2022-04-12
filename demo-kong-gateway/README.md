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

Replace listen_address with your address (e,g, Vboxnet1, e,g 192.168.59.1)

```yaml
- name: KONG_PROXY_LISTEN
    value: '192.168.59.1:8000, 192.168.59.1:8443 ssl'
    # value: '0.0.0.0:8000, 127.0.0.1:8443 ssl'
- name: KONG_ADMIN_LISTEN
    value: '192.168.59.1:8001, 192.168.59.1:8444 ssl'
    # value: '0.0.0.0:8001, 127.0.0.1:8444 ssl'
```

Create k8s deployment

`kubectl apply -f k8s/demo-kong-gateway-deployment.yml`

Create k8s service

`kubectl apply -f k8s/demo-kong-gateway-service.yml`

export service to external

`minikube service --url demo-kong-gateway`
