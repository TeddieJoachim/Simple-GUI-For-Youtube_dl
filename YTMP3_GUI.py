import tkinter as tk
import customtkinter as ctk
import youtube_dl
import os
import shutil


class MainApplication(ctk.CTkFrame):
    def __init__(self, parent, *args, **kwargs):
        ctk.CTkFrame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("dark-blue")

        self.quit_button = ctk.CTkButton(text='Quit', command=lambda:quit_program(self))
        self.quit_button.pack(anchor=tk.NW)

        self.lbl_title = ctk.CTkLabel(text='Enter a valid YouTube URL below. Wait for it to finish, then click next to add it to the queue. \nFor playlists, you will then have to click seek all to add the rest of the files to your queue.', text_font=('Robotica', 15))
        self.lbl_title.pack(pady=20)

        self.ent_url = ctk.CTkEntry(width=500)
        self.ent_url.pack(pady=10)
        
        self.btn_download = ctk.CTkButton(master=root, width=150, height=50, text='Download', command=lambda:download_url(self))
        self.btn_download.pack(pady=10)

        self.btn_next = ctk.CTkButton(master=root, width=150, height=50, text='Next/Enqueue', command=lambda:add_to_queue(self))
        self.btn_next.configure(state=ctk.DISABLED)
        self.btn_next.pack(pady=10)

        self.ent_path = ctk.CTkEntry(width=250, placeholder_text='Example: Users/ted/Desktop')
        self.ent_path.pack(pady=10)

        self.lbl_queue = ctk.CTkLabel(text='Below is the queue. After being added to the queue, \nfiles can be shuttled to the directory specified above.', text_font = ('Robotica', 15))
        self.lbl_queue.pack(pady=10)

        self.vert_scroller = tk.Scrollbar(orient=tk.VERTICAL)
        self.lbox_shuttle_queue = tk.Listbox(master=root, width=70, height=15, selectmode='extended')
        self.lbox_shuttle_queue.pack(pady=15)
        self.lbox_shuttle_queue.config(yscrollcommand=self.vert_scroller.set)
        self.vert_scroller.config(command=self.lbox_shuttle_queue.yview)

        self.btn_shuttle = ctk.CTkButton(master=root, width=150, height=50, text='Shuttle Files', command=lambda:shuttle_files(self))
        self.btn_shuttle.pack(pady=10)

        self.btn_seek_all = ctk.CTkButton(master=root, text='Seek all', width=150, height=50, command=lambda:seek_all(self))
        self.btn_seek_all.pack(pady=10)

        self.file_id = []
        self.shuttle_id_queue = []


        def display_downloader_warning(self, error_code):
            self.btn_download.configure(state=tk.DISABLED)
            self.btn_next.configure(state=tk.DISABLED)
            self.btn_shuttle.configure(state=tk.DISABLED)
            self.btn_seek_all.configure(state=tk.DISABLED)
            self.error_window = ctk.CTkToplevel(self)
            self.error_window.geometry('400x200')
            error_label = ctk.CTkLabel(master=self.error_window, text=f'Error: {error_code}')
            error_label.pack(pady=10)
            clear_errors = ctk.CTkButton(master=self.error_window, text='OK', width=100, height=50, command=lambda:clear_error_window(self))
            clear_errors.pack(pady=30)


        def clear_error_window(self):
            self.btn_download.configure(state=tk.NORMAL)
            self.btn_next.configure(state=tk.NORMAL)
            self.btn_shuttle.configure(state=tk.NORMAL)
            self.btn_seek_all.configure(state=tk.NORMAL)
            self.error_window.destroy()


        ydl_opts = {
            'format': 'bestaudio/best',
            'cachedir':False,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        
        def download_url(self):
            download_id = []
            full_url = self.ent_url.get()
            if full_url == '':
                display_downloader_warning(self, error_code='Empty URL field!')
                return None
            v_equal_slice = full_url.split('watch?v=', 1)
            v_equal_string = v_equal_slice.pop(-1)
            final_id = v_equal_string[0:11]
            if len(final_id) != 11:
                display_downloader_warning(self, error_code='Failed to extract proper ID.')
                return None
            download_id.append(final_id)
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                filenames = [self.ent_url.get()] 
                try:
                    ydl.download(filenames)
                    send_it = download_id.pop(0)
                    self.file_id.append(send_it)
                    self.btn_next.configure(state=tk.NORMAL)
                except:
                    display_downloader_warning(self, error_code=f'Try again! May have been a forbidden HTTP error. Or {filenames} is invalid.')
                    self.file_id.clear()
                    download_id.clear()
                    return None


        def add_to_queue(self):
            self.ent_url.delete(0, 'end')
            if len(self.file_id[0]) != 11:
                display_downloader_warning(self, error_code='File ID improperly formatted. Tell Ted there is an error in the enqueue.')
                return None
            else:
                user_directory = os.getcwd()
                id_to_add = self.file_id.pop(0)
                if id_to_add in self.shuttle_id_queue:
                    display_downloader_warning(self, error_code='Found duplicate ID entering the queue, popped it off and returned none, carry on.')
                    return None
                self.shuttle_id_queue.append(id_to_add)
                with os.scandir(user_directory) as new_files:
                    matching_file = [file.name for file in new_files if id_to_add in file.name]
                    file_name = matching_file.pop(0)
                self.lbox_shuttle_queue.insert(tk.END, file_name)   


        def shuttle_files(self):
            user_directory = os.getcwd()
            ids_to_dequeue = []
            user_destination = self.ent_path.get()
            try:
                assert os.path.exists(user_destination)
            except:
                display_downloader_warning(self, error_code=f'Invalid destination choice: {user_destination}')
                return None
            paths = []
            selected_file_tuple = self.lbox_shuttle_queue.curselection()
            selected_file_list = [i for i in selected_file_tuple]
            if len(selected_file_list) == 0:
                display_downloader_warning(self, error_code='Select files to shuttle them!')
                return None
            index = selected_file_list[0]
            while len(paths) != len(selected_file_list):
                selected_file_id = self.shuttle_id_queue[index]
                with os.scandir(user_directory) as file_names:
                    for file in file_names:
                        if selected_file_id in file.name:
                            selected_file_path = file.path
                            paths.append(selected_file_path)
                            ids_to_dequeue.append(selected_file_id)
                    index += 1
            iter_count = 0
            while len(paths) > 0:
                path_to_send = paths.pop(0)
                shutil.move(path_to_send, user_destination)
                iter_count += 1
            self.lbox_shuttle_queue.delete(selected_file_list[0], selected_file_list[-1])
            self.shuttle_id_queue = [id for id in self.shuttle_id_queue if id not in ids_to_dequeue]
        

        def seek_all(self):
            seek_all_id_queue = []
            mp3_s = []
            user_directory = os.getcwd()
            with os.scandir(user_directory) as files:
                for file in files:
                    if '.mp3' in file.name:
                        file_id = file.name[-15:-4]
                        seek_all_id_queue.append(file_id)
                        mp3_s.append(file)
                    continue
            if len(mp3_s) == 0:
                display_downloader_warning(self, error_code='No files with mp3 extensions were found.')
                return None
            id_already_in_queue_check = [i for i in self.shuttle_id_queue if i in seek_all_id_queue]
            if len(id_already_in_queue_check) > 0:
                seek_all_id_queue = [id for id in seek_all_id_queue if id not in id_already_in_queue_check]
            iter_count = 0
            while len(seek_all_id_queue) > 0:
                seek_all_id_to_dequeue = seek_all_id_queue.pop(0)
                self.file_id.append(seek_all_id_to_dequeue)
                add_to_queue(self)
                iter_count += 1


        def quit_program(self):
            lonely_files = []
            user_dir = os.getcwd()
            with os.scandir(user_dir) as files:
                for file in files:
                    if '.mp3' in file.name:
                        lonely_files.append(file.name)
                    continue
                if len(lonely_files) == 0:
                    root.destroy()
                if len(lonely_files) > 0:
                    self.lonely_file_warning = ctk.CTkLabel(text='There appear to be mp3 files in your current working directory.\nYou should be able to find them there, if not, there may have been an error.')
                    self.lonely_file_warning.pack()
                    self.user_choice = ctk.CTkButton(text='Click me to quit!', command=lambda:killswitch(self))
                    self.user_choice.pack()
        
        
        def killswitch(self):
            root.destroy()


        
if __name__ == '__main__':
    root = ctk.CTk()
    root.geometry('800x900')
    MainApplication(root)
    root.mainloop()
