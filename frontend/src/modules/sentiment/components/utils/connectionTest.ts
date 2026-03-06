// connectionTest.ts
// Utility to test backend connection and display responses

export interface ConnectionTestResult {
  success: boolean;
  endpoint: string;
  status: number;
  data?: any;
  error?: string;
  responseTime: number;
}

/**
 * Test connection to backend health endpoint
 */
export const testBackendHealth = async (): Promise<ConnectionTestResult> => {
  const startTime = Date.now();
  const endpoint = '/health';
  
  try {
    const response = await fetch(endpoint);
    const responseTime = Date.now() - startTime;
    
    if (!response.ok) {
      return {
        success: false,
        endpoint,
        status: response.status,
        error: `HTTP ${response.status}: ${response.statusText}`,
        responseTime
      };
    }
    
    const data = await response.json();
    
    return {
      success: true,
      endpoint,
      status: response.status,
      data,
      responseTime
    };
  } catch (error: any) {
    return {
      success: false,
      endpoint,
      status: 0,
      error: error.message || 'Network error',
      responseTime: Date.now() - startTime
    };
  }
};

/**
 * Test news chat endpoint
 */
export const testNewsChatEndpoint = async (question: string = "What's the latest financial news?"): Promise<ConnectionTestResult> => {
  const startTime = Date.now();
  const endpoint = '/news-chat/ask';
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        message: question,
        user_id: 'test_user',
        include_sources: true,
        context_limit: 3
      })
    });
    
    const responseTime = Date.now() - startTime;
    
    if (!response.ok) {
      const errorText = await response.text();
      return {
        success: false,
        endpoint,
        status: response.status,
        error: `HTTP ${response.status}: ${errorText}`,
        responseTime
      };
    }
    
    const data = await response.json();
    
    return {
      success: true,
      endpoint,
      status: response.status,
      data,
      responseTime
    };
  } catch (error: any) {
    return {
      success: false,
      endpoint,
      status: 0,
      error: error.message || 'Network error',
      responseTime: Date.now() - startTime
    };
  }
};

/**
 * Test knowledge base endpoint
 */
export const testKnowledgeBaseEndpoint = async (question: string = "What are the key highlights from the CSE Annual Report?"): Promise<ConnectionTestResult> => {
  const startTime = Date.now();
  const endpoint = '/api/knowledge/query';
  
  try {
    const response = await fetch(endpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        question,
        user_id: 'test_user'
      })
    });
    
    const responseTime = Date.now() - startTime;
    
    if (!response.ok) {
      const errorText = await response.text();
      return {
        success: false,
        endpoint,
        status: response.status,
        error: `HTTP ${response.status}: ${errorText}`,
        responseTime
      };
    }
    
    const data = await response.json();
    
    return {
      success: true,
      endpoint,
      status: response.status,
      data,
      responseTime
    };
  } catch (error: any) {
    return {
      success: false,
      endpoint,
      status: 0,
      error: error.message || 'Network error',
      responseTime: Date.now() - startTime
    };
  }
};

/**
 * Test all endpoints and return summary
 */
export const testAllEndpoints = async (): Promise<{
  newsChat: ConnectionTestResult;
  knowledgeBase: ConnectionTestResult;
}> => {
  console.log('🔍 Testing backend connections...');
  
  const newsChat = await testNewsChatEndpoint();
  console.log('News Chat:', newsChat);
  
  const knowledgeBase = await testKnowledgeBaseEndpoint();
  console.log('Knowledge Base:', knowledgeBase);
  
  return {
    newsChat,
    knowledgeBase
  };
};

/**
 * Display connection test results in console with formatting
 */
export const displayConnectionResults = (results: {
  newsChat: ConnectionTestResult;
  knowledgeBase: ConnectionTestResult;
}) => {
  console.group('🔌 Backend Connection Test Results');
  
  console.log('\n💬 News Chat Endpoint:');
  console.log(`  Status: ${results.newsChat.success ? '✅ Working' : '❌ Failed'}`);
  console.log(`  Response Time: ${results.newsChat.responseTime}ms`);
  if (results.newsChat.data) {
    console.log('  Response:', results.newsChat.data);
  }
  if (results.newsChat.error) {
    console.error('  Error:', results.newsChat.error);
  }
  
  console.log('\n📚 Knowledge Base Endpoint:');
  console.log(`  Status: ${results.knowledgeBase.success ? '✅ Working' : '❌ Failed'}`);
  console.log(`  Response Time: ${results.knowledgeBase.responseTime}ms`);
  if (results.knowledgeBase.data) {
    console.log('  Response:', results.knowledgeBase.data);
  }
  if (results.knowledgeBase.error) {
    console.error('  Error:', results.knowledgeBase.error);
  }
  
  console.groupEnd();
};

export default {
  testBackendHealth,
  testNewsChatEndpoint,
  testKnowledgeBaseEndpoint,
  testAllEndpoints,
  displayConnectionResults
};
