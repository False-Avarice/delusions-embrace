from contextlib import redirect_stdout
from io import StringIO
from itertools import product
from pathlib import Path
import runpy
import unittest
from unittest.mock import Mock, patch

from app import app
import main


class GameTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def choose(self, scene, index=0):
        response = self.client.post('/choice', json={
            'choice_history': scene['choice_history'],
            'choice_index': index,
        })
        self.assertEqual(response.status_code, 200, response.get_json())
        return response.get_json()

    def test_all_endings_and_glitch_are_reachable_in_both_versions(self):
        intro = self.client.post('/start').get_json()
        endings = set()
        glitch_paths = 0

        for path in product(range(3), repeat=5):
            with self.subTest(path=path):
                first, second, time, loop, identity = path
                scene = intro
                web_glitch = False
                for index in (0, first, second, 0, time, loop, 0, identity, 0, 0):
                    scene = self.choose(scene, index)
                    web_glitch |= any('f e a t u r e s' in text for text in scene['text'])

                terminal_lines = []
                with patch.multiple(
                    main,
                    get_choice=Mock(side_effect=path),
                    type_text=Mock(side_effect=lambda line, **_: terminal_lines.append(line)),
                    clear_screen=Mock(),
                ), patch.object(main.time, 'sleep'), redirect_stdout(StringIO()):
                    main.main()

                terminal_glitch = any('f e a t u r e s' in text for text in terminal_lines)
                self.assertEqual(web_glitch, terminal_glitch)
                glitch_paths += web_glitch
                ending_start = next(i for i, line in enumerate(terminal_lines) if 'ENDING:' in line)
                endings.add(terminal_lines[ending_start])
                self.assertEqual(scene['text'][:-2], terminal_lines[ending_start + 1:-1])
                self.assertEqual(scene['choices'], ['Restart'])

        self.assertEqual(len(endings), 4)
        self.assertGreater(glitch_paths, 0)
        self.assertLess(glitch_paths, 243)

    def test_restart_resets_the_run(self):
        intro = self.client.post('/start').get_json()
        scene = intro
        for _ in range(10):
            scene = self.choose(scene)
        self.assertEqual(scene['choices'], ['Restart'])
        restarted = self.choose(scene)
        self.assertEqual(restarted, intro)
        self.assertEqual(self.choose(restarted), self.choose(intro))

    def test_choice_retries_and_independent_runs(self):
        first_tab = self.choose(self.client.post('/start').get_json())
        expected = self.choose(first_tab, 1)
        second_tab = self.choose(self.client.post('/start').get_json())
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
            {'choice_history': [0] * 11, 'choice_index': 0},
        )
        for payload in payloads:
            with self.subTest(payload=payload):
                response = self.client.post('/choice', json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn('error', response.get_json())

    def test_terminal_exits_cleanly_when_input_closes(self):
        output = StringIO()
        with patch('builtins.input', side_effect=EOFError), patch.object(main.time, 'sleep'):
            with redirect_stdout(output):
                runpy.run_path(str(Path(main.__file__)), run_name='__main__')
        self.assertIn('Game exited.', output.getvalue())
