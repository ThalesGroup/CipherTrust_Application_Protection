package example;


class CustomException extends Exception {
	private int errorCode;

	public CustomException(String message, int errorCode) {
		super(message);
		this.errorCode = errorCode;
	}

	public int getErrorCode() {
		return errorCode;
	}
}