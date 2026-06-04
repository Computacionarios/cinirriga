import json
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.animation import Animation

# Se estiver rodando no celular Android, importa as classes nativas do Java via PyJnius
if platform == 'android':
    from jnius import autoclass
    BluetoothAdapter = autoclass('android.bluetooth.BluetoothAdapter')
    UUID = autoclass('java.util.UUID')
else:
    BluetoothAdapter = None
    UUID = None

# --- DESIGN RESPONSIVO PARA ANDROID (MOBILE) ---
KV = '''
#:import utils kivy.utils

MDScreen:
    md_bg_color: utils.get_color_from_hex('#242424')

    MDNavigationLayout:

        MDScreenManager:
            MDScreen:
                
                # ----------------------------------------------------
                # CAMADA 1: CONTEÚDO PRINCIPAL DO APP
                # ----------------------------------------------------
                MDBoxLayout:
                    orientation: 'vertical'

                    # Cabeçalho Principal Fixado
                    MDTopAppBar:
                        title: "Cinrriga"
                        anchor_title: "center"
                        md_bg_color: utils.get_color_from_hex('#1b8a4f')
                        elevation: 2
                        left_action_items: [["menu", lambda x: nav_drawer_left.set_state("open")]]
                        right_action_items: [["bluetooth", lambda x: app.conectar_bluetooth()]]

                    # Painel de Monitoramento com Scroll Responsivo
                    ScrollView:
                        do_scroll_x: False
                        
                        MDBoxLayout:
                            orientation: 'vertical'
                            padding: "16dp"
                            spacing: "16dp"

                            # 1. Painel Superior: Informações dos Sensores (Ocupa ~55% da tela)
                            BoxLayout:
                                size_hint_y: 0.55
                                
                                Image:
                                    source: "sessaoinfo.png"
                                    allow_stretch: True
                                    keep_ratio: True

                            # 2. Painel Inferior: Botões (Ocupa ~45% da tela)
                            MDFloatLayout:
                                size_hint_y: 0.45
                                
                                Image:
                                    source: "sacoes.png"
                                    allow_stretch: True
                                    keep_ratio: True
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                                MDGridLayout:
                                    cols: 2
                                    spacing: "16dp"
                                    padding: "12dp"
                                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                                    size_hint: (0.9, 0.9)

                                    # Botões Invisíveis baseados na proporção da imagem de fundo
                                    Button:
                                        background_color: (0, 0, 0, 0)
                                        on_release: app.abrir_popup_regar()

                                    Button:
                                        background_color: (0, 0, 0, 0)
                                        on_release: app.acao_botoes("Regular rega (Desativado no momento)")

                                    Button:
                                        background_color: (0, 0, 0, 0)
                                        on_release: app.acao_botoes("Alterar intervalo")

                                    Button:
                                        background_color: (0, 0, 0, 0)
                                        on_release: app.acao_botoes("Fertilização")

                # ----------------------------------------------------
                # CAMADA 2: POPUP DE REGAR (ANIMADO DE BAIXO PARA CIMA)
                # ----------------------------------------------------
                MDFloatLayout:
                    id: popup_regar_container
                    size_hint: 1, 1
                    pos_hint: {'center_x': 0.5, 'center_y': -0.5}
                    
                    # Layout da janelinha do Popup (Responsivo para largura de celular)
                    MDFloatLayout:
                        size_hint: 0.9, 0.45
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                        Image:
                            source: "stateregar.png"
                            allow_stretch: True
                            keep_ratio: True
                            pos_hint: {'center_x': 0.5, 'center_y': 0.5}

                        # Botão Menos [-] (Hitbox Vermelha Semitransparente)
                        Button:
                            size_hint: (0.20, 0.16)
                            pos_hint: {'center_x': 0.32, 'center_y': 0.52}
                            background_color: (1, 0, 0, 0.4)
                            on_release: app.ajustar_tempo(-1)

                        # Contador Digital Central
                        MDLabel:
                            text: app.texto_duracao
                            halign: "center"
                            font_style: "H4"
                            bold: True
                            size_hint: (0.2, 0.1)
                            pos_hint: {'center_x': 0.5, 'center_y': 0.52}
                            theme_text_color: "Custom"
                            text_color: 1, 1, 1, 1

                        # Botão Mais [+] (Hitbox Azul Semitransparente - Corrigido pos_hint)
                        Button:
                            size_hint: (0.20, 0.16)
                            pos_hint: {'center_x': 0.68, 'center_y': 0.52}
                            background_color: (0, 0, 1, 0.4)
                            on_release: app.ajustar_tempo(1)

                        # Botão Confirmar "Regar" (Hitbox Verde Semitransparente)
                        Button:
                            size_hint: (0.42, 0.15)
                            pos_hint: {'center_x': 0.28, 'center_y': 0.26}
                            background_color: (0, 1, 0, 0.4)
                            on_release: app.confirmar_rega()

                        # Botão "Cancelar" (Hitbox Amarela Semitransparente)
                        Button:
                            size_hint: (0.42, 0.15)
                            pos_hint: {'center_x': 0.72, 'center_y': 0.26}
                            background_color: (1, 1, 0, 0.4)
                            on_release: app.fechar_popup_regar()

        # ----------------------------------------------------
        # MENU LATERAL (ESQUERDA): BLUETOOTH
        # ----------------------------------------------------
        MDNavigationDrawer:
            id: nav_drawer_left
            anchor_view: "left"
            radius: (0, 16, 16, 0)
            md_bg_color: utils.get_color_from_hex('#1e1e1e')
            MDBoxLayout:
                orientation: 'vertical'
                padding: "16dp"
                MDLabel:
                    text: "Dispositivos Bluetooth"
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
'''

