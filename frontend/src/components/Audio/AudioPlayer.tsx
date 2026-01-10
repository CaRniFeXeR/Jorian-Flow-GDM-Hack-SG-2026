import { useEffect, useRef, useState, useImperativeHandle, forwardRef } from 'react';
import { generateTtsApiV1TtsTtsPost } from '../../client';
import type { TtsResponse } from '../../client/types.gen';

export interface AudioPlayerRef {
    play: () => Promise<void>;
    pause: () => void;
    isPlaying: () => boolean;
}

interface AudioPlayerProps {
    text: string;
    onLoadStart?: () => void;
    onLoadComplete?: () => void;
    onError?: (error: Error) => void;
    autoPlay?: boolean;
    hidden?: boolean;
}

const AudioPlayer = forwardRef<AudioPlayerRef, AudioPlayerProps>(({
    text,
    onLoadStart,
    onLoadComplete,
    onError,
    autoPlay = false,
    hidden = false,
}, ref) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const [isLoading, setIsLoading] = useState(false);
    const [currentSrc, setCurrentSrc] = useState<string | null>(null);

    useImperativeHandle(ref, () => ({
        play: async () => {
            if (audioRef.current) {
                try {
                    await audioRef.current.play();
                } catch (err) {
                    console.error('Error playing audio:', err);
                    onError?.(err as Error);
                }
            }
        },
        pause: () => {
            if (audioRef.current) {
                audioRef.current.pause();
            }
        },
        isPlaying: () => {
            return audioRef.current ? !audioRef.current.paused : false;
        },
    }));

    useEffect(() => {
        if (!text.trim()) {
            return;
        }

        const loadAudio = async () => {
            try {
                setIsLoading(true);
                onLoadStart?.();

                // Call TTS API to generate audio
                const response = await generateTtsApiV1TtsTtsPost({
                    body: { text },
                    baseUrl: 'http://localhost:8000',
                });

                if (response.error) {
                    throw new Error('Failed to generate TTS audio');
                }

                const ttsData = response.data as TtsResponse;
                const filename = ttsData.filename;

                // Construct audio URL
                const audioUrl = `http://localhost:8000/api/v1/tts/audio/${filename}`;

                setCurrentSrc(audioUrl);
                setIsLoading(false);
                onLoadComplete?.();

                // Auto play if requested
                if (autoPlay && audioRef.current) {
                    audioRef.current.play().catch((err) => {
                        console.error('Error playing audio:', err);
                        onError?.(err);
                    });
                }
            } catch (error) {
                setIsLoading(false);
                const err = error instanceof Error ? error : new Error('Unknown error');
                onError?.(err);
                console.error('Error loading audio:', err);
            }
        };

        loadAudio();
    }, [text, autoPlay, onLoadStart, onLoadComplete, onError]);

    if (hidden) {
        return (
            <audio
                ref={audioRef}
                src={currentSrc || undefined}
                style={{ display: 'none' }}
            >
                Your browser does not support the audio element.
            </audio>
        );
    }

    return (
        <div className="audio-player">
            {isLoading && (
                <div className="text-sm text-gray-500">Loading audio...</div>
            )}
            <audio
                ref={audioRef}
                src={currentSrc || undefined}
                controls
                className="w-full"
            >
                Your browser does not support the audio element.
            </audio>
        </div>
    );
});

AudioPlayer.displayName = 'AudioPlayer';

export default AudioPlayer;
