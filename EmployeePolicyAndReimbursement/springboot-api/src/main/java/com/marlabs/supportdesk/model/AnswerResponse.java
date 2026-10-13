package com.marlabs.supportdesk.model;

import java.util.List;

public class AnswerResponse {
    private String status;
    private String answer;
    private List<Citation> citations;

    public AnswerResponse() {
    }

    public AnswerResponse(String status, String answer, List<Citation> citations) {
        this.status = status;
        this.answer = answer;
        this.citations = citations;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getAnswer() {
        return answer;
    }

    public void setAnswer(String answer) {
        this.answer = answer;
    }

    public List<Citation> getCitations() {
        return citations;
    }

    public void setCitations(List<Citation> citations) {
        this.citations = citations;
    }
}
