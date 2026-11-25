document.addEventListener('DOMContentLoaded', () => {
    const storyLog = document.getElementById('story-log');
    const choicesContainer = document.getElementById('choices-container');
    const status = document.getElementById('game-status');
    let choiceHistory = [];

    startGame();

    async function requestScene(url, options) {
        const response = await fetch(url, { method: 'POST', ...options });
        if (!response.ok) throw new Error(`Game request failed: ${response.status}`);
        return response.json();
    }

    async function startGame() {
        choicesContainer.replaceChildren();
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

    function handleResponse(data) {
        choiceHistory = data.choice_history;
        if (choiceHistory.length === 0) {
            storyLog.replaceChildren();
        }

        // Clear choices container to prepare for new choices
        choicesContainer.innerHTML = '';
        choicesContainer.classList.remove('visible');
        choicesContainer.classList.add('hidden');

        if (data.text && data.text.length > 0) {
            // Add a small break before new text if not intro
            if (storyLog.children.length > 0) {
                 const spacer = document.createElement('div');
                 spacer.style.height = "20px";
                 storyLog.appendChild(spacer);
            }

            typeWriterSequence(data.text, 0, () => {
                showChoices(data.choices);
            });
        } else {
            showChoices(data.choices);
        }
    }

    function typeWriterSequence(lines, index, callback) {
        if (index >= lines.length) {
            callback();
            return;
        }

        const line = lines[index];
        const p = document.createElement('p');
        
        // Check for glitch keyword (simple heuristic based on text content or manual marking)
        // In this implementation, we'll just check if the text contains wide spacing "f e a t u r e s"
        if (line.includes("f e a t u r e s")) {
            p.classList.add('glitch');
            p.setAttribute('data-text', line);
        }

        storyLog.appendChild(p);

        // Simple typing effect
        let charIndex = 0;
        const speed = 30; // ms per char

        function typeChar() {
            if (charIndex < line.length) {
                p.textContent += line.charAt(charIndex);
                charIndex++;
                storyLog.scrollTop = storyLog.scrollHeight; // Auto-scroll to bottom
                setTimeout(typeChar, speed + (Math.random() * 20));
            } else {
                // Line finished
                setTimeout(() => {
                    typeWriterSequence(lines, index + 1, callback);
                }, 500); // Pause between lines
            }
        }

        // Handle empty lines as breaks
        if (line.trim() === "") {
            p.innerHTML = "&nbsp;"; // Maintain height
            setTimeout(() => {
                typeWriterSequence(lines, index + 1, callback);
            }, 300);
        } else {
            typeChar();
        }
    }

    function showChoices(choices, onChoice = makeChoice) {
        if (!choices || choices.length === 0) return;

        choices.forEach((choiceText, index) => {
            const btn = document.createElement('button');
            btn.classList.add('choice-btn');
            btn.textContent = choiceText;
            btn.onclick = () => onChoice(index, choiceText);
            choicesContainer.appendChild(btn);
        });

        choicesContainer.classList.remove('hidden');
        // Small delay to fade in
        setTimeout(() => {
            choicesContainer.classList.add('visible');
        }, 100);
    }

    async function makeChoice(index, choiceText) {
        const buttons = choicesContainer.querySelectorAll('button');
        buttons.forEach(b => b.disabled = true);
        status.textContent = '';

        let scene;
        try {
            scene = await requestScene('/choice', {
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ choice_index: index, choice_history: choiceHistory })
            });
        } catch {
            status.textContent = 'Your choice could not be loaded. Select it again to retry.';
            buttons.forEach(b => b.disabled = false);
            return;
        }

        if (scene.choice_history.length > 0) {
            const choiceP = document.createElement('p');
            choiceP.textContent = `> ${choiceText}`;
            choiceP.style.color = 'var(--highlight-color)';
            choiceP.style.fontStyle = 'italic';
            choiceP.style.marginTop = '10px';
            choiceP.style.marginBottom = '20px';
            storyLog.appendChild(choiceP);
            storyLog.scrollTop = storyLog.scrollHeight;
        }

        handleResponse(scene);
    }
});
