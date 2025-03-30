import tkinter as tk
from tkinter import ttk, messagebox
from dmc_cache import DirectMappedCache  # นำเข้าคลาสจาก dmc_cache.py
import math
import random

class DMCGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Direct Mapped Cache GUI (Lines & Log in Main Window)")
        
        # Variables
        self.var_cache_size = tk.StringVar(value="32")
        self.var_block_size = tk.StringVar(value="4")
        self.var_num_access = tk.StringVar(value="10")
        
        self.sim = None
        self.address_list = []
        self.current_step = 0
        
        # Flag สำหรับ Auto Run
        self.auto_running = False
        
        self.create_widgets()
    
    def create_widgets(self):
        # -- ส่วนกรอกพารามิเตอร์ --
        frame_top = tk.LabelFrame(self.root, text="Cache Parameters", padx=10, pady=10)
        frame_top.pack(padx=10, pady=5, fill="x")
        
        tk.Label(frame_top, text="Cache Size (Bytes):").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame_top, textvariable=self.var_cache_size, width=10).grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(frame_top, text="Block Size (Bytes):").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame_top, textvariable=self.var_block_size, width=10).grid(row=1, column=1, padx=5, pady=5)
        
        tk.Label(frame_top, text="Number of Accesses:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(frame_top, textvariable=self.var_num_access, width=10).grid(row=2, column=1, padx=5, pady=5)       
        
        # -- ส่วนปุ่มควบคุม --
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(padx=10, pady=5, fill="x")
        
        btn_start = tk.Button(frame_buttons, text="Start Simulation", command=self.start_simulation)
        btn_start.pack(side="left", padx=5)
        
        self.btn_next_step = tk.Button(frame_buttons, text="Next Step", command=self.do_next_step, state="disabled")
        self.btn_next_step.pack(side="left", padx=5)
        
        # ปุ่ม Auto Run
        self.btn_auto_run = tk.Button(frame_buttons, text="Auto Run", command=self.start_auto_run, state="disabled")
        self.btn_auto_run.pack(side="left", padx=5)
        
        # ปุ่ม Run All (ใหม่)
        self.btn_run_all = tk.Button(frame_buttons, text="Run All", command=self.run_all, state="disabled")
        self.btn_run_all.pack(side="left", padx=5)
        
        # ปุ่ม Stop (ใหม่)
        self.btn_stop = tk.Button(frame_buttons, text="Stop", command=self.stop_run, state="disabled")
        self.btn_stop.pack(side="left", padx=5)
        
        # -- Frame กลาง: Text + ตาราง
        frame_center = tk.Frame(self.root)
        frame_center.pack(padx=10, pady=10, fill="both", expand=True)

        # Text สำหรับแสดงผล Access Step
        self.text_result = tk.Text(frame_center, width=45)
        self.text_result.pack(side="left", fill="both", expand=True)
        
        # -- Frame ด้านขวา: ใส่ 2 ตาราง (Cache Lines / Access Log) ซ้อนกัน
        frame_tables = tk.Frame(frame_center)
        frame_tables.pack(side="left", padx=10, fill="both", expand=True)
        
        # ตาราง Cache Lines
        lbl_lines = tk.Label(frame_tables, text="Cache Lines", font=("Arial", 10, "bold"))
        lbl_lines.pack()
        
        columns_lines = ("Index", "Valid", "TagHex")
        self.tree_cache = ttk.Treeview(frame_tables, columns=columns_lines, show="headings", height=8)
        self.tree_cache.pack(pady=5, fill="x")
        
        self.tree_cache.heading("Index", text="Line Index")
        self.tree_cache.heading("Valid", text="Valid")
        self.tree_cache.heading("TagHex", text="Tag (Hex)")
        
        self.tree_cache.column("Index", width=60, anchor="center")
        self.tree_cache.column("Valid", width=60, anchor="center")
        self.tree_cache.column("TagHex", width=80, anchor="center")
        
        # ตาราง Access Log
        lbl_log = tk.Label(frame_tables, text="Access Log", font=("Arial", 10, "bold"))
        lbl_log.pack()
        
        columns_log = ("No", "AddrHex", "Offset", "Index", "TagHex", "HitMiss")
        self.tree_log = ttk.Treeview(frame_tables, columns=columns_log, show="headings", height=8)
        self.tree_log.pack(pady=5, fill="x")
        
        self.tree_log.heading("No", text="#")
        self.tree_log.heading("AddrHex", text="Address (Hex)")
        self.tree_log.heading("Offset", text="Offset")
        self.tree_log.heading("Index", text="Index")
        self.tree_log.heading("TagHex", text="Tag (Hex)")
        self.tree_log.heading("HitMiss", text="Hit/Miss")
        
        self.tree_log.column("No", width=30, anchor="center")
        self.tree_log.column("AddrHex", width=70, anchor="center")
        self.tree_log.column("Offset", width=50, anchor="center")
        self.tree_log.column("Index", width=50, anchor="center")
        self.tree_log.column("TagHex", width=60, anchor="center")
        self.tree_log.column("HitMiss", width=60, anchor="center")
    
    def start_simulation(self):
        """เริ่ม simulation ใหม่: สร้างหรือ reset cache, สุ่ม address, เปิดปุ่ม Next/Auto/RunAll/Stop"""
        self.text_result.delete("1.0", tk.END)
        
        # ยกเลิก auto run ถ้ากำลังทำอยู่
        self.auto_running = False
        
        # อ่านค่าพารามิเตอร์
        try:
            csize = int(self.var_cache_size.get())
            bsize = int(self.var_block_size.get())
            nacc = int(self.var_num_access.get())
            if csize <= 0 or bsize <= 0 or nacc <= 0:
                raise ValueError("ต้องเป็นจำนวนบวกเท่านั้น")
        except ValueError as e:
            messagebox.showerror("Error", f"Input Error: {e}")
            return
        
        if not self.sim:
            # ยังไม่เคยมี simulator -> สร้างใหม่
            self.sim = DirectMappedCache(csize, bsize, 32)
        else:
            # เคยมี -> อัปเดตค่าแล้ว reset
            self.sim.cache_size = csize
            self.sim.block_size = bsize
            self.sim.num_lines = max(1, csize // bsize)
            self.sim.offset_bits = int(math.log2(bsize)) if bsize > 1 else 0
            self.sim.index_bits = int(math.log2(self.sim.num_lines)) if self.sim.num_lines > 1 else 0
            self.sim.reset()
        
        # สุ่ม address
        self.address_list = [random.randint(0, 255) for _ in range(nacc)]
        self.current_step = 0
        
        # อัปเดตข้อความ
        self.text_result.insert(tk.END, "Simulation Started!\n")
        self.text_result.insert(tk.END, f"Cache Size={csize}, Block Size={bsize}, Accesses={nacc}\n")
        self.text_result.insert(tk.END, "Address range [0..255]\n")
        self.text_result.insert(tk.END, "Use 'Next Step' / 'Auto Run' / 'Run All'\n\n")
        
        # อัปเดตตาราง cache lines + log ให้ว่าง
        self.update_cache_lines_table()
        self.update_access_log_table()
        
        # เปิดปุ่ม
        self.btn_next_step.config(state="normal")
        self.btn_auto_run.config(state="normal")
        self.btn_run_all.config(state="normal")
        self.btn_stop.config(state="disabled")  # ยังไม่ต้อง stop จนกว่าจะ auto run
    
    def do_next_step(self):
        """ทำทีละ 1 Step (Access 1 ครั้ง)"""
        if self.current_step >= len(self.address_list):
            self.finish_simulation()
            return
        
        addr = self.address_list[self.current_step]
        self.sim.access(addr)
        self.current_step += 1
        
        # ดึงสถิติ
        stats = self.sim.get_stats()
        
        # เอารายการล่าสุดใน access_log
        last_access = self.sim.access_log[-1]
        address, offset, index, tag, is_hit = last_access
        
        # แสดงใน text
        self.text_result.insert(tk.END, f"Step #{self.current_step}: Address=0x{address:X}\n")
        self.text_result.insert(tk.END, f"  offset={offset}, index={index}, tag=0x{tag:X}\n")
        if is_hit:
            self.text_result.insert(tk.END, "  => HIT\n")
        else:
            self.text_result.insert(tk.END, "  => MISS\n")
        self.text_result.insert(tk.END, f"  Hit={stats['hit_count']} Miss={stats['miss_count']} (Hit Rate={stats['hit_rate']:.3f})\n\n")
        
        # อัปเดตตาราง
        self.update_cache_lines_table()
        self.update_access_log_table()
        
        # เช็คจบ
        if self.current_step >= len(self.address_list):
            self.finish_simulation()
    
    def finish_simulation(self):
        self.text_result.insert(tk.END, "All steps completed.\n")
        self.btn_next_step.config(state="disabled")
        self.btn_auto_run.config(state="disabled")
        self.btn_run_all.config(state="disabled")
        self.btn_stop.config(state="disabled")
        self.auto_running = False
    
    def update_cache_lines_table(self):
        """อัปเดตข้อมูลใน Treeview ของ Cache Lines ให้ตรงกับ self.sim.lines"""
        # เคลียร์ของเก่า
        for item in self.tree_cache.get_children():
            self.tree_cache.delete(item)
        
        if not self.sim:
            return
        
        # ใส่ข้อมูลตาม line
        for i, line in enumerate(self.sim.lines):
            valid_str = "1" if line.valid else "0"
            tag_hex = f"{line.tag:X}" if line.tag is not None else "-"
            self.tree_cache.insert("", "end", values=(i, valid_str, tag_hex))
    
    def update_access_log_table(self):
        """อัปเดตข้อมูลใน Treeview ของ Access Log ให้ตรงกับ self.sim.access_log"""
        for item in self.tree_log.get_children():
            self.tree_log.delete(item)
        
        if not self.sim:
            return
        
        for i, (addr, offset, index, tag, is_hit) in enumerate(self.sim.access_log, start=1):
            addr_hex = f"{addr:X}"
            tag_hex = f"{tag:X}"
            hm_str = "HIT" if is_hit else "MISS"
            self.tree_log.insert("", "end", values=(i, addr_hex, offset, index, tag_hex, hm_str))
    
    def start_auto_run(self):
        """กดปุ่ม Auto Run แล้วให้รันอัตโนมัติจนจบ หรือจนกด Stop"""
        if not self.sim or self.current_step >= len(self.address_list):
            return
        
        self.auto_running = True
        self.btn_auto_run.config(state="disabled")
        self.btn_stop.config(state="normal")  # เปิดให้หยุดได้
        self.btn_run_all.config(state="disabled")  # กันไม่ให้กด Run All ซ้อน
        self.auto_run_step()
    
    def auto_run_step(self):
        """ฟังก์ชันเรียกซ้ำผ่าน after() เพื่อรันต่อเนื่อง"""
        if (not self.auto_running) or (self.current_step >= len(self.address_list)):
            # หยุดเพราะกด Stop หรือวิ่งครบ
            self.auto_running = False
            self.btn_stop.config(state="disabled")
            return
        
        # ทำ 1 step
        self.do_next_step()
        
        # ถ้ายังเหลือ address -> ทำต่อ
        if self.current_step < len(self.address_list):
            self.root.after(500, self.auto_run_step)
        else:
            # จบแล้ว
            self.auto_running = False
            self.btn_stop.config(state="disabled")
    
    def stop_run(self):
        """หยุดการ auto run กลางคัน"""
        if self.auto_running:
            self.auto_running = False
            self.btn_stop.config(state="disabled")
            self.btn_auto_run.config(state="normal")
            self.btn_run_all.config(state="normal")
            self.text_result.insert(tk.END, "Auto Run stopped.\n")
    
    def run_all(self):
        """รันต่อเนื่องจนจบในคราวเดียว (ไม่มี delay)"""
        # ปิด auto run ถ้ามี
        self.auto_running = False
        self.btn_auto_run.config(state="disabled")
        self.btn_stop.config(state="disabled")
        
        while self.current_step < len(self.address_list):
            self.do_next_step()
            # ถ้า do_next_step ทำจบแล้วจะ break ออก
            if self.current_step >= len(self.address_list):
                break