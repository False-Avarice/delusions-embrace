import subprocess
import sys
import unittest

from app import MAX_CHOICES_PER_RUN, STORY_VERSION, app
from game_engine import GameEngine
import main


class GameTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def start(self):
        response = self.client.post('/start')
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    def choose(self, scene, index=0):
        response = self.client.post('/choice', json={
            'choice_history': scene['choice_history'],
            'story_version': scene['story_version'],
            'choice_index': index,
        })
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def test_every_path_finishes_and_door_outcomes_follow_the_selected_cue(self):
        engine = GameEngine()
        initial = engine.get_initial_state()
        stack = [(initial, engine.process_step(initial), (), 0)]
        endings = set()
        while stack:
            state, scene, choices, words = stack.pop()
            words += sum(len(text.split()) for text in scene['text'])
            for paragraph, (anchor, _) in scene['audio'].get('paragraphs', {}).items():
                self.assertIn(anchor, scene['text'][paragraph])
            for index in scene['audio'].get('choices', {}):
                self.assertIn(index, range(len(scene['choices'])))

            if state['current_step'] == 'restart':
                endings.add(scene['title'])
                orientation, action = choices[-2:]
                if action == 'Open the bedroom door.':
                    found_landing = orientation in (
                        'Listen for your neighbour on the landing.',
                        'Follow the draught under the door.',
                    )
                    self.assertEqual(scene['title'], 'Cold Clarity' if found_landing else 'Fractured')
                elif action == 'Ask Irina to stay.':
                    self.assertEqual(scene['title'], 'The Ghost in the Room')
                elif action == 'Tell her she wanted to stay.':
                    self.assertEqual(orientation, 'Tell her she was warm.')
                    self.assertEqual(choices[-4:-2], (
                        'Turn the receipt over and read it.',
                        "Ask Irina what's on the other side.",
                    ))
                    self.assertEqual(scene['title'], 'A Better Irina')
                else:
                    self.assertEqual(action, 'Let Irina go and stay in the room.')
                    self.assertEqual(scene['title'], 'Quiet Resignation')
                self.assertEqual(scene['choices'], ['Restart'])
                self.assertLessEqual(words, 2200)
                continue

            self.assertLess(len(choices), MAX_CHOICES_PER_RUN)
            self.assertTrue(scene['choices'])
            for index, choice in enumerate(scene['choices']):
                next_state = state.copy()
                next_scene = engine.process_step(next_state, index)
                stack.append((next_state, next_scene, (*choices, choice), words))

        self.assertEqual(endings, {
            'Cold Clarity', 'Fractured', 'Quiet Resignation', 'The Ghost in the Room', 'A Better Irina',
        })

    def test_room_pays_off_each_street_route_and_respects_the_receipt_choice(self):
        cases = (
            (0, 0, 0, 0, 'brass tongue stays still', 'unfolds her hand', 'Follow the draught under the door.'),
            (0, 0, 1, 0, 'brass tongue stays still', 'unfolds her hand', 'Follow the sound of the café bell.'),
            (1, 1, 1, 1, 'dark bedroom window gives one hollow knock', 'take your key out', 'Follow the repeating knocks.'),
            (2, 0, 1, 2, 'hooked mark your heel left', 'unfolds her hand', 'Follow the hooked marks.'),
        )
        for street, key, table, receipt, street_echo, key_echo, cue in cases:
            with self.subTest(street=street, table=table):
                scene = self.start()
                for index in (0, 0, key, street, table):
                    scene = self.choose(scene, index)
                if table:
                    self.assertIn('Then the table is back.', scene['text'][scene['glitch_line']])
                else:
                    self.assertIsNone(scene['glitch_line'])
                room = self.choose(scene, receipt)
                self.assertEqual(room['title'], 'The Room')
                text = ' '.join(room['text'])
                self.assertIn(street_echo, text)
                self.assertIn(key_echo, text)
                self.assertEqual(room['choices'][1], cue)

                ending = self.choose(self.choose(room, 0), 1)
                text += ' '.join(ending['text'])
                if receipt == 2:
                    self.assertNotIn('Please stay until I fall asleep', text)
                    self.assertIn('The blue ink stays inside.', text)
                else:
                    self.assertIn('Please stay until I fall asleep', text)

    def test_restart_resets_the_run(self):
        intro = self.start()
        scene = intro
        for _ in range(MAX_CHOICES_PER_RUN):
            if scene['choices'] == ['Restart']:
                break
            scene = self.choose(scene)
        self.assertEqual(scene['choices'], ['Restart'])
        restarted = self.choose(scene)
        self.assertEqual(restarted, intro)
        self.assertEqual(self.choose(restarted), self.choose(intro))

    def test_secret_choice_requires_reading_the_receipt_and_asking_irina(self):
        scene = self.start()
        for _ in range(5):
            scene = self.choose(scene)
        for receipt in range(3):
            room = self.choose(scene, receipt)
            for cue in range(3):
                with self.subTest(receipt=receipt, cue=cue):
                    at_the_door = self.choose(room, cue)
                    self.assertEqual(
                        'Tell her she was warm.' in at_the_door['choices'],
                        receipt == 0 and cue == 2,
                    )

    def test_secret_choice_lets_the_player_stop_or_continue_and_restart(self):
        intro = self.start()
        scene = intro
        for index in (0, 0, 0, 0, 0, 0, 2, 3):
            scene = self.choose(scene, index)
        self.assertIn('Please stop.', ' '.join(scene['text']))

        stop = self.choose(scene, 0)
        self.assertEqual(stop['title'], 'Quiet Resignation')
        self.assertIn("I'll stop", stop['text'][0])

        ending = self.choose(scene, 1)
        self.assertEqual(ending['title'], 'A Better Irina')
        self.assertEqual(len(ending['choice_history']), MAX_CHOICES_PER_RUN)
        self.assertEqual(self.choose(ending), intro)

    def test_sound_cues_follow_the_window_route_into_the_secret_ending(self):
        def cues(scene):
            anchors = scene['audio'].get('paragraphs', {})
            return [anchors[key] for key in sorted(anchors, key=int)]

        opening = self.choose(self.start())
        self.assertEqual([sound for _, sound in cues(opening)], ['chair', 'bell', 'cup'])
        server = self.choose(opening)
        self.assertEqual(cues(server), [])
        street = self.choose(server)
        self.assertEqual(cues(street), [['Outside, cold rain', 'street']])
        self.assertEqual(street['audio']['choices'], {'1': 'tap'})
        window = self.choose(street, 1)
        self.assertEqual(window['audio']['location'], 'street')
        self.assertEqual([sound for _, sound in cues(window)], ['answer', 'cafe', 'bell'])

        receipt = self.choose(window)
        self.assertEqual(receipt['audio']['location'], 'cafe')
        room = self.choose(receipt)
        self.assertEqual(room['audio'].get('location', receipt['audio']['location']), 'cafe')
        self.assertEqual(cues(room), [['The lamp goes out.', 'blackout']])
        door = self.choose(room, 2)
        self.assertEqual(door['audio']['location'], 'room')
        warning = self.choose(door, 3)
        self.assertEqual(warning['audio'].get('location', door['audio']['location']), 'room')
        self.assertEqual(cues(warning), [['Please stop.', 'hush']])
        morning = self.choose(warning, 1)
        self.assertEqual(morning['audio']['location'], 'quiet')
        self.assertEqual(cues(morning), [['sets the cup down', 'cup']])

    def test_choice_retries_and_independent_runs(self):
        first_tab = self.choose(self.start())
        expected = self.choose(first_tab, 1)
        second_tab = self.choose(self.start())
        self.assertNotEqual(self.choose(second_tab, 0), expected)

        self.client = app.test_client()
        self.assertEqual(self.choose(first_tab, 1), expected)

    def test_invalid_choices_and_history_return_json_errors(self):
        payloads = (
            [],
            {},
            {'choice_history': []},
            {'choice_history': [], 'choice_index': True},
            {'choice_history': [], 'choice_index': 1},
            {'choice_history': [0], 'choice_index': 3},
            {'choice_history': [0, -1], 'choice_index': 0},
            {'choice_history': [0] * (MAX_CHOICES_PER_RUN + 1), 'choice_index': 0},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                if isinstance(payload, dict):
                    payload = {**payload, 'story_version': STORY_VERSION}
                response = self.client.post('/choice', json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.get_json())

    def test_previous_story_history_requires_a_fresh_run(self):
        for version in ({}, {'story_version': 1}):
            with self.subTest(version=version):
                response = self.client.post('/choice', json={
                    'choice_history': [0, 1],
                    'choice_index': 0,
                    **version,
                })
                self.assertEqual(response.status_code, 409)

    def test_terminal_renders_the_same_passages_and_ending(self):
        cases = (
            ('Cold Clarity', (0, 2, 1, 1, 0, 2, 1, 2)),
            ('A Better Irina', (0, 0, 0, 0, 0, 0, 2, 3, 1)),
        )
        for ending, choices in cases:
            with self.subTest(ending=ending):
                output = subprocess.run(
                    [sys.executable, '-B', main.__file__, '--instant'],
                    input=''.join(f'{choice + 1}\n' for choice in choices),
                    capture_output=True, text=True, check=True,
                ).stdout
                scene = self.start()
                for index in choices:
                    scene = self.choose(scene, index)
                    for paragraph in scene['text']:
                        self.assertIn(paragraph, output)
                self.assertEqual(scene['title'], ending)
                self.assertIn(ending.upper(), output)

    def test_terminal_exits_cleanly_when_input_closes(self):
        result = subprocess.run(
            [sys.executable, '-B', main.__file__, '--instant'],
            input='', capture_output=True, text=True, check=True,
        )
        self.assertIn('Game exited.', result.stdout)
        self.assertEqual(result.stderr, '')
