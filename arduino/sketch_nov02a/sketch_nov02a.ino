#include<SPI.h>
#include<RF24.h>
#include <Wire.h>
#include <Adafruit_MotorShield.h>

RF24 radio(9,10);
Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// tilt motor on M1, lift motor on M2
Adafruit_DCMotor *tiltMotor = AFMS.getMotor(1);
Adafruit_DCMotor *liftMotor = AFMS.getMotor(2);


void setup(void) {
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  const uint64_t pipe = 0xE0E0F1F1E0LL;
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.powerUp();
  Serial.begin(9600);
  AFMS.begin();
  tiltMotor->setSpeed(200);
  tiltMotor->run(FORWARD);
  tiltMotor->run(RELEASE);
  liftMotor->setSpeed(200);
  liftMotor->run(FORWARD);
  liftMotor->run(RELEASE);
}

void loop(void) {
  radio.startListening();
  char receivedMessage[16] = {0};
  if (radio.available()) {
    radio.read(receivedMessage, sizeof(receivedMessage));
    radio.stopListening();
    String stringMessage(receivedMessage);
    Serial.println(stringMessage);
    if (stringMessage == "tilt up") {
      tiltMotor->run(FORWARD);
    } else if (stringMessage == "tilt down") {
      tiltMotor->run(BACKWARD);
    } else if (stringMessage == "tilt stop") {
      tiltMotor->run(RELEASE);
    } else if (stringMessage == "lift up") {
      liftMotor->run(FORWARD);
    } else if (stringMessage == "lift down") {
      liftMotor->run(BACKWARD);  
    } else if (stringMessage == "lift stop") {
      liftMotor->run(RELEASE);  
    }
  }
  delay(10);
}
