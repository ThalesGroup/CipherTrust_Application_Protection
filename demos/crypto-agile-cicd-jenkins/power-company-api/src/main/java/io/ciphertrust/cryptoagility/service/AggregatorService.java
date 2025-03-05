package io.ciphertrust.cryptoagility.service;

import java.util.List;

import io.ciphertrust.cryptoagility.entity.Aggregator;

public interface AggregatorService {
    public Aggregator createAggregator(Aggregator aggregator);
    public Aggregator getAggregatorById(Long id);
    public List<Aggregator> getAllAggregators();
    public void addSmartMeterToAggregator(Long aggregatorId, Long smartMeterId);
}
