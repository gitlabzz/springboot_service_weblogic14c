package com.example.helloservice;

import javax.xml.transform.Source;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import org.springframework.ws.test.server.MockWebServiceClient;
import org.springframework.xml.transform.StringSource;

import static org.springframework.ws.test.server.RequestCreators.withPayload;
import static org.springframework.ws.test.server.ResponseMatchers.payload;

@SpringBootTest
class HelloEndpointTest {

    @Autowired
    private ApplicationContext applicationContext;

    private MockWebServiceClient client;

    @BeforeEach
    void setup() {
        client = MockWebServiceClient.createClient(applicationContext);
    }

    @Test
    void helloEndpointReturnsConfiguredGreeting() throws Exception {
        Source requestPayload = new StringSource(
            "<HelloRequest xmlns=\"http://example.com/hello\"><name>Codex</name></HelloRequest>");
        Source expectedResponse = new StringSource(
            "<HelloResponse xmlns=\"http://example.com/hello\"><greeting>Hello from WebLogic 14c Spring Boot!, Codex!</greeting></HelloResponse>");

        client.sendRequest(withPayload(requestPayload))
              .andExpect(payload(expectedResponse));
    }
}
