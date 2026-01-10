import React from 'react';
import { motion } from 'framer-motion';
import { ArrowRight, Sparkles } from 'lucide-react';
import { useOnboarding } from '../../context/OnboardingContext';

interface WelcomeScreenProps {
    onNext: () => void;
}

const WelcomeScreen: React.FC<WelcomeScreenProps> = ({ onNext }) => {
    const { fetchThemes, userLocation } = useOnboarding();

    const handleGetStarted = async () => {
        // Trigger theme fetching in the background
        // Don't wait for it to complete - it will load while user selects preferences
        if (userLocation.latitude !== null && userLocation.longitude !== null) {
            fetchThemes().catch(error => {
                console.error('Error fetching themes in background:', error);
            });
        }
        
        // Move to next step immediately
        onNext();
    };

    return (
        <motion.div
            key="step0"
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -300, opacity: 0 }}
            transition={{ duration: 0.3 }}
            className="flex flex-col items-center justify-center h-full max-w-2xl mx-auto"
        >
            <motion.div
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: 0.1 }}
                className="mb-8"
            >
                <Sparkles className="w-20 h-20 text-blue-600" />
            </motion.div>
            <h1 className="text-4xl font-bold text-gray-900 mb-4 text-center">
                Create Your Perfect Walking Tour
            </h1>
            <p className="text-lg text-gray-600 mb-8 text-center max-w-md">
                Discover personalized walking tours tailored to your interests. Let's create your perfect adventure.
            </p>
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={handleGetStarted}
                className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white text-lg font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-shadow"
            >
                Get Started
                <ArrowRight className="inline-block ml-2 w-5 h-5" />
            </motion.button>
        </motion.div>
    );
};

export default WelcomeScreen;
