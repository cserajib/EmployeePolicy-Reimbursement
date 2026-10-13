package com.marlabs.supportdesk;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.marlabs.supportdesk.controller.SupportDeskController;
import com.marlabs.supportdesk.model.AnswerRequest;
import com.marlabs.supportdesk.model.AnswerResponse;
import com.marlabs.supportdesk.model.Citation;
import com.marlabs.supportdesk.service.PolicyService;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(SupportDeskController.class)
class SupportdeskControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private PolicyService policyService;

    @BeforeEach
    void setUp() {
        doNothing().when(policyService).validateCaller("atlas-employee-01");
        when(policyService.answer(any(AnswerRequest.class), eq("atlas-employee-01")))
                .thenReturn(new AnswerResponse("ANSWERED", "INR 25000", List.of(new Citation("policy-1", "..."))));
    }

    @Test
    void answerRequiresCallerHeader() throws Exception {
        mockMvc.perform(post("/api/answer")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"question\":\"What is my limit?\",\"as_of\":\"2026-09-21\"}"))
                .andExpect(status().isBadRequest());
    }

    @Test
    void answerAcceptsKnownCaller() throws Exception {
        mockMvc.perform(post("/api/answer")
                        .header("X-Caller-Id", "atlas-employee-01")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"question\":\"What is my annual certification reimbursement limit?\",\"as_of\":\"2026-09-21\"}"))
                .andExpect(status().isOk());
    }
}
