package io.ciphertrust.cryptoagility.serviceImpl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.cryptoagility.entity.SmartMeter;
import io.ciphertrust.cryptoagility.entity.User;
import io.ciphertrust.cryptoagility.entity.UserBill;
import io.ciphertrust.cryptoagility.entity.UserPayment;
import io.ciphertrust.cryptoagility.repository.SmartMeterRepository;
import io.ciphertrust.cryptoagility.repository.UserBillRepository;
import io.ciphertrust.cryptoagility.repository.UserPaymentRepository;
import io.ciphertrust.cryptoagility.repository.UserRepository;
import io.ciphertrust.cryptoagility.service.UserService;
import jakarta.persistence.EntityManager;
import jakarta.persistence.EntityNotFoundException;
import jakarta.transaction.Transactional;

@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private UserPaymentRepository userPaymentRepository;

    @Autowired
    private SmartMeterRepository meterRepository;

    @Autowired
    private UserBillRepository userBillRepository;

    @Autowired
    private EntityManager entityManager;

    @Override
    @Transactional
    public User createUser(User user) {
        return userRepository.save(user);
    }

    @Override
    public User getUserById(Long id) {
        return userRepository.findById(id)
                .orElseThrow(() -> new EntityNotFoundException("User not found with id: " + id));
    }

    @Override
    public User getUserByUsernameAndPassword(String username, String password) {
        return userRepository.findByUsernameAndPassword(username, password)
                .orElseThrow(() -> new EntityNotFoundException("Invalid username or password or both"));
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
        user.setPaymentInfo(paymentInfo);
        return userPaymentRepository.saveAndFlush(paymentInfo);
    }

    @Override
    public UserPayment getPaymentInfosByUserId(Long userId) {
        User user = getUserById(userId);
        return user.getPaymentInfo();
    }

    @Override
    public void deletePaymentInfo(Long paymentInfoId) {
        userPaymentRepository.deleteById(paymentInfoId);
    }

    @Override
    @Transactional
    public SmartMeter addSmartMeter(Long userId, SmartMeter meter) {
        User user = getUserById(userId);
        user = entityManager.merge(user);
        meter = entityManager.merge(meter);

        meter.setUser(user);
        user.setSmartMeter(meter);
        return meterRepository.save(meter);
    }

    @Override
    public SmartMeter getSmartMetersByUserId(Long userId) {
        User user = getUserById(userId);
        return user.getSmartMeter();
    }

    @Override
    public void deleteSmartMeter(Long meterId) {
        meterRepository.deleteById(meterId);
    }

    @Override
    public UserBill addBillToUser(Long userId, UserBill bill) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        bill.setUser(user);
        return userBillRepository.save(bill);
    }

    @Override
    public List<UserBill> getBillsForUser(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return user.getBills();
    }
}
