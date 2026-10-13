package com.marlabs.supportdesk.controller;

import com.marlabs.supportdesk.model.AnswerRequest;
import com.marlabs.supportdesk.model.AnswerResponse;
import com.marlabs.supportdesk.service.PolicyService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class SupportDeskController {

    private final PolicyService policyService;

    public SupportDeskController(PolicyService policyService) {
        this.policyService = policyService;
    }

    @PostMapping("/answer")
    public ResponseEntity<AnswerResponse> answer(
            @RequestHeader("X-Caller-Id") String callerId,
            @Valid @RequestBody AnswerRequest request) {

        if (callerId == null || callerId.isBlank()) {
            return ResponseEntity.badRequest().build();
        }

        try {
            policyService.validateCaller(callerId);
            AnswerResponse response = policyService.answer(request, callerId);
            return ResponseEntity.ok(response);
        } catch (IllegalArgumentException ex) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).build();
        }
    }
}
