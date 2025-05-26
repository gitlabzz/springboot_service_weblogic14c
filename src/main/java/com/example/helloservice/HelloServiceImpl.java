package com.example.helloservice;

import jakarta.jws.WebService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
@WebService(endpointInterface = "com.example.helloservice.HelloService",
        serviceName = "HelloService",
        targetNamespace = "http://example.com/hello")
public class HelloServiceImpl implements HelloService {

    @Value("${hello.message:Hello}")
    private String message;

    @Override
    public String sayHello(String name) {
        return message + " " + name + "!";
    }
}
