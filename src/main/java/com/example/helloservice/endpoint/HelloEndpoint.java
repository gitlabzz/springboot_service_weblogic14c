package com.example.helloservice.endpoint;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.ws.server.endpoint.annotation.Endpoint;
import org.springframework.ws.server.endpoint.annotation.PayloadRoot;
import org.springframework.ws.server.endpoint.annotation.RequestPayload;
import org.springframework.ws.server.endpoint.annotation.ResponsePayload;
import com.example.helloservice.schema.HelloRequest;
import com.example.helloservice.schema.HelloResponse;
import weblogic.jws.Policies;
import weblogic.jws.Policy;

@Endpoint
@Policies({@Policy(uri = "policy:clientcertreq.xml")})
public class HelloEndpoint {

    private static final String NS = "http://example.com/hello";

    @Value("${greeting.message:Hello default}")
    private String greeting;

    @PayloadRoot(namespace = NS, localPart = "HelloRequest")
    @ResponsePayload
    public HelloResponse hello(@RequestPayload HelloRequest request) {
        HelloResponse resp = new HelloResponse();
        resp.setGreeting(String.format("%s, %s!", greeting, request.getName()));
        return resp;
    }
}
