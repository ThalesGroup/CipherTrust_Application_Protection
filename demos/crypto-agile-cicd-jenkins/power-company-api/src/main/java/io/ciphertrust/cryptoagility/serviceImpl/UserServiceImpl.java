package io.ciphertrust.cryptoagility.serviceImpl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.cryptoagility.entity.User;
import io.ciphertrust.cryptoagility.entity.UserPayment;
import io.ciphertrust.cryptoagility.repository.UserPaymentRepository;
import io.ciphertrust.cryptoagility.repository.UserRepository;
import io.ciphertrust.cryptoagility.service.UserService;
import jakarta.persistence.EntityNotFoundException;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private UserPaymentRepository userPaymentRepository;

    @Override
    public User createUser(User user) {
        return userRepository.save(user);
    }

    @Override
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("User not found with id: " + id));
    }

    @Override
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @Override
    public User updateUser(Long id, User user) {
        User existingUser = getUserById(id);
        existingUser.setName(user.getName());
        existingUser.setUsername(user.getUsername());
        existingUser.setPassword(user.getPassword());
        existingUser.setEmail(user.getEmail());
        existingUser.setContactNum(user.getContactNum());
        existingUser.setAddressLineOne(user.getAddressLineOne());
        existingUser.setAddressLineTwo(user.getAddressLineTwo());
        existingUser.setCity(user.getCity());
        existingUser.setState(user.getState());
        existingUser.setCountry(user.getCountry());
        existingUser.setZip(user.getZip());
        return userRepository.save(existingUser);
    }

    @Override
    public void deleteUser(Long id) {
        userRepository.deleteById(id);
    }

    @Override
    public UserPayment addPaymentInfo(Long userId, UserPayment paymentInfo) {
        User user = getUserById(userId);
        paymentInfo.setUser(user);
        return userPaymentRepository.save(paymentInfo);
    }

    @Override
    public List<UserPayment> getPaymentInfosByUserId(Long userId) {
        User user = getUserById(userId);
        return user.getPaymentCards();
    }

    @Override
    public void deletePaymentInfo(Long paymentInfoId) {
        userPaymentRepository.deleteById(paymentInfoId);
    }

}
