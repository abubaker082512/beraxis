import React from 'react';
import { motion } from 'framer-motion';
import { 
  Phone, 
  PhoneIncoming, 
  PhoneOutgoing, 
  CheckCircle2, 
  XCircle, 
  TrendingUp, 
  BarChart3, 
  Clock,
  ArrowUpRight,
  ArrowDownRight
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  AreaChart, 
  Area 
} from 'recharts';

const data = [
  { name: 'Mon', calls: 400, success: 240 },
  { name: 'Tue', calls: 300, success: 139 },
  { name: 'Wed', calls: 200, success: 980 },
  { name: 'Thu', calls: 278, success: 390 },
  { name: 'Fri', calls: 189, success: 480 },
  { name: 'Sat', calls: 239, success: 380 },
  { name: 'Sun', calls: 349, success: 430 },
];

const stats = [
  { 
    name: 'Total Calls', 
    value: '12,458', 
    change: '+12.5%', 
    trend: 'up', 
    icon: Phone,
    color: 'text-primary'
  },
  { 
    name: 'Active Campaigns', 
    value: '24', 
    change: '+3', 
    trend: 'up', 
    icon: BarChart3,
    color: 'text-blue-500'
  },
  { 
    name: 'Success Rate', 
    value: '84.2%', 
    change: '-2.1%', 
    trend: 'down', 
    icon: CheckCircle2,
    color: 'text-emerald-500'
  },
  { 
    name: 'Total Revenue', 
    value: '$45,231', 
    change: '+18.2%', 
    trend: 'up', 
    icon: TrendingUp,
    color: 'text-amber-500'
  }
];

export default function DashboardOverview() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Dashboard Overview</h1>
          <p className="text-muted-foreground">Welcome back, here's what's happening today.</p>
        </div>
        <div className="flex space-x-3">
          <button className="px-4 py-2 bg-muted border border-border rounded-lg text-sm font-medium hover:bg-muted/80 transition-all flex items-center">
            <Clock className="w-4 h-4 mr-2" />
            Last 7 Days
          </button>
          <button className="px-4 py-2 bg-primary text-black rounded-lg text-sm font-bold hover:bg-primary/90 transition-all neon-glow">
            Export Report
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, i) => (
          <motion.div
            key={stat.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
          >
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm hover:border-primary/30 transition-all">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className={`p-2 rounded-lg bg-muted ${stat.color}`}>
                    <stat.icon className="w-6 h-6" />
                  </div>
                  <div className={`flex items-center text-xs font-bold px-2 py-1 rounded-full ${
                    stat.trend === 'up' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'
                  }`}>
                    {stat.trend === 'up' ? <ArrowUpRight className="w-3 h-3 mr-1" /> : <ArrowDownRight className="w-3 h-3 mr-1" />}
                    {stat.change}
                  </div>
                </div>
                <h3 className="text-sm font-medium text-muted-foreground">{stat.name}</h3>
                <p className="text-2xl font-bold font-display mt-1">{stat.value}</p>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Chart */}
        <Card className="lg:col-span-2 border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Call Activity</CardTitle>
            <CardDescription>Daily call volume vs success rate</CardDescription>
          </CardHeader>
          <CardContent className="h-[400px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="colorCalls" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#00E5FF" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#00E5FF" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F1F23" vertical={false} />
                <XAxis 
                  dataKey="name" 
                  stroke="#94A3B8" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false} 
                />
                <YAxis 
                  stroke="#94A3B8" 
                  fontSize={12} 
                  tickLine={false} 
                  axisLine={false} 
                  tickFormatter={(value) => `${value}`}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111113', border: '1px solid #1F1F23', borderRadius: '8px' }}
                  itemStyle={{ color: '#00E5FF' }}
                />
                <Area 
                  type="monotone" 
                  dataKey="calls" 
                  stroke="#00E5FF" 
                  strokeWidth={3}
                  fillOpacity={1} 
                  fill="url(#colorCalls)" 
                />
                <Area 
                  type="monotone" 
                  dataKey="success" 
                  stroke="#10B981" 
                  strokeWidth={2}
                  fillOpacity={0} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
          <CardHeader>
            <CardTitle>Recent Calls</CardTitle>
            <CardDescription>Latest interactions across all campaigns</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {[
                { name: 'Alice Johnson', status: 'Success', time: '2m ago', type: 'outbound' },
                { name: 'Bob Smith', status: 'Voicemail', time: '15m ago', type: 'outbound' },
                { name: 'Charlie Brown', status: 'Failed', time: '1h ago', type: 'inbound' },
                { name: 'Diana Prince', status: 'Success', time: '2h ago', type: 'outbound' },
                { name: 'Edward Norton', status: 'Success', time: '4h ago', type: 'inbound' },
              ].map((call, i) => (
                <div key={i} className="flex items-center justify-between group cursor-pointer">
                  <div className="flex items-center space-x-3">
                    <div className={`p-2 rounded-full ${
                      call.type === 'outbound' ? 'bg-primary/10 text-primary' : 'bg-blue-500/10 text-blue-500'
                    }`}>
                      {call.type === 'outbound' ? <PhoneOutgoing className="w-4 h-4" /> : <PhoneIncoming className="w-4 h-4" />}
                    </div>
                    <div>
                      <p className="text-sm font-medium group-hover:text-primary transition-colors">{call.name}</p>
                      <p className="text-xs text-muted-foreground">{call.time} • {call.type}</p>
                    </div>
                  </div>
                  <div className={`text-xs font-bold px-2 py-1 rounded-full ${
                    call.status === 'Success' ? 'bg-emerald-500/10 text-emerald-500' : 
                    call.status === 'Voicemail' ? 'bg-amber-500/10 text-amber-500' : 'bg-red-500/10 text-red-500'
                  }`}>
                    {call.status}
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-8 py-2 text-sm font-medium text-primary hover:underline">
              View All Logs
            </button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
