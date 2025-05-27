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

    private ServletRegistrationBean<MessageDispatcherServlet> createServletRegistration(
            ApplicationContext ctx, String path) {
        MessageDispatcherServlet servlet = new MessageDispatcherServlet();
        servlet.setApplicationContext(ctx);
        servlet.setTransformWsdlLocations(true);
        return new ServletRegistrationBean<>(servlet, path);
    }

    @Bean
    public ServletRegistrationBean<MessageDispatcherServlet> messageDispatcherServlet11(ApplicationContext ctx) {
        return createServletRegistration(ctx, "/services/HelloService/*");
    }

    @Bean
    public ServletRegistrationBean<MessageDispatcherServlet> messageDispatcherServlet12(ApplicationContext ctx) {
        return createServletRegistration(ctx, "/services/HelloService12/*");
    }

    @Bean(name = "HelloService")
    public DefaultWsdl11Definition helloWsdl(XsdSchema schema) {
        DefaultWsdl11Definition def = new DefaultWsdl11Definition();
        def.setPortTypeName("HelloPort");
        def.setLocationUri("/services/HelloService");
        def.setTargetNamespace("http://example.com/hello");
        def.setSchema(schema);
        return def;
    }

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
