package com.thalesgroup.crdp_demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpMethod;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.client.RestTemplate;

import com.thalesgroup.crdp_demo.model.CRDPProtectRequest;
import com.thalesgroup.crdp_demo.model.CRDPProtectResponse;
import com.thalesgroup.crdp_demo.model.CRDPRevealRequest;
import com.thalesgroup.crdp_demo.model.CRDPRevealResponse;
import com.thalesgroup.crdp_demo.model.Payload;

/**
 * @author CipherTrust.io
 *
 */
@RestController
public class CRDP {
    @Value("${PROTECTION_POLICY:PPName}")
    private String protectionPolicy;

    @Autowired
    private RestTemplate restTemplate;

    @PostMapping("/api/crdp/protect")
	public Payload protect(@RequestBody Payload bean) {
		Payload response = new Payload();

        HttpHeaders headers = new HttpHeaders();
		headers.set("Content-Type", "application/json");
		String url = "http://crdp-service:8090/v1/protect";
        CRDPProtectRequest request = new CRDPProtectRequest();
        request.setData(bean.getData());
        request.setPolicyName(protectionPolicy);

        HttpEntity<CRDPProtectRequest> entity = new HttpEntity<>(request, headers);
        ResponseEntity<CRDPProtectResponse> CRDPResponse = restTemplate.exchange(url, HttpMethod.POST, entity, CRDPProtectResponse.class);

		response.setData(CRDPResponse.getBody().getCipherText());
        return response;
	}

    @PostMapping("/api/crdp/reveal")
	public Payload reveal(@RequestBody Payload bean) {
		Payload response = new Payload();

        HttpHeaders headers = new HttpHeaders();
		headers.set("Content-Type", "application/json");
		String url = "http://crdp-service:8090/v1/reveal";
        CRDPRevealRequest request = new CRDPRevealRequest();
        request.setData(bean.getData());
        request.setPolicyName(protectionPolicy);
        request.setUsername(bean.getUsername());

        HttpEntity<CRDPRevealRequest> entity = new HttpEntity<>(request, headers);
        ResponseEntity<CRDPRevealResponse> CRDPResponse = restTemplate.exchange(url, HttpMethod.POST, entity, CRDPRevealResponse.class);

		response.setData(CRDPResponse.getBody().getData());
        return response;
	}
}
