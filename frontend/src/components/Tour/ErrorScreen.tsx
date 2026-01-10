import React from 'react';
import { motion } from 'framer-motion';
import { AlertCircle, ArrowLeft } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface ErrorScreenProps {
    message?: string;
}

const ErrorScreen: React.FC<ErrorScreenProps> = ({
    message = "This theme is not possible in the current area. Please try a different theme that matches your location.",
}) => {
    const navigate = useNavigate();

    return (
        <div className="relative w-full h-screen overflow-hidden bg-gray-50 flex flex-col">
            {/* Map at 30% top */}
            <div className="absolute top-0 left-0 right-0" style={{ height: '30vh' }}>
                {/* Map would go here - using placeholder for now */}
            </div>

            {/* Error Content */}
            <div className="absolute bottom-0 left-0 right-0 bg-white rounded-t-[2.5rem] shadow-2xl flex flex-col" style={{ height: '70vh' }}>
                <div className="flex-1 flex flex-col items-center justify-center px-6">
                    <motion.div
                        initial={{ scale: 0.8, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        transition={{ duration: 0.3 }}
                        className="text-center max-w-md"
                    >
                        <div className="mb-6">
                            <div className="inline-flex items-center justify-center w-20 h-20 bg-red-100 rounded-full mb-4">
                                <AlertCircle className="w-10 h-10 text-red-600" />
                            </div>
                        </div>
                        <h2 className="text-3xl font-bold text-gray-900 mb-4">
                            Theme Not Available
                        </h2>
                        <p className="text-lg text-gray-600 mb-8">
                            {message}
                        </p>
                        <motion.button
                            whileHover={{ scale: 1.05 }}
                            whileTap={{ scale: 0.95 }}
                            onClick={() => navigate('/')}
                            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-blue-500 text-white text-lg font-semibold rounded-2xl shadow-lg hover:shadow-xl transition-shadow flex items-center mx-auto"
                        >
                            <ArrowLeft className="w-5 h-5 mr-2" />
                            Go Back
                        </motion.button>
                    </motion.div>
                </div>
            </div>
        </div>
    );
};

export default ErrorScreen;
