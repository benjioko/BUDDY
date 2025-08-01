#define stepPin 3
#define dirPin 2

const float stepsPerRev = 1600.0;              // 1/8 microstepping
const float degPerStep = 360.0 / stepsPerRev;  // ~0.225°
const float targetSpeedDegPerSec = 137.5;      // degrees per second

// === Customize these ===
float startAngle = 0.0;
float stopAngle  = 90.0;  // ← change this to test other positions

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

  float deltaDeg = stopAngle - startAngle;
  bool direction = deltaDeg >= 0;
  int stepsToMove = round(abs(deltaDeg) / degPerStep);

  // Calculate step rate based on target angular velocity
  float timeToMoveSec = abs(deltaDeg) / targetSpeedDegPerSec;
  float delayPerStep_us = (timeToMoveSec / stepsToMove) * 1e6 / 2;  // divide by 2 for HIGH and LOW

  digitalWrite(dirPin, direction ? HIGH : LOW);

  for (int i = 0; i < stepsToMove; i++) {
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(delayPerStep_us);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(delayPerStep_us);
  }

  // done
  while (true);
}

void loop() {
  // nothing
}