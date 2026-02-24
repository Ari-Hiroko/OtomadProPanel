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
        self.title("MIDI 轨道解析与批量导出工作站")
        self.geometry("1100x700")
        self.minsize(900, 600)
        # 核心数据
        self.midi_data = None
        self.instruments = []
        self.current_output_data = None
        self.temp_midi_path = os.path.join(tempfile.gettempdir(), "preview_temp.mid")
        self.current_bpm = None  # 新增：存储用户输入或MIDI文件中的BPM
        self.original_bpm = None  # 新增：存储原始BPM用于时间转换
        self.output_folder = ""  # 新增：存储输出文件夹路径
        self.selected_tracks = []  # 新增：存储选中的轨道索引
        self.setup_ui()

    def setup_ui(self):
        # 整体布局：左侧控制栏 (Sidebar)，右侧主内容区 (Main)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # ================= 左侧控制栏 =================
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)  # 固定宽度
        
        # 标题
        self.lbl_title = ctk.CTkLabel(self.sidebar, text="MIDI 提取控制台", font=TITLE_FONT)
        self.lbl_title.pack(pady=(20, 20), padx=20)
        
        # 1. 文件加载区
        self.btn_browse = ctk.CTkButton(self.sidebar, text="📂 加载 MIDI 文件", font=DEFAULT_FONT, command=self.browse_file)
        self.btn_browse.pack(pady=(10, 5), padx=20, fill="x")
        self.lbl_filepath = ctk.CTkLabel(self.sidebar, text="未选择文件...", text_color="gray", font=("Microsoft YaHei", 11), wraplength=240)
        self.lbl_filepath.pack(pady=(0, 15), padx=20)
        
        # 2. 输出文件夹选择
        self.output_folder_frame = ctk.CTkFrame(self.sidebar)
        self.output_folder_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_output_folder = ctk.CTkLabel(self.output_folder_frame, text="输出文件夹:", font=DEFAULT_FONT)
        self.lbl_output_folder.pack(pady=5, padx=10, anchor="w")
        
        self.btn_select_output_folder = ctk.CTkButton(self.output_folder_frame, text="📁 选择输出文件夹", font=DEFAULT_FONT, command=self.select_output_folder)
        self.btn_select_output_folder.pack(pady=5, padx=10, fill="x")
        
        self.lbl_current_output_folder = ctk.CTkLabel(self.output_folder_frame, text="未选择文件夹", text_color="gray", font=("Microsoft YaHei", 11))
        self.lbl_current_output_folder.pack(pady=(0, 5), padx=10, anchor="w")
        
        # 3. 基础信息区 (BPM)
        self.bpm_frame = ctk.CTkFrame(self.sidebar)
        self.bpm_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_bpm = ctk.CTkLabel(self.bpm_frame, text="BPM: --", font=DEFAULT_FONT)
        self.lbl_bpm.pack(pady=5, padx=10, anchor="w")
        
        # 添加BPM输入框
        self.bpm_entry = ctk.CTkEntry(self.bpm_frame, font=DEFAULT_FONT)
        self.bpm_entry.pack(pady=5, padx=10, fill="x")
        self.bpm_entry.configure(state="disabled")
        self.bpm_entry.bind("<Return>", self.on_bpm_enter)
        
        # 4. 轨道选择区
        self.track_selection_frame = ctk.CTkFrame(self.sidebar)
        self.track_selection_frame.pack(pady=10, padx=20, fill="x")
        
        self.lbl_track = ctk.CTkLabel(self.track_selection_frame, text="选择解析轨道:", font=DEFAULT_FONT)
        self.lbl_track.pack(pady=(5, 5), padx=10, anchor="w")
        
        # 添加全选/取消全选按钮
        self.selection_control_frame = ctk.CTkFrame(self.track_selection_frame, fg_color="transparent")
        self.selection_control_frame.pack(pady=(0, 5), padx=10, fill="x")
        
        self.btn_select_all = ctk.CTkButton(self.selection_control_frame, text="全选", font=DEFAULT_FONT, width=60, command=self.select_all_tracks)
        self.btn_select_all.pack(side="left", padx=(0, 5))
        
        self.btn_deselect_all = ctk.CTkButton(self.selection_control_frame, text="取消全选", font=DEFAULT_FONT, width=80, command=self.deselect_all_tracks)
        self.btn_deselect_all.pack(side="left")
        
        # 创建轨道列表框
        self.track_listbox = tk.Listbox(
            self.track_selection_frame, 
            selectmode=tk.EXTENDED,
            height=8,
            bg="#333333",
            fg="white",
            selectbackground="#1f5fb9",
            font=("Microsoft YaHei", 11),
            borderwidth=0,
            highlightthickness=0
        )
        self.track_listbox.pack(pady=5, padx=10, fill="both", expand=True)
        self.track_listbox.bind("<<ListboxSelect>>", self.on_track_selection_change)
        
        # 5. 播放控制区
        self.play_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.play_frame.pack(pady=5, padx=20, fill="x")
        self.btn_play = ctk.CTkButton(self.play_frame, text="▶ 试听选中轨道", font=DEFAULT_FONT, fg_color="#2E8B57", hover_color="#226B43", state="disabled", command=self.play_preview)
        self.btn_play.pack(side="left", fill="x", expand=True, padx=(0, 5))
        self.btn_stop = ctk.CTkButton(self.play_frame, text="⏹ 停止", font=DEFAULT_FONT, fg_color="#CD5C5C", hover_color="#A52A2A", width=60, state="disabled", command=self.stop_preview)
        self.btn_stop.pack(side="right")
        
        # 6. 提取与导出区
        self.btn_extract = ctk.CTkButton(self.sidebar, text="⚡ 提取选中轨道", font=DEFAULT_FONT, state="disabled", command=self.extract_selected_notes)
        self.btn_extract.pack(pady=(30, 10), padx=20, fill="x")
        self.btn_export_batch = ctk.CTkButton(self.sidebar, text="📦 批量导出 JSON", font=DEFAULT_FONT, state="disabled", fg_color="#b87333", hover_color="#8b5a2b", command=self.export_batch)
        self.btn_export_batch.pack(pady=(0, 10), padx=20, fill="x")
        self.btn_export_single = ctk.CTkButton(self.sidebar, text="💾 单个导出 JSON", font=DEFAULT_FONT, state="disabled", fg_color="#4a7abc", hover_color="#3a5a8a", command=self.export_data)
        self.btn_export_single.pack(pady=(0, 20), padx=20, fill="x")
        
        # ================= 右侧主内容区 =================
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=6)  # 图表占 6 成高度
        self.main_frame.grid_rowconfigure(1, weight=4)  # 文本占 4 成高度
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

    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="选择输出文件夹")
        if folder_path:
            self.output_folder = folder_path
            self.lbl_current_output_folder.configure(text=os.path.basename(folder_path))
            self.log(f"输出文件夹设置为: {folder_path}")

    def load_midi(self, file_path):
        self.stop_preview()  # 停止之前可能在播放的声音
        self.log(f"正在解析: {os.path.basename(file_path)} ...")
        self.update()
        try:
            self.midi_data = pretty_midi.PrettyMIDI(file_path)
            self.instruments = self.midi_data.instruments
            if not self.instruments:
                self.log("错误：MIDI 文件中没有音符轨道。")
                return
            
            # 尝试从MIDI文件获取实际BPM
            try:
                # 获取MIDI文件中的tempo变化
                tempo_changes = self.midi_data.get_tempo_changes()
                if tempo_changes:
                    bpm = tempo_changes[0][1]
                    self.original_bpm = bpm  # 保存原始BPM
                    self.lbl_bpm.configure(text=f"实际 BPM: {bpm:.1f}")
                    self.current_bpm = bpm
                    self.bpm_entry.configure(state="disabled")
                else:
                    # 如果没有tempo变化，尝试从文件中获取默认BPM
                    bpm = self.midi_data.estimate_tempo()
                    if bpm is not None:
                        self.original_bpm = bpm  # 保存原始BPM
                        self.lbl_bpm.configure(text=f"估算 BPM: {bpm:.1f}")
                        self.current_bpm = bpm
                        self.bpm_entry.configure(state="disabled")
                    else:
                        self.lbl_bpm.configure(text="BPM: 未设置")
                        self.current_bpm = None
                        self.original_bpm = 120.0  # 默认BPM
                        self.bpm_entry.configure(state="normal")
                        self.bpm_entry.delete(0, "end")
                        self.bpm_entry.focus()
            except Exception as e:
                self.log(f"获取BPM失败: {e}")
                self.lbl_bpm.configure(text="BPM: 未知")
                self.current_bpm = None
                self.original_bpm = 120.0  # 默认BPM
                self.bpm_entry.configure(state="normal")
                self.bpm_entry.delete(0, "end")
                self.bpm_entry.focus()
                
            # 2. 渲染全轨道预览图
            self.render_plot()
            
            # 3. 更新轨道列表框选项
            self.track_listbox.delete(0, tk.END)
            for i, inst in enumerate(self.instruments):
                track_text = f"{i}: {inst.name} ({len(inst.notes)} notes)"
                self.track_listbox.insert(tk.END, track_text)
            
            # 启用所有按钮
            self.btn_extract.configure(state="normal")
            self.btn_play.configure(state="normal")
            self.btn_stop.configure(state="normal")
            self.btn_export_batch.configure(state="normal")
            
            self.log(f"加载成功！共发现 {len(self.instruments)} 个轨道。")
        except Exception as e:
            self.log(f"解析失败: {e}")
            messagebox.showerror("错误", f"无法解析 MIDI 文件:\n{e}")
    
    def on_bpm_enter(self, event):
        try:
            bpm = float(self.bpm_entry.get())
            if bpm <= 0:
                raise ValueError("BPM must be positive")
            self.current_bpm = bpm
            self.lbl_bpm.configure(text=f"实际 BPM: {bpm:.1f}")
            self.bpm_entry.configure(state="disabled")
            self.log(f"BPM 设置为: {bpm:.1f}")
        except ValueError as e:
            messagebox.showerror("输入错误", "请输入有效的BPM值 (必须是正数)")

    def select_all_tracks(self):
        if not self.instruments:
            return
        self.track_listbox.select_set(0, tk.END)
        self.on_track_selection_change(None)

    def deselect_all_tracks(self):
        self.track_listbox.select_clear(0, tk.END)
        self.on_track_selection_change(None)

    def on_track_selection_change(self, event):
        selected_indices = self.track_listbox.curselection()
        self.selected_tracks = list(selected_indices)
        self.log(f"已选择 {len(selected_indices)} 个轨道: {[self.track_listbox.get(i) for i in selected_indices]}")

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
            self.ax.hlines(y=pitches, xmin=starts, xmax=ends, colors=colors(i), linewidth=2)
            
            # 图例代理
            self.ax.scatter([], [], color=colors(i), label=f"Track {i}")
        if len(self.instruments) <= 10:
            # 如果轨道太多就不显示图例了，防挡住画面
            self.ax.legend(loc='upper right', fontsize=8, facecolor='#2b2b2b', edgecolor='gray', labelcolor='white')
        self.fig.tight_layout()
        self.canvas.draw()

    def play_preview(self):
        if not self.instruments or not self.selected_tracks:
            return
        # 播放第一个选中的轨道
        track_idx = self.selected_tracks[0]
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

    def extract_selected_notes(self):
        if not self.instruments or not self.selected_tracks:
            self.log("请选择至少一个轨道进行提取。")
            return

        all_output_data = {}
        failed_tracks = []

        for track_idx in self.selected_tracks:
            selected_inst = self.instruments[track_idx]
            if not selected_inst.notes:
                self.log(f"警告: 轨道 {track_idx} 没有音符，无法提取。")
                failed_tracks.append(track_idx)
                continue

            self.log(f"正在提取轨道 {track_idx} 的数据...")
            
            output_data = []
            
            # 如果设置了新的BPM，则进行时间转换
            if self.current_bpm and self.original_bpm and self.current_bpm != self.original_bpm:
                # 计算BPM比率用于时间转换
                time_ratio = self.original_bpm / self.current_bpm
                
                for note in selected_inst.notes:
                    # 调整时间戳
                    adjusted_start_time = note.start * time_ratio
                    output_data.append({
                        "pitch": note.pitch,
                        "start_time": round(adjusted_start_time, 4)
                    })
            else:
                # 如果BPM没有改变，使用原始时间戳
                for note in selected_inst.notes:
                    output_data.append({
                        "pitch": note.pitch,
                        "start_time": round(note.start, 4)
                    })
            
            output_data.sort(key=lambda x: x["start_time"])
            track_name = selected_inst.name or f"Track_{track_idx}"
            all_output_data[track_name] = {
                "track_index": track_idx,
                "notes": output_data
            }

        if all_output_data:
            self.current_output_data = all_output_data  # 保存到内存供导出使用
            output_json = json.dumps(all_output_data, indent=4, ensure_ascii=False)
            self.textbox.delete("1.0", "end")
            self.textbox.insert("0.0", output_json)
            
            # 显示BPM信息
            bpm_info = f" (BPM: {self.current_bpm:.1f})" if self.current_bpm else ""
            success_count = len(self.selected_tracks) - len(failed_tracks)
            self.log(f"✅ 批量提取完成！成功 {success_count} 个轨道{bpm_info}。可点击导出按钮保存。")
            
            # 启用导出按钮
            self.btn_export_single.configure(state="normal")
        else:
            self.log("❌ 没有任何轨道成功提取。")

    def export_data(self):
        if not self.current_output_data:
            self.log("没有数据可供导出。")
            return
        save_path = filedialog.asksaveasfilename(
            title="保存 JSON 数据",
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")]
        )
        if save_path:
            try:
                with open(save_path, 'w', encoding='utf-8') as f:
                    json.dump(self.current_output_data, f, indent=4, ensure_ascii=False)
                self.log(f"💾 数据已成功导出至: {save_path}")
            except Exception as e:
                self.log(f"导出失败: {e}")
                messagebox.showerror("导出错误", str(e))

    def export_batch(self):
        if not self.instruments or not self.selected_tracks:
            self.log("请选择至少一个轨道进行批量导出。")
            return
        
        if not self.output_folder:
            self.log("请先选择输出文件夹。")
            self.select_output_folder()
            if not self.output_folder:
                return

        success_count = 0
        failed_tracks = []

        for track_idx in self.selected_tracks:
            selected_inst = self.instruments[track_idx]
            if not selected_inst.notes:
                self.log(f"警告: 轨道 {track_idx} 没有音符，跳过导出。")
                failed_tracks.append(track_idx)
                continue

            # 提取音符数据
            output_data = []
            
            # 如果设置了新的BPM，则进行时间转换
            if self.current_bpm and self.original_bpm and self.current_bpm != self.original_bpm:
                # 计算BPM比率用于时间转换
                time_ratio = self.original_bpm / self.current_bpm
                
                for note in selected_inst.notes:
                    # 调整时间戳
                    adjusted_start_time = note.start * time_ratio
                    output_data.append({
                        "pitch": note.pitch,
                        "start_time": round(adjusted_start_time, 4)
                    })
            else:
                # 如果BPM没有改变，使用原始时间戳
                for note in selected_inst.notes:
                    output_data.append({
                        "pitch": note.pitch,
                        "start_time": round(note.start, 4)
                    })
            
            output_data.sort(key=lambda x: x["start_time"])
            
            # 生成文件名
            track_name = selected_inst.name or f"Track_{track_idx}"
            # 替换非法字符
            safe_track_name = "".join(c for c in track_name if c.isalnum() or c in (' ', '-', '_', '.')).rstrip()
            if not safe_track_name:
                safe_track_name = f"Track_{track_idx}"
            
            file_path = os.path.join(self.output_folder, f"{safe_track_name}.json")
            
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, indent=4, ensure_ascii=False)
                self.log(f"💾 轨道 {track_idx} ({track_name}) 数据已导出至: {file_path}")
                success_count += 1
            except Exception as e:
                self.log(f"导出轨道 {track_idx} 时出错: {e}")
                failed_tracks.append(track_idx)

        total_selected = len(self.selected_tracks)
        self.log(f"📦 批量导出完成！成功: {success_count}, 失败: {len(failed_tracks)}, 总计: {total_selected}")

    def log(self, message):
        self.textbox.insert("end", f"\n[System] {message}")
        self.textbox.see("end")

    def on_closing(self):
        """窗口关闭时的清理工作"""
        self.stop_preview()
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