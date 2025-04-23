package io.ciphertrust.migration.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import io.ciphertrust.migration.entity.User;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsernameAndPassword(String name, String password);
}
