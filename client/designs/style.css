#include <Wire.h>
#include <MPU6050.h>
#include <SoftwareSerial.h>

#define DEBUG true
#define LM35 A0

MPU6050 mpu;
SoftwareSerial esp(10, 11);

// Timers
unsigned long timer = 0;
float timeStep = 0.01;

// Pitch, Roll and Yaw values
int pitch = 0.0;
int roll = 0.0;
int yaw = 0.0;

// ESP MAC Address
String espMacAddress;

void espSetup(){
  String networkName = "randomName";
  String networkPassword = "randomPassword";
  
  // Reset the esp in case of power outage
  sendData("AT+RST\r\n", 10000, DEBUG);
  
  // Configure ESP to operate as client
  sendData("AT+CWMODE=3\r\n", 10000, DEBUG);

  // List access points
//  sendData("AT+CWLAP\r\n", 10000, DEBUG);

  // Join an access point
  sendData("AT+CWJAP=\"FLOW-WiFi\",\"Honeymad5\"\r\n", 5000, DEBUG);

  // Verify that access point has been joined
  //sendData("AT+CIFSR\r\n", 3000, DEBUG);  
}

String getMacAddress(){
  String response = "";
  response = sendData("AT+CIPSTAMAC?\r\n\r\n", 3000, false);  
  return response.substring(42, 59);
}

String sendData(String command, const int timeout, boolean debug) {
    String response = "";
    
    esp.print(command); // send the read character to the esp8266
    
    unsigned long time = millis();
    
    while( (time+timeout) > millis())
    {
      while(esp.available())
      {
        
        // The esp has data so display its output to the serial window 
        char c = esp.read(); // read the next character.
        response += c;
      }  
    }
    
    if(debug)
    {
      Serial.print(response);
    }
    
    return response;
}

void gyroscopeSetup(){
  // Initialize MPU6050
  Serial.println("Initialize MPU6050");
  while(!mpu.begin(MPU6050_SCALE_2000DPS, MPU6050_RANGE_2G))
  {
    Serial.println("Could not find a valid MPU6050 sensor, check wiring!");
    delay(500);
  }
  
  // If you want, you can set gyroscope offsets
  mpu.setGyroOffsetX(138);
  mpu.setGyroOffsetY(80);
  mpu.setGyroOffsetZ(9);
  
  // Calibrate gyroscope. The calibration must be at rest.
  // If you don't want calibrate, comment this line.
  mpu.calibrateGyro();

  // Set threshold sensivty. Default 3.
  // If you don't want use threshold, comment this line or set 0.
  mpu.setThreshold(1);
}

int readGyroscope(){  
  Vector rawGyro = mpu.readRawGyro();
  Vector normGyro = mpu.readNormalizeGyro();

//  Serial.print(" Xraw = ");
//  Serial.print(rawGyro.XAxis);
//  Serial.print(" Yraw = ");
//  Serial.print(rawGyro.YAxis);
//  Serial.print(" Zraw = ");
//  Serial.println(rawGyro.ZAxis);
//
//  Serial.print(" Xnorm = ");
//  Serial.print(normGyro.XAxis);
//  Serial.print(" Ynorm = ");
//  Serial.print(normGyro.YAxis);
//  Serial.print(" Znorm = ");
//  Serial.println(normGyro.ZAxis);

  return (int)rawGyro.YAxis;
}

int getTemperature(int testing){
  float voltage, temp;

  if (testing == 0){
    // Read temperature from the LM35 sensor
    voltage = analogRead(LM35) * (5.0/1023.0);
    temp = 100 * voltage;
  }
  else{
    // Generate random test data
    temp = random(30, 41);
  }  

  return (int)temp;
}

String generatePostRequest(String route, String portNumber, int cLength, String pData) {
  String requestType = "POST /" + route + " HTTP/1.1\r\n";
  String hostInfo = "Host: 192.168.1.11:" + portNumber + "\r\n";
  String contentType = "Content-Type: application/json\r\n";
  String contentLength = "Content-Length: " + String(cLength) + "\r\n\r\n";
  String postData = pData + "\r\n\r\n";

  return requestType + hostInfo + contentType + contentLength + postData;
}

String generateCIPSend(int requestLength){
  String cipSend = "AT+CIPSEND=" + String(requestLength) + "\r\n";
  
  return cipSend;
}

String generatePost(String patient_id, float pos, int temp){
  String post = "{\"patient_id\": \""+patient_id+ "\", \"position\": "+String(pos)+ ", \"temperature\": "+String(temp)+"}\r\n\r\n";
  
  return post;
}

void setup() {
  Serial.begin(9600);
  esp.begin(9600);

  Serial.println("################################################");
  Serial.println("                   START SETUP                  ");
  Serial.println("################################################");

  // Setup the gyroscope
  gyroscopeSetup();

  // Setup the ESP8266
  espSetup();

  // Setup the LM35
  pinMode(LM35, INPUT);

  // Get the MAC address of the ESP
  espMacAddress = getMacAddress();
  Serial.print("MAC Address: "); Serial.println(espMacAddress);

  Serial.println("################################################");
  Serial.println("                     END SETUP                  ");
  Serial.println("################################################");
}

void loop() {  
  int temp;
  int pos;

  pos = readGyroscope();
  temp = getTemperature(0);

  String postData = generatePost(espMacAddress, pos, temp);
  String postRequest = generatePostRequest("api/record", "5000", postData.length(), postData);  
  String CIPSend = generateCIPSend(postRequest.length());

  sendData("AT+CIPSTART=\"TCP\",\"192.168.1.6\",5000\r\n", 3000, DEBUG);
  sendData(CIPSend, 1000, DEBUG);
  sendData(postRequest, 5000, DEBUG);
}
