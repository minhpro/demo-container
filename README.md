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
