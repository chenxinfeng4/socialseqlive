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
    pinWriting(pot);
  }
  digitalWrite(PinNum, LOW);                               //when time out, auto close the PinNum.
  pinWriting(LOW);
}


void pinWriting(boolean now_status)
{
  static boolean pre_status = 0;
  static unsigned long t_raise = 0;
  if(pre_status == LOW && now_status == HIGH) {
    t_raise = millis();
  }
  else if(pre_status == HIGH && now_status == LOW) {
    sendmsg("OUT", 1, t_raise, millis());
  }
  pre_status = now_status;
}


void sendmsg(char prefix[], int pin, unsigned long t_raise, unsigned long t_decline)
{
  char buf[40], temp[11];  //long is 10 char + '\0';
  unsigned long AppBeginTime = time_bg;
  buf[0] = '\0';
  strcat(buf, prefix);
  strcat(buf,itoa(pin, temp,10));
  strcat(buf, ":");
  strcat(buf, ultoa(t_raise - AppBeginTime, temp, 10));
  strcat(buf, " ");
  strcat(buf, ultoa(t_decline - t_raise, temp, 10));
  strcat(buf, "\n");
  Serial.print(buf);
}


void loop() {
  // read the serial input
  while(Serial.available()){
    char act_code = Serial.read();
    do_action(act_code);
  }
}
