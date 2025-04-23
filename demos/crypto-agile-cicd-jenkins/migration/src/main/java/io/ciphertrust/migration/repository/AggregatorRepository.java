package io.ciphertrust.migration.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import io.ciphertrust.migration.entity.Aggregator;

public interface AggregatorRepository extends JpaRepository<Aggregator, Long> {
}