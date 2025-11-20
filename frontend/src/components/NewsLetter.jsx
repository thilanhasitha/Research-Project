import React, { useState } from 'react';
import { Mail } from 'lucide-react';

const Newsletter = () => {
  const [email, setEmail] = useState('');

  const handleEmailSubmit = () => {
    if (email.trim()) {
      console.log('Email submitted:', email);
      alert(`Thank you for subscribing with: ${email}`);
      setEmail('');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleEmailSubmit();
    }
  };

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 text-white">Join the community!</h3>
      <p className="text-gray-400 text-sm mb-4">
        Hey! Drop your Email address and get on the list. Perks? Nice deals, 
        New stuff. Just ask Deals and Early lineups on new collections.
      </p>
      <div className="flex">
        <input
          type="email"
          placeholder="Email Address"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          onKeyPress={handleKeyPress}
          className="flex-1 bg-gray-700 rounded-l-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500 text-white placeholder-gray-400"
        />
        <button 
          onClick={handleEmailSubmit}
          className="bg-purple-600 hover:bg-purple-700 px-4 py-2 rounded-r-lg transition-colors"
        >
          <Mail className="h-4 w-4 text-white" />
        </button>
      </div>
    </div>
  );
};

export default Newsletter;