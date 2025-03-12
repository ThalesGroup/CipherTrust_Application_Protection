package io.ciphertrust.cryptoagility.controller;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.ciphertrust.cryptoagility.entity.SmartMeter;
import io.ciphertrust.cryptoagility.entity.User;
import io.ciphertrust.cryptoagility.entity.UserBill;
import io.ciphertrust.cryptoagility.entity.UserPayment;
import io.ciphertrust.cryptoagility.service.UserService;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {

    @Autowired
    private UserService userService;

     // Authenticate a user
     @GetMapping("/{username}/{password}")
     public ResponseEntity<Long> authenticate(@PathVariable String username, @PathVariable String password) {
         User user = userService.getUserByUsernameAndPassword(username, password);
         return ResponseEntity.ok(user.getId());
     }

    // Create a new user
    @PostMapping(consumes = MediaType.APPLICATION_JSON_VALUE)
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
    @PutMapping(value = "/{id}", consumes = MediaType.APPLICATION_JSON_VALUE)
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
    @PostMapping(value="/{userId}/payment-info", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<UserPayment> addPaymentInfo(@PathVariable Long userId, @RequestBody UserPayment paymentInfo) {
        UserPayment savedPaymentInfo = userService.addPaymentInfo(userId, paymentInfo);
        return ResponseEntity.ok(savedPaymentInfo);
    }

    // Get all payment info for a user
    @GetMapping("/{userId}/payment-info")
    public ResponseEntity<UserPayment> getPaymentInfosByUserId(@PathVariable Long userId) {
        UserPayment paymentInfo = userService.getPaymentInfosByUserId(userId);
        return ResponseEntity.ok(paymentInfo);
    }

    // Delete payment info by ID
    @DeleteMapping("/payment-info/{paymentInfoId}")
    public ResponseEntity<Void> deletePaymentInfo(@PathVariable Long paymentInfoId) {
        userService.deletePaymentInfo(paymentInfoId);
        return ResponseEntity.noContent().build();
    }

    // Add Smart Meter for a user
    @PostMapping(value = "/{userId}/smart-meter", consumes = MediaType.APPLICATION_JSON_VALUE)
    public ResponseEntity<SmartMeter> addSmartMeter(@PathVariable Long userId, @RequestBody SmartMeter meter) {
        SmartMeter savedSmartMeterInfo = userService.addSmartMeter(userId, meter);
        return ResponseEntity.ok(savedSmartMeterInfo);
    }

    // Get all smart meters for a user
    @GetMapping("/{userId}/smart-meter")
    public ResponseEntity<SmartMeter> getSmartMetersByUserId(@PathVariable Long userId) {
        SmartMeter smartMeter = userService.getSmartMetersByUserId(userId);
        return ResponseEntity.ok(smartMeter);
    }

    // Delete smart meter by ID
    @DeleteMapping("/smart-meter/{smartMeterId}")
    public ResponseEntity<Void> deleteSmartMeter(@PathVariable Long smartMeterId) {
        userService.deleteSmartMeter(smartMeterId);
        return ResponseEntity.noContent().build();
    }

    @PostMapping("/{userId}/bills")
    public ResponseEntity<UserBill> addBillToUser(
            @PathVariable Long userId,
            @RequestBody UserBill bill) {
        UserBill savedBill = userService.addBillToUser(userId, bill);
        return ResponseEntity.ok(savedBill);
    }

    @GetMapping("/{userId}/bills")
    public ResponseEntity<List<UserBill>> getBillsForUser(@PathVariable Long userId) {
        List<UserBill> bills = userService.getBillsForUser(userId);
        return ResponseEntity.ok(bills);
    }
}