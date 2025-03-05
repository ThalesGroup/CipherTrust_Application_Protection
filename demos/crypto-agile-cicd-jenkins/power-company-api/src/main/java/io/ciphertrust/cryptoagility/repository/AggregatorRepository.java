package io.ciphertrust.cryptoagility.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.cryptoagility.entity.Aggregator;

public interface AggregatorRepository extends JpaRepository<Aggregator, Long> {
}