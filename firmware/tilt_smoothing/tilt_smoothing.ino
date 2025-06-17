#define stepPin 4
#define dirPin 3

const int dataLength = 10;
int deltaSteps[dataLength] = {
  -10, -29, -44, -56, -61, -62, -56, -44, -29, -9
};
unsigned int delayTimes[dataLength] = {
  4159, 1437, 947, 742, 683, 672, 742, 947, 1437, 4622
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
