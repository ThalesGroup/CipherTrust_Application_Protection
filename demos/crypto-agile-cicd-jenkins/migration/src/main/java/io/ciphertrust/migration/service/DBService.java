package io.ciphertrust.migration.service;

import java.util.List;

import io.ciphertrust.migration.entity.SmartMeterData;
import io.ciphertrust.migration.entity.User;
import io.ciphertrust.migration.entity.UserPayment;

public interface DBService {
    List<User> getAllUsers();
    User updatUser(User user);
    List<UserPayment> getAllPaymentInfo();
    UserPayment updatUserPayment(UserPayment payment);
    List<SmartMeterData> getAllMeterData();
    SmartMeterData updatMeterData(SmartMeterData meterData);
}
