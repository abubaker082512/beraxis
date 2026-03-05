import React from 'react';
import { motion } from 'framer-motion';
import {
  Plus,
  Search,
  Filter,
  MoreVertical,
  Play,
  Pause,
  Trash2,
  Edit2,
  Upload,
  FileText,
  Users,
  BarChart3,
  Megaphone,
  Bot,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import api from '@/lib/api';

export default function Campaigns() {
  const [isCreateModalOpen, setIsCreateModalOpen] = React.useState(false);
  const [campaigns, setCampaigns] = React.useState<any[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [isCreating, setIsCreating] = React.useState(false);
  const [newCampaign, setNewCampaign] = React.useState({ name: '', description: '' });

  const fetchCampaigns = async () => {
    setIsLoading(true);
    try {
      const response = await api.get('/campaigns');
      if (response.data.success) {
        setCampaigns(response.data.data);
      }
    } catch (err) {
      console.error('Failed to fetch campaigns');
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchCampaigns();
  }, []);

  const handleCreate = async () => {
    if (!newCampaign.name) return;
    setIsCreating(true);
    try {
      const response = await api.post('/campaigns', newCampaign);
      if (response.data.success) {
        setIsCreateModalOpen(false);
        setNewCampaign({ name: '', description: '' });
        fetchCampaigns();
      }
    } catch (err) {
      console.error('Failed to create campaign');
    } finally {
      setIsCreating(false);
    }
  };

  const toggleCampaign = async (id: string, currentStatus: string) => {
    const action = currentStatus === 'active' ? 'pause' : 'start';
    try {
      await api.post(`/campaigns/${id}/${action}`);
      fetchCampaigns();
    } catch (err) {
      console.error(`Failed to ${action} campaign`);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Campaigns</h1>
          <p className="text-muted-foreground">Manage and monitor your AI calling campaigns.</p>
        </div>
        <Button onClick={() => setIsCreateModalOpen(true)}>
          <Plus className="w-4 h-4 mr-2" />
          Create Campaign
        </Button>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 bg-card/50 p-4 rounded-xl border border-border">
        <div className="relative w-full sm:w-96">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input placeholder="Search campaigns..." className="pl-10" />
        </div>
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <Button variant="outline" size="sm">
            <Filter className="w-4 h-4 mr-2" />
            Filter
          </Button>
          <select className="bg-background border border-border rounded-md px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
            <option>All Status</option>
            <option>Active</option>
            <option>Paused</option>
            <option>Draft</option>
          </select>
        </div>
      </div>

      {/* Campaign List */}
      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
          <Loader2 className="w-8 h-8 animate-spin mb-4" />
          <p>Loading campaigns...</p>
        </div>
      ) : campaigns.length === 0 ? (
        <Card className="border-dashed border-2 py-20">
          <CardContent className="flex flex-col items-center justify-center text-center">
            <Megaphone className="w-12 h-12 text-muted-foreground mb-4 opacity-50" />
            <h3 className="text-xl font-bold">No campaigns yet</h3>
            <p className="text-muted-foreground mb-6">Create your first campaign to start calling leads.</p>
            <Button onClick={() => setIsCreateModalOpen(true)}>Get Started</Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {campaigns.map((campaign) => (
            <Card key={campaign.id} className="border-border/50 bg-card/50 hover:border-primary/30 transition-all group">
              <CardContent className="p-6">
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6">
                  <div className="flex items-center space-x-4">
                    <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${campaign.status === 'active' ? 'bg-primary/10 text-primary' :
                      campaign.status === 'paused' ? 'bg-amber-500/10 text-amber-500' : 'bg-muted text-muted-foreground'
                      }`}>
                      <Megaphone className="w-6 h-6" />
                    </div>
                    <div>
                      <h3 className="text-lg font-bold group-hover:text-primary transition-colors">{campaign.name}</h3>
                      <p className="text-sm text-muted-foreground">Created at {new Date(campaign.created_at).toLocaleDateString()}</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-8 flex-1 max-w-2xl">
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Status</p>
                      <div className="flex items-center">
                        <div className={`w-2 h-2 rounded-full mr-2 ${campaign.status === 'active' ? 'bg-primary neon-glow' :
                          campaign.status === 'paused' ? 'bg-amber-500' : 'bg-muted-foreground'
                          }`}></div>
                        <span className="text-sm font-medium capitalize">{campaign.status}</span>
                      </div>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Leads</p>
                      <p className="text-sm font-medium">{campaign.total_leads?.toLocaleString() || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Calls</p>
                      <p className="text-sm font-medium">{campaign.calls_made?.toLocaleString() || 0}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Success</p>
                      <p className="text-sm font-medium text-emerald-500">{campaign.success_rate}%</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="icon" className="hover:text-primary" onClick={() => toggleCampaign(campaign.id, campaign.status)}>
                      {campaign.status === 'active' ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                    </Button>
                    <Button variant="ghost" size="icon" className="hover:text-primary">
                      <Edit2 className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon" className="hover:text-red-500">
                      <Trash2 className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="icon">
                      <MoreVertical className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Campaign Modal */}
      {isCreateModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-2xl bg-card border border-border rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="p-6 border-b border-border flex items-center justify-between">
              <h2 className="text-2xl font-bold font-display">Create New Campaign</h2>
              <button onClick={() => setIsCreateModalOpen(false)} className="text-muted-foreground hover:text-foreground">
                <Plus className="w-6 h-6 rotate-45" />
              </button>
            </div>
            <div className="p-8 space-y-6">
              <div className="space-y-2">
                <label className="text-sm font-medium">Campaign Name</label>
                <Input
                  placeholder="e.g. Summer Sales Outreach"
                  value={newCampaign.name}
                  onChange={(e) => setNewCampaign({ ...newCampaign, name: e.target.value })}
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <label className="text-sm font-medium flex items-center">
                    <Upload className="w-4 h-4 mr-2 text-primary" />
                    Description (Internal)
                  </label>
                  <textarea
                    className="w-full h-32 bg-background border border-border rounded-xl p-3 text-sm focus:outline-none focus:ring-1 focus:ring-primary"
                    placeholder="Short description of this campaign..."
                    value={newCampaign.description}
                    onChange={(e) => setNewCampaign({ ...newCampaign, description: e.target.value })}
                  />
                </div>
                <div className="space-y-4">
                  <label className="text-sm font-medium flex items-center">
                    <Bot className="w-4 h-4 mr-2 text-primary" />
                    Select AI Agent
                  </label>
                  <select className="w-full bg-background border border-border rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-primary">
                    <option>Sales Agent - Professional</option>
                    <option>Support Agent - Friendly</option>
                    <option>Survey Agent - Direct</option>
                  </select>
                  <div className="p-4 rounded-xl bg-muted/50 border border-border">
                    <p className="text-xs font-bold uppercase text-muted-foreground mb-2">Agent Preview</p>
                    <p className="text-sm italic">"Hello! This is Sarah from Beraxis. I'm calling to..."</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="p-6 border-t border-border flex justify-end space-x-4">
              <Button variant="ghost" onClick={() => setIsCreateModalOpen(false)}>Cancel</Button>
              <Button onClick={handleCreate} disabled={isCreating || !newCampaign.name}>
                {isCreating ? 'Creating...' : 'Create & Launch'}
              </Button>
            </div>
          </motion.div>
        </div>
      )}
    </div>
  );
}

function MegaphoneIcon({ className }: { className?: string }) {
  return <Megaphone className={className} />;
}

function BotIcon({ className }: { className?: string }) {
  return <Bot className={className} />;
}
