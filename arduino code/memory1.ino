#define stepPin 4
#define dirPin 3

const int rev = 1600;
int angle = (200*16 + 400);
int difference = angle % rev;
int speed = 1000;

void moveMotor(int steps, int speed, bool direction){
  for (int i = 0; i < steps; i++){
    digitalWrite(stepPin, direction);
    delayMicroseconds(speed);
    digitalWrite(stepPin, direction);
    delayMicroseconds(speed);
  }
}

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  digitalWrite(dirPin, HIGH);  //clockwise

// initial motion
moveMotor(angle, speed, HIGH);

//revert
moveMotor(difference, speed, LOW);

}

void loop() {
  
}
