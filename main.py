import threading

# Care-Bot: Daily Schedule Coordinator for Elderly Care
# ENG7007 - Applications for Social and Service Robots
# Cardiff Metropolitan University 2025-26
# Student: Md Amjad Hossain Khan (st20341331)

class MyClass(GeneratedClass):
    def __init__(self):
        GeneratedClass.__init__(self)
        self.tts = None
        self.leds = None
        self.memory = None
        self.asr = None
        self.posture = None
        self.touchSubscriber = None
        self.speechSubscriber = None
        self.scheduleStarted = False
        self.isRunning = False
        self.wordQueue = []

    def onLoad(self):
        # settings up all the services i need
        self.tts = self.session().service("ALTextToSpeech")
        self.leds = self.session().service("ALLeds")
        self.memory = self.session().service("ALMemory")
        self.asr = self.session().service("ALSpeechRecognition")
        self.posture = self.session().service("ALRobotPosture")

        # pause asr before configuring all
        self.asr.pause(True)
        self.asr.setLanguage("English")
        self.asr.setVocabulary(["yes", "no", "ready", "repeat", "stop"], False)
        self.asr.pause(False)
        self.asr.subscribe("ScheduleASR")

        # connecting the head touch sensor
        self.touchSubscriber = self.memory.subscriber("FrontTactilTouched")
        self.touchSubscriber.signal.connect(self.onHeadTouched)

        # connecting speech recognition
        self.speechSubscriber = self.memory.subscriber("WordRecognized")
        self.speechSubscriber.signal.connect(self.onWordRecognized)

    def onUnload(self):
        try:
            self.asr.pause(True)
            self.asr.unsubscribe("ScheduleASR")
            self.asr.pause(False)
        except:
            pass

    def onHeadTouched(self, value):
        # only trigger once
        if value == 1 and not self.scheduleStarted and not self.isRunning:
            self.scheduleStarted = True
            self.isRunning = True
            self.runSchedule()

    def onWordRecognized(self, value):
        if not self.scheduleStarted:
            return
        if self.isRunning:
            return
        if not value or len(value) < 2:
            return
        if value[0] == "" or value[0] == "<...>":
            return
        if value[1] < 0.55:
            return

        word = value[0].lower()

        # add to queue, only if queue is empty
        if word not in self.wordQueue:
            self.wordQueue.append(word)
            self.processWord()

    def processWord(self):
        if not self.wordQueue:
            return
        if self.isRunning:
            self.wordQueue = []
            return

        self.isRunning = True
        word = self.wordQueue[0]
        self.wordQueue = []

        try:
            if word == "yes" or word == "ready":
                self.leds.fadeRGB("FaceLeds", 0x00FF00, 0.5)
                self.tts.say("Wonderful! Have a great day!")
                self.tts.say("Say stop to finish.")

            elif word == "repeat":
                self.tts.say("Of course. Let me repeat today's schedule.")
                self.saySchedule()

            elif word == "no":
                self.leds.fadeRGB("FaceLeds", 0xFF8800, 0.5)
                self.tts.say("No problem at all. Please let a member of staff know if you need help.")
                self.tts.say("Say stop to finish.")

            elif word == "stop":
                self.tts.say("Goodbye for now. Have a lovely day!")
                self.leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.5)
                self.posture.goToPosture("Crouch", 0.5)
                self.isRunning = False
                self.onStopped()
                return

        except Exception as e:
            pass

        self.isRunning = False

    def saySchedule(self):
        self.tts.say("8am, Breakfast in the dining room.")
        self.tts.say("10am, Morning exercise with the physiotherapist.")
        self.tts.say("12pm, Lunch is served.")
        self.tts.say("3pm, Music and singing session in the lounge.")
        self.tts.say("5pm, Evening meal and free time.")

    def runSchedule(self):
        import datetime
        try:
            self.posture.goToPosture("StandInit", 0.5)
            self.leds.fadeRGB("FaceLeds", 0xFFFFFF, 0.5)
            self.tts.setParameter("speed", 80)
            self.tts.say("Good morning! I am your care assistant today.")
            self.tts.say("You can say yes, no, repeat, or stop at any time.")

            current_hour = datetime.datetime.now().hour

            if 6 <= current_hour < 10:
                self.tts.say("It is morning time. Breakfast will be served soon.")
            elif 10 <= current_hour < 12:
                self.tts.say("It is time for your morning exercise. Let us stay active!")
            elif 12 <= current_hour < 14:
                self.tts.say("It is lunchtime. Please make your way to the dining room.")
            elif 14 <= current_hour < 17:
                self.tts.say("It is afternoon. Your music session starts at 3pm.")
            else:
                self.tts.say("It is evening time. Dinner will be served shortly.")

            self.leds.fadeRGB("FaceLeds", 0x0000FF, 0.5)
            self.tts.say("Here is your full schedule for today.")
            self.saySchedule()

            self.leds.fadeRGB("FaceLeds", 0xFFFF00, 0.5)
            self.tts.say("Are you ready to start your day? Please say yes or no.")

        except Exception as e:
            pass

        self.isRunning = False

    def onInput_onStart(self):
        self.posture.goToPosture("Crouch", 0.5)
        self.leds.fadeRGB("FaceLeds", 0xFF00FF, 0.5)
        self.tts.say("Hello, I'm Lily your carebot! Please touch my head to begin today's schedule.")

    def onInput_onStop(self):
        self.onUnload()
        self.onStopped()
