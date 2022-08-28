# Import modules:
from gpiozero import MotionSensor
from picamera import PiCamera
from datetime import datetime
from time import sleep
import time
from datetime import timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
 
# Set up variables for email. "toaddr" is the receiver of the motion alert email. "me" is the sender email. The sender email should be a throwaway address because of the lack of security:
targetEmail = 'me@email.com'
senderEmail = 'throwawayEmail@email.com'
senderPassword = 'throwawayEmailPassword'
subject = 'Motion detected!'
           
# Create an email using Python's "email.mime": 
msg = MIMEMultipart()
# Set the email to our data input above:
msg['Subject'] = subject
msg['From'] = senderEmail
msg['To'] = targetEmail
           
# Set two variables to current time. This is for a time check later to avoid spamming emails:
MsgTimer = datetime.today()
PicTimer = datetime.today()
 
# Configurable variables that control the initial time between emails and the initial time between pictures. By default, emails are every 15 minutes and pictures are continuous (0 minutes):
EmailStartingTime = 15
PictureStartingTime = 0
 
 
# Access the pi camera and the motion sensor:
camera = PiCamera()
pir = MotionSensor(4)
while True:
    try: 
        # Set current time to variable "now" for what hour it is:
        now = datetime.now().time()
       
        # Set "nowTime" to the time right now for email delay. NOT to be confused with earlier "now" var:
        nowTime = datetime.today()
 
        
        # If the current time is past our timer, run loop (details below):
        if PicTimer < nowTime:
            pir.wait_for_motion()
            # Set current time to variable "now" for what hour it is:
            now = datetime.now().time()
            # Takes two pictures in form: month, day, year _ time (in AM and PM):
            filename = datetime.now().strftime("%m-%d-%Y_%r.jpg")
            camera.capture(filename)
            sleep(1)
            camera.capture(filename)
            
            # After taking pictures, wait until motion has ended to avoid ceaseless image spamming:
            pir.wait_for_no_motion()
            # Set the picture delay to the default of 0 (constant), or set it to what the user input:
            PicTimer = datetime.today() + timedelta(minutes=PictureStartingTime)
            # Reset the picture delay to 0 once the amount of time the user input has passed:
            PictureStartingTime = 0

         
        # Same setup as with PicTimer, this time for email:
            if MsgTimer < nowTime:
                # Connect to Gmail server and log in:
                s = smtplib.SMTP('smtp.gmail.com',587)
                s.starttls()
                s.login(senderEmail,senderPassword)
                # Send email with "msg" object contents:
                s.send_message(msg)
                s.quit()
                # Similar to PicTimer, set MsgTimer for a default 15 mins, or what the user input:
                MsgTimer = datetime.today() + timedelta(minutes=EmailStartingTime)
                # Also like PicTimer, reset MsgTimer to 15 mins after user input time ends:
                EmailStartingTime = 15
                print("email sent! Also, sleeping email for", EmailStartingTime, "minutes.")

    # Pause when 'ctrl' and then 'c' are pressed and motion is detected:
    except KeyboardInterrupt:
        print("\nPausing.. (Enter hours to pause email and hit ENTER to continue.)")
        try:
            response = input()
            try: 
                UserInput = int(response)
                # Convert user input in hours to minutes:
                UserInputInMins = UserInput*60
                # Make both timers the time the user input:
                EmailStartingTime = UserInputInMins
                PictureStartingTime = UserInputInMins
            except:
                print("Wasn't an int. Try again.")
                continue
             
            if response == 'quit':
                break
            print('Resuming...')
        except KeyboardInterrupt:
            print('Resuming...')
            continue
