// Firmware to control 2 x BTS7960 drivers. Feedback is provided by potentiometer feedback on 24V linear actuators
// Position and PWM output signal are provided by PID loops
// [estop, enable, toolPos, steerPos]

// Rob Lloyd
// Lincoln 2021

//ESTOP INPUT NOT DONE YET


#include "BTS7960.h"
#include <PID_v1.h>
#include <movingAvg.h>                  // https://github.com/JChristensen/movingAvg

//=========================================================================================
// for motor, left is backwards
const uint8_t T_R_EN = 3;
const uint8_t T_L_EN = 4;
const uint8_t T_R_PWM = 5;
const uint8_t T_L_PWM = 6;
const uint8_t T_FB = A1;

BTS7960 tController(T_L_EN, T_R_EN, T_L_PWM, T_R_PWM);
int tPosition;
movingAvg tPositionAvg(4);                // define the moving average object
int tCentre = 50;  // sets the home position for the tool
int tDeadband = 1; //Stops the actuator hunting quite so much
int tMax = 1000; //tCentre - 90;
int tMin = 40; //tCentre + 90;

//Define Variables we'll be connecting to
double tSetpoint, tInput, tOutputLeft, tOutputRight;

//Specify the links and initial tuning parameters
double tKp = 3, tKi = 0.1, tKd = 0.1;
PID tLeftPID(&tInput, &tOutputLeft, &tSetpoint, tKp, tKi, tKd, DIRECT);
PID tRightPID(&tInput, &tOutputRight, &tSetpoint, tKp, tKi, tKd, REVERSE);

//=====================================================================================

// For actuator, extend is....
const uint8_t S_R_EN = 7;
const uint8_t S_L_EN = 8;
const uint8_t S_R_PWM = 9;
const uint8_t S_L_PWM = 10;
const uint8_t S_FB = A0;

BTS7960 sController(S_L_EN, S_R_EN, S_L_PWM, S_R_PWM);
int sPosition;
movingAvg sPositionAvg(4);                // define the moving average object
int sCentre = 500; // sets the centre position for steering
int sDeadband = 1; //Stops the actuator hunting quite so much
int sMax = 1000; //sCentre - 90;
int sMin = 40; //sCentre + 90;

//Define Variables we'll be connecting to
double sSetpoint, sInput, sOutputLeft, sOutputRight;

//Specify the links and initial tuning parameters
double sKp = 3, sKi = 0.1, sKd = 0.1;
PID sLeftPID(&sInput, &sOutputLeft, &sSetpoint, sKp, sKi, sKd, DIRECT);
PID sRightPID(&sInput, &sOutputRight, &sSetpoint, sKp, sKi, sKd, REVERSE);



//=====================================================================================

// Comms
// length of data packet. 2*motor speed + steering position
const int messageLength = 4;
// Array for the received message
int received[messageLength];
// Flag to signal when a message has been received
bool commandReceived = false;

// VAriables that deal with checking the time since the last serial message
// If we lose connection, we should stop
unsigned long lastMillis;
unsigned long currentMillis;
const unsigned long period = 250;  //the value is a number of milliseconds, ie 2s

// we need to know if there is an error state from anywhere....
boolean error = false;
bool enable = false;
// Somewhere to store variables

void setup() {
  pinMode(S_FB, INPUT);
  pinMode(S_R_EN, OUTPUT);
  pinMode(S_L_EN, OUTPUT);
  pinMode(S_R_PWM, OUTPUT);
  pinMode(S_L_PWM, OUTPUT);

  pinMode(T_FB, INPUT);
  pinMode(T_R_EN, OUTPUT);
  pinMode(T_L_EN, OUTPUT);
  pinMode(T_L_PWM, OUTPUT);
  pinMode(T_R_PWM, OUTPUT);

  sInput = analogRead(S_FB);
  sPositionAvg.begin();
  sSetpoint = sCentre;

  tInput = analogRead(T_FB);
  tPositionAvg.begin();
  tSetpoint = tCentre;

  tController.Stop();
  tController.Disable();
  sController.Stop();
  sController.Disable();

  // Setup serial connection, announce device and initiate dacs
  Serial.begin(115200);
  delay(100);
  //Serial.write(49);                 // Announce the controller to the PC with '1'
  //Serial.write(10);
  //Serial.write(13);
  //turn the PID on
  sLeftPID.SetMode(AUTOMATIC);
  sRightPID.SetMode(AUTOMATIC);
  tLeftPID.SetMode(AUTOMATIC);
  tRightPID.SetMode(AUTOMATIC);
  //Serial.write(50);                 // Announce the setup complete with '2'
  lastMillis = millis();            // Record the time for connection checking
}

void loop() {
  checkConnection();
  sLeftPID.Compute();
  sRightPID.Compute();
  tLeftPID.Compute();
  tRightPID.Compute();
  if (commandReceived) {
    processSerialCommand();
  }
  if (!enable) {
    //digitalWrite(BRAKE_PIN, enable);
    tController.Stop();
    tController.Disable();
    sController.Stop();
    sController.Disable();
  }
  else {
    tController.Enable();
    sController.Enable();

    //Actuator
    sSetpoint = map(received[3], 0, 255, sMax, sMin);
    sPosition = analogRead(S_FB);
    sInput = sPositionAvg.reading(sPosition);
    if (sInput <= sSetpoint + sDeadband && sInput >= sSetpoint - sDeadband) {
      //actuatorController.Stop();
      sController.Disable();
    }
    else if (sInput > sSetpoint + sDeadband) {
      sController.Enable();
      sController.TurnRight(sOutputRight);

    }
    else if (sInput < sSetpoint - sDeadband) {
      sController.Enable();
      
      sController.TurnLeft(sOutputLeft);
    }

    // tool

    tSetpoint = map(received[2], 0, 255, tMin, tMax);
    tPosition = analogRead(T_FB);
    tInput = tPositionAvg.reading(tPosition);
    if (tInput <= tSetpoint + tDeadband && tInput >= tSetpoint - tDeadband) {
      tController.Disable();
    }
    else if (tInput > tSetpoint + tDeadband) {
      tController.Enable();
      tController.TurnRight(tOutputRight);

    }
    else if (tInput < tSetpoint - tDeadband) {
      tController.Enable();
      tController.TurnLeft(tOutputLeft);

    }

    //delay(10);
  }
}

// ======================== FUNCTIONS =====================================
// function to check the time since the last serial command
void checkConnection() {
  currentMillis = millis();
  if (currentMillis - lastMillis >= period) {
    enable = false;
    error = true;
  }
}

// When new characters are received, the serialEvent interrupt triggers this function
void serialEvent()   {
  // Read the Serial Buffer
  for (int i = 0; i < messageLength; i++) {
    received[i] = Serial.read();
    delay(1);
  }
  // Change the flag because a command has been received
  commandReceived = true;

  // Record the time
  lastMillis = millis();
}

// Function to split up the received serial command and set the appropriate variables
void processSerialCommand() {
  error = bool(received[0]);                                  // Error Flag
  enable = bool(received[1]);                          // Motor Enable Flag
  // Motor Directions
  tSetpoint = int(received[2]);
  sSetpoint = int(received[3]);

  for (int i = 0; i < messageLength; i++) {
    Serial.write(received[i]);
  }
  //Serial.write(13);
  commandReceived = false;
}
