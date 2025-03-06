package com.thalesgroup.crdp_demo.controller;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import com.thalesgroup.crdp_demo.model.Payload;
import com.thalesgroup.crdp_demo.service.Crypto;

/**
 * @author CipherTrust.io
 *
 */
@RestController
public class BouncyCastle {
	@Autowired
    private Crypto BCService;

    @PostMapping("/api/bouncy/encrypt")
	public Payload protect(@RequestBody Payload bean) {
		Payload response = new Payload();
		try {
            response.setData(BCService.BouncyCastleEncrypt(bean.getData()));
        } catch (Exception e) {
            e.printStackTrace();
        }
		return response;
	}

    @PostMapping("/api/bouncy/decrypt")
	public Payload reveal(@RequestBody Payload bean) {
		Payload response = new Payload();
		try {
            response.setData(BCService.BouncyCastleDecrypt(bean.getData()));
        } catch (Exception e) {
            e.printStackTrace();
        }
		return response;
	}
}
