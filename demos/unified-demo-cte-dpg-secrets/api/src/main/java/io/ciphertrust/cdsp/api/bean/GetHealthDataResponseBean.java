package io.ciphertrust.cdsp.api.bean;

import java.util.List;
import io.ciphertrust.cdsp.api.model.HealthData;

public class GetHealthDataResponseBean {
    private List<HealthData> data;

	public List<HealthData> getData() {
		return data;
	}

	public void setData(List<HealthData> data) {
		this.data = data;
	}

	public GetHealthDataResponseBean(List<HealthData> data) {
		this.data = data;
	}

	public GetHealthDataResponseBean() {
	}

	@Override
	public String toString() {
		return "GetHealthDataResponseBean [data=" + data + "]";
	}
}
