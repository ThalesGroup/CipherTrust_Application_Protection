package io.ciphertrust.cryptoagility.controller;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import io.ciphertrust.cryptoagility.entity.SmartMeterData;
import io.ciphertrust.cryptoagility.service.SmartMeterDataService;

@RestController
@RequestMapping("/api/smart-meter-data")
public class SmartMeterDataController {

    @Autowired
    private SmartMeterDataService smartMeterDataService;

    // Save telemetry data
    @PostMapping
    public ResponseEntity<SmartMeterData> saveSmartMeterData(@RequestBody SmartMeterData data) {
        SmartMeterData savedData = smartMeterDataService.saveSmartMeterData(data);
        return ResponseEntity.ok(savedData);
    }

    // Get telemetry data by ID
    @GetMapping("/{id}")
    public ResponseEntity<SmartMeterData> getSmartMeterDataById(@PathVariable Long id) {
        SmartMeterData data = smartMeterDataService.getSmartMeterDataById(id);
        return ResponseEntity.ok(data);
    }

    // Get all telemetry data
    @GetMapping
    public ResponseEntity<List<SmartMeterData>> getAllSmartMeterData() {
        List<SmartMeterData> dataList = smartMeterDataService.getAllSmartMeterData();
        return ResponseEntity.ok(dataList);
    }

    // Get telemetry data within a timestamp range
    @GetMapping("/filter")
    public ResponseEntity<List<SmartMeterData>> getSmartMeterDataByTimestampRange(
            @RequestParam LocalDateTime start,
            @RequestParam LocalDateTime end) {
        List<SmartMeterData> dataList = smartMeterDataService.getSmartMeterDataByTimestampRange(start, end);
        return ResponseEntity.ok(dataList);
    }

    // Delete telemetry data by ID
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteSmartMeterData(@PathVariable Long id) {
        smartMeterDataService.deleteSmartMeterData(id);
        return ResponseEntity.noContent().build();
    }
}