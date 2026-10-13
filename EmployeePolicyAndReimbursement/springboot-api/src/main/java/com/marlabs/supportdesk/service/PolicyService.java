package com.marlabs.supportdesk.service;

import com.marlabs.supportdesk.model.AnswerRequest;
import com.marlabs.supportdesk.model.AnswerResponse;
import com.marlabs.supportdesk.model.Citation;
import java.util.List;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class PolicyService {

    private final RestTemplate restTemplate;
    private final String pythonServiceUrl;

    public PolicyService(@Value("${supportdesk.python-service-url:http://localhost:8001}") String pythonServiceUrl) {
        this.restTemplate = new RestTemplate();
        this.pythonServiceUrl = pythonServiceUrl;
    }

    public AnswerResponse answer(AnswerRequest request, String callerId) {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.set("X-Caller-Id", callerId);

        HttpEntity<AnswerRequest> entity = new HttpEntity<>(request, headers);
        ResponseEntity<AnswerResponse> response = restTemplate.exchange(
                pythonServiceUrl + "/answer",
                HttpMethod.POST,
                entity,
                AnswerResponse.class
        );

        if (response.getBody() == null) {
            throw new IllegalStateException("Empty response from policy service");
        }

        return response.getBody();
    }

    public void validateCaller(String callerId) {
        List<String> known = List.of("atlas-employee-01", "atlas-contractor-01", "boreal-employee-01");
        if (!known.contains(callerId)) {
            throw new IllegalArgumentException("Unknown caller identity");
        }
    }
}
