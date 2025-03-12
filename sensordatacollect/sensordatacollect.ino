#include <DHT.h>
#include <SoftwareSerial.h>

#define MOISTURE_SENSOR_PIN A0  
#define DHTPIN 2                
#define DHTTYPE DHT11           
#define PH_RX 5                 
#define PH_TX 6                 

DHT dht(DHTPIN, DHTTYPE);
SoftwareSerial pHSerial(PH_RX, PH_TX); 

void setup() {
    Serial.begin(9600);  
    dht.begin();         
    pHSerial.begin(9600);

    Serial.println("MoisturePercentage,Temperature,Humidity,pH");
}

void loop() {
    int moistureValue = analogRead(MOISTURE_SENSOR_PIN);
    int moisturePercentage = map(moistureValue, 1023, 247, 0, 100);
    moisturePercentage = constrain(moisturePercentage, 0, 100);

    float temperature = dht.readTemperature(); 
    float humidity = dht.readHumidity(); 

    String pHValue = "N/A"; 
    if (pHSerial.available()) {
        pHValue = pHSerial.readStringUntil('\n');
        pHValue.trim();  // Removes spaces and unwanted characters
    }

    Serial.print(moisturePercentage);
    Serial.print(",");
    Serial.print(temperature);
    Serial.print(",");
    Serial.print(humidity);
    Serial.print(",");
    Serial.println(pHValue);  // Ensures only pH value is sent

    delay(1000);  // Wait for 30 minutes before taking the next reading
}
