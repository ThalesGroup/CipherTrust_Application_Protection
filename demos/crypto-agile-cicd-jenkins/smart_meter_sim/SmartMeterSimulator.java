import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Random;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class SmartMeterSimulator {

    private static final String API_URL = "http://localhost:9090/api/v1/smart-meter-data"; // Replace with your API URL
    private static final DateTimeFormatter TIMESTAMP_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss");
    private static final Random RANDOM = new Random();

    private final Long userId;
    private final Long smartMeterId;

    public SmartMeterSimulator(Long userId, Long smartMeterId) {
        this.userId = userId;
        this.smartMeterId = smartMeterId;
    }

    public void start() {
        ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
        scheduler.scheduleAtFixedRate(this::sendTelemetryData, 0, 1, TimeUnit.MINUTES); // Send data every 15 minutes
    }

    private void sendTelemetryData() {
        try {
            // Simulate telemetry data
            double totalEnergyConsumption = 100 + RANDOM.nextDouble() * 50; // Random value between 100 and 150 kWh
            double instantaneousPowerUsage = 2 + RANDOM.nextDouble() * 3; // Random value between 2 and 5 kW
            double voltage = 220 + RANDOM.nextDouble() * 20; // Random value between 220 and 240 volts
            double current = 5 + RANDOM.nextDouble() * 5; // Random value between 5 and 10 amperes
            double powerFactor = 0.9 + RANDOM.nextDouble() * 0.1; // Random value between 0.9 and 1.0
            double frequency = 50 + RANDOM.nextDouble() * 2; // Random value between 50 and 52 Hz
            String timestamp = LocalDateTime.now().format(TIMESTAMP_FORMAT);
            double temperature = 20 + RANDOM.nextDouble() * 10; // Random value between 20 and 30 °C
            double humidity = 40 + RANDOM.nextDouble() * 30; // Random value between 40 and 70 %
            String detailedConsumptionIntervals = "0-15min: " + (0.5 + RANDOM.nextDouble() * 0.5) + "kWh";

            // Create JSON payload
            String jsonPayload = String.format(
                    "{\"totalEnergyConsumption\": %.2f, " +
                            "\"instantaneousPowerUsage\": %.2f, " +
                            "\"voltage\": %.2f, " +
                            "\"current\": %.2f, " +
                            "\"powerFactor\": %.2f, " +
                            "\"frequency\": %.2f, " +
                            "\"timestamp\": \"%s\", " +
                            "\"temperature\": %.2f, " +
                            "\"humidity\": %.2f, " +
                            "\"detailedConsumptionIntervals\": \"%s\", " +
                            "\"smartMeter\": {\"id\": %d}}",
                    totalEnergyConsumption, instantaneousPowerUsage, voltage, current,
                    powerFactor, frequency, timestamp, temperature, humidity,
                    detailedConsumptionIntervals, smartMeterId);

            // Send HTTP POST request
            URL url = new URL(API_URL);
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("POST");
            connection.setRequestProperty("Content-Type", "application/json");
            connection.setDoOutput(true);

            try (OutputStream os = connection.getOutputStream()) {
                byte[] input = jsonPayload.getBytes("utf-8");
                os.write(input, 0, input.length);
            }

            int responseCode = connection.getResponseCode();
            if (responseCode == HttpURLConnection.HTTP_OK) {
                System.out.println("Data sent successfully for user " + userId + " and smart meter " + smartMeterId);
            } else {
                System.err.println("Failed to send data. Response code: " + responseCode);
            }

            connection.disconnect();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {
        if (args.length < 2) {
            System.err.println("Usage: java SmartMeterSimulator <userId> <smartMeterId>");
            System.exit(1);
        }

        Long userId = Long.parseLong(args[0]);
        Long smartMeterId = Long.parseLong(args[1]);

        SmartMeterSimulator simulator = new SmartMeterSimulator(userId, smartMeterId);
        simulator.start();

        System.out.println("Smart meter simulator started for user " + userId + " and smart meter " + smartMeterId);
    }
}