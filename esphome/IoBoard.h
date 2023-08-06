
#include "esphome.h"

#define MinUpdate   60000
#define MsgTxPeriod  1000
#define MsgRxMax    60000

#define get_iob(constructor) static_cast<IoBoard *>(constructor.get_component(0))

#define iobGetSwitch(iob, id) get_iob(iob)->getSwitch(id)

class IoBoardSwitchHost {

   public:

      virtual void updateSwitch(void) {};
};

class IoBoardSwitch : public Switch {
   public:

      bool state;

      IoBoardSwitchHost * ioBoard = {nullptr};

      IoBoardSwitch(IoBoardSwitchHost *ioBoard) {
         this->state = false;
         this->ioBoard = ioBoard;
      }

      void write_state(bool state) {
         this->state = state;
         this->ioBoard->updateSwitch();
         publish_state(this->state);
      }
};

class IoBoard : public Component, public IoBoardSwitchHost {
   public:

      IoBoardSwitch * ioSwitch[12] = {nullptr, nullptr, nullptr, nullptr, nullptr, nullptr,
                                      nullptr, nullptr, nullptr, nullptr, nullptr, nullptr};

      char rxBuffer[50];
      unsigned int rxCount;
      unsigned long lastMsgTx;
      unsigned long lastMsgRx;

      void setup() override {
         Serial.begin(9600);
         rxCount = 0;
         lastMsgTx = millis();
         lastMsgRx = millis();
      }

      void sendMsg() {
         unsigned int outputValues[12];
         unsigned int x;
         char txBuffer[50];

         // Update relay states and check for needed updates
         for (x = 0; x < 12; x++) {
           if ( ioSwitch[x] != NULL ) {
              if ( ioSwitch[x]->state ) outputValues[x] = 100;
              else outputValues[x] = 0;
           }
           else outputValues[x] = 0;
         }

         sprintf(txBuffer,"STATE %i %i %i %i %i %i %i %i %i %i %i %i\n",
                          outputValues[0], outputValues[1], outputValues[2],
                          outputValues[3], outputValues[4], outputValues[5],
                          outputValues[6], outputValues[7], outputValues[8],
                          outputValues[9], outputValues[10], outputValues[11]);

         Serial.write(txBuffer);
         lastMsgTx = millis();
      }

      void loop() override {
         unsigned int x;
         unsigned int statusValues[12];
         unsigned int tempValue;
         int tmp;
         char mark[10];
         char c;

         // Get serial data
         while (Serial.available()) {
            if ( rxCount == 50 ) rxCount = 0;

            c = Serial.read();
            rxBuffer[rxCount++] = c;
            rxBuffer[rxCount] = '\0';
         }

         // Check for incoming message
         if ( rxCount > 7 && rxBuffer[rxCount-1] == '\n' ) {

            // Parse string
            tmp = sscanf(rxBuffer,"%s %i %i %i %i %i %i %i %i %i %i %i %i",
                         mark, &(statusValues[0]), &(statusValues[1]), &(statusValues[2]),
                         &(statusValues[3]), &(statusValues[4]), &(statusValues[5]),
                         &(statusValues[6]), &(statusValues[7]), &(statusValues[8]),
                         &(statusValues[9]), &(statusValues[10]), &(statusValues[11]));

            // Check marker
            if ( tmp == 13 && strcmp(mark,"STATUS") == 0 ) lastMsgRx = millis();
            rxCount = 0;
         }

        // Min time between messages
        if (( millis() - lastMsgTx ) > MsgTxPeriod) sendMsg();
      }

      void updateSwitch() override {
         this->sendMsg();
      }

      IoBoardSwitch * getSwitch(unsigned int x) {
         if ( x > 11 ) return NULL;

         if ( ioSwitch[x] == NULL ) ioSwitch[x] = new IoBoardSwitch(this);
         return ioSwitch[x];
      }
};

