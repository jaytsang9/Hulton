# -*- coding: utf-8 -*-
"""
Created on Sun Nov 29 12:35:19 2020

@author: Johnny
"""
from datetime import datetime
from collections import namedtuple
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="1337h4x0rColonia1!",
  database="mydatabase"
)
mycursor = mydb.cursor(buffered = True)

count = 1
while count == 1:
    print("Welcome to Hulton! \n Main Menu: \n")
    print("1. Registration \n")
    print("2. Hotel Management \n")
    print("3. Find available rooms and book!\n")
    print("4. To login, input your CID\n")
    print("5. Review your stay")

    choice = input("Pick an option: ")

    if choice == "1": 
        print("Registeration \n")
        name = input("Name: ")
        address = input("Address: ")
        phone = input("Phone Number: ")
        email = input("Email: ")

        sql = "INSERT INTO customer (name, address, phone_No, email) VALUES (%s, %s, %s, %s)"
        val = (name, address, phone, email)
        mycursor.execute(sql, val)
        mydb.commit()
        CID = mycursor.lastrowid
        print("\nYour customer id is : ", CID)
        print("\n")


    if choice == "2": 
        print("Hotel Statistics \n")
        begin_date = input("Begin Date format yyyy/mm/dd: ")
        end_date = input("\n End Date format yyyy/mm/dd: ")
        val = (begin_date, end_date)
        print("If looking for highest rating room type by hotel, enter '1': ")
        print("If looking for best customer (in terms of money spent), enter '2': ")
        print("If looking for highest rated breakfast type across all hotels, enter '3': ")
        print("If looking for highest rated service type across all hotels, enter '4': ")
        selection = input()
        
        if selection == "1":
            
            sql = """SELECT hotel.hotelID, room.rType, MAX(room_review.rating)
                    FROM hotel, room, room_review, room_reservation 
                    WHERE hotel.hotelID = room.hotelID AND 
                    room.hotelID = room_review.hotelID AND
                    room.roomNo = room_review.roomNo AND 
                    room.hotelID = room_reservation.hotelID AND 
                    room.roomNo = room_reservation.roomNo AND
                    checkInDate >= %s AND
                    checkOutDate <= %s GROUP BY room.hotelID"""
            mycursor.execute(sql,val)
            mydb.commit()
            print("\n")
            for row in mycursor:
                print(row)
            print("\n") 
              
        if selection == "2":
            sql = """SELECT customer.CID, customer.Name, SUM(reservation.totalPrice)
                    FROM customer, reservation, room_reservation
                    WHERE customer.CID = reservation.CID AND
                    room_reservation.invoiceNo = reservation.invoiceNo AND
                    checkInDate >= %s AND
                    checkOutDate <= %s
                    GROUP BY customer.CID ORDER BY SUM(reservation.totalPrice) DESC
                    LIMIT 5"""
            mycursor.execute(sql,val)
            mydb.commit()
            print("\n")
            for row in mycursor:
                print(row)
            print("\n") 
            
        if selection == "3":
            
          sql ="""SELECT brev.bType, AVG(brev.rating) FROM breakfast_review brev, room_reservation rresv, rrserv_breakfast rresv_b 
          WHERE rresv.checkInDate >= %s AND rresv.checkOutDate <= %s AND rresv.hotelid = rresv_b.hotelid AND rresv.roomNo = rresv_b.roomNo AND rresv.checkInDate = rresv_b.checkInDate
          GROUP BY 1 ORDER BY 2 DESC LIMIT 1"""
          val = (begin_date, end_date) 
          mycursor.execute(sql,val)
          mydb.commit()
          print("\n")
          for row in mycursor:
              print(row)
          print("\n")        
          
        if selection == "4":
        
          sql = """SELECT srev.sType, AVG(srev.rating) FROM service_review srev, room_reservation rresv, rresv_service rresv_s 
          WHERE rresv.checkInDate >= %s AND rresv.checkOutDate <= %s AND rresv.hotelid = rresv_s.hotelid AND rresv.roomNo = rresv_s.roomNo AND rresv.checkInDate = rresv_s.checkInDate
          GROUP BY 1 ORDER BY 2 DESC LIMIT 1"""

          val = (begin_date, end_date)
                  
          mycursor.execute(sql,val)
          mydb.commit()
          print("\n")
          for row in mycursor:
              print(row)
          print("\n") 
          
    if choice == "3":
        print("To Book, input your CID.")
        cid = int(input("CID: "))
        country = input("Please enter country of interest: ")
        state = input("Please enter state of interest: ")

        sql = "SELECT * FROM hotel WHERE country = %s AND state = %s"
        val = (country,state)
        mycursor.execute(sql,val)
        for row in mycursor:
            print("Hotel ID: ", row[0],)
            print("Street:  ",row[1],)
            print("Country: ", row[2],)
            print("State: ", row[3],)
            print("zip: ", row[4], "\n") # displays the above query - finds rooms in a hotel @ requested country and state

        hotelID = input("Please select the hotel ID corresponding to your choice: ")

        sql = "SELECT * FROM room WHERE hotelID = %s"
        val = (hotelID,)
        mycursor.execute(sql,val)
        for row in mycursor:
            print("Hotel ID: ", row[0],)
            print("Room No: ",row[1],)
            print("Room Type: ", row[2],)
            print("Price: $", row[3],)
            print("Description: ", row[4],)
            print("Floor: ", row[5],)  # displays the above query - finds rooms in a hotel @ requested country and state
            print("Capacity: ", row[6], "\n")

        roomNo = input("Please select the room number which corresponds to the room of your choice: ")
        checkInDate = input("Please enter check in date in format yyyy/mm/dd: ")
        checkOutDate = input("Please enter check out date in format yyyy/mm/dd: ")
        
        sql = "SELECT price from room where hotelID = %s and roomNo = %s"
        val = (hotelID,roomNo)
        mycursor.execute(sql,val)       # checks to see if the room from the previous query is available at the selected check in date
        row = mycursor.fetchone()
        price = row[0]

        sql = "SELECT EXISTS(SELECT * from room_reservation WHERE hotelID = %s AND roomNo = %s AND checkInDate = %s)"
        val = (hotelID,roomNo,checkInDate)
        mycursor.execute(sql,val)       # checks to see if the room from the previous query is available at the selected check in date
        row = mycursor.fetchone()
        booly = row[0]
        if booly == 1:
            print("Sorry, we are all booked on that date in that room in that hotel")
            break
        
        discount = 0
        Range = namedtuple('Range', ['start', 'end'])         #converts user inputted date to date objects
        date_time_strIn = checkInDate
        date_time_objIn = datetime.date(datetime.strptime(date_time_strIn, '%Y/%m/%d'))
        date_time_strOut = checkOutDate
        date_time_objOut = datetime.date(datetime.strptime(date_time_strOut, '%Y/%m/%d'))
       
        sql = "SELECT startDate, endDate from discounted_room WHERE hotelID = %s AND roomNo = %s"
        val = (hotelID,roomNo)
        mycursor.execute(sql,val)
        if mycursor.rowcount != 0:   # Checks if that room number or hotel combo is discounted at any point
            row = mycursor.fetchone()
            start = row[0]  # if it exists, will get start and end dates from database in row0 and row1
            end = row[1]
            r1 = Range(start=date_time_objIn, end=date_time_objOut)
            r2 = Range(start=start, end=end)
            latest_start = max(r1.start, r2.start)
            earliest_end = min(r1.end, r2.end)
            delta = (earliest_end - latest_start).days + 1
            overlap = max(0, delta)
            if overlap > 0:
                sql = "SELECT discount FROM discounted_room WHERE hotelID = %s and roomNo = %s"
                val = (hotelID,roomNo)
                mycursor.execute(sql,val)
                for row in mycursor:
                  discount = row[0]
                discountedprice = price - (discount*price)
                print(discountedprice)
            
                
        # ------------ BOOK RESERVATION ----------- #
        cNumber = cType = bAddress = name = str
        code = int
        expDate = None
        res_input = input("Would you like to create a reservation for this date? Y or N: ")
        if res_input in ["y","Y"]:
            
            cc_input = input("Do you have a credit card already on file? Y or N: ")
            if cc_input in ["y","Y"]:
                cNumber = input("Please enter credit card number on file: ")
                sql = "SELECT * from credit_card where cNumber = %s"
                val = (cNumber,)
                mycursor.execute(sql,val)
                row = mycursor.fetchone()
                cType = row[1]
                bAddress = row[2]
                code = row[3]
                expDate = row[4]
                name = row[5]
            
            else:
                print("Please enter credit card information. \n")
                cNumber = input("Credit Card Number: ")
                cType = input("Card Type: ")
                bAddress = input("Billing Address: ")
                code = input("Security Code: ")
                expDate = input("expDate, format yyyy/mm/dd ")
                name = input("Your Name: ")
                sql = "INSERT INTO credit_card (cNumber, cType, bAddress, code, expDate, name) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (cNumber, cType, bAddress, code, expDate, name)
                mycursor.execute(sql, val)
                mydb.commit()
            # ------------- CREATE RESERVATION -------------
            sql = "INSERT INTO reservation (CID, cNumber, rDate) VALUES (%s, %s, %s)"
            val = (cid, cNumber, checkInDate)
            mycursor.execute(sql, val)
            mydb.commit()
            # # ------------- GETTING INVOICE NUMBER -----------
            sql = "SELECT reservation.invoiceNo FROM reservation WHERE CID = %s AND cNumber = %s AND rDate = %s"
            val = (cid, cNumber, checkInDate)
            mycursor.execute(sql, val)
            invoice_num = mycursor.fetchone()
            print("\n")
            
            #-------------- STORING INTO room_reservation -----------
            sql = "INSERT INTO room_reservation (invoiceNo, hotelID, roomNo, checkInDate, checkOutDate) VALUES (%s, %s, %s, %s, %s)"
            val = (invoice_num[0], hotelID, roomNo, checkInDate, checkOutDate)
            mycursor.execute(sql, val)
            mydb.commit()
            #------------- BOOKING BREAKFAST ------------
            breakfast_input = input("Would you like to book your breakfasts during your stay?: Y or N: ")
            if breakfast_input in ["y","Y"]:
                print("Below are the available breakfast options for you hotel.")
                sql = "SELECT bType, bPrice, description FROM breakfast WHERE hotelID = %s"
                val = (hotelID,)
                mycursor.execute(sql, val)
                for row in mycursor:
                    print("Breakfast type: ", row[0])
                    print("Price: $", row[1])
                    print("Description: ", row[2], "\n") 
                breakfastChoice = input("Which breakfast would you like? Please type the breakfast type: ")
                noOfOrders = int(input("How many times would you like to eat breakfast?: "))
                sql = "INSERT INTO rrserv_breakfast (bType, hotelID, roomNo, checkInDate, noOfOrders) VALUES (%s, %s, %s, %s, %s)"
                val = (breakfastChoice, hotelID, roomNo, checkInDate, noOfOrders)
                mycursor.execute(sql, val)
                mydb.commit()
            #------------- BOOKING SERVICE ------------
            service_input = input("\nWould you like to book a service during your stay?: Y or N: ")
            if service_input != "N" or "n":
                print("Below are the available service options for you hotel.")
                sql = "SELECT sType, sPrice FROM service WHERE hotelID = %s"
                val = (hotelID,)
                mycursor.execute(sql, val)
                for row in mycursor:
                    print("Service type: ", row[0])
                    print("Price: $", row[1], "\n")
                serviceChoice = input("Which service would you like to use during yout stay? Please type the service type: ")
                sql = "INSERT INTO rresv_service (sType, hotelID, roomNo, checkInDate) VALUES (%s, %s, %s, %s)"
                val = (serviceChoice, hotelID, roomNo, checkInDate)
                mycursor.execute(sql, val)
                mydb.commit()
                     
            #------------- TOTALING BILL -------------
            sql = "SELECT bPrice FROM breakfast WHERE hotelID = %s AND bType = %s"
            val =(hotelID, breakfastChoice)
            mycursor.execute(sql, val)
            breakfastPrice = mycursor.fetchone()
            #print(breakfastPrice[0])
            sql = "SELECT sPrice FROM service WHERE hotelID = %s AND sType = %s"
            val =(hotelID, serviceChoice)
            mycursor.execute(sql, val)
            servicePrice = mycursor.fetchone()
            #print(servicePrice[0])
            # sql = "SELECT price FROM room WHERE hotelID = %s AND roomNo = %s"
            # val =(hotelID, roomNo)
            # mycursor.execute(sql, val)
            # roomPrice = mycursor.fetchone()
            #print(roomPrice[0])
            mydb.commit()
            roomPrice = price - (discount*price)
            breakfastPrice = breakfastPrice[0]
            servicePrice = servicePrice[0]
            breakfastPrice = float(breakfastPrice)
            servicePrice = float(servicePrice)
            total = roomPrice+ noOfOrders*breakfastPrice+servicePrice
            print("\nYour total for this reservation will be: ", total)
            print("Thank you for you choosing to stay with us!")
            sql = "UPDATE reservation SET totalPrice = %s WHERE invoiceNo = %s"
            val = (total,invoice_num[0])
            mycursor.execute(sql, val)
            mydb.commit()
        break;
    if choice == "4":
        print("To login, input your CID.")
        cid = int(input("CID: "))
        # #Checks DB for existing CID
        # cidCheck = "SELECT CID from customer"
        # mycursor.execute(cidCheck)
        # check = mycursor.fetchall()
        # for row in check :
        #     print(row)
        # sql = "SELECT CID FROM customer WHERE CID = %s"
        # val = (cid,)
        # mycursor.execute(sql, val)
        # mydb.commit()
        print("Here you can update registration information")
        print("Change name? Type 1")
        print("Change Address? Type 2")
        print("Change Phone_No? Type 3")
        print("Change Email? Type 4")
        choice = input("Which of the following would you like to update?: ")
        if choice == "1":
            newName = input("Change name: ")
            sql = "UPDATE customer SET name =%s WHERE cid = %s"
            mycursor.execute(sql,(newName,cid))
            mydb.commit()
        if choice == "2":
            newAddress = input("Change address: ")
            sql = "UPDATE customer SET address =%s WHERE cid = %s"
            mycursor.execute(sql,(newAddress,cid))
            mydb.commit()
        if choice == "3":
            newPhone = input("Change Phone_No: ")
            sql = "UPDATE customer SET phone_no =%s WHERE cid = %s"
            mycursor.execute(sql,(newPhone,cid))
            mydb.commit()
        if choice == "4":
            newEmail = input("Change Email: ")
            sql = "UPDATE customer SET email =%s WHERE cid = %s"
            mycursor.execute(sql,(newEmail,cid))
            mydb.commit()
    if choice == "5":
        print("Thank you for choosing to stay at the Hulton!") 
        customerID = input("What is your CID: ")
        sql = "SELECT r.invoiceNo, rresv.hotelID, rresv.roomNo, rresv.checkInDate FROM room_reservation rresv JOIN reservation r ON rresv.invoiceNo = r.invoiceNo WHERE r.cid = %s"
        val = (customerID, )
        mycursor.execute(sql, val)
        myresult = mycursor.fetchall()
        for x in myresult:
            print("Invoice #: ", x[0])
            print("Hotel ID: ", x[1])
            print("Room #: ", x[2])
            print("Date: ", x[3], "\n")
        print("Choose invoice number corresponding to the reservation you want to review")
        invoice_num = input("invoice #: ")
        sql = ("SELECT hotelID, roomNo, checkInDate FROM room_reservation WHERE invoiceNo = %s")
        val = (invoice_num,)
        mycursor.execute(sql, val)
        hotelid=None
        roomNo=None
        for row in mycursor:
            hotelid = row[0]
            roomNo = row[1]
            checkInDate = row[2]
        rating = input("Please give us a rating on the room(1-10): ")
        text = input("Please tell us about your stay: ")
        sql = "INSERT INTO room_review (rating, text, CID, hotelID, roomNo) VALUES (%s, %s, %s, %s, %s)"
        val = (rating, text, customerID, hotelid, roomNo)
        mycursor.execute(sql, val)
        mydb.commit()
        
        print("\nPlease rate your breakfast")
        sql = "SELECT btype FROM rrserv_breakfast WHERE hotelID = %s AND roomNo = %s AND checkInDate = %s"
        val = (hotelid, roomNo, checkInDate)
        mycursor.execute(sql,val)
        result = mycursor.fetchall()
        mydb.commit()
        for x in result:
          btype = x[0]  
        bRating = input("Please give us a rating (1-10): ")
        bText = input("Please tell us about your stay: ")
        sql = "INSERT INTO breakfast_review (hotelID, bType, CID, text, rating) VALUES (%s, %s, %s, %s, %s)"
        val = (hotelid, btype, customerID, bText, bRating)
        mycursor.execute(sql, val)
        mydb.commit()
        
        print("\nPlease rate your services")
        sql = "SELECT sType FROM rresv_service WHERE hotelID = %s AND roomNo = %s AND checkInDate = %s"
        val = (hotelid, roomNo, checkInDate)
        mycursor.execute(sql,val)
        result = mycursor.fetchall()
        mydb.commit()
        for x in result:
          stype = x[0]  
        sRating = input("Please give us a rating (1-10): ")
        sText = input("Please tell us about your stay: ")
        sql = "INSERT INTO service_review (hotelID, sType, CID, text, rating) VALUES (%s, %s, %s, %s, %s)"
        val = (hotelid, stype, customerID, sText, sRating)
        mycursor.execute(sql, val)
        mydb.commit()
mydb.close()