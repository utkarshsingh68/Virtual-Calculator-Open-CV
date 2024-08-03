import cv2
from cvzone.HandTrackingModule import HandDetector
import pyttsx3

class Calculator:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw_button(self, img):
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 125, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos, (self.pos[0] + self.width, self.pos[1] + self.height),
                      (200, 200, 200), 3)
        cv2.putText(img, self.value, (self.pos[0] + 30, self.pos[1] + 70), cv2.FONT_HERSHEY_PLAIN,
                    2, (50, 50, 50), 2)

    def click(self, x, y, img):
        if self.pos[0] < x < self.pos[0] + self.width and \
                self.pos[1] < y < self.pos[1] + self.height:
            cv2.rectangle(img, (self.pos[0] + 3, self.pos[1] + 3),
                          (self.pos[0] + self.width - 3, self.pos[1] + self.height - 3),
                          (255, 255, 255), cv2.FILLED)
            cv2.putText(img, self.value, (self.pos[0] + 25, self.pos[1] + 80), cv2.FONT_HERSHEY_PLAIN,
                        5, (0, 0, 0), 5)
            return True
        else:
            return False

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)
engine.say("please wait! the virtual calculator is starting")
engine.runAndWait()

buttons = [['7', '8', '9', 'C'],
           ['4', '5', '6', '*'],
           ['1', '2', '3', '+'],
           ['0', '-', '/', '='],
           ['(', ')', '.', 'del']]
button_list = []
for x in range(4):
    for y in range(5):
        xpos = x * 100 + 700
        ypos = y * 100 + 100
        button_list.append(Calculator((xpos, ypos), 100, 100, buttons[y][x]))

equation = ''
counter = 0

# Webcam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(3, 1280)
cap.set(4, 1080)
detector = HandDetector(detectionCon=0.7, maxHands=6)

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)

    for button in button_list:
        button.draw_button(img)

    # Check for hand
    if hands:
        # Find distance between fingers
        lm_list = hands[0]['lmList']
        # Ensure landmarks contain x and y values
        if len(lm_list[8]) >= 2 and len(lm_list[12]) >= 2:
            x, y = lm_list[8][0], lm_list[8][1]
            length, _, img = detector.findDistance(lm_list[8][:2], lm_list[12][:2], img)

            # If clicked check which button and perform action
            if length < 50 and counter == 0:
                for i, button in enumerate(button_list):
                    if button.click(x, y, img):
                        my_value = buttons[int(i % 5)][int(i / 5)]  # get correct number
                        if my_value == '=':
                            try:
                                equation = str(eval(equation))
                            except SyntaxError:
                                print("Syntax Error")
                                engine.say("Syntax Error")
                                engine.runAndWait()
                                equation = 'Syntax Error'
                        elif equation == 'Syntax Error':
                            equation = ''
                        elif my_value == 'C':
                            equation = ''
                        elif my_value == 'del':
                            equation = equation[:-1]
                        else:
                            equation += my_value
                        counter = 1

    # to avoid multiple clicks
    if counter != 0:
        counter += 1
        if counter > 30:
            counter = 0

    # Final answer
    cv2.rectangle(img, (700, 20), (1100, 100),
                  (225, 225, 225), cv2.FILLED)

    cv2.rectangle(img, (700, 20), (1100, 100),
                  (200,200, 200), 3)
    cv2.putText(img, equation, (710, 80), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 0, 0), 3)
    cv2.putText(img, 'VIRTUAL CALCULATOR -->', (50, 50), cv2.FONT_HERSHEY_PLAIN,
                3, (0, 0, 0), 3)
    cv2.imshow("Virtual Calculator", img)
    cv2.moveWindow("Virtual Calculator", 0, 0)
    # close the webcam
    if cv2.waitKey(10) & 0xFF == ord("q"):
        break

print("lmList[8]:", lm_list[8])
print("lmList[12]:", lm_list[12])
