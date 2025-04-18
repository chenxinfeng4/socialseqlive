const int PinNum = 6;             // the number of the LED pin
const float duration = 1;         // time for running, unit = sec.
const float Hz = 50;              // frequency, unit = Hz.
const float Duty = 0.25;          // duty, unit = 0~1.
unsigned long time_bg = 0;


void setup() {
  // initialize serial communication at 9600 bits per second
  Serial.begin(9600);
  Serial.println("Hello from SeqLive-Arduino");

  time_bg = millis();
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(PinNum, OUTPUT);
  digitalWrite(PinNum, LOW);
}


void do_action(char act_code) {
  // doing something
  if(act_code == 'a'){
    Serial.println("Hello from SeqLive-Arduino");
  }
  else if(act_code == 'b'){
    Serial.println("Doing.");
    cpp_HzDuty(PinNum, duration, Hz, Duty);
  }
  else if(act_code == '\r' || act_code == '\n'){
    ;
  }
  else{
    Serial.println("Doing nothing.");
  }
}


void cpp_HzDuty(int PinNum, float duration, float Hz, float Duty)
{
  const unsigned long utime = duration * 1000000;          //time for running, unit = (u)s.
  const unsigned long ubgtime = micros();                  //begin time, unit = us.
  const unsigned long uT_fast = 1 / Hz * 1000000;          //fast cycle time, unit = us.
  const unsigned long uT_div_fast = uT_fast * Duty;        //fast cycle watershed, unit = us.
  unsigned long ut;                                        //ut: time now, unit = us.
  boolean pot;                                             //(pot)ential, which will write to PinNum.
  while ((ut = micros() - ubgtime) < utime){
    if(Serial.available()){
      char act_code = Serial.read();
    }
    pot = (ut % uT_fast) < uT_div_fast;
    digitalWrite(PinNum, pot);
  }
  digitalWrite(PinNum, LOW);                               //when time out, auto close the PinNum.
}


void loop() {
  // read the serial input
  while(Serial.available()){
    char act_code = Serial.read();
    do_action(act_code);
  }
}
