import socket
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import os

# Color Palette Mapping
COLOR_DARK_BLUE = "#0A2947"
COLOR_SAND      = "#F3E4C9"
COLOR_SAGE      = "#D3D4C0"
COLOR_BROWN     = "#8B5E3C"
COLOR_BLACK     = "#000000"

UDP_IP = "0.0.0.0"  
UDP_PORT = 4210

class ModernTabbedDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("ESP32-C3 SYSTEM MONITOR")
        self.root.geometry("850x600")
        self.root.configure(fg_color=COLOR_SAND)
        
        # Telemetry History
        self.history_time = []
        self.history_temp = []
        self.history_hum = []
        self.gateway_ip = "0.0.0.0"

        self.setup_ui()

        # Threading for network socket
        self.running = True
        self.listener_thread = threading.Thread(target=self.listen_udp, daemon=True)
        self.listener_thread.start()

    def setup_ui(self):
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

        # --- HEADER BLOCK ---
        header = ctk.CTkFrame(self.root, fg_color=COLOR_DARK_BLUE, border_color=COLOR_BLACK, border_width=3, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        
        title = ctk.CTkLabel(header, text="ESP32-C3 WEATHER HUB", font=("Arial Black", 16), text_color=COLOR_SAND)
        title.pack(side="left", padx=15, pady=12)
        
        self.status_var = tk.StringVar(value="STATUS: WAITING FOR GATEWAY")
        status_lbl = ctk.CTkLabel(header, textvariable=self.status_var, font=("Arial Black", 11), text_color=COLOR_SAGE)
        status_lbl.pack(side="right", padx=15)

        # --- BRUTALIST TABVIEW INTERFACE ---
        self.tabview = ctk.CTkTabview(self.root, 
                                      fg_color=COLOR_SAND, 
                                      segmented_button_fg_color=COLOR_DARK_BLUE,
                                      segmented_button_selected_color=COLOR_BROWN,
                                      segmented_button_selected_hover_color=COLOR_BROWN,
                                      segmented_button_unselected_color=COLOR_DARK_BLUE,
                                      text_color=COLOR_SAND,
                                      border_color=COLOR_BLACK,
                                      border_width=3,
                                      corner_radius=0)
        self.tabview.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")
        
        self.tab_data = self.tabview.add("REALTIME DATA")
        self.tab_serial = self.tabview.add("SERIAL MONITOR")
        self.tab_graphs = self.tabview.add("ANALYTICS GRAPHS")

        self.setup_data_tab()
        self.setup_serial_tab()
        self.setup_graphs_tab()

    def setup_data_tab(self):
        self.tab_data.grid_columnconfigure(0, weight=1)
        self.tab_data.grid_columnconfigure(1, weight=1)
        self.tab_data.grid_rowconfigure(0, weight=1)

        self.temp_var = tk.StringVar(value="-- °C")
        self.hum_var = tk.StringVar(value="-- %")

        t_card = ctk.CTkFrame(self.tab_data, fg_color=COLOR_SAGE, border_color=COLOR_BLACK, border_width=3, corner_radius=0)
        t_card.grid(row=0, column=0, padx=15, pady=20, sticky="nsew")
        ctk.CTkLabel(t_card, text="TEMPERATURE", font=("Arial Black", 14), text_color=COLOR_DARK_BLUE).pack(anchor="w", padx=15, pady=15)
        ctk.CTkLabel(t_card, textvariable=self.temp_var, font=("Arial Black", 36), text_color=COLOR_BLACK).pack(expand=True)

        h_card = ctk.CTkFrame(self.tab_data, fg_color=COLOR_SAGE, border_color=COLOR_BLACK, border_width=3, corner_radius=0)
        h_card.grid(row=0, column=1, padx=15, pady=20, sticky="nsew")
        ctk.CTkLabel(h_card, text="HUMIDITY", font=("Arial Black", 14), text_color=COLOR_DARK_BLUE).pack(anchor="w", padx=15, pady=15)
        ctk.CTkLabel(h_card, textvariable=self.hum_var, font=("Arial Black", 36), text_color=COLOR_BLACK).pack(expand=True)

    def setup_serial_tab(self):
        self.tab_serial.grid_columnconfigure(0, weight=1)
        self.tab_serial.grid_rowconfigure(0, weight=1)
        self.tab_serial.grid_rowconfigure(1, weight=0)

        self.serial_console = ctk.CTkTextbox(self.tab_serial, fg_color=COLOR_BLACK, text_color="#00FF00", font=("Courier", 13), corner_radius=0, border_width=2, border_color=COLOR_BLACK)
        self.serial_console.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        action_panel = ctk.CTkFrame(self.tab_serial, fg_color=COLOR_SAND, height=50, corner_radius=0)
        action_panel.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        download_btn = ctk.CTkButton(action_panel, text="DOWNLOAD PDF REPORT", font=("Arial Black", 11),
                                      fg_color=COLOR_BROWN, text_color=COLOR_SAND, hover_color=COLOR_DARK_BLUE,
                                      border_color=COLOR_BLACK, border_width=2, corner_radius=0,
                                      command=self.export_pdf_report)
        download_btn.pack(side="right", pady=5)

    def setup_graphs_tab(self):
        self.tab_graphs.grid_columnconfigure(0, weight=1)
        self.tab_graphs.grid_rowconfigure(0, weight=1)

        graph_frame = ctk.CTkFrame(self.tab_graphs, fg_color=COLOR_SAND, border_color=COLOR_BLACK, border_width=2, corner_radius=0)
        graph_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.fig, self.ax = plt.subplots(figsize=(6, 3), facecolor=COLOR_SAND)
        self.ax.set_facecolor(COLOR_SAND)
        for spine in ["top", "right"]: self.ax.spines[spine].set_visible(False)
        for spine in ["left", "bottom"]: 
            self.ax.spines[spine].set_color(COLOR_BLACK)
            self.ax.spines[spine].set_linewidth(2)

        self.canvas = FigureCanvasTkAgg(self.fig, master=graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def listen_udp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((UDP_IP, UDP_PORT))
        sock.settimeout(1.0) 

        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8')
                temp, hum = message.split(',')
                
                self.gateway_ip = addr[0]
                self.root.after(0, self.process_telemetry, temp, hum)
            except socket.timeout:
                continue
            except Exception:
                continue

    def process_telemetry(self, temp, hum):
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        log_entry = f"[{timestamp}] payload from {self.gateway_ip} -> TEMP: {temp}°C | HUMIDITY: {hum}%\n"
        self.serial_console.insert(tk.END, log_entry)
        self.serial_console.see(tk.END)
        
        if temp == "0.0" and hum == "0.0":
            self.temp_var.set("SENSOR ERR")
            self.hum_var.set("SENSOR ERR")
        else:
            self.temp_var.set(f"{temp} °C")
            self.hum_var.set(f"{hum} %")
            
            self.history_time.append(timestamp)
            self.history_temp.append(float(temp))
            self.history_hum.append(float(hum))
            
            if len(self.history_time) > 20:
                self.history_time.pop(0)
                self.history_temp.pop(0)
                self.history_hum.pop(0)
                
            self.update_graph()
            
        self.status_var.set(f"IP: {self.gateway_ip}")

    def update_graph(self):
        self.ax.clear()
        self.ax.set_facecolor(COLOR_SAND)
        
        self.ax.plot(self.history_time, self.history_temp, color=COLOR_DARK_BLUE, linewidth=3, label="Temperature (°C)")
        self.ax.plot(self.history_time, self.history_hum, color=COLOR_BROWN, linewidth=3, linestyle="--", label="Humidity (%)")
        
        self.ax.legend(loc="upper left", frameon=False)
        self.ax.tick_params(colors=COLOR_BLACK, labelsize=9)
        self.fig.autofmt_xdate()
        self.canvas.draw()

    def export_pdf_report(self):
        if not self.history_time:
            messagebox.showwarning("No Data", "Telemetry history is completely empty.")
            return
        
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                filetypes=[("PDF Document", "*.pdf")])
        if not file_path:
            return

        try:
            from fpdf import FPDF
            
            # Save chart snapshot temporarily
            temp_img_path = "temp_chart_export.png"
            self.fig.savefig(temp_img_path, facecolor=COLOR_SAND, edgecolor=COLOR_BLACK, dpi=200, bbox_inches='tight')

            # Create Brutalist PDF Document
            pdf = FPDF()
            pdf.add_page()
            
            # Global color background fill setup
            pdf.set_fill_color(243, 228, 201) # COLOR_SAND
            pdf.rect(0, 0, 210, 297, "F")
            
            # 1. Header block styling
            pdf.set_fill_color(10, 41, 71) # COLOR_DARK_BLUE
            pdf.rect(10, 10, 190, 22, "DF") 
            pdf.set_text_color(243, 228, 201) 
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(190, 22, "  ESP32-C3 TELEMETRY REPORT", ln=True, align="L")
            pdf.ln(12) 

            # 2. Meta block box layout spacing
            pdf.set_fill_color(211, 212, 192) # COLOR_SAGE
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Courier", "B", 10)
            
            meta_text = (f" GENERATED ON: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                         f" GATEWAY SOURCE IP: {self.gateway_ip}\n"
                         f" STATUS STATUS: EXPORT_SUCCESS // LOGS: {len(self.history_time)}")
            pdf.multi_cell(190, 7, meta_text, border=1, fill=True)
            pdf.ln(15) # Spacing before chart block titles

            # 3. Graph title block tag
            pdf.set_fill_color(139, 94, 60) # COLOR_BROWN
            pdf.set_text_color(243, 228, 201)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 9, "VISUAL ANALYTICS", border=1, ln=True, fill=True)
            pdf.ln(10) # <-- FIXED: Increased padding here so text title doesn't hit the image boundary

            # 4. Chart drawing assignment with safety positioning coordinates
            chart_y = pdf.get_y()
            pdf.image(temp_img_path, x=15, y=chart_y, w=180)
            
            # 5. Generous clear space calculation past chart container boundaries
            pdf.set_y(chart_y + 115) 
            pdf.ln(25) # <-- FIXED: Extended layout gap spacing to separate table completely

            # 6. Data table tag block identifier
            pdf.set_fill_color(139, 94, 60)
            pdf.set_text_color(243, 228, 201)
            pdf.set_font("Helvetica", "B", 11)
            pdf.cell(50, 9, "DATA LOG TABLE", border=1, ln=True, fill=True)
            pdf.ln(6)

            # 7. Data table column header height alignment settings
            pdf.set_fill_color(10, 41, 71)
            pdf.set_text_color(243, 228, 201)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(60, 12, "Timestamp", border=1, align="C", fill=True)
            pdf.cell(65, 12, "Temperature", border=1, align="C", fill=True)
            pdf.cell(65, 12, "Humidity", border=1, align="C", fill=True)
            pdf.ln()

            # 8. Data stream tracking metrics cells settings
            pdf.set_text_color(0, 0, 0)
            pdf.set_font("Courier", "", 10)
            for idx, (t, temp, hum) in enumerate(zip(self.history_time, self.history_temp, self.history_hum)):
                if idx % 2 == 0:
                    pdf.set_fill_color(255, 255, 255)
                else:
                    pdf.set_fill_color(211, 212, 192)
                
                pdf.cell(60, 10, str(t), border=1, align="C", fill=True)
                pdf.cell(65, 10, f"{temp} C", border=1, align="C", fill=True)
                pdf.cell(65, 10, f"{hum} %", border=1, align="C", fill=True)
                pdf.ln()

            pdf.output(file_path)
            
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
                
            messagebox.showinfo("Export Complete", f"PDF report successfully saved:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"An error occurred during compilation:\n{str(e)}")

if __name__ == "__main__":
    ctk.set_appearance_mode("Light") 
    root = ctk.CTk()
    app = ModernTabbedDashboard(root)
    
    def on_closing():
        app.running = False
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
