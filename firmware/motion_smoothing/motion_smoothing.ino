#define stepPin 6
#define dirPin 5

const int dataLength = 60;

// --- linX axis ---
int deltaSteps[dataLength] = {
  -11, -32, -52, -70, -86, -101, -115, -127, -138, -146, -154, -160, -165, -167, -169, -169, -168, -165, -160, -154, -146, -138, -127, -114, -102, -86, -70, -52, -32, -11, 11, 32, 52, 70, 86, 102, 114, 127, 138, 146, 154, 160, 165, 168, 169, 169, 167, 165, 160, 154, 146, 138, 127, 115, 101, 86, 70, 52, 32, 11
};
unsigned int delayTimes[dataLength] = {
  3790, 1299, 801, 595, 483, 412, 362, 327, 302, 285, 270, 260, 252, 249, 246, 246, 247, 252, 260, 270, 285, 302, 327, 365, 408, 483, 595, 801, 1299, 3790, 3790, 1299, 801, 595, 483, 408, 365, 327, 302, 285, 270, 260, 252, 247, 246, 246, 249, 252, 260, 270, 285, 302, 327, 362, 412, 483, 595, 801, 1299, 3790
};

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
}

void loop() {
  for (int i = 0; i < dataLength; i++) {
    int direction = deltaSteps[i] >= 0 ? HIGH : LOW;
    digitalWrite(dirPin, direction);

    for (int j = 0; j < abs(deltaSteps[i]); j++) {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(delayTimes[i] / 2);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(delayTimes[i] / 2);
    }
  }

  while (true); // Stop after completing motion
}