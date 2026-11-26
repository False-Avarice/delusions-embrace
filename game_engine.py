class GameEngine:
    def __init__(self):
        self.steps = {
            "begin": self._closing_time,
            "coffee": self._coffee,
            "key": self._across_the_street,
            "street": self._second_bell,
            "table": self._receipt,
            "receipt": self._room,
            "listen": self._at_the_door,
            "door": self._aftermath,
            "irina_memory": self._irina_memory,
        }

    @staticmethod
    def get_initial_state():
        return {"current_step": "begin"}

    def process_step(self, state, choice_index=None):
        if choice_index is None or state["current_step"] == "restart":
            state.clear()
            return self._scene(state, "begin", [], ["Begin"], title="Delusions Embrace", audio={"location": "cafe"})
        return self.steps[state["current_step"]](state, choice_index)

    @staticmethod
    def _scene(state, next_step, text, choices, *, title=None, glitch_line=None, audio=None):
        state["current_step"] = next_step
        return {"title": title, "text": text, "choices": choices, "glitch_line": glitch_line, "audio": audio or {}}

    def _closing_time(self, state, _choice):
        return self._scene(state, "coffee", [
            "The café is warm enough to make your coat smell of wet wool. "
            "You keep it on. The walk home takes six minutes and you have been putting it off "
            "for the better part of an hour. At home the radiator knocks once, pauses, then knocks twice. "
            "You can hear that rhythm even with the pillow over your head.",
            "The server lifts chairs onto the tables by the window. Behind him, the clock says 11:47. "
            "You have watched the minute hand twitch in place three times. The fourth time, the door "
            "opens and the little brass bell above it rings twice.",
            "A woman carries a cup from the counter to your table. You know her name is Irina "
            "before she tells you. There's a thread coming loose from her cuff. She winds it "
            "around her finger while she waits for you to make room.",
            "“Two sugars,” she says, setting the coffee down in front of you. “Leave the second one at the bottom.” "
            "She even puts the handle on your left. The small kindness takes you so much by surprise "
            "that you touch the cup before you remember you haven't ordered.",
            "The server comes over with his pad. “What can I get you?” "
            "Irina says, “Coffee. Two sugars.” You hear the little catch in your own voice "
            "that comes from speaking after a long silence. The server writes it down without looking up. "
            "He tears a slip from his pad and puts it between you. One coffee. Under the price he has written 11:47.",
        ], [
            "Ask the server who ordered the coffee.",
            "Ask Irina how she knows your order.",
            "Move the cup and see what happens.",
        ], title="Closing Time", audio={"paragraphs": {
            1: ("door opens", "bell"),
            3: ("setting the coffee down", "cup"),
        }})

    def _coffee(self, state, choice):
        encounter, response = (
            ("server",
             "The server looks at your hand on the cup. “You did. I watched you carry it over.” "
             "He says it kindly, as though you've put on your coat and asked him where your coat is. "
             "You watch him take the other chair off the table nearest the door, check its legs, "
             "and put it back up again. He gives the chair more attention than he gave Irina."),
            ("irina",
             "“I remember the sugar coming apart,” Irina says. “You always leave the last mouthful.” "
             "She moves her finger over a little hollow in the tabletop. You could fit a sugar cube in it. "
             "“I remember that too.” She says it with such quiet affection that for a second you want to ask "
             "how long the two of you have known each other."),
            ("cup",
             "You slide the cup away from its wet ring. A chip in the glaze makes a pale crescent at the rim. "
             "You watch the crescent while Irina turns to cough into her sleeve. When she turns back, "
             "the rim still faces the same way. The wet ring is under the cup again. "
             "Your fingertip is still on the handle. You take it off."),
        )[choice]
        state["encounter"] = encounter
        cues = {}
        if encounter == "server":
            cues[0] = ("the other chair", "chair")
        elif encounter == "cup":
            cues[0] = ("You slide the cup", "cup")

        return self._scene(state, "key", [
            response,
            "You try to stand. The floor feels far enough away that your knees give a little. "
            "Irina sets both feet flat and waits for you to copy her. “Which foot is colder?” "
            "Your left sock is wet where your shoe let in the rain. Saying so helps. "
            "She counts softly while you breathe. You feel both feet against the tiles.",
            "She stays quiet while you drink. The coffee is too sweet. It is exactly what you wanted. "
            "You fold the receipt once, print facing out, and tuck it into your coat pocket. "
            "Your room key comes up with your hand. The little nick beside the round hole catches in the lining.",
            "From the kitchen the server calls, “Are you waiting for anyone? I'm locking up in a minute.” "
            "Irina looks across the road at the pharmacy's dark window. “Go as far as the pharmacy,” she says. "
            "“See if you can still see me from there.”",
            "You ask if she'll leave while you're gone. She holds out her hand for the key. "
            "“I'll give it back when you come back for it.” You turn it over in your palm. "
            "She keeps her hand open while you decide.",
        ], [
            "Give Irina the key to hold.",
            "Keep the key in your pocket.",
        ], audio={"paragraphs": cues})

    def _across_the_street(self, state, choice):
        state["gave_key"] = choice == 0
        key_response = (
            "You put the key into Irina's palm. She closes her hand around it and draws the loose cuff over her fist. "
            "The absence of the key in your pocket gives you the uneasy freedom of someone who's left a door unlocked."
            if state["gave_key"] else
            "You slip the key back into your coat. Its nick grazes your knuckle on the way in. "
            "Irina folds her empty hand into her lap. “All right,” she says. “You know where I'll be.”"
        )
        return self._scene(state, "street", [
            key_response,
            "Outside, cold rain gets down between your collar and your neck. That feels useful. "
            "You cross the road while there's a gap between cars and stand under the pharmacy awning. "
            "The shutters are down behind the glass. A paper sign lists the opening hours with Saturday crossed out.",
            "You turn to look back. Somebody is sitting in your chair. They have your coat and the thumb-size repair "
            "on its left shoulder. As you watch, they put one foot flat on the tiles, then the other. "
            "Irina leans over and waits for them to speak. You can see her mouth, and you know what she's asking. "
            "Which foot is colder?",
            "You pull at your own coat until you can see the repair. It's still there, wet through. "
            "Across the road the other you lifts the cup with their left hand. The server has gone. "
            "The chairs around your table are all upside down.",
            "A car comes between you and the café, throwing dirty water up onto the kerb. "
            "You expect the sight to clear when it passes. The other you is looking straight at the pharmacy now, "
            "with the cup suspended an inch from their mouth. Irina reaches across and turns their face back toward her.",
        ], [
            "Cross back and go through the café door.",
            "Knock on the pharmacy window.",
            "Keep walking toward home.",
        ], title="Across the Street", audio={"location": "street", "choices": {1: "tap"}})

    def _second_bell(self, state, choice):
        street, return_text = (
            ("door", [
                "You cross back. Through the café glass you can still see the back of your own coat. "
                "The bell above the door rings twice before your hand touches the handle. "
                "As you open it, you watch the little brass tongue. It hangs perfectly still.",
                "Inside, you turn to look at the table. Your chair is empty and pulled out. "
                "Your left hand is curled around something warm. When you look down, it's the cup. "
                "You put it down carefully. Irina presses a napkin against the spilled coffee at its foot.",
            ]),
            ("window", [
                "You knock once on the pharmacy window. The glass answers with two knocks. The sound is too hollow for glass. "
                "You hear it through the bones of your wrist, the way you can hear the pipes at home if you touch the radiator. "
                "You lift your hand. The answering knocks repeat.",
                "The shutter behind the window rolls up. Irina is on the other side, with her palm flat on the pane opposite yours. "
                "You pull back and catch your hip on the café table. Across the road, through the glass behind her, "
                "the pharmacy is shuttered. On the café glass, two fresh circles of fog are level with your palms.",
            ]),
            ("walk", [
                "You walk toward home. At the corner you stop to scrape grit from your heel with the edge of your other shoe. "
                "Your sole is torn and leaves a little hooked mark when you drag it. "
                "There's a pale hooked mark on the pavement ahead. Then another, at exactly the length of your stride.",
                "You follow them as far as your building. There is a hooked mark at shoulder height on the entrance door. "
                "You push the door open. It is the door of the café. The stairs have become a row of chairs tipped onto tables. "
                "At the far end Irina pulls out your chair with her foot.",
            ]),
        )[choice]
        state["street"] = street

        cues = {2: ("You sit.", "bell")}
        if street == "door":
            cues[0] = ("The bell above the door", "bell")
        elif street == "window":
            cues[0] = ("The glass answers", "answer")
        return self._scene(state, "table", [
            *return_text,
            "You sit. The brass bell sounds twice. Irina waits for a third ring with her head tilted, then relaxes. "
            "“I thought you might stay over there,” she says. Her voice has lost the little catch that sounded like yours.",
            "You search the window for movement. Across the road the pharmacy sign is dark. There is a lamp on your table now, "
            "with a scorch on the shade. Your lamp at home has that scorch. You struck a match too close to it once when "
            "the bulb went out.",
            "Beneath the cloth, your knee finds a chipped corner. You have to get past the same corner of your desk every time "
            "you get out of bed. You run your thumb over the chip. From the outside it would look as if you were simply "
            "sitting with a woman and trying to think of something to say.",
            "“Put your hand on this end,” Irina says. “We can see what's underneath.” "
            "She rests her hand on the rim of the cup. You can't tell which of you let go of it last.",
        ], [
            "Lift the cloth and look underneath yourself.",
            "Ask Irina to move the table.",
        ], title="The Second Bell", audio={"location": "cafe", "paragraphs": cues})

    def _receipt(self, state, choice):
        state["felt_draft"] = choice == 0
        if state["felt_draft"]:
            response = [
                "You lift the cloth and crouch. Beneath the tabletop there's a nail bent sideways over two empty screw holes. "
                "You hammered it flat when it caught your sleeve at home. There is still a bit of blue thread under its head.",
                "A thin draught cuts across your ankle. You hold the hanging cloth aside and feel where the cold begins, "
                "a finger's width from the floor. There's a line under your bedroom door about that wide. "
                "The bell rings and stops. Down here the cold goes right on moving.",
                "When you sit up again, the lamp is on the other end of the table. You hadn't heard it move. "
                "Irina is staring at the space under the cloth as if she wants to ask what you saw.",
            ]
        else:
            response = [
                "Irina lifts her side of the table without putting down the cup. One leg clears the floor. "
                "You brace yourself for the scrape of the other three legs. Instead you hear a drawer being pulled open.",
                "The underside of the table is the front of your bedside drawer. The little brass pull is cold against your knee. "
                "There is a long moment when the cup and Irina's hand are upright and the rest of the table is on its side.",
                "Then the table is back. Then the table is back. Then the table is back.",
            ]

        return self._scene(state, "receipt", [
            *response,
            "Something crinkles when you shift in your seat. You take the receipt out of your pocket. "
            "The price and the time are still there. At one edge of the fold you can see blue ink pressing through from the back. "
            "It was dry when you put it away. Now the paper is soft enough to split if you rub it.",
            "Irina puts the cup down. Her finger brushes the paper and comes away with a little blue stain. "
            "“You can turn it over,” she says. “I won't mind.”",
            "You think of the front door closing behind the last person you had over. That was a week when an hour could go by "
            "and you'd still be listening to the empty landing, trying to decide whether you heard their footsteps coming back. "
            "Irina waits with her hands in her lap.",
        ], [
            "Turn the receipt over and read it.",
            "Ask Irina to read it to you.",
            "Fold it smaller without looking.",
        ], glitch_line=None if state["felt_draft"] else 2)

    def _room(self, state, choice):
        receipt, response = (
            ("read",
             "You turn it over. The blue ink says, “Please stay until I fall asleep.” It is your handwriting. "
             "The p in asleep has the extra loop it always gets when you write against your knee. "
             "You can remember holding a pen that way. The memory stops at the tip of the pen."),
            ("heard",
             "“Please stay until I fall asleep,” Irina says, looking straight at you. You are still holding the receipt "
             "with the printed side up. You wait for her to reach for it. She never does. Somewhere nearby a spring squeaks, "
             "like the edge of a mattress taking someone's weight."),
            ("folded",
             "You fold the receipt a second time, keeping the ink inside. Irina raises her hand a little and drops it. "
             "You put the paper in your pocket. Your fingers stay closed around it for a while. "
             "It fits there like something you've carried for a long time."),
        )[choice]
        state["receipt"] = receipt

        encounter_echo = {
            "server": "From the corner by the wardrobe you hear the server say, “I watched you carry it over.” "
                      "You wait for the scratch of his pencil. The room stays quiet.",
            "irina": "The mug on the desk has a little white hill of sugar at the bottom. "
                     "“You always leave the last mouthful,” Irina says. There is the same quiet affection in her voice.",
            "cup": "You find the pale crescent in the rim of the mug on the desk. You push the mug a little to one side. "
                   "The wet ring goes with it. You take your finger off the handle.",
        }[state["encounter"]]
        street_echo = {
            "door": "Above the bedroom door hangs the café bell. Two rings come from it while the brass tongue stays still.",
            "window": "The dark bedroom window gives one hollow knock. Without touching it you hear two more, close enough "
                      "to feel in the wrist you used at the pharmacy.",
            "walk": "At shoulder height on your bedroom door is the hooked mark your heel left on the pavement. "
                    "Your shoe makes the same shape when you drag it against the floor.",
        }[state["street"]]
        key_echo = (
            "Irina unfolds her hand and puts your key on the desk. You see the nick in it. "
            "“I said I'd give it back,” she says."
            if state["gave_key"] else
            "You take your key out of your own pocket and put it on the desk. The nick catches once on the lining. "
            "Irina reaches toward the key, then moves her hand to her knee."
        )

        return self._scene(state, "listen", [
            response,
            "The lamp goes out. In the dark you hear the slow knock of the radiator. Once, a pause, twice. "
            "When the light comes back the radiator is beside your bed. Your hand is still on the corner of the table. "
            "Beneath your fingers it's the corner of your desk. There is no café around it.",
            encounter_echo,
            street_echo,
            "Irina is beside the bed, sitting with her back very straight. Her shoes have made no wet marks on the floor. "
            "One part of you has been waiting a long time to find somebody there.",
            key_echo,
            "The bedroom door is shut. You know what's on the other side on an ordinary night. "
            "Your neighbour comes home late and has to pull their door toward them before the lock turns. "
            "Sometimes you hear them set their bag down so they can use both hands. "
            "Tonight the sound keeps falling so close to the bell that you can't tell which of them you heard.",
        ], [label for label, _, _ in self._door_cues(state)], title="The Room",
            audio={"location": "room", "paragraphs": {1: ("The lamp goes out.", "blackout")}})

    @staticmethod
    def _door_cues(state):
        if state["felt_draft"]:
            familiar = (
                "Follow the draught under the door.", "draft",
                "You kneel in the strip of cold, the way you did under the cloth. It smells of stairwell stone and washing powder. "
                "The bell starts up. You wait with your knuckles on the floor. The air falters for a second as somebody "
                "passes the gap outside. You hear a bag brush the door. The air comes back, colder. "
                "You stand with your hand on the knob.",
            )
        else:
            label, response = {
                "door": (
                    "Follow the sound of the café bell.",
                    "You follow the two rings. There's space between them for one step, and then another. "
                    "You stop by the door and hear the second ring repeat by itself. The doorknob is warm in your hand "
                    "like the handle of a cup you've held for a long time. Down at floor level, nothing moves.",
                ),
                "window": (
                    "Follow the repeating knocks.",
                    "You touch the window where you heard the first knock. The answer comes from the bedroom door. "
                    "You cross the room and put your palm flat on the wood. The other side knocks twice, and the same "
                    "two little blows travel into your wrist. You find the knob in the dark without looking down.",
                ),
                "walk": (
                    "Follow the hooked marks.",
                    "Another hooked mark appears beside the one on the door, a stride higher. You remember following "
                    "those marks home. You can still feel the grit under your heel. The new mark is already there "
                    "when you lift your foot. You set it down again with your hand on the knob.",
                ),
            }[state["street"]]
            familiar = (label, "echo", response)

        return (
            ("Listen for your neighbour on the landing.", "landing",
             "You let the bell finish. There is a small pause that keeps getting longer. At last you hear the bag go down, "
             "then the familiar pull on the door. The lock sticks. Your neighbour sighs and says, “Wrong one,” "
             "then tries another key. Irina opens her mouth halfway through the sentence. She closes it again. "
             "You put your hand on the knob on your side."),
            familiar,
            ("Ask Irina what's on the other side.", "irina",
             "“When it rings twice,” Irina says, “the server will ask if you're waiting for anyone.” "
             "You wait. The bell rings twice. Somewhere on the other side of the door, a man asks, "
             "“Are you waiting for anyone?” His voice has the exact weary lift you heard from the café kitchen. "
             "He starts the question again before you can answer. You put your hand on the knob."),
        )

    def _at_the_door(self, state, choice):
        _, cue, response = self._door_cues(state)[choice]
        state["exit_cue"] = cue

        text = [
            response,
            "Irina asks if you want her to keep counting with you. You can still feel what it was like to put both feet "
            "flat on the tiles and have somebody wait while you found the words for the cold. "
            "She has set her feet flat again, ready for you to copy her.",
            "You look down at your hand on the knob. It would take very little to let go of it.",
        ]
        choices = [
            "Ask Irina to stay.",
            "Let Irina go and stay in the room.",
            "Open the bedroom door.",
        ]
        if cue == "irina" and state["receipt"] == "read":
            text.append(
                "Irina rubs her wrists. “I was cold at the café,” she says. "
                "You look down at the receipt in your other hand. A few words in your own handwriting "
                "feel more certain than anything you can remember."
            )
            choices.append("Tell her she was warm.")
        return self._scene(state, "door", text, choices)

    def _aftermath(self, state, choice):
        if choice == 3:
            return self._scene(state, "irina_memory", [
                "“You were warm.”",
                "She lets go of her sleeves. “Yes. You gave me your coat.” "
                "You can feel it against your shoulders, still damp from the rain. "
                "You've been wearing it all night.",
                "She looks down at her hands. “I remember both now. Please stop.”",
            ], [
                "Let Irina go and stay in the room.",
                "Tell her she wanted to stay.",
            ], audio={"location": "quiet"})
        if choice == 0:
            title, text = "The Ghost in the Room", self._ghost(state)
        elif choice == 1:
            title, text = "Quiet Resignation", self._resignation(state)
        elif state["exit_cue"] in ("landing", "draft"):
            title, text = "Cold Clarity", self._clarity()
        else:
            title, text = "Fractured", self._fractured(state)

        ending_audio = {
            "The Ghost in the Room": {"paragraphs": {len(text) - 3: ("the radiator knocks", "radiator")}},
            "Quiet Resignation": {"location": "quiet", "paragraphs": {len(text) - 1: ("knocks once", "pipe")}},
            "Cold Clarity": {"location": "quiet"},
            "Fractured": {"location": "cafe"},
        }[title]
        return self._scene(state, "restart", text, ["Restart"], title=title, audio=ending_audio)

    def _irina_memory(self, state, choice):
        if choice == 0:
            return self._scene(state, "restart", [
                "“I'll stop,” you say. Irina holds one sleeve in her fist again.",
                *self._resignation(state),
            ], ["Restart"], title="Quiet Resignation", audio={"location": "quiet", "paragraphs": {4: ("knocks once", "pipe")}})

        return self._scene(state, "restart", [
            "“You wanted to stay.”",
            "Irina draws a breath. “I wanted to stay,” she says. She looks toward the door halfway through. "
            "You wait until she says it again without looking.",
            "In the morning, Irina brings you coffee. She sets the cup down with the handle facing away from you.",
            "At the café, she knew to put it on your left. You rest your hands in your lap and wait.",
            "She waits for you to tell her where it goes.",
        ], ["Restart"], title="A Better Irina", audio={"paragraphs": {2: ("sets the cup down", "cup")}})

    @staticmethod
    def _ghost(state):
        receipt_echo = {
            "read": "“Until I fall asleep,” you add. The words are easier to say now that you've seen them written down.",
            "heard": "“Until I fall asleep,” she says for you. You let her finish.",
            "folded": "You keep the paper folded. Everything you need to ask her is already out in the room.",
        }[state["receipt"]]
        key_echo = (
            "You put the key back in her open hand."
            if state["gave_key"] else
            "You turn the key over on the desk until the nick is under your thumb."
        )
        return [
            "“Stay,” you say. Irina moves her chair closer. The feet make the ordinary sound of wood on a bare floor. "
            "For a while there is enough warmth between you that you can feel it through the wool of your coat.",
            receipt_echo,
            key_echo,
            "The clock on your desk says 11:47. The minute hand twitches. You wait for it to move forward. "
            "Irina sets her hand over yours and the two of you listen while the radiator knocks once, waits, and knocks twice.",
            "There is a spare cup on the shelf above the desk. You fetch it for her. "
            "Her spoon clinks against the rim. Once, a pause, then twice.",
            "Before she can tell you how she takes it, you put two sugars in her cup.",
        ]

    @staticmethod
    def _resignation(state):
        receipt_echo = {
            "read": "You turn the receipt print side up. You remember what you wrote. The paper can stay on the desk until morning.",
            "heard": "You put the receipt down print side up. All you have of the words is the way she said them.",
            "folded": "You press the crease flat and put the folded receipt on the desk. The blue ink stays inside.",
        }[state["receipt"]]
        return [
            "“You can go,” you say. You let the knob turn back under your palm. Irina draws her coat around herself. "
            "For a second you're embarrassed at making a guest get up. Then you see the empty chair and realize you never heard her stand.",
            receipt_echo,
            "You sit on the edge of the bed, work off your shoes and peel away the wet sock. "
            "The floor is cold on that side and a little warmer on the other. "
            "You put both feet down. You can give the answer in your own voice now, even with nobody there to ask.",
            "The radiator knocks once. There is a longer pause than you expected. You reach for the lamp and turn it off.",
        ]

    @staticmethod
    def _clarity():
        return [
            "The knob turns. Cold air comes all the way up your sleeves. A ceiling bulb lights the landing and the worn strip of carpet "
            "where everybody on this floor turns toward the stairs. Somebody has set a shopping bag down against the wall.",
            "Your neighbour looks up with two keys in their hand. “Did I wake you?” they ask. "
            "You tell them you've been up for a while. They ask if you'd mind holding the bag while they get their door open. "
            "It is heavier at one end. Something glass rolls gently into something else.",
            "From your room there is a single knock. You wait for the rest of it while your neighbour tries the lock. "
            "When their door opens, you lift the bag over the threshold and step into the light.",
        ]

    @staticmethod
    def _fractured(state):
        cue_echo = (
            "The man stops halfway through asking if you're waiting for anyone. You hear the end of his question from your own mouth."
            if state["exit_cue"] == "irina" else {
                "door": "The bell rings twice behind you. Your hand is still on the knob. Irina raises a finger for the bill.",
                "window": "Two knocks come from the table. When you look down, your own knuckles are against the wood.",
                "walk": "The hooked marks run to your chair. You try to stop at the last one. Your shoe has already come down on it.",
            }[state["street"]]
        )
        return [
            "You open the bedroom door into the café. The windows are dark and the clock says 11:47. "
            "Your chair is occupied. There's rain on the shoulders of the coat the person in it is wearing. "
            "They put one foot flat on the floor and then the other.",
            cue_echo,
            "There is a pad in your hand now. The top slip is already made out for one coffee. You can see the wet ring "
            "on the table where it belongs. You mean to leave the slip at the empty seat. You put it down between them.",
            "Irina turns to the person in your chair. “Which foot is colder?” "
            "The person begins to answer. Behind you, someone opens the bedroom door.",
        ]
