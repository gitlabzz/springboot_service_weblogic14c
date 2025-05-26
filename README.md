# Spring Boot WebLogic 14c Example

This project contains a minimal Spring Boot application packaged as a WAR file for deployment to Oracle WebLogic 14c.

## Building

Use Maven to build the project:

```bash
mvn package
```

The output `demo-0.0.1-SNAPSHOT.war` can be deployed to WebLogic 14c.

## Endpoints

After deployment, access the sample endpoint at:

```
http://<weblogic-host>:7001/hello
```

It will return `Hello, WebLogic 14c!`.
