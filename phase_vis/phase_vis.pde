/**
 * oscP5broadcastClient by andreas schlegel
 * an osc broadcast client.
 * an example for broadcast server is located in the oscP5broadcaster exmaple.
 * oscP5 website at http://www.sojamo.de/oscP5
 */

import oscP5.*;
import netP5.*;


OscP5 oscP5;

/* a NetAddress contains the ip address and port number of a remote location in the network. */
NetAddress myBroadcastLocation; 

float pi = 3.14159265358979323846;

float xo; 
float yo; 
float angle = 0;
float pos = 100;

void setup() {
  size(400,800);
  xo = width/2; 
  yo = height/2;
  frameRate(25);
  
  /* create a new instance of oscP5. 
   * 12000 is the port number you are listening for incoming osc messages.
   */
  oscP5 = new OscP5(this,7111);
  
  /* create a new NetAddress. a NetAddress is used when sending osc messages
   * with the oscP5.send method.
   */
  
  /* the address of the osc broadcast server */
  //smyBroadcastLocation = new NetAddress("127.0.0.1",32000);
}


void draw() {
  background(255, 255, 255);
  //color(0,54,0,23);
  stroke(198);
  ellipse(xo, yo+200, 188, 188);
  line(xo+(94*cos(angle*2)),yo+200+94*sin(angle*2),xo,yo+200-pos);
  line(xo,yo+200,xo,yo+200-pos);
  translate(xo, yo+200); 
  
  rotate(angle); 
  strokeWeight(4); 
  float radSec = angle;
  pushMatrix(); 
  rotate(angle); 
  line(0, 0, 94, 0);
  popMatrix();
}

/* incoming osc message are forwarded to the oscEvent method. */
void oscEvent(OscMessage theOscMessage) {
  /* get and print the address pattern and the typetag of the received OscMessage */
  //println("### received an osc message with addrpattern "+theOscMessage.addrPattern()+" and typetag "+theOscMessage.typetag());
  //println("### received an osc message with addrpattern "+theOscMessage.addrPattern()+" and typetag "+theOscMessage.typetag());
  //println(theOscMessage.addrPattern());
  if(theOscMessage.checkAddrPattern("/phase")==true){
    angle = theOscMessage.get(0).floatValue()/2;
    //println(theOscMessage.get(0).floatValue()/(2*pi));
  }
  if(theOscMessage.checkAddrPattern("/position")==true){
    pos = theOscMessage.get(0).floatValue();
    //println(theOscMessage.get(0).floatValue()/(2*pi));
  }
  //theOscMessage.print();
}