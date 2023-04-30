from tkinter import *
from tkinter import ttk

class Main(object):
    def __init__(self, master) -> None:
        self.master=master
        #mainframe
        mainFrame= Frame(self.master)
        #topframe
        mainFrame.pack()
        topFrame = Frame(mainFrame, width=900, height= 70, borderwidth=2, relief=SUNKEN, padx=20)

        topFrame.pack(side=TOP, fill=X) 
        self.btn_add_member=Button(
            topFrame, text='New Member', font='arial 12 bold', padx=10)
        self.btn_add_member.pack(side=LEFT)

        self.btn_add_member=Button(
            topFrame, text='New Book', font='arial 12 bold', padx=10)
        self.btn_add_member.pack(side=LEFT)
        
        self.btn_add_member=Button(
            topFrame, text='Issue', font='arial 12 bold', padx=10)
        self.btn_add_member.pack(side=LEFT)
        #centerFrame

        centerFrame = Frame(mainFrame, width=900, height= 800, relief=RIDGE)
        centerFrame.pack(side=TOP)
        #leftFrame
        leftFrame = Frame(centerFrame, width=400, height= 700, relief=SUNKEN, borderwidth=2)
        leftFrame.pack(side=LEFT)
        self.leftab = ttk.Notebook(leftFrame, width=600,height=600)
        self.leftab.pack()
        self.tab1 = ttk.Frame(self.leftab)
        self.tab2 = ttk.Frame(self.leftab)
        self.leftab.add(self.tab1, text='Management')
        self.leftab.add(self.tab2, text='Summary')

        self.management_box = Listbox(self.tab1, width=40, height = 30, font='times 12 bold')

        self.sb= Scrollbar(self.tab1, orient=VERTICAL)
        self.management_box.grid(row=0, column=0, padx=(10,0), pady=10,sticky=N)
        self.sb.configure(command=self.management_box.yview)
        self.management_box.configure(yscrollcommand=self.sb.set) 
        self.sb.grid(row=0, column= 0, sticky = N + S + E) 


        self.list_details = Listbox(self.tab1, width=80, height= 30, font='times 12 bold')
        self.list_details.grid(row=0,column=1,padx=(10,0), pady=10, sticky=N )

        #summary
        self.lbl_book_count = Label(self.tab2, text="", pady=20, font="verdana 14 bold")
        self.lbl_book_count.grid(row=0)

        self.lbl_member_counter = Label(self.tab2, text="", pady=20, font="verdana 14 bold")
        self.lbl_member_counter.grid(row=1, sticky=N)

        self.lbl_taken_count = Label(self.tab2, text="", pady=20, font="verdana 14 bold")
        self.lbl_taken_count.grid(row=2, sticky=W)







        rightframe=Frame(centerFrame, width=300, height=700, relief=SUNKEN, borderwidth=2)
        rightframe.pack()
        searchbar=LabelFrame(rightframe, width=250, height=75, text="Search")
        searchbar.pack(fill=BOTH)
        self.lbl_search= Label(searchbar, text='Search Book: ', font='arial 12 bold')
        self.lbl_search.grid(row=0, column=0, padx=20, pady=10)
        self.ent_search=Entry(searchbar, width=30,bd=10)
        self.ent_search.grid(row=0,column=1, columnspan=3, padx=10, pady=10)
        self.btn_search_btn = Button(
            searchbar, text='Search Now', font='arial 12')
        self.btn_search_btn.grid(row=0,column=4,  padx=20, pady=10) 
        
        list_bar = LabelFrame(rightframe, width=280, height=200, text="Books List", bg='#fff')
        list_bar.pack(fill=BOTH)
        list_lbl=Label(list_bar, text="Sort by", font="times 16")
        list_lbl.grid(row=0,column=2)
        self.listchoice=IntVar()
        rb_all_book = Radiobutton(list_bar, text='Sort All books', var=self.listchoice, value=1)
        rb_all_book.grid(row=1, column=0)
        rb_in_stock=Radiobutton(list_bar, text='In Stock', var=self.listchoice, value=2)
        rb_in_stock.grid(row=1, column=1 )
        rb_issued_book =  Radiobutton(
            list_bar, text='Issued Books', var=self.listchoice, value=3) 
        rb_issued_book.grid(row=1, column=2 ) 
        btn_show_books = Button(list_bar, text="Show Books", font='arial 12 bold')
        btn_show_books.grid(row=1,column=3,padx=40,pady=10)
        welcome_image = Frame(rightframe, width=300, height=400)
        welcome_image.pack(fill=BOTH)
        self.welcome_main_image = PhotoImage(file='images/new.png')
        self.imageslbl=Label(welcome_image, image=self.welcome_main_image)
        self.imageslbl.grid(row=1, column=1)
        self.btn_search_btn = Button (
         searchbar, text='Search Now', font = 'arial 12'   
        )







def main():
    mainwin=Tk()
    app = Main(mainwin)
    mainwin.title("LMS BOOKS")
    mainwin.geometry('1300x900')
    mainwin.mainloop()


if __name__ == '__main__':
    main( )        

