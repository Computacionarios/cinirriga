const int pinoSensor = A0; //pino do sensor de umidade
const int pinoRele = 8; //pino do rele
const int valAr = 0; // valor mínimo de umidade (no ar)
const int valAgua = 876; // valor máximo de umidade (imerso em água)

int umidade = 0; //valor da umidade base
int porcentagem = 0; //porcentagem de umidade no solo (calcula depois)
const int limiteUmidade = 30; //num minimo de umidade, menos que isso tá seco

void setup() {
  pinMode(pinoRele, OUTPUT); // rele é saída
  digitalWrite(pinoRele, LOW); // inicia o rele com desligado
  Serial.begin(9600); // serial begin sem segredo
}

void loop() {
  umidade= analogRead(pinoSensor); // lê o valor dito pelo sensor de umidade
  porcentagem = map(umidade, valAr, valAgua, 0, 100); // transforma pra porcentagem
  porcentagem = constrain(porcentagem, 0, 100); // USA CONSTRAIN PRA MANTER UM LIMITE DE UMIDADE, TANTO PRA CIMA COMO PRA BAIXO
  
  // printando a umidade para acompanhar
  Serial.print("Umidade medida: ");
  Serial.print(porcentagem);
  Serial.println("%.");
  
  // vê se a porcentagem está abaixo do limite (vê se tá seco)
  if (porcentagem < limiteUmidade) {
    Serial.println("Alerta: Solo Seco! Ligando a bomba...");
    
    digitalWrite(pinoRele, HIGH); // ativa o relé (liga a bomba) por 3 segundos
    delay(3000);
    
    digitalWrite(pinoRele, LOW);  // desativa o relé (desliga a bomba)
    Serial.println("Bomba desligada. Aguardando a água infiltrar...");
    
    // pausa de segurança, valor a ser estimado ainda, serve para dar um tempo da ativação da bomba para a próxima leitura de umidade
    delay(1000); 
  } else { // caso não esteja seco
    Serial.println("Solo com boa umidade. Bomba desligada.");
    digitalWrite(pinoRele, LOW); // relé fica desligado
  }
  
  delay(1000); // delay de 1 segundo para a próxima leitura do sensor
}