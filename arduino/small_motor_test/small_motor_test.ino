/* 
This is a test sketch for the Adafruit assembled Motor Shield for Arduino v2
It won't work with v1.x motor shields! Only for the v2's with built in PWM
control

For use with the Adafruit Motor Shield v2 
---->  http://www.adafruit.com/products/1438
*/

#include <Wire.h>

// Create the motor shield object with the default I2C address
//Adafruit_MotorShield AFMS = Adafruit_MotorShield(); 
// Or, create it with a different I2C address (say for stacking)
// Adafruit_MotorShield AFMS = Adafruit_MotorShield(0x61); 

// Select which 'port' M1, M2, M3 or M4. In this case, M1
//Adafruit_DCMotor *myMotor = AFMS.getMotor(2);
// You can also make another motor on port M2
//Adafruit_DCMotor *myOtherMotor = AFMS.getMotor(2);

int liftMotor[3] = {9,12,11};
int tiltMotor[3] = {8,13,10};


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

void setup() {
  Serial.begin(9600);           // set up Serial library at 9600 bps
  for (int i = 0; i < 3; i ++) {
    pinMode(liftMotor[i], OUTPUT);
    pinMode(tiltMotor[i], OUTPUT);  
  }
  coast(liftMotor);
  coast(tiltMotor);
}

void loop() {
  uint8_t i;
  
  Serial.print("tick");

  for (i=0; i<255; i++) {
    forward(tiltMotor, i);  
    delay(5);
  }
  delay(1000);
  for (i=255; i!=0; i--) {
    forward(tiltMotor, i);  
    delay(5);
  }
  
  Serial.print("tock");

  for (i=0; i<255; i++) {
    reverse(tiltMotor, i);  
    delay(5);
  }
  delay(1000);
  for (i=255; i!=0; i--) {
    reverse(tiltMotor, i);  
    delay(5);
  }

  Serial.print("tech");
  delay(1000);
  coast(tiltMotor);
}
