import React from 'react';
import { motion } from 'framer-motion';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Check, Zap, Shield, Globe, Cpu, MessageSquare, BarChart3, Users, Headphones, PhoneCall } from 'lucide-react';

export default function Features() {
  const features = [
    {
      title: "AI Script Builder",
      description: "Create complex conversation flows with our drag-and-drop visual editor. No coding required.",
      icon: Cpu,
      details: ["Conditional logic", "Dynamic variables", "Multi-language support"]
    },
    {
      title: "Voice Intelligence",
      description: "Our agents understand context, sentiment, and intent, providing a truly human-like experience.",
      icon: MessageSquare,
      details: ["Sentiment analysis", "Intent detection", "Custom knowledge base"]
    },
    {
      title: "Global Infrastructure",
      description: "Deploy agents globally with low-latency servers. Connect to any SIP or VoIP provider.",
      icon: Globe,
      details: ["Local phone numbers", "SIP trunking", "Global data centers"]
    },
    {
      title: "Advanced Analytics",
      description: "Deep insights into every call. Monitor performance, conversion rates, and agent efficiency.",
      icon: BarChart3,
      details: ["Real-time dashboards", "Custom reporting", "Exportable data"]
    }
  ];

  return (
    <div className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-20">
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-4xl md:text-6xl font-bold font-display mb-6"
          >
            Powerful Features for <span className="text-primary">Modern Teams</span>
          </motion.h1>
          <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
            Beraxis is built with the latest in voice AI technology to give you a competitive edge.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-32">
          {features.map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: i % 2 === 0 ? -20 : 20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
            >
              <Card className="h-full border-border/50 hover:border-primary/30 transition-all bg-card/30 backdrop-blur-sm">
                <CardHeader>
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4">
                    <feature.icon className="text-primary w-6 h-6" />
                  </div>
                  <CardTitle className="text-2xl">{feature.title}</CardTitle>
                  <CardDescription className="text-base">{feature.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-3">
                    {feature.details.map((detail, j) => (
                      <li key={j} className="flex items-center space-x-3 text-sm text-muted-foreground">
                        <Check className="text-primary w-4 h-4" />
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Deep Dive Section */}
        <div className="bg-primary/5 rounded-3xl p-12 border border-primary/10">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div>
              <h2 className="text-3xl md:text-4xl font-bold font-display mb-6">Human-Like Voice Synthesis</h2>
              <p className="text-lg text-muted-foreground mb-8">
                We use proprietary neural voice models that capture the nuances of human speech, including natural pauses, intonations, and emotions.
              </p>
              <div className="space-y-6">
                <div className="flex items-start space-x-4">
                  <div className="mt-1 p-2 bg-primary/20 rounded-full">
                    <Zap className="text-primary w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg">Ultra-Low Latency</h4>
                    <p className="text-muted-foreground">Conversations flow naturally with response times under 500ms.</p>
                  </div>
                </div>
                <div className="flex items-start space-x-4">
                  <div className="mt-1 p-2 bg-primary/20 rounded-full">
                    <Shield className="text-primary w-5 h-5" />
                  </div>
                  <div>
                    <h4 className="font-bold text-lg">Secure & Compliant</h4>
                    <p className="text-muted-foreground">Enterprise-grade security with full data encryption and compliance.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="relative">
              <div className="aspect-square bg-gradient-to-br from-primary/20 to-transparent rounded-full absolute -inset-10 blur-3xl -z-10"></div>
              <img 
                src="https://picsum.photos/seed/voice-tech/800/800" 
                alt="Voice Technology" 
                className="rounded-2xl shadow-2xl border border-white/10"
                referrerPolicy="no-referrer"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
