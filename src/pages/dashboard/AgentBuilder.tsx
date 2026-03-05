import React from 'react';
import { motion } from 'framer-motion';
import { 
  Play, 
  Save, 
  Wand2, 
  Mic, 
  Volume2, 
  Settings, 
  Code2, 
  MessageSquare,
  ChevronRight,
  Plus,
  Trash2,
  Phone
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function AgentBuilder() {
  const [activeTab, setActiveTab] = React.useState('prompt');

  return (
    <div className="h-[calc(100vh-12rem)] flex flex-col space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">AI Agent Builder</h1>
          <p className="text-muted-foreground">Configure your agent's personality, script, and voice.</p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline">
            <Wand2 className="w-4 h-4 mr-2" />
            AI Optimize
          </Button>
          <Button>
            <Save className="w-4 h-4 mr-2" />
            Save Agent
          </Button>
        </div>
      </div>

      <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8 overflow-hidden">
        {/* Editor Side */}
        <Card className="lg:col-span-2 flex flex-col border-border/50 bg-card/50 backdrop-blur-sm overflow-hidden">
          <div className="flex border-b border-border">
            {[
              { id: 'prompt', name: 'System Prompt', icon: MessageSquare },
              { id: 'flow', name: 'Flow Builder', icon: Code2 },
              { id: 'voice', name: 'Voice Settings', icon: Volume2 },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center space-x-2 px-6 py-4 text-sm font-medium transition-all relative ${
                  activeTab === tab.id ? 'text-primary' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <tab.icon className="w-4 h-4" />
                <span>{tab.name}</span>
                {activeTab === tab.id && (
                  <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary neon-glow" />
                )}
              </button>
            ))}
          </div>

          <div className="flex-1 overflow-y-auto p-6 no-scrollbar">
            {activeTab === 'prompt' && (
              <div className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Agent Identity</label>
                  <Input placeholder="e.g. Sarah, Senior Sales Representative" />
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold uppercase tracking-wider text-muted-foreground">System Instructions</label>
                  <textarea 
                    className="w-full h-64 bg-background border border-border rounded-xl p-4 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-primary transition-all"
                    placeholder="You are a helpful sales assistant. Your goal is to book a demo for the Beraxis platform..."
                    defaultValue={`You are Sarah, a professional and friendly sales representative for Beraxis.
Your objective is to call leads who have expressed interest in AI automation.

TONE: Professional, empathetic, and persistent but not pushy.

KNOWLEDGE BASE:
- Beraxis is a voice AI platform.
- It reduces costs by 60% compared to human call centers.
- It integrates with Twilio and Salesforce.

OBJECTION HANDLING:
- "Is this a robot?": "I'm an AI assistant, but I'm here to help you just like a human would. How can I assist you today?"
- "Too expensive": "We have plans starting at just $59/mo, which is significantly cheaper than hiring a full-time agent."`}
                  ></textarea>
                </div>
                <div className="space-y-4">
                  <label className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Dynamic Variables</label>
                  <div className="flex flex-wrap gap-2">
                    {['{{first_name}}', '{{company}}', '{{last_call_date}}', '{{product_interest}}'].map(v => (
                      <span key={v} className="px-2 py-1 bg-primary/10 border border-primary/20 rounded text-xs text-primary font-mono cursor-pointer hover:bg-primary/20 transition-colors">
                        {v}
                      </span>
                    ))}
                    <button className="px-2 py-1 bg-muted border border-border rounded text-xs hover:bg-muted/80 transition-colors">
                      + Add Variable
                    </button>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'flow' && (
              <div className="space-y-6">
                <div className="p-4 bg-primary/5 border border-primary/20 rounded-xl">
                  <p className="text-sm text-primary font-medium">Visual Flow Builder is in Beta. Use the prompt editor for complex logic.</p>
                </div>
                <div className="space-y-4">
                  {[
                    { title: 'Greeting', content: 'Hello! Is this {{first_name}}?' },
                    { title: 'Introduction', content: 'I\'m Sarah from Beraxis. I saw you were interested in our AI Caller.' },
                    { title: 'Qualifying Question', content: 'Are you currently using any automation for your outbound calls?' },
                  ].map((step, i) => (
                    <div key={i} className="flex items-start space-x-4 p-4 bg-card border border-border rounded-xl group">
                      <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-xs font-bold shrink-0">
                        {i + 1}
                      </div>
                      <div className="flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                          <h4 className="font-bold">{step.title}</h4>
                          <div className="flex space-x-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button className="p-1 hover:text-primary"><Settings className="w-4 h-4" /></button>
                            <button className="p-1 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
                          </div>
                        </div>
                        <p className="text-sm text-muted-foreground italic">"{step.content}"</p>
                      </div>
                    </div>
                  ))}
                  <Button variant="outline" className="w-full border-dashed">
                    <Plus className="w-4 h-4 mr-2" />
                    Add Step
                  </Button>
                </div>
              </div>
            )}

            {activeTab === 'voice' && (
              <div className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <label className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Select Voice</label>
                    <div className="space-y-2 max-h-64 overflow-y-auto pr-2 no-scrollbar">
                      {[
                        { name: 'Sarah (Professional)', gender: 'Female', accent: 'US' },
                        { name: 'James (Authoritative)', gender: 'Male', accent: 'UK' },
                        { name: 'Elena (Friendly)', gender: 'Female', accent: 'Spanish' },
                        { name: 'Marcus (Deep)', gender: 'Male', accent: 'US' },
                      ].map((voice, i) => (
                        <div key={i} className={`p-3 rounded-lg border cursor-pointer transition-all flex items-center justify-between group ${
                          i === 0 ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                        }`}>
                          <div className="flex items-center space-x-3">
                            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center">
                              <Mic className={`w-4 h-4 ${i === 0 ? 'text-primary' : 'text-muted-foreground'}`} />
                            </div>
                            <div>
                              <p className="text-sm font-medium">{voice.name}</p>
                              <p className="text-xs text-muted-foreground">{voice.gender} • {voice.accent}</p>
                            </div>
                          </div>
                          <button className="p-2 opacity-0 group-hover:opacity-100 transition-opacity hover:text-primary">
                            <Play className="w-4 h-4 fill-current" />
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div className="space-y-6">
                    <div className="space-y-2">
                      <label className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Voice Speed</label>
                      <input type="range" className="w-full accent-primary" />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Slow</span>
                        <span>Normal</span>
                        <span>Fast</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Stability</label>
                      <input type="range" className="w-full accent-primary" />
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>More Varied</span>
                        <span>Stable</span>
                      </div>
                    </div>
                    <div className="p-4 rounded-xl bg-primary/5 border border-primary/20">
                      <h4 className="text-sm font-bold mb-2 flex items-center">
                        <Mic className="w-4 h-4 mr-2 text-primary" />
                        Voice Cloning
                      </h4>
                      <p className="text-xs text-muted-foreground mb-4">Upload a 30-second audio clip to clone your own voice.</p>
                      <Button variant="outline" size="sm" className="w-full">Upload Sample</Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Simulator Side */}
        <Card className="border-border/50 bg-card/50 backdrop-blur-sm flex flex-col">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Phone className="w-5 h-5 mr-2 text-primary" />
              Test Simulator
            </CardTitle>
            <CardDescription>Simulate a call with your current configuration.</CardDescription>
          </CardHeader>
          <CardContent className="flex-1 flex flex-col">
            <div className="flex-1 bg-background/50 rounded-xl border border-border p-4 mb-6 overflow-y-auto no-scrollbar space-y-4">
              <div className="flex justify-start">
                <div className="bg-muted rounded-2xl rounded-tl-none p-3 max-w-[80%]">
                  <p className="text-xs font-bold text-primary mb-1">Sarah (AI)</p>
                  <p className="text-sm italic">"Hello! Is this John?"</p>
                </div>
              </div>
              <div className="flex justify-end">
                <div className="bg-primary/10 border border-primary/20 rounded-2xl rounded-tr-none p-3 max-w-[80%]">
                  <p className="text-xs font-bold text-muted-foreground mb-1 text-right">You</p>
                  <p className="text-sm">"Yes, this is John. Who's calling?"</p>
                </div>
              </div>
              <div className="flex justify-start">
                <div className="bg-muted rounded-2xl rounded-tl-none p-3 max-w-[80%]">
                  <p className="text-xs font-bold text-primary mb-1">Sarah (AI)</p>
                  <p className="text-sm italic">"I'm Sarah from Beraxis. I saw you were interested in our AI Caller platform. Do you have a moment to chat?"</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="relative">
                <Input placeholder="Type your response..." className="pr-12" />
                <button className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-primary hover:bg-primary/10 rounded-lg transition-all">
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
              <div className="flex space-x-3">
                <Button className="flex-1 py-6 bg-emerald-500 hover:bg-emerald-600 text-white shadow-[0_0_15px_rgba(16,185,129,0.3)]">
                  <Phone className="w-4 h-4 mr-2" />
                  Start Voice Test
                </Button>
              </div>
              <p className="text-[10px] text-center text-muted-foreground uppercase tracking-widest">
                Microphone access required for voice test
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
