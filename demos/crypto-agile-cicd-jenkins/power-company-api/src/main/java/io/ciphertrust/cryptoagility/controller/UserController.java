package io.ciphertrust.cryptoagility.controller;

import io.ciphertrust.cryptoagility.entity.User;
import io.ciphertrust.cryptoagility.entity.UserPayment;
import io.ciphertrust.cryptoagility.service.UserService;
import io.ciphertrust.cryptoagility.serviceImpl.UserServiceImpl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1")
public class UserController {

    @Autowired
    private UserService userService;

    // Create a new user
    @PostMapping
    public ResponseEntity<User> createUser(@RequestBody User user) {
        User createdUser = userService.createUser(user);
        return ResponseEntity.ok(createdUser);
    }

    // Get a user by ID
    @GetMapping("/{id}")
    public ResponseEntity<User> getUserById(@PathVariable Long id) {
        User user = userService.getUserById(id);
        return ResponseEntity.ok(user);
    }

    // Get all users
    @GetMapping
    public ResponseEntity<List<User>> getAllUsers() {
        List<User> users = userService.getAllUsers();
        return ResponseEntity.ok(users);
    }

    // Update a user
    @PutMapping("/{id}")
    public ResponseEntity<User> updateUser(@PathVariable Long id, @RequestBody User user) {
        User updatedUser = userService.updateUser(id, user);
        return ResponseEntity.ok(updatedUser);
    }

    // Delete a user
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userService.deleteUser(id);
        return ResponseEntity.noContent().build();
    }

    // Add payment info for a user
    @PostMapping("/{userId}/payment-info")
    public ResponseEntity<UserPayment> addPaymentInfo(@PathVariable Long userId, @RequestBody UserPayment paymentInfo) {
        UserPayment savedPaymentInfo = userService.addPaymentInfo(userId, paymentInfo);
        return ResponseEntity.ok(savedPaymentInfo);
    }

    // Get all payment info for a user
    @GetMapping("/{userId}/payment-info")
    public ResponseEntity<List<UserPayment>> getPaymentInfosByUserId(@PathVariable Long userId) {
        List<UserPayment> paymentInfos = userService.getPaymentInfosByUserId(userId);
        return ResponseEntity.ok(paymentInfos);
    }

    // Delete payment info by ID
    @DeleteMapping("/payment-info/{paymentInfoId}")
    public ResponseEntity<Void> deletePaymentInfo(@PathVariable Long paymentInfoId) {
        userService.deletePaymentInfo(paymentInfoId);
        return ResponseEntity.noContent().build();
    }
}