import React from 'react';
import { motion } from 'framer-motion';
import { 
  Users, 
  Shield, 
  Server, 
  Key, 
  Activity, 
  AlertTriangle,
  CheckCircle2,
  MoreVertical,
  UserPlus
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';

export default function AdminPanel() {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold font-display">Admin Panel</h1>
          <p className="text-muted-foreground">System-wide management for multi-tenant SaaS.</p>
        </div>
        <Button>
          <UserPlus className="w-4 h-4 mr-2" />
          Add New Tenant
        </Button>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { name: 'API Status', status: 'Operational', icon: Activity, color: 'text-emerald-500' },
          { name: 'Voice Servers', status: 'Healthy', icon: Server, color: 'text-emerald-500' },
          { name: 'Database', status: 'Operational', icon: Server, color: 'text-emerald-500' },
        ].map((item, i) => (
          <Card key={i} className="border-border/50 bg-card/50">
            <CardContent className="p-6 flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className={`p-2 rounded-lg bg-muted ${item.color}`}>
                  <item.icon className="w-5 h-5" />
                </div>
                <div>
                  <p className="text-xs text-muted-foreground uppercase font-bold tracking-wider">{item.name}</p>
                  <p className="text-sm font-medium">{item.status}</p>
                </div>
              </div>
              <CheckCircle2 className="w-5 h-5 text-emerald-500" />
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Tenant Management */}
        <Card className="lg:col-span-2 border-border/50 bg-card/50">
          <CardHeader>
            <CardTitle className="text-xl flex items-center">
              <Users className="w-5 h-5 mr-2 text-primary" />
              Tenant Management
            </CardTitle>
            <CardDescription>Manage client organizations and their permissions.</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-border text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    <th className="px-6 py-4">Organization</th>
                    <th className="px-6 py-4">Plan</th>
                    <th className="px-6 py-4">Users</th>
                    <th className="px-6 py-4">Status</th>
                    <th className="px-6 py-4">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-border">
                  {[
                    { name: 'Acme Corp', plan: 'Enterprise', users: 45, status: 'Active' },
                    { name: 'Global Sales Inc', plan: 'Professional', users: 12, status: 'Active' },
                    { name: 'Tech Solutions', plan: 'Starter', users: 3, status: 'Suspended' },
                    { name: 'Nexus AI', plan: 'Enterprise', users: 89, status: 'Active' },
                  ].map((tenant, i) => (
                    <tr key={i} className="text-sm hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4 font-medium">{tenant.name}</td>
                      <td className="px-6 py-4 text-muted-foreground">{tenant.plan}</td>
                      <td className="px-6 py-4">{tenant.users}</td>
                      <td className="px-6 py-4">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                          tenant.status === 'Active' ? 'bg-emerald-500/10 text-emerald-500' : 'bg-red-500/10 text-red-500'
                        }`}>
                          {tenant.status}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <button className="p-2 hover:bg-muted rounded-lg transition-all">
                          <MoreVertical className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Security & API Keys */}
        <div className="space-y-8">
          <Card className="border-border/50 bg-card/50">
            <CardHeader>
              <CardTitle className="text-xl flex items-center">
                <Key className="w-5 h-5 mr-2 text-primary" />
                System API Keys
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-xs font-bold text-muted-foreground uppercase">Master API Key</p>
                <div className="flex items-center space-x-2">
                  <div className="flex-1 bg-background border border-border rounded px-3 py-1.5 text-xs font-mono truncate">
                    abt_master_live_842910482910482
                  </div>
                  <Button variant="outline" size="sm">Copy</Button>
                </div>
              </div>
              <Button variant="outline" className="w-full text-xs">Regenerate Master Key</Button>
            </CardContent>
          </Card>

          <Card className="border-red-500/20 bg-red-500/5">
            <CardHeader>
              <CardTitle className="text-xl flex items-center text-red-500">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Danger Zone
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-xs text-muted-foreground">These actions are irreversible and affect the entire system.</p>
              <Button variant="outline" className="w-full text-red-500 border-red-500/30 hover:bg-red-500/10">
                Maintenance Mode
              </Button>
              <Button variant="outline" className="w-full text-red-500 border-red-500/30 hover:bg-red-500/10">
                Purge System Logs
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
