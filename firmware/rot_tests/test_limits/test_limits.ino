#define stepPin 3
#define dirPin 2

const float stepsPerRev = 1600.0;          // 1/8 microstepping
const float degPerStep = 360.0 / stepsPerRev;  // ~0.225°

int angles[] = {5, 10, 20, 25, 30, 40, 45, 50, 60};
const int numAngles = sizeof(angles) / sizeof(angles[0]);

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  digitalWrite(dirPin, HIGH); // Forward only
}

void loop() {
  int prevAngle = 0;

  for (int i = 0; i < numAngles; i++) {
    int deltaDeg = angles[i] - prevAngle;
    int steps = round(deltaDeg / degPerStep);  // convert angle delta to step count

    if (steps == 0) continue;

    unsigned long delayPerStep = 1000000UL / steps / 2;  // microseconds for each half step

    for (int j = 0; j < steps; j++) {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(delayPerStep);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(delayPerStep);
    }

    delay(100);  // optional pause before next movement
    prevAngle = angles[i];
  }

  while (true); // Stop after completing all segments
}