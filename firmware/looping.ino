#define stepPin 4
#define dirPin 3

void setup() {
  pinMode(stepPin, OUTPUT);
  pinMode(dirPin, OUTPUT);

  digitalWrite(dirPin, HIGH);  //clockwise
}

void loop() {
  //intitialization
  int i = 0; 
  int rev = 1600;
  int angle = (200*16 + 400);
  int difference = angle%rev;
  for (i; i < angle; i++) { //this is rotate the motor
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(1000);
  }
 if (angle%rev != 0){         // this is to revert the position to the orginal position
   int i = 0;
   digitalWrite(dirPin, LOW); // counterclockwise 
  for(i; i < difference; i++ ){
    digitalWrite(stepPin, HIGH);
    delayMicroseconds(1000);
    digitalWrite(stepPin, LOW);
    delayMicroseconds(1000);
  }
 }
  while (true); // stop everything
}
