// All times are in seconds on the Web Audio clock.
export class Soundscape {
    constructor() {
        this.context = null;
        this.location = 'cafe';
    }

    async enable() {
        const Context = window.AudioContext || window.webkitAudioContext;
        this.context = new Context();
        const ctx = this.context;
        await ctx.resume();
        if (this.context !== ctx) return;

        this.master = ctx.createGain();
        this.master.gain.value = 1.25;
        this.master.connect(ctx.destination);

        // Independent rain channels keep the street wide even at low volume.
        this.noise = ctx.createBuffer(2, ctx.sampleRate * 6, ctx.sampleRate);
        for (let channel = 0; channel < this.noise.numberOfChannels; channel++) {
            const samples = this.noise.getChannelData(channel);
            for (let i = 0; i < samples.length; i++) samples[i] = (Math.random() - 0.5) * 0.85;
            // Scatter short resonant droplets over the steady wash.
            for (let drop = 0; drop < 110; drop++) {
                const start = Math.floor(Math.random() * samples.length);
                const pitch = 450 + Math.random() * 1750;
                const strength = 0.35 + Math.random() * 0.45;
                for (let i = 0; i < ctx.sampleRate * 0.04; i++) {
                    const t = i / ctx.sampleRate;
                    samples[(start + i) % samples.length] += strength * Math.exp(-150 * t) * Math.sin(2 * Math.PI * pitch * t);
                }
            }
        }
        const rain = ctx.createBufferSource();
        rain.buffer = this.noise;
        rain.loop = true;
        this.rainFilter = ctx.createBiquadFilter();
        this.rainFilter.type = 'lowpass';
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
        this.beginPassage(this.location);
    }

    disable() {
        const ctx = this.context;
        this.context = null;
        this.effects = null;
        this.noise = null;
        this.master = null;
        this.hum = null;
        this.rain = null;
        this.rainFilter = null;
        if (ctx && ctx.state !== 'closed') return ctx.close();
    }

    beginPassage(location) {
        if (location) this.location = location;
        const ctx = this.context;
        if (!ctx || !this.master || ctx.state === 'closed') return;
        // One-shots scheduled for the previous passage end when the reader moves on.
        if (this.effects) {
            const previous = this.effects;
            previous.gain.setTargetAtTime(0, ctx.currentTime, 0.008);
            setTimeout(() => previous.disconnect(), 50);
        }
        this.effects = ctx.createGain();
        this.effects.connect(this.master);

        const mix = {
            cafe: [0.09, 1150, 0.012],
            street: [0.14, 2900, 0.003],
            room: [0.012, 550, 0.014],
            quiet: [0, 550, 0]
        }[this.location];
        const [rain, cutoff, hum] = mix;
        this.rain.gain.setTargetAtTime(rain, ctx.currentTime, 0.25);
        this.rainFilter.frequency.setTargetAtTime(cutoff, ctx.currentTime, 0.25);
        this.hum.gain.setTargetAtTime(hum, ctx.currentTime, 0.25);
    }

    // A short attack and independent decay for each resonance keep the impacts soft.
    strike(frequency, strength, duration, delay, destination = this.effects) {
        const ctx = this.context;
        const start = ctx.currentTime + delay;
        const note = ctx.createOscillator();
        const envelope = ctx.createGain();
        note.frequency.value = frequency;
        envelope.gain.setValueAtTime(0.00001, start);
        envelope.gain.exponentialRampToValueAtTime(strength, start + 0.007);
        envelope.gain.exponentialRampToValueAtTime(0.00001, start + duration);
        note.connect(envelope).connect(destination);
        note.start(start);
        note.stop(start + duration);
        note.onended = () => envelope.disconnect();
    }

    play(cue) {
        const ctx = this.context;
        if (!ctx || ctx.state !== 'running' || !this.effects || document.hidden) return;
        switch (cue) {
            case 'bell':
                for (const offset of [0, 0.24]) {
                    this.strike(1054, 0.095, 1.05, offset);
                    this.strike(2383, 0.034, 0.6, offset);
                    this.strike(3320, 0.014, 0.28, offset);
                }
                break;
            case 'tap':
                // The player's tap belongs to the click, so let its tail cross the request.
                this.strike(630, 0.15, 0.095, 0, this.master);
                this.strike(1610, 0.045, 0.075, 0, this.master);
                break;
            case 'answer':
            case 'radiator':
            case 'blackout':
            case 'pipe': {
                const rhythms = {
                    answer: [0.32, 0.55],
                    radiator: [0, 0.7, 0.91],
                    blackout: [0.4, 1.1, 1.31],
                    pipe: [0]
                };
                if (cue === 'blackout') this.strike(1054, 0.033, 0.9, 0);
                for (const offset of rhythms[cue]) {
                    this.strike(166, 0.14, 0.19, offset);
                    this.strike(403, 0.052, 0.15, offset);
                    this.strike(807, 0.018, 0.26, offset);
                }
                break;
            }
            case 'chair':
            case 'cup': {
                const chair = cue === 'chair';
                const duration = chair ? 0.56 : 0.3;
                const scrape = ctx.createBufferSource();
                scrape.buffer = this.noise;
                const filter = ctx.createBiquadFilter();
                filter.type = 'bandpass';
                filter.frequency.value = chair ? 480 : 1600;
                const envelope = ctx.createGain();
                const now = ctx.currentTime;
                envelope.gain.setValueAtTime(0, now);
                envelope.gain.linearRampToValueAtTime(0.11, now + 0.08);
                envelope.gain.exponentialRampToValueAtTime(0.0001, now + duration);
                scrape.connect(filter).connect(envelope).connect(this.effects);
                scrape.start(now);
                scrape.stop(now + duration + 0.01);
                scrape.onended = () => envelope.disconnect();
                if (chair) {
                    this.strike(112, 0.09, 0.14, duration);
                } else {
                    this.strike(1840, 0.065, 0.22, 0.21);
                    this.strike(2713, 0.018, 0.14, 0.21);
                }
                break;
            }
        }
    }
}
