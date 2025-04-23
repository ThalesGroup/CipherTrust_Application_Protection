package io.ciphertrust.migration.service.impl;

import java.util.List;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import io.ciphertrust.migration.entity.SmartMeterData;
import io.ciphertrust.migration.entity.User;
import io.ciphertrust.migration.entity.UserPayment;
import io.ciphertrust.migration.repository.SmartMeterDataRepository;
import io.ciphertrust.migration.repository.UserPaymentRepository;
import io.ciphertrust.migration.repository.UserRepository;
import io.ciphertrust.migration.service.DBService;

@Service
public class DBServiceImpl implements DBService {

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private UserPaymentRepository userPaymentRepository;

    @Autowired
    private SmartMeterDataRepository smartMeterDataRepository;

    @Override
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @Override
    public User updatUser(User user) {
        User updated = userRepository.findById(user.getId())
            .orElseThrow(() -> new RuntimeException("User not found with id: " + user.getId()));
        if (updated != null) {
            updated.setEmail(user.getEmail());
            updated.setContactNum(user.getContactNum());
            updated.setAddressLineOne(user.getAddressLineOne());
            updated.setAddressLineTwo(user.getAddressLineTwo());
            return userRepository.save(updated);
        } else {
            throw new RuntimeException("User not found with id: " + user.getId());
        }
    }

    @Override
    public List<UserPayment> getAllPaymentInfo() {
        return userPaymentRepository.findAll();
    }

    @Override
    public UserPayment updatUserPayment(UserPayment payment) {
        UserPayment updated = userPaymentRepository.findById(payment.getId())
            .orElseThrow(() -> new RuntimeException("UserPayment not found with id: " + payment.getId()));
        if (updated != null) {
            updated.setCardNumber(payment.getCardNumber());
            updated.setCvv(payment.getCvv());
            return userPaymentRepository.save(updated);
        } else {
            throw new RuntimeException("UserPayment not found with id: " + payment.getId());
        }
    }

    @Override
    public List<SmartMeterData> getAllMeterData() {
        return smartMeterDataRepository.findAll();
    }

    @Override
    public SmartMeterData updatMeterData(SmartMeterData meterData) {
        SmartMeterData updated = smartMeterDataRepository.findById(meterData.getId())
            .orElseThrow(() -> new RuntimeException("SmartMeterData not found with id: " + meterData.getId()));
        if (updated != null) {
            updated.setTotalEnergyConsumption(meterData.getTotalEnergyConsumption());
            updated.setInstantaneousPowerUsage(meterData.getInstantaneousPowerUsage());
            return smartMeterDataRepository.save(updated);
        } else {
            throw new RuntimeException("SmartMeterData not found with id: " + meterData.getId());
        }
    }
    
}
