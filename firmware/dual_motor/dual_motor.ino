#define stepX  6    // X-axis pins  (same as your original stepPin / dirPin)
#define dirX   5

#define stepT  3    // Tilt-axis pins – choose any two free I/O pins
#define dirT   2

const int dataLength = 60;

// --- linX axis ---
int deltaStepsLin[dataLength] = {
  -11, -32, -52, -70, -86, -101, -115, -127, -138, -146, -154, -160, -165, -167, -169, -169, -168, -165, -160, -154, -146, -138, -127, -114, -102, -86, -70, -52, -32, -11, 11, 32, 52, 70, 86, 102, 114, 127, 138, 146, 154, 160, 165, 168, 169, 169, 167, 165, 160, 154, 146, 138, 127, 115, 101, 86, 70, 52, 32, 11
};
unsigned int delayTimesLin[dataLength] = {
  3790, 1299, 801, 595, 483, 412, 362, 327, 302, 285, 270, 260, 252, 249, 246, 246, 247, 252, 260, 270, 285, 302, 327, 365, 408, 483, 595, 801, 1299, 3790, 3790, 1299, 801, 595, 483, 408, 365, 327, 302, 285, 270, 260, 252, 247, 246, 246, 249, 252, 260, 270, 285, 302, 327, 362, 412, 483, 595, 801, 1299, 3790
};

// --- rotX axis ---
int deltaStepsRot[dataLength] = {
  -20, -20, -20, -19, -18, -17, -16, -15, -14, -12, -10, -8, -6, -4, -1, 0, 0, 1, 2, 4, 5, 8, 10, 13, 16, 19, 24, 28, 32, 38, 45, 53, 62, 66, 70, 72, -1528, 70, 66, 62, 53, 45, 35, 22, 7, -7, -20, -32, -42, -50, -58, -63, -68, 1529, -71, -71, -68, -65, -61, -53
};
unsigned int delayTimesRot[dataLength] = {
  2085, 2079, 2085, 2194, 2311, 2452, 2606, 2773, 2978, 3475, 4159, 5212, 6950, 10399, 41700, 0, 0, 41700, 20850, 10399, 8340, 5212, 4159, 3207, 2606, 2189, 1737, 1489, 1299, 1097, 926, 784, 672, 631, 594, 579, 27, 594, 631, 672, 784, 926, 1191, 1890, 5957, 5957, 2079, 1303, 992, 831, 718, 661, 611, 27, 587, 585, 613, 641, 681, 786
};

int currentIndexX = 0;
int currentIndexT = 0;

int stepsRemainingX = 0;
int stepsRemainingT = 0;

unsigned long lastStepTimeX = 0;
unsigned long lastStepTimeT = 0;

bool steppingX = false;
bool steppingT = false;

void setup() {
  pinMode(stepX, OUTPUT);
  pinMode(dirX, OUTPUT);
  pinMode(stepT, OUTPUT);
  pinMode(dirT, OUTPUT);

  // Prime first motion segment
  if (currentIndexX < dataLength) {
    digitalWrite(dirX, deltaStepsLin[currentIndexX] >= 0 ? HIGH : LOW);
    stepsRemainingX = abs(deltaStepsLin[currentIndexX]);
    lastStepTimeX = micros();
    steppingX = true;
  }

  if (currentIndexT < dataLength) {
    digitalWrite(dirT, deltaStepsRot[currentIndexT] >= 0 ? HIGH : LOW);
    stepsRemainingT = abs(deltaStepsRot[currentIndexT]);
    lastStepTimeT = micros();
    steppingT = true;
  }
}

void loop() {
  unsigned long now = micros();

  // --- LINEAR X AXIS ---
  if (steppingX && stepsRemainingX > 0) {
    if (now - lastStepTimeX >= delayTimesLin[currentIndexX]) {
      digitalWrite(stepX, HIGH);
      delayMicroseconds(2);  // Small pulse width
      digitalWrite(stepX, LOW);

      lastStepTimeX = now;
      stepsRemainingX--;
    }
  } else if (steppingX && currentIndexX < dataLength - 1) {
    currentIndexX++;
    digitalWrite(dirX, deltaStepsLin[currentIndexX] >= 0 ? HIGH : LOW);
    stepsRemainingX = abs(deltaStepsLin[currentIndexX]);
  }

  // --- ROTATION AXIS ---
  if (steppingT && stepsRemainingT > 0) {
    if (now - lastStepTimeT >= delayTimesRot[currentIndexT]) {
      digitalWrite(stepT, HIGH);
      delayMicroseconds(2);  // Small pulse width
      digitalWrite(stepT, LOW);

      lastStepTimeT = now;
      stepsRemainingT--;
    }
  } else if (steppingT && currentIndexT < dataLength - 1) {
    currentIndexT++;
    digitalWrite(dirT, deltaStepsRot[currentIndexT] >= 0 ? HIGH : LOW);
    stepsRemainingT = abs(deltaStepsRot[currentIndexT]);
  }

  // Stop condition
  if (currentIndexX >= dataLength && currentIndexT >= dataLength) {
    while (true); // Done
  }
}