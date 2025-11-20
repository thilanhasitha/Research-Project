// routes/routeConfig.js
// Central configuration for all routes in your application
export const ROUTES = {
  // Main navigation routes
  HOME: '/',
  EXPLAINABLEAI: '/explainableai',
  FRAUDE: '/fraude',
  PORTFOLIO: '/portfolio',
  HELP: '/help',
  CHECKOUT: '/checkout',
  PROFILE: '/profile',
 
  // User routes
  
  LOGIN: '/login',
  REGISTER: '/register',
 
  // Support routes
  CONTACT: '/contact',
  FAQ: '/faq',
  SUPPORT: '/support',
  
 
//   // Admin routes
//   POLICY_FORM: '/policy-form',
//   PRODUCT_INPUT: '/product-input',
 
//   // Dynamic routes
//   PRODUCT_DETAIL: '/product/:id',
//   SEARCH: '/search',
};

// Navigation items for Header
export const NAV_ITEMS = [
  { name: 'Home', path: ROUTES.HOME },
  { name: 'Explainableai', path: ROUTES.EXPLAINABLEAI },
  { name: 'Fraude', path: ROUTES.FRAUDE },
  { name: 'Portfolio', path: ROUTES.PORTFOLIO },
  { name: 'Help', path: ROUTES.HELP },

];

// Footer menu links
export const FOOTER_MENU_LINKS = [
  { name: 'Home', path: ROUTES.HOME },
  { name: 'Explainableai', path: ROUTES.EXPLAINABLEAI },
  { name: 'Fraude', path: ROUTES.FRAUDE },
  { name: 'Portfolio', path: ROUTES.PORTFOLIO },
];

// Footer support links
export const FOOTER_SUPPORT_LINKS = [
  
  { name: 'FAQ', path: ROUTES.FAQ },
  { name: 'Submit a request', path: ROUTES.SUPPORT },
 
];

// Footer additional links
export const FOOTER_ADDITIONAL_LINKS = [
  { name: 'Contact us', path: ROUTES.CONTACT },
  
];