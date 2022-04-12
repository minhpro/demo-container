## Build and run containers

**Build jar**

`./mvnw clean package`

Build for java 8

Modify pom.xml

```properties
<properties>
    <maven.compiler.target>1.8</maven.compiler.target>
    <maven.compiler.source>1.8</maven.compiler.source>
</properties>
```

`./mvnw clean package`

**Build image**

`docker build -t demo-container .`

java8

`docker build -f Dockerfile-java8 -t demo-container .`

**Run container**

`docker run --name demo-container -p 8080:8080 -d demo-container`

**Test API**

`curl localhost:8080/greet`

## Deploy k8s minikube

**Start minikube cluster**

`minikube start --driver=virtualbox`

Check the virtualbox network IP

`ifconfig -a | grep "vbox"`

`ifconfig vboxnet1`

=> IP, e,g: 192.168.59.1

Create deployment and service

```shell
kubectl apply -f k8s/demo-container-deployment.yml
kubectl apply -f k8s/demo-container-service.yml
```

Expose service to external 

`minikube service --url demo-container-service`

