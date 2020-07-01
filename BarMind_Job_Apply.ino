#include <ESP8266WiFi.h>
#include <PubSubClient.h>

// Dane do łączenia się z WiFi:
const char* ssid = "Nazwa_Sieci";
const char* password =  "Haslo";

// Dane do łączenia się z MQTT:
const char* mqttServer = "farmer.cloudmqtt.com";
const int mqttPort = 11538;
const char* mqttUser = "Username";
const char* mqttPassword = "Password";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
// Inicjacja pompek:
  pinMode(16, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(4, OUTPUT);
  pinMode(0, OUTPUT);

// Łączenie z WiFi:
  Serial.begin(115200);
  WiFi.begin(ssid, password);
 
  while (WiFi.status() != WL_CONNECTED) {
    delay(600);
    Serial.println("Łącze z WiFi...");
  }
  Serial.println("Połączono z Wifi");

// Inicjacja MQTT:
  client.setServer(mqttServer, mqttPort);
  client.setCallback(callback);
 
  while (!client.connected()) 
  {
    Serial.println("Łączenie z MQTT...");
    
    if (client.connect("BarMind", mqttUser, mqttPassword )) 
    {
      Serial.println("Połączono!");  
    } 
    else 
    {
      Serial.print("failed with state: ");
      Serial.print(client.state());
      delay(2000);
    }
  }
  //Dołączenie do Tematu:
  client.subscribe("barkeep");
}

boolean reconnect() {
  if (client.connect("BarMind", mqttUser, mqttPassword )) {
    client.subscribe("barkeep");
  }
  return client.connected();
}

//funkcja używana do nalewania płynu przez pompki
void pourDrink(int pumpNumber, int mililiters)
{
  // ~90ml/min = 1.49ml/s
  int waitFor = (mililiters / 1.49) * 1000;
  
  switch(pumpNumber)
  {
    case 1:
    {
      digitalWrite(16, HIGH);
      delay(waitFor);
      digitalWrite(16, LOW);
      break;
    }
    case 2:
    {
      digitalWrite(5, HIGH);
      delay(waitFor);
      digitalWrite(5, LOW);
      break;
    }
    case 3:
    {
      digitalWrite(4, HIGH);
      delay(waitFor);
      digitalWrite(4, LOW);
      break;
    }
    case 4:
    {
      digitalWrite(0, HIGH);
      delay(waitFor);
      digitalWrite(0, LOW);
      break;
    }
    default:
    {
      client.publish("BarMind", "Pump problem");
      break;
    }
  }
}

//funkcja z biblioteki PubSubClient która odczytuje komunikaty wysyłane w chmurze
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.println("Nowy drink:");
  char newMsg[100] = "";
  int i = 0;
  for (i = 0; i < length; i++) {
    newMsg[i] = payload[i];
  }
  //newMsg[i] = '0';
  Serial.println(newMsg);
  //dzielimy otrzymana wiadomość w naszym wypadku np "1:200;2:100" naleje 200ml na pompce nr 1 i 100ml na pompce nr 2 
  char* readPump = strtok(newMsg, ";");
  while(readPump != 0)
  {
    char* separator = strchr(readPump, ':');
    if (separator != 0)
    {
      *separator = 0;
      int pumpNumber = atoi(readPump);
      ++separator;
      int mililiters = atoi(separator);
      Serial.print("Pump ");
      Serial.print(pumpNumber);
      Serial.print(" pouring ");
      Serial.print(mililiters);
      Serial.print(" ml");
      Serial.println();
      pourDrink(pumpNumber, mililiters);
    }
    readPump = strtok(0, ";");
  }
  Serial.println("Nalane");
  //client.publish("BarMind", "Nalane");
  return;
}

//loop upewniajacy się, że cały czas jesteśmy połączeni z serwerem
void loop() {
  if (!client.connected()) 
  {
    Serial.println("MQTT rozłączone");
    if(reconnect())
    {
      Serial.println("Połączono z MQTT ponownie");
    } else {
      Serial.println("Próba ponownego połączenia nieudana");
    }
  } else {
    client.loop();
  }
}
