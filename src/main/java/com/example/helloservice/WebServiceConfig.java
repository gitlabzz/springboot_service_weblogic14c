package com.example.helloservice;

import jakarta.xml.ws.Endpoint;
import jakarta.xml.ws.soap.SOAPBinding;
import org.apache.cxf.Bus;
import org.apache.cxf.jaxws.EndpointImpl;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class WebServiceConfig {

    @Autowired
    private Bus bus;

    @Autowired
    private HelloService helloService;

    @Bean
    public Endpoint helloServiceEndpoint() {
        EndpointImpl endpoint = new EndpointImpl(bus, helloService);
        endpoint.publish("/HelloService");
        return endpoint;
    }

    @Bean
    public Endpoint helloServiceSoap12Endpoint() {
        EndpointImpl endpoint = new EndpointImpl(bus, helloService, SOAPBinding.SOAP12HTTP_BINDING);
        endpoint.publish("/HelloService12");
        return endpoint;
    }
}
