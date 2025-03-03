package io.ciphertrust.cryptoagility.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.ciphertrust.cryptoagility.entity.SmartMeter;
import io.ciphertrust.cryptoagility.service.SmartMeterService;

@RestController
@RequestMapping("/api/smart-meters")
public class SmartMeterController {

    @Autowired
    private SmartMeterService smartMeterService;

    @PostMapping
    public ResponseEntity<SmartMeter> addSmartMeter(@RequestBody SmartMeter smartMeter) {
        SmartMeter savedSmartMeter = smartMeterService.addSmartMeter(smartMeter);
        return ResponseEntity.ok(savedSmartMeter);
    }

    @GetMapping("/{id}")
    public ResponseEntity<SmartMeter> getSmartMeterById(@PathVariable Long id) {
        SmartMeter smartMeter = smartMeterService.getSmartMeterById(id);
        return ResponseEntity.ok(smartMeter);
    }

    @GetMapping("/user/{userId}")
    public ResponseEntity<List<SmartMeter>> getSmartMetersByUserId(@PathVariable Long userId) {
        List<SmartMeter> smartMeters = smartMeterService.getSmartMetersByUserId(userId);
        return ResponseEntity.ok(smartMeters);
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSmartMeter(@PathVariable Long id) {
        smartMeterService.deleteSmartMeter(id);
        return ResponseEntity.noContent().build();
    }
}
