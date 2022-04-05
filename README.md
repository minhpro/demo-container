**Build jar**

`./mvnw clean package`

**Build image**

`docker build -t demo-container .`

**Run container**

`docker run --name demo-container -p 8080:8080 -d demo-container`

**Test API**

`curl localhost:8080/greet`
