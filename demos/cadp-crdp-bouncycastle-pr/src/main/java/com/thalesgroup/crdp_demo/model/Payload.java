package com.thalesgroup.crdp_demo.model;

/**
 * @author CipherTrust.io
 *
 */
public class Payload {

    private String data;
    private String username;

    public String getData() {
        return data;
    }
    public void setData(String data) {
        this.data = data;
    }
    public String getUsername() {
        return username;
    }
    public void setUsername(String username) {
        this.username = username;
    }
    public Payload(String data) {
        this.data = data;
    }
    public Payload() {
    }
}
