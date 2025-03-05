package io.ciphertrust.cryptoagility.serviceImpl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.cryptoagility.entity.Aggregator;
import io.ciphertrust.cryptoagility.entity.SmartMeter;
import io.ciphertrust.cryptoagility.repository.AggregatorRepository;
import io.ciphertrust.cryptoagility.repository.SmartMeterRepository;
import io.ciphertrust.cryptoagility.service.AggregatorService;

@Service
public class AggregatorServiceImpl implements AggregatorService{

    @Autowired
    private AggregatorRepository aggregatorRepository;

    @Autowired
    private SmartMeterRepository smartMeterRepository;

    public Aggregator createAggregator(Aggregator aggregator) {
        return aggregatorRepository.save(aggregator);
    }

    public Aggregator getAggregatorById(Long id) {
        return aggregatorRepository.findById(id).orElseThrow(() -> new RuntimeException("Aggregator not found"));
    }

    public List<Aggregator> getAllAggregators() {
        return aggregatorRepository.findAll();
    }

    public void addSmartMeterToAggregator(Long aggregatorId, Long smartMeterId) {
        Aggregator aggregator = aggregatorRepository.findById(aggregatorId)
                .orElseThrow(() -> new RuntimeException("Aggregator not found"));

        // Fetch the existing SmartMeter
        SmartMeter smartMeter = smartMeterRepository.findById(smartMeterId)
                .orElseThrow(() -> new RuntimeException("SmartMeter not found"));

        // Associate the SmartMeter with the Aggregator
        smartMeter.setAggregator(aggregator);
        aggregator.getSmartMeters().add(smartMeter);

        // Save the updated Aggregator
        aggregatorRepository.save(aggregator);
    }
}
