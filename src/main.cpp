#include <Arduino.h>

// Motor control pins
const int pwmOpen = 25;   // Open direction
const int pwmClose = 26;  // Close direction (use a different pin than open)

// Pedal input pin (analog)
const int pedalPin = 34;  // ADC-capable pin on ESP32

// PWM config
const int pwmFreq = 500;
const int pwmResolution = 8; // 0–255
const int pwmChannelOpen = 0;
const int pwmChannelClose = 1;

// Control tuning
const int deadband = 20;     // ADC tolerance for position hold
const int throttleMin = 116; // Known throttle closed position (ADC)
const int throttleMax = 887; // Known throttle open position (ADC)

// Fake current throttle state (in absence of TPS)
int virtualThrottlePos = throttleMin;

void stopMotor() {
  ledcWrite(pwmChannelOpen, 0);
  ledcWrite(pwmChannelClose, 0);
}

void driveOpen(int duty) {
  ledcWrite(pwmChannelOpen, duty);
  ledcWrite(pwmChannelClose, 0);
}

void driveClose(int duty) {
  ledcWrite(pwmChannelOpen, 0);
  ledcWrite(pwmChannelClose, duty);
}

void setup() {
  Serial.begin(115200);

  // Set up PWM channels
  ledcSetup(pwmChannelOpen, pwmFreq, pwmResolution);
  ledcSetup(pwmChannelClose, pwmFreq, pwmResolution);

  // Attach PWM pins
  ledcAttachPin(pwmOpen, pwmChannelOpen);
  ledcAttachPin(pwmClose, pwmChannelClose);

  // Initialize motor off
  ledcWrite(pwmChannelOpen, 0);
  ledcWrite(pwmChannelClose, 0);
}

void loop() {
  // Read pedal value (0–4095)
  int pedalADC = analogRead(pedalPin);
  int targetThrottle = map(pedalADC, 0, 4095, throttleMin, throttleMax);

  // Compare to virtual throttle position
  int error = targetThrottle - virtualThrottlePos;

  Serial.print("Pedal ADC: "); Serial.print(pedalADC);
  Serial.print(" | Target: "); Serial.print(targetThrottle);
  Serial.print(" | VirtualPos: "); Serial.println(virtualThrottlePos);

  if (abs(error) < deadband) {
    // Close enough, stop motor
    stopMotor();
  } else if (error > 0) {
    // Need to open
    driveOpen(120);
    virtualThrottlePos += 2; // Fake position increase
  } else {
    // Need to close
    driveClose(120);
    virtualThrottlePos -= 2; // Fake position decrease
  }

  delay(20);  // Tune this for stability
}