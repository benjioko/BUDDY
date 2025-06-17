#define stepPin 4
#define dirPin 3

const int rev = 1600;
const float degStep = 1.8/8;
int angle = 45; //in degrees;
//get step @ angle
int steps = angle/degStep; 
int difference = steps % rev;
int speed = 1000;

void moveMotor(int steps, int speed, bool direction){
  digitalWrite(dirPin, direction);
  for (int i = 0; i < steps; i++){
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(speed);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(speed);
  }
}

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

// initial motion
moveMotor(steps, speed, LOW);

//revert
moveMotor(difference, speed, HIGH);

}

void loop() {
  
}
