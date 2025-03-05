package io.ciphertrust.cryptoagility.controller;

import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.ciphertrust.cryptoagility.dto.AggregatorResponse;
import io.ciphertrust.cryptoagility.entity.Aggregator;
import io.ciphertrust.cryptoagility.service.AggregatorService;

@RestController
@RequestMapping("/api/v1/aggregators")
public class AggregatorController {

    @Autowired
    private AggregatorService aggregatorService;

    @PostMapping
    public ResponseEntity<Aggregator> createAggregator(@RequestBody Aggregator aggregator) {
        Aggregator createdAggregator = aggregatorService.createAggregator(aggregator);
        return ResponseEntity.ok(createdAggregator);
    }

    @GetMapping
    public ResponseEntity<List<AggregatorResponse>> getAllAggregators() {
        List<Aggregator> aggregators = aggregatorService.getAllAggregators();
        List<AggregatorResponse> response = aggregators.stream()
                .map(aggregator -> new AggregatorResponse(
                        aggregator.getId(),
                        aggregator.getCurrentStatus(),
                        aggregator.getStatusUpdateTime(),
                        aggregator.getLocation(),
                        aggregator.getSmartMeters()))
                .collect(Collectors.toList());
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<AggregatorResponse> getAggregatorById(@PathVariable Long id) {
        Aggregator aggregator = aggregatorService.getAggregatorById(id);
        AggregatorResponse response = new AggregatorResponse(
                aggregator.getId(),
                aggregator.getCurrentStatus(),
                aggregator.getStatusUpdateTime(),
                aggregator.getLocation(),
                aggregator.getSmartMeters());
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{aggregatorId}/smartmeters/{smartMeterId}")
    public ResponseEntity<Void> addExistingSmartMeterToAggregator(
            @PathVariable Long aggregatorId,
            @PathVariable Long smartMeterId) {
        aggregatorService.addSmartMeterToAggregator(aggregatorId, smartMeterId);
        return ResponseEntity.ok().build();
    }
}