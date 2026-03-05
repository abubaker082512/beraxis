import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/Card';
import { Calendar, Clock, Video, CheckCircle2 } from 'lucide-react';

export default function BookDemo() {
  const [step, setStep] = React.useState(1);

  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold font-display mb-6">See Beraxis <br /><span className="text-primary">In Action</span></h1>
            <p className="text-xl text-muted-foreground mb-10 leading-relaxed">
              Schedule a 15-minute personalized demo with one of our AI experts. We'll show you how to:
            </p>
            <ul className="space-y-6">
              {[
                "Build your first AI agent in minutes",
                "Integrate with your current CRM",
                "Set up automated outbound campaigns",
                "Analyze call sentiment and performance"
              ].map((item, i) => (
                <li key={i} className="flex items-center space-x-4">
                  <div className="p-1 bg-primary/20 rounded-full">
                    <CheckCircle2 className="text-primary w-5 h-5" />
                  </div>
                  <span className="text-lg font-medium">{item}</span>
                </li>
              ))}
            </ul>
            <div className="mt-12 p-6 rounded-2xl bg-card border border-border flex items-center space-x-4">
              <div className="w-12 h-12 rounded-full overflow-hidden">
                <img src="https://i.pravatar.cc/150?u=sarah" alt="Sarah" referrerPolicy="no-referrer" />
              </div>
              <div>
                <p className="font-bold">Sarah Jenkins</p>
                <p className="text-sm text-muted-foreground">Head of Customer Success</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Card className="border-border bg-card/50 backdrop-blur-sm shadow-2xl">
              <CardHeader>
                <CardTitle>Schedule Your Demo</CardTitle>
                <CardDescription>Select a time that works for you</CardDescription>
              </CardHeader>
              <CardContent>
                {step === 1 ? (
                  <div className="space-y-6">
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Full Name</label>
                        <Input placeholder="John Doe" />
                      </div>
                      <div className="space-y-2">
                        <label className="text-sm font-medium">Work Email</label>
                        <Input type="email" placeholder="john@company.com" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Company Name</label>
                      <Input placeholder="Acme Inc." />
                    </div>
                    <div className="space-y-2">
                      <label className="text-sm font-medium">Monthly Call Volume</label>
                      <select className="flex h-10 w-full rounded-md border border-border bg-background px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary transition-all">
                        <option>Under 1,000 calls</option>
                        <option>1,000 - 10,000 calls</option>
                        <option>10,000 - 100,000 calls</option>
                        <option>100,000+ calls</option>
                      </select>
                    </div>
                    <Button className="w-full py-6 text-lg" onClick={() => setStep(2)}>
                      Continue to Calendar
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="p-4 rounded-xl border border-border bg-background/50">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="font-bold flex items-center"><Calendar className="mr-2 w-4 h-4" /> March 2026</h4>
                        <div className="flex space-x-2">
                          <Button variant="ghost" size="sm">Prev</Button>
                          <Button variant="ghost" size="sm">Next</Button>
                        </div>
                      </div>
                      <div className="grid grid-cols-7 gap-2 text-center text-xs text-muted-foreground mb-2">
                        <span>S</span><span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span>
                      </div>
                      <div className="grid grid-cols-7 gap-2">
                        {[...Array(31)].map((_, i) => (
                          <button 
                            key={i} 
                            className={`h-8 rounded-md flex items-center justify-center text-sm transition-colors ${
                              i + 1 === 15 ? 'bg-primary text-black font-bold' : 'hover:bg-primary/20'
                            }`}
                          >
                            {i + 1}
                          </button>
                        ))}
                      </div>
                    </div>
                    <div className="space-y-2">
                      <h4 className="text-sm font-medium flex items-center"><Clock className="mr-2 w-4 h-4" /> Available Times</h4>
                      <div className="grid grid-cols-3 gap-2">
                        {["9:00 AM", "10:30 AM", "1:00 PM", "2:30 PM", "4:00 PM", "5:30 PM"].map((time) => (
                          <Button key={time} variant="outline" size="sm" className="text-xs">{time}</Button>
                        ))}
                      </div>
                    </div>
                    <div className="flex space-x-4">
                      <Button variant="ghost" className="flex-1" onClick={() => setStep(1)}>Back</Button>
                      <Button className="flex-[2]" onClick={() => alert('Demo Scheduled!')}>Confirm Booking</Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
