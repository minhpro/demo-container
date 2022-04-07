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

**Add linux user**

`sudo adduser kong`


Connect db

`sudo -u kong bash -c 'psql -d kong'`
