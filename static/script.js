import { Soundscape } from './soundscape.js';

document.addEventListener('DOMContentLoaded', () => {
    const storyLog = document.getElementById('story-log');
    const choicesContainer = document.getElementById('choices-container');
    const status = document.getElementById('game-status');
    const revealButton = document.getElementById('reveal-passage');
    const soundButton = document.getElementById('sound-toggle');
    const sound = new Soundscape();
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    const characterDelay = 16;
    const paragraphDelay = 180;
    let choiceHistory = [];
    let storyVersion;
    let choiceSounds = {};

    function updateSoundButton() {
        soundButton.textContent = sound.context ? 'Sound on' : 'Sound off';
        soundButton.setAttribute('aria-pressed', String(Boolean(sound.context)));
    }

    soundButton.hidden = !(window.AudioContext || window.webkitAudioContext);
    soundButton.onclick = async () => {
        const failureMessage = 'Audio could not start. Select Sound to retry.';
        if (status.textContent === failureMessage) status.textContent = '';
        soundButton.disabled = true;
        try {
            if (sound.context) await sound.disable();
            else await sound.enable();
        } catch {
            await sound.disable();
            status.textContent = failureMessage;
        } finally {
            updateSoundButton();
            soundButton.disabled = false;
        }
    };
    document.addEventListener('visibilitychange', async () => {
        const ctx = sound.context;
        if (!ctx) return;
        try {
            if (document.hidden) {
                sound.beginPassage();
                await ctx.suspend();
            } else {
                await ctx.resume();
            }
        } catch {
            if (sound.context === ctx) {
                await sound.disable();
                updateSoundButton();
            }
        }
    });
    window.addEventListener('pagehide', () => {
        sound.disable();
        updateSoundButton();
    });

    async function requestScene(url, options) {
        const response = await fetch(url, { method: 'POST', ...options });
        if (!response.ok) {
            const error = new Error(`Game request failed: ${response.status}`);
            error.status = response.status;
            throw error;
        }
        return response.json();
    }

    async function startGame() {
        choicesContainer.hidden = true;
        status.textContent = '';

        let scene;
        try {
            scene = await requestScene('/start');
        } catch {
            status.textContent = 'The game could not start. Try again.';
            showChoices(['Try again'], startGame);
            return;
        }
        handleResponse(scene);
    }

    function handleResponse(scene) {
        const audio = scene.audio || {};
        const cues = audio.paragraphs || {};
        choiceSounds = audio.choices || {};
        sound.beginPassage(audio.location);
        let passedCue = false;
        choiceHistory = scene.choice_history;
        storyVersion = scene.story_version;
        if (choiceHistory.length === 0) {
            storyLog.replaceChildren();
        }
        choicesContainer.replaceChildren();
        choicesContainer.hidden = true;

        const passage = document.createElement('section');
        passage.className = 'passage';
        if (scene.title) {
            const heading = document.createElement(choiceHistory.length === 0 ? 'h1' : 'h2');
            heading.textContent = scene.title;
            passage.appendChild(heading);
        }
        const paragraphs = document.createElement('div');
        passage.appendChild(paragraphs);
        storyLog.appendChild(passage);

        let timer;

        function finishPassage() {
            const revealHadFocus = document.activeElement === revealButton;
            revealButton.hidden = true;
            revealButton.onclick = null;
            showChoices(scene.choices);
            if (revealHadFocus) storyLog.focus({ preventScroll: true });
        }

        function revealPassage() {
            clearTimeout(timer);
            const firstCue = Object.values(cues)[0];
            if (!passedCue && firstCue) sound.play(firstCue[1]);
            paragraphs.replaceChildren();
            for (const text of scene.text) {
                const paragraph = document.createElement('p');
                paragraph.textContent = text;
                paragraphs.appendChild(paragraph);
            }
            const storyTop = storyLog.getBoundingClientRect().top;
            storyLog.scrollTop += passage.getBoundingClientRect().top - storyTop;
            finishPassage();
        }

        function typeParagraph(index) {
            if (index === scene.text.length) {
                finishPassage();
                return;
            }
            const paragraph = document.createElement('p');
            paragraphs.appendChild(paragraph);
            const text = scene.text[index];
            const started = performance.now();
            const cue = cues[index];
            const anchor = cue ? text.indexOf(cue[0]) : -1;
            let triggered = false;

            function typeCharacters() {
                const length = Math.min(text.length, 1 + Math.floor((performance.now() - started) / characterDelay));
                paragraph.textContent = text.slice(0, length);
                if (!triggered && anchor >= 0 && length >= anchor + cue[0].length) {
                    sound.play(cue[1]);
                    passedCue = true;
                    triggered = true;
                }
                storyLog.scrollTop = storyLog.scrollHeight;
                if (length < text.length) {
                    timer = setTimeout(typeCharacters, characterDelay);
                    return;
                }
                if (index === scene.glitch_line) paragraph.classList.add('glitch');
                timer = setTimeout(() => typeParagraph(index + 1), paragraphDelay);
            }

            typeCharacters();
        }

        if (reducedMotion.matches || scene.text.length === 0) {
            revealPassage();
        } else {
            revealButton.hidden = false;
            revealButton.onclick = revealPassage;
            typeParagraph(0);
        }
    }

    function showChoices(choices, onChoice = makeChoice) {
        choicesContainer.replaceChildren();
        choices.forEach((text, index) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'choice-btn';
            button.textContent = text;
            button.onclick = () => onChoice(index, text);
            choicesContainer.appendChild(button);
        });
        choicesContainer.hidden = choices.length === 0;
    }

    async function makeChoice(index, choiceText) {
        if (choiceSounds[index]) sound.play(choiceSounds[index]);
        const buttons = choicesContainer.querySelectorAll('button');
        buttons.forEach(button => button.disabled = true);
        status.textContent = '';

        let scene;
        try {
            scene = await requestScene('/choice', {
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    choice_index: index,
                    choice_history: choiceHistory,
                    story_version: storyVersion
                })
            });
        } catch (error) {
            if (error.status === 409) {
                status.textContent = 'The story has changed. Start a new run.';
                showChoices(['Start a new run'], startGame);
                return;
            }
            status.textContent = 'Your choice could not be loaded. Select it again to retry.';
            buttons.forEach(button => button.disabled = false);
            return;
        }

        if (scene.choice_history.length > 0) {
            const chosen = document.createElement('p');
            chosen.className = 'selected-choice';
            chosen.textContent = `> ${choiceText}`;
            storyLog.appendChild(chosen);
        }
        handleResponse(scene);
    }

    startGame();
});
