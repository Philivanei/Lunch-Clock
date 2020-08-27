#include "RTClib.h"

// Relais PINS
#define RELAISPOWER 5
#define RELAISB 6
#define RELAISC 7
// Button PINS
#define BROTZEITBUTTON 4

RTC_DS3231 rtc;
// One dimension to store the day count and another one to store the name of the specific day
char daysOfTheWeek[7][12] = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};

bool powerTurn = false;
bool evenNumber = true;
byte lastMinute;
byte brotzeitTime = 1;
int brotzeitTimeCount = 1;


void setup () {
  Serial.begin(9600);
  initializeRTC();
  initializePins();
  
  lastMinute = getMinute();
}

void loop () {
  
  Serial.print(getHour());
  Serial.print(":");
  Serial.print(getMinute());
  Serial.print(":");
  Serial.print(getSecond());
  Serial.println("\n");
  
  checkButton();
  clockLogic();
}


void clockLogic(){
    switch(brotzeitTime){
    
    case 1:
    //Serial.println(brotzeitTimeCount);
    if(lastMinute != getMinute()){
      moveClockHands();
      lastMinute = getMinute();
    }
    break;
    
    case 2:
    //Serial.println(brotzeitTimeCount);
    if(lastMinute != getMinute()){
      if((brotzeitTimeCount % 2) == 0){
        brotzeitTimeCount = brotzeitTimeCount + 1;
        lastMinute = getMinute();
      }else{
        brotzeitTimeCount = brotzeitTimeCount + 1;
        moveClockHands();
        lastMinute = getMinute();
      }
    }
    break;
    
    case 3:
    //Serial.println(brotzeitTimeCount);
    if((brotzeitTimeCount % 2) == 0 && evenNumber){
      if(lastMinute != getMinute()){
        lastMinute = getMinute();
        evenNumber = false;
        brotzeitTimeCount = brotzeitTimeCount - 1;
        moveClockHands();
      }
    } else if(lastMinute != getMinute()){
      lastMinute = getMinute();
      moveClockHands();
      delay(200);
      moveClockHands();
      brotzeitTimeCount = brotzeitTimeCount - 2;
    }
    
    if(brotzeitTimeCount <= 1){
      brotzeitTimeCount = 1;
      brotzeitTime = 1;
      evenNumber = true;
    }
    break;
    
    default:
    if(lastMinute != getMinute()){
      moveClockHands();
      lastMinute = getMinute();
    }
    break;
  }
}


void moveClockHands(){
  if(powerTurn){
      digitalWrite(RELAISB,LOW);
      digitalWrite(RELAISC,LOW);
      delay(50);
      digitalWrite(RELAISPOWER,HIGH);
      delay(700);
      digitalWrite(RELAISPOWER,LOW);
      lastMinute = getMinute();
      powerTurn = false;
  }else{
      digitalWrite(RELAISB,HIGH);
      digitalWrite(RELAISC,HIGH);
      delay(50);
      digitalWrite(RELAISPOWER,HIGH);
      delay(700);
      digitalWrite(RELAISPOWER,LOW);
      lastMinute = getMinute();
      powerTurn = true;
    }
}


void checkButton(){
  if(digitalRead(BROTZEITBUTTON) == HIGH){
    delay(2000);
    brotzeitTime = brotzeitTime + 1;
  }
}


byte getHour(){
  return rtc.now().hour();
}
byte getMinute(){
  return rtc.now().minute();
}
byte getSecond(){
  return rtc.now().second();
}


void initializePins(){
  pinMode(RELAISPOWER,OUTPUT);
  pinMode(RELAISB,OUTPUT);
  pinMode(RELAISC,OUTPUT);
  pinMode(BROTZEITBUTTON,INPUT);
  digitalWrite(RELAISPOWER,LOW);
  digitalWrite(RELAISB,HIGH);
  digitalWrite(RELAISC,HIGH);
}


void initializeRTC(){
  if (! rtc.begin()) {
    Serial.println("Couldn't find RTC");
    while (1);
  }
  
  if (rtc.lostPower()) {
    Serial.println("RTC lost power, lets set the time!");
    // following line sets the RTC to the date & time this sketch was compiled
    rtc.adjust(DateTime(F(__DATE__), F(__TIME__)));
    // This line sets the RTC with an explicit date & time, for example to set
    // January 21, 2014 at 3am you would call:
    // rtc.adjust(DateTime(2014, 1, 21, 3, 0, 0));
  }
}
