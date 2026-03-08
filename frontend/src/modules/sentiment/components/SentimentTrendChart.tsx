import { useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { SentimentTrendPoint } from '../types';

interface SentimentTrendChartProps {
  data: SentimentTrendPoint[];
  days?: number;
}

const SentimentTrendChart = ({ data, days = 7 }: SentimentTrendChartProps) => {
  // Transform data for chart
  const chartData = useMemo(() => {
    return data.map((point) => ({
      date: new Date(point.date).toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      }),
      score: point.score,
      sentiment: point.sentiment,
      volume: point.volume,
      fullDate: point.date,
    }));
  }, [data]);

  // Calculate average score for reference line
  const averageScore = useMemo(() => {
    if (data.length === 0) return 0;
    return data.reduce((sum, point) => sum + point.score, 0) / data.length;
  }, [data]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      const score = data.score;
      const sentiment = data.sentiment;
      
      return (
        <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3">
          <p className="text-sm font-semibold text-gray-900 mb-1">
            {new Date(data.fullDate).toLocaleDateString('en-US', { 
              weekday: 'short',
              month: 'short', 
              day: 'numeric',
              year: 'numeric'
            })}
          </p>
          <div className="space-y-1">
            <p className="text-sm text-gray-600">
              Score: <span className="font-semibold text-gray-900">{score.toFixed(1)}/100</span>
            </p>
            <p className="text-sm text-gray-600">
              Sentiment: <span className={`font-semibold capitalize ${
                sentiment === 'positive' ? 'text-green-600' :
                sentiment === 'negative' ? 'text-red-600' :
                'text-gray-600'
              }`}>
                {sentiment}
              </span>
            </p>
            <p className="text-sm text-gray-600">
              Articles: <span className="font-semibold text-gray-900">{data.volume}</span>
            </p>
          </div>
        </div>
      );
    }
    return null;
  };

  // Determine fill gradient based on overall trend
  const getGradientColors = () => {
    if (data.length < 2) return { start: '#9CA3AF', end: '#6B7280' };
    
    const firstScore = data[0].score;
    const lastScore = data[data.length - 1].score;
    
    if (lastScore > firstScore + 10) {
      // Positive trend
      return { start: '#34D399', end: '#10B981' };
    } else if (lastScore < firstScore - 10) {
      // Negative trend
      return { start: '#F87171', end: '#EF4444' };
    } else {
      // Neutral trend
      return { start: '#60A5FA', end: '#3B82F6' };
    }
  };

  const gradientColors = getGradientColors();

  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-[300px] bg-gray-50 rounded-lg">
        <div className="text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <p className="mt-2 text-sm text-gray-600">No trend data available</p>
          <p className="text-xs text-gray-500 mt-1">Search for a topic to see sentiment trends</p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-4 flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Sentiment Trend</h3>
          <p className="text-sm text-gray-500">Last {days} days</p>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600">Average Score</p>
          <p className="text-lg font-bold text-gray-900">{averageScore.toFixed(1)}</p>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={300}>
        <AreaChart
          data={chartData}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor={gradientColors.start} stopOpacity={0.8} />
              <stop offset="95%" stopColor={gradientColors.end} stopOpacity={0.1} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
          <XAxis
            dataKey="date"
            tick={{ fill: '#6B7280', fontSize: 12 }}
            tickLine={{ stroke: '#E5E7EB' }}
          />
          <YAxis
            domain={[0, 100]}
            tick={{ fill: '#6B7280', fontSize: 12 }}
            tickLine={{ stroke: '#E5E7EB' }}
            label={{ 
              value: 'Sentiment Score', 
              angle: -90, 
              position: 'insideLeft',
              style: { fill: '#6B7280', fontSize: 12 }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            y={averageScore}
            stroke="#9CA3AF"
            strokeDasharray="5 5"
            label={{
              value: 'Avg',
              position: 'right',
              fill: '#6B7280',
              fontSize: 11,
            }}
          />
          <Area
            type="monotone"
            dataKey="score"
            stroke={gradientColors.end}
            strokeWidth={2}
            fillOpacity={1}
            fill="url(#colorScore)"
            animationDuration={1000}
          />
        </AreaChart>
      </ResponsiveContainer>

      {/* Trend indicator */}
      <div className="mt-4 flex items-center justify-center gap-4 text-sm">
        {data.length >= 2 && (
          <>
            {data[data.length - 1].score > data[0].score + 10 ? (
              <div className="flex items-center gap-1 text-green-600">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Improving</span>
              </div>
            ) : data[data.length - 1].score < data[0].score - 10 ? (
              <div className="flex items-center gap-1 text-red-600">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Declining</span>
              </div>
            ) : (
              <div className="flex items-center gap-1 text-gray-600">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14" />
                </svg>
                <span className="font-medium">Stable</span>
              </div>
            )}
            <span className="text-gray-400">|</span>
            <span className="text-gray-600">
              <span className="font-medium text-gray-900">
                {Math.abs(data[data.length - 1].score - data[0].score).toFixed(1)}
              </span> point change
            </span>
          </>
        )}
      </div>
    </div>
  );
};

export default SentimentTrendChart;
