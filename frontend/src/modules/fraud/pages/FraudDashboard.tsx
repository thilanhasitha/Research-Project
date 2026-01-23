import Card from '../../../shared/components/Card';
import Button from '../../../shared/components/Button';

const FraudDashboard = () => {
  const alerts = [
    {
      id: '1',
      symbol: 'XYZ',
      type: 'Suspicious Volume',
      severity: 'High',
      time: '10 mins ago',
      description: 'Unusual trading volume spike detected'
    },
    {
      id: '2',
      symbol: 'ABC',
      type: 'Price Manipulation',
      severity: 'Critical',
      time: '1 hour ago',
      description: 'Potential pump and dump pattern'
    },
    {
      id: '3',
      symbol: 'DEF',
      type: 'Unusual Pattern',
      severity: 'Medium',
      time: '3 hours ago',
      description: 'Irregular trading pattern detected'
    }
  ];

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      'Critical': 'bg-red-100 text-red-800 border-red-200',
      'High': 'bg-orange-100 text-orange-800 border-orange-200',
      'Medium': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      'Low': 'bg-blue-100 text-blue-800 border-blue-200'
    };
    return colors[severity] || colors.Low;
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Fraud Detection</h1>
        <p className="text-gray-600">Real-time suspicious trading pattern detection</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Active Alerts</p>
            <p className="text-3xl font-bold text-gray-900">12</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Critical</p>
            <p className="text-3xl font-bold text-red-600">3</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Under Investigation</p>
            <p className="text-3xl font-bold text-yellow-600">5</p>
          </div>
        </Card>
        <Card>
          <div className="text-center">
            <p className="text-sm text-gray-600 mb-1">Resolved Today</p>
            <p className="text-3xl font-bold text-green-600">8</p>
          </div>
        </Card>
      </div>

      {/* Alerts List */}
      <Card title="Recent Alerts">
        <div className="space-y-4">
          {alerts.map((alert) => (
            <div key={alert.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="text-lg font-bold text-gray-900">{alert.symbol}</span>
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold border ${getSeverityColor(alert.severity)}`}>
                      {alert.severity}
                    </span>
                    <span className="text-sm text-gray-500">{alert.time}</span>
                  </div>
                  <p className="text-sm font-medium text-gray-900 mb-1">{alert.type}</p>
                  <p className="text-sm text-gray-600">{alert.description}</p>
                </div>
                <div className="flex gap-2 ml-4">
                  <Button size="sm" variant="outline">View Details</Button>
                  <Button size="sm" variant="primary">Investigate</Button>
                </div>
              </div>
            </div>
          ))}
        </div>

        <div className="mt-6 text-center">
          <Button variant="outline">Load More Alerts</Button>
        </div>
      </Card>
    </div>
  );
};

export default FraudDashboard;
