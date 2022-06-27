### Rolling update

0. Check that pods are running

`kubectl get pods | grep gateway`

1. Call heavy request

```sh
curl -i -X GET \
  --url http://192.168.59.100:31180/heavy-greet \
  --header 'Host: example.com'
```

2. Perform rolling update

Open a new tab (new ssh session)

`kubectl set image deployment demo-kong-gateway kong=demo-kong-gateway:v2`

3. Check that there is pod that are being terminated

`kubectl get pods | grep gateway`

4. Call a normal request

Open a new tab (new ssh sesion)

```sh
curl -i -X GET \
  --url http://192.168.59.100:31180/greet \
  --header 'Host: example.com'
```

Check that response is ok

5. Wait 2 minutes, check that step 1 response is ok