package io.ciphertrust.cryptoagility.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import io.ciphertrust.cryptoagility.entity.User;

public interface UserRepository extends JpaRepository<User, Long> {

}
