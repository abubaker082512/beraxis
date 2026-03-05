import React from 'react';
import { motion } from 'framer-motion';
import { 
  Search, 
  Filter, 
  Download, 
  Play, 
  FileText, 
  Smile, 
  Meh, 
  Frown,
  MoreHorizontal,
  PhoneIncoming,
  PhoneOutgoing,
  Clock
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function CallLogs() {
  const logs = [
    { id: 1, contact: 'Alice Johnson', duration: '2:45', sentiment: 'positive', status: 'Answered', time: '10:30 AM', type: 'outbound' },
    { id: 2, contact: 'Bob Smith', duration: '0:15', sentiment: 'neutral', status: 'Voicemail', time: '09:15 AM', type: 'outbound' },
    { id: 3, contact: 'Charlie Brown', duration: '1:20', sentiment: 'negative', status: 'Answered', time: 'Yesterday', type: 'inbound' },
    { id: 4, contact: 'Diana Prince', duration: '5:10', sentiment: 'positive', status: 'Answered', time: 'Yesterday', type: 'outbound' },
    { id: 5, contact: 'Edward Norton', duration: '0:00', sentiment: 'neutral', status: 'Failed', time: 'Yesterday', type: 'inbound' },
    { id: 6, contact: 'Fiona Apple', duration: '3:30', sentiment: 'positive', status: 'Answered', time: '2 days ago', type: 'outbound' },
  ];

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <Smile className="w-4 h-4 text-emerald-500" />;
      case 'neutral': return <Meh className="w-4 h-4 text-amber-500" />;
      case 'negative': return <Frown className="w-4 h-4 text-red-500" />;
      default: return null;
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Call Logs</h1>
          <p className="text-muted-foreground">Review recordings, transcripts, and sentiment analysis.</p>
        </div>
        <Button variant="outline">
          <Download className="w-4 h-4 mr-2" />
          Export CSV
        </Button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-card/50 p-4 rounded-xl border border-border">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search by contact or number..." className="pl-10" />
        </div>
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <select className="bg-background border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
            <option>All Sentiments</option>
            <option>Positive</option>
            <option>Neutral</option>
            <option>Negative</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <Card className="border-border/50 bg-card/50 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-border bg-muted/30">
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Contact</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Type</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Duration</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Sentiment</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Status</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Time</th>
                <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-muted-foreground">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {logs.map((log) => (
                <tr key={log.id} className="hover:bg-white/5 transition-colors group">
                  <td className="px-6 py-4">
                    <p className="text-sm font-medium group-hover:text-primary transition-colors">{log.contact}</p>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center text-xs">
                      {log.type === 'outbound' ? <PhoneOutgoing className="w-3 h-3 mr-2 text-primary" /> : <PhoneIncoming className="w-3 h-3 mr-2 text-blue-500" />}
                      <span className="capitalize">{log.type}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center text-xs text-muted-foreground">
                      <Clock className="w-3 h-3 mr-2" />
                      {log.duration}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      {getSentimentIcon(log.sentiment)}
                      <span className="text-xs capitalize">{log.sentiment}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                      log.status === 'Answered' ? 'bg-emerald-500/10 text-emerald-500' : 
                      log.status === 'Voicemail' ? 'bg-amber-500/10 text-amber-500' : 'bg-red-500/10 text-red-500'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-muted-foreground">
                    {log.time}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center space-x-2">
                      <button className="p-2 hover:bg-primary/10 hover:text-primary rounded-lg transition-all" title="Play Recording">
                        <Play className="w-4 h-4 fill-current" />
                      </button>
                      <button className="p-2 hover:bg-primary/10 hover:text-primary rounded-lg transition-all" title="View Transcript">
                        <FileText className="w-4 h-4" />
                      </button>
                      <button className="p-2 hover:bg-muted rounded-lg transition-all">
                        <MoreHorizontal className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Transcript Preview Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <Card className="border-border/50 bg-card/50 p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-primary" />
            Transcript Preview
          </h3>
          <div className="space-y-4 max-h-64 overflow-y-auto pr-2 no-scrollbar text-sm">
            <div className="flex space-x-3">
              <span className="font-bold text-primary shrink-0">AI:</span>
              <p className="italic">"Hello! Is this Alice Johnson?"</p>
            </div>
            <div className="flex space-x-3">
              <span className="font-bold text-muted-foreground shrink-0">User:</span>
              <p>"Yes, speaking. Who is this?"</p>
            </div>
            <div className="flex space-x-3">
              <span className="font-bold text-primary shrink-0">AI:</span>
              <p className="italic">"I'm Sarah from Beraxis. I'm calling about the AI automation demo you requested. Is now a good time?"</p>
            </div>
            <div className="flex space-x-3">
              <span className="font-bold text-muted-foreground shrink-0">User:</span>
              <p>"Oh, hi Sarah! Yes, I remember. I have a few minutes."</p>
            </div>
          </div>
        </Card>

        <Card className="border-border/50 bg-card/50 p-6">
          <h3 className="text-lg font-bold mb-4 flex items-center">
            <Smile className="w-5 h-5 mr-2 text-primary" />
            Sentiment Analysis
          </h3>
          <div className="space-y-6">
            <div>
              <div className="flex justify-between text-xs mb-2">
                <span className="text-muted-foreground uppercase tracking-wider font-bold">Overall Sentiment</span>
                <span className="text-emerald-500 font-bold">POSITIVE (85%)</span>
              </div>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 neon-glow" style={{ width: '85%' }}></div>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="text-center p-3 rounded-xl bg-emerald-500/5 border border-emerald-500/10">
                <p className="text-lg font-bold text-emerald-500">85%</p>
                <p className="text-[10px] text-muted-foreground uppercase font-bold">Positive</p>
              </div>
              <div className="text-center p-3 rounded-xl bg-amber-500/5 border border-amber-500/10">
                <p className="text-lg font-bold text-amber-500">10%</p>
                <p className="text-[10px] text-muted-foreground uppercase font-bold">Neutral</p>
              </div>
              <div className="text-center p-3 rounded-xl bg-red-500/5 border border-red-500/10">
                <p className="text-lg font-bold text-red-500">5%</p>
                <p className="text-[10px] text-muted-foreground uppercase font-bold">Negative</p>
              </div>
            </div>
            <p className="text-xs text-muted-foreground italic">
              "The customer showed high interest in the pricing and integration features. Recommended follow-up within 24 hours."
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
}
