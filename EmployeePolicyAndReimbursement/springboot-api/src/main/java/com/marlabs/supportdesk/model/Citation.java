package com.marlabs.supportdesk.model;

public class Citation {
    private String chunk_id;
    private String quote;

    public Citation() {
    }

    public Citation(String chunk_id, String quote) {
        this.chunk_id = chunk_id;
        this.quote = quote;
    }

    public String getChunk_id() {
        return chunk_id;
    }

    public void setChunk_id(String chunk_id) {
        this.chunk_id = chunk_id;
    }

    public String getQuote() {
        return quote;
    }

    public void setQuote(String quote) {
        this.quote = quote;
    }
}
