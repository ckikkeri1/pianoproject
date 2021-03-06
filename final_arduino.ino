/*
 * This file uses the data fron the photoresistor to detect 
 * when a key is pressed or not because the finger blocks the 
 * light when a key is pressed. The lines related to the button
 * was used in conjunction with the arduino speaker to test
 * the photoresistor. 
 */
const int  buttonPin = 2;    // the pin that the pushbutton is attached to
int buttonPushCounter = 0;   // counter for the number of button presses
int buttonState = 0;         // current state of the button
int lastButtonState = 0;     // previous state of the button

// variable to hold sensor value
int sensorValue;
// variable to calibrate low value
int sensorLow = 1023;
// variable to calibrate high value
int sensorHigh = 0;
// LED pin
const int ledPin = 13;

void setup() {
  // Make the LED pin an output and turn it on to show calibration begins
  pinMode(ledPin, OUTPUT);
  pinMode(buttonPin, INPUT);
  digitalWrite(ledPin, HIGH);
  
  Serial.begin(9600);

  // calibrate for the first five seconds after program runs
  while (millis() < 5000) {
    // record the maximum sensor value
    sensorValue = analogRead(A0);
    if (sensorValue > sensorHigh) {
      sensorHigh = sensorValue;
    }
    // record the minimum sensor value
    if (sensorValue < sensorLow) {
      sensorLow = sensorValue;
    }
  }
  // turn the LED off, signaling the end of the calibration period
  digitalWrite(ledPin, LOW);
}

void loop() {
  //button stuff
  buttonState = digitalRead(buttonPin);
  if (buttonState != lastButtonState) {
    // if the state has changed, increment the counter
    if (buttonState == HIGH) {
      // if the current state is HIGH then the button went from off to on:
      buttonPushCounter++;
      //Serial.println(buttonPushCounter);
    } else {
      // if the current state is LOW then the button went from on to off:
    }
    // Delay a little bit to avoid bouncing
    delay(50);
  }
  // save the current state as the last state, for next time through the loop
  lastButtonState = buttonState;
  

  //read the input from A0 and store it in a variable
  sensorValue = analogRead(A0);
  
  // map the sensor values to a wide range of pitches
  int uncal = map(sensorValue, sensorLow, sensorHigh, 50, 4000);
  int pitch = constrain(uncal, 50, 4000);
  Serial.println(sensorValue);
  if (buttonPushCounter % 2 == 0){
    tone(8, 0, 20);  
  }else{
    tone(8, pitch, 20); // play the tone for 20 ms on pin 8
  }
  
  
  // wait for a moment
  delay(10);
}
