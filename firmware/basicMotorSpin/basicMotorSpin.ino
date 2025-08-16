#define stepPin 3
#define dirPin 2

const int stepsPerRev = 200 * 16; // 200 steps, 16× microstepping

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

  Serial.begin(9600);
  Serial.println("Enter angle to rotate (positive = CW, negative = CCW):");
}

void loop() {
  if (Serial.available() > 0) {
    float angle = Serial.parseFloat(); // read angle as float
    Serial.print("Rotating ");
    Serial.print(angle);
    Serial.println(" degrees...");

    // Determine direction
    if (angle >= 0) {
      digitalWrite(dirPin, HIGH); // CW
    } else {
      digitalWrite(dirPin, LOW); // CCW
      angle = -angle; // make it positive for step count calculation
    }

    // Calculate steps to move
    int stepsToMove = (int)((angle / 360.0) * stepsPerRev);

    // Move the motor
    for (int i = 0; i < stepsToMove; i++) {
      digitalWrite(stepPin, HIGH);
      delayMicroseconds(1000);
      digitalWrite(stepPin, LOW);
      delayMicroseconds(1000);
    }

    Serial.println("Done!");
    Serial.println("Enter next angle:");
  }
}