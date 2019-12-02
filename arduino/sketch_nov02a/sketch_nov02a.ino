/**
 * Code for the Blessed Rest wake-up system
 * Developed by Taite Clark, Braden Elkins, Christopher Gould and Grady Habicht
 * for Introduction to Engineering Design, Fall 2019
 */
#include<SPI.h>
#include<RF24.h>
#include <Wire.h>

RF24 radio(9,10);


char tiltStatus = 's'; // s=stop, f=fwd, r=reverse
char tiltStatusOld = 's';
char liftStatus = 's';
char liftStatusOld = 's';
int liftMotor[3] = {4,8,6}; // {IN1, IN2, ENA}
int tiltMotor[3] = {3,7,5};
byte tiltSpeed = 0;
byte liftSpeed = 0;

void forward(int motor[3], int spd) {
    digitalWrite(motor[0], 1);
    digitalWrite(motor[1], 0);
    analogWrite(motor[2], spd);
}

void reverse(int motor[3], int spd) {
  digitalWrite(motor[0], 0);
  digitalWrite(motor[1], 1);
  analogWrite(motor[2], spd); 
}

void coast(int motor[3]) {
  digitalWrite(motor[0], 1);
  digitalWrite(motor[1], 1);  
}

void setup(void) {
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  const uint64_t pipe = 0xE0E0F1F1E0LL;
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.powerUp();
  Serial.begin(9600);
  for (int i = 0; i < 3; i ++) {
    pinMode(liftMotor[i], OUTPUT);
    pinMode(tiltMotor[i], OUTPUT);  
  }
  coast(liftMotor);
  coast(tiltMotor);
  
  tiltStatus = 's';
  liftStatus = 's';
}

void loop(void) {
  radio.startListening();
  char receivedMessage[2] = {0};
  if (radio.available()) {
    radio.read(receivedMessage, sizeof(receivedMessage));
    radio.stopListening();
    tiltStatusOld = tiltStatus;
    liftStatusOld = liftStatus;
    tiltStatus = receivedMessage[0];
    liftStatus = receivedMessage[1];
    Serial.println(tiltStatus);
  }
  if (tiltStatus == 's') {
    tiltSpeed = 0;
    coast(tiltMotor);  
  } else if (tiltStatus == 'f') {
    if (tiltStatusOld == 'r') {
      // prevent bad things from quickly switching
      tiltSpeed = 0;  
    } else if (tiltSpeed < 100) {
      tiltSpeed += 5;
    }  
    forward(tiltMotor, tiltSpeed);
  } else if (tiltStatus == 'r') {
    if (tiltStatusOld == 'f') {
      tiltSpeed = 0;  
    } else if (tiltSpeed < 100) {
      tiltSpeed += 5;  
    }  
    reverse(tiltMotor, tiltSpeed);
  }
  if (liftStatus == 's') {
    liftSpeed = 0;
    coast(liftMotor);  
  } else if (liftStatus == 'f') {
    if (liftStatusOld == 'r') {
      // prevent bad things resulting from quickly switching
      liftSpeed = 0;  
    } else if (liftSpeed < 100) {
      liftSpeed += 5;
    }  
    forward(liftMotor, liftSpeed);
  } else if (liftStatus == 'r') {
    if (liftStatusOld == 'f') {
      liftSpeed = 0;  
    } else if (liftSpeed < 100) {
      liftSpeed += 5;  
    }  
    reverse(liftMotor, liftSpeed);
  }
  delay(10);
}
