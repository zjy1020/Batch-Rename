import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path
import re


class BatchRenameTool:
    def __init__(self, root):
        self.root = root
        self.root.title("批量重命名工具")
        self.root.geometry("900x600")
        
        self.current_folder = None
        self.file_list = []  # 存储 (原路径, 新名称) 的列表
        self.editing_item = None  # 当前正在编辑的项目
        
        self.setup_ui()
    
    def setup_ui(self):
        # 顶部工具栏
        toolbar_frame = tk.Frame(self.root, pady=10)
        toolbar_frame.pack(fill=tk.X, padx=10)
        
        # 选择文件夹按钮
        self.folder_btn = tk.Button(
            toolbar_frame,
            text="选择文件夹",
            command=self.select_folder,
            width=12,
            height=2
        )
        self.folder_btn.pack(side=tk.LEFT, padx=5)
        
        # 刷新按钮
        self.refresh_btn = tk.Button(
            toolbar_frame,
            text="刷新",
            command=self.refresh_files,
            width=12,
            height=2,
            state=tk.DISABLED
        )
        self.refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # 格式重命名按钮
        self.format_btn = tk.Button(
            toolbar_frame,
            text="格式重命名",
            command=self.format_rename,
            width=12,
            height=2,
            state=tk.DISABLED
        )
        self.format_btn.pack(side=tk.LEFT, padx=5)
        
        # 应用更改按钮
        self.apply_btn = tk.Button(
            toolbar_frame,
            text="应用更改",
            command=self.apply_changes,
            width=12,
            height=2,
            state=tk.DISABLED,
            bg="#4CAF50",
            fg="white"
        )
        self.apply_btn.pack(side=tk.LEFT, padx=5)
        
        # 处理按钮区域
        process_frame = tk.Frame(self.root, pady=5)
        process_frame.pack(fill=tk.X, padx=10)
        
        tk.Label(process_frame, text="批量处理（选中文件）:", font=("Arial", 9, "bold")).pack(side=tk.LEFT, padx=5)
        
        # 空格处理按钮
        self.space_btn = tk.Button(
            process_frame,
            text="空格→下划线",
            command=lambda: self.process_selected("space_to_underscore"),
            width=12,
            height=1,
            state=tk.DISABLED,
            bg="#2196F3",
            fg="white"
        )
        self.space_btn.pack(side=tk.LEFT, padx=3)
        
        # 下划线处理按钮
        self.underscore_btn = tk.Button(
            process_frame,
            text="下划线→空格",
            command=lambda: self.process_selected("underscore_to_space"),
            width=12,
            height=1,
            state=tk.DISABLED,
            bg="#2196F3",
            fg="white"
        )
        self.underscore_btn.pack(side=tk.LEFT, padx=3)
        
        # 去除空格按钮
        self.remove_space_btn = tk.Button(
            process_frame,
            text="去除空格",
            command=lambda: self.process_selected("remove_space"),
            width=12,
            height=1,
            state=tk.DISABLED,
            bg="#2196F3",
            fg="white"
        )
        self.remove_space_btn.pack(side=tk.LEFT, padx=3)
        
        # 去除下划线按钮
        self.remove_underscore_btn = tk.Button(
            process_frame,
            text="去除下划线",
            command=lambda: self.process_selected("remove_underscore"),
            width=12,
            height=1,
            state=tk.DISABLED,
            bg="#2196F3",
            fg="white"
        )
        self.remove_underscore_btn.pack(side=tk.LEFT, padx=3)
        
        # 去除横线按钮
        self.remove_dash_btn = tk.Button(
            process_frame,
            text="去除横线",
            command=lambda: self.process_selected("remove_dash"),
            width=12,
            height=1,
            state=tk.DISABLED,
            bg="#2196F3",
            fg="white"
        )
        self.remove_dash_btn.pack(side=tk.LEFT, padx=3)
        
        # 去除点号按钮
        self.remove_dot_btn = tk.Button(
            process_frame,
            text="去除点号",
            command=lambda: self.process_selected("remove_dot"),
            width=12,
            height=1,
            state=tk.DISABLED,
            bg="#2196F3",
            fg="white"
        )
        self.remove_dot_btn.pack(side=tk.LEFT, padx=3)
        
        # 当前文件夹显示
        self.folder_label = tk.Label(
            toolbar_frame,
            text="未选择文件夹",
            fg="gray",
            anchor="w"
        )
        self.folder_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # 文件列表框架
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建Treeview显示文件列表（支持多选）
        columns = ("原文件名", "新文件名")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="tree headings", height=20, selectmode='extended')
        
        # 设置列
        self.tree.heading("#0", text="序号")
        self.tree.heading("原文件名", text="原文件名")
        self.tree.heading("新文件名", text="新文件名（可编辑）")
        
        self.tree.column("#0", width=60, anchor="center")
        self.tree.column("原文件名", width=350, anchor="w")
        self.tree.column("新文件名", width=350, anchor="w")
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 绑定单击编辑事件
        self.tree.bind("<Button-1>", self.on_single_click)
        
        # 状态栏
        self.status_label = tk.Label(
            self.root,
            text="就绪",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padx=5
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def select_folder(self):
        """选择文件夹"""
        folder = filedialog.askdirectory(title="选择要重命名的文件夹")
        if folder:
            self.current_folder = folder
            self.folder_label.config(text=f"当前文件夹: {folder}", fg="black")
            self.load_files()
            self.refresh_btn.config(state=tk.NORMAL)
            self.format_btn.config(state=tk.NORMAL)
            self.apply_btn.config(state=tk.NORMAL)
            self.enable_process_buttons()
    
    def load_files(self):
        """加载文件夹中的所有文件"""
        if not self.current_folder:
            return
        
        self.tree.delete(*self.tree.get_children())
        self.file_list = []
        
        try:
            files = [f for f in os.listdir(self.current_folder) 
                    if os.path.isfile(os.path.join(self.current_folder, f))]
            files.sort()
            
            for idx, filename in enumerate(files, 1):
                file_path = os.path.join(self.current_folder, filename)
                self.file_list.append((file_path, filename))
                self.tree.insert("", tk.END, text=str(idx), values=(filename, filename))
            
            self.status_label.config(text=f"已加载 {len(files)} 个文件")
        except Exception as e:
            messagebox.showerror("错误", f"加载文件时出错: {str(e)}")
            self.status_label.config(text="加载文件失败")
    
    def refresh_files(self):
        """刷新文件列表"""
        if self.current_folder:
            self.load_files()
            self.enable_process_buttons()
            self.status_label.config(text="文件列表已刷新")
    
    def on_single_click(self, event):
        """单击事件，直接开始编辑"""
        # 如果当前有正在编辑的项目，先保存它
        if self.editing_item:
            self.save_current_edit()
        
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            if column == "#2":  # 新文件名列
                # 使用 identify_row 直接获取被点击的项目
                item = self.tree.identify_row(event.y)
                if item:
                    # 延迟一下，确保选择已经更新，但不要太长
                    self.root.after(50, lambda i=item: self.start_edit(i))
    
    def start_edit(self, item):
        """开始编辑单元格"""
        # 如果已经有编辑框，先保存
        if self.editing_item and self.editing_item != item:
            self.save_current_edit()
        
        # 如果正在编辑同一个项目，不重复创建
        if self.editing_item == item and hasattr(self, 'edit_entry'):
            try:
                if self.edit_entry.winfo_exists():
                    return
            except:
                pass
        
        # 获取当前值
        values = self.tree.item(item, "values")
        if not values:
            return
        
        # 获取列的位置
        column = "#2"
        bbox = self.tree.bbox(item, column)
        if not bbox:
            return
        
        # 创建编辑框
        self.editing_item = item
        self.edit_entry = tk.Entry(self.tree, width=bbox[2])
        self.edit_entry.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
        self.edit_entry.insert(0, values[1] if len(values) > 1 else "")
        self.edit_entry.select_range(0, tk.END)
        self.edit_entry.focus()
        
        def save_edit(event=None):
            self.save_current_edit()
        
        def cancel_edit(event=None):
            if hasattr(self, 'edit_entry'):
                try:
                    self.edit_entry.destroy()
                except:
                    pass
            self.editing_item = None
        
        def on_focus_out(event=None):
            # 延迟保存，避免与单击事件冲突
            self.root.after(200, self.save_current_edit)
        
        self.edit_entry.bind("<Return>", save_edit)
        self.edit_entry.bind("<FocusOut>", on_focus_out)
        self.edit_entry.bind("<Escape>", cancel_edit)
        # Entry 默认支持 Ctrl+Z 撤销，无需额外配置
    
    def save_current_edit(self):
        """保存当前编辑的内容"""
        if not hasattr(self, 'edit_entry') or not self.editing_item:
            return
        
        try:
            item = self.editing_item
            new_name = self.edit_entry.get().strip()
            
            if new_name:
                # 更新Treeview
                self.tree.set(item, "新文件名", new_name)
                # 更新file_list
                idx = int(self.tree.item(item, "text")) - 1
                if 0 <= idx < len(self.file_list):
                    old_path, old_name = self.file_list[idx]
                    self.file_list[idx] = (old_path, new_name)
        except Exception as e:
            # 如果出错，只记录，不中断
            pass
        finally:
            # 确保清理编辑框
            try:
                if hasattr(self, 'edit_entry'):
                    self.edit_entry.destroy()
            except:
                pass
            self.editing_item = None
    
    def format_rename(self):
        """格式重命名对话框"""
        if not self.file_list:
            messagebox.showwarning("警告", "没有可重命名的文件")
            return
        
        # 创建格式输入对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("格式重命名")
        dialog.geometry("500x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 说明文本
        info_text = """
格式说明：
  {name} - 原文件名（不含扩展名）
  {ext} - 文件扩展名
  {num} - 序号（从1开始）
  {num:03d} - 序号，3位数字，不足补0（如：001, 002）
  
示例：
  {num:03d}_{name} - 001_原文件名.txt
  {name}_{num} - 原文件名_1.txt
  新名称_{num:03d}{ext} - 新名称_001.txt
        """
        
        tk.Label(dialog, text=info_text, justify=tk.LEFT, anchor="w").pack(padx=20, pady=10, fill=tk.X)
        
        # 格式输入框
        format_frame = tk.Frame(dialog)
        format_frame.pack(padx=20, pady=10, fill=tk.X)
        
        tk.Label(format_frame, text="格式:").pack(side=tk.LEFT)
        format_entry = tk.Entry(format_frame, width=40)
        format_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        format_entry.insert(0, "{num:03d}_{name}{ext}")
        format_entry.focus()
        
        # 预览区域
        preview_frame = tk.Frame(dialog)
        preview_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        tk.Label(preview_frame, text="预览（前5个文件）:").pack(anchor="w")
        
        preview_text = tk.Text(preview_frame, height=8, width=50)
        preview_scroll = ttk.Scrollbar(preview_frame, orient=tk.VERTICAL, command=preview_text.yview)
        preview_text.configure(yscrollcommand=preview_scroll.set)
        preview_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        preview_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        def update_preview(event=None):
            """更新预览"""
            format_str = format_entry.get().strip()
            if not format_str:
                preview_text.delete(1.0, tk.END)
                return
            
            preview_text.delete(1.0, tk.END)
            for i, (file_path, old_name) in enumerate(self.file_list[:5], 1):
                try:
                    path_obj = Path(old_name)
                    name_without_ext = path_obj.stem
                    ext = path_obj.suffix
                    
                    new_name = format_str.format(
                        name=name_without_ext,
                        ext=ext,
                        num=i,
                        num03d=f"{i:03d}",
                        num04d=f"{i:04d}",
                        num05d=f"{i:05d}"
                    )
                    preview_text.insert(tk.END, f"{old_name} → {new_name}\n")
                except Exception as e:
                    preview_text.insert(tk.END, f"{old_name} → 错误: {str(e)}\n")
        
        format_entry.bind("<KeyRelease>", update_preview)
        update_preview()
        
        # 按钮
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(padx=20, pady=10)
        
        def apply_format():
            format_str = format_entry.get().strip()
            if not format_str:
                messagebox.showwarning("警告", "请输入格式")
                return
            
            try:
                # 应用格式到所有文件
                for i, (file_path, old_name) in enumerate(self.file_list, 1):
                    path_obj = Path(old_name)
                    name_without_ext = path_obj.stem
                    ext = path_obj.suffix
                    
                    new_name = format_str.format(
                        name=name_without_ext,
                        ext=ext,
                        num=i,
                        num03d=f"{i:03d}",
                        num04d=f"{i:04d}",
                        num05d=f"{i:05d}"
                    )
                    
                    # 更新Treeview
                    item = self.tree.get_children()[i - 1]
                    self.tree.set(item, "新文件名", new_name)
                    # 更新file_list
                    self.file_list[i - 1] = (file_path, new_name)
                
                self.status_label.config(text=f"已应用格式重命名到 {len(self.file_list)} 个文件")
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("错误", f"应用格式时出错: {str(e)}")
        
        tk.Button(btn_frame, text="应用", command=apply_format, width=10).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="取消", command=dialog.destroy, width=10).pack(side=tk.LEFT, padx=5)
    
    def apply_changes(self):
        """应用所有更改"""
        if not self.file_list:
            return
        
        # 检查是否有重名冲突
        new_names = [name for _, name in self.file_list]
        if len(new_names) != len(set(new_names)):
            messagebox.showerror("错误", "存在重复的文件名，请检查后重试")
            return
        
        # 确认对话框
        result = messagebox.askyesno(
            "确认",
            f"确定要重命名 {len(self.file_list)} 个文件吗？\n此操作不可撤销！"
        )
        
        if not result:
            return
        
        success_count = 0
        error_count = 0
        errors = []
        
        # 先检查所有新文件名是否有效
        for file_path, new_name in self.file_list:
            if not new_name or new_name.strip() == "":
                errors.append(f"文件名不能为空: {os.path.basename(file_path)}")
                error_count += 1
                continue
            
            # 检查非法字符
            invalid_chars = '<>:"/\\|?*'
            if any(char in new_name for char in invalid_chars):
                errors.append(f"文件名包含非法字符: {new_name}")
                error_count += 1
                continue
        
        if errors:
            error_msg = "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n... 还有 {len(errors) - 10} 个错误"
            messagebox.showerror("错误", f"发现以下错误:\n{error_msg}")
            return
        
        # 执行重命名（先重命名到临时名称，避免冲突）
        temp_renames = []
        try:
            # 第一步：重命名为临时名称
            for file_path, new_name in self.file_list:
                old_name = os.path.basename(file_path)
                if old_name == new_name:
                    continue  # 名称未改变，跳过
                
                temp_name = f"__TEMP__{os.urandom(8).hex()}_{new_name}"
                temp_path = os.path.join(self.current_folder, temp_name)
                temp_renames.append((file_path, temp_path, new_name))
                os.rename(file_path, temp_path)
            
            # 第二步：从临时名称重命名为最终名称
            for old_path, temp_path, new_name in temp_renames:
                new_path = os.path.join(self.current_folder, new_name)
                os.rename(temp_path, new_path)
                success_count += 1
            
            messagebox.showinfo("成功", f"成功重命名 {success_count} 个文件")
            self.status_label.config(text=f"成功重命名 {success_count} 个文件")
            self.refresh_files()
            
        except Exception as e:
            # 如果出错，尝试恢复
            for old_path, temp_path, _ in temp_renames:
                try:
                    if os.path.exists(temp_path):
                        os.rename(temp_path, old_path)
                except:
                    pass
            
            messagebox.showerror("错误", f"重命名时出错: {str(e)}")
            self.status_label.config(text="重命名失败")
    
    def enable_process_buttons(self):
        """启用处理按钮"""
        self.space_btn.config(state=tk.NORMAL)
        self.underscore_btn.config(state=tk.NORMAL)
        self.remove_space_btn.config(state=tk.NORMAL)
        self.remove_underscore_btn.config(state=tk.NORMAL)
        self.remove_dash_btn.config(state=tk.NORMAL)
        self.remove_dot_btn.config(state=tk.NORMAL)
    
    def process_selected(self, process_type):
        """处理选中的文件"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("警告", "请先选择要处理的文件")
            return
        
        # 获取选中项的索引
        selected_indices = []
        for item in selected_items:
            try:
                idx = int(self.tree.item(item, "text")) - 1
                if 0 <= idx < len(self.file_list):
                    selected_indices.append((item, idx))
            except:
                continue
        
        if not selected_indices:
            messagebox.showwarning("警告", "没有有效的选中文件")
            return
        
        # 应用处理
        count = 0
        for item, idx in selected_indices:
            file_path, current_name = self.file_list[idx]
            path_obj = Path(current_name)
            name_without_ext = path_obj.stem
            ext = path_obj.suffix
            
            # 根据处理类型修改文件名
            new_name_without_ext = self.apply_process(name_without_ext, process_type)
            new_name = new_name_without_ext + ext
            
            # 更新Treeview和file_list
            self.tree.set(item, "新文件名", new_name)
            self.file_list[idx] = (file_path, new_name)
            count += 1
        
        self.status_label.config(text=f"已处理 {count} 个文件")
    
    def apply_process(self, name, process_type):
        """应用处理规则到文件名"""
        if process_type == "space_to_underscore":
            # 空格替换为下划线
            return name.replace(" ", "_")
        elif process_type == "underscore_to_space":
            # 下划线替换为空格
            return name.replace("_", " ")
        elif process_type == "remove_space":
            # 去除所有空格
            return name.replace(" ", "")
        elif process_type == "remove_underscore":
            # 去除所有下划线
            return name.replace("_", "")
        elif process_type == "remove_dash":
            # 去除所有横线（连字符）
            return name.replace("-", "")
        elif process_type == "remove_dot":
            # 去除所有点号（除了扩展名的点）
            return name.replace(".", "")
        else:
            return name
    
def main():
    root = tk.Tk()
    app = BatchRenameTool(root)
    root.mainloop()


if __name__ == "__main__":
    main()

