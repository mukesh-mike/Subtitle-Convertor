from Tkinter import *
from tkFileDialog import *
import tkMessageBox
import requests
import threading
import re
from google.cloud import translate
import os
import operator


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\Users\mukes\Downloads\mks7738147108 -e9da44bad920.json"




def create_widget_in_frame1():
    Frame(root, borderwidth=2, height=2, relief=SUNKEN).pack(fill=X)
    Label(frame1, text="Import File : ").grid(row=1, column=0)

    global from_file
    from_file = StringVar()
    from_file.set("")

    ImportFile = Label(frame1, textvariable=from_file, width=50,relief=RIDGE)
    ImportFile.grid(row=1, column=1, padx=5)
    Button(frame1, text="Browse", command=select_fromfile).grid(row=1, column=3)
    global b2
    b2 = Button(frame1, text="Submit",command=lambda: remove(from_file))
    b2.grid(row=2, column=0, pady=5)


def select_fromfile():
    file = askopenfilename(initialdir='C:\Users\mukes\Downloads\subtitle_translator-master', title='Select File',
                                filetypes=[("SRT Files", "*.srt")])
    from_file.set(file)


def remove(from_file):
    if counter.get() > 0 :
        optMenuto.grid_remove()

    get_lang_list(from_file)
    counter.set(counter.get()+1)




def get_lang_list(from_file):

    if from_file.get():
        try:
            translate_client = translate.Client()
            result = translate_client.get_languages()

            global lang
            lang={}
            global lang_code
            lang_code={}

            for i in result:
                templang = u'{name}'.format(**i)
                templangcode = u'{language}'.format(**i)
                lang[templang] = templangcode
                lang_code[templangcode] = templang

            sorted_lang = sorted(lang.keys(), key=operator.itemgetter(0))
            print(sorted_lang)


            #language detect
            a = open(from_file.get(), "r")
            text = ""
            count = 0
            ll = []
            for i in a:
                ll = i.split()
                if len(ll) > 1 and ll[1] == "-->":
                    continue
                else:
                    text = text + i

                count = count+1
                if count > 10:
                    break
            print(text)

            detect = translate_client.detect_language(text)

            code_detect ='{}'.format(detect['language'])
            lang_detect = lang_code[code_detect]

            create_widget_in_frame2(sorted_lang,lang_detect)

        except:
            error("No Internet Connection")


    else:
        error("No File Selected")



def error(err):
    tkMessageBox.showerror(
        "Message",
        err
    )



def create_widget_in_frame2(choices,lang_detect):
    frame2.pack(fill=X)
    global fromlang
    fromlang = StringVar()
    fromlang.set(lang_detect)
    global tolang
    tolang= StringVar()
    tolang.set("")
    global dest_path
    dest_path = StringVar()
    dest_path.set("C:\Users\mukes\Downloads\subtitle_translator-master")
    global name
    name = StringVar()
    name.set("")

    Label(frame2,text="Select Destination Folder : ").grid(row=1,column=0)
    dest_label = Label(frame2,textvariable=dest_path,width=40,relief=RIDGE)
    dest_label.grid(row=1,column=1,padx=5,pady=5)
    Button(frame2,text="Browse",command=sel_destfolder).grid(row=1,column=2)

    Label(frame2,text="Enter Target File-Name : ").grid(row=2,column=0,sticky=E)
    global file_name
    file_name = Entry(frame2,textvariable=name,width=47).grid(row=2,column=1)


    Label(frame2, text="language detected : ").grid(row=0, column=0,sticky=E)
    labelfrom = Label(frame2,textvariable=fromlang,borderwidth=2,relief=RIDGE)
    labelfrom.grid(row=0, column=1, padx=5, pady=5,sticky=W)
    Label(frame2, text="Convert to : ").grid(row=0,column=1)
    global optMenuto
    optMenuto = OptionMenu(frame2, tolang, *choices)
    optMenuto.grid(row=0, column=1, padx=5,sticky=E)
    global b1
    b1 = Button(frame2,text="Convert",command=check_fields)
    b1.grid(row=3,column=0,pady=5)
    Label(frame2,text="Status").grid(row=3,column=1,padx=5,sticky=W)
    global status
    status = StringVar()
    status.set("")
    Label(frame2,textvariable=status,width = 27,relief=RIDGE).grid(row=3,column=1)



def sel_destfolder():
    file = askdirectory(initialdir='C:\Users\mukes\Downloads\subtitle_translator-master', title='Select Target File Folder')
    dest_path.set(file)


def state_change():
    b1.config(state="disabled")
    b2.config(state="disabled")
    status.set("Converting....")


def check_fields():
    if tolang.get():
        if dest_path.get():
            if name.get():
                threading.Thread(target=state_change).start()
                threading.Thread(target=translator).start()

            else:
                error("Please Enter Target File-Name")
        else:
            error("Please Select Destination Folder")
    else:
        error("Please Select Target-File Language")



def translator():
    source_langcode = lang[fromlang.get()]
    dest_langcode = lang[tolang.get()]

    global file_out
    file_out = open(dest_path.get() + "/" + name.get() + ".srt", 'a+')
    file_out.truncate(0)
    file_in = open(from_file.get(), "r")
    for i in file_in:
        ll = []
        ll = i.split()
        if len(ll) > 1 and ll[1] == "-->":
            file_out.write(i)
        else:
            str = ""
            for j in i:
                if j == " ":
                    str = str + "%20"
                else:
                    str = str + j

            convertstring(str, source_langcode, dest_langcode)
    file_out.close()
    b1.config(state="normal")
    b2.config(state="normal")
    status.set("Converted")



def convertstring(str,source_langcode,dest_langcode):
    with requests.Session() as s:
        temp = str.decode('UTF-8')
        url = "https://www.googleapis.com/language/translate/v2?key=AIzaSyAs5AEATk8CWfzAgkL4ErRC9nf0WOpCYl8&q="+temp+"&source="+source_langcode+"&target="+dest_langcode
        f = requests.get(url, verify=False)
        a = f.text.encode('UTF-8')
        par = a[71:len(a) - 22]
        file_out.write(par+"\n")
        #print par+"\n"




root = Tk()
root.title("Subtitle Convertor")
root.resizable(width=False,height=True)
frame1 = Frame(root)
frame1.pack(fill=X)
create_widget_in_frame1()


frame2 = Frame(root)

counter = IntVar()
counter.set(0)


root.mainloop()