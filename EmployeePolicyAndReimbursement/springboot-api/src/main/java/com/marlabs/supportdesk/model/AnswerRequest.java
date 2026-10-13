package com.marlabs.supportdesk.model;

import com.fasterxml.jackson.annotation.JsonFormat;
import java.time.LocalDate;

public class AnswerRequest {
    private String question;

    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate as_of;

    private String tenant;
    private String role;

    public String getQuestion() {
        return question;
    }

    public void setQuestion(String question) {
        this.question = question;
    }

    public LocalDate getAs_of() {
        return as_of;
    }

    public void setAs_of(LocalDate as_of) {
        this.as_of = as_of;
    }

    public String getTenant() {
        return tenant;
    }

    public void setTenant(String tenant) {
        this.tenant = tenant;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
    }
}
