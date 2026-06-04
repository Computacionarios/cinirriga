//Inclui a biblioteca do Servo
#include <Servo.h>

Servo meuServo; //Define meuServo como a forma de chamar as funções do Servo.h
int pino_mov = 8; //Define o pino de movimento do servor motor
int angulo_servo = 0; //Variável que detem o angulo de giro da plataforma
int pino_rele = 4; //Define o pino que controla o relé

void setup()
{
 meuServo.attach(pino_mov); //Atribui ao pino a função e receber os ângulos e rotação do servor
  pinMode(pino_rele, OUTPUT); //Define o pino do rele como saida
}

void loop()
{
  meuServo.write(0); //Define a posição inicial do Servor motor
  delay(2000);
  
  angulo_servo = 60; //Diz que o ângulo de rotação deve ser 60 graus
  rega(angulo_servo); //Executa a função rega
  
  angulo_servo = 120;
  rega(angulo_servo);
  
  angulo_servo = 180;
  rega(angulo_servo);

}

void rega(int angulo) {
  meuServo.write(angulo); //Gira o servo no ângulo corresponente
  delay(2000); //Espera dois segundos
  digitalWrite(4, HIGH); //Liga o reelé para ligar a válvula
  delay(8000); //Rega por 8 segundos
  digitalWrite(4, LOW); //Desliga a válvula
  delay(1000); //Espera mais 1 segundo
  
}
