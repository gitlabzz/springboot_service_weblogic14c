package com.example.helloservice.config;

import org.springframework.boot.web.servlet.ServletRegistrationBean;
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.core.io.ClassPathResource;
import org.springframework.ws.config.annotation.EnableWs;
import org.springframework.ws.transport.http.MessageDispatcherServlet;
import org.springframework.ws.wsdl.wsdl11.DefaultWsdl11Definition;
import org.springframework.xml.xsd.SimpleXsdSchema;
import org.springframework.xml.xsd.XsdSchema;

@EnableWs
@Configuration
public class WebServiceConfig {

    @Bean
    public ServletRegistrationBean<MessageDispatcherServlet> springWsServlet(ApplicationContext ctx) {
        MessageDispatcherServlet servlet = new MessageDispatcherServlet();
        servlet.setApplicationContext(ctx);
        servlet.setTransformWsdlLocations(true);

        ServletRegistrationBean<MessageDispatcherServlet> reg = new ServletRegistrationBean<>(servlet, "/services/*");
        reg.setName("spring-ws");   // unique in the whole web-app
        reg.setLoadOnStartup(1);    // initialise before MVC servlet
        return reg;
    }

    // ---- WSDL 1.1 -------------
    @Bean(name = "HelloService")
    public DefaultWsdl11Definition helloWsdl(XsdSchema schema) {
        DefaultWsdl11Definition def = new DefaultWsdl11Definition();
        def.setPortTypeName("HelloPort");
        def.setLocationUri("/services/HelloService");
        def.setTargetNamespace("http://example.com/hello");
        def.setSchema(schema);
        return def;
    }

    // ---- WSDL 1.2 -------------
    @Bean(name = "HelloService12")
    public DefaultWsdl11Definition helloWsdl12(XsdSchema schema) {
        DefaultWsdl11Definition def = new DefaultWsdl11Definition();
        def.setPortTypeName("HelloPort");
        def.setLocationUri("/services/HelloService12");
        def.setTargetNamespace("http://example.com/hello");
        def.setSchema(schema);
        return def;
    }

    @Bean
    public XsdSchema helloSchema() {
        return new SimpleXsdSchema(new ClassPathResource("xsd/hello.xsd"));
    }
}
