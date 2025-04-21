package io.ciphertrust.cryptoagility.serviceImpl;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.cryptoagility.dto.AggregatorEnergyStatus;
import io.ciphertrust.cryptoagility.dto.AggregatorSummary;
import io.ciphertrust.cryptoagility.entity.Aggregator;
import io.ciphertrust.cryptoagility.entity.SmartMeter;
import io.ciphertrust.cryptoagility.entity.SmartMeterData;
import io.ciphertrust.cryptoagility.repository.AggregatorRepository;
import io.ciphertrust.cryptoagility.repository.SmartMeterDataRepository;
import io.ciphertrust.cryptoagility.repository.SmartMeterRepository;
import io.ciphertrust.cryptoagility.service.AggregatorService;
import jakarta.persistence.EntityManager;
import jakarta.transaction.Transactional;

@Service
public class AggregatorServiceImpl implements AggregatorService{

    @Autowired
    private AggregatorRepository aggregatorRepository;

    @Autowired
    private SmartMeterRepository smartMeterRepository;

    @Autowired
    private SmartMeterDataRepository smartMeterDataRepository;

    @Autowired
    private EntityManager entityManager;

    @Override
    public Aggregator createAggregator(Aggregator aggregator) {
        return aggregatorRepository.save(aggregator);
    }

    @Transactional
    @Override
    public Aggregator getAggregatorById(Long id) {
        Aggregator aggregator = aggregatorRepository.findById(id)
            .orElseThrow(() -> new RuntimeException("Aggregator not found"));
        // Access the lazy-loaded collection within the transactional context
        aggregator.getSmartMeters().size(); // Force initialization
        return aggregator;
    }

    @Override
    public List<Aggregator> getAllAggregators() {
        return aggregatorRepository.findAll();
    }

    @Transactional
    @Override
    public void addSmartMeterToAggregator(Long aggregatorId, Long smartMeterId) {
        Aggregator aggregator = aggregatorRepository.findById(aggregatorId)
                .orElseThrow(() -> new RuntimeException("Aggregator not found"));

        // Fetch the existing SmartMeter
        SmartMeter smartMeter = smartMeterRepository.findById(smartMeterId)
                .orElseThrow(() -> new RuntimeException("SmartMeter not found"));

        // Reattach entities if necessary
        aggregator = entityManager.merge(aggregator);
        smartMeter = entityManager.merge(smartMeter);

        // Associate the SmartMeter with the Aggregator
        smartMeter.setAggregator(aggregator);
        aggregator.getSmartMeters().add(smartMeter);

        // Save the updated Aggregator
        //aggregatorRepository.save(aggregator);
    }

    @Override
    public AggregatorEnergyStatus calculateEnergyStatus(Long aggregatorId, double threshold) {
        // Fetch the Aggregator
        Aggregator aggregator = aggregatorRepository.findById(aggregatorId)
            .orElseThrow(() -> new RuntimeException("Aggregator not found"));

        // Calculate the total energy consumption for the last 24 hours
        LocalDateTime startTime = LocalDateTime.now().minusHours(24);
        double totalEnergyConsumption = aggregator.getSmartMeters().stream()
            .mapToDouble(smartMeter -> {
                List<SmartMeterData> telemetryData = smartMeterDataRepository
                    .findTelemetryDataBySmartMeterIdAndTimestampAfter(smartMeter.getId(), startTime);
                return telemetryData.stream()
                    .mapToDouble(data -> {
                        //String totalEnergyStr = bcService.decryptTelemetryData(data.getTotalEnergyConsumption());
                        String totalEnergyStr = data.getTotalEnergyConsumption();
                        return Double.parseDouble(totalEnergyStr);
                    })
                    .sum();
            })
            .sum();

        // Determine the status based on the threshold
        String status;
        if (totalEnergyConsumption > threshold) {
            status = "critical";
        } else if (totalEnergyConsumption > 0.7 * threshold) {
            status = "degraded";
        } else {
            status = "good";
        }

        // Return the result
        return new AggregatorEnergyStatus(aggregatorId, totalEnergyConsumption, status);
    }

    @Override
    public List<AggregatorSummary> getAllAggregatorsSummary(double threshold) {
        List<Aggregator> aggregators = aggregatorRepository.findAll();
        return aggregators.stream()
                .map(aggregator -> {
                    // Calculate total energy consumption for the last 24 hours
                    LocalDateTime startTime = LocalDateTime.now().minusHours(24);
                    double totalEnergyConsumption = aggregator.getSmartMeters().stream()
                        .mapToDouble(smartMeter -> {
                            List<SmartMeterData> telemetryData = smartMeterDataRepository
                                .findTelemetryDataBySmartMeterIdAndTimestampAfter(smartMeter.getId(), startTime);
                            return telemetryData.stream()
                                .mapToDouble(data -> {
                                    String totalEnergyStr = data.getTotalEnergyConsumption();
                                    return Double.parseDouble(totalEnergyStr);
                                })
                                .sum();
                        })
                        .sum();

                    // Determine the status based on the threshold
                    String status;
                    if (totalEnergyConsumption > threshold) {
                        status = "critical";
                    } else if (totalEnergyConsumption > 0.7 * threshold) {
                        status = "degraded";
                    } else {
                        status = "good";
                    }

                    // Get the total number of smart meters
                    int totalSmartMeters = aggregator.getSmartMeters().size();

                    // Create and return the AggregatorSummary DTO
                    return new AggregatorSummary(
                        aggregator.getId(),
                        aggregator.getName(),
                        aggregator.getLocation(),
                        totalEnergyConsumption,
                        status,
                        totalSmartMeters
                    );
                })
                .collect(Collectors.toList());
    }
}
