declare global {
    interface Window {
        MIDIjs: {
            play: (url: string) => void;
            stop: () => void;
        };
    }
}

export {};