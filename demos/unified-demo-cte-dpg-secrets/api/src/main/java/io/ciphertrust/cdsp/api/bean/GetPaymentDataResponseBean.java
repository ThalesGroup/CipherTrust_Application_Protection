package io.ciphertrust.cdsp.api.bean;

import java.util.List;
import io.ciphertrust.cdsp.api.model.PaymentData;

public class GetPaymentDataResponseBean {
    private List<PaymentData> data;
    

	public List<PaymentData> getData() {
		return data;
	}

	public void setData(List<PaymentData> data) {
		this.data = data;
	}

	public GetPaymentDataResponseBean(List<PaymentData> data) {
		this.data = data;
	}

	public GetPaymentDataResponseBean() {
	}

	@Override
	public String toString() {
		return "GetPaymentDataResponseBean [data=" + data + "]";
	}
}
