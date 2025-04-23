package io.ciphertrust.migration;

import java.util.List;

import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import io.ciphertrust.migration.entity.SmartMeterData;
import io.ciphertrust.migration.entity.User;
import io.ciphertrust.migration.entity.UserPayment;
import io.ciphertrust.migration.service.BouncyCastleService;
import io.ciphertrust.migration.service.DBService;

@Component
public class MigrationAppRunner implements CommandLineRunner {

    private final BouncyCastleService bc;
    private final DBService db;

    public MigrationAppRunner(BouncyCastleService bc, DBService db) {
        this.bc = bc;
        this.db = db;
    }

    @Override
    public void run(String... args) throws Exception {
        if (args.length > 0) {
            String serviceArg = args[0];
            List<User> users = db.getAllUsers();
            List<UserPayment> payments = db.getAllPaymentInfo();
            List<SmartMeterData> smartMeterData = db.getAllMeterData();
            
            if ("bc".equalsIgnoreCase(serviceArg)) {
                for (User user : users) {
                    user.setAddressLineOne(bc.encryptCVV(user.getAddressLineOne()));
                    user.setAddressLineTwo(bc.encryptCVV(user.getAddressLineTwo()));
                    user.setEmail(bc.encryptCVV(user.getEmail()));
                    user.setContactNum(bc.encryptCVV(user.getContactNum()));
                    db.updatUser(user);
                }
                for (UserPayment payment : payments) {
                    payment.setCardNumber(bc.encryptCreditCard(payment.getCardNumber()));
                    payment.setCvv(bc.encryptCVV(payment.getCvv()));
                    db.updatUserPayment(payment);
                }
                for (SmartMeterData data : smartMeterData) {
                    data.setTotalEnergyConsumption(bc.encryptTelemetryData(data.getTotalEnergyConsumption()));
                    data.setInstantaneousPowerUsage(bc.encryptTelemetryData(data.getInstantaneousPowerUsage()));
                    db.updatMeterData(data);
                }
            } else if ("crdp".equalsIgnoreCase(serviceArg)) {
                System.out.println("No worries, BDT already took care of me while you were away!");                
            } else {
                System.out.println("Invalid argument. Use 'abc' or 'def'");
            }
        } else {
            System.out.println("No argument provided. Use 'bc' or 'crdp' to select service");
        }
    }

}
