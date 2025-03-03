package io.ciphertrust.cryptoagility.service;

import java.util.List;

import io.ciphertrust.cryptoagility.entity.User;
import io.ciphertrust.cryptoagility.entity.UserPayment;

public interface UserService {
    User createUser(User user);
    User getUserById(Long id);
    List<User> getAllUsers();
    User updateUser(Long id, User user);
    void deleteUser(Long id);
    UserPayment addPaymentInfo(Long userId, UserPayment paymentInfo);
    List<UserPayment> getPaymentInfosByUserId(Long userId);
    void deletePaymentInfo(Long paymentInfoId);
}