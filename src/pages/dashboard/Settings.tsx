import React from 'react';
import { motion } from 'framer-motion';
import { 
  Settings as SettingsIcon, 
  Phone, 
  Globe, 
  Shield, 
  Bell, 
  Cpu, 
  Webhook, 
  Save,
  Lock,
  User,
  Zap
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function Settings() {
  const [activeSection, setActiveSection] = React.useState('general');

  const sections = [
    { id: 'general', name: 'General', icon: SettingsIcon },
    { id: 'sip', name: 'SIP & VoIP', icon: Phone },
    { id: 'ai', name: 'AI Models', icon: Cpu },
    { id: 'webhooks', name: 'Webhooks', icon: Webhook },
    { id: 'security', name: 'Security', icon: Shield },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Settings</h1>
          <p className="text-muted-foreground">Configure your platform preferences and integrations.</p>
        </div>
        <Button>
          <Save className="w-4 h-4 mr-2" />
          Save Changes
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Sidebar Nav */}
        <div className="space-y-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => setActiveSection(section.id)}
              className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all ${
                activeSection === section.id 
                  ? 'bg-primary/10 text-primary border border-primary/20' 
                  : 'text-muted-foreground hover:bg-white/5 hover:text-foreground'
              }`}
            >
              <section.icon className="w-5 h-5" />
              <span className="font-medium">{section.name}</span>
            </button>
          ))}
        </div>

        {/* Content Area */}
        <div className="lg:col-span-3 space-y-8">
          {activeSection === 'general' && (
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle>General Settings</CardTitle>
                <CardDescription>Basic information about your organization.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Organization Name</label>
                    <Input defaultValue="Beraxis by ABT IT" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Contact Email</label>
                    <Input defaultValue="admin@abtit.com" />
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Timezone</label>
                    <select className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
                      <option>UTC (GMT+0)</option>
                      <option>EST (GMT-5)</option>
                      <option>PST (GMT-8)</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Default Language</label>
                    <select className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
                      <option>English (US)</option>
                      <option>Spanish</option>
                      <option>French</option>
                    </select>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === 'sip' && (
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle>SIP & VoIP Configuration</CardTitle>
                <CardDescription>Connect your telephony providers.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-8">
                <div className="p-6 rounded-2xl border border-primary/20 bg-primary/5">
                  <h4 className="font-bold mb-4 flex items-center">
                    <Globe className="w-5 h-5 mr-2 text-primary" />
                    Twilio Integration
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Account SID</label>
                      <Input type="password" value="ACxxxxxxxxxxxxxxxxxxxxxxxx" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Auth Token</label>
                      <Input type="password" value="••••••••••••••••••••••••" />
                    </div>
                  </div>
                  <Button variant="outline" className="mt-6">Test Connection</Button>
                </div>

                <div className="space-y-4">
                  <h4 className="font-bold">Custom SIP Trunk</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium">SIP Server</label>
                      <Input placeholder="sip.provider.com" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Port</label>
                      <Input placeholder="5060" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Username</label>
                      <Input placeholder="Username" />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Password</label>
                      <Input type="password" placeholder="••••••••" />
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === 'ai' && (
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle>AI Model Selection</CardTitle>
                <CardDescription>Choose the underlying LLM for your agents.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  {[
                    { name: 'GPT-4o (Recommended)', provider: 'OpenAI', desc: 'Best for complex reasoning and natural flow.', latency: 'Low' },
                    { name: 'Claude 3.5 Sonnet', provider: 'Anthropic', desc: 'Excellent for creative scripts and empathy.', latency: 'Medium' },
                    { name: 'Llama 3 (Local)', provider: 'ABT VPS', desc: 'On-premise hosting for maximum data privacy.', latency: 'Ultra-Low' },
                  ].map((model, i) => (
                    <div key={i} className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      i === 0 ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50'
                    }`}>
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-bold">{model.name}</h4>
                        <span className="text-[10px] font-bold px-2 py-0.5 bg-muted rounded uppercase tracking-wider">{model.provider}</span>
                      </div>
                      <p className="text-sm text-muted-foreground mb-2">{model.desc}</p>
                      <div className="flex items-center text-xs text-primary font-bold">
                        <Zap className="w-3 h-3 mr-1" />
                        Latency: {model.latency}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {activeSection === 'webhooks' && (
            <Card className="border-border/50 bg-card/50">
              <CardHeader>
                <CardTitle>Webhook Settings</CardTitle>
                <CardDescription>Receive real-time updates for call events.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between p-4 bg-muted/50 rounded-xl border border-border">
                    <div className="flex items-center space-x-3">
                      <Webhook className="w-5 h-5 text-primary" />
                      <div>
                        <p className="text-sm font-medium">CRM Sync Webhook</p>
                        <p className="text-xs text-muted-foreground">https://api.crm.com/webhooks/calls</p>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button variant="ghost" size="sm">Edit</Button>
                      <Button variant="ghost" size="sm" className="text-red-500">Delete</Button>
                    </div>
                  </div>
                  <Button variant="outline" className="w-full border-dashed">
                    Add New Webhook
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
