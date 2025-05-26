# Hello Service for WebLogic 14c

This project demonstrates a minimal SOAP web service built with Spring Boot 3 and Apache CXF. The service loads its greeting message from `application.properties` and exposes two endpoints supporting SOAP 1.1 and SOAP 1.2.

## Building

```bash
mvn package -DskipTests
```

The build produces `target/hello-service.war` which can be deployed to WebLogic 14c running on JDK 17.

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



curl http://192.168.210.147:8001/hello-soap-weblogic14c-0.0.1-SNAPSHOT/ws/hello.wsdl