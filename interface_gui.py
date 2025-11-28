import gi
import threading
import simulador

# Configura a versão do GTK antes de importar
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GLib, Gdk

# Importa o Canvas e a Toolbar do Matplotlib
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar
from matplotlib.figure import Figure

class JanelaPrincipal(Gtk.Window):
    def __init__(self):
        super().__init__(title="Simulador de Redes - TR1 (GTK + Zoom)")
        self.set_border_width(10)
        self.set_default_size(1000, 750)
        
        # Instancia o simulador
        self.sim = simulador.Simulador()
        self.sim.registrar_callback(self.atualizar_interface_rx)

        # Layout Principal (Box Vertical)
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        # --- ÁREA DE CONFIGURAÇÃO (Topo) ---
        frame_config = Gtk.Frame(label="Configurações")
        vbox.pack_start(frame_config, False, False, 0)
        
        grid_config = Gtk.Grid()
        grid_config.set_column_spacing(10)
        grid_config.set_row_spacing(5)
        grid_config.set_margin_top(10)
        grid_config.set_margin_bottom(10)
        grid_config.set_margin_start(10)
        frame_config.add(grid_config)

        # Drops de Seleção
        self.combo_mod_bb = self.criar_combo(["NRZ-POLAR", "MANCHESTER", "BIPOLAR"])
        self.combo_mod_port = self.criar_combo(["ASK", "FSK", "BPSK", "QPSK", "8PSK", "16-QAM", "Nenhuma"])
        
        self.combo_enquadramento = self.criar_combo(["Contagem de Caracteres", "Inserção de Bytes", "Inserção de Bits"])
        self.combo_erro = self.criar_combo(["Nenhum", "Paridade Par", "Checksum", "CRC", "Hamming"])
        
        # Slider de Ruído (CORREÇÃO: Usando Gtk.Scale moderno em vez de HScale)
        self.scale_ruido = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 5, 0.1)
        self.scale_ruido.set_size_request(150, -1)
        self.scale_ruido.set_value(0.0)

        # Adicionando ao Grid
        self.add_label_field(grid_config, "Mod. Banda Base:", self.combo_mod_bb, 0, 0)
        self.add_label_field(grid_config, "Mod. Portadora:", self.combo_mod_port, 0, 1)
        
        self.add_label_field(grid_config, "Enquadramento:", self.combo_enquadramento, 2, 0)
        self.add_label_field(grid_config, "Controle de Erro:", self.combo_erro, 2, 1)
        self.add_label_field(grid_config, "Ruído (SNR):", self.scale_ruido, 4, 0)

        # --- ÁREA DE TRANSMISSÃO E RECEPÇÃO (Meio) ---
        hbox_msgs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        vbox.pack_start(hbox_msgs, False, False, 0)

        # TX
        box_tx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        hbox_msgs.pack_start(box_tx, True, True, 0)
        box_tx.pack_start(Gtk.Label(label="Mensagem a Enviar (TX):", xalign=0), False, False, 0)
        self.entry_tx = Gtk.Entry()
        self.entry_tx.set_text("Digite sua mensagem...")
        box_tx.pack_start(self.entry_tx, False, False, 0)
        
        btn_enviar = Gtk.Button(label="Transmitir")
        btn_enviar.connect("clicked", self.ao_clicar_enviar)
        box_tx.pack_start(btn_enviar, False, False, 0)

        # RX
        box_rx = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        hbox_msgs.pack_start(box_rx, True, True, 0)
        box_rx.pack_start(Gtk.Label(label="Mensagem Recebida (RX):", xalign=0), False, False, 0)
        self.lbl_rx = Gtk.Label(label="aguardando...")
        self.lbl_rx.set_markup("<span background='#eeeeee' foreground='#000000' size='large'> ... </span>")
        box_rx.pack_start(self.lbl_rx, False, False, 0)
        
        self.lbl_status = Gtk.Label(label="")
        box_rx.pack_start(self.lbl_status, False, False, 0)

        # --- ÁREA DE GRÁFICOS (Fundo) ---
        self.fig = Figure(figsize=(5, 4), dpi=100)
        self.ax1 = self.fig.add_subplot(211) # Cima: Sinal Enviado
        self.ax2 = self.fig.add_subplot(212) # Baixo: Sinal Recebido
        self.fig.tight_layout()

        # Canvas (O Gráfico em si)
        self.canvas = FigureCanvas(self.fig)
        self.canvas.set_size_request(-1, 400)
        vbox.pack_start(self.canvas, True, True, 0)

        # Barra de Ferramentas (Toolbar)
        # CORREÇÃO AQUI: Removido o argumento 'self' extra
        self.toolbar = NavigationToolbar(self.canvas)
        vbox.pack_start(self.toolbar, False, False, 0)

    # --- Métodos Auxiliares de UI ---
    def criar_combo(self, opcoes):
        combo = Gtk.ComboBoxText()
        for op in opcoes:
            combo.append_text(op)
        combo.set_active(0)
        return combo

    def add_label_field(self, grid, label_text, widget, col, row):
        lbl = Gtk.Label(label=label_text, xalign=1)
        grid.attach(lbl, col * 2, row, 1, 1)
        grid.attach(widget, col * 2 + 1, row, 1, 1)

    # --- Lógica de Controle ---
    def ao_clicar_enviar(self, widget):
        # 1. Pega configurações
        texto = self.entry_tx.get_text()
        mod_bb = self.combo_mod_bb.get_active_text()
        
        opcao_port = self.combo_mod_port.get_active_text()
        if opcao_port == "Nenhuma":
            usa_port = False
            mod_port = "ASK" 
        else:
            usa_port = True
            mod_port = opcao_port

        enquad = self.combo_enquadramento.get_active_text()
        erro = self.combo_erro.get_active_text()
        ruido = self.scale_ruido.get_value()

        # 2. Configura Simulador
        self.sim.configurar(mod_bb, mod_port, usa_port, enquad, erro, ruido)
        
        # 3. Transmite
        self.lbl_status.set_text("Transmitindo...")
        self.sim.transmitir(texto)

    def atualizar_interface_rx(self, mensagem_rx, status):
        GLib.idle_add(self._atualizar_gui_safe, mensagem_rx, status)

    def _atualizar_gui_safe(self, mensagem_rx, status):
        # Atualiza Texto
        self.lbl_rx.set_markup(f"<span background='#ccffcc' size='large'> {mensagem_rx} </span>")
        self.lbl_status.set_text(f"Status: {status}")

        # Atualiza Gráficos
        self.ax1.clear()
        self.ax2.clear()

        sinal_tx = self.sim.sinal_transmitido
        sinal_rx = self.sim.sinal_recebido

        if sinal_tx:
            self.ax1.plot(sinal_tx, color='blue')
            if self.combo_mod_port.get_active_text() == "Nenhuma":
                self.ax1.set_title(f"Sinal Transmitido (Banda Base: {self.combo_mod_bb.get_active_text()})")
            else:
                self.ax1.set_title("Sinal Transmitido (Modulado)")
            self.ax1.grid(True, alpha=0.3)

        if sinal_rx:
            self.ax2.plot(sinal_rx, color='red', alpha=0.7)
            self.ax2.set_title("Sinal Recebido (RX - Com Ruído)")
            self.ax2.grid(True, alpha=0.3)

        self.canvas.draw()

# --- Inicialização ---
if __name__ == "__main__":
    win = JanelaPrincipal()
    win.connect("destroy", Gtk.main_quit)
    win.show_all()
    Gtk.main()