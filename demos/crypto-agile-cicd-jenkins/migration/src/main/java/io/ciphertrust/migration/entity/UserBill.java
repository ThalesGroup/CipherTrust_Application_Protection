package io.ciphertrust.migration.entity;

import jakarta.persistence.*;
import java.time.YearMonth;

import com.fasterxml.jackson.annotation.JsonBackReference;

@Entity
@Table(name = "user_bills")
public class UserBill {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "amount_paid", nullable = false)
    private Double amountPaid;

    @Column(name = "status", nullable = false)
    private String status; // e.g., "paid" or "due"

    @Column(name = "month_year", nullable = false)
    private YearMonth monthYear; // Represents the month and year of the bill

    @ManyToOne
    @JoinColumn(name = "user_id", nullable = false)
    @JsonBackReference("user-bills")
    private User user; // Associated user

    // Constructors, Getters, and Setters

    public UserBill() {
    }

    public UserBill(Double amountPaid, String status, YearMonth monthYear) {
        this.amountPaid = amountPaid;
        this.status = status;
        this.monthYear = monthYear;
    }

    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public Double getAmountPaid() {
        return amountPaid;
    }

    public void setAmountPaid(Double amountPaid) {
        this.amountPaid = amountPaid;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public YearMonth getMonthYear() {
        return monthYear;
    }

    public void setMonthYear(YearMonth monthYear) {
        this.monthYear = monthYear;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }
}
