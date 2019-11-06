#include<SPI.h>
#include<RF24.h>

RF24 radio(9,10);
int led = 7;
int led2 = 6;

void setup(void) {
  radio.begin();
  radio.setPALevel(RF24_PA_MAX);
  radio.setChannel(0x76);
  const uint64_t pipe = 0xE0E0F1F1E0LL;
  radio.openReadingPipe(1, pipe);
  radio.enableDynamicPayloads();
  radio.powerUp();
  pinMode(led, OUTPUT);
  Serial.begin(9600);
}

void loop(void) {
  radio.startListening();
  char receivedMessage[16] = {0};
  if (radio.available()) {
    radio.read(receivedMessage, sizeof(receivedMessage));
    radio.stopListening();
    String stringMessage(receivedMessage);
    Serial.println(stringMessage);
    if (stringMessage == "test on") {
      digitalWrite(led, HIGH);
    } else if (stringMessage == "test off") {
      digitalWrite(led, LOW);
    } else if (stringMessage == "test2 on") {
      digitalWrite(led2, HIGH);
    } else if (stringMessage == "test2 off") {
      digitalWrite(led2, LOW);
    }
  }
  delay(10);
}
