import React from 'react';
import { motion } from 'framer-motion';
import { 
  CreditCard, 
  Check, 
  Zap, 
  Clock, 
  ArrowUpRight, 
  History,
  ShieldCheck,
  AlertCircle
} from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/Card';

export default function Billing() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold font-display">Billing & Subscription</h1>
        <p className="text-muted-foreground">Manage your plan, payment methods, and usage.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Current Plan */}
        <Card className="lg:col-span-2 border-primary/30 bg-primary/5 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 blur-3xl rounded-full -mr-32 -mt-32"></div>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">Professional Plan</CardTitle>
                <CardDescription>Your current subscription plan</CardDescription>
              </div>
              <div className="px-3 py-1 bg-primary text-black text-xs font-bold rounded-full uppercase tracking-wider">
                Active
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Monthly Cost</p>
                <p className="text-3xl font-bold font-display">$179.00</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Next Billing Date</p>
                <p className="text-xl font-medium">March 15, 2026</p>
              </div>
              <div>
                <p className="text-xs text-muted-foreground uppercase tracking-wider font-bold mb-1">Payment Method</p>
                <div className="flex items-center">
                  <CreditCard className="w-4 h-4 mr-2 text-muted-foreground" />
                  <p className="text-sm font-medium">Visa ending in 4242</p>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="flex justify-between text-sm mb-2">
                <span className="font-medium">Monthly Usage (Minutes)</span>
                <span className="text-muted-foreground">1,245 / 2,500 mins</span>
              </div>
              <div className="w-full h-2 bg-muted rounded-full overflow-hidden">
                <div className="h-full bg-primary neon-glow" style={{ width: '50%' }}></div>
              </div>
              <p className="text-xs text-muted-foreground">You have used 50% of your monthly allowance. Plan resets in 14 days.</p>
            </div>
          </CardContent>
          <CardFooter className="border-t border-primary/10 pt-6 flex space-x-4">
            <Button>Upgrade Plan</Button>
            <Button variant="outline">Cancel Subscription</Button>
          </CardFooter>
        </Card>

        {/* Payment Methods */}
        <Card className="border-border/50 bg-card/50">
          <CardHeader>
            <CardTitle className="text-xl">Payment Methods</CardTitle>
            <CardDescription>Manage your cards and billing info</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="p-4 rounded-xl border border-primary/20 bg-primary/5 flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-muted rounded flex items-center justify-center">
                  <CreditCard className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-bold">Visa •••• 4242</p>
                  <p className="text-xs text-muted-foreground">Expires 12/28</p>
                </div>
              </div>
              <div className="text-[10px] font-bold text-primary uppercase border border-primary/30 px-2 py-0.5 rounded">Primary</div>
            </div>
            <Button variant="outline" className="w-full border-dashed">
              Add New Method
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Billing History */}
      <Card className="border-border/50 bg-card/50">
        <CardHeader>
          <CardTitle className="text-xl flex items-center">
            <History className="w-5 h-5 mr-2 text-primary" />
            Billing History
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-border text-xs font-bold uppercase tracking-wider text-muted-foreground">
                  <th className="px-6 py-4">Invoice ID</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {[
                  { id: 'INV-2026-001', date: 'Feb 15, 2026', amount: '$179.00', status: 'Paid' },
                  { id: 'INV-2026-002', date: 'Jan 15, 2026', amount: '$179.00', status: 'Paid' },
                  { id: 'INV-2025-012', date: 'Dec 15, 2025', amount: '$179.00', status: 'Paid' },
                ].map((inv) => (
                  <tr key={inv.id} className="text-sm hover:bg-white/5 transition-colors">
                    <td className="px-6 py-4 font-medium">{inv.id}</td>
                    <td className="px-6 py-4 text-muted-foreground">{inv.date}</td>
                    <td className="px-6 py-4 font-bold">{inv.amount}</td>
                    <td className="px-6 py-4">
                      <span className="text-[10px] font-bold px-2 py-0.5 bg-emerald-500/10 text-emerald-500 rounded-full uppercase">
                        {inv.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <button className="text-primary hover:underline font-medium">Download PDF</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
