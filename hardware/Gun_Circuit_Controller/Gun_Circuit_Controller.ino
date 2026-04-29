#include <Servo.h>

Servo turretServo;
Servo triggerServo;

// Pins
const int turretPin = 9;
const int triggerPin = 10;
const int ledRed = 6;
const int ledGreen = 7;

// State
int currentAngle = 90;
int targetAngle = 90;

bool firing = false;
unsigned long fireStart = 0;

String inputBuffer = "";

void setup() {
  Serial.begin(9600);

  turretServo.attach(turretPin);
  triggerServo.attach(triggerPin);

  pinMode(ledRed, OUTPUT);
  pinMode(ledGreen, OUTPUT);

  turretServo.write(currentAngle);
  triggerServo.write(90);  // default (released position)
}

void loop() {
  readSerial();
  updateTurret();
  updateTrigger();  // 🔥 handles firing sequence
}

void readSerial() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n') {
      processCommand(inputBuffer);
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }
}

void processCommand(String cmd) {
  if (cmd.length() < 3) return;

  char type = cmd.charAt(0);
  int value = cmd.substring(2).toInt();

  switch (type) {

    case 'A':  // Angle
      value = constrain(value, 50, 130);
      if (value != targetAngle) {
        targetAngle = value;
        digitalWrite(ledGreen, HIGH);
      }
      break;

    case 'F':  // 🔥 FIRE (single-shot trigger)
      if (value == 1 && !firing) {
        firing = true;
        fireStart = millis();

        digitalWrite(ledRed, HIGH);
        triggerServo.write(60);  // press trigger
      }
      break;

    case 'M':  // Movement LED
      digitalWrite(ledGreen, value == 1 ? HIGH : LOW);
      break;

    default:
      break;
  }
}

void updateTurret() {
  if (currentAngle != targetAngle) {
    currentAngle = targetAngle;

    turretServo.write(currentAngle);

    if (currentAngle == targetAngle) {
      digitalWrite(ledGreen, LOW);
    }
  }
}

void updateTrigger() {
  if (firing) {
    unsigned long elapsed = millis() - fireStart;

    // Release trigger after 200ms
    if (elapsed > 200) {
      triggerServo.write(90);
    }

    // End firing after 1 second
    if (elapsed > 1000) {
      digitalWrite(ledRed, LOW);
      firing = false;
    }
  }
}