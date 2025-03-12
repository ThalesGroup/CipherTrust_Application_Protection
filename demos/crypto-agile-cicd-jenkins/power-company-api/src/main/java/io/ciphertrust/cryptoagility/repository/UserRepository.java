package io.ciphertrust.cryptoagility.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import io.ciphertrust.cryptoagility.entity.User;

public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByUsernameAndPassword(String name, String password);
}
