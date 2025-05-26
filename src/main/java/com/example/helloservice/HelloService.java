package com.example.helloservice;

import jakarta.jws.WebMethod;
import jakarta.jws.WebParam;
import jakarta.jws.WebService;

@WebService(targetNamespace = "http://example.com/hello", name = "HelloService")
public interface HelloService {

    @WebMethod
    String sayHello(@WebParam(name = "name") String name);
}
