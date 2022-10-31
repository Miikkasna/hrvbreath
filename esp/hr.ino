const byte interruptPin = 2;
volatile byte beat = false;
unsigned long last_time = 0;
unsigned int interval = 0;

void detect() {
  beat = true;
}

void setup() {
  Serial.begin(9600);
  pinMode(interruptPin, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(interruptPin), detect, RISING);
  last_time = millis();
}

void loop() {
  if(beat){
    interval = int(millis() - last_time);
    last_time = millis();
    Serial.println(interval);
    beat = false;
  }
}
