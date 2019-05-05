#include "config.h"
#include "Arduino.h"
#include "debouncer.cpp"
#include "DigiCDC.h"

Debouncer btn_debounce( BTN_DEBOUNCE_MS );

char cdc_input;
char btn_state;
boolean led_state;

void setup() {
  pinMode( INPUT_PULLUP, PIN_BTN );
  pinMode( OUTPUT, PIN_LED );
  SerialUSB.begin();
}

void loop() {

  // read button and if pressed print . to serial
  btn_state = digitalRead( PIN_BTN );
  if ( btn_state==0 && btn_debounce.check() ){
    SerialUSB.print( "." );
  }

  // read serial for led state
  if ( SerialUSB.available() ) {
    cdc_input = SerialUSB.read();
    // 0 = led off
    if ( cdc_input == 48 ){
      SerialUSB.print("0");
      digitalWrite( PIN_LED, 0 );
    }
    // 1 = led on
    if ( cdc_input == 49 ) {
      SerialUSB.print("1");
      digitalWrite( PIN_LED, 1 );
    }
    // 2 = led toggle
    if ( cdc_input == 50 ){
      led_state = digitalRead( PIN_LED );
      if (led_state){
        SerialUSB.print("0");
      } else {
        SerialUSB.print("1");
      }
      digitalWrite( PIN_LED, !led_state );
    }
    // 9 = get identification byte, returns 'r' or byte 114
    if ( cdc_input == 57 ){
      SerialUSB.print("r");
    }
  }

}
