const recordings = ['rain.mp3', 'chair.wav', 'cup.wav', 'bell.wav', 'tap.wav', 'inside-knock.wav', 'radiator.wav'];

const mixes = {
    cafe:   { rain: 0.52, cutoff: 1350, hum: 0.002 },
    street: { rain: 0.55, cutoff: 8500, hum: 0 },
    room:   { rain: 0,    cutoff: 1350, hum: 0.011 },
    quiet:  { rain: 0,    cutoff: 1350, hum: 0 }
};

async function loadRecordings(ctx) {
    const entries = await Promise.all(recordings.map(async file => {
        const response = await fetch(new URL('audio/' + file, import.meta.url));
        if (!response.ok) throw new Error('Could not load ' + file);
        const buffer = await ctx.decodeAudioData(await response.arrayBuffer());
        return [file.split('.')[0], buffer];
    }));
    return Object.fromEntries(entries);
}

// Start each fade from the current mix, including when a reader skips mid-transition.
function fade(param, target, now, duration, delay) {
    const current = param.value;
    if (param.cancelAndHoldAtTime) param.cancelAndHoldAtTime(now);
    else param.cancelScheduledValues(now);
    param.setValueAtTime(current, now);
    if (delay) param.setValueAtTime(current, now + delay);
    param.linearRampToValueAtTime(target, now + delay + duration);
}

export class Soundscape {
    constructor() {
        this.context = null;
        this.location = 'cafe';
        this.buffers = null;
    }

    async enable() {
        const Context = window.AudioContext || window.webkitAudioContext;
        const ctx = new Context();
        this.context = ctx;
        await ctx.resume();
        if (this.context !== ctx) return;
        if (!this.buffers) this.buffers = await loadRecordings(ctx);
        if (this.context !== ctx) return;

        this.master = ctx.createGain();
        this.master.connect(ctx.destination);

        // Keep one continuous take of rain as the player crosses the glass.
        const rain = ctx.createBufferSource();
        rain.buffer = this.buffers.rain;
        rain.loop = true;
        this.rainFilter = ctx.createBiquadFilter();
        this.rainFilter.type = 'lowpass';
        this.rainFilter.Q.value = -3;
        this.rainFilter.frequency.value = mixes[this.location].cutoff;
        this.rain = ctx.createGain();
        this.rain.gain.value = 0;
        rain.connect(this.rainFilter).connect(this.rain).connect(this.master);
        rain.start();

        this.hum = ctx.createGain();
        this.hum.gain.value = 0;
        this.hum.connect(this.master);
        for (const frequency of [73, 147.2]) {
            const note = ctx.createOscillator();
            note.frequency.value = frequency;
            note.connect(this.hum);
            note.start();
        }
        this.beginPassage();
        this.applyMix(0.55);
    }

    disable() {
        const ctx = this.context;
        this.context = null;
        this.master = null;
        this.effects = null;
        this.hum = null;
        this.rain = null;
        this.rainFilter = null;
        if (ctx && ctx.state !== 'closed') return ctx.close();
    }

    applyMix(duration, delay = 0) {
        if (!this.master) return;
        const mix = mixes[this.location];
        const now = this.context.currentTime;
        fade(this.rain.gain, mix.rain, now, duration, delay);
        fade(this.rainFilter.frequency, mix.cutoff, now, duration, delay);
        fade(this.hum.gain, mix.hum, now, duration, delay);
    }

    enter(location, duration = 0.65, delay = 0) {
        if (this.location === location) return;
        this.location = location;
        this.applyMix(duration, delay);
    }

    beginPassage(location) {
        if (location) this.enter(location);
        if (!this.master) return;
        const ctx = this.context;
        if (this.effects) {
            const previous = this.effects;
            previous.gain.setTargetAtTime(0, ctx.currentTime, 0.008);
            setTimeout(() => previous.disconnect(), 50);
        }
        this.effects = ctx.createGain();
        this.effects.connect(this.master);
    }

    sample(name, when, level = 1, destination = this.effects) {
        const ctx = this.context;
        const source = ctx.createBufferSource();
        source.buffer = this.buffers[name];
        const gain = ctx.createGain();
        gain.gain.value = level;
        source.connect(gain).connect(destination);
        source.onended = () => {
            source.disconnect();
            gain.disconnect();
        };
        source.start(when);
    }

    radiator(when) {
        this.sample('radiator', when);
        this.sample('radiator', when + 0.84, 0.87);
        this.sample('radiator', when + 1.09, 0.96);
    }

    play(cue) {
        // Track the reader's location even when sound is off or the tab is hidden.
        if (cue === 'cafe' || cue === 'street') return this.enter(cue);
        if (cue === 'hush') return this.enter('quiet', 0.035);
        if (cue === 'blackout') this.enter('room', 0.88, 0.24);

        const ctx = this.context;
        if (!this.effects || ctx.state !== 'running' || document.hidden) return;
        const now = ctx.currentTime;
        switch (cue) {
            case 'chair':
            case 'cup':
            case 'bell':
                this.sample(cue, now);
                break;
            case 'tap':
                // The tap follows the player's finger across the scene request.
                this.sample('tap', now, 1, this.master);
                break;
            case 'answer':
                this.sample('inside-knock', now + 0.32);
                this.sample('inside-knock', now + 0.65, 0.88);
                break;
            case 'blackout':
                this.sample('bell', now);
                this.radiator(now + 1.18);
                break;
            case 'radiator':
                this.radiator(now);
                break;
            case 'pipe':
                this.sample('radiator', now);
                break;
        }
    }
}
