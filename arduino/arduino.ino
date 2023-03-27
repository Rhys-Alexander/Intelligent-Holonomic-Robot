// NOTICE
// To be clear,
// this is my colleage's arduino code.
// Please don't judge me one this code.

double ki = 1.65;
double kp = 4.7;

float currentSpeed[3];
float targetSpeed[3];
float tempSpeed[3];
float speedError[3];
float linearErrorMagnitude;
float xCorrection, yCorrection;

const float maxAcc = 250.0 / 1000.0;
const float maxOmegaAcc = 250.0 / 1000.0;

char nextChar;
String dataIn;
double params[6];

typedef struct motorInfo {
  int pinA;
  int pinB;
  int pinForward;
  int pinBack;
  int distance;
  int lastDistance;
  double speed;
  double targetSpeed;
  int pwmChannelForward;
  int pwmChannelBack;
  int pe;
  int ie;
  int error;
  double lastPulsePeriod;
  int lastPulseTime;
} motorInfo;

motorInfo motor1;
motorInfo motor2;
motorInfo motor3;

int splitToDoubles(String toSplit, char symbol, double *doubles) {
  int i = 0;
  int splits = 0;
  String temp;
  while (i < toSplit.length()) {


    if (toSplit[i] == symbol) {
      doubles[splits] = temp.toFloat();
      temp = "";
      splits++;
    } else {
      temp = temp + String(toSplit[i]);
    }
    i++;
  }
  doubles[splits] = temp.toFloat();
  return splits;
}

void IRAM_ATTR encoder1A() {
  if (digitalRead(motor1.pinA) ^ digitalRead(motor1.pinB)) {
    motor1.distance--;
    motor1.lastPulsePeriod = -(micros() - motor1.lastPulseTime);
  } else {
    motor1.distance++;
    motor1.lastPulsePeriod = (micros() - motor1.lastPulseTime);
  }
  motor1.lastPulseTime = micros();
}

void IRAM_ATTR encoder1B() {
  if (digitalRead(motor1.pinB) ^ digitalRead(motor1.pinA)) {
    motor1.distance++;
    motor1.lastPulsePeriod = (micros() - motor1.lastPulseTime);
  } else {
    motor1.distance--;
    motor1.lastPulsePeriod = -(micros() - motor1.lastPulseTime);
  }

  motor1.lastPulseTime = micros();
}

void IRAM_ATTR encoder2A() {
  if (digitalRead(motor2.pinA) ^ digitalRead(motor2.pinB)) {
    motor2.distance--;
    motor2.lastPulsePeriod = -(micros() - motor2.lastPulseTime);
  } else {
    motor2.distance++;
    motor2.lastPulsePeriod = (micros() - motor2.lastPulseTime);
  }
  motor2.lastPulseTime = micros();
}

void IRAM_ATTR encoder2B() {
  if (digitalRead(motor2.pinB) ^ digitalRead(motor2.pinA)) {
    motor2.distance++;
    motor2.lastPulsePeriod = (micros() - motor2.lastPulseTime);
  } else {
    motor2.distance--;
    motor2.lastPulsePeriod = -(micros() - motor2.lastPulseTime);
  }

  motor2.lastPulseTime = micros();
}

void IRAM_ATTR encoder3A() {
  if (digitalRead(motor3.pinA) ^ digitalRead(motor3.pinB)) {
    motor3.distance--;
    motor3.lastPulsePeriod = -(micros() - motor3.lastPulseTime);
  } else {
    motor3.distance++;
    motor3.lastPulsePeriod = (micros() - motor3.lastPulseTime);
  }
  motor3.lastPulseTime = micros();
}

void IRAM_ATTR encoder3B() {
  if (digitalRead(motor3.pinB) ^ digitalRead(motor3.pinA)) {
    motor3.distance++;
    motor3.lastPulsePeriod = (micros() - motor3.lastPulseTime);
  } else {
    motor3.distance--;
    motor3.lastPulsePeriod = -(micros() - motor3.lastPulseTime);
  }

  motor3.lastPulseTime = micros();
}

void IRAM_ATTR speedCalculation(motorInfo *motor) {
  motor->speed = motor->distance - motor->lastDistance;
  motor->lastDistance = motor->distance;

  double sussySpeed = 100000 / (motor->lastPulsePeriod + 1);

  //motor->pe=kp*(motor->targetSpeed-sussySpeed);
  //motor->ie+=ki*(motor->targetSpeed-sussySpeed);

  motor->pe = kp * (motor->targetSpeed - motor->speed);
  motor->ie += ki * (motor->targetSpeed - motor->speed);

  motor->ie = constrain(motor->ie, -1000, 1000);
  motor->error = constrain((motor->pe + motor->ie), -1000, 1000);
  /*
  if (motor->error>0){
    ledcWrite(motor->pwmChannelBack, 0);
    ledcWrite(motor->pwmChannelForward, motor->error);
  }
  else{
    motor->error *=-1;
    ledcWrite(motor->pwmChannelForward, 0);
    ledcWrite(motor->pwmChannelBack, motor->error);
  } 
  */

  if (motor->targetSpeed != 0) {
    if (motor->error > 0) {
      ledcWrite(motor->pwmChannelForward, 1024);
      ledcWrite(motor->pwmChannelBack, 1000 - motor->error);
    } else {
      motor->error *= -1;
      ledcWrite(motor->pwmChannelBack, 1024);
      ledcWrite(motor->pwmChannelForward, 1000 - motor->error);
    }
  } else {
    ledcWrite(motor->pwmChannelBack, 1024);
    ledcWrite(motor->pwmChannelForward, 1024);
  }
}

