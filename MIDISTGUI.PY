import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import pretty_midi
import json
import os
import tempfile
import ctypes  # <--- 新增这个，删除 pygame
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.cm as cm

# --- 初始化与外观设置 ---
ctk.set_appearance_mode("Dark")  # 默认使用暗色模式，显得更专业
ctk.set_default_color_theme("blue")

# 全局字体设置，修复默认字体在某些系统下的粗细/发虚问题
# 推荐使用微软雅黑或其他无衬线标准字体
DEFAULT_FONT = ("Microsoft YaHei", 13, "normal")
TITLE_FONT = ("Microsoft YaHei", 16, "bold")

class MidiWorkstationApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("MIDI 轨道解析与提取工作站")
        self.geometry("1100x700")
        self.minsize(900, 600)

        # 核心数据
        self.midi_data = None
        self.instruments = []
        self.current_output_data = None
        self.temp_midi_path = os.path.join(tempfile.gettempdir(), "preview_temp.mid")



        self.setup_ui()

    def setup_ui(self):
        # 整体布局：左侧控制栏 (Sidebar)，右侧主内容区 (Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ================= 左侧控制栏 =================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False) # 固定宽度

        # 标题
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="MIDI 提取控制台", font=TITLE_FONT)
        self.lbl_title.pack(pady=(20, 20), padx=20)

        # 1. 文件加载区
        self.btn_browse = ctk.CTkButton(self.sidebar, text="📂 加载 MIDI 文件", font=DEFAULT_FONT, command=self.browse_file)
        self.btn_browse.pack(pady=(10, 5), padx=20, fill="x")

        self.lbl_filepath = ctk.CTkLabel(self.sidebar, text="未选择文件...", text_color="gray", font=("Microsoft YaHei", 11), wraplength=240)
        self.lbl_filepath.pack(pady=(0, 15), padx=20)

        # 2. 基础信息区 (BPM)
        self.info_frame = ctk.CTkFrame(self.sidebar)
        self.info_frame.pack(pady=10, padx=20, fill="x")
        self.lbl_bpm = ctk.CTkLabel(self.info_frame, text="BPM: --", font=DEFAULT_FONT)
        self.lbl_bpm.pack(pady=10)

        # 3. 轨道操作区
        self.lbl_track = ctk.CTkLabel(self.sidebar, text="选择解析轨道:", font=DEFAULT_FONT)
        self.lbl_track.pack(pady=(20, 5), padx=20, anchor="w")

        self.combo_track = ctk.CTkComboBox(self.sidebar, values=["请先加载文件"], state="disabled", font=DEFAULT_FONT)
        self.combo_track.pack(pady=(0, 15), padx=20, fill="x")

        # 4. 播放控制区
        self.play_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.play_frame.pack(pady=5, padx=20, fill="x")
        
        self.btn_play = ctk.CTkButton(self.play_frame, text="▶ 试听选中轨道", font=DEFAULT_FONT, fg_color="#2E8B57", hover_color="#226B43", state="disabled", command=self.play_preview)
        self.btn_play.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.btn_stop = ctk.CTkButton(self.play_frame, text="⏹ 停止", font=DEFAULT_FONT, fg_color="#CD5C5C", hover_color="#A52A2A", width=60, state="disabled", command=self.stop_preview)
        self.btn_stop.pack(side="right")

        # 5. 提取与导出区
        self.btn_extract = ctk.CTkButton(self.sidebar, text="⚡ 提取音符数据", font=DEFAULT_FONT, state="disabled", command=self.extract_notes)
        self.btn_extract.pack(pady=(30, 10), padx=20, fill="x")

        self.btn_export = ctk.CTkButton(self.sidebar, text="💾 导出 JSON", font=DEFAULT_FONT, state="disabled", fg_color="#b87333", hover_color="#8b5a2b", command=self.export_data)
        self.btn_export.pack(pady=(0, 20), padx=20, fill="x")


        # ================= 右侧主内容区 =================
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=6) # 图表占 6 成高度
        self.main_frame.grid_rowconfigure(1, weight=4) # 文本占 4 成高度
        self.main_frame.grid_columnconfigure(0, weight=1)

        # 右上：Matplotlib 预览图容器
        self.plot_container = ctk.CTkFrame(self.main_frame, corner_radius=10)
        self.plot_container.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="nsew")
        
        # 初始化空白图表
        self.fig = Figure(figsize=(6, 3), dpi=100)
        # 适配暗色模式的图表背景
        self.fig.patch.set_facecolor('#2b2b2b')
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor('#333333')
        self.ax.tick_params(colors='white')
        for spine in self.ax.spines.values():
            spine.set_edgecolor('gray')
            
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_container)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # 右下：数据输出区
        self.textbox = ctk.CTkTextbox(self.main_frame, wrap="none", font=("Consolas", 13))
        self.textbox.grid(row=1, column=0, padx=10, pady=(5, 10), sticky="nsew")
        self.log("欢迎使用 MIDI 工作站！请点击左侧加载文件。")

    def browse_file(self):
        file_path = filedialog.askopenfilename(
            title="选择 MIDI 文件",
            filetypes=(("MIDI Files", "*.mid *.midi"), ("All Files", "*.*"))
        )
        if file_path:
            self.lbl_filepath.configure(text=os.path.basename(file_path))
            self.load_midi(file_path)

    def load_midi(self, file_path):
        self.stop_preview() # 停止之前可能在播放的声音
        self.log(f"正在解析: {os.path.basename(file_path)} ...")
        self.update()
        
        try:
            self.midi_data = pretty_midi.PrettyMIDI(file_path)
            self.instruments = self.midi_data.instruments
            
            if not self.instruments:
                self.log("错误：MIDI 文件中没有音符轨道。")
                return

            # 1. 估算 BPM 并显示
            try:
                bpm = self.midi_data.estimate_tempo()
                self.lbl_bpm.configure(text=f"估算 BPM: {bpm:.1f}")
            except:
                self.lbl_bpm.configure(text="BPM: 未知")

            # 2. 渲染全轨道预览图
            self.render_plot()

            # 3. 更新下拉菜单选项
            track_options = []
            for i, inst in enumerate(self.instruments):
                track_options.append(f"{i}: {inst.name} ({len(inst.notes)} notes)")

            self.combo_track.configure(state="normal", values=track_options)
            self.combo_track.set(track_options[0])
            
            # 启用所有按钮
            self.btn_extract.configure(state="normal")
            self.btn_play.configure(state="normal")
            self.btn_stop.configure(state="normal")
            
            self.log(f"加载成功！共发现 {len(self.instruments)} 个轨道。")

        except Exception as e:
            self.log(f"解析失败: {e}")
            messagebox.showerror("错误", f"无法解析 MIDI 文件:\n{e}")

    def render_plot(self):
        self.ax.clear()
        
        # 保持暗色模式外观
        self.ax.set_facecolor('#333333')
        self.ax.set_xlabel("Time (Seconds)", color='white', fontsize=10)
        self.ax.set_ylabel("Pitch (MIDI Note)", color='white', fontsize=10)
        self.ax.set_title("Piano Roll Preview (All Tracks)", color='white', fontsize=12)

        colors = cm.get_cmap('tab10', max(10, len(self.instruments)))
        
        for i, inst in enumerate(self.instruments):
            notes = inst.notes
            if not notes:
                continue
            
            # 提取起始、结束、音高数据进行批量绘制，提升渲染效率
            starts = [n.start for n in notes]
            ends = [n.end for n in notes]
            pitches = [n.pitch for n in notes]
            
            self.ax.hlines(y=pitches, xmin=starts, xmax=ends, 
                           colors=colors(i), linewidth=2)
            
            # 图例代理
            self.ax.scatter([], [], color=colors(i), label=f"Track {i}")

        if len(self.instruments) <= 10: # 如果轨道太多就不显示图例了，防挡住画面
            self.ax.legend(loc='upper right', fontsize=8, facecolor='#2b2b2b', edgecolor='gray', labelcolor='white')

        self.fig.tight_layout()
        self.canvas.draw()

    def play_preview(self):
        if not self.instruments: return
        
        track_idx = int(self.combo_track.get().split(":")[0])
        selected_inst = self.instruments[track_idx]
        
        if not selected_inst.notes:
            self.log(f"轨道 {track_idx} 为空，无法播放。")
            return

        self.log(f"🎵 正在播放轨道: {track_idx} ...")
        
        try:
            temp_midi = pretty_midi.PrettyMIDI()
            temp_midi.time_signature_changes = self.midi_data.time_signature_changes
            temp_midi.key_signature_changes = self.midi_data.key_signature_changes
            temp_midi.instruments.append(selected_inst)
            
            temp_midi.write(self.temp_midi_path)
            
            # --- 使用 Windows 原生 MCI 接口播放 MIDI ---
            self.stop_preview()  # 确保播放前先停止并关闭上一个流
            
            # 1. 打开文件并起个别名 (alias)
            open_cmd = f'open "{self.temp_midi_path}" type sequencer alias my_midi'
            ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, None)
            
            # 2. 播放
            play_cmd = 'play my_midi'
            ctypes.windll.winmm.mciSendStringW(play_cmd, None, 0, None)
            
        except Exception as e:
            self.log(f"播放出错: {e}")

    def stop_preview(self):
        # --- 使用 Windows 原生 MCI 接口停止并释放 MIDI ---
        ctypes.windll.winmm.mciSendStringW('stop my_midi', None, 0, None)
        ctypes.windll.winmm.mciSendStringW('close my_midi', None, 0, None)
        self.log("⏹ 播放已停止。")

    def extract_notes(self):
        if not self.instruments: return
            
        track_idx = int(self.combo_track.get().split(":")[0])
        selected_inst = self.instruments[track_idx]
        
        if not selected_inst.notes:
            self.log(f"警告: 轨道 {track_idx} 没有音符，无法提取。")
            return

        self.log(f"正在提取轨道 {track_idx} 的数据...")
        
        output_data = []
        for note in selected_inst.notes:
            output_data.append({
                "pitch": note.pitch,
                "start_time": round(note.start, 4)
            })

        output_data.sort(key=lambda x: x["start_time"])
        self.current_output_data = output_data # 保存到内存供导出使用
        
        output_json = json.dumps(output_data, indent=4)
        
        self.textbox.delete("1.0", "end")
        self.textbox.insert("0.0", output_json)
        self.log(f"✅ 提取完成！共计 {len(output_data)} 个音符。可点击导出按钮保存。")
        
        # 启用导出按钮
        self.btn_export.configure(state="normal")

    def export_data(self):
        if not self.current_output_data:
            return
            
        save_path = filedialog.asksaveasfilename(
            title="保存 JSON 数据",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile="extracted_notes.json"
        )
        
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_output_data, f, indent=4)
                self.log(f"💾 数据已成功导出至: {save_path}")
            except Exception as e:
                self.log(f"导出失败: {e}")
                messagebox.showerror("导出错误", str(e))

    def log(self, message):
        self.textbox.insert("end", f"\n[System] {message}")
        self.textbox.see("end")

    def on_closing(self):
        """窗口关闭时的清理工作"""
        self.stop_preview() # <--- 换成这个
        
        if os.path.exists(self.temp_midi_path):
            try:
                os.remove(self.temp_midi_path)
            except:
                pass
        self.destroy()

if __name__ == "__main__":
    app = MidiWorkstationApp()
    # 绑定关闭事件，确保清理临时文件和 pygame 进程
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()