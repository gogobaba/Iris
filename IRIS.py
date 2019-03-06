from skimage.measure import compare_ssim  as ssim
import matplotlib.pyplot as plt
import cv2
import urllib.request
import urllib.parse
import urllib.error
import tkinter as tk
from tkinter import font as tkfont
from tkinter import *
import os
from tkinter import filedialog
import sqlite3
import numpy as np


class SampleApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Calibri', size=18, weight="bold")

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.geometry("700x500+600+200")  # Width x Height + Position  Right + Position Left
        self.title('IRIS - Interface')

        self.frames = {}
        for F in (LoginPage, Home, Methods):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()


class LoginPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="Welcome to IRIS UI", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        username = ""  # that's the given username
        password = ""  # that's the given password

        # username entry
        username_entry = Entry(self)
        username_entry.pack()

        # password entry
        password_entry = Entry(self, show='*')
        password_entry.pack()

        def trylogin():
            # check if both username and password in the entries are same of the given ones
            if username == username_entry.get() and password == password_entry.get():
                controller.show_frame("Home")
            else:
                print("Wrong")

        button = tk.Button(self, text="Log In", command=trylogin)
        button.pack()


class Home(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="IRIS - Home", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        url1 = tk.StringVar()

        def urlimages():
            firstimage = url1.get()
            resource = urllib.request.urlopen(firstimage)
            output = open("1.png", "wb")
            output.write(resource.read())
            output.close()

        label = tk.Label(self, text="Sample Image:")
        label.pack()
        tk.Entry(self, textvariable=url1).pack()

        submit = tk.Button(self, text='Save image', command=urlimages)
        submit.pack()

        def fileDialog():
            file = filedialog.askopenfile(initialdir="/", title='Choose a file', filetype=(("jpeg", "*.jpg"), ('All Files', "*.*")))
            print(file.read())

        label3 = tk.Label(self, text="      ")
        label3.pack()

        button = tk.Button(self, text='Browse images', command=fileDialog)
        button.pack()

        label4 = tk.Label(self, text="      ")
        label4.pack()

        label5 = tk.Label(self, text="      ")
        label5.pack()

        label6 = tk.Label(self, text="      ")
        label6.pack()

        next = tk.Button(self, text="Continue...", command=lambda: controller.show_frame("Methods"))
        next.pack()


class Methods(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, text="IRIS - Methods", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        def SSIM():
            connectdb = sqlite3.connect("results.db")
            cursor = connectdb.cursor()

            img1 = cv2.imread("1.png")
            img11 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            imageA = cv2.resize(img11, (450, 237))
            database = os.listdir("db")

            for image in database:

                img2 = cv2.imread("db/" + image)

                imgprocess = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

                imageB = cv2.resize(imgprocess, (450, 237))

                s = ssim(imageA, imageB)

                print('Comparing input image to ' + image + " using MSE")

                title = "Comparing"
                fig = plt.figure(title)
                if s < 0:
                    s = 0

                result = s * 100

                cursor.execute("INSERT INTO SSIM (percentage, filename) VALUES (?, ?);", (result, image))
                connectdb.commit()

            percentages = list(connectdb.cursor().execute("SELECT * FROM SSIM order by percentage desc limit 10"))
            print(percentages[0])

            highest = percentages[0]
            highestperct = round(highest[0], 2)
            print(highestperct)

            for root, dirs, files in os.walk("db"):
                if highest[1] in files:
                    path = os.path.join(root, highest[1])

            print(path)

            img3 = cv2.imread(path)

            img3process = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)

            imageC = cv2.resize(img3process, (450, 237))

            plt.suptitle("Percentage : " + str(highestperct) + "%")

            # show first image
            ax = fig.add_subplot(1, 2, 1)
            plt.imshow(imageA, cmap=plt.cm.gray)
            plt.axis("off")

            # show the second image
            ax = fig.add_subplot(1, 2, 2)
            plt.imshow(imageC, cmap=plt.cm.gray)
            plt.axis("off")
            # show the images
            plt.show()

            cursor.execute("DELETE FROM SSIM")
            connectdb.commit()

        def MSE():
            connectdb = sqlite3.connect("results.db")
            cursor = connectdb.cursor()

            img1 = cv2.imread("1.png")
            img11 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
            imageA = cv2.resize(img11, (450, 237))
            database = os.listdir("db")

            for image in database:

                img2 = cv2.imread("db/" + image)

                imgprocess = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

                imageB = cv2.resize(imgprocess, (450, 237))

                def mse(imageA, imageB):
                    # the 'Mean Squared Error' between the two images is the
                    # sum of the squared difference between the two images;
                    # NOTE: the two images must have the same dimension
                    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
                    err /= float(imageA.shape[0] * imageA.shape[1])
                    return err

                m = mse(imageA, imageB)

                print('Comparing input image to ' + image + " using MSE")

                title = "Comparing"
                fig = plt.figure(title)

                cursor.execute("INSERT INTO MSE (percentage, filename) VALUES (?, ?);", (m, image))
                connectdb.commit()

            percentages = list(connectdb.cursor().execute("SELECT * FROM MSE WHERE percentage"))

            smallest = min(percentages)
            print(smallest)
            minperct = round(smallest[0], 2)
            print(minperct)

            for root, dirs, files in os.walk("db"):
                if smallest[1] in files:
                    path = os.path.join(root, smallest[1])

            print(path)

            img3 = cv2.imread(path)

            img3process = cv2.cvtColor(img3, cv2.COLOR_BGR2GRAY)

            imageC = cv2.resize(img3process, (450, 237))

            plt.suptitle("MSE : " + str(minperct))

            # show first image
            ax = fig.add_subplot(1, 2, 1)
            plt.imshow(imageA, cmap=plt.cm.gray)
            plt.axis("off")

            # show the second image
            ax = fig.add_subplot(1, 2, 2)
            plt.imshow(imageC, cmap=plt.cm.gray)
            plt.axis("off")
            # show the images
            plt.show()

            cursor.execute("DELETE FROM MSE")
            connectdb.commit()


        def goback():
            controller.show_frame("Home")
            removeimg = "rm 1.png"
            os.system(removeimg)

        methodssim = tk.Button(self, text="SSIM (Structural similarity)", command=SSIM)
        methodssim.pack()

        methodmse = tk.Button(self, text="MSE (Mean squared error)", command=MSE)
        methodmse.pack()

        label4 = tk.Label(self, text="      ")
        label4.pack()

        label5 = tk.Label(self, text="      ")
        label5.pack()

        label6 = tk.Label(self, text="      ")
        label6.pack()

        back = tk.Button(self, text="Go back", command=goback)
        back.pack()


if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()