void motorSetup(motorInfo *motor, int _pinA, int _pinB, int _pinForward, int _pinBack, int _pwmChannelForward, int _pwmChannelBack) {
  motor->pinA = _pinA;
  motor->pinB = _pinB;
  motor->pinForward = _pinForward;
  motor->pinBack = _pinBack;
  motor->pwmChannelForward = _pwmChannelForward;
  motor->pwmChannelBack = _pwmChannelBack;
  ledcSetup(motor->pwmChannelForward, 60, 10);
  ledcSetup(motor->pwmChannelBack, 60, 10);
  ledcAttachPin(motor->pinForward, motor->pwmChannelForward);
  ledcAttachPin(motor->pinBack, motor->pwmChannelBack);
}

void IRAM_ATTR updateSpeed() {
  speedCalculation(&motor1);
  speedCalculation(&motor2);
  speedCalculation(&motor3);
}

void setup() {
  Serial.begin(500000);
  Serial.println("hi");

  hw_timer_t *speedTimer = NULL;                         //Declare timer, but don't initialize it yet
  speedTimer = timerBegin(3, 80, true);                  //Set up a timer with a prescaler of 80 which counts up once per microsecond
  timerAttachInterrupt(speedTimer, &updateSpeed, true);  //Run speed calculation interrupt each time it overflows
  timerAlarmWrite(speedTimer, 40000, true);              //Set timer overflow
  timerAlarmEnable(speedTimer);                          //Enable configured timer



  //Motor mess
  motorSetup(&motor3, 34, 35, 23, 22, 1, 2);
  motorSetup(&motor1, 32, 33, 19, 18, 3, 4);
  motorSetup(&motor2, 39, 36, 16, 17, 5, 6);

  pinMode(motor1.pinA, INPUT);
  pinMode(motor1.pinB, INPUT);
  attachInterrupt(motor1.pinA, encoder1A, CHANGE);
  attachInterrupt(motor1.pinB, encoder1B, CHANGE);


  pinMode(motor2.pinA, INPUT);
  pinMode(motor2.pinB, INPUT);
  attachInterrupt(motor2.pinA, encoder2A, CHANGE);
  attachInterrupt(motor2.pinB, encoder2B, CHANGE);

  pinMode(motor3.pinA, INPUT);
  pinMode(motor3.pinB, INPUT);
  attachInterrupt(motor3.pinA, encoder3A, CHANGE);
  attachInterrupt(motor3.pinB, encoder3B, CHANGE);

}

int lastTrigger = 10000;
int period = 2000;
bool flag;
int lastValidSignal;

float angle, turn, speed;

void loop() {
  delay(1);

  while (Serial.available()) {
    nextChar = Serial.read();
    if (nextChar == 10) {
      splitToDoubles(dataIn, ',', params);
      lastValidSignal = millis();
      //for (int i = 0; i < 6; i++) {
      //  Serial.print(params[i]);
      //  Serial.print("\t");
      //}
     // Serial.println();
      dataIn = "";



      break;
    } 
    else {
      dataIn += nextChar;
    }
  }

  if (millis()-lastValidSignal<3000){
  targetSpeed[0] = params[0];
  targetSpeed[1] = params[1];
  targetSpeed[2] = params[2];
  }
  else{
  targetSpeed[0] = 0;
  targetSpeed[1] = 0;
  targetSpeed[2] = 0;
  }


  currentSpeed[0] = motor3.speed / (2 * sin(PI / 3)) - motor2.speed / (2 * sin(PI / 3));
  currentSpeed[1] = -(2 * motor1.speed / 3) + motor2.speed / 3 + motor3.speed / 3;
  currentSpeed[2] = (motor3.speed + motor1.speed + motor2.speed) / 3;

  speedError[0] = targetSpeed[0] - tempSpeed[0];
  speedError[1] = targetSpeed[1] - tempSpeed[1];
  speedError[2] = targetSpeed[2] - tempSpeed[2];

  linearErrorMagnitude = sqrt(speedError[0] * speedError[0] + speedError[1] * speedError[1]);
  if (linearErrorMagnitude !=0){
    xCorrection = maxAcc * speedError[0] / linearErrorMagnitude;
    yCorrection = maxAcc * speedError[1] / linearErrorMagnitude;
  }
  else{
    xCorrection = 0;
    yCorrection = 0;
  }


  //Serial.println(String(xCorrection) + "\t" + String(yCorrection) + "\t" + String(sqrt(xCorrection * xCorrection + yCorrection * yCorrection)));

  if (abs(speedError[0]) > xCorrection) {
    tempSpeed[0] += xCorrection;
  } else {
    tempSpeed[0] = targetSpeed[0];
  }

  if (abs(speedError[1]) > yCorrection) {
    tempSpeed[1] += yCorrection;
  } else {
    tempSpeed[1] = targetSpeed[1];
  }

  motor1.targetSpeed = targetSpeed[2] - tempSpeed[0] * cos(0) - tempSpeed[1] * sin(0);
  motor2.targetSpeed = targetSpeed[2] - tempSpeed[0] * cos(2 * PI / 3) - tempSpeed[1] * sin(2 * PI / 3);
  motor3.targetSpeed = targetSpeed[2] - tempSpeed[0] * cos(4 * PI / 3) - tempSpeed[1] * sin(4 * PI / 3);



  //Serial.println(String(tempSpeed[0]) + "\t" + String(tempSpeed[1]));
}
