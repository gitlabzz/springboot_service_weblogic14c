# Hello Service for WebLogic 14c

This project demonstrates a minimal SOAP web service built with Spring Boot 2.7.18 and Spring Web Services. The service loads its greeting message from `application.properties` and exposes two endpoints supporting SOAP 1.1 and SOAP 1.2.

## Building

```bash
mvn package -DskipTests
```

If the Maven wrapper `mvnw` is available, you can run `./mvnw` instead of `mvn`.

The build produces `target/hello-service.war` which can be deployed to WebLogic 14c running on JDK 17.

### Deploying to WebLogic

1. Build the WAR without skipping tests if desired:
   ```bash
   mvn package
   ```
2. Copy `target/hello-service.war` to your WebLogic domain's `autodeploy` directory or use the Administration Console to deploy it.

### Running Tests

Run the unit tests with:

```bash
mvn test
```

## Endpoints

* **SOAP 1.1** – `/services/HelloService`
* **SOAP 1.2** – `/services/HelloService12`

WSDL is available by appending `?wsdl` to either endpoint.

## Example Request

```
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:hel="http://example.com/hello">
  <soapenv:Header/>
  <soapenv:Body>
    <hel:sayHello>
      <name>World</name>
    </hel:sayHello>
  </soapenv:Body>
</soapenv:Envelope>
```

The response contains the greeting configured in `application.properties`.
