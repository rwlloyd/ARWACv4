// ARWAC v4 - Actuator Firmware
// Rob Lloyd - 02/2021
// University of Lincoln

#include <PID_v1.h>                     // https://playground.arduino.cc/Code/PIDLibrary/
#include <movingAvg.h>                  // https://github.com/JChristensen/movingAvg

const uint8_t sPWM = 9;
const uint8_t sDIR = 10;
const uint8_t sFB = A0;

const uint8_t tPWM = 11;
const uint8_t tDIR = 12;
const uint8_t tFB = A1;

int sPos;
int tPos;
movingAvg sPosAvg(4);
int sActuatorCentre = 263; // !!!!!!!!!!!!    This will need to be calibrated  !!!!!!!!!!!!!
int sActuatorTravel = 90;
int sActuatorDeadband = 1; //Stops the actuator hunting quite so much
int sActuatorMax = sActuatorCentre - sActuatorTravel;
int sActuatorMin = sActuatorCentre + sActuatorTravel;
int vel = 200;

// PID Controller for the steering actuator
//Define Variables we'll be connecting to
double sActuatorSetpoint, sActuatorInput, sActuatorOutputLeft, sActuatorOutputRight;

//Specify the links and initial tuning parameters
double Kp = 3, Ki = 0.1, Kd = 0.1;
PID leftPID(&sActuatorInput, &sActuatorOutputLeft, &sActuatorSetpoint, Kp, Ki, Kd, DIRECT);
PID rightPID(&sActuatorInput, &sActuatorOutputRight, &sActuatorSetpoint, Kp, Ki, Kd, REVERSE);

// Comms
// length of data packet. 2*motor speed + steering position
const int messageLength = 3;
// Array for the received message
int received[messageLength];
// Flag to signal when a message has been received
bool commandReceived = false;

// VAriables that deal with checking the time since the last serial message
// If we lose connection, we should stop
unsigned long lastMillis;
unsigned long currentMillis;
const unsigned long period = 250;  //the value is a number of milliseconds, ie 2s

bool enable = false;

void setup() {
  pinMode(sFB, INPUT);
  pinMode(sPWM, OUTPUT);
  pinMode(sDIR, OUTPUT);

  sActuatorInput = analogRead(sFB);
  sPosAvg.begin();
  sActuatorSetpoint = sActuatorCentre;

  // Setup serial connection, announce device and initiate dacs
  Serial.begin(115200);
  delay(100);
  //Serial.write(49);                 // Announce the controller to the PC with '1'
  //Serial.write(10);
  //Serial.write(13);
  //turn the PID on
  leftPID.SetMode(AUTOMATIC);
  rightPID.SetMode(AUTOMATIC);
  //Serial.write(50);                 // Announce the setup complete with '2'
  lastMillis = millis();            // Record the time for connection checking
}

// ======================== FUNCTIONS =====================================
// function to check the time since the last serial command
void checkConnection() {
  currentMillis = millis();
  if (currentMillis - lastMillis >= period) {
    enable = false;
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
  enable = bool(received[0]);                                  // enable
  sPos = bool(received[1]);                          // desired steer -100 -> +100
  // Motor Directions
  tPos = int(received[2]);
  // parrot back
  for (int i = 0; i < messageLength; i++) {
    Serial.write(received[i]);
  }
  //Serial.write(13);
  commandReceived = false;
}

void loop() {
  checkConnection();
  leftPID.Compute();
  rightPID.Compute();
  if (commandReceived) {
    processSerialCommand();
  }
  if (!enable) {
    digitalWrite(sPWM, 0);
  }
  else {

    //Actuator
    sActuatorSetpoint = map(received[1], -100, 100, sActuatorMax, sActuatorMin);
    sPos = analogRead(sFB);
    sActuatorInput = sPosAvg.reading(sPos);
    if (sActuatorInput <= sActuatorSetpoint + sActuatorDeadband && sActuatorInput >= sActuatorSetpoint - sActuatorDeadband) {
      digitalWrite(sPWM, 0);
    }
    else if (sActuatorInput > sActuatorSetpoint + sActuatorDeadband) {
      digitalWrite(sDIR, HIGH);
      digitalWrite(sPWM, sActuatorOutputRight);
    }
    else if (sActuatorInput < sActuatorSetpoint - sActuatorDeadband) {
      digitalWrite(sDIR, LOW);
      digitalWrite(sPWM, sActuatorOutputLeft);
    }
  }
}
