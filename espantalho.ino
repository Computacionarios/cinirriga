#define sensor_PIR 2
#define led 3
#define buzzer 4
#define button 5

bool sistema_ligado = true;
bool estado_sensor = false;    
bool movimento_detectado = false;  
bool estado_anterior = HIGH;

void setup() {
  pinMode(sensor_PIR, INPUT);              //declara sensor como entrada, recebe o sinal
  pinMode(led, OUTPUT);                    //declara led como saída, emiti luz se receber o sinal
  pinMode(buzzer, OUTPUT);
  pinMode(button, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop() 
{
  estado_sensor = digitalRead(sensor_PIR);                          //recebe a informação
  int estado_atual = digitalRead(button);
  if (estado_atual == LOW && estado_anterior == HIGH)
  {
  sistema_ligado = !sistema_ligado;
  delay(200);  
  } 
 estado_anterior = estado_atual;
  
 if (sistema_ligado){ 
  if (estado_sensor){
    
    if (!movimento_detectado){                                       //verifica o estado do sensor, se detectar movimento o led acende

      digitalWrite(led, HIGH);
      digitalWrite(buzzer, HIGH);
      Serial.println("Movimento detectado");
      
      movimento_detectado = true;
    }
  } 
  else{
    if (movimento_detectado){                                        //senão detecetar o led apaga

      digitalWrite(led, LOW);
      digitalWrite(buzzer, LOW);
      Serial.println("Sem Movimento");

      movimento_detectado = false;  
    }
  }
 }
  else
  {
  digitalWrite(led, LOW);
  digitalWrite(buzzer, LOW);  
  movimento_detectado = false;
  }
  delay(50);
}