class IrrigacaoApp(MDApp):
    duracao_rega = NumericProperty(1)
    texto_duracao = StringProperty("1")
    
    # Armazenará o objeto de stream de saída do Bluetooth do celular
    bluetooth_output_stream = None
    dispositivo_conectado = False

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Green"
        return Builder.load_string(KV)

    # --- ANIMAÇÕES DO POPUP BOTTOM-UP ---
    def abrir_popup_regar(self):
        self.duracao_rega = 1
        self.texto_duracao = str(self.duracao_rega)
        anim = Animation(pos_hint={'center_y': 0.5}, duration=0.3, transition='out_quad')
        anim.start(self.root.ids.popup_regar_container)

    def fechar_popup_regar(self):
        anim = Animation(pos_hint={'center_y': -0.5}, duration=0.3, transition='in_quad')
        anim.start(self.root.ids.popup_regar_container)

    # --- LÓGICA DE TEMPO EM SEGUNDOS ---
    def ajustar_tempo(self, valor):
        if self.duracao_rega + valor >= 1:
            self.duracao_rega += valor
            self.texto_duracao = str(self.duracao_rega)

    # --- CONEXÃO BLUETOOTH (NATIVA DO ANDROID) ---
    def conectar_bluetooth(self):
        print("[BLUETOOTH] Iniciando tentativa de conexão...")
        
        if platform != 'android':
            print("[SIMULAÇÃO] Bluetooth só conecta rodando no Android real.")
            self.dispositivo_conectado = True
            return

        try:
            adapter = BluetoothAdapter.getDefaultAdapter()
            if not adapter or not adapter.isEnabled():
                print("[ERRO] Bluetooth desligado no Android.")
                return

            # Coleta os dispositivos que já estão pareados no Android
            paired_devices = adapter.getBondedDevices().toArray()
            
            # Altere para o nome exato que está configurado no seu Arduino (ex: "HC-05", "ESP32_Cinrriga")
            nome_alvo = "HC-05" 
            device_alvo = None

            for device in paired_devices:
                if device.getName() == nome_alvo:
                    device_alvo = device
                    break

            if device_alvo:
                # UUID padrão para conexões SPP (Serial Port Profile) do Arduino/HC-05
                spp_uuid = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")
                socket = device_alvo.createRfcommSocketToServiceRecord(spp_uuid)
                socket.connect() # Estabelece a conexão física
                
                # Guarda o canal de envio de dados
                self.bluetooth_output_stream = socket.getOutputStream()
                self.dispositivo_conectado = True
                print(f"[SUCESSO] Conectado a: {nome_alvo}")
            else:
                print(f"[AVISO] Dispositivo pareado chamado '{nome_alvo}' não foi encontrado.")

        except Exception as e:
            print(f"[ERRO BLUETOOTH] Falha na conexão nativa: {str(e)}")
            self.dispositivo_conectado = False

    # --- ENVIO DE DADOS EM FORMATO JSON ---
    def confirmar_rega(self):
        # 1. Cria a estrutura de dados (tabela) que o Arduino vai interpretar
        payload = {
            "comando": "REGAR",
            "duracao_segundos": self.duracao_rega,
            "sensor_ativo": True
        }
        
        # 2. Transforma o dicionário Python em uma String estruturada no formato JSON
        json_string = json.dumps(payload) + "\n"  # \n serve como caractere terminador para o Arduino saber onde o pacote termina

        print(f"[JSON GERADO] Enviando: {json_string.strip()}")

        # 3. Envia os dados caso esteja conectado via Bluetooth
        if self.dispositivo_conectado and self.bluetooth_output_stream:
            try:
                # Transforma a string em um array de bytes (Java-compatible) antes de enviar
                self.bluetooth_output_stream.write(json_string.encode('utf-8'))
                self.bluetooth_output_stream.flush()
                print("[BLUETOOTH] JSON enviado com sucesso ao Arduino.")
            except Exception as e:
                print(f"[ERRO ENVIO] Falha ao transmitir dados: {str(e)}")
        else:
            print("[AVISO] Comando não enviado. Nenhuma conexão Bluetooth ativa encontrada.")

        self.fechar_popup_regar()

    def acao_botoes(self, nome_acao):
        print(f"Funcionalidade chamada: {nome_acao}")


if __name__ == '__main__':
    IrrigacaoApp().run()